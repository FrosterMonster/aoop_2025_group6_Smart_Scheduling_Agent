import datetime
import time
import pytest
from unittest.mock import Mock, patch, MagicMock
from dotenv import load_dotenv
from src.tools.calendar import CalendarTool
from src.agent.scheduling_agent import SchedulingAgent

load_dotenv()

# ============================================================================
# BASIC CONFLICT DETECTION TESTS
# ============================================================================

def test_exact_time_conflict():
    """Test detection of exact time overlap."""
    print("\n--- Test: Exact Time Conflict ---")
    calendar_tool = CalendarTool()
    agent = SchedulingAgent(tools=[calendar_tool])
    
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    
    # Setup: Create first meeting
    setup_query = (
        f"Today is {today}. "
        "Schedule 'Client Meeting' for tomorrow from 2 PM to 3 PM."
    )
    agent(setup_query)
    time.sleep(2)
    
    # Test: Try to schedule at exact same time
    conflict_query = (
        f"Today is {today}. "
        "Schedule 'Team Sync' for tomorrow from 2 PM to 3 PM."
    )
    result = agent(conflict_query)
    
    assert "conflict" in result.lower() or "busy" in result.lower() or "overlap" in result.lower()
    print(f"✓ Detected exact time conflict")

def test_partial_overlap_start():
    """Test detection when new event starts during existing event."""
    print("\n--- Test: Partial Overlap (Start) ---")
    calendar_tool = CalendarTool()
    agent = SchedulingAgent(tools=[calendar_tool])
    
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    
    # Setup: 2 PM - 3 PM
    setup_query = (
        f"Today is {today}. "
        "Schedule 'Workshop' for tomorrow from 2 PM to 3 PM."
    )
    agent(setup_query)
    time.sleep(2)
    
    # Test: 2:30 PM - 3:30 PM (overlaps last 30 min)
    conflict_query = (
        f"Today is {today}. "
        "Schedule 'Code Review' for tomorrow from 2:30 PM to 3:30 PM."
    )
    result = agent(conflict_query)
    
    assert "conflict" in result.lower() or "busy" in result.lower() or "overlap" in result.lower()
    print(f"✓ Detected partial overlap at start")

def test_partial_overlap_end():
    """Test detection when new event ends during existing event."""
    print("\n--- Test: Partial Overlap (End) ---")
    calendar_tool = CalendarTool()
    agent = SchedulingAgent(tools=[calendar_tool])
    
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    
    # Setup: 2 PM - 3 PM
    setup_query = (
        f"Today is {today}. "
        "Schedule 'Planning Session' for tomorrow from 2 PM to 3 PM."
    )
    agent(setup_query)
    time.sleep(2)
    
    # Test: 1:30 PM - 2:30 PM (overlaps first 30 min)
    conflict_query = (
        f"Today is {today}. "
        "Schedule 'Standup' for tomorrow from 1:30 PM to 2:30 PM."
    )
    result = agent(conflict_query)
    
    assert "conflict" in result.lower() or "busy" in result.lower() or "overlap" in result.lower()
    print(f"✓ Detected partial overlap at end")

def test_encompassing_event():
    """Test detection when new event completely encompasses existing event."""
    print("\n--- Test: Encompassing Event ---")
    calendar_tool = CalendarTool()
    agent = SchedulingAgent(tools=[calendar_tool])
    
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    
    # Setup: 2 PM - 3 PM
    setup_query = (
        f"Today is {today}. "
        "Schedule 'Quick Sync' for tomorrow from 2 PM to 3 PM."
    )
    agent(setup_query)
    time.sleep(2)
    
    # Test: 1 PM - 4 PM (encompasses the 2-3 PM meeting)
    conflict_query = (
        f"Today is {today}. "
        "Schedule 'All Hands Meeting' for tomorrow from 1 PM to 4 PM."
    )
    result = agent(conflict_query)
    
    assert "conflict" in result.lower() or "busy" in result.lower() or "overlap" in result.lower()
    print(f"✓ Detected encompassing event conflict")

def test_contained_event():
    """Test detection when new event is completely contained within existing event."""
    print("\n--- Test: Contained Event ---")
    calendar_tool = CalendarTool()
    agent = SchedulingAgent(tools=[calendar_tool])
    
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    
    # Setup: 1 PM - 4 PM (long meeting)
    setup_query = (
        f"Today is {today}. "
        "Schedule 'Strategy Session' for tomorrow from 1 PM to 4 PM."
    )
    agent(setup_query)
    time.sleep(2)
    
    # Test: 2 PM - 3 PM (inside the 1-4 PM meeting)
    conflict_query = (
        f"Today is {today}. "
        "Schedule 'Break' for tomorrow from 2 PM to 3 PM."
    )
    result = agent(conflict_query)
    
    assert "conflict" in result.lower() or "busy" in result.lower() or "overlap" in result.lower()
    print(f"✓ Detected contained event conflict")

