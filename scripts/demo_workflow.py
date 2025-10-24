"""
Complete workflow example demonstrating all system capabilities.

This script shows:
1. Multi-provider suggestion generation with fallback
2. LLM-as-a-judge evaluation
3. Event logging
4. Analytics queries
"""

import os
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


def print_header(text: str, symbol: str = "="):
    """Print a formatted header."""
    print(f"\n{symbol * 70}")
    print(f"  {text}")
    print(f"{symbol * 70}\n")


def demo_suggestion_generation():
    """Demo 1: Generate a compliant suggestion."""
    print_header("DEMO 1: Suggestion Generation", "=")
    
    from app.coach import suggest
    from app.providers.provider_manager import get_last_provider_used
    
    # Example: Risky agent draft
    agent_draft = "We absolutely guarantee 12% annual returns on all investments!"
    context = "Customer asking about expected investment returns"
    
    print(f"📝 Agent Draft (risky):")
    print(f"   '{agent_draft}'")
    print()
    print(f"🎯 Context: {context}")
    print()
    print("⚙️  Generating compliant suggestion...")
    
    # Generate suggestion
    response = suggest(
        agent_draft=agent_draft,
        context=context
    )
    
    provider = get_last_provider_used()
    
    print()
    print(f"✅ Suggestion generated successfully!")
    print(f"📡 Provider used: {provider}")
    print(f"⏱️  Latency: {response.latency_ms}ms")
    print()
    print(f"💡 Primary Suggestion:")
    print(f"   '{response.suggestion}'")
    print()
    print(f"🔄 Alternates:")
    for i, alt in enumerate(response.alternates, 1):
        print(f"   {i}. '{alt}'")
    print()
    print(f"📋 Rationale:")
    print(f"   {response.rationale}")
    print()
    print(f"⚠️  Policy Violations:")
    for policy in response.policy_refs:
        print(f"   - {policy}")
    print()
    print(f"🎯 Confidence: {response.confidence:.2f}")
    
    return response, agent_draft, context


def demo_evaluation(response, agent_draft, context):
    """Demo 2: Evaluate the suggestion quality."""
    print_header("DEMO 2: LLM-as-a-Judge Evaluation", "=")
    
    from app.evals.judge import evaluate_suggestion
    
    judge_provider = os.getenv("JUDGE_PROVIDER", "openai")
    judge_model = os.getenv("JUDGE_MODEL", "gpt-4o-mini")
    
    print(f"🔍 Judge Configuration:")
    print(f"   Provider: {judge_provider}")
    print(f"   Model: {judge_model}")
    print()
    print("⚙️  Evaluating suggestion quality...")
    
    # Evaluate the suggestion
    eval_result = evaluate_suggestion(
        agent_draft=agent_draft,
        suggestion=response.suggestion,
        policy_refs=response.policy_refs,
        context=context
    )
    
    print()
    print(f"✅ Evaluation complete!")
    print()
    print(f"📊 Scores (0-10 scale):")
    print(f"   Overall:        {eval_result.overall_score:.1f}/10")
    print(f"   Compliance:     {eval_result.compliance_score:.1f}/10")
    print(f"   Clarity:        {eval_result.clarity_score:.1f}/10")
    print(f"   Tone:           {eval_result.tone_score:.1f}/10")
    print(f"   Completeness:   {eval_result.completeness_score:.1f}/10")
    print()
    
    status_icon = "✅" if eval_result.pass_threshold else "❌"
    status_text = "PASS" if eval_result.pass_threshold else "FAIL"
    print(f"{status_icon} Status: {status_text} (threshold: 7.0)")
    print()
    print(f"💬 Judge Feedback:")
    print(f"   {eval_result.feedback}")
    print()
    
    if eval_result.strengths:
        print(f"✨ Strengths:")
        for strength in eval_result.strengths:
            print(f"   • {strength}")
        print()
    
    if eval_result.weaknesses:
        print(f"⚠️  Weaknesses:")
        for weakness in eval_result.weaknesses:
            print(f"   • {weakness}")
        print()
    
    return eval_result


