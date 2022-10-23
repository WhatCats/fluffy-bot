'''
Created on Mar 30, 2021

@author: Josef
'''
import asyncio

from command.decorators import needs_data
from main.datamanager import remove
from main.player_manager import get_author_player, remove_player
from command.errors import InvalidSyntax, CommandError

@needs_data
async def unlink_command(ctx, _, __):
    bot = ctx.bot
    
    if len(ctx.message.content) > 7:
        raise InvalidSyntax(f'Usage: `+unlink`.')
    
    player = get_author_player(ctx.author.id)
    if player is False:
        raise CommandError(f'You have not **linked** your **discord account** with your **minecraft account** yet. To do so use the **"+link"** command.')
    
    uuid = player.uuid
    discord = str(ctx.author)
    
    def check(m):
        return m.content.lower() in ("y", "yes", "n", "no") and m.author == ctx.author and m.channel == ctx.channel
    
    await ctx.send(f'Are you sure you wish to **unlink** your discord account **"{discord}"** **from** your minecraft account **"{uuid}"**? All data gatherd will be **deleted**. **[y/n]**')
    
    try:
        msg = await bot.wait_for("message", check=check, timeout=30)
    except asyncio.TimeoutError:
        await bot.send("Canceled.")
        return
            
    if msg.content.lower() in ("y", "yes"):
        remove_player(uuid)
        remove(uuid)
        await bot.send(f'Succesfully **unlinked** discord account **"{discord}"** **from** minecraft account **"{uuid}"**.')
    else:
        await bot.send("Canceled.")
        