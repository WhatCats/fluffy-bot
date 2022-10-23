'''
Created on Apr 8, 2021

@author: Josef
'''
from duels.util import get_duels_title
from main.draw_tools import draw_text

def draw_bridge_extra(draw, coords, font, bridgedata):
    title = get_duels_title(bridgedata["The Bridge_wins"], game = "The Bridge", default="§7None")
    coords = draw_text(draw, coords, title, font)
    coords = (coords[0] + 15, coords[1])
    
    text =  "§f(" + str(bridgedata["The Bridge_wlr"]) + " W/L)"
    draw_text(draw, coords, text, font)
