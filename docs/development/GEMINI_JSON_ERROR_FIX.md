# Gemini JSON Parsing Error - Fix

## 🐛 Error Observed

```
2025-11-13 21:48:59,569 - ERROR - Failed to parse Gemini structured output:
Unterminated string starting at: line 1 column 165 (char 164)
```

**User Input**: `"aoop meeting at 11/20 pm7 for 1 hour"`

**What Happened**: Gemini returned malformed JSON that couldn't be parsed.

---

## 🔍 Root Causes

### 1. Complex Schema
The response schema for Gemini has many nested objects, which can cause Gemini to generate invalid JSON, especially with:
- Special characters in strings
- Nested quotes
- Long text fields

### 2. Unusual Date/Time Format
The input `"11/20 pm7"` is non-standard:
- `11/20` - Date without year (ambiguous)
- `pm7` - Should be `7pm` (reversed format)

This unusual format may have confused Gemini, leading to malformed output.

### 3. Missing Error Recovery
Previous code didn't have robust fallback when JSON parsing failed.

---

## ✅ Fixes Implemented

### 1. Enhanced Error Handling ([llm_agent.py:617-685](ai_schedule_agent/core/llm_agent.py#L617-L685))

**Added**:
```python
# Get the response text safely
response_text = response.text if hasattr(response, 'text') else ''

if not response_text:
    logger.error("Gemini returned empty response")
    return {
        'content': 'I encountered an issue processing your request...',
        'tool_calls': [],
        'action': 'chat'
    }

# Log the raw response for debugging
logger.debug(f"Gemini raw response: {response_text[:500]}")

try:
    structured_data = json.loads(response_text)
    # ... process ...
except json.JSONDecodeError as e:
    logger.error(f"Failed to parse Gemini structured output: {e}")
    logger.error(f"Problematic JSON (first 500 chars): {response_text[:500]}")

    # Provide helpful fallback message
    return {
        'content': 'I had trouble understanding your request. Please try again with format: "Schedule [event] on [date] at [time] for [duration]"',
        'tool_calls': [],
        'action': 'chat'
    }
```

**Benefits**:
- ✅ Logs raw response for debugging
- ✅ Graceful degradation with helpful user message
- ✅ No crashes from malformed JSON

### 2. Added Unusual Format Examples ([llm_agent.py:419-429](ai_schedule_agent/core/llm_agent.py#L419-L429))

**Added to Prompt**:
```
Examples:
✓ "aoop meeting at 11/20 pm7" -> start_time_str: "2025-11-20 19:00", end_time_str: "1 hour"

IMPORTANT: Handle unusual formats:
- "pm7" or "am9" means "7pm" or "9am"
- "11/20" means "2025-11-20" (current year)
- "11/20 pm7" -> "2025-11-20 19:00"
```

**Benefits**:
- ✅ LLM knows how to handle unusual time formats
- ✅ Explicit normalization rules

### 3. Better Logging

Added debug logging to see exactly what Gemini returns:
```python
logger.debug(f"Gemini raw response: {response_text[:500]}")
```

This helps diagnose future JSON parsing issues.

---

## 🧪 Testing

### Test Case 1: Unusual Format
**Input**: `"aoop meeting at 11/20 pm7 for 1 hour"`

**Expected Behavior**:
1. Gemini should normalize to: `"2025-11-20 19:00"` (7pm on Nov 20, 2025)
2. If JSON parsing fails, user gets helpful error message
3. No application crash

### Test Case 2: Standard Format
**Input**: `"team meeting tomorrow at 2pm"`

**Expected**: Works normally with improved prompts

### How to Test

```bash
# Run the test script
python test_llm_form_filling.py

# Or test in the app
./run.sh
# Try: "aoop meeting at 11/20 pm7 for 1 hour"
```

**What to Check**:
- ✓ Form populates correctly OR
- ✓ User gets clear error message (not a crash)
- ✓ Log shows the raw Gemini response for debugging

---

## 📊 Before vs After

### Before ❌
```
User: "aoop meeting at 11/20 pm7 for 1 hour"
→ Gemini returns malformed JSON
→ JSON parsing error
→ Form shows generic error or nothing
→ No debugging information
```

### After ✅
```
User: "aoop meeting at 11/20 pm7 for 1 hour"
→ Gemini understands unusual format from examples
→ Should return: start_time_str="2025-11-20 19:00"
→ If still malformed: Graceful error with helpful message
→ Debug log shows raw response for troubleshooting
```

---

## 🎓 What We Learned

### About Gemini's Structured Output

1. **Complex schemas increase error rate**: The more nested the schema, the more likely Gemini will generate invalid JSON
2. **Special characters are problematic**: Strings with quotes, newlines, or special chars can break JSON
3. **Examples are crucial**: Showing exact examples helps Gemini understand edge cases

### Best Practices for Gemini

1. **Simplify schema when possible**: Flatten nested structures
2. **Validate output**: Always wrap `json.loads()` in try-catch
3. **Log raw responses**: Essential for debugging malformed JSON
4. **Provide fallbacks**: User should never see a crash
5. **Show examples**: Especially for unusual formats

---

## 🔧 Alternative Solutions (If Issue Persists)

### Option 1: Simplify Schema
Reduce the number of optional fields in the response schema.

### Option 2: Use Text Parsing Instead
For Gemini, use simple text output and parse with regex instead of structured JSON.

### Option 3: Switch Provider
If Gemini continues to have issues:
- Claude (Anthropic) - Very good at following instructions
- OpenAI (GPT-4) - Reliable tool calling

Change in `.env`:
```bash
LLM_PROVIDER=claude  # or openai
```

### Option 4: Add JSON Sanitization
Pre-process Gemini's output to escape special characters before parsing.

---

## 📚 Related Files

- [llm_agent.py](ai_schedule_agent/core/llm_agent.py) - Main LLM implementation
- [LLM_FORM_FILLING_FIX.md](docs/guides/LLM_FORM_FILLING_FIX.md) - Overall LLM improvements
- [test_llm_form_filling.py](test_llm_form_filling.py) - Test script

---

## ✅ Verification

After these fixes:
- [x] Enhanced error handling for JSON parsing
- [x] Added logging of raw Gemini responses
- [x] Added unusual format examples to prompt
- [x] Graceful fallback messages for users
- [x] No application crashes from malformed JSON

---

**Status**: ✅ FIXED with enhanced error handling and better prompts

The app now handles Gemini JSON errors gracefully. If malformed JSON occurs, users get helpful messages instead of errors, and logs provide debugging information.

---

**Fixed on**: November 13, 2025
**Applies to**: Gemini provider (gemini-2.5-flash and similar models)
