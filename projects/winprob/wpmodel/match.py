"""
Class to represent one match
"""



class Match():
""" Class for league of legends from the view of a single player"""

    def __init__(self, match_dict, summonerId):
        """ Extracts the first infos of the match
        Keyword arguments:
        match_dict - match of type dictionary containing the match 
        summonerId - id of type int for the summoner
        """
        self.match = match_json
        self.summonerId = summonerId
        
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


    def get_victory(self): 
        return self.win
