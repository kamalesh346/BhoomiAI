import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from db.database import _conn

def update_schema():
    c = _conn()
    cur = c.cursor()

    try:
        cur.execute("ALTER TABLE chat_sessions ADD COLUMN summary TEXT;")
        print("✅ Added 'summary' column to chat_sessions.")
    except Exception as e:
        print(f"ℹ️ Could not add 'summary' column (might already exist): {e}")

    try:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS chat_choices (
            id INT AUTO_INCREMENT PRIMARY KEY,
            chat_session_id INT,
            message_id VARCHAR(255),
            selected_option VARCHAR(255),
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
