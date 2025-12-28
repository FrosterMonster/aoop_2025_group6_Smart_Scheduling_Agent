# Strict Time Window Constraint Fix

## Critical Issue Fixed

**Problem**: The time selection logic had the priority backwards - it was finding ANY optimal slot and then checking if it fit the user's requested time period, rather than ONLY searching within the requested time period.

**User Feedback**: "the time chosen should first fit the requirement of the prompt next it should fit the free time of the user"

---

## The Bug

### Before Fix

**Input**: "明天下午排3小時開會" (schedule 3-hour meeting tomorrow afternoon)
- User requests: Afternoon (1pm-6pm window)
- User has meeting: 1pm-4pm (busy)
- Only 2 hours free in afternoon: 4pm-6pm
- Duration needed: 3 hours

**Buggy Behavior**:
```python
# Old logic:
1. Call find_optimal_slot(event, search_start=tomorrow_1pm, search_days=1)
2. Scheduling engine uses working_hours (e.g., 9am-6pm) for entire day
3. Finds 3-hour slot: 4pm-7pm ❌ (goes past 6pm!)
4. Checks: "Does 4pm start within 1pm-6pm?" → Yes ✓
5. Populates form with 4pm-7pm ❌ WRONG!
```

**Why This Is Wrong**:
- User said "下午" (afternoon) = 1pm-6pm
- Event ends at 7pm = EVENING, not afternoon!
- Violates user's explicit time constraint

---

## The Fix

### After Fix

**Same Scenario**: "明天下午排3小時開會"

**Correct Behavior**:
```python
# New logic:
1. Define strict window: 1pm-6pm
2. Query calendar for busy slots on target date
3. For each 30-min slot from 1pm to 3pm (last possible start time):
   - Check if 3-hour slot fits ENTIRELY before 6pm
   - Check if slot is free (no conflicts)
   - Calculate score for free slots
4. No 3-hour slot fits entirely in 1pm-6pm window
5. Return None

# User sees:
⚠️ No free 180-minute slot in afternoon (13:00-18:00)
   on 2025-12-28

💡 Suggestions:
   • Try a shorter duration (e.g., 90 minutes)
   • Choose a different time period (morning/evening)
   • Select a different day
```

**Why This Is Correct**:
- Respects user's constraint FIRST (午 = 1pm-6pm)
- Only shows slots that fit ENTIRELY within window
- Provides helpful alternatives when no slot fits

---

## Implementation

