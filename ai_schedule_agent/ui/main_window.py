"""Main application window with i18n support"""

import os
import json
import tkinter as tk
from tkinter import ttk, messagebox, font
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
# Lazy import heavy tabs to speed up startup - imported when tabs are created
# from ai_schedule_agent.ui.tabs.quick_schedule_tab import QuickScheduleTab
# from ai_schedule_agent.ui.tabs.calendar_view_tab import CalendarViewTab
# from ai_schedule_agent.ui.tabs.settings_tab import SettingsTab
# from ai_schedule_agent.ui.tabs.insights_tab import InsightsTab
from ai_schedule_agent.utils.logging import logger
from ai_schedule_agent.utils.i18n import get_i18n
from ai_schedule_agent.ui.modern_theme import ModernTheme


class SchedulerUI:
    """Main UI for the scheduling agent"""

    def __init__(self):
        self.root = tk.Tk()
        self.config = ConfigManager()

        # Initialize i18n
        self.i18n = get_i18n(self.config)

        # Get window title and size from config
        app_title = self.i18n.t('app_title')
        window_width = self.config.get_setting('ui', 'window_width', default=1200)
        window_height = self.config.get_setting('ui', 'window_height', default=800)

        self.root.title(app_title)
        self.root.geometry(f"{window_width}x{window_height}")

        # Apply modern UI styling
        self.setup_styles()

        # Initialize components
        self.user_profile = self.load_or_create_profile()
        self.calendar = CalendarIntegration()
        self.engine = SchedulingEngine(self.user_profile, self.calendar)
        self.nlp_processor = NLPProcessor()
        self.notification_manager = NotificationManager(self.user_profile.email)

        # UI Components
        self.status_bar = None
        self.quick_schedule_tab = None
        self.calendar_view_tab = None
        self.settings_tab = None
        self.insights_tab = None
        self.notebook = None

        self.setup_ui()

        # Start background threads
        self.start_background_tasks()

    def setup_styles(self):
        """Setup modern UI styles with glassmorphism effect"""
        style = ttk.Style()

        # Apply ModernTheme configuration
        ModernTheme.configure_styles(style, self.root)

        logger.info("Modern UI theme configured with glassmorphism and neumorphism effects")

    def load_or_create_profile(self) -> UserProfile:
        """Load existing profile or create new one"""
        profile_file = self.config.get_path('user_profile', '.config/user_profile.json')

        if os.path.exists(profile_file):
            with open(profile_file, 'r') as f:
                data = json.load(f)
                return UserProfile.from_dict(data)
        else:
            # Create default profile
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
        """Save user profile to file"""
        profile_file = self.config.get_path('user_profile', '.config/user_profile.json')
        with open(profile_file, 'w') as f:
            json.dump(self.user_profile.to_dict(), f, indent=2, default=str)

    def setup_ui(self):
        """Setup the main UI components with i18n"""
        logger.info("Setting up UI...")

        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Tab 1: Quick Schedule (lazy import)
        logger.info("Loading Quick Schedule tab...")
        from ai_schedule_agent.ui.tabs.quick_schedule_tab import QuickScheduleTab
        quick_tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(quick_tab_frame, text=self.i18n.t('tab_quick_schedule'))
        self.quick_schedule_tab = QuickScheduleTab(
            quick_tab_frame,
            self.nlp_processor,
            self.engine,
            self.schedule_event,
            self.update_status
            # TODO: Pass i18n when tab is updated to support it
        )

        # Tab 2: Calendar View (lazy import)
        logger.info("Loading Calendar View tab...")
        from ai_schedule_agent.ui.tabs.calendar_view_tab import CalendarViewTab
        calendar_tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(calendar_tab_frame, text=self.i18n.t('tab_calendar_view'))
        self.calendar_view_tab = CalendarViewTab(
            calendar_tab_frame,
            self.calendar,
            self.engine.pattern_learner,
            self.update_status
            # TODO: Pass i18n when tab is updated to support it
        )

        # Tab 3: Settings (lazy import)
        logger.info("Loading Settings tab...")
        from ai_schedule_agent.ui.tabs.settings_tab import SettingsTab
        settings_tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(settings_tab_frame, text=self.i18n.t('tab_settings'))
        self.settings_tab = SettingsTab(
            settings_tab_frame,
            self.user_profile,
            self.save_profile
            # TODO: Pass i18n and language callback when tab is updated
        )

        # Tab 4: Insights - LAZY LOAD on first access to avoid numpy import delay
        # Create placeholder frame that loads content when clicked
        logger.info("Creating Insights tab placeholder...")
        self.insights_tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.insights_tab_frame, text=self.i18n.t('tab_insights'))
        self.insights_tab = None  # Will be loaded on first access
        self._insights_loaded = False

        # Add tab change handler to lazy load Insights
        self.notebook.bind('<<NotebookTabChanged>>', self._on_tab_changed)

        logger.info("UI setup complete (Insights tab will load on demand)")

        # Status bar with i18n
        self.status_bar = ttk.Label(self.root, text=self.i18n.t('ready'), relief=tk.SUNKEN, padding=[10, 5])
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def _on_tab_changed(self, event):
        """Handle tab change - lazy load Insights tab on first access"""
        selected_tab = self.notebook.index(self.notebook.select())

        # Check if user switched to Insights tab (index 3)
        if selected_tab == 3 and not self._insights_loaded:
            self._insights_loaded = True
            logger.info("Loading Insights tab for first time (loading numpy...)...")
            self.update_status(self.i18n.t('loading_analytics'))

            # Import and create InsightsTab
            from ai_schedule_agent.ui.tabs.insights_tab import InsightsTab
            self.insights_tab = InsightsTab(
                self.insights_tab_frame,
                self.engine,
                self.calendar,
                self.user_profile,
                self.notification_manager
                # TODO: Pass i18n when tab is updated to support it
            )

            logger.info("Insights tab loaded successfully")
            self.update_status(self.i18n.t('ready'))

    def on_language_changed(self, new_language: str):
        """Handle language change - requires UI restart

        Args:
            new_language: New language code
        """
        logger.info(f"Language changed to: {new_language}")

        # Show message to user
        messagebox.showinfo(
            self.i18n.t('success'),
            "Language will be updated on next restart.\n\n"
            "語言將在下次啟動時更新。"
        )

        # Update i18n
        self.i18n.set_language(new_language)

        # Note: Full UI refresh would require recreating all widgets
        # For now, language takes effect on next restart
        # TODO: Implement live language switching by recreating UI components

    def schedule_event(self, event: Event):
        """Actually schedule the event"""
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
                self.calendar_view_tab.refresh()

                # Show success message
                self.quick_schedule_tab.display_result(f"✅ Event '{event.title}' scheduled successfully!")
                self.update_status(f"Event scheduled: {event.title}")

                # Check for batch opportunities
                suggestions = self.engine.suggest_batch_opportunities()
                if suggestions:
                    self.quick_schedule_tab.display_result(f"💡 Suggestion: {suggestions[0]['message']}")

            else:
                messagebox.showerror("Error", "Failed to create event in Google Calendar")

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def update_status(self, message):
        """Update status bar"""
        self.status_bar.config(text=message)
        self.root.update_idletasks()

    def start_background_tasks(self):
        """Start background threads for notifications and monitoring"""

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
