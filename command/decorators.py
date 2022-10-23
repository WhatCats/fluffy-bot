'''
Created on May 5, 2021

@author: Josef
'''
from command.errors import InputError
from main.globals import is_restored

def needs_data(func):
    async def wrapper(*args, **kwargs):
        if not is_restored():
            raise InputError(f'Player data is not restored yet. Please try again in a moment.')    
        await func(*args, **kwargs)
    return wrapper