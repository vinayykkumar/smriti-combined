"""
Pytest configuration for test suite.
Verifies that tests are using the test database, not production.
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables
load_dotenv(project_root / ".env")

def pytest_configure(config):
    """
    Verify test database is being used before running tests.
    """
    db_name = os.getenv("DATABASE_NAME", "")
    
    if "test" in db_name.lower():
        print(f"✓ Using test database: {db_name}")
    else:
        print(f"\n{'='*60}")
        print(f"⚠️  WARNING: Using database '{db_name}'")
        print(f"⚠️  This may NOT be a test database!")
        print(f"⚠️  Update DATABASE_NAME in .env to 'smriti_test' before testing")
        print(f"{'='*60}\n")
        
        # Uncomment the line below to prevent tests from running on production
        # raise RuntimeError("Refusing to run tests on non-test database")
