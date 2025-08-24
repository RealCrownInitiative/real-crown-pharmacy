import os
from dotenv import load_dotenv
from supabase import create_client, Client
import streamlit as st
from datetime import datetime

# 🔐 Load environment variables and initialize Supabase
load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

# 🔐 Role check helper
def require_role(allowed_roles):
    user = st.session_state.get("user")
    if not user:
        st.warning("🔒 Please log in to record a sale.")
        return None
    if user.get("role") not in allowed_roles:
        st.error("🚫 You do not have permission to record sales.")
        return None
    return user

def run():
    st.title("💰 Record Drug Sale")

    # 🔒 Enforce access control
    user = require_role(["cashier", "pharmacist", "admin"])
    if not user:
        st.stop()

    user_id = user.get("id")

    # 📦 Fetch available drugs
    drug_data = supabase.table("drugs").select("id", "name", "price", "stock_quantity").execute().data
    if not drug_data:
        st.warning("⚠️ No drugs available. Please add drugs first.")
        st.stop()

    # 🧪 Drug selection
    drug_options = {drug["name"]: drug for drug in drug_data}
    selected_drug_name = st.selectbox("🧪 Select Drug", list(drug_options.keys()))
    selected_drug = drug_options[selected_drug_name]

    # 📊 Quantity input
    quantity_sold = st.number_input("📦 Quantity Sold", min_value=1, max_value=selected_drug["stock_quantity"])
    total_price = quantity_sold * selected_drug["price"]
    st.write(f"💵 Total Price: UGX {total_price:,}")

    # ✅ Confirm sale
    if st.button("🧾 Record Sale"):
        try:
            # 🧾 Insert into sales table
            sale = {
                "drug_id": selected_drug["id"],
                "quantity_sold": quantity_sold,
                "total_price": total_price,
                "sold_by": user_id,
                "date_sold": datetime.now().isoformat()
            }
            supabase.table("sales").insert(sale).execute()

            # 📉 Update stock
            new_stock = selected_drug["stock_quantity"] - quantity_sold
            supabase.table("drugs").update({"stock_quantity": new_stock}).eq("id", selected_drug["id"]).execute()

            st.success(f"✅ Sale recorded successfully. Stock updated to {new_stock} units.")
        except Exception as e:
            st.error("❌ Failed to record sale.")
            st.exception(e)
