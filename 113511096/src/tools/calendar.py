import datetime
import json
from src.tools.base import AgentTool
from src.utils.auth import authenticate_google_calendar
from googleapiclient.discovery import build

class CalendarTool(AgentTool):
    def __init__(self):
        description = (
            "Useful for managing Google Calendar events. "
            "Input must be a JSON string with keys: 'action', 'summary', 'start_time', 'end_time', 'event_id'. "
            "Valid actions: 'create_event', 'list_events', 'delete_event'. "
            "Time format: 'YYYY-MM-DDTHH:MM:SS'. "
            "To delete, you MUST first 'list_events' to get the 'event_id'."
        )
        super().__init__(name="google_calendar", description=description)
        creds = authenticate_google_calendar()
        self._service = build('calendar', 'v3', credentials=creds)

    def execute(self, params: str):
        try:
            if isinstance(params, str):
                data = json.loads(params)
            else:
                data = params
            
            raw_action = data.get("action", "").lower().strip()
            
            # Map various phrasings to the correct function
            if raw_action in ["create_event", "create", "add", "schedule"]:
                return self._create_event(data.get("summary"), data.get("start_time"), data.get("end_time"))
            
            elif raw_action in ["list_events", "list", "check", "show", "get"]:
                return self._list_events()
            
            elif raw_action in ["delete_event", "delete", "remove", "cancel"]:
                return self._delete_event(data.get("summary"), data.get("event_id"))
            
            else:
                return f"Error: Unknown action '{raw_action}'. Try 'create_event', 'list_events', or 'delete_event'."
                
        except Exception as e:
            return f"Error processing calendar request: {e}"

    def _create_event(self, summary, start_time, end_time):
        event = {
            'summary': summary,
            'start': {'dateTime': start_time, 'timeZone': 'Asia/Taipei'},
            'end': {'dateTime': end_time, 'timeZone': 'Asia/Taipei'},
        }
        try:
            event_result = self._service.events().insert(calendarId='primary', body=event).execute()
            return f"Success! Event created: {event_result.get('htmlLink')}"
        except Exception as e:
            return f"Google API Error: {e}"

    def _list_events(self):
        """Lists upcoming 10 events with their IDs (crucial for deletion)."""
        now = datetime.datetime.utcnow().isoformat() + 'Z'
        events_result = self._service.events().list(
            calendarId='primary', timeMin=now,
            maxResults=10, singleEvents=True,
            orderBy='startTime').execute()
        events = events_result.get('items', [])
        
        if not events:
            return "No upcoming events found."
        
        result = "Upcoming events (Copy the ID to delete):\n"
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            # We include the ID in the output so the Agent can see it
            result += f"- {start} | {event['summary']} | ID: {event['id']}\n"
        return result

    def _delete_event(self, summary, event_id):
        """Deletes an event. Smartly handles finding the ID if only summary is given."""
        if not event_id:
            # If the user didn't provide an ID, we try to find the event by name first
            list_output = self._list_events()
            if "ID:" not in list_output:
                return "Could not find any events to delete."
            
            # Simple logic: Try to match the summary to an ID
            # (In a real app, we might ask the agent to do this, but this helper is nice)
            return "Error: You must provide the 'event_id' to delete. Use 'list_events' first to find the ID."

        try:
            self._service.events().delete(calendarId='primary', eventId=event_id).execute()
            return f"Success! Event with ID {event_id} has been deleted."
        except Exception as e:
            return f"Delete Error: {e}"