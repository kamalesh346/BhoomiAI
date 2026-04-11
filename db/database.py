"""
MySQL Database Layer for BhoomiAI
"""

import hashlib
import json
import os
from urllib.parse import parse_qs, unquote, urlparse

from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "").strip()


def _parse_mysql_url(url: str) -> dict:
    """
    Parse mysql://user:password@host:port/dbname into pymysql.connect kwargs.
    Supports cloud-hosted URLs with query parameters like ssl-mode=REQUIRED.
    """
    normalized_url = url.strip()
    if not normalized_url:
        raise ValueError("DATABASE_URL is empty")

    parsed = urlparse(normalized_url)
    if parsed.scheme not in {"mysql", "mysql+pymysql"}:
        raise ValueError(f"Unsupported database scheme: {parsed.scheme}")

    if not parsed.hostname:
        raise ValueError("Invalid MySQL URL: missing host")

    database = parsed.path.lstrip("/")
    if not database:
        raise ValueError("Invalid MySQL URL: missing database name")

    params = dict(
        host=parsed.hostname,
        port=parsed.port or 3306,
        user=unquote(parsed.username or ""),
        password=unquote(parsed.password or ""),
        database=database,
        charset="utf8mb4",
        cursorclass=__import__("pymysql").cursors.DictCursor,
    )

    query = parse_qs(parsed.query, keep_blank_values=True)
    ssl_mode = (query.get("ssl-mode", [""])[0] or query.get("ssl_mode", [""])[0]).upper()
    if ssl_mode in {"REQUIRED", "VERIFY_CA", "VERIFY_IDENTITY"}:
        params["ssl"] = {}

    connect_timeout = query.get("connect_timeout", [""])[0]
    if connect_timeout:
        params["connect_timeout"] = int(connect_timeout)

    read_timeout = query.get("read_timeout", [""])[0]
    if read_timeout:
        params["read_timeout"] = int(read_timeout)

    write_timeout = query.get("write_timeout", [""])[0]
    if write_timeout:
        params["write_timeout"] = int(write_timeout)

    return params


import pymysql
import pymysql.cursors


def _conn():
    return pymysql.connect(**_parse_mysql_url(DATABASE_URL))


