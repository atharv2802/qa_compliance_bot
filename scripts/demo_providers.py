"""
Demo script showing multi-provider fallback in action.

Tests primary and fallback providers with simulated failures.
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()


def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def demo_provider_status():
    """Show configured providers and their status."""
    print_section("Provider Status")
    
    try:
        from app.providers.provider_manager import get_provider_manager
        
        manager = get_provider_manager()
        status = manager.get_provider_status()
        
        print(f"Primary Provider: {status['primary']}")
        print(f"Fallback Providers: {', '.join(status['fallbacks']) or 'None'}")
        print()
        print("Provider Availability:")
        for provider, state in status['providers'].items():
            icon = "✅" if state == "available" else "❌"
            print(f"  {icon} {provider}: {state}")
        
        return True
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def demo_normal_operation():
    """Demo normal operation with primary provider."""
    print_section("Normal Operation (Primary Provider)")
    
    try:
        from app.coach import suggest
        from app.providers.provider_manager import get_last_provider_used
        
        response = suggest(
            agent_draft="We guarantee 12% returns every year.",
            context="Customer asking about returns"
        )
        
        provider = get_last_provider_used()
        
        print(f"✅ Suggestion generated successfully")
        print(f"📡 Provider used: {provider}")
        print(f"⏱️  Latency: {response.latency_ms}ms")
        print()
        print(f"Suggestion: {response.suggestion}")
        
        return True
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def demo_fallback_simulation():
    """Demo fallback behavior (informational)."""
    print_section("Fallback Behavior (How It Works)")
    
    print("The system automatically tries providers in order:")
    print()
    print("1. Try PRIMARY provider")
    print("   ├─ Success → Return response")
    print("   └─ Failure → Continue to step 2")
    print()
    print("2. Try FALLBACK #1 provider")
    print("   ├─ Success → Return response")
    print("   └─ Failure → Continue to step 3")
    print()
    print("3. Try FALLBACK #2 provider")
    print("   ├─ Success → Return response")
    print("   └─ Failure → Return error")
    print()
    print("Fallback triggers:")
    print("  • API key errors")
    print("  • Rate limiting (429)")
    print("  • Network timeouts")
    print("  • Service outages")
    print("  • Parse failures")
    print()
    print("Each response includes metadata: '_provider_used'")


def demo_configuration_examples():
    """Show configuration examples."""
    print_section("Configuration Examples")
    
    examples = [
        {
            "name": "OpenAI Primary, Anthropic Fallback",
            "env": {
                "LLM_PROVIDER": "openai",
                "LLM_FALLBACK_PROVIDERS": "anthropic",
                "OPENAI_API_KEY": "sk-...",
                "ANTHROPIC_API_KEY": "sk-ant-..."
            },
            "use_case": "High reliability with Claude backup"
        },
        {
            "name": "Groq Primary (Fast), OpenAI Fallback",
            "env": {
                "LLM_PROVIDER": "groq",
                "LLM_FALLBACK_PROVIDERS": "openai",
                "GROQ_API_KEY": "gsk_...",
                "OPENAI_API_KEY": "sk-..."
            },
            "use_case": "Ultra-low latency with reliability backup"
        },
        {
            "name": "Full Redundancy (All Three)",
            "env": {
                "LLM_PROVIDER": "openai",
                "LLM_FALLBACK_PROVIDERS": "anthropic,groq",
                "OPENAI_API_KEY": "sk-...",
                "ANTHROPIC_API_KEY": "sk-ant-...",
                "GROQ_API_KEY": "gsk_..."
            },
            "use_case": "Maximum uptime and reliability"
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"{i}. {example['name']}")
        print(f"   Use Case: {example['use_case']}")
        print(f"   Config:")
        for key, value in example['env'].items():
            if "KEY" in key:
                value = value[:10] + "..." if len(value) > 10 else value
            print(f"     {key}={value}")
        print()


def demo_provider_comparison():
    """Show provider comparison."""
    print_section("Provider Comparison")
    
    print("┌─────────────┬──────────────────┬──────────┬──────────┬──────────┬─────────┐")
    print("│ Provider    │ Model            │ Latency  │ P95      │ Cost/1M  │ Quality │")
    print("├─────────────┼──────────────────┼──────────┼──────────┼──────────┼─────────┤")
    print("│ Groq        │ Llama 3.1 8B     │ 300ms    │ 450ms    │ Free     │ ⭐⭐⭐⭐  │")
    print("│ OpenAI      │ GPT-4o-mini      │ 500ms    │ 700ms    │ $0.15    │ ⭐⭐⭐⭐⭐ │")
    print("│ Anthropic   │ Claude 3 Haiku   │ 600ms    │ 850ms    │ $0.25    │ ⭐⭐⭐⭐⭐ │")
    print("└─────────────┴──────────────────┴──────────┴──────────┴──────────┴─────────┘")
    print()
    print("Recommendations:")
    print("  • Production: OpenAI primary, Anthropic fallback")
    print("  • Development: Groq primary (fast iteration)")
    print("  • Cost-sensitive: Groq primary, OpenAI fallback")


def main():
    """Run the multi-provider demo."""
    print("\n" + "🌐" * 35)
    print("  QA COACH - MULTI-PROVIDER SUPPORT DEMO")
    print("  OpenAI + Anthropic + Groq with Automatic Fallback")
    print("🌐" * 35)
    
    # Check if any provider is configured
    has_openai = bool(os.getenv("OPENAI_API_KEY"))
    has_anthropic = bool(os.getenv("ANTHROPIC_API_KEY"))
    has_groq = bool(os.getenv("GROQ_API_KEY"))
    
    if not (has_openai or has_anthropic or has_groq):
        print("\n⚠️  No LLM providers configured!")
        print()
        print("Please configure at least one provider in your .env file:")
        print()
        print("  # OpenAI")
        print("  OPENAI_API_KEY=sk-...")
        print()
        print("  # Anthropic")
        print("  ANTHROPIC_API_KEY=sk-ant-...")
        print()
        print("  # Groq")
        print("  GROQ_API_KEY=gsk_...")
        print()
        print("See MULTI_PROVIDER_GUIDE.md for detailed setup instructions.")
        return
    
    # Show provider status
    if not demo_provider_status():
        return
    
    # Show normal operation
    demo_normal_operation()
    
    # Explain fallback
    demo_fallback_simulation()
    
    # Show configuration examples
    demo_configuration_examples()
    
    # Show provider comparison
    demo_provider_comparison()
    
    # Summary
    print_section("Summary")
    print("✅ Multi-provider support enables:")
    print("   • Automatic failover for high availability")
    print("   • Cost optimization (use cheaper providers first)")
    print("   • Latency optimization (use faster providers)")
    print("   • Vendor diversification")
    print()
    print("📚 Documentation:")
    print("   • Full guide: MULTI_PROVIDER_GUIDE.md")
    print("   • API status: GET /providers/status")
    print("   • Test providers: pytest tests/test_provider_manager.py")
    print()
    print("🔧 Current Configuration:")
    print(f"   Primary: {os.getenv('LLM_PROVIDER', 'openai')}")
    print(f"   Fallbacks: {os.getenv('LLM_FALLBACK_PROVIDERS', 'none')}")
    print()


if __name__ == "__main__":
    main()
