'''
Created on 17 Dec 2020

@author: Josef
'''

import os
from pathlib import Path


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        # Error can be ignored
        base_path = sys._MEIPASS  # @UndefinedVariable
    except Exception:
        base_path = Path(__file__).resolve().parent

    return os.path.join(base_path, relative_path)