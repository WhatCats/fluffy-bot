'''
Created on Apr 24, 2021

@author: Josef
'''
import yaml

class Loader(yaml.SafeLoader):
    def construct_python_tuple(self, node):
        return tuple(self.construct_sequence(node))
    
Loader.add_constructor(
    u'tag:yaml.org,2002:python/tuple',
    Loader.construct_python_tuple)