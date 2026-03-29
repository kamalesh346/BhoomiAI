import streamlit as st
from db.database import create_farmer, login_farmer


def render_auth_page():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="text-align:center;padding:2rem 0 1.5rem;">
            <div style="font-size:4rem;">🌾</div>
            <h1 style="font-family:'Sora',sans-serif;color:#1a4a1a;margin:0;">Digital Sarathi</h1>
            <p style="color:#6b7280;font-size:1rem;margin-top:0.5rem;">
                Your AI-powered farming consultant
            </p>
        </div>
        """, unsafe_allow_html=True)

        tab_login, tab_signup = st.tabs(["🔑 Login", "🌱 Create Account"])

        with tab_login:
            st.markdown("#### Welcome back, Kisan!")
            email = st.text_input("Email", placeholder="you@example.com", key="login_email")
            password = st.text_input("Password", type="password", key="login_pass")

            col_btn, col_demo = st.columns(2)
            with col_btn:
                if st.button("Login →", use_container_width=True):
                    if not email or not password:
                        st.error("Please fill in all fields.")
                    else:
                        farmer = login_farmer(email.strip(), password)
                        if farmer:
                            st.session_state.authenticated = True
                            st.session_state.farmer_id = farmer["id"]
                            st.session_state.farmer = farmer
                            st.session_state.page = "dashboard"
                            st.success("Login successful!")
                            st.rerun()
                        else:
                            st.error("Invalid email or password.")

            with col_demo:
                if st.button("🧪 Demo Login", use_container_width=True):
                    farmer = login_farmer("test@farmer.com", "test123")
                    if farmer:
                        st.session_state.authenticated = True
                        st.session_state.farmer_id = farmer["id"]
                        st.session_state.farmer = farmer
                        st.session_state.page = "dashboard"
                        st.rerun()
                    else:
                        st.warning("Demo user not seeded yet. Please wait and retry.")

        with tab_signup:
            st.markdown("#### Join thousands of smart farmers!")
            name = st.text_input("Full Name", placeholder="Raju Sharma", key="reg_name")
            email_reg = st.text_input("Email", placeholder="you@example.com", key="reg_email")
            location = st.selectbox("State / Location", [
                "Maharashtra", "Punjab", "Haryana", "Uttar Pradesh",
                "Madhya Pradesh", "Rajasthan", "Gujarat", "Karnataka",
                "Tamil Nadu", "Andhra Pradesh", "Telangana", "Kerala",
                "West Bengal", "Odisha", "Bihar", "Chhattisgarh",
                "Jharkhand", "Assam", "Other"
            ], key="reg_location")
            pass1 = st.text_input("Password", type="password", key="reg_pass1")
            pass2 = st.text_input("Confirm Password", type="password", key="reg_pass2")

            if st.button("Create Account →", use_container_width=True):
                if not all([name, email_reg, pass1, pass2]):
                    st.error("All fields are required.")
                elif pass1 != pass2:
                    st.error("Passwords do not match.")
                elif len(pass1) < 6:
                    st.error("Password must be at least 6 characters.")
                else:
                    try:
                        farmer = create_farmer(name.strip(), email_reg.strip(), pass1, location)
                        st.session_state.authenticated = True
                        st.session_state.farmer_id = farmer["id"]
                        st.session_state.farmer = farmer
                        st.session_state.page = "profile"
                        st.success("Account created! Let's set up your farm profile.")
                        st.rerun()
                    except Exception as e:
                        if "unique" in str(e).lower():
                            st.error("This email is already registered. Please login.")
                        else:
                            st.error(f"Registration failed: {e}")

        st.markdown("""
        <div style="text-align:center;margin-top:2rem;padding:1rem;background:#f0fdf4;border-radius:12px;">
            <strong>🌾 Features:</strong> Multi-agent crop recommendations · AI consultant · 
            Subsidy alerts · Soil health tracking
        </div>
        """, unsafe_allow_html=True)
