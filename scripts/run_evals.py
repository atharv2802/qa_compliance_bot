"""
Run evaluations on a batch of test cases.

This script runs the LLM-as-a-judge evaluator on suggestions
to measure quality and generate evaluation reports.
"""

import os
import sys
import json
import time
from datetime import datetime
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()


def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def run_batch_evaluation(
    test_cases: List[Dict],
    output_file: str = None
) -> Dict:
    """
    Run evaluation on a batch of test cases.
    
    Args:
        test_cases: List of dicts with 'agent_draft', 'suggestion', 'policy_refs', etc.
        output_file: Optional file path to save results
    
    Returns:
        Dict with evaluation summary and detailed results
    """
    from app.evals.judge import evaluate_suggestion
    
    results = []
    scores = {
        "overall": [],
        "compliance": [],
        "clarity": [],
        "tone": [],
        "completeness": []
    }
    
    print(f"Running evaluations on {len(test_cases)} test cases...")
    print(f"Judge: {os.getenv('JUDGE_PROVIDER', 'openai')}/{os.getenv('JUDGE_MODEL', 'gpt-4o-mini')}")
    print()
    
    for i, case in enumerate(test_cases, 1):
        print(f"[{i}/{len(test_cases)}] Evaluating... ", end="", flush=True)
        
        start_time = time.time()
        
        try:
            eval_result = evaluate_suggestion(
                agent_draft=case["agent_draft"],
                suggestion=case["suggestion"],
                policy_refs=case.get("policy_refs", []),
                context=case.get("context", ""),
                required_disclosures=case.get("required_disclosures", None)
            )
            
            latency = int((time.time() - start_time) * 1000)
            
            # Track scores
            scores["overall"].append(eval_result.overall_score)
            scores["compliance"].append(eval_result.compliance_score)
            scores["clarity"].append(eval_result.clarity_score)
            scores["tone"].append(eval_result.tone_score)
            scores["completeness"].append(eval_result.completeness_score)
            
            # Store result
            result = {
                "case_id": case.get("id", f"case_{i}"),
                "agent_draft": case["agent_draft"],
                "suggestion": case["suggestion"],
                "policy_refs": case.get("policy_refs", []),
                "overall_score": eval_result.overall_score,
                "compliance_score": eval_result.compliance_score,
                "clarity_score": eval_result.clarity_score,
                "tone_score": eval_result.tone_score,
                "completeness_score": eval_result.completeness_score,
                "pass_threshold": eval_result.pass_threshold,
                "feedback": eval_result.feedback,
                "strengths": eval_result.strengths,
                "weaknesses": eval_result.weaknesses,
                "latency_ms": latency
            }
            
            results.append(result)
            
            status = "✅ PASS" if eval_result.pass_threshold else "❌ FAIL"
            print(f"{status} (score: {eval_result.overall_score:.1f}, {latency}ms)")
        
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            results.append({
                "case_id": case.get("id", f"case_{i}"),
                "agent_draft": case["agent_draft"],
                "suggestion": case["suggestion"],
                "error": str(e)
            })
    
    # Calculate summary statistics
    summary = {
        "total_cases": len(test_cases),
        "successful_evals": len([r for r in results if "error" not in r]),
        "failed_evals": len([r for r in results if "error" in r]),
        "pass_rate": len([r for r in results if r.get("pass_threshold", False)]) / len(results) * 100,
        "avg_overall_score": sum(scores["overall"]) / len(scores["overall"]) if scores["overall"] else 0,
        "avg_compliance_score": sum(scores["compliance"]) / len(scores["compliance"]) if scores["compliance"] else 0,
        "avg_clarity_score": sum(scores["clarity"]) / len(scores["clarity"]) if scores["clarity"] else 0,
        "avg_tone_score": sum(scores["tone"]) / len(scores["tone"]) if scores["tone"] else 0,
        "avg_completeness_score": sum(scores["completeness"]) / len(scores["completeness"]) if scores["completeness"] else 0,
        "timestamp": datetime.now().isoformat()
    }
    
    output = {
        "summary": summary,
        "results": results
    }
    
    # Save to file if specified
    if output_file:
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, "w") as f:
            json.dump(output, f, indent=2)
        print(f"\n✅ Results saved to: {output_file}")
    
    return output


def print_summary(output: Dict):
    """Print evaluation summary."""
    summary = output["summary"]
    
    print_section("Evaluation Summary")
    
    print(f"Total Cases:      {summary['total_cases']}")
    print(f"Successful Evals: {summary['successful_evals']}")
    print(f"Failed Evals:     {summary['failed_evals']}")
    print(f"Pass Rate:        {summary['pass_rate']:.1f}%")
    print()
    print("Average Scores (0-10 scale):")
    print(f"  Overall:        {summary['avg_overall_score']:.2f}")
    print(f"  Compliance:     {summary['avg_compliance_score']:.2f}")
    print(f"  Clarity:        {summary['avg_clarity_score']:.2f}")
    print(f"  Tone:           {summary['avg_tone_score']:.2f}")
    print(f"  Completeness:   {summary['avg_completeness_score']:.2f}")


