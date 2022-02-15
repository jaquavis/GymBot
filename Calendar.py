import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import logging


class Calendar:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.SCOPES = ['https://www.googleapis.com/auth/calendar']  # If modifying these scopes, delete the file token.json
        self.creds = None
        self.tokenFileName = None
        self.credsFileName = None

    def authenticate(self):
        if os.path.exists(self.tokenFileName):
            self.creds = Credentials.from_authorized_user_file(self.tokenFileName, self.SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.credsFileName, self.SCOPES)
                self.creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(self.tokenFileName, 'w') as token:
                token.write(self.creds.to_json())

    def book_event(self, start_time, end_time):
        try:
            calendar = build('calendar', 'v3', credentials=self.creds)

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
                "reminders": {
                    "useDefault": False,
                }
            }
            calendar.events().insert(calendarId='primary', body=event).execute()
            print('Calendar event created')

        except HttpError as error:
            self.logger.warning('An error occurred: %s' % error)
