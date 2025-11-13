# Energy Patterns Not Saving - Fix

## 🐛 Problem

User reported: **"ENERGY PATTERN ISNT SAVED"**

Despite the auto-save system working correctly, energy pattern slider values were not persisting across app restarts.

---

## 🔍 Root Cause

**JSON Key Type Conversion Issue**

When Python dictionaries with integer keys are serialized to JSON, the keys are converted to strings:

```python
# In Python (before save)
energy_patterns = {9: 0.7, 10: 0.9, 11: 1.0}

# In JSON file (after save)
"energy_patterns": {"9": 0.7, "10": 0.9, "11": 1.0}

# In Python (after load, BEFORE fix)
energy_patterns = {"9": 0.7, "10": 0.9, "11": 1.0}  # Keys are strings!
```

**The mismatch occurred in two places:**

1. **Settings Tab Load** (`settings_tab.py:243`):
   ```python
   for i in range(6, 22):  # i is an integer
       if i in self.user_profile.energy_patterns:  # Fails! Keys are strings
           slider.set(self.user_profile.energy_patterns[i] * 10)
   ```
   The check `9 in {"9": 0.7, "10": 0.9}` returns `False` because `9 != "9"`.

2. **Auto-Save** (`settings_tab.py:76-77`):
   ```python
   for hour, slider in self.energy_sliders.items():  # hour is int
       self.user_profile.energy_patterns[hour] = slider.get() / 10.0
   ```
   This creates NEW integer keys, but the old string keys remain!

**Result**:
- Energy patterns were being saved with integer keys
- But when loaded from JSON, they became string keys
- Settings tab couldn't find the values (looking for int keys)
- Sliders defaulted to 5 instead of saved values
- User thought nothing was being saved

---

## ✅ Solution

### Fix 1: Convert String Keys to Integers on Load

Modified `UserProfile.from_dict()` to convert energy pattern keys from strings to integers:

**File**: `ai_schedule_agent/models/user_profile.py`

```python
@classmethod
def from_dict(cls, data):
    """Create from dictionary"""
    # Convert energy_patterns keys from strings to integers
    # (JSON serialization converts int keys to strings)
    if 'energy_patterns' in data:
        data['energy_patterns'] = {
            int(k): v for k, v in data['energy_patterns'].items()
        }
    return cls(**data)
```

**Effect**: Energy patterns loaded from JSON now have integer keys that match the code's expectations.

### Fix 2: Enhanced Debug Logging

Added comprehensive logging to track energy patterns through the save/load cycle:

**File**: `ai_schedule_agent/ui/tabs/settings_tab.py` (line 99)

```python
print(f"[AUTO-SAVE] Energy patterns: {self.user_profile.energy_patterns}")
```

**File**: `ai_schedule_agent/ui/modern_main_window.py` (lines 92-95)

```python
logger.info(f"  Energy patterns (raw): {data.get('energy_patterns', {})}")
profile = UserProfile.from_dict(data)
logger.info(f"  Energy patterns (converted): {profile.energy_patterns}")
```

**Effect**: Full visibility into energy patterns during save and load operations.

---

## 📊 Data Flow (Before Fix)

```
User adjusts slider (hour 9 → 0.8)
        ↓
auto_save_settings() triggered
        ↓
user_profile.energy_patterns[9] = 0.8  ← Integer key
        ↓
save_profile() → JSON serialization
        ↓
JSON file: {"energy_patterns": {"9": 0.8}}  ← String key!
        ↓
App restart
        ↓
load_or_create_profile() → JSON deserialization
        ↓
user_profile.energy_patterns = {"9": 0.8}  ← Still string key
        ↓
Settings tab loads: if 9 in energy_patterns  ← FAILS!
        ↓
Slider defaults to 5 (user's value lost)
```

---

## 📊 Data Flow (After Fix)

```
User adjusts slider (hour 9 → 0.8)
        ↓
auto_save_settings() triggered
        ↓
user_profile.energy_patterns[9] = 0.8  ← Integer key
        ↓
save_profile() → JSON serialization
        ↓
JSON file: {"energy_patterns": {"9": 0.8}}  ← String key (unavoidable)
        ↓
App restart
        ↓
load_or_create_profile() → JSON deserialization
        ↓
UserProfile.from_dict() converts keys:
  {"9": 0.8} → {9: 0.8}  ← Integer key restored!
        ↓
user_profile.energy_patterns = {9: 0.8}  ← Integer key
        ↓
Settings tab loads: if 9 in energy_patterns  ← SUCCESS!
        ↓
Slider set to 8 (user's value restored) ✓
```

---

## 🧪 Testing

### Manual Test

1. **Open app** → Go to Settings tab
2. **Adjust energy sliders** → Set hour 9 to 8, hour 14 to 3
3. **Wait 2 seconds** → Check console: `[AUTO-SAVE] Energy patterns: {9: 0.8, 14: 0.3, ...}`
4. **Close app** → Check logs: `Profile saved on exit`
5. **Check JSON file**:
   ```bash
   cat .config/user_profile.json | grep -A 20 energy_patterns
   ```
   Should show: `"9": 0.8, "14": 0.3`
6. **Reopen app** → Check logs:
   ```
   Energy patterns (raw): {"9": 0.8, "14": 0.3, ...}
   Energy patterns (converted): {9: 0.8, 14: 0.3, ...}
   ```
7. **Go to Settings tab** → Verify sliders show correct values ✓

### Expected Console Output

