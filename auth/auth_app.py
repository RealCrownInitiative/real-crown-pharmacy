import os
from dotenv import load_dotenv
from supabase import create_client, Client
import streamlit as st
import hashlib

# 🔐 Load Supabase credentials from .env
load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

# 🔑 Password hashing
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# 🚀 Main function to run this module
def run():
    auth_mode = st.sidebar.radio("Choose Action", ["Login", "Register"])

    # 🔐 Optional: Restrict registration to logged-in admins
    def require_admin():
        user = st.session_state.get("user")
        if not user or user["role"] != "admin":
            st.warning("🚫 Only admins can register new users.")
            return False
        return True

    # 📝 Registration
    if auth_mode == "Register":
        st.title("📝 User Registration")

        if not require_admin():
            st.stop()

        name = st.text_input("Full Name")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        role = st.selectbox("Role", ["pharmacist", "admin", "cashier", "procurement", "supervisor"])

        if st.button("Register"):
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
                            "role": role
                        }).execute()
                        st.success("✅ Registration successful! You can now log in.")
                    except Exception as e:
                        st.error(f"❌ Registration failed: {e}")

    # 🔐 Login
    elif auth_mode == "Login":
        st.title("🔐 User Login")

        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            if not email or not password:
                st.warning("⚠️ Please enter both email and password.")
            else:
                hashed_pw = hash_password(password)
                try:
                    user_data = supabase.table("users").select("*").eq("email", email).eq("password_hash", hashed_pw).execute().data
                    if user_data:
                        user = user_data[0]
                        st.session_state["user"] = user
                        st.success(f"✅ Welcome, {user['name']}!")

                        st.info(f"👤 Logged in as: {user['name']} ({user['role']})")

                        if user["role"] == "admin":
                            st.header("🛒 Admin Dashboard")
                            st.write("You can manage purchases, inventory, and users.")
                        else:
                            st.header("💊 Pharmacist Dashboard")
                            st.write("You can enter sales and view your performance.")

                        if st.sidebar.button("Logout"):
                            st.session_state.clear()
                            st.experimental_rerun()
                    else:
                        st.error("❌ Invalid email or password.")
                except Exception as e:
                    st.error(f"⚠️ Connection error: {e}")
