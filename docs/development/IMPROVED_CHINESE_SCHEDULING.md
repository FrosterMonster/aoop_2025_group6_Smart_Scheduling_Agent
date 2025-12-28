# Improved Chinese Scheduling Logic

## Problem

Previously, when a user entered "明天下午排3小時開會" (schedule 3-hour meeting tomorrow afternoon), the system would:
- ❌ Hardcode 2pm as the default time
- ❌ Ignore user's actual calendar availability
- ❌ Not use the sophisticated scheduling engine

## Solution

The system now **intelligently distinguishes** between:

### 1. **Specific Time Requests** (Use exact time)
When user specifies exact time like "2點":

**Input**: `"明天下午2點開會"`
**Behavior**:
- ✅ Uses **2pm exactly** as requested
- ✅ `datetime` = Tomorrow 14:00
- ✅ No scheduling engine needed

### 2. **Time Period Requests** (Find optimal slot)
When user only specifies period like "下午":

**Input**: `"明天下午排3小時開會"`
**Behavior**:
- ✅ **No hardcoded time** - leaves `datetime` empty
- ✅ Sets `target_date` = Tomorrow's date
- ✅ Sets `time_preference` = { period: 'afternoon', start_hour: 13, end_hour: 18 }
- ✅ **Scheduling engine finds optimal free slot** within 1pm-6pm range

---

## Implementation Details

### Code Changes ([nlp_processor.py:858-890](ai_schedule_agent/core/nlp_processor.py#L858-L890))

```python
# If specific time (X點) is mentioned, use it
if '點' in time_str:
    dt = parse_nl_time(time_str)
    result['datetime'] = dt  # Use exact time

else:
    # NO specific time - let scheduling engine find slot
    if '下午' in time_str:
        result['time_preference'] = {
            'period': 'afternoon',
            'start_hour': 13,  # 1pm
            'end_hour': 18     # 6pm
        }
    # ... other periods

    result['target_date'] = tomorrow.date()
    # datetime is NOT set - triggers scheduling engine
```

### Time Period Mappings

| Chinese | English | Time Range | Use Case |
|---------|---------|------------|----------|
| 上午/早上 | Morning | 9am - 12pm | "明天上午開會" |
| 中午 | Noon | 11am - 2pm | "明天中午討論" |
| 下午 | Afternoon | 1pm - 6pm | "明天下午排課" |
| 晚上/傍晚 | Evening | 6pm - 9pm | "今天晚上會議" |

---

## Expected Behavior Examples

### Example 1: Period Only (Optimal Slot)

**Input**: `"明天下午排3小時開會"`

**Extraction**:
```python
{
    'title': '開會',
    'target_date': datetime.date(2025, 12, 28),  # Tomorrow
    'time_preference': {
        'period': 'afternoon',
        'start_hour': 13,
        'end_hour': 18
    },
    'duration': 180,  # 3 hours
    'datetime': None  # Not set!
}
```

**Scheduling Engine Behavior**:
1. Queries user's calendar for tomorrow (12/28)
2. Finds busy periods
3. Looks for 3-hour free slot between 1pm-6pm
4. Considers:
   - ✅ User's energy patterns (peak productivity hours)
   - ✅ Existing meetings (avoid conflicts)
   - ✅ Buffer time (breaks between events)
   - ✅ Priority (important meetings get best slots)

**Result**: Event scheduled at **optimal available time**, e.g., 2:30pm-5:30pm if that's the best free slot.

### Example 2: Specific Time (Exact Scheduling)

**Input**: `"明天下午2點開會"`

**Extraction**:
```python
{
    'title': '開會',
    'datetime': datetime(2025, 12, 28, 14, 0),  # Exact: 2pm
    'duration': 60,  # Default 1 hour if not specified
    'time_preference': None  # Not needed
}
```

**Behavior**: Event created at exactly 2pm (no optimization).

### Example 3: Time Range (Start + End)

**Input**: `"明天下午2點到5點討論專案"`

**Extraction**:
```python
{
    'title': '討論專案',
    'datetime': datetime(2025, 12, 28, 14, 0),
    'end_datetime': datetime(2025, 12, 28, 17, 0),
    'duration': 180,  # Calculated from range
}
```