def _hash(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()


def _serialize_farmer_row(row):
    if not row:
        return row

    row = dict(row)
    row.pop("password", None)

    for k, v in row.items():
        if hasattr(v, "isoformat"):
            row[k] = v.isoformat()

    return row


def init_db():
    c = _conn()
    cur = c.cursor()

    cur.execute(
        """
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
        soil_type_distribution TEXT,
        npk_n FLOAT,
        npk_p FLOAT,
        npk_k FLOAT,
        soil_ph FLOAT,
        language_preference VARCHAR(10) DEFAULT 'en',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """
    )

    cur.execute(
        """
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
    """
    )

    cur.execute(
        """
    CREATE TABLE IF NOT EXISTS pest_history (
        id INT AUTO_INCREMENT PRIMARY KEY,
        farmer_id INT,
        pest_name VARCHAR(100) NOT NULL,
        affected_crop VARCHAR(100),
        severity VARCHAR(20),
        observation_date DATE NOT NULL,
        description TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (farmer_id) REFERENCES farmers(id) ON DELETE CASCADE
    )
    """
    )

    cur.execute(
        """
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
    """
    )

    cur.execute(
        """
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
    """
    )

    cur.execute(
        """
    CREATE TABLE IF NOT EXISTS chat_choices (
        id INT AUTO_INCREMENT PRIMARY KEY,
        chat_session_id INT,
        message_id VARCHAR(100),
        selected_option VARCHAR(10),
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (chat_session_id) REFERENCES chat_sessions(id) ON DELETE CASCADE
    )
    """
    )

    c.commit()
    cur.close()
    c.close()


def seed_test_data():
    c = _conn()
    cur = c.cursor()

    cur.execute("SELECT id FROM farmers WHERE email=%s", ("test@farmer.com",))
    if cur.fetchone():
        cur.close()
        c.close()
        return

    cur.execute(
        """
    INSERT INTO farmers
    (name,email,password,land_size,water_source,budget,risk_level,
     equipment,location,soil_type,npk_n,npk_p,npk_k,soil_ph)
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """,
        (
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
            75,
            35,
            45,
            6.8,
        ),
    )

    c.commit()
    cur.close()
    c.close()


def create_farmer(name, email, password, location, land_size=1.0):
    c = _conn()
    cur = c.cursor()

    cur.execute("SELECT id FROM farmers WHERE email=%s", (email,))
    if cur.fetchone():
        cur.close()
        c.close()
        raise ValueError("Email already exists")

    cur.execute(
        "INSERT INTO farmers (name,email,password,location,land_size) VALUES (%s,%s,%s,%s,%s)",
        (name.strip(), email.strip(), _hash(password), location.strip(), land_size),
    )
    fid = cur.lastrowid
    c.commit()

    cur.execute("SELECT * FROM farmers WHERE id=%s", (fid,))
    row = cur.fetchone()

    cur.close()
    c.close()

    return _serialize_farmer_row(row)


def login_farmer(email, password):
    c = _conn()
    cur = c.cursor()

    cur.execute(
        "SELECT * FROM farmers WHERE email=%s AND password=%s",
        (email, _hash(password)),
    )

    row = cur.fetchone()

    cur.close()
    c.close()

    return _serialize_farmer_row(row)


def get_farmer(farmer_id):
    c = _conn()
    cur = c.cursor()

    cur.execute("SELECT * FROM farmers WHERE id=%s", (farmer_id,))
    row = cur.fetchone()

    cur.close()
    c.close()

    if row:
        row = _serialize_farmer_row(row)
        for field in ("equipment", "soil_type_distribution"):
            if field in row and isinstance(row[field], str):
                try:
                    row[field] = json.loads(row[field])
                except Exception:
                    row[field] = [] if field == "equipment" else [{"type": "", "size": 0}]

    return row


def save_recommendation(
    farmer_id, option_a, option_b, option_c, explanation, subsidy_info, pest_warnings
):
    c = _conn()
    cur = c.cursor()

    cur.execute(
        """
    INSERT INTO recommendations
    (farmer_id,option_a,option_b,option_c,explanation,subsidy_info,pest_warnings)
    VALUES (%s,%s,%s,%s,%s,%s,%s)
    """,
        (
            farmer_id,
            json.dumps(option_a),
            json.dumps(option_b),
            json.dumps(option_c),
            explanation,
            subsidy_info,
            pest_warnings,
        ),
    )

    c.commit()
    cur.close()
    c.close()


def get_recommendations(farmer_id, limit=5):
    c = _conn()
    cur = c.cursor()

    cur.execute(
        """
    SELECT * FROM recommendations
    WHERE farmer_id=%s ORDER BY created_at DESC
    LIMIT %s
    """,
        (farmer_id, limit),
    )

    rows = cur.fetchall()

    cur.close()
    c.close()

    return rows


def update_farmer_profile(farmer_id, **kwargs):
    allowed = [
        "name",
        "land_size",
        "water_source",
        "budget",
        "risk_level",
        "equipment",
        "location",
        "soil_type",
        "soil_type_distribution",
        "recent_pest_activity",
        "npk_n",
        "npk_p",
        "npk_k",
        "soil_ph",
        "language_preference",
    ]
    updates = {k: v for k, v in kwargs.items() if k in allowed}
    if not updates:
        return

    if "equipment" in updates and not isinstance(updates["equipment"], str):
        updates["equipment"] = json.dumps(updates["equipment"])
    if "soil_type_distribution" in updates and not isinstance(
        updates["soil_type_distribution"], str
    ):
        updates["soil_type_distribution"] = json.dumps(updates["soil_type_distribution"])

    c = _conn()
    cur = c.cursor()

    items = list(updates.items())
    cols = ", ".join(f"{k}=%s" for k, v in items)
    vals = [v for k, v in items]

    cur.execute(f"UPDATE farmers SET {cols} WHERE id=%s", vals + [farmer_id])
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


def get_pest_history(farmer_id):
    c = _conn()
    cur = c.cursor()
    cur.execute(
        "SELECT * FROM pest_history WHERE farmer_id=%s ORDER BY observation_date DESC",
        (farmer_id,),
    )
    rows = cur.fetchall()
    cur.close()
    c.close()
    if rows:
        for row in rows:
            for k, v in row.items():
                if hasattr(v, "isoformat"):
                    row[k] = v.isoformat()
    return rows or []


def add_pest_history(
    farmer_id, pest_name, affected_crop, severity, observation_date, description=""
):
    c = _conn()
    cur = c.cursor()
    cur.execute(
        """
        INSERT INTO pest_history (farmer_id, pest_name, affected_crop, severity, observation_date, description)
        VALUES (%s,%s,%s,%s,%s,%s)
    """,
        (farmer_id, pest_name, affected_crop, severity, observation_date, description),
    )
    c.commit()
    cur.close()
    c.close()


def add_crop_history(farmer_id, crop, season, year, yield_kg=None, income=None, notes=""):
    c = _conn()
    cur = c.cursor()
    cur.execute(
        """
        INSERT INTO crop_history (farmer_id,crop,season,year,yield_kg,income,notes)
        VALUES (%s,%s,%s,%s,%s,%s,%s)
    """,
        (farmer_id, crop, season, year, yield_kg, income, notes),
    )
    c.commit()
    cur.close()
    c.close()


def create_new_chat_session(farmer_id):
    c = _conn()
    cur = c.cursor()
    cur.execute(
        "INSERT INTO chat_sessions (farmer_id, messages, context) VALUES (%s, %s, %s)",
        (farmer_id, json.dumps([]), json.dumps({})),
    )
    sid = cur.lastrowid
    c.commit()
    cur.execute("SELECT * FROM chat_sessions WHERE id=%s", (sid,))
    row = cur.fetchone()
    cur.close()
    c.close()

    if row:
        row = dict(row)
        for k, v in row.items():
            if hasattr(v, "isoformat"):
                row[k] = v.isoformat()
        for field in ("messages", "context"):
            if isinstance(row.get(field), str):
                try:
                    row[field] = json.loads(row[field])
                except Exception:
                    row[field] = [] if field == "messages" else {}
    return row


def get_or_create_chat_session(farmer_id):
    c = _conn()
    cur = c.cursor()
    cur.execute(
        """
        SELECT * FROM chat_sessions WHERE farmer_id=%s
        ORDER BY created_at DESC LIMIT 1
    """,
        (farmer_id,),
    )
    row = cur.fetchone()
    if not row:
        cur.execute(
            "INSERT INTO chat_sessions (farmer_id, messages, context) VALUES (%s, %s, %s)",
            (farmer_id, json.dumps([]), json.dumps({})),
        )
        sid = cur.lastrowid
        c.commit()
        cur.execute("SELECT * FROM chat_sessions WHERE id=%s", (sid,))
        row = cur.fetchone()
    cur.close()
    c.close()

    row = dict(row)
    for field in ("messages", "context"):
        if isinstance(row.get(field), str):
            try:
                row[field] = json.loads(row[field])
            except Exception:
                row[field] = [] if field == "messages" else {}
    return row


def update_chat_session(session_id, messages, context):
    c = _conn()
    cur = c.cursor()
    cur.execute(
        """
        UPDATE chat_sessions SET messages=%s, context=%s
        WHERE id=%s
    """,
        (json.dumps(messages), json.dumps(context), session_id),
    )
    c.commit()
    cur.close()
    c.close()
