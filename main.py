import os
import logging
import requests
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from datetime import datetime, timedelta, timezone
import pytz
from functions_framework import http

# Load environment variables
load_dotenv()

# change this to an environment variable in a .env filr
# can upload these to cloud functions (GCP) when you're building the function
DISCORD_WEBHOOK_URL = 'DISCORD-WEBHOOK-KEY'

# Set up logging for debugging with structured format
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')


SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

#Get your credentials file from GCP
CREDENTIALS_FILE = 'Automation_OAuth_Token.json'

#Array of calendar ID's which can be found in the app or online
CALENDARS = [
    {'id': 'calender_id_1', 'label': 'label_1'},
    {'id': 'calender_id_2', 'label': 'label_2'},
    {'id': 'calender_id_3', 'label': 'label_3'}
]

#function to authenticate google details and account 
def authenticate_google():
    logging.debug("Authenticating with Google...")
    creds = None

    # check if credentials exist, otherwise generate one
    # would suggest getting these credentials locally and uploading to GCP secrets
    try:
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
            logging.debug("Loaded credentials from token.json")
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                logging.debug("Refreshing credentials...")
                creds.refresh(Request())
            else:
                logging.debug("Initiating new OAuth flow...")
                flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
                creds = flow.run_local_server(port=0)
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
                logging.debug("Credentials saved to token.json")
    except Exception as e:
        logging.error(f"Error during Google authentication: {str(e)}", exc_info=True)
    return creds

# Gets your calendar events for the next day
def get_calendar_events(service):
    logging.debug("Fetching calendar events...")
    events = []
    try:
        tomorrow_start = (datetime.now(timezone.utc) + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
        tomorrow_end = (datetime.now(timezone.utc) + timedelta(days=2)).replace(hour=0, minute=0, second=0, microsecond=0).isoformat()

        for calendar in CALENDARS:
            logging.debug(f"Fetching events for calendar: {calendar['label']}")
            events_result = service.events().list(
                calendarId=calendar['id'],
                timeMin=tomorrow_start,
                timeMax=tomorrow_end,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            calendar_events = events_result.get('items', [])
            logging.debug(f"Fetched {len(calendar_events)} events for calendar {calendar['label']}")

            for event in calendar_events:
                event['calendarLabel'] = calendar['label']
                events.append(event)
                start = event['start'].get('dateTime', event['start'].get('date'))
                logging.debug(f"Added event: {event['summary']} at {start} from {calendar['label']}")
    except Exception as e:
        logging.error(f"Error fetching events: {str(e)}", exc_info=True)

    logging.debug(f"Collected events: {events}")
    return events

# Formats the messages into a more readable format
def format_event_message(events):
    logging.debug("Formatting event message...")
    if not events:
        logging.debug("No events to format.")
        return "# Tomorrow's schedule:\n\n* No events scheduled."

    message_content = "# Tomorrow's schedule:\n\n"
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        time_zone = event.get('start', {}).get('timeZone', 'UTC')
        dt = datetime.fromisoformat(start.replace('Z', '+00:00')).astimezone(pytz.timezone(time_zone))
        formatted_time = dt.strftime('%I:%M %p')
        message_content += f"* {formatted_time} - {event['summary']} ({event['calendarLabel']})\n"
    
    logging.debug("Event message formatted")
    return message_content

# Actual request itself, logs in, gets calendar events and sends discord message
@http
def test_function(request):
    logging.info("Starting full function test.")
    if not DISCORD_WEBHOOK_URL:
        logging.error("Discord Webhook URL is not set")
        return "Discord Webhook URL not set", 400

    creds = authenticate_google()
    if not creds:
        logging.error("Failed to authenticate with Google")
        return "Failed to authenticate with Google", 500

    service = build('calendar', 'v3', credentials=creds)
    events = get_calendar_events(service)
    if not events:
        logging.info("No events found for tomorrow. No message will be sent.")
        return "No events found.", 200

    message = format_event_message(events)
    payload = {"content": message}
    logging.debug(f"Sending payload to Discord: {payload}")
    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
        logging.debug(f"Discord response: {response.status_code}, {response.text}")
        
        if response.status_code == 204:
            logging.info("Message sent successfully.")
            return "Message sent successfully.", 200
        else:
            logging.error(f"Error sending message: {response.status_code} {response.text}")
            return f"Error: {response.status_code} {response.text}", 400
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}", exc_info=True)
        return f"Error: {str(e)}", 500
