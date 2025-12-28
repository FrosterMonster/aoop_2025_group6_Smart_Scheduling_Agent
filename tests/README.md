# Test Suite

This directory contains all test scripts for the AI Schedule Agent.

## Running Tests

### Individual Tests

Run specific tests from the project root:
```bash
# From project root
python -m tests.test_gemini_safety_fix
python -m tests.test_chinese_extraction
python -m tests.test_tkinter
```

Or navigate to the tests directory:
```bash
cd tests
python test_gemini_safety_fix.py
```

### All Tests

Run the full test suite using pytest:
```bash
pytest tests/
```

---

## Test Files

### Gemini LLM Tests

**[test_gemini_safety_fix.py](test_gemini_safety_fix.py)**
- Tests Gemini safety filter and shortened prompt fixes
- Verifies no RECITATION errors (finish_reason=4)
- Checks token limit enforcement (200 tokens)
- Validates proper JSON generation
- **Run this to verify Gemini integration works**

**[test_gemini_llm.py](test_gemini_llm.py)**
- Tests Gemini LLM processing with updated prompt
- Verifies JSON validity and conciseness
- Checks no clarification requests in output
- Validates form population from LLM output

### NLP & Processing Tests

**[test_nlp_processor.py](test_nlp_processor.py)**
- Unit tests for NLPProcessor class
- Tests pattern matching and extraction
- Validates LLM integration
- Comprehensive test coverage

**[test_chinese_extraction.py](test_chinese_extraction.py)**
- Tests Chinese pattern extraction
- Validates time parsing for Chinese input
- Examples: "明天下午排3小時開會"
- Tests rule-based NLP (without LLM)

**[test_time_parser.py](test_time_parser.py)**
- Unit tests for time parsing utilities
- Tests various time format parsing
- Validates timezone handling
- Tests relative time expressions

**[test_title_extraction.py](test_title_extraction.py)**
- Tests title extraction from Chinese input
- Validates three-tier pattern matching
- Tests quoted titles, post-duration, post-action patterns

### LLM Integration Tests

**[test_llm_form_filling.py](test_llm_form_filling.py)**
- Tests LLM form filling functionality
- Validates start_time_str and end_time_str generation
- Tests Chinese input processing
- Verifies field population accuracy

### Calendar & Integration Tests

**[test_calendar_auth.py](test_calendar_auth.py)**
- Tests Google Calendar authentication
- Validates OAuth flow
- Tests calendar API access
- Verifies credentials handling

**[test_energy_patterns.py](test_energy_patterns.py)**
- Tests energy pattern detection
- Validates pattern learning functionality
- Tests user preference tracking

### UI Tests

**[test_ui_form_population.py](test_ui_form_population.py)**
- Tests UI form population logic
- Validates three-way form filling logic
- Tests time_preference and target_date handling
- Verifies integration with scheduling engine

**[test_settings_save.py](test_settings_save.py)**
- Tests settings persistence
- Validates auto-save functionality
- Tests configuration loading

**[test_tkinter.py](test_tkinter.py)**
- Tests Tkinter installation and functionality
- Validates UI framework availability
- Useful for Python 3.13 compatibility checks

### Configuration

**[conftest.py](conftest.py)**
- Pytest configuration and fixtures
- Shared test utilities
- Common setup/teardown logic

**[__init__.py](__init__.py)**
- Makes tests directory a Python package

---

## Test Categories

### 🚀 Quick Smoke Tests (Run First)

Start with these to verify basic functionality:
```bash
python -m tests.test_tkinter              # Verify Tkinter works
python -m tests.test_chinese_extraction   # Test basic NLP
python -m tests.test_gemini_safety_fix    # Test Gemini integration
```

### 🧪 Integration Tests

Test full system integration:
```bash
python -m tests.test_llm_form_filling
python -m tests.test_ui_form_population
python -m tests.test_calendar_auth
```

### 🔬 Unit Tests

Detailed component testing:
```bash
pytest tests/test_nlp_processor.py -v
pytest tests/test_time_parser.py -v
```

---

## Recent Test Additions

### December 28, 2025

**test_gemini_safety_fix.py** - New
- Tests fixes for Gemini RECITATION safety filter
- Validates 200 token limit enforcement
- Checks malformed JSON auto-fix
- Verifies post-processing truncation

**test_gemini_llm.py** - Updated
- Added environment variable checks
- Improved error messages
- Validates no clarification requests

---

## Test Requirements

### Environment Setup

1. Copy `.env.template` to `.env`
2. Configure API keys:
   ```
   GEMINI_API_KEY=your_key_here
   OPENAI_API_KEY=your_key_here
   ANTHROPIC_API_KEY=your_key_here
   ```
3. Set `LLM_PROVIDER` based on which LLM you want to test

### Python Dependencies

Install test dependencies:
```bash
pip install -r requirements.txt
pip install pytest pytest-cov
```

### Dry Run Mode

Most tests use `DRY_RUN=1` to avoid making actual API calls or calendar changes. This is set automatically in test scripts.

---

## Common Test Issues

### ImportError

If you get import errors, make sure you're running from the project root:
```bash
# From project root
python -m tests.test_name
```

### API Key Errors

Tests requiring LLM will check for valid API keys and exit gracefully if not configured.

### Tkinter Errors (Python 3.13)

If you're on Python 3.13 and get tkinter errors, see:
- [FOR_PYTHON313_USERS.md](../FOR_PYTHON313_USERS.md)
- Run: `python fix_python313.py`

---

## Writing New Tests

### Test Naming

- File: `test_<component>.py`
- Function: `test_<specific_behavior>()`
- Use descriptive names that explain what's being tested

### Test Structure

```python
"""Test description"""
import os
os.environ['DRY_RUN'] = '1'  # Enable dry run

from ai_schedule_agent.core.component import Component

def test_specific_behavior():
    """Test that specific behavior works correctly"""
    # Arrange
    component = Component()

    # Act
    result = component.do_something()

    # Assert
    assert result == expected
```

### Running During Development

Use pytest's `-v` (verbose) and `-s` (show print) flags:
```bash
pytest tests/test_your_test.py -v -s
```

---

## Test Coverage

Generate coverage report:
```bash
pytest --cov=ai_schedule_agent --cov-report=html tests/
```

View coverage:
```bash
open htmlcov/index.html  # On macOS/Linux
start htmlcov/index.html # On Windows
```

---

## CI/CD Integration

These tests are designed to be run in CI/CD pipelines. Set environment variables:
```yaml
env:
  DRY_RUN: 1
  GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
  # Add other API keys as needed
```

---

## Support

If tests fail:
1. Check the logs in `.config/logs/app.log`
2. Verify `.env` configuration
3. Ensure all dependencies are installed
4. See [TROUBLESHOOTING.md](../TROUBLESHOOTING.md)
