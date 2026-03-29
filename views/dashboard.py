import streamlit as st
import pandas as pd
import json
from datetime import datetime

from db.database import get_farmer, get_crop_history, save_recommendation, get_recommendations
from agents.orchestrator import run_recommendation_pipeline


def render_dashboard():
    farmer_id = st.session_state.farmer_id
    farmer = get_farmer(farmer_id)
    
    if not farmer:
        st.error("Farmer profile not found. Please log in again.")
        st.session_state.authenticated = False
        st.rerun()
        return

    st.session_state.farmer = farmer

    st.markdown(f"""
    <div class="main-header">
        <div style="font-size:2.5rem;">🌾</div>
        <div>
            <h2 style="margin:0;color:white;">
                Namaste, {farmer.get('name', 'Farmer')}! 🙏
            </h2>
            <p style="margin:0;opacity:0.8;font-size:0.9rem;">
                📍 {farmer.get('location') or ''} · {farmer.get('land_size') or 1} ha · 
                {farmer.get('water_source') or ''} water · Budget ₹{(farmer.get('budget') or 0):,}
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ─── Run Recommendations Button ───────────────────────────────────────────
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("### 🤖 AI-Powered Crop Recommendations")
    with col2:
        run_btn = st.button("🔄 Get Fresh Recommendations", use_container_width=True)

    if run_btn or st.session_state.last_recommendations is None:
        with st.spinner("🧠 Running multi-agent analysis... (Soil → Water → Market → Policy → AI)"):
            try:
                history = get_crop_history(farmer_id)
                recs = run_recommendation_pipeline(farmer, history)
                st.session_state.last_recommendations = recs

                # Save to DB
                save_recommendation(
                    farmer_id,
                    recs.get("option_a", {}),
                    recs.get("option_b", {}),
                    recs.get("option_c", {}),
                    recs.get("explanation", ""),
                    recs.get("subsidy_info", ""),
                    recs.get("pest_warnings", "")
                )
                st.success("✅ Fresh recommendations generated!")
            except Exception as e:
                st.error(f"Analysis failed: {e}")
                return

    recs = st.session_state.last_recommendations
    if not recs:
        st.info("👆 Click 'Get Fresh Recommendations' to start your personalized analysis.")
        return

    # ─── Recommendation Cards ─────────────────────────────────────────────────
    st.markdown(f"""
    <div style="background:#f0fdf4;border-radius:12px;padding:1rem;margin-bottom:1rem;border-left:4px solid #4caf50;">
        <strong>🎯 AI Analysis:</strong> {recs.get('explanation', '')}
    </div>
    """, unsafe_allow_html=True)

    colA, colB, colC = st.columns(3)

    with colA:
        _render_option_card(recs.get("option_a", {}), "A", "🛡️ Safe / Stable",
                            "#4caf50", "badge-green", "safe")

    with colB:
        _render_option_card(recs.get("option_b", {}), "B", "📈 High Reward",
                            "#f59e0b", "badge-amber", "reward")

    with colC:
        _render_option_card(recs.get("option_c", {}), "C", "🌱 Soil Health",
                            "#8b5e3c", "badge-brown", "soil")

    # ─── Conflict Warnings ────────────────────────────────────────────────────
    conflicts = recs.get("conflicts", [])
    if conflicts:
        with st.expander(f"⚠️ {len(conflicts)} Constraint(s) Detected", expanded=False):
            for c in conflicts:
                resolvable = c.get("resolvable", False)
                icon = "✅ Resolvable" if resolvable else "⛔ Hard Constraint"
                st.markdown(f"""
                **{c['crop']}** — {c['issue']}  
                Water Score: {c['water_score']} · Soil Score: {c['soil_score']} · {icon}
                """)
                if resolvable:
                    st.caption("💡 Consider drip irrigation or water-efficient practices.")

    # ─── Subsidy & Pest Info ──────────────────────────────────────────────────
    exp1, exp2 = st.columns(2)
    with exp1:
        if recs.get("subsidy_info"):
            with st.expander("💰 Subsidies & Government Schemes", expanded=False):
                st.markdown(recs["subsidy_info"][:800] + "..." if len(recs.get("subsidy_info", "")) > 800
                            else recs.get("subsidy_info", ""))

    with exp2:
        if recs.get("pest_warnings"):
            with st.expander("🐛 Pest & Disease Advisory", expanded=False):
                st.markdown(recs["pest_warnings"][:600] + "..." if len(recs.get("pest_warnings", "")) > 600
                            else recs.get("pest_warnings", ""))

    # ─── Statistics Section ───────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 📊 Farm Analytics")

    crop_history = get_crop_history(farmer_id)

    if crop_history:
        _render_statistics(crop_history, farmer)
    else:
        st.info("📝 Add crop history in the History page to see analytics.")

    # ─── Score Breakdown ──────────────────────────────────────────────────────
    _render_score_comparison(recs)


def _render_option_card(option, label, title, color, badge_class, card_class):
    if not option:
        return

    roi_pct = 0
    if option.get("investment", 0) > 0:
        roi_pct = round(((option.get("expected_income", 0) - option.get("investment", 0))
                         / option.get("investment", 1)) * 100)

    st.markdown(f"""
    <div class="option-card {card_class}">
        <span class="badge {badge_class}">Option {label}</span>
        <h3 style="margin:0.3rem 0;color:{color};">{option.get('crop', 'N/A')}</h3>
        <p style="color:#6b7280;font-size:0.85rem;margin:0 0 0.8rem;">{title}</p>
        <table style="width:100%;font-size:0.85rem;border-collapse:collapse;">
            <tr><td style="color:#6b7280;padding:2px 0;">💰 Investment</td>
                <td style="text-align:right;font-weight:600;">₹{option.get('investment', 0):,}</td></tr>
            <tr><td style="color:#6b7280;padding:2px 0;">📦 Expected Yield</td>
                <td style="text-align:right;font-weight:600;">{option.get('expected_yield', 0):,} kg</td></tr>
            <tr><td style="color:#6b7280;padding:2px 0;">💵 Market Price</td>
                <td style="text-align:right;font-weight:600;">₹{option.get('market_price', 0):,}/qtl</td></tr>
            <tr><td style="color:#6b7280;padding:2px 0;">🎯 Expected Income</td>
                <td style="text-align:right;font-weight:600;color:{color};">₹{option.get('expected_income', 0):,}</td></tr>
            <tr><td style="color:#6b7280;padding:2px 0;">📈 Est. ROI</td>
                <td style="text-align:right;font-weight:600;color:{'#16a34a' if roi_pct > 0 else '#dc2626'};">{roi_pct:+}%</td></tr>
            <tr><td style="color:#6b7280;padding:2px 0;">⏱️ Duration</td>
                <td style="text-align:right;">{option.get('duration_days', 90)} days</td></tr>
            <tr><td style="color:#6b7280;padding:2px 0;">💧 Water Need</td>
                <td style="text-align:right;">{option.get('water_need', 'medium').title()}</td></tr>
        </table>
        <div style="margin-top:0.8rem;background:#f9fafb;border-radius:6px;padding:0.4rem 0.6rem;font-size:0.8rem;">
            🎯 AI Score: <strong>{option.get('score', 0.5):.2f}</strong> &nbsp;|&nbsp;
            🌱 Sustainability: <strong>{option.get('sustainability_score', 0.5):.2f}</strong>
        </div>
    </div>
    """, unsafe_allow_html=True)


def _render_statistics(crop_history, farmer):
    df = pd.DataFrame(crop_history)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 💵 Income Over Time")
        if "year" in df.columns and "income" in df.columns:
            income_by_year = df.groupby("year")["income"].sum().reset_index()
            income_by_year.columns = ["Year", "Total Income (₹)"]
            st.bar_chart(income_by_year.set_index("Year"))

    with col2:
        st.markdown("#### 🌾 Yield History by Crop")
        if "crop" in df.columns and "yield_kg" in df.columns:
            yield_by_crop = df.groupby("crop")["yield_kg"].mean().reset_index()
            yield_by_crop.columns = ["Crop", "Avg Yield (kg)"]
            st.bar_chart(yield_by_crop.set_index("Crop"))

    col3, col4 = st.columns(2)

    with col3:
        st.markdown("#### 📉 Risk Tolerance Gauge")
        risk = farmer.get("risk_level", "medium")
        risk_val = {"low": 30, "medium": 60, "high": 90}.get(risk, 60)
        st.progress(risk_val / 100, text=f"Risk Tolerance: {risk.title()} ({risk_val}%)")
        st.caption("Higher risk tolerance enables higher-reward crop recommendations.")

    with col4:
        st.markdown("#### 🏆 Best Performing Crops")
        if "income" in df.columns and "crop" in df.columns:
            top = df.nlargest(3, "income")[["crop", "year", "income", "yield_kg"]]
            top.columns = ["Crop", "Year", "Income (₹)", "Yield (kg)"]
            st.dataframe(top, use_container_width=True, hide_index=True)


def _render_score_comparison(recs):
    st.markdown("#### 🔬 Agent Score Breakdown")

    options = {
        "Option A (Safe)": recs.get("option_a", {}),
        "Option B (High Reward)": recs.get("option_b", {}),
        "Option C (Soil Health)": recs.get("option_c", {}),
    }

    score_data = []
    for label, opt in options.items():
        if opt:
            score_data.append({
                "Option": f"{label}: {opt.get('crop', '')}",
                "Soil Score": opt.get("soil_suitability", 0.5),
                "Market Score": opt.get("market_score", 0.5),
                "Sustainability": opt.get("sustainability_score", 0.5),
                "Overall AI Score": opt.get("score", 0.5),
            })

    if score_data:
        df_scores = pd.DataFrame(score_data).set_index("Option")
        st.bar_chart(df_scores)
