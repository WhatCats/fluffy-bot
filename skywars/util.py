'''
Created on May 2, 2021

@author: Josef
'''
from api.util import add_value, get_value
from calculations.format import format_ratio
from main.draw_tools import findOccurrences, draw_text

def get_skywars_level(level):
    level = str(level)
    color = findOccurrences(level, "§")[0]
    color = level[color:color+2]
    return f'{color}[{level}]'
   
def draw_skywars_extra(draw, coords, font, skywarsdata):
    coords = draw_text(draw, coords, get_skywars_level(skywarsdata["level"]), font)
    coords = (coords[0] + 15, coords[1])
    
    text =  "§f(" + str(skywarsdata["overall_kdr"]) + " K/D)"
    return draw_text(draw, coords, text, font)

swmodes = {"solo_insane" : "_solo_insane", "solo_normal" : "_solo_normal", "ranked_normal" : "_ranked_normal", "mega_normal" : "_mega_normal", "team_insane" : "_team_insane", "team_normal" : "_team_normal", "overall" : ""}
def get_skywars_all(result):
    skywars_stats = {}
    if "stats" in result["player"].keys() and "SkyWars" in result["player"]["stats"].keys():
        skywars_stats = result["player"]["stats"]["SkyWars"].copy() 
    all_stats = {}
    
    add_value(skywars_stats, "levelFormatted", all_stats, "level", default="§71⋆")
    add_value(skywars_stats, "skywars_experience", all_stats, "exp")
    add_value(skywars_stats, "souls", all_stats, "souls")
    add_value(skywars_stats, "heads", all_stats, "heads")
    add_value(skywars_stats, "coins", all_stats, "coins")
    
    void_kills = add_value(skywars_stats, "void_kills", all_stats, "overall_void_kills")
    overall_kills = get_value(skywars_stats, "kills")
    all_stats["overall_pvp_kills"] = overall_kills - void_kills
        
    for name, lookup in swmodes.items():
        wins = add_value(skywars_stats, f"wins{lookup}", all_stats, f"{name}_wins")
        losses = add_value(skywars_stats, f"losses{lookup}", all_stats, f"{name}_losses")
        kills = add_value(skywars_stats, f"kills{lookup}", all_stats, f"{name}_kills")
        deaths = add_value(skywars_stats, f"deaths{lookup}", all_stats, f"{name}_deaths")
        all_stats[f'{name}_wlr'] = format_ratio(wins, losses)
        all_stats[f'{name}_kdr'] = format_ratio(kills, deaths)
    
    return all_stats

def get_skywars_stats(result):
    return get_skywars_all(result)
    
