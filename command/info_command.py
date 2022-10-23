'''
Created on Jun 14, 2021

@author: Josef
'''
from discord.colour import Colour
from discord.embeds import Embed


thumbnail = 'https://cdn.discordapp.com/attachments/834051034916585512/853966480675700736/info.png'
color = Colour.from_rgb(0, 126, 255)

async def info_command(ctx, *_):
    
    title = 'How to use Fluffybot?'
    description='Fluffybot is a bot designed by WhatCats made primarily for stats projections, although it can also stats check people. ' \
                'The bot will collect game data of users who have linked their Minecraft and Discord account. ' \
                'The bot has already undergone lots of testing but still may occasionally report unexpected errors. ' \
                'These errors, depending on their severity, can be reported to WhatCats as well as suggestions for ' \
                'future features or improvement of current features. For proper use of the bot please carefully read through these instructions.'
    
    embed = Embed(title=title, description=description, colour=color)
    embed.set_thumbnail(url=thumbnail)
    
    embed.add_field(
        inline = False,
        name = 'Linking your MC & Discord with Hypixel', 
        value = 'If you wish for Fluffybot to be able to give you stats projections you need to link Fluffybot with your Minecraft account. '
                'In order to do so you first need to link your Minecraft & Discord account with **Hypixel**. ' \
                'To do this log on to Hypixel and right click `My Profile` (your head) then in `Social Media` settings click `Discord` and paste your Discord username in chat. ' \
    )
    
    embed.add_field(
        inline = False,
        name = 'Linking Fluffybot with your MC account',
        value = 'Once you have linked your Minecraft and Discord account you can use ' \
                'the `+link ign=<your ign> resettime=<your reset time> timezone=<your timezone>` where *<your reset time>* is the hour at which your day usually ends (number between 0-23), ' \
                'and *<your timezone>* is a timezone from the tz database. To get all timezones in your country use the `+timezones <countrycode(2/3 digit ISO)>` command. ' \
                'After a successful linkage you can use the keyword `me` in commands to refer to your Minecraft account. ' \
                'For the best projection results please make sure that in `My Profile` (Your head) -> `Settings & Visibility` -> `API Settings` you have `Recent Games` enabled. ' \
                'That way individuell games can be tracked and saved for later calculations.'
    )
    
    embed.add_field(
        inline = False,
        name = 'Stats Projections',
        value = 'Once your account is linked the bot can calculate duels stats projections for you. ' \
                'Simply use the `+projection <gamemode>` command where *<gamemode>* is a type of duels, and specify parameters for the projeciton (wins=<wins> wlr=<wlr> days=<days>). ' \
                'Example: `+projection bridge wins=5000`. If multiple parameters are specified (`+projection bridge wins=5000 days=5`) the one that would occur first is used. ' \
                'Pay attention to the accuracy of the projections as it will be very low after first linking your account, but will increase the longer your account is linked.'
    )
    
    embed.add_field(
        inline = False,
        name = 'Stats checking',
        value = 'The bot can also stats check in skywars, bedwars, duels using `+s <player ign> <gamemode>` similar to Blitzbot but with pretty images. ' \
                'Example (if your account is linked): `+s me bridge`.'
    )
    
    embed.add_field(
        inline = False,
        name = 'Bot private messaging you',
        value = 'The bot stores lots of your game data while your playing on Hypixel for calculating stats projections. ' \
                'The bot will message you a summary of your games after they have completed by default (This could take up to a day to take effect after linking your account). ' \
                'If you wish to stop this behavior just message the bot `stop` or if you are a little more blunt `shut up` or `fuck off`. ' \
                'If you wish to resume this behavior try `start` or if you hurt the bots feelings you may want to hit it with a `jk`.'
    )
    
    await ctx.send(embed=embed)
    
    
    