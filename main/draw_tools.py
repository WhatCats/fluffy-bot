'''
Created on Mar 7, 2021

@author: Josef
'''
from _io import BytesIO
from concurrent.futures.thread import ThreadPoolExecutor
from enum import Enum
import os

from PIL import Image, ImageFont, ImageDraw
import discord

from resources.path import resource_path


class Oriantation(Enum):
    CENTER = 0
    LEFT = 1
    RIGHT = 2

def from_fonts(fontname):
    fonts = resource_path("fonts")
    return os.path.join(fonts, fontname)
        
def get_font(size):
    return ImageFont.truetype(from_fonts("Minecraftia.ttf"), size + 6)

def get_other_font(size):
    return ImageFont.truetype(from_fonts("Minecraft2.ttf"), size + 9) 
    
def discord_image(pilimage):
    with BytesIO() as image_binary:
        pilimage.save(image_binary, 'PNG')
        image_binary.seek(0)
        return discord.File(fp=image_binary, filename='image.png')

colorcodes = {"§c": "#FF5555", "§6": "#FFAA00", "§a": "#55FF55", "§e": "#FFFF55", "§d": "#FF55FF", "§f": "#FFFFFF",
          "§9": "#5555FF", "§2": "#00AA00", "§4": "#AA0000", "§3": "#00AAAA", "§5": "#AA00AA", 
          "§8": "#555555", "§0": "#000000", "§1": "#0000AA", "§b": "#55FFFF", "§7": "#AAAAAA", "§r": "#FFFFFF"}
def draw_text(draw, coords, text, font, color="#FFFFFF", shadow=False, oriantation=Oriantation.LEFT):
    ogcoords = coords

    if font.getname()[0] == "Minecraftia":
        coords = (coords[0], coords[1] - 9)
    elif font.getname()[0] == "Minecraft":
        coords = (coords[0], coords[1] + 1)
    
    width = font.getsize(remove_color(text))[0]
    if oriantation == Oriantation.RIGHT:
        coords = (coords[0] - width, coords[1])
    elif oriantation == Oriantation.CENTER:
        coords = (coords[0] - (width/2), coords[1])
        
    colors = findOccurrences(text, "§")
    lastcode = 0
    for c in colors:
        code = text[c:c+2]
        if code in colorcodes.keys():
            
            if shadow is True:
                draw_shadow(draw, coords, text[lastcode:c], color, font) 
            draw.text(coords, text[lastcode:c], fill=color, font=font)
            coords = (coords[0] + font.getsize(text[lastcode:c])[0], coords[1])
            
            color = colorcodes[code]
            lastcode = c + 2
    
    if shadow is True:
        draw_shadow(draw, coords, text[lastcode:], color, font) 
    draw.text(coords, text[lastcode:], fill=color, font=font)
    coords = (coords[0] + font.getsize(text[lastcode:])[0], ogcoords[1])
            
    return coords

def draw_grid(image, disteast, distsouth, coordmap, columns, formats, data):
    places = []
    
    column = 0
    row = 0
    for index, form in enumerate(formats):
        index += 1
        for m in coordmap:
            text = str(data[m["value"].format(form)])
            place = (m["place"][0] + (disteast * column), m["place"][1] + (distsouth * row))
            size = m["size"]
            oriantation = m["oriantation"]
        
            places.append((text, place, size, oriantation))
        column += 1
        if column >= columns:
            column = 0
            row += 1
        
    draw = ImageDraw.Draw(image)
    for text, coords, size, orientation in places:
        draw_text(draw, coords, text, get_other_font(size), oriantation=orientation)
        
def draw_texts(image, coordmap, data):
    places = []
    
    for m in coordmap:
        text = str(data[m["value"]])
        place = m["place"]
        size = m["size"]
        oriantation = m["oriantation"]
        
        places.append((text, place, size, oriantation))
        
    draw = ImageDraw.Draw(image)
    for text, coords, size, orientation in places:
        draw_text(draw, coords, text, get_other_font(size), oriantation=orientation)
          
def draw_values(image, bmpdata, data):
    draw = ImageDraw.Draw(image)
    
    def draw_value(value):  
        orientation = Oriantation(value["orientation"])
        if callable(data[value["value"]]):
            data[value["value"]](draw, value["coords"], value["size"], data, orientation=orientation)
            return
                
        font = get_other_font(value["size"])
        draw_text(draw, value["coords"], str(data[value["value"]]), font, oriantation=orientation)  
    
    with ThreadPoolExecutor() as pool:
        pool.map(draw_value, bmpdata) 
    
def remove_color(text):
    colorlesstext = ""
    colors = findOccurrences(text, "§")
    lastcode = 0
    for c in colors:
        code = text[c:c+2]
        if code in colorcodes.keys():
            colorlesstext = colorlesstext + text[lastcode:c]
            lastcode = c + 2
    
    return colorlesstext + text[lastcode:]
    
def findOccurrences(s, ch):
    return [i for i, letter in enumerate(s) if letter == ch]

ranks = {"YOUTUBER" : "§c[§fYOUTUBER§c] ", "ADMIN" : "§c[ADMIN] ", "MOD" : "§2[MOD] ", "HELPER" : "§9[HELPER] ", 
         "VIP" : "§a[VIP] ", "VIP_PLUS" : "§a[VIP§6+§a] ", "MVP" : "§b[MVP] ", "MVP_PLUS" : "§b[MVP{}+§b] ", 
         "MVP_PLUS_PLUS" : "§6[MVP{}++§6] ", "NON" : "§7"}      
