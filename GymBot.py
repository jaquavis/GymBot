# GymBot
# pyinstaller --onefile --add-binary "GymBot.ico;files" --add-binary "chromedriver.exe;files" --add-binary "credentials.json;files" -i GymBot.ico GymBot.py
from __future__ import print_function
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from win10toast import ToastNotifier
from Iac01Bot import Iac01Bot
import signal
import sys
from GymBotGUI import GymBotGUI
import datetime
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


# TODO logging levels
# TODO calendar linking
# TODO fix return key support
# TODO Exit cleanup
# TODO Bug: fix time inputs single digits numbers don't work (i.e., 06)
# TODO Disable calendar alert reminders
# TODO Daemonic thread


def signal_handler(sig, frame):
    print('\nExiting')
    driver.quit()


if getattr(sys, 'frozen', False):  # Running as compiled
    running_dir = sys._MEIPASS + "/files/"  # Same path name than pyinstaller option
else:
    running_dir = "./"  # Path name when run with Python interpreter

# Define paths
iconFileName = running_dir + 'GymBot.ico'
driverFileName = running_dir + 'chromedriver.exe'
credsFileName = running_dir + 'credentials.json'
tokenFileName = running_dir + 'token.json'
login_url = "https://iac01.ucalgary.ca/CamRecWebBooking/Login.aspx"
default_url = "https://iac01.ucalgary.ca/CamRecWebBooking/default.aspx"

if __name__ == "__main__":
    print("GymBot® v0.11")

    # Authenticate calendar credentials
    SCOPES = ['https://www.googleapis.com/auth/calendar']  # If modifying these scopes, delete the file token.json
    creds = None

    if os.path.exists(tokenFileName):
        creds = Credentials.from_authorized_user_file(tokenFileName, SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credsFileName, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(tokenFileName, 'w') as token:
            token.write(creds.to_json())

    # Define objects
    ser = Service(driverFileName)
    op = webdriver.ChromeOptions()
    op.add_argument("--headless")
    op.add_argument('--log-level=3')
    op.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(service=ser, options=op)  # webdriver
    toaster = ToastNotifier()                           # notifier
    toaster.icon = iconFileName                         # notifier: icon
    iac01bot = Iac01Bot(driver)                         # iac01bot
    iac01bot.url = login_url                            # iac01bot: url
    signal.signal(signal.SIGINT, signal_handler)        # signal handler
    gui = GymBotGUI(iac01bot, toaster)                  # interface app

    # Start process
    gui.create_main_window()

    # Calendar booking
    try:
        calendar = build('calendar', 'v3', credentials=creds)

        today = datetime.datetime.now().isoformat()
        start_time = f"{today[0:11]}{gui.time_slot_text[10:15]}:00.000"
        end_time = f"{today[0:11]}{gui.time_slot_text[19:24]}:00.000"

        event = {
            'summary': 'Gym',
            'description': 'Booked by GymBot®',
            'start': {
                'dateTime': start_time,
                'timeZone': 'Canada/Mountain',
            },
            'end': {
                'dateTime': end_time,
                'timeZone': 'Canada/Mountain',
            },
        }
        event_stat = calendar.events().insert(calendarId='primary', body=event).execute()
        print('Calendar event created')

    except HttpError as error:
        print('An error occurred: %s' % error)

    # Cleanup
    print('\nExiting')
    driver.quit()
