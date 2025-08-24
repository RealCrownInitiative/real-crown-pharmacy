import streamlit as st
from auth.supabase_client import create_user  # Adjust path as needed

def run():
    st.subheader("👥 Register New User")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    role = st.selectbox("Role", ["admin", "pharmacist", "cashier", "procurement", "supervisor"])

    if st.button("Register User"):
        result = create_user(email=email, password=password, role=role)
        if result["success"]:
            st.success("✅ User registered successfully.")
        else:
            st.error(f"❌ Registration failed: {result['error']}")
