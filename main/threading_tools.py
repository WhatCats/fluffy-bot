'''
Created on Apr 6, 2021

@author: Josef
'''
import threading
import typing

def run_all(tasks: typing.Dict[typing.Hashable, tuple]):
    results = {}
    
    def execute(key, call):
        def wrapped(*args, **kwargs):
            results[key] = call(*args, **kwargs)
        return wrapped
    
    threads = []
    for key, (call, *args) in tasks.items():
        thread = threading.Thread(target=execute(key, call), args=args)
        thread.setDaemon(True)
        thread.start()
        threads.append(thread)
    
    for t in threads:
        t.join()
        
    return results