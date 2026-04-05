import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from db.database import _conn

def update_schema():
    c = _conn()
    cur = c.cursor()

    # Update farmers table
    try:
        cur.execute("ALTER TABLE farmers ADD COLUMN soil_type_distribution TEXT;")
        print("✅ Added 'soil_type_distribution' column to farmers.")
    except Exception:
        print("ℹ️ 'soil_type_distribution' column already exists.")

    try:
        cur.execute("ALTER TABLE farmers ADD COLUMN recent_pest_activity TEXT;")
        print("✅ Added 'recent_pest_activity' column to farmers.")
    except Exception:
        print("ℹ️ 'recent_pest_activity' column already exists.")

    try:
        cur.execute("ALTER TABLE farmers MODIFY COLUMN equipment TEXT;")
        print("✅ Modified 'equipment' column to TEXT in farmers.")
    except Exception:
        print("ℹ️ Could not modify 'equipment' column.")

    # Update chat_sessions table
    try:
        cur.execute("ALTER TABLE chat_sessions ADD COLUMN summary TEXT;")
        print("✅ Added 'summary' column to chat_sessions.")
    except Exception:
        print("ℹ️ 'summary' column already exists.")

    # Create pest_history table - FIXING TYPE INCOMPATIBILITY (using INT)
    try:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS pest_history (
            id INT AUTO_INCREMENT PRIMARY KEY,
            farmer_id INT,
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

    # Create chat_choices table
    try:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS chat_choices (
            id INT AUTO_INCREMENT PRIMARY KEY,
            chat_session_id INT,
            message_id VARCHAR(100),
            selected_option VARCHAR(10),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (chat_session_id) REFERENCES chat_sessions(id) ON DELETE CASCADE
        )
        """)
        print("✅ Created 'chat_choices' table.")
    except Exception as e:
        print(f"❌ Failed to create 'chat_choices' table: {e}")

    c.commit()
    cur.close()
    c.close()

if __name__ == "__main__":
    print("Updating database schema...")
    update_schema()
