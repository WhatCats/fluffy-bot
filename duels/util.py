'''
Created on Apr 8, 2021

@author: Josef
'''
from collections import OrderedDict

from api.util import add_value
from calculations.format import format_ratio
from main.draw_tools import draw_text

titles = {10000 : {"title" : "§5{}Godlike", "maxwins" : 28000, "steps" : 2000}, 
          5000 : {"title" : "§e{}Grandmaster", "maxwins" : 10000, "steps" : 1000}, 
          2000 : {"title" : "§4{}Legend", "maxwins" : 5000, "steps" : 600}, 
          1000 : {"title" : "§2{}Master", "maxwins" : 2000, "steps" : 200},
          500 : {"title" : "§3{}Diamond", "maxwins" : 1000, "steps" : 100},
          250 : {"title" : "§6{}Gold", "maxwins" : 500, "steps" : 50}, 
          100 : {"title" : "§f{}Iron", "maxwins" : 250, "steps" : 30},
          50 : {"title" : "§8{}Rookie", "maxwins" : 100, "steps" : 10}}

def write_roman(num):
    roman = OrderedDict()
    roman[9] = "IX"
    roman[5] = "V"
    roman[4] = "IV"
    roman[1] = "I"

    def roman_num(num):
        for r in roman.keys():
            x, _ = divmod(num, r)
            yield roman[r] * x
            num -= (r * x)
            if num <= 0:
                break

    return "".join([a for a in roman_num(num)])    

def get_duels_title(wins, game="", default=""):
    multi = 1
    if game == "overall":
        game = ""
        
    if game != "":
        game = game + " "
            
    if game == "":
        multi = 2
    
    if wins >= (28000*multi):
        return f'§6✫ §5{game}Godlike X'
    
    if wins < (50*multi):
        return default
    
    title = "Error"
    for minwins, titledata in titles.items():
        minwins *= multi
        if wins >= minwins and wins < (titledata["maxwins"] * multi):
            num = int((wins - minwins) / (titledata["steps"] * multi)) + 1
            
            if num > 1:
                title = f'§6✫ {titledata["title"].format(game)} {write_roman(num)}'
            else:
                title = f'§6✫ {titledata["title"].format(game)}'
                
            break
    
    return title

def draw_duels_extra(draw, coords, font, duelsdata):
    text = get_duels_title(duelsdata["overall_wins"], default="§7None")
    coords = draw_text(draw, coords, text, font)
    coords = (coords[0] + 15, coords[1])
    
    text =  "§f(" + str(duelsdata["overall_wlr"]) + " W/L)"
    draw_text(draw, coords, text, font)

def get_layout(result, mode, default):
    if len(result) == 0:
        return default
    
    key = f"layout_{mode}_layout"
    if not (key in result):
        return default
    
    layout = result[key] 
    hotbar = []
  
    for i in range(9):
        i = str(i)
        if i in layout.keys():
            hotbar.append(layout[i])
        else:
            hotbar.append("empty")
        
    return hotbar

bridge_default = ("iron_sword", "bow", "diamond_pickaxe", "stained_clay_1", "stained_clay_2", "golden_apple", "empty", "glyph_menu", "arrow")
uhc_default = ("diamond_sword", "bow", "fishing_rod", "diamond_axe", "golden_apple", "golden_head", "lava_bucket_1", "lava_bucket_2", "water_bucket_1")
gamemodes = {"UHC" : [uhc_default, "uhc", "uhc_duel", "uhc_doubles", "uhc_four"], "The Bridge" : [bridge_default, "bridge", "bridge_duel", "bridge_doubles", "bridge_2v2v2v2", "bridge_3v3v3v3", "bridge_four"], 
            "Classic" : [(), "classic", "classic_duel"], "Combo" : [(), "combo", "combo_duel"], "Bow" : [(), "bow", "bow_duel"], "Nodebuff" : [(), "potion", "potion_duel"], "OP" : [(), "op", "op_duel", "op_doubles"], 
            "TNT" : [False, "bowspleef", "bowspleef_duel"], "SkyWars" : [False, "sw", "sw_duel", "sw_doubles"], "Sumo" : [False, "sumo", "sumo_duel"], "Mega Walls" : [False, "mw", "mw_duel", "mw_doubles"], 
            "Blitz" : [False, "blitz", "blitz_duel"], "overall" : [False, "overall", None]} 

def get_modes(gametype):
    if not gametype in gamemodes:
        return False
    
    val = gamemodes[gametype]
    val = val.copy()
    _ = val.pop(0)
    _ = val.pop(0)
    
    if val[0] != None:
        return val
    return ['overall',]
    
