"""Quick test script for Chinese pattern extraction"""
import os
os.environ['DRY_RUN'] = '1'  # Enable dry run mode

from ai_schedule_agent.core.nlp_processor import NLPProcessor

# Initialize with LLM disabled to test rule-based patterns
nlp = NLPProcessor(use_llm=False)

# Test cases
test_cases = [
    "明天下午排3小時開會",
    "請安排「與教授會面」，時間是今天晚上8點到9點",
    "後天上午10點開會2小時",
    "明天下午2點到5點討論專案",
]

print("=" * 60)
print("Chinese Pattern Extraction Test")
print("=" * 60)

for text in test_cases:
    print(f"\nInput: {text}")
    result = nlp.parse_scheduling_request(text)

    print(f"  Title: {result.get('title')}")
    print(f"  Datetime: {result.get('datetime')}")
    print(f"  End Datetime: {result.get('end_datetime')}")
    print(f"  Duration: {result.get('duration')} minutes" if result.get('duration') else "  Duration: Not set")
    print(f"  Action: {result.get('action')}")
    print("-" * 60)

print("\n✅ Test complete! Check if extraction works correctly.")
