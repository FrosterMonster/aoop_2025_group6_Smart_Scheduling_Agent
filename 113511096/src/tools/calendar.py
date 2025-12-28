from googleapiclient.discovery import build
from src.tools.base import AgentTool
from src.utils.auth import authenticate_google_calendar
import datetime

class CalendarTool(AgentTool):
    """
    Inherits from AgentTool, specializing in Google Calendar API interactions.
    """
    def __init__(self):
        super().__init__(name="Google Calendar", description="Manage calendar events")
        # Initialize API service
        creds = authenticate_google_calendar()
        self._service = build('calendar', 'v3', credentials=creds) # Encapsulation: _service 

    def execute(self, action: str, **kwargs):
        """
        Implementation of the abstract execute method (Polymorphism).
        Dispatch based on action type.
        """
        if action == "create_event":
            return self._create_event(kwargs.get("summary"), kwargs.get("start_time"), kwargs.get("end_time"))
        elif action == "list_events":
            return self._list_events()
        else:
            return f"Action '{action}' not supported."

    def _create_event(self, summary, start_time, end_time):
        """
        Basic event creation function[cite: 12, 70].
        Expected time format: 'YYYY-MM-DDTHH:MM:SS' (ISO format)
        """
        event = {
            'summary': summary,
            'start': {
                'dateTime': start_time,
                'timeZone': 'Asia/Taipei', # Adjust as needed
            },
            'end': {
                'dateTime': end_time,
                'timeZone': 'Asia/Taipei',
            },
        }

        try:
            event_result = self._service.events().insert(calendarId='primary', body=event).execute()
            return f"Event created: {event_result.get('htmlLink')}"
        except Exception as e:
            return f"An error occurred: {e}"

    def _list_events(self):
        """Helper to list upcoming 10 events."""
        now = datetime.datetime.utcnow().isoformat() + 'Z'
        events_result = self._service.events().list(
            calendarId='primary', timeMin=now,
            maxResults=10, singleEvents=True,
            orderBy='startTime').execute()
        events = events_result.get('items', [])
        
        if not events:
            return "No upcoming events found."
        
        result = "Upcoming events:\n"
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            result += f"{start} - {event['summary']}\n"
        return result