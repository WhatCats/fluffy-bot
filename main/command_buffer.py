'''
Created on June 17, 2021

@author: Josef
''' 
import asyncio
from configparser import ConfigParser
from queue import Queue
import socket
from threading import Thread

from main.globals import get_bot
from resources.path import resource_path


config = ConfigParser()
config.read(resource_path("config.ini")) 
config = config["SETTINGS"]

helperbusy = True
mainbusy = False
helper = False
queue = Queue() 

def listen(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))

if config.has_section('helper'):
    helper = True
    server = config.get('helper')
    server = server.split(':')
    thread = Thread(target=listen, args=(server[0], int(server[1])), daemon=True)
    thread.start()
   
async def helper_work(message):
    pass

async def main_work(message):
    bot = get_bot()
    await bot.process_commands(message)
    
    global mainbusy
    mainbusy = False

def worker():
    while True:
        message = queue.get()
    
        if not mainbusy:
            mainbusy = True
            asyncio.create_task(main_work(message))
            return
        
        if not helperbusy:
            helperbusy = True
            asyncio.create_task(helper_work(message))
            return
      
def process_command(message):
    if helper:
        return
    
    