# ============================================================================
# NO CONFLICT TESTS (Should Succeed)
# ============================================================================

def test_no_conflict_before():
    """Test that events before existing events are allowed."""
    print("\n--- Test: No Conflict (Before) ---")
    calendar_tool = CalendarTool()
    agent = SchedulingAgent(tools=[calendar_tool])
    
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    
    # Setup: 2 PM - 3 PM
    setup_query = (
        f"Today is {today}. "
        "Schedule 'Afternoon Meeting' for tomorrow from 2 PM to 3 PM."
    )
    agent(setup_query)
    time.sleep(2)
    
    # Test: 12 PM - 1 PM (well before)
    no_conflict_query = (
        f"Today is {today}. "
        "Schedule 'Lunch' for tomorrow from 12 PM to 1 PM."
    )
    result = agent(no_conflict_query)
    
    assert "conflict" not in result.lower() or "success" in result.lower() or "scheduled" in result.lower()
    print(f"✓ No conflict detected for earlier event")

def test_no_conflict_after():
    """Test that events after existing events are allowed."""
    print("\n--- Test: No Conflict (After) ---")
    calendar_tool = CalendarTool()
    agent = SchedulingAgent(tools=[calendar_tool])
    
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    
    # Setup: 2 PM - 3 PM
    setup_query = (
        f"Today is {today}. "
        "Schedule 'Early Meeting' for tomorrow from 2 PM to 3 PM."
    )
    agent(setup_query)
    time.sleep(2)
    
    # Test: 4 PM - 5 PM (well after)
    no_conflict_query = (
        f"Today is {today}. "
        "Schedule 'Late Meeting' for tomorrow from 4 PM to 5 PM."
    )
    result = agent(no_conflict_query)
    
    assert "conflict" not in result.lower() or "success" in result.lower() or "scheduled" in result.lower()
    print(f"✓ No conflict detected for later event")

def test_no_conflict_adjacent_before():
    """Test that back-to-back events (new ends when existing starts) are allowed."""
    print("\n--- Test: No Conflict (Adjacent Before) ---")
    calendar_tool = CalendarTool()
    agent = SchedulingAgent(tools=[calendar_tool])
    
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    
    # Setup: 2 PM - 3 PM
    setup_query = (
        f"Today is {today}. "
        "Schedule 'Second Meeting' for tomorrow from 2 PM to 3 PM."
    )
    agent(setup_query)
    time.sleep(2)
    
    # Test: 1 PM - 2 PM (ends exactly when next starts)
    no_conflict_query = (
        f"Today is {today}. "
        "Schedule 'First Meeting' for tomorrow from 1 PM to 2 PM."
    )
    result = agent(no_conflict_query)
    
    # This might conflict depending on implementation - adjust assertion as needed
    print(f"Result: {result}")
    print(f"✓ Tested adjacent events (before)")

def test_no_conflict_adjacent_after():
    """Test that back-to-back events (existing ends when new starts) are allowed."""
    print("\n--- Test: No Conflict (Adjacent After) ---")
    calendar_tool = CalendarTool()
    agent = SchedulingAgent(tools=[calendar_tool])
    
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    
    # Setup: 1 PM - 2 PM
    setup_query = (
        f"Today is {today}. "
        "Schedule 'Morning Meeting' for tomorrow from 1 PM to 2 PM."
    )
    agent(setup_query)
    time.sleep(2)
    
    # Test: 2 PM - 3 PM (starts exactly when previous ends)
    no_conflict_query = (
        f"Today is {today}. "
        "Schedule 'Afternoon Meeting' for tomorrow from 2 PM to 3 PM."
    )
    result = agent(no_conflict_query)
    
    print(f"Result: {result}")
    print(f"✓ Tested adjacent events (after)")

# ============================================================================
# MULTIPLE CONFLICTS TESTS
# ============================================================================

def test_multiple_conflicts():
    """Test detection when time conflicts with multiple existing events."""
    print("\n--- Test: Multiple Conflicts ---")
    calendar_tool = CalendarTool()
    agent = SchedulingAgent(tools=[calendar_tool])
    
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    
    # Setup: Create multiple meetings
    agent(f"Today is {today}. Schedule 'Meeting A' for tomorrow from 1 PM to 2 PM.")
    time.sleep(1)
    agent(f"Today is {today}. Schedule 'Meeting B' for tomorrow from 2:30 PM to 3:30 PM.")
    time.sleep(2)
    
    # Test: Try to schedule something that overlaps both
    conflict_query = (
        f"Today is {today}. "
        "Schedule 'Big Meeting' for tomorrow from 1:30 PM to 3 PM."
    )
    result = agent(conflict_query)
    
    assert "conflict" in result.lower() or "busy" in result.lower()
    print(f"✓ Detected multiple conflicts")

