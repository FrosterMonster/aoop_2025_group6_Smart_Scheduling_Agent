"""Insights tab for analytics and pattern analysis"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import datetime
from datetime import timedelta
from collections import defaultdict, Counter
import numpy as np


class InsightsTab:
    """Insights tab UI component"""

    def __init__(self, parent, scheduling_engine, calendar_integration, user_profile, notification_manager):
        self.parent = parent
        self.scheduling_engine = scheduling_engine
        self.calendar = calendar_integration
        self.user_profile = user_profile
        self.notification_manager = notification_manager
        self.insights_display = None

        self.setup_ui()

    def setup_ui(self):
        """Setup insights tab UI"""

        # Controls
        controls_frame = ttk.Frame(self.parent)
        controls_frame.pack(pady=10)

        ttk.Button(controls_frame, text="Analyze Patterns",
                  command=self.analyze_patterns).pack(side='left', padx=5)
        ttk.Button(controls_frame, text="Get Suggestions",
                  command=self.get_scheduling_suggestions).pack(side='left', padx=5)
        ttk.Button(controls_frame, text="Check Work-Life Balance",
                  command=self.check_work_life_balance).pack(side='left', padx=5)

        # Insights display
        self.insights_display = scrolledtext.ScrolledText(self.parent, height=25, width=90)
        self.insights_display.pack(pady=10, padx=10, fill='both', expand=True)

    def analyze_patterns(self):
        """Analyze scheduling patterns"""
        self.insights_display.delete(1.0, tk.END)
        self.insights_display.insert(tk.END, "📊 SCHEDULING PATTERNS ANALYSIS\n")
        self.insights_display.insert(tk.END, "="*50 + "\n\n")

        # Analyze time preferences
        self.insights_display.insert(tk.END, "⏰ Time Preferences by Event Type:\n")
        self.insights_display.insert(tk.END, "-"*30 + "\n")

        for event_type, hours in self.scheduling_engine.pattern_learner.time_preferences.items():
            if hours:
                most_common = hours.most_common(3)
                self.insights_display.insert(tk.END, f"\n{event_type.value}:\n")
                for hour, count in most_common:
                    self.insights_display.insert(tk.END, f"  • {hour:02d}:00 - {count} times\n")

        # Analyze weekly patterns
        self.insights_display.insert(tk.END, "\n\n📅 Weekly Patterns:\n")
        self.insights_display.insert(tk.END, "-"*30 + "\n")

        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        for day_idx, patterns in self.scheduling_engine.pattern_learner.scheduling_patterns.items():
            if patterns and day_idx < len(days):
                self.insights_display.insert(tk.END, f"\n{days[day_idx]}:\n")

                # Count event types
                type_counts = Counter(p['type'] for p in patterns)
                for event_type, count in type_counts.most_common():
                    self.insights_display.insert(tk.END, f"  • {event_type.value}: {count} events\n")

        # Suggest optimizations
        self.insights_display.insert(tk.END, "\n\n💡 Optimization Suggestions:\n")
        self.insights_display.insert(tk.END, "-"*30 + "\n")

        batch_suggestions = self.scheduling_engine.suggest_batch_opportunities()
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
