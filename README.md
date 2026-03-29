# 🌾 Digital Sarathi v1.0

> **Your AI-powered farming consultant** — Multi-agent crop recommendations, RAG-based policy insights, and interactive advisory chat for Indian farmers.

---

## 🎯 Features

| Feature | Description |
|---|---|
| 🤖 Multi-Agent AI | LangGraph pipeline with 8 specialized agents (Soil, Water, Market, Policy, etc.) |
| 🌾 Crop Recommendations | 3 personalized options: Safe, High Reward, Soil Health |
| 💬 Consultant Chat | Interactive Q&A with context-aware follow-up questions |
| 📚 RAG System | FAISS + all-MiniLM-L6-v2 for government scheme retrieval |
| ⚖️ Conflict Resolution | Dynamic LLM-based reasoning (not hardcoded rules) |
| 🔐 Authentication | Signup/Login with hashed passwords |
| 📊 Analytics Dashboard | Income charts, yield history, risk visualization |
| 🗄️ Database | PostgreSQL (auto-falls back to in-memory mock) |

---

## 🏗️ Architecture

```
Input (Farmer Profile)
    │
    ▼
┌─────────────────────────────────────────────┐
│           LangGraph Workflow                │
│                                             │
│  Farmer Profile Agent                       │
│       │                                     │
│       ▼                                     │
│  Crop Knowledge Agent  (filter ~80 crops)   │
│       │                                     │
│       ▼                                     │
│  ┌────────────────────────────────────┐     │
│  │     Parallel Agent Scoring         │     │
│  │  Soil · Water/Climate · Market     │     │
│  │  Policy/RAG · Sustainability       │     │
│  │  Pest Advisory                     │     │
│  └────────────────────────────────────┘     │
│       │                                     │
│       ▼                                     │
│  Conflict Resolution Engine (LLM-driven)    │
│       │                                     │
│       ▼                                     │
│  Recommendation Generator                   │
│  → Option A (Safe) · B (Reward) · C (Soil) │
└─────────────────────────────────────────────┘
```

---

## 📁 Folder Structure

```
digital_sarathi/
├── app.py                    # Main Streamlit entry point
├── config.py                 # All configuration & constants
├── requirements.txt
├── .env.example
├── .streamlit/
│   └── config.toml           # Streamlit theme
│
├── agents/
│   ├── orchestrator.py       # LangGraph workflow + all 8 agents
│   └── consultant.py         # Consultant chat agent
│
├── rag/
│   ├── retriever.py          # FAISS RAG system
│   └── faiss_index/          # Auto-created on first run
│
├── db/
│   ├── database.py           # PostgreSQL + mock fallback
│   └── mock_database.py      # In-memory mock (no DB needed)
│
├── utils/
│   ├── llm.py                # LLM abstraction (Groq/OpenAI/Mock)
│   └── helpers.py            # Formatting utilities
│
├── pages/
│   ├── auth.py               # Login / Signup page
│   ├── dashboard.py          # Main recommendations + charts
│   ├── chat.py               # Consultant chat UI
│   ├── profile.py            # Farmer profile setup
│   └── history.py            # Crop & recommendation history
│
├── data/
│   ├── crops.json            # ~80 Indian crops dataset
│   ├── doc_pmfby.txt         # PMFBY insurance scheme
│   ├── doc_pmkisan.txt       # PM-KISAN & KCC schemes
│   ├── doc_msp_organic.txt   # MSP, PKVY organic scheme
│   ├── doc_pest_advisory.txt # IPM pest management
│   └── doc_water_sustainability.txt
│
└── scripts/
    ├── init_db.py            # DB setup script
    └── build_rag.py          # FAISS index builder
```

---

## ⚡ Quick Start

### Option 1: Demo Mode (No DB, No API Keys)

Runs completely offline with mock data and rule-based AI responses.

```bash
# 1. Clone / extract project
cd digital_sarathi

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install streamlit langchain langchain-community langgraph \
            sentence-transformers faiss-cpu pandas numpy \
            python-dotenv requests

# 4. Run the app
streamlit run app.py
```

