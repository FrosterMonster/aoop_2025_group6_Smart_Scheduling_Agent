"""Quick test script to verify energy patterns save and load correctly"""

import os
import json
import sys

# Add project to path
sys.path.insert(0, os.path.dirname(__file__))

from ai_schedule_agent.models.user_profile import UserProfile

# Test profile path
profile_path = os.path.abspath('.config/user_profile.json')
print(f"Profile path: {profile_path}")

print("\n=== Test 1: Create profile with energy patterns ===")
profile = UserProfile()
profile.email = "test@example.com"
profile.energy_patterns = {
    6: 0.3,
    7: 0.4,
    8: 0.6,
    9: 0.8,
    10: 1.0,
    11: 0.9,
    12: 0.7,
    13: 0.5,
    14: 0.6,
    15: 0.8
}

print(f"Created energy_patterns (integer keys): {profile.energy_patterns}")

# Ensure directory exists
os.makedirs(os.path.dirname(profile_path), exist_ok=True)

# Save
print(f"\nSaving profile to: {profile_path}")
with open(profile_path, 'w') as f:
    json.dump(profile.to_dict(), f, indent=2)

print("✓ Profile saved")

# Read raw JSON to see what's actually stored
print("\n=== Test 2: Check JSON file (raw) ===")
with open(profile_path, 'r') as f:
    raw_data = json.load(f)
    print(f"JSON energy_patterns keys (type): {type(list(raw_data['energy_patterns'].keys())[0])}")
    print(f"JSON energy_patterns: {raw_data['energy_patterns']}")

# Load profile back
print("\n=== Test 3: Load profile back ===")
if os.path.exists(profile_path):
    with open(profile_path, 'r') as f:
        data = json.load(f)

    print(f"Loaded raw data (before from_dict):")
    print(f"  Keys type: {type(list(data['energy_patterns'].keys())[0])}")
    print(f"  Sample keys: {list(data['energy_patterns'].keys())[:5]}")

    loaded_profile = UserProfile.from_dict(data)

    print(f"\nLoaded profile (after from_dict):")
    print(f"  Keys type: {type(list(loaded_profile.energy_patterns.keys())[0])}")
    print(f"  Sample keys: {list(loaded_profile.energy_patterns.keys())[:5]}")
    print(f"  Energy patterns: {loaded_profile.energy_patterns}")

    # Verify
    print("\n=== Test 4: Verification ===")

    # Check that we can lookup with integer keys
    if 9 in loaded_profile.energy_patterns:
        print(f"✓✓✓ SUCCESS: Integer key lookup works!")
        print(f"    Energy at hour 9: {loaded_profile.energy_patterns[9]}")
    else:
        print(f"✗✗✗ FAIL: Integer key lookup failed")
        print(f"    Available keys: {list(loaded_profile.energy_patterns.keys())}")

    # Check values match
    if loaded_profile.energy_patterns[9] == profile.energy_patterns[9]:
        print(f"✓✓✓ SUCCESS: Values match!")
    else:
        print(f"✗✗✗ FAIL: Values don't match")
        print(f"    Original: {profile.energy_patterns[9]}")
        print(f"    Loaded: {loaded_profile.energy_patterns[9]}")

    # Check all keys are integers
    all_int = all(isinstance(k, int) for k in loaded_profile.energy_patterns.keys())
    if all_int:
        print(f"✓✓✓ SUCCESS: All keys are integers!")
    else:
        print(f"✗✗✗ FAIL: Some keys are not integers")
        print(f"    Key types: {[type(k) for k in loaded_profile.energy_patterns.keys()]}")

else:
    print(f"✗✗✗ FAIL: Profile file not found at {profile_path}")

print("\n=== Test complete ===")
