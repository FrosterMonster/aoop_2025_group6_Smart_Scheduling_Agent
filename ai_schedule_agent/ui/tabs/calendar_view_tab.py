"""Calendar view tab for displaying events"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import datetime
from datetime import timedelta
import calendar
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
        self.current_date = datetime.datetime.now()
        self.selected_date = None
        self.day_frames = {}

        # Color scheme
        self.colors = {
            'bg_primary': '#ffffff',
            'bg_secondary': '#f5f5f5',
            'bg_today': '#e3f2fd',
            'bg_selected': '#bbdefb',
            'bg_weekend': '#fafafa',
            'priority_low': '#4caf50',
            'priority_medium': '#2196f3',
            'priority_high': '#ff9800',
            'priority_critical': '#f44336',
            'border': '#e0e0e0',
            'text_primary': '#212121',
            'text_secondary': '#757575'
        }

        self.setup_ui()

    def setup_ui(self):
        """Setup calendar view tab UI"""

        # Header frame with navigation
        header_frame = tk.Frame(self.parent, bg=self.colors['bg_secondary'], height=60)
        header_frame.pack(fill='x', padx=0, pady=0)
        header_frame.pack_propagate(False)

        # Navigation buttons
        nav_frame = tk.Frame(header_frame, bg=self.colors['bg_secondary'])
        nav_frame.pack(side='left', padx=20, pady=10)

        ttk.Button(nav_frame, text="◀ Prev", command=self.prev_period, width=8).pack(side='left', padx=2)
        ttk.Button(nav_frame, text="Today", command=self.go_to_today, width=8).pack(side='left', padx=2)
        ttk.Button(nav_frame, text="Next ▶", command=self.next_period, width=8).pack(side='left', padx=2)

        # Current date display
        self.date_label = tk.Label(header_frame, text="", font=('Arial', 16, 'bold'),
                                   bg=self.colors['bg_secondary'], fg=self.colors['text_primary'])
        self.date_label.pack(side='left', padx=20)

        # View controls
        controls_frame = tk.Frame(header_frame, bg=self.colors['bg_secondary'])
        controls_frame.pack(side='right', padx=20, pady=10)

        tk.Label(controls_frame, text="View:", bg=self.colors['bg_secondary'],
                fg=self.colors['text_secondary']).pack(side='left', padx=5)

        self.view_range_var = tk.StringVar(value="Month")
        view_range = ttk.Combobox(controls_frame, textvariable=self.view_range_var,
                                  values=["Week", "Month"], state='readonly', width=10)
        view_range.pack(side='left', padx=5)
        view_range.bind('<<ComboboxSelected>>', lambda e: self.refresh())

        ttk.Button(controls_frame, text="🔄 Sync", command=self.sync_google_calendar, width=8).pack(side='left', padx=5)

        # Main container with scrollbar
        main_container = tk.Frame(self.parent, bg=self.colors['bg_primary'])
        main_container.pack(fill='both', expand=True, padx=0, pady=0)

        # Canvas for scrolling
        canvas = tk.Canvas(main_container, bg=self.colors['bg_primary'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)

        self.scrollable_frame = tk.Frame(canvas, bg=self.colors['bg_primary'])
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Mouse wheel scrolling
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", on_mousewheel)

        # Calendar display area
        self.calendar_display = tk.Frame(self.scrollable_frame, bg=self.colors['bg_primary'])
        self.calendar_display.pack(fill='both', expand=True, padx=20, pady=20)

        # Initial load
        self.refresh()

    def prev_period(self):
        """Navigate to previous period"""
        view = self.view_range_var.get()
        if view == "Week":
            self.current_date -= timedelta(days=7)
        else:  # Month
            # Go to first day of previous month
            first_day = self.current_date.replace(day=1)
            self.current_date = (first_day - timedelta(days=1)).replace(day=1)
        self.refresh()

    def next_period(self):
        """Navigate to next period"""
        view = self.view_range_var.get()
        if view == "Week":
            self.current_date += timedelta(days=7)
        else:  # Month
            # Go to first day of next month
            year = self.current_date.year
            month = self.current_date.month
            if month == 12:
                self.current_date = datetime.datetime(year + 1, 1, 1)
            else:
                self.current_date = datetime.datetime(year, month + 1, 1)
        self.refresh()

    def go_to_today(self):
        """Go to today's date"""
        self.current_date = datetime.datetime.now()
        self.refresh()

    def refresh(self):
        """Refresh the calendar view"""
        # Clear existing display
        for widget in self.calendar_display.winfo_children():
            widget.destroy()

        self.day_frames = {}

        try:
            view_range = self.view_range_var.get()

            if view_range == "Week":
                self.display_week_view()
            else:  # Month
                self.display_month_view()

        except Exception as e:
            error_label = tk.Label(self.calendar_display, text=f"Error loading calendar: {str(e)}",
                                  fg='red', bg=self.colors['bg_primary'], font=('Arial', 12))
            error_label.pack(pady=20)

    def display_month_view(self):
        """Display calendar in month grid view"""
        year = self.current_date.year
        month = self.current_date.month

        # Update header label
        self.date_label.config(text=f"{calendar.month_name[month]} {year}")

        # Get calendar data
        cal = calendar.monthcalendar(year, month)
        today = datetime.date.today()

        # Fetch events for the month
        first_day = datetime.datetime(year, month, 1)
        if month == 12:
            last_day = datetime.datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            last_day = datetime.datetime(year, month + 1, 1) - timedelta(days=1)

        events = self.calendar.get_events(
            first_day.isoformat() + 'Z',
            (last_day + timedelta(days=1)).isoformat() + 'Z'
        )

        # Group events by day
        events_by_day = defaultdict(list)
        for event in events:
            if 'dateTime' in event.get('start', {}):
                start = datetime.datetime.fromisoformat(event['start']['dateTime'].replace('Z', '+00:00'))
                day = start.date()
                events_by_day[day].append(event)

        # Create day headers
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        header_frame = tk.Frame(self.calendar_display, bg=self.colors['bg_primary'])
        header_frame.pack(fill='x', pady=(0, 5))

        for i, day_name in enumerate(day_names):
            header = tk.Label(header_frame, text=day_name, font=('Arial', 11, 'bold'),
                            bg=self.colors['bg_secondary'], fg=self.colors['text_primary'],
                            padx=10, pady=8, relief='flat', borderwidth=1)
            header.grid(row=0, column=i, sticky='ew', padx=1)
            header_frame.columnconfigure(i, weight=1, uniform="day")

        # Create calendar grid
        for week_num, week in enumerate(cal):
            week_frame = tk.Frame(self.calendar_display, bg=self.colors['bg_primary'])
            week_frame.pack(fill='both', expand=True, pady=1)

            for day_num, day in enumerate(week):
                if day == 0:
                    # Empty cell for days outside current month
                    empty_frame = tk.Frame(week_frame, bg=self.colors['bg_secondary'],
                                          relief='flat', borderwidth=1)
                    empty_frame.grid(row=0, column=day_num, sticky='nsew', padx=1)
                else:
                    date_obj = datetime.date(year, month, day)
                    self.create_day_cell(week_frame, day_num, date_obj, events_by_day.get(date_obj, []), today)

                week_frame.columnconfigure(day_num, weight=1, uniform="day")
            week_frame.rowconfigure(0, weight=1)

    def display_week_view(self):
        """Display calendar in week view with time slots"""
        # Calculate week start (Monday)
        current = self.current_date
        week_start = current - timedelta(days=current.weekday())
        week_end = week_start + timedelta(days=6)

        # Update header label
        self.date_label.config(text=f"Week of {week_start.strftime('%b %d, %Y')}")

        # Fetch events for the week
        events = self.calendar.get_events(
            week_start.isoformat() + 'Z',
            (week_end + timedelta(days=1)).isoformat() + 'Z'
        )

        # Group events by day
        events_by_day = defaultdict(list)
        for event in events:
            if 'dateTime' in event.get('start', {}):
                start = datetime.datetime.fromisoformat(event['start']['dateTime'].replace('Z', '+00:00'))
                day = start.date()
                events_by_day[day].append(event)

        # Create day columns
        today = datetime.date.today()
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

        days_container = tk.Frame(self.calendar_display, bg=self.colors['bg_primary'])
        days_container.pack(fill='both', expand=True)

        for i in range(7):
            day_date = week_start + timedelta(days=i)
            day_frame = tk.Frame(days_container, bg=self.colors['bg_primary'],
                                relief='solid', borderwidth=1)
            day_frame.grid(row=0, column=i, sticky='nsew', padx=2, pady=2)

            # Day header
            is_today = day_date.date() == today
            header_bg = self.colors['bg_today'] if is_today else self.colors['bg_secondary']

            header = tk.Label(day_frame, text=f"{day_names[i]}\n{day_date.strftime('%b %d')}",
                            font=('Arial', 10, 'bold' if is_today else 'normal'),
                            bg=header_bg, fg=self.colors['text_primary'],
                            pady=10, relief='flat')
            header.pack(fill='x')

            # Events list
            events_frame = tk.Frame(day_frame, bg=self.colors['bg_primary'])
            events_frame.pack(fill='both', expand=True, padx=5, pady=5)

            day_events = sorted(events_by_day.get(day_date.date(), []),
                              key=lambda x: x['start']['dateTime'])

            if day_events:
                for event in day_events[:5]:  # Show max 5 events
                    self.create_event_widget(events_frame, event)

                if len(day_events) > 5:
                    more_label = tk.Label(events_frame, text=f"+ {len(day_events) - 5} more",
                                        font=('Arial', 8), fg=self.colors['text_secondary'],
                                        bg=self.colors['bg_primary'])
                    more_label.pack(pady=2)
            else:
                no_events = tk.Label(events_frame, text="No events",
                                    font=('Arial', 9), fg=self.colors['text_secondary'],
                                    bg=self.colors['bg_primary'])
                no_events.pack(pady=10)

            days_container.columnconfigure(i, weight=1, uniform="day")

    def create_day_cell(self, parent, column, date_obj, events, today):
        """Create a single day cell in month view"""
        is_today = date_obj == today
        is_weekend = date_obj.weekday() >= 5

        # Choose background color
        if is_today:
            bg_color = self.colors['bg_today']
        elif is_weekend:
            bg_color = self.colors['bg_weekend']
        else:
            bg_color = self.colors['bg_primary']

        # Day frame
        day_frame = tk.Frame(parent, bg=bg_color, relief='solid', borderwidth=1,
                           highlightbackground=self.colors['border'], highlightthickness=1)
        day_frame.grid(row=0, column=column, sticky='nsew', padx=1)

        # Day number
        day_label = tk.Label(day_frame, text=str(date_obj.day),
                           font=('Arial', 12, 'bold' if is_today else 'normal'),
                           bg=bg_color, fg=self.colors['text_primary'],
                           anchor='ne', padx=8, pady=5)
        day_label.pack(fill='x')

        # Events container
        events_frame = tk.Frame(day_frame, bg=bg_color)
        events_frame.pack(fill='both', expand=True, padx=3, pady=3)

        # Show events (max 3 in month view)
        sorted_events = sorted(events, key=lambda x: x['start']['dateTime'])
        for event in sorted_events[:3]:
            self.create_event_widget(events_frame, event, compact=True)

        if len(sorted_events) > 3:
            more_label = tk.Label(events_frame, text=f"+{len(sorted_events) - 3} more",
                                font=('Arial', 7), fg=self.colors['text_secondary'],
                                bg=bg_color)
            more_label.pack(anchor='w', pady=1)

        self.day_frames[date_obj] = day_frame

    def create_event_widget(self, parent, event, compact=False):
        """Create an event display widget"""
        start = datetime.datetime.fromisoformat(event['start']['dateTime'].replace('Z', '+00:00'))
        end = datetime.datetime.fromisoformat(event['end']['dateTime'].replace('Z', '+00:00'))

        # Get priority
        props = event.get('extendedProperties', {}).get('private', {})
        priority = props.get('priority', '2')

        # Choose color based on priority
        color_map = {
            '1': self.colors['priority_low'],
            '2': self.colors['priority_medium'],
            '3': self.colors['priority_high'],
            '4': self.colors['priority_critical']
        }
        event_color = color_map.get(priority, self.colors['priority_medium'])

        # Create event frame
        if compact:
            event_frame = tk.Frame(parent, bg=event_color, relief='flat', borderwidth=0)
            event_frame.pack(fill='x', pady=1, padx=2)

            time_text = start.strftime('%H:%M')
            title_text = event.get('summary', 'Untitled')

            event_label = tk.Label(event_frame, text=f"{time_text} {title_text[:20]}",
                                 font=('Arial', 7), bg=event_color, fg='white',
                                 anchor='w', padx=3, pady=1)
            event_label.pack(fill='x')
        else:
            event_frame = tk.Frame(parent, bg=event_color, relief='solid', borderwidth=1)
            event_frame.pack(fill='x', pady=2)

            time_label = tk.Label(event_frame, text=f"{start.strftime('%H:%M')} - {end.strftime('%H:%M')}",
                                font=('Arial', 8, 'bold'), bg=event_color, fg='white',
                                anchor='w', padx=5, pady=2)
            time_label.pack(fill='x')

            title_label = tk.Label(event_frame, text=event.get('summary', 'Untitled'),
                                 font=('Arial', 9), bg=event_color, fg='white',
                                 anchor='w', padx=5, pady=2, wraplength=150)
            title_label.pack(fill='x')

            if event.get('location'):
                loc_label = tk.Label(event_frame, text=f"📍 {event['location']}",
                                   font=('Arial', 7), bg=event_color, fg='white',
                                   anchor='w', padx=5, pady=1)
                loc_label.pack(fill='x')

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
