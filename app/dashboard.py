"""
Streamlit dashboard for QA Coach.

Provides interactive UI for live suggestions and analytics reports.
"""

import os
import sys
import json
import time
from datetime import datetime, timedelta
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.absolute()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import streamlit as st
import pandas as pd
import duckdb
from dotenv import load_dotenv

from app.coach import suggest
from engine.rules import get_rules_engine

# Load environment variables
load_dotenv()

# Configuration
API_URL = os.getenv("API_URL", "http://localhost:8000")
DB_PATH = os.getenv("RUNS_DB", "./data/qa_runs.duckdb")
SYNTHETIC_DATA_PATH = os.getenv("DATA_DIR", "./data") + "/synthetic/coach_cases.jsonl"


# ============================================================================
# API Helper Functions
# ============================================================================

def get_events_from_api():
    """Get events from API instead of direct database access."""
    import requests
    try:
        response = requests.get(f"{API_URL}/events/stats", timeout=5)
        if response.ok:
            return response.json()
        return None
    except Exception as e:
        st.error(f"Could not connect to API: {e}")
        return None


# ============================================================================
# Database Functions
# ============================================================================

@st.cache_resource
def get_db_connection():
    """
    Get database connection for dashboard in READ-ONLY mode.
    
    This prevents database locking conflicts with the API server.
    The API holds a WRITE lock, but multiple readers can coexist.
    
    Returns:
        DuckDB connection in read-only mode, or None if database is locked/unavailable
    """
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    # Check if database file exists
    if not os.path.exists(DB_PATH):
        st.warning("⚠️ Database not initialized yet. Start the API server or use Live Suggestions first.")
        return None
    
    try:
        # Open in READ-ONLY mode to coexist with API's WRITE lock
        conn = duckdb.connect(DB_PATH, read_only=True)
        return conn
    except Exception as e:
        # Database is locked by API or another error
        print(f"✗ Cannot open database in read-only mode: {str(e)}")
        return None


def log_event_to_db(event_type, session_id, agent_draft, suggestion_used, policy_refs, latency_ms):
    """
    Log an event to the database via API (never writes directly to DB).
    
    The dashboard NEVER writes directly to the database to avoid lock conflicts.
    All writes go through the API, which holds the WRITE lock.
    The dashboard only READS from the database in read-only mode.
    
    Args:
        event_type: Type of event (offered, accepted, edited, rejected)
        session_id: User session ID
        agent_draft: Original agent draft text
        suggestion_used: The suggestion that was used (or None)
        policy_refs: List of policy references
        latency_ms: Response latency in milliseconds
    
    Returns:
        bool: True if event was logged successfully, False otherwise
    """
    import requests
    
    API_URL = os.getenv("API_URL", "http://localhost:8000")
    
    try:
        response = requests.post(
            f"{API_URL}/events/coach",
            json={
                "event": event_type,
                "session_id": session_id,
                "agent_draft": agent_draft,
                "suggestion_used": suggestion_used,
                "policy_refs": policy_refs,
                "latency_ms": latency_ms,
                "ab_test_bucket": os.getenv("AB_TEST_BUCKET", "on")
            },
            timeout=2
        )
        if response.ok:
            print(f"✓ Event logged via API: {event_type} (Status: {response.status_code})")
            return True
        else:
            print(f"✗ Event logging failed: {event_type} (Status: {response.status_code}, Error: {response.text})")
            return False
    except requests.exceptions.ConnectionError:
        print(f"✗ Event not logged: API not running (event: {event_type})")
        return False
    except requests.exceptions.Timeout:
        print(f"✗ Event not logged: API timeout (event: {event_type})")
        return False
    except Exception as e:
        print(f"✗ Event error: {event_type} - {str(e)}")
        return False


# ============================================================================
# Data Loading Functions
# ============================================================================

