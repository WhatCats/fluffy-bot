'''
Created on Apr 21, 2021

@author: Josef
'''
import asyncio
from datetime import datetime, timedelta
import fnmatch
import logging
import os
from pathlib import Path
import sys
import time

logspath = os.path.dirname(Path(__file__).resolve().parent)
logspath = os.path.join(logspath, "logs")
if not os.path.exists(logspath):
    os.makedirs(logspath)

MAX_LOGS = 10     
logformat = logging.Formatter('%(asctime)s %(levelname)s %(message)s', '%H:%M:%S')

def when_done(fut):
    try:
        fut.result()
    except asyncio.CancelledError:
        return
        
def remove_old():
    logs = {}
    for logfile in fnmatch.filter(os.listdir(logspath), '*.log'):
        try:
            date = datetime.strptime(logfile[:-4], '%Y%m%d')
        except Exception:
            logging.warning(f"Log file has invalid date: {logfile}")
            continue
    
        logs[date] = logfile
    
    while len(logs) > MAX_LOGS:
        oldestdate = min(logs.keys())
        oldestfile = logs[oldestdate]
        logging.info(f"Deleting old log file: {oldestfile}")
        os.remove(os.path.join(logspath, str(oldestfile)))
        del logs[oldestdate]

async def remove_later(file_handler):
    tomorrow = datetime.utcnow() + timedelta(1)
    midnight = datetime(year=tomorrow.year, month=tomorrow.month, 
                        day=tomorrow.day, hour=0, minute=0, second=0)
    delay = (midnight - datetime.utcnow()).seconds

    await asyncio.sleep(delay)
    
    while (datetime.utcnow().day != tomorrow.day):
        await asyncio.sleep(1)
    
    logger = logging.getLogger()
    logging.info("------- Log End -------")
    logger.removeHandler(file_handler)
    
    date = datetime.utcnow().strftime('%Y%m%d')
    
    file_handler = logging.FileHandler(os.path.join(logspath, f"{date}.log"), encoding='utf8')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logformat)
    logger.addHandler(file_handler)
    
    logging.info("------- Log Start -------")  
    remove_old()
    
    task = asyncio.create_task(remove_later(file_handler))
    task.add_done_callback(when_done)
    
async def setup_log():
    date = datetime.utcnow().strftime('%Y%m%d')
    
    logger = logging.getLogger()
    logger.setLevel(0)
    logformat.converter = time.gmtime
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logformat)
    logger.addHandler(console_handler)
    
    file_handler = logging.FileHandler(os.path.join(logspath, f"{date}.log"), encoding='utf8')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logformat)
    logger.addHandler(file_handler)
    
    logging.info("------- App startup -------")
    remove_old()
    
    task = asyncio.create_task(remove_later(file_handler))
    task.add_done_callback(when_done)
    
def _handle_task_result(task: asyncio.Task) -> None:
    try:
        task.result()
    except asyncio.CancelledError:
        pass
    except Exception:
        logging.exception('Exception raised by task = %r', task)
    