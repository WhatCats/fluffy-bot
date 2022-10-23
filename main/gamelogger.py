'''
Created on May 26, 2021

@author: Josef
'''
import asyncio
from configparser import ConfigParser
import logging
import random

from discord.colour import Colour
from discord.embeds import Embed

from resources.path import resource_path
from main.globals import get_bot

channelid = 847098382413725707
thumbnail = 'https://cdn.discordapp.com/attachments/834051034916585512/853631677426040832/hypixelometer_5f6fca330c70f.png'
color = Colour.from_rgb(223, 9, 255)

async def log_game(pm, *args):
    async def try_send(pm, time, title, dmtitle, description, fields, dontdm):
        try:
            bot = get_bot()
            if bot is None:
                raise Exception('Bot is None')
            
            config = ConfigParser()
            config.read(resource_path("config.ini")) 
            config = config["SETTINGS"]
              
            embed = Embed(title=title, description=description, colour=color)
            dmembed = Embed(title=dmtitle, description=description, colour=color)
        
            embed.timestamp = dmembed.timestamp = time
            author = await bot.fetch_user(pm.discord)
            embed.set_footer(text=f"Played by {author.name} • Created by WhatCats", icon_url=author.avatar_url)
            dmembed.set_footer(text=f"Played by You", icon_url=author.avatar_url)
            
            embed.set_thumbnail(url=thumbnail)
            dmembed.set_thumbnail(url=thumbnail)
            
            if len(fields) > 0:
                value = ''
                for k, v in fields.items():
                    value += f'_{k}:_ `{v}`\n'
                
                embed.add_field(name="Summary", value=value)
                dmembed.add_field(name="Summary", value=value)
            
            try:
                if pm.dodms is True and not dontdm and config.getboolean('dmpeople') :
                    await author.send(embed=dmembed)
            except Exception:
                pass
            
            msg = await bot.get_channel(channelid).send(embed=embed)
            
            return True, msg
        except Exception as e:
            logging.exception("Unexpected Exception while logging game.")
            return False, e
    
    success, result = await try_send(pm, *args)
    wait = 0
    while success is False:
        wait += (10 + random.randint(0, 10))
        logging.info(f'[300] Unable to log game from {pm.uuid}. Trying again in {wait} seconds.')
        await asyncio.sleep(wait)
        success, result = await try_send(pm, *args)
        
    return result
        