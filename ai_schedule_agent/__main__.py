"""
AI Schedule Agent - Main Entry Point

This module serves as the entry point for the application.
Checks Python version compatibility and launches either the setup wizard or main application.
"""

import sys
import os

# Check Python version before importing anything else
MIN_PYTHON = (3, 9)
MAX_PYTHON = (3, 12)

if sys.version_info < MIN_PYTHON:
    sys.exit(f"Error: Python {MIN_PYTHON[0]}.{MIN_PYTHON[1]} or higher is required. "
             f"You are using Python {sys.version_info.major}.{sys.version_info.minor}")

if sys.version_info[:2] > MAX_PYTHON:
    print(f"Warning: This application was tested with Python up to {MAX_PYTHON[0]}.{MAX_PYTHON[1]}. "
          f"You are using Python {sys.version_info.major}.{sys.version_info.minor}. "
          f"If you encounter issues, consider using Python {MAX_PYTHON[0]}.{MAX_PYTHON[1]}")

# Now safe to import the application modules
from ai_schedule_agent.config.manager import ConfigManager
from ai_schedule_agent.ui.setup_wizard import SetupWizard
from ai_schedule_agent.ui.main_window import SchedulerUI


def main():
    """Main entry point for the application"""
    # Initialize config
    config = ConfigManager()

    # Check if this is first run
    profile_file = config.get_path('user_profile', '.config/user_profile.json')

    if not os.path.exists(profile_file):
        # Run setup wizard
        print("First-time setup detected. Launching setup wizard...")
        wizard = SetupWizard()
        wizard.run()
    else:
        # Run main application
        print("Starting AI Schedule Agent...")
        app = SchedulerUI()
        app.run()


if __name__ == "__main__":
    main()
