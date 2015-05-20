import rawpi
import json
from model import WinProbabilityPipeline
from match import Match
from events import summarize_important_events
from subprocess import call




def get_summoner_id(region, summonerName):
    """Wraps the API handler to get the id by name"""
    return json.loads(rawpi.get_summoner_by_name(region, summonerName).text)[summonerName]["id"]

def get_last_match_id(region, summonerId):
    ## get last fifteen matches
    match_history = rawpi.get_matchhistory(region, summonerId)
    match_history = json.loads(match_history.text)["matches"]
    match_ids = [x["matchId"] for x in match_history]

    matchId = match_ids[len(match_ids) - 1]
    return matchId


def get_last_match(region, matchId, summonerName):
    ## download last match
    match = Match(json.loads(rawpi.get_match(region=region, matchId=matchId, includeTimeline=True).text), summonerName=summonerName)
    return match

def get_last_match_winprob(match):
    ## load pipeline
    wp = WinProbabilityPipeline()
    wp.from_file("/Users/chris/Projects/lol/projects/winprob/model-serialized/wp-pipeline.pkl")
    timestamps = match.timestamps
    winprob = wp.predict(match.match, match.teamId)
    return get_winprobability_string_png(timestamps, winprob)


if __name__=="__main__":
    main(sys.argv)
