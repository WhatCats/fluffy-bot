'''
Created on May 2, 2021

@author: Josef
'''
from datetime import datetime
import logging
import math

from api.util import get_value

def get_status(lastlogout, lastlogin):
    if (lastlogout < lastlogin):
        return "§aOnline"
    return "§cOffline"

colors = {"RED": "§c", "GOLD" : "§6", "GREEN" : "§a", "YELLOW" : "§e", "LIGHT_PURPLE" : "§d", "WHITE" : "§f",
          "BLUE" : "§9", "DARK_GREEN" : "§2", "DARK_RED" : "§4", "DARK_AQUA" : "§3", "DARK_PURPLE" : "§5", 
          "DARK_GRAY" : "§8", "BLACK" : "§0", "DARK_BLUE" : "§1", "GRAY" : "§7"}
def get_plus_color(result):
    if "rankPlusColor" in result["player"]:
        return colors[result["player"]["rankPlusColor"]]

def get_guild_tag(result):
    if result is None or result["guild"] is None:
        return "§7None"
        
    if not "tag" in result["guild"] or not "tagColor" in result["guild"]:
        return "§7None"
    
    text = result["guild"]["tag"]
    color = colors[result["guild"]["tagColor"]]
    return f'{color}[{text}]'

def get_rank(result):
    player = result["player"]
    if "rank" in player.keys() and player["rank"] != "NORMAL":
        return player["rank"]
    
    if "monthlyPackageRank" in player.keys() and player["monthlyPackageRank"] != "NONE":
        return "MVP_PLUS_PLUS"
    
    if "newPackageRank" in player.keys():
        return player["newPackageRank"]
    
    return "NON"

def get_quests(result):
    playerdata = result["player"]   
    questscompleted = 0
    if "quests" in playerdata:
        quests = playerdata["quests"].values()
        for value in quests:
            if not "completions" in value.keys():
                continue
            
            questscompleted += len(value["completions"])
            
    return questscompleted

def get_hypixel_all(result, friendsresult, guildresult):
    playerdata = result["player"]
    
    network_experience = get_value(playerdata, "networkExp") 
    network_level = (math.sqrt((2 * network_experience) + 30625) / 50) - 2.5
    network_level = int(math.floor(network_level))
    
    firstts = int(playerdata["firstLogin"]) / 1000
    firstts = datetime.utcfromtimestamp(firstts)
    
    lastts = firstts
    if "lastLogout" in playerdata.keys():
        lastts = int(result["player"]["lastLogout"]) / 1000
        lastts = datetime.utcfromtimestamp(lastts)
    
    latestts = lastts
    if "lastLogin" in playerdata.keys():
        latestts = int(playerdata["lastLogin"]) / 1000
        latestts = datetime.utcfromtimestamp(latestts)
    status = get_status(lastts, latestts)
      
    return {"pluscolor" : get_plus_color(result), "network_level" : network_level, "rank" : get_rank(result), "karma" : get_value(playerdata, "karma"), "friends" : len(friendsresult), 
            "mostrecentgametype" : get_value(playerdata, "mostRecentGameType", default="NONE"), "achievementpoints" : get_value(playerdata, "achievementPoints"), "firstlogin" : firstts, 
            "lastlogout" : lastts, "lastlogin" : latestts, "quests" : get_quests(result), "status" : status, "guild" : get_guild_tag(guildresult)}
    