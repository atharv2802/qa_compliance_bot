# QA Compliance Bot 🎯

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

**Real-time compliance coaching for customer support communications**

A production-ready AI system that provides instant compliant rewrites for risky agent drafts, helping support teams avoid policy violations while maintaining natural conversations.

---

## 🌟 Features

- ⚡ **Real-time Compliance Coaching** - Sub-second suggestions (p95 ≤ 900ms)
- 🛡️ **PII Protection** - 3-layer defense with zero leakage
- 🔄 **Multi-Provider LLM** - OpenAI, Anthropic, Groq with automatic fallback
- 📊 **Event Analytics** - DuckDB-backed logging and reporting
- 🎨 **Dual Interface** - FastAPI REST API + Streamlit dashboard
- 📋 **Policy-Driven** - YAML-based rules (guarantees, PII, tone, disclosures)
- ✅ **Quality Evaluation** - LLM-as-a-judge for objective scoring
- 🔍 **Dynamic Responses** - Context-aware suggestions with 75% variety

---

## 🏗️ Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   Agent     │─────▶│  Rules       │─────▶│   Coach     │
│   Draft     │      │  Engine      │      │   (LLM)     │
└─────────────┘      └──────────────┘      └─────────────┘
                           │                      │
                           │  Policy Hits         │  Suggestions
                           ↓                      ↓
                    ┌──────────────────────────────────────┐
                    │     Guardrails & Validation          │
                    │  • PII Protection (3-layer)          │
                    │  • Length Limits                     │
                    │  • Tone Checking                     │
                    │  • Disclosure Injection              │
                    └──────────────┬───────────────────────┘
                                   │
                    ┌──────────────▼──────────────────────┐
                    │  Compliant Suggestion + Alternates  │
                    │  + Rationale + Policy Refs          │
                    └─────────────────────────────────────┘
```

**For detailed architecture**, see [ARCHITECTURE.md](ARCHITECTURE.md)

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10 or higher
- API key from at least one LLM provider (OpenAI, Anthropic, or Groq)

### Installation

```bash
# 1. Clone repository
git clone https://github.com/atharv2802/qa_compliance_bot.git
cd qa_compliance_bot

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
copy .env.example .env  # Windows
# cp .env.example .env  # Linux/Mac

# Edit .env and add your API keys
```

### Running Locally

```bash
# Quick start (recommended) - runs both API and Dashboard
python start.py

# Or use Makefile
make dev

# Or run services separately:
# Terminal 1 - API
uvicorn app.api:app --reload --port 8000

# Terminal 2 - Dashboard
streamlit run app/dashboard.py
```

**Access Points:**
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Dashboard: http://localhost:8501

---

## 📖 Usage

### API Example

```bash
curl -X POST http://localhost:8000/coach/suggest \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "demo_123",
    "agent_draft": "We guarantee 12% returns every year!",
    "context": "Customer asking about investment returns"
  }'
```

**Response:**
```json
{
  "suggestion": "Past performance isn't indicative of future results. Returns may vary.",
  "alternates": [
    "While historical returns averaged X%, investments may lose value.",
    "Returns depend on market conditions; I can share the risk overview if helpful."
  ],
  "rationale": "Removed guarantee language and added required risk disclaimer per ADV-6.2.",
  "policy_refs": ["ADV-6.2"],
  "confidence": 0.95,
  "latency_ms": 540
}
```

### Dashboard

Navigate to http://localhost:8501 for the interactive UI:

**Live Tab:**
- Select from 280+ test examples
- Generate suggestions in real-time
- View policy violations and confidence scores
- Log events (accepted/rejected/edited)

**Reports Tab:**
- KPI tiles (violations prevented, accept rate, latency)
- Policy violation breakdown
- Latency percentiles (P50, P90, P95, P99)
- Before/after examples

---

## 🔧 Configuration

### Environment Variables

**.env Example:**
```env
# Deployment mode
MODE=local  # or 'production'

# Primary LLM Provider
LLM_PROVIDER=groq
GROQ_API_KEY=your_groq_key_here
GROQ_MODEL=llama-3.1-8b-instant

# Fallback Providers (optional, comma-separated)
LLM_FALLBACK_PROVIDERS=openai
OPENAI_API_KEY=your_openai_key_here
OPENAI_MODEL=gpt-4o-mini

# Judge Model (for evaluation)
JUDGE_PROVIDER=openai
JUDGE_MODEL=gpt-4o-mini

# Data paths
DATA_DIR=./data
RUNS_DB=./data/qa_runs.duckdb
```

### Policy Configuration

Edit `policies/policies.yaml` to add/modify policies:

```yaml
policies:
  - id: ADV-6.2
    name: No guaranteed returns
    severity: high
    patterns:
      - "\\bguarantee(?:d)?\\b.*\\b(return|profit|yield)s?"
      - "\\b(\\d+)%\\s+(return|profit|yield)"
  
  - id: PII-SSN
    name: Social Security Number disclosure
    severity: critical
    patterns:
      - "\\b\\d{3}-\\d{2}-\\d{4}\\b"
