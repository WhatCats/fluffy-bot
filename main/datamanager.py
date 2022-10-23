'''
Created on Mar 7, 2021

@author: Josef
'''
import asyncio
import json
import logging
import os
from pathlib import Path
import random

from api.hypixel_api import get_init_stats
from main.globals import set_restored
from main.player_manager import PlayerManager
from resources.path import resource_path


statspath = resource_path("stats")

async def new_playermanager(uuid, timezone="utc", resettime=0):
    result, stats = await get_init_stats(uuid)
    wait = 0
    while result is False:
        wait += (10 + random.randint(0, 10))
        logging.info(f'[200] Unable to get player stats: {uuid}. {stats} Trying again in {wait} seconds.')
        await asyncio.sleep(wait)
        result, stats = await get_init_stats(uuid)
        
    if stats["discord"] == None:
        logging.warning(f"Restoration of mc account {uuid} aborted because no discord account linked.")
        return
        
    return PlayerManager(stats, uuid, stats["discord"], timezone, resettime)

def is_ghost_file(uuid):
    for filename in os.listdir(statspath):
        if filename.endswith(".json"): 
            uuid = filename[:-5]
            if uuid.endswith("_DEL"):
                return True
        
    return False
        
async def load_data(uuid, restore=False):
    filepath = os.path.join(statspath, f'{uuid}.json')
    restorepath = os.path.join(statspath, f'{uuid}_DEL.json')
    if not Path(filepath).is_file():
        if not restore or not Path(restorepath).is_file():
            return False
        
        os.rename(restorepath, filepath)
        logging.info("Hard restoring data of {0}".format(uuid))
    
    if os.path.getsize(filepath) == 0:
        logging.warning(f"File {filepath} is empty.")
        return await new_playermanager(uuid)
         
    with open(filepath, "rb") as f:
        restoredata = json.load(f)
    
    result, stats = await get_init_stats(uuid)
    wait = 0
    while result is False:
        wait += (10 + random.randint(0, 10))
        logging.info(f'[201] Waiting for player stats: {uuid}. {stats} Trying agian in {wait} seconds.')
        await asyncio.sleep(wait)
        result, stats = await get_init_stats(uuid)
        
    pm = PlayerManager(stats, restore=restoredata)
    
    logging.info("Restored data for: {0}".format(uuid))
    return pm

async def restore_all():
    tasks = []
    
    for filename in os.listdir(statspath):
        if filename.endswith(".json"): 
            uuid = filename[:-5]
            if uuid.endswith("_DEL"):
                continue
            
            tasks.append(load_data(uuid))
            
    data = await asyncio.gather(*tasks)
    set_restored(True)   
    
    return data
        
def remove(uuid):
    filepath = os.path.join(statspath, f'{uuid}.json')
    if not Path(filepath).is_file():
        return False
    
    os.rename(filepath, filepath[:-5] + "_DEL.json")
        