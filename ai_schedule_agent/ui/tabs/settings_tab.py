"""Settings tab for user preferences configuration"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox


class SettingsTab:
    """Settings tab UI component"""

    def __init__(self, parent, user_profile, save_profile_callback):
        self.parent = parent
        self.user_profile = user_profile
        self.save_profile = save_profile_callback

        self.working_hours_entries = {}
        self.energy_sliders = {}
        self.rules_text = None
        self.email_entry = None

        self.setup_ui()

    def setup_ui(self):
        """Setup settings tab UI"""

        # Working Hours Section
        ttk.Label(self.parent, text="Working Hours", font=('Arial', 14, 'bold')).pack(pady=10)

        hours_frame = ttk.Frame(self.parent)
        hours_frame.pack(pady=10)

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
        ttk.Separator(self.parent, orient='horizontal').pack(fill='x', pady=20)
        ttk.Label(self.parent, text="Energy Patterns (0-10 scale)", font=('Arial', 14, 'bold')).pack(pady=10)

        energy_frame = ttk.Frame(self.parent)
        energy_frame.pack(pady=10)

        for i in range(6, 22):  # 6 AM to 9 PM
            ttk.Label(energy_frame, text=f"{i:02d}:00").grid(row=i-6, column=0, sticky='e', padx=5)

            slider = ttk.Scale(energy_frame, from_=0, to=10, orient='horizontal', length=200)
            slider.grid(row=i-6, column=1, padx=5, pady=2)

            # Load existing value
            if i in self.user_profile.energy_patterns:
                slider.set(self.user_profile.energy_patterns[i] * 10)

            self.energy_sliders[i] = slider

        # Behavioral Rules Section
        ttk.Separator(self.parent, orient='horizontal').pack(fill='x', pady=20)
        ttk.Label(self.parent, text="Behavioral Rules", font=('Arial', 14, 'bold')).pack(pady=10)

        rules_frame = ttk.Frame(self.parent)
        rules_frame.pack(pady=10)

        ttk.Label(rules_frame, text="Add rules (e.g., 'No meetings before 10 AM'):").pack()

        self.rules_text = scrolledtext.ScrolledText(rules_frame, height=5, width=60)
        self.rules_text.pack(pady=5)

        # Load existing rules
        for rule in self.user_profile.behavioral_rules:
            self.rules_text.insert(tk.END, rule + "\n")

        # Email Settings
        ttk.Separator(self.parent, orient='horizontal').pack(fill='x', pady=20)
        ttk.Label(self.parent, text="Email Settings", font=('Arial', 14, 'bold')).pack(pady=10)

        email_frame = ttk.Frame(self.parent)
        email_frame.pack(pady=10)

        ttk.Label(email_frame, text="Your Email:").grid(row=0, column=0, sticky='e', padx=5, pady=3)
        self.email_entry = ttk.Entry(email_frame, width=30)
        self.email_entry.grid(row=0, column=1, padx=5, pady=3)
        self.email_entry.insert(0, self.user_profile.email)

        # Save button
        ttk.Button(self.parent, text="Save Settings",
                  command=self.save_settings, style='Accent.TButton').pack(pady=20)

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
