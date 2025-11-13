"""Google Calendar API integration"""

import os
import pickle
import datetime
from datetime import timedelta
from typing import List

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from ai_schedule_agent.models.event import Event
from ai_schedule_agent.config.manager import ConfigManager
from ai_schedule_agent.utils.logging import logger

# Google Calendar API scope
SCOPES = ['https://www.googleapis.com/auth/calendar']


class CalendarIntegration:
    """Google Calendar integration handler"""

    def __init__(self):
        self.service = None
        self.credentials = None
        self.config = ConfigManager()

    def authenticate(self):
        """Authenticate with Google Calendar using OAuth 2.0"""
        creds = None

        # Get paths from config
        token_file = self.config.get_path('token_file', 'token.pickle')
        credentials_file = self.config.get_path('google_credentials', 'credentials.json')

        # Token file stores the user's access and refresh tokens
        if os.path.exists(token_file):
            with open(token_file, 'rb') as token:
                creds = pickle.load(token)

        # If there are no (valid) credentials available, let the user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    logger.info("Refreshing expired access token...")
                    creds.refresh(Request())
                    logger.info("✓ Token refreshed successfully")
                except Exception as refresh_error:
                    logger.warning(f"Token refresh failed: {refresh_error}")
                    logger.info("Deleting expired token and requesting new authentication...")
                    # Delete expired token
                    if os.path.exists(token_file):
                        os.remove(token_file)
                    # Request new authentication
                    if not os.path.exists(credentials_file):
                        raise FileNotFoundError(
                            f"Google credentials file not found at {credentials_file}. "
                            f"Please follow the setup instructions in .config/README.md"
                        )
                    flow = InstalledAppFlow.from_client_secrets_file(
                        credentials_file, SCOPES)
                    creds = flow.run_local_server(port=0)
            else:
                if not os.path.exists(credentials_file):
                    raise FileNotFoundError(
                        f"Google credentials file not found at {credentials_file}. "
                        f"Please follow the setup instructions in .config/README.md"
                    )
                logger.info("=" * 60)
                logger.info("GOOGLE CALENDAR AUTHENTICATION REQUIRED")
                logger.info("=" * 60)
                logger.info("A browser window will open for one-time authentication.")
                logger.info("Steps:")
                logger.info("  1. Sign in to your Google account")
                logger.info("  2. Grant calendar access permissions")
                logger.info("  3. Browser will show 'Authentication successful'")
                logger.info("  4. Return to the application")
                logger.info("")
                logger.info("This only needs to be done ONCE. Token will be saved.")
                logger.info("=" * 60)

                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_file, SCOPES)
                creds = flow.run_local_server(port=0)

                logger.info("=" * 60)
                logger.info("✓ AUTHENTICATION SUCCESSFUL")
                logger.info("=" * 60)
                logger.info("Token saved. You won't need to authenticate again.")
                logger.info("=" * 60)

            # Save credentials for next run
            with open(token_file, 'wb') as token:
                pickle.dump(creds, token)

        self.credentials = creds
        self.service = build('calendar', 'v3', credentials=creds)

    def get_events(self, time_min=None, time_max=None):
        """Fetch events from Google Calendar"""
        if not self.service:
            self.authenticate()

        if not time_min:
            time_min = datetime.datetime.utcnow().isoformat() + 'Z'
        if not time_max:
            time_max = (datetime.datetime.utcnow() + timedelta(days=30)).isoformat() + 'Z'

        try:
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy='startTime'
            ).execute()

            return events_result.get('items', [])
        except HttpError as error:
            logger.error(f'An error occurred: {error}')
            return []

    def create_event(self, event: Event):
        """Create event in Google Calendar (respects DRY_RUN mode)"""
        # Check DRY_RUN mode
        if self.config.is_dry_run():
            logger.info(f"DRY_RUN: Would create event '{event.title}' from {event.start_time} to {event.end_time}")
            return {
                'id': 'dry_run_event_id',
                'htmlLink': f'https://calendar.google.com/calendar/dry_run',
                'summary': event.title,
                'dry_run': True
            }

        if not self.service:
            self.authenticate()

        try:
            google_event = event.to_google_event()
            created_event = self.service.events().insert(
                calendarId='primary',
                body=google_event
            ).execute()

            logger.info(f"Created event: '{event.title}' (ID: {created_event['id']})")
            return created_event
        except HttpError as error:
            logger.error(f'An error occurred creating event: {error}')
            return None

    def update_event(self, event_id: str, event: Event):
        """Update existing event (respects DRY_RUN mode)"""
        # Check DRY_RUN mode
        if self.config.is_dry_run():
            logger.info(f"DRY_RUN: Would update event ID '{event_id}' with '{event.title}' from {event.start_time} to {event.end_time}")
            return {
                'id': event_id,
                'htmlLink': f'https://calendar.google.com/calendar/dry_run',
                'summary': event.title,
                'dry_run': True
            }

        if not self.service:
            self.authenticate()

        try:
            google_event = event.to_google_event()
            updated_event = self.service.events().update(
                calendarId='primary',
                eventId=event_id,
                body=google_event
            ).execute()

            logger.info(f"Updated event: '{event.title}' (ID: {event_id})")
            return updated_event
        except HttpError as error:
            logger.error(f'An error occurred updating event: {error}')
            return None

    def check_availability(self, start_time: datetime.datetime,
                          end_time: datetime.datetime,
                          attendees: List[str]) -> bool:
        """Check if all attendees are available using FreeBusy API"""
        if not self.service:
            self.authenticate()

        free_busy_query = {
            'timeMin': start_time.isoformat(),
            'timeMax': end_time.isoformat(),
            'items': [{'id': email} for email in attendees]
        }

        try:
            free_busy_result = self.service.freebusy().query(
                body=free_busy_query
            ).execute()

            for email, calendar in free_busy_result['calendars'].items():
                if calendar.get('busy'):
                    return False

            return True
        except HttpError as error:
            logger.error(f'An error occurred: {error}')
            return True  # Assume available if check fails
