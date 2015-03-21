import sys
sys.path.append('/Users/chris/Projects/lol/lib/')
import rawpi
import json
from model import WinProbabilityPipeline
from match import Match
from visualize import plot_winprobability
from subprocess import call




def main(argvs):
    region = argvs[1]
    print region
    ## take summonerId
    summonerName = argvs[2]
    print summonerName
    ## get summonerID
    try:
        summonerId = json.loads(rawpi.get_summoner_by_name(region, summonerName).text)[summonerName]["id"]
    except: 
        print "Could not find summoner"
    print summonerId
    get_last_game_winprob(region, summonerId)


def get_last_game_winprob(region, summonerId):
    ## get last ten matches
    match_history = rawpi.get_matchhistory(region, summonerId)
    match_history = json.loads(match_history.text)["matches"]
    match_ids = [x["matchId"] for x in match_history]
    matchId = match_ids[len(match_ids) - 1]
    print matchId
    ## download last match
    match = Match(json.loads(rawpi.get_match(region=region, matchId=matchId, includeTimeline=True).text), summonerId)
    ## load pipeline
    wp = WinProbabilityPipeline()
    wp.from_file("../model-serialized/wp-pipeline.pkl")
    timestamps = match.timestamps
    winprob = wp.predict(match.match, match.teamId)
    plot_winprobability(timestamps, winprob)
    print match.win
    call(["open", "winprob.png"])


if __name__=="__main__":
    main(sys.argv)
