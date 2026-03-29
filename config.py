import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Base paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"

# ─── LLM Configuration (Groq) ────────────────────────────────────────────────
# Get a free key at https://console.groq.com
GROQ_API_KEY     = os.getenv("GROQ_API_KEY", "")
GROQ_BASE_URL    = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MIXTRAL     = "llama-3.1-8b-instant"   # primary model
GROQ_LLAMA       = "llama-3.1-8b-instant"       # fallback model

# Legacy aliases (keep so agent code calling generate_response(model="mixtral") still works)
LLM_MODEL        = "groq"
OPENAI_API_KEY   = ""   # not used
TOGETHER_API_KEY = ""   # not used

# OpenRouter kept as empty — not used anymore
OPENROUTER_API_KEY        = ""
OPENROUTER_BASE_URL       = ""
OPENROUTER_PRIMARY_MODEL  = GROQ_MIXTRAL
OPENROUTER_FALLBACK_MODEL = GROQ_LLAMA

# ─── Weather ──────────────────────────────────────────────────────────────────
OPENWEATHER_API_KEY  = os.getenv("OPENWEATHER_API_KEY", "")
OPENWEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5"

# ─── Security ─────────────────────────────────────────────────────────────────
SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-production")

# ─── Database ─────────────────────────────────────────────────────────────────
# Priority order when DATABASE_URL is set:
#   mysql://...      → MySQL  (requires pymysql)
#   postgresql://... → PostgreSQL  (requires psycopg2-binary)
#   (blank / placeholder) → SQLite  (zero config, built-in)

_raw_db_url = os.getenv("DATABASE_URL", "")

_placeholder_urls = (
    "postgresql://postgres:password@localhost:5432/digital_sarathi",
    "mysql://root:password@localhost:3306/digital_sarathi",
)

if not _raw_db_url or _raw_db_url in _placeholder_urls:
    DATABASE_URL = ""
    SQLITE_PATH  = str(BASE_DIR / "digital_sarathi.db")
    USE_SQLITE   = True
    DB_BACKEND   = "sqlite"
elif _raw_db_url.startswith("mysql"):
    DATABASE_URL = _raw_db_url
    SQLITE_PATH  = ""
    USE_SQLITE   = False
    DB_BACKEND   = "mysql"
else:
    # assume postgresql
    DATABASE_URL = _raw_db_url
    SQLITE_PATH  = ""
    USE_SQLITE   = False
    DB_BACKEND   = "postgres"

# ─── Embedding / RAG ──────────────────────────────────────────────────────────
EMBEDDING_MODEL  = "all-MiniLM-L6-v2"
FAISS_INDEX_PATH = str(BASE_DIR / "rag" / "faiss_index")
CROPS_JSON_PATH  = str(DATA_DIR / "crops.json")

# ─── India state → region map ─────────────────────────────────────────────────
STATE_REGION_MAP = {
    "Punjab": "North",          "Haryana": "North",
    "Uttar Pradesh": "North",   "Uttarakhand": "North",
    "Himachal Pradesh": "North","Jammu": "North",
    "Delhi": "North",           "Rajasthan": "West",
    "Gujarat": "West",          "Maharashtra": "West",
    "Goa": "West",              "Madhya Pradesh": "Central",
    "Chhattisgarh": "Central",  "Jharkhand": "Central",
    "Bihar": "East",            "West Bengal": "East",
    "Odisha": "East",           "Assam": "Northeast",
    "Meghalaya": "Northeast",   "Manipur": "Northeast",
    "Nagaland": "Northeast",    "Arunachal Pradesh": "Northeast",
    "Mizoram": "Northeast",     "Tripura": "Northeast",
    "Sikkim": "Northeast",      "Tamil Nadu": "South",
    "Kerala": "South",          "Karnataka": "South",
    "Andhra Pradesh": "South",  "Telangana": "South",
}

# ─── Season → month map ───────────────────────────────────────────────────────
MONTH_SEASON_MAP = {
    1:  ["Rabi", "Winter"],  2: ["Rabi", "Winter"],
    3:  ["Rabi", "Summer"],  4: ["Summer"],
    5:  ["Summer"],          6: ["Kharif", "Summer"],
    7:  ["Kharif"],          8: ["Kharif"],
    9:  ["Kharif"],         10: ["Rabi"],
    11: ["Rabi"],           12: ["Rabi", "Winter"],
}
