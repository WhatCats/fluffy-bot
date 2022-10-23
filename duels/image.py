'''
Created on Apr 16, 2021

@author: Josef
'''
from concurrent.futures.thread import ThreadPoolExecutor
import fnmatch
import logging
import os
import random

from PIL import Image, ImageDraw
import emoji
import yaml

from bedwars.util import draw_bedwars_extra
from bridge.image import draw_bridge_stats
from duels.util import get_duels_title, get_best_duel, get_duel_type
from main.draw_tools import combine_images, draw_guild, Oriantation, \
    draw_network_level, draw_head, get_font, discord_image, \
    get_other_font, draw_text, draw_playername, draw_grid, draw_values, \
    draw_texts
from main.gamemodes import Gamemode
from main.yamlloader import Loader
from resources.path import resource_path
from skywars.util import draw_skywars_extra


backgrounds = []
for file in fnmatch.filter(os.listdir(resource_path("backgrounds_duels")), '*.png'):
    name = file[:-4]
    image = Image.open(os.path.join(resource_path("backgrounds_duels"), file))
    backgrounds.append(image)
    
forgrounds = {}
for file in fnmatch.filter(os.listdir(resource_path("forgrounds_duels")), '*.png'):
    name = file[:-4]
    image = Image.open(os.path.join(resource_path("forgrounds_duels"), file))
    forgrounds[name] = image

yamlconfigs = {}
for file in fnmatch.filter(os.listdir(resource_path("forgrounds_duels")), '*.yml'):
    name = file[:-4]
    with open(os.path.join(resource_path("forgrounds_duels"), file), "r") as f:
        yamlconfigs[name] = yaml.load(f, Loader=Loader)

def random_bg():
    return random.choice(backgrounds).copy()

def make_image(bg, baseimage, statsdata, num):
    fg = forgrounds[f"stats{num}"]
    image = combine_images(bg.copy(), fg)
    image = combine_images(image, baseimage)
    bmpdata = yamlconfigs[f"stats{num}_map"]
    
    statsdata["layout"] = draw_layout
    draw_values(image, bmpdata, statsdata)
    return discord_image(image)

def make_first(bg, baseimage, statsdata, duelsdata):
    fg = forgrounds["stats"]
    image = combine_images(bg.copy(), fg)
    image = combine_images(image, baseimage)
    
    coordmap = [{"oriantation" : Oriantation.CENTER, "value" : "{}_wins", "place" : (198, 213), "size" : 16}, {"oriantation" : Oriantation.CENTER, "value" : "{}_losses", "place" : (198, 269), "size" : 16},
            {"oriantation" : Oriantation.CENTER, "value" : "{}_wlr", "place" : (198, 325), "size" : 16}, {"oriantation" : Oriantation.CENTER, "value" : "{}_games", "place" : (466, 213), "size" : 16},
            {"oriantation" : Oriantation.CENTER, "value" : "{}_best_winstreak", "place" : (466, 269), "size" : 16}, {"oriantation" : Oriantation.CENTER, "value" : "{}_winstreak", "place" : (466, 325), "size" : 16},
            {"oriantation" : Oriantation.CENTER, "value" : "{}_bow_hits", "place" : (735, 269), "size" : 16}, {"oriantation" : Oriantation.CENTER, "value" : "{}_bow_shots", "place" : (735, 213), "size" : 16},
            {"oriantation" : Oriantation.CENTER, "value" : "{}_bow_accuracy", "place" : (735, 325), "size" : 16}, {"oriantation" : Oriantation.CENTER, "value" : "{}_melee_hits", "place" : (1004, 269), "size" : 16},
            {"oriantation" : Oriantation.CENTER, "value" : "{}_melee_swings", "place" : (1004, 213), "size" : 16}, {"oriantation" : Oriantation.CENTER, "value" : "{}_melee_accuracy", "place" : (1004, 325), "size" : 16}]
    draw_grid(image, 0, 229, coordmap, 1, ["overall", get_best_duel(duelsdata)], statsdata)
    draw_duels_title((195, 146), image, 20, "overall", statsdata)
    draw_duels_title((235, 375), image, 20, get_best_duel(duelsdata), statsdata)
    return discord_image(image)
    
