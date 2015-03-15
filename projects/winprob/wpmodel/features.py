## Module to extract features from the timelines
import numpy as np
import pandas as pd


def get_team_memberids(match, reference_teamId=100):
    """
    Return a dictionary with participant -> team
    """
    return [x["participantId"] for x in match["participants"] if  x["teamId"] == 100]


def get_winner(match, reference_teamId=100):
    """
    Extract id of winning team
    """
    return filter(lambda x: x["teamId"] == reference_teamId, match["teams"])[0]["winner"]


def get_teamId(match, summonerId):
    """
    Input: Match dictionary and the summonerId
    Output: The ID of the team the summoner was in for this match
    """
    ## Find participantId for summonerId
    participantId = get_participantId(match, summonerId)
    ## Find and return teamId for summonerId
    return filter(lambda x: x["participantId"] == participantId, match["participants"])[0]["teamId"]

def get_participantId(match, summonerId):
    """
    Input: Match dictionary and the summonerId
    Output: The participant ID the summoner was given for this game
    """
    return filter(lambda x: x["player"]["summonerId"] == summonerId, match["participantIdentities"])[0]["participantId"]

def get_summoner_win(match, summonerId):
    """
    Input: Match dictionary and the summonerId
    Output: 
    """
    summoner_team = get_teamId(match, summonerId)
    return get_winner(match, reference_teamId=summoner_team)


def get_labels(matches, reference_teamId=100):
    """
    Input: List of matches and the reference team id
    Output: A vector with size equal the sum of all (match lengths - 1). Each entry indicates if the reference has won in this match
    """
    label_frames = []
    for match in matches: 
        winner = get_winner(match, reference_teamId)
        matchId = match["matchId"]
        timestamps =  [frame["timestamp"] / 60000 for frame in match["timeline"]["frames"]]
        label_frames.append(pd.DataFrame({"winner": winner, "matchId": matchId, "timestamp": timestamps}))
    
    labels = pd.concat(label_frames)                
    labels = labels[labels.timestamp != 0]
    labels.set_index(["matchId", "timestamp"], inplace=True)
    return labels

def filter_events(events, event_type, filter_fun=lambda x: x):
    """
    INPUT:
        events: from game frame
        event_type: that should be filtered and returned
        filter_fun: additional filter function for the events
    """
    return filter(lambda x: x["eventType"] == event_type and filter_fun(x), events)


def filter_team_events(events, team, team_100, id_field="killerId"):
    """
    Return events that belong to a specific team. 
    Input: event list, team id that should be filtered, list of participantIds for team_100, id_field used for filtering
    Output: event list only containing events from specified team
    """
    if team == 100:
        player_ids = team_100
    else:
        player_ids = np.setdiff1d(range(1, 10), team_100)
    return [event for event in events if event[id_field] in player_ids]


def frame_events_to_dict(events, team_100):
    """
    Extract features from the events, which contain neutral objectives, kill, shopping and lots more
    TODO: 
    Write tests for event summaries. In match["teams"] there is a summary of the events which could be used.
    """
    results = {}

    dragon_kill = filter_events(events, u'ELITE_MONSTER_KILL', lambda x: x[u'monsterType'] ==  u"DRAGON")

    dragon_100 = len(filter_team_events(dragon_kill, 100, team_100))
    dragon_200 = len(filter_team_events(dragon_kill, 200, team_100))

    results.setdefault("dragon_kill_100", dragon_100)
    results.setdefault("dragon_kill_200", dragon_200)

    champion_kills = filter_events(events, 'CHAMPION_KILL')
    results.setdefault("champion_kill_100", len(filter_team_events(champion_kills, 100, team_100)))
    results.setdefault("champion_kill_200", len(filter_team_events(champion_kills, 200, team_100)))


    building_kills = filter_events(events, "BUILDING_KILL")

    if len(building_kills) > 0:
        building_kills_100 = len(filter_team_events(building_kills, 100, team_100))
        building_kills_200 = len(filter_team_events(building_kills, 200, team_100))

        inner_kills_100 = len([kill for kill in building_kills if (kill["towerType"] == u'INNER_TURRET' and  kill["killerId"] in team_100)])
        inner_kills_200 = len([kill for kill in building_kills if (kill["towerType"] == u'INNER_TURRET' and kill["killerId"] not in team_100)])
        inhibitor_kills_100 =  len([kill for kill in building_kills if (kill['buildingType'] == u'INHIBITOR_BUILDING' and kill["killerId"] in team_100)])
        inhibitor_kills_200 =  len([kill for kill in building_kills if (kill['buildingType'] == u'INHIBITOR_BUILDING' and kill["killerId"] not in team_100)])

        results.setdefault("building_kill_100", building_kills_100)
        results.setdefault("building_kill_200", building_kills_200)
        results.setdefault("kill_inner_100", inner_kills_100)
        results.setdefault("kill_inner_200", inner_kills_200)
        results.setdefault("kill_inhibitor_100", inhibitor_kills_100)
        results.setdefault("kill_inhibitor_200", inhibitor_kills_200)

    return results

def frame_participant_to_dict(pframes, team_100):
    """
    Extract features from the participantFrames, which contain gold, minionkills, junglekills, level
    """
    pframes_100 = [v for k, v in pframes.iteritems() if int(k) in team_100]
    pframes_200 = [v for k, v in pframes.iteritems() if int(k) not in team_100]

    sum_of_gold_100 = np.sum([x["totalGold"] for x in pframes_100])
    sum_of_gold_200 = np.sum([x["totalGold"] for x in pframes_200])

    level_max_100 = max(x["level"] for x in pframes_100)
    level_max_200 = max(x["level"] for x in pframes_200)
    level_sum_100 = np.sum(x["level"] for x in pframes_100)
    level_sum_200 = np.sum(x["level"] for x in pframes_200)

    result =  {"gold_100": sum_of_gold_100, "gold_200": sum_of_gold_200, "level_max_100": level_max_100, "level_max_200": level_max_200,
               "level_sum_100": level_sum_100, "level_sum_200": level_sum_200}
    return result

