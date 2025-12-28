# src/tools/calendar.py (Update)
import datetime
import json
from src.tools.base import AgentTool
from src.utils.auth import authenticate_google_calendar
from googleapiclient.discovery import build

class CalendarTool(AgentTool):
    def __init__(self):
        # The description is CRITICAL. It tells the LLM how to use this tool.
        description = (
            "Useful for managing Google Calendar events. "
            "Input should be a JSON string with keys: 'action', 'summary', 'start_time', 'end_time'. "
            "start_time and end_time must be in ISO format 'YYYY-MM-DDTHH:MM:SS'."
        )
        super().__init__(name="google_calendar", description=description)
        creds = authenticate_google_calendar()
        self._service = build('calendar', 'v3', credentials=creds)

    def execute(self, params: str):
        """
        Parses the input string (JSON) and executes the calendar action.
        """
        try:
            # The LLM might send a JSON string, so we parse it
            if isinstance(params, str):
                data = json.loads(params)
            else:
                data = params
            
            action = data.get("action")
            
            if action == "create_event":
                return self._create_event(data.get("summary"), data.get("start_time"), data.get("end_time"))
            elif action == "list_events":
                return self._list_events()
            else:
                return f"Error: Unknown action '{action}'"
        except Exception as e:
            return f"Error processing calendar request: {e}"

    # ... (Keep _create_event and _list_events from Week 1) ...

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