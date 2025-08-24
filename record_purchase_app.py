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
    drug_names = [drug["name"] for drug in drug_data]

    typed_drug_name = st.text_input("🧪 Drug Name (type or select)", placeholder="Start typing...")
    matching_drugs = [name for name in drug_names if typed_drug_name.lower() in name.lower()]
    selected_drug_name = st.selectbox("Matching Drugs", matching_drugs) if matching_drugs else typed_drug_name

    # 🧑‍💼 Fetch suppliers
    supplier_data = supabase.table("suppliers").select("id", "name").execute().data
    supplier_names = [s["name"] for s in supplier_data]

    typed_supplier_name = st.text_input("🏢 Supplier Name", placeholder="Start typing...")
    matching_suppliers = [name for name in supplier_names if typed_supplier_name.lower() in name.lower()]
    selected_supplier_name = st.selectbox("Matching Suppliers", matching_suppliers) if matching_suppliers else typed_supplier_name

    quantity_purchased = st.number_input("📦 Quantity Purchased", min_value=1)
    unit_cost = st.number_input("💵 Unit Cost (UGX)", min_value=0)
    selected_date = st.date_input("🗓️ Purchase Date", value=date.today())
    expiry_date = st.date_input("📅 Expiry Date (optional)", value=None)

    # ✅ Submission logic
    if st.button("📦 Record Purchase") and selected_drug_name and selected_supplier_name and unit_cost > 0:
        try:
            # 🔎 Check or add supplier
            existing_supplier = next((s for s in supplier_data if s["name"].lower() == selected_supplier_name.lower()), None)
            if existing_supplier:
                supplier_id = existing_supplier["id"]
            else:
                new_supplier = {"name": selected_supplier_name}
                result = supabase.table("suppliers").insert(new_supplier).execute()
                supplier_id = result.data[0]["id"]

            # 🔎 Check or add drug
            existing_drug = next((d for d in drug_data if d["name"].lower() == selected_drug_name.lower()), None)
            if existing_drug:
                drug_id = existing_drug["id"]
                current_stock = existing_drug["stock_quantity"]
            else:
                new_drug = {
                    "name": selected_drug_name,
                    "category": "Other",
                    "description": "Auto-added during purchase",
                    "price": unit_cost,
                    "stock_quantity": 0,
                    "expiry_date": expiry_date.isoformat() if expiry_date else None,
                    "supplier_id": supplier_id
                }
                result = supabase.table("drugs").insert(new_drug).execute()
                drug_id = result.data[0]["id"]
                current_stock = 0
                st.info(f"🆕 New drug added: {selected_drug_name}")

            # 💾 Record purchase
            purchase = {
                "drug_id": drug_id,
                "supplier_id": supplier_id,
                "quantity_purchased": quantity_purchased,
                "unit_cost": unit_cost,
                "entered_by": user_id,
                "created_at": datetime.now().isoformat(),
                "date_purchased": selected_date.isoformat(),
                "expiry_date": expiry_date.isoformat() if expiry_date else None
            }
            supabase.table("purchases").insert(purchase).execute()

            # 📈 Update stock
            new_stock = current_stock + quantity_purchased
            supabase.table("drugs").update({"stock_quantity": new_stock}).eq("id", drug_id).execute()

            total_cost = quantity_purchased * unit_cost
            st.success(f"✅ Purchase recorded. Stock updated to {new_stock} units. Total cost: UGX {total_cost:,.0f}")
        except Exception as e:
            st.error(f"❌ Failed to record purchase: {e}")