def frame_to_dict(frame, match_dict, team_100):
    """
    Extract one frame from the timeline(frames) and build features and add label
    INPUT:
        frame is one frame of the timeline
        match_dict is a dictionary with the label and features that are the same for the whole match
        team_100 is the list of ids for member of team with id of 100
    OUTPUT:
        dictionairy with label and features for one frame
    """
    participants_dict = frame_participant_to_dict(frame["participantFrames"], team_100)
    if "events" in frame:
        events_dict = frame_events_to_dict(frame["events"], team_100)
    else:
        events_dict = {}


    timestamp = {"timestamp": frame["timestamp"] / 60000}
    return dict(timestamp.items() + match_dict.items() + participants_dict.items() + events_dict.items())


def match_to_dataset(match):
    """
    Take a match dict and turn it into a pandas dataset row
    """
    team_100 = get_team_memberids(match)
    winner_100 =  get_winner(match)
    match_dict = {"winner_100": winner_100, "matchId": match["matchId"]}
    ## first frame is not informative
    frames = match["timeline"]["frames"][1:]
    dataset = [frame_to_dict(frame=frame, match_dict=match_dict, team_100=team_100) for frame in frames]
    return dataset


def matches_to_dataframe(matches_dict):
    """
    Same as matches_to_experiment_dataframe, but for production
    """
    return matches_to_experiment_dataframe(matches_dict)

def matches_to_experiment_dataframe(matches_dict):
    """
    Input: List of timelines dictionairies
    Output: Pandas dataframe where each row represents one minute of a game with all its features
    This function computes lots of features and is for experimentation and training of the random forest
    """
    data_rows =  [match_to_dataset(match) for match in matches_dict if "timeline" in match]
    data_rows_flattened = [item for sublist in data_rows for item in sublist]
    matches_df = pd.DataFrame(data_rows_flattened)
    matches_df = matches_df.reset_index()
    matches_df_plus = compute_additional_experiment_features(matches_df)
    result = matches_df_plus.reset_index().set_index(["matchId", "timestamp"])
    return result


def compute_additional_experiment_features(matches):
    """
    Compute some additional features like cumsum and diffs
    """
    matches.set_index("matchId")
    matches.fillna(0, inplace=True)
    matches["gold_diff"] = matches.gold_100 - matches.gold_200
    matches["dragons_100"] = matches.groupby(level=0).dragon_kill_100.cumsum()
    matches["dragons_200"] = matches.groupby(level=0).dragon_kill_200.cumsum()
    matches["dragons_diff"] = matches.dragons_100 - matches.dragons_200
    matches["gold_diff_rel"] = matches.gold_100 / matches.gold_200
    matches["level_sum_diff"] = matches.level_sum_100 - matches.level_sum_200
    matches["level_max_diff"] = matches.level_max_100 - matches.level_max_200
    matches["champion_kill_100_sum"] = matches.groupby(level=0).champion_kill_100.cumsum()
    matches["champion_kill_200_sum"] = matches.groupby(level=0).champion_kill_200.cumsum()
    matches["champion_kill_sum_diff"] = matches.champion_kill_100_sum - matches.champion_kill_200_sum
    matches["building_kill_100_sum"] = matches.groupby(level=0).building_kill_100.cumsum()
    matches["building_kill_200_sum"] = matches.groupby(level=0).building_kill_200.cumsum()
    matches["inhibitor_kill_100_sum"] = matches.groupby(level=0).kill_inhibitor_100.cumsum()
    matches["inhibitor_kill_200_sum"] = matches.groupby(level=0).kill_inhibitor_200.cumsum()
    matches["kill_inner_100_sum"] = matches.groupby(level=0).kill_inner_100.cumsum()
    matches["kill_inner_200_sum"] = matches.groupby(level=0).kill_inner_200.cumsum()
    return matches



class FeatureBuilder():

    def __init__(self, kind):
        if kind not in ["experiment", "production"]:
            raise Exception("kind must be either experiment or production")
        self.kind = kind
    
    def fit(self, matches, y):
        pass

    def fit_transform(self, matches, y=None):
        return self.transform(matches, y)
    
    def transform(self, matches, y=None):
        if self.kind == "experiment":
            features = matches_to_experiment_dataframe(matches)
            X = features[["gold_diff","gold_100", "gold_200",  "gold_diff_rel", 
               "dragons_100", "dragons_200",  "dragons_diff", 
               "level_max_100", "level_max_200", "level_sum_100", "level_sum_200", "level_sum_diff", "level_max_diff", 
               "champion_kill_100", "champion_kill_200", "champion_kill_100_sum", "champion_kill_200_sum", "champion_kill_sum_diff", 
               "building_kill_100", "building_kill_200", "kill_inhibitor_100", "kill_inhibitor_200", "building_kill_200", "building_kill_100",
               "inhibitor_kill_100_sum", "inhibitor_kill_200_sum", "kill_inner_100", "kill_inner_200", "kill_inner_100_sum", "kill_inner_200_sum"
               ]]
        else:
            features = matches_to_dataframe(matches)
            X = features[["gold_diff", "level_sum_diff", "champion_kill_sum_diff", "dragons_diff"]]

        return X

