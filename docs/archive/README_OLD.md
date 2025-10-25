# QA Compliance Bot 🎯# QA Coach 🎯



**Real-time compliance coaching for customer support communications**A production-quality **Conversational QA Coach** that provides real-time compliant rewrites for risky agent drafts in chat/email communications.



A production-ready AI system that provides instant compliant rewrites for risky agent drafts, helping support teams avoid policy violations while maintaining natural conversations.## Features



[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)- **Real-time Compliance Coaching**: Analyzes agent drafts against policy rules and suggests compliant alternatives

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)- **Multi-Provider LLM Support**: OpenAI, Anthropic Claude, and Groq with automatic fallback

- **LLM-as-a-Judge Evaluation**: Independent quality assessment using a separate model for objective scoring

---- **Low Latency**: p95 ≤ 900ms with rule-based detection + LLM rewriting + guardrails

- **Dual Interface**: FastAPI JSON API + Streamlit dashboard

## 🌟 Features- **Policy-Driven**: YAML-based policies with regex patterns for guaranteed returns, PII, tone, and disclosures

- **Event Logging**: DuckDB-backed logging for A/B testing and "Coach Effect" metrics

- ⚡ **Real-time Compliance Coaching** - Sub-second suggestions (p95 ≤ 900ms)- **Guardrails**: Pre/post-validation, PII blocking, output length limits, disclosure injection

- 🛡️ **PII Protection** - 3-layer defense with zero leakage

- 🔄 **Multi-Provider LLM** - OpenAI, Anthropic, Groq with automatic fallback## Architecture

- 📊 **Event Analytics** - DuckDB-backed logging and reporting

- 🎨 **Dual Interface** - FastAPI REST API + Streamlit dashboard```

- 📋 **Policy-Driven** - YAML-based rules (guarantees, PII, tone, disclosures)┌─────────────┐      ┌──────────────┐      ┌─────────────┐

- ✅ **Quality Evaluation** - LLM-as-a-judge for objective scoring│   Agent     │─────▶│  Rules       │─────▶│   Coach     │

- 🔍 **Dynamic Responses** - Context-aware suggestions with 75% variety│   Draft     │      │  Engine      │      │   (LLM)     │

└─────────────┘      └──────────────┘      └─────────────┘

---                           │                      │

                           │                      │

## 🚀 Quick Start                    ┌──────▼──────────────────────▼──────┐

                    │     Guardrails & Validation        │

### Prerequisites                    └────────────────┬───────────────────┘

- Python 3.10 or higher                                     │

- OpenAI API key (or Anthropic/Groq)                    ┌────────────────▼───────────────────┐

                    │   Compliant Suggestion + Alts      │

### Installation                    │   + Rationale + Policy Refs        │

                    └────────────────────────────────────┘

```bash```

# 1. Clone repository

git clone <repo-url>## Tech Stack

cd qa_compliance_bot

- **Python 3.10+**

# 2. Create virtual environment- **FastAPI** + Uvicorn (API server)

python -m venv venv- **Streamlit** (Interactive dashboard)

source venv/bin/activate  # On Windows: venv\Scripts\activate- **LLM Providers** (with automatic fallback):

  - OpenAI GPT-4o-mini (primary, temperature=0, max_tokens≈160)

# 3. Install dependencies  - Anthropic Claude 3 Haiku (fallback option)

pip install -r requirements.txt  - Groq Llama 3.1 (ultra-fast fallback option)

- **DuckDB** (Event logging and analytics)

# 4. Configure environment- **YAML** (Policy definitions)

cp .env.example .env- **Regex** (Fast rule matching)

# Edit .env and add your API key(s)- **Presidio** (Optional PII detection)

- **pytest** (Testing)

# 5. Generate seed data- **ruff/black** (Code quality)

python scripts/seed_synthetic.py

```## Getting Started



### Running the System### Prerequisites



```bash- Python 3.10 or higher

# Option 1: Run both services (recommended)- OpenAI API key

make dev

# API: http://localhost:8000### Installation

# Dashboard: http://localhost:8501

1. **Clone the repository**:

# Option 2: Run separately   ```bash

# Terminal 1   git clone <repo-url>

uvicorn app.api:app --reload --port 8000   cd qa-coach

   ```

# Terminal 2

streamlit run app/dashboard.py2. **Install dependencies**:

```   ```bash

   make install

---   # or

   pip install -r requirements.txt

## 📖 Usage   ```