def get_duels_all(result):
    duels_stats = {}
    if "stats" in result["player"].keys() and "Duels" in result["player"]["stats"].keys():
        duels_stats = result["player"]["stats"]["Duels"].copy() 
    
    all_stats = {} 
    for key, val in gamemodes.items():
        val = val.copy()
        hotbar = val.pop(0)
        wsmode = val.pop(0)
        
        length = len(val)
        i = 0
         
        while i < length:
            mode = val[i]
            i += 1
            if mode is None:
                gm = ""
                gm2 = f'{key}_'
            else:
                gm = gm2 = f'{mode}_'
            
            wins = all_stats[f'{gm2}wins'] = (add_value(duels_stats, f"{gm}wins", all_stats, f"{key}_wins"))
            losses = all_stats[f'{gm2}losses'] = add_value(duels_stats, f"{gm}losses", all_stats, f"{key}_losses")
            all_stats[f'{gm2}wlr'] = format_ratio(wins, losses)
            add_value(duels_stats, f"{gm}rounds_played", all_stats, f"{key}_games")
            if mode != None:
                add_value(duels_stats, f"current_winstreak_mode_{mode}", all_stats, f"{gm2}winstreak")
                add_value(duels_stats, f"best_winstreak_mode_{mode}", all_stats, f"{gm2}best_winstreak")
            
            hits = add_value(duels_stats, f"{gm}melee_hits", all_stats, f"{key}_melee_hits", default="N/A")
            swings = add_value(duels_stats, f"{gm}melee_swings", all_stats, f"{key}_melee_swings", default="N/A")
            if isinstance(hits, int) and isinstance(swings, int):
                all_stats[f'{key}_melee_accuracy'] = format_ratio(hits, swings, percent=True)
            else:
                all_stats[f'{key}_melee_accuracy'] = "N/A"
            
            hits = add_value(duels_stats, f"{gm}bow_hits", all_stats, f"{key}_bow_hits", default="N/A")
            shots = add_value(duels_stats, f"{gm}bow_shots", all_stats, f"{key}_bow_shots", default="N/A")
            if isinstance(hits, int) and isinstance(shots, int):
                all_stats[f'{key}_bow_accuracy'] = format_ratio(hits, shots, percent=True)
            else:
                all_stats[f'{key}_bow_accuracy'] = "N/A"
                
            if key == 'The Bridge' or key == "overall":
                all_stats[f"{gm2}goals"] = add_value(duels_stats, f"{gm}goals", all_stats, f"{key}_goals")
            
            if hotbar is False:
                all_stats[f'{key}_layout'] = None    
            else:
                layout = get_layout(duels_stats, mode, hotbar)
                if not f'{key}_layout' in all_stats:
                    all_stats[f'{key}_layout'] = layout
        
        all_stats[f'{key}_wlr'] = format_ratio(all_stats[f'{key}_wins'], all_stats[f'{key}_losses'])   
        add_value(duels_stats, f'current_{wsmode}_winstreak', all_stats, f"{key}_winstreak")
        add_value(duels_stats, f'best_{wsmode}_winstreak', all_stats, f"{key}_best_winstreak")
    
    add_value(duels_stats, f'current_winstreak', all_stats, f"overall_winstreak")
    
    return all_stats

def get_duels_stats(result):
    data = get_duels_all(result)
    modekeys = list(gamemodes.keys())[:-1]
    for key in list(data.keys()):
        for mk in modekeys:
            if key.startswith(mk):
                del data[key]
    
    return data

gamemodesneat = {"UHC": [], "The Bridge": ["BRIDGE", "BRIG", "BRIGE", "BIRG", "BRIGG", "BERG"], "Classic": ["CLASS", "LUCAS", "BABYRAGE"], "Combo": ["WOMBOCOMBO",], 
             "Bow": [], "Nodebuff": ["POTION", "POT"], "OP": [], "TNT": ["BOWSPLEEF", "BS"], "SkyWars": ["SW",], "Sumo": [], 
             "Mega Walls": ["WALLS", "MEGA", "MW"], "Blitz": [], "overall": ["ALL",]} 
def get_duel_type(gametype):
    gametype = gametype.upper().replace(' ', '')
    for key, values in gamemodesneat.items():
        if gametype == key.upper().replace(' ', ''):
            return key
        
        if len(values) == 0:
            continue
        
        allvalues = values.copy()
        for v in values:
            allvalues.append(v + 'S') 
        allvalues2 = list(set(allvalues.copy()))
        for v in allvalues:
            allvalues2.append(v + 'DUEL')
            allvalues2.append(v + 'DUELS')
            
        if gametype in allvalues2:
            return key
    
    
    for key, values in gamemodes.items():
        vs = values.copy()[2:]
        for v in vs:
            if v != None and gametype == v.upper():
                return key
                 
    return False  

def get_best_duel(duelsdata):
    best = (0, "UHC")
    for gamemode in gamemodesneat.keys():
        if gamemode == "overall":
            continue
        
        wins = duelsdata[f'{gamemode}_wins']
        if wins >= best[0]:
            best = (wins, gamemode)
    
    return best[1]   

def get_gamemode(index):
    gms = list(gamemodesneat.keys())
    return gms[index]
