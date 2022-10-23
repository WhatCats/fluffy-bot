'''
Created on 10 Mar 2021

@author: Josef
'''
"""

def calculate_virgames(dailywins, dailylosses, currentwins, currentlosses, gametimeagame, games=None, gametime=None):
    extra = wrap_extra_data(dailywins, dailylosses, gametimeagame)
   
    if not games is None:
        if games <= 0 or games > 999999:
            return "Invalid ammount of games."
        
        result = calculate_games(dailywins, dailylosses, currentwins, currentlosses, games, f'in {games} games')  
        return {**result, **extra}
    
    if not gametime is None:
        if gametime < (gametimeagame / 60) or gametime > 999999:
            return "Invalid ammount of gametime."
        
        if gametimeagame is False:
            return "Not enough data for calculation."
        
        games = int(math.ceil(gametime / (gametimeagame/60)))
        result = calculate_games(dailywins, dailylosses, currentwins, currentlosses, games, f'after {gametime} minutes gametime')  
        
    return {**result, **extra}
        
def calculate_games(dailywins, dailylosses, currentwins, currentlosses, games, virstats):
    wins = games / ((dailywins / dailylosses) + 1)
    losses = games - wins
    wlr = (currentwins + wins) / (currentlosses + losses)
    time = int(math.ceil(games / (dailywins + dailylosses), 1))
    
    return wraper(wins, losses, wlr, time, virstats)

"""
    
def check_ratiogoal(dailyterm1, dailyterm2, currentterm1, currentterm2, ratio):
    if ratio <= (currentterm1/currentterm2) or ratio > (dailyterm1/dailyterm2):
        return False
        
    return True

def calc_gametime(games, gametimeagame):
    if gametimeagame is False:
        return "N/A"
     
    return gametimeagame * (games)  
   
def calc_ratio_goal(ratiogoal, currentterm2, currentterm1, dailyterm1, dailyterm2, gametimeagame):  
    if (dailyterm1 - (ratiogoal * dailyterm2)) > 0:
        time = (((ratiogoal * currentterm2) - currentterm1) / (dailyterm1 - (ratiogoal * dailyterm2)))
    else:
        time = ((ratiogoal * currentterm2) - currentterm1)
        
    term1 = dailyterm1 * time
    term2 = dailyterm2 * time
    games = term1 + term2 + currentterm1 + currentterm2
    
    return term1 + currentterm1, term2 + currentterm2, (term1 + currentterm1) / (term2 + currentterm2), time, calc_gametime(games, gametimeagame)

def calc_wins_goal(term1goal, currentterm2, currentterm1, dailyterm1, dailyterm2, gametimeagame):
    time = (term1goal - currentterm1) / dailyterm1
    term2 = time * dailyterm2
    ratio = (term1goal) / (term2 + currentterm2)
    
    games = term1goal + term2 + currentterm1 + currentterm2
    
    return term1goal, term2 + currentterm2, ratio, time, calc_gametime(games, gametimeagame)

def calc_time_goal(term1goal, currentterm2, currentterm1, dailyterm1, dailyterm2, gametimeagame):
    wins = dailyterm1 * term1goal
    losses = dailyterm2 * term1goal
    wlr = (wins + currentterm1) / (losses + currentterm2)
    games = (wins + currentterm1 + losses + currentterm2)
    
    return wins + currentterm1, losses + currentterm2, wlr, term1goal, calc_gametime(games, gametimeagame)
    
def check_number(num, minnum=0, maxnum=999999):
    if num <= minnum or num > maxnum:
        return False
    return True

def combine_stats(initdays, initterm1, initterm2, days, term1, term2):
        overwriteat = 100
        
        time1, time2 = initdays, days
        wins1, losses1 = initterm1, initterm2
        wins2, losses2 = term1, term2
    
        if time2 + time1 <= overwriteat:
            dailywins = (wins1 + wins2) / (time1 + time2)
            dailylosses = (losses1 + losses2) / (time1 + time2)
        elif time2 >= overwriteat:
            dailywins = wins2 / time2
            dailylosses = losses2 / time2
        else:
            timefromtime1 = overwriteat - time2
            newwins1 = (wins1 / time1) * timefromtime1
            newlosses1 = (losses1 / time1) * timefromtime1
        
            gamesperday = (newwins1 + newlosses1 + wins2 + losses2) / 100
            wlr = (newwins1 + wins2) / (newlosses1 + losses2)
        
            dailylosses = gamesperday / (wlr + 1)
            dailywins = dailylosses * wlr
            
        return dailywins, dailylosses
    
def combine_stat(initdays, initstat, days, stat):
        overwriteat = 100
        
        if initdays + days <= overwriteat:
            return (initstat + stat) / (initdays + days)
        elif days >= overwriteat:
            return stat / days
        else:
            timefromtime1 = overwriteat - days
            newstat = (initstat / initdays) * timefromtime1
            return (newstat + stat) / overwriteat
    