"""Quick test to verify Chinese title extraction fix"""
import os
os.environ['DRY_RUN'] = '1'

from ai_schedule_agent.core.nlp_processor import NLPProcessor

# Initialize NLP processor
nlp = NLPProcessor(use_llm=False)

print("=" * 70)
print("Chinese Title Extraction Test")
print("=" * 70)

test_cases = [
    {
        'input': '明天下午排3小時開會',
        'expected_title': '開會',
        'expected_duration': 180
    },
    {
        'input': '明天排1小時討論專案',
        'expected_title': '討論專案',
        'expected_duration': 60
    },
    {
        'input': '今天晚上排2小時會議',
        'expected_title': '會議',
        'expected_duration': 120
    },
    {
        'input': '明天安排「團隊會議」',
        'expected_title': '團隊會議',
        'expected_duration': None
    },
    {
        'input': '排開會',
        'expected_title': '開會',
        'expected_duration': None
    },
]

passed = 0
failed = 0

for i, test in enumerate(test_cases, 1):
    print(f"\n{'='*70}")
    print(f"Test {i}: {test['input']}")
    print(f"{'='*70}")

    result = nlp.parse_scheduling_request(test['input'])

    title = result.get('title')
    duration = result.get('duration')

    print(f"Expected: title='{test['expected_title']}', duration={test['expected_duration']}")
    print(f"Got:      title='{title}', duration={duration}")

    title_match = title == test['expected_title']
    duration_match = duration == test['expected_duration']

    if title_match and duration_match:
        print("✅ PASS")
        passed += 1
    else:
        print("❌ FAIL")
        if not title_match:
            print(f"   Title mismatch: expected '{test['expected_title']}', got '{title}'")
        if not duration_match:
            print(f"   Duration mismatch: expected {test['expected_duration']}, got {duration}")
        failed += 1

print(f"\n{'='*70}")
print(f"Results: {passed} passed, {failed} failed")
print(f"{'='*70}")