def draw_duels_stats(statsdata, gamemode):
    duelsdata = statsdata.pop(Gamemode.DUELS)
    statsdata = {**statsdata, **duelsdata}
    
    if get_duel_type(gamemode) == "The Bridge":
        return draw_bridge_stats(statsdata)
    
    initialindex = 0
    if get_duel_type(gamemode) != False:
        gametypes = {"UHC": 1, "The Bridge": 2, "Classic": 1, "Bow": 3, "Nodebuff": 2, "OP": 1, "TNT": 3, "SkyWars": 1, "Sumo": 2, 
             "Mega Walls": 3, "Blitz": 3, "Combo": 2, "overall": 0} 
        if get_duel_type(gamemode) in gametypes:
            initialindex = gametypes[get_duel_type(gamemode)]
    
    bg = random_bg()
    
    logging.info(f'Showing duels stats of {statsdata["uuid"]} ({statsdata["name"]})')
    
    baseimage = Image.new("RGBA", (bg.size), (255, 0, 0, 0))
    draw_base(baseimage, statsdata.copy())
    
    imgs = []
    with ThreadPoolExecutor() as e:
        if gamemode == "ALL": 
            imgs.append(e.submit(draw_bridge_stats, statsdata.copy()))
        imgs.append(e.submit(make_first, bg, baseimage, statsdata, duelsdata))
        imgs.append(e.submit(make_image, bg, baseimage, statsdata, "2"))
        imgs.append(e.submit(make_image, bg, baseimage, statsdata, "3"))
        imgs.append(e.submit(make_image, bg, baseimage, statsdata, "4"))
        
    
    emojis = emoji.emojize(":star:"), emoji.emojize(":one:", use_aliases=True), emoji.emojize(":two:", use_aliases=True), emoji.emojize(":three:", use_aliases=True)
    if gamemode == "ALL":
        emojis = (emoji.emojize(":zero:", use_aliases=True),) + emojis
    return dict(zip(emojis, [img.result() for img in imgs])), initialindex

def draw_duels_projection(statsdata):
    bg = random_bg()
    fg = forgrounds["projection"]
    image = combine_images(bg, fg)
    
    logging.info(f'Showing duels projection of {statsdata["uuid"]} ({statsdata["name"]})')
    draw_playernamefull((65, 180), image, 20, statsdata, gametype=statsdata["gametype"])
    coordmap = [{"oriantation" : Oriantation.RIGHT, "value" : "goal", "place" : (585, 102), "size" : 20}, {"oriantation" : Oriantation.CENTER, "value" : "wins", "place" : (197, 300), "size" : 20},
            {"oriantation" : Oriantation.CENTER, "value" : "losses", "place" : (197, 385), "size" : 20}, {"oriantation" : Oriantation.CENTER, "value" : "wlr", "place" : (197, 470), "size" : 20},
            {"oriantation" : Oriantation.CENTER, "value" : "gametimeagame", "place" : (565, 310), "size" : 20}, {"oriantation" : Oriantation.CENTER, "value" : "gametime", "place" : (565, 395), "size" : 20},
            {"oriantation" : Oriantation.CENTER, "value" : "dailywlr", "place" : (565, 480), "size" : 20}, {"oriantation" : Oriantation.CENTER, "value" : "dailygames", "place" : (953, 309), "size" : 20},
            {"oriantation" : Oriantation.CENTER, "value" : "dailywins", "place" : (953, 390), "size" : 20}, {"oriantation" : Oriantation.CENTER, "value" : "dailylosses", "place" : (953, 475), "size" : 20},
            {"oriantation" : Oriantation.LEFT, "value" : "mostmap", "place" : (393, 526), "size" : 22}, {"oriantation" : Oriantation.LEFT, "value" : "date", "place" : (151, 589), "size" : 18},
            {"oriantation" : Oriantation.LEFT, "value" : "accuracy", "place" : (196, 616), "size" : 12}]
    draw_texts(image, coordmap, statsdata)
    draw_head(image, (1000, 38), statsdata["head"], (110, 102), rotation=3.7, mirror=True)
    
    return discord_image(image)

def draw_playernamefull(coords, image, fontsize, statsdata, gametype='overall'):
    font = get_other_font(fontsize)
    draw = ImageDraw.Draw(image)
    title = get_duels_title(statsdata["wins"], game=gametype) if ("wins" in statsdata) else get_duels_title(statsdata["overall_wins"], game=gametype)
    
    coords = draw_text(draw, coords, title, font, shadow = True)
    coords = (coords[0] + 15, coords[1])
    draw_playername(coords, image, fontsize, statsdata)
    
def draw_duels_title(coords, image, fontsize, mode, statsdata):
    font = get_other_font(fontsize)
    draw = ImageDraw.Draw(image)
    title = get_duels_title(statsdata[f"{mode}_wins"], game=mode, default="§7None")
    
    draw_text(draw, coords, title, font, shadow=True)

def draw_layout(draw, coords, fontsize, statsdata, orientation=Oriantation.LEFT):
    pass

def draw_base(image, statsdata):
    draw_playernamefull((97, 86), image, 20, statsdata)
    draw_guild(image, (1004.5, 597), 17, statsdata["guild"], Oriantation.CENTER)
    draw_network_level(image, (1004.5, 634), 17, statsdata["network_level"], Oriantation.CENTER)
    draw_head(image, (1000, 19), statsdata["head"], (110, 102), rotation=3.7, mirror=True)
    
    draw = ImageDraw.Draw(image)
    font = get_font(18)
    draw_skywars_extra(draw, (288, 600), font, statsdata.pop(Gamemode.SKYWARS))
    draw_bedwars_extra(draw, (280, 632), font, statsdata.pop(Gamemode.BEDWARS))
    