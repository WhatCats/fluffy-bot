'''
Created on Apr 20, 2021

@author: Josef
'''
from discord.embeds import Embed
import asyncio
from discord.colour import Colour
from datetime import datetime
import pytz

channelid = 834051034916585512
botid = 818121868288327711
callbacks = []

async def get_url(bot, image):
    try:
        msg = await bot.get_channel(channelid).send(content=str(datetime.now(pytz.timezone('Europe/Berlin'))), file=image)
        return msg.attachments[0].url
    except Exception:
        return False

class ReactionImage():
    def __init__(self, emojis, author, timestamp, colour=Colour.default(), initialindex=0):
        self.emojis = emojis
        self.author = author
        self.msgid = None
        self.timestamp = timestamp
        self.colour = colour
        callbacks.append(self.on_reaction)
        
        if len(emojis) == 0:
            return
        
        #values_view = emojis.values()
        #value_iterator = iter(values_view)
        #self.embed = self.make_embed(next(value_iterator))
        self.embed = self.make_embed(list(emojis.values())[initialindex])
    
    def make_embed(self, imageurl):
        embed = Embed(colour=self.colour)
        embed.timestamp = self.timestamp
        embed.set_footer(text=f"Requested by {self.author.name}", icon_url=self.author.avatar_url)
        embed.set_image(url=imageurl)
        return embed
    
    async def on_reaction(self, reaction, user):
        if reaction.message.id != self.msgid:
            return
        
        if user.id == botid:
            return
 
        if reaction.emoji in self.emojis:
            embed = self.make_embed(self.emojis[reaction.emoji])
            await reaction.message.edit(embed=embed)
        await reaction.remove(user)
                       
    async def send(self, channel, msg=None):  
        if msg is None:
            msg = await channel.send(embed=self.embed)
        
        async def add_emoji(emoji, imageurl):
            await msg.add_reaction(emoji)
            embed = self.make_embed(imageurl)
            await msg.edit(embed=embed)
        
        calls = []
        for emoji, imageurl in self.emojis.items(): 
            calls.append(add_emoji(emoji, imageurl))
        await asyncio.gather(*calls)
        
        await msg.edit(embed=self.embed)    
        self.msgid = msg.id
        return msg
    
async def check_reactions(*args):
        for callback in callbacks:
            await callback(*args)
        