'''
Created on May 2, 2021

@author: Josef
'''
import fnmatch
import logging
import os
import random

from PIL import Image, ImageDraw
import yaml

from bedwars.util import draw_bedwars_extra
from duels.util import draw_duels_extra
from main.draw_tools import combine_images, discord_image, draw_guild, \
    Oriantation, draw_network_level, draw_head, get_font, draw_text, \
    draw_playername, draw_values
from main.gamemodes import Gamemode
from main.yamlloader import Loader
from resources.path import resource_path
from skywars.util import get_skywars_level

backgrounds = []
for file in fnmatch.filter(os.listdir(resource_path("backgrounds_skywars")), '*.png'):
    name = file[:-4]
    image = Image.open(os.path.join(resource_path("backgrounds_skywars"), file))
    backgrounds.append(image)
    
forgrounds = {}
for file in fnmatch.filter(os.listdir(resource_path("forgrounds_skywars")), '*.png'):
    name = file[:-4]
    image = Image.open(os.path.join(resource_path("forgrounds_skywars"), file))
    forgrounds[name] = image
    
yamlconfigs = {}
for file in fnmatch.filter(os.listdir(resource_path("forgrounds_skywars")), '*.yml'):
    name = file[:-4]
    with open(os.path.join(resource_path("forgrounds_skywars"), file), "r") as f:
        yamlconfigs[name] = yaml.load(f, Loader=Loader)

def random_bg():
    return random.choice(backgrounds).copy()

def draw_skywars_stats(statsdata, _):
    bg = random_bg()
    fg = forgrounds["stats"]
    image = combine_images(bg, fg)
    
    swdata = statsdata.pop(Gamemode.SKYWARS)
    statsdata = {**statsdata, **swdata}
    logging.info(f'Showing skywars stats of {statsdata["uuid"]} ({statsdata["name"]})')
    
    bmpdata = yamlconfigs["stats_map"]
    draw_values(image, bmpdata, statsdata)
    
    draw_playernamefull((97, 86), image, 20, statsdata)
    draw_guild(image, (1004.5, 597), 17, statsdata["guild"], Oriantation.CENTER)
    draw_network_level(image, (1004.5, 634), 17, statsdata["network_level"], Oriantation.CENTER)
    draw_head(image, (1000, 19), statsdata["head"], (110, 102), rotation=3.7, mirror=True)

    draw = ImageDraw.Draw(image)
    font = get_font(18)
    draw_bedwars_extra(draw, (275, 602), font, statsdata.pop(Gamemode.BEDWARS))
    draw_duels_extra(draw, (223, 631), font, statsdata.pop(Gamemode.DUELS))
    
    return discord_image(image)

def draw_playernamefull(coords, image, fontsize, statsdata):
    font = get_font(fontsize)
    draw = ImageDraw.Draw(image)
    
    level = get_skywars_level(statsdata["level"])
    coords = draw_text(draw, coords, level, font, shadow = True)
    coords = (coords[0] + 15, coords[1])
    coords = draw_playername(coords, image, fontsize, statsdata)
    