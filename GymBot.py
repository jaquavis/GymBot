# GymBot®
from __future__ import print_function
import os.path
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from win10toast import ToastNotifier
from Iac01Bot import Iac01Bot
import signal
import sys
from GymBotGUI import GymBotGUI
import datetime
from Calendar import Calendar
from os import path
import logging
from tkinter import PhotoImage
from Settings import Settings


def signal_handler(sig, frame):
    driver.quit()
    gui.exit_all()
    pass


if getattr(sys, 'frozen', False):  # Running as compiled
    running_dir = sys._MEIPASS + "/files/"  # Same path name than pyinstaller option
else:
    running_dir = "./"  # Path name when run with Python interpreter

# Define paths
localPath = path.expandvars(r'%LOCALAPPDATA%\GymBot') + '\\'
iconFileName = running_dir + 'GymBot.ico'
pngFileName = running_dir + 'GymBot.png'
lightFileName = running_dir + 'GymBot_light.png'
darkFileName = running_dir + 'GymBot_dark.png'
driverFileName = running_dir + 'chromedriver.exe'
credsFileName = running_dir + 'credentials.json'
tokenFileName = localPath + 'GymBotToken.json'
configFileName = localPath + 'GymBotUserConfig.json'
login_url = "https://iac01.ucalgary.ca/CamRecWebBooking/Login.aspx"
default_url = "https://iac01.ucalgary.ca/CamRecWebBooking/default.aspx"

if not os.path.exists(localPath):
    os.makedirs(localPath)

if __name__ == "__main__":
    print("GymBot® v0.20")

    # Define objects
    ser = Service(driverFileName)
    op = webdriver.ChromeOptions()
    op.add_argument("--headless")
    op.add_argument('--log-level=3')
    op.add_experimental_option('excludeSwitches', ['enable-logging'])
    logger = logging.getLogger(__name__)                # logger
    driver = webdriver.Chrome(service=ser, options=op)  # webdriver
    toaster = ToastNotifier()                           # notifier
    toaster.icon = iconFileName                         # notifier: icon
    iac01bot = Iac01Bot(driver)                         # iac01bot
    iac01bot.login_url = login_url                      # iac01bot: login url
    iac01bot.default_url = default_url                  # iac01bot: default url
    signal.signal(signal.SIGINT, signal_handler)        # signal handler
    calendar = Calendar()                               # calendar
    calendar.credsFileName = credsFileName              # calendar: credentials
    calendar.tokenFileName = tokenFileName              # calendar: token
    settings = Settings()                               # settings
    settings.config_path = configFileName               # settings: config
    gui = GymBotGUI(iac01bot,                           # interface
                    toaster,
                    calendar,
                    settings)
    gui.icon_photo = PhotoImage(file=pngFileName)       # interface: png
    gui.light_photo = PhotoImage(file=lightFileName)    # interface: light png
    gui.dark_photo = PhotoImage(file=darkFileName)      # interface: dark png

    # Start process
    gui.set_theme_mode()
    gui.create_main_window()

    # Calendar booking
    if gui.booking_successful:
        try:
            today = datetime.datetime.now().isoformat()
            start_time = f"{today[0:11]}{iac01bot.time_slot_text[10:15]}:00.000"
            end_time = f"{today[0:11]}{iac01bot.time_slot_text[19:24]}:00.000"
            if gui.add_to_cal:
                calendar.book_event(start_time, end_time)
        except TypeError:
            logger.warning("Could not find event times")

    # Cleanup
    print('\nExiting: You may now close this window')
    driver.quit()
    gui.exit_all()
