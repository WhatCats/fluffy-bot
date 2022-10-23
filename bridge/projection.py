'''
Created on Apr 2, 2021

@author: Josef
'''
from calculations.calculations import check_ratiogoal, calc_ratio_goal, \
    check_number, calc_wins_goal, calc_time_goal
from calculations.format import format_time, format_ratio, calc_date
from main.gamemodes import Gamemode

gm = Gamemode.BRIDGE
def calculate_projection(statsdata, currentdata, wins=None, wlr=None, days=None):
    dailywins, dailylosses, gametimeagame = statsdata.get_stats(gm)
    bridgedata = currentdata.pop(gm)
    currentwins, currentlosses = bridgedata["overall_wins"], bridgedata["overall_losses"]

    wlr_goal = wins_goal = time_goal = {"time" : -1}
    if not wlr is None:
        result = check_ratiogoal(dailywins, dailylosses, currentwins, currentlosses, wlr)
        if result is False:
            return f"The value `{wlr}` is a Invalid W/L."
        
        wlr_goal = calc_ratio_goal(wlr, currentlosses, currentwins, dailywins, dailylosses, gametimeagame)
        wlr_goal = wrap_projection(*wlr_goal)
        wlr_goal["goal"] = f'at a {round(wlr, 1)} W/L'
    if not wins is None:
        result = check_number(wins)
        if result is False:
            return f"The value `{wins}` is a Invalid amount of wins."
        
        wins_goal = calc_wins_goal(wins, currentlosses, currentwins, dailywins, dailylosses, gametimeagame)
        wins_goal = wrap_projection(*wins_goal)
        wins_goal["goal"] = f'at {int(round(wins, 0))} wins'
    if not days is None:
        result = check_number(days)
        if result is False:
            return f"The value `{days}` is a Invalid amount of days."
        
        time_goal = calc_time_goal(days, currentlosses, currentwins, dailywins, dailylosses, gametimeagame)
        time_goal = wrap_projection(*time_goal)
        time_goal["goal"] = f'in {days} days'
    
    overall = {wlr_goal["time"] : wlr_goal, wins_goal["time"] : wins_goal, time_goal["time"] : time_goal}
    extra = wrap_extra_data(dailywins, dailylosses, gametimeagame, statsdata.get_most_map(gm), statsdata.get_accuracy(gm))
    
    return {**overall[max(overall.keys())], **currentdata, **extra, "gamemode" : gm}

def wrap_extra_data(dailywins, dailylosses, gametimeagame, mostmap, accuracy): 
    gametimeagame = format_time(gametimeagame)
    dailywlr = format_ratio(dailywins, dailylosses)
        
    return {"dailywins" : round(dailywins, 1), "dailylosses" : round(dailylosses, 1), 
            "gametimeagame" : gametimeagame, "dailygames" : round(dailywins + dailylosses, 1), 
            "dailywlr" : dailywlr, "mostmap" : mostmap, "accuracy" : str(accuracy) + "%"}
    
def wrap_projection(wins, losses, wlr, time, gametime):
    date = calc_date(time)
    return {"wins" : int(wins), "losses" : int(losses), "wlr" : round(wlr, 1), "time" : time, "date" : date, "gametime" : format_time(gametime)}