```
[AUTO-SAVE] Settings saved successfully
[AUTO-SAVE] Working hours: {'Monday': ('09:00', '19:00'), ...}
[AUTO-SAVE] Energy patterns: {6: 0.5, 7: 0.5, 8: 0.5, 9: 0.8, 10: 0.5, ...}
[AUTO-SAVE] Email: your.email@example.com

INFO - Loading user profile from: D:\...\group_6\.config\user_profile.json
INFO - ✓ User profile loaded successfully
INFO -   Working hours: {'Monday': ['09:00', '19:00'], ...}
INFO -   Energy patterns (raw): {"9": 0.8, "10": 0.5, "11": 0.5, ...}
INFO -   Energy patterns (converted): {9: 0.8, 10: 0.5, 11: 0.5, ...}
INFO -   Email: your.email@example.com
```

---

## 📁 Files Modified

### 1. `ai_schedule_agent/models/user_profile.py` (lines 23-32)
**Change**: Enhanced `from_dict()` method to convert energy pattern keys

**Before**:
```python
@classmethod
def from_dict(cls, data):
    """Create from dictionary"""
    return cls(**data)
```

**After**:
```python
@classmethod
def from_dict(cls, data):
    """Create from dictionary"""
    # Convert energy_patterns keys from strings to integers
    # (JSON serialization converts int keys to strings)
    if 'energy_patterns' in data:
        data['energy_patterns'] = {
            int(k): v for k, v in data['energy_patterns'].items()
        }
    return cls(**data)
```

### 2. `ai_schedule_agent/ui/tabs/settings_tab.py` (line 99)
**Change**: Added energy patterns to debug logging

**Before**:
```python
print(f"[AUTO-SAVE] Working hours: {self.user_profile.working_hours}")
print(f"[AUTO-SAVE] Email: {self.user_profile.email}")
```

**After**:
```python
print(f"[AUTO-SAVE] Working hours: {self.user_profile.working_hours}")
print(f"[AUTO-SAVE] Energy patterns: {self.user_profile.energy_patterns}")
print(f"[AUTO-SAVE] Email: {self.user_profile.email}")
```

### 3. `ai_schedule_agent/ui/modern_main_window.py` (lines 92-95)
**Change**: Added detailed energy patterns logging during load

**Before**:
```python
logger.info(f"  Working hours: {data.get('working_hours', {})}")
logger.info(f"  Email: {data.get('email', 'Not set')}")
return UserProfile.from_dict(data)
```

**After**:
```python
logger.info(f"  Working hours: {data.get('working_hours', {})}")
logger.info(f"  Energy patterns (raw): {data.get('energy_patterns', {})}")
logger.info(f"  Email: {data.get('email', 'Not set')}")
profile = UserProfile.from_dict(data)
logger.info(f"  Energy patterns (converted): {profile.energy_patterns}")
return profile
```

---

## 🎯 Why This Works

### JSON Serialization Limitation

JSON specification only supports string keys for objects. When Python's `json.dump()` encounters a dictionary with non-string keys, it automatically converts them:

```python
import json

data = {9: 0.8, 10: 0.9}
json.dumps(data)  # '{"9": 0.8, "10": 0.9}'
```

This is standard behavior and cannot be changed.

### Our Solution

Instead of fighting JSON's behavior, we **embrace it** and convert back to integers when loading:

```python
# Serialization: int → string (automatic)
{9: 0.8} → {"9": 0.8}

# Deserialization: string → int (manual, in from_dict)
{"9": 0.8} → {9: 0.8}
```

This ensures the in-memory representation always uses integer keys, matching the code's expectations.

---

## 🔧 Alternative Solutions (Not Chosen)

### Option 1: Use String Keys Everywhere
Change `Dict[int, float]` to `Dict[str, float]` and use string keys throughout the code.

**Pros**: No conversion needed
**Cons**: Less intuitive code (`energy_patterns["9"]` vs `energy_patterns[9]`)
**Not chosen**: Integer keys are more natural for hour representations

### Option 2: Custom JSON Encoder/Decoder
Write custom JSON encoder that preserves integer keys.

**Pros**: Full control over serialization
**Cons**: More complex, non-standard JSON format
**Not chosen**: Too much complexity for a simple fix

### Option 3: Store as Array Instead of Dict
Use list indexed by hour offset: `energy_patterns[3]` for hour 9 (9-6=3).

**Pros**: Natural integer indexing
**Cons**: Confusing offset math, sparse array for limited hours
**Not chosen**: Less readable and maintainable

---

## ✅ Verification Checklist

- [x] Energy patterns save with integer keys in memory
- [x] Energy patterns serialize to JSON with string keys
- [x] Energy patterns deserialize back to integer keys
- [x] Settings tab sliders load correct values from profile
- [x] Slider changes trigger auto-save
- [x] Energy patterns persist across app restarts
- [x] Debug logging shows conversion at each step
- [x] No errors in console

---

## 📝 Summary

**Root Cause**: JSON serialization converts integer dictionary keys to strings, causing key lookup failures.

**Fix**: Convert string keys back to integers in `UserProfile.from_dict()` method.

**Impact**: Energy patterns now reliably persist across app restarts!

**Lines Changed**: 3 files, 12 lines total

**Result**: **Energy patterns ARE NOW SAVED!** ✓

---

**Last Updated**: November 6, 2025
**Version**: 1.2.1 (Hotfix)
**Status**: ✅ Fixed and Tested
