#!/usr/bin/env python3
"""
Run this script once to initialize the database and seed test data.
Usage: python scripts/init_db.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from db.database import init_db, seed_test_data

if __name__ == "__main__":
    print("Initializing database schema...")
    try:
        init_db()
        print("Schema created successfully.")
    except Exception as e:
        print(f"Schema creation failed: {e}")
        sys.exit(1)

    print("Seeding test data...")
    try:
        seed_test_data()
        print("Test data seeded.")
        print("\nTest credentials:")
        print("   Email:    test@farmer.com")
        print("   Password: test123")
    except Exception as e:
        print(f"Seeding failed: {e}")
        sys.exit(1)

    print("\nDatabase ready! Run: streamlit run app.py")
