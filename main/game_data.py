'''
Created on June 18, 2021

@author: Josef
'''
import asyncio
from datetime import datetime, timedelta, timezone
import logging
import re
from time import sleep
from typing import Tuple, Union, Dict

from main.gamelogger import log_game


Modes = Dict[str, str]
Key = Tuple[str, str]
Keys = Tuple[Key, ...]
GameKeys = Dict[str, Keys]

class GameData():   
    def __init__(self, gamemode, gametype, datakeys, extrakeys, hiddenkeys, modes, uuid, *args, **kwargs):
        self.uuid = uuid
        self.gamemode = gamemode
        self.gametype = gametype
        
        self.modes = modes
        self.datakeys = datakeys
        
        #self.extrakeys =  self.hiddenkeys = {'GAME_MODE': (('checkkey', 'neatkey'),)}
        self.extrakeys = extrakeys
        self.hiddenkeys = hiddenkeys
        
        
        if 'restore' in kwargs:
            self.rebuild(kwargs['restore']) 
        else:
            self.new(*args, **kwargs)
        
    def new(self, initdays, stats):
        self.initdays = initdays
        self.overwriteindex = 0
        
        self.dailydata = []
        self.lastend = datetime.now(timezone.utc).timestamp()
        
        self.lasthandled = -1
        self.games = {}
        
        self.expand(stats)
        self.initstats = {"days": initdays, **stats}
        self.mostrecentstats = self.initstats
        self.laststats = self.initstats
    
    def rebuild(self, restore):
        for attr in ('initdays', 'overwriteindex', 'dailydata', 'lastend', 'lasthandled',
                     'games', 'initstats', 'mostrecentstats', 'laststats'):
            setattr(self, attr, restore[attr])
        
    def serialize(self):
        data = {}
        for attr in ('initdays', 'overwriteindex', 'dailydata', 'lastend', 'lasthandled',
                     'games', 'initstats', 'mostrecentstats', 'laststats'):
            data[attr] = getattr(self, attr)
        return data
    
    def get_recent_stats(self):
        """The most recent stats check result"""
        return self.mostrecentstats
    
    def get_games(self, gametype: int = 1) -> dict:
        """Returns all games of specific type"""
        games = {}
        for date, game in self.games.items():
            if game['type'] == gametype:
                games[date] = game
                
        return games
        
    def get_accuracy(self) -> int:
        """Calculate accuracy from game ammount & ammount of days as integer."""
        def get_percent(length):
            if length == 0:
                return 1
            elif length >= 100:
                return 75
            
            return float(length) * 0.75
            
        days = get_percent(len(self.dailydata))
        games = get_percent(len(self.get_games()))
        return int(round((days + games) / 2, 0))
    
    def get_timepergame(self) -> Union[str, bool]:
        """Returns the average time per game OR False if there is no data."""
        def count_games(games):
            totaltime = totalgames = 0
            for _, game in games.items():
                totaltime += game["length"]
                totalgames += 1
            return totaltime, totalgames
        
        totaltime, totalgames = count_games(self.get_games())       
        if totalgames == 0 or totaltime == 0:
            return False
        return totaltime / totalgames
    
    def get_most_map(self) -> Union[str, bool]:
        """Returns the most played map OR False if there is no data."""
        def count_games(games):
            playedmaps = {}
            for _, game in games.items():
                bedwarsmap = game["map"]
                playedmaps[bedwarsmap] = (playedmaps[bedwarsmap] + 1) if bedwarsmap in playedmaps else 1
            return playedmaps
        
        playedmaps = count_games(self.get_games())
        playedmaps = {v:k for k, v in playedmaps.items()}   
        maximum = max(tuple(playedmaps.keys()), default=False) 
        return False if maximum is False else playedmaps[maximum]
           
    def get_gamemodeallkey_occurrences(self) -> Tuple[GameKeys, Dict[str, int]]:  
        """Returns Keys in a diffrent format: {Gamemode: ((key, neatmode),)}, {key: occurrences}"""
           
        gamemodeallkeys = {}
        keyoccurrences = {}       
        for gamemode in tuple(self.modes.keys()):
            
            gamemodekeys = self.get_gamemode_keys(gamemode, True)
            gamemodeallkeys[gamemode] = gamemodekeys
            for (key, _) in gamemodekeys:
                if key in keyoccurrences:
                    keyoccurrences[key] += 1
                else:
                    keyoccurrences[key] = 1 
        
        return gamemodeallkeys, keyoccurrences
    
    def get_gamemode_keys(self, gamemode: str, usehidden: bool) -> tuple:
        """Returns all keys for the gamemode."""
        gamemodekeys = self.datakeys
            
        if gamemode in self.extrakeys:
            gamemodekeys = tuple(set(gamemodekeys + self.extrakeys[gamemode]))
            
        if gamemode in self.hiddenkeys and usehidden:
            gamemodekeys = tuple(set(gamemodekeys + self.hiddenkeys[gamemode]))
            
        return gamemodekeys
        
    def get_keygamemodes(self) -> Dict[Key, Tuple[str, ...]]:
        """Returns keys and their gamemodes"""
        keygamemodes = {}
        
        def unpack(gamekeys: GameKeys) -> None:
            for gamemode, keys in gamekeys.items():
                for key in keys:
                    if key in keygamemodes:
                        keygamemodes[key].append(gamemode)
                    else:
                        keygamemodes[key] = [gamemode,]
                        
        unpack(self.extrakeys)
        unpack(self.hiddenkeys)
        
        allmodes = tuple(self.modes.keys())
        for key in self.datakeys:
            keygamemodes[key] = allmodes
            
        keygamemodes = {k:tuple(set(v)) for k, v in keygamemodes.items()}
        return keygamemodes
        
    def get_allkeys(self) -> Keys:
        """Group keys from datakeys, extrakeys and hiddenkeys"""
        allkeys = self.datakeys
        allkeys = tuple(set(allkeys + tuple(set([e for a in self.extrakeys.values() for e in a]))))
        allkeys = tuple(set(allkeys + tuple(set([e for a in self.hiddenkeys.values() for e in a]))))
        return allkeys
    
    def expand(self, stats: dict) -> None:
        """Formats hypixel stats for data classes"""
        gamemodeallkeys, keyoccurrences = self.get_gamemodeallkey_occurrences()
        for gamemode, keys in gamemodeallkeys.items():
            for (key, _) in keys:
                checkkey = f'{gamemode}_{key}'
                if not checkkey in stats:
                    #key is a global
                    globalkey = f'overall_{key}'
                    globalvalue = stats[globalkey] if globalkey in stats else stats[key]
                    stats[checkkey] = (globalvalue / keyoccurrences[key]) if globalvalue > 0 else 0
                    stats[globalkey] = globalvalue
                    
    def get_global_differences(self, oldstats: dict, newstats: dict) -> Dict[str, int]:
        """Gets the difference between an old and new stats dictionary"""
        differences = {}
        for (key, _), gamemodes in self.get_keygamemodes().items():
            for gamemode in gamemodes:
                checkkey = f'{gamemode}_{key}'
                if not checkkey in newstats:
                    break
            else:
                #Not a global key.
                continue
            
            #Key is a global key.
            differences[key] = (newstats[key] - oldstats[key]) if key in oldstats else 0

        return differences 
    
    def get_gamemodestats(self, stats: dict) -> dict:
        """Returns the ammount of games for each gamemode."""
        gamemodestats = {}    
        for gamemode in tuple(self.modes.keys()):
            wins = stats[f'{gamemode}_wins'] - self.mostrecentstats[f'{gamemode}_wins']
            losses = stats[f'{gamemode}_losses'] - self.mostrecentstats[f'{gamemode}_losses']
            gamemodestats[gamemode] = gamemodestats[gamemode] + (wins+losses) if gamemode in gamemodestats else (wins+losses)
        return gamemodestats
    
    def update_stats(self, oldstats: dict, newstats: dict, gamemodegames: Dict[str, int] = None) -> None:
        """Update modified oldstats with differences of non expanded raw newstats"""  
        differences = self.get_global_differences(oldstats, newstats)
        
        keygamemodes = self.get_keygamemodes()
        keygamemodes = {k[0]:v for k, v in keygamemodes.items()}
        keyoccurrences = {k:len(v) for k, v in keygamemodes.items()}
        
        gameammount = sum(tuple(gamemodegames.values())) if not gamemodegames is None else 0
        
        for key, difference in differences.items():
            globalkey = f'overall_{key}'
            newstats[globalkey] = newstats[key]
            
            if gameammount > 0:
                for gamemode, games in gamemodegames.items():
                    checkkey = f'{gamemode}_{key}'
                    add = (difference/gameammount)*games
                    newstats[checkkey] = (oldstats[checkkey] + add) if checkkey in oldstats else add
                    
                for gamemode in keygamemodes[key]:
                    checkkey = f'{gamemode}_{key}'
                    if not checkkey in newstats:
                        newstats[checkkey] = oldstats[checkkey] if checkkey in oldstats else 0
            else:        
                ammount = keyoccurrences[key]
                for gamemode in keygamemodes[key]:
                    checkkey = f'{gamemode}_{key}'
                    add = (difference / ammount) if ammount != 0 else 0
                    newstats[checkkey] = (oldstats[checkkey] + add) if checkkey in oldstats else add
    
    def get_keystats(self, stats: dict) -> dict:    
        """Returns all keys that are in datakeys/extrakeys/hiddenkeys""" 
        keystats = {}
        gamemodeallkeys, _ = self.get_gamemodeallkey_occurrences()
        gamemodeallkeys = {k:(v + (('wins', 'Wins'), ('losses', 'Losses'))) for k, v in gamemodeallkeys.items()}
        for gamemode, keys in gamemodeallkeys.items():
            for (key, _) in keys:
                checkkey = f'{gamemode}_{key}'
                globalkey = f'overall_{key}'
                
                if checkkey in stats:
                    keystats[checkkey] = stats[checkkey]
                    
                if globalkey in stats:
                    keystats[globalkey] = stats[globalkey]
                    
        return keystats
    
    def get_difference(self, oldstats: dict, newstats: dict) -> dict:
        """Return the difference of keystats between oldstats & newstats."""
        keystats = self.get_keystats(newstats)
        gainedstats = {}
        for key in tuple(keystats.keys()):
            if key in oldstats:
                gainedstats[key] = (keystats[key] - oldstats[key])
            else:
                gainedstats[key] = keystats[key]
                logging.warning(f"Missing a key in oldstats while getting stats difference: {str(key)}. So had to use raw value: {str(keystats[key])}")
                
        return gainedstats
               
    def daily_save(self, dailywaittime) -> None:
        """Saves the difference, between current stats and stats from a day ago, as todays stats in dailydata"""
        stats = self.mostrecentstats
        
        end = datetime.now(timezone.utc).timestamp()
        data = {"endtime": end, "starttime": self.lastend, 'apiwaittime': dailywaittime}
        self.lastend = end
        
        gainedstats = self.get_difference(self.laststats, stats)
        
        data['gainedstats'] = gainedstats
        data['statsstate'] = stats.copy()
        
        if self.overwriteindex < 730:
            if len(self.dailydata) > self.overwriteindex:
                self.dailydata[self.overwriteindex] = data
            else:
                self.dailydata.append(data)
            self.overwriteindex += 1
        else:
            self.dailydata[0] = data
            self.overwriteindex = 1
        
        logging.info(f"{self.gamemode.name.capitalize()} daily stats stored for " + str(stats["ign"]))
        self.daily_reset()
        
    def daily_reset(self) -> None:
        """Resets all daily data collections and saves current stats for next day comparison."""
        self.laststats = self.get_keystats(self.mostrecentstats)
    
    def updatefrom_mostrecentstats(self, stats: dict) -> dict:
        """Updates stats from mostrecentstats. Returns ammount of games played in each gamemode."""
        gamemodestats = self.get_gamemodestats(stats)
        self.update_stats(self.mostrecentstats, stats, gamemodestats)
        return gamemodestats
    
    def set_handled(self, timestamp):
        self.lasthandled = timestamp
          
    def save_games(self, stats: dict, games: dict, embeddata: tuple) -> bool:
        """Handles new games and stats"""
        games = {k: v for (k, v) in games.items() if (v['end'] > self.lasthandled)}
        games = {k: v for (k, v) in games.items() if str(v["mode"]) in tuple(self.modes.keys())}
        
        gamemodegames = {}
        for date, game in games.items():
            gamemode = game["mode"]
            if gamemode in gamemodegames:
                gamemodegames[gamemode][date] = game
            else:
                gamemodegames[gamemode] = {date: game}
            
            #Set last handled to most recent game end
            ended = game['end']
            if ended > self.lasthandled:    
                self.lasthandled = ended
        
        gainedstats = self.get_difference(self.mostrecentstats, stats)
        for gamemode in tuple(self.modes.keys()):
            statswins = gainedstats[f'{gamemode}_wins']
            statslosses = gainedstats[f'{gamemode}_losses']
            games = gamemodegames[gamemode] if gamemode in gamemodegames else {}
            gamesammount = len(games)
            if any([v > 0 for v in (statswins, statslosses, gamesammount)]):
                self.save_gamemode(gamemode, stats["ign"], statswins, statslosses, gainedstats, gamesammount, games, embeddata)
                sleep(0.1)
                
        self.mostrecentstats = stats
        return True
        
    def save_gamemode(self, gamemode: str, playername: str, statswins: int, statslosses: int, gainedstats: dict, gameammount: int, games: dict, embeddata: tuple) -> None:
        """Handles game and stats of gamemode"""
        allkeys = self.get_gamemode_keys(gamemode, True)
        displaykeys = self.get_gamemode_keys(gamemode, False)

        neatmode = self.modes[gamemode]
        statsammount = statswins + statslosses
        playername = re.sub(r'([_*~`|])', r'\\\1', playername)
        
        title = f'{playername} played {neatmode}'
        title2 = f'You played {neatmode}'
        
        dontdm = False
        if (gameammount == statsammount and (statswins == 0 or statslosses == 0)):
            """Games and stats line up AND all wins or all losses.
                (Games can be matched with stats) (Will dm player)"""
            description, summary = self.save_each_game(gamemode, neatmode, statswins, statslosses, gainedstats, gameammount, games, allkeys, displaykeys)    
        else:
            if statsammount >= 1:
                """Either one or more game was not recorded OR diffrent gameresults
                    (Games can not be matched with stats so show stats) (Will dm player)"""
                description, summary = self.save_stats_summary(gamemode, neatmode, statswins, statslosses, gainedstats, gameammount, allkeys, displaykeys)
            else:
                """Games but no stats (Probably Private games) 
                    Just say they were private (Will not dm player)"""
                dontdm = True
                if gameammount > 1:
                    description = f'Found {gameammount} new {neatmode} games, but '\
                                f'could not find any Stats for these games. '\
                                f'_(Probably because these games were Private)_'  
                else:
                    description = f'Found {gameammount} new {neatmode} game, but '\
                                f'could not find any Stats for this game. '\
                                f'_(Probably because this game was Private)_'
                               
                summary = {}      
        
        asyncio.create_task(
            log_game(*embeddata, title, title2, description, summary, dontdm)
        )
        
    def save_stats_summary(self, gamemode: str, neatmode: str, statswins: int, statslosses: int, gainedstats: dict, 
                                gameammount: int, allkeys: tuple, displaykeys: tuple) -> Tuple[str, dict]:
        """Saves game as statsgame and returns a description and summary"""
        timestamp = datetime.now(timezone.utc).timestamp()
        
        presentstats = {}
        
        presentstats['mode'] = gamemode        
        presentstats['type'] = 2 
                
        for (keyname, _) in (*allkeys, ('wins', 'Wins'), ('losses', 'Losses')):
            presentstats[keyname] = gainedstats[f'{gamemode}_{keyname}']
        
        self.games[timestamp] = presentstats
       
        statsammount = statswins + statslosses 
        e1 = 's' if statsammount > 1 else ''
        if gameammount != statsammount:
            if gameammount > 1:
                description=f'Found {statsammount} new {neatmode} game{e1}. '\
                            f'Summary is from Stats because Games did not match Statsdata ({gameammount}/{statsammount}). '\
                            f'_(Probably because atleast one of the games you played was Private)_'
            elif gameammount > 0:
                description = f'Found {statsammount} new {neatmode} game{e1}. '\
                            f'Summary is from Stats because Game did not match Statsdata ({gameammount}/{statsammount}). '\
                            f'_(Probably because the game you played was Private)_'
            else:
                description = f'Found {statsammount} new {neatmode} game{e1}. '\
                            f'Summary is from Stats because there are no new recentgames. '\
                            f'_(Probably because the game you played was Private)_'
        else:
            if gameammount > 1:
                description=f'Found {statsammount} new {neatmode} game{e1}. '\
                            f'Summary is from Stats because game results could not be determined. '\
                            f'_(Probably because atleast one of the games you played was Private)_'
            elif gameammount > 0:
                description=f'Found {statsammount} new {neatmode} game{e1}. '\
                            f'Summary is from Stats because game result could not be determined. '\
                            f'_(Probably because the game you played was Private)_'
            else:
                description=f'Found {statsammount} new {neatmode} game{e1}. '\
                            f'Summary is from Stats because there are no new recentgames. '\
                            f'_(Probably because the game you played was Private)_'
           
        summary = {}
        if statsammount <= 1:
            summary["Won"] = 'True' if statswins == 1 else 'False'
        else:
            summary["Wins"] = statswins
            summary["Losses"] = statslosses
            
        for (keyname, neatname) in displaykeys:
            summary[neatname] = gainedstats[f'{gamemode}_{keyname}']
        
        return description, summary
    
    def save_each_game(self, gamemode: str, neatmode: str, statswins: int, statslosses: int, gainedstats: dict, 
                            gameammount: int, games: dict, allkeys: tuple, displaykeys: tuple) -> Tuple[str, dict]:
        gameresult = True if statslosses == 0 else False  
        length = 0
        gamemaps = []
        for date, game in games.items():
            length += game["length"]
            gamemaps.append(game["map"])
            
            game['type'] = 1
            game["result"] = gameresult

            for (keyname, _) in allkeys:
                game[keyname] = gainedstats[f'{gamemode}_{keyname}'] / gameammount
            
            self.games[date] = game    
                
        length = str(timedelta(seconds=int(length)))
            
        e1 = 's' if gameammount > 1 else ''
        description = f'Found {gameammount} new {neatmode} game{e1}.'
        if gameresult is None and gameammount <= 1:
            description += f' The Game result could not be resolved. _(Probably because it was Private)_'
                
        summary = {"Length": length}
        if gameammount <= 1:
            summary["Won"] = str(gameresult) if gameresult != None else 'Unkown'
            summary["Map"] = gamemaps[0]
        else:
            if all(x==gamemaps[0] for x in gamemaps):
                summary["Map"] = gamemaps[0]
            summary["Wins"] = statswins
            summary["Losses"] = statslosses
            
        for (keyname, neatname) in displaykeys:
            summary[neatname] = gainedstats[f'{gamemode}_{keyname}']
            
        return description, summary
    
    def get_data(self, mode='overall', neat=False):
        """Returns alldata collected summerized"""
        
        alldata = {}
        alldata['wins'] = 0
        alldata['losses'] = 0
        for _, game in self.games.items():
            gm = game['mode']
            if mode != gm and not mode == 'overall':
                continue
            
            allkeys = self.get_gamemode_keys(gm, True)
            gametype = game['type']
            if gametype == 1:
                result = game['result']
                if result:
                    alldata['wins'] += 1
                else:
                    alldata['losses'] += 1
            elif gametype == 2:
                alldata['wins'] += game['wins']
                alldata['losses'] += game['losses']
                
            for (key, neatkey) in allkeys:
                alldatakey = neatkey if neat else key
                if key in game:
                    alldata[alldatakey] = alldata[alldatakey] + game[key] if alldatakey in alldata else game[key]
        
        for (key, neatkey) in self.get_allkeys():
            alldatakey = neatkey if neat else key
            if not alldatakey in alldata:
                alldata[alldatakey] = 0
        return alldata    
    
    def is_gametype(self, game: dict) -> bool:
        """Checks if a game is of this gametype."""
        if game["gameType"] != self.gametype:
            return False
             
        return True
        