### File Modified
[quick_schedule_tab.py:182-279](ai_schedule_agent/ui/tabs/quick_schedule_tab.py#L182-L279)

### Key Changes

#### 1. Manual Slot Search Within Window

**Old (Incorrect)**:
```python
# Problem: Relies on find_optimal_slot which uses user's working_hours (9am-6pm)
# This is WIDER than the requested time period (1pm-6pm for afternoon)
optimal_slot = scheduling_engine.find_optimal_slot(
    temp_event,
    search_start=tomorrow_1pm,
    search_days=1
)
```

**New (Correct)**:
```python
# Solution: Manually search ONLY within the requested time window
window_start = datetime.combine(target_date, time(hour=13))  # 1pm
window_end = datetime.combine(target_date, time(hour=18))    # 6pm

# Get busy slots from calendar
busy_slots = [...]

# Search for free slots STRICTLY within window
optimal_slot = None
best_score = -1
current_slot = window_start

while current_slot + timedelta(minutes=duration) <= window_end:  # KEY CHECK!
    slot_end = current_slot + timedelta(minutes=duration)

    # Verify slot is free
    if is_free(current_slot, slot_end, busy_slots):
        score = calculate_score(current_slot)
        if score > best_score:
            best_score = score
            optimal_slot = (current_slot, slot_end)

    current_slot += timedelta(minutes=30)
```

#### 2. Strict Window Constraint

**Critical Line 234**:
```python
while current_slot + timedelta(minutes=duration) <= window_end:
```

This ensures:
- `current_slot` = Start time
- `current_slot + duration` = End time
- End time must be `<= window_end` (6pm for afternoon)

**Example**:
- Window: 1pm-6pm
- Duration: 180 minutes (3 hours)
- Last valid start time: 3pm (ends at 6pm exactly)
- 3:30pm start would end at 6:30pm → REJECTED ✓

#### 3. User-Friendly Feedback

**When Slot Found**:
```
✅ Found optimal afternoon slot: 14:00 - 17:00
   Free slot within 13:00-18:00 window as requested
```

**When No Slot Found**:
```
⚠️ No free 180-minute slot in afternoon (13:00-18:00)
   on 2025-12-28

💡 Suggestions:
   • Try a shorter duration (e.g., 90 minutes)
   • Choose a different time period (morning/evening)
   • Select a different day
```

---

## Priority Order

The fix ensures the correct priority:

### ✅ Correct Priority (After Fix)

1. **First**: Does slot fit user's time period requirement?
   - "下午" = Must fit entirely within 1pm-6pm
   - **HARD CONSTRAINT** - Never violated

2. **Second**: Is slot free in user's calendar?
   - Check against existing events
   - **HARD CONSTRAINT** - Never violated

3. **Third**: Which free slot is optimal?
   - Use energy patterns, scoring
   - **SOFT PREFERENCE** - Best among valid options

### ❌ Wrong Priority (Before Fix)

1. First: Is slot free in user's calendar? ✓
2. Second: Which free slot is optimal? ✓
3. Third: Does slot fit time period? ❌ (Checked too late!)

**Problem**: By checking time window LAST, we already committed to a slot that might violate the user's constraint.

---

## Examples

### Example 1: Slot Fits Within Window

**Input**: "明天下午排2小時開會"

**Calendar**:
```
12:00-13:00  Lunch
15:00-16:00  Team sync
```

**Free Afternoon Slots (1pm-6pm)**:
- 13:00-15:00 (2 hours) ✓ Fits entirely in afternoon
- 16:00-18:00 (2 hours) ✓ Fits entirely in afternoon

**Algorithm**:
1. Check 13:00-15:00: Free? Yes. Score: 8.5 (post-lunch energy)
2. Check 13:30-15:30: Free? No (conflicts with 15:00 meeting)
3. Check 14:00-16:00: Free? No (conflicts with 15:00 meeting)
4. Check 14:30-16:30: Free? No (conflicts with 15:00 and 16:00 meetings)
5. Check 15:00-17:00: Free? No (conflicts with 15:00 meeting)
6. Check 15:30-17:30: Free? No (conflicts with 16:00 meeting)
7. Check 16:00-18:00: Free? Yes. Score: 7.0 (late afternoon)

**Result**: 13:00-15:00 (higher score)

**User Sees**:
```
✅ Found optimal afternoon slot: 13:00 - 15:00
   Free slot within 13:00-18:00 window as requested
```

---

### Example 2: No Slot Fits

**Input**: "明天下午排4小時開會"

**Calendar**:
```
13:00-15:00  Meeting A
15:30-17:00  Meeting B
```

**Free Afternoon Windows**:
- 13:00-13:00: 0 minutes (too short)
- 15:00-15:30: 30 minutes (too short)
- 17:00-18:00: 60 minutes (too short)

**Total free time in afternoon**: 90 minutes
**Required**: 240 minutes (4 hours)

**Algorithm**:
1. Start at 13:00, need slot until 17:00 (4 hours later)
2. 17:00 > 18:00 (window end) → SKIP
3. Start at 13:30, need slot until 17:30 → SKIP (past window)
4. ... (all start times rejected because end time exceeds 6pm)
5. No valid slot found

**Result**: None

**User Sees**:
```
⚠️ No free 240-minute slot in afternoon (13:00-18:00)
   on 2025-12-28

💡 Suggestions:
   • Try a shorter duration (e.g., 120 minutes)
   • Choose a different time period (morning/evening)
   • Select a different day
```

---

### Example 3: Morning Period

**Input**: "明天上午排3小時討論"

**Window**: 9am-12pm (3 hours total)

**Calendar**: Empty

**Free Morning Slots**:
- 9:00-12:00 ✓ Exactly fits window

**Algorithm**:
1. Check 9:00-12:00: Free? Yes. Score: 9.0 (morning energy peak)
2. Check 9:30-12:30: End time 12:30 > 12:00 → REJECTED
3. Check 10:00-13:00: End time 13:00 > 12:00 → REJECTED

**Result**: 9:00-12:00 (only valid slot)

**User Sees**:
```
✅ Found optimal morning slot: 09:00 - 12:00
   Free slot within 09:00-12:00 window as requested
```

---

## Technical Details

### Overlap Detection Logic

```python
# Two time slots overlap if:
# NOT (slot1 ends before slot2 starts OR slot1 starts after slot2 ends)

def is_free(slot_start, slot_end, busy_slots):
    for busy_start, busy_end in busy_slots:
        if not (slot_end <= busy_start or slot_start >= busy_end):
            return False  # Overlap detected
    return True  # No overlaps
```

**Examples**:
```
Slot:  [14:00 -------- 17:00]
Busy:  [12:00 -- 13:00]         → Free (busy ends before slot starts)
Busy:  [18:00 -- 19:00]         → Free (busy starts after slot ends)
Busy:  [15:00 -- 16:00]         → CONFLICT (overlap)
Busy:  [13:00 ----------- 18:00] → CONFLICT (overlap)
```

### Time Window Validation

```python
# Must check BOTH conditions:
slot_start >= window_start  # Starts within window
slot_end <= window_end      # Ends within window

# Implemented as loop condition:
while current_slot + timedelta(minutes=duration) <= window_end:
    # current_slot is implicitly >= window_start (we start there)
    # current_slot + duration <= window_end ensures end is within window
```

---

## Benefits of This Fix

### 1. Respects User Intent
- User says "下午" (afternoon) → System ONLY searches afternoon
- No surprises with events ending in evening when user asked for afternoon

### 2. Clear Feedback
- When slot found: Shows exact time range that fits
- When no slot: Explains why and suggests alternatives

### 3. Predictable Behavior
- "明天上午" always searches 9am-12pm
- "明天下午" always searches 1pm-6pm
- "明天晚上" always searches 6pm-9pm
- Consistent with user's mental model

### 4. Correct Constraint Hierarchy
```
User's Time Requirement (MUST SATISFY)
        ↓
Calendar Availability (MUST SATISFY)
        ↓
Optimal Scoring (BEST AMONG VALID)
```

---

## Edge Cases

### Edge Case 1: Exact Fit
**Scenario**: 3-hour slot requested, exactly 3 hours free in window

**Example**:
- Input: "明天上午排3小時"
- Window: 9am-12pm (3 hours)
- Calendar: Empty
- Result: 9:00-12:00 ✓ Perfect fit

### Edge Case 2: Multiple Free Slots
**Scenario**: Several free slots available

**Example**:
- Input: "明天下午排1小時"
- Free: 1pm-2pm, 3pm-4pm, 5pm-6pm
- Scores: 8.5, 9.0, 7.5
- Result: 3pm-4pm (highest score) ✓

### Edge Case 3: Slot Starts Before Window
**Scenario**: Event in progress when window starts

**Example**:
- Busy: 8am-2pm
- Window: 1pm-6pm (afternoon)
- Free afternoon: 2pm-6pm (4 hours)
- Request: 3 hours
- Result: 2pm-5pm ✓ Valid (starts after busy ends, ends before window ends)

### Edge Case 4: Past Time
**Scenario**: Target date is today, current time is 2pm, user asks for morning slot

**Example**:
- Input: "今天上午排2小時" (today morning)
- Current time: 2pm
- Window: 9am-12pm (already past)
- All morning slots < current_time + 30min → SKIPPED
- Result: No slot found ✓ Correct (can't schedule in the past)

---

## Testing

### Test Case 1: Basic Fit
```python
Input: "明天下午排2小時開會"
Expected:
  - Window: 13:00-18:00
  - Duration: 120 minutes
  - If free slot exists in afternoon: Form populated
  - If no free slot: Error message with suggestions
```

### Test Case 2: Exact Window Size
```python
Input: "明天上午排3小時" (morning = 9am-12pm = 3 hours)
Expected:
  - If free: Slot from 9:00-12:00
  - If any conflict: No slot found (can't fit 3 hours if any time is busy)
```

### Test Case 3: Oversize Request
```python
Input: "明天晚上排4小時" (evening = 6pm-9pm = 3 hours max)
Expected:
  - No slot found (4 hours > 3 hours available)
  - Error message suggests shorter duration
```

---

## Related Documentation

- [IMPROVED_CHINESE_SCHEDULING.md](IMPROVED_CHINESE_SCHEDULING.md) - NLP extraction of time periods
- [UI_FORM_POPULATION_FIX.md](UI_FORM_POPULATION_FIX.md) - Initial form population implementation
- [nlp_processor.py:858-890](ai_schedule_agent/core/nlp_processor.py#L858-L890) - Time preference extraction

---

## Summary

This fix ensures that **user's time period requirements are treated as hard constraints**, not soft preferences. When a user says "明天下午" (tomorrow afternoon), the system will ONLY suggest times that fit entirely within the afternoon window (1pm-6pm), and will clearly communicate when no such slot exists.

**Key Principle**:
> The time chosen should **first** fit the requirement of the prompt, **next** it should fit the free time of the user.

This is now correctly implemented with strict time window validation.
