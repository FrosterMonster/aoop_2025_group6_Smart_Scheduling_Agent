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
        self.tooltip = None  # Initialize tooltip tracking

        # Modern color scheme with gradients and better contrast
        self.colors = {
            'bg_primary': '#fafbfc',
            'bg_secondary': '#f0f2f5',
            'bg_today': '#e8f4fd',
            'bg_selected': '#d0e9ff',
            'bg_weekend': '#f8f9fa',
            'bg_hover': '#f5f7fa',
            'priority_low': '#34a853',     # Google Green
            'priority_medium': '#4285f4',   # Google Blue
            'priority_high': '#fbbc04',     # Google Yellow
            'priority_critical': '#ea4335', # Google Red
            'border': '#dadce0',
            'border_light': '#e8eaed',
            'text_primary': '#202124',
            'text_secondary': '#5f6368',
            'text_light': '#80868b',
            'accent_blue': '#1a73e8',
            'accent_purple': '#8430ce',
            'accent_green': '#1e8e3e',
            'card_shadow': '#00000010'
        }

        self.setup_ui()

    def setup_ui(self):
        """Setup calendar view tab UI with modern design"""

        # Header frame with navigation and gradient effect
        header_frame = tk.Frame(self.parent, bg=self.colors['bg_secondary'], height=70)
        header_frame.pack(fill='x', padx=0, pady=0)
        header_frame.pack_propagate(False)

        # Add subtle top border
        tk.Frame(header_frame, bg=self.colors['border'], height=1).pack(fill='x')

        # Navigation buttons with icons
        nav_frame = tk.Frame(header_frame, bg=self.colors['bg_secondary'])
        nav_frame.pack(side='left', padx=20, pady=15)

        # Style buttons with better spacing
        prev_btn = ttk.Button(nav_frame, text="◀", command=self.prev_period, width=3)
        prev_btn.pack(side='left', padx=2)

        today_btn = ttk.Button(nav_frame, text="Today", command=self.go_to_today, width=8)
        today_btn.pack(side='left', padx=2)

        next_btn = ttk.Button(nav_frame, text="▶", command=self.next_period, width=3)
        next_btn.pack(side='left', padx=2)

        # Current date display with larger, bolder font
        self.date_label = tk.Label(header_frame, text="", font=('Segoe UI', 18, 'bold'),
                                   bg=self.colors['bg_secondary'], fg=self.colors['text_primary'])
        self.date_label.pack(side='left', padx=20)

        # View controls with modern styling
        controls_frame = tk.Frame(header_frame, bg=self.colors['bg_secondary'])
        controls_frame.pack(side='right', padx=20, pady=15)

        tk.Label(controls_frame, text="View:", bg=self.colors['bg_secondary'],
                fg=self.colors['text_secondary'], font=('Segoe UI', 10)).pack(side='left', padx=5)

        self.view_range_var = tk.StringVar(value="Month")
        view_range = ttk.Combobox(controls_frame, textvariable=self.view_range_var,
                                  values=["Week", "Month"], state='readonly', width=10,
                                  font=('Segoe UI', 10))
        view_range.pack(side='left', padx=5)
        view_range.bind('<<ComboboxSelected>>', lambda e: self.refresh())

        ttk.Button(controls_frame, text="🔄 Sync", command=self.sync_google_calendar, width=10).pack(side='left', padx=5)

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

        # Create day headers with modern styling
        day_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        header_frame = tk.Frame(self.calendar_display, bg=self.colors['bg_primary'])
        header_frame.pack(fill='x', pady=(10, 8))

        for i, day_name in enumerate(day_names):
            is_weekend = i >= 5
            header = tk.Label(header_frame, text=day_name.upper(),
                            font=('Segoe UI', 9, 'bold'),
                            bg=self.colors['bg_primary'],
                            fg=self.colors['text_secondary'] if not is_weekend else self.colors['accent_purple'],
                            padx=10, pady=6)
            header.grid(row=0, column=i, sticky='ew', padx=2)
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
        """Create a single day cell in month view with hover effects"""
        is_today = date_obj == today
        is_weekend = date_obj.weekday() >= 5

        # Choose background color
        if is_today:
            bg_color = self.colors['bg_today']
        elif is_weekend:
            bg_color = self.colors['bg_weekend']
        else:
            bg_color = self.colors['bg_primary']

        # Day frame with rounded corners effect and shadow - fixed height to prevent wiggling
        day_frame = tk.Frame(parent, bg=bg_color, relief='flat',
                           highlightbackground=self.colors['border_light'],
                           highlightthickness=1, height=120)  # Fixed minimum height
        day_frame.grid(row=0, column=column, sticky='nsew', padx=2, pady=2)
        day_frame.grid_propagate(False)  # Prevent frame from resizing based on content

        # Add hover effect without changing thickness to prevent wiggling
        def on_enter(e):
            day_frame.config(highlightbackground=self.colors['accent_blue'])

        def on_leave(e):
            day_frame.config(highlightbackground=self.colors['border_light'])

        day_frame.bind("<Enter>", on_enter)
        day_frame.bind("<Leave>", on_leave)

        # Header container for day number and event count
        header_container = tk.Frame(day_frame, bg=bg_color)
        header_container.pack(fill='x', padx=6, pady=4)

        # Day number with modern styling
        if is_today:
            # Today indicator as a circle
            day_circle = tk.Label(header_container, text=str(date_obj.day),
                                font=('Segoe UI', 11, 'bold'),
                                bg=self.colors['accent_blue'], fg='white',
                                width=3, height=1, relief='flat')
            day_circle.pack(side='left', padx=2)
        else:
            day_label = tk.Label(header_container, text=str(date_obj.day),
                               font=('Segoe UI', 11, 'bold' if events else 'normal'),
                               bg=bg_color,
                               fg=self.colors['text_primary'] if events else self.colors['text_light'],
                               anchor='w')
            day_label.pack(side='left', padx=2)

        # Event count badge
        if events:
            count_badge = tk.Label(header_container, text=f"●{len(events)}",
                                 font=('Segoe UI', 8),
                                 bg=bg_color,
                                 fg=self.colors['accent_blue'])
            count_badge.pack(side='right', padx=2)

        # Events container
        events_frame = tk.Frame(day_frame, bg=bg_color)
        events_frame.pack(fill='both', expand=True, padx=4, pady=2)

        # Show events (max 3 in month view)
        sorted_events = sorted(events, key=lambda x: x['start']['dateTime'])
        for i, event in enumerate(sorted_events[:3]):
            self.create_event_widget(events_frame, event, compact=True, date_obj=date_obj)

        if len(sorted_events) > 3:
            more_label = tk.Label(events_frame, text=f"+{len(sorted_events) - 3} more",
                                font=('Segoe UI', 7), fg=self.colors['accent_blue'],
                                bg=bg_color, cursor="hand2")
            more_label.pack(anchor='w', pady=2, padx=2)
            # Add click handler to show all events
            more_label.bind("<Button-1>", lambda e: self.show_day_events(date_obj, sorted_events))

        self.day_frames[date_obj] = day_frame

    def create_event_widget(self, parent, event, compact=False, date_obj=None):
        """Create an event display widget with hover and click effects"""
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
            event_frame = tk.Frame(parent, bg=event_color, relief='flat',
                                 cursor="hand2")
            event_frame.pack(fill='x', pady=1, padx=1)

            time_text = start.strftime('%H:%M')
            title_text = event.get('summary', 'Untitled')

            # Truncate title if too long
            display_title = (title_text[:18] + '...') if len(title_text) > 18 else title_text

            event_label = tk.Label(event_frame, text=f"• {time_text} {display_title}",
                                 font=('Segoe UI', 8), bg=event_color, fg='white',
                                 anchor='w', padx=4, pady=2)
            event_label.pack(fill='x')

            # Add hover effect
            def on_enter(e):
                event_frame.config(relief='raised', borderwidth=1)
                # Show tooltip
                self.show_event_tooltip(event_label, event, start, end)

            def on_leave(e):
                event_frame.config(relief='flat')
                self.hide_tooltip()

            def on_click(e):
                self.show_event_details(event, start, end)

            event_frame.bind("<Enter>", on_enter)
            event_frame.bind("<Leave>", on_leave)
            event_frame.bind("<Button-1>", on_click)
            event_label.bind("<Enter>", on_enter)
            event_label.bind("<Leave>", on_leave)
            event_label.bind("<Button-1>", on_click)

        else:
            event_frame = tk.Frame(parent, bg=event_color, relief='flat',
                                 cursor="hand2")
            event_frame.pack(fill='x', pady=3, padx=2)

            time_label = tk.Label(event_frame, text=f"🕐 {start.strftime('%H:%M')} - {end.strftime('%H:%M')}",
                                font=('Segoe UI', 9, 'bold'), bg=event_color, fg='white',
                                anchor='w', padx=6, pady=3)
            time_label.pack(fill='x')

            title_label = tk.Label(event_frame, text=event.get('summary', 'Untitled'),
                                 font=('Segoe UI', 10), bg=event_color, fg='white',
                                 anchor='w', padx=6, pady=2, wraplength=180)
            title_label.pack(fill='x')

            if event.get('location'):
                loc_label = tk.Label(event_frame, text=f"📍 {event['location']}",
                                   font=('Segoe UI', 8), bg=event_color, fg='white',
                                   anchor='w', padx=6, pady=2)
                loc_label.pack(fill='x')

            # Add hover and click effects
            def on_enter(e):
                event_frame.config(relief='raised', borderwidth=2)

            def on_leave(e):
                event_frame.config(relief='flat')

            def on_click(e):
                self.show_event_details(event, start, end)

            for widget in [event_frame, time_label, title_label]:
                widget.bind("<Enter>", on_enter)
                widget.bind("<Leave>", on_leave)
                widget.bind("<Button-1>", on_click)

    def show_event_tooltip(self, widget, event, start, end):
        """Show tooltip with event details on hover"""
        # Destroy any existing tooltip first
        self.hide_tooltip()

        try:
            # Create tooltip window
            self.tooltip = tk.Toplevel(widget)
            self.tooltip.wm_overrideredirect(True)

            # Position near mouse cursor
            try:
                x = widget.winfo_rootx() + 20
                y = widget.winfo_rooty() + 20
                self.tooltip.wm_geometry(f"+{x}+{y}")
            except:
                pass  # If widget not rendered yet, skip positioning

            # Tooltip content with modern design
            tooltip_frame = tk.Frame(self.tooltip, bg='#2d2d2d', relief='flat', borderwidth=0)
            tooltip_frame.pack(fill='both', expand=True)

            # Add subtle shadow effect with padding
            inner_frame = tk.Frame(tooltip_frame, bg='#2d2d2d')
            inner_frame.pack(fill='both', expand=True, padx=1, pady=1)

            title = tk.Label(inner_frame, text=event.get('summary', 'Untitled'),
                            font=('Segoe UI', 10, 'bold'), bg='#2d2d2d', fg='white',
                            padx=12, pady=6, anchor='w')
            title.pack(fill='x')

            time_info = tk.Label(inner_frame,
                               text=f"{start.strftime('%I:%M %p')} - {end.strftime('%I:%M %p')}",
                               font=('Segoe UI', 9), bg='#2d2d2d', fg='#aaaaaa',
                               padx=12, pady=2, anchor='w')
            time_info.pack(fill='x')

            if event.get('location'):
                loc = tk.Label(inner_frame, text=f"📍 {event['location']}",
                             font=('Segoe UI', 8), bg='#2d2d2d', fg='#aaaaaa',
                             padx=12, pady=2, anchor='w')
                loc.pack(fill='x')

            if event.get('description'):
                desc_text = event.get('description', '')
                if len(desc_text) > 100:
                    desc_text = desc_text[:100] + '...'
                desc = tk.Label(inner_frame, text=desc_text,
                              font=('Segoe UI', 8), bg='#2d2d2d', fg='#cccccc',
                              padx=12, pady=6, anchor='w', wraplength=280, justify='left')
                desc.pack(fill='x')

            # Bind tooltip itself to hide on mouse leave
            self.tooltip.bind("<Leave>", lambda e: self.hide_tooltip())

        except Exception as e:
            # Silently fail if tooltip creation fails
            self.hide_tooltip()

    def hide_tooltip(self):
        """Hide the tooltip safely"""
        try:
            if self.tooltip and self.tooltip.winfo_exists():
                self.tooltip.destroy()
        except:
            pass
        finally:
            self.tooltip = None

    def show_event_details(self, event, start, end):
        """Show detailed event information in a modern popup"""
        # Hide tooltip first
        self.hide_tooltip()

        details_window = tk.Toplevel(self.parent)
        details_window.title("Event Details")
        details_window.geometry("500x550")
        details_window.configure(bg=self.colors['bg_primary'])
        details_window.resizable(False, False)

        # Make it modal
        details_window.transient(self.parent)
        details_window.grab_set()

        # Get priority for color
        props = event.get('extendedProperties', {}).get('private', {})
        priority = props.get('priority', '2')
        color_map = {
            '1': self.colors['priority_low'],
            '2': self.colors['priority_medium'],
            '3': self.colors['priority_high'],
            '4': self.colors['priority_critical']
        }
        header_color = color_map.get(priority, self.colors['accent_blue'])

        # Header with gradient effect
        header = tk.Frame(details_window, bg=header_color, height=80)
        header.pack(fill='x')
        header.pack_propagate(False)

        title_label = tk.Label(header, text=event.get('summary', 'Untitled Event'),
                             font=('Segoe UI', 16, 'bold'), bg=header_color,
                             fg='white', padx=25, pady=20, anchor='w', wraplength=450)
        title_label.pack(fill='both')

        # Content area with card design
        content = tk.Frame(details_window, bg=self.colors['bg_primary'])
        content.pack(fill='both', expand=True, padx=25, pady=20)

        # Time card
        time_card = tk.Frame(content, bg=self.colors['bg_secondary'], relief='flat')
        time_card.pack(fill='x', pady=(0, 15))

        time_inner = tk.Frame(time_card, bg=self.colors['bg_secondary'])
        time_inner.pack(fill='both', padx=15, pady=12)

        tk.Label(time_inner, text="🕐  Time", font=('Segoe UI', 11, 'bold'),
                bg=self.colors['bg_secondary'], fg=self.colors['text_primary']).pack(anchor='w')

        duration = end - start
        hours = duration.seconds // 3600
        minutes = (duration.seconds % 3600) // 60
        duration_str = f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"

        tk.Label(time_inner,
                text=f"{start.strftime('%A, %B %d, %Y')}\n{start.strftime('%I:%M %p')} - {end.strftime('%I:%M %p')} ({duration_str})",
                font=('Segoe UI', 10), bg=self.colors['bg_secondary'],
                fg=self.colors['text_secondary'], justify='left').pack(anchor='w', pady=(5, 0))

        # Location card (if exists)
        if event.get('location'):
            loc_card = tk.Frame(content, bg=self.colors['bg_secondary'], relief='flat')
            loc_card.pack(fill='x', pady=(0, 15))

            loc_inner = tk.Frame(loc_card, bg=self.colors['bg_secondary'])
            loc_inner.pack(fill='both', padx=15, pady=12)

            tk.Label(loc_inner, text="📍  Location", font=('Segoe UI', 11, 'bold'),
                    bg=self.colors['bg_secondary'], fg=self.colors['text_primary']).pack(anchor='w')
            tk.Label(loc_inner, text=event['location'],
                    font=('Segoe UI', 10), bg=self.colors['bg_secondary'],
                    fg=self.colors['text_secondary'], wraplength=430).pack(anchor='w', pady=(5, 0))

        # Description card (if exists)
        if event.get('description'):
            desc_card = tk.Frame(content, bg=self.colors['bg_secondary'], relief='flat')
            desc_card.pack(fill='both', expand=True, pady=(0, 15))

            desc_inner = tk.Frame(desc_card, bg=self.colors['bg_secondary'])
            desc_inner.pack(fill='both', padx=15, pady=12)

            tk.Label(desc_inner, text="📝  Description", font=('Segoe UI', 11, 'bold'),
                    bg=self.colors['bg_secondary'], fg=self.colors['text_primary']).pack(anchor='w')

            desc_text = scrolledtext.ScrolledText(desc_inner, height=10, wrap=tk.WORD,
                                                 font=('Segoe UI', 10),
                                                 bg='white',
                                                 fg=self.colors['text_secondary'],
                                                 relief='flat', padx=5, pady=5,
                                                 borderwidth=0, highlightthickness=0)
            desc_text.insert('1.0', event['description'])
            desc_text.config(state='disabled')
            desc_text.pack(fill='both', expand=True, pady=(8, 0))

        # Action buttons
        button_frame = tk.Frame(details_window, bg=self.colors['bg_primary'])
        button_frame.pack(fill='x', padx=25, pady=(0, 20))

        close_btn = ttk.Button(button_frame, text="Close", command=details_window.destroy, width=12)
        close_btn.pack(side='right')

        # Center the window
        details_window.update_idletasks()
        x = (details_window.winfo_screenwidth() // 2) - (details_window.winfo_width() // 2)
        y = (details_window.winfo_screenheight() // 2) - (details_window.winfo_height() // 2)
        details_window.geometry(f"+{x}+{y}")

    def show_day_events(self, date_obj, events):
        """Show all events for a specific day in a modern popup"""
        # Hide tooltip first
        self.hide_tooltip()

        day_window = tk.Toplevel(self.parent)
        day_window.title(f"Events - {date_obj.strftime('%B %d, %Y')}")
        day_window.geometry("500x650")
        day_window.configure(bg=self.colors['bg_primary'])
        day_window.resizable(False, True)

        # Make it modal
        day_window.transient(self.parent)
        day_window.grab_set()

        # Header with modern gradient
        header = tk.Frame(day_window, bg=self.colors['accent_blue'], height=80)
        header.pack(fill='x')
        header.pack_propagate(False)

        # Day name in header
        day_name = date_obj.strftime('%A')
        date_str = date_obj.strftime('%B %d, %Y')

        header_content = tk.Frame(header, bg=self.colors['accent_blue'])
        header_content.pack(fill='both', expand=True, padx=25, pady=15)

        tk.Label(header_content, text=day_name,
                font=('Segoe UI', 20, 'bold'), bg=self.colors['accent_blue'],
                fg='white', anchor='w').pack(anchor='w')
        tk.Label(header_content, text=date_str,
                font=('Segoe UI', 11), bg=self.colors['accent_blue'],
                fg='white', anchor='w').pack(anchor='w')

        # Event count badge
        count_frame = tk.Frame(day_window, bg=self.colors['bg_primary'])
        count_frame.pack(fill='x', padx=25, pady=(15, 10))

        count_badge = tk.Frame(count_frame, bg=self.colors['accent_blue'])
        count_badge.pack(side='left')

        tk.Label(count_badge, text=f"  {len(events)} event(s)  ",
                font=('Segoe UI', 10, 'bold'), bg=self.colors['accent_blue'],
                fg='white', padx=8, pady=4).pack()

        # Events list with scrollbar
        canvas = tk.Canvas(day_window, bg=self.colors['bg_primary'],
                          highlightthickness=0, bd=0)
        scrollbar = ttk.Scrollbar(day_window, orient="vertical", command=canvas.yview)

        events_container = tk.Frame(canvas, bg=self.colors['bg_primary'])
        events_container.bind("<Configure>",
                             lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        canvas.create_window((0, 0), window=events_container, anchor="nw", width=470)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True, padx=(25, 0))
        scrollbar.pack(side="right", fill="y", padx=(0, 25))

        # Display all events with cards
        sorted_events = sorted(events, key=lambda x: x['start']['dateTime'])
        for i, event in enumerate(sorted_events):
            event_card = tk.Frame(events_container, bg=self.colors['bg_secondary'],
                                relief='flat')
            event_card.pack(fill='x', pady=5, padx=5)

            # Create event content inside card
            start = datetime.datetime.fromisoformat(event['start']['dateTime'].replace('Z', '+00:00'))
            end = datetime.datetime.fromisoformat(event['end']['dateTime'].replace('Z', '+00:00'))

            # Get priority color
            props = event.get('extendedProperties', {}).get('private', {})
            priority = props.get('priority', '2')
            color_map = {
                '1': self.colors['priority_low'],
                '2': self.colors['priority_medium'],
                '3': self.colors['priority_high'],
                '4': self.colors['priority_critical']
            }
            event_color = color_map.get(priority, self.colors['priority_medium'])

            # Color strip
            color_strip = tk.Frame(event_card, bg=event_color, width=4)
            color_strip.pack(side='left', fill='y')

            # Event info
            info_frame = tk.Frame(event_card, bg=self.colors['bg_secondary'])
            info_frame.pack(side='left', fill='both', expand=True, padx=12, pady=10)

            tk.Label(info_frame, text=event.get('summary', 'Untitled'),
                    font=('Segoe UI', 11, 'bold'), bg=self.colors['bg_secondary'],
                    fg=self.colors['text_primary'], anchor='w').pack(anchor='w')

            tk.Label(info_frame,
                    text=f"🕐 {start.strftime('%I:%M %p')} - {end.strftime('%I:%M %p')}",
                    font=('Segoe UI', 9), bg=self.colors['bg_secondary'],
                    fg=self.colors['text_secondary'], anchor='w').pack(anchor='w', pady=(2, 0))

            if event.get('location'):
                tk.Label(info_frame, text=f"📍 {event['location']}",
                        font=('Segoe UI', 9), bg=self.colors['bg_secondary'],
                        fg=self.colors['text_secondary'], anchor='w').pack(anchor='w', pady=(2, 0))

            # Make card clickable
            def make_click_handler(e, s, en):
                return lambda _: self.show_event_details(e, s, en)

            event_card.config(cursor="hand2")
            event_card.bind("<Button-1>", make_click_handler(event, start, end))

            # Hover effect
            def make_hover_handler(card):
                def on_enter(e):
                    card.config(bg=self.colors['bg_hover'])
                    for child in card.winfo_children():
                        if isinstance(child, tk.Frame) and child != color_strip:
                            child.config(bg=self.colors['bg_hover'])
                            for subchild in child.winfo_children():
                                if isinstance(subchild, tk.Label):
                                    subchild.config(bg=self.colors['bg_hover'])
                def on_leave(e):
                    card.config(bg=self.colors['bg_secondary'])
                    for child in card.winfo_children():
                        if isinstance(child, tk.Frame) and child != color_strip:
                            child.config(bg=self.colors['bg_secondary'])
                            for subchild in child.winfo_children():
                                if isinstance(subchild, tk.Label):
                                    subchild.config(bg=self.colors['bg_secondary'])
                return on_enter, on_leave

            enter_handler, leave_handler = make_hover_handler(event_card)
            event_card.bind("<Enter>", enter_handler)
            event_card.bind("<Leave>", leave_handler)

        # Close button
        button_frame = tk.Frame(day_window, bg=self.colors['bg_primary'])
        button_frame.pack(fill='x', padx=25, pady=20)
        ttk.Button(button_frame, text="Close", command=day_window.destroy, width=12).pack(side='right')

        # Center the window
        day_window.update_idletasks()
        x = (day_window.winfo_screenwidth() // 2) - (day_window.winfo_width() // 2)
        y = (day_window.winfo_screenheight() // 2) - (day_window.winfo_height() // 2)
        day_window.geometry(f"+{x}+{y}")

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
