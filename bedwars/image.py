'''
Created on Apr 8, 2021

@author: Josef
'''
import fnmatch
import logging
import os
import random

from PIL import ImageDraw, Image

from bedwars.util import get_bedwars_level
from bridge.util import draw_bridge_extra
from duels.util import draw_duels_extra
from main.draw_tools import draw_text, get_font, draw_guild, combine_images, \
    Oriantation, draw_network_level, draw_head, \
    discord_image, draw_playername, oriant_coords, draw_grid
from main.gamemodes import Gamemode
from resources.path import resource_path
from skywars.util import draw_skywars_extra


backgrounds = []
for file in fnmatch.filter(os.listdir(resource_path("backgrounds_bedwars")), '*.png'):
    name = file[:-4]
    image = Image.open(os.path.join(resource_path("backgrounds_bedwars"), file))
    backgrounds.append(image)
    
forgrounds = {}
for file in fnmatch.filter(os.listdir(resource_path("forgrounds_bedwars")), '*.png'):
    name = file[:-4]
    image = Image.open(os.path.join(resource_path("forgrounds_bedwars"), file))
    forgrounds[name] = image

items = {}
for file in fnmatch.filter(os.listdir(resource_path("layout_bedwars")), '*.png'):
    name = file[:-4]
    image = Image.open(os.path.join(resource_path("layout_bedwars"), file))
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
            
def draw_bedwars_stats(statsdata, _):
    bg = random_bg()
    fg = forgrounds["stats"]
    image = combine_images(bg, fg)
    
    bedwarsdata = statsdata.pop(Gamemode.BEDWARS)
    statsdata = {**statsdata, **bedwarsdata}
    
    logging.info(f'Showing bedwars stats of {statsdata["uuid"]} ({statsdata["name"]})')
    coordmap = [{"oriantation" : Oriantation.LEFT, "value" : "{}_wins", "place" : (115, 183), "size" : 16}, {"oriantation" : Oriantation.LEFT, "value" : "{}_losses", "place" : (157, 206), "size" : 16},
            {"oriantation" : Oriantation.LEFT, "value" : "{}_final_kills", "place" : (130, 232), "size" : 16}, {"oriantation" : Oriantation.LEFT, "value" : "{}_final_deaths", "place" : (168, 256), "size" : 16},
            {"oriantation" : Oriantation.LEFT, "value" : "{}_beds", "place" : (125, 282), "size" : 16}, {"oriantation" : Oriantation.LEFT, "value" : "{}_winstreak", "place" : (93, 306), "size" : 16},
            {"oriantation" : Oriantation.CENTER, "value" : "{}_wlr", "place" : (341, 206), "size" : 16}, {"oriantation" : Oriantation.CENTER, "value" : "{}_fkdr", "place" : (341, 255), "size" : 16},
            {"oriantation" : Oriantation.CENTER, "value" : "{}_kdr", "place" : (341, 305), "size" : 16}]
            
    draw_grid(image, 381, 208, coordmap, 3, ["eight_one", "eight_two", "four_three", "four_four", "two_four", "overall"], statsdata)
    draw_playernamefull((97, 86), image, 20, statsdata)
    draw_guild(image, (1004.5, 597), 17, statsdata["guild"], Oriantation.CENTER)
    draw_hotbar(image, (1004.5, 554), statsdata["layout"], Oriantation.CENTER)
    draw_network_level(image, (1004.5, 634), 17, statsdata["network_level"], Oriantation.CENTER)
    draw_head(image, (1000, 19), statsdata["head"], (110, 102), rotation=3.7, mirror=True)

    draw = ImageDraw.Draw(image)
    font = get_font(18)
    draw_skywars_extra(draw, (293, 566), font, statsdata.pop(Gamemode.SKYWARS))
    draw_bridge_extra(draw, (262, 598), font, statsdata[Gamemode.DUELS])
    draw_duels_extra(draw, (250, 631), font, statsdata.pop(Gamemode.DUELS))
    
    return discord_image(image)
    
def draw_playernamefull(coords, image, fontsize, statsdata):
    font = get_font(fontsize)
    draw = ImageDraw.Draw(image)
    
    level = get_bedwars_level(statsdata["exp"])
    coords = draw_text(draw, coords, level, font, shadow = True)
    coords = (coords[0] + 15, coords[1])
    coords = draw_playername(coords, image, fontsize, statsdata)
    