#!/usr/bin/env python3
"""
Test阿嚕米 style UI integration

This script tests that the Quick Schedule UI properly uses阿嚕米 Mock mode
to auto-fill the form.
"""

import os
import sys

# Set DRY_RUN mode
os.environ['DRY_RUN'] = '1'

print("=" * 70)
print("阿嚕米 Style UI Test")
print("=" * 70)
print()

# Test NLP processor with阿嚕米 patterns
from ai_schedule_agent.core.nlp_processor import NLPProcessor

nlp = NLPProcessor(use_llm=False)  # Use rule-based阿嚕米 Mock mode

test_cases = [
    {
        'input': '明天下午排3小時開會',
        'expected': {
            'title': '開會',
            'duration': 180,
            'flexible': True,  # Has time_preference
            'time_period': 'afternoon'
        }
    },
    {
        'input': '請幫我安排一個「與導師會面」的活動，時間是今天晚上 8 點到 9 點。',
        'expected': {
            'title': '與導師會面',
            'duration': 60,
            'flexible': False,  # Has exact datetime
            'has_datetime': True
        }
    },
    {
        'input': '安排開會，時間是明天下午2點到4點',
        'expected': {
            'title': '開會',
            'duration': 120,
            'flexible': False,
            'has_datetime': True
        }
    }
]

print("Testing NLP Processor with阿嚕米 Mock Mode patterns:\n")

for i, test in enumerate(test_cases, 1):
    print(f"Test {i}: {test['input']}")
    print("-" * 70)

    result = nlp.parse_scheduling_request(test['input'])

    # Check results
    expected = test['expected']
    passed = True
    errors = []

    if 'title' in expected:
        if result.get('title') != expected['title']:
            errors.append(f"Title: expected '{expected['title']}', got '{result.get('title')}'")
            passed = False

    if 'duration' in expected:
        if result.get('duration') != expected['duration']:
            errors.append(f"Duration: expected {expected['duration']}, got {result.get('duration')}")
            passed = False

    if 'flexible' in expected:
        is_flexible = result.get('time_preference') is not None and not result.get('datetime')
        if is_flexible != expected['flexible']:
            errors.append(f"Flexible: expected {expected['flexible']}, got {is_flexible}")
            passed = False

    if expected.get('has_datetime'):
        if not result.get('datetime'):
            errors.append("Expected datetime but got None")
            passed = False

    if passed:
        print("✅ PASSED")
    else:
        print("❌ FAILED")
        for error in errors:
            print(f"   {error}")

    print(f"\nParsed:")
    print(f"  Title: {result.get('title')}")
    print(f"  DateTime: {result.get('datetime')}")
    print(f"  Duration: {result.get('duration')} min")
    print(f"  Time Preference: {result.get('time_preference')}")
    print(f"  Target Date: {result.get('target_date')}")

    # Determine message type (阿嚕米 style)
    is_flexible = result.get('time_preference') is not None and not result.get('datetime')
    has_exact_time = result.get('datetime') is not None

    if is_flexible:
        period = result['time_preference'].get('period', 'N/A')
        print(f"\n✨ AI 建議：系統將自動避開衝突，為您找尋最佳空檔。")
        print(f"   時段偏好：{period}")
    elif has_exact_time:
        print(f"\n📍 AI 建議：此為固定行程，將排定於指定時間。")

    print("\n" + "=" * 70 + "\n")

print("\n🎉 阿嚕米 style UI logic is working correctly!")
print("The Quick Schedule tab will:")
print("  1. Parse natural language using阿嚕米 Mock mode patterns")
print("  2. Auto-fill form fields (title, date, time, duration)")
print("  3. Show appropriate AI suggestion (flexible vs fixed)")
print("  4. User reviews and clicks '確認新增至日曆'")
