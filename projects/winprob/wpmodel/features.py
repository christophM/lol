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



def filter_events(events, event_type, filter_fun=lambda x: x):
    """
    INPUT: 
        events: from game frame
        event_type: that should be filtered and returned
        filter_fun: additional filter function for the events
    """
    return filter(lambda x: x["eventType"] == event_type and filter_fun(x), events)


def filter_team_events(events, team, team_100, id_field="killerId"):
    if team == 100:
        player_ids = team_100
    else:
        player_ids = np.setdiff1d(range(1, 10), team_100)
    return [event for event in events if event[id_field] in player_ids]


def frame_events_to_dict(events, team_100):
    """
    Extract features from the events, which contain neutral objectives, kill, shopping and lots more
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
    team_100 = get_team_memberids(match)
    winner_100 =  get_winner(match)
    match_dict = {"winner_100": winner_100, "matchId": match["matchId"]}
    ## first frame is not informative
    frames = match["timeline"]["frames"][1:]
    dataset = [frame_to_dict(frame=frame, match_dict=match_dict, team_100=team_100) for frame in frames]
    return dataset
