'''
Created on June 16, 2021

@author: Josef
'''
def get_extragamekeys(gamedata, stats):  
    #Extra & Hidden keys in a diffrent format
    def unpack(checkkeys):  
        extrakeys = {}
        extrakeytimes = {}       
        for gamemode, keys in checkkeys.items():
            gamemode = gamemode.lower()
            extradata = {}
            for (key, _) in keys:
                if key in stats:
                    if key in extrakeytimes:
                        extrakeytimes[key] += 1
                    else:
                        extrakeytimes[key] = 1
                    extradata[key] = stats[key]
            extrakeys[gamemode] = extradata 
        return extrakeys, extrakeytimes
        
        
    return unpack(gamedata.extrakeys) + unpack(gamedata.hiddenkeys)
    
def fill_globals(gamedata, stats): 
    #Supplys data to the daily savers
    globalkeys = {}       
    for (key, _) in gamedata.datakeys:
        if key in stats:
            stats[f'overall_{key}'] = stats[key]
            globalkeys[key] = stats[key]
            
    extrakeys, extrakeytimes, hiddenkeys, hiddenkeytimes = get_extragamekeys(gamedata, stats)
    for gamemode, _ in gamedata.modes.items(): 
        gamemode = gamemode.lower()    
        for gkey, gvalue in globalkeys.items():
            stats[f'{gamemode}_{gkey}'] = (gvalue / len(gamedata.modes))
                
        if gamemode in extrakeys:
            for gkey, gvalue in extrakeys[gamemode].items():
                stats[f'{gamemode}_{gkey}'] = (gvalue / extrakeytimes[gkey])
        
        if gamemode in hiddenkeys:
            for gkey, gvalue in hiddenkeys[gamemode].items():
                stats[f'{gamemode}_{gkey}'] = (gvalue / hiddenkeytimes[gkey])
        
    for dictionary in list(extrakeys.values()):
        for gkey, gvalue in dictionary.items():
            stats[f'overall_{gkey}'] = gvalue
            
    for dictionary in list(hiddenkeys.values()):
        for gkey, gvalue in dictionary.items():
            stats[f'overall_{gkey}'] = gvalue
    
    return stats

def get_extrakeys(gamedata, mode='overall'):
    #Extrakeys relevant for gamemode
    keys = {}
    for (gamemode, keyset) in gamedata.extrakeys.items():
        if gamemode.lower() == mode or mode == 'overall':
            for (check, neat) in keyset:
                keys[f'{mode}_{check}'] = neat
    return keys
    
def get_hiddenkeys(gamedata, mode='overall'):
    #Hiddenkeys relevant for gamemode
    keys = {}
    for (gamemode, keyset) in gamedata.hiddenkeys.items():
        if gamemode.lower() == mode or mode == 'overall':
            for (check, neat) in keyset:
                keys[f'{mode}_{check}'] = neat
    return keys
                       
def all_keys(gamedata, mode='overall'):
    #All keys relavent for gamemode
    allkeys = {}
    if mode == 'overall':
        for gamemode in [*list(gamedata.modes.keys()), 'overall']: 
            gamemode = gamemode.lower()   
             
            datakeys, extrakeys, hiddenkeys = get_keys(gamedata, gamemode)
            allkeys.update(datakeys)
            allkeys.update(extrakeys)
            allkeys.update(hiddenkeys)
    else:
        datakeys, extrakeys, hiddenkeys = get_keys(gamedata, mode)
        allkeys.update(datakeys)
        allkeys.update(extrakeys)
        allkeys.update(hiddenkeys)
            
    return allkeys
    
def get_keys(gamedata, mode='overall'):
    #All keys relevant for gamemode in diffrent format
    datakeys = {}
    for (check, neat) in gamedata.datakeys:
        datakeys[f'{mode}_{check}'] = neat
        
    return datakeys, get_extrakeys(gamedata, mode), get_hiddenkeys(gamedata, mode)

