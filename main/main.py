'''
Created on Mar 7, 2021

@author: Josef
'''
import asyncio
from configparser import ConfigParser
import logging

import discord
from discord.ext import commands
from discord.ext.commands.errors import CommandInvokeError
from emoji.core import emojize

from command.commands import Commands
from command.errors import SafeMode, NotAdmin, BadServer, InputError, \
    UnexpectedError, InvalidSyntax, CommandError, CommandDisabled
from main.globals import set_bot
from main.image import check_reactions
from main.player_manager import get_author_player, PlayerManager
from main.statuslogger import get_status
from resources.path import resource_path


intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="+", intents=intents)
bot.add_cog(Commands(bot))
set_bot(bot)

config = ConfigParser()
config.read(resource_path("config.ini")) 
keys = config["KEYS"]

def connect_bot():
    bot.run(keys["discord"])
    
@bot.event
async def on_ready():
    logging.info("Fluffy Bot is ready.")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, 
                                name=emojize('api.hypixel.net :eyes:', use_aliases=True)))
    
    #e = discord.Embed(title="test")
    #e.set_image(url=r'https://cdn.discordapp.com/attachments/834051034916585512/854495214042873866/image.png')
    
    #f1 = discord.File(resource_path("image2.png"), filename="image.png")
    #f2 = discord.File(resource_path("image.png"), filename="image.png")
    #f3 = discord.File(resource_path("image.png"), filename="image.png")
    
    #asyncio.create_task(bot.get_channel(799654956042813523).send(file=f1))
    #asyncio.create_task(bot.get_channel(799654956042813523).send(file=f2))
    #asyncio.create_task(bot.get_channel(799654956042813523).send(file=f3))

@bot.event
async def on_message(message):
    if message.author.bot:
        #Ignore messages from bots
        return
    
    channel = message.channel
    if not isinstance(channel, discord.DMChannel):
        #Ignore messages that are not dms
        await bot.process_commands(message)
        return
    
    authorid = message.author.id
    pm = get_author_player(authorid)
    if not isinstance(pm, PlayerManager):
        #Ignore unlinked discord users
        return
    
    stopdms = ("shutup", "SHUTUP", "shut up", "SHUT UP", "fuck off", "fuckoff", "leave", "quite", "stop")
    startdms = ("JK", "jk", "join", "start", "START", "msgme", "gimme")
    
    msg = message.content
    logging.info(f'New private message from {message.author.name}: {msg}')
    if msg in stopdms:
        
        if pm.dodms is True:
            pm.set_dodms(False)
            await channel.send('I will no longer message you your game summarys.')
        else:
            await channel.send('I have already stoped messaging you your game summarys.')
        
    elif msg in startdms:
        
        if pm.dodms is False:
            pm.set_dodms(True)
            await channel.send('I will start messaging you your game summarys again.')
        else:
            await channel.send('I will already message you your game summarys.')
        
    
    
@bot.event
async def on_disconnect():
    logging.info("Disconnected from Fluffy Bot.")
    
@bot.event
async def on_connect():
    logging.info("Connected to Fluffy Bot.")

@bot.event
async def on_reaction_add(reaction, user):
    await check_reactions(reaction, user)
       
@bot.event
async def on_command_error(ctx, error):
    unexpected = False
    
    if isinstance(error, BadServer):
        return
    elif isinstance(error, commands.errors.CommandNotFound):
        exception = "That command does not exist for a list of commands type `+help`**.**"
    elif isinstance(error, commands.errors.MissingRequiredArgument):
        exception = f"This command is missing the argument `<{error.param}>`**.**"
    elif isinstance(error, SafeMode):
        exception = "Only admins can run commands at the moment."
    elif isinstance(error, CommandDisabled):
        exception = "This command was disabled by a administrator."
    elif isinstance(error, InvalidSyntax):
        exception = f"Invaild command syntax. {error.corect}"
    elif isinstance(error, NotAdmin):
        exception = "You must be a bot admin to run this command."
    elif isinstance(error, InputError) or isinstance(error, CommandError):
        exception = error.msg
    elif isinstance(error, UnexpectedError):
        exception = error.msg
        unexpected = True
    elif isinstance(error, CommandInvokeError):
        error = error.original
        exception = f'An unexpected error occurred during a command ({error.__class__.__name__}: {error}).' 
        unexpected = True
    else:
        exception = f'An unexpected error occurred during a command ({error.__class__.__name__}: {error}).' 
        unexpected = True
    
    cmdstatus = get_status(ctx.message.id)
    if cmdstatus is False:
        await ctx.send(exception)
    else:
        await cmdstatus.exception(exception, unexpected)
        
    if unexpected:  
        try:
            raise error
        except:
            logging.exception(f'An unexpected error occurred during a command')
            