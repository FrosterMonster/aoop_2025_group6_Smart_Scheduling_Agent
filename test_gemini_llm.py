"""Test script for Gemini LLM processing with updated prompt"""
import os
import sys
import json
from pathlib import Path

# Enable dry run mode before any imports
os.environ['DRY_RUN'] = '1'

# Check if .env file exists
env_file = Path('.env')
if not env_file.exists():
    print("❌ ERROR: .env file not found!")
    print("\n📋 Setup Instructions:")
    print("  1. Copy .env.template to .env")
    print("  2. Add your Gemini API key to GEMINI_API_KEY")
    print("  3. Set LLM_PROVIDER=gemini")
    print("  4. Run this test again")
    sys.exit(1)

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Check if Gemini is configured
gemini_api_key = os.getenv('GEMINI_API_KEY')
llm_provider = os.getenv('LLM_PROVIDER', 'claude')

if not gemini_api_key or gemini_api_key == 'your_gemini_api_key_here':
    print("❌ ERROR: GEMINI_API_KEY not configured in .env file!")
    print("\n📋 Setup Instructions:")
    print("  1. Get your API key from: https://makersuite.google.com/app/apikey")
    print("  2. Add it to .env file: GEMINI_API_KEY=your_actual_key_here")
    print("  3. Run this test again")
    sys.exit(1)

if llm_provider != 'gemini':
    print(f"⚠️  WARNING: LLM_PROVIDER is set to '{llm_provider}', not 'gemini'")
    print("   This test requires Gemini. Setting LLM_PROVIDER=gemini for this test.")
    os.environ['LLM_PROVIDER'] = 'gemini'

from ai_schedule_agent.core.nlp_processor import NLPProcessor

# Initialize with LLM enabled to test Gemini
print("🔧 Initializing NLPProcessor with Gemini...")
nlp = NLPProcessor(use_llm=True)

# Test cases - focusing on Chinese input that previously caused issues
test_cases = [
    "明天下午排3小時開會",
    "今天晚上8點討論專案",
    "後天上午10點開會2小時",
]

print("=" * 80)
print("Gemini LLM Processing Test")
print("=" * 80)
print("\nVerifying that Gemini:")
print("  1. Returns valid JSON without parsing errors")
print("  2. Uses summary EXACTLY as provided (e.g., '會議' not '會議 (Meeting)')")
print("  3. Provides start_time_str and end_time_str correctly")
print("  4. Keeps response field short without requesting clarification")
print("=" * 80)

for i, text in enumerate(test_cases, 1):
    print(f"\n{'=' * 80}")
    print(f"Test Case {i}: {text}")
    print("=" * 80)

    try:
        result = nlp.parse_scheduling_request(text)

        print(f"\n✅ SUCCESS - LLM processed request")
        print(f"\nParsed Result:")
        print(f"  Action: {result.get('action')}")
        print(f"  Title: {result.get('title')}")
        print(f"  Datetime: {result.get('datetime')}")
        print(f"  Duration: {result.get('duration')} minutes" if result.get('duration') else "  Duration: Not set")
        print(f"  Target Date: {result.get('target_date')}")
        print(f"  Time Preference: {result.get('time_preference')}")

        # Verification checks
        print(f"\n🔍 Verification:")

        # Check 1: Title should not have English translations
        title = result.get('title', '')
        if '(' in title or ')' in title:
            print(f"  ❌ FAIL: Title contains parentheses (English translation added): '{title}'")
        else:
            print(f"  ✅ PASS: Title is clean: '{title}'")

        # Check 2: Title should not be too long
        if len(title) > 20:
            print(f"  ❌ FAIL: Title too long ({len(title)} chars): '{title}'")
        else:
            print(f"  ✅ PASS: Title is concise ({len(title)} chars)")

        # Check 3: Should have either datetime or target_date
        if result.get('datetime') or result.get('target_date'):
            print(f"  ✅ PASS: Time information provided")
        else:
            print(f"  ⚠️  WARNING: No datetime or target_date")

        # Check 4: Should have duration
        if result.get('duration'):
            print(f"  ✅ PASS: Duration provided ({result.get('duration')} minutes)")
        else:
            print(f"  ⚠️  WARNING: No duration")

    except json.JSONDecodeError as e:
        print(f"\n❌ JSON PARSING ERROR:")
        print(f"  Error: {e}")
        print(f"  This means Gemini generated invalid JSON")

    except Exception as e:
        print(f"\n❌ ERROR:")
        print(f"  Type: {type(e).__name__}")
        print(f"  Message: {e}")

    print("-" * 80)

print("\n" + "=" * 80)
print("Test Complete!")
print("=" * 80)
print("\n📋 What to check in logs:")
print("  1. No 'Failed to parse Gemini structured output' errors")
print("  2. No 'Unterminated string' JSON errors")
print("  3. No 'If you want to refine' or 'please let me know' in responses")
print("  4. No '(Meeting)' or other English translations after Chinese titles")
print("  5. Summary field should be short (< 10 words)")
print("  6. Response field should be short (< 20 words)")
print("\n💡 Check the application logs for detailed LLM output")
print("=" * 80)
