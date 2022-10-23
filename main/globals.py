'''
Created on June 17, 2021

@author: Josef
'''
_bot = None
_datarestored = False 

def set_bot(bot):
    global _bot
    _bot=bot

def get_bot():
    global _bot
    return _bot

def set_restored(restored):
    global _datarestored
    _datarestored = restored

def is_restored():
    global _datarestored
    return _datarestored