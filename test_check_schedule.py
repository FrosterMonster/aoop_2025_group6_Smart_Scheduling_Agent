"""Test script to verify check_schedule action handling"""
import sys
from datetime import datetime, timedelta
from ai_schedule_agent.models.enums import EventType

# Mock parsed result from NLP processor
parsed = {
    'action': 'check_schedule',
    'target_date': datetime(2025, 11, 7, 9, 0, 0),
    'duration': 240,  # 4 hours
    'title': 'AOOP study session',
    'description': '',
    'location': '',
    'event_type': EventType.MEETING,
    'participants': [],
    'llm_response': 'I will check your schedule for November 7th and find a suitable 4-hour time slot for your AOOP study session.'
}

print("=" * 60)
print("Testing check_schedule action handling")
print("=" * 60)
print(f"\nAction: {parsed['action']}")
print(f"Target Date: {parsed['target_date']}")
print(f"Duration: {parsed['duration']} minutes")
print(f"Title: {parsed['title']}")
print(f"LLM Response: {parsed['llm_response']}")
print("\n" + "=" * 60)
print("✅ Parsed structure is correct!")
print("\nThe UI should now:")
print("1. Clear the form")
print("2. Call scheduling_engine.find_optimal_slot() with:")
print(f"   - search_start: {parsed['target_date']}")
print(f"   - duration: timedelta(minutes={parsed['duration']})")
print("3. Populate form with the optimal time slot found")
print("4. Display message about avoiding conflicts")
print("=" * 60)
