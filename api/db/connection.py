import sys
from pathlib import Path

# Ensure root directory is accessible so we can reuse config and db.database
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from db.database import _conn

def get_db_connection():
    return _conn()
