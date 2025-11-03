"""Calendar view tab for displaying events"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import datetime
from datetime import timedelta
from collections import defaultdict


class CalendarViewTab:
    """Calendar view tab UI component"""

    def __init__(self, parent, calendar_integration, pattern_learner, update_status_callback):
        self.parent = parent
        self.calendar = calendar_integration
        self.pattern_learner = pattern_learner
        self.update_status = update_status_callback
        self.view_range_var = None
        self.calendar_display = None

        self.setup_ui()

    def setup_ui(self):
        """Setup calendar view tab UI"""

        # Controls frame
        controls_frame = ttk.Frame(self.parent)
        controls_frame.pack(pady=10)

        ttk.Label(controls_frame, text="View Range:").grid(row=0, column=0, padx=5)

        self.view_range_var = tk.StringVar(value="Week")
        view_range = ttk.Combobox(controls_frame, textvariable=self.view_range_var,
                                  values=["Day", "Week", "Month"], state='readonly', width=10)
        view_range.grid(row=0, column=1, padx=5)

        ttk.Button(controls_frame, text="Refresh", command=self.refresh).grid(row=0, column=2, padx=10)
        ttk.Button(controls_frame, text="Sync with Google", command=self.sync_google_calendar).grid(row=0, column=3, padx=5)

        # Calendar display
        self.calendar_display = scrolledtext.ScrolledText(self.parent, height=25, width=100)
        self.calendar_display.pack(pady=10, padx=10, fill='both', expand=True)

        # Initial load
        self.refresh()

    def refresh(self):
        """Refresh the calendar view"""
        self.calendar_display.delete(1.0, tk.END)

        try:
            # Get events based on view range
            view_range = self.view_range_var.get()

            if view_range == "Day":
                days = 1
            elif view_range == "Week":
                days = 7
            else:  # Month
                days = 30

            start_time = datetime.datetime.now()
            end_time = start_time + timedelta(days=days)

            events = self.calendar.get_events(
                start_time.isoformat() + 'Z',
                end_time.isoformat() + 'Z'
            )

            # Group events by day
            events_by_day = defaultdict(list)
            for event in events:
                if 'dateTime' in event.get('start', {}):
                    start = datetime.datetime.fromisoformat(event['start']['dateTime'].replace('Z', '+00:00'))
                    day = start.date()
                    events_by_day[day].append(event)

            # Display events
            current_date = start_time.date()
            for day_offset in range(days):
                display_date = current_date + timedelta(days=day_offset)

                self.calendar_display.insert(tk.END, f"\n{'='*60}\n")
                self.calendar_display.insert(tk.END, f"{display_date.strftime('%A, %B %d, %Y')}\n")
                self.calendar_display.insert(tk.END, f"{'='*60}\n")

                if display_date in events_by_day:
                    for event in sorted(events_by_day[display_date],
                                      key=lambda x: x['start']['dateTime']):
                        start = datetime.datetime.fromisoformat(event['start']['dateTime'].replace('Z', '+00:00'))
                        end = datetime.datetime.fromisoformat(event['end']['dateTime'].replace('Z', '+00:00'))

                        # Get extended properties if available
                        props = event.get('extendedProperties', {}).get('private', {})
                        priority = props.get('priority', '2')
                        tags = props.get('tags', '')

                        # Format display
                        priority_emoji = {
                            '1': '🔵',  # Low
                            '2': '🟢',  # Medium
                            '3': '🟡',  # High
                            '4': '🔴'   # Critical
                        }.get(priority, '⚪')

                        self.calendar_display.insert(tk.END,
                            f"{priority_emoji} {start.strftime('%H:%M')} - {end.strftime('%H:%M')}: "
                            f"{event.get('summary', 'Untitled')}")

                        if event.get('location'):
                            self.calendar_display.insert(tk.END, f" 📍 {event['location']}")

                        if tags:
                            self.calendar_display.insert(tk.END, f" 🏷️ {tags}")

                        self.calendar_display.insert(tk.END, "\n")
                else:
                    self.calendar_display.insert(tk.END, "  No events scheduled\n")

        except Exception as e:
            self.calendar_display.insert(tk.END, f"Error loading calendar: {str(e)}\n")

    def sync_google_calendar(self):
        """Sync with Google Calendar and import historical events"""
        from ai_schedule_agent.models.event import Event

        try:
            self.update_status("Authenticating with Google Calendar...")
            self.calendar.authenticate()

            self.update_status("Syncing events...")

            # Import historical events for learning
            historical_events = self.calendar.get_events(
                (datetime.datetime.now() - timedelta(days=30)).isoformat() + 'Z',
                datetime.datetime.now().isoformat() + 'Z'
            )

            for g_event in historical_events:
                if 'dateTime' in g_event.get('start', {}):
                    # Convert Google event to our Event model
                    event = Event(
                        title=g_event.get('summary', ''),
                        description=g_event.get('description', ''),
                        start_time=datetime.datetime.fromisoformat(
                            g_event['start']['dateTime'].replace('Z', '+00:00')
                        ),
                        end_time=datetime.datetime.fromisoformat(
                            g_event['end']['dateTime'].replace('Z', '+00:00')
                        ),
                        location=g_event.get('location', ''),
                        google_event_id=g_event['id']
                    )

                    # Add to pattern learner
                    self.pattern_learner.add_event(event)

            self.refresh()
            self.update_status("Sync completed successfully")
            messagebox.showinfo("Success", "Calendar synced successfully!")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to sync: {str(e)}")
            self.update_status("Sync failed")
