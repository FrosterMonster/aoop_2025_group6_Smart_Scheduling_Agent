# 🤖 LLM Provider Setup Guide

Your AI Schedule Agent now supports **multiple LLM providers**: Claude (Anthropic), OpenAI GPT, and Google Gemini. This guide will help you configure and use them.

---

## 📋 Quick Start

### Step 1: Choose Your Provider

| Provider | Best For | Cost | Setup Difficulty |
|----------|----------|------|------------------|
| **Claude 3.5 Sonnet** ⭐ | Best overall, excellent Chinese support | Moderate | Easy |
| **OpenAI GPT-3.5** | Fastest, cheapest | Low | Easy |
| **OpenAI GPT-4** | Most accurate | High | Easy |
| **Google Gemini** | Future option | TBD | Medium |

**Recommendation**: Start with **Claude 3.5 Sonnet** (default) or **GPT-3.5-turbo** for cost-effectiveness.

---

### Step 2: Get Your API Key

#### **For Claude (Anthropic)** - RECOMMENDED

1. Go to: https://console.anthropic.com/settings/keys
2. Sign up/login to Anthropic
3. Click "Create Key"
4. Copy your key (starts with `sk-ant-...`)

**Pricing**: $3/million input tokens, $15/million output tokens

#### **For OpenAI**

1. Go to: https://platform.openai.com/api-keys
2. Sign up/login to OpenAI
3. Click "Create new secret key"
4. Copy your key (starts with `sk-...`)

**Pricing**: $0.50/$1.50 per million tokens (GPT-3.5), $30/$60 per million (GPT-4)

---

### Step 3: Configure Your API Key

#### **Method 1: Using `.env` File** (RECOMMENDED)

1. **Copy the template:**
   ```bash
   cp .env.template .env
   ```

2. **Edit `.env` file:**
   ```bash
   # For Claude (default)
   LLM_PROVIDER=claude
   ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
   CLAUDE_MODEL=claude-3-5-sonnet-20241022

   # OR for OpenAI
   LLM_PROVIDER=openai
   OPENAI_API_KEY=sk-your-actual-key-here
   OPENAI_MODEL=gpt-3.5-turbo
   ```

3. **Save and close**

#### **Method 2: Using `settings.json`**

Edit `.config/settings.json`:
```json
{
  "llm": {
    "provider": "claude",
    "max_tokens": 1000,
    "claude": {
      "model": "claude-3-5-sonnet-20241022",
      "api_key": "sk-ant-your-key-here"
    },
    "openai": {
      "model": "gpt-3.5-turbo",
      "api_key": null
    }
  }
}
```

**Note:** `.env` takes priority over `settings.json`

---

## 🔄 Switching Between Providers

### Quick Switch (Edit `.env`):

```bash
# Switch to Claude
LLM_PROVIDER=claude
ANTHROPIC_API_KEY=sk-ant-your-key

# Switch to OpenAI
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-key
```

**Restart the application** after changing providers.

---

## 🧪 Testing Your Setup

### Test 1: Check Provider Availability

```python
from ai_schedule_agent.core.llm_agent import LLMAgent

agent = LLMAgent()
print(f"Current provider: {agent.get_current_provider()}")
print(f"Is available: {agent.is_available()}")

# Expected output:
# Current provider: claude
# Is available: True
```

### Test 2: Process a Request

```python
result = agent.process_request("請幫我安排明天下午2點與導師會面")
print(f"Provider: {result['provider']}")
print(f"Action: {result['action']}")
print(f"Response: {result['response']}")
```

### Test 3: DRY_RUN Mode (Safe Testing)

In `.env`, set:
```bash
DRY_RUN=1
```

This will simulate all calendar operations without making real API calls.

---

## 📊 Provider Comparison

### Claude 3.5 Sonnet vs OpenAI GPT

| Feature | Claude 3.5 Sonnet | GPT-3.5-turbo | GPT-4 |
|---------|-------------------|---------------|-------|
| **Response Quality** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Speed** | Fast (~2s) | Very Fast (~1s) | Moderate (~3s) |
| **Cost per 1000 requests** | ~$2.40 | ~$0.40 | ~$23.00 |
| **Context Window** | 200K tokens | 16K tokens | 128K tokens |
| **Chinese Language** | Excellent | Very Good | Excellent |
| **Tool Calling** | ✅ Native | ✅ Native | ✅ Native |
| **Best Use Case** | Complex scheduling | Quick responses | Mission-critical |

### Cost Example (1 month, 1000 requests)

**Assumptions**: 500 input tokens + 200 output tokens per request

- **Claude 3.5 Sonnet**: $2.40/month
- **GPT-3.5-turbo**: $0.40/month
- **GPT-4**: $23.00/month

---

## ⚙️ Configuration Reference

### `.env` File Structure

```bash
# ============================================================================
# LLM Provider Selection
# ============================================================================
LLM_PROVIDER=claude              # Options: claude, openai, gemini
USE_LLM=1                        # 1=use LLM, 0=use rule-based fallback

# ============================================================================
# API Keys (REQUIRED - choose one)
# ============================================================================
ANTHROPIC_API_KEY=sk-ant-xxx     # For Claude
OPENAI_API_KEY=sk-xxx            # For OpenAI
GEMINI_API_KEY=xxx               # For Gemini (future)

# ============================================================================
# Model Selection
# ============================================================================
CLAUDE_MODEL=claude-3-5-sonnet-20241022
OPENAI_MODEL=gpt-3.5-turbo
GEMINI_MODEL=gemini-pro

# ============================================================================
# Advanced Settings
# ============================================================================
MAX_TOKENS=1000                  # Max response length
DRY_RUN=0                        # 1=simulate, 0=real API calls
DEFAULT_TIMEZONE=Asia/Taipei     # Your timezone
LOG_LEVEL=INFO                   # DEBUG, INFO, WARNING, ERROR
```

