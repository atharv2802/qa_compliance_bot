# Multi-Provider Support Guide

## Overview

QA Coach now supports **three LLM providers** with automatic fallback:

1. **OpenAI** (GPT-4o-mini, GPT-4, etc.)
2. **Anthropic** (Claude 3 Haiku, Sonnet, Opus)
3. **Groq** (Llama 3.1, Mixtral, etc.)

The system automatically falls back to alternate providers if the primary fails, ensuring high availability.

---

## Quick Start

### 1. Install Dependencies

```bash
# Install all providers (recommended)
pip install -r requirements.txt

# Or install selectively
pip install openai  # For OpenAI
pip install anthropic  # For Anthropic
pip install groq  # For Groq
```

### 2. Configure Environment

Edit your `.env` file:

```env
# Primary provider (required)
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini

# Fallback providers (optional, comma-separated)
LLM_FALLBACK_PROVIDERS=anthropic,groq

# API Keys (provide at least one)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GROQ_API_KEY=gsk_...

# Model overrides (optional)
ANTHROPIC_MODEL=claude-3-haiku-20240307
GROQ_MODEL=llama-3.1-8b-instant
```

### 3. Test Configuration

```bash
# Check provider status via API
curl http://localhost:8000/providers/status

# Or use the Python API
python -c "
from app.providers.provider_manager import get_provider_manager
print(get_provider_manager().get_provider_status())
"
```

---

## Configuration Examples

### Example 1: OpenAI Primary, Anthropic Fallback

**Use Case**: High reliability with Claude as backup

```env
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
LLM_FALLBACK_PROVIDERS=anthropic

OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

### Example 2: Anthropic Primary, No Fallback

**Use Case**: Using Claude exclusively

```env
LLM_PROVIDER=anthropic
LLM_MODEL=claude-3-haiku-20240307

ANTHROPIC_API_KEY=sk-ant-...
```

### Example 3: Groq Primary (Fast), OpenAI Fallback (Reliable)

**Use Case**: Ultra-low latency with reliability backup

```env
LLM_PROVIDER=groq
LLM_MODEL=llama-3.1-8b-instant
LLM_FALLBACK_PROVIDERS=openai

GROQ_API_KEY=gsk_...
OPENAI_API_KEY=sk-...
```

### Example 4: Full Redundancy

**Use Case**: Maximum reliability with all providers

```env
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
LLM_FALLBACK_PROVIDERS=anthropic,groq

OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GROQ_API_KEY=gsk_...
```

---

## Provider Characteristics

### OpenAI (GPT-4o-mini)
- **Latency**: ~400-600ms
- **Cost**: $0.15/1M input tokens
- **JSON Mode**: ✅ Native support
- **Best For**: Balanced performance and quality
- **Models**: gpt-4o-mini, gpt-4o, gpt-4-turbo

### Anthropic (Claude 3 Haiku)
- **Latency**: ~500-800ms
- **Cost**: $0.25/1M input tokens
- **JSON Mode**: ✅ Via system prompt
- **Best For**: Safety and reasoning
- **Models**: claude-3-haiku-20240307, claude-3-sonnet, claude-3-opus

### Groq (Llama 3.1 8B)
- **Latency**: ~200-400ms (fastest!)
- **Cost**: Free tier available
- **JSON Mode**: ✅ Native support
- **Best For**: Ultra-low latency
- **Models**: llama-3.1-8b-instant, mixtral-8x7b-32768

---

## How Fallback Works

### Automatic Fallback Flow

```
┌─────────────┐
│ API Request │
└──────┬──────┘
       │
       ▼
┌──────────────────┐
│ Try Primary      │  (e.g., OpenAI)
│ Provider         │
└──────┬───────────┘
       │
       ├──Success──► Return Response
       │
       ▼ Failure
┌──────────────────┐
│ Try Fallback #1  │  (e.g., Anthropic)
│ Provider         │
└──────┬───────────┘
       │
       ├──Success──► Return Response
       │
       ▼ Failure
┌──────────────────┐
│ Try Fallback #2  │  (e.g., Groq)
│ Provider         │
└──────┬───────────┘
       │
       ├──Success──► Return Response
       │
       ▼ Failure