Login with: `test@farmer.com` / `test123`

---

### Option 2: Full Setup (PostgreSQL + Groq LLM)

```bash
# 1. Install all requirements
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Edit .env with your values:
#   DATABASE_URL=postgresql://user:pass@localhost:5432/digital_sarathi
#   GROQ_API_KEY=your_key_here         # Free at console.groq.com
#   OPENWEATHER_API_KEY=your_key_here  # Free at openweathermap.org

# 3. Create PostgreSQL database
createdb digital_sarathi
# OR: psql -c "CREATE DATABASE digital_sarathi;"

# 4. Initialize DB + seed test data
python scripts/init_db.py

# 5. Build RAG vector index (downloads ~90MB model once)
python scripts/build_rag.py

# 6. Run the app
streamlit run app.py
```

---

## 🔑 API Keys

| Key | Where to Get | Required? |
|---|---|---|
| `GROQ_API_KEY` | [console.groq.com](https://console.groq.com) (free) | For real LLM responses |
| `OPENWEATHER_API_KEY` | [openweathermap.org](https://openweathermap.org/api) (free) | For live weather |
| `DATABASE_URL` | Your PostgreSQL instance | For persistent data |

**Without API keys:** The app works in demo mode with rule-based responses and mock weather data.

---

## 🤖 Agents Overview

| Agent | Input | Output |
|---|---|---|
| Farmer Profile | DB profile | Enriched profile (region, season, water score) |
| Crop Knowledge | Season, region | ~30 filtered candidate crops |
| Soil Agent | NPK, pH | Suitability score per crop (0–1) |
| Water/Climate | Water source + OpenWeather | Feasibility score with live weather |
| Market Intelligence | Crop category, price | Market demand score |
| Policy/RAG | Crop list, location | Relevant subsidy/scheme text |
| Sustainability | Crop history | Rotation score (penalizes repetition) |
| Pest Advisory | Crops, season | Non-blocking pest warnings |
| Conflict Resolution | All scores | Weighted composite, conflict detection |
| Recommendation | Composite scores | Option A / B / C with explanation |

---

## 💬 Consultant Chat

The chat page offers an interactive advisory session:

- **Dynamic questioning** — asks follow-up questions based on context
- **RAG-enhanced** — answers about subsidies/schemes pull from policy docs
- **Context-aware** — remembers farmer profile and conversation history
- **Quick suggestions** — preset buttons for common questions

---

## 📊 Dashboard Statistics

- Income over time (bar chart)
- Yield by crop (bar chart)
- Risk tolerance gauge
- Top performing crops table
- Agent score comparison (per recommendation)
- Conflict warnings with resolution advice

---

## 🧪 Test Account

| Field | Value |
|---|---|
| Email | test@farmer.com |
| Password | test123 |
| Profile | 2.5 ha, Maharashtra, Canal water, Black Cotton soil |
| History | 5 seasons pre-seeded (Cotton, Wheat, Soybean, Chickpea, Jowar) |

---

## 🔧 Customization

**Add more crops:** Edit `data/crops.json` following the existing schema.

**Add more policy docs:** Add `data/doc_*.txt` files, then run `python scripts/build_rag.py`.

**Change LLM model:** Set `LLM_MODEL=llama` in `.env` to use LLaMA 3 via Groq.

**Adjust agent weights:** Edit the `weights` dict in `agents/orchestrator.py` → `conflict_resolution_engine()`.

---

## 🐛 Troubleshooting

**Database connection error** → App automatically uses in-memory mock. No action needed for demo.

**Embedding model download slow** → First run downloads `all-MiniLM-L6-v2` (~90MB). Subsequent runs use cache.

**LLM responses are generic** → Add `GROQ_API_KEY` to `.env` for real Mixtral/LLaMA responses.

**Port already in use** → Run with `streamlit run app.py --server.port 8502`

---

## 📜 License

MIT License — Free to use, modify, and distribute.

---

*Built with ❤️ for Indian farmers | Digital Sarathi v1.0*