def print_detailed_results(output: Dict, top_n: int = 5):
    """Print detailed results for top and bottom performers."""
    results = output["results"]
    results_with_scores = [r for r in results if "overall_score" in r]
    
    if not results_with_scores:
        return
    
    # Sort by overall score
    sorted_results = sorted(results_with_scores, key=lambda x: x["overall_score"], reverse=True)
    
    # Top performers
    print_section(f"Top {top_n} Performers")
    for i, result in enumerate(sorted_results[:top_n], 1):
        print(f"{i}. Score: {result['overall_score']:.1f} (ID: {result['case_id']})")
        print(f"   Agent Draft: {result['agent_draft'][:80]}...")
        print(f"   Suggestion:  {result['suggestion'][:80]}...")
        print(f"   Strengths: {', '.join(result['strengths'][:3])}")
        print()
    
    # Bottom performers
    print_section(f"Bottom {top_n} Performers")
    for i, result in enumerate(sorted_results[-top_n:], 1):
        print(f"{i}. Score: {result['overall_score']:.1f} (ID: {result['case_id']})")
        print(f"   Agent Draft: {result['agent_draft'][:80]}...")
        print(f"   Suggestion:  {result['suggestion'][:80]}...")
        print(f"   Weaknesses: {', '.join(result['weaknesses'][:3])}")
        print()


def load_test_cases_from_db(limit: int = 50) -> List[Dict]:
    """Load test cases from synthetic data in DuckDB."""
    import duckdb
    
    db_path = os.getenv("RUNS_DB", "./data/qa_runs.duckdb")
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        print("   Run scripts/seed_synthetic.py first to generate test data.")
        return []
    
    conn = duckdb.connect(db_path, read_only=True)
    
    # Get events with suggestions
    rows = conn.execute(f"""
        SELECT 
            id,
            agent_draft,
            suggestion_used as suggestion,
            policy_refs
        FROM coach_events
        WHERE suggestion_used IS NOT NULL
        AND event = 'accepted'
        LIMIT {limit}
    """).fetchall()
    
    conn.close()
    
    test_cases = []
    for row in rows:
        policy_refs = json.loads(row[3]) if row[3] else []
        test_cases.append({
            "id": row[0],
            "agent_draft": row[1],
            "suggestion": row[2],
            "policy_refs": policy_refs,
            "context": ""
        })
    
    return test_cases


def create_sample_test_cases() -> List[Dict]:
    """Create sample test cases for evaluation."""
    return [
        {
            "id": "sample_1",
            "agent_draft": "We guarantee 12% annual returns on all investments.",
            "suggestion": "Historical performance has shown varying results, and past performance does not guarantee future returns.",
            "policy_refs": ["ADV-6.2"],
            "context": "Customer asking about investment returns"
        },
        {
            "id": "sample_2",
            "agent_draft": "Your SSN is 123-45-6789. Let me update your account.",
            "suggestion": "I can help update your account. For security, please verify your identity through our secure portal.",
            "policy_refs": ["PII-SSN"],
            "context": "Customer account update request"
        },
        {
            "id": "sample_3",
            "agent_draft": "This investment is perfect for everyone!",
            "suggestion": "This investment option may be suitable depending on your individual financial situation and goals. For important disclosures, visit our website.",
            "policy_refs": ["DISC-1.1"],
            "context": "Customer asking about investment products",
            "required_disclosures": ["For important disclosures, visit our website."]
        },
        {
            "id": "sample_4",
            "agent_draft": "You're an idiot if you don't buy this.",
            "suggestion": "This product has features that many customers find valuable. I'd be happy to discuss whether it fits your needs.",
            "policy_refs": ["TONE"],
            "context": "Aggressive sales attempt"
        },
        {
            "id": "sample_5",
            "agent_draft": "Our fund never loses money, ever.",
            "suggestion": "Our fund has a strong historical track record, though all investments carry some level of risk. Past performance does not guarantee future results.",
            "policy_refs": ["ADV-6.2"],
            "context": "Customer asking about fund performance"
        }
    ]


def main():
    """Run the evaluation script."""
    print("\n" + "📊" * 35)
    print("  QA COACH - BATCH EVALUATION")
    print("  LLM-as-a-Judge Quality Assessment")
    print("📊" * 35)
    
    # Check if judge is configured
    judge_provider = os.getenv("JUDGE_PROVIDER", "openai")
    judge_model = os.getenv("JUDGE_MODEL", "gpt-4o-mini")
    
    print(f"\n🔍 Judge Configuration:")
    print(f"   Provider: {judge_provider}")
    print(f"   Model: {judge_model}")
    
    # Determine test cases source
    use_db = "--db" in sys.argv
    limit = 50
    
    if "--limit" in sys.argv:
        idx = sys.argv.index("--limit")
        if idx + 1 < len(sys.argv):
            limit = int(sys.argv[idx + 1])
    
    if use_db:
        print(f"\n📁 Loading test cases from database (limit: {limit})...")
        test_cases = load_test_cases_from_db(limit=limit)
        if not test_cases:
            print("\n⚠️  No test cases found in database. Using sample cases instead.")
            test_cases = create_sample_test_cases()
    else:
        print(f"\n📝 Using sample test cases...")
        test_cases = create_sample_test_cases()
    
    if not test_cases:
        print("\n❌ No test cases available.")
        return
    
    # Run evaluation
    output_file = f"./data/eval_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    output = run_batch_evaluation(test_cases, output_file=output_file)
    
    # Print results
    print_summary(output)
    print_detailed_results(output, top_n=3)
    
    # Usage instructions
    print_section("Next Steps")
    print("📈 Analyze results:")
    print(f"   • View JSON: {output_file}")
    print(f"   • Pass rate: {output['summary']['pass_rate']:.1f}%")
    print()
    print("🔧 Improve scores by:")
    print("   • Tuning coach prompts (app/coach.py)")
    print("   • Adjusting policy rules (policies/policies.yaml)")
    print("   • Testing different LLM providers")
    print()
    print("📊 Run more evaluations:")
    print("   • Sample cases:  python scripts/run_evals.py")
    print("   • From database: python scripts/run_evals.py --db --limit 100")
    print()


if __name__ == "__main__":
    main()
