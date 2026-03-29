import json
import streamlit as st
from db.database import get_farmer, update_farmer_profile


def render_profile():
    farmer_id = st.session_state.farmer_id
    farmer = get_farmer(farmer_id)
    st.session_state.farmer = farmer

    st.markdown("""
    <div class="main-header">
        <div>
            <div style="font-size:2rem;">👤</div>
        </div>
        <div>
            <h2 style="margin:0;color:white;">Farm Profile</h2>
            <p style="margin:0;opacity:0.8;font-size:0.9rem;">
                Complete your profile for accurate AI recommendations
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.form("profile_form"):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### 🧑 Personal Details")
            name = st.text_input("Full Name", value=farmer.get("name", ""))
            location = st.selectbox("State / Location", [
                "Maharashtra", "Punjab", "Haryana", "Uttar Pradesh",
                "Madhya Pradesh", "Rajasthan", "Gujarat", "Karnataka",
                "Tamil Nadu", "Andhra Pradesh", "Telangana", "Kerala",
                "West Bengal", "Odisha", "Bihar", "Chhattisgarh",
                "Jharkhand", "Assam", "Other"
            ], index=_get_state_idx(farmer.get("location", "Maharashtra")))

            st.markdown("#### 🌱 Farm Details")
            land_size = st.number_input(
                "Land Size (hectares)", min_value=0.1, max_value=500.0,
                value=float(farmer.get("land_size", 1.0)), step=0.1
            )
            soil_type = st.selectbox("Soil Type", [
                "Loamy", "Sandy Loam", "Clay", "Clay Loam",
                "Sandy", "Black Cotton", "Red Soil", "Alluvial"
            ], index=_get_soil_idx(farmer.get("soil_type", "Loamy")))

        with col2:
            st.markdown("#### 💧 Water & Resources")
            water_source = st.selectbox("Primary Water Source", [
                "Canal", "Borewell", "Well", "River", "Tank", "Rain-fed"
            ], index=_get_idx(["Canal", "Borewell", "Well", "River", "Tank", "Rain-fed"],
                              farmer.get("water_source", "Canal")))

            budget = st.number_input(
                "Seasonal Budget (₹)", min_value=5000, max_value=5000000,
                value=int(farmer.get("budget", 50000)), step=5000
            )
            risk_level = st.select_slider(
                "Risk Tolerance",
                options=["low", "medium", "high"],
                value=farmer.get("risk_level", "medium")
            )

            st.markdown("#### 🚜 Equipment Available")
            equipment_options = [
                "Tractor", "Power Tiller", "Drip Irrigation",
                "Sprinkler", "Harvester", "Sprayer", "None"
            ]
            current_eq = farmer.get("equipment") or "[]"
            if isinstance(current_eq, str):
                try:
                    current_eq = json.loads(current_eq)
                except Exception:
                    current_eq = []
            if not isinstance(current_eq, list):
                current_eq = []
            
            equipment = st.multiselect(
                "Equipment", equipment_options,
                default=[e for e in current_eq if e in equipment_options]
            )

        st.markdown("#### 🧪 Soil Test Results (if available)")
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            npk_n = st.number_input("Nitrogen (N) kg/ha", min_value=0, max_value=400,
                                    value=int(farmer.get("npk_n", 80)))
        with c2:
            npk_p = st.number_input("Phosphorus (P) kg/ha", min_value=0, max_value=200,
                                    value=int(farmer.get("npk_p", 40)))
        with c3:
            npk_k = st.number_input("Potassium (K) kg/ha", min_value=0, max_value=300,
                                    value=int(farmer.get("npk_k", 40)))
        with c4:
            soil_ph = st.number_input("Soil pH", min_value=3.0, max_value=10.0,
                                      value=float(farmer.get("soil_ph", 6.5)), step=0.1)

        submitted = st.form_submit_button("💾 Save Profile", use_container_width=True)

        if submitted:
            try:
                update_farmer_profile(
                    farmer_id,
                    name=name, location=location, land_size=land_size,
                    soil_type=soil_type, water_source=water_source,
                    budget=budget, risk_level=risk_level,
                    equipment=json.dumps(equipment),
                    npk_n=npk_n, npk_p=npk_p, npk_k=npk_k, soil_ph=soil_ph
                )
                st.session_state.farmer = get_farmer(farmer_id)
                st.success("✅ Profile saved successfully!")
            except Exception as e:
                st.error(f"Save failed: {e}")

    # Quick Summary Card
    st.markdown("---")
    st.markdown("#### 📊 Your Farm at a Glance")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🌾 Land", f"{farmer.get('land_size') or 1} ha")
    c2.metric("💧 Water", farmer.get("water_source") or "N/A")
    c3.metric("💰 Budget", f"₹{(farmer.get('budget') or 50000):,}")
    c4.metric("⚖️ Risk Level", (farmer.get("risk_level") or "medium").title())


def _get_state_idx(state):
    states = ["Maharashtra", "Punjab", "Haryana", "Uttar Pradesh",
              "Madhya Pradesh", "Rajasthan", "Gujarat", "Karnataka",
              "Tamil Nadu", "Andhra Pradesh", "Telangana", "Kerala",
              "West Bengal", "Odisha", "Bihar", "Chhattisgarh",
              "Jharkhand", "Assam", "Other"]
    return states.index(state) if state in states else 0


def _get_soil_idx(soil):
    soils = ["Loamy", "Sandy Loam", "Clay", "Clay Loam", "Sandy", "Black Cotton", "Red Soil", "Alluvial"]
    return soils.index(soil) if soil in soils else 0


def _get_idx(options, value):
    return options.index(value) if value in options else 0
