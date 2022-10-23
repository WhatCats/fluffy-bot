'''
Created on Apr 9, 2021

@author: Josef
'''
import asyncio
from PIL import Image
from resources.path import resource_path

class BadRequest(Exception):
    def __init__(self, status):
        self.status = status
        super().__init__() 
        
    def __str__(self):
        return str(self.status)
    
def add_value(dictionary1, key1, dictionary2, key2, default=0):
    if key1 in dictionary1.keys():
        default = dictionary1[key1]       
    
    if (key2 in dictionary2.keys()):
        if isinstance(dictionary2[key2], int) and isinstance(default, int):
            dictionary2[key2] += default
    else:
        dictionary2[key2] = default
        
    return default

def get_value(dictionary, key, default=0):
    try:
        return dictionary[key]
    except KeyError:
        return default
    
async def multiple_requests(*coros):
    results = []
    requests = await asyncio.gather(*coros)
    for success, r in requests:
        if success is False:
            return success, r
        results.append(r)
    return True, results

def default_renders():
    head = Image.open(resource_path("default_head.png"))
    body = Image.open(resource_path("default_body.png"))
    return head, body
