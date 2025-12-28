# LLM-First Processing Strategy

## Overview

The system now uses an **LLM-first strategy** where the LLM handles form filling and scheduling time determination, with rule-based NLP as a fallback.

---

## Architecture Change

### Previous Strategy (Removed)

**OLD**: Pattern-first approach
```
Input → Chinese Patterns → If sufficient, skip LLM → Fill form
                        → If insufficient, use LLM → Fill form
```

**Problem**: LLM's intelligence for time selection and form filling was underutilized

### Current Strategy (Active)

**NEW**: LLM-first approach
```
Input → LLM (if enabled) → Intelligent time selection → Fill form
     → If LLM fails/disabled → Chinese Patterns → Fill form
```

**Benefit**: LLM makes intelligent decisions about:
- Optimal time selection based on calendar availability
- Form field population
- Handling ambiguous requests
- Complex scheduling logic

---

## How It Works

### Step 1: LLM Processing (Primary)

**File**: [nlp_processor.py:89-133](../../ai_schedule_agent/core/nlp_processor.py#L89-L133)

```python
# Try LLM processing first if enabled
# LLM handles intelligent time selection and form filling
if self.use_llm:
    self._ensure_llm_initialized()

if self.use_llm and self.llm_agent:
    try:
        logger.info(f"Processing with LLM: '{text}'")
        llm_result = self.llm_agent.process_request(text)

        # LLM returns structured data with optimal time selected
        if llm_result.get('success'):
            return self._convert_llm_result_to_dict(llm_result, text)
    except Exception as e:
        logger.error(f"Error in LLM processing: {e}. Falling back to rule-based NLP.")
```

**What LLM Does**:
1. Analyzes user request: "明天下午排3小時開會"
2. Checks calendar for free slots in afternoon
3. Selects optimal 3-hour slot (e.g., 2pm-5pm)
4. Returns structured data with exact start time
5. UI populates form directly from LLM response

### Step 2: Rule-Based Fallback (Secondary)

**File**: [nlp_processor.py:135-154](../../ai_schedule_agent/core/nlp_processor.py#L135-L154)

```python
# Rule-based processing (original logic)
logger.info(f"Processing with rule-based NLP: '{text}'")

# Try Chinese-specific patterns (from 阿嚕米)
chinese_result = self._extract_with_chinese_patterns(text)

result = {
    'action': 'create',
    'event_type': EventType.MEETING,
    'participants': [],
    'datetime': chinese_result.get('datetime'),
    'target_date': chinese_result.get('target_date'),
    'time_preference': chinese_result.get('time_preference'),
    'duration': chinese_result.get('duration'),
    'title': chinese_result.get('title'),
    # ... other fields
}
```

**When Used**:
- LLM is disabled (`use_llm=False`)
- LLM fails (API error, parsing error, etc.)
- Offline mode

---

## Example Flow

### Input: "明天下午排3小時開會"

#### Path 1: LLM Processing (Primary)

**Step 1**: LLM receives request
```
Processing with LLM: '明天下午排3小時開會'
```

**Step 2**: LLM analyzes
- Language: Chinese
- Action: Schedule event
- Duration: 3 hours
- Time period: Tomorrow afternoon
- Event type: Meeting

**Step 3**: LLM checks calendar
```python
# LLM internally queries calendar API
calendar.get_free_busy(
    start=tomorrow_1pm,
    end=tomorrow_6pm
)
# Returns: 2pm-5pm is free
```

**Step 4**: LLM selects optimal time
```python
# LLM decides: 2pm is optimal
# - Within afternoon window (1pm-6pm)
# - Fits 3-hour duration (2pm-5pm)
# - Good energy level at 2pm
# - No conflicts
```

**Step 5**: LLM returns structured result
```json
{
  "action": "schedule_event",
  "response": "好的，我已為您安排明天下午2點的3小時會議。",
  "event": {
    "summary": "會議",
    "start_time_str": "tomorrow 2pm",
    "end_time_str": "3 hours",
    "description": null,
    "location": null
  }
}
```

**Step 6**: UI populates form
```
Title: 會議
Date: 2025-12-29
Start Time: 14:00 ← Exact time from LLM
Duration: 180
```

**User sees**: Form ready to submit, one click to create!

---

#### Path 2: Rule-Based Fallback (If LLM Fails)

**Step 1**: LLM fails (e.g., API timeout)
```
ERROR - Error in LLM processing: API timeout. Falling back to rule-based NLP.
```

**Step 2**: Chinese patterns extract
```python
{
    'title': '開會',
    'duration': 180,
    'target_date': date(2025, 12, 29),
    'time_preference': {'period': 'afternoon', 'start_hour': 13, 'end_hour': 18}
}
```

**Step 3**: UI handles time preference
```python
# UI layer finds optimal slot within afternoon window
optimal_slot = find_optimal_slot_in_window(
    date=tomorrow,
    start_hour=13,
    end_hour=18,
    duration=180
)
# Returns: (14:30, 17:30)
```

**Step 4**: UI populates form
```
Title: 開會
Date: 2025-12-29
Start Time: 14:30 ← UI determined time
Duration: 180
```

---

## Comparison: LLM vs Rule-Based

| Aspect | LLM Processing | Rule-Based Processing |
|--------|----------------|----------------------|
| **Time Selection** | LLM chooses optimal time | UI layer finds optimal slot |
| **Intelligence** | Context-aware, learns patterns | Fixed regex patterns |
| **Calendar Integration** | LLM can query calendar | Patterns extract metadata, UI queries calendar |
| **Ambiguity Handling** | LLM resolves ambiguity | Falls back to defaults |
| **Speed** | 3-5 seconds (API call) | <0.1 seconds (local) |
| **Reliability** | Depends on API availability | 100% local |
| **Cost** | API costs per request | Free |

---

## When LLM is Used vs Not Used

### LLM is USED when:
✅ `use_llm=True` in settings
✅ API key is configured
✅ Network is available
✅ For ALL requests (Chinese, English, complex, simple)

### Rule-Based is USED when:
❌ `use_llm=False` in settings
❌ API key missing
❌ Network unavailable
❌ LLM fails/errors
❌ Offline mode

---

## Configuration

**Enable LLM-first**:
```python
nlp_processor = NLPProcessor(use_llm=True)  # Default
```

**Disable LLM** (force rule-based only):
```python
nlp_processor = NLPProcessor(use_llm=False)
```

**Check in settings**:
```
Settings Tab → LLM Provider → Select provider (Claude/OpenAI/Gemini)
              → API Key: [configured]
              → use_llm automatically set to True
```

---

## LLM System Prompt

The LLM is instructed to:

1. **Understand context**:
   - Current date/time
   - User's timezone
   - Calendar availability

2. **Make intelligent decisions**:
   - Choose optimal time within requested period
   - Balance user preferences with availability
   - Provide specific start times, not ranges

3. **Fill form directly**:
   - Return `start_time_str` with exact time
   - Return `duration` or `end_time_str`
   - Return `summary` (event title)

4. **Don't ask questions** (unless truly necessary):
   - Create reasonable defaults
   - Use context to fill gaps
   - Be concise in responses

---

## Benefits of LLM-First Strategy

### 1. Intelligent Time Selection
**Example**: "明天下午開會"

**LLM**:
- Checks tomorrow's afternoon (1pm-6pm)
- Finds free slots: 2pm-3pm, 4pm-5pm
- Considers energy patterns: user alert at 2pm
- Suggests: 2pm ✅ Intelligent choice

**Rule-based**:
- Extracts: afternoon = 13:00-18:00
- UI searches for first free slot
- Might suggest: 1pm if free ❌ Less optimal

### 2. Context Awareness
**Example**: "Follow-up meeting with John"

**LLM**:
- Can reference previous meetings
- Suggests time after existing "John" meetings
- Includes "Follow-up" in title

**Rule-based**:
- Extracts: title="Follow-up meeting with John"
- No context of previous meetings
- Generic time suggestion

### 3. Natural Language Understanding
**Example**: "Can we meet sometime next week?"

**LLM**:
- Understands question format
- Suggests specific time next week
- Responds conversationally

**Rule-based**:
- Might fail to extract "next week"
- Falls back to defaults
- No conversational response

---

## Trade-offs

### LLM-First Advantages:
✅ More intelligent time selection
✅ Better ambiguity handling
✅ Context awareness
✅ Natural conversation

### LLM-First Disadvantages:
❌ Slower (3-5 seconds)
❌ Costs API credits
❌ Requires internet
❌ May have parsing errors

### Why Keep Rule-Based Fallback:
✅ **Reliability**: Always works offline
✅ **Speed**: Instant for simple requests
✅ **Cost**: Free
✅ **Privacy**: No data sent to external APIs

---

## Code Changes

**Modified**: [nlp_processor.py:89-139](../../ai_schedule_agent/core/nlp_processor.py#L89-L139)

**Before**:
```python
# Try Chinese patterns first, skip LLM if sufficient
chinese_quick_check = self._extract_with_chinese_patterns(text)
if has_title and (has_time_info or has_duration):
    # Skip LLM
    pass
elif self.use_llm:
    # Use LLM only for complex
```

**After**:
```python
# Try LLM first if enabled
if self.use_llm and self.llm_agent:
    # LLM handles all requests
    llm_result = self.llm_agent.process_request(text)
    if llm_result.get('success'):
        return llm_result

# Fallback to rule-based only if LLM fails/disabled
chinese_result = self._extract_with_chinese_patterns(text)
```

---

## Related Documentation

- [LLM_OPTIMIZATION_FIX.md](LLM_OPTIMIZATION_FIX.md) - Previous optimization (now reverted)
- [COMPLETE_CHINESE_SCHEDULING_FIX.md](COMPLETE_CHINESE_SCHEDULING_FIX.md) - Overall architecture
- [llm_agent.py](../../ai_schedule_agent/core/llm_agent.py) - LLM implementation

---

## Summary

**Strategy**: LLM-first with rule-based fallback

**Flow**:
1. Try LLM (intelligent time selection, form filling)
2. If fails → Use Chinese patterns + UI scheduling
3. Both paths → Event created

**Result**:
- Best of both worlds: intelligence when online, reliability when offline
- LLM handles complex logic (time selection, ambiguity)
- Patterns provide fast, reliable fallback

**User Experience**:
- LLM makes smart decisions about scheduling
- Form filled with optimal time
- One click to create event
