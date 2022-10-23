'''
Created on May 7, 2021

@author: Josef
'''
from calculations.calculations import combine_stats, combine_stat
from main.game_data import GameData
from main.gamemodes import Gamemode

class SkywarsData(GameData):
    def __init__(self, *args, **kwargs):
        gamemode = Gamemode.SKYWARS
        gametype = 'SKYWARS'
        datakeys = (('kills', 'Kills'),)
        modes = {"solo_insane": "Solo Skywars - Insane", "solo_normal": "Solo Skywars - Normal", "ranked_normal": "Ranked Skywars", "mega_normal": "Mega Skywars", 
                 "team_insane": "Skywars Doubles - Insane", "team_normal": "Skywars Doubles - Normal"}
        extrakeys = {"solo_insane": (('exp', 'Experience'), ('souls', 'Souls')), "solo_normal": (('exp', 'Experience'), ('souls', 'Souls')), 
                     "team_insane": (('exp', 'Experience'), ('souls', 'Souls')), "team_normal": (('exp', 'Experience'), ('souls', 'Souls'))}
        hiddenkeys = {"team_insane": (('deaths', 'Deaths'),), "team_normal": (('deaths', 'Deaths'),)}
        super().__init__(gamemode, gametype, datakeys, extrakeys, hiddenkeys, modes, *args, **kwargs)
    
    def get_all(self, days):
        data = self.get_data(neat=True)
        stats = self.get_stats(days)
        return {"initstats" : self.initstats, "Data Collected": data, 
                "Calculations": {"Accuracy": self.get_accuracy(), "MostMap": self.get_most_map(), "TimePerGame": stats[7],
                                 "Days": days, "DailyWins": stats[0], "DailyLosses": stats[1], "AverageWLR": stats[0]/stats[1],
                                 "DailyKills": stats[2], "DailyDeaths": stats[3], "KillsPerGame": stats[4], "DeathsPerGame": stats[5], "DailyEXP": stats[6]}}
    def get_stats(self, days):
        data = self.get_data()
        dailywins, dailylosses = combine_stats(self.initdays, self.initstats["overall_wins"], self.initstats["overall_losses"], days, data["wins"], data["losses"])
        dailykills, dailydeaths = combine_stats(self.initdays, self.initstats["overall_kills"], self.initstats["overall_deaths"], days, data["kills"], data["deaths"])
        killsgame, deathsgame = combine_stats(self.initstats["overall_wins"] + self.initstats["overall_losses"], self.initstats["overall_kills"], self.initstats["overall_deaths"], 
                                              data["wins"] + data["losses"], data["kills"], data["deaths"])
        dailyexp = combine_stat(self.initdays, self.initstats["overall_exp"], days, data["exp"])
        return dailywins, dailylosses, dailykills, dailydeaths, killsgame, deathsgame, dailyexp, self.get_timepergame()
