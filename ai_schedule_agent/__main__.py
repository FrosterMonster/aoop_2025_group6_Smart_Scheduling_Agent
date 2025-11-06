"""
AI Schedule Agent - Main Entry Point

This module serves as the entry point for the application.
Checks Python version compatibility and launches either the setup wizard or main application.
"""

import sys
import os
import time

# Track startup time for performance monitoring
_startup_start = time.time()

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


def main():
    """Main entry point for the application"""
    # Defer imports until main() is called to speed up startup
    from ai_schedule_agent.config.manager import ConfigManager
    from ai_schedule_agent.ui.setup_wizard import SetupWizard

    # Check for modern UI flag (can be set via environment variable or config)
    use_modern_ui = os.environ.get('USE_MODERN_UI', 'true').lower() == 'true'

    if use_modern_ui:
        from ai_schedule_agent.ui.modern_main_window import ModernSchedulerUI as SchedulerUI
    else:
        from ai_schedule_agent.ui.main_window import SchedulerUI

    _import_end = time.time()
    import_time = (_import_end - _startup_start) * 1000  # Convert to ms

    # Initialize config
    config = ConfigManager()

    # Check if this is first run
    profile_file = config.get_path('user_profile', '.config/user_profile.json')

    _init_end = time.time()
    init_time = (_init_end - _import_end) * 1000  # Convert to ms

    if not os.path.exists(profile_file):
        # Run setup wizard
        print(f"⚡ Startup time: imports={import_time:.0f}ms, init={init_time:.0f}ms, total={(_init_end - _startup_start)*1000:.0f}ms")
        print("First-time setup detected. Launching setup wizard...")
        wizard = SetupWizard()
        wizard.run()
    else:
        # Run main application
        ui_type = "Modern Healthcare UI" if use_modern_ui else "Classic Tabbed UI"
        print(f"⚡ Startup time: imports={import_time:.0f}ms, init={init_time:.0f}ms, total={(_init_end - _startup_start)*1000:.0f}ms")
        print(f"Starting AI Schedule Agent ({ui_type})...")
        app = SchedulerUI()
        app.run()


if __name__ == "__main__":
    main()
