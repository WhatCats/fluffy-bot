'''
Created on June 17, 2021

@author: Josef
'''
from _io import StringIO
from datetime import datetime

from discord.file import File
import pycountry
import pytz

from command.errors import InvalidSyntax


async def tz_command(ctx, args, _):
    if len(args) != 1:
        raise InvalidSyntax('This command only takes one argument. Usage: `+timezones <countrycode>` (*<countrycode>*  as 2 or 3 digit ISO code)')
    
    countrycode = args[0].upper()
    if len(countrycode) == 2:
        try:
            country = pycountry.countries.get(alpha_2=countrycode)
        except Exception:
            raise InvalidSyntax(f'Your country code of `{countrycode}` is invalid.') 
    elif len(countrycode) == 3:
        try:
            country = pycountry.countries.get(alpha_3=countrycode)
        except Exception:
            raise InvalidSyntax(f'Your country code of `{countrycode}` is invalid.') 
    else:
        raise InvalidSyntax(f'`{args[0]}` is not a valid country code. Your country code should be of format: **2 or 3 digit ISO**.') 
    
    countrycode = country.alpha_2
    timezones = pytz.country_timezones[countrycode]
    display = {}
    for tz in timezones:
        now = datetime.now(pytz.timezone(tz))
        offset = now.utcoffset().total_seconds()/60/60
        display[str(tz)] = offset
        
    with StringIO() as fp:
        for key, value in display.items():
            fp.write(f'"{key}" • {value}\n')
        fp.seek(0)
        await ctx.channel.send(content=f'Here is list of timezones in **{country.name}**.\nFormat: `Timezone name` • `UTC offset`.\n The complete `timezone name` can be used with the `+link` command.', 
                               file=File(fp=fp, filename="timezones.txt"))
        
        