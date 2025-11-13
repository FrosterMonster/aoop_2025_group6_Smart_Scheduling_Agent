"""Setup wizard for first-time users"""

import os
import json
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox

from ai_schedule_agent.config.manager import ConfigManager
from ai_schedule_agent.models.user_profile import UserProfile
from ai_schedule_agent.integrations.google_calendar import CalendarIntegration


class SetupWizard:
    """Initial setup wizard for first-time users"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("AI Schedule Agent - Setup Wizard")
        self.root.geometry("600x700")

        self.config = ConfigManager()
        self.user_profile = UserProfile()
        self.current_step = 0

        self.notebook = None
        self.working_hours_entries = {}
        self.energy_sliders = {}

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
6. Place the file in the .config directory

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
            credentials_file = self.config.get_path('google_credentials', '.config/credentials.json')
            if not os.path.exists(credentials_file):
                messagebox.showerror("Error", f"credentials.json not found at {credentials_file}")
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
        from ai_schedule_agent.ui.main_window import SchedulerUI

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
            profile_file = self.config.get_path('user_profile', '.config/user_profile.json')
            with open(profile_file, 'w') as f:
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
