"""
Demo script for QA Coach.

Demonstrates the system with example API calls and showcases key features.
"""

import requests
import json
import time
from typing import Dict, Any


API_BASE_URL = "http://localhost:8000"


def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def print_response(response: Dict[Any, Any]):
    """Pretty print a response."""
    print(json.dumps(response, indent=2))


def demo_health_check():
    """Demo: Health check endpoint."""
    print_section("1. Health Check")
    
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        print(f"Status: {response.status_code}")
        print_response(response.json())
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure the API server is running: make api")
        return False


def demo_guaranteed_returns():
    """Demo: Guaranteed returns violation."""
    print_section("2. Guaranteed Returns Violation (ADV-6.2)")
    
    payload = {
        "session_id": "demo-session-1",
        "agent_draft": "We guarantee 12% annual returns on this investment.",
        "context": "Customer asking about expected returns",
        "policy_hits": ["ADV-6.2"],
        "brand_tone": "professional, clear, empathetic",
        "required_disclosures": ["Investments may lose value."]
    }
    
    print("📤 Request:")
    print(f"  Draft: \"{payload['agent_draft']}\"")
    print(f"  Policy: {payload['policy_hits']}")
    print()
    
    try:
        start = time.time()
        response = requests.post(
            f"{API_BASE_URL}/coach/suggest",
            json=payload,
            timeout=10
        )
        latency = int((time.time() - start) * 1000)
        
        print(f"⏱️  Latency: {latency}ms")
        print()
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Suggestion:")
            print(f"  {data['suggestion']}")
            print()
            print("🔄 Alternates:")
            for i, alt in enumerate(data.get('alternates', []), 1):
                print(f"  {i}. {alt}")
            print()
            print(f"📊 Confidence: {data['confidence']:.0%}")
            print(f"📝 Rationale: {data['rationale']}")
            print(f"🏷️  Policies: {', '.join(data['policy_refs'])}")
            
            # Log event
            log_event("offered", payload["session_id"], payload["agent_draft"], 
                     data["suggestion"], data["policy_refs"], latency)
            
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            print_response(response.json())
            return False
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def demo_pii_detection():
    """Demo: PII detection and blocking."""
    print_section("3. PII Detection (PII-SSN)")
    
    payload = {
        "session_id": "demo-session-2",
        "agent_draft": "I found your account using SSN 123-45-6789.",
        "context": "Account verification",
        "brand_tone": "professional, clear, empathetic"
    }
    
    print("📤 Request:")
    print(f"  Draft: \"{payload['agent_draft']}\"")
    print()
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/coach/suggest",
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print("🛡️  PII Detected - Safe Template Used:")
            print(f"  {data['suggestion']}")
            print()
            print(f"📝 Rationale: {data['rationale']}")
            print(f"🏷️  Policies: {', '.join(data['policy_refs'])}")
            return True
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def demo_inappropriate_tone():
    """Demo: Inappropriate tone detection."""
    print_section("4. Inappropriate Tone (TONE)")
    
    payload = {
        "session_id": "demo-session-3",
        "agent_draft": "Don't be an idiot, just follow the instructions.",
        "context": "Customer confused about process",
        "brand_tone": "professional, clear, empathetic"
    }
    
    print("📤 Request:")
    print(f"  Draft: \"{payload['agent_draft']}\"")
    print()
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/coach/suggest",
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Professional Rewrite:")
            print(f"  {data['suggestion']}")
            print()
            print("🔄 Alternates:")
            for i, alt in enumerate(data.get('alternates', []), 1):
                print(f"  {i}. {alt}")
            return True
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def demo_clean_text():
    """Demo: Clean text (no violations)."""
    print_section("5. Clean Text (No Violations)")
    
    payload = {
        "session_id": "demo-session-4",
        "agent_draft": "I can share our historical performance and explain the risks.",
        "context": "Customer inquiry",
        "brand_tone": "professional, clear, empathetic"
    }
    
    print("📤 Request:")
    print(f"  Draft: \"{payload['agent_draft']}\"")
    print()
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/coach/suggest",
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Minimal Changes:")
            print(f"  {data['suggestion']}")
            print()
            print(f"📊 Confidence: {data['confidence']:.0%}")
            return True
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def log_event(event_type: str, session_id: str, draft: str, 
              suggestion: str, policy_refs: list, latency: int):
    """Log an event to the system."""
    try:
        payload = {
            "event": event_type,
            "session_id": session_id,
            "agent_draft": draft,
            "suggestion_used": suggestion,
            "policy_refs": policy_refs,
            "latency_ms": latency,
            "ab_test_bucket": "on"
        }
        
        requests.post(f"{API_BASE_URL}/events/coach", json=payload, timeout=5)
    except:
        pass  # Silent fail for demo


def demo_event_stats():
    """Demo: Event statistics."""
    print_section("6. Event Statistics")
    
    try:
        response = requests.get(f"{API_BASE_URL}/events/stats", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print(f"📊 Total Events: {data['total_events']}")
            print()
            print("Event Breakdown:")
            for event, count in data['event_counts'].items():
                print(f"  • {event}: {count}")
            return True
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Run the demo."""
    print("\n" + "🎯" * 35)
    print("  QA COACH DEMO")
    print("  Conversational Compliance Coaching in Action")
    print("🎯" * 35)
    
    # Health check first
    if not demo_health_check():
        print("\n❌ API server not responding. Please start it with:")
        print("   make api")
        print("   or")
        print("   uvicorn app.api:app --reload --port 8000")
        return
    
    # Run demos
    demos = [
        demo_guaranteed_returns,
        demo_pii_detection,
        demo_inappropriate_tone,
        demo_clean_text,
        demo_event_stats
    ]
    
    for demo in demos:
        time.sleep(1)  # Brief pause between demos
        try:
            demo()
        except KeyboardInterrupt:
            print("\n\n⚠️  Demo interrupted by user")
            break
        except Exception as e:
            print(f"\n❌ Demo error: {e}")
    
    # Summary
    print_section("Demo Complete!")
    print("✓ Demonstrated key features:")
    print("  • Guaranteed returns detection and rewriting")
    print("  • PII blocking with safe templates")
    print("  • Inappropriate tone correction")
    print("  • Clean text handling")
    print("  • Event logging and statistics")
    print()
    print("Next steps:")
    print("  • Open the Streamlit dashboard: http://localhost:8501")
    print("  • View API docs: http://localhost:8000/docs")
    print("  • Run tests: make test")
    print("  • Generate report: make report")
    print()


if __name__ == "__main__":
    main()
