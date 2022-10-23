'''
Created on Apr 6, 2021

@author: Josef
'''
from _io import StringIO
from configparser import ConfigParser
from copy import copy
import json

import discord
from discord.ext import commands
from discord.file import File
import yaml

from command.errors import SafeMode, InvalidSyntax, NotAdmin, InputError, \
    BadServer, CommandDisabled
from command.info_command import info_command
from command.link_command import link_command
from command.stats_command import stats_command
from command.statsat_command import statsat_command
from command.unlink_command import unlink_command
from main.player_manager import get_players, get_author_player
from main.statuslogger import CommandStatus
from resources.path import resource_path
from command.tz_commnad import tz_command
from main.globals import is_restored


config = ConfigParser()
config.read(resource_path("config.ini")) 
config = config["SETTINGS"]
botadmins = [int(e.strip()) for e in config["admins"].split(',')]

def check_admin(ctx):
    if not is_admin(ctx.author):
        raise NotAdmin(ctx.author)
    return True
    
def check_data(_):
    if not is_restored():
        raise InputError(f'Player data is not restored yet. Please try again in a moment.')    
    return True
    
class Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.help_command.cog = self
        self.sudo_commands = []
        
    async def cog_check(self, ctx):
        config = ConfigParser()
        config.read(resource_path("config.ini")) 
        config = config["SETTINGS"]
        
        if config.getboolean('testversion') and ctx.guild.id != 799654955139989514:
            raise BadServer(ctx.guild.id)
        
        if not config.getboolean('testversion') and ctx.guild.id == 799654955139989514:
            raise BadServer(ctx.guild.id)
        
        safemode = config.getboolean('safemode')
        enabled = json.loads(config.get("enabledcommands"))

        sudocommand = False
        if ctx.message.id in self.sudo_commands:
            sudocommand = True
            self.sudo_commands.remove(ctx.message.id)
            
        if safemode and not (is_admin(ctx.author) or sudocommand):
            raise SafeMode(ctx.author)
        
        if not ctx.command.name in enabled and not (is_admin(ctx.author) or sudocommand):
            raise CommandDisabled(ctx.command)
        
        if ctx.message is ctx:
            return True
    
        if await get_params(ctx.message.content) is False:
            raise InvalidSyntax()
    
        return True
    
    async def wraper(self, ctx):
        args, params = await get_params(ctx.message.content)
        return ctx, args, params
    
    @commands.command(
        help="Returns a list of all timezones in the given country. They can then be used in the +link command.",
        brief="Prints a list of timezones in country.",
        aliases=("tz",)
    )
    async def timezones(self, ctx): 
        args = await self.wraper(ctx)
        await tz_command(*args)
    
     
    @commands.command(
        help="Displays current stats of a player. Usage: +s <player> <gamemode>",
        brief="Shows player stats.",
        aliases=("s",)
    )
    async def stats(self, ctx): 
        commandstatus = CommandStatus(ctx)
        await commandstatus.show(ctx)
        
        args = await self.wraper(ctx)
        await stats_command(*args)
     
      
    @commands.command(
        help="Shows the current state of the linkage. Usage: +status",
        brief="Shows linkage state.",
        aliases=("linkstatus",)
    )
    @commands.check(check_data)
    async def status(self, ctx): 
        async with ctx.typing():
            pm = get_author_player(ctx.author.id)
            if pm is False:
                await ctx.channel.send("This discord account has not been linked with a minecraft account yet.") 
                return
            
            with StringIO() as f:
                yaml.dump({"Tasks" : pm.stats.get_status(), "PlayerData" : {"Discord" : pm.discord, "Uuid" : pm.uuid, "Timezone" : pm.timezone, "Resettime" : pm.resettime}, "StatsData" : pm.stats.summerized()}, f)  
                f.seek(0)
                await ctx.channel.send(file=File(fp=f, filename="data.yaml"))   
          
    @commands.command(
        help="Unlinks Discord and Minecarft account. Usage: +unlink",
        brief="Unlinks Discord & Minecraft account.",
        aliases=("delink",)
    )
    async def unlink(self, ctx): 
        async with ctx.typing():
            args = await self.wraper(ctx)
            await unlink_command(*args)
          
          
    @commands.command(
        help="Links Discord and Minecarft account. Usage: +link ign=<ign> timezone=<timezone> resettime=<resettime>",
        brief="Links Discord & Minecraft account.",
        aliases=("l",)
    )
    async def link(self, ctx): 
        async with ctx.typing():
            args = await self.wraper(ctx)
            await link_command(*args)
          
            
    @commands.command(
        help="Creates a stats projection based on the command parameters. Usage: +projection <gamemode> wins=<wins> wlr=<wlr> time=<days>",
        brief="Creates a stats projection.",
        aliases=("statsat", "proj")
    )
    async def projection(self, ctx): 
        commandstatus = CommandStatus(ctx)
        await commandstatus.show(ctx)
        
        args = await self.wraper(ctx)
        await statsat_command(*args)
        
        
    @commands.command(hidden=True)
    @commands.check(check_admin)
    async def sudo(self, ctx, User: discord.Member, *, message):
        new_message = copy(ctx.message)
        new_message.author = User
        
        new_message.content = ctx.prefix + message
        
        self.sudo_commands.append(ctx.message.id)
        await self.bot.process_commands(new_message)
       
        
    @commands.command(hidden=True)
    @commands.check(check_admin)
    async def info(self, ctx):
        args = await self.wraper(ctx)
        await info_command(*args)
     
        
    @commands.command(hidden=True)
    @commands.check(check_admin)
    @commands.check(check_data)
    async def forcestart(self, ctx, User: discord.Member):
        pm = get_author_player(User.id)
        if pm is False:
            raise InputError("User is not linked.")
        
        result = await pm.stats.force_start()
        if result is False:
            raise InputError("Tasks already started.")
        await ctx.send("Started tasks for User.")
        
        
    @commands.command(hidden=True)
    @commands.check(check_admin)
    @commands.check(check_data)
    async def reset(self, ctx, User: discord.Member):
        pm = get_author_player(User.id)
        if pm is False:
            raise InputError("User is not linked.")
        
        pm.stats.reset()
        await ctx.send("Tasks reset for User.")
        
        
    @commands.command(hidden=True)
    @commands.check(check_admin)
    async def sudoall(self, ctx, *, message):
        for member in ctx.guild.members:
            new_message = copy(ctx.message)
            new_message.content = ctx.prefix + message
            new_message.author = member
            
            self.sudo_commands.append(ctx.message.id)
            await self.bot.process_commands(new_message)
            
    @commands.command(hidden=True)
    @commands.check(check_admin)
    @commands.check(check_data)
    async def sudolinked(self, ctx, *, message):
        for _, pm in get_players().items():
            
            author = ctx.guild.get_member(pm.discord)
            if author is None:
                continue
            
            new_message = copy(ctx.message)
            new_message.content = ctx.prefix + message
            new_message.author = author
            
            self.sudo_commands.append(ctx.message.id)
            await self.bot.process_commands(new_message)

async def get_params(message):
    lst = message.strip().replace("\\", "").split()
    del lst[0]
    message = " ".join(lst)
    
    if message.startswith("=") or message.endswith("="):
        return False
    
    params = {}
    while len(find_occurrences(message, '=')) != 0:
        equals = find_occurrences(message, "=")[0]
        
        left = message[:equals]
        left = left.split()[::-1]
        
        right = message[equals+1:]
        right = right.split()
        
        params[left.pop(0).strip().lower()] = right.pop(0).strip()
        
        message = " ".join(left[::-1] + right)
    
    args = [arg.strip() for arg in message.split()]
    return args, params

def find_occurrences(s, ch):
    return [i for i, letter in enumerate(s) if letter == ch]

def is_admin(author):
        if not author.id in botadmins:
            return False
        return True
    