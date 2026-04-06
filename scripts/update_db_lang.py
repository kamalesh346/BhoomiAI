import sys
from pathlib import Path
import os
from dotenv import load_dotenv
import pymysql

sys.path.insert(0, str(Path(__file__).parent.parent))

from db.database import _parse_mysql_url, DATABASE_URL

def update_schema():
    print(f"Connecting to database: {DATABASE_URL}")
    params = _parse_mysql_url(DATABASE_URL)
    conn = pymysql.connect(**params)
    cur = conn.cursor()
    
    try:
        print("Checking for language_preference column in farmers table...")
        cur.execute("SHOW COLUMNS FROM farmers LIKE 'language_preference'")
        result = cur.fetchone()
        
        if not result:
            print("Adding language_preference column...")
            cur.execute("ALTER TABLE farmers ADD COLUMN language_preference VARCHAR(10) DEFAULT 'en'")
            conn.commit()
            print("✅ Column added successfully.")
        else:
            print("✅ Column already exists.")
            
    except Exception as e:
        print(f"❌ Failed to update schema: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    update_schema()
