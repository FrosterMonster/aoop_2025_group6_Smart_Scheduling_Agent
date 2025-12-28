"""Quick schedule tab for natural language and form-based scheduling"""

import datetime
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

        # Natural language input (阿嚕米 style)
        ttk.Label(self.parent, text="📅 AI 智能排程助手", font=('Arial', 14, 'bold')).pack(pady=10)
        ttk.Label(self.parent, text="輸入自然語言，系統自動解析並填充表單", font=('Arial', 10), foreground='gray').pack(pady=2)

        self.nl_input = ttk.Entry(self.parent, width=80, font=('Arial', 11))
        self.nl_input.pack(pady=5)
        self.nl_input.bind('<Return>', lambda e: self.process_nl_input())
        self.nl_input.insert(0, "例如：明天下午排3小時開會")
        self.nl_input.bind('<FocusIn>', lambda e: self.nl_input.delete(0, tk.END) if self.nl_input.get().startswith("例如") else None)

        nl_button_frame = ttk.Frame(self.parent)
        nl_button_frame.pack(pady=5)
        ttk.Button(nl_button_frame, text="🔍 開始解析", command=self.process_nl_input, style='Accent.TButton').pack(side='left', padx=5)
        ttk.Button(nl_button_frame, text="清除", command=self.clear_nl_input).pack(side='left', padx=5)

        # Separator
        ttk.Separator(self.parent, orient='horizontal').pack(fill='x', pady=20)

        # Detailed form (阿嚕米 style)
        ttk.Label(self.parent, text="📋 詳細活動表單", font=('Arial', 12, 'bold')).pack(pady=10)
        ttk.Label(self.parent, text="（由上方 AI 自動填充，或手動編輯）", font=('Arial', 9), foreground='gray').pack(pady=2)

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

        # Submit and Clear buttons (阿嚕米 style)
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=len(fields)+4, column=0, columnspan=2, pady=20)

        ttk.Button(button_frame, text="✅ 確認新增至日曆",
                  command=self.schedule_event_from_form, style='Accent.TButton').pack(side='left', padx=5)
        ttk.Button(button_frame, text="清除表單",
                  command=self.clear_form).pack(side='left', padx=5)

        # Result display
        self.result_text = scrolledtext.ScrolledText(self.parent, height=8, width=80)
        self.result_text.pack(pady=10)

    def process_nl_input(self):
        """Process natural language input and populate the form (阿嚕米 style)

        This method follows阿嚕米's design:
        1. Parse natural language using Mock mode patterns
        2. Auto-fill the form below
        3. Show suggestion based on flexible/fixed time
        """
        text = self.nl_input.get()
        if not text:
            return

        self.update_status("🔍 正在解析自然語言...")

        # Parse the input using阿嚕米 Mock mode
        parsed = self.nlp_processor.parse_scheduling_request(text)

        # Clear result display
        self.result_text.delete(1.0, tk.END)

        # Handle different actions
        if parsed['action'] == 'check_schedule':
            # Handle check_schedule action - find optimal slot first
            self._handle_check_schedule_action(parsed)
        elif parsed['action'] == 'create':
            # Display parsed information (阿嚕米 style)
            self.result_text.insert(tk.END, "✨ AI 解析結果\n")
            self.result_text.insert(tk.END, "=" * 60 + "\n\n")

            # Display parsed fields in a nicer format
            if parsed.get('title'):
                self.result_text.insert(tk.END, f"  📌 Title: {parsed['title']}\n")
            if parsed.get('datetime'):
                self.result_text.insert(tk.END, f"  📅 Date/Time: {parsed['datetime'].strftime('%Y-%m-%d %H:%M')}\n")
            if parsed.get('duration'):
                self.result_text.insert(tk.END, f"  ⏱️  Duration: {parsed['duration']} minutes\n")
            if parsed.get('location'):
                self.result_text.insert(tk.END, f"  📍 Location: {parsed['location']}\n")
            if parsed.get('participants'):
                self.result_text.insert(tk.END, f"  👥 Participants: {', '.join(parsed['participants'])}\n")
            if parsed.get('event_type'):
                event_type_str = parsed['event_type'].value if hasattr(parsed['event_type'], 'value') else str(parsed['event_type'])
                self.result_text.insert(tk.END, f"  🏷️  Type: {event_type_str}\n")

            # Determine if this is flexible or fixed time (阿嚕米 logic)
            is_flexible = parsed.get('time_preference') is not None and not parsed.get('datetime')
            has_exact_time = parsed.get('datetime') is not None

            self.result_text.insert(tk.END, "\n" + "=" * 60 + "\n")

            if is_flexible:
                # Flexible scheduling (阿嚕米 style message)
                self.result_text.insert(tk.END, "✨ AI 建議：系統將自動避開衝突，為您找尋最佳空檔。\n")
                self.result_text.insert(tk.END, f"   時段偏好：{parsed['time_preference'].get('period', 'N/A')}\n")
                self.is_flexible_var.set(True)
            elif has_exact_time:
                # Fixed time (阿嚕米 style message)
                self.result_text.insert(tk.END, "📍 AI 建議：此為固定行程，將排定於指定時間。\n")
                self.is_flexible_var.set(False)
            else:
                # General case
                self.result_text.insert(tk.END, "📝 表單已填充，請檢查後點擊「Schedule Event」確認。\n")

            self.result_text.insert(tk.END, "\n下方表單已自動填充，請檢查後提交。\n")

            # Clear existing form data
            for entry in self.form_entries.values():
                entry.delete(0, tk.END)
            self.tags_entry.delete(0, tk.END)

            # Title
            title = parsed.get('title', '')
            if title:
                self.form_entries['title'].insert(0, title)

            # Description (if any)
            description = parsed.get('description', '')
            if description:
                self.form_entries['description'].insert(0, description)

            # Location
            location = parsed.get('location', '')
            if location:
                self.form_entries['location'].insert(0, location)

            # Participants
            participants = parsed.get('participants', [])
            if participants:
                self.form_entries['participants'].insert(0, ', '.join(participants))

            # Date and time
            if parsed.get('datetime'):
                # User specified exact time - use it
                dt = parsed['datetime']
                self.form_entries['date'].insert(0, dt.strftime('%Y-%m-%d'))
                self.form_entries['start_time'].insert(0, dt.strftime('%H:%M'))

                # Duration
                duration = parsed.get('duration', self.scheduling_engine.user_profile.preferred_meeting_length)
                self.form_entries['duration'].insert(0, str(duration))
            elif parsed.get('target_date') and parsed.get('time_preference'):
                # User specified time period (e.g., "明天下午") - find optimal slot within that period
                import datetime as dt_module
                from datetime import timedelta

                target_date = parsed['target_date']
                time_pref = parsed['time_preference']
                duration = parsed.get('duration', self.scheduling_engine.user_profile.preferred_meeting_length)
                start_hour = time_pref.get('start_hour', 9)
                end_hour = time_pref.get('end_hour', 18)

                # Create event with duration
                temp_event = Event(
                    title=title or 'New Event',
                    event_type=parsed.get('event_type', EventType.MEETING),
                    duration_minutes=duration,
                    participants=participants,
                    location=location
                )

                # CRITICAL: Manually find free slots STRICTLY within the time preference window
                # We can't rely on find_optimal_slot because it uses working_hours from profile
                # which might be wider than the user's requested time period

                # Create search window for the specific time period
                window_start = dt_module.datetime.combine(target_date, dt_module.time(hour=start_hour))
                window_end = dt_module.datetime.combine(target_date, dt_module.time(hour=end_hour))

                # Get busy times for the target date
                day_start = dt_module.datetime.combine(target_date, dt_module.time(hour=0))
                day_end = dt_module.datetime.combine(target_date, dt_module.time(hour=23, minute=59))

                existing_events = self.scheduling_engine.calendar.get_events(
                    day_start.isoformat() + 'Z',
                    day_end.isoformat() + 'Z'
                )

                # Extract busy slots
                busy_slots = []
                for e in existing_events:
                    if 'dateTime' in e.get('start', {}):
                        event_start = dt_module.datetime.fromisoformat(e['start']['dateTime'].replace('Z', '+00:00'))
                        event_end = dt_module.datetime.fromisoformat(e['end']['dateTime'].replace('Z', '+00:00'))
                        event_start = event_start.replace(tzinfo=None)
                        event_end = event_end.replace(tzinfo=None)
                        busy_slots.append((event_start, event_end))

                # Find free slots STRICTLY within the time preference window
                optimal_slot = None
                best_score = -1
                current_slot = window_start

                while current_slot + timedelta(minutes=duration) <= window_end:
                    slot_end = current_slot + timedelta(minutes=duration)

                    # Skip if in the past
                    if current_slot < dt_module.datetime.now() + timedelta(minutes=30):
                        current_slot += timedelta(minutes=30)
                        continue

                    # Check if this slot is free
                    is_free = True
                    for busy_start, busy_end in busy_slots:
                        # Slots overlap if: NOT (slot ends before busy starts OR slot starts after busy ends)
                        if not (slot_end <= busy_start or current_slot >= busy_end):
                            is_free = False
                            break

                    if is_free:
                        # Calculate score using scheduling engine's scoring logic
                        score = self.scheduling_engine._calculate_slot_score(current_slot, temp_event.event_type)
                        if score > best_score:
                            best_score = score
                            optimal_slot = (current_slot, slot_end)

                    # Move to next 30-minute slot
                    current_slot += timedelta(minutes=30)

                if optimal_slot:
                    start_time, end_time = optimal_slot

                    # Slot is guaranteed to fit within window (we checked in the search loop)
                    self.form_entries['date'].insert(0, start_time.strftime('%Y-%m-%d'))
                    self.form_entries['start_time'].insert(0, start_time.strftime('%H:%M'))
                    self.form_entries['duration'].insert(0, str(duration))

                    period_name = time_pref.get('period', 'preferred time')
                    self.result_text.insert(tk.END, f"\n✅ Found optimal {period_name} slot: {start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}\n")
                    self.result_text.insert(tk.END, f"   Free slot within {start_hour}:00-{end_hour}:00 window as requested\n")
                else:
                    # No slot found within the time preference window
                    period_name = time_pref.get('period', 'preferred time')
                    self.result_text.insert(tk.END, f"\n⚠️ No free {duration}-minute slot in {period_name} ({start_hour}:00-{end_hour}:00)\n")
                    self.result_text.insert(tk.END, f"   on {target_date.strftime('%Y-%m-%d')}\n")
                    self.result_text.insert(tk.END, f"\n💡 Suggestions:\n")
                    self.result_text.insert(tk.END, f"   • Try a shorter duration (e.g., {duration//2} minutes)\n")
                    self.result_text.insert(tk.END, f"   • Choose a different time period (morning/evening)\n")
                    self.result_text.insert(tk.END, f"   • Select a different day\n")
            else:
                # No datetime or time preference - try to find any optimal time
                duration = parsed.get('duration', self.scheduling_engine.user_profile.preferred_meeting_length)

                temp_event = Event(
                    title=title or 'New Event',
                    event_type=parsed.get('event_type', EventType.MEETING),
                    duration_minutes=duration,
                    participants=participants,
                    location=location
                )

                optimal_slot = self.scheduling_engine.find_optimal_slot(temp_event)
                if optimal_slot:
                    start_time, end_time = optimal_slot
                    self.form_entries['date'].insert(0, start_time.strftime('%Y-%m-%d'))
                    self.form_entries['start_time'].insert(0, start_time.strftime('%H:%M'))
                    self.form_entries['duration'].insert(0, str(duration))

                    self.result_text.insert(tk.END, f"\n💡 Suggested optimal time: {start_time.strftime('%Y-%m-%d %H:%M')}\n")

            # Event type
            event_type = parsed.get('event_type', EventType.MEETING)
            if isinstance(event_type, EventType):
                self.event_type_var.set(event_type.value)
            else:
                self.event_type_var.set(str(event_type))

            # Priority (default to medium)
            priority = parsed.get('priority', 'MEDIUM')
            if isinstance(priority, str):
                self.priority_var.set(priority.upper())

            # Prep time and follow-up time (if specified)
            if parsed.get('prep_time'):
                self.form_entries['prep_time'].insert(0, str(parsed['prep_time']))

            if parsed.get('followup_time'):
                self.form_entries['followup_time'].insert(0, str(parsed['followup_time']))

            # Tags (if any)
            tags = parsed.get('tags', [])
            if tags:
                self.tags_entry.insert(0, ', '.join(tags))

            # Check for conflicts and display warning
            if parsed.get('datetime'):
                temp_event = Event(
                    title=title or 'New Event',
                    event_type=parsed.get('event_type', EventType.MEETING),
                    start_time=parsed['datetime'],
                    end_time=parsed['datetime'] + timedelta(minutes=parsed.get('duration', 60))
                )

                conflicts = self.scheduling_engine.check_conflicts(temp_event)
                if conflicts:
                    self.result_text.insert(tk.END, "\n⚠️  WARNING: Conflicts detected:\n")
                    for conflict in conflicts:
                        self.result_text.insert(tk.END, f"     - {conflict['event']['summary']}\n")
                else:
                    self.result_text.insert(tk.END, "\n✅ No conflicts detected.\n")

        self.update_status("Form populated - review and click 'Schedule Event'")

    def _handle_check_schedule_action(self, parsed):
        """Handle check_schedule action by finding optimal slot and populating form"""
        # Display parsed information
        self.result_text.insert(tk.END, "🔍 Checking Schedule for Optimal Time Slot\n")
        self.result_text.insert(tk.END, "=" * 60 + "\n\n")

        # Get target date and duration
        target_date = parsed.get('target_date')
        duration = parsed.get('duration', 60)  # minutes
        title = parsed.get('title', 'New Event')
        description = parsed.get('description', '')
        location = parsed.get('location', '')
        event_type = parsed.get('event_type', EventType.MEETING)
        participants = parsed.get('participants', [])

        # Display parsed fields
        self.result_text.insert(tk.END, f"  📌 Title: {title}\n")
        if target_date:
            self.result_text.insert(tk.END, f"  📅 Target Date: {target_date.strftime('%Y-%m-%d')}\n")
        self.result_text.insert(tk.END, f"  ⏱️  Duration: {duration} minutes\n")
        if location:
            self.result_text.insert(tk.END, f"  📍 Location: {location}\n")
        if participants:
            self.result_text.insert(tk.END, f"  👥 Participants: {', '.join(participants)}\n")

        # Display LLM response if available
        if parsed.get('llm_response'):
            self.result_text.insert(tk.END, f"\n💬 AI: {parsed['llm_response']}\n")

        self.result_text.insert(tk.END, "\n" + "=" * 60 + "\n")

        # Clear existing form data
        for entry in self.form_entries.values():
            entry.delete(0, tk.END)
        self.tags_entry.delete(0, tk.END)

        # Check if LLM has already suggested a time
        suggested_time = parsed.get('suggested_time')

        if suggested_time:
            # Use LLM-suggested time
            self.result_text.insert(tk.END, "🤖 AI analyzed your calendar and found optimal time...\n\n")

            start_time = suggested_time['start_time']
            end_time = start_time + timedelta(minutes=duration)

            # Display LLM reasoning
            reasoning = suggested_time.get('reasoning', '')
            if reasoning:
                # Extract just the reasoning part (after "Reasoning:")
                reasoning_lines = reasoning.split('\n')
                for line in reasoning_lines:
                    if 'reasoning' in line.lower() or 'suggest' in line.lower():
                        self.result_text.insert(tk.END, f"💡 {line.strip()}\n")

            optimal_slot = (start_time, end_time)
        else:
            # Fallback to traditional scheduling engine
            self.result_text.insert(tk.END, "🔎 Searching for available time slots...\n\n")

            # Create a temporary event to find optimal slot
            # Set temporary start/end times to indicate desired duration
            temp_start = target_date if target_date else datetime.datetime.now()
            temp_end = temp_start + timedelta(minutes=duration)

            temp_event = Event(
                title=title,
                event_type=event_type,
                participants=participants,
                location=location,
                description=description,
                start_time=temp_start,
                end_time=temp_end
            )

            # Find optimal slot
            if target_date:
                # Search from the target date
                optimal_slot = self.scheduling_engine.find_optimal_slot(
                    temp_event,
                    search_start=target_date
                )
            else:
                # Search from now
                optimal_slot = self.scheduling_engine.find_optimal_slot(
                    temp_event
                )

        if optimal_slot:
            start_time, end_time = optimal_slot

            # Populate form with optimal slot
            self.form_entries['title'].insert(0, title)
            if description:
                self.form_entries['description'].insert(0, description)
            if location:
                self.form_entries['location'].insert(0, location)
            if participants:
                self.form_entries['participants'].insert(0, ', '.join(participants))

            self.form_entries['date'].insert(0, start_time.strftime('%Y-%m-%d'))
            self.form_entries['start_time'].insert(0, start_time.strftime('%H:%M'))

            actual_duration = int((end_time - start_time).total_seconds() / 60)
            self.form_entries['duration'].insert(0, str(actual_duration))

            # Set event type
            if isinstance(event_type, EventType):
                self.event_type_var.set(event_type.value)

            # Display success message
            self.result_text.insert(tk.END, f"\n✅ Optimal time slot found:\n")
            self.result_text.insert(tk.END, f"   📅 {start_time.strftime('%Y-%m-%d %H:%M')} - {end_time.strftime('%H:%M')}\n")
            self.result_text.insert(tk.END, f"   ⏱️  Duration: {actual_duration} minutes\n")
            self.result_text.insert(tk.END, "\n💡 This time slot avoids conflicts with your existing schedule.\n")
            self.result_text.insert(tk.END, "Please review and click 'Schedule Event' to confirm.\n")

            self.update_status("Optimal time slot found - review and confirm")
        else:
            # No optimal slot found
            self.result_text.insert(tk.END, f"\n⚠️ No available time slot found for the requested date/time.\n")

            # Still populate what we have
            self.form_entries['title'].insert(0, title)
            if description:
                self.form_entries['description'].insert(0, description)
            if location:
                self.form_entries['location'].insert(0, location)
            if participants:
                self.form_entries['participants'].insert(0, ', '.join(participants))

            self.form_entries['duration'].insert(0, str(duration))

            # Set event type
            if isinstance(event_type, EventType):
                self.event_type_var.set(event_type.value)

            self.result_text.insert(tk.END, "Please manually specify a date and time, or try a different date.\n")
            self.update_status("No optimal slot found - please specify time manually")

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

    def clear_nl_input(self):
        """Clear natural language input field"""
        self.nl_input.delete(0, tk.END)
        self.result_text.delete(1.0, tk.END)

    def clear_form(self):
        """Clear all form fields"""
        for entry in self.form_entries.values():
            entry.delete(0, tk.END)
        self.tags_entry.delete(0, tk.END)
        self.event_type_var.set(EventType.MEETING.value)
        self.priority_var.set("MEDIUM")
        self.is_flexible_var.set(True)
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, "✅ Form cleared. Ready for new event.\n")
