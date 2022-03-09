pyinstaller --onefile \
--add-binary "GymBot.ico:files" \
--add-binary "GymBot_light.png:files" \
--add-binary "GymBot_dark.png:files" \
--add-binary "GymBot.png:files" \
--add-binary "chromedriver_mac64:files" \
-i GymBot.ico GymBot.py