**Behavior**: Event created at exactly 2pm-5pm (user specified exact range).

---

## UI Integration

### Quick Schedule Tab Flow

1. **User enters Chinese text**: "明天下午排3小時開會"

2. **NLP Processing**:
   ```python
   result = nlp_processor.parse_scheduling_request(text)
   # result has: target_date, time_preference, duration, title
   ```

3. **UI Decision Logic**:
   ```python
   if result.get('datetime'):
       # User specified exact time - use it
       form.set_datetime(result['datetime'])
   elif result.get('target_date') and result.get('time_preference'):
       # User specified period - find optimal slot
       optimal_slot = scheduling_engine.find_optimal_slot(
           target_date=result['target_date'],
           duration=result['duration'],
           time_preference=result['time_preference']
       )
       form.set_datetime(optimal_slot.start_time)
   else:
       # Fallback to default
       form.set_datetime(None)
   ```

4. **Form Display**:
   - Title: "開會" ✓
   - Date: Tomorrow ✓
   - Time: **Best available slot** (e.g., 2:30pm) ✓
   - Duration: 3 hours ✓

---

## Benefits

### Before (Hardcoded Defaults)
- ❌ Always used 2pm for "下午"
- ❌ Might conflict with existing events
- ❌ Ignored user's productivity patterns
- ❌ Wasted scheduling engine capabilities

### After (Intelligent Scheduling)
- ✅ Finds truly optimal time slot
- ✅ Respects calendar availability
- ✅ Uses energy patterns and preferences
- ✅ Only 1pm-6pm range for "下午" (sensible constraint)
- ✅ Smarter than just picking first available slot

---

## Technical Notes

### Why Not Always Use Scheduling Engine?

When user says "明天2點" (tomorrow 2pm), they have a **specific constraint** - maybe:
- Meeting someone who's only available at 2pm
- Following their own rigid schedule
- Appointment with external party

**Respecting explicit times is critical for UX.**

### Time Preference Structure

```python
time_preference = {
    'period': 'afternoon',  # Human-readable
    'start_hour': 13,       # Constraint: earliest time
    'end_hour': 18,         # Constraint: latest time
}
```

This gives scheduling engine:
- **Flexibility**: Any time between 1pm-6pm
- **Constraint**: Not before 1pm, not after 6pm
- **Guidance**: "afternoon" suggests post-lunch energy levels

---

## Future Enhancements

1. **User Profile Integration**:
   - "下午" could mean 2pm-5pm for one user
   - But 1pm-6pm for another user
   - Store per-user time period preferences

2. **Smart Defaults**:
   - If user always schedules "下午" meetings at 3pm
   - Learn pattern and suggest 3pm first

3. **Multi-Day Scheduling**:
   - "這週下午排10小時" (Schedule 10 hours this week, afternoons)
   - Distribute across multiple afternoon slots

4. **Conflict Resolution**:
   - If no 3-hour afternoon slot available tomorrow
   - Suggest: "Split into 2x 1.5hr sessions?" or "Move to next day?"

---

## Testing

### Test Cases

1. **Specific Time**:
   - Input: "明天2點開會"
   - Assert: `datetime` is set to exact 2pm

2. **Morning Period**:
   - Input: "明天上午開會"
   - Assert: `time_preference.start_hour == 9`
   - Assert: `datetime` is None (triggers scheduling)

3. **Afternoon + Duration**:
   - Input: "明天下午排3小時"
   - Assert: `duration == 180`
   - Assert: `time_preference.period == 'afternoon'`

4. **Evening**:
   - Input: "今天晚上討論"
   - Assert: `time_preference.start_hour == 18`

---

## Summary

**Key Improvement**: The system now **intelligently decides** whether to:
- Use **exact time** when user specifies (明天2點)
- Invoke **scheduling engine** when user gives period (明天下午)

This leverages the full power of ai_schedule_agent's sophisticated scheduling algorithms while respecting user intent.

**Impact on "明天下午排3小時開會"**:
- Before: Always 2pm (hardcoded) ❌
- After: Best available afternoon slot (intelligent) ✅
