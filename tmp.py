"""
AI Schedule Agent - Intelligent Personal Scheduling Assistant
A comprehensive scheduling agent that integrates with Google Calendar and learns from user patterns
"""

import os
import json
import pickle
import datetime
import re
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging
from collections import defaultdict, Counter

# Google Calendar API imports
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# UI and notification imports
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import queue
from plyer import notification  # For desktop notifications
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# NLP for natural language processing
import spacy
import dateparser
from datetime import timedelta

# Machine Learning for pattern recognition
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Google Calendar API scope
SCOPES = ['https://www.googleapis.com/auth/calendar']

# Event Types Enumeration
class EventType(Enum):
    DAILY = "daily"
    SHORT_TERM = "short_term"
    LONG_TERM = "long_term"
    FOCUS = "focus"
    MEETING = "meeting"
    PERSONAL = "personal"
    BREAK = "break"

class Priority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

# Data Models
@dataclass
class UserProfile:
    """User preferences and patterns"""
    working_hours: Dict[str, Tuple[str, str]] = field(default_factory=dict)  # day: (start, end)
    locations: List[str] = field(default_factory=list)
    energy_patterns: Dict[int, float] = field(default_factory=dict)  # hour: energy_level (0-1)
    preferred_meeting_length: int = 60  # minutes
    focus_time_length: int = 120  # minutes
    email: str = ""
    behavioral_rules: List[str] = field(default_factory=list)
    learned_patterns: Dict = field(default_factory=dict)
    
    def to_dict(self):
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data):
        return cls(**data)

@dataclass
class Event:
    """Event data model"""
    title: str
    description: str = ""
    start_time: datetime.datetime = None
    end_time: datetime.datetime = None
    event_type: EventType = EventType.MEETING
    priority: Priority = Priority.MEDIUM
    location: str = ""
    is_virtual: bool = False
    participants: List[str] = field(default_factory=list)
    required_resources: List[str] = field(default_factory=list)
    prep_time: int = 0  # minutes
    followup_time: int = 0  # minutes
    is_flexible: bool = True
    tags: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)  # event IDs
    google_event_id: str = ""
    recurrence_rule: str = ""  # RRULE for recurring events
    
    def to_google_event(self):
        """Convert to Google Calendar event format"""
        event = {
            'summary': self.title,
            'description': self.description,
            'start': {
                'dateTime': self.start_time.isoformat(),
                'timeZone': 'UTC',
            },
            'end': {
                'dateTime': self.end_time.isoformat(),
                'timeZone': 'UTC',
            },
            'location': self.location,
            'attendees': [{'email': p} for p in self.participants],
            'extendedProperties': {
                'private': {
                    'eventType': self.event_type.value,
                    'priority': str(self.priority.value),
                    'isFlexible': str(self.is_flexible),
                    'tags': ','.join(self.tags),
                    'prepTime': str(self.prep_time),
                    'followupTime': str(self.followup_time),
                }
            }
        }
        
        if self.recurrence_rule:
            event['recurrence'] = [self.recurrence_rule]
            
        return event

class PatternLearner:
    """Learn from user scheduling patterns"""
    
    def __init__(self):
        self.event_history = []
        self.scheduling_patterns = defaultdict(list)
        self.time_preferences = defaultdict(Counter)
        
    def add_event(self, event: Event):
        """Add event to learning history"""
        self.event_history.append(event)
        
        # Learn time preferences
        hour = event.start_time.hour
        self.time_preferences[event.event_type][hour] += 1
        
        # Learn scheduling patterns
        day_of_week = event.start_time.weekday()
        self.scheduling_patterns[day_of_week].append({
            'type': event.event_type,
            'hour': hour,
            'duration': (event.end_time - event.start_time).seconds // 60
        })
    
    def get_optimal_time(self, event_type: EventType, date: datetime.date) -> Optional[int]:
        """Get optimal hour for event type based on patterns"""
        if event_type in self.time_preferences:
            preferences = self.time_preferences[event_type]
            if preferences:
                return max(preferences, key=preferences.get)
        return None
    
    def suggest_batch_events(self) -> List[Tuple[EventType, List[int]]]:
        """Suggest events that could be batched together"""
        suggestions = []
        
        for event_type in EventType:
            hours = [e.start_time.hour for e in self.event_history 
                    if e.event_type == event_type]
            
            if len(hours) > 3:
                # Use clustering to find common time slots
                hours_array = np.array(hours).reshape(-1, 1)
                if len(set(hours)) > 1:
                    kmeans = KMeans(n_clusters=min(3, len(set(hours))), random_state=42)
                    kmeans.fit(hours_array)
                    
                    clusters = defaultdict(list)
                    for hour, label in zip(hours, kmeans.labels_):
                        clusters[label].append(hour)
                    
                    for cluster_hours in clusters.values():
                        if len(cluster_hours) > 2:
                            suggestions.append((event_type, cluster_hours))
        
        return suggestions

class CalendarIntegration:
    """Google Calendar integration handler"""
    
    def __init__(self):
        self.service = None
        self.credentials = None
        
    def authenticate(self):
        """Authenticate with Google Calendar"""
        creds = None
        
        # Token file stores the user's access and refresh tokens
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        
        # If there are no (valid) credentials available, let the user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save credentials for next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        
        self.credentials = creds
        self.service = build('calendar', 'v3', credentials=creds)
        
    def get_events(self, time_min=None, time_max=None):
        """Fetch events from Google Calendar"""
        if not self.service:
            self.authenticate()
            
        if not time_min:
            time_min = datetime.datetime.utcnow().isoformat() + 'Z'
        if not time_max:
            time_max = (datetime.datetime.utcnow() + timedelta(days=30)).isoformat() + 'Z'
        
        try:
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            return events_result.get('items', [])
        except HttpError as error:
            logger.error(f'An error occurred: {error}')
            return []
    
    def create_event(self, event: Event):
        """Create event in Google Calendar"""
        if not self.service:
            self.authenticate()
        
        try:
            google_event = event.to_google_event()
            created_event = self.service.events().insert(
                calendarId='primary',
                body=google_event
            ).execute()
            
            return created_event['id']
        except HttpError as error:
            logger.error(f'An error occurred: {error}')
            return None
    
    def update_event(self, event_id: str, event: Event):
        """Update existing event"""
        if not self.service:
            self.authenticate()
        
        try:
            google_event = event.to_google_event()
            updated_event = self.service.events().update(
                calendarId='primary',
                eventId=event_id,
                body=google_event
            ).execute()
            
            return updated_event['id']
        except HttpError as error:
            logger.error(f'An error occurred: {error}')
            return None
    
    def check_availability(self, start_time: datetime.datetime, 
                          end_time: datetime.datetime, 
                          attendees: List[str]) -> bool:
        """Check if all attendees are available"""
        if not self.service:
            self.authenticate()
        
        free_busy_query = {
            'timeMin': start_time.isoformat(),
            'timeMax': end_time.isoformat(),
            'items': [{'id': email} for email in attendees]
        }
        
        try:
            free_busy_result = self.service.freebusy().query(
                body=free_busy_query
            ).execute()
            
            for email, calendar in free_busy_result['calendars'].items():
                if calendar.get('busy'):
                    return False
            
            return True
        except HttpError as error:
            logger.error(f'An error occurred: {error}')
            return True  # Assume available if check fails

