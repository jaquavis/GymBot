# GymBot®
# pyinstaller --onefile --add-binary "GymBot.ico;files" --add-binary "GymBot.png;files" --add-binary "chromedriver.exe;files" --add-binary "credentials.json;files" -i GymBot.ico GymBot.py
from __future__ import print_function
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


# Lukas:
# TODO Exit cleanup
# TODO confirm bookings - running two instances at once wont work
# TODO py2app - mac release
# TODO add per/user options for theme

# Nathan:
# TODO End threads / destroy all windows
# TODO Find out how to use return to enter login
# TODO Alert if website is down
# TODO loading wheel (rotating text)


def signal_handler(sig, frame):
    print('\nExiting: You may now close this window')
    driver.quit()


if getattr(sys, 'frozen', False):  # Running as compiled
    running_dir = sys._MEIPASS + "/files/"  # Same path name than pyinstaller option
else:
    running_dir = "./"  # Path name when run with Python interpreter

# Define paths
iconFileName = running_dir + 'GymBot.ico'
pngFileName = running_dir + 'GymBot.png'
driverFileName = running_dir + 'chromedriver.exe'
credsFileName = running_dir + 'credentials.json'
tokenFileName = path.expandvars(r'%LOCALAPPDATA%\GymBotToken.json')
login_url = "https://iac01.ucalgary.ca/CamRecWebBooking/Login.aspx"
default_url = "https://iac01.ucalgary.ca/CamRecWebBooking/default.aspx"

if __name__ == "__main__":
    print("GymBot® v0.15")

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
    iac01bot.url = login_url                            # iac01bot: url
    signal.signal(signal.SIGINT, signal_handler)        # signal handler
    calendar = Calendar()                               # calendar
    calendar.credsFileName = credsFileName              # calendar: credentials
    calendar.tokenFileName = tokenFileName              # calendar: token
    gui = GymBotGUI(iac01bot, toaster, calendar)        # interface
    gui.icon_photo = PhotoImage(file=pngFileName)      # interface: png

    # Start process
    gui.set_theme_mode()
    gui.create_main_window()

    # Calendar booking
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
