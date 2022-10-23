'''
Created on Mar 5, 2021

@author: Josef
'''
import asyncio
from configparser import ConfigParser
from datetime import datetime
from json.decoder import JSONDecodeError
import logging
import socket

import aiohttp
from aiohttp.client import ClientTimeout
from aiohttp.client_exceptions import ContentTypeError, ClientConnectorError

from api.util import multiple_requests, BadRequest, get_value
from bedwars.util import get_bedwars_all, get_bedwars_stats
from duels.util import get_duels_all, get_duels_stats
from hypixel.util import get_hypixel_all
from main.gamemodes import Gamemode
from resources.path import resource_path
from skywars.util import get_skywars_all, get_skywars_stats


config = ConfigParser()
config.read(resource_path("config.ini")) 
keys = config["KEYS"]
apikey = keys["hypixel"]

#Hypixel API (api.hypixel.net)
async def hypixel_request(endpoint, log=True, **params):
    paramstr = ""
    for key, value in params.items():
        paramstr = f'{paramstr}&{key}={value}'
    
    try:
        conn = aiohttp.TCPConnector(family=socket.AF_INET)
        async with aiohttp.ClientSession(connector=conn, timeout=ClientTimeout(total=7)) as session:
            async with session.get(f"https://api.hypixel.net/{endpoint}?key={apikey}{paramstr}") as r:
                if r.status != 200:
                    raise BadRequest(r.status)
                
                result = await r.json()
                
                if result["success"] is False:
                    if "cause" in result:
                        return False, f'Unable to make this request. Reason: {result["cause"]}'
                    return False, f'Unable to make this request. Unkown reason.'
        
                if "player" in result.keys() and result["player"] is None:
                    return False, "That player could not be found."
                
                return True, result
    except BadRequest as e:
        if log: logging.warning(f"Unable to reach api.hypixel.net. Request status was: ({e}).")
    except ClientConnectorError as e:
        if log: logging.warning(f"Unable to reach api.hypixel.net. Connection error was: ({e}).")
    except (ContentTypeError, JSONDecodeError, KeyError):
        if log: logging.warning(f"Unable to decode the responce from api.hypixel.net. Decode error.")
    except (TimeoutError, asyncio.TimeoutError):
        if log: logging.warning(f"Unable to reach api.hypixel.net. Request has timed out.")
    
    return False, "Unable to reach the hypixel api at the moment."

async def get_init_stats(uuid):
    success, result = await hypixel_request("player", uuid=uuid)
    if success is False:
        return success, result
    
    if not "player" in result:
        return False, "That player could not be found."
    
    
    ts = int(result["player"]["firstLogin"]) / 1000
    ts = datetime.utcfromtimestamp(ts)
        
    try:
        discord = result["player"]["socialMedia"]["links"]["DISCORD"]
    except KeyError:
        discord = None
            
    return success, {Gamemode.BEDWARS: get_bedwars_stats(result), Gamemode.SKYWARS: get_skywars_stats(result),
            Gamemode.DUELS: get_duels_stats(result), "discord": discord, "firstlogin": ts, "ign": result["player"]["displayname"], 'time': datetime.today().timestamp()}

async def get_guild(uuid):
    success, result = await hypixel_request("guild", log=False, player=uuid)
    if success is False:
        return (True, None)
     
    return (True, result)

async def get_friends(uuid):
    success, result = await hypixel_request("friends", uuid=uuid)
    if success is False:
        return success, result
    
    if "records" not in result.keys():
        return True, 0
    
    friends = result["records"]
    return success, friends
    
async def get_data(uuid):
     
    success, results = await multiple_requests(get_friends(uuid), get_guild(uuid), hypixel_request("player", uuid=uuid))
    if success is False:
        return success, results 
        
    friendsresult, guildresult, result = results
    
    if not "player" in result:
        return False, "That player could not be found."
    playerdata = result["player"]
    
    try:
        discord = playerdata["socialMedia"]["links"]["DISCORD"]
    except KeyError:
        discord = None
      
    return True, {"name" : get_value(playerdata, "displayname", default="None"), "uuid" : uuid, "latest" : get_value(playerdata, "mostRecentGameType", "None"),
                Gamemode.BEDWARS : get_bedwars_all(result), Gamemode.SKYWARS : get_skywars_all(result), "discord" : discord, Gamemode.DUELS : get_duels_all(result), **get_hypixel_all(result, friendsresult, guildresult)}
                                     
async def get_stats(uuid):
    success, result = await hypixel_request("player", uuid=uuid)
    if success is False:
        return success, result
    
    if not "player" in result:
        return False, "That player could not be found."
        
    return success, {Gamemode.BEDWARS : get_bedwars_stats(result), Gamemode.SKYWARS : get_skywars_stats(result),
                     Gamemode.DUELS : get_duels_stats(result), "ign": result["player"]["displayname"], 'time': datetime.today().timestamp()}
                        
async def get_games(uuid): 
    success, result = await hypixel_request("recentgames", uuid=uuid)
    if success is False:
        return success, result
    
    if not "games" in result:
        return False, "Unable to get games."
        
    return success, result["games"]
        