class NLPProcessor:
    """Natural Language Processing for scheduling requests"""
    
    def __init__(self):
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except:
            # If spacy model not installed, use basic parsing
            self.nlp = None
            logger.warning("Spacy model not found. Using basic NLP parsing.")
    
    def parse_scheduling_request(self, text: str) -> Dict:
        """Parse natural language scheduling request"""
        result = {
            'action': None,
            'event_type': None,
            'participants': [],
            'datetime': None,
            'duration': None,
            'location': None,
            'title': None
        }
        
        # Extract datetime
        parsed_date = dateparser.parse(text, settings={'PREFER_DATES_FROM': 'future'})
        if parsed_date:
            result['datetime'] = parsed_date
        
        # Basic keyword extraction
        text_lower = text.lower()
        
        # Determine action
        if any(word in text_lower for word in ['schedule', 'book', 'arrange', 'set up']):
            result['action'] = 'create'
        elif any(word in text_lower for word in ['reschedule', 'move', 'change']):
            result['action'] = 'reschedule'
        elif any(word in text_lower for word in ['cancel', 'delete', 'remove']):
            result['action'] = 'cancel'
        
        # Determine event type
        if 'meeting' in text_lower:
            result['event_type'] = EventType.MEETING
        elif 'focus' in text_lower or 'deep work' in text_lower:
            result['event_type'] = EventType.FOCUS
        elif 'break' in text_lower:
            result['event_type'] = EventType.BREAK
        
        # Extract participants (email patterns)
        import re
        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
        result['participants'] = emails
        
        # Extract duration
        duration_patterns = [
            (r'(\d+)\s*hour', lambda x: int(x) * 60),
            (r'(\d+)\s*minute', lambda x: int(x)),
            (r'(\d+)\s*min', lambda x: int(x))
        ]
        
        for pattern, converter in duration_patterns:
            match = re.search(pattern, text_lower)
            if match:
                result['duration'] = converter(match.group(1))
                break
        
        # Extract title (simplified - take the quoted text or main noun phrase)
        quoted = re.findall(r'"([^"]*)"', text)
        if quoted:
            result['title'] = quoted[0]
        
        return result

class SchedulingEngine:
    """Core scheduling engine with optimization"""
    
    def __init__(self, user_profile: UserProfile, calendar: CalendarIntegration):
        self.user_profile = user_profile
        self.calendar = calendar
        self.pattern_learner = PatternLearner()
        self.pending_events = []
        
    def find_optimal_slot(self, event: Event, 
                         search_start: datetime.datetime = None,
                         search_days: int = 14) -> Optional[Tuple[datetime.datetime, datetime.datetime]]:
        """Find optimal time slot for an event"""
        
        if not search_start:
            search_start = datetime.datetime.now()
        
        # Get existing events
        search_end = search_start + timedelta(days=search_days)
        existing_events = self.calendar.get_events(
            search_start.isoformat() + 'Z',
            search_end.isoformat() + 'Z'
        )
        
        # Convert to busy slots
        busy_slots = []
        for e in existing_events:
            if 'dateTime' in e.get('start', {}):
                start = datetime.datetime.fromisoformat(e['start']['dateTime'].replace('Z', '+00:00'))
                end = datetime.datetime.fromisoformat(e['end']['dateTime'].replace('Z', '+00:00'))
                busy_slots.append((start, end))
        
        # Calculate event duration including prep and followup
        total_duration = ((event.end_time - event.start_time).seconds // 60 if event.end_time and event.start_time 
                         else self.user_profile.preferred_meeting_length)
        total_duration += event.prep_time + event.followup_time
        
        # Find available slots
        candidates = []
        current_date = search_start.date()
        
        for day_offset in range(search_days):
            check_date = current_date + timedelta(days=day_offset)
            day_name = check_date.strftime('%A')
            
            # Get working hours for this day
            if day_name in self.user_profile.working_hours:
                start_hour, end_hour = self.user_profile.working_hours[day_name]
                start_time = datetime.datetime.combine(check_date, 
                                                       datetime.datetime.strptime(start_hour, '%H:%M').time())
                end_time = datetime.datetime.combine(check_date,
                                                     datetime.datetime.strptime(end_hour, '%H:%M').time())
                
                # Check each hour slot
                current_slot = start_time
                while current_slot + timedelta(minutes=total_duration) <= end_time:
                    slot_end = current_slot + timedelta(minutes=total_duration)
                    
                    # Check if slot is free
                    is_free = True
                    for busy_start, busy_end in busy_slots:
                        if not (slot_end <= busy_start or current_slot >= busy_end):
                            is_free = False
                            break
                    
                    if is_free:
                        # Calculate slot score based on energy patterns and preferences
                        score = self._calculate_slot_score(current_slot, event.event_type)
                        candidates.append((current_slot, slot_end, score))
                    
                    current_slot += timedelta(minutes=30)  # Check every 30 minutes
        
        # Return best candidate
        if candidates:
            candidates.sort(key=lambda x: x[2], reverse=True)
            return (candidates[0][0], candidates[0][1])
        
        return None
    
    def _calculate_slot_score(self, slot_time: datetime.datetime, event_type: EventType) -> float:
        """Calculate score for a time slot based on user preferences"""
        score = 0.5  # Base score
        
        hour = slot_time.hour
        
        # Energy pattern score
        if hour in self.user_profile.energy_patterns:
            energy_level = self.user_profile.energy_patterns[hour]
            
            # High energy for demanding tasks
            if event_type in [EventType.FOCUS, EventType.LONG_TERM]:
                score += energy_level * 0.3
            # Lower energy acceptable for routine tasks
            elif event_type in [EventType.DAILY, EventType.SHORT_TERM]:
                score += (1 - abs(energy_level - 0.5)) * 0.3
        
        # Historical preference score
        optimal_hour = self.pattern_learner.get_optimal_time(event_type, slot_time.date())
        if optimal_hour:
            hour_diff = abs(hour - optimal_hour)
            score += max(0, 1 - (hour_diff / 12)) * 0.2
        
        return score
    
    def check_conflicts(self, event: Event) -> List[Dict]:
        """Check for scheduling conflicts"""
        conflicts = []
        
        if not event.start_time or not event.end_time:
            return conflicts
        
        # Get events in the same timeframe
        existing_events = self.calendar.get_events(
            (event.start_time - timedelta(hours=1)).isoformat() + 'Z',
            (event.end_time + timedelta(hours=1)).isoformat() + 'Z'
        )
        
        for e in existing_events:
            if 'dateTime' in e.get('start', {}):
                start = datetime.datetime.fromisoformat(e['start']['dateTime'].replace('Z', '+00:00'))
                end = datetime.datetime.fromisoformat(e['end']['dateTime'].replace('Z', '+00:00'))
                
                # Check overlap
                if not (event.end_time <= start or event.start_time >= end):
                    conflicts.append({
                        'event': e,
                        'type': 'time_overlap',
                        'severity': 'high'
                    })
        
        return conflicts
    
    def suggest_batch_opportunities(self) -> List[Dict]:
        """Suggest opportunities to batch similar tasks"""
        suggestions = []
        
        batch_candidates = self.pattern_learner.suggest_batch_events()
        
        for event_type, common_hours in batch_candidates:
            avg_hour = int(np.mean(common_hours))
            suggestions.append({
                'type': 'batch_suggestion',
                'event_type': event_type,
                'suggested_time': avg_hour,
                'frequency': len(common_hours),
                'message': f"You often schedule {event_type.value} tasks around {avg_hour}:00. "
                          f"Would you like to make this a routine?"
            })
        
        return suggestions

