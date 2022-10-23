'''
Created on Apr 2, 2021

@author: Josef
'''
from enum import Enum, auto
from duels.util import get_duel_type

class Gamemode(Enum):

    BEDWARS = auto()
    SKYWARS = auto()
    DUELS = auto()
    HYPIXEL = auto()

    @classmethod
    def from_string(cls, name):
        if name.upper() == "BW":
            return cls["BEDWARS"]
        elif name.upper() == "SW":
            return cls["SKYWARS"]
        elif name.upper() == "MC":
            return cls["HYPIXEL"]
        elif name.upper() in cls.__members__:
            return cls[name.upper()]
        elif get_duel_type(name.upper()) != False:
            return cls["DUELS"]
        
        return False
        