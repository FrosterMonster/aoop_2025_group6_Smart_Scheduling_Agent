"""Settings tab for user preferences configuration"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox


class SettingsTab:
    """Settings tab UI component with modern design"""

    def __init__(self, parent, user_profile, save_profile_callback):
        self.parent = parent
        self.user_profile = user_profile
        self.save_profile = save_profile_callback

        self.working_hours_entries = {}
        self.energy_sliders = {}
        self.energy_labels = {}
        self.rules_text = None
        self.email_entry = None
        self.auto_save_timer = None

        # Modern colors
        self.colors = {
            'bg_primary': '#fafbfc',
            'bg_secondary': '#f0f2f5',
            'text_primary': '#202124',
            'text_secondary': '#5f6368',
            'accent_blue': '#1a73e8',
            'accent_green': '#1e8e3e',
            'border': '#dadce0'
        }

        self.setup_ui()

    def create_section_header(self, parent, text):
        """Create a styled section header"""
        header_frame = tk.Frame(parent, bg=self.colors['bg_primary'])
        header_frame.pack(fill='x', pady=(20, 10), padx=20)

        tk.Label(header_frame, text=text,
                font=('Segoe UI', 14, 'bold'),
                bg=self.colors['bg_primary'],
                fg=self.colors['text_primary']).pack(anchor='w')

    def create_card(self, parent):
        """Create a card-style container"""
        card = tk.Frame(parent, bg=self.colors['bg_secondary'], relief='flat')
        card.pack(fill='x', pady=(0, 15), padx=20)
        return card

    def schedule_auto_save(self):
        """Schedule auto-save after a short delay to avoid excessive saves"""
        # Show "saving..." status
        if hasattr(self, 'save_status_label'):
            self.save_status_label.config(text="💾 Saving...",
                                         fg=self.colors['accent_blue'])

        # Cancel any existing timer
        if self.auto_save_timer:
            self.parent.after_cancel(self.auto_save_timer)

        # Schedule new save after 1 second of inactivity
        self.auto_save_timer = self.parent.after(1000, self.auto_save_settings)

    def auto_save_settings(self):
        """Automatically save settings without showing message"""
        try:
            # Save working hours
            for day, (start_entry, end_entry) in self.working_hours_entries.items():
                start = start_entry.get().strip()
                end = end_entry.get().strip()
                if start and end:
                    self.user_profile.working_hours[day] = (start, end)

            # Save energy patterns
            for hour, slider in self.energy_sliders.items():
                self.user_profile.energy_patterns[hour] = slider.get() / 10.0

            # Save behavioral rules
            rules_text = self.rules_text.get('1.0', tk.END).strip()
            if rules_text:
                self.user_profile.behavioral_rules = [
                    rule.strip() for rule in rules_text.split('\n')
                    if rule.strip()
                ]
            else:
                self.user_profile.behavioral_rules = []

            # Save email
            email = self.email_entry.get().strip()
            if email:
                self.user_profile.email = email

            # Save to file (with error handling)
            try:
                self.save_profile()
                print(f"[AUTO-SAVE] Settings saved successfully")
                print(f"[AUTO-SAVE] Working hours: {self.user_profile.working_hours}")
                print(f"[AUTO-SAVE] Energy patterns: {self.user_profile.energy_patterns}")
                print(f"[AUTO-SAVE] Email: {self.user_profile.email}")
            except Exception as save_error:
                print(f"[AUTO-SAVE] File save error: {save_error}")
                raise

            # Show success status
            if hasattr(self, 'save_status_label'):
                self.save_status_label.config(text="✓ Changes saved automatically",
                                             fg=self.colors['accent_green'])

        except Exception as e:
            # Show error status
            if hasattr(self, 'save_status_label'):
                self.save_status_label.config(text="⚠ Auto-save failed",
                                             fg='#ea4335')
            print(f"[AUTO-SAVE] Error: {e}")
            import traceback
            traceback.print_exc()

    def setup_ui(self):
        """Setup settings tab UI with modern design and scrolling"""
        # Main container with scrollbar
        main_container = tk.Frame(self.parent, bg=self.colors['bg_primary'])
        main_container.pack(fill='both', expand=True)

        # Canvas for scrolling
        canvas = tk.Canvas(main_container, bg=self.colors['bg_primary'],
                          highlightthickness=0, bd=0)
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)

        # Scrollable frame
        scrollable_frame = tk.Frame(canvas, bg=self.colors['bg_primary'])
        scrollable_frame.bind("<Configure>",
                             lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=1000)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True, padx=0, pady=0)
        scrollbar.pack(side="right", fill="y")

        # Enable mousewheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # Working Hours Section
        self.create_section_header(scrollable_frame, "⏰ Working Hours")

        hours_card = self.create_card(scrollable_frame)
        hours_inner = tk.Frame(hours_card, bg=self.colors['bg_secondary'])
        hours_inner.pack(fill='both', padx=15, pady=15)

        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

        for i, day in enumerate(days):
            day_frame = tk.Frame(hours_inner, bg=self.colors['bg_secondary'])
            day_frame.pack(fill='x', pady=5)

            # Day label
            tk.Label(day_frame, text=f"{day}:",
                    font=('Segoe UI', 10),
                    bg=self.colors['bg_secondary'],
                    fg=self.colors['text_primary'],
                    width=12, anchor='w').pack(side='left', padx=(0, 10))

            # Start time
            start_entry = tk.Entry(day_frame, width=10,
                                  font=('Segoe UI', 10),
                                  bg='white', fg=self.colors['text_primary'],
                                  relief='solid', bd=1)
            start_entry.pack(side='left', padx=5)

            tk.Label(day_frame, text="to",
                    font=('Segoe UI', 10),
                    bg=self.colors['bg_secondary'],
                    fg=self.colors['text_secondary']).pack(side='left', padx=5)

            # End time
            end_entry = tk.Entry(day_frame, width=10,
                                font=('Segoe UI', 10),
                                bg='white', fg=self.colors['text_primary'],
                                relief='solid', bd=1)
            end_entry.pack(side='left', padx=5)

            # Load existing values
            if day in self.user_profile.working_hours:
                start, end = self.user_profile.working_hours[day]
                start_entry.insert(0, start)
                end_entry.insert(0, end)
            else:
                start_entry.insert(0, "09:00")
                end_entry.insert(0, "17:00")

            # Bind auto-save to changes
            start_entry.bind('<KeyRelease>', lambda e: self.schedule_auto_save())
            start_entry.bind('<FocusOut>', lambda e: self.schedule_auto_save())
            end_entry.bind('<KeyRelease>', lambda e: self.schedule_auto_save())
            end_entry.bind('<FocusOut>', lambda e: self.schedule_auto_save())

            self.working_hours_entries[day] = (start_entry, end_entry)

        # Energy Patterns Section
        self.create_section_header(scrollable_frame, "⚡ Energy Patterns")

        energy_card = self.create_card(scrollable_frame)
        energy_inner = tk.Frame(energy_card, bg=self.colors['bg_secondary'])
        energy_inner.pack(fill='both', padx=15, pady=15)

        tk.Label(energy_inner,
                text="Rate your typical energy level throughout the day (0 = Low, 10 = High)",
                font=('Segoe UI', 9),
                bg=self.colors['bg_secondary'],
                fg=self.colors['text_secondary']).pack(anchor='w', pady=(0, 10))

        for i in range(6, 22):  # 6 AM to 9 PM
            hour_frame = tk.Frame(energy_inner, bg=self.colors['bg_secondary'])
            hour_frame.pack(fill='x', pady=3)

            # Hour label
            tk.Label(hour_frame, text=f"{i:02d}:00",
                    font=('Segoe UI', 10),
                    bg=self.colors['bg_secondary'],
                    fg=self.colors['text_primary'],
                    width=8).pack(side='left')

            # Slider
            slider = tk.Scale(hour_frame, from_=0, to=10, orient='horizontal',
                            length=300, bg=self.colors['bg_secondary'],
                            fg=self.colors['text_primary'],
                            highlightthickness=0, bd=0,
                            troughcolor='white',
                            activebackground=self.colors['accent_blue'])
            slider.pack(side='left', padx=10)

            # Value label
            value_label = tk.Label(hour_frame, text="5",
                                  font=('Segoe UI', 10, 'bold'),
                                  bg=self.colors['bg_secondary'],
                                  fg=self.colors['accent_blue'],
                                  width=3)
            value_label.pack(side='left')

            # Load existing value
            if i in self.user_profile.energy_patterns:
                slider.set(self.user_profile.energy_patterns[i] * 10)
                value_label.config(text=str(int(self.user_profile.energy_patterns[i] * 10)))
            else:
                slider.set(5)

            # Update label when slider moves AND auto-save
            def make_update_label(lbl, sld):
                def update(val):
                    lbl.config(text=str(int(float(val))))
                    self.schedule_auto_save()  # Auto-save on slider change
                return update

            slider.config(command=make_update_label(value_label, slider))

            self.energy_sliders[i] = slider
            self.energy_labels[i] = value_label

        # Behavioral Rules Section
        self.create_section_header(scrollable_frame, "📋 Behavioral Rules")

        rules_card = self.create_card(scrollable_frame)
        rules_inner = tk.Frame(rules_card, bg=self.colors['bg_secondary'])
        rules_inner.pack(fill='both', padx=15, pady=15)

        tk.Label(rules_inner,
                text="Add scheduling rules (one per line, e.g., 'No meetings before 10 AM'):",
                font=('Segoe UI', 10),
                bg=self.colors['bg_secondary'],
                fg=self.colors['text_primary']).pack(anchor='w', pady=(0, 5))

        self.rules_text = scrolledtext.ScrolledText(rules_inner, height=8, width=80,
                                                     font=('Segoe UI', 10),
                                                     bg='white',
                                                     fg=self.colors['text_primary'],
                                                     relief='solid', bd=1,
                                                     wrap=tk.WORD)
        self.rules_text.pack(fill='x', pady=5)

        # Load existing rules
        if self.user_profile.behavioral_rules:
            for rule in self.user_profile.behavioral_rules:
                self.rules_text.insert(tk.END, rule + "\n")

        # Bind auto-save to text changes
        self.rules_text.bind('<KeyRelease>', lambda e: self.schedule_auto_save())
        self.rules_text.bind('<FocusOut>', lambda e: self.schedule_auto_save())

        # Email Settings
        self.create_section_header(scrollable_frame, "📧 Email Settings")

        email_card = self.create_card(scrollable_frame)
        email_inner = tk.Frame(email_card, bg=self.colors['bg_secondary'])
        email_inner.pack(fill='both', padx=15, pady=15)

        email_row = tk.Frame(email_inner, bg=self.colors['bg_secondary'])
        email_row.pack(fill='x', pady=5)

        tk.Label(email_row, text="Your Email:",
                font=('Segoe UI', 10),
                bg=self.colors['bg_secondary'],
                fg=self.colors['text_primary'],
                width=12, anchor='w').pack(side='left', padx=(0, 10))

        self.email_entry = tk.Entry(email_row, width=40,
                                    font=('Segoe UI', 10),
                                    bg='white', fg=self.colors['text_primary'],
                                    relief='solid', bd=1)
        self.email_entry.pack(side='left', padx=5)

        if self.user_profile.email:
            self.email_entry.insert(0, self.user_profile.email)

        # Bind auto-save to email changes
        self.email_entry.bind('<KeyRelease>', lambda e: self.schedule_auto_save())
        self.email_entry.bind('<FocusOut>', lambda e: self.schedule_auto_save())

        # Save Button and Status
        button_frame = tk.Frame(scrollable_frame, bg=self.colors['bg_primary'])
        button_frame.pack(fill='x', pady=30, padx=20)

        # Auto-save status indicator
        self.save_status_label = tk.Label(button_frame,
                                          text="✓ Changes saved automatically",
                                          font=('Segoe UI', 10),
                                          bg=self.colors['bg_primary'],
                                          fg=self.colors['text_secondary'])
        self.save_status_label.pack(side='left', padx=10)

        save_btn = tk.Button(button_frame,
                            text="💾  Save Now",
                            font=('Segoe UI', 11, 'bold'),
                            bg=self.colors['accent_green'],
                            fg='white',
                            relief='flat',
                            padx=30, pady=10,
                            cursor='hand2',
                            command=self.save_settings)
        save_btn.pack(side='right')

        # Hover effect
        def on_enter(e):
            save_btn.config(bg='#1a7c3a')  # Darker green

        def on_leave(e):
            save_btn.config(bg=self.colors['accent_green'])

        save_btn.bind('<Enter>', on_enter)
        save_btn.bind('<Leave>', on_leave)

    def save_settings(self):
        """Save user settings"""
        try:
            # Save working hours
            for day, (start_entry, end_entry) in self.working_hours_entries.items():
                start = start_entry.get().strip()
                end = end_entry.get().strip()
                if start and end:
                    self.user_profile.working_hours[day] = (start, end)

            # Save energy patterns
            for hour, slider in self.energy_sliders.items():
                self.user_profile.energy_patterns[hour] = slider.get() / 10.0

            # Save behavioral rules
            rules_text = self.rules_text.get('1.0', tk.END).strip()
            if rules_text:
                self.user_profile.behavioral_rules = [
                    rule.strip() for rule in rules_text.split('\n')
                    if rule.strip()
                ]
            else:
                self.user_profile.behavioral_rules = []

            # Save email
            email = self.email_entry.get().strip()
            if email:
                self.user_profile.email = email

            # Save to file
            self.save_profile()

            messagebox.showinfo("Success", "✅ Settings saved successfully!")

        except Exception as e:
            messagebox.showerror("Error", f"❌ Failed to save settings:\n{str(e)}")
