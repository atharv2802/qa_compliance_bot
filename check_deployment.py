#!/usr/bin/env python3
"""
Simple Deployment Readiness Check
Verifies files are in place without requiring dependencies
"""

import os
from pathlib import Path

def check_file(filepath, description):
    """Check if file exists."""
    exists = Path(filepath).exists()
    status = "✓" if exists else "✗"
    print(f"{status} {description:<40} {filepath}")
    return exists

def main():
    print("=" * 70)
    print("QA Compliance Bot - Deployment Readiness Check")
    print("=" * 70)
    print()
    
    checks = []
    
    print("📁 Core Files:")
    checks.append(check_file("requirements.txt", "Dependencies list"))
    checks.append(check_file("start.py", "Startup script"))
    checks.append(check_file(".env.example", "Environment template"))
    checks.append(check_file("render.yaml", "Render blueprint"))
    print()
    
    print("📚 Documentation:")
    checks.append(check_file("README.md", "Main readme"))
    checks.append(check_file("ARCHITECTURE.md", "Architecture guide"))
    checks.append(check_file("EXTRAS.md", "Extras & deployment guide"))
    print()
    
    print("🐍 Application Code:")
    checks.append(check_file("app/api.py", "FastAPI server"))
    checks.append(check_file("app/dashboard.py", "Streamlit dashboard"))
    checks.append(check_file("app/coach.py", "Core logic"))
    checks.append(check_file("engine/rules.py", "Rules engine"))
    print()
    
    print("⚙️  Configuration:")
    checks.append(check_file("policies/policies.yaml", "Policy definitions"))
    checks.append(check_file("configs/config.yaml", "App config"))
    print()
    
    print("🧪 Testing:")
    checks.append(check_file("tests/test_coach_guardrails.py", "Coach tests"))
    checks.append(check_file("tests/test_rules.py", "Rules tests"))
    print()
    
    # Check .env
    print("🔐 Environment:")
    if Path(".env").exists():
        print("✓ .env file exists (contains secrets)")
        checks.append(True)
    else:
        print("⚠️  .env not found - create from .env.example")
        print("   Run: copy .env.example .env (Windows)")
        print("   Run: cp .env.example .env (Linux/Mac)")
        checks.append(False)
    print()
    
    # Check gitignore
    print("🔒 Security:")
    if Path(".gitignore").exists():
        with open(".gitignore", "r") as f:
            content = f.read()
            if ".env" in content:
                print("✓ .gitignore protects .env file")
                checks.append(True)
            else:
                print("⚠️  .env not in .gitignore!")
                checks.append(False)
    print()
    
    # Summary
    print("=" * 70)
    passed = sum(checks)
    total = len(checks)
    percentage = (passed / total) * 100
    
    print(f"Results: {passed}/{total} checks passed ({percentage:.1f}%)")
    print()
    
    if all(checks):
        print("✅ READY FOR DEPLOYMENT!")
        print()
        print("Next steps:")
        print("  1. Install dependencies: pip install -r requirements.txt")
        print("  2. Configure .env with your API keys")
        print("  3. Local test: python start.py")
        print("  4. Deploy to Render: git push origin main")
        print()
        print("📖 Documentation:")
        print("  • README.md - Quick start and overview")
        print("  • ARCHITECTURE.md - System architecture details")
        print("  • EXTRAS.md - Deployment, guides, troubleshooting")
        return 0
    else:
        print("⚠️  SOME FILES MISSING - Please review above")
        print()
        print("This may be normal if:")
        print("  • You haven't created .env yet (copy from .env.example)")
        print("  • You're checking a partial clone")
        return 1

if __name__ == "__main__":
    exit(main())
