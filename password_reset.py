import os
import streamlit as st
from dotenv import load_dotenv
from supabase import create_client, Client
import hashlib

# Load environment variables
load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

# Initialize Supabase client
supabase: Client = create_client(url, key)

# Hashing function
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

# Optional: Require login to reset password
def require_login():
    user = st.session_state.get("user")
    if not user:
        st.warning("🔐 Please log in to reset your password.")
        return None
    return user

# UI
st.title("🔐 Reset Password")
st.markdown("Enter your registered email and a new password below.")

email = st.text_input("📧 Email")
new_password = st.text_input("🔑 New Password", type="password")

if st.button("Reset Password"):
    if not email or not new_password:
        st.warning("⚠️ Please fill in both fields.")
    else:
        # Optional: Match email to logged-in user
        logged_in_user = st.session_state.get("user")
        if logged_in_user and logged_in_user["email"] != email:
            st.error("🚫 You can only reset your own password.")
        else:
            hashed_pw = hash_password(new_password)
            try:
                response = supabase.table("users").update({"password_hash": hashed_pw}).eq("email", email).execute()
                if response.data:
                    st.success("✅ Password updated successfully!")
                else:
                    st.error("❌ Email not found or update failed.")
            except Exception as e:
                st.error(f"❌ Failed to update password: {e}")
