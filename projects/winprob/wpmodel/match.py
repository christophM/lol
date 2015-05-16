"""
Class to represent one match
"""
import datetime
import rawpi
import json


class Match():
    """ Class for league of legends from the view of a single player"""

    def __init__(self, match_dict, summonerName=None):
        """ Extracts the first infos of the match
        Keyword arguments:
        match_dict - match of type dictionary containing the match 
        summonerName - summoner name of type string for the summoner
        """
        self.match = match_dict
        ## if summonerName not provided, then take the first summoner from the game
        self.summonerName = summonerName if summonerName is not None else self.match["participantIdentities"][0]["player"]["summonerName"]
        self.timestamps = [x["timestamp"] / 60000 for x in self.match["timeline"]["frames"]]
        self.durance = max(self.timestamps)
        
        ## MatchId
        self.matchId = self.match["matchId"]
        ## Extract id of summoner for this game
        self.participantId = filter(lambda x: x["player"]["summonerName"].lower() == self.summonerName.lower(), 
                                    self.match["participantIdentities"])[0]["participantId"]
        ## Extract team id of summoner for this game
        self.teamId = filter(lambda x: x["participantId"] == self.participantId, 
                             self.match["participants"])[0]["teamId"]
        ## Extract ids of team member
        self.team_members = [x["participantId"] for x in self.match["participants"] if  x["teamId"] == self.teamId]
        ## Extract if player won
        self.win = filter(lambda x: x["teamId"] == self.teamId, 
                          self.match["teams"])[0]["winner"]
        self.winprob = None
        ## Ugly hacked
        self.date = datetime.datetime.fromtimestamp(self.match["matchCreation"] / 1000)
        self.region = self.match["region"].lower()


    def get_victory(self): 
        return self.win
    
    def set_winprob(self, winprob):
        """Add the win probability for the match"""
        if len(winprob) != len(self.timestamps):
            raise Exception("Win probability array must match the timeline")
        self.winprob = winprob

    def get_winprob(self):
        """ Get the win probability path for the match"""
        if self.winprob is None:
            raise Exception("Must set win probability first")

        return self.winprob

    def get_winprob_dataframe(self):
        """ Get the win probability path for the match
            This will return a list of dict """
        if self.winprob is None:
            raise Exception("Must set win probability first")
        
        timeline = []
        for timestamp in self.timestamps[1:]:
            if timestamp == 1:
                winprob_before = 0.5
            else:
                winprob_before = self.winprob[timestamp - 2]
            timeline.append({"timestamp": timestamp, 
                             "winprob_now": self.winprob[timestamp - 1],
                             "winprob_before": winprob_before})
        return timeline

        
    def get_participant_summary(self, participantId=None):
        """Extract the stats for the participant"""
        if not participantId:
            participantId = self.participantId
        player = filter(lambda x: x["participantId"] == self.participantId, self.match["participants"])[0]
        stats = player["stats"]
        champ = rawpi.get_champion_list_by_id(self.region, player["championId"])
        stats.setdefault("champion", json.loads(champ.text)["name"])
        ## kills, deaths, assists, champion name, gold, minion kills,  role (nice-to-have)
        return stats
