import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from db.database import _conn

def update_schema():
    c = _conn()
    cur = c.cursor()

    # Create pest_history table - USING INT UNSIGNED
    try:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS pest_history (
            id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
            farmer_id INT UNSIGNED,
            pest_name VARCHAR(100),
            affected_crop VARCHAR(100),
            severity VARCHAR(20),
            observation_date DATE,
            description TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (farmer_id) REFERENCES farmers(id) ON DELETE CASCADE
        )
        """)
        print("✅ Created 'pest_history' table.")
    except Exception as e:
        print(f"❌ Failed to create 'pest_history' table: {e}")

    c.commit()
    cur.close()
    c.close()

if __name__ == "__main__":
    print("Updating database schema...")
    update_schema()
