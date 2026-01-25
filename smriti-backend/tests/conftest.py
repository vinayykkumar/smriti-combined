"""
Pytest configuration for test suite.
Verifies that tests are using the test database, not production.
"""
import os
import sys
from pathlib import Path

# Set test environment variables BEFORE any app imports
# This prevents ValidationError when settings module loads
os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("MONGODB_URI", "mongodb://localhost:27017")
os.environ.setdefault("DATABASE_NAME", "smriti_test")
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-testing-only-not-for-production")
os.environ.setdefault("CRON_SECRET", "test-cron-secret-for-testing-only")

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Now try to load .env (will override defaults if .env exists)
try:
    from dotenv import load_dotenv
    load_dotenv(project_root / ".env")
except ImportError:
    pass  # dotenv not required for tests

def pytest_configure(config):
    """
    Verify test database is being used before running tests.
    """
    db_name = os.getenv("DATABASE_NAME", "")
    
    if "test" in db_name.lower():
        print(f"[OK] Using test database: {db_name}")
    else:
        print(f"\n{'='*60}")
        print(f"[WARNING] Using database '{db_name}'")
        print(f"[WARNING] This may NOT be a test database!")
        print(f"[WARNING] Update DATABASE_NAME in .env to 'smriti_test' before testing")
        print(f"{'='*60}\n")
        
        # Uncomment the line below to prevent tests from running on production
        # raise RuntimeError("Refusing to run tests on non-test database")
