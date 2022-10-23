'''
Created on Apr 2, 2021

@author: Josef
'''
from datetime import datetime, timedelta
import logging

from calculations.calculations import combine_stats
from main.gamemodes import Gamemode

class BridgeData():
    def __init__(self, uuid, bridgestats, initdays):
        self.uuid = uuid
        self.games = {}
        self.daily_data = []
        self.gamemode = Gamemode.BRIDGE
        
        self.initstats = {"days" : initdays, **bridgestats}
        self.initdays = initdays
        
        self.mostrecentstats = self.initstats
        self.laststats = self.initstats
        self.overwriteindex = -1
    
    def get_recent_stats(self):
        return self.mostrecentwins, self.mostrecentlosses
    
    def get_all(self, days):
        data = self.get_data()
        stats = self.get_stats(days)
        return {"initstats" : self.initstats, "Data Collected" : {"wins": data[0], "losses": data[1], "goals": data[2]}, 
                "Calculations": {"accuracy": self.get_accuracy(), "mostmap": self.get_most_map(), "Timepergame": self.get_timepergame(),
                                 "Days": days, "Dailywins": stats[0], "Dailylosses": stats[1], "AverageWLR": stats[0]/stats[1]}}
           
    def get_data(self):
        wins = losses = goals = 0
        
        for data in self.daily_data:
            wins += data["wins"]
            losses += data["losses"]
            goals += data["goals"]
        
        for _, game in self.games.items():
            result = game["result"]
            if result is None:
                continue
            
            goals += game["goals"]
            
            if result is True:
                wins += 1
            else:
                losses += 1
        
        return wins, losses, goals
    
    def get_games(self):
        games = []
        for data in self.daily_data:
            for game in data["games"]:
                games.append(game)
                
        return games
    
    def get_accuracy(self):
        def get_percent(length):
            if length == 0:
                return 1
            elif length >= 100:
                return 75
            
            return float(len(self.daily_data) * 0.75)
            
        days = get_percent(len(self.daily_data))
        games = get_percent(len(self.get_games()))
        return int(round((days + games) / 2, 0))
    
    def get_stats(self, days):
        stats = self.get_data()
        return *combine_stats(self.initdays, self.initstats["wins"], self.initstats["losses"], days, stats[0], stats[1]), self.get_timepergame()
    
    def get_timepergame(self):
        def count_games(games):
            totaltime = 0
            totalgames = 0
            for _, game in games.items():
                totaltime += game["length"]
                totalgames += 1
            return totaltime, totalgames
        
        totaltime, totalgames = count_games(self.games) 
        for data in self.daily_data:
            result = count_games(data["games"])
            totaltime += result[0]
            totalgames += result[1]
        
        if totalgames == 0 or totaltime == 0:
            return False
        return totaltime / totalgames
    
    def get_most_map(self):
        def count_games(games):
            playedmaps = {}
            for _, game in games.items():
                bridgemap = game["map"]
                if bridgemap in playedmaps:
                    playedmaps[bridgemap] = playedmaps[bridgemap] + 1
                else:
                    playedmaps[bridgemap] = 1
            return playedmaps
        
        playedmaps = count_games(self.games)
        for data in self.daily_data:
            playedmaps = {**count_games(data["games"]), **playedmaps}
                    
        maxmap = None
        maxplayed = 0
        for bridgemap, played in playedmaps.items():
            if played >= maxplayed:
                maxplayed = played
                maxmap = bridgemap
        
        return maxmap
    
    def save_stats(self, bridgestats):
        data = {"wins" : bridgestats["wins"] - self.laststats["wins"], "losses" : bridgestats["losses"] - self.laststats["losses"], "goals" : bridgestats["goals"] - self.laststats["goals"], 
                "time" : datetime.today(), "games" : self.games}
        logging.info("Bridge Stats stored for " + self.uuid + ": " + str(data))
        if self.overwriteindex != -1 and self.overwriteindex < 365:
            self.daily_data[self.overwriteindex] = data
            self.overwriteindex += 1
        elif len(self.daily_data) >= 365 or self.overwriteindex >= 365:
            self.daily_data[0] = (data)
            self.overwriteindex = 1
        else:
            self.daily_data.append(data)
        
        self.daily_reset(bridgestats)
    
    def daily_reset(self, bridgestats):
        self.games = {}
        self.laststats = bridgestats
           
    def save_games(self, stats, games):
        gameammount = len(games)
        gameresult = None
        
        if ((stats["wins"] - self.mostrecentstats["wins"]) + (stats["losses"] - self.mostrecentstats["losses"])) == gameammount:
            if (stats["wins"] - self.mostrecentstats["wins"]) == 0:
                gameresult = False
            else:
                gameresult = True
        
        length = 0
        for date, game in games.items():
            length += game["length"]
            
            game["result"] = gameresult
            if gameresult != None:
                game["goals"] = (stats["goals"] - self.mostrecentstats["goals"]) / gameammount
                
            self.games[date] = game
            
        fields = {"Goals": (stats["goals"] - self.mostrecentstats["goals"]), "Length": str(timedelta(seconds=int(length)))}
            
        if gameammount > 1:
            fields["Wins"] = (stats["wins"] - self.mostrecentstats["wins"])
            fields["Losses"] = (stats["losses"] - self.mostrecentstats["losses"])
        else:
            fields["Won"] = gameresult
            
        self.mostrecentstats = stats
        
        if len(games) < 1:
            return None
        
        logging.info(f'New Bridge game(s) found for {self.uuid}: {str(games)}') 
        if gameresult is None:
            return False
        return fields
        
    def is_gametype(self, game):
        if game["gameType"] != "DUELS":
            return False
             
        if not game["mode"].startswith("BRIDGE"):
            return False
        
        return True
    