def draw_playername(coords, image, size, playerdata):
    rank = playerdata["rank"]
    font = get_font(size)
    draw = ImageDraw.Draw(image)

    prefix = ranks[rank].format(playerdata["pluscolor"])
    name = f'{prefix}{playerdata["name"]}'
    
    return draw_text(draw, coords, name, font, shadow=True)
    
def draw_shadow(draw, coords, text, color, font):
    coords = (coords[0] + 3, coords[1] + 3)
    
    rgbcolor = tuple(int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
    rgbcolor = (int(rgbcolor[0]/4), int(rgbcolor[1]/4), int(rgbcolor[2]/4))
    color = '#%02x%02x%02x' % rgbcolor
    
    draw.text(coords, text, fill=color, font=font)

def draw_head(image, coords, headimage, size, rotation = 0, mirror=False, oriantation=Oriantation.LEFT):
    draw_object(image, coords, headimage, size, rotation, False, oriantation)
    
def draw_body(image, coords, bodyimage, size, rotation = 0, mirror=False, oriantation=Oriantation.LEFT):
    draw_object(image, coords, bodyimage, size, rotation, False, oriantation)

def draw_object(image, coords, addimage, size, rotation = 0, mirror=False, oriantation=Oriantation.LEFT): 
    if addimage is False:
        return False
    
    addimage = addimage.resize(size)
    coords = oriant_coords(coords, addimage.width, oriantation)
    if mirror is True:
        addimage = addimage.transpose(Image.FLIP_LEFT_RIGHT)
    
    addimage = addimage.rotate(rotation, resample=Image.BICUBIC, expand=True)
    image.paste(addimage, coords, addimage)
       
def draw_guild(image, coords, fontsize, guild, oriantation=Oriantation.LEFT):
    font = get_font(fontsize)
    draw = ImageDraw.Draw(image)
    
    width = font.getsize("Guild:")[0] + 9 + font.getsize(remove_color(guild))[0]
    coords = oriant_coords(coords, width, oriantation)
    
    draw_text(draw, coords, "Guild:", font, color="#00AA00", shadow=True)
    coords = (coords[0] + font.getsize("Guild:")[0] + 9, coords[1])
    draw_text(draw, coords, guild, font, shadow=True)
    
def draw_status(image, coords, fontsize, status, oriantation=Oriantation.LEFT):
    font = get_font(fontsize)
    draw = ImageDraw.Draw(image)
    
    width = font.getsize("Status:")[0] + 9 + font.getsize(remove_color(status))[0]
    coords = oriant_coords(coords, width, oriantation)
    
    draw_text(draw, coords, "Status:", font, color="#AAAAAA", shadow=True)
    coords = (coords[0] + font.getsize("Status:")[0] + 9, coords[1])
    draw_text(draw, coords, status, font, shadow=True)
        
def oriant_coords(coords, width, oriantation):
    if oriantation == Oriantation.RIGHT:
        coords = (int(round(coords[0] - width, 0)), coords[1])
    elif oriantation == Oriantation.CENTER:
        coords = (int(round(coords[0] - (width/2), 0)), coords[1])
    return coords

def draw_network_level(image, coords, fontsize, level, oriantation=Oriantation.LEFT): 
    font = get_font(fontsize)
    level = str(level)
    draw = ImageDraw.Draw(image)
    
    width = font.getsize("Level:")[0] + 9 + font.getsize(level)[0]
    coords = oriant_coords(coords, width, oriantation)
    
    draw_text(draw, coords, "Level:", font, color="#FFFF55", shadow=True)
    coords = (coords[0] + font.getsize("Level:")[0] + 9, coords[1])
    draw_text(draw, coords, level, font, color="#00FFFF", shadow=True)
          
def draw_discord(image, coords, author, profile, oriantation=Oriantation.LEFT):
    font = ImageFont.truetype(from_fonts("Roboto.ttf"), 20)
    width = font.getsize(str(author))[0] + 26 + 32
    
    if oriantation == Oriantation.RIGHT:
        coords = (coords[0] - width, coords[1])
    elif oriantation == Oriantation.CENTER:
        coords = (coords[0] - (width/2), coords[1])
    
    if profile is False:
        draw = ImageDraw.Draw(image)
        draw.text(coords, str(author), fill="white", font=font)
        return 
    
    profile = profile.resize((26, 26))
    
    bigsize = (profile.size[0] * 3, profile.size[1] * 3)
    mask = Image.new("L", bigsize, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0,0) + bigsize, fill=255)
    mask = mask.resize(profile.size, Image.ANTIALIAS)
    profile.putalpha(mask)
    
    image.paste(profile, coords, profile)
    coords = (coords[0] + 32, coords[1] + 2)
    
    draw = ImageDraw.Draw(image)
    draw.text(coords, str(author), fill="white", font=font)
            
def combine_images(bg, fg):
    """ https://stackoverflow.com/questions/5324647/how-to-merge-a-transparent-png-image-with-another-image-using-pil """
    bg.paste(fg, (0,0), fg)
    return bg
