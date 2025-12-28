"""Test script to verify UI form population handles time_preference correctly

This script tests the three-way logic flow:
1. Explicit time (datetime set)
2. Time period (target_date + time_preference)
3. No time info (fallback to any optimal slot)
"""
import os
os.environ['DRY_RUN'] = '1'

from ai_schedule_agent.core.nlp_processor import NLPProcessor
from datetime import date, datetime

# Initialize NLP processor
nlp = NLPProcessor(use_llm=False)

print("=" * 70)
print("UI Form Population Test - Time Preference Handling")
print("=" * 70)

test_cases = [
    {
        'input': '明天下午排3小時開會',
        'expected_case': 'Case 2: Time Period',
        'expected_fields': ['target_date', 'time_preference', 'duration', 'title'],
        'should_not_have': ['datetime']
    },
    {
        'input': '明天下午2點開會',
        'expected_case': 'Case 1: Explicit Time',
        'expected_fields': ['datetime', 'title'],
        'should_not_have': []
    },
    {
        'input': '明天上午10點到12點討論專案',
        'expected_case': 'Case 1: Explicit Time Range',
        'expected_fields': ['datetime', 'end_datetime', 'title'],
        'should_not_have': []
    },
    {
        'input': '今天晚上開會',
        'expected_case': 'Case 2: Time Period (Evening)',
        'expected_fields': ['target_date', 'time_preference', 'title'],
        'should_not_have': ['datetime']
    },
]

for i, test in enumerate(test_cases, 1):
    print(f"\n{'='*70}")
    print(f"Test {i}: {test['expected_case']}")
    print(f"{'='*70}")
    print(f"Input: {test['input']}")

    result = nlp.parse_scheduling_request(test['input'])

    print(f"\nExtracted Fields:")
    print(f"  Title: {result.get('title')}")
    print(f"  Datetime: {result.get('datetime')}")
    print(f"  End Datetime: {result.get('end_datetime')}")
    print(f"  Target Date: {result.get('target_date')}")
    print(f"  Time Preference: {result.get('time_preference')}")
    print(f"  Duration: {result.get('duration')} minutes" if result.get('duration') else "  Duration: Not set")

    # Verify expected fields
    print(f"\n✓ Verification:")
    all_good = True

    for field in test['expected_fields']:
        if result.get(field) is not None:
            print(f"  ✓ {field}: Present")
        else:
            print(f"  ✗ {field}: MISSING (expected!)")
            all_good = False

    for field in test['should_not_have']:
        if result.get(field) is None:
            print(f"  ✓ {field}: Correctly absent")
        else:
            print(f"  ✗ {field}: PRESENT (should be absent!)")
            all_good = False

    # Determine which UI case would be used
    print(f"\n📋 UI Form Population Logic:")
    if result.get('datetime'):
        print(f"  → Case 1: Use exact time from 'datetime'")
        print(f"     Time: {result['datetime'].strftime('%Y-%m-%d %H:%M')}")
    elif result.get('target_date') and result.get('time_preference'):
        print(f"  → Case 2: Find optimal slot within time preference")
        tp = result['time_preference']
        print(f"     Date: {result['target_date']}")
        print(f"     Period: {tp.get('period', 'N/A')}")
        print(f"     Window: {tp.get('start_hour', 'N/A')}:00 - {tp.get('end_hour', 'N/A')}:00")
        print(f"     Duration: {result.get('duration', 'default')} minutes")
        print(f"     → Will call: find_optimal_slot(event, search_start={result['target_date']} {tp.get('start_hour', 9)}:00, search_days=1)")
    else:
        print(f"  → Case 3: Find any optimal slot (no constraints)")
        print(f"     → Will call: find_optimal_slot(event)")

    if all_good:
        print(f"\n✅ Test PASSED")
    else:
        print(f"\n❌ Test FAILED")

print("\n" + "=" * 70)
print("Test Summary")
print("=" * 70)
print("\nIf all tests passed, the UI form population logic will:")
print("1. Use exact times when user specifies them ('明天2點')")
print("2. Find optimal slots within time windows when user gives periods ('明天下午')")
print("3. Find any optimal slot when no time info is given")
print("\nThis ensures intelligent scheduling respects user intent while")
print("leveraging the scheduling engine's sophisticated slot-finding logic.")
print("=" * 70)
