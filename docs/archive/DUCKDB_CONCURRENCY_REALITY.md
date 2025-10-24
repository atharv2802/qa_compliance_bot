# DuckDB Concurrency - The Real Problem

**Date**: October 23, 2025  
**Discovery**: DuckDB READ-ONLY mode doesn't work as expected with concurrent writer

---

## 🔍 What We Discovered

### The Assumption (WRONG ❌)
```python
# We thought this would work:
API:       duckdb.connect(path)              → WRITE lock
Dashboard: duckdb.connect(path, read_only=True) → READ alongside writer

# Expected: Both coexist
# Reality: Still get "file is being used by another process"
```

### The Reality

**DuckDB Locking Behavior:**
- ✅ Multiple `read_only=True` connections can coexist (no writers)
- ❌ `read_only=True` **CANNOT** coexist with a WRITE connection
- ❌ Even read-only mode requires file access that conflicts with writer

**Error Message:**
```
IO Error: Cannot open file "data\qa_runs.duckdb": 
The process cannot access the file because it is being used by another process.
File is already open in python.exe (PID 22448)
```

---

## 💡 Real Solutions

### Solution 1: API-Only Access (Recommended ✅)

**Dashboard NEVER touches database directly**

```python
# Dashboard - NO direct DB access
def get_reports_data():
    """Get reports via API, not direct DB access."""
    response = requests.get("http://localhost:8000/analytics/summary")
    return response.json()

# API - Single source of truth
@app.get("/analytics/summary")
def get_analytics():
    conn = duckdb.connect(DB_PATH)  # Only API touches DB
    # ... query and return JSON
```

**Benefits:**
- ✅ No file locking issues
- ✅ RESTful architecture
- ✅ Scalable (multiple dashboards can connect)
- ✅ Works remotely

**Implementation:**
- Add `/analytics/summary` endpoint to API
- Add `/analytics/events` endpoint for raw event data
- Dashboard calls these endpoints instead of direct DB queries

---

### Solution 2: Separate Databases

**One for writes, one for reads**

```python
# API writes to main DB
api_conn = duckdb.connect("data/qa_runs_write.duckdb")

# Background job copies to read DB
def sync_db():
    # Every 5 seconds, export and import
    conn_write = duckdb.connect("data/qa_runs_write.duckdb")
    conn_read = duckdb.connect("data/qa_runs_read.duckdb")
    
    data = conn_write.execute("SELECT * FROM coach_events").df()
    conn_read.execute("CREATE OR REPLACE TABLE coach_events AS SELECT * FROM data")
    
# Dashboard reads from read-only copy
dashboard_conn = duckdb.connect("data/qa_runs_read.duckdb", read_only=True)
```

**Benefits:**
- ✅ Truly concurrent access
- ✅ No API dependency for reads
- ⚠️ Data lag (5-60 seconds)
- ⚠️ More complex

---

### Solution 3: Use SQLite or PostgreSQL

**DuckDB is optimized for analytics, not concurrent OLTP**

```python
# Use SQLite instead (better concurrency)
import sqlite3

# API - WRITE
conn = sqlite3.connect("data/qa_runs.db", timeout=10)

# Dashboard - READ
conn = sqlite3.connect("data/qa_runs.db", timeout=10)
conn.execute("PRAGMA query_only = ON")  # Read-only pragma
```

**Benefits:**
- ✅ Better concurrent access
- ✅ More mature locking
- ⚠️ Slower for analytics
- ⚠️ Migration required

---

## 🎯 Recommended Approach: API-Based Reports

Let me implement this now...

### Step 1: Add Analytics Endpoints to API

```python
# app/api.py

@app.get("/analytics/summary")
def get_analytics_summary():
    """Get summary analytics for dashboard."""
    conn = get_db()
    
    total = conn.execute("SELECT COUNT(*) FROM coach_events").fetchone()[0]
    offered = conn.execute("SELECT COUNT(*) FROM coach_events WHERE event = 'offered'").fetchone()[0]
    accepted = conn.execute("SELECT COUNT(*) FROM coach_events WHERE event IN ('accepted', 'edited')").fetchone()[0]
    avg_latency = conn.execute("SELECT AVG(latency_ms) FROM coach_events WHERE latency_ms > 0").fetchone()[0]
    
    return {
        "total_events": total,
        "suggestions_offered": offered,
        "suggestions_accepted": accepted,
        "accept_rate": (accepted / offered * 100) if offered > 0 else 0,
        "avg_latency_ms": int(avg_latency) if avg_latency else 0
    }

@app.get("/analytics/events")
def get_analytics_events(limit: int = 100):
    """Get recent events for dashboard."""
    conn = get_db()
    
    events = conn.execute(f"""
        SELECT 
            id, ts, event, session_id,
            agent_draft, suggestion_used,
            policy_refs, latency_ms, ab_test_bucket
        FROM coach_events
        ORDER BY ts DESC
        LIMIT {limit}
    """).df()
    
    return events.to_dict(orient="records")

@app.get("/analytics/policies")
def get_policy_violations():
    """Get policy violation counts."""
    conn = get_db()
    
    policies_data = conn.execute("""
        SELECT policy_refs FROM coach_events WHERE policy_refs IS NOT NULL
    """).fetchall()
    
    policy_counts = {}
    for row in policies_data:
        try:
            policies = json.loads(row[0])
            for p in policies:
                policy_counts[p] = policy_counts.get(p, 0) + 1
        except:
            pass
    
    return policy_counts
```

### Step 2: Update Dashboard to Use API

```python
# app/dashboard.py

def get_analytics_from_api():
    """Get analytics from API instead of direct DB access."""
    try:
        response = requests.get(f"{API_URL}/analytics/summary", timeout=5)
        if response.ok:
            return response.json()
        return None
    except:
        return None

def render_reports_tab():
    """Render reports using API data."""
    st.header("📈 Coach Effect Reports")
    
    # Check API availability
    data = get_analytics_from_api()
    
    if data is None:
        st.error("❌ Cannot load reports - API is not running")
        st.info("💡 Start the API: uvicorn app.api:app --reload")
        return
    
    # Display metrics from API
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Events", f"{data['total_events']:,}")
    
    with col2:
        st.metric("Suggestions Offered", f"{data['suggestions_offered']:,}")
    
    with col3:
        st.metric("Accept Rate", f"{data['accept_rate']:.1f}%")
    
    with col4:
        st.metric("Avg Latency", f"{data['avg_latency_ms']} ms")
    
    # Get events from API
    events_response = requests.get(f"{API_URL}/analytics/events?limit=100")
    if events_response.ok:
        events = events_response.json()
        st.subheader("Recent Events")
        st.dataframe(pd.DataFrame(events))
    
    # Get policy violations from API
    policies_response = requests.get(f"{API_URL}/analytics/policies")
    if policies_response.ok:
        policies = policies_response.json()
        st.subheader("Violations Prevented by Policy")
        st.bar_chart(policies)
```

---

## ✅ This Will Work Because:

1. **Only API touches database** → No file locking conflicts
2. **Dashboard uses HTTP requests** → Works even if dashboard is on different machine
3. **Simple architecture** → Clear separation of concerns
4. **Scalable** → Can have multiple dashboard instances
5. **Production-ready** → Standard REST API pattern

---

## 📝 Next Steps

1. Add analytics endpoints to `app/api.py`
2. Update dashboard to use API instead of direct DB
3. Remove `get_db_connection()` from dashboard
4. Test with both services running
5. Verify Reports tab works

---

**Conclusion:** The `read_only=True` approach doesn't work with DuckDB when there's a concurrent writer. The correct solution is to use API-based access for all dashboard reads.