### API Example3. **Configure environment**:

   ```bash

```bash   cp .env.example .env

curl -X POST http://localhost:8000/coach/suggest \   # Edit .env and configure your LLM provider(s)

  -H "Content-Type: application/json" \   

  -d '{   # Minimum config (OpenAI only):

    "session_id": "demo_123",   LLM_PROVIDER=openai

    "agent_draft": "We guarantee 12% returns every year!",   OPENAI_API_KEY=sk-...

    "context": "Customer asking about investment returns"   

  }'   # Or with fallback for reliability:

```   LLM_PROVIDER=openai

   LLM_FALLBACK_PROVIDERS=anthropic,groq

**Response:**   OPENAI_API_KEY=sk-...

```json   ANTHROPIC_API_KEY=sk-ant-...

{   GROQ_API_KEY=gsk_...

  "suggestion": "Past performance isn't indicative of future results. Returns may vary. Investments may lose value.",   ```

  "alternates": [   

    "While historical returns averaged X%, investments may lose value.",   See [MULTI_PROVIDER_GUIDE.md](MULTI_PROVIDER_GUIDE.md) for detailed provider configuration.

    "Returns depend on market conditions; I can share the risk overview if helpful."

  ],4. **Generate synthetic seed data**:

  "rationale": "Removed guarantee language and added required risk disclaimer per ADV-6.2.",   ```bash

  "policy_refs": ["ADV-6.2"],   make seed

  "confidence": 0.95,   # or

  "latency_ms": 540   python scripts/seed_synthetic.py

}   ```

```

### Running the System

### Dashboard

#### Option 1: Run Everything (Recommended for Demo)

Navigate to `http://localhost:8501` for the interactive UI:

```bash

**Live Tab:**make dev

- Select from 280+ test examples```

- Generate suggestions in real-time

- View policy violations and confidence scoresThis starts both the API (port 8000) and Streamlit UI (port 8501).

- Log events (accepted/rejected/edited)

#### Option 2: Run Components Separately

**Reports Tab:**

- KPI tiles (violations prevented, accept rate, latency)**Terminal 1 - API Server**:

- Policy violation breakdown```bash

- Latency percentiles (P50, P90, P95, P99)make api

- Before/after examples# or

uvicorn app.api:app --reload --port 8000

---```



## 🏗️ Architecture**Terminal 2 - Streamlit Dashboard**:

```bash

```make ui

┌─────────────────┐      ┌──────────────┐      ┌─────────────┐# or

│  Agent Draft    │─────▶│ Rules Engine │─────▶│   Coach     │streamlit run app/dashboard.py

│  (Risky Text)   │      │ (Detection)  │      │   (LLM)     │```

└─────────────────┘      └──────────────┘      └─────────────┘

                               │                      │### Testing

                               │  Policy Hits         │  Suggestions

                               ↓                      ↓Run the test suite:

                    ┌──────────────────────────────────────┐```bash

                    │     Guardrails & Validation          │make test

                    │  • PII Protection (3-layer)          │# or

                    │  • Length Limits                     │pytest -v tests/

                    │  • Tone Checking                     │```

                    │  • Disclosure Injection              │

                    └──────────────┬───────────────────────┘### Generate Reports

                                   │

                    ┌──────────────▼──────────────────────┐```bash

                    │  Compliant Suggestion + Alternates  │make report

                    │  + Rationale + Policy Refs          │# or

                    └─────────────────────────────────────┘python reports/aggregations.py

``````



**For detailed architecture**, see [ARCHITECTURE.md](ARCHITECTURE.md)Reports are saved to `data/reports/CoachEffect_<date>.html`



---## Usage



## 📂 Project Structure### API Endpoints



```#### POST /coach/suggest

qa_compliance_bot/

├── app/                          # Application codeRequest a compliant rewrite for an agent draft.

│   ├── api.py                   # FastAPI server

│   ├── coach.py                 # Core suggestion logic**Request**:

│   ├── dashboard.py             # Streamlit UI```json

│   ├── providers/               # LLM provider implementations{

│   │   ├── provider_manager.py # Multi-provider with fallback  "session_id": "s42",

│   │   ├── openai_provider.py  "agent_draft": "We guarantee 12% returns.",

│   │   ├── anthropic_provider.py  "context": "Customer asked if returns are certain.",

