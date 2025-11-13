"""Quick test script to verify settings save and load"""

import os
import json
import sys

# Add project to path
sys.path.insert(0, os.path.dirname(__file__))

from ai_schedule_agent.models.user_profile import UserProfile

# Test profile path
profile_path = os.path.abspath('.config/user_profile.json')
print(f"Profile path: {profile_path}")

# Test 1: Create and save profile
print("\n=== Test 1: Creating test profile ===")
profile = UserProfile()
profile.email = "test@example.com"
profile.working_hours = {
    'Monday': ('08:00', '18:00'),
    'Tuesday': ('08:00', '18:00')
}
profile.energy_patterns = {
    9: 0.8,
    10: 1.0,
    11: 0.9
}
profile.behavioral_rules = ["No meetings before 9 AM", "Lunch break at 12 PM"]

# Ensure directory exists
os.makedirs(os.path.dirname(profile_path), exist_ok=True)

# Save
print(f"Saving profile to: {profile_path}")
with open(profile_path, 'w') as f:
    json.dump(profile.to_dict(), f, indent=2)

print(f"✓ Profile saved")
print(f"  Email: {profile.email}")
print(f"  Working hours: {profile.working_hours}")

# Test 2: Load profile
print("\n=== Test 2: Loading profile ===")
if os.path.exists(profile_path):
    with open(profile_path, 'r') as f:
        data = json.load(f)

    loaded_profile = UserProfile.from_dict(data)
    print(f"✓ Profile loaded")
    print(f"  Email: {loaded_profile.email}")
    print(f"  Working hours: {loaded_profile.working_hours}")
    print(f"  Energy patterns: {loaded_profile.energy_patterns}")
    print(f"  Behavioral rules: {loaded_profile.behavioral_rules}")

    # Verify
    if loaded_profile.email == profile.email:
        print("\n✓✓✓ SUCCESS: Email matches!")
    else:
        print(f"\n✗✗✗ FAIL: Email doesn't match ({loaded_profile.email} != {profile.email})")

    if loaded_profile.working_hours == profile.working_hours:
        print("✓✓✓ SUCCESS: Working hours match!")
    else:
        print(f"✗✗✗ FAIL: Working hours don't match")
else:
    print(f"✗✗✗ FAIL: Profile file not found at {profile_path}")

print("\n=== Test complete ===")