### Available Models

#### Claude Models
- `claude-3-5-sonnet-20241022` - **Recommended** (best balance)
- `claude-3-opus-20240229` - Most powerful (slower, expensive)
- `claude-3-haiku-20240307` - Fastest (cheaper, less capable)

#### OpenAI Models
- `gpt-3.5-turbo` - **Recommended for budget** (fast, cheap)
- `gpt-4` - Most accurate (expensive)
- `gpt-4-turbo-preview` - Latest GPT-4 (balanced)

---

## 🛡️ Security Best Practices

### ✅ DO:
- ✅ Use `.env` file for API keys (git-ignored)
- ✅ Start with `DRY_RUN=1` for testing
- ✅ Monitor your API usage regularly
- ✅ Set up billing alerts on provider dashboards
- ✅ Revoke old keys periodically

### ❌ DON'T:
- ❌ Commit `.env` file to git
- ❌ Put API keys in `settings.json` (use `.env` instead)
- ❌ Share API keys with anyone
- ❌ Use production keys for development
- ❌ Forget to revoke exposed keys immediately

---

## 🐛 Troubleshooting

### Problem: "LLM agent not available"

**Causes & Solutions:**

1. **No API key configured**
   ```bash
   # Check .env file
   cat .env | grep API_KEY
   # Should show your key (not empty)
   ```

2. **Wrong provider name**
   ```bash
   # Valid options: claude, anthropic, openai, gemini
   LLM_PROVIDER=claude  # Correct
   LLM_PROVIDER=claude3  # Wrong!
   ```

3. **Package not installed**
   ```bash
   # For Claude
   pip install anthropic

   # For OpenAI
   pip install openai

   # Or install all
   pip install -r requirements.txt
   ```

### Problem: "API call failed"

**Common causes:**

1. **Invalid API key**
   - Double-check your key
   - Regenerate if necessary

2. **Insufficient credits**
   - Check your billing dashboard
   - Add payment method

3. **Rate limit exceeded**
   - Wait a few seconds
   - Reduce request frequency

### Problem: "Provider not switching"

**Solution:** Restart the application after editing `.env` or `settings.json`

```bash
# Kill the app (Ctrl+C)
# Then restart
./run.sh
```

---

## 💰 Cost Management

### Monitor Your Usage

**Claude (Anthropic):**
- Dashboard: https://console.anthropic.com/settings/usage

**OpenAI:**
- Dashboard: https://platform.openai.com/usage

### Set Budget Limits

1. **Anthropic:** Set monthly budget in console
2. **OpenAI:** Set usage limits in organization settings

### Optimize Costs

1. **Use `MAX_TOKENS=1000`** (default) to limit response length
2. **Enable `DRY_RUN=1`** during development
3. **Choose cheaper models** for non-critical tasks:
   - Claude Haiku instead of Claude Opus
   - GPT-3.5 instead of GPT-4
4. **Cache common responses** (implement if needed)

---

## 🎯 Recommended Configurations

### For Development/Testing
```bash
LLM_PROVIDER=claude
ANTHROPIC_API_KEY=sk-ant-your-key
CLAUDE_MODEL=claude-3-haiku-20240307  # Cheapest
DRY_RUN=1                              # Safe mode
MAX_TOKENS=500                         # Lower limit
```

### For Production (Quality)
```bash
LLM_PROVIDER=claude
ANTHROPIC_API_KEY=sk-ant-your-key
CLAUDE_MODEL=claude-3-5-sonnet-20241022  # Best balance
DRY_RUN=0
MAX_TOKENS=1000
```

### For Production (Budget)
```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-key
OPENAI_MODEL=gpt-3.5-turbo  # Cheapest
DRY_RUN=0
MAX_TOKENS=800
```

---

## 🆘 Need Help?

1. **Check logs:** `.config/logs/app.log`
2. **Enable debug mode:** `LOG_LEVEL=DEBUG` in `.env`
3. **Test provider manually:**
   ```python
   from ai_schedule_agent.core.llm_agent import LLMAgent
   agent = LLMAgent()
   print(agent.get_current_provider())
   print(agent.is_available())
   ```

---

## 📚 Additional Resources

### Official Documentation
- **Claude API:** https://docs.anthropic.com/
- **OpenAI API:** https://platform.openai.com/docs/
- **Google Gemini:** https://ai.google.dev/docs

### Getting API Keys
- **Claude:** https://console.anthropic.com/settings/keys
- **OpenAI:** https://platform.openai.com/api-keys
- **Gemini:** https://makersuite.google.com/app/apikey

### Pricing
- **Claude:** https://www.anthropic.com/pricing
- **OpenAI:** https://openai.com/pricing
- **Gemini:** https://ai.google.dev/pricing

---

**You're all set! Choose your provider, add your API key, and start scheduling with AI! 🚀**
