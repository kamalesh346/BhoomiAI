import streamlit as st
import pandas as pd
import json
from datetime import datetime

from db.database import get_crop_history, add_crop_history, get_recommendations


def render_history():
    farmer_id = st.session_state.farmer_id

    st.markdown("""
    <div class="main-header">
        <div style="font-size:2.5rem;">📜</div>
        <div>
            <h2 style="margin:0;color:white;">Farm History</h2>
            <p style="margin:0;opacity:0.8;font-size:0.9rem;">
                Track your past crops, yields, and AI recommendations
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    tab_crops, tab_recs = st.tabs(["🌾 Crop History", "🤖 Past Recommendations"])

    # ─── Crop History Tab ─────────────────────────────────────────────────────
    with tab_crops:
        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown("#### 📋 Past Crop Records")
            history = get_crop_history(farmer_id)

            if history:
                df = pd.DataFrame(history)
                display_cols = ["crop", "season", "year", "yield_kg", "income", "notes"]
                df_display = df[[c for c in display_cols if c in df.columns]].copy()
                df_display.columns = [c.replace("_", " ").title() for c in df_display.columns]
                st.dataframe(df_display, use_container_width=True, hide_index=True)

                # Summary metrics
                if "income" in df.columns:
                    col_m1, col_m2, col_m3 = st.columns(3)
                    col_m1.metric("Total Seasons", len(df))
                    col_m2.metric("Total Income", f"₹{df['income'].sum():,.0f}")
                    if "yield_kg" in df.columns:
                        col_m3.metric("Total Yield", f"{df['yield_kg'].sum():,.0f} kg")
            else:
                st.info("No crop history recorded yet. Add your first record below!")

        with col2:
            st.markdown("#### ➕ Add New Record")
            with st.form("add_history"):
                crop_name = st.text_input("Crop Name", placeholder="e.g. Wheat")
                season = st.selectbox("Season", ["Kharif", "Rabi", "Summer", "Annual"])
                year = st.number_input("Year", min_value=2000, max_value=2030,
                                       value=datetime.now().year)
                yield_kg = st.number_input("Yield (kg)", min_value=0.0, step=50.0)
                income = st.number_input("Income (₹)", min_value=0.0, step=1000.0)
                notes = st.text_area("Notes", placeholder="Any observations...", height=80)

                if st.form_submit_button("Add Record", use_container_width=True):
                    if crop_name:
                        add_crop_history(farmer_id, crop_name, season, year,
                                         yield_kg or None, income or None, notes)
                        st.success("✅ Record added!")
                        st.rerun()
                    else:
                        st.error("Please enter a crop name.")

    # ─── Past Recommendations Tab ─────────────────────────────────────────────
    with tab_recs:
        st.markdown("#### 🤖 AI Recommendation History")
        past_recs = get_recommendations(farmer_id, limit=10)

        if not past_recs:
            st.info("No recommendations generated yet. Go to Dashboard to get your first AI crop recommendation!")
        else:
            for i, rec in enumerate(past_recs):
                ts = rec.get("created_at", "")
                if hasattr(ts, "strftime"):
                    ts_str = ts.strftime("%d %B %Y, %I:%M %p")
                else:
                    ts_str = str(ts)[:16]

                with st.expander(f"📅 Recommendation #{len(past_recs) - i} — {ts_str}", expanded=(i == 0)):
                    col_a, col_b, col_c = st.columns(3)

                    def parse_option(opt):
                        if isinstance(opt, str):
                            try:
                                return json.loads(opt)
                            except Exception:
                                return {}
                        return opt or {}

                    opt_a = parse_option(rec.get("option_a"))
                    opt_b = parse_option(rec.get("option_b"))
                    opt_c = parse_option(rec.get("option_c"))

                    with col_a:
                        st.markdown(f"""
                        **🛡️ Safe Option**  
                        Crop: **{opt_a.get('crop') or 'N/A'}**  
                        Income: ₹{(opt_a.get('expected_income') or 0):,}
                        """)

                    with col_b:
                        st.markdown(f"""
                        **📈 High Reward**  
                        Crop: **{opt_b.get('crop') or 'N/A'}**  
                        Income: ₹{(opt_b.get('expected_income') or 0):,}
                        """)

                    with col_c:
                        st.markdown(f"""
                        **🌱 Soil Health**  
                        Crop: **{opt_c.get('crop') or 'N/A'}**  
                        Income: ₹{(opt_c.get('expected_income') or 0):,}
                        """)

                    if rec.get("explanation"):
                        st.markdown(f"**💡 Analysis:** {rec['explanation']}")
