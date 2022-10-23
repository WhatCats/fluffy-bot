'''
Created on Apr 3, 2021

@author: Josef
'''
import fnmatch
import logging
import os
import random

from PIL import Image, ImageDraw

from bedwars.util import draw_bedwars_extra
from duels.util import draw_duels_extra, get_duels_title
from main.draw_tools import Oriantation, combine_images, draw_playername, \
    draw_head, discord_image, draw_network_level, draw_guild, \
    get_font, oriant_coords, draw_text, draw_grid, get_other_font
from main.gamemodes import Gamemode
from resources.path import resource_path
from skywars.util import draw_skywars_extra


backgrounds = []
for file in fnmatch.filter(os.listdir(resource_path("backgrounds_bridge")), '*.png'):
    name = file[:-4]
    image = Image.open(os.path.join(resource_path("backgrounds_bridge"), file))
    backgrounds.append(image)
    
forgrounds = {}
for file in fnmatch.filter(os.listdir(resource_path("forgrounds_bridge")), '*.png'):
    name = file[:-4]
    image = Image.open(os.path.join(resource_path("forgrounds_bridge"), file))
    forgrounds[name] = image
    
items = {}
for file in fnmatch.filter(os.listdir(resource_path("layout_bridge")), '*.png'):
    name = file[:-4]
    image = Image.open(os.path.join(resource_path("layout_bridge"), file))
    items[name] = image

def random_bg():
    return random.choice(backgrounds).copy()

def draw_hotbar(image, coords, layout, oriantation=Oriantation.LEFT):
    width = 288
    coords = oriant_coords(coords, width, oriantation)
        
    for item in layout:
        img = items[item]
        image.paste(img, coords, img)
        coords = (coords[0] + 32, coords[1])

def draw_bridge_stats(statsdata):
    bg = random_bg()
    fg = forgrounds["stats"]
    image = combine_images(bg, fg)
    
    logging.info(f'Showing bridge stats of {statsdata["uuid"]} ({statsdata["name"]})')
    coordmap = [{"oriantation" : Oriantation.CENTER, "value" : "{}_wins", "place" : (124, 203), "size" : 16}, {"oriantation" : Oriantation.CENTER, "value" : "{}_losses", "place" : (124, 255), "size" : 16},
            {"oriantation" : Oriantation.CENTER, "value" : "{}_wlr", "place" : (124, 305), "size" : 16}, {"oriantation" : Oriantation.CENTER, "value" : "{}_goals", "place" : (311, 203), "size" : 16},
            {"oriantation" : Oriantation.CENTER, "value" : "{}_best_winstreak", "place" : (311, 255), "size" : 16}, {"oriantation" : Oriantation.CENTER, "value" : "{}_winstreak", "place" : (311, 305), "size" : 16}]
    
    draw_grid(image, 381, 208, coordmap, 3, ["bridge_duel", "bridge_doubles", "bridge_four", "bridge_2v2v2v2", "bridge_3v3v3v3", "The Bridge"], statsdata)
    
    draw_playernamefull((97, 86), image, 20, statsdata["The Bridge_wins"], statsdata)
    draw_guild(image, (1004.5, 597), 17, statsdata["guild"], Oriantation.CENTER)
    draw_hotbar(image, (1004.5, 554), statsdata["The Bridge_layout"], Oriantation.CENTER)
    draw_network_level(image, (1004.5, 634), 17, statsdata["network_level"], Oriantation.CENTER)
    draw_head(image, (1000, 19), statsdata["head"], (110, 102), rotation=3.7, mirror=True)
    
    draw = ImageDraw.Draw(image)
    font = get_font(18)
    draw_skywars_extra(draw, (293, 566), font, statsdata.pop(Gamemode.SKYWARS))
    draw_bedwars_extra(draw, (297, 597), font, statsdata.pop(Gamemode.BEDWARS))
    draw_duels_extra(draw, (249, 627), font, statsdata)
    
    return discord_image(image)
    
def draw_playernamefull(coords, image, fontsize, wins, statsdata):
    font = get_other_font(fontsize)
    draw = ImageDraw.Draw(image)
    title = get_duels_title(wins, game = "The Bridge")
    
    coords = draw_text(draw, coords, title, font, shadow = True)
    coords = (coords[0] + 15, coords[1])
    draw_playername(coords, image, fontsize, statsdata)
    