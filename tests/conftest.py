"""
Pytest configuration and fixtures.
"""

import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set test environment variables
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "test-key-placeholder")
os.environ["DATA_DIR"] = "./test_data"
os.environ["RUNS_DB"] = ":memory:"  # Use in-memory DB for tests