┌──────────────────┐
│ Return Error     │
│ All Failed       │
└──────────────────┘
```

### What Triggers Fallback?

- API key errors (invalid/missing)
- Rate limiting (429 errors)
- Timeout errors
- Network failures
- Service outages
- JSON parsing failures after retries

### Response Metadata

Each successful response includes metadata about which provider was used:

```json
{
  "suggestion": "We can't guarantee specific returns...",
  "alternates": [...],
  "rationale": "...",
  "confidence": 0.85,
  "_provider_used": "anthropic"  // ← Provider metadata
}
```

---

## Monitoring Provider Usage

### Check Provider Status

```bash
# Via API
curl http://localhost:8000/providers/status
```

**Response:**
```json
{
  "primary": "openai",
  "fallbacks": ["anthropic", "groq"],
  "providers": {
    "openai": "available",
    "anthropic": "available",
    "groq": "unavailable: GROQ_API_KEY not found"
  }
}
```

### Track Which Provider Was Used

In your application code:

```python
from app.providers.provider_manager import get_last_provider_used

response = suggest(agent_draft="...")
provider = get_last_provider_used()
print(f"Response from: {provider}")
```

In API responses, check the `_provider_used` field.

---

## Cost Optimization Strategies

### Strategy 1: Groq Primary for Speed + Cost

```env
# Groq is free/cheap and fast
LLM_PROVIDER=groq
LLM_MODEL=llama-3.1-8b-instant
LLM_FALLBACK_PROVIDERS=openai

# Only use OpenAI as backup
GROQ_API_KEY=gsk_...
OPENAI_API_KEY=sk-...
```

**Result**: Most requests use free Groq, OpenAI only for fallback.

### Strategy 2: Haiku Primary for Balance

```env
# Claude Haiku is affordable and good quality
LLM_PROVIDER=anthropic
LLM_MODEL=claude-3-haiku-20240307
LLM_FALLBACK_PROVIDERS=groq

ANTHROPIC_API_KEY=sk-ant-...
GROQ_API_KEY=gsk_...
```

**Result**: Good quality at $0.25/1M tokens with free fallback.

### Strategy 3: Smart Routing (Future Enhancement)

Route based on request complexity:
- Simple requests → Groq (fast/cheap)
- Complex requests → GPT-4o-mini (quality)
- Critical requests → Claude (safety)

---

## Troubleshooting

### Issue: "All LLM providers failed"

**Cause**: No providers are configured correctly.

**Solution**:
1. Check API keys in `.env`
2. Verify at least one key is valid
3. Test each provider:

```bash
# Test OpenAI
python -c "from app.providers.openai_provider import OpenAIProvider; OpenAIProvider()"

# Test Anthropic
python -c "from app.providers.anthropic_provider import AnthropicProvider; AnthropicProvider()"

# Test Groq
python -c "from app.providers.groq_provider import GroqProvider; GroqProvider()"
```

### Issue: "Provider X not available"

**Cause**: Package not installed or API key missing.

**Solution**:
```bash
# Install missing package
pip install anthropic  # or groq

# Add API key to .env
ANTHROPIC_API_KEY=sk-ant-...
```

### Issue: Slow Responses

**Cause**: Using slow primary provider.

**Solution**: Switch to Groq for fastest responses:
```env
LLM_PROVIDER=groq
LLM_MODEL=llama-3.1-8b-instant
```

### Issue: High Costs

**Cause**: Using expensive models.

**Solution**: Use cheaper alternatives:
- OpenAI: `gpt-4o-mini` instead of `gpt-4`
- Anthropic: `claude-3-haiku` instead of `claude-3-opus`
- Groq: Free tier available

---

## Advanced: Provider-Specific Features

### OpenAI

```python
from app.providers.openai_provider import OpenAIProvider

# Custom configuration
provider = OpenAIProvider(
    model="gpt-4o-mini",
    temperature=0,
    max_tokens=160,
    timeout=5,
    max_retries=2
)
```

### Anthropic

```python
from app.providers.anthropic_provider import AnthropicProvider

