"""
Aggregations and reporting for QA Coach analytics.

Generates HTML reports with KPIs, charts, and insights.
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

import duckdb
import pandas as pd
from jinja2 import Environment, FileSystemLoader
from dotenv import load_dotenv

# Load environment
load_dotenv()

DB_PATH = os.getenv("RUNS_DB", "./data/qa_runs.duckdb")


def get_db_connection():
    """Get database connection."""
    return duckdb.connect(DB_PATH)


def calculate_violations_prevented() -> int:
    """Calculate total violations prevented."""
    conn = get_db_connection()
    
    try:
        result = conn.execute("""
            SELECT COUNT(*) FROM coach_events WHERE event = 'offered'
        """).fetchone()
        return result[0] if result else 0
    except:
        return 0


def calculate_accept_rate() -> float:
    """Calculate suggestion accept rate."""
    conn = get_db_connection()
    
    try:
        offered = conn.execute(
            "SELECT COUNT(*) FROM coach_events WHERE event = 'offered'"
        ).fetchone()[0]
        
        accepted = conn.execute(
            "SELECT COUNT(*) FROM coach_events WHERE event IN ('accepted', 'edited')"
        ).fetchone()[0]
        
        if offered == 0:
            return 0.0
        
        return round((accepted / offered) * 100, 1)
    except:
        return 0.0


def calculate_latency_metrics() -> Dict[str, int]:
    """Calculate latency percentiles."""
    conn = get_db_connection()
    
    try:
        df = pd.read_sql(
            "SELECT latency_ms FROM coach_events WHERE latency_ms > 0",
            conn
        )
        
        if df.empty:
            return {"avg": 0, "p95": 0, "p99": 0}
        
        return {
            "avg": int(df['latency_ms'].mean()),
            "p95": int(df['latency_ms'].quantile(0.95)),
            "p99": int(df['latency_ms'].quantile(0.99))
        }
    except:
        return {"avg": 0, "p95": 0, "p99": 0}


def get_policy_breakdown() -> List[Dict[str, Any]]:
    """Get violation counts by policy."""
    conn = get_db_connection()
    
    try:
        rows = conn.execute("""
            SELECT policy_refs, COUNT(*) as count
            FROM coach_events
            WHERE policy_refs IS NOT NULL AND policy_refs != '[]'
            GROUP BY policy_refs
        """).fetchall()
        
        # Parse JSON policy refs
        policy_counts = {}
        for row in rows:
            try:
                policies = json.loads(row[0])
                for policy in policies:
                    policy_counts[policy] = policy_counts.get(policy, 0) + row[1]
            except:
                pass
        
        # Calculate percentages
        total = sum(policy_counts.values())
        if total == 0:
            return []
        
        breakdown = []
        for policy_id, count in sorted(policy_counts.items(), key=lambda x: x[1], reverse=True):
            breakdown.append({
                "policy_id": policy_id,
                "count": count,
                "percentage": round((count / total) * 100, 1)
            })
        
        return breakdown
    except:
        return []


def get_event_breakdown() -> List[Dict[str, Any]]:
    """Get event counts by type."""
    conn = get_db_connection()
    
    try:
        df = pd.read_sql("""
            SELECT event, COUNT(*) as count
            FROM coach_events
            GROUP BY event
        """, conn)
        
        if df.empty:
            return []
        
        total = df['count'].sum()
        
        breakdown = []
        for _, row in df.iterrows():
            breakdown.append({
                "event_type": row['event'],
                "count": int(row['count']),
                "percentage": round((row['count'] / total) * 100, 1)
            })
        
        return sorted(breakdown, key=lambda x: x['count'], reverse=True)
    except:
        return []


def get_example_rewrites(limit: int = 5) -> List[Dict[str, Any]]:
    """Get example before/after rewrites."""
    conn = get_db_connection()
    
    try:
        rows = conn.execute("""
            SELECT agent_draft, suggestion_used, policy_refs
            FROM coach_events
            WHERE event IN ('accepted', 'edited')
              AND suggestion_used IS NOT NULL
              AND LENGTH(agent_draft) < 150
            ORDER BY ts DESC
            LIMIT ?
        """, [limit]).fetchall()
        
        examples = []
        severity_map = {
            "PII-SSN": "critical",
            "ADV-6.2": "high",
            "DISC-1.1": "medium",
            "TONE": "low"
        }
        
        for row in rows:
            try:
                policies = json.loads(row[2])
                policy_str = ", ".join(policies[:2])  # Show first 2
                
                # Get severity of first policy
                severity = "medium"
                if policies:
                    severity = severity_map.get(policies[0], "medium")
                
                examples.append({
                    "before": row[0][:100] + ("..." if len(row[0]) > 100 else ""),
                    "after": row[1][:100] + ("..." if len(row[1]) > 100 else ""),
                    "policy": policy_str or "UNKNOWN",
                    "severity": severity
                })
            except:
                pass
        
        return examples
    except:
        return []


def get_ab_test_results() -> List[Dict[str, Any]]:
    """Get A/B test comparison if available."""
    conn = get_db_connection()
    
    try:
        df = pd.read_sql("""
            SELECT 
                ab_test_bucket,
                COUNT(*) as total,
                SUM(CASE WHEN event IN ('accepted', 'edited') THEN 1 ELSE 0 END) as accepted,
                AVG(latency_ms) as avg_latency
            FROM coach_events
            WHERE ab_test_bucket IS NOT NULL
            GROUP BY ab_test_bucket
        """, conn)
        
        if df.empty:
            return []
        
        results = []
        for _, row in df.iterrows():
            accept_rate = (row['accepted'] / row['total'] * 100) if row['total'] > 0 else 0
            results.append({
                "name": row['ab_test_bucket'],
                "count": int(row['total']),
                "accept_rate": round(accept_rate, 1),
                "avg_latency": int(row['avg_latency']) if row['avg_latency'] else 0
            })
        
        return results
    except:
        return []


def generate_report(output_dir: str = None):
    """
    Generate HTML report with all metrics and insights.
    
    Args:
        output_dir: Output directory for report (default: ./data/reports)
    """
    if output_dir is None:
        output_dir = "./data/reports"
    
    # Ensure output directory exists
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Collect data
    total_violations = calculate_violations_prevented()
    accept_rate = calculate_accept_rate()
    latency = calculate_latency_metrics()
    policy_breakdown = get_policy_breakdown()
    event_breakdown = get_event_breakdown()
    examples = get_example_rewrites(limit=5)
    ab_test_results = get_ab_test_results()
    
    # Prepare template data
    template_data = {
        "report_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_violations": total_violations,
        "total_suggestions": total_violations,  # Same for now
        "accept_rate": accept_rate,
        "avg_latency": latency["avg"],
        "p95_latency": latency["p95"],
        "p99_latency": latency["p99"],
        "policy_breakdown": policy_breakdown,
        "event_breakdown": event_breakdown,
        "examples": examples,
        "ab_test_enabled": len(ab_test_results) > 0,
        "ab_test_results": ab_test_results
    }
    
    # Load and render template
    template_dir = Path(__file__).parent / "templates"
    env = Environment(loader=FileSystemLoader(str(template_dir)))
    template = env.get_template("report.html.j2")
    
    html_content = template.render(**template_data)
    
    # Write report
    output_filename = f"CoachEffect_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    output_path = Path(output_dir) / output_filename
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✓ Report generated: {output_path}")
    print(f"✓ Total violations prevented: {total_violations}")
    print(f"✓ Accept rate: {accept_rate}%")
    print(f"✓ Avg latency: {latency['avg']}ms")
    print(f"✓ P95 latency: {latency['p95']}ms")
    
    return str(output_path)


def main():
    """Main entry point for report generation."""
    print("Generating QA Coach Effect Report...")
    print("=" * 60)
    
    try:
        report_path = generate_report()
        print("=" * 60)
        print(f"Report available at: {report_path}")
        print("\nOpen in browser to view detailed analytics.")
    except Exception as e:
        print(f"Error generating report: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
