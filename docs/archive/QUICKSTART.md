# QA Compliance Coach - Quick Start Guide

## ✅ Prerequisites Completed
- ✅ Virtual environment created and activated
- ✅ All dependencies installed
- ✅ API keys configured in `.env`
- ✅ All 66 tests passing

---

## 🚀 Running the Application

### Step 1: Activate Virtual Environment (if not already active)

```powershell
# Navigate to project directory
cd D:\qa_compliance_bot

# Activate virtual environment
.\venv\Scripts\Activate.ps1
```

**Expected output:** Your prompt should show `(venv)` at the beginning

---

### Step 2: Verify Database Exists

```powershell
# Check if database file exists
Test-Path .\qa_coach.duckdb
```

**If it returns `False`**, the database will be created automatically when you start the app.

---

### Step 3: (Optional) Seed Synthetic Test Data

Generate 280+ realistic test cases for demonstration:

```powershell
python scripts/seed_synthetic.py
```

**Expected output:**
```
✅ Generated 280+ synthetic events
📊 Breakdown:
   - ADV-6.2 (Guaranteed Returns): 93 cases
   - DISC-1.1 (Missing Disclosure): 26 cases
   - PII-SSN (SSN Exposure): 17 cases
   - TONE (Unprofessional): 23 cases
   - CLEAN (No Violations): 50 cases
   - Multi-violation cases: 71 cases
```

---

### Step 4: Start the FastAPI Backend

Open a **new terminal** (keep it running):

```powershell
# Terminal 1 - API Server
cd D:\qa_compliance_bot
.\venv\Scripts\Activate.ps1
uvicorn app.api:app --reload --host 0.0.0.0 --port 8000
```

**Expected output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [xxxxx] using WatchFiles
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**✅ API is now running at:** http://localhost:8000

**Test it:** Open browser and go to http://localhost:8000/docs (Interactive API documentation)

---

### Step 5: Start the Streamlit Dashboard

Open **another new terminal** (keep both running):

```powershell
# Terminal 2 - Dashboard
cd D:\qa_compliance_bot
.\venv\Scripts\Activate.ps1
streamlit run app/dashboard.py
```

**Expected output:**
```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```

**✅ Dashboard is now running at:** http://localhost:8501

---

## 🎯 Using the Application

### Option A: Interactive Dashboard (Recommended for Testing)

1. Open: http://localhost:8501
2. Navigate to **"Live Coaching"** tab
3. Enter sample agent text:
   ```
   Hi! I can guarantee you'll get 15% returns on this investment with zero risk!
   ```
4. Click **"Get Coach Suggestion"**
5. View:
   - 🚨 Policy violations detected
   - ✅ Compliant suggestion
   - 📊 Confidence score
   - 🎯 LLM-as-a-judge evaluation

6. Navigate to **"Reports"** tab to see analytics:
   - Violation trends over time
   - Policy hit frequencies
   - Average confidence scores
   - Top violation types

---

### Option B: API Endpoints (For Integration)

#### 1. Health Check
```powershell
curl http://localhost:8000/health
```

#### 2. Get Suggestion
```powershell
curl -X POST "http://localhost:8000/suggest" `
  -H "Content-Type: application/json" `
  -d '{
    "agent_draft": "I guarantee 15% returns with no risk!",
    "case_id": "TEST-001",
    "agent_id": "AGT-123"
  }'
```

**Response:**
```json
{
  "suggestion": "I'd be happy to discuss potential investment returns...",
  "alternates": ["Alternative 1", "Alternative 2"],
  "rationale": "Original text violated ADV-6.2 (Guaranteed Returns)...",
  "policy_refs": ["ADV-6.2"],
  "confidence": 0.89,
  "latency_ms": 1250,
  "provider_used": "groq"
}
```

#### 3. Evaluate Suggestion (LLM-as-a-Judge)
```powershell
curl -X POST "http://localhost:8000/evals/judge" `
  -H "Content-Type: application/json" `
  -d '{
    "original_text": "I guarantee 15% returns!",
    "coach_suggestion": "I can discuss potential returns based on historical data.",
    "policy_refs": ["ADV-6.2"]
  }'
```

#### 4. Get Analytics
```powershell
# All events
curl http://localhost:8000/events

# Filtered by policy
curl "http://localhost:8000/events?policy_id=ADV-6.2"

# Date range
curl "http://localhost:8000/events?start_date=2025-10-01&end_date=2025-10-22"
```

---

## 🧪 Test Sample Violations

### 1. Guaranteed Returns (ADV-6.2)
```
"I can guarantee you'll get 15% returns every year with zero risk!"
```

### 2. Missing Disclosure (DISC-1.1)
```
"This investment opportunity is perfect for you! Let me tell you about the incredible growth potential."
```

### 3. PII Exposure (PII-SSN)
```
"Please verify your social security number 123-45-6789 for this account."
```

### 4. Unprofessional Tone (TONE)
```
"Look buddy, if you don't understand this, maybe investing isn't for you."
```

### 5. Clean Text (Should Pass)
```
"Based on historical performance, similar investments have shown varying returns. Past performance does not guarantee future results. Would you like to review the prospectus?"
```

---

## 📊 Multi-Provider Configuration

Your current setup:
- **Primary**: Groq (llama-3.1-8b-instant) - Fast, free tier
- **Fallback**: OpenAI (gpt-4o-mini) - Activates if Groq fails
- **Judge**: OpenAI (gpt-4o-mini) - For evaluations

