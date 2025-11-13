#!/usr/bin/env python3
"""Test script to verify LLM form filling works correctly

This script tests the complete flow:
1. User input (natural language)
2. LLM processing (with improved prompts)
3. NLP processor conversion
4. Form field population

Run this to verify the LLM improvements work as expected.
"""

import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ai_schedule_agent.core.nlp_processor import NLPProcessor
from ai_schedule_agent.config.manager import ConfigManager
from ai_schedule_agent.utils.logging import logger


def test_llm_form_filling():
    """Test LLM form filling with various inputs"""

    print("=" * 80)
    print(" LLM FORM FILLING TEST")
    print("=" * 80)
    print()

    # Initialize NLP processor with LLM
    config = ConfigManager()

    # Check if LLM is configured
    provider = config.get_llm_provider()
    api_key = config.get_api_key(provider)

    if not api_key:
        print("❌ ERROR: No LLM API key configured!")
        print()
        print("Please configure your API key in .env:")
        print("  - For Claude: ANTHROPIC_API_KEY=sk-ant-...")
        print("  - For OpenAI: OPENAI_API_KEY=sk-...")
        print("  - For Gemini: GEMINI_API_KEY=...")
        print()
        print("Then set LLM_PROVIDER=claude|openai|gemini")
        return False

    print(f"✓ LLM Provider: {provider}")
    print(f"✓ API Key configured: {api_key[:20]}...")
    print()

    # Create NLP processor with LLM enabled
    nlp = NLPProcessor(use_llm=True)

    if not nlp.use_llm:
        print("❌ ERROR: LLM not available! Falling back to rule-based NLP.")
        return False

    print("✓ LLM mode enabled")
    print()

    # Test cases
    test_cases = [
        {
            "input": "Schedule team meeting tomorrow at 2pm",
            "expected": {
                "has_title": True,
                "has_datetime": True,
                "has_duration": True,
                "title_keywords": ["team", "meeting"]
            }
        },
        {
            "input": "Coffee with John today at 3pm for 30 minutes",
            "expected": {
                "has_title": True,
                "has_datetime": True,
                "has_duration": True,
                "duration_value": 30,
                "title_keywords": ["coffee", "john"]
            }
        },
        {
            "input": "Meeting next Monday at 10am",
            "expected": {
                "has_title": True,
                "has_datetime": True,
                "has_duration": True,
                "title_keywords": ["meeting"]
            }
        },
        {
            "input": "Call with client tomorrow 9am for 1 hour",
            "expected": {
                "has_title": True,
                "has_datetime": True,
                "has_duration": True,
                "duration_value": 60,
                "title_keywords": ["call", "client"]
            }
        }
    ]

    passed = 0
    failed = 0

    for i, test in enumerate(test_cases, 1):
        print(f"Test Case {i}: {test['input']}")
        print("-" * 80)

        try:
            # Process with LLM
            result = nlp.parse_scheduling_request(test['input'])

            # Check action
            if result.get('action') != 'create':
                print(f"  ⚠️  Warning: Expected action 'create', got '{result.get('action')}'")

            # Check title
            title = result.get('title')
            if test['expected']['has_title']:
                if title:
                    print(f"  ✓ Title: {title}")

                    # Check keywords
                    if 'title_keywords' in test['expected']:
                        title_lower = title.lower()
                        missing_keywords = [kw for kw in test['expected']['title_keywords']
                                          if kw.lower() not in title_lower]
                        if missing_keywords:
                            print(f"    ⚠️  Missing keywords: {missing_keywords}")
                else:
                    print(f"  ✗ Title: MISSING!")
                    failed += 1
                    continue

            # Check datetime
            dt = result.get('datetime')
            if test['expected']['has_datetime']:
                if dt:
                    print(f"  ✓ DateTime: {dt.strftime('%Y-%m-%d %H:%M')}")

                    # Verify it's in the future
                    if dt < datetime.now():
                        print(f"    ⚠️  Warning: DateTime is in the past!")
                else:
                    print(f"  ✗ DateTime: MISSING!")
                    failed += 1
                    continue

            # Check duration
            duration = result.get('duration')
            if test['expected']['has_duration']:
                if duration:
                    print(f"  ✓ Duration: {duration} minutes")

                    # Check specific duration value if specified
                    if 'duration_value' in test['expected']:
                        expected_duration = test['expected']['duration_value']
                        if duration == expected_duration:
                            print(f"    ✓ Matches expected: {expected_duration} minutes")
                        else:
                            print(f"    ⚠️  Expected {expected_duration} minutes, got {duration}")
                else:
                    print(f"  ✗ Duration: MISSING!")
                    failed += 1
                    continue

            # Check location
            location = result.get('location', '')
            if location:
                print(f"  ✓ Location: {location}")

            # Check participants
            participants = result.get('participants', [])
            if participants:
                print(f"  ✓ Participants: {', '.join(participants)}")

            # Check LLM response
            llm_response = result.get('llm_response', '')
            if llm_response:
                print(f"  ✓ LLM Response: {llm_response[:60]}...")

            print(f"  ✓ PASSED")
            passed += 1

        except Exception as e:
            print(f"  ✗ FAILED: {e}")
            logger.error(f"Test failed: {e}", exc_info=True)
            failed += 1

        print()

    # Summary
    print("=" * 80)
    print(" TEST SUMMARY")
    print("=" * 80)
    print(f"Total: {passed + failed}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print()

    if failed == 0:
        print("✅ ALL TESTS PASSED!")
        print("LLM form filling is working correctly.")
        return True
    else:
        print(f"❌ {failed} test(s) failed")
        print("Please check the LLM configuration and prompts.")
        return False


if __name__ == '__main__':
    success = test_llm_form_filling()
    sys.exit(0 if success else 1)
