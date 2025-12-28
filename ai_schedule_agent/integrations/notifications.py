"""Notification and reminder management"""

import queue
import smtplib
from datetime import timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from plyer import notification

from ai_schedule_agent.models.event import Event
from ai_schedule_agent.models.enums import Priority
from ai_schedule_agent.config.manager import ConfigManager
from ai_schedule_agent.utils.logging import logger


class NotificationManager:
    """Handle desktop and email notifications"""

    def __init__(self, user_email: str = None):
        self.user_email = user_email
        self.notification_queue = queue.Queue()
        self.config = ConfigManager()

        # Load SMTP settings from config
        self.smtp_server = self.config.get_setting('smtp', 'server')
        self.smtp_port = self.config.get_setting('smtp', 'port', default=587)
        self.smtp_username = self.config.get_setting('smtp', 'username')
        self.smtp_password = self.config.get_setting('smtp', 'password')

        # Load notification settings
        self.desktop_enabled = self.config.get_setting('notifications', 'desktop_enabled', default=True)
        self.email_enabled = self.config.get_setting('notifications', 'email_enabled', default=False)

    def setup_email(self, smtp_server: str, smtp_username: str, smtp_password: str):
        """Setup email configuration and save to config"""
        self.smtp_server = smtp_server
        self.smtp_username = smtp_username
        self.smtp_password = smtp_password

        # Update config
        self.config.update_setting(smtp_server, 'smtp', 'server')
        self.config.update_setting(smtp_username, 'smtp', 'username')
        self.config.update_setting(smtp_password, 'smtp', 'password')

    def send_desktop_notification(self, title: str, message: str):
        """Send desktop notification using plyer"""
        if not self.desktop_enabled:
            return

        try:
            notification.notify(
                title=title,
                message=message,
                app_icon=None,
                timeout=10,
            )
        except Exception as e:
            logger.error(f"Failed to send desktop notification: {e}")

    def send_email_notification(self, subject: str, body: str, recipient: str = None):
        """Send email notification via SMTP"""
        if not self.email_enabled:
            return False

        if not self.smtp_server or not self.smtp_username or not self.smtp_password:
            logger.warning("Email not configured")
            return False

        recipient = recipient or self.user_email
        if not recipient:
            logger.warning("No recipient email specified")
            return False

        try:
            msg = MIMEMultipart()
            msg['From'] = self.smtp_username
            msg['To'] = recipient
            msg['Subject'] = subject

            msg.attach(MIMEText(body, 'plain'))

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)

            return True
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False

    def schedule_reminder(self, event: Event, advance_notice_minutes: int = None):
        """Schedule a reminder for an event"""
        if not event.start_time:
            return

        # Get reminder times from config if not specified
        if advance_notice_minutes is None:
            if event.priority in [Priority.HIGH, Priority.CRITICAL]:
                advance_notice_minutes = self.config.get_setting('notifications', 'high_priority_reminder_minutes', default=30)
            else:
                advance_notice_minutes = self.config.get_setting('notifications', 'default_reminder_minutes', default=15)

        reminder_time = event.start_time - timedelta(minutes=advance_notice_minutes)

        # Calculate importance-based reminder frequency
        if event.priority == Priority.CRITICAL:
            reminder_intervals = [60, 30, 15, 5]  # Multiple reminders
        elif event.priority == Priority.HIGH:
            reminder_intervals = [30, 10]
        else:
            reminder_intervals = [advance_notice_minutes]

        for interval in reminder_intervals:
            self.notification_queue.put({
                'time': event.start_time - timedelta(minutes=interval),
                'event': event,
                'type': 'reminder'
            })
