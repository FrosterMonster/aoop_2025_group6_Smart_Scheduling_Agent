"""Test script to verify Gemini safety filter and shortened prompt fixes"""
import os
import sys
from pathlib import Path

# Enable dry run mode
os.environ['DRY_RUN'] = '1'

# Check .env exists
env_file = Path('.env')
if not env_file.exists():
    print("❌ ERROR: .env file not found!")
    print("Please copy .env.template to .env and configure GEMINI_API_KEY")
    sys.exit(1)

# Load environment
from dotenv import load_dotenv
load_dotenv()

# Verify Gemini configuration
gemini_api_key = os.getenv('GEMINI_API_KEY')
if not gemini_api_key or gemini_api_key == 'your_gemini_api_key_here':
    print("❌ ERROR: GEMINI_API_KEY not configured!")
    sys.exit(1)

# Set Gemini as provider
os.environ['LLM_PROVIDER'] = 'gemini'

from ai_schedule_agent.core.nlp_processor import NLPProcessor

print("=" * 80)
print("Gemini Safety Filter & Shortened Prompt Test")
print("=" * 80)
print("\nTesting fixes:")
print("  1. Safety settings to prevent RECITATION false positives")
print("  2. Shortened prompt (from ~200 lines to ~40 lines)")
print("  3. Proper error handling for finish_reason=4")
print("=" * 80)

# Initialize NLP processor
print("\n🔧 Initializing NLPProcessor with Gemini...")
nlp = NLPProcessor(use_llm=True)

# Test input that previously triggered RECITATION error
test_input = "明天下午排3小時開會"

print(f"\n📝 Test Input: {test_input}")
print("-" * 80)

try:
    print("🚀 Processing...")
    result = nlp.parse_scheduling_request(test_input)

    print("\n✅ SUCCESS! No RECITATION error")
    print("\n📋 Result:")
    print(f"  Action: {result.get('action')}")
    print(f"  Title: {result.get('title')}")
    print(f"  Datetime: {result.get('datetime')}")
    print(f"  Duration: {result.get('duration')} minutes" if result.get('duration') else "  Duration: Not set")
    print(f"  Target Date: {result.get('target_date')}")

    # Verification
    print("\n🔍 Verification:")
    title = result.get('title', '')

    # Check 1: Should have a title
    if title:
        print(f"  ✅ Title extracted: '{title}'")
    else:
        print(f"  ❌ No title extracted")

    # Check 2: Title should not have English translations
    if '(' in title or ')' in title:
        print(f"  ❌ Title has parentheses: '{title}'")
    else:
        print(f"  ✅ Title is clean (no parentheses)")

    # Check 3: Should have time info
    if result.get('datetime') or result.get('target_date'):
        print(f"  ✅ Time information present")
    else:
        print(f"  ⚠️  No time information")

    # Check 4: Should have duration
    if result.get('duration'):
        expected_duration = 180  # 3 hours
        actual_duration = result.get('duration')
        if actual_duration == expected_duration:
            print(f"  ✅ Duration correct: {actual_duration} minutes")
        else:
            print(f"  ⚠️  Duration mismatch: expected {expected_duration}, got {actual_duration}")
    else:
        print(f"  ⚠️  No duration extracted")

except Exception as e:
    print(f"\n❌ ERROR: {type(e).__name__}: {e}")
    print("\nIf you see RECITATION error, the safety filter fix didn't work.")
    print("Check the application logs for more details.")
    sys.exit(1)

print("\n" + "=" * 80)
print("Test Complete!")
print("=" * 80)
print("\n💡 Next steps:")
print("  1. Check logs at .config/logs/app.log")
print("  2. Verify no 'finish_reason=4' or 'RECITATION' warnings")
print("  3. Verify LLM provided start_time_str and end_time_str")
print("=" * 80)
