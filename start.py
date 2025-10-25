#!/usr/bin/env python3
"""
Startup script for QA Compliance Bot
Handles both local and production environments
"""

import os
import sys
import subprocess
from pathlib import Path

def check_env_file():
    """Check if .env file exists, create from example if not."""
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists():
        if env_example.exists():
            print("⚠️  .env file not found. Creating from .env.example...")
            env_example.read_text().replace("MODE=local", "MODE=local")
            env_file.write_text(env_example.read_text())
            print("✓ .env file created. Please edit it with your API keys.")
            return False
        else:
            print("❌ Neither .env nor .env.example found!")
            return False
    return True

def check_dependencies():
    """Check if required packages are installed."""
    try:
        import fastapi
        import streamlit
        import duckdb
        return True
    except ImportError as e:
        print(f"❌ Missing dependencies: {e}")
        print("Run: pip install -r requirements.txt")
        return False

def start_api():
    """Start the FastAPI server."""
    print("\n🚀 Starting FastAPI API server...")
    print("📍 API will be available at: http://localhost:8000")
    print("📚 API docs at: http://localhost:8000/docs")
    
    subprocess.Popen([
        sys.executable, "-m", "uvicorn",
        "app.api:app",
        "--reload",
        "--host", "0.0.0.0",
        "--port", "8000"
    ])

def start_dashboard():
    """Start the Streamlit dashboard."""
    print("\n🎨 Starting Streamlit dashboard...")
    print("📍 Dashboard will be available at: http://localhost:8501")
    
    subprocess.run([
        sys.executable, "-m", "streamlit",
        "run",
        "app/dashboard.py",
        "--server.port", "8501"
    ])

def main():
    """Main startup function."""
    print("=" * 60)
    print("QA Compliance Bot - Startup")
    print("=" * 60)
    
    # Check environment
    if not check_env_file():
        sys.exit(1)
    
    if not check_dependencies():
        sys.exit(1)
    
    # Get mode from environment
    from dotenv import load_dotenv
    load_dotenv()
    mode = os.getenv("MODE", "local")
    
    print(f"\n📊 Running in {mode.upper()} mode")
    
    # Show what will start
    print("\nStarting services:")
    print("  1. FastAPI API (port 8000)")
    print("  2. Streamlit Dashboard (port 8501)")
    print("\nPress Ctrl+C to stop all services\n")
    
    try:
        # Start API in background
        start_api()
        
        # Wait a moment for API to start
        import time
        time.sleep(3)
        
        # Start dashboard (blocks)
        start_dashboard()
        
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down services...")
        sys.exit(0)

if __name__ == "__main__":
    main()
