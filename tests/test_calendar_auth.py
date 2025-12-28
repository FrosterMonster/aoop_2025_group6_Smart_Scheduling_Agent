"""Test script to re-authenticate with Google Calendar"""

import os
import sys

# Add project to path
sys.path.insert(0, os.path.dirname(__file__))

from ai_schedule_agent.integrations.google_calendar import CalendarIntegration
from ai_schedule_agent.utils.logging import logger

def test_authentication():
    """Test Google Calendar authentication"""
    print("\n" + "="*60)
    print("Google Calendar Authentication Test")
    print("="*60)

    print("\n[1] Initializing Calendar Integration...")
    calendar = CalendarIntegration()

    print("\n[2] Starting authentication flow...")
    print("    ⚠ A browser window will open for Google OAuth")
    print("    ⚠ Sign in with your Google account")
    print("    ⚠ Grant calendar access permissions")
    print()

    try:
        calendar.authenticate()
        print("\n✓✓✓ Authentication successful!")
        print(f"✓ New token saved to: {calendar.config.get_path('token_file', 'token.pickle')}")

        print("\n[3] Testing calendar access...")
        events = calendar.get_events()
        print(f"✓ Successfully fetched {len(events)} upcoming events")

        if events:
            print("\n[4] Sample events:")
            for i, event in enumerate(events[:3], 1):
                title = event.get('summary', 'No Title')
                start = event.get('start', {}).get('dateTime', event.get('start', {}).get('date', 'No time'))
                print(f"    {i}. {title} - {start}")

        print("\n" + "="*60)
        print("✓✓✓ ALL TESTS PASSED")
        print("="*60)
        print("\nYou can now run your application normally!")
        return True

    except FileNotFoundError as e:
        print(f"\n✗✗✗ ERROR: {e}")
        print("\nPlease ensure credentials.json is in the .config directory")
        return False

    except Exception as e:
        print(f"\n✗✗✗ ERROR: {e}")
        print("\nAuthentication failed. Please check:")
        print("  1. Your credentials.json is valid")
        print("  2. You have internet connection")
        print("  3. The Google Cloud project has Calendar API enabled")
        return False

if __name__ == "__main__":
    success = test_authentication()
    sys.exit(0 if success else 1)
