# ⚠️ DATABASE LOCKING ISSUE - SOLUTION

## Problem
DuckDB doesn't support concurrent access from multiple processes. When both the API and Dashboard try to access the same database file, you get:

```
IOException: IO Error: Cannot open file "qa_runs.duckdb":
The process cannot access the file because it is being used by another process.
```

## Solutions

### **Option 1: Run Only Dashboard (Recommended for Testing)**

If you just want to test the dashboard without the API:

```powershell
# Terminal 1 - Dashboard Only
cd D:\qa_compliance_bot
.\venv\Scripts\Activate.ps1
streamlit run app/dashboard.py
```

Open: http://localhost:8501

**Limitations:**
- ✅ Dashboard works perfectly
- ❌ No API endpoints available
- ❌ Can't log events (but suggestions still work)

---

### **Option 2: Run Only API (Recommended for Integration)**

If you want to use the API programmatically:

```powershell
# Terminal 1 - API Only
cd D:\qa_compliance_bot
.\venv\Scripts\Activate.ps1
uvicorn app.api:app --reload
```

Open: http://localhost:8000/docs

**Limitations:**
- ✅ API works perfectly
- ✅ Database logging works
- ❌ No web dashboard UI

---

### **Option 3: Use Separate Databases (Both Running)**

Modify `.env` to use different database files:

**For API** - Keep using: `./data/qa_runs.duckdb`

**For Dashboard** - Create new file: `./data/dashboard.duckdb`

Edit `app/dashboard.py` line 30:
```python
# Change from:
DB_PATH = os.getenv("RUNS_DB", "./data/qa_runs.duckdb")

# To:
DB_PATH = os.getenv("DASHBOARD_DB", "./data/dashboard.duckdb")
```

Then both can run:
```powershell
# Terminal 1 - API
uvicorn app.api:app --reload

# Terminal 2 - Dashboard  
streamlit run app/dashboard.py
```

**Limitations:**
- ✅ Both work simultaneously
- ❌ They see different data (separate databases)

---

### **Option 4: Dashboard Uses API Only (Best Long-term Solution)**

The dashboard should get all data through API calls instead of direct database access.

**Current Implementation:**
- ✅ `log_event_to_db()` - Already uses API
- ❌ `render_reports_tab()` - Still uses direct DB access

**To Fix:**
We need to create API endpoints that the dashboard can use:
- `GET /events/stats` - Get statistics
- `GET /events` - Get all events
- `GET /analytics/summary` - Get summary data

Then update dashboard to call these endpoints instead of querying the database directly.

---

## **Recommended Approach (Right Now)**

### **For Development/Testing:**

**Run Dashboard Only:**
```powershell
cd D:\qa_compliance_bot
.\venv\Scripts\Activate.ps1
streamlit run app/dashboard.py
```

- Go to http://localhost:8501
- Use the "Live Suggestions" tab
- Suggestions work fine
- Reports tab may show "no events" but that's okay for testing

---

### **For Production Use:**

1. **Primary:** Run API server
   ```powershell
   uvicorn app.api:app --reload
   ```

2. **Testing:** Use API docs at http://localhost:8000/docs

3. **Dashboard:** Run separately when API is stopped, or implement Option 4 above

---

## **Quick Fix for Your Current Situation**

Since Streamlit is already running and working:

1. ✅ **Keep using Streamlit** - It's working now!
2. ✅ **Test the Live Suggestions tab** - This works without the database
3. ⚠️ **Skip the Reports tab for now** - It needs database access
4. 📝 **When you want reports:** Stop Streamlit, start API, use /events/stats endpoint

---

## **What We Should Do Next (Future Enhancement)**

Create these API endpoints:
- `GET /events` - Return all events as JSON
- `GET /analytics/violations` - Violation counts by policy
- `GET /analytics/timeline` - Events over time

Then update `render_reports_tab()` to use these endpoints instead of direct DB queries.

This way:
- ✅ API manages all database access
- ✅ Dashboard just displays data from API
- ✅ No file locking issues
- ✅ Both can run simultaneously

---

## **For Now - Use This:**

```powershell
# Terminal - Dashboard Only (works great!)
cd D:\qa_compliance_bot
.\venv\Scripts\Activate.ps1
streamlit run app/dashboard.py
```

Go to http://localhost:8501 and use the **Live Suggestions** tab! 🎉
