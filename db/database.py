"""
MySQL Database Layer for Digital Sarathi
"""

import hashlib
import json
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "")


# ─── MySQL URL Parser (FIXED) ────────────────────────────────────────────────
def _parse_mysql_url(url: str) -> dict:
    """
    Parse mysql://user:password@host:port/dbname
    into pymysql.connect(**kwargs)
    """

    url = url.replace("mysql://", "").replace("mysql+pymysql://", "")

    if "@" not in url:
        raise ValueError("Invalid MySQL URL format")

    # 🔥 FIX: rsplit instead of split
    auth, rest = url.rsplit("@", 1)

    user, password = (auth.split(":", 1) + [""])[:2]

    if "/" not in rest:
        raise ValueError("Invalid MySQL URL: missing database name")

    host_port, db = rest.split("/", 1)

    if ":" in host_port:
        host, port_str = host_port.split(":", 1)
        port = int(port_str)
    else:
        host, port = host_port, 3306

    return dict(
        host=host,
        port=port,
        user=user,
        password=password,
        database=db,
        charset="utf8mb4",
        cursorclass=__import__("pymysql").cursors.DictCursor
    )


# ─── DB INIT ────────────────────────────────────────────────────────────────
import pymysql
import pymysql.cursors


def _conn():
    return pymysql.connect(**_parse_mysql_url(DATABASE_URL))


