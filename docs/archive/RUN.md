# QA Compliance Coach - Running Instructions

## 🚀 Quick Start

### Prerequisites
- Python 3.10+ installed
- Virtual environment created and activated
- Dependencies installed (`pip install -r requirements.txt`)
- `.env` file configured with API keys

---

## Running the Application

⚠️ **Database Locking Note:** DuckDB doesn't support multiple processes accessing the same file. Choose one option below:

### Option A: Dashboard Only (✅ Recommended for UI Testing)

```powershell
cd D:\qa_compliance_bot
.\venv\Scripts\Activate.ps1
streamlit run app/dashboard.py
```

**Expected output:**
```
  You can now view your Streamlit app in your browser.
  Local URL: http://localhost:8501
```

✅ **Dashboard at:** http://localhost:8501  
✅ **Live Suggestions tab works perfectly**  
⚠️ **Reports tab requires database** (will show message if no data)

---

### Option B: API Only (✅ Recommended for Integration)

```powershell
cd D:\qa_compliance_bot
.\venv\Scripts\Activate.ps1
uvicorn app.api:app --reload
```

**Expected output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Application startup complete.
```

✅ **API running at:** http://localhost:8000  
📚 **API docs at:** http://localhost:8000/docs

---

###Option C: Both Simultaneously

See `DATABASE_LOCKING_SOLUTION.md` for advanced configuration to run both at the same time.

---

✅ **Dashboard at:** http://localhost:8501

---

## Using the Dashboard

1. **Select a test case** from the dropdown (or enter custom text)
2. **Click "Get Coaching Suggestion"**
3. **View results:**
   - Compliant suggestion
   - Policy violations detected
   - Confidence score
   - Response time

4. **Check Reports tab** for analytics

---

## Testing the API

### Health Check
```powershell
curl http://localhost:8000/health
```

### Get Suggestion
```powershell
curl -X POST http://localhost:8000/coach/suggest -H "Content-Type: application/json" -d '{\"session_id\":\"test\",\"agent_draft\":\"We guarantee 15% returns!\",\"context\":\"\",\"brand_tone\":\"professional\"}'
```

### Provider Status
```powershell
curl http://localhost:8000/providers/status
```

---

## Common Commands

```powershell
# Run all tests
pytest

# Generate synthetic test data
python scripts/seed_synthetic.py

# Validate setup
python scripts/quickstart.py

# Run evaluations
python scripts/run_evals.py --sample 50
```

---

## Stopping the Services

1. **Terminal 1 (API):** Press `Ctrl+C`
2. **Terminal 2 (Dashboard):** Press `Ctrl+C`
3. **Deactivate venv:** `deactivate`

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'app'"

**Solution:**
```powershell
cd D:\qa_compliance_bot          # Must be in project root
.\venv\Scripts\Activate.ps1      # Activate venv
$env:PYTHONPATH = "."            # Set Python path
streamlit run app/dashboard.py  # Run from root
```

### Port Already in Use

**Port 8000 (API):**
```powershell
netstat -ano | findstr :8000
taskkill /PID <PID_NUMBER> /F
```

**Port 8501 (Dashboard):**
```powershell
taskkill /IM streamlit.exe /F
```

### "Execution Policy" Error

```powershell
# Run PowerShell as Administrator
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## URLs

| Service | URL |
|---------|-----|
| Dashboard | http://localhost:8501 |
| API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |
| Health Check | http://localhost:8000/health |

---

## System Configuration

- **Primary LLM:** Groq (llama-3.1-8b-instant) - Fast, free
- **Fallback LLM:** OpenAI (gpt-4o-mini) - Reliable
- **Judge LLM:** OpenAI (gpt-4o-mini) - Quality evaluation
- **Database:** DuckDB (`data/qa_runs.duckdb`)
- **Test Data:** 280+ synthetic cases

---

## Next Steps

1. ✅ Start both services (API + Dashboard)
2. 🧪 Test with sample violations
3. 📊 View analytics in Reports tab
4. 🔍 Explore API docs at `/docs`
5. 📖 Read detailed guides in `docs/` folder

---

**For complete documentation, see:** `START_HERE.md`
