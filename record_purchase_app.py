import os
from dotenv import load_dotenv
from supabase import create_client, Client
import streamlit as st
from datetime import datetime, date

# 🌍 Load environment variables
load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

# 🔐 Role check helper
def require_role(allowed_roles):
    user = st.session_state.get("user")
    if not user:
        st.warning("🔐 Please log in to record a purchase.")
        return None
    if user["role"] not in allowed_roles:
        st.error("🚫 You do not have permission to record purchases.")
        return None
    return user

def run():
    st.title("📥 Record Drug Purchase")

    # 🔒 Enforce access control
    user = require_role(["procurement", "admin"])
    if not user:
        st.stop()

    user_id = user["id"]

    # 📦 Fetch drugs
    drug_data = supabase.table("drugs").select("id", "name", "stock_quantity").execute().data
    if not drug_data:
        st.warning("⚠️ No drugs available. Please add drugs first.")
        st.stop()

    drug_options = {drug["name"]: drug for drug in drug_data}
    selected_drug_name = st.selectbox("🧪 Select Drug", list(drug_options.keys()))
    selected_drug = drug_options[selected_drug_name]

    # 🧑‍💼 Fetch suppliers
    supplier_data = supabase.table("suppliers").select("id", "name").execute().data
    supplier_names = [s["name"] for s in supplier_data]

    typed_supplier_name = st.text_input("🏢 Type Supplier Name", placeholder="Start typing...")

    # 🔍 Supplier suggestions
    if typed_supplier_name:
        matches = [name for name in supplier_names if typed_supplier_name.lower() in name.lower()]
        selected_supplier_name = st.selectbox("Matching Suppliers", matches) if matches else typed_supplier_name

    quantity_purchased = st.number_input("📦 Quantity Purchased", min_value=1)
    unit_cost = st.number_input("💵 Unit Cost (UGX)", min_value=0)
    selected_date = st.date_input("🗓️ Purchase Date", value=date.today())

    # ✅ Submission logic
    if st.button("📦 Record Purchase") and typed_supplier_name and unit_cost > 0:
        try:
            # 🔎 Check if supplier exists
            existing_supplier = next((s for s in supplier_data if s["name"].lower() == selected_supplier_name.lower()), None)

            if existing_supplier:
                supplier_id = existing_supplier["id"]
            else:
                # ➕ Add new supplier
                new_supplier = {"name": selected_supplier_name}
                result = supabase.table("suppliers").insert(new_supplier).execute()
                supplier_id = result.data[0]["id"]

            # 💾 Record purchase
            purchase = {
                "drug_id": selected_drug["id"],
                "supplier_id": supplier_id,
                "quantity_purchased": quantity_purchased,
                "unit_cost": unit_cost,
                "entered_by": user_id,
                "created_at": datetime.now().isoformat(),         # Timestamp of entry
                "date_purchased": selected_date.isoformat()       # Actual purchase date
            }
            supabase.table("purchases").insert(purchase).execute()

            # 📈 Update stock
            new_stock = selected_drug["stock_quantity"] + quantity_purchased
            supabase.table("drugs").update({"stock_quantity": new_stock}).eq("id", selected_drug["id"]).execute()

            total_cost = quantity_purchased * unit_cost
            st.success(f"✅ Purchase recorded. Stock updated to {new_stock} units. Total cost: UGX {total_cost:,.0f}")
        except Exception as e:
            st.error(f"❌ Failed to record purchase: {e}")