**Test provider fallback:**
```powershell
# Temporarily set invalid Groq key to test fallback
$env:GROQ_API_KEY="invalid_key_for_testing"
curl -X POST http://localhost:8000/suggest -H "Content-Type: application/json" -d '{\"agent_draft\":\"test\"}'
# Should automatically fall back to OpenAI
```

---

## 🔍 Monitoring & Debugging

### View API Logs
Check Terminal 1 (where uvicorn is running) for:
- Request logs
- Provider switching (Groq → OpenAI fallback)
- Error messages
- Response times

### View Dashboard Logs
Check Terminal 2 (where Streamlit is running) for:
- UI interactions
- Chart rendering
- Database queries

### Check Database
```powershell
# View database contents
python -c "import duckdb; conn = duckdb.connect('qa_coach.duckdb'); print(conn.execute('SELECT COUNT(*) FROM events').fetchone()[0], 'events'); conn.close()"
```

---

## 🛠️ Troubleshooting

### Issue: "Port 8000 already in use"
```powershell
# Find and kill process
Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess | Stop-Process -Force

# Or use different port
uvicorn app.api:app --reload --port 8001
```

### Issue: "Port 8501 already in use"
```powershell
# Find and kill process
Get-Process -Id (Get-NetTCPConnection -LocalPort 8501).OwningProcess | Stop-Process -Force

# Or use different port
streamlit run app/dashboard.py --server.port 8502
```

### Issue: "API connection failed" in Dashboard
- Verify API is running at http://localhost:8000
- Check Terminal 1 for error messages
- Verify `.env` has valid API keys

### Issue: "No data to display" in Reports
- Run seed script: `python scripts/seed_synthetic.py`
- Or use the Live Coaching tab to generate some events first

### Issue: Provider errors
```powershell
# Test Groq connection
python -c "import os; from groq import Groq; client = Groq(api_key=os.getenv('GROQ_API_KEY')); print('Groq:', client.chat.completions.create(messages=[{'role':'user','content':'hi'}],model='llama-3.1-8b-instant').choices[0].message.content)"

# Test OpenAI connection
python -c "import os; from openai import OpenAI; client = OpenAI(api_key=os.getenv('OPENAI_API_KEY')); print('OpenAI:', client.chat.completions.create(messages=[{'role':'user','content':'hi'}],model='gpt-4o-mini').choices[0].message.content)"
```

---

## 🎬 Complete Workflow Example

**Terminal 1:**
```powershell
cd D:\qa_compliance_bot
.\venv\Scripts\Activate.ps1
uvicorn app.api:app --reload
```

**Terminal 2:**
```powershell
cd D:\qa_compliance_bot
.\venv\Scripts\Activate.ps1
streamlit run app/dashboard.py
```

**Browser:**
1. Open http://localhost:8501
2. Go to "Live Coaching" tab
3. Test various policy violations
4. Check "Reports" tab for analytics
5. Open http://localhost:8000/docs for API documentation

---

## 📝 API Documentation

**Interactive Swagger UI:** http://localhost:8000/docs
**ReDoc:** http://localhost:8000/redoc

### Available Endpoints:
- `GET /health` - Health check
- `POST /suggest` - Get coaching suggestion
- `POST /evals/judge` - Evaluate suggestion quality
- `GET /events` - Get all logged events
- `GET /events/{event_id}` - Get specific event
- `GET /analytics/summary` - Get summary statistics

---

## 🎯 Next Steps

1. **Explore the Dashboard:**
   - Test different violation types
   - View real-time analytics
   - Check judge evaluations

2. **Test API Integration:**
   - Use Postman or curl to test endpoints
   - View interactive docs at /docs
   - Test error handling and fallback

3. **Review Code:**
   - `app/coach.py` - Core suggestion logic
   - `app/judge.py` - LLM-as-a-judge evaluation
   - `app/providers/provider_manager.py` - Multi-provider fallback
   - `app/rules.py` - Policy detection rules

4. **Generate Reports:**
   - Run seed script for more data
   - Export analytics from dashboard
   - Test different time ranges

---

## 🛑 Stopping the Application

**Stop Dashboard (Terminal 2):**
Press `Ctrl+C`

**Stop API (Terminal 1):**
Press `Ctrl+C`

**Deactivate Virtual Environment:**
```powershell
deactivate
```

---

## 📚 Additional Resources

- **Full Documentation:** `EVALS_GUIDE.md`, `MULTI_PROVIDER_GUIDE.md`
- **Test Fixes Summary:** `TEST_FIXES_SUMMARY.md`
- **Setup Instructions:** `README.md`
- **API Tests:** Run `pytest tests/ -v`
- **Coverage Report:** Run `pytest tests/ --cov=app --cov-report=html`

---

## ✅ Success Checklist

- [ ] Virtual environment activated (`(venv)` in prompt)
- [ ] API running at http://localhost:8000
- [ ] Dashboard running at http://localhost:8501
- [ ] Can access http://localhost:8000/docs
- [ ] Can access http://localhost:8501
- [ ] Tested a sample violation in Live Coaching
- [ ] Viewed analytics in Reports tab
- [ ] All tests passing: `pytest tests/ -v`

---

**🎉 You're all set! Happy coaching!**
