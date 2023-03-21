import os
import datetime
import csv
import pytz
from google.oauth2 import credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow



# Set up authentication with Google Calendar API
SCOPES = ['https://www.googleapis.com/auth/calendar']
creds = None
creds_file = 'token.json'  # Update with your credentials file

if os.path.exists(creds_file):
    creds = credentials.Credentials.from_authorized_user_file(creds_file, SCOPES)


if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'client_secret.json', SCOPES)
        creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open(creds_file, 'w') as token:
        token.write(creds.to_json())


# Set up the Google Calendar API client
service = build('calendar', 'v3', credentials=creds)

# Define London timezone
london_tz = pytz.timezone('Europe/London')


# Define the CSV file path and the calendar ID to create events for
csv_file = 'data.csv'  # Update with your CSV file path
calendar_name = 'Ramadan Timings 2023'


# Function to create a new calendar
def create_calendar():
    calendar = {
        'summary': calendar_name,
        'timeZone': 'Europe/London'  # Use London timezone
    }
    created_calendar = service.calendars().insert(body=calendar).execute()
    print(f'Calendar created: {calendar_name} ({created_calendar["id"]})')
    return created_calendar['id']


# Function to create an event in the specified calendar
def create_event(start_time, end_time, event_summary, calendar_id):
    start_time = london_tz.localize(start_time).isoformat()
    end_time = london_tz.localize(end_time).isoformat()
    event = {
        'summary': event_summary,
        'start': {
            'dateTime': start_time,
            'timeZone': 'Europe/London'  # Use London timezone for start time
        },
        'end': {
            'dateTime': end_time,
            'timeZone': 'Europe/London'  # Use London timezone for end time
        }
    }
    try:
        event = service.events().insert(calendarId=calendar_id, body=event).execute()
        print(f'Event created: {event_summary}')
    except HttpError as error:
        print(f'An error occurred: {error}')
        event = None
    return event


# Create the calendar if it doesn't already exist and get its ID
calendar_id = None
page_token = None
while True:
    calendar_list = service.calendarList().list(pageToken=page_token).execute()
    for calendar in calendar_list['items']:
        if calendar['summary'] == calendar_name:
            calendar_id = calendar['id']
            print(f'Calendar already exists: {calendar_name} ({calendar_id})')
            break
    page_token = calendar_list.get('nextPageToken')
    if not page_token or calendar_id is not None:
        break
if calendar_id is None:
    calendar_id = create_calendar()


# Read the CSV file and create events in the calendar
with open(csv_file, 'r') as file:
    reader = csv.DictReader(file)
    for row in reader:
        date = row['date']
        sehri_start_time = datetime.datetime.strptime(date + ' ' + row['sehri'], '%d/%m/%Y %H:%M')
        sehri_end_time = sehri_start_time + datetime.timedelta(minutes=5)
        sehri_event_summary = f'Sehri {date}'
        create_event(sehri_start_time, sehri_end_time, sehri_event_summary, calendar_id)
        
        iftar_start_time = datetime.datetime.strptime(date + ' ' + row['iftar'], '%d/%m/%Y %H:%M')
        iftar_end_time = iftar_start_time + datetime.timedelta(minutes=5)
        iftar_event_summary = f'Iftar {date}'
        create_event(iftar_start_time, iftar_end_time, iftar_event_summary, calendar_id)