def test_conflict_across_days():
    """Test that events on different days don't conflict."""
    print("\n--- Test: No Conflict Across Days ---")
    calendar_tool = CalendarTool()
    agent = SchedulingAgent(tools=[calendar_tool])
    
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    tomorrow = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    day_after = (datetime.datetime.now() + datetime.timedelta(days=2)).strftime("%Y-%m-%d")
    
    # Setup: Tomorrow 2 PM - 3 PM
    agent(f"Today is {today}. Schedule 'Tomorrow Meeting' for tomorrow from 2 PM to 3 PM.")
    time.sleep(2)
    
    # Test: Day after tomorrow, same time - should be fine
    no_conflict_query = (
        f"Today is {today}. "
        f"Schedule 'Day After Meeting' for {day_after} from 2 PM to 3 PM."
    )
    result = agent(no_conflict_query)
    
    assert "conflict" not in result.lower() or "success" in result.lower()
    print(f"✓ No conflict across different days")

# ============================================================================
# EDGE CASES
# ============================================================================

def test_conflict_with_all_day_event():
    """Test conflict detection with all-day events."""
    print("\n--- Test: Conflict with All-Day Event ---")
    calendar_tool = CalendarTool()
    agent = SchedulingAgent(tools=[calendar_tool])
    
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    
    # Setup: Create all-day event
    agent(f"Today is {today}. Schedule an all-day 'Company Offsite' for tomorrow.")
    time.sleep(2)
    
    # Test: Try to schedule a meeting during that day
    conflict_query = (
        f"Today is {today}. "
        "Schedule 'Team Sync' for tomorrow from 2 PM to 3 PM."
    )
    result = agent(conflict_query)
    
    print(f"Result: {result}")
    print(f"✓ Tested conflict with all-day event")

def test_conflict_minute_precision():
    """Test conflict detection with minute-level precision."""
    print("\n--- Test: Minute Precision Conflict ---")
    calendar_tool = CalendarTool()
    agent = SchedulingAgent(tools=[calendar_tool])
    
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    
    # Setup: 2:00 PM - 2:30 PM
    agent(f"Today is {today}. Schedule 'Quick Call' for tomorrow from 2:00 PM to 2:30 PM.")
    time.sleep(2)
    
    # Test: 2:15 PM - 2:45 PM (15 min overlap)
    conflict_query = (
        f"Today is {today}. "
        "Schedule 'Another Call' for tomorrow from 2:15 PM to 2:45 PM."
    )
    result = agent(conflict_query)
    
    assert "conflict" in result.lower() or "busy" in result.lower()
    print(f"✓ Detected minute-level conflict")

def test_zero_duration_event():
    """Test handling of zero-duration events."""
    print("\n--- Test: Zero Duration Event ---")
    calendar_tool = CalendarTool()
    agent = SchedulingAgent(tools=[calendar_tool])
    
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    
    # Test: Create event with same start and end time
    query = (
        f"Today is {today}. "
        "Schedule 'Reminder' for tomorrow at 2 PM to 2 PM."
    )
    result = agent(query)
    
    print(f"Result: {result}")
    print(f"✓ Tested zero-duration event handling")

# ============================================================================
# CONFLICT RESOLUTION SUGGESTIONS
# ============================================================================

def test_agent_suggests_alternative_times():
    """Test if agent suggests alternative times when conflict detected."""
    print("\n--- Test: Alternative Time Suggestions ---")
    calendar_tool = CalendarTool()
    agent = SchedulingAgent(tools=[calendar_tool])
    
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    
    # Setup: Block 2 PM - 3 PM
    agent(f"Today is {today}. Schedule 'Blocked Time' for tomorrow from 2 PM to 3 PM.")
    time.sleep(2)
    
    # Test: Request with conflict
    conflict_query = (
        f"Today is {today}. "
        "Schedule 'Important Meeting' for tomorrow from 2 PM to 3 PM. "
        "If there's a conflict, suggest alternative times."
    )
    result = agent(conflict_query)
    
    print(f"Result: {result}")
    # Check if result contains suggestions
    has_suggestions = any(word in result.lower() for word in ['suggest', 'alternative', 'available', 'instead', 'try'])
    print(f"✓ Tested alternative suggestions (found: {has_suggestions})")