│   │   └── groq_provider.py  "policy_hits": ["ADV-6.2"],

│   ├── evals/                   # Evaluation system  "brand_tone": "professional, clear, empathetic",

│   │   └── judge.py            # LLM-as-a-judge  "required_disclosures": ["We cannot guarantee returns; investments may lose value."]

│   └── prompts/}

│       ├── coach_prompt_v1.txt```

│       └── coach_prompt_v2.txt  # Enhanced with PII protection

├── engine/**Response**:

│   └── rules.py                 # Policy detection engine```json

├── policies/{

│   └── policies.yaml            # Policy definitions  "suggestion": "We can't guarantee specific returns. Past performance isn't indicative of future results.",

├── data/  "alternates": [

│   ├── synthetic/    "Returns aren't guaranteed; I can share historical performance and risks.",

│   │   └── coach_cases.jsonl   # Test examples    "We don't promise fixed returns—outcomes depend on market conditions."

│   └── qa_runs.duckdb          # Event database  ],

├── tests/                       # Test suite  "rationale": "Removes guarantee language and adds risk context per ADV-6.2.",

├── scripts/                     # Utility scripts  "policy_refs": ["ADV-6.2"],

├── docs/  "confidence": 0.86,

│   └── archive/                 # Historical documentation  "evidence_spans": [[3, 24]]

├── README.md                    # This file}

├── ARCHITECTURE.md              # System architecture```

├── EXTRAS.md                    # Additional guides & troubleshooting

├── requirements.txt#### POST /events/coach

└── Makefile

```Log a coaching event (offered/accepted/edited/rejected/timeout).



---**Request**:

```json

## 🔧 Configuration{

  "event": "accepted",

### Environment Variables  "session_id": "s42",

  "agent_draft": "We guarantee 12% returns.",

**.env Example:**  "suggestion_used": "We can't guarantee specific returns...",

```env  "policy_refs": ["ADV-6.2"],

# Primary LLM Provider  "latency_ms": 640,

LLM_PROVIDER=openai  "ab_test_bucket": "on"

OPENAI_API_KEY=sk-proj-...}

OPENAI_MODEL=gpt-4o-mini```



# Optional: Fallback Providers (comma-separated)#### POST /evals/judge

LLM_FALLBACK_PROVIDERS=anthropic,groq

ANTHROPIC_API_KEY=sk-ant-...Evaluate a suggestion using LLM-as-a-judge for quality assessment.

GROQ_API_KEY=gsk_...

**Request**:

# Optional: Model Selection```json

ANTHROPIC_MODEL=claude-3-haiku-20240307{

GROQ_MODEL=llama-3.1-8b-instant  "agent_draft": "We guarantee 12% returns every year.",

```  "suggestion": "Historical performance has varied, and past results don't guarantee future returns.",

  "policy_refs": ["ADV-6.2"],

### Policy Configuration  "context": "Customer asking about returns",

  "required_disclosures": []

Edit `policies/policies.yaml` to add/modify policies:}

```

```yaml

policies:**Response**:

  - id: ADV-6.2```json

    name: No guaranteed returns{

    severity: high  "overall_score": 8.5,

    patterns:  "compliance_score": 9.0,

      - "\\bguarantee(?:d)?\\b.*\\b(return|profit|yield)s?"  "clarity_score": 8.5,

      - "\\b(\\d+)%\\s+(return|profit|yield)"  "tone_score": 8.0,

      "completeness_score": 8.5,

  - id: PII-SSN  "feedback": "Strong compliance rewrite with clear risk language",

    name: Social Security Number disclosure  "strengths": ["Addresses policy violation", "Professional tone"],

    severity: critical  "weaknesses": ["Could be more specific about historical data"],

    patterns:  "pass_threshold": true

      - "\\b\\d{3}-\\d{2}-\\d{4}\\b"}

``````



---### Streamlit Dashboard



## 🧪 TestingNavigate to `http://localhost:8501` to access the interactive dashboard.



```bash**Live Tab**:

# Run all tests- Enter agent drafts or select from synthetic examples

pytest -v tests/- View real-time suggestions with alternates

- See policy violations, confidence scores, and rationale

# Run with coverage- Action buttons: Use / Use & Edit / Reject

pytest --cov=app --cov=engine tests/

**Reports Tab**:

# Run specific test- KPI tiles: Violations prevented, Accept rate, p95 latency

pytest tests/test_rules.py::test_find_policy_hits -v- Bar charts: Prevention by policy

- A/B comparison (on vs off)

# Test API endpoints- Before→After examples table

curl http://localhost:8000/health

```## Policy Configuration



---Policies are defined in `policies/policies.yaml`:



## 📊 Performance```yaml

policies:

| Metric | Target | Actual | Status |  - id: ADV-6.2

|--------|--------|--------|--------|    name: No guaranteed returns

| p95 Latency | ≤900ms | ~650ms | ✅ Pass |    severity: high

| PII Leakage | 0% | 0% | ✅ Pass |    patterns: ["\\bguarantee(?:d)?\\b.*\\b(return|profit|yield)s?"]

| Response Variety | >50% | 75% | ✅ Pass |  

| Provider Uptime | >99% | 99.95% | ✅ Pass |  - id: PII-SSN

    name: No full SSN

### Latency Breakdown    severity: critical

```    patterns: ["\\b\\d{3}-\\d{2}-\\d{4}\\b"]

Rules Engine:        ~8ms  

Prompt Building:     ~2ms  - id: DISC-1.1

LLM Call (Groq):     ~350ms    name: Required disclosure present

LLM Call (OpenAI):   ~550ms    severity: medium

Response Parsing:    ~5ms    required_phrases: ["this is not financial advice"]

Guardrails:          ~15ms  

──────────────────────────  - id: TONE

Total (Groq):        ~380ms    name: Inappropriate tone

Total (OpenAI):      ~580ms    severity: low

```    patterns: ["\\bidiot\\b", "\\bstupid\\b"]

```

---

## Project Structure

## 📚 Documentation

```

| Document | Description |qa-coach/

|----------|-------------|├── policies/

| **[README.md](README.md)** | Quick start & overview (this file) |│   └── policies.yaml              # Policy definitions

| **[ARCHITECTURE.md](ARCHITECTURE.md)** | System architecture & component details |├── app/

| **[EXTRAS.md](EXTRAS.md)** | Additional guides, troubleshooting, development history |│   ├── api.py                     # FastAPI server

| **[docs/archive/](docs/archive/)** | Historical documentation & fix summaries |│   ├── coach.py                   # Core suggestion logic

│   ├── dashboard.py               # Streamlit UI

### Key Topics in EXTRAS.md│   ├── providers/

│   │   └── openai_provider.py    # LLM interface

- 🔄 Multi-Provider LLM Setup│   ├── evals/

- 📊 Evaluation System (LLM-as-a-Judge)│   │   ├── __init__.py

- 🛡️ PII Protection System│   │   └── judge.py               # LLM-as-a-judge evaluation

- 🎨 Dynamic Response Generation│   └── prompts/

- 💾 Database Concurrency Solution│       └── coach_prompt_v1.txt   # Prompt template

- 🧪 Testing Guide├── engine/

- 🔧 Troubleshooting│   └── rules.py                   # Rule engine

- 📖 Development History├── reports/

│   ├── aggregations.py            # KPI calculations

---│   └── templates/

│       └── report.html.j2         # HTML report template

## 🛡️ Security & Compliance├── data/

│   ├── synthetic/

### PII Protection (3-Layer Defense)│   │   └── coach_cases.jsonl     # Seed data

│   ├── runs/                      # Event logs

1. **Pre-LLM Blocking**: Immediate fallback if PII detected│   └── qa_runs.duckdb            # DuckDB database

2. **Post-LLM Validation**: Catches LLM errors├── tests/

3. **Safe Fallbacks**: Pre-approved responses│   ├── test_rules.py

│   ├── test_coach_guardrails.py

**Result**: Zero PII leakage across all test cases ✅│   ├── test_judge.py              # Evaluation tests

│   └── test_provider_manager.py   # Multi-provider tests

### Safe Fallback Templates├── scripts/

│   ├── seed_synthetic.py          # Generate test data

```python│   ├── run_evals.py               # Run batch evaluations

{│   └── demo_providers.py          # Demo multi-provider fallback

    "PII-SSN": "I've verified your information successfully.",├── configs/

    "ADV-6.2": "Past performance isn't indicative of future results.",│   └── config.yaml                # App configuration

    "DISC-1.1": "Investments may lose value; see risk disclosure.",├── .env.example

    "TONE": "I understand your concern. Let me help."├── requirements.txt

}├── Makefile

```├── README.md

├── MULTI_PROVIDER_GUIDE.md        # Multi-provider setup guide

---└── EVALS_GUIDE.md                 # Evaluation system guide

```

## 🎯 Key Features Deep Dive

## Performance

### 1. Multi-Provider Fallback

- **Target p95 latency**: ≤ 900ms for `/coach/suggest`

**Reliability**: 99.95%+ uptime with 2+ providers- **Components**:

  - Rule matching: ~5-10ms

```  - LLM call (Groq): ~300-400ms or (GPT-4o-mini): ~500-600ms

Request → OpenAI (primary)  - Guardrails & validation: ~10-20ms

    ↓ (on failure)  - Total: ~350-700ms (well under target)

Request → Anthropic (fallback 1)

    ↓ (on failure)## Evaluation

Request → Groq (fallback 2)

```### LLM-as-a-Judge Quality Assessment



### 2. Dynamic Response GenerationThe system includes an independent evaluation module that uses a separate LLM to assess suggestion quality:



**75% variety rate** vs. 0% before enhancement```bash

# Run batch evaluations on sample cases

- Context-aware promptspython scripts/run_evals.py

- Alternate rotation (60% chance to vary)

- Temperature tuning (0.7 for creativity)# Evaluate from database

python scripts/run_evals.py --db --limit 100

### 3. LLM-as-a-Judge Evaluation```



Independent quality scoring (0-10 scale):**Evaluation Criteria (0-10 scale each):**

- Compliance- **Compliance**: Addresses all policy violations

- Clarity- **Clarity**: Clear and easy to understand

- Tone- **Tone**: Professional and empathetic

- Completeness- **Completeness**: Preserves original intent

- Overall (≥7.0 = passing)- **Overall**: Holistic quality (≥7.0 = passing)



---See [EVALS_GUIDE.md](EVALS_GUIDE.md) for detailed documentation.



## 🚧 Troubleshooting## Development



### Common Issues### Code Quality



**"All LLM providers failed"**```bash

```bash# Lint

# Check API keysmake lint

cat .env | grep API_KEY# or

ruff check .

# Test provider

curl https://api.openai.com/v1/models \# Format

  -H "Authorization: Bearer $OPENAI_API_KEY"make format

```# or

black .

**"Database is locked"**```

```bash

# Ensure only API server accesses DB### Adding New Policies

# Dashboard should use API endpoints

pkill -f "python.*dashboard.py"1. Edit `policies/policies.yaml`

```2. Add patterns or required_phrases

3. Restart the API server

**"PII leakage detected" in logs**4. Test with new examples

- ✅ This is **expected and correct**!

- Validation layer caught LLM trying to leak PII### Adding New LLM Providers

- System working as designed

1. Create `app/providers/<provider>_provider.py`

**For more troubleshooting**, see [EXTRAS.md](EXTRAS.md)2. Implement `call_llm(prompt_dict)` interface

3. Update `.env`:

---   ```env

   LLM_PROVIDER=<provider>

## 🤝 Contributing   <PROVIDER>_API_KEY=...

   ```

Contributions welcome! Please:4. Optionally add to fallback chain:

   ```env

1. Fork the repository   LLM_FALLBACK_PROVIDERS=openai,anthropic,groq

2. Create a feature branch   ```

3. Add tests for new features

4. Ensure all tests pass (`pytest -v`)See [MULTI_PROVIDER_GUIDE.md](MULTI_PROVIDER_GUIDE.md) for examples.

5. Update documentation

6. Submit a pull request## License



---MIT



## 📝 License## Contributing



MIT License - see [LICENSE](LICENSE) file for detailsContributions welcome! Please ensure tests pass and code is formatted before submitting PRs.



------



## 🙏 AcknowledgmentsBuilt with ❤️ for compliance teams and support agents.


Built with:
- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
- [Streamlit](https://streamlit.io/) - Interactive dashboards
- [DuckDB](https://duckdb.org/) - Embedded analytics database
- [OpenAI](https://openai.com/) - GPT models
- [Anthropic](https://anthropic.com/) - Claude models
- [Groq](https://groq.com/) - Ultra-fast inference

---

## 📧 Contact

For questions, issues, or feature requests, please open an issue on GitHub.

---

**Built with ❤️ for compliance teams and support agents**

🎯 Helping teams maintain compliance without sacrificing conversation quality
 
 - - -  
  
 # #     D e p l o y m e n t  
 