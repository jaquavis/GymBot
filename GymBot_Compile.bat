pyinstaller --onefile ^
--add-binary "GymBot.ico;files" ^
--add-binary "GymBot_light.png;files" ^
--add-binary "GymBot_dark.png;files" ^
--add-binary "GymBot.png;files" ^
--add-binary "chromedriver.exe;files" ^
--add-binary "credentials.json;files" ^
-i GymBot.ico GymBot.py ^
--noconsole