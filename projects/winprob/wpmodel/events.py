import numpy as np


def filter_events(events, event_type, filter_fun=lambda x: x):
    """Filter events of special types and with certain attributes
    
    Keyword arguments
    events - list of events as contained in lol match (from api)
    event_type - string with the event type that should be filtered
    filter_fun - additional filter function to be applied to the events
    """
    return filter(lambda x: x["eventType"] == event_type and filter_fun(x), events)


def filter_team_events(events, team_members, enemy=False, id_field="killerId"):
    """ Filter events that belong to a specific team.

    Keyword arguments
    events - list of events as contained in a lol match (from api)
    team_members - list of int containing the ids of the team members
    enemy - flag of type boolean. False if team events from team_members should 
            be extracted, True if opposite team should be filtered
    id_fields - field name of type string specifying in which field of the events to look 
    """
    if enemy:
        team_events = [event for event in events if event[id_field] not in team_members]
    else:
        team_events = [event for event in events if event[id_field]  in team_members]
    
    return team_events



def get_events_by_timestamps(match, timestamps):
    """Select all events from given timestamps

    Keyword arguments
    match - the match of type Match
    timestamps - timestamps of type int for filtering the frames
    """
    frames = match.match["timeline"]["frames"]
    events = np.array([frame.get("events") for frame in frames])
    return events[timestamps]

def get_top_n_minutes(match, n=3):
    """Select timeframes with the biggest jump in winprobability
    
    Keyword arguments: 
    match - the match of type Match
    n - number of type int for how many top frames should be extracted
    """
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
    def to_percentage(number):
        return 100 * round(number, 4)
    for minute in top_minutes:
        events = get_events_by_timestamps(match, minute + 1)
        events_summary = summarize_important_events_one_frame(events, match.team_members, match.participantId)
        winprob_jump = to_percentage(match.winprob[minute + 1] - match.winprob[minute])
        winprob_from = to_percentage(match.winprob[minute])
        winprob_to = to_percentage(match.winprob[minute + 1])
        top_events.append({"timestamp": minute, "winprob_from": winprob_from, "winprob_to": winprob_to, "summary": events_summary, "winprob_jump": winprob_jump})
    return top_events

def summarize_important_events_one_frame(events_frame, team_members, participantId):
    """Summarize one frames events
    
    Keyword arguments
    events_frame - list of events as contained in a lol match (from api). One event in 
                   this list has the fields: team, summoner, target, verb
    team_members - list of int with the ids of the participants teams members
    participantId - the id of type int of the participant for which the events 
                    are extracted
    """
    events = []

    champion_kills =  filter_events(events_frame, "CHAMPION_KILL")

    champion_kills_summoner_team = filter_team_events(champion_kills, team_members, enemy=False)
    if champion_kills_summoner_team:
        events.append({"who": "summoner_team", 
                       "what": "champion_kill", 
                       "count": len(champion_kills_summoner_team)})

    champion_kills_summoner = filter_events(champion_kills, "CHAMPION_KILL", lambda x: x["killerId"] == participantId)
    if champion_kills_summoner:
        events.append({"who": "summoner", 
                       "what": "champion_kill",
                       "count": len(champion_kills_summoner)})

    champion_kills_enemy_team = filter_team_events(champion_kills, team_members, enemy=True)
    if champion_kills_enemy_team:
        events.append({"who": "enemy_team", 
                       "what": "champion_kill", 
                       "count": len(champion_kills_enemy_team)})

    dragon_kill = filter_events(events_frame, u'ELITE_MONSTER_KILL', lambda x: x[u'monsterType'] ==  u"DRAGON")
    dragon_summoner_team = filter_team_events(dragon_kill, team_members, enemy=False)
    if dragon_summoner_team:
        events.append({"who": "summoner_team", 
                       "what": "dragon_kill", 
                       "count": 1})

    dragon_enemy_team = filter_team_events(dragon_kill, team_members, enemy=True)
    if dragon_enemy_team:
        events.append({"who": "enemy_team", 
                       "what": "dragon_kill", 
                       "count": 1})
        
    baron_kill = filter_events(events_frame, u'ELITE_MONSTER_KILL', lambda x: x[u'monsterType'] == u"BARON")
    baron_summoner_team = filter_team_events(baron_kill, team_members, enemy=False)
    if baron_summoner_team:
        events.append({"who": "summoner_team",
                       "what": "baron_kill", 
                       "count": 1})

    baron_enemy_team = filter_team_events(baron_kill, team_members, enemy=True)
    if baron_enemy_team:
        events.append({"who": "enemy_team",
                       "what": "baron_kill", 
                       "count": 1})

    return events
