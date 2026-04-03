"""
Utility helpers for Digital Sarathi Streamlit app.
"""
import streamlit as st
from typing import Any


def require_login():
    """Redirect to auth page if not logged in."""
    if not st.session_state.get("authenticated"):
        st.session_state.page = "auth"
        st.rerun()


def fmt_inr(amount: float) -> str:
    """Format number as Indian Rupees with commas."""
    if amount >= 100000:
        return f"₹{amount/100000:.1f}L"
    elif amount >= 1000:
        return f"₹{amount:,.0f}"
    return f"₹{amount:.0f}"


def fmt_pct(value: float) -> str:
    """Format as percentage with sign."""
    return f"{value:+.1f}%"


def score_color(score: float) -> str:
    """Return color hex for a 0-1 score."""
    if score >= 0.75:
        return "#16a34a"
    elif score >= 0.5:
        return "#ca8a04"
    else:
        return "#dc2626"


def score_label(score: float) -> str:
    """Return text label for a 0-1 score."""
    if score >= 0.75:
        return "Excellent"
    elif score >= 0.6:
        return "Good"
    elif score >= 0.45:
        return "Fair"
    else:
        return "Poor"


def water_need_label(need: str) -> str:
    """Human-readable water need."""
    return {
        "low": "💧 Low",
        "medium": "💧💧 Medium",
        "high": "💧💧💧 High",
        "very_high": "💧💧💧💧 Very High"
    }.get(need, need.title())


def risk_badge(risk: str) -> str:
    """Return colored badge HTML for risk level."""
    colors = {
        "low": ("🟢", "#d1fae5", "#065f46"),
        "medium": ("🟡", "#fef3c7", "#92400e"),
        "high": ("🔴", "#fee2e2", "#991b1b"),
    }
    icon, bg, text = colors.get(risk, ("⚪", "#f3f4f6", "#374151"))
    return f'<span style="background:{bg};color:{text};padding:2px 10px;border-radius:20px;font-size:0.8rem;font-weight:600;">{icon} {risk.title()}</span>'
