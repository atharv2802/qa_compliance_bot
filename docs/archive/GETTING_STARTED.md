# 🚀 Getting Started Checklist

Use this checklist to get your QA Coach system up and running!

## ✅ Phase 1: Initial Setup (5 minutes)

- [ ] **1.1** Copy environment template
  ```bash
  cp .env.example .env
  ```

- [ ] **1.2** Get API keys:
  - [ ] Groq (primary): https://console.groq.com/keys
  - [ ] OpenAI (fallback): https://platform.openai.com/api-keys  
  - [ ] Anthropic (optional): https://console.anthropic.com/

- [ ] **1.3** Configure `.env` file:
  ```bash
  # Required (minimum config)
  GROQ_API_KEY=gsk_...                    # Your Groq API key
  OPENAI_API_KEY=sk-...                   # Your OpenAI API key
  
  # Optional (for additional fallback)
  ANTHROPIC_API_KEY=sk-ant-...            # Your Anthropic API key
  
  # Judge config (using OpenAI for evaluation)
  JUDGE_PROVIDER=openai
  JUDGE_MODEL=gpt-4o-mini
  ```

- [ ] **1.4** Install dependencies:
  ```bash
  pip install -r requirements.txt
  ```

## ✅ Phase 2: Verification (10 minutes)

- [ ] **2.1** Run tests to verify installation:
  ```bash
  pytest
  ```
  Expected: 70+ tests pass

- [ ] **2.2** Check provider status:
  ```bash
  python scripts/demo_providers.py
  ```
  Expected: All configured providers show as "available"

- [ ] **2.3** Generate test data:
  ```bash
  python scripts/seed_synthetic.py
  ```
  Expected: 150+ test cases created in database

- [ ] **2.4** Run batch evaluation:
  ```bash
  python scripts/run_evals.py
  ```
  Expected: Evaluation summary with scores

## ✅ Phase 3: Start Services (2 minutes)

- [ ] **3.1** Start API server (Terminal 1):
  ```bash
  uvicorn app.api:app --reload
  ```
  Expected: Server running on http://localhost:8000

- [ ] **3.2** Test API health:
  ```bash
  curl http://localhost:8000/health
  ```
  Expected: `{"status":"healthy","version":"1.0.0"}`

- [ ] **3.3** Start Dashboard (Terminal 2):
  ```bash
  streamlit run app/dashboard.py
  ```
  Expected: Dashboard running on http://localhost:8501

## ✅ Phase 4: Test Core Features (10 minutes)

### Test 1: Suggestion Generation

- [ ] **4.1** Via API:
  ```bash
  curl -X POST http://localhost:8000/coach/suggest \
    -H "Content-Type: application/json" \
    -d '{
      "session_id": "test1",
      "agent_draft": "We guarantee 12% returns every year!",
      "context": "Customer asking about returns"
    }'
  ```
  Expected: JSON response with suggestion, alternates, policy_refs

- [ ] **4.2** Via Dashboard:
  - Go to http://localhost:8501
  - Enter draft: "We guarantee 12% returns every year!"
  - Click "Get Suggestion"
  - Expected: Compliant suggestion appears

### Test 2: Evaluation System

- [ ] **4.3** Via API:
  ```bash
  curl -X POST http://localhost:8000/evals/judge \
    -H "Content-Type: application/json" \
    -d '{
      "agent_draft": "We guarantee 12% returns!",
      "suggestion": "Past results do not guarantee future returns.",
      "policy_refs": ["ADV-6.2"]
    }'
  ```
  Expected: JSON with scores (compliance, clarity, tone, etc.)

- [ ] **4.4** Via Python:
  ```bash
  python scripts/demo_workflow.py
  ```
  Expected: Complete workflow demo showing all features

### Test 3: Provider Fallback

- [ ] **4.5** Check provider status:
  ```bash
  curl http://localhost:8000/providers/status
  ```
  Expected: Shows primary=groq, fallbacks=[openai, anthropic]

- [ ] **4.6** Test with invalid primary key (optional):
  - Temporarily break GROQ_API_KEY in .env
  - Make a suggestion request
  - Expected: Falls back to OpenAI automatically
  - Restore GROQ_API_KEY afterward

### Test 4: Event Logging

- [ ] **4.7** Make a few suggestion requests
- [ ] **4.8** Check event stats:
  ```bash
  curl http://localhost:8000/events/stats
  ```
  Expected: Shows total_events, event_counts, recent_events

- [ ] **4.9** View dashboard Reports tab
  Expected: Charts and KPIs showing logged events

## ✅ Phase 5: Customization (Optional)

- [ ] **5.1** Review policies:
  - Open `policies/policies.yaml`
  - Review existing policies (ADV-6.2, PII-SSN, DISC-1.1, TONE)
  - Add custom policies as needed

- [ ] **5.2** Tune coach prompts:
  - Open `app/prompts/coach_prompt_v1.txt`
  - Customize tone, style, instructions
  - Restart API server to apply changes

