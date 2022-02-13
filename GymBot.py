# pyinstaller --onefile --add-binary "GymBot.ico;files" --add-binary "chromedriver.exe;files" -i GymBot.ico GymBot.py
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.service import Service
from win10toast import ToastNotifier
from Iac01Bot import Iac01Bot
from pwinput import pwinput
import tkinter as tk
from tkinter import *
import signal
import sys
import os
from GymBotGUI import GymBotGUI


# TODO logging levels
# TODO calendar linking

def signal_handler(sig, frame):
    print('\nExiting')
    driver.quit()

if getattr(sys, 'frozen', False):  # Running as compiled
    running_dir = sys._MEIPASS + "/files/"  # Same path name than pyinstaller option
else:
    running_dir = "./"  # Path name when run with Python interpreter

iconFileName = running_dir + "GymBot.ico"
driverFileName = running_dir + "chromedriver.exe"

if __name__ == "__main__":
    login_url = "https://iac01.ucalgary.ca/CamRecWebBooking/Login.aspx"
    default_url = "https://iac01.ucalgary.ca/CamRecWebBooking/Login.aspx"

    # Define objects
    global ser
    global op
    global driver
    global toaster
    global iac01bot

    ser = Service(driverFileName)
    op = webdriver.ChromeOptions()
    op.add_argument("--headless")
    op.add_argument('--log-level=3')
    op.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(service=ser, options=op)  # webdriver
    toaster = ToastNotifier()                           # notifier
    iac01bot = Iac01Bot(driver)                         # iac01bot
    signal.signal(signal.SIGINT, signal_handler)        # signal handler
    GUI = GymBotGUI(iac01bot)                           # interface app

    # Start process
    GUI.create_main_window()

    # Cleanup
    driver.quit()
