# Digital Sarathi v2.0 🌾

A production-ready, AI-powered agricultural consultant built with **React**, **FastAPI**, and **LangGraph**.

## Architecture
- **Frontend**: React (Vite), TailwindCSS, Axios, Lucide Icons.
- **Backend**: FastAPI (Python), Uvicorn, Pydantic.
- **AI Agent**: LangGraph-based flow with recommendation options (A/B/C) and session summarization.
- **Database**: MySQL.

## Getting Started

### 1. Prerequisites
- Python 3.10+
- Node.js & npm
- MySQL Server

### 2. Backend Setup
1. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up your `.env` file with `DATABASE_URL` and `GROQ_API_KEY`.
4. Run migrations:
   ```bash
   python scripts/update_db.py
   ```
5. Start the server:
   ```bash
   python -m uvicorn main:app --port 8000 --reload
   ```

### 3. Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```

## Features
- **Consultant Chat**: Interactive AI advisor that provides A/B/C crop options.
- **Smart Memory**: AI summarizes consultations after every 6 messages.
- **Farm Dashboard**: Overview of farm profile and detailed crop history.
- **Modern UI**: Clean, responsive, and professional interface.
