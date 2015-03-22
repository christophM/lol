import numpy as np


def filter_events(events, event_type, filter_fun=lambda x: x):
    """
    INPUT:
        events: from game frame
        event_type: that should be filtered and returned
        filter_fun: additional filter function for the events
    """
    return filter(lambda x: x["eventType"] == event_type and filter_fun(x), events)


def filter_team_events(events, team_members, enemy=False, id_field="killerId"):
    """
    Return events that belong to a specific team.
    Input: event list, team id that should be filtered, list of participantIds for team_100, id_field used for filtering
    Output: event list only containing events from specified team
    """
    if enemy:
        team_events = [event for event in events if event[id_field] not in team_members]
    else:
        team_events = [event for event in events if event[id_field]  in team_members]
    
    return team_events



def get_events_by_timestamps(match, timestamps):
    """Select all events from given timestamps"""
    frames = match.match["timeline"]["frames"]
    events = np.array([frame.get("events") for frame in frames])
    return events[timestamps]

def get_top_n_minutes(match, n=3):
    ## get_top_n_minutes
    jumps = np.abs(np.append(np.diff(match.get_winprob()), 0))
    top_jumps_indices = jumps.argsort()[-n:][::-1]
    return top_jumps_indices

def summarize_important_events(match, top=3):
    """Summarize events that yielded biggest winprobability jumps

    Keyword arguments:
    match - LoL match of type Match containing the match that should be summarized
    top - Number of events
    """

    top_minutes = get_top_n_minutes(match, n=top)
    top_events = []
    for minute in top_minutes:
        events = get_events_by_timestamps(match, minute + 1)
        events_summary = summarize_important_events_one_frame(events, match.team_members, match.participantId)
        winprob_from = match.winprob[minute]
        winprob_to = match.winprob[minute + 1]
        top_events.append({"minute": minute + 1, "winprob_from": winprob_from, "winprob_to": winprob_to, "summary": events_summary})
    return top_events

def summarize_important_events_one_frame(events_frame, team_members, participantId):
    """Summarize one frames events"""
    champion_kills =  filter_events(events_frame, "CHAMPION_KILL")
    champion_kills_summoner_team = filter_team_events(champion_kills, team_members, enemy=False)
    champion_kills_summoner = filter_events(champion_kills, "CHAMPION_KILL", lambda x: x["killerId"] == participantId)
    champion_kills_enemy_team = filter_team_events(champion_kills, team_members, enemy=True)

    dragon_kill = filter_events(events_frame, u'ELITE_MONSTER_KILL', lambda x: x[u'monsterType'] ==  u"DRAGON")
    dragon_summoner_team = len(filter_team_events(dragon_kill, team_members, enemy=False))
    dragon_enemy_team = len(filter_team_events(dragon_kill, team_members, enemy=True))

    ## you killed n champs
    ## your team killed n champs
    ## your team killed dragon
    ## enemy team killed dragon
    return {"champ_kills_summoner_team": len(champion_kills_summoner_team),
            "champ_kills_summoner": len(champion_kills_summoner),
            "champ_kills_enemy_team": len(champion_kills_enemy_team),
            "dragon_summoner_team": dragon_summoner_team,
            "dragon_enemy_team": dragon_enemy_team}
