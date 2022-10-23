'''
Created on Apr 5, 2021

@author: Josef
'''
import asyncio
from concurrent.futures.thread import ThreadPoolExecutor

from discord.colour import Colour
from discord.embeds import Embed
from emoji.core import emojize

from api.hypixel_api import get_data
from api.other_apis import get_uuid, get_head, get_body
from api.util import multiple_requests, default_renders
from bedwars import image as bedwars_image
from command.errors import InvalidSyntax, InputError, CommandError, \
    UnexpectedError
from duels import image as duels_image
from hypixel import image as hypixel_image
from main.gamemodes import Gamemode
from main.image import ReactionImage, get_url
from main.player_manager import get_author_player
from main.statuslogger import get_status
from skywars import image as skywars_image


async def stats_command(ctx, args, params):
    cmdstatus = get_status(ctx.message.id)
    await cmdstatus.set(emojize(":mag:  Checking command syntax"))
    
    if len(args) < 1 or len(args) > 2 or len(params) > 0:
        raise InvalidSyntax(corect=f'Usage: `+stats <player> <gamemode>`.')
    
    if len(args) == 1 or args[1].upper() in ("LATEST", "RECENT"):
        gamemode = gametype = None
    else:   
        if args[1].upper() != "ALL":
            gamemode = Gamemode.from_string(args[1])
            if gamemode is False:
                raise InputError(f'Invalid gamemode `{args[1]}`.')
            gametype = args[1]
        else:
            gamemode = gametype = "ALL"
    
    uuid = None
    ign = args[0]
    if ign == "me":
        pm = get_author_player(ctx.author.id) 
        if pm is False:
            await cmdstatus.warning("To have `me` refer to your account you need to link it", "**+link** to link your account")
        else:
            uuid = pm.uuid
    
    if uuid is None:        
        await cmdstatus.set(emojize(":mag:  Validating player ign with *api.mojang.com*"))    
        result, uuid = await get_uuid(ign)
        if result is False:
            raise CommandError(uuid)
        if uuid is None:
            raise CommandError(f'Unable to find a player with the name `{args[0]}`.')
    
    await cmdstatus.set(emojize(":chart_with_upwards_trend:  Requesting player data from *api.hypixel.net*")) 
    result, currentdata = await get_data(uuid) 
    if result is False:
        raise CommandError(currentdata) 
    
    recentgm = Gamemode.from_string(currentdata["latest"])
    if not recentgm is False and gamemode is None:
        gamemode = recentgm
        gametype = currentdata["latest"]
    
    await cmdstatus.set(emojize(":chart_with_downwards_trend:  Requesting skin renders from *mc-heads.net*")) 
    result, avatars = await multiple_requests(get_head(uuid), get_body(uuid))
    if result is False:
        await cmdstatus.warning("Unable to get skin renders at the moment", "*mc-heads.net* is unreachable")
        currentdata["head"], currentdata["body"] = default_renders()
    else:
        currentdata["head"], currentdata["body"] = avatars

    await process_image(ctx, cmdstatus, get_creator(gamemode), currentdata, gametype)
    #await cmdstatus.completed()
    #with StringIO() as fp:
        #yaml.dump(currentdata[Gamemode.DUELS], fp)
        #fp.seek(0)   
        #await ctx.send(file=discord.File(fp=fp, filename='stats.yaml'))
        
def get_creator(gamemode):
    if gamemode == Gamemode.BEDWARS:
        return bedwars_image.draw_bedwars_stats
    elif gamemode == Gamemode.DUELS:
        return duels_image.draw_duels_stats
    elif gamemode == Gamemode.SKYWARS:
        return skywars_image.draw_skywars_stats
    elif gamemode == "ALL":
        return bedwars_image.draw_bedwars_stats, skywars_image.draw_skywars_stats, duels_image.draw_duels_stats
    else:
        return hypixel_image.draw_hypixel_stats
    
async def process_image(ctx, cmdstatus, imagecreator, currentdata, gametype):
    await cmdstatus.set(emojize(":art:  Drawing Image(s)"))
    with ThreadPoolExecutor() as pool:
        loop = asyncio.get_running_loop()
        try:
            creators = [e for e in imagecreator]
        except TypeError:
            image = await loop.run_in_executor(pool, imagecreator, currentdata, gametype)
        else:
            image = await asyncio.gather(*[loop.run_in_executor(pool, creator, currentdata.copy(), gametype) for creator in creators])
    
    asyncio.create_task(cmdstatus.set(emojize(":package:  Packaging and sending files")))
    if isinstance(image, list):
        results = []
        for result in image:
            if isinstance(result, tuple):
                result = result[0] #dict
                for r in list(result.values()):
                    results.append(r)
            else:
                results.append(result)
        if len(results) >= 10:
            raise CommandError("Execution not possible.")
        
        nums = [':zero:',':one:',':two:',':three:',':four:',':five:',':six:',':seven:',':eight:',':nine:']
        image = dict(zip([emojize(num, use_aliases=True) for num in nums[:len(results)]], results)), 0
        
    if isinstance(image, tuple):
        files = {}
        async def add_file(emoji, file):
            url = await get_url(ctx.bot, file)
            if url is False:
                raise UnexpectedError("A unexpected error occured while making a url.")
            files[emoji] = url
         
        calls = []    
        for emoji, file in image[0].items():
            calls.append(add_file(emoji, file))
           
        await asyncio.gather(*calls)
        
        image = ReactionImage(files, ctx.author, cmdstatus.timestamp, colour=Colour.from_rgb(223, 9, 255), initialindex=image[1])
        msg = await cmdstatus.completed(embed=True)
        await image.send(ctx.channel, msg=msg)
        return
    
    colour = Colour.from_rgb(223, 9, 255)
    if isinstance(image, str): 
        s = image
        s = (s[:2020] + '..') if len(s) > 2020 else s
        embed = Embed(description=s, colour=colour)
        msg = await cmdstatus.completed(embed=embed)
        return
    
    imageurl = await get_url(ctx.bot, image)
    embed = Embed(colour=colour)
    embed.set_image(url=imageurl)
    msg = await cmdstatus.completed(embed=embed)
    