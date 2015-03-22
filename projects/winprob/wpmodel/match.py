"""
Class to represent one match
"""



class Match():
    """ Class for league of legends from the view of a single player"""

    def __init__(self, match_dict, summonerId=None):
        """ Extracts the first infos of the match
        Keyword arguments:
        match_dict - match of type dictionary containing the match 
        summonerId - id of type int for the summoner
        """
        self.match = match_dict
        ## if summonerId not provided, then take the first summoner from the game
        self.summonerId = summonerId if summonerId is not None else self.match["participantIdentities"][0]["player"]["summonerId"]
        self.timestamps = [x["timestamp"] / 60000 for x in self.match["timeline"]["frames"]]
        self.durance = max(self.timestamps)
        
        ## MatchId
        self.matchId = self.match["matchId"]
        ## Extract id of summoner for this game
        self.participantId = filter(lambda x: x["player"]["summonerId"] == self.summonerId, 
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


    def get_victory(self): 
        return self.win
    
    def set_winprob(self, winprob):
        if len(winprob) != len(self.timestamps):
            raise Exception("Win probability array must match the timeline")
        self.winprob = winprob

    def get_winprob(self):
        if self.winprob is None:
            raise Exception("Must set win probability first")

        return self.winprob
