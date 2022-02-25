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
        self.config_path = None

    def get_settings(self):  # Returns settings data
        try:
            if os.stat(self.config_path).st_size != 0:
                with open(self.config_path) as settings_file:
                    settings_data = json.load(settings_file)

        except FileNotFoundError:
            with open(self.config_path, "w+") as settings_file:
                print("No settings found: Creating new user profile")
                settings_file.write(self.default_settings)

        with open(self.config_path) as settings_file:
            settings_data = json.load(settings_file)
            return settings_data

    def set_settings(self, theme="NoChange", username="NoChange", password="NoChange"):
        settings_data = self.get_settings()

        if username != "NoChange":
            settings_data['user_profile']['username'] = username

        if password != "NoChange":
            settings_data['user_profile']['password'] = password

        if theme != "NoChange":
            settings_data['settings']['theme'] = theme

        with open(self.config_path, "w") as settings_file:
            settings_data_to_write = json.dumps(settings_data, indent=2)
            settings_file.write(settings_data_to_write)
