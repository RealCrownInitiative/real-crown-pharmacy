import streamlit as st
from auth.supabase_client import create_user  # Ensure this function accepts name, email, password, role

def run():
    st.subheader("👥 Register New User")

    name = st.text_input("Full Name").strip().title()
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    role = st.selectbox("Role", ["admin", "pharmacist", "cashier", "procurement", "supervisor"])

    if st.button("Register User"):
        if not name or not email or not password:
            st.warning("⚠️ Please fill in all fields.")
        else:
            result = create_user(name=name, email=email, password=password, role=role)
            if result.get("success"):
                st.success("✅ User registered successfully.")
            else:
                st.error(f"❌ Registration failed: {result.get('error', 'Unknown error')}")
