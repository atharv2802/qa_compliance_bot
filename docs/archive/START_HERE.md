# 🚀 START HERE - Complete Running Instructions

## ✅ Current Status
- ✅ Project location: `D:\qa_compliance_bot`
- ✅ Virtual environment: `venv` (created)
- ✅ Dependencies: Installed
- ✅ Tests: All 66 passing
- ✅ Configuration: `.env` with Groq + OpenAI keys

---

## 🎯 **QUICK START (Direct Commands)**

### **Terminal 1 - Start API Server:**
```powershell
cd D:\qa_compliance_bot
.\venv\Scripts\Activate.ps1
uvicorn app.api:app --reload
```

### **Terminal 2 - Start Dashboard:**
```powershell
cd D:\qa_compliance_bot
.\venv\Scripts\Activate.ps1
$env:PYTHONPATH = "."
streamlit run app/dashboard.py
```

**Done!** Open http://localhost:8501 in your browser.

---

## 📋 **STEP-BY-STEP FIRST TIME SETUP**

### **Step 1: Open First Terminal (API Server)**

1. Press `Windows Key + X` → Select **"Windows PowerShell"**
2. Run these commands:

```powershell
cd D:\qa_compliance_bot
.\venv\Scripts\Activate.ps1
uvicorn app.api:app --reload
```

**Expected output:**
```
INFO:     Will watch for changes in these directories: ['D:\\qa_compliance_bot']
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [xxxxx] using WatchFiles
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**✅ Verify:** 
- Open http://localhost:8000 in browser → Should see API info JSON
- Open http://localhost:8000/docs → Should see Swagger documentation

**🛑 KEEP THIS TERMINAL RUNNING!**

---

### **Step 2: Open Second Terminal (Dashboard)**

1. Press `Windows Key + X` again → Select **"Windows PowerShell"** (new window)
2. Run these commands:

```powershell
cd D:\qa_compliance_bot
.\venv\Scripts\Activate.ps1
$env:PYTHONPATH = "."
streamlit run app/dashboard.py
```

**Expected output:**
```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```

**✅ Your browser should automatically open to http://localhost:8501**

If not, manually visit: http://localhost:8501

**🛑 KEEP THIS TERMINAL RUNNING TOO!**

---

## 🎯 **USING THE DASHBOARD**

### **Live Coaching Tab**

1. **See dropdown:** "Select a test case"
2. **Select:** "We guarantee 12% returns every year!"
3. **Click:** "Get Coaching Suggestion"
4. **Wait:** 2-3 seconds (Groq is fast!)
5. **See results:**
   - ✅ Compliant suggestion
   - 🔄 Alternate versions
   - 📋 Rationale
   - 🎯 Policy violations fixed
   - ⚡ Response time
   - 🤖 Provider used (groq)

6. **Try more:**
   - Select different violations
   - Type your own text in "Or enter custom text"
   - Test PII violations (SSN)
   - Test tone issues (rude language)
   - Test clean compliant text

### **Reports Tab**

1. Click **"Reports"** in sidebar
2. View analytics:
   - Total suggestions
   - Acceptance rate
   - Policy violation counts
   - Latency metrics
   - Before/after examples

---

## 🧪 **TESTING THE API DIRECTLY**

Open a **third terminal** (or use browser):

### **Test Health:**
```powershell
curl http://localhost:8000/health
```

**Expected:**
```json
{"status":"healthy","version":"1.0.0"}
```

### **Test Root:**
```powershell
curl http://localhost:8000/
```

**Expected:**
```json
{
  "name": "QA Coach API",
  "version": "1.0.0",
  "status": "running",
  "docs": "/docs",
  "endpoints": {...}
}
```

### **Test Suggestion:**
```powershell
curl -X POST http://localhost:8000/coach/suggest -H "Content-Type: application/json" -d '{\"session_id\":\"test\",\"agent_draft\":\"We guarantee 15% returns!\",\"context\":\"\",\"brand_tone\":\"professional\"}'
```

### **Test Provider Status:**
```powershell
curl http://localhost:8000/providers/status
```

**Expected:**
```json
{
  "primary": "groq",
  "fallbacks": ["openai"],
  "provider_chain": ["groq", "openai"],
  "last_used": "groq"
}
```

---

## ❌ **COMMON ISSUES & FIXES**

### **Issue: "ModuleNotFoundError: No module named 'app'"**

**Cause:** Running Streamlit from wrong directory or Python path not set

**Fix:**
```powershell
# Make sure you're in the project root
cd D:\qa_compliance_bot

# Verify you're in the right place
dir  # Should see app/, venv/, .env, etc.

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Set Python path (CRITICAL!)
$env:PYTHONPATH = "."

# Run Streamlit
streamlit run app/dashboard.py
```

---

### **Issue: "404 Not Found" when visiting http://localhost:8000**

**Before fix:** This was normal, `/` endpoint didn't exist

**After fix:** Now shows API info JSON (fixed in this session)

**Also check:**
- http://localhost:8000/docs ← Should work
- http://localhost:8000/health ← Should work

---

### **Issue: "Port 8000 already in use"**

**Fix:**
```powershell
# Find and kill the process
netstat -ano | findstr :8000
taskkill /PID <PID_NUMBER> /F

