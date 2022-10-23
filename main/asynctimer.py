'''
Created on Apr 6, 2021

@author: Josef
'''
import asyncio
from datetime import datetime, timedelta
import logging

import pytz

class Timer:
    def __init__(self, timeout, callback, onexception=None):
        self._timeout = timeout
        self._callback = callback
        self._onexception = onexception
        self._task = asyncio.create_task(self._job())
        self._task.add_done_callback(self.when_done)

    async def _job(self):
        await asyncio.sleep(self._timeout)
        await self._callback()
    
    def get_finish(self, timezone="utc"):
        tz = pytz.timezone(timezone)
        time = datetime.now(tz)
        
        time = time + timedelta(seconds=self._timeout)
        return time    
        
    def when_done(self, fut):
        try:
            fut.result()
        except asyncio.CancelledError:
            return
        except Exception as e:
            logging.exception(f"Exception in timer caught")
            if not self._onexception is None:
                self._onexception(e, self._callback)
        
    def cancel(self):
        self._task.cancel()