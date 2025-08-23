import os
from dotenv import load_dotenv
from supabase import create_client, Client
import streamlit as st
import pandas as pd

# 🔐 Load Supabase credentials from .env
load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

# 🔐 Role check helper
def require_role(allowed_roles):
    user = st.session_state.get("user")
    if not user:
        st.warning("🔐 Please log in to access the inventory dashboard.")
        return False
    if user["role"] not in allowed_roles:
        st.error("🚫 You do not have permission to view inventory.")
        return False
    return True

def run():
    st.title("📦 Drug Inventory Dashboard")

    # 🔐 Enforce access control
    if not require_role(["pharmacist", "admin"]):
        st.stop()

    # Fetch drugs from Supabase
    response = supabase.table("drugs").select("*").execute()
    drug_data = response.data

    if drug_data:
        df = pd.DataFrame(drug_data)
        df["expiry_date"] = pd.to_datetime(df["expiry_date"]).dt.date  # Format date
        st.dataframe(df)
    else:
        st.info("No drugs found in inventory.")