def combine_stats(gamedata, oldstats, newstats):
    #Used to combine mostrecentstats with raw stats check
    newglobalkeys = {}       
    for (key, _) in gamedata.datakeys:
        if key in newstats:
            newstats[f'overall_{key}'] = newstats[key]
            newglobalkeys[key] = newstats[key]
           
    oldglobalkeys = {}       
    for (key, _) in gamedata.datakeys:
        if key in oldstats:
            oldglobalkeys[key] = oldstats[key]
            
    newextrakeys, newextrakeystimes, newhiddenkeys, newhiddenkeystimes = get_extragamekeys(gamedata, newstats)
    oldextrakeys, _, oldhiddenkeys, _ = get_extragamekeys(gamedata, oldstats)
    
    for gamemode, _ in gamedata.modes.items(): 
        gamemode = gamemode.lower()    
        
        def handle(newkeydictionary, oldkeydictionary, gamemodes):
            for gkey, gvalue in newkeydictionary.items():
                key = f'{gamemode}_{gkey}'
                if key in oldkeydictionary and not key in newkeydictionary:
                    newstats[key] = oldkeydictionary[key]
                else:
                    gvalue /= gamemodes[gkey] if isinstance(gamemodes, dict) else gamemodes
                    newstats[key] = gvalue
                    
        handle(newglobalkeys, oldglobalkeys, len(gamedata.modes))
        
        if gamemode in newextrakeys:
            if gamemode in oldextrakeys:
                handle(newextrakeys[gamemode], oldextrakeys[gamemode], newextrakeystimes)
            else:
                handle(newextrakeys[gamemode], {}, newextrakeystimes)
        
        if gamemode in newhiddenkeys:
            if gamemode in oldhiddenkeys:        
                handle(newhiddenkeys[gamemode], oldhiddenkeys[gamemode], newhiddenkeystimes)
            else:
                handle(newhiddenkeys[gamemode], {}, newhiddenkeystimes)
    
    for dictionary in [*list(newextrakeys.values()), *list(newhiddenkeys.values())]:
        for gkey, gvalue in dictionary.items():
            if not f'overall_{gkey}' in newstats:
                newstats[f'overall_{gkey}'] = gvalue
    
    return newstats
    

def extract(gamedata, mode='overall', neat=False):
    #get collected data
    allkeys = all_keys(gamedata, mode)
    wins = losses = 0
    datas = {key:0 for key in list(allkeys.keys())}
        
    for data in gamedata.daily_data:
        wins += data[f"{mode}_wins"]
        losses += data[f"{mode}_losses"]
        for key in allkeys:
            datas[key] += data[key] if key in data else 0
        
    for _, game in gamedata.games.items(): 
        result = game["result"]
        gamemode = game["mode"]
        if (gamemode != mode) and mode != 'overall':
            continue
            
        for key in list(allkeys.keys()):
            datas[key] += game[key] if key in game else 0
                    
        if result is True:
            wins += 1
        else:
            losses += 1 
                
    if neat:
        newdatas = {}
        for key in list(datas.keys()):
            neatkey = allkeys[key]
            newdatas[neatkey] = datas[key]
            newdatas["Wins"], newdatas["Losses"] = wins, losses
        return newdatas
        
    datas["wins"], datas["losses"] = wins, losses    
    return datas

def get_gamemodegames(games):
    #games in a diffrent format
    gamemodegames = {}
        
    for date, game in games.items():
        gamemode = game["mode"]
        if gamemode in gamemodegames:
            gamemodegames[gamemode].append((date, game))
        else:
            gamemodegames[gamemode] = [(date, game),]
    return gamemodegames

def fill_globals_games(gamedata, stats, games):
    mostrecentstats = gamedata.mostrecentstats
    gamemodegames = get_gamemodegames(games)
        
    globalkeys = {}       
    for (key, _) in gamedata.datakeys:
        if key in stats:
            stats[f'overall_{key}'] = stats[key]
            globalkeys[key] = stats[key] - mostrecentstats[key]
        
    extrakeys, extrakeytimes, hiddenkeys, hiddenkeytimes = get_extragamekeys(gamedata, stats)
    gameammount = len(games)
    for gamemode, games in gamemodegames.items():
        gamemode = gamemode.lower()
           
        for gkey, gvalue in globalkeys.items():
            stats[f'{gamemode}_{gkey}'] = (gvalue / gameammount) * len(games) + mostrecentstats[f'{gamemode}_{gkey}']
         
        if gamemode in extrakeys:
            for gkey, gvalue in extrakeys[gamemode].items():
                stats[f'{gamemode}_{gkey}'] = (gvalue / extrakeytimes[gkey]) * len(games) + mostrecentstats[f'{gamemode}_{gkey}']
           
        if gamemode in hiddenkeys:
            for gkey, gvalue in hiddenkeys[gamemode].items():
                stats[f'{gamemode}_{gkey}'] = (gvalue / hiddenkeytimes[gkey]) * len(games) + mostrecentstats[f'{gamemode}_{gkey}']     
    
    for dictionary in [*list(extrakeys.values()), *list(hiddenkeys.values())]:
        for gkey, gvalue in dictionary.items():
            if not f'overall_{gkey}' in stats:
                stats[f'overall_{gkey}'] = gvalue
                