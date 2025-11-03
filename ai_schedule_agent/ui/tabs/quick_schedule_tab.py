"""Quick schedule tab for natural language and form-based scheduling"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import timedelta

from ai_schedule_agent.models.event import Event
from ai_schedule_agent.models.enums import EventType, Priority


class QuickScheduleTab:
    """Quick schedule tab UI component"""

    def __init__(self, parent, nlp_processor, scheduling_engine, schedule_callback, update_status_callback):
        self.parent = parent
        self.nlp_processor = nlp_processor
        self.scheduling_engine = scheduling_engine
        self.schedule_callback = schedule_callback
        self.update_status = update_status_callback

        self.setup_ui()

    def setup_ui(self):
        """Setup quick schedule tab UI"""

        # Natural language input
        ttk.Label(self.parent, text="Natural Language Input:", font=('Arial', 12)).pack(pady=10)

        self.nl_input = ttk.Entry(self.parent, width=80, font=('Arial', 11))
        self.nl_input.pack(pady=5)
        self.nl_input.bind('<Return>', lambda e: self.process_nl_input())

        ttk.Button(self.parent, text="Process", command=self.process_nl_input).pack(pady=5)

        # Separator
        ttk.Separator(self.parent, orient='horizontal').pack(fill='x', pady=20)

        # Detailed form
        ttk.Label(self.parent, text="Detailed Event Form:", font=('Arial', 12)).pack(pady=10)

        form_frame = ttk.Frame(self.parent)
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
        self.result_text = scrolledtext.ScrolledText(self.parent, height=8, width=80)
        self.result_text.pack(pady=10)

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
                duration = parsed.get('duration', self.scheduling_engine.user_profile.preferred_meeting_length)
                event.end_time = event.start_time + timedelta(minutes=duration)
            else:
                optimal_slot = self.scheduling_engine.find_optimal_slot(event)
                if optimal_slot:
                    event.start_time, event.end_time = optimal_slot

            # Check for conflicts
            conflicts = self.scheduling_engine.check_conflicts(event)

            if conflicts:
                self.result_text.insert(tk.END, "\n⚠️ Conflicts detected:\n")
                for conflict in conflicts:
                    self.result_text.insert(tk.END, f"  - {conflict['event']['summary']}\n")

                # Ask for confirmation
                if messagebox.askyesno("Conflicts Detected",
                                       "There are conflicts. Do you want to schedule anyway?"):
                    self.schedule_callback(event)
            else:
                # Ask for confirmation
                self.result_text.insert(tk.END, f"\n✅ Proposed Time: {event.start_time} - {event.end_time}\n")
                if messagebox.askyesno("Confirm Scheduling",
                                       f"Schedule '{event.title}' at {event.start_time}?"):
                    self.schedule_callback(event)

        self.update_status("Ready")

    def schedule_event_from_form(self):
        """Schedule event from detailed form"""
        import datetime

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

            duration = int(self.form_entries['duration'].get() or self.scheduling_engine.user_profile.preferred_meeting_length)

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
                conflicts = self.scheduling_engine.check_conflicts(event)
                if conflicts:
                    if not messagebox.askyesno("Conflicts Detected",
                                              "There are scheduling conflicts. Continue anyway?"):
                        return
            else:
                # Find optimal slot
                optimal_slot = self.scheduling_engine.find_optimal_slot(event)
                if optimal_slot:
                    event.start_time, event.end_time = optimal_slot

                    if not messagebox.askyesno("Time Suggestion",
                                              f"Suggested time: {event.start_time}. Accept?"):
                        return
                else:
                    messagebox.showerror("Error", "No available time slot found")
                    return

            # Schedule the event
            self.schedule_callback(event)

            # Clear form
            for entry in self.form_entries.values():
                entry.delete(0, tk.END)
            self.tags_entry.delete(0, tk.END)

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def display_result(self, message):
        """Display result message"""
        self.result_text.insert(tk.END, f"\n{message}\n")
