# Analytics Endpoints Added

**Date**: October 23, 2025  
**New Endpoints**: `/analytics/latency` and `/analytics/policies`

---

## 📊 New API Endpoints

### 1. `/analytics/latency` - GET

**Purpose:** Get detailed latency statistics for coach suggestions

**Response:**
```json
{
  "avg_latency_ms": 234,
  "min_latency_ms": 89,
  "max_latency_ms": 1205,
  "total_requests": 42,
  "percentiles": {
    "p50": 215,
    "p90": 456,
    "p95": 623,
    "p99": 1105
  }
}
```

**Usage:**
```bash
curl http://localhost:8000/analytics/latency
```

**Dashboard Integration:**
- Shows in "Avg Latency" metric (top KPI tiles)
- Displays detailed latency analysis section:
  - Min / P50 / P95 / Max latencies
  - Total requests count

---

### 2. `/analytics/policies` - GET

**Purpose:** Get policy violation counts across all events

**Response:**
```json
{
  "policy_violations": {
    "POL001": 15,
    "POL003": 12,
    "POL002": 8,
    "POL005": 3
  },
  "total_policies": 4,
  "total_violations": 38
}
```

**Usage:**
```bash
curl http://localhost:8000/analytics/policies
```

**Dashboard Integration:**
- Populates "Violations by Policy" bar chart
- Shows total violations and policy count
- Sorted by count (most violations first)

---

## 🎨 Dashboard Updates

### Reports Tab Enhanced

**Before:**
```
📊 Key Metrics
├─ Total Events
├─ Suggestions Offered
├─ Accept Rate
└─ Avg Latency: N/A  ❌

Charts:
├─ Events by Type ✅
└─ Violations by Policy: "Add endpoint" ❌
```

**After:**
```
📊 Key Metrics
├─ Total Events
├─ Suggestions Offered
├─ Accept Rate
└─ Avg Latency: 234 ms ✅ (from /analytics/latency)

Charts:
├─ Events by Type ✅
└─ Violations by Policy ✅ (from /analytics/policies)
    └─ Shows: POL001: 15, POL003: 12, etc.

⚡ Latency Analysis (NEW!)
├─ Min: 89 ms
├─ P50: 215 ms
├─ P95: 623 ms
└─ Max: 1205 ms
```

---

## 🔧 Implementation Details

### API (`app/api.py`)

**Lines 321-377:** Added `/analytics/latency` endpoint
- Queries: AVG, MIN, MAX latency
- Calculates: P50, P90, P95, P99 percentiles
- Returns: JSON with latency statistics

**Lines 379-428:** Added `/analytics/policies` endpoint
- Queries: All policy_refs from events
- Parses: JSON arrays of policies
- Aggregates: Count per policy
- Returns: Sorted dictionary of violations

### Dashboard (`app/dashboard.py`)

**Lines 435-444:** Updated latency metric
- Calls `/analytics/latency` endpoint
- Displays avg_latency_ms in KPI tile

**Lines 463-482:** Updated policy violations chart
- Calls `/analytics/policies` endpoint
- Creates bar chart from policy_violations
- Shows summary caption with totals

**Lines 486-502:** Added latency analysis section
- Shows Min, P50, P95, Max in 4 columns
- Displays total requests count
- Appears between charts and recent events

---

## 🧪 Testing

### Test Latency Endpoint

```bash
curl http://localhost:8000/analytics/latency
```

**Expected Output:**
```json
{
  "avg_latency_ms": 234,
  "min_latency_ms": 89,
  "max_latency_ms": 1205,
  "total_requests": 42,
  "percentiles": {
    "p50": 215,
    "p90": 456,
    "p95": 623,
    "p99": 1105
  }
}
```

### Test Policies Endpoint

```bash
curl http://localhost:8000/analytics/policies
```

**Expected Output:**
```json
{
  "policy_violations": {
    "POL001": 15,
    "POL003": 12,
    "POL002": 8
  },
  "total_policies": 3,
  "total_violations": 35
}
```

### Test in Dashboard

1. Open http://localhost:8501
2. Go to "Reports" tab
3. Check:
   - ✅ "Avg Latency" shows number (not "N/A")
   - ✅ "Violations by Policy" shows bar chart
   - ✅ "⚡ Latency Analysis" section appears
   - ✅ All metrics load from API

---

## 📈 Benefits

1. **Complete Analytics** - Full latency insights (min, max, percentiles)
2. **Policy Tracking** - See which policies are most violated
3. **API-Based** - No database lock issues
4. **Exportable** - Can curl endpoints for data export
5. **Production Ready** - RESTful design, JSON responses

---

## 🎯 API Documentation

Visit http://localhost:8000/docs to see:
- `/analytics/latency` - Interactive docs
- `/analytics/policies` - Interactive docs
- Try it out directly from Swagger UI

---

## ✅ Status

| Endpoint | Status | Used By |
|----------|--------|---------|
| `/events/stats` | ✅ Working | Reports tab (KPIs, charts) |
| `/analytics/latency` | ✅ Added | Avg latency metric + analysis section |
| `/analytics/policies` | ✅ Added | Policy violations chart |

**All endpoints are now integrated into the Reports tab!** 🎉
