#!/usr/bin/env python3
"""
Test script for 阿嚕米 Mock Mode integration

This script tests that the Chinese pattern extraction in nlp_processor.py
correctly uses 阿嚕米_archived's Mock mode logic for form filling.
"""

import os
import sys

# Set DRY_RUN mode
os.environ['DRY_RUN'] = '1'

from ai_schedule_agent.core.nlp_processor import NLPProcessor
from ai_schedule_agent.utils.logging import logger

# Test cases from 阿嚕米_archived
TEST_CASES = [
    {
        'name': '阿嚕米 Case 1: Quoted title with time range',
        'input': '請幫我安排一個「與導師會面」的活動，時間是今天晚上 8 點到 9 點。',
        'expected': {
            'title': '與導師會面',
            'has_datetime': True,
            'has_duration': True
        }
    },
    {
        'name': '阿嚕米 Case 2: Time range with 到',
        'input': '安排開會，時間是明天下午2點到4點',
        'expected': {
            'title': '開會',
            'has_datetime': True,
            'has_duration': True,
            'duration_mins': 120
        }
    },
    {
        'name': '阿嚕米 Case 3: Single time with implicit duration',
        'input': '明天下午3點排開會',
        'expected': {
            'title': '開會',
            'has_datetime': True,
            'duration_mins': 60  # Default 1 hour
        }
    },
    {
        'name': 'ASA Enhancement: Duration + Title pattern',
        'input': '明天下午排3小時開會',
        'expected': {
            'title': '開會',
            'duration_mins': 180,
            'has_target_date': True,
            'has_time_preference': True
        }
    },
    {
        'name': 'ASA Enhancement: Action keyword without quotes',
        'input': '安排討論會議',
        'expected': {
            'title': '討論會議',
        }
    }
]


def test_arumi_mock_integration():
    """Test 阿嚕米 Mock mode integration"""
    print("=" * 70)
    print("阿嚕米 Mock Mode Integration Test")
    print("=" * 70)
    print()

    # Initialize NLP processor with rule-based mode (no LLM)
    nlp = NLPProcessor(use_llm=False)

    passed = 0
    failed = 0

    for i, test_case in enumerate(TEST_CASES, 1):
        print(f"\nTest {i}: {test_case['name']}")
        print("-" * 70)
        print(f"Input: {test_case['input']}")

        try:
            # Parse using rule-based NLP (阿嚕米 Mock mode patterns)
            result = nlp.parse_scheduling_request(test_case['input'])

            # Validate expected fields
            expected = test_case['expected']
            errors = []

            # Check title
            if 'title' in expected:
                actual_title = result.get('title', '')
                expected_title = expected['title']
                if actual_title != expected_title:
                    errors.append(f"Title mismatch: expected '{expected_title}', got '{actual_title}'")

            # Check datetime presence
            if expected.get('has_datetime'):
                if not result.get('datetime'):
                    errors.append("Expected datetime but got None")

            # Check duration
            if 'duration_mins' in expected:
                actual_duration = result.get('duration')
                expected_duration = expected['duration_mins']
                if actual_duration != expected_duration:
                    errors.append(f"Duration mismatch: expected {expected_duration}min, got {actual_duration}min")

            if expected.get('has_duration'):
                if not result.get('duration'):
                    errors.append("Expected duration but got None")

            # Check target_date and time_preference (for time period scheduling)
            if expected.get('has_target_date'):
                if not result.get('target_date'):
                    errors.append("Expected target_date but got None")

            if expected.get('has_time_preference'):
                if not result.get('time_preference'):
                    errors.append("Expected time_preference but got None")

            # Print results
            if errors:
                print("❌ FAILED")
                for error in errors:
                    print(f"   {error}")
                failed += 1
            else:
                print("✅ PASSED")
                passed += 1

            # Print extracted fields
            print(f"\nExtracted:")
            print(f"  Title: {result.get('title')}")
            print(f"  Datetime: {result.get('datetime')}")
            print(f"  End Datetime: {result.get('end_datetime')}")
            print(f"  Duration: {result.get('duration')} minutes" if result.get('duration') else "  Duration: None")
            print(f"  Target Date: {result.get('target_date')}")
            print(f"  Time Preference: {result.get('time_preference')}")

        except Exception as e:
            print(f"❌ EXCEPTION: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    # Summary
    print()
    print("=" * 70)
    print("Test Summary")
    print("=" * 70)
    print(f"Passed: {passed}/{len(TEST_CASES)}")
    print(f"Failed: {failed}/{len(TEST_CASES)}")
    print()

    if failed == 0:
        print("🎉 All tests passed! 阿嚕米 Mock mode is working correctly!")
        return 0
    else:
        print(f"⚠️  {failed} test(s) failed")
        return 1


if __name__ == '__main__':
    sys.exit(test_arumi_mock_integration())
