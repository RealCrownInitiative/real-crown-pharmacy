import os
import streamlit as st
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

# Initialize Supabase client
supabase: Client = create_client(url, key)

# 🔐 Login check helper
def require_login():
    user = st.session_state.get("user")
    if not user:
        st.warning("⚠️ No user session found. Please log in first.")
        return None
    return user

# UI
st.title("👤 Edit Profile")
st.markdown("Update your name and email below. Changes will reflect immediately.")

# Retrieve user from session
user = require_login()
if not user:
    st.stop()

new_name = st.text_input("📝 Name", value=user.get("name", ""))
new_email = st.text_input("📧 Email", value=user.get("email", ""))

if st.button("Update Profile"):
    if not new_name or not new_email:
        st.error("❌ Both fields are required.")
    else:
        try:
            response = supabase.table("users").update({
                "name": new_name,
                "email": new_email
            }).eq("id", user["id"]).execute()

            if response.data:
                st.success("✅ Profile updated successfully!")
                # Update session state
                st.session_state["user"]["name"] = new_name
                st.session_state["user"]["email"] = new_email
            else:
                st.error("❌ Update failed. Please check your inputs.")
        except Exception as e:
            st.error(f"❌ Error: {e}")