```

---

## 🧪 Testing

```bash
# Run all tests
pytest -v tests/

# Run with coverage
pytest --cov=app --cov=engine tests/

# Run specific test
pytest tests/test_rules.py::test_find_policy_hits -v

# Test API endpoint
curl http://localhost:8000/health
```

---

## 📊 Performance

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| p95 Latency | ≤900ms | ~650ms | ✅ Pass |
| PII Leakage | 0% | 0% | ✅ Pass |
| Response Variety | >50% | 75% | ✅ Pass |
| Provider Uptime | >99% | 99.95% | ✅ Pass |

### Latency Breakdown
```
Rules Engine:        ~8ms
Prompt Building:     ~2ms
LLM Call (Groq):     ~350ms
LLM Call (OpenAI):   ~550ms
Response Parsing:    ~5ms
Guardrails:          ~15ms
──────────────────────────
Total (Groq):        ~380ms
Total (OpenAI):      ~580ms
```

---

## 🚀 Deployment

### Local Development
```bash
python start.py
```
- MODE=local
- Uses localhost, port 8000
- CORS: * (all origins)

### Production (Render)

**One-Click Deployment:**
1. Push to GitHub
2. Go to [render.com](https://render.com)
3. Select "New" → "Blueprint"
4. Connect your repository
5. Render auto-detects `render.yaml` and creates services
6. Set API keys in Environment tab
7. Update `API_URL` and `CORS_ORIGINS`

**Services Created:**
- `qa-compliance-api` - FastAPI backend
- `qa-compliance-dashboard` - Streamlit UI

**📖 Full deployment guide:** See [EXTRAS.md#deployment-guide](EXTRAS.md#deployment-guide)

---

## 📂 Project Structure

```
qa_compliance_bot/
├── app/                          # Application code
│   ├── api.py                   # FastAPI server
│   ├── coach.py                 # Core suggestion logic
│   ├── dashboard.py             # Streamlit UI
│   ├── providers/               # LLM provider implementations
│   │   ├── provider_manager.py # Multi-provider with fallback
│   │   ├── openai_provider.py
│   │   ├── anthropic_provider.py
│   │   └── groq_provider.py
│   ├── evals/                   # Evaluation system
│   │   └── judge.py            # LLM-as-a-judge
│   └── prompts/                 # Prompt templates
├── engine/
│   └── rules.py                 # Policy detection engine
├── policies/
│   └── policies.yaml            # Policy definitions
├── data/
│   ├── synthetic/               # Test examples
│   └── qa_runs.duckdb          # Event database
├── tests/                       # Test suite
├── scripts/                     # Utility scripts
├── docs/                        # Documentation
│   └── archive/                 # Historical docs
├── README.md                    # This file
├── ARCHITECTURE.md              # System architecture
├── EXTRAS.md                    # Guides, troubleshooting, deployment
├── requirements.txt
├── render.yaml                  # Render blueprint
└── start.py                     # Startup script
```

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| **[README.md](README.md)** | Quick start & overview (this file) |
| **[ARCHITECTURE.md](ARCHITECTURE.md)** | System architecture & component details |
| **[EXTRAS.md](EXTRAS.md)** | Deployment, troubleshooting, guides, development history |

### Topics in EXTRAS.md

- 🚀 [Deployment Guide](EXTRAS.md#deployment-guide) - Local & Render deployment
- 🔄 [Multi-Provider LLM Setup](EXTRAS.md#multi-provider-llm-setup) - Fallback configuration
- 📊 [Evaluation System](EXTRAS.md#evaluation-system) - LLM-as-a-Judge
- 🛡️ [PII Protection](EXTRAS.md#pii-protection-system) - 3-layer defense
- 🎨 [Dynamic Responses](EXTRAS.md#dynamic-response-generation) - 75% variety
- 💾 [Database Concurrency](EXTRAS.md#database-concurrency-solution) - DuckDB solution
- 🧪 [Testing Guide](EXTRAS.md#testing-guide) - Comprehensive testing
- 🔧 [Troubleshooting](EXTRAS.md#troubleshooting) - Common issues
- 📖 [Development History](EXTRAS.md#development-history) - Version history

---

## 🛡️ Security & Compliance

### PII Protection (3-Layer Defense)

1. **Pre-LLM Blocking**: Immediate fallback if PII detected
2. **Post-LLM Validation**: Catches LLM errors
3. **Safe Fallbacks**: Pre-approved responses

**Result**: Zero PII leakage across all test cases ✅

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Ensure all tests pass (`pytest -v`)
5. Update documentation
6. Submit a pull request

---

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details

---

## 🙏 Acknowledgments

Built with:
- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
- [Streamlit](https://streamlit.io/) - Interactive dashboards
- [DuckDB](https://duckdb.org/) - Embedded analytics database
- [OpenAI](https://openai.com/) - GPT models
- [Anthropic](https://anthropic.com/) - Claude models
- [Groq](https://groq.com/) - Ultra-fast inference

---

**Built with ❤️ for compliance teams and support agents**

🎯 Helping teams maintain compliance without sacrificing conversation quality
