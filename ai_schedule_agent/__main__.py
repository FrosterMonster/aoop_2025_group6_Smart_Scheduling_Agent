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

    # Check for modern UI flag (can be set via environment variable or config)
    use_modern_ui = os.environ.get('USE_MODERN_UI', 'true').lower() == 'true'

    # Try to import tkinter first to give better error message
    try:
        import tkinter as tk
    except ImportError as e:
        print("\n" + "="*60)
        print("ERROR: Tkinter is not installed!")
        print("="*60)
        print("\nThis application requires Tkinter for the GUI.")
        print("\nTo fix this issue:")
        print("  1. Install Python with Tkinter support")
        print("  2. Recreate the virtual environment")
        print("\nDetailed instructions:")
        print("  - Windows: Reinstall Python and check 'tcl/tk and IDLE'")
        print("  - Linux: sudo apt-get install python3-tk")
        print("  - macOS: brew install python-tk")
        print("\nSee: docs/guides/TKINTER_INSTALLATION.md")
        print("Test: python -m tkinter")
        print("="*60 + "\n")
        sys.exit(1)
    except Exception as e:
        if "init.tcl" in str(e) or "TclError" in str(e):
            print("\n" + "="*60)
            print("ERROR: Tkinter/Tcl is not properly configured!")
            print("="*60)
            print(f"\nError details: {str(e)}")
            print("\n⚠ This is a KNOWN ISSUE with Python 3.13 on Windows!")
            print("\nRECOMMENDED SOLUTION:")
            print("  1. Install Python 3.12.7 from:")
            print("     https://www.python.org/downloads/release/python-3127/")
            print("  2. Remove the old virtual environment:")
            print("     rm -rf venv")
            print("  3. Recreate with Python 3.12:")
            print("     ./venv_setup.sh")
            print("\nALTERNATIVE (if you must use Python 3.13):")
            print("  1. Repair/Reinstall Python 3.13:")
            print("     Settings → Apps → Python → Modify")
            print("     Ensure 'tcl/tk and IDLE' is checked")
            print("  2. Recreate the virtual environment:")
            print("     rm -rf venv")
            print("     ./venv_setup.sh")
            print("\nTest after fix: python -m tkinter")
            print("="*60 + "\n")
            sys.exit(1)

    # Import UI modules after tkinter check
    try:
        from ai_schedule_agent.ui.setup_wizard import SetupWizard
        if use_modern_ui:
            from ai_schedule_agent.ui.modern_main_window import ModernSchedulerUI as SchedulerUI
        else:
            from ai_schedule_agent.ui.main_window import SchedulerUI
    except Exception as e:
        if "init.tcl" in str(e) or "TclError" in str(e) or "tkinter" in str(e).lower():
            print("\n" + "="*60)
            print("ERROR: Failed to initialize GUI components!")
            print("="*60)
            print(f"\nError: {str(e)}")
            print("\n⚠ Python 3.13 has known Tkinter issues on Windows!")
            print("\nPlease install Python 3.12.7 instead:")
            print("  https://www.python.org/downloads/release/python-3127/")
            print("\nThen recreate your virtual environment:")
            print("  rm -rf venv && ./venv_setup.sh")
            print("="*60 + "\n")
            sys.exit(1)
        raise

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
        try:
            wizard = SetupWizard()
            wizard.run()
        except Exception as e:
            if "init.tcl" in str(e) or "TclError" in str(e):
                print("\n" + "="*60)
                print("ERROR: Cannot start setup wizard - Tkinter error!")
                print("="*60)
                print(f"\nError: {str(e)}")
                print("\n⚠ Python 3.13 has Tkinter compatibility issues!")
                print("\nSOLUTION: Use Python 3.12 instead")
                print("  1. Download: https://www.python.org/downloads/release/python-3127/")
                print("  2. Remove old venv: rm -rf venv")
                print("  3. Run setup: ./venv_setup.sh")
                print("="*60 + "\n")
                sys.exit(1)
            raise
    else:
        # Run main application
        ui_type = "Modern Healthcare UI" if use_modern_ui else "Classic Tabbed UI"
        print(f"⚡ Startup time: imports={import_time:.0f}ms, init={init_time:.0f}ms, total={(_init_end - _startup_start)*1000:.0f}ms")
        print(f"Starting AI Schedule Agent ({ui_type})...")
        try:
            app = SchedulerUI()
            app.run()
        except Exception as e:
            if "init.tcl" in str(e) or "TclError" in str(e):
                print("\n" + "="*60)
                print("ERROR: Cannot start application - Tkinter error!")
                print("="*60)
                print(f"\nError: {str(e)}")
                print("\n⚠ Python 3.13 has Tkinter compatibility issues!")
                print("\nSOLUTION: Use Python 3.12 instead")
                print("  1. Download: https://www.python.org/downloads/release/python-3127/")
                print("  2. Remove old venv: rm -rf venv")
                print("  3. Run setup: ./venv_setup.sh")
                print("="*60 + "\n")
                sys.exit(1)
            raise


if __name__ == "__main__":
    main()
