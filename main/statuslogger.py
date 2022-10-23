'''
Created on May 2, 2021

@author: Josef
'''
import asyncio
from datetime import datetime, timezone
import math
import string

from discord.colour import Colour
from discord.embeds import Embed
from discord.errors import NotFound
from emoji.core import emojize


statuses = {}
normalimage = "https://cdn.discordapp.com/attachments/834051034916585512/839477996632408084/normal.png"
warningimage = "https://cdn.discordapp.com/attachments/834051034916585512/839478271225102336/warning.png"
errorimage = "https://cdn.discordapp.com/attachments/834051034916585512/839478283133255690/error.png"

def get_status(statusid):
    if statusid in statuses:
        return statuses[statusid]
    return False

def get_width(st):
    size = 0
    for s in st:
        if s in 'lij|\' ': size += 37
        elif s in '![]fI.,:;/\\t': size += 50
        elif s in '`-(){}r"': size += 60
        elif s in '*^zcsJkvxy': size += 85
        elif s in 'aebdhnopqug#$L+<>=?_~FZT' + string.digits: size += 95
        elif s in 'BSPEAKVXY&UwNRCHD': size += 112
        elif s in 'QGOMm%W@': size += 135
        else: size += 50
    return size

def get_title(title, size=4200):
        length = get_width(title)
        if length < size:
            title += (" " * math.floor((size - length) / 37))
        title += "\u200b"
        return title
      
class CommandStatus():
    def __init__(self, ctx):
        self.ctx = ctx
        self.id = ctx.message.id
        self.timestamp = datetime.now(timezone.utc)
        self.steps = []
        self.warnings = []
        self.infos = []
        self.error = None
        self.currentstatus = "Initializing command"
        
        self.embed = Embed(title="Your command is being processed ...", colour=Colour.green())
        self.format_embed(self.embed)
        self.msg = None
 
        statuses[self.id] = self
        
    async def show(self, ctx):
        self.msg = await ctx.reply(embed=self.embed, mention_author=False)
    
    def add_footer(self, embed):
        embed.timestamp = self.timestamp
        author = self.ctx.message.author
        
        embed.set_footer(text=f"Requested by {author.name} • Created by WhatCats", icon_url=author.avatar_url)
        return embed
        
    def format_embed(self, embed, addfield=True, thumbnail=normalimage):
        self.add_footer(embed)
        if addfield:
            embed.add_field(name="Currently", value=f"{self.currentstatus} **...**")
        embed.set_thumbnail(url=thumbnail)
        return embed
        
    async def reload_embed(self, addfield=True, thumbnail=normalimage):
        if self.msg is None:
            return
        
        self.format_embed(self.embed, addfield=addfield, thumbnail=thumbnail)
        await self.msg.edit(embed=self.embed)
    
    def get_description(self):
        if len(self.steps) == 0:
            return ""
        
        description = ""
        for emoji, text in self.steps:
            description += emojize(f"\n{emoji}    {text}", use_aliases=True)
        
        return description
        
    async def set(self, status):
        description = self.get_description()
        self.steps.append((":white_check_mark:", status))
        self.currentstatus = status
        
        self.embed = Embed(description=description, title=self.embed.title, colour=self.embed.colour)
        await self.reload_embed()
            
    async def exception(self, exception, unexpected):
        if len(self.steps) > 0: self.steps.append((":x:", self.steps.pop(-1)[1]))
        description = self.get_description()
        self.error = str(exception)
        
        if len(description) == 0: 
            self.embed = Embed(description=str(exception), colour=Colour.from_rgb(255, 0, 0), title="Command could not execute")
            await self.reload_embed(addfield=False, thumbnail=errorimage)
            await self.fold()
            return 
        
        if unexpected:
            self.embed = Embed(description=description, colour=Colour.from_rgb(255, 0, 0), title="An unexpected error has occurred")
        else:
            self.embed = Embed(description=description, colour=Colour.from_rgb(255, 0, 0), title="An error has occurred")
        self.embed.add_field(name="Error", value=str(exception))
        await self.reload_embed(addfield=False, thumbnail=errorimage)
        await self.fold()
    
    async def fold(self):
        if self.id in statuses:            
            del statuses[self.id]
            
        asyncio.create_task(self.log_embed())
             
    async def warning(self, warning, reason):
        self.steps.append((":warning:", warning))
        self.warnings.append((warning, reason))
        description = self.get_description()
        
        self.embed = Embed(description=description, title=self.embed.title, colour=Colour.gold())
        await self.reload_embed(thumbnail=warningimage)
        
    async def info(self, msg):
        self.infos.append(msg)
           
    async def log_embed(self):
        if self.msg is None:
            return
        try:
            embed = self.msg.embeds[0]
            thumbnail = embed.thumbnail.url
            embed = Embed(description=embed.description, title="Command was processed", colour=embed.colour)
            #string = re.sub(r'([_*~`|])', r'\\\1', self.ctx.message.content)
            embed.add_field(name = "Command", value = f"`{self.ctx.message.content}`")
            if len(self.infos) > 0:
                embed.add_field(name = "Infos", value = "\n".join([f"`{info}`" for info in self.infos]))
            if not self.error is None:
                embed.add_field(name="Error", value=self.error)
            embed.set_thumbnail(url=thumbnail)
            self.add_footer(embed)
            msg = await self.ctx.bot.get_channel(839218712576917524).send(embed=embed)
            return msg
        except Exception:
            return False
    
    def get_content(self): 
        content = None
        if len(self.warnings) == 1:
            warning, reason = self.warnings[0]
            content = emojize(f":warning: **{warning}** ({reason})")
        elif len(self.warnings) > 0:
            content = emojize(f":warning: **Warnings** :warning:")
            for warning, reason in self.warnings:
                content += emojize(f"\n `{warning} ({reason})`")
        
        if len(self.infos) == 1:
            info = self.infos[0]
            if content is None: 
                content = f":grey_exclamation: *{info}*"
            else:
                content += f"\n:grey_exclamation: *{info}*"
        elif len(self.infos) > 0:
            if content is None: 
                content = f":grey_exclamation: *Infos* :grey_exclamation:"
            else:
                content += f"\n:grey_exclamation: *Infos* :grey_exclamation:"
                       
            for message in self.infos:
                content += emojize(f"\n `{message}`")
                   
        return content
             
    async def completed(self, embed=None, file=None):   
        if self.msg is None:
            return
          
        try:
            if embed is None and file is None:
                await self.fold()
                await self.msg.delete()
            elif embed is True:
                await self.fold()
                return self.msg
            else:
                self.add_footer(embed)
                content = self.get_content()
                
                await self.fold()
                await self.msg.edit(content=content, embed=embed, file=file)
                return self.msg
        except NotFound:
            pass
        