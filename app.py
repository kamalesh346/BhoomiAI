"""
Digital Sarathi v1.0 — Main Streamlit Entry Point
"""
import streamlit as st
from pathlib import Path
import sys
import logging
import warnings
import os

# Suppress the transformers/sentence-transformers/torch warnings
os.environ["TRANSFORMERS_VERBOSITY"] = "error"
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)
logging.getLogger("transformers").setLevel(logging.ERROR)
logging.getLogger("sentence_transformers").setLevel(logging.ERROR)

# Ensure module path
sys.path.insert(0, str(Path(__file__).parent))

# Page config — must be first Streamlit call
st.set_page_config(
    page_title="Digital Sarathi | Smart Farming Assistant",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize DB on startup
try:
    from db.database import init_db, seed_test_data
    init_db()
    seed_test_data()
except Exception as e:
    st.warning(f"Database setup issue: {e}. Some features may be limited.")

# ─── Global CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;600;700&family=Space+Grotesk:wght@400;500;600&display=swap');

:root {
    --green-dark: #1a4a1a;
    --green-mid: #2d7a2d;
    --green-light: #4caf50;
    --amber: #f59e0b;
    --amber-light: #fef3c7;
    --earth: #8b5e3c;
    --cream: #fafaf5;
    --text-dark: #1a1a1a;
    --text-muted: #6b7280;
    --card-bg: #ffffff;
    --border: #e5e7eb;
}

html, body, [class*="css"] {
    font-family: 'Space Grotesk', sans-serif;
    background: var(--cream);
}

h1, h2, h3 {
    font-family: 'Sora', sans-serif;
    font-weight: 700;
}

.main-header {
    background: linear-gradient(135deg, #1a4a1a 0%, #2d7a2d 60%, #4caf50 100%);
    padding: 2rem 2rem 1.5rem;
    border-radius: 16px;
    margin-bottom: 1.5rem;
    color: white;
    display: flex;
    align-items: center;
    gap: 1rem;
}

.stMetric {
    background: white;
    border-radius: 12px;
    padding: 1rem;
    border: 1px solid var(--border);
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}

.stButton > button {
    background: linear-gradient(135deg, #2d7a2d, #4caf50);
    color: white;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    font-family: 'Sora', sans-serif;
    transition: all 0.2s;
}

.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(45, 122, 45, 0.4);
}

.option-card {
    background: white;
    border-radius: 16px;
    padding: 1.5rem;
    border-left: 5px solid #4caf50;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    margin-bottom: 1rem;
}

.option-card.reward { border-left-color: #f59e0b; }
.option-card.soil { border-left-color: #8b5e3c; }

.badge {
    display: inline-block;
    padding: 0.2rem 0.8rem;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    margin-bottom: 0.5rem;
}
.badge-green { background: #d1fae5; color: #065f46; }
.badge-amber { background: #fef3c7; color: #92400e; }
.badge-brown { background: #fde8d8; color: #7c3d12; }

.sidebar-logo {
    text-align: center;
    padding: 1rem 0;
    border-bottom: 1px solid rgba(255,255,255,0.2);
    margin-bottom: 1rem;
}

.chat-bubble-user {
    background: #e8f5e9;
    border-radius: 12px 12px 2px 12px;
    padding: 0.75rem 1rem;
    margin: 0.5rem 0;
    margin-left: 15%;
    color: #1a4a1a;
    font-size: 0.9rem;
}

.chat-bubble-bot {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 12px 12px 12px 2px;
    padding: 0.75rem 1rem;
    margin: 0.5rem 0;
    margin-right: 15%;
    color: #1a1a1a;
    font-size: 0.9rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}
</style>
""", unsafe_allow_html=True)


# ─── Session Defaults ────────────────────────────────────────────────────────
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "farmer_id" not in st.session_state:
    st.session_state.farmer_id = None
if "farmer" not in st.session_state:
    st.session_state.farmer = None
if "page" not in st.session_state:
    st.session_state.page = "auth"
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []
if "last_recommendations" not in st.session_state:
    st.session_state.last_recommendations = None


# ─── Navigation ──────────────────────────────────────────────────────────────
def navigate(page: str):
    st.session_state.last_nav_page = st.session_state.get("page", "auth")
    st.session_state.page = page
    st.rerun()


def logout():
    for key in ["authenticated", "farmer_id", "farmer", "chat_messages",
                "last_recommendations", "chat_session_id", "chat_initialized", "last_nav_page"]:
        if key in st.session_state:
            del st.session_state[key]
    st.session_state.page = "auth"
    st.rerun()


# ─── Sidebar ─────────────────────────────────────────────────────────────────
if st.session_state.authenticated and st.session_state.farmer:
    farmer = st.session_state.farmer
    with st.sidebar:
        st.markdown(f"""
        <div class="sidebar-logo">
            <div style="font-size:2.5rem;">🌾</div>
            <div style="font-family:'Sora',sans-serif;font-weight:700;font-size:1.2rem;color:#1a4a1a;">
                Digital Sarathi
            </div>
            <div style="font-size:0.8rem;color:#6b7280;">v1.0</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"**👨‍🌾 {farmer['name']}**")
        st.markdown(f"📍 {farmer.get('location', 'N/A')} · {farmer.get('land_size', 1)} ha")
        st.markdown("---")

        pages = {
            "🏠 Dashboard": "dashboard",
            "💬 Consultant Chat": "chat",
            "👤 My Profile": "profile",
            "📜 History": "history",
        }
        for label, pg in pages.items():
            if st.button(label, use_container_width=True, key=f"nav_{pg}"):
                navigate(pg)

        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            logout()
else:
    with st.sidebar:
        st.markdown("""
        <div style="text-align:center;padding:2rem 0;">
            <div style="font-size:3rem;">🌾</div>
            <div style="font-family:'Sora',sans-serif;font-weight:700;font-size:1.3rem;color:#1a4a1a;">
                Digital Sarathi
            </div>
            <div style="color:#6b7280;font-size:0.85rem;margin-top:0.5rem;">
                Your Smart Farming Assistant
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.info("🌱 Login or create account to get personalized crop recommendations powered by AI.")


# ─── Page Router ─────────────────────────────────────────────────────────────
page = st.session_state.get("page", "auth")

if not st.session_state.authenticated:
    from views.auth import render_auth_page
    render_auth_page()
elif page == "dashboard":
    from views.dashboard import render_dashboard
    render_dashboard()
elif page == "chat":
    from views.chat import render_chat
    render_chat()
elif page == "profile":
    from views.profile import render_profile
    render_profile()
elif page == "history":
    from views.history import render_history
    render_history()
else:
    from views.dashboard import render_dashboard
    render_dashboard()
