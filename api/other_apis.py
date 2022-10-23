'''
Created on Apr 3, 2021

@author: Josef
'''
from _io import BytesIO
import asyncio
from json.decoder import JSONDecodeError
import logging
import socket

from PIL import Image, UnidentifiedImageError
import aiohttp
from aiohttp.client import ClientTimeout
from aiohttp.client_exceptions import ContentTypeError, ClientConnectorError

from api.util import BadRequest

#Mojang API (api.mojang.com)
async def get_uuid(ign):
    try:
        conn = aiohttp.TCPConnector(family=socket.AF_INET)
        async with aiohttp.ClientSession(connector=conn, timeout=ClientTimeout(total=4)) as session:
            async with session.get(f"https://api.mojang.com/users/profiles/minecraft/{ign}") as r:
                if r.status != 200:
                    raise BadRequest(r.status)  
                result = await r.json()
                return True, result["id"]
    except BadRequest as e:
        if e.status == 204:
            return True, None
        logging.warning(f"Unable to reach api.mojang.com. Request status was: ({e}).")    
    except ClientConnectorError as e:
        logging.warning(f"Unable to reach api.mojang.com. Connection error was: ({e}).")
    except (ContentTypeError, JSONDecodeError, KeyError):
        logging.warning(f"Unable to decode the responce from api.mojang.com. Decode error.")
    except (TimeoutError, asyncio.TimeoutError):
        logging.warning(f"Unable to reach api.mojang.com. Request has timed out.")
    return False, "Unable to reach the mojang api at the moment."

#MCHeads API (mc-heads.net)        
async def get_head(uuid):
    try:
        conn = aiohttp.TCPConnector(family=socket.AF_INET)
        async with aiohttp.ClientSession(connector=conn, timeout=ClientTimeout(total=5)) as session:
            async with session.get(f'https://mc-heads.net/head/{uuid}/left') as r:
                if r.status != 200:
                    raise BadRequest(r.status)
                buffer = BytesIO(await r.read())
                return True, Image.open(buffer)
    except BadRequest as e:
        logging.warning(f"Unable to reach mc-heads.net. Request status was: ({e}).")
    except ClientConnectorError as e:
        logging.warning(f"Unable to reach mc-heads.net. Connection error was: ({e}).")
    except UnidentifiedImageError:
        logging.warning(f"Unable to decode the responce from mc-heads.net. (Bad image from mc-heads.net).")
    except (TimeoutError, asyncio.TimeoutError):
        logging.warning(f"Unable to reach mc-heads.net. Request has timed out.")
    return False, None

#MCHeads API (mc-heads.net)     
async def get_body(uuid):
    try:
        conn = aiohttp.TCPConnector(family=socket.AF_INET)
        async with aiohttp.ClientSession(connector=conn, timeout=ClientTimeout(total=5)) as session:
            async with session.get(f'https://mc-heads.net/body/{uuid}/left') as r:
                if r.status != 200:
                    raise BadRequest(r.status)
                buffer = BytesIO(await r.read())
                return True, Image.open(buffer)
    except BadRequest as e:
        logging.warning(f"Unable to reach mc-heads.net. Request status was: ({e}).")
    except ClientConnectorError as e:
        logging.warning(f"Unable to reach mc-heads.net. Connection error was: ({e}).")
    except UnidentifiedImageError:
        logging.warning(f"Unable to decode the responce from mc-heads.net. (Bad image from mc-heads.net).")
    except (TimeoutError, asyncio.TimeoutError):
        logging.warning(f"Unable to reach mc-heads.net. Request has timed out.")
    return False, None
 
#Discord profile urls   
async def get_profile(author):
    try:
        conn = aiohttp.TCPConnector(family=socket.AF_INET)
        async with aiohttp.ClientSession(connector=conn, timeout=ClientTimeout(total=4)) as session:
            async with session.get(author.avatar_url) as r:
                if r.status != 200:
                    raise BadRequest(r.status)
                buffer = BytesIO(await r.read())
                return True, Image.open(buffer)
    except BadRequest as e:
        logging.warning(f"Unable to get player profile. Request status was: ({e}).")
    except ClientConnectorError as e:
        logging.warning(f"Unable to get player profile. Connection error was: ({e}).")
    except UnidentifiedImageError:
        logging.warning(f"Unable to decode the responce from crafatar.com. (Bad image from crafatar.com).")
    except (TimeoutError, asyncio.TimeoutError):
        logging.warning(f"Unable to get player profile. Request has timed out.")
    return False, None
        