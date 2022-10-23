'''
Created on 12 Mar 2021

@author: Josef
'''
import asyncio
from concurrent.futures.thread import ThreadPoolExecutor

from discord.colour import Colour
from discord.embeds import Embed
from emoji.core import emojize

from api.hypixel_api import get_data
from api.other_apis import get_head, get_body
from api.util import multiple_requests, default_renders
from command.decorators import needs_data
from command.errors import InputError, CommandError
from duels import image as duels_image
from duels import projection as duels_projection
from main.gamemodes import Gamemode
from main.image import get_url
from main.player_manager import get_author_player
from main.statuslogger import get_status

@needs_data
async def statsat_command(ctx, args, params): 
    cmdstatus = get_status(ctx.message.id)
    await cmdstatus.set(emojize(":mag:  Checking command syntax"))
     
    if len(args) == 0:
        raise InputError(f'Missing required argument <gamemode>.\n Usage: `+projection <gamemode> wins=<wins> days=<days> ...`.')
    elif len(args) > 1:
        raise InputError(f'Too many arguments.\n Usage: `+projection <gamemode> wins=<wins> days=<days> ...`.')
    
    gamemode = Gamemode.from_string(args[0])
    if gamemode is False or gamemode is Gamemode.HYPIXEL:
        raise InputError(f'Invalid gamemode `{args[0]}`.')
       
    player = get_author_player(ctx.author.id)
    if player is False:
        raise CommandError(f'You first need to **link** your **discord account** with your **minecraft account**. To do so use the **+link** command.')
    
    posibleparams = {Gamemode.BEDWARS: ["wins", "wlr", "days", "fkdr", "level"],
                     Gamemode.DUELS: ["wins", "wlr", "days"], Gamemode.SKYWARS: ["wins", "wlr", "days"]}
    params = check_params(params, posibleparams[gamemode])
    
    await cmdstatus.set(emojize(":chart_with_upwards_trend:  Requesting player data from *api.hypixel.net*")) 
    result, currentdata = await get_data(player.uuid) 
    if result is False:
        raise CommandError(currentdata)
    
    if str(currentdata["discord"]) != str(ctx.author):
        raise CommandError(f"Please **relink** your discord account to your minecraft account, with hypixel, first.")
    
    await cmdstatus.set(emojize(":chart_with_downwards_trend:  Requesting skin renders from *mc-heads.net*")) 
    result, avatars = await multiple_requests(get_head(player.uuid), get_body(player.uuid))
    if result is False:
        await cmdstatus.warning("Unable to get skin renders at the moment", "*mc-heads.net* is unreachable")
        currentdata["head"], currentdata["body"] = default_renders()
    else:
        currentdata["head"], currentdata["body"] = avatars
    
    await cmdstatus.set(emojize(":pencil:  Calculating stats")) 
    data = calculate_projection(gamemode, args[0].upper(), player.stats, currentdata, **params)
    if isinstance(data, str):
        raise CommandError(data)
    
    imagecreator = get_creator(gamemode)
    
    if imagecreator is None:
        msg = await cmdstatus.completed(embed=True)
        await msg.edit(embed=None, file=None, content=':construction: There is no image creator for this yet :construction:\nHere are some numbers without any context:\n' + str(data))
        return
    
    if "accuracynum" in data:
        accuracy = data["accuracynum"]
        if accuracy < 10:
            await cmdstatus.warning("The accuracy of this projection is still very low.", "The accuracy will get higher the longer your account is linked.")
    
    await process_image(ctx, cmdstatus, imagecreator, data)
    
def calculate_projection(gamemode, gametype, data, currentdata, **kwargs):
    if gamemode == Gamemode.DUELS:
        return duels_projection.calculate_projection(data, gametype, currentdata, **kwargs)
    else:
        return data.get_stats(gamemode)

async def process_image(ctx, cmdstatus, imagecreator, data):
    await cmdstatus.set(emojize(":art:  Drawing Image(s)"))
    with ThreadPoolExecutor() as pool:
        loop = asyncio.get_running_loop()
        image = await loop.run_in_executor(pool, imagecreator, data)
    
    await cmdstatus.set(emojize(":package:  Packaging and sending files"))
    
    embed = Embed(colour=Colour.from_rgb(223, 9, 255))
    embed.set_image(url=await get_url(ctx.bot, image))
    
    await cmdstatus.completed(embed=embed)
        
def get_creator(gamemode):
    if gamemode == Gamemode.DUELS:
        return duels_image.draw_duels_projection
    
def is_number(value, comma=False):
    if comma is True:
        value = value.replace('.','',1)
        
    if value.isdigit():
        return True
    else:
        return False
       
def check_params(params, possiblekeys):
    for key, _ in params.items():
        if not key in possiblekeys:
            raise InputError(f"Unknown parameter `{key}`.")
    
    if len(params) == 0:
        raise InputError(f'This command needs atleast one parameter: `{", ".join(possiblekeys)}`.')
    
    if "wins" in params.keys():
        if is_number(params["wins"]):
            params["wins"] = int(params["wins"])
        else:
            raise InputError(f'Unkown amount of wins `{params["wins"]}`. It must be a **whole number**.')
        
    if "level" in params.keys():
        if is_number(params["level"]):
            params["level"] = int(params["level"])
        else:
            raise InputError(f'Unkown level `{params["level"]}`. It must be a **whole number**.')
            
    if "days" in params.keys():
        if is_number(params["days"]):
            params["days"] = int(params["days"])
        else:
            raise InputError(f'Unkown amount of days `{params["days"]}`. It must be a **whole number**.')
    
    if "wlr" in params.keys():
        if is_number(params["wlr"], comma=True):
            params["wlr"] = float(params["wlr"])
        else:
            raise InputError(f'Unkown W/L ratio `{params["wlr"]}`. It must be a **number**.')
        
    if "fkdr" in params.keys():
        if is_number(params["fkdr"], comma=True):
            params["fkdr"] = float(params["fkdr"])
        else:
            raise InputError(f'Unkown final K/D ratio `{params["fkdr"]}`. It must be a **number**.')
    
    return params