def _hash(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()


# ─── TABLE SETUP ────────────────────────────────────────────────────────────
def init_db():
    c = _conn()
    cur = c.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS farmers (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        email VARCHAR(100) UNIQUE NOT NULL,
        password VARCHAR(64) NOT NULL,
        land_size FLOAT DEFAULT 1.0,
        water_source VARCHAR(50) DEFAULT 'Rain-fed',
        budget INT DEFAULT 50000,
        risk_level VARCHAR(20) DEFAULT 'medium',
        equipment TEXT,
        location VARCHAR(100),
        soil_type VARCHAR(50),
        npk_n FLOAT,
        npk_p FLOAT,
        npk_k FLOAT,
        soil_ph FLOAT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS crop_history (
        id INT AUTO_INCREMENT PRIMARY KEY,
        farmer_id INT,
        crop VARCHAR(100),
        season VARCHAR(50),
        year INT,
        yield_kg FLOAT,
        income FLOAT,
        notes TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (farmer_id) REFERENCES farmers(id) ON DELETE CASCADE
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS recommendations (
        id INT AUTO_INCREMENT PRIMARY KEY,
        farmer_id INT,
        option_a TEXT,
        option_b TEXT,
        option_c TEXT,
        explanation TEXT,
        subsidy_info TEXT,
        pest_warnings TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (farmer_id) REFERENCES farmers(id) ON DELETE CASCADE
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS chat_sessions (
        id INT AUTO_INCREMENT PRIMARY KEY,
        farmer_id INT,
        messages TEXT,
        context TEXT,
        summary TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        FOREIGN KEY (farmer_id) REFERENCES farmers(id) ON DELETE CASCADE
    )
    """)

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

    c.commit()
    cur.close()
    c.close()


# ─── SEED DATA ──────────────────────────────────────────────────────────────
def seed_test_data():
    c = _conn()
    cur = c.cursor()

    cur.execute("SELECT id FROM farmers WHERE email=%s", ("test@farmer.com",))
    if cur.fetchone():
        return

    cur.execute("""
    INSERT INTO farmers
    (name,email,password,land_size,water_source,budget,risk_level,
     equipment,location,soil_type,npk_n,npk_p,npk_k,soil_ph)
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, (
        "Raju Patel",
        "test@farmer.com",
        _hash("test123"),
        2.5,
        "Canal",
        80000,
        "medium",
        json.dumps(["Tractor"]),
        "Maharashtra",
        "Black Soil",
        75, 35, 45, 6.8
    ))

    c.commit()
    cur.close()
    c.close()


# ─── CORE FUNCTIONS ─────────────────────────────────────────────────────────
def create_farmer(name, email, password, location):
    c = _conn()
    cur = c.cursor()

    cur.execute(
        "INSERT INTO farmers (name,email,password,location) VALUES (%s,%s,%s,%s)",
        (name, email, _hash(password), location)
    )
    fid = cur.lastrowid
    c.commit()
    
    cur.execute("SELECT * FROM farmers WHERE id=%s", (fid,))
    row = cur.fetchone()
    
    cur.close()
    c.close()
    
    if row:
        row = dict(row)
        for k, v in row.items():
            if hasattr(v, 'isoformat'):
                row[k] = v.isoformat()
    return row


def login_farmer(email, password):
    c = _conn()
    cur = c.cursor()

    cur.execute(
        "SELECT * FROM farmers WHERE email=%s AND password=%s",
        (email, _hash(password))
    )

    row = cur.fetchone()

    cur.close()
    c.close()

    if row:
        row = dict(row)
        for k, v in row.items():
            if hasattr(v, 'isoformat'):
                row[k] = v.isoformat()
    return row


def get_farmer(farmer_id):
    c = _conn()
    cur = c.cursor()

    cur.execute("SELECT * FROM farmers WHERE id=%s", (farmer_id,))
    row = cur.fetchone()

    cur.close()
    c.close()

    if row:
        row = dict(row)
        for k, v in row.items():
            if hasattr(v, 'isoformat'):
                row[k] = v.isoformat()
    return row


def save_recommendation(farmer_id, option_a, option_b, option_c,
                        explanation, subsidy_info, pest_warnings):

    c = _conn()
    cur = c.cursor()

    cur.execute("""
    INSERT INTO recommendations
    (farmer_id,option_a,option_b,option_c,explanation,subsidy_info,pest_warnings)
    VALUES (%s,%s,%s,%s,%s,%s,%s)
    """, (
        farmer_id,
        json.dumps(option_a),
        json.dumps(option_b),
        json.dumps(option_c),
        explanation,
        subsidy_info,
        pest_warnings
    ))

    c.commit()
    cur.close()
    c.close()


def get_recommendations(farmer_id, limit=5):
    c = _conn()
    cur = c.cursor()

    cur.execute("""
    SELECT * FROM recommendations
    WHERE farmer_id=%s ORDER BY created_at DESC
    LIMIT %s
    """, (farmer_id, limit))

    rows = cur.fetchall()

    cur.close()
    c.close()

    return rows


def update_farmer_profile(farmer_id, **kwargs):
    allowed = ["name", "land_size", "water_source", "budget", "risk_level",
               "equipment", "location", "soil_type", "npk_n", "npk_p", "npk_k", "soil_ph"]
    updates = {k: v for k, v in kwargs.items() if k in allowed}
    if not updates:
        return
    c = _conn()
    cur = c.cursor()
    cols = ", ".join(f"{k}=%s" for k in updates)
    cur.execute(f"UPDATE farmers SET {cols} WHERE id=%s",
                list(updates.values()) + [farmer_id])
    c.commit()
    cur.close()
    c.close()


def get_crop_history(farmer_id):
    c = _conn()
    cur = c.cursor()
    cur.execute("SELECT * FROM crop_history WHERE farmer_id=%s ORDER BY year DESC", (farmer_id,))
    rows = cur.fetchall()
    cur.close()
    c.close()
    return rows or []


def add_crop_history(farmer_id, crop, season, year, yield_kg=None, income=None, notes=""):
    c = _conn()
    cur = c.cursor()
    cur.execute("""
        INSERT INTO crop_history (farmer_id,crop,season,year,yield_kg,income,notes)
        VALUES (%s,%s,%s,%s,%s,%s,%s)
    """, (farmer_id, crop, season, year, yield_kg, income, notes))
    c.commit()
    cur.close()
    c.close()


def create_new_chat_session(farmer_id):
    c = _conn()
    cur = c.cursor()
    cur.execute("INSERT INTO chat_sessions (farmer_id, messages, context) VALUES (%s, %s, %s)", 
                (farmer_id, json.dumps([]), json.dumps({})))
    sid = cur.lastrowid
    c.commit()
    cur.execute("SELECT * FROM chat_sessions WHERE id=%s", (sid,))
    row = cur.fetchone()
    cur.close()
    c.close()

    # Ensure messages/context are dicts/lists
    if row:
        row = dict(row)
        for k, v in row.items():
            if hasattr(v, 'isoformat'):
                row[k] = v.isoformat()
        for field in ("messages", "context"):
            if isinstance(row.get(field), str):
                try:
                    row[field] = json.loads(row[field])
                except:
                    row[field] = [] if field == "messages" else {}
    return row


def get_or_create_chat_session(farmer_id):
    c = _conn()
    cur = c.cursor()
    cur.execute("""
        SELECT * FROM chat_sessions WHERE farmer_id=%s
        ORDER BY created_at DESC LIMIT 1
    """, (farmer_id,))
    row = cur.fetchone()
    if not row:
        cur.execute("INSERT INTO chat_sessions (farmer_id, messages, context) VALUES (%s, %s, %s)", 
                    (farmer_id, json.dumps([]), json.dumps({})))
        sid = cur.lastrowid
        c.commit()
        cur.execute("SELECT * FROM chat_sessions WHERE id=%s", (sid,))
        row = cur.fetchone()
    cur.close()
    c.close()

    # Ensure messages/context are dicts/lists
    row = dict(row)
    for field in ("messages", "context"):
        if isinstance(row.get(field), str):
            try:
                row[field] = json.loads(row[field])
            except:
                row[field] = [] if field == "messages" else {}
    return row


def update_chat_session(session_id, messages, context):
    c = _conn()
    cur = c.cursor()
    cur.execute("""
        UPDATE chat_sessions SET messages=%s, context=%s
        WHERE id=%s
    """, (json.dumps(messages), json.dumps(context), session_id))
    c.commit()
    cur.close()
    c.close()