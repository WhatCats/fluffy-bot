'''
Created on May 7, 2021

@author: Josef
'''
from calculations.calculations import combine_stats, combine_stat
from main.game_data import GameData
from main.gamemodes import Gamemode
from duels.util import get_modes

class DuelsData(GameData):
    def __init__(self, *args, **kwargs):
        gamemode = Gamemode.DUELS
        gametype = 'DUELS'
        datakeys = ()
        modes = {
            "uhc_duel": "UHC Duels", "uhc_doubles": "UHC Doubles", "uhc_four": "UHC 4v4", "bridge_duel": "Solo Bridge", "bridge_doubles": "Bridge Doubles", "bridge_threes": "Bridge Threes",
            "bridge_2v2v2v2": "Bridge 2v2v2v2", "bridge_3v3v3v3": "Bridge 3v3v3v3", "bridge_four": "Bridge 4v4", "capture_threes": "Bridge CTF", "classic_duel": "Classic Duels", "combo_duel": "Combo Duels", 
            "bow_duel": "Bow Duels", "potion_duel": "Nodebuff Duels", "op_duel": "OP Duels", "op_doubles": "OP Doubles", "bowspleef_duel": "Bowspleef Duels", 
            "sw_duel": "Skywars Duels", "sw_doubles": "Skywars Doubles", "sumo_duel": "Sumo Duels", "mw_duel": "Mega Walls Duels", "mw_doubles": "Mega Walls Doubles",
            "blitz_duel": "Blitz Duels", "duel_arena": "Duel Arena", "parkour_eight": "Hypixel Parkour", "boxing_duel": "Hypixel Boxing"
        }
        extrakeys = {
            "bridge_duel": (('goals', 'Goals'),), 
            "bridge_doubles": (('goals', 'Goals'),), 
            "bridge_2v2v2v2": (('goals', 'Goals'),), 
            "bridge_3v3v3v3": (('goals', 'Goals'),), 
            "bridge_threes": (('goals', 'Goals'),),
            "bridge_four": (('goals', 'Goals'),), 
            "capture_threes": (('goals', 'Goals'), ('captures', 'Captures'))
            "boxing_duel": (('melee_hits', 'Melee hits'),) 
        }
        hiddenkeys = {}
        super().__init__(gamemode, gametype, datakeys, extrakeys, hiddenkeys, modes, *args, **kwargs)
    
    def get_all(self, days):
        data = self.get_data(neat=True)
        stats = self.get_stats(days)
        return {"initstats" : self.initstats, "Data Collected" : data, 
                "Calculations": {"Accuracy": self.get_accuracy(), "MostMap": self.get_most_map(), "TimePerGame": stats[3],
                                 "Days": days, "DailyWins": stats[0], "DailyLosses": stats[1], "DailyGoals": stats[2]}}
    
    def get_stats(self, days, gametype='overall'):
        modes = get_modes(gametype)
        wins = losses = initwins = initlosses = 0
        for mode in modes:
            data = self.get_data(mode=mode.lower())
            wins += data['wins']
            losses += data['losses']
            initwins += self.initstats[f"{mode}_wins"]
            initlosses += self.initstats[f"{mode}_losses"]
        
        data = self.get_data()
        dailywins, dailylosses = combine_stats(self.initdays, initwins, initlosses, days, wins, losses)
        dailygoals = combine_stat(self.initdays, self.initstats[f"overall_goals"], days, data[f'goals']) if gametype == "The Bridge" else 0
        return dailywins, dailylosses, dailygoals, self.get_timepergame()
    