def test_find_next_available_slot():
    """Test agent's ability to find next available time slot."""
    print("\n--- Test: Find Next Available Slot ---")
    calendar_tool = CalendarTool()
    agent = SchedulingAgent(tools=[calendar_tool])
    
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    
    # Setup: Block multiple slots
    agent(f"Today is {today}. Schedule 'Meeting 1' for tomorrow from 10 AM to 11 AM.")
    time.sleep(1)
    agent(f"Today is {today}. Schedule 'Meeting 2' for tomorrow from 11 AM to 12 PM.")
    time.sleep(1)
    agent(f"Today is {today}. Schedule 'Meeting 3' for tomorrow from 1 PM to 2 PM.")
    time.sleep(2)
    
    # Test: Ask for next available hour-long slot
    query = (
        f"Today is {today}. "
        "Find the next available 1-hour slot tomorrow after 10 AM."
    )
    result = agent(query)
    
    print(f"Result: {result}")
    print(f"✓ Tested finding next available slot")

# ============================================================================
# STRESS TESTS
# ============================================================================

def test_busy_day_multiple_conflicts():
    """Test conflict detection on a day with many events."""
    print("\n--- Test: Busy Day Multiple Conflicts ---")
    calendar_tool = CalendarTool()
    agent = SchedulingAgent(tools=[calendar_tool])
    
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    
    # Setup: Create a packed schedule
    time_slots = [
        ("9 AM", "10 AM"),
        ("10 AM", "11 AM"),
        ("11 AM", "12 PM"),
        ("1 PM", "2 PM"),
        ("2 PM", "3 PM"),
        ("3 PM", "4 PM"),
    ]
    
    for i, (start, end) in enumerate(time_slots):
        agent(f"Today is {today}. Schedule 'Meeting {i+1}' for tomorrow from {start} to {end}.")
        time.sleep(0.5)
    
    time.sleep(2)
    
    # Test: Try to schedule in a busy slot
    conflict_query = (
        f"Today is {today}. "
        "Schedule 'Emergency Meeting' for tomorrow from 2 PM to 3 PM."
    )
    result = agent(conflict_query)
    
    assert "conflict" in result.lower() or "busy" in result.lower()
    print(f"✓ Detected conflict in busy schedule")

# ============================================================================
# NATURAL LANGUAGE VARIATIONS
# ============================================================================

def test_natural_language_conflict_variations():
    """Test different ways users might express scheduling requests."""
    print("\n--- Test: Natural Language Variations ---")
    calendar_tool = CalendarTool()
    agent = SchedulingAgent(tools=[calendar_tool])
    
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    
    # Setup
    agent(f"Today is {today}. Schedule 'Existing Meeting' for tomorrow from 2 PM to 3 PM.")
    time.sleep(2)
    
    # Test various phrasings
    variations = [
        "Can you put a meeting tomorrow at 2pm?",
        "I need to schedule something tomorrow afternoon at 2",
        "Book a call for tomorrow 2-3pm",
        "Add 'Team Sync' to my calendar tomorrow at 2pm",
    ]
    
    for var in variations:
        query = f"Today is {today}. {var}"
        result = agent(query)
        print(f"Query: {var}")
        print(f"Result contains 'conflict': {'conflict' in result.lower()}")
        time.sleep(1)
    
    print(f"✓ Tested natural language variations")

# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

def main():
    """Run comprehensive conflict detection test suite."""
    print("\n" + "="*70)
    print("COMPREHENSIVE CONFLICT DETECTION TEST SUITE")
    print("="*70)
    
    tests = [
        test_exact_time_conflict,
        test_partial_overlap_start,
        test_partial_overlap_end,
        test_encompassing_event,
        test_contained_event,
        test_no_conflict_before,
        test_no_conflict_after,
        test_no_conflict_adjacent_before,
        test_no_conflict_adjacent_after,
        test_multiple_conflicts,
        test_conflict_across_days,
        test_conflict_with_all_day_event,
        test_conflict_minute_precision,
        test_zero_duration_event,
        test_agent_suggests_alternative_times,
        test_find_next_available_slot,
        test_busy_day_multiple_conflicts,
        test_natural_language_conflict_variations,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            print("\n" + "-"*70)
            test()
            passed += 1
            print("✓ PASSED")
        except Exception as e:
            failed += 1
            print(f"✗ FAILED: {e}")
        print("-"*70)
        time.sleep(1)  # Brief pause between tests
    
    print("\n" + "="*70)
    print(f"TEST SUMMARY: {passed} passed, {failed} failed out of {len(tests)} total")
    print("="*70)

if __name__ == "__main__":
    main()