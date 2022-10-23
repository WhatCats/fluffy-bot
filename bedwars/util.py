'''
Created on Apr 8, 2021

@author: Josef
'''
import math

from api.util import add_value, get_value
from calculations.format import format_ratio
from main.draw_tools import draw_text


BEDWARS_EXP_PER_PRESTIGE = 487000
BEDWARS_LEVELS_PER_PRESTIGE = 100

def calc_bedwars_level(exp):
    if exp < 500:
        return 1
    
    prestige = int(exp / BEDWARS_EXP_PER_PRESTIGE)
    exp = exp % BEDWARS_EXP_PER_PRESTIGE;
    
    #First four levels are diffrent   
    if exp < 500:
        return (prestige * BEDWARS_LEVELS_PER_PRESTIGE)
    elif exp < 1500:
        return 1 + (prestige * BEDWARS_LEVELS_PER_PRESTIGE)
    elif exp < 3500:
        return 2 + (prestige * BEDWARS_LEVELS_PER_PRESTIGE)
    elif exp < 7000:
        return 3 + (prestige * BEDWARS_LEVELS_PER_PRESTIGE)
    elif exp < 12000:
        return 4 + (prestige * BEDWARS_LEVELS_PER_PRESTIGE)
    
    exp -= 7000
    return math.floor(exp / 5000 + 4) + (prestige * BEDWARS_LEVELS_PER_PRESTIGE)  
    
bwlevels = {3000 : "§e[{}§6{}{}§c{}⚝§4]", 2900 : "§b[{}§3{}{}§1{}⚝]", 2800 : "§a[{}§2{}{}§6{}⚝§e]", 2700 : "§e[{}§f{}{}§8{}⚝]", 2600 : "§4[{}§c{}{}§d{}⚝§5]", 2500 : "§f[{}§a{}{}§2{}⚝]",
            2400 : "§b[{}§f{}{}§7{}⚝§8]", 2300 : "§5[{}§d{}{}§6{}§e⚝]", 2200 : "§6[{}§f{}{}§b{}§3⚝]", 2100 : "§f[{}§e{}{}§6{}⚝]", 2000 : "§8[§7{}§f{}{}§7{}✪§8]", 1900 : "§5[{}{}{}{}✪]",
            1800 : "§1[{}{}{}{}✪]", 1700 : "§d[{}{}{}{}✪]", 1600 : "§4[{}{}{}{}✪]", 1500 : "§3[{}{}{}{}✪]", 1400 : "§2[{}{}{}{}✪]", 1300 : "§b[{}{}{}{}✪]",
            1200 : "§6[{}{}{}{}✪]", 1100 : "§f[{}{}{}{}✪]", 1000 : "§c[§6{}§e{}§a{}§b{}§d✫$5]", 900 : "§5[{}{}{}✫]", 800 : "§1[{}{}{}✫]", 700 : "§d[{}{}{}✫]", 600 : "§4[{}{}{}✫]",
            500 : "§3[{}{}{}✫]", 400 : "§2[{}{}{}✫]", 300 : "§b[{}{}{}✫]", 200 : "§6[{}{}{}✫]", 100 : "§f[{}{}{}✫]", 0 : "§7[{}✫]"}
def get_bedwars_level(exp):
    level = int(calc_bedwars_level(exp))
    num = [int(d) for d in str(level)]
    levelprefix = "§cError"
    for minlevel, prefix in bwlevels.items():
        if level >= minlevel:
            if level < 100:
                levelprefix = prefix.format(level)
            else:
                levelprefix = prefix.format(*num)
            break
        
    return levelprefix

def draw_bedwars_extra(draw, coords, font, bedwarsdata):
    text = get_bedwars_level(bedwarsdata["exp"])
    coords = draw_text(draw, coords, text, font)
    coords = (coords[0] + 15, coords[1])
    
    text =  "§f(" + str(bedwarsdata["overall_fkdr"]) + " FKDR)"
    draw_text(draw, coords, text, font)
    
bwmodes = [("eight_one_", "eight_one_"), ("eight_two_", "eight_two_"), ("four_three_", "four_three_"), 
           ("four_four_", "four_four_"), ("two_four_", "two_four_"), ("overall_", "")]
def get_bedwars_all(result):
    bedwars_stats = {}
    if "stats" in result["player"].keys() and "Bedwars" in result["player"]["stats"].keys():
        bedwars_stats = result["player"]["stats"]["Bedwars"].copy()
    all_stats = {}
    
    for mode, lookup in bwmodes:
        add_value(bedwars_stats, f"{lookup}winstreak", all_stats, f"{mode}winstreak")
        fdeaths = add_value(bedwars_stats, f"{lookup}final_deaths_bedwars", all_stats, f"{mode}final_deaths")
        fkills = add_value(bedwars_stats, f"{lookup}final_kills_bedwars", all_stats, f"{mode}final_kills")
        deaths = add_value(bedwars_stats, f"{lookup}deaths_bedwars", all_stats, f"{mode}deaths")
        kills = add_value(bedwars_stats, f"{lookup}kills_bedwars", all_stats, f"{mode}kills")
        add_value(bedwars_stats, f"{lookup}beds_broken_bedwars", all_stats, f"{mode}beds")
        losses = add_value(bedwars_stats, f"{lookup}losses_bedwars", all_stats, f"{mode}losses")
        wins = add_value(bedwars_stats, f"{lookup}wins_bedwars", all_stats, f"{mode}wins")
        
        all_stats[f'{mode}wlr'] = format_ratio(wins, losses)
        all_stats[f'{mode}fkdr'] = format_ratio(fkills, fdeaths)
        all_stats[f'{mode}kdr'] = format_ratio(kills, deaths)
    
    all_stats["exp"] = get_value(bedwars_stats, "Experience")
    
    if "favorite_slots" in bedwars_stats.keys():
        slots = bedwars_stats["favorite_slots"].split(',')
        slots = [string.lower() for string in slots]
    else:
        slots = ["null"] * 9
        
    all_stats["layout"] = slots
    
    return all_stats

def get_bedwars_stats(result):
    data = get_bedwars_all(result)
    del data["layout"]
    return data
