# QA Coach - Command Cheat Sheet

## 🚀 START THE APP

### Terminal 1 - API
```powershell
cd D:\qa_compliance_bot
.\venv\Scripts\Activate.ps1
uvicorn app.api:app --reload
```
→ http://localhost:8000

### Terminal 2 - Dashboard
```powershell
cd D:\qa_compliance_bot
.\venv\Scripts\Activate.ps1
streamlit run app/dashboard.py
```
→ http://localhost:8501

**Note:** No need to set PYTHONPATH - it's handled automatically!

---

## 🧪 TESTING

```powershell
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_coach_guardrails.py -v
```

---

## 🌱 DATA GENERATION

```powershell
# Generate 280+ synthetic test cases
python scripts/seed_synthetic.py

# Validate setup
python scripts/quickstart.py

# Run evaluations
python scripts/run_evals.py --sample 50
```

---

## 🔍 API TESTING

```powershell
# Health check
curl http://localhost:8000/health

# Provider status
curl http://localhost:8000/providers/status

# Test suggestion
curl -X POST http://localhost:8000/coach/suggest -H "Content-Type: application/json" -d '{\"session_id\":\"test\",\"agent_draft\":\"We guarantee 15% returns!\",\"context\":\"\",\"brand_tone\":\"professional\"}'
```

---

## 🛑 STOP SERVICES

1. Press `Ctrl+C` in API terminal
2. Press `Ctrl+C` in Dashboard terminal
3. `deactivate` (to exit venv)

---

## ⚡ TROUBLESHOOTING

### Module not found
```powershell
cd D:\qa_compliance_bot
$env:PYTHONPATH = "."
```

### Port in use
```powershell
# Kill port 8000
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Kill Streamlit
taskkill /IM streamlit.exe /F
```

### Execution policy
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## 📍 IMPORTANT URLS

- Dashboard: http://localhost:8501
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

---

## 📝 CONFIGURATION

**Edit `.env` to change:**
- LLM_PROVIDER (groq, openai)
- LLM_MODEL
- API keys
- Judge provider/model

**Current setup:**
- Primary: Groq (llama-3.1-8b-instant)
- Fallback: OpenAI (gpt-4o-mini)
- Judge: OpenAI (gpt-4o-mini)
