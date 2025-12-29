# Development Documentation

This directory contains technical documentation for the AI Schedule Agent development.

## Recent Major Updates (December 2025)

### Chinese Scheduling Improvements

1. **[GEMINI_TOKEN_LIMIT_FIX.md](GEMINI_TOKEN_LIMIT_FIX.md)** - Latest (Dec 28, 2025)
   - Fix Gemini generating 200+ char summaries causing malformed JSON
   - Force token limit to 200 (prevents extreme verbosity)
   - Auto-fix unterminated strings in malformed JSON
   - Post-process truncation of verbose output
   - Handles finish_reason=2 (MAX_TOKENS)

2. **[GEMINI_SAFETY_FILTER_FIX.md](GEMINI_SAFETY_FILTER_FIX.md)** - Dec 28, 2025
   - Fix Gemini RECITATION safety filter blocking all requests (finish_reason=4)
   - Shortened prompt from ~200 lines to ~40 lines (80% reduction)
   - Added safety_settings to prevent false positives
   - Added explicit finish_reason error handling

   - Test script: [tests/test_gemini_safety_fix.py](../../tests/test_gemini_safety_fix.py)


2. **[GEMINI_VERBOSE_OUTPUT_FIX.md](GEMINI_VERBOSE_OUTPUT_FIX.md)** - Dec 28, 2025
   - Fix Gemini generating verbose/broken JSON output
   - Fix Gemini requesting clarification instead of accepting user input
   - Added strict "ONLY JSON" rules and length limits
   - Added 10 "Do NOT" rules to prevent asking for details
   - Multiple layers of reminders for concise output
   - Test script: [tests/test_gemini_llm.py](../../tests/test_gemini_llm.py)


3. **[GEMINI_FUNCTION_CALLING_FIX.md](GEMINI_FUNCTION_CALLING_FIX.md)** - Dec 28, 2025
   - Fix Gemini not providing start_time_str and end_time_str
   - Added Chinese examples to LLM prompt
   - Strengthened REQUIRED field requirements

2. **[LLM_FIRST_STRATEGY.md](LLM_FIRST_STRATEGY.md)** - Dec 28, 2025
   - LLM handles form filling and scheduling time determination
   - Intelligent time selection based on calendar availability
   - Rule-based NLP as reliable fallback

3. **[CHINESE_TITLE_EXTRACTION_FIX.md](CHINESE_TITLE_EXTRACTION_FIX.md)** - Dec 28, 2025
   - Fix title extraction from Chinese input (was extracting "3" instead of "開會")
   - Three-tier pattern matching (quoted → after duration → after action)
   - Handles "明天下午排3小時開會" correctly now

3. **[LLM_OPTIMIZATION_FIX.md](LLM_OPTIMIZATION_FIX.md)** - Dec 28, 2025 *(Superseded)*
   - Previous approach: Skip LLM for simple Chinese input
   - Now superseded by LLM_FIRST_STRATEGY
   - Kept for historical reference

3. **[COMPLETE_CHINESE_SCHEDULING_FIX.md](COMPLETE_CHINESE_SCHEDULING_FIX.md)** - Dec 28, 2025
   - Complete overview of all Chinese scheduling fixes
   - NLP field copying fix
   - Enhanced logging
   - Before/after comparison

4. **[STRICT_TIME_WINDOW_FIX.md](STRICT_TIME_WINDOW_FIX.md)** - Dec 27, 2025
   - Fix priority: time requirement first, then free time
   - Strict enforcement of time windows (afternoon, morning, evening)
   - Prevents events from ending outside requested period

4. **[UI_FORM_POPULATION_FIX.md](UI_FORM_POPULATION_FIX.md)** - Dec 27, 2025
   - Three-way logic for form population
   - Proper handling of time_preference and target_date
   - Integration with scheduling engine

5. **[IMPROVED_CHINESE_SCHEDULING.md](IMPROVED_CHINESE_SCHEDULING.md)** - Dec 27, 2025
   - Smart time period detection
   - Distinguished specific time vs time period
   - Time preference metadata structure

6. **[COMPLETE_SOLUTION_SUMMARY.md](COMPLETE_SOLUTION_SUMMARY.md)** - Dec 27, 2025
   - End-to-end architecture overview
   - All layers explained (NLP → UI → Scheduling Engine)
   - Testing and verification

