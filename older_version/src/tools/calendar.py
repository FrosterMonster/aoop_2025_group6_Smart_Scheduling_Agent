import datetime
import json
from src.tools.base import AgentTool
from src.utils.auth import authenticate_google_calendar
from googleapiclient.discovery import build

class CalendarTool(AgentTool):
    def __init__(self):
        description = (
            "Useful for managing Google Calendar events. "
            "Input must be a JSON string. "
            "Keys: 'action', 'summary', 'start_time', 'end_time', 'event_id'. "
            "Valid actions: 'create_event', 'list_events', 'delete_event', 'update_event'. "
            "Time format: 'YYYY-MM-DDTHH:MM:SS'. "
            "CRITICAL: To update or delete, you MUST first 'list_events' to get the 'event_id'."
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
            
            # --- ACTION ROUTING ---
            if raw_action in ["create_event", "create", "add", "schedule"]:
                return self._create_event(data.get("summary"), data.get("start_time"), data.get("end_time"))
            
            elif raw_action in ["list_events", "list", "check", "show", "get"]:
                return self._list_events()
            
            elif raw_action in ["delete_event", "delete", "remove", "cancel"]:
                return self._delete_event(data.get("event_id"))
                
            elif raw_action in ["update_event", "update", "change", "reschedule", "move"]:
                return self._update_event(
                    data.get("event_id"), 
                    data.get("start_time"), 
                    data.get("end_time"),
                    data.get("summary")
                )
            
            else:
                return f"Error: Unknown action '{raw_action}'. Valid actions: create, list, delete, update."
                
        except Exception as e:
            return f"Error processing calendar request: {e}"

    # --- HELPER FUNCTIONS ---

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
        # We list events for the next 7 days
        now = datetime.datetime.utcnow().isoformat() + 'Z'
        events_result = self._service.events().list(
            calendarId='primary', timeMin=now,
            maxResults=10, singleEvents=True,
            orderBy='startTime').execute()
        events = events_result.get('items', [])
        
        if not events:
            return "No upcoming events found."
        
        result = "Upcoming events (Copy the ID to update/delete):\n"
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            # ID is crucial here
            result += f"- {start} | {event['summary']} | ID: {event['id']}\n"
        return result

    def _delete_event(self, event_id):
        if not event_id:
            return "Error: missing 'event_id'. Please use 'list_events' to find the ID first."
        try:
            self._service.events().delete(calendarId='primary', eventId=event_id).execute()
            return f"Success! Event {event_id} deleted."
        except Exception as e:
            return f"Delete Error: {e}"

    def _update_event(self, event_id, start_time=None, end_time=None, summary=None):
        if not event_id:
            return "Error: missing 'event_id'. Please use 'list_events' to find the ID first."
        
        try:
            # 1. Get the existing event first (so we don't overwrite missing fields with None)
            event = self._service.events().get(calendarId='primary', eventId=event_id).execute()
            
            # 2. Update only the fields provided
            if summary:
                event['summary'] = summary
            if start_time:
                event['start']['dateTime'] = start_time
            if end_time:
                event['end']['dateTime'] = end_time
                
            # 3. Push the update
            updated_event = self._service.events().update(calendarId='primary', eventId=event_id, body=event).execute()
            return f"Success! Event updated: {updated_event.get('htmlLink')}"
        except Exception as e:
            return f"Update Error: {e}"