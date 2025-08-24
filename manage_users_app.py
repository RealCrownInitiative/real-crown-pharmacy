import streamlit as st
from auth.supabase_client import supabase, hash_password  # Ensure hash_password is exposed
from datetime import datetime

def require_admin():
    user = st.session_state.get("user")
    return user and user.get("role") == "admin"

def run():
    st.subheader("👥 Register New User")

    if not require_admin():
        st.error("🔐 Only admins can register new users.")
        st.stop()

    name = st.text_input("Full Name").strip().title()
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    role = st.selectbox("Role", ["admin", "pharmacist", "cashier", "procurement", "supervisor"])

    if st.button("Register User"):
        if not name or not email or not password:
            st.warning("⚠️ Please fill in all fields.")
        else:
            hashed_pw = hash_password(password)

            existing = supabase.table("users").select("id").eq("email", email).execute().data
            if existing:
                st.error("❌ Email already registered.")
            else:
                try:
                    supabase.table("users").insert({
                        "name": name,
                        "email": email,
                        "password_hash": hashed_pw,
                        "role": role,
                        "verified": False
                    }).execute()

                    # 📝 Audit log
                    supabase.table("audit_logs").insert({
                        "action": "register_user",
                        "performed_by": st.session_state["user"]["email"],
                        "details": f"Registered {email} as {role}",
                        "timestamp": datetime.utcnow().isoformat()
                    }).execute()

                    st.success("✅ Registration successful.")
                except Exception as e:
                    st.error("❌ Registration failed. Please try again or contact support.")
