import datetime
import json
from src.tools.base import AgentTool
from src.utils.auth import authenticate_google_calendar
from googleapiclient.discovery import build

class CalendarTool(AgentTool):
    def __init__(self):
        # We explicitly tell the LLM which actions are valid
        description = (
            "Useful for managing Google Calendar events. "
            "Input must be a JSON string with keys: 'action', 'summary', 'start_time', 'end_time'. "
            "Valid actions are: 'create_event', 'list_events'. "
            "Time format: 'YYYY-MM-DDTHH:MM:SS'."
        )
        super().__init__(name="google_calendar", description=description)
        creds = authenticate_google_calendar()
        self._service = build('calendar', 'v3', credentials=creds)

    def execute(self, params: str):
        """
        Parses the input string (JSON) and executes the calendar action.
        """
        try:
            # Handle cases where the LLM sends a dict instead of a JSON string
            if isinstance(params, str):
                data = json.loads(params)
            else:
                data = params
            
            # 1. Normalize the action (convert to lower case and strip spaces)
            raw_action = data.get("action", "").lower().strip()
            
            # 2. Flexible Action Matching (The Fix)
            # The Agent might guess "create", "add", or "insert". We map them all to _create_event.
            if raw_action in ["create_event", "create", "add", "insert", "schedule"]:
                return self._create_event(data.get("summary"), data.get("start_time"), data.get("end_time"))
            
            elif raw_action in ["list_events", "list", "get", "show"]:
                return self._list_events()
            
            else:
                return f"Error: Unknown action '{raw_action}'. Valid actions are 'create_event' or 'list_events'."
                
        except Exception as e:
            return f"Error processing calendar request: {e}"

    def _create_event(self, summary, start_time, end_time):
        event = {
            'summary': summary,
            'start': {
                'dateTime': start_time,
                'timeZone': 'Asia/Taipei', # Ensure this matches your locale
            },
            'end': {
                'dateTime': end_time,
                'timeZone': 'Asia/Taipei',
            },
        }

        try:
            event_result = self._service.events().insert(calendarId='primary', body=event).execute()
            return f"Success! Event created: {event_result.get('htmlLink')}"
        except Exception as e:
            return f"Google API Error: {e}"

    def _list_events(self):
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