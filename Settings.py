import logging
import os
from os import path
import json


class Settings:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.default_settings = '''
        {
            "user_profile": {
                "username": null,
                "password": null
            },
            "settings": {
                "theme": "Auto"
            }
        }
        '''
        self.username = None
        self.password = None
        self.theme = "auto"

    def get_settings(self):  # Returns settings data
        try:
            if os.stat(path.expandvars(r'%LOCALAPPDATA%\GymBotSettings.json')).st_size != 0:
                with open(path.expandvars(r'%LOCALAPPDATA%\GymBotSettings.json')) as settings_file:
                    settings_data = json.load(settings_file)
                    return settings_data

        except FileNotFoundError:
            with open(path.expandvars(r'%LOCALAPPDATA%\GymBotSettings.json'), "w+") as settings_file:
                print("No settings found: Creating new user profile")
                settings_file.write(self.default_settings)
                return None

    def set_settings(self, theme=None, username=None, password=None):
        settings_data = self.get_settings()
        settings_data['user_profile']['username'] = username
        settings_data['user_profile']['password'] = password
        settings_data['settings']['theme'] = theme
        with open(path.expandvars(r'%LOCALAPPDATA%\GymBotSettings.json'), "w") as settings_file:
            settings_data_to_write = json.dumps(settings_data, indent=2)
            settings_file.write(settings_data_to_write)