class NotificationManager:
    """Handle notifications and reminders"""
    
    def __init__(self, user_email: str = None):
        self.user_email = user_email
        self.notification_queue = queue.Queue()
        self.smtp_server = None
        self.smtp_port = 587
        self.smtp_username = None
        self.smtp_password = None
        
    def setup_email(self, smtp_server: str, smtp_username: str, smtp_password: str):
        """Setup email configuration"""
        self.smtp_server = smtp_server
        self.smtp_username = smtp_username
        self.smtp_password = smtp_password
    
    def send_desktop_notification(self, title: str, message: str):
        """Send desktop notification"""
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
        """Send email notification"""
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
    
    def schedule_reminder(self, event: Event, advance_notice_minutes: int):
        """Schedule a reminder for an event"""
        if not event.start_time:
            return
        
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

class SchedulerUI:
    """Main UI for the scheduling agent"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("AI Schedule Agent")
        self.root.geometry("1200x800")
        
        # Initialize components
        self.user_profile = self.load_or_create_profile()
        self.calendar = CalendarIntegration()
        self.engine = SchedulingEngine(self.user_profile, self.calendar)
        self.nlp_processor = NLPProcessor()
        self.notification_manager = NotificationManager(self.user_profile.email)
        
        # UI Components
        self.setup_ui()
        
        # Start background threads
        self.start_background_tasks()
    
    def load_or_create_profile(self) -> UserProfile:
        """Load existing profile or create new one"""
        profile_file = 'user_profile.json'
        
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
        with open('user_profile.json', 'w') as f:
            json.dump(self.user_profile.to_dict(), f, indent=2, default=str)
    
    def setup_ui(self):
        """Setup the main UI components"""
        
        # Create notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Tab 1: Quick Schedule
        self.quick_tab = ttk.Frame(notebook)
        notebook.add(self.quick_tab, text='Quick Schedule')
        self.setup_quick_schedule_tab()
        
        # Tab 2: Calendar View
        self.calendar_tab = ttk.Frame(notebook)
        notebook.add(self.calendar_tab, text='Calendar View')
        self.setup_calendar_view_tab()
        
        # Tab 3: Settings
        self.settings_tab = ttk.Frame(notebook)
        notebook.add(self.settings_tab, text='Settings')
        self.setup_settings_tab()
        
        # Tab 4: Insights
        self.insights_tab = ttk.Frame(notebook)
        notebook.add(self.insights_tab, text='Insights')
        self.setup_insights_tab()
        
        # Status bar
        self.status_bar = ttk.Label(self.root, text="Ready", relief=tk.SUNKEN)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def setup_quick_schedule_tab(self):
        """Setup quick schedule tab"""
        
        # Natural language input
        ttk.Label(self.quick_tab, text="Natural Language Input:", font=('Arial', 12)).pack(pady=10)
        
        self.nl_input = ttk.Entry(self.quick_tab, width=80, font=('Arial', 11))
        self.nl_input.pack(pady=5)
        self.nl_input.bind('<Return>', lambda e: self.process_nl_input())
        
        ttk.Button(self.quick_tab, text="Process", command=self.process_nl_input).pack(pady=5)
        
        # Separator
        ttk.Separator(self.quick_tab, orient='horizontal').pack(fill='x', pady=20)
        
        # Detailed form
        ttk.Label(self.quick_tab, text="Detailed Event Form:", font=('Arial', 12)).pack(pady=10)
        
        form_frame = ttk.Frame(self.quick_tab)
        form_frame.pack(pady=10)
        
        # Event details
        fields = [
            ("Title:", "title"),
            ("Description:", "description"),
            ("Location:", "location"),
            ("Participants (comma-separated):", "participants"),
            ("Date (YYYY-MM-DD):", "date"),
            ("Start Time (HH:MM):", "start_time"),
            ("Duration (minutes):", "duration"),
            ("Prep Time (minutes):", "prep_time"),
            ("Follow-up Time (minutes):", "followup_time")
        ]
        
        self.form_entries = {}
        for i, (label, field) in enumerate(fields):
            ttk.Label(form_frame, text=label).grid(row=i, column=0, sticky='e', padx=5, pady=3)
            entry = ttk.Entry(form_frame, width=40)
            entry.grid(row=i, column=1, padx=5, pady=3)
            self.form_entries[field] = entry
        
        # Event type dropdown
        ttk.Label(form_frame, text="Event Type:").grid(row=len(fields), column=0, sticky='e', padx=5, pady=3)
        self.event_type_var = tk.StringVar(value=EventType.MEETING.value)
        event_type_dropdown = ttk.Combobox(form_frame, textvariable=self.event_type_var, 
                                          values=[e.value for e in EventType], state='readonly')
        event_type_dropdown.grid(row=len(fields), column=1, padx=5, pady=3, sticky='w')
        
        # Priority dropdown
        ttk.Label(form_frame, text="Priority:").grid(row=len(fields)+1, column=0, sticky='e', padx=5, pady=3)
        self.priority_var = tk.StringVar(value="MEDIUM")
        priority_dropdown = ttk.Combobox(form_frame, textvariable=self.priority_var,
                                        values=[p.name for p in Priority], state='readonly')
        priority_dropdown.grid(row=len(fields)+1, column=1, padx=5, pady=3, sticky='w')
        
        # Flexible checkbox
        self.is_flexible_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(form_frame, text="Flexible timing", 
                       variable=self.is_flexible_var).grid(row=len(fields)+2, column=1, sticky='w', pady=3)
        
        # Tags entry
        ttk.Label(form_frame, text="Tags (comma-separated):").grid(row=len(fields)+3, column=0, sticky='e', padx=5, pady=3)
        self.tags_entry = ttk.Entry(form_frame, width=40)
        self.tags_entry.grid(row=len(fields)+3, column=1, padx=5, pady=3)
        
        # Submit button
        ttk.Button(form_frame, text="Schedule Event", 
                  command=self.schedule_event_from_form).grid(row=len(fields)+4, column=0, columnspan=2, pady=20)
        
        # Result display
        self.result_text = scrolledtext.ScrolledText(self.quick_tab, height=8, width=80)
        self.result_text.pack(pady=10)
    
    def setup_calendar_view_tab(self):
        """Setup calendar view tab"""
        
        # Controls frame
        controls_frame = ttk.Frame(self.calendar_tab)
        controls_frame.pack(pady=10)
        
        ttk.Label(controls_frame, text="View Range:").grid(row=0, column=0, padx=5)
        
        self.view_range_var = tk.StringVar(value="Week")
        view_range = ttk.Combobox(controls_frame, textvariable=self.view_range_var,
                                  values=["Day", "Week", "Month"], state='readonly', width=10)
        view_range.grid(row=0, column=1, padx=5)
        
        ttk.Button(controls_frame, text="Refresh", command=self.refresh_calendar_view).grid(row=0, column=2, padx=10)
        ttk.Button(controls_frame, text="Sync with Google", command=self.sync_google_calendar).grid(row=0, column=3, padx=5)
        
        # Calendar display
        self.calendar_display = scrolledtext.ScrolledText(self.calendar_tab, height=25, width=100)
        self.calendar_display.pack(pady=10, padx=10, fill='both', expand=True)
        
        # Initial load
        self.refresh_calendar_view()
    
    def setup_settings_tab(self):
        """Setup settings tab"""
        
        # Working Hours Section
        ttk.Label(self.settings_tab, text="Working Hours", font=('Arial', 14, 'bold')).pack(pady=10)
        
        hours_frame = ttk.Frame(self.settings_tab)
        hours_frame.pack(pady=10)
        
        self.working_hours_entries = {}
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        for i, day in enumerate(days):
            ttk.Label(hours_frame, text=f"{day}:").grid(row=i, column=0, sticky='e', padx=5, pady=3)
            
            start_entry = ttk.Entry(hours_frame, width=8)
            start_entry.grid(row=i, column=1, padx=2, pady=3)
            
            ttk.Label(hours_frame, text="to").grid(row=i, column=2, padx=2, pady=3)
            
            end_entry = ttk.Entry(hours_frame, width=8)
            end_entry.grid(row=i, column=3, padx=2, pady=3)
            
            # Load existing values
            if day in self.user_profile.working_hours:
                start, end = self.user_profile.working_hours[day]
                start_entry.insert(0, start)
                end_entry.insert(0, end)
            
            self.working_hours_entries[day] = (start_entry, end_entry)
        
        # Energy Patterns Section
        ttk.Separator(self.settings_tab, orient='horizontal').pack(fill='x', pady=20)
        ttk.Label(self.settings_tab, text="Energy Patterns (0-10 scale)", font=('Arial', 14, 'bold')).pack(pady=10)
        
        energy_frame = ttk.Frame(self.settings_tab)
        energy_frame.pack(pady=10)
        
        self.energy_sliders = {}
        for i in range(6, 22):  # 6 AM to 9 PM
            ttk.Label(energy_frame, text=f"{i:02d}:00").grid(row=i-6, column=0, sticky='e', padx=5)
            
            slider = ttk.Scale(energy_frame, from_=0, to=10, orient='horizontal', length=200)
            slider.grid(row=i-6, column=1, padx=5, pady=2)
            
            # Load existing value
            if i in self.user_profile.energy_patterns:
                slider.set(self.user_profile.energy_patterns[i] * 10)
            
            self.energy_sliders[i] = slider
        
        # Behavioral Rules Section
        ttk.Separator(self.settings_tab, orient='horizontal').pack(fill='x', pady=20)
        ttk.Label(self.settings_tab, text="Behavioral Rules", font=('Arial', 14, 'bold')).pack(pady=10)
        
        rules_frame = ttk.Frame(self.settings_tab)
        rules_frame.pack(pady=10)
        
        ttk.Label(rules_frame, text="Add rules (e.g., 'No meetings before 10 AM'):").pack()
        
        self.rules_text = scrolledtext.ScrolledText(rules_frame, height=5, width=60)
        self.rules_text.pack(pady=5)
        
        # Load existing rules
        for rule in self.user_profile.behavioral_rules:
            self.rules_text.insert(tk.END, rule + "\n")
        
        # Email Settings
        ttk.Separator(self.settings_tab, orient='horizontal').pack(fill='x', pady=20)
        ttk.Label(self.settings_tab, text="Email Settings", font=('Arial', 14, 'bold')).pack(pady=10)
        
        email_frame = ttk.Frame(self.settings_tab)
        email_frame.pack(pady=10)
        
        ttk.Label(email_frame, text="Your Email:").grid(row=0, column=0, sticky='e', padx=5, pady=3)
        self.email_entry = ttk.Entry(email_frame, width=30)
        self.email_entry.grid(row=0, column=1, padx=5, pady=3)
        self.email_entry.insert(0, self.user_profile.email)
        
        # Save button
        ttk.Button(self.settings_tab, text="Save Settings", 
                  command=self.save_settings, style='Accent.TButton').pack(pady=20)
    
    def setup_insights_tab(self):
        """Setup insights tab"""
        
        # Controls
        controls_frame = ttk.Frame(self.insights_tab)
        controls_frame.pack(pady=10)
        
        ttk.Button(controls_frame, text="Analyze Patterns", 
                  command=self.analyze_patterns).pack(side='left', padx=5)
        ttk.Button(controls_frame, text="Get Suggestions", 
                  command=self.get_scheduling_suggestions).pack(side='left', padx=5)
        ttk.Button(controls_frame, text="Check Work-Life Balance", 
                  command=self.check_work_life_balance).pack(side='left', padx=5)
        
        # Insights display
        self.insights_display = scrolledtext.ScrolledText(self.insights_tab, height=25, width=90)
        self.insights_display.pack(pady=10, padx=10, fill='both', expand=True)
    
    def process_nl_input(self):
        """Process natural language input"""
        text = self.nl_input.get()
        if not text:
            return
        
        self.update_status("Processing natural language input...")
        
        # Parse the input
        parsed = self.nlp_processor.parse_scheduling_request(text)
        
        # Display parsed information
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, "Parsed Information:\n")
        self.result_text.insert(tk.END, "-" * 50 + "\n")
        
        for key, value in parsed.items():
            if value:
                self.result_text.insert(tk.END, f"{key.title()}: {value}\n")
        
        # Create event based on parsed info
        if parsed['action'] == 'create':
            event = Event(
                title=parsed.get('title', 'New Event'),
                event_type=parsed.get('event_type', EventType.MEETING),
                participants=parsed.get('participants', []),
                location=parsed.get('location', '')
            )
            
            # Find optimal time if not specified
            if parsed['datetime']:
                event.start_time = parsed['datetime']
                duration = parsed.get('duration', self.user_profile.preferred_meeting_length)
                event.end_time = event.start_time + timedelta(minutes=duration)
            else:
                optimal_slot = self.engine.find_optimal_slot(event)
                if optimal_slot:
                    event.start_time, event.end_time = optimal_slot
            
            # Check for conflicts
            conflicts = self.engine.check_conflicts(event)
            
            if conflicts:
                self.result_text.insert(tk.END, "\n⚠️ Conflicts detected:\n")
                for conflict in conflicts:
                    self.result_text.insert(tk.END, f"  - {conflict['event']['summary']}\n")
                
                # Ask for confirmation
                if messagebox.askyesno("Conflicts Detected", 
                                       "There are conflicts. Do you want to schedule anyway?"):
                    self.schedule_event(event)
            else:
                # Ask for confirmation
                self.result_text.insert(tk.END, f"\n✅ Proposed Time: {event.start_time} - {event.end_time}\n")
                if messagebox.askyesno("Confirm Scheduling", 
                                       f"Schedule '{event.title}' at {event.start_time}?"):
                    self.schedule_event(event)
        
        self.update_status("Ready")
    
    def schedule_event_from_form(self):
        """Schedule event from detailed form"""
        try:
            # Collect form data
            title = self.form_entries['title'].get()
            if not title:
                messagebox.showerror("Error", "Title is required")
                return
            
            # Parse date and time
            date_str = self.form_entries['date'].get()
            time_str = self.form_entries['start_time'].get()
            
            if date_str and time_str:
                start_time = datetime.datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
            else:
                start_time = None
            
            duration = int(self.form_entries['duration'].get() or self.user_profile.preferred_meeting_length)
            
            # Create event
            event = Event(
                title=title,
                description=self.form_entries['description'].get(),
                location=self.form_entries['location'].get(),
                event_type=EventType(self.event_type_var.get()),
                priority=Priority[self.priority_var.get()],
                is_flexible=self.is_flexible_var.get(),
                prep_time=int(self.form_entries['prep_time'].get() or 0),
                followup_time=int(self.form_entries['followup_time'].get() or 0),
                tags=self.tags_entry.get().split(',') if self.tags_entry.get() else []
            )
            
            # Parse participants
            participants_str = self.form_entries['participants'].get()
            if participants_str:
                event.participants = [p.strip() for p in participants_str.split(',')]
            
            # Set time or find optimal slot
            if start_time:
                event.start_time = start_time
                event.end_time = start_time + timedelta(minutes=duration)
                
                # Check for conflicts
                conflicts = self.engine.check_conflicts(event)
                if conflicts:
                    if not messagebox.askyesno("Conflicts Detected", 
                                              "There are scheduling conflicts. Continue anyway?"):
                        return
            else:
                # Find optimal slot
                optimal_slot = self.engine.find_optimal_slot(event)
                if optimal_slot:
                    event.start_time, event.end_time = optimal_slot
                    
                    if not messagebox.askyesno("Time Suggestion", 
                                              f"Suggested time: {event.start_time}. Accept?"):
                        return
                else:
                    messagebox.showerror("Error", "No available time slot found")
                    return
            
            # Check dependencies
            if event.dependencies:
                self.notification_manager.send_desktop_notification(
                    "Dependency Reminder",
                    f"This event depends on: {', '.join(event.dependencies)}"
                )
            
            # Schedule the event
            self.schedule_event(event)
            
            # Clear form
            for entry in self.form_entries.values():
                entry.delete(0, tk.END)
            self.tags_entry.delete(0, tk.END)
            
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
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
                self.refresh_calendar_view()
                
                # Show success message
                self.result_text.insert(tk.END, f"\n✅ Event '{event.title}' scheduled successfully!\n")
                self.update_status(f"Event scheduled: {event.title}")
                
                # Check for batch opportunities
                suggestions = self.engine.suggest_batch_opportunities()
                if suggestions:
                    self.result_text.insert(tk.END, "\n💡 Suggestion: ")
                    self.result_text.insert(tk.END, suggestions[0]['message'] + "\n")
                
            else:
                messagebox.showerror("Error", "Failed to create event in Google Calendar")
                
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def refresh_calendar_view(self):
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
            logger.error(f"Calendar refresh error: {e}")
    
    def sync_google_calendar(self):
        """Sync with Google Calendar"""
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
                    self.engine.pattern_learner.add_event(event)
            
            self.refresh_calendar_view()
            self.update_status("Sync completed successfully")
            messagebox.showinfo("Success", "Calendar synced successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to sync: {str(e)}")
            self.update_status("Sync failed")
    
    def save_settings(self):
        """Save user settings"""
        try:
            # Save working hours
            for day, (start_entry, end_entry) in self.working_hours_entries.items():
                start = start_entry.get()
                end = end_entry.get()
                if start and end:
                    self.user_profile.working_hours[day] = (start, end)
            
            # Save energy patterns
            for hour, slider in self.energy_sliders.items():
                self.user_profile.energy_patterns[hour] = slider.get() / 10.0
            
            # Save behavioral rules
            rules_text = self.rules_text.get(1.0, tk.END).strip()
            if rules_text:
                self.user_profile.behavioral_rules = rules_text.split('\n')
            
            # Save email
            self.user_profile.email = self.email_entry.get()
            
            # Save to file
            self.save_profile()
            
            messagebox.showinfo("Success", "Settings saved successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {str(e)}")
    
    def analyze_patterns(self):
        """Analyze scheduling patterns"""
        self.insights_display.delete(1.0, tk.END)
        self.insights_display.insert(tk.END, "📊 SCHEDULING PATTERNS ANALYSIS\n")
        self.insights_display.insert(tk.END, "="*50 + "\n\n")
        
        # Analyze time preferences
        self.insights_display.insert(tk.END, "⏰ Time Preferences by Event Type:\n")
        self.insights_display.insert(tk.END, "-"*30 + "\n")
        
        for event_type, hours in self.engine.pattern_learner.time_preferences.items():
            if hours:
                most_common = hours.most_common(3)
                self.insights_display.insert(tk.END, f"\n{event_type.value}:\n")
                for hour, count in most_common:
                    self.insights_display.insert(tk.END, f"  • {hour:02d}:00 - {count} times\n")
        
        # Analyze weekly patterns
        self.insights_display.insert(tk.END, "\n\n📅 Weekly Patterns:\n")
        self.insights_display.insert(tk.END, "-"*30 + "\n")
        
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        for day_idx, patterns in self.engine.pattern_learner.scheduling_patterns.items():
            if patterns and day_idx < len(days):
                self.insights_display.insert(tk.END, f"\n{days[day_idx]}:\n")
                
                # Count event types
                type_counts = Counter(p['type'] for p in patterns)
                for event_type, count in type_counts.most_common():
                    self.insights_display.insert(tk.END, f"  • {event_type.value}: {count} events\n")
        
        # Suggest optimizations
        self.insights_display.insert(tk.END, "\n\n💡 Optimization Suggestions:\n")
        self.insights_display.insert(tk.END, "-"*30 + "\n")
        
        batch_suggestions = self.engine.suggest_batch_opportunities()
        if batch_suggestions:
            for suggestion in batch_suggestions[:3]:
                self.insights_display.insert(tk.END, f"• {suggestion['message']}\n")
        else:
            self.insights_display.insert(tk.END, "• No batch optimization opportunities found yet.\n")
    
    def get_scheduling_suggestions(self):
        """Get AI scheduling suggestions"""
        self.insights_display.delete(1.0, tk.END)
        self.insights_display.insert(tk.END, "🤖 AI SCHEDULING SUGGESTIONS\n")
        self.insights_display.insert(tk.END, "="*50 + "\n\n")
        
        # Check for upcoming gaps that could be utilized
        self.insights_display.insert(tk.END, "📌 Available Time Slots (Next 7 Days):\n")
        self.insights_display.insert(tk.END, "-"*30 + "\n")
        
        # Find gaps in schedule
        events = self.calendar.get_events(
            datetime.datetime.now().isoformat() + 'Z',
            (datetime.datetime.now() + timedelta(days=7)).isoformat() + 'Z'
        )
        
        # Convert to busy periods
        busy_periods = []
        for event in events:
            if 'dateTime' in event.get('start', {}):
                start = datetime.datetime.fromisoformat(event['start']['dateTime'].replace('Z', '+00:00'))
                end = datetime.datetime.fromisoformat(event['end']['dateTime'].replace('Z', '+00:00'))
                busy_periods.append((start, end))
        
        busy_periods.sort()
        
        # Find gaps
        gaps = []
        for i in range(len(busy_periods) - 1):
            gap_start = busy_periods[i][1]
            gap_end = busy_periods[i + 1][0]
            gap_duration = (gap_end - gap_start).seconds // 60
            
            if gap_duration >= 30:  # At least 30 minutes
                gaps.append((gap_start, gap_end, gap_duration))
        
        # Display top gaps
        for gap_start, gap_end, duration in gaps[:5]:
            self.insights_display.insert(tk.END, 
                f"• {gap_start.strftime('%a %b %d, %H:%M')} - {gap_end.strftime('%H:%M')} "
                f"({duration} minutes)\n")
        
        if not gaps:
            self.insights_display.insert(tk.END, "• No significant gaps found\n")
        
        # Energy-based suggestions
        self.insights_display.insert(tk.END, "\n\n⚡ Energy-Based Recommendations:\n")
        self.insights_display.insert(tk.END, "-"*30 + "\n")
        
        # Find peak energy hours
        peak_hours = sorted(self.user_profile.energy_patterns.items(), 
                          key=lambda x: x[1], reverse=True)[:3]
        
        self.insights_display.insert(tk.END, "Peak energy hours for demanding tasks:\n")
        for hour, energy in peak_hours:
            self.insights_display.insert(tk.END, f"• {hour:02d}:00 (Energy: {energy*10:.1f}/10)\n")
        
        # Context switching suggestions
        self.insights_display.insert(tk.END, "\n\n🔄 Context Switching Optimization:\n")
        self.insights_display.insert(tk.END, "-"*30 + "\n")
        
        # Analyze recent events for context switching
        context_switches = 0
        last_type = None
        
        for event in events:
            props = event.get('extendedProperties', {}).get('private', {})
            event_type = props.get('eventType')
            
            if last_type and event_type and last_type != event_type:
                context_switches += 1
            last_type = event_type
        
        if context_switches > 5:
            self.insights_display.insert(tk.END, 
                f"⚠️ High context switching detected ({context_switches} switches this week)\n")
            self.insights_display.insert(tk.END, 
                "Consider batching similar tasks together to improve focus.\n")
        else:
            self.insights_display.insert(tk.END, 
                "✅ Context switching is well managed.\n")
    
    def check_work_life_balance(self):
        """Check work-life balance"""
        self.insights_display.delete(1.0, tk.END)
        self.insights_display.insert(tk.END, "⚖️ WORK-LIFE BALANCE ANALYSIS\n")
        self.insights_display.insert(tk.END, "="*50 + "\n\n")
        
        # Calculate work hours this week
        events = self.calendar.get_events(
            (datetime.datetime.now() - timedelta(days=7)).isoformat() + 'Z',
            datetime.datetime.now().isoformat() + 'Z'
        )
        
        total_work_hours = 0
        total_personal_hours = 0
        events_by_type = defaultdict(int)
        
        for event in events:
            if 'dateTime' in event.get('start', {}):
                start = datetime.datetime.fromisoformat(event['start']['dateTime'].replace('Z', '+00:00'))
                end = datetime.datetime.fromisoformat(event['end']['dateTime'].replace('Z', '+00:00'))
                duration_hours = (end - start).seconds / 3600
                
                props = event.get('extendedProperties', {}).get('private', {})
                event_type = props.get('eventType', 'meeting')
                
                if event_type in ['meeting', 'focus', 'long_term']:
                    total_work_hours += duration_hours
                elif event_type in ['personal', 'break']:
                    total_personal_hours += duration_hours
                
                events_by_type[event_type] += duration_hours
        
        # Display statistics
        self.insights_display.insert(tk.END, "📊 Past Week Statistics:\n")
        self.insights_display.insert(tk.END, "-"*30 + "\n")
        self.insights_display.insert(tk.END, f"Work Hours: {total_work_hours:.1f} hours\n")
        self.insights_display.insert(tk.END, f"Personal Time: {total_personal_hours:.1f} hours\n")
        
        if total_work_hours > 0:
            balance_ratio = total_personal_hours / total_work_hours
            self.insights_display.insert(tk.END, f"Balance Ratio: {balance_ratio:.2f}\n\n")
            
            if balance_ratio < 0.2:
                self.insights_display.insert(tk.END, "⚠️ Warning: Very low personal time!\n")
                self.insights_display.insert(tk.END, "Consider scheduling more breaks and personal activities.\n")
            elif balance_ratio < 0.4:
                self.insights_display.insert(tk.END, "⚡ Moderate balance - could use more personal time.\n")
            else:
                self.insights_display.insert(tk.END, "✅ Good work-life balance!\n")
        
        # Time breakdown by category
        self.insights_display.insert(tk.END, "\n📈 Time Distribution:\n")
        self.insights_display.insert(tk.END, "-"*30 + "\n")
        
        for event_type, hours in sorted(events_by_type.items(), key=lambda x: x[1], reverse=True):
            percentage = (hours / sum(events_by_type.values())) * 100 if events_by_type else 0
            self.insights_display.insert(tk.END, f"{event_type}: {hours:.1f}h ({percentage:.1f}%)\n")
        
        # Recommendations
        self.insights_display.insert(tk.END, "\n💡 Recommendations:\n")
        self.insights_display.insert(tk.END, "-"*30 + "\n")
        
        if total_work_hours > 40:
            self.insights_display.insert(tk.END, "• Consider reducing meeting frequency\n")
            self.insights_display.insert(tk.END, "• Block out focus time for deep work\n")
        
        if total_personal_hours < 10:
            self.insights_display.insert(tk.END, "• Schedule regular breaks throughout the day\n")
            self.insights_display.insert(tk.END, "• Add personal activities to your calendar\n")
            self.insights_display.insert(tk.END, "• Consider setting 'no meeting' hours\n")
        
        # Send reminder notification
        self.notification_manager.send_desktop_notification(
            "Work-Life Balance Check",
            f"Work: {total_work_hours:.1f}h | Personal: {total_personal_hours:.1f}h this week"
        )
    
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


class SetupWizard:
    """Initial setup wizard for first-time users"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("AI Schedule Agent - Setup Wizard")
        self.root.geometry("600x700")
        
        self.user_profile = UserProfile()
        self.current_step = 0
        self.setup_steps()
    
    def setup_steps(self):
        """Setup wizard steps"""
        
        # Title
        title = ttk.Label(self.root, text="Welcome to AI Schedule Agent!", 
                         font=('Arial', 18, 'bold'))
        title.pack(pady=20)
        
        # Subtitle
        subtitle = ttk.Label(self.root, 
                           text="Let's set up your scheduling preferences",
                           font=('Arial', 12))
        subtitle.pack(pady=5)
        
        # Create notebook for steps
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Step 1: Basic Info
        self.step1_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.step1_frame, text="Basic Information")
        self.setup_step1()
        
        # Step 2: Working Hours
        self.step2_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.step2_frame, text="Working Hours")
        self.setup_step2()
        
        # Step 3: Energy Patterns
        self.step3_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.step3_frame, text="Energy Patterns")
        self.setup_step3()
        
        # Step 4: Preferences
        self.step4_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.step4_frame, text="Preferences")
        self.setup_step4()
        
        # Step 5: Google Calendar
        self.step5_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.step5_frame, text="Google Calendar")
        self.setup_step5()
        
        # Navigation buttons
        nav_frame = ttk.Frame(self.root)
        nav_frame.pack(pady=20)
        
        self.prev_button = ttk.Button(nav_frame, text="Previous", command=self.previous_step)
        self.prev_button.pack(side='left', padx=10)
        
        self.next_button = ttk.Button(nav_frame, text="Next", command=self.next_step)
        self.next_button.pack(side='left', padx=10)
        
        self.finish_button = ttk.Button(nav_frame, text="Finish", command=self.finish_setup)
        self.finish_button.pack(side='left', padx=10)
        self.finish_button.config(state='disabled')
    
    def setup_step1(self):
        """Setup basic information step"""
        ttk.Label(self.step1_frame, text="Your Information", 
                 font=('Arial', 14, 'bold')).pack(pady=20)
        
        # Email
        ttk.Label(self.step1_frame, text="Email Address:").pack(pady=5)
        self.email_entry = ttk.Entry(self.step1_frame, width=40)
        self.email_entry.pack(pady=5)
        
        # Primary location
        ttk.Label(self.step1_frame, text="Primary Work Location:").pack(pady=5)
        self.location_entry = ttk.Entry(self.step1_frame, width=40)
        self.location_entry.pack(pady=5)
        
        # Meeting length preference
        ttk.Label(self.step1_frame, text="Preferred Meeting Length (minutes):").pack(pady=5)
        self.meeting_length = ttk.Spinbox(self.step1_frame, from_=15, to=120, 
                                         increment=15, width=10)
        self.meeting_length.set(60)
        self.meeting_length.pack(pady=5)
        
        # Focus time preference
        ttk.Label(self.step1_frame, text="Preferred Focus Block Length (minutes):").pack(pady=5)
        self.focus_length = ttk.Spinbox(self.step1_frame, from_=30, to=240, 
                                       increment=30, width=10)
        self.focus_length.set(120)
        self.focus_length.pack(pady=5)
    
    def setup_step2(self):
        """Setup working hours step"""
        ttk.Label(self.step2_frame, text="Define Your Working Hours", 
                 font=('Arial', 14, 'bold')).pack(pady=20)
        
        ttk.Label(self.step2_frame, 
                 text="Leave blank for days you don't typically work").pack(pady=5)
        
        self.working_hours_entries = {}
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        hours_frame = ttk.Frame(self.step2_frame)
        hours_frame.pack(pady=10)
        
        for i, day in enumerate(days):
            ttk.Label(hours_frame, text=f"{day}:").grid(row=i, column=0, sticky='e', padx=5, pady=3)
            
            start_entry = ttk.Entry(hours_frame, width=8)
            start_entry.grid(row=i, column=1, padx=2, pady=3)
            
            ttk.Label(hours_frame, text="to").grid(row=i, column=2, padx=2, pady=3)
            
            end_entry = ttk.Entry(hours_frame, width=8)
            end_entry.grid(row=i, column=3, padx=2, pady=3)
            
            # Default for weekdays
            if i < 5:  # Monday to Friday
                start_entry.insert(0, "09:00")
                end_entry.insert(0, "17:00")
            
            self.working_hours_entries[day] = (start_entry, end_entry)
    
    def setup_step3(self):
        """Setup energy patterns step"""
        ttk.Label(self.step3_frame, text="Your Energy Patterns Throughout the Day", 
                 font=('Arial', 14, 'bold')).pack(pady=20)
        
        ttk.Label(self.step3_frame, 
                 text="Rate your typical energy level for each hour (0=Low, 10=High)").pack(pady=5)
        
        canvas_frame = ttk.Frame(self.step3_frame)
        canvas_frame.pack(pady=10)
        
        # Create scrollable frame for sliders
        canvas = tk.Canvas(canvas_frame, height=400)
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        self.energy_sliders = {}
        for hour in range(6, 22):  # 6 AM to 9 PM
            frame = ttk.Frame(scrollable_frame)
            frame.pack(pady=5)
            
            ttk.Label(frame, text=f"{hour:02d}:00", width=6).pack(side='left', padx=5)
            
            slider = ttk.Scale(frame, from_=0, to=10, orient='horizontal', length=300)
            slider.pack(side='left', padx=5)
            
            # Set default pattern (higher in morning, dip after lunch, slight recovery)
            if 9 <= hour <= 11:
                slider.set(8)
            elif 14 <= hour <= 15:
                slider.set(5)
            else:
                slider.set(6)
            
            value_label = ttk.Label(frame, text="6", width=3)
            value_label.pack(side='left', padx=5)
            
            # Update label when slider moves
            slider.configure(command=lambda v, l=value_label: l.configure(text=f"{float(v):.0f}"))
            
            self.energy_sliders[hour] = slider
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def setup_step4(self):
        """Setup preferences step"""
        ttk.Label(self.step4_frame, text="Scheduling Rules & Preferences", 
                 font=('Arial', 14, 'bold')).pack(pady=20)
        
        ttk.Label(self.step4_frame, 
                 text="Add any specific rules for your schedule\n"
                      "(e.g., 'No meetings before 10 AM', 'Friday afternoons for deep work')").pack(pady=5)
        
        self.rules_text = scrolledtext.ScrolledText(self.step4_frame, height=10, width=60)
        self.rules_text.pack(pady=10)
        
        # Add some example rules
        self.rules_text.insert(tk.END, "# Example rules (modify or delete as needed):\n")
        self.rules_text.insert(tk.END, "No meetings before 10 AM\n")
        self.rules_text.insert(tk.END, "Keep Fridays meeting-free for deep work\n")
        self.rules_text.insert(tk.END, "Lunch break between 12 PM and 1 PM\n")
        self.rules_text.insert(tk.END, "Maximum 3 hours of meetings per day\n")
    
    def setup_step5(self):
        """Setup Google Calendar step"""
        ttk.Label(self.step5_frame, text="Google Calendar Setup", 
                 font=('Arial', 14, 'bold')).pack(pady=20)
        
        instructions = """To connect with Google Calendar:

1. Go to: https://console.cloud.google.com/
2. Create a new project or select an existing one
3. Enable the Google Calendar API
4. Create credentials (OAuth 2.0 Client ID)
5. Download the credentials as 'credentials.json'
6. Place the file in the same directory as this application

Once you have the credentials.json file ready:"""
        
        ttk.Label(self.step5_frame, text=instructions, justify='left').pack(pady=10)
        
        self.google_status = ttk.Label(self.step5_frame, text="Status: Not configured", 
                                      foreground='red')
        self.google_status.pack(pady=10)
        
        ttk.Button(self.step5_frame, text="Test Google Calendar Connection", 
                  command=self.test_google_connection).pack(pady=10)
        
        self.skip_google_var = tk.BooleanVar()
        ttk.Checkbutton(self.step5_frame, text="Skip Google Calendar setup for now", 
                       variable=self.skip_google_var).pack(pady=10)
    
    def test_google_connection(self):
        """Test Google Calendar connection"""
        try:
            if not os.path.exists('credentials.json'):
                messagebox.showerror("Error", "credentials.json not found in application directory")
                return
            
            calendar = CalendarIntegration()
            calendar.authenticate()
            
            self.google_status.config(text="Status: Connected successfully!", foreground='green')
            messagebox.showinfo("Success", "Google Calendar connected successfully!")
            
        except Exception as e:
            self.google_status.config(text=f"Status: Connection failed", foreground='red')
            messagebox.showerror("Error", f"Failed to connect: {str(e)}")
    
    def previous_step(self):
        """Go to previous step"""
        current = self.notebook.index(self.notebook.select())
        if current > 0:
            self.notebook.select(current - 1)
            
            # Update button states
            if current - 1 == 0:
                self.prev_button.config(state='disabled')
            self.next_button.config(state='normal')
            self.finish_button.config(state='disabled')
    
    def next_step(self):
        """Go to next step"""
        current = self.notebook.index(self.notebook.select())
        if current < 4:
            self.notebook.select(current + 1)
            
            # Update button states
            self.prev_button.config(state='normal')
            if current + 1 == 4:
                self.next_button.config(state='disabled')
                self.finish_button.config(state='normal')
    
    def finish_setup(self):
        """Complete setup and save profile"""
        try:
            # Collect all data
            self.user_profile.email = self.email_entry.get()
            if self.location_entry.get():
                self.user_profile.locations = [self.location_entry.get()]
            
            self.user_profile.preferred_meeting_length = int(self.meeting_length.get())
            self.user_profile.focus_time_length = int(self.focus_length.get())
            
            # Working hours
            for day, (start_entry, end_entry) in self.working_hours_entries.items():
                start = start_entry.get()
                end = end_entry.get()
                if start and end:
                    self.user_profile.working_hours[day] = (start, end)
            
            # Energy patterns
            for hour, slider in self.energy_sliders.items():
                self.user_profile.energy_patterns[hour] = slider.get() / 10.0
            
            # Rules
            rules_text = self.rules_text.get(1.0, tk.END).strip()
            if rules_text:
                rules = [r.strip() for r in rules_text.split('\n') 
                        if r.strip() and not r.strip().startswith('#')]
                self.user_profile.behavioral_rules = rules
            
            # Save profile
            with open('user_profile.json', 'w') as f:
                json.dump(self.user_profile.to_dict(), f, indent=2, default=str)
            
            messagebox.showinfo("Success", "Setup completed! Starting AI Schedule Agent...")
            
            # Close wizard and start main app
            self.root.destroy()
            
            # Start main application
            app = SchedulerUI()
            app.run()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to complete setup: {str(e)}")
    
    def run(self):
        """Run the setup wizard"""
        self.root.mainloop()


# Main entry point
if __name__ == "__main__":
    # Check if this is first run
    if not os.path.exists('user_profile.json'):
        # Run setup wizard
        wizard = SetupWizard()
        wizard.run()
    else:
        # Run main application
        app = SchedulerUI()
        app.run()