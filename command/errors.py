'''
Created on Apr 6, 2021

@author: Josef
'''
from discord.ext import commands

class SafeMode(commands.CommandError):
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        
class CommandDisabled(commands.CommandError):
    def __init__(self, command, *args, **kwargs):
        self.commnad = command
        super().__init__(*args, **kwargs)

class NotAdmin(commands.CommandError):
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        
class BadServer(commands.CommandError):
    def __init__(self, guild_id, *args, **kwargs):
        self.guild_id = guild_id
        super().__init__(*args, **kwargs)
        
class InputError(commands.CommandError):
    def __init__(self, msg, *args, **kwargs):
        self.msg = msg
        super().__init__(*args, **kwargs)
        
class UnexpectedError(commands.CommandError):
    def __init__(self, msg, *args, **kwargs):
        self.msg = msg
        super().__init__(*args, **kwargs)
        
class CommandError(commands.CommandError):
    def __init__(self, msg, *args, **kwargs):
        self.msg = msg
        super().__init__(*args, **kwargs)
        
class InvalidSyntax(commands.CommandError):
    def __init__(self, corect="To add a command parameter and/or a argument: `+command <arg1> <arg2> paramname=paramvalue`.", *args, **kwargs):
        self.corect = corect
        super().__init__(*args, **kwargs)