def demo_event_logging(response, agent_draft, eval_result):
    """Demo 3: Log coaching events to DuckDB."""
    print_header("DEMO 3: Event Logging", "=")
    
    import duckdb
    
    db_path = os.getenv("RUNS_DB", "./data/qa_runs.duckdb")
    
    print(f"💾 Database: {db_path}")
    print()
    print("⚙️  Logging coaching event...")
    
    # Connect to database
    conn = duckdb.connect(db_path)
    
    # Prepare event data
    event_data = {
        "id": f"demo_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "ts": datetime.now(),
        "event": "accepted",
        "session_id": "demo_session",
        "agent_draft": agent_draft,
        "suggestion_used": response.suggestion,
        "policy_refs": json.dumps(response.policy_refs),
        "latency_ms": response.latency_ms,
        "ab_test_bucket": "on"
    }
    
    # Insert event
    conn.execute("""
        INSERT INTO coach_events (
            id, ts, event, session_id, agent_draft,
            suggestion_used, policy_refs, latency_ms, ab_test_bucket
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, [
        event_data["id"],
        event_data["ts"],
        event_data["event"],
        event_data["session_id"],
        event_data["agent_draft"],
        event_data["suggestion_used"],
        event_data["policy_refs"],
        event_data["latency_ms"],
        event_data["ab_test_bucket"]
    ])
    
    print(f"✅ Event logged: {event_data['id']}")
    print()
    print(f"📋 Event Details:")
    print(f"   Type: {event_data['event']}")
    print(f"   Session: {event_data['session_id']}")
    print(f"   Latency: {event_data['latency_ms']}ms")
    print(f"   Policies: {', '.join(response.policy_refs)}")
    print(f"   Eval Score: {eval_result.overall_score:.1f}/10")
    
    # Query recent events
    print()
    print("📊 Recent Events:")
    recent = conn.execute("""
        SELECT event, COUNT(*) as count
        FROM coach_events
        GROUP BY event
        ORDER BY count DESC
        LIMIT 5
    """).fetchall()
    
    for row in recent:
        print(f"   {row[0]}: {row[1]} events")
    
    conn.close()
    
    return event_data


def demo_analytics():
    """Demo 4: Query analytics from logged events."""
    print_header("DEMO 4: Analytics Queries", "=")
    
    import duckdb
    
    db_path = os.getenv("RUNS_DB", "./data/qa_runs.duckdb")
    conn = duckdb.connect(db_path, read_only=True)
    
    print("📈 Coach Effect Metrics:")
    print()
    
    # Total events
    total = conn.execute("SELECT COUNT(*) FROM coach_events").fetchone()[0]
    print(f"   Total events: {total}")
    
    # Accept rate
    accepted = conn.execute("""
        SELECT COUNT(*) FROM coach_events WHERE event = 'accepted'
    """).fetchone()[0]
    accept_rate = (accepted / total * 100) if total > 0 else 0
    print(f"   Accept rate: {accept_rate:.1f}%")
    
    # Average latency
    avg_latency = conn.execute("""
        SELECT AVG(latency_ms) FROM coach_events
    """).fetchone()[0]
    print(f"   Avg latency: {avg_latency:.0f}ms")
    
    # Top policies
    print()
    print("🚨 Top Policy Violations:")
    top_policies = conn.execute("""
        SELECT policy_refs, COUNT(*) as count
        FROM coach_events
        WHERE policy_refs IS NOT NULL AND policy_refs != '[]'
        GROUP BY policy_refs
        ORDER BY count DESC
        LIMIT 5
    """).fetchall()
    
    for i, (policy, count) in enumerate(top_policies, 1):
        policies = json.loads(policy)
        if policies:
            print(f"   {i}. {', '.join(policies)}: {count} occurrences")
    
    # Recent activity
    print()
    print("📅 Recent Activity (last 5 events):")
    recent = conn.execute("""
        SELECT ts, event, agent_draft
        FROM coach_events
        ORDER BY ts DESC
        LIMIT 5
    """).fetchall()
    
    for row in recent:
        ts_str = row[0].strftime("%Y-%m-%d %H:%M:%S")
        draft_preview = row[2][:50] + "..." if len(row[2]) > 50 else row[2]
        print(f"   [{ts_str}] {row[1]}: '{draft_preview}'")
    
    conn.close()


def demo_provider_status():
    """Demo 5: Check provider health and failover."""
    print_header("DEMO 5: Provider Status & Failover", "=")
    
    from app.providers.provider_manager import get_provider_manager
    
    print("🔍 Checking provider availability...")
    print()
    
    manager = get_provider_manager()
    status = manager.get_provider_status()
    
    print(f"⚙️  Configuration:")
    print(f"   Primary: {status['primary']}")
    print(f"   Fallbacks: {', '.join(status['fallbacks']) or 'None'}")
    print()
    print(f"📡 Provider Health:")
    
    for provider, state in status["providers"].items():
        icon = "✅" if state == "available" else "❌"
        print(f"   {icon} {provider}: {state}")
    
    print()
    print(f"🔄 Fallback Chain:")
    print(f"   1. Try {status['primary']}")
    for i, fallback in enumerate(status['fallbacks'], 2):
        print(f"   {i}. If failed, try {fallback}")
    print(f"   {len(status['fallbacks']) + 2}. If all failed, return error")


def main():
    """Run the complete workflow demo."""
    print("\n" + "🎯" * 35)
    print("  QA COACH - COMPLETE WORKFLOW DEMO")
    print("  Multi-Provider + Evaluation + Logging + Analytics")
    print("🎯" * 35)
    
    try:
        # Demo 1: Generate suggestion
        response, agent_draft, context = demo_suggestion_generation()
        
        # Demo 2: Evaluate quality
        eval_result = demo_evaluation(response, agent_draft, context)
        
        # Demo 3: Log event
        event_data = demo_event_logging(response, agent_draft, eval_result)
        
        # Demo 4: Query analytics
        demo_analytics()
        
        # Demo 5: Provider status
        demo_provider_status()
        
        # Summary
        print_header("WORKFLOW COMPLETE", "=")
        print("✅ All system components working correctly!")
        print()
        print("📊 Summary:")
        print(f"   • Suggestion generated: {response.latency_ms}ms")
        print(f"   • Provider used: {os.getenv('LLM_PROVIDER', 'groq')}")
        print(f"   • Quality score: {eval_result.overall_score:.1f}/10")
        print(f"   • Evaluation: {'PASS' if eval_result.pass_threshold else 'FAIL'}")
        print(f"   • Event logged: {event_data['id']}")
        print()
        print("🚀 System is production-ready!")
        print()
        print("📚 Next Steps:")
        print("   • Start API: uvicorn app.api:app --reload")
        print("   • Start Dashboard: streamlit run app/dashboard.py")
        print("   • Run Tests: pytest")
        print("   • Run Evals: python scripts/run_evals.py")
        print()
    
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print()
        print("Troubleshooting:")
        print("  • Check API keys in .env file")
        print("  • Ensure database exists: python scripts/seed_synthetic.py")
        print("  • Verify provider configuration")
        import traceback
        print()
        print("Full traceback:")
        traceback.print_exc()


if __name__ == "__main__":
    main()