### Migration and Archive

7. **[MIGRATION_FROM_ARUMI.md](MIGRATION_FROM_ARUMI.md)** - Dec 22, 2025
   - Migration guide from 阿嚕米 to ai_schedule_agent
   - Feature mapping
   - Breaking changes

### Python 3.13 Compatibility

8. **[FIX_PYTHON_313_TKINTER_ERROR.md](FIX_PYTHON_313_TKINTER_ERROR.md)** - Dec 22, 2025
   - Fix tkinter import errors in Python 3.13
   - Updated setup scripts

9. **[FOR_PYTHON313_USERS.md](FOR_PYTHON313_USERS.md)** - Dec 22, 2025
   - Python 3.13 specific instructions

10. **[PYTHON313_FIX_SUMMARY.md](PYTHON313_FIX_SUMMARY.md)** - Dec 22, 2025
    - Summary of Python 3.13 fixes

### LLM and NLP Improvements

11. **[GEMINI_JSON_ERROR_FIX.md](GEMINI_JSON_ERROR_FIX.md)** - Nov 13, 2025
    - Fix Gemini JSON parsing errors
    - Improved error handling

12. **[LLM_IMPROVEMENTS_SUMMARY.md](LLM_IMPROVEMENTS_SUMMARY.md)** - Nov 13, 2025
    - Summary of LLM-related improvements

13. **[CHINESE_TIME_AND_PAST_SLOT_FIX.md](CHINESE_TIME_AND_PAST_SLOT_FIX.md)** - Nov 13, 2025
    - Earlier Chinese time parsing fixes
    - Past time slot prevention

### Performance and Setup

14. **[PERFORMANCE_OPTIMIZATIONS.md](PERFORMANCE_OPTIMIZATIONS.md)** - Nov 5, 2025
    - General performance improvements

15. **[STARTUP_OPTIMIZATION_SUMMARY.md](STARTUP_OPTIMIZATION_SUMMARY.md)** - Nov 5, 2025
    - Application startup optimizations

16. **[SETUP_IMPROVEMENTS_SUMMARY.md](SETUP_IMPROVEMENTS_SUMMARY.md)** - Nov 13, 2025
    - Setup script improvements

### UI and Refactoring

17. **[CHANGELOG_UI_FIXES.md](CHANGELOG_UI_FIXES.md)** - Nov 6, 2025
    - UI bug fixes and improvements

18. **[BEFORE_AFTER_COMPARISON.md](BEFORE_AFTER_COMPARISON.md)** - Nov 5, 2025
    - Comparison of major changes

19. **[REFACTORING_SUMMARY.md](REFACTORING_SUMMARY.md)** - Nov 4, 2025
    - Code refactoring summary

---

## Quick Reference

### For Chinese Scheduling Issues
Start with:
1. [LLM_OPTIMIZATION_FIX.md](LLM_OPTIMIZATION_FIX.md) - Performance and behavior
2. [COMPLETE_CHINESE_SCHEDULING_FIX.md](COMPLETE_CHINESE_SCHEDULING_FIX.md) - Complete overview
3. [STRICT_TIME_WINDOW_FIX.md](STRICT_TIME_WINDOW_FIX.md) - Time window constraints

### For Setup Issues
Start with:
1. [FOR_PYTHON313_USERS.md](FOR_PYTHON313_USERS.md) - If using Python 3.13
2. [SETUP_IMPROVEMENTS_SUMMARY.md](SETUP_IMPROVEMENTS_SUMMARY.md) - General setup

### For Migration
1. [MIGRATION_FROM_ARUMI.md](MIGRATION_FROM_ARUMI.md) - Migration guide

### For Architecture Understanding
1. [COMPLETE_SOLUTION_SUMMARY.md](COMPLETE_SOLUTION_SUMMARY.md) - Full system overview

---

## Documentation Guidelines

When adding new documentation:
1. Use descriptive filenames (e.g., `FEATURE_NAME_FIX.md`)
2. Include date in the file (see examples above)
3. Link to related documentation
4. Update this README with a summary
5. Place files in `docs/development/`
