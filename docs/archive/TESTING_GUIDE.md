# Testing Guide - Dropdown & Event Logging

**Date**: October 23, 2025  
**Services Running**: API (port 8000) + Streamlit (port 8501)

---

## ✅ Services Status

Both services are now running in separate PowerShell windows:

```
API:        http://localhost:8000  ✓ Running
Streamlit:  http://localhost:8501  ✓ Running
Database:   15 events logged      ✓ Working
```

---

## 🧪 Test 1: Dropdown Selection

### Steps:
1. **Open browser**: Navigate to http://localhost:8501
2. **Go to Live Suggestions tab** (should be default tab)
3. **Find the dropdown**: Look for "Choose a pre-loaded example:"
4. **Click the dropdown** and you should see test cases like:
   - (Select a test case)
   - POL001: Hi, I'm Sarah...
   - POL002: You're approved...
   - POL003: Hi there...
   - etc.

5. **Select any test case** (e.g., "POL001: Hi, I'm Sarah...")

### Expected Result:
✅ **BOTH text areas should immediately populate with:**
- **Agent's draft message**: Full text from the example
- **Conversation context**: Context text from the example

### If It Doesn't Work:
❌ Text areas remain empty or show previous text
- This means the dropdown fix didn't work
- Please tell me EXACTLY what you see

---

## 🧪 Test 2: Event Logging

### Steps:
1. **With text in the text areas** (from dropdown or typed manually)
2. **Click**: "🔍 Get Suggestion" button
3. **Wait** for the suggestion to appear (2-3 seconds)
4. **Look for warning message**:
   - ✅ If API is working: NO warning should appear
   - ⚠️ If API not running: "Event not logged - API may not be running"

5. **After suggestion appears**, you'll see three buttons:
   - ✅ Use
   - ✏️ Use & Edit
   - ❌ Reject

6. **Click "✅ Use" button**

### Expected Result:
✅ **Green success message should appear**:
- "✓ Event logged as accepted"

❌ **If API not running, red error message**:
- "✗ Event NOT logged - API not running!"

### If It Shows Error:
This means API is not accessible. Check:
```powershell
# Run this in a new terminal
python -c "import requests; print(requests.get('http://localhost:8000/health').status_code)"
```
Should print: `200`

---

## 🧪 Test 3: Verify Events in Database

### Method A: Via API (While API Running)
```powershell
# In a new PowerShell terminal
curl http://localhost:8000/events/recent
```

Should show JSON with recent events.

### Method B: Direct Database Access (Stop API First)
```powershell
# 1. Stop the API (Ctrl+C in API window or close it)

# 2. Check database
python -c "import duckdb; conn = duckdb.connect('data/qa_runs.duckdb'); print(conn.execute('SELECT COUNT(*) FROM coach_events').fetchone()[0], 'events'); conn.close()"
```

Should show count like: `18 events` (more than the original 15)

---

## 📊 Quick Diagnostic Script

Run this anytime to check status:

```powershell
cd D:\qa_compliance_bot
python test_issues.py
```

This will show:
- ✓/✗ API status
- ✓/✗ Event logging capability  
- ✓/✗ Database access
- ✓/✗ Streamlit status
- Event count in database

---

## 🔍 Troubleshooting

### Problem: Dropdown doesn't populate text areas

**Check 1**: Is the page fully loaded?
- Wait 2-3 seconds after page loads
- Look for the dropdown to appear

**Check 2**: Are there examples loaded?
- Check sidebar - should show "X examples loaded"
- If 0 examples, check `data/synthetic/examples.json` exists

**Check 3**: Does selection change?
- When you select an item, does the dropdown show the selected text?
- Or does it stay on "(Select a test case)"?

**Check 4**: Look at browser console
- Press F12
- Go to Console tab
- Look for any JavaScript errors (red text)
- Send me screenshot if you see errors

---

### Problem: Events not being logged

**Check 1**: Is API running?
```powershell
curl http://localhost:8000/health
```
Should return: `{"status":"healthy"}`

**Check 2**: Is there a firewall/antivirus blocking?
- Check Windows Defender
- Check if port 8000 is accessible

**Check 3**: Look at Streamlit terminal output
- When you click ✅ Use button
- You should see in terminal: `✓ Event logged: accepted (Status: 200)`
- If you see `✗ Event not logged: API not running`, then API isn't accessible

**Check 4**: Check API terminal output
- Should show: `INFO:     127.0.0.1:XXXXX - "POST /events/coach HTTP/1.1" 200 OK`

---

## 📝 What to Report

Please tell me:

### For Dropdown Issue:
1. ❓ Do you see the dropdown?
2. ❓ Does it have test cases listed?
3. ❓ When you select a test case, does the dropdown text change?
4. ❓ Do the text areas below populate with text?
5. ❓ Any error messages?

### For Event Logging Issue:
1. ❓ When you click "Get Suggestion", do you see a warning?
2. ❓ When you click "✅ Use", what message do you see?
   - Green "✓ Event logged as accepted" = WORKING
   - Red "✗ Event NOT logged" = NOT WORKING
3. ❓ What does the diagnostic script show? (run `python test_issues.py`)

---

## 🎯 Expected Working Behavior

Here's what SHOULD happen when everything works:

1. Open http://localhost:8501
2. Select "POL001: Hi, I'm Sarah..." from dropdown
3. → Text areas instantly fill with example text
4. Click "Get Suggestion"
5. → Wait 2-3 seconds, suggestion appears
6. → NO warning about event logging
7. Click "✅ Use"
8. → Green message: "✓ Event logged as accepted"
9. Run `python test_issues.py`
10. → Shows API running, 16+ events in database

If ANY step doesn't work as described, that's the issue!

---

## 💡 Current Code Changes

I made these changes to fix the issues:

### Fix 1: Dropdown (dashboard.py lines 175-227)
- Added session state initialization
- Detect when selection changes
- Update session state with example text
- Use `st.rerun()` to refresh UI with new values

### Fix 2: Event Logging (dashboard.py lines 93-126)
- Added debug print statements
- Shows success/failure in terminal
- Returns True/False to indicate success
- UI shows green success or red error messages

### Fix 3: Better Error Messages
- "✓ Event logged as accepted" = SUCCESS
- "✗ Event NOT logged - API not running!" = FAILURE
- Terminal shows exact error reason

---

Test now and report back what you see! 🚀
