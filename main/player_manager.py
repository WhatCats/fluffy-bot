'''
Created on 12 Mar 2021

@author: Josef
'''
import codecs
import json
import os

from main.stats_data import StatsData
from resources.path import resource_path

players = {}

def get_players():
    return players

def get_player(uuid):
    if not uuid in players.keys():
        return False
    
    return players[uuid]

def get_author_player(discord):
    for _, pm in players.items():
        if pm.discord == discord:
            return pm
    
    return False
    
def remove_player(uuid):
    del players[uuid]

def add_player(playermanager):
    players[playermanager.uuid] = playermanager

class PlayerManager():
    def __init__(self, initstats, *args, **kwargs):
        if 'restore' in kwargs:
            self.rebuild(kwargs['restore'], initstats)
        else:
            self.new(initstats, *args, **kwargs)
        
        self.start_tasks()
        self.save_data()
        add_player(self)
    
    def new(self, initstats, uuid, discord, timezone, resettime):
        self.uuid = uuid
        self.discord = discord
        self.timezone = timezone
        self.resettime = resettime
        self.dodms = True
        
        self.stats = StatsData(self, initstats)   
           
    def rebuild(self, restore, initstats):
        for attr in ('uuid', 'discord', 'timezone', 'resettime', 'dodms'):
            setattr(self, attr, restore[attr])
            
        self.stats = StatsData(self, initstats, restore=restore['stats'])
        
    def serialize(self):
        data = {}
        for attr in ('uuid', 'discord', 'timezone', 'resettime', 'dodms'):
            obj = getattr(self, attr)
            if isinstance(obj, (int, str, float, bool, None, dict, list)):
                data[attr] = obj
            else:
                data[attr] = str(obj)
        
        data["stats"] = self.stats.serialize()
        return data
    
    def save_data(self):  
        data = self.serialize()
        path = os.path.join(resource_path('stats'), f'{self.uuid}.json')
        with open(path, 'wb') as savefile:
            json.dump(data, codecs.getwriter('utf-8')(savefile), ensure_ascii=False, indent=4)
          
    def start_tasks(self):
        self.stats.start_tasks()
        
    def set_dodms(self, dodms):
        self.dodms = self.stats.dodms = dodms
        self.save_data()
        
    def get_stats_accuracy(self, gamemode):
        if len(self.stats[gamemode]) == 0:
            return 1
        elif len(self.stats[gamemode]) >= 100:
            return 75
        
        return float((len(self.stats[gamemode]) * 0,75))
        
    def get_stats(self, gamemode):
        return self.stats.get_stats(gamemode)
    
    def get_game_data(self, gamemode):
        return self.stats.get_data(gamemode)
    
    def set_timezone(self, tz):
        self.timezone = tz
        self.stats.timezone = tz
        
    def set_resettime(self, rt):
        self.resettime = rt
        self.stats.resettime = rt
        
            