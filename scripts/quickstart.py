"""
Quick start script for QA Coach.

Helps users set up and run the system quickly.
"""

import os
import sys
from pathlib import Path


def check_python_version():
    """Check Python version."""
    if sys.version_info < (3, 10):
        print("❌ Python 3.10 or higher required")
        print(f"   Current version: {sys.version}")
        return False
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor}")
    return True


def check_env_file():
    """Check if .env file exists."""
    if not os.path.exists(".env"):
        print("⚠ .env file not found")
        print("  Creating from .env.example...")
        
        if os.path.exists(".env.example"):
            import shutil
            shutil.copy(".env.example", ".env")
            print("  ✓ Created .env file")
            print("  ⚠ Please edit .env and add your OPENAI_API_KEY")
            return False
        else:
            print("  ❌ .env.example not found")
            return False
    
    print("✓ .env file exists")
    
    # Check if API key is set
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your_openai_api_key_here":
        print("  ⚠ OPENAI_API_KEY not set in .env")
        return False
    
    print("✓ OPENAI_API_KEY configured")
    return True


def check_dependencies():
    """Check if dependencies are installed."""
    try:
        import fastapi
        import streamlit
        import duckdb
        import openai
        print("✓ Dependencies installed")
        return True
    except ImportError as e:
        print(f"⚠ Missing dependencies: {e}")
        print("  Run: pip install -r requirements.txt")
        return False


def generate_seed_data():
    """Generate synthetic seed data."""
    print("\n🌱 Generating seed data...")
    
    try:
        from scripts.seed_synthetic import main as seed_main
        seed_main()
        return True
    except Exception as e:
        print(f"❌ Error generating seed data: {e}")
        return False


def main():
    """Run quick start checks and setup."""
    print("=" * 60)
    print("QA Coach - Quick Start")
    print("=" * 60)
    print()
    
    # Run checks
    checks = [
        ("Python Version", check_python_version()),
        ("Dependencies", check_dependencies()),
        ("Environment", check_env_file()),
    ]
    
    print()
    print("=" * 60)
    print("Setup Status")
    print("=" * 60)
    
    all_passed = all(result for _, result in checks)
    
    if not all_passed:
        print("\n⚠ Setup incomplete. Please address the issues above.")
        print("\nQuick setup commands:")
        print("  1. pip install -r requirements.txt")
        print("  2. cp .env.example .env")
        print("  3. Edit .env and add your OPENAI_API_KEY")
        print("  4. python scripts/quickstart.py")
        sys.exit(1)
    
    print("\n✓ All checks passed!")
    
    # Generate seed data
    if not os.path.exists("./data/synthetic/coach_cases.jsonl"):
        if generate_seed_data():
            print("✓ Seed data generated")
    else:
        print("✓ Seed data already exists")
    
    print()
    print("=" * 60)
    print("Ready to Go! 🚀")
    print("=" * 60)
    print()
    print("Next steps:")
    print()
    print("1. Start the API server:")
    print("   > make api")
    print("   or")
    print("   > uvicorn app.api:app --reload --port 8000")
    print()
    print("2. In another terminal, start the Streamlit dashboard:")
    print("   > make ui")
    print("   or")
    print("   > streamlit run app/dashboard.py")
    print()
    print("3. Run tests:")
    print("   > make test")
    print("   or")
    print("   > pytest -v")
    print()
    print("4. Generate a report:")
    print("   > make report")
    print("   or")
    print("   > python reports/aggregations.py")
    print()
    print("API will be available at: http://localhost:8000")
    print("Dashboard will be available at: http://localhost:8501")
    print("API docs at: http://localhost:8000/docs")
    print()


if __name__ == "__main__":
    main()
