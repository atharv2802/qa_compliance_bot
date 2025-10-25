#!/usr/bin/env python3
"""
Configuration Verification Script
Checks if the deployment setup is correct for both local and production modes
"""

import os
import sys
from pathlib import Path

def check_file_exists(filepath, description):
    """Check if a file exists."""
    if Path(filepath).exists():
        print(f"✓ {description}: {filepath}")
        return True
    else:
        print(f"✗ {description} missing: {filepath}")
        return False

def check_env_file():
    """Check environment file."""
    if Path(".env").exists():
        print("✓ .env file exists")
        # Check for required variables
        from dotenv import load_dotenv
        load_dotenv()
        
        required = ["LLM_PROVIDER", "MODE"]
        optional = ["GROQ_API_KEY", "OPENAI_API_KEY", "API_URL"]
        
        missing = []
        for var in required:
            if not os.getenv(var):
                missing.append(var)
        
        if missing:
            print(f"  ⚠️  Missing required variables: {', '.join(missing)}")
            return False
        else:
            print(f"  ✓ Required variables present")
            
        mode = os.getenv("MODE", "local")
        print(f"  ℹ️  Current MODE: {mode}")
        
        return True
    else:
        print("✗ .env file not found")
        print("  Run: copy .env.example .env")
        return False

def check_dependencies():
    """Check if dependencies are installed."""
    try:
        import fastapi
        import streamlit
        import duckdb
        import dotenv
        print("✓ Core dependencies installed")
        return True
    except ImportError as e:
        print(f"✗ Missing dependency: {e}")
        print("  Run: pip install -r requirements.txt")
        return False

def check_render_config():
    """Check render.yaml configuration."""
    if not Path("render.yaml").exists():
        print("✗ render.yaml not found")
        return False
    
    print("✓ render.yaml exists")
    
    # Check content
    with open("render.yaml", "r") as f:
        content = f.read()
        
        checks = {
            "qa-compliance-api": "API service defined",
            "qa-compliance-dashboard": "Dashboard service defined",
            "sync: false": "Secrets properly configured",
            "MODE": "MODE variable present",
            "disk:": "Persistent disk configured"
        }
        
        for check, desc in checks.items():
            if check in content:
                print(f"  ✓ {desc}")
            else:
                print(f"  ⚠️  {desc} - not found")
    
    return True

def check_code_modifications():
    """Check if code has been properly modified."""
    checks = []
    
    # Check api.py
    with open("app/api.py", "r") as f:
        api_content = f.read()
        if 'MODE = os.getenv("MODE"' in api_content:
            print("✓ app/api.py: MODE configuration added")
            checks.append(True)
        else:
            print("✗ app/api.py: MODE configuration missing")
            checks.append(False)
    
    # Check dashboard.py
    with open("app/dashboard.py", "r") as f:
        dash_content = f.read()
        if 'MODE = os.getenv("MODE"' in dash_content:
            print("✓ app/dashboard.py: MODE configuration added")
            checks.append(True)
        else:
            print("✗ app/dashboard.py: MODE configuration missing")
            checks.append(False)
    
    return all(checks)

def main():
    """Main verification function."""
    print("=" * 60)
    print("QA Compliance Bot - Deployment Configuration Verification")
    print("=" * 60)
    print()
    
    results = []
    
    # Check required files
    print("📁 Checking Required Files...")
    results.append(check_file_exists("requirements.txt", "Requirements"))
    results.append(check_file_exists(".env.example", "Environment template"))
    results.append(check_file_exists("render.yaml", "Render blueprint"))
    results.append(check_file_exists("start.py", "Startup script"))
    results.append(check_file_exists("DEPLOYMENT.md", "Deployment guide"))
    print()
    
    # Check documentation
    print("📚 Checking Documentation...")
    results.append(check_file_exists("QUICKSTART_DEPLOYMENT.md", "Quick start"))
    results.append(check_file_exists("DEPLOYMENT_SUMMARY.md", "Summary"))
    print()
    
    # Check environment
    print("🔧 Checking Environment Configuration...")
    results.append(check_env_file())
    print()
    
    # Check dependencies
    print("📦 Checking Dependencies...")
    results.append(check_dependencies())
    print()
    
    # Check render config
    print("☁️  Checking Render Configuration...")
    results.append(check_render_config())
    print()
    
    # Check code modifications
    print("💻 Checking Code Modifications...")
    results.append(check_code_modifications())
    print()
    
    # Final result
    print("=" * 60)
    if all(results):
        print("✅ ALL CHECKS PASSED - Ready for deployment!")
        print()
        print("Next steps:")
        print("  1. Local: python start.py")
        print("  2. Production: git push origin main (then connect to Render)")
        print()
        print("📖 See DEPLOYMENT.md for full instructions")
        return 0
    else:
        print("❌ SOME CHECKS FAILED - Please fix issues above")
        print()
        print("Common fixes:")
        print("  • Missing .env: copy .env.example .env")
        print("  • Missing deps: pip install -r requirements.txt")
        print("  • Check DEPLOYMENT.md for troubleshooting")
        return 1

if __name__ == "__main__":
    sys.exit(main())
