import sys
sys.path.append('/Users/chris/Projects/lol/lib/')
import rawpi
import json
from model import WinProbabilityPipeline
from match import Match
from visualize import plot_winprobability, get_winprobability_string_png
from events import summarize_important_events
from subprocess import call




def main(argvs):
    region = argvs[1]
    print region
    ## take summonerId
    summonerName = argvs[2]
    print summonerName
    ## get summonerID
    match = get_last_match(region, summonerName)
    get_last_match_winprob(match, console=True)

def get_last_match(region, summonerName):
    try:
        summonerId = json.loads(rawpi.get_summoner_by_name(region, summonerName).text)[summonerName]["id"]
    except: 
        print "Could not find summoner"
    print summonerId

    ## get last ten matches
    match_history = rawpi.get_matchhistory(region, summonerId)
    match_history = json.loads(match_history.text)["matches"]
    match_ids = [x["matchId"] for x in match_history]

    matchId = match_ids[len(match_ids) - 1]
    print matchId
    ## download last match
    match = Match(json.loads(rawpi.get_match(region=region, matchId=matchId, includeTimeline=True).text), summonerId)
    return match

def get_last_match_winprob(match, filename="winprob.png", console=False):
    ## load pipeline
    wp = WinProbabilityPipeline()
    wp.from_file("/Users/chris/Projects/lol/projects/winprob/model-serialized/wp-pipeline.pkl")
    timestamps = match.timestamps
    winprob = wp.predict(match.match, match.teamId)
    if console:
        plot_winprobability(timestamps, winprob, filename=filename)
        print match.win
        match.set_winprob(winprob)
        print summarize_important_events(match)
        print match.get_participant_summary()
        call(["open", "winprob.png"])
    else:
        return get_winprobability_string_png(timestamps, winprob)


if __name__=="__main__":
    main(sys.argv)
