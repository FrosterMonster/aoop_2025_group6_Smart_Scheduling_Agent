"""
Legacy wrapper for backward compatibility

This file serves as a thin wrapper to maintain backward compatibility
with the old monolithic main.py structure.

New code should use: python -m ai_schedule_agent

This wrapper simply imports and runs the modular package.
"""

# Import and run the modular version
from ai_schedule_agent.__main__ import main

if __name__ == "__main__":
    main()
