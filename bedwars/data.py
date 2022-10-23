'''
Created on Apr 8, 2021

@author: Josef
'''
from calculations.calculations import combine_stats, combine_stat
from main.gamemodes import Gamemode
from main.game_data import GameData

class BedwarsData(GameData):
    def __init__(self, *args, **kwargs):
        gamemode = Gamemode.BEDWARS
        gametype = 'BEDWARS'
        datakeys = (('final_kills', 'Final Kills'), ('final_deaths', 'Final Deaths'), ('exp', 'Experience'), ('beds', 'Beds'))
        modes = {"eight_one": "Solo Bedwars", "eight_two": "Bedwars Doubles", "four_three": "Bedwars Threes", "four_four": "Bedwars Fours", "two_four": "Bedwars 4v4"}
        extrakeys = {}
        hiddenkeys = {}
        
        super().__init__(gamemode, gametype, datakeys, extrakeys, hiddenkeys, modes, *args, **kwargs)
    
    def get_all(self, days):
        data = self.get_data(neat=True)
        stats = self.get_stats(days)
        return {"initstats" : self.initstats, "Data Collected" : data, 
                "Calculations": {"Accuracy": self.get_accuracy(), "MostMap": self.get_most_map(), "TimePerGame": stats[9],
                                 "Days": days, "DailyWins": stats[0], "DailyLosses": stats[1], "AverageWLR": stats[0]/stats[1],
                                 "DailyFinalKills": stats[2], "DailyFinalDeaths": stats[3], "AverageFKDR": stats[2]/stats[3],
                                 "FinalKillPerGame": stats[4], "FinalDeathsPerGame": stats[5], "DailyEXP": stats[6],
                                 "DailyBeds": stats[7], "BedsPerGame": stats[8]}}
    
    def get_stats(self, days):
        data = self.get_data()
        dailywins, dailylosses = combine_stats(self.initdays, self.initstats["overall_wins"], self.initstats["overall_losses"], days, data['wins'], data['losses'])
        dailyfkills, dailyfdeaths = combine_stats(self.initdays, self.initstats["overall_final_kills"], self.initstats["overall_final_deaths"], days, data["final_kills"], data["final_deaths"])
        fkillsgame, fdeathsgame = combine_stats(self.initstats["overall_wins"] + self.initstats["overall_losses"], self.initstats["overall_final_kills"], self.initstats["overall_final_deaths"], 
                                                data['wins'] + data['losses'], data["final_kills"], data["final_deaths"])
        dailybeds = combine_stat(self.initdays, self.initstats["overall_beds"], days, data["beds"])
        bedsgame = combine_stat(self.initstats["overall_wins"] + self.initstats["overall_losses"], self.initstats["overall_beds"], data['wins'] + data['losses'], data["beds"])
        dailyexp = combine_stat(self.initdays, self.initstats["exp"], days, data['exp'])
        return dailywins, dailylosses, dailyfkills, dailyfdeaths, fkillsgame, fdeathsgame, dailyexp, dailybeds, bedsgame, self.get_timepergame()
    