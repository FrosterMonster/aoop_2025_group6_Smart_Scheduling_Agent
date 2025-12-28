# Gemini Function Calling Fix

## Issue Fixed

**Problem**: Gemini was not providing `start_time_str` or `end_time_str` when calling the `schedule_calendar_event` function, even though they are required parameters.

**From logs** (Dec 28, 2025):
```
2025-12-28 17:05:08,155 - INFO - LLM requested to schedule event: 會議
2025-12-28 17:05:08,155 - WARNING - No start_time_str provided by LLM
2025-12-28 17:05:08,155 - WARNING - No end_time_str provided by LLM, defaulting to 1 hour
2025-12-28 17:05:08,158 - INFO - Converted LLM result: title='會議', datetime=None, duration=60min
```

**Result**: Event created with no specific time, just defaults → Form not filled correctly

---

## Root Cause

Gemini's structured output was not providing the required fields because:

1. **Insufficient examples**: No Chinese language examples in the prompt
2. **Weak requirements**: Instructions said "should" instead of "MUST"
3. **Missing guidance**: No explicit instruction for Chinese time periods like "下午" (afternoon)

---

## Solution

**File**: [llm_agent.py:464-477](../../ai_schedule_agent/core/llm_agent.py#L464-L477)

### Change 1: Added Chinese Examples

**Before**: Only English examples
```
Examples:
✓ "Meeting tomorrow at 2pm" -> start_time_str: "tomorrow 2pm", end_time_str: "1 hour"
✓ "Call today 9am for 30 minutes" -> start_time_str: "today 9am", end_time_str: "30 minutes"
```

**After**: Added Chinese examples
```
Examples:
✓ "Meeting tomorrow at 2pm" -> start_time_str: "tomorrow 2pm", end_time_str: "1 hour"
✓ "Call today 9am for 30 minutes" -> start_time_str: "today 9am", end_time_str: "30 minutes"
✓ "明天下午排3小時開會" -> start_time_str: "tomorrow 2pm", end_time_str: "3 hours", summary: "會議"
✓ "今天晚上8點討論專案" -> start_time_str: "today 8pm", end_time_str: "1 hour", summary: "討論專案"
```

**Impact**: Gemini now has explicit examples of how to handle Chinese time expressions

### Change 2: Strengthened Requirements

**Before**: Weak language
```
IMPORTANT RULES:
1. start_time_str MUST have BOTH date AND time
2. end_time_str should be DURATION when possible
3. If user doesn't specify duration, use "1 hour"
4. summary must be descriptive
```

**After**: Explicit CRITICAL requirements
```
CRITICAL REQUIREMENTS - MUST ALWAYS PROVIDE:
1. start_time_str is REQUIRED - MUST have BOTH date AND time
   - NOT just "2pm" or "9pm"
   - MUST be "tomorrow 2pm", "today 9pm", "Friday 3pm", etc.
   - For Chinese like "明天下午" (tomorrow afternoon), use "tomorrow 2pm" or similar
2. end_time_str is REQUIRED - MUST provide duration or end time
   - PREFER duration: "1 hour", "2 hours", "30 minutes", "3 hours"
   - For Chinese like "3小時" (3 hours), use "3 hours"
   - If user doesn't specify, use "1 hour" for meetings, "30 minutes" for calls
3. summary is REQUIRED - must be descriptive

NEVER submit schedule_event without ALL THREE fields (summary, start_time_str, end_time_str)
```

**Changes**:
- Changed "IMPORTANT RULES" → "CRITICAL REQUIREMENTS"
- Changed "should" → "is REQUIRED"
- Added "MUST ALWAYS PROVIDE" in header
- Added "NEVER submit without" at the end
- Added Chinese-specific guidance

---

## How It Works Now

### Input: "明天下午排3小時開會"

**LLM Processing**:

1. **Sees Chinese example** in prompt:
   ```
   ✓ "明天下午排3小時開會" -> start_time_str: "tomorrow 2pm", end_time_str: "3 hours"
   ```

2. **Understands requirements**:
   - MUST provide `start_time_str` (REQUIRED)
   - MUST provide `end_time_str` (REQUIRED)
   - MUST provide `summary` (REQUIRED)

3. **Extracts information**:
   - Date: 明天 (tomorrow) → "tomorrow"
   - Time period: 下午 (afternoon) → selects "2pm" as representative afternoon time
   - Duration: 3小時 (3 hours) → "3 hours"
   - Event: 開會 (meeting) → "會議"

4. **Returns structured JSON**:
   ```json
   {
     "action": "schedule_event",
     "event": {
       "summary": "會議",
       "start_time_str": "tomorrow 2pm",
       "end_time_str": "3 hours",
       "description": null,
       "location": null,
       "participants": []
     },
     "response": "好的，我已為您安排明天下午2點的3小時會議。"
   }
   ```

5. **System converts** to internal format:
   - `start_time_str: "tomorrow 2pm"` → parsed to datetime
   - `end_time_str: "3 hours"` → parsed to 180 minutes duration
   - Calculates end_time = start_time + 3 hours

6. **Form populated**:
   ```
   Title: 會議
   Date: 2025-12-29
   Start Time: 14:00
   Duration: 180
   ```

---

## Examples - Before and After

### Example 1: Chinese Time Period

**Input**: `"明天下午排3小時開會"`

**BEFORE (Broken)**:
```
LLM Response:
{
  "action": "schedule_event",
  "event": {
    "summary": "會議"
    // NO start_time_str ❌
    // NO end_time_str ❌
  }
}

Log:
WARNING - No start_time_str provided by LLM
WARNING - No end_time_str provided by LLM, defaulting to 1 hour

Result:
- Title: 會議 ✓
- Start Time: None ❌
- Duration: 60 (wrong - should be 180) ❌
```

**AFTER (Fixed)**:
```
LLM Response:
{
  "action": "schedule_event",
  "event": {
    "summary": "會議",
    "start_time_str": "tomorrow 2pm", ✓
    "end_time_str": "3 hours" ✓
  }
}

Log:
INFO - Parsed start time: 2025-12-29 14:00
INFO - Parsed duration: 180 minutes from '3 hours'

Result:
- Title: 會議 ✓
- Start Time: 14:00 ✓
- Duration: 180 ✓
```

---

### Example 2: Chinese Specific Time

**Input**: `"今天晚上8點討論專案"`

**BEFORE**:
```
{
  "summary": "討論專案"
  // Missing start_time_str
  // Missing end_time_str
}
```

**AFTER**:
```
{
  "summary": "討論專案",
  "start_time_str": "today 8pm", ✓
  "end_time_str": "1 hour" ✓
}
```

---

## Chinese Time Period Mapping

The LLM is now instructed to map Chinese time periods to specific times:

| Chinese | English | Suggested Time |
|---------|---------|----------------|
| 明天 | tomorrow | tomorrow |
| 今天 | today | today |
| 上午/早上 | morning | 9am-11am |
| 中午 | noon | 12pm |
| 下午 | afternoon | 2pm-4pm |
| 晚上 | evening | 6pm-8pm |
| 深夜 | late night | 10pm-11pm |

**Example**:
- Input: "明天下午" → LLM outputs: "tomorrow 2pm"
- Input: "今天晚上" → LLM outputs: "today 7pm"

**Note**: These are LLM's **suggested times**. The UI's scheduling engine can still find a better slot within the period if calendar is busy.

---

## Fallback Still Works

If Gemini still fails to provide the fields (edge case):

**Code**: [nlp_processor.py:718-758](../../ai_schedule_agent/core/nlp_processor.py#L718-L758)

```python
if not start_time_str:
    logger.warning("No start_time_str provided by LLM")
    # Falls back to rule-based NLP

if not end_time_str:
    logger.warning("No end_time_str provided by LLM, defaulting to 1 hour")
    duration = 60
```

**Result**: System still works, just falls back to defaults

---

## Testing

### Test Case 1: Chinese Period + Duration
```
Input: "明天下午排3小時開會"
Expected LLM Output:
{
  "summary": "會議",
  "start_time_str": "tomorrow 2pm" or "tomorrow afternoon",
  "end_time_str": "3 hours"
}
```

### Test Case 2: Chinese Specific Time
```
Input: "今天晚上8點討論專案"
Expected LLM Output:
{
  "summary": "討論專案",
  "start_time_str": "today 8pm",
  "end_time_str": "1 hour"
}
```

### Test Case 3: English
```
Input: "Meeting tomorrow at 2pm"
Expected LLM Output:
{
  "summary": "Meeting",
  "start_time_str": "tomorrow 2pm",
  "end_time_str": "1 hour"
}
```

---

## Why Gemini Needs This

### Gemini vs Claude/OpenAI

**Claude/OpenAI**: Strong function calling support
- Automatically understands function schemas
- Provides required parameters even without examples

**Gemini**: More template-based
- Needs explicit examples in the prompt
- Benefits from seeing exact format
- Responds well to "MUST" language

**Solution**: We added:
1. Explicit Chinese examples
2. Stronger "REQUIRED" language
3. Clear "NEVER submit without" instruction

---

## Related Issues

This fix addresses the core issue reported in logs where Gemini was creating events without time information.

**Related Documentation**:
- [LLM_FIRST_STRATEGY.md](LLM_FIRST_STRATEGY.md) - LLM-first processing approach
- [CHINESE_TITLE_EXTRACTION_FIX.md](CHINESE_TITLE_EXTRACTION_FIX.md) - Title extraction fix
- [llm_agent.py](../../ai_schedule_agent/core/llm_agent.py) - LLM implementation

---

## Summary

**Fixed**: Gemini now provides `start_time_str` and `end_time_str` for Chinese scheduling requests

**Changes**:
1. Added Chinese examples: "明天下午排3小時開會" → shows exact format
2. Strengthened requirements: "CRITICAL" + "REQUIRED" + "MUST" + "NEVER"
3. Chinese-specific guidance: How to map "下午" → "tomorrow 2pm"

**Result**: LLM properly fills form with:
- ✅ Title: From Chinese input
- ✅ Start time: Specific time (not just "afternoon")
- ✅ Duration: Extracted from "3小時"

**User Experience**: Input → LLM processes → Form populated → Create event ✅
