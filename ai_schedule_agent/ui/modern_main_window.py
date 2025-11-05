"""Modern sidebar-based main window for AI Schedule Agent"""

import os
import json
import tkinter as tk
from tkinter import ttk, messagebox, font as tkfont
import threading
import datetime
from datetime import timedelta

from ai_schedule_agent.config.manager import ConfigManager
from ai_schedule_agent.models.user_profile import UserProfile
from ai_schedule_agent.models.event import Event
from ai_schedule_agent.models.enums import Priority
from ai_schedule_agent.core.scheduling_engine import SchedulingEngine
from ai_schedule_agent.core.nlp_processor import NLPProcessor
from ai_schedule_agent.integrations.google_calendar import CalendarIntegration
from ai_schedule_agent.integrations.notifications import NotificationManager
from ai_schedule_agent.utils.logging import logger
from ai_schedule_agent.utils.i18n import get_i18n
from ai_schedule_agent.ui.modern_theme import ModernTheme


class ModernSchedulerUI:
    """Modern AI Schedule Agent UI with sidebar layout and all original features"""

    def __init__(self):
        self.root = tk.Tk()
        self.config = ConfigManager()
        self.i18n = get_i18n(self.config)

        # Window configuration
        self.root.title(self.i18n.t('app_title'))
        self.root.geometry("1400x900")
        self.root.minsize(1200, 700)

        # Apply modern styling
        self.setup_styles()

        # Initialize backend components
        self.user_profile = self.load_or_create_profile()
        self.calendar = CalendarIntegration()
        self.engine = SchedulingEngine(self.user_profile, self.calendar)
        self.nlp_processor = NLPProcessor()
        self.notification_manager = NotificationManager(self.user_profile.email)

        # UI state
        self.selected_filters = set()
        self.current_view = 'day'  # day, week, month
        self.current_date = datetime.datetime.now()

        # Build the modern UI
        self.setup_modern_ui()

        # Start background tasks
        self.start_background_tasks()

    def setup_styles(self):
        """Setup modern UI styles"""
        style = ttk.Style()
        ModernTheme.configure_styles(style, self.root)
        self.root.configure(bg=ModernTheme.COLORS['bg_primary'])
        logger.info("Modern healthcare UI theme configured")

    def load_or_create_profile(self) -> UserProfile:
        """Load or create user profile"""
        profile_file = self.config.get_path('user_profile', '.config/user_profile.json')

        if os.path.exists(profile_file):
            with open(profile_file, 'r') as f:
                data = json.load(f)
                return UserProfile.from_dict(data)
        else:
            profile = UserProfile()
            profile.working_hours = {
                'Monday': ('09:00', '17:00'),
                'Tuesday': ('09:00', '17:00'),
                'Wednesday': ('09:00', '17:00'),
                'Thursday': ('09:00', '17:00'),
                'Friday': ('09:00', '17:00')
            }
            profile.energy_patterns = {
                9: 0.7, 10: 0.9, 11: 1.0, 12: 0.8,
                13: 0.6, 14: 0.7, 15: 0.8, 16: 0.7
            }
            return profile

    def save_profile(self):
        """Save user profile"""
        profile_file = self.config.get_path('user_profile', '.config/user_profile.json')
        with open(profile_file, 'w') as f:
            json.dump(self.user_profile.to_dict(), f, indent=2, default=str)

    def setup_modern_ui(self):
        """Setup the modern AI Schedule Agent UI layout with all original features"""
        logger.info("Setting up modern AI Schedule Agent UI...")

        # Main container with gradient background
        main_container = tk.Frame(self.root, bg=ModernTheme.COLORS['bg_primary'])
        main_container.pack(fill='both', expand=True)

        # === LEFT SIDEBAR ===
        self.create_sidebar(main_container)

        # === RIGHT CONTENT AREA ===
        right_container = tk.Frame(main_container, bg=ModernTheme.COLORS['bg_primary'])
        right_container.pack(side='left', fill='both', expand=True)

        # Main content area with all tabs
        self.create_main_content(right_container)

        # Status bar at bottom
        self.create_status_bar(right_container)

        logger.info("Modern AI Schedule Agent UI setup complete")

    def create_sidebar(self, parent):
        """Create left sidebar with navigation to all original features"""
        sidebar = tk.Frame(parent, bg=ModernTheme.COLORS['bg_sidebar'], width=280)
        sidebar.pack(side='left', fill='y', padx=0, pady=0)
        sidebar.pack_propagate(False)

        # === TOP SECTION: Logo and App Name ===
        top_section = tk.Frame(sidebar, bg=ModernTheme.COLORS['bg_sidebar'])
        top_section.pack(fill='x', padx=20, pady=20)

        # App logo/icon
        logo_label = tk.Label(
            top_section,
            text="🤖",
            font=('Segoe UI Emoji', 32),
            bg=ModernTheme.COLORS['bg_sidebar'],
            fg=ModernTheme.COLORS['primary']
        )
        logo_label.pack(pady=(0, 10))

        # App name
        app_name = tk.Label(
            top_section,
            text="AI Schedule Agent",
            font=('Microsoft YaHei', 14, 'bold'),
            bg=ModernTheme.COLORS['bg_sidebar'],
            fg=ModernTheme.COLORS['text_primary']
        )
        app_name.pack()

        # === NAVIGATION SECTION ===
        nav_section = tk.Frame(sidebar, bg=ModernTheme.COLORS['bg_sidebar'])
        nav_section.pack(fill='x', padx=20, pady=(30, 10))

        # Navigation buttons for all original tabs
        self.nav_buttons = {}
        nav_items = [
            ("quick_schedule", "⚡ Quick Schedule", 0),
            ("calendar", "📅 Calendar View", 1),
            ("settings", "⚙️ Settings", 2),
            ("insights", "📊 Insights", 3),
        ]

        for nav_id, label, tab_index in nav_items:
            self.create_nav_button(nav_section, nav_id, label, tab_index)

        # === DIVIDER ===
        divider = tk.Frame(sidebar, bg=ModernTheme.COLORS['divider'], height=1)
        divider.pack(fill='x', padx=20, pady=20)

        # === FILTER SECTION ===
        filter_section = tk.Frame(sidebar, bg=ModernTheme.COLORS['bg_sidebar'])
        filter_section.pack(fill='both', expand=True, padx=20, pady=10)

        # Filter title
        filter_title = tk.Label(
            filter_section,
            text="Event Filters",
            font=('Microsoft YaHei', 11, 'bold'),
            bg=ModernTheme.COLORS['bg_sidebar'],
            fg=ModernTheme.COLORS['text_primary'],
            anchor='w'
        )
        filter_title.pack(fill='x', pady=(0, 15))

        # Event type filters with color dots
        event_types = [
            ("meeting", "Meetings", ModernTheme.CONSULTATION_COLORS['meeting']),
            ("focus", "Focus Work", ModernTheme.CONSULTATION_COLORS['focus']),
            ("break", "Breaks", ModernTheme.CONSULTATION_COLORS['break']),
            ("personal", "Personal", ModernTheme.CONSULTATION_COLORS['personal']),
            ("task", "Tasks", ModernTheme.CONSULTATION_COLORS['task']),
            ("other", "Other", ModernTheme.CONSULTATION_COLORS['other']),
        ]

        self.filter_buttons = {}
        for event_type, label, color in event_types:
            self.create_filter_button(filter_section, event_type, label, color)

    def create_nav_button(self, parent, nav_id, label, tab_index):
        """Create a navigation button for switching tabs"""
        btn_frame = tk.Frame(parent, bg=ModernTheme.COLORS['bg_sidebar'])
        btn_frame.pack(fill='x', pady=4)

        nav_btn = tk.Label(
            btn_frame,
            text=label,
            font=('Microsoft YaHei', 11),
            bg=ModernTheme.COLORS['bg_sidebar'],
            fg=ModernTheme.COLORS['text_secondary'],
            cursor='hand2',
            anchor='w',
            padx=15,
            pady=10
        )
        nav_btn.pack(fill='x')

        def on_click(e=None):
            # Switch to the selected tab
            if hasattr(self, 'content_notebook'):
                self.content_notebook.select(tab_index)
            # Update button styles
            for btn_id, btn in self.nav_buttons.items():
                if btn_id == nav_id:
                    btn.config(
                        bg=ModernTheme.COLORS['primary'],
                        fg='white',
                        font=('Microsoft YaHei', 11, 'bold')
                    )
                else:
                    btn.config(
                        bg=ModernTheme.COLORS['bg_sidebar'],
                        fg=ModernTheme.COLORS['text_secondary'],
                        font=('Microsoft YaHei', 11)
                    )

        nav_btn.bind('<Button-1>', on_click)
        self.add_hover_effect_nav(nav_btn, nav_id)
        self.nav_buttons[nav_id] = nav_btn

        # Set first as default
        if tab_index == 0:
            nav_btn.config(
                bg=ModernTheme.COLORS['primary'],
                fg='white',
                font=('Microsoft YaHei', 11, 'bold')
            )

    def add_hover_effect_nav(self, widget, nav_id):
        """Add hover effect to navigation button"""
        def on_enter(e):
            if widget.cget('bg') != ModernTheme.COLORS['primary']:
                widget.config(bg=ModernTheme.COLORS['hover'])

        def on_leave(e):
            if widget.cget('bg') != ModernTheme.COLORS['primary']:
                widget.config(bg=ModernTheme.COLORS['bg_sidebar'])

        widget.bind('<Enter>', on_enter)
        widget.bind('<Leave>', on_leave)

    def create_filter_button(self, parent, event_type, label, color):
        """Create a filter button with color dot"""
        filter_frame = tk.Frame(parent, bg=ModernTheme.COLORS['bg_sidebar'])
        filter_frame.pack(fill='x', pady=6)

        # Color dot
        dot_canvas = tk.Canvas(
            filter_frame,
            width=12,
            height=12,
            bg=ModernTheme.COLORS['bg_sidebar'],
            highlightthickness=0
        )
        dot_canvas.pack(side='left', padx=(0, 10))
        dot_canvas.create_oval(2, 2, 10, 10, fill=color, outline='')

        # Label button
        label_btn = tk.Label(
            filter_frame,
            text=label,
            font=('Microsoft YaHei', 10),
            bg=ModernTheme.COLORS['bg_sidebar'],
            fg=ModernTheme.COLORS['text_secondary'],
            cursor='hand2',
            anchor='w'
        )
        label_btn.pack(side='left', fill='x', expand=True)

        # Click handler
        def toggle_filter(e=None):
            if event_type in self.selected_filters:
                self.selected_filters.remove(event_type)
                label_btn.config(fg=ModernTheme.COLORS['text_secondary'])
            else:
                self.selected_filters.add(event_type)
                label_btn.config(fg=ModernTheme.COLORS['text_primary'], font=('Microsoft YaHei', 10, 'bold'))
            self.refresh_calendar()

        label_btn.bind('<Button-1>', toggle_filter)
        self.filter_buttons[event_type] = (label_btn, dot_canvas)

    def create_main_content(self, parent):
        """Create main content area with all original tabs integrated"""
        # Content container
        content_container = tk.Frame(parent, bg=ModernTheme.COLORS['bg_primary'])
        content_container.pack(fill='both', expand=True, padx=10, pady=10)

        # Create notebook (tabbed interface) but hide the tabs - navigation is via sidebar
        style = ttk.Style()
        style.layout('Hidden.TNotebook.Tab', [])  # Hide tab headers

        self.content_notebook = ttk.Notebook(content_container, style='Hidden.TNotebook')
        self.content_notebook.pack(fill='both', expand=True)

        # === Tab 1: Quick Schedule ===
        logger.info("Loading Quick Schedule tab...")
        from ai_schedule_agent.ui.tabs.quick_schedule_tab import QuickScheduleTab
        quick_tab_frame = ttk.Frame(self.content_notebook)
        self.content_notebook.add(quick_tab_frame, text='Quick Schedule')
        self.quick_schedule_tab = QuickScheduleTab(
            quick_tab_frame,
            self.nlp_processor,
            self.engine,
            self.schedule_event,
            self.update_status
        )

        # === Tab 2: Calendar View ===
        logger.info("Loading Calendar View tab...")
        from ai_schedule_agent.ui.tabs.calendar_view_tab import CalendarViewTab
        calendar_tab_frame = ttk.Frame(self.content_notebook)
        self.content_notebook.add(calendar_tab_frame, text='Calendar View')
        self.calendar_view_tab = CalendarViewTab(
            calendar_tab_frame,
            self.calendar,
            self.engine.pattern_learner,
            self.update_status
        )

        # === Tab 3: Settings ===
        logger.info("Loading Settings tab...")
        from ai_schedule_agent.ui.tabs.settings_tab import SettingsTab
        settings_tab_frame = ttk.Frame(self.content_notebook)
        self.content_notebook.add(settings_tab_frame, text='Settings')
        self.settings_tab = SettingsTab(
            settings_tab_frame,
            self.user_profile,
            self.save_profile
        )

        # === Tab 4: Insights - LAZY LOAD ===
        logger.info("Creating Insights tab placeholder...")
        self.insights_tab_frame = ttk.Frame(self.content_notebook)
        self.content_notebook.add(self.insights_tab_frame, text='Insights')
        self.insights_tab = None
        self._insights_loaded = False

        # Bind tab change to lazy load insights
        self.content_notebook.bind('<<NotebookTabChanged>>', self._on_tab_changed)

        logger.info("All tabs loaded")

    def _on_tab_changed(self, event):
        """Handle tab change - lazy load Insights tab"""
        selected_tab = self.content_notebook.index(self.content_notebook.select())

        # Load Insights tab on first access (index 3)
        if selected_tab == 3 and not self._insights_loaded:
            self._insights_loaded = True
            logger.info("Loading Insights tab for first time...")
            self.update_status(self.i18n.t('loading_analytics'))

            from ai_schedule_agent.ui.tabs.insights_tab import InsightsTab
            self.insights_tab = InsightsTab(
                self.insights_tab_frame,
                self.engine,
                self.calendar,
                self.user_profile,
                self.notification_manager
            )

            logger.info("Insights tab loaded")
            self.update_status(self.i18n.t('ready'))

    def schedule_event(self, event: Event):
        """Schedule an event (integrated from original UI)"""
        try:
            # Add to Google Calendar
            event_id = self.calendar.create_event(event)
            if event_id:
                event.google_event_id = event_id

                # Add to pattern learner
                self.engine.pattern_learner.add_event(event)

                # Schedule reminders
                if event.priority == Priority.HIGH or event.priority == Priority.CRITICAL:
                    self.notification_manager.schedule_reminder(event, 30)
                else:
                    self.notification_manager.schedule_reminder(event, 15)

                # Update displays
                if hasattr(self, 'calendar_view_tab') and self.calendar_view_tab:
                    self.calendar_view_tab.refresh()

                # Show success message
                if hasattr(self, 'quick_schedule_tab') and self.quick_schedule_tab:
                    self.quick_schedule_tab.display_result(f"✅ Event '{event.title}' scheduled successfully!")
                self.update_status(f"Event scheduled: {event.title}")

                # Check for batch opportunities
                suggestions = self.engine.suggest_batch_opportunities()
                if suggestions and hasattr(self, 'quick_schedule_tab') and self.quick_schedule_tab:
                    self.quick_schedule_tab.display_result(f"💡 Suggestion: {suggestions[0]['message']}")

            else:
                messagebox.showerror("Error", "Failed to create event in Google Calendar")

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def create_status_bar(self, parent):
        """Create bottom status bar"""
        self.status_bar = tk.Label(
            parent,
            text=self.i18n.t('ready'),
            font=('Microsoft YaHei', 9),
            bg=ModernTheme.COLORS['bg_secondary'],
            fg=ModernTheme.COLORS['text_secondary'],
            anchor='w',
            padx=20,
            pady=8
        )
        self.status_bar.pack(side='bottom', fill='x')

    def add_hover_effect(self, widget, hover_color, normal_color):
        """Add hover effect to a widget"""
        widget.bind('<Enter>', lambda e: widget.config(bg=hover_color))
        widget.bind('<Leave>', lambda e: widget.config(bg=normal_color))

    def update_status(self, message):
        """Update status bar"""
        if hasattr(self, 'status_bar'):
            self.status_bar.config(text=message)
            self.root.update_idletasks()

    def start_background_tasks(self):
        """Start background threads for notifications and auto-save"""
        # Notification processor thread
        def process_notifications():
            while True:
                try:
                    # Check notification queue
                    if not self.notification_manager.notification_queue.empty():
                        notification = self.notification_manager.notification_queue.get()

                        # Check if it's time to send
                        if notification['time'] <= datetime.datetime.now():
                            event = notification['event']

                            # Send desktop notification
                            self.notification_manager.send_desktop_notification(
                                f"Reminder: {event.title}",
                                f"Starting at {event.start_time.strftime('%H:%M')}"
                            )

                            # Send email for important events
                            if event.priority in [Priority.HIGH, Priority.CRITICAL]:
                                self.notification_manager.send_email_notification(
                                    f"Important Event: {event.title}",
                                    f"Your event '{event.title}' is starting at {event.start_time}.\n"
                                    f"Location: {event.location}\n"
                                    f"Participants: {', '.join(event.participants)}"
                                )
                        else:
                            # Put it back in queue if not time yet
                            self.notification_manager.notification_queue.put(notification)

                    # Sleep for a minute before checking again
                    threading.Event().wait(60)

                except Exception as e:
                    logger.error(f"Notification processing error: {e}")

        # Start notification thread
        notification_thread = threading.Thread(target=process_notifications, daemon=True)
        notification_thread.start()

        # Auto-save thread
        def auto_save():
            while True:
                try:
                    self.save_profile()
                    threading.Event().wait(300)  # Save every 5 minutes
                except Exception as e:
                    logger.error(f"Auto-save error: {e}")

        save_thread = threading.Thread(target=auto_save, daemon=True)
        save_thread.start()

    def run(self):
        """Run the application"""
        self.root.mainloop()
