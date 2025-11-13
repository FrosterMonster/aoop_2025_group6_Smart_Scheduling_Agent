#!/usr/bin/env python3
"""Test script to verify tkinter installation"""

import sys

def test_tkinter():
    """Test tkinter installation"""
    print("=" * 60)
    print("TKINTER INSTALLATION TEST")
    print("=" * 60)
    print(f"\nPython version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    print(f"Platform: {sys.platform}")

    try:
        import tkinter
        print("\n✓ tkinter module found")
        print(f"  Tkinter version: {tkinter.TkVersion}")
        print(f"  Tcl version: {tkinter.TclVersion}")

        # Try creating a window
        try:
            print("\n[Testing window creation...]")
            root = tkinter.Tk()
            root.withdraw()  # Don't show window
            print("✓ tkinter window creation successful")
            root.destroy()
        except Exception as e:
            print(f"✗ Window creation failed: {e}")
            return False

        print("\n" + "=" * 60)
        print("✓✓✓ ALL TESTS PASSED")
        print("=" * 60)
        print("\nTkinter is properly installed!")
        print("You can now run the AI Schedule Agent application.")
        return True

    except ImportError as e:
        print(f"\n✗✗✗ TKINTER NOT FOUND")
        print(f"Error: {e}")
        print("\n" + "=" * 60)
        print("INSTALLATION INSTRUCTIONS")
        print("=" * 60)

        if sys.platform.startswith('linux'):
            print("\n📦 Linux (Ubuntu/Debian):")
            print("  sudo apt-get update")
            print("  sudo apt-get install python3-tk")
            print("\n📦 Linux (Fedora/RHEL):")
            print("  sudo dnf install python3-tkinter")
            print("\n📦 Linux (Arch):")
            print("  sudo pacman -S tk")

        elif sys.platform == 'darwin':
            print("\n📦 macOS:")
            print("  brew install python-tk")

        elif sys.platform == 'win32':
            print("\n📦 Windows:")
            print("  1. Go to 'Add or Remove Programs'")
            print("  2. Find Python 3.x")
            print("  3. Click 'Modify'")
            print("  4. Ensure 'tcl/tk and IDLE' is checked")
            print("  5. Click 'Next' → 'Install'")

        print("\n" + "=" * 60)
        print("After installation, run this test again:")
        print("  python test_tkinter.py")
        print("=" * 60)

        return False

if __name__ == "__main__":
    success = test_tkinter()
    sys.exit(0 if success else 1)
