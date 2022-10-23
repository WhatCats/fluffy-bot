'''
Created on Mar 7, 2021

@author: Josef
'''
import asyncio
import atexit
from datetime import datetime
import fnmatch
import logging
import os
import sys
from time import sleep

from aiohttp.client_exceptions import ClientConnectionError

from api.hypixel_api import get_init_stats
from main.datamanager import restore_all
from main.logger import setup_log
from main.main import connect_bot
from main.player_manager import PlayerManager
from main.ignore_error import ignore_aiohttp_ssl_error
from main.globals import set_restored

async def test():
    _, stats = await get_init_stats('2ba4678444f84983bc0e10d09b297900')
    pm = PlayerManager(stats, '2ba4678444f84983bc0e10d09b297900', 568427070020124672, 'europe/berlin', 3)
    await pm.stats.force_start()
    set_restored(True)
    
def when_done(fut):
    try:
        fut.result()
    except asyncio.CancelledError:
        pass
    except Exception:
        logging.exception(f"An unexpected error occurred.")
        sys.exit(0)

try:
    
    loop = asyncio.get_event_loop()
    
    ignore_aiohttp_ssl_error(loop)
    
    loop.create_task(setup_log())
    task = loop.create_task(restore_all())
    
    task.add_done_callback(when_done)
    #loop.create_task(test())
    
    connect_bot()
    
except KeyboardInterrupt:
    logging.info("------- App shutdown -------")
except ClientConnectionError:
    logging.exception(f"Unable to connect to the bot at the moment.")
except Exception as e:
    logging.exception(f"An unexpected error occurred: {e}")