@st.cache_data
def load_synthetic_examples():
    """Load synthetic test cases for the dropdown."""
    examples = []
    
    if os.path.exists(SYNTHETIC_DATA_PATH):
        with open(SYNTHETIC_DATA_PATH, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    examples.append(json.loads(line))
                except:
                    pass
    
    return examples


# ============================================================================
# UI Components
# ============================================================================

def render_policy_badge(policy_id, severity):
    """Render a policy badge."""
    colors = {
        "critical": "#FF4B4B",
        "high": "#FF8C42",
        "medium": "#FFD93D",
        "low": "#A8DADC"
    }
    color = colors.get(severity, "#CCCCCC")
    
    st.markdown(
        f'<span style="background-color: {color}; color: white; '
        f'padding: 4px 12px; border-radius: 12px; font-size: 12px; '
        f'font-weight: bold; margin-right: 8px;">{policy_id}</span>',
        unsafe_allow_html=True
    )


def render_live_tab():
    """Render the Live Suggestions tab."""
    st.header("🎯 Live QA Coach")
    
    # Load examples
    examples = load_synthetic_examples()
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Agent Draft")
        
        # Initialize session state
        if 'agent_draft_input' not in st.session_state:
            st.session_state['agent_draft_input'] = ""
        if 'context_input' not in st.session_state:
            st.session_state['context_input'] = ""
        
        # Example selector with callback
        if examples:
            example_options = ["(Select a test case)"] + [
                f"{ex.get('policy_id', 'UNKNOWN')}: {ex.get('agent_draft', '')[:60]}..."
                for ex in examples
            ]
            
            def on_example_selected():
                """Callback when example is selected from dropdown."""
                selected = st.session_state.example_selector
                if selected != "(Select a test case)":
                    idx = example_options.index(selected) - 1
                    # Directly update the text area widget states
                    st.session_state.agent_draft_input = examples[idx].get("agent_draft", "")
                    st.session_state.context_input = examples[idx].get("context", "")
            
            selected_example = st.selectbox(
                "Choose a pre-loaded example:",
                example_options,
                key="example_selector",
                on_change=on_example_selected,
                help="Select a pre-loaded test case to populate the fields below"
            )
        
        # Text inputs - keys match what we set in the callback
        agent_draft = st.text_area(
            "Agent's draft message:",
            height=120,
            key="agent_draft_input",
            help="Select an example above or type your own text"
        )
        
        context = st.text_area(
            "Conversation context (optional):",
            height=60,
            key="context_input",
            help="Additional context about the conversation"
        )
        
        brand_tone = st.text_input(
            "Brand tone:",
            value="professional, clear, empathetic",
            key="brand_tone_input"
        )
        
        # Analyze button
        analyze_clicked = st.button("🔍 Get Suggestion", type="primary", use_container_width=True)
    
    with col2:
        st.subheader("Compliant Suggestions")
        
        if analyze_clicked and agent_draft:
            with st.spinner("Analyzing draft..."):
                start_time = time.time()
                
                try:
                    # Get suggestion
                    response = suggest(
                        agent_draft=agent_draft,
                        context=context,
                        brand_tone=brand_tone
                    )
                    
                    latency = int((time.time() - start_time) * 1000)
                    
                    # Store in session state
                    st.session_state['last_response'] = response
                    st.session_state['last_draft'] = agent_draft
                    st.session_state['last_latency'] = latency
                    
                    # Log "offered" event
                    session_id = st.session_state.get('session_id', 'streamlit-session')
                    logged = log_event_to_db(
                        "offered",
                        session_id,
                        agent_draft,
                        response.suggestion,
                        response.policy_refs,
                        response.latency_ms
                    )
                    if not logged:
                        st.warning("⚠️ Event not logged - API may not be running", icon="⚠️")
                
                except Exception as e:
                    st.error(f"Error generating suggestion: {str(e)}")
                    st.session_state['last_response'] = None
        
        # Display results
        if 'last_response' in st.session_state and st.session_state['last_response']:
            response = st.session_state['last_response']
            
            # Primary suggestion
            st.markdown("### ✅ Primary Suggestion")
            st.success(response.suggestion)
            
            # Alternates
            st.markdown("### 🔄 Alternates")
            for i, alt in enumerate(response.alternates, 1):
                st.info(f"**Alt {i}:** {alt}")
            
            # Action buttons
            col_btn1, col_btn2, col_btn3 = st.columns(3)
            with col_btn1:
                if st.button("✅ Use", use_container_width=True):
                    session_id = st.session_state.get('session_id', 'streamlit-session')
                    logged = log_event_to_db(
                        "accepted",
                        session_id,
                        st.session_state['last_draft'],
                        response.suggestion,
                        response.policy_refs,
                        st.session_state.get('last_latency', 0)
                    )
                    if logged:
                        st.success("✓ Event logged as accepted")
                    else:
                        st.error("✗ Event NOT logged - API not running!")
            
            with col_btn2:
                if st.button("✏️ Use & Edit", use_container_width=True):
                    session_id = st.session_state.get('session_id', 'streamlit-session')
                    logged = log_event_to_db(
                        "edited",
                        session_id,
                        st.session_state['last_draft'],
                        response.suggestion,
                        response.policy_refs,
                        st.session_state.get('last_latency', 0)
                    )
                    if logged:
                        st.success("✓ Event logged as edited")
                    else:
                        st.error("✗ Event NOT logged - API not running!")
            
            with col_btn3:
                if st.button("❌ Reject", use_container_width=True):
                    session_id = st.session_state.get('session_id', 'streamlit-session')
                    logged = log_event_to_db(
                        "rejected",
                        session_id,
                        st.session_state['last_draft'],
                        None,
                        response.policy_refs,
                        st.session_state.get('last_latency', 0)
                    )
                    if logged:
                        st.warning("✓ Event logged as rejected")
                    else:
                        st.error("✗ Event NOT logged - API not running!")
            
            # Metadata
            st.markdown("---")
            st.markdown("### 📊 Details")
            
            col_meta1, col_meta2 = st.columns(2)
            with col_meta1:
                st.metric("Confidence", f"{response.confidence:.1%}")
                st.metric("Latency", f"{response.latency_ms} ms")
            
            with col_meta2:
                st.markdown("**Rationale:**")
                st.caption(response.rationale)
            
            # Policy badges
            st.markdown("**Policies:**")
            for policy_id in response.policy_refs:
                engine = get_rules_engine()
                policy = engine.get_policy_by_id(policy_id)
                if policy:
                    render_policy_badge(policy_id, policy.severity)
            
            # Evidence spans
            if response.evidence_spans and response.evidence_spans != [(0, 0)]:
                st.markdown("**Violations detected at:**")
                for span in response.evidence_spans:
                    if span != (0, 0):
                        st.caption(f"Position {span[0]}-{span[1]}")


def render_reports_tab():
    """Render the Reports & Analytics tab using API data (no direct DB access)."""
    import requests
    
    st.header("📈 Coach Effect Reports")
    
    # Get data from API instead of direct database access
    try:
        response = requests.get(f"{API_URL}/events/stats", timeout=5)
        if not response.ok:
            st.error(f"❌ Cannot load reports - API returned status {response.status_code}")
            st.info("💡 Make sure the API is running: `uvicorn app.api:app --reload`")
            return
        
        stats = response.json()
        
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to API - Reports unavailable")
        st.info("💡 **Start the API to view reports:**")
        st.code("uvicorn app.api:app --reload", language="bash")
        st.markdown("---")
        st.markdown("**Why API is required:**")
        st.markdown("- DuckDB doesn't support concurrent read + write access")
        st.markdown("- API holds WRITE lock for event logging")
        st.markdown("- Dashboard gets data via API endpoints (REST pattern)")
        return
    except Exception as e:
        st.error(f"❌ Error loading reports: {str(e)}")
        return
    
    total_events = stats.get("total_events", 0)
    
    if total_events == 0:
        st.info("ℹ️ No events logged yet. Use the Live tab to generate some suggestions!")
        return
    
    # KPI tiles
    st.subheader("📊 Key Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    event_counts = stats.get("event_counts", {})
    offered = event_counts.get("offered", 0)
    accepted = event_counts.get("accepted", 0) + event_counts.get("edited", 0)
    
    # Total events
    with col1:
        st.metric("Total Events", f"{total_events:,}")
    
    # Violations prevented
    with col2:
        st.metric("Suggestions Offered", f"{offered:,}")
    
    # Accept rate
    with col3:
        accept_rate = (accepted / offered * 100) if offered > 0 else 0
        st.metric("Accept Rate", f"{accept_rate:.1f}%")
    
    # Avg latency from API endpoint
    with col4:
        try:
            latency_response = requests.get(f"{API_URL}/analytics/latency", timeout=5)
            if latency_response.ok:
                latency_data = latency_response.json()
                avg_latency = latency_data.get("avg_latency_ms", 0)
                st.metric("Avg Latency", f"{avg_latency} ms")
            else:
                st.metric("Avg Latency", "N/A")
        except:
            st.metric("Avg Latency", "N/A")
    
    st.markdown("---")
    
    # Charts
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.subheader("Events by Type")
        if event_counts:
            events_df = pd.DataFrame(
                list(event_counts.items()),
                columns=['event', 'count']
            )
            st.bar_chart(events_df.set_index('event'))
    
    with col_chart2:
        st.subheader("Violations by Policy")
        try:
            policies_response = requests.get(f"{API_URL}/analytics/policies", timeout=5)
            if policies_response.ok:
                policies_data = policies_response.json()
                policy_violations = policies_data.get("policy_violations", {})
                
                if policy_violations:
                    policy_df = pd.DataFrame(
                        list(policy_violations.items()),
                        columns=['Policy', 'Count']
                    )
                    st.bar_chart(policy_df.set_index('Policy'))
                    
                    # Show summary stats
                    total_violations = policies_data.get("total_violations", 0)
                    total_policies = policies_data.get("total_policies", 0)
                    st.caption(f"📊 {total_violations:,} violations across {total_policies} policies")
                else:
                    st.info("No policy violations detected yet")
            else:
                st.warning("⚠️ Could not load policy data")
        except Exception as e:
            st.warning(f"⚠️ Error loading policies: {str(e)}")
    
    st.markdown("---")
    
    # Latency details section
    try:
        latency_response = requests.get(f"{API_URL}/analytics/latency", timeout=5)
        if latency_response.ok:
            latency_data = latency_response.json()
            
            st.subheader("⚡ Latency Analysis")
            
            col_lat1, col_lat2, col_lat3, col_lat4 = st.columns(4)
            
            with col_lat1:
                st.metric("Min", f"{latency_data.get('min_latency_ms', 0)} ms")
            
            with col_lat2:
                percentiles = latency_data.get('percentiles', {})
                st.metric("P50 (Median)", f"{percentiles.get('p50', 0)} ms")
            
            with col_lat3:
                st.metric("P95", f"{percentiles.get('p95', 0)} ms")
            
            with col_lat4:
                st.metric("Max", f"{latency_data.get('max_latency_ms', 0)} ms")
            
            # Latency distribution info
            st.caption(f"📊 Based on {latency_data.get('total_requests', 0):,} requests")
            
    except Exception:
        pass  # Skip latency section if not available
    
    st.markdown("---")
    
    # Recent events table
    st.subheader("📋 Recent Events")
    recent_events = stats.get("recent_events", [])
    
    if recent_events:
        recent_df = pd.DataFrame(recent_events)
        st.dataframe(recent_df, use_container_width=True)
    else:
        st.info("No recent events")
    
    # Export note
    st.markdown("---")
    st.info("💡 **Export data via API:**")
    st.code("curl http://localhost:8000/events/stats > events.json", language="bash")
    st.code("curl http://localhost:8000/analytics/policies > policies.json", language="bash")
    st.code("curl http://localhost:8000/analytics/latency > latency.json", language="bash")


# ============================================================================
# Main App
# ============================================================================

def main():
    """Main Streamlit app."""
    st.set_page_config(
        page_title="QA Coach Dashboard",
        page_icon="🎯",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Sidebar
    with st.sidebar:
        st.title("🎯 QA Coach")
        st.markdown("---")
        
        # Session ID
        if 'session_id' not in st.session_state:
            st.session_state['session_id'] = f"session-{int(time.time())}"
        
        st.caption(f"Session: {st.session_state['session_id']}")
        
        st.markdown("---")
        
        # Info
        st.markdown("### About")
        st.info(
            "QA Coach provides real-time compliance suggestions "
            "for agent drafts, helping prevent policy violations "
            "before messages are sent."
        )
        
        st.markdown("### Status")
        engine = get_rules_engine()
        st.success(f"✓ {len(engine.policies)} policies loaded")
        
        # Check API connectivity
        import requests
        api_running = False
        try:
            response = requests.get(f"{API_URL}/health", timeout=1)
            if response.ok:
                api_running = True
                st.success("✓ API connected")
                st.caption("Event logging enabled")
        except:
            st.info("ℹ️ API not running")
            st.caption("Suggestions work, events not logged")
        
        # Check DB status
        try:
            conn = get_db_connection()
            if conn:
                event_count = conn.execute("SELECT COUNT(*) FROM coach_events").fetchone()[0]
                if api_running:
                    st.warning("⚠️ Reports unavailable")
                    st.caption(f"Database locked by API (use API endpoints to view {event_count} events)")
                else:
                    st.success(f"✓ Database accessible")
                    st.caption(f"{event_count} events in database")
        except Exception as e:
            if api_running:
                st.caption("Database locked by API (this is normal)")
            else:
                st.caption("Database check failed")
    
    # Main content - tabs
    tab1, tab2 = st.tabs(["🎯 Live Suggestions", "📈 Reports"])
    
    with tab1:
        render_live_tab()
    
    with tab2:
        render_reports_tab()


if __name__ == "__main__":
    main()