# Use Claude Opus for better quality
provider = AnthropicProvider(
    model="claude-3-opus-20240229",
    temperature=0,
    max_tokens=160
)
```

### Groq

```python
from app.providers.groq_provider import GroqProvider

# Use Mixtral for better reasoning
provider = GroqProvider(
    model="mixtral-8x7b-32768",
    temperature=0,
    max_tokens=160
)
```

---

## Performance Comparison

Based on typical QA Coach workload (compliance suggestions):

| Provider | Model | Avg Latency | P95 Latency | Cost/1M | Quality |
|----------|-------|-------------|-------------|---------|---------|
| Groq | Llama 3.1 8B | 300ms | 450ms | Free | ⭐⭐⭐⭐ |
| OpenAI | GPT-4o-mini | 500ms | 700ms | $0.15 | ⭐⭐⭐⭐⭐ |
| Anthropic | Claude Haiku | 600ms | 850ms | $0.25 | ⭐⭐⭐⭐⭐ |

**Recommendation**: 
- **Production**: OpenAI primary, Anthropic fallback (best balance)
- **Development**: Groq primary (fast iteration)
- **Cost-sensitive**: Groq primary, OpenAI fallback

---

## Testing Multi-Provider Setup

### Test Script

```python
# test_providers.py
from app.providers.provider_manager import ProviderManager

manager = ProviderManager()

# Test prompt
prompt = {
    "system": "You are a test assistant. Respond with JSON only.",
    "user": "Generate a JSON object with a 'message' field saying 'Hello from [provider name]'"
}

# Try each provider
for provider in manager.provider_chain:
    try:
        result = manager._get_provider_instance(provider).call_llm(prompt)
        print(f"✓ {provider}: {result.get('message', 'OK')}")
    except Exception as e:
        print(f"✗ {provider}: {e}")
```

Run:
```bash
python test_providers.py
```

---

## Migration Guide

### From Single Provider to Multi-Provider

**Before:**
```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
```

**After (with fallback):**
```env
LLM_PROVIDER=openai
LLM_FALLBACK_PROVIDERS=anthropic,groq

OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GROQ_API_KEY=gsk_...
```

**No code changes needed!** The system automatically uses fallback providers.

---

## API Reference

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `LLM_PROVIDER` | Yes | `openai` | Primary provider name |
| `LLM_FALLBACK_PROVIDERS` | No | `` | Comma-separated fallback providers |
| `LLM_MODEL` | No | Provider default | Model name for primary |
| `OPENAI_API_KEY` | If using OpenAI | - | OpenAI API key |
| `ANTHROPIC_API_KEY` | If using Anthropic | - | Anthropic API key |
| `GROQ_API_KEY` | If using Groq | - | Groq API key |
| `ANTHROPIC_MODEL` | No | `claude-3-haiku` | Anthropic model override |
| `GROQ_MODEL` | No | `llama-3.1-8b` | Groq model override |

---

## FAQ

**Q: Can I use multiple providers simultaneously?**  
A: The system tries providers sequentially (fallback), not in parallel.

**Q: Does fallback increase latency?**  
A: Only if the primary fails. Successful primary calls have no overhead.

**Q: Which provider is cheapest?**  
A: Groq offers free tier, then OpenAI gpt-4o-mini ($0.15/1M), then Anthropic Haiku ($0.25/1M).

**Q: Which provider is fastest?**  
A: Groq (~300ms avg) > OpenAI (~500ms) > Anthropic (~600ms).

**Q: Can I add custom providers?**  
A: Yes! Create a provider class with `call_llm(prompt_dict)` method in `app/providers/`.

**Q: How do I monitor which provider is being used?**  
A: Check the `_provider_used` field in responses or use `get_last_provider_used()`.

---

## Support

For issues with specific providers:
- **OpenAI**: https://platform.openai.com/docs
- **Anthropic**: https://docs.anthropic.com/
- **Groq**: https://console.groq.com/docs

For QA Coach multi-provider issues, check the logs or test with:
```bash
curl http://localhost:8000/providers/status
```

---

**Last Updated**: October 22, 2025  
**Version**: 1.1.0 (Multi-Provider Support)
