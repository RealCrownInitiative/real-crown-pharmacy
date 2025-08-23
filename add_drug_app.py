import os
from dotenv import load_dotenv
from supabase import create_client, Client
import streamlit as st

# 🔐 Load Supabase credentials from .env
load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def run():
    st.title("🩺 Add New Drug to Inventory")

    # 🔐 Role-Based Access Control
    def require_role(allowed_roles):
        user = st.session_state.get("user")
        if not user:
            st.warning("🔐 Please log in to access this section.")
            return False
        if user["role"] not in allowed_roles:
            st.error("🚫 You do not have permission to add drugs.")
            return False
        return True

    if not require_role(["pharmacist", "admin"]):
        st.stop()

    # Drug details
    name = st.text_input("Drug Name")
    category = st.selectbox("Category", ["Pain Relief", "Antibiotic", "Antihistamine", "Diabetes", "Other"])
    description = st.text_area("Description")
    price = st.number_input("Price (UGX)", min_value=0)
    stock_quantity = st.number_input("Stock Quantity", min_value=0)
    expiry_date = st.date_input("Expiry Date (optional)")

    # Fetch suppliers from Supabase
    supplier_data = supabase.table("suppliers").select("id", "name").execute().data

    # Check if supplier data is available
    if supplier_data:
        supplier_options = {supplier["name"]: supplier["id"] for supplier in supplier_data}
        selected_supplier_name = st.selectbox("Select Supplier", list(supplier_options.keys()))
        selected_supplier_id = supplier_options.get(selected_supplier_name)
    else:
        st.warning("⚠️ No suppliers found. Please add suppliers first.")
        selected_supplier_id = None

    # Submit button
    if st.button("➕ Add Drug"):
        drug = {
            "name": name,
            "category": category,
            "description": description,
            "price": price,
            "stock_quantity": stock_quantity,
            "expiry_date": expiry_date.isoformat() if expiry_date else None,
            "supplier_id": selected_supplier_id
        }
        response = supabase.table("drugs").insert(drug).execute()
        st.success(f"✅ Drug added: {name}")