# Then restart API
cd D:\qa_compliance_bot
.\venv\Scripts\Activate.ps1
uvicorn app.api:app --reload
```

---

### **Issue: "Port 8501 already in use"**

**Fix:**
```powershell
# Kill Streamlit
taskkill /IM streamlit.exe /F

# Then restart Dashboard
cd D:\qa_compliance_bot
.\venv\Scripts\Activate.ps1
$env:PYTHONPATH = "."
streamlit run app/dashboard.py
```

---

### **Issue: Dashboard shows "Connection error" or "Cannot reach API"**

**Cause:** API server not running

**Fix:**
1. Check Terminal 1 - should show API running
2. Visit http://localhost:8000/health
3. If not working, restart API in Terminal 1:
   ```powershell
   cd D:\qa_compliance_bot
   .\venv\Scripts\Activate.ps1
   uvicorn app.api:app --reload
   ```

---

### **Issue: "execution policy" error**

**Fix:**
```powershell
# Run PowerShell as Administrator
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then try activating venv again
.\venv\Scripts\Activate.ps1
```

---

### **Issue: Virtual environment not activating**

**Fix:**
```powershell
# Manual activation
cd D:\qa_compliance_bot
.\venv\Scripts\Activate.ps1

# Verify (should see (venv) in prompt)
```

---

## 🎬 **COMPLETE WORKFLOW DEMO**

After both services are running:

1. **Open dashboard:** http://localhost:8501

2. **Test violation:**
   - Input: "I guarantee you'll get 15% returns with zero risk!"
   - Click "Get Coaching Suggestion"

3. **See results:**
   - Policy: ADV-6.2 (Guaranteed Returns)
   - Suggestion: Compliant rewrite
   - Confidence: ~0.85
   - Latency: ~350ms
   - Provider: groq

4. **Check Reports tab:**
   - View analytics
   - See trends
   - Export data

5. **Test API docs:**
   - Visit http://localhost:8000/docs
   - Try `POST /coach/suggest`
   - See interactive examples

---

## 🔍 **VERIFICATION CHECKLIST**

Run these checks to ensure everything works:

### ✅ **API Checks:**
```powershell
# 1. Health check
curl http://localhost:8000/health

# 2. Root endpoint
curl http://localhost:8000/

# 3. Provider status
curl http://localhost:8000/providers/status

# 4. Docs page (in browser)
# Open: http://localhost:8000/docs
```

### ✅ **Dashboard Checks:**
- [ ] Dashboard loads at http://localhost:8501
- [ ] Can select test cases from dropdown
- [ ] "Get Coaching Suggestion" button works
- [ ] See suggestion results within 3 seconds
- [ ] Reports tab shows analytics
- [ ] No errors in browser console (F12)

### ✅ **Integration Checks:**
- [ ] Dashboard can reach API
- [ ] Provider fallback works (Groq → OpenAI)
- [ ] Events logged to database
- [ ] Analytics update in real-time

---

## 🛑 **STOPPING THE SERVICES**

When you're done:

1. **Stop Dashboard (Terminal 2):**
   - Click on Streamlit terminal
   - Press `Ctrl+C`
   - Wait for "Stopping..."

2. **Stop API (Terminal 1):**
   - Click on API terminal
   - Press `Ctrl+C`
   - Wait for "Shutting down"

3. **Deactivate venv:**
   ```powershell
   deactivate
   ```

---

## 📚 **NEXT STEPS**

Now that everything is running:

1. **Explore test cases** in the dropdown
2. **Try custom violations** in text area
3. **Check all policy types:**
   - ADV-6.2: Guaranteed returns
   - PII-SSN: Social security numbers
   - TONE: Unprofessional language
   - DISC-1.1: Missing disclosures
   - CLEAN: Compliant examples

4. **Generate more data:**
   ```powershell
   python scripts/seed_synthetic.py
   ```

5. **Run evaluations:**
   ```powershell
   python scripts/run_evals.py --sample 50
   ```

6. **Create reports:**
   ```powershell
   python reports/aggregations.py
   ```

---

## 📞 **QUICK REFERENCE**

| What | URL |
|------|-----|
| **Dashboard** | http://localhost:8501 |
| **API Root** | http://localhost:8000 |
| **API Docs** | http://localhost:8000/docs |
| **Health Check** | http://localhost:8000/health |
| **Provider Status** | http://localhost:8000/providers/status |

### **Start Commands:**

**Terminal 1 - API:**
```powershell
cd D:\qa_compliance_bot
.\venv\Scripts\Activate.ps1
uvicorn app.api:app --reload
```

**Terminal 2 - Dashboard:**
```powershell
cd D:\qa_compliance_bot
.\venv\Scripts\Activate.ps1
$env:PYTHONPATH = "."
streamlit run app/dashboard.py
```

### **Other Commands:**

| What | Command |
|------|---------|
| **Run Tests** | `pytest` |
| **Seed Data** | `python scripts/seed_synthetic.py` |
| **Run Evals** | `python scripts/run_evals.py` |
| **Validate Setup** | `python scripts/quickstart.py` |
| **Stop Services** | `Ctrl+C` in each terminal |

---

## 🎉 **YOU'RE ALL SET!**

**Main interface:** http://localhost:8501

Start testing compliance violations and see real-time coaching! 🚀
