'''
Created on Apr 9, 2021

@author: Josef
'''
import fnmatch
import logging
import os
import random

from PIL import Image, ImageDraw

from bedwars.util import draw_bedwars_extra
from bridge.util import draw_bridge_extra
from duels.util import draw_duels_extra
from main.draw_tools import combine_images, draw_network_level, Oriantation, \
    get_font, discord_image, draw_text, draw_playername, \
    draw_body, draw_status, draw_texts
from main.gamemodes import Gamemode
from resources.path import resource_path
from skywars.util import draw_skywars_extra


backgrounds = []
for file in fnmatch.filter(os.listdir(resource_path("backgrounds_hypixel")), '*.png'):
    name = file[:-4]
    image = Image.open(os.path.join(resource_path("backgrounds_hypixel"), file))
    backgrounds.append(image)
    
forgrounds = {}
for file in fnmatch.filter(os.listdir(resource_path("forgrounds_hypixel")), '*.png'):
    name = file[:-4]
    image = Image.open(os.path.join(resource_path("forgrounds_hypixel"), file))
    forgrounds[name] = image

def random_bg():
    return random.choice(backgrounds).copy()

def draw_hypixel_stats(statsdata, _):
    bg = random_bg()
    fg = forgrounds["stats"]
    image = combine_images(bg, fg)
    
    statsdata["firstlogin"] = statsdata["firstlogin"].strftime("%m/%d/%Y")
    statsdata["lastlogin"] = statsdata["lastlogin"].strftime("%m/%d/%Y")
    
    logging.info(f'Showing hypixel stats of {statsdata["uuid"]} ({statsdata["name"]})')
    coordmap = [{"oriantation" : Oriantation.CENTER, "value" : "karma", "place" : (231, 219), "size" : 16}, {"oriantation" : Oriantation.CENTER, "value" : "achievementpoints", "place" : (231, 328), "size" : 16},
            {"oriantation" : Oriantation.CENTER, "value" : "quests", "place" : (231, 437), "size" : 16}, {"oriantation" : Oriantation.CENTER, "value" : "friends", "place" : (633, 219), "size" : 16},
            {"oriantation" : Oriantation.CENTER, "value" : "firstlogin", "place" : (633, 328), "size" : 16}, {"oriantation" : Oriantation.CENTER, "value" : "lastlogin", "place" : (633, 437), "size" : 16}]
    
    draw_texts(image, coordmap, statsdata)
    
    draw_playernamefull((72, 95), image, 20, statsdata)
    draw_network_level(image, (999, 70), 18, statsdata["network_level"], oriantation=Oriantation.CENTER)
    draw_status(image, (999, 450), 18, statsdata["status"], oriantation=Oriantation.CENTER)
    draw_body(image, (999, 130), statsdata["body"], (120, 270), rotation=0, mirror=True, oriantation=Oriantation.CENTER)
    
    draw = ImageDraw.Draw(image)
    font = get_font(18)
    draw_skywars_extra(draw, (290, 530), font, statsdata.pop(Gamemode.SKYWARS))
    draw_bedwars_extra(draw, (295, 563), font, statsdata.pop(Gamemode.BEDWARS))
    draw_bridge_extra(draw, (265, 594), font, statsdata[Gamemode.DUELS])
    draw_duels_extra(draw, (249, 626), font, statsdata.pop(Gamemode.DUELS))
    
    return discord_image(image)

def draw_playernamefull(coords, image, fontsize, statsdata):
    font = get_font(fontsize)
    draw = ImageDraw.Draw(image)
    
    coords = draw_playername(coords, image, fontsize, statsdata)
    if statsdata["guild"] == "§7None":
        return coords
    
    coords = (coords[0] + 15, coords[1])
    return draw_text(draw, coords, statsdata["guild"], font, shadow = True)
    