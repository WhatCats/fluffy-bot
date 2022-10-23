'''
Created on 13 Mar 2021

@author: Josef
'''
from configparser import ConfigParser

import pytz

from api.hypixel_api import get_init_stats
from api.other_apis import get_uuid
from command.decorators import needs_data
from command.errors import CommandError, InputError, InvalidSyntax
from main.datamanager import is_ghost_file, load_data
from main.player_manager import get_player, PlayerManager, get_author_player, \
    get_players
from resources.path import resource_path


config = ConfigParser()
config.read(resource_path("config.ini")) 
config = config["SETTINGS"]
PLAYER_CAP = int(config["playercap"])

@needs_data
async def link_command(ctx, args, params):
    if len(args) > 0:
        raise InvalidSyntax(f'Usage: `+link ign=<ign> resettime=<resettime> timezone=<timezone>`.')
    
    params = check_params(params, ["ign", "resettime", "timezone"])
    
    player = get_author_player(ctx.author.id)
    if player is False and "ign" not in params:
        raise InputError(f"Missing one required parameter: ign=*<ign>*.")
    
    extratext = ""
    if player is False:
        if len(get_players()) >= PLAYER_CAP:
            raise CommandError(f"They player limit of 30 has been reached. To extend the limit contact a bot administrator.") 
            
        ign = params["ign"]
        result, uuid = await get_uuid(ign)
        if result is False:
            raise CommandError(uuid)
        if uuid is None:
            raise CommandError(f'There is **no minecraft account** with the username `{ign}`.')
    
        extratext = f'For best possible projections please make sure that **"Recent Games"** is enabled in My Profile -> Settings -> API Settings.'
    else:
        uuid = player.uuid

    result, stats = await get_init_stats(uuid)
    if result is False:
        raise CommandError(stats)
        
    if str(stats["discord"]) != str(ctx.author):
        raise CommandError(f"Please **relink** your **discord account** to your **minecraft account**, with **hypixel**, first.")
        
    ign = stats["ign"]
    str1, str2, str3 = "was", "", ""
    if not get_player(uuid) is False:
        pm = get_player(uuid)
        if pm.discord == ctx.author.id:
            str1 = "is"
        pm.discord = ctx.author.id
            
        timezone = pm.timezone
        resettime = pm.resettime
            
        if "timezone" in params and pm.timezone != params["timezone"]:
            str2 = "now "
            pm.set_timezone(params["timezone"])
            timezone = params["timezone"]
            
        if "resettime" in params and pm.resettime != params["resettime"]:
            str3 = "now "
            pm.set_resettime(params["resettime"])
            resettime = params["resettime"]
                
        if str2 == "now " or str3 == "now ":
            pm.save_data()
            pm.stats.reset() 
                
        pm.save_data()
        
    else:
        timezone = "utc"
        resettime = 0
            
        if "timezone" in params:
            timezone = params["timezone"]
            
        if "resettime" in params:
            resettime = params["resettime"]
            
        if is_ghost_file(uuid):
            pm = load_data(uuid, restore=True)
            pm.timezone = timezone
            pm.resettime = resettime
        else:
            pm = PlayerManager(stats, uuid, ctx.author.id, timezone, resettime)
            
        if not "timezone" in params and not "resettime" in params:
            await ctx.send(f':warning: It is recomended you set your `timezone` and `resettime` to when your day usually ends, ' +  
                            'so that a day is better defined while calculating. (Use `+link timezone=<your timezone> resettime=<your resettime>`. ' +
                            'For *<your timezone>* you cna use the **2 DIGIT ISO** code of your country **or** a timezone from the list of **+timezones** command. ' +
                            'The *<your resettime>* should be a number between 0-23.')
            
        elif not "timezone" in params:
            await ctx.send(f':warning: Your resettime was set to {resettime} but since you did not give a timezone the default (UTC) is being used. ' +  
                            'If you wish to change this use `+link timezone=<your timezone>`. ' +
                            'For *<your timezone>* you cna use the **2 DIGIT ISO** code of your country **or** a timezone from the list of **+timezones** command.')
            
        elif not "resettime" in params:
            await ctx.send(f':warning: Your timezone was set to {timezone} but since you did not give a resettime the default (0) is being used. ' +  
                            'If you wish to change this use `+link resettime=<your resettime>`. ' +
                            'The *<your resettime>* should be a number between 0-23.')
          
    await ctx.send(f'Discord account `{ctx.author}` {str1} linked with minecraft account `{ign}`. The timezone is {str2}`{timezone}` and the resettime is {str3}`{resettime}`. ' +
                   f'If you wish to change any values simply type the **+link** command again. {extratext}')
        
def check_params(params, neededkeys):
    for key, _ in params.items():
        if not key in neededkeys:
            raise CommandError(f'Unknown parameter `{key}`.')
    
    if "timezone" in params:
        tz = params["timezone"] = params["timezone"].lower()
        try:
            pytz.timezone(tz)
        except Exception:
            raise CommandError(f'Unkown timezone `{tz}`. You can use the `+timezones <countrycode(2/3 digit ISO)>` command to get a list of timezones in your country.')
        
    if "resettime" in params:
        num = params["resettime"]
        if not num.isnumeric():
            raise CommandError(f"Unkown time `{num}`. It must be a **whole number**.")
        
        params["resettime"] = num = int(num)
        
        if num > 23 or num < 0:
            raise CommandError(f"Unkown time `{num}`. It must be a **valid time** (0-23).")
        
    return params
