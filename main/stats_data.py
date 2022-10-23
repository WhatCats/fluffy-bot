'''
Created on Mar 7, 2021

@author: Josef
'''
import asyncio
from datetime import datetime, timedelta, timezone, date
import logging
import random

import pytz

from api.hypixel_api import get_stats, get_games
from bedwars.data import BedwarsData
from duels.data import DuelsData
from main.asynctimer import Timer
from main.gamemodes import Gamemode
from skywars.data import SkywarsData

bot = None
    
gamemodesdata = {Gamemode.BEDWARS: BedwarsData, Gamemode.SKYWARS: SkywarsData,
                 Gamemode.DUELS: DuelsData}
    
class StatsData():
    def __init__(self, playermanager, initstats, *args, **kwargs):
        self.pm = playermanager
        self.gamedata = {}
        self.daily_task = self.minutely_task = self.start_task = None
        
        if 'restore' in kwargs:
            self.rebuild(kwargs['restore'])
        else:
            self.new(initstats, *args, **kwargs)
            
        self.check_data(initstats)  
            
    def new(self, initstats):
        self.creation = datetime.now(timezone.utc)
        self.initdays = (datetime.today() - initstats["firstlogin"]).days
        self.dailywaittime = 0
        
        self.scheduled_time = None
        
    def rebuild(self, restore):
        self.creation = datetime.fromtimestamp(restore['creation'], timezone.utc)
        self.initdays = restore['initdays']
        self.dailywaittime = restore['dailywaittime']
        
        scheduled = restore['scheduled']
        if not scheduled is None:
            self.scheduled_time = datetime.fromtimestamp(
                                    scheduled['time'], pytz.timezone(scheduled['tzinfo']))
        else:
            self.scheduled_time = None
        
        global gamemodesdata    
        for gamemode, gamedata in restore['gamedata'].items():
            gamemode = Gamemode.from_string(gamemode)
            self.gamedata[gamemode] = gamemodesdata[gamemode](self.pm.uuid, restore=gamedata)
    
    def serialize(self):
        data = {}
        data['creation'] = self.creation.timestamp()
        data['initdays'] = self.initdays
        data['dailywaittime'] = self.dailywaittime
        
        if not self.scheduled_time is None:
            scheduled = {}
            scheduled['time'] = self.scheduled_time.timestamp()
            scheduled['tzinfo'] = str(self.scheduled_time.tzinfo)
            data['scheduled'] = scheduled
        else:
            data['scheduled'] = None
        
        gamemodes = {}    
        for gamemode, gamedata in self.gamedata.items():
            gamemodes[gamemode.name] = gamedata.serialize()  
        data['gamedata'] = gamemodes 
        
        return data  
    
    def save_data(self):
        self.pm.save_data()
            
    def check_data(self, initstats):
        global gamemodesdata
        for gamemode, DataClass in gamemodesdata.items():
            if not gamemode in self.gamedata:
                self.gamedata[gamemode] = DataClass(self.pm.uuid, self.initdays, initstats[gamemode])

    def get_days(self, gamemode):
        days = 0
        if self.scheduled_time != None:
            timeleft = self.scheduled_time - datetime.now(timezone.utc)
            days = (86400 - timeleft.total_seconds()) / 86400
        return len(self.gamedata[gamemode].dailydata) + days
    
    def summerized(self):
        alldata = {}
        for gamemode, gamedata in self.gamedata.items():
            alldata[gamemode.name] = gamedata.get_all(self.get_days(gamemode))
        return alldata
        
    def get_accuracy(self, gamemode):
        return self.gamedata[gamemode].get_accuracy()
               
    def get_data(self, gamemode, *args, **kwargs):
        return self.gamedata[gamemode].get_data(*args, **kwargs) 
    
    def get_stats(self, gamemode, *args, **kwargs):
        return self.gamedata[gamemode].get_stats(self.get_days(gamemode), *args, **kwargs) 
    
    def get_most_map(self, gamemode) -> str:    
        mostmap = self.gamedata[gamemode].get_most_map() 
        if not isinstance(mostmap, str):
            return "N/A"
        return mostmap
          
    async def store_stats(self, **kwargs):
        for _, gamedata in self.gamedata.items():
            gamedata.daily_save(self.dailywaittime)
        
        self.dailywaittime = 0
        self.save_data() 
        self.schedule_daily_task(**kwargs)
        
    async def store_games(self, new=False):
        starttime = datetime.now(timezone.utc)
        result, stats = await get_stats(self.pm.uuid)
        wait = 0
        while result is False:
            wait += (10 + random.randint(0, 10))
            logging.warning(f'[204] Unable to get player stats: {self.pm.uuid}. {stats} Trying again in {wait} seconds.')
            self.dailywaittime += wait
            await asyncio.sleep(wait)
            result, stats = await get_stats(self.pm.uuid)   
        
        gamestats = {gm:stats.pop(gm) for gm in tuple(self.gamedata.keys())}
        
        gamemodegamemodestatsammount = {}
        gamemodestats = {}
        
        for gamemode, gamedata in self.gamedata.items():
            modestats = {**gamestats[gamemode], **stats}
            gamemodestatsammount = gamedata.updatefrom_mostrecentstats(modestats) 
            gamemodegamemodestatsammount[gamemode] = gamemodestatsammount
            gamemodestats[gamemode] = modestats
        
        currenttime = datetime.now(timezone.utc).timestamp()  
        if not new and not any([(num > 0) for v in tuple(gamemodegamemodestatsammount.values()) for num in tuple(v.values())]):
            for gamedata in tuple(self.gamedata.values()):
                gamedata.set_handled(currenttime)
            self.save_data()
            self.schedule_minutely_task()
            return
        
        result, games = await get_games(self.pm.uuid)
        if result is False:
            logging.warning(f'[203] Unable to get player games: {self.pm.uuid}. {games} Trying again in 3 seconds.')
            self.dailywaittime += 3
            await asyncio.sleep(3)
            result, games = await get_games(self.pm.uuid)
            
        if result is False:
            logging.warning(f'[203] Unable to get player games: {self.pm.uuid}. {games} Aborted.')
            self.save_data()
            self.schedule_minutely_task()
            return
        
        games = self.find_games(games)
        for gamemode, gamos in games.items():
            gamedata = self.gamedata[gamemode]
            gamedata.save_games(gamemodestats[gamemode], gamos, (self.pm, starttime)) 
        
        self.save_data()
        self.schedule_minutely_task()
        
    def find_games(self, games):
        newgames = {}
        for game in games:
            if not "ended" in game.keys():
                continue
            
            for gamemode, gamedata in self.gamedata.items():
                if gamedata.is_gametype(game):
                    if not gamemode in newgames.keys():
                        newgames[gamemode] = {}
                    break
            else:
                continue
            
            gameend = int(game["ended"]) / 1000
            gameend = datetime.fromtimestamp(gameend, timezone.utc)
                
            gamestart = int(game["date"]) / 1000
            gamestart = datetime.fromtimestamp(gamestart, timezone.utc)
            
            mode = game["mode"]
            if (mode.startswith(game["gameType"])):
                mode = mode[(len(game["gameType"]) + 1):]
            
            length = (gameend - gamestart).total_seconds()
            newgames[gamemode][gamestart.timestamp()] = {"start": gamestart.timestamp(), "end": gameend.timestamp(), "length": length, "mode": mode.lower(), "map": game["map"]}
        
        return newgames
    
    def current_time(self):
        tz = pytz.timezone(self.pm.timezone)
        time = datetime.now(tz)
        return time
    
    def set_resettime(self, resettime):
        #TODO
        pass
        
    def stop(self):
        tasks = ["daily_task", "start_task"]
        for task in tasks:
            task = getattr(self, task)
            if task is None:
                continue
            task.cancel()
            setattr(self, task, None)
            
    def stop_minutely(self):
        if not self.minutely_task is None:
            self.minutely_task.cancel()
            self.minutely_task = None
        
    def reset(self):
        self.stop()
        self.scheduled_time = None
        self.save_data()
        self.start_tasks()
    
    def get_status(self):
        if not self.start_task is None:
            return f"Waiting to start tasks at {str(self.start_task.get_finish(self.pm.timezone))}"
        
        if not self.scheduled_time is None:
            return f"Tasks started, scheduled time is at {str(self.scheduled_time)}."
        
        return f"Unkown state."
        
    async def force_start(self):
        if self.start_task is None:
            return False
        
        self.start_task.cancel()
        self.start_task = None
        
        try:
            today = self.current_time()
            scheduled_time = None
            if self.pm.resettime > today.hour:
                scheduled_time = today.replace(hour=self.pm.resettime, minute=0, microsecond=0)
            await self.store_stats(y=scheduled_time)
        except Exception as e:
            raise e
            return False
                
        return True
                        
    def start_tasks(self):  
        asyncio.create_task(self.store_games(new=True))
        
        today = datetime.now(timezone.utc)
        scheduled_time = self.scheduled_time
        
        #Check if scheduled time has to be recreated
        if self.scheduled_time is None or scheduled_time < today:
            x = self.current_time()
            if x.hour < self.pm.resettime:
                y = x.replace(hour=self.pm.resettime, minute=0, microsecond=0)
            else:
                y = (x + timedelta(days=1)).replace(hour=self.pm.resettime, minute=0, microsecond=0)
                
            delta_t=y-datetime.now(timezone.utc)
        
            secs=delta_t.total_seconds()
            logging.info(f"Starting tasks for {self.pm.uuid} at {str(y)}") 
            
            self.start_task = Timer(secs, self.store_stats)
            return 
        
        #Resume with schedule time
        if scheduled_time > today:
            logging.info(f"Resuming for {self.pm.uuid} at scheduled time: {scheduled_time}")
            self.schedule_task(self.store_stats, scheduled_time)
                    
    def schedule_daily_task(self, y=None):
        logging.info("Starting daily task for: " + self.pm.uuid)
        self.schedule_task(self.store_stats, y=y)
    
    def _on_task_exception(self, _, callback): 
        async def keep_trying():
            attempts = 0
            wait = 10
            
            while True:
                try:
                    await asyncio.sleep(wait)
                    attempts += 1
                    await callback()
                    break
                except Exception:
                    wait += (10 + random.randint(0, 10))
                    logging.exception(f"Exception while trying task again. Attempts: {attempts}. Trying again in {wait} seconds.")
                    
        asyncio.create_task(keep_trying())
        
    def schedule_task(self, task, y=None):
        x = self.current_time()
        if y is None:
            y = (x + timedelta(days=1)).replace(hour=self.pm.resettime, minute=0, second=0, microsecond=0)
        self.scheduled_time = y
        delta_t=y-datetime.now(timezone.utc)
        
        secs=delta_t.total_seconds()
        
        self.daily_task = Timer(secs, task, onexception=self._on_task_exception)
        self.save_data() 
            
    def schedule_minutely_task(self):
        x = datetime.now(timezone.utc)
        y = x + timedelta(seconds=30)
        delta_t=y-datetime.now(timezone.utc)

        secs=delta_t.total_seconds()
        
        self.minutely_task = Timer(secs, self.store_games, onexception=self._on_task_exception)
        