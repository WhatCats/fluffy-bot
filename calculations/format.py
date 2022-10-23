'''
Created on Apr 2, 2021

@author: Josef
'''
from datetime import timedelta, datetime

def format_time(secs, hourname=" hours", minname=" minutes", secname=" seconds"):
    if secs == "N/A" or secs is False:
        return "N/A"
    
    secs = int(round(secs,0))
    hours = 0
    mins = 0
    while secs >= 60:
        mins += 1
        secs -= 60
        
    while mins >= 60:
        hours +=1
        mins -= 60
    
    secs = int(round(secs, 0))
    
    if hours >= 100:
        if secs >= 30:
            mins += 1
        if mins != 0:
            secs = 0
    
    if hours >= 100000:
        if mins >= 30:
            hours += 1
        mins = 0 
        secs = 0   
            
    output = ''
    if hours != 0:
        output = f'{hours}{hourname}'
        
    if mins != 0:
        output = f'{output} {mins}{minname} '
        
    if secs != 0:
        output = f'{output} {secs}{secname}'
    
    return output.strip()

def format_ratio(turm1, turm2, percent=False):
    if turm1 == 0 and turm2 >= 0:
        ratio = 0
    elif turm1 >= 0 and turm2 == 0:
        ratio = "∞"
    elif turm1 == 0 and turm2 == 0:
        ratio = 0
    else:
        if percent is True:
            ratio = str(int(round((turm1 / turm2) * 100, 0))) + "%"
        else:
            ratio = round((turm1 / turm2), 1)
    
    return ratio

def format_discord(discord):
    if discord is None or discord is False:
        return "No discord."
    return discord
    
def calc_date(days=0, minutes=0, seconds=0, form="%m/%d/%Y"):
    return (datetime.today() + timedelta(days=days, minutes=minutes, seconds=seconds)).strftime(form)
          
def wrap_extra_stats(bedwarsdata=None, duelsdata=None, skywarsdata=None, bridgedata=None):
    extra_stats = {}
    
    if not bedwarsdata is None:
        extra_stats["bedwars_fkdr"] = format_ratio(bedwarsdata["overall_final_kills"], bedwarsdata["overall_final_deaths"])
        extra_stats["bedwars_level"] = bedwarsdata["level"]
    
    if not duelsdata is None:
        extra_stats["duels_wins"] = duelsdata["overall_wins"]
        extra_stats["duels_wlr"] = format_ratio(duelsdata["overall_wins"], duelsdata["overall_losses"])
    
    if not skywarsdata is None:
        extra_stats["skywars_level"] = skywarsdata["level"]
        extra_stats["skywars_wlr"] = format_ratio(skywarsdata["overall_wins"], skywarsdata["overall_losses"])
        
    if not bridgedata is None:
        extra_stats["bridge_wins"] = bridgedata["overall_wins"]
        extra_stats["bridge_wlr"] = format_ratio(bridgedata["overall_wins"], bridgedata["overall_losses"])
    
    return extra_stats     
    