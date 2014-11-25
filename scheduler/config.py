#coding: utf-8
import os

try:
    settings_file = os.environ["SCHEDULER_SETTINGS"]
except KeyError:
    settings_file = "settings"

settings_module = __import__(settings_file)
    

class Settings(object):
    def __init__(self, module):
        for setting in dir(module):
            if setting == setting.upper():
                setattr(self, setting, getattr(module, setting))

settings = Settings(settings_module)
