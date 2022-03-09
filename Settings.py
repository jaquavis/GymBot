import os
import json


class Settings:
    def __init__(self, version):
        self.version = version
        self.default_settings = f'''
        {{
            "version": "{self.version}",
            "user_profile": {{
                "username": null,
                "password": null
            }},
            "settings": {{
                "theme": "Auto",
                "add_to_cal": false,
                "autofill": false
            }}
        }}
        '''
        self.username = None
        self.password = None
        self.theme = "auto"
        self.config_path = None

    def get_settings(self):  # Returns settings data
        try:
            if os.stat(self.config_path).st_size != 0:
                with open(self.config_path):
                    pass

        except FileNotFoundError:
            with open(self.config_path, "w+") as settings_file:
                print("No settings found: Creating new user profile")
                settings_file.write(self.default_settings)

        with open(self.config_path) as settings_file:
            settings_data = json.load(settings_file)
            return settings_data

    def set_settings(self, theme="NoChange",
                     username="NoChange",
                     password="NoChange",
                     add_to_cal="NoChange",
                     autofill="NoChange"):
        settings_data = self.get_settings()

        if username != "NoChange":
            settings_data['user_profile']['username'] = username

        if password != "NoChange":
            settings_data['user_profile']['password'] = password

        if theme != "NoChange":
            settings_data['settings']['theme'] = theme

        if add_to_cal != "NoChange":
            settings_data['settings']['add_to_cal'] = add_to_cal

        if autofill != "NoChange":
            settings_data['settings']['autofill'] = autofill

        with open(self.config_path, "w") as settings_file:
            settings_data_to_write = json.dumps(settings_data, indent=2)
            settings_file.write(settings_data_to_write)

    def version_check(self):
        try:
            if self.get_settings()['version'] == self.version:
                pass
            else:
                try:
                    with open(self.config_path, "w+") as settings_file:
                        print("User configuration out of date: Writing new user profile")
                        settings_file.write(self.default_settings)

                except FileNotFoundError:
                    print("Fatal error")

        except KeyError:
            try:
                with open(self.config_path, "w+") as settings_file:
                    print("User configuration out of date: Writing new user profile")
                    settings_file.write(self.default_settings)

            except FileNotFoundError:
                print("Fatal error")

        except json.decoder.JSONDecodeError:
            print("Error: corrupt configuration file removed")
            print("Please restart the program")
            os.remove(self.config_path)