- [ ] **5.3** Adjust evaluation threshold:
  - Default pass threshold: 7.0
  - Modify in `app/evals/judge.py` if needed

- [ ] **5.4** Configure A/B testing:
  - Set AB_TEST_BUCKET in .env (on/off)
  - Track metrics via /events/stats

## ✅ Phase 6: Production Readiness (Optional)

- [ ] **6.1** Performance testing:
  - Run load tests on /coach/suggest
  - Verify p95 latency < 900ms
  - Monitor with Groq (~350ms) vs OpenAI (~550ms)

- [ ] **6.2** Monitoring setup:
  - Set up alerts for /health endpoint
  - Monitor /providers/status for failures
  - Track /events/stats for usage patterns

- [ ] **6.3** Backup strategy:
  - DuckDB database: `./data/qa_runs.duckdb`
  - Set up regular backups
  - Consider replication for high availability

- [ ] **6.4** Cost monitoring:
  - Groq: Free tier (check usage limits)
  - OpenAI: Track token usage ($0.15/1M)
  - Anthropic: Track token usage ($0.25/1M)

- [ ] **6.5** Security review:
  - API keys secured (never commit to git)
  - CORS configured appropriately
  - Rate limiting considered
  - PII handling verified

## 📊 Success Criteria

Your system is ready when:

✅ All tests pass (pytest shows 70+ passing tests)
✅ API responds to /health with "healthy"
✅ Dashboard loads and shows suggestions
✅ Provider fallback works (primary → fallback1 → fallback2)
✅ Evaluations return scores (0-10 scale)
✅ Events logged to DuckDB
✅ Latency < 900ms for /coach/suggest
✅ Evaluation pass rate > 80%

## 🎯 Quick Commands Reference

```bash
# Installation
pip install -r requirements.txt

# Testing
pytest                                    # All tests
pytest tests/test_judge.py               # Evaluation tests
python scripts/run_evals.py              # Batch evaluation

# Services
uvicorn app.api:app --reload            # Start API (port 8000)
streamlit run app/dashboard.py          # Start dashboard (port 8501)

# Demos
python scripts/demo_providers.py        # Provider status
python scripts/demo_workflow.py         # Complete workflow

# Data
python scripts/seed_synthetic.py        # Generate test data

# Health Checks
curl http://localhost:8000/health       # API health
curl http://localhost:8000/providers/status  # Provider status
curl http://localhost:8000/events/stats     # Event statistics
```

## 🆘 Troubleshooting

### Issue: Tests fail with import errors
**Solution:** Install dependencies: `pip install -r requirements.txt`

### Issue: API returns 500 error
**Solution:** 
1. Check .env file has valid API keys
2. Check /providers/status endpoint
3. Review logs for specific error

### Issue: Provider fallback not working
**Solution:**
1. Verify LLM_FALLBACK_PROVIDERS is set in .env
2. Check all provider API keys are valid
3. Test with: `python scripts/demo_providers.py`

### Issue: Low evaluation scores
**Solution:**
1. Review judge feedback in eval results
2. Tune coach prompts in `app/coach.py`
3. Update policies in `policies/policies.yaml`
4. Try different judge models

### Issue: High latency
**Solution:**
1. Use Groq as primary (fastest: ~300ms)
2. Run evaluations async or in batch
3. Check network connectivity
4. Monitor provider status

### Issue: Database errors
**Solution:**
1. Run: `python scripts/seed_synthetic.py`
2. Check data directory exists
3. Verify DuckDB installed: `pip install duckdb`

## 📚 Documentation

- **README.md** - Main documentation
- **MULTI_PROVIDER_GUIDE.md** - Provider setup (400+ lines)
- **EVALS_GUIDE.md** - Evaluation system (500+ lines)
- **SYSTEM_OVERVIEW.md** - Complete system (400+ lines)
- **ARCHITECTURE.md** - System diagrams (500+ lines)
- **IMPLEMENTATION_COMPLETE.md** - Implementation summary

## 🎓 Learning Path

1. **Start Here:** README.md
2. **Setup Providers:** MULTI_PROVIDER_GUIDE.md
3. **Run Demo:** `python scripts/demo_workflow.py`
4. **Add Evaluations:** EVALS_GUIDE.md
5. **Customize:** Edit policies.yaml and prompts
6. **Deploy:** Follow Production Readiness checklist

## ✨ Next Steps

After completing this checklist:

1. **Test with real data**: Replace synthetic data with actual use cases
2. **Tune for your domain**: Customize policies and prompts
3. **Monitor performance**: Track latency and quality metrics
4. **Iterate**: Use evaluation feedback to improve
5. **Scale**: Add load balancing, caching, rate limiting

---

**Status:** System ready when all Phase 1-4 items are checked ✅

**Support:** Review documentation or check error messages for guidance

**Version:** 1.0.0 | Last Updated: October 22, 2025
