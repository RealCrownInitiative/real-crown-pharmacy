import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv
from supabase import create_client, Client
from datetime import datetime, timedelta

# ------------------ Supabase Setup ------------------ #
load_dotenv()
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

# ------------------ Role Check Helper ------------------ #
def require_login():
    user = st.session_state.get("user")
    if not user:
        st.error("🔐 Access denied. Please log in.")
        return None
    return user

# ------------------ Admin Dashboard ------------------ #
def admin_dashboard():
    st.title("🧑‍⚕️ Admin Dashboard")
    st.markdown("""
    Welcome to the admin dashboard. Here you can:
    - 👥 Manage users   
    - 📊 View system reports  
    - 🧾 View sales and purchases  
    """)
    st.markdown("---")

# ------------------ Pharmacist Dashboard ------------------ #
def pharmacist_dashboard():
    st.title("💊 Pharmacist Dashboard")
    st.markdown("""
    Welcome to the pharmacist dashboard. Here you can:
    - 🧾 View prescriptions  
    - 💉 Dispense medications  
    - 📦 Track stock levels  
    - 🧾 View sales and purchases  
    """)
    st.markdown("---")

# ------------------ Sales Viewer ------------------ #
def view_sales():
    st.subheader("🧾 Sales Records")
    selected_date = st.date_input("Select date to view sales")

    start = datetime.combine(selected_date, datetime.min.time())
    end = start + timedelta(days=1)

    query = supabase.table("sales").select("*, drugs(name), sold_by(name)") \
        .gte("date_sold", start.isoformat()) \
        .lt("date_sold", end.isoformat()) \
        .execute()

    data = query.data
    if data:
        df = pd.DataFrame(data)
        df["Drug Name"] = df["drugs"].apply(lambda x: x["name"])
        df["Sold By"] = df["sold_by"].apply(lambda x: x["name"])

        st.dataframe(df[[
            "Drug Name",
            "quantity_sold",
            "total_price",
            "Sold By",
            "date_sold"
        ]])
    else:
        st.info("No sales recorded on this date.")


# ------------------ Purchases Viewer ------------------ #
def view_purchases():
    st.subheader("📦 Purchase Records")
    selected_date = st.date_input("Select date to view purchases")

    start = datetime.combine(selected_date, datetime.min.time())
    end = start + timedelta(days=1)

    query = supabase.table("purchases").select("*, drugs(name)") \
        .gte("created_at", start.isoformat()) \
        .lt("created_at", end.isoformat()) \
        .execute()

    data = query.data
    if data:
        df = pd.DataFrame(data)
        df["Drug Name"] = df["drugs"].apply(lambda x: x["name"])
        df["Total Cost"] = df["quantity_purchased"] * df["unit_cost"]

        st.dataframe(df[[
            "Drug Name",
            "quantity_purchased",
            "unit_cost",
            "Total Cost",
            "created_at"
        ]])
    else:
        st.info("No purchases recorded on this date.")

        
# ------------------ Manage Users ------------------ #
def manage_users():
    st.title("👥 Manage Users")

    query = supabase.table("users").select("*").execute()
    users = query.data

    if not users:
        st.info("No users found.")
        return

    df = pd.DataFrame(users)
    st.dataframe(df[["id", "name", "email", "role", "verified"]])

    st.markdown("### 🔧 Admin Controls")

    for user in users:
        col1, col2, col3 = st.columns([3, 2, 2])
        with col1:
            st.write(f"**{user['name']}** ({user['email']}) — *{user['role']}*")
        with col2:
            verify_toggle = st.checkbox("Verified", value=user["verified"], key=f"verify_{user['id']}")
            if verify_toggle != user["verified"]:
                supabase.table("users").update({"verified": verify_toggle}).eq("id", user["id"]).execute()
                st.success(f"{user['name']} verification updated.")
        with col3:
            if st.button("🗑️ Delete", key=f"delete_{user['id']}"):
                supabase.table("users").delete().eq("id", user["id"]).execute()
                st.warning(f"{user['name']} deleted.")



# ------------------ Main Dashboard Router ------------------ #
def show_dashboard():
    user = require_login()
    if not user:
        return

    role = user["role"]

    st.sidebar.title("🔍 Navigation")
    if role == "admin":
        selection = st.sidebar.radio("Choose a section:", [
            "Dashboard", "Manage Users", "Reports", "Sales", "Purchases"
        ])
    else:
        selection = st.sidebar.radio("Choose a section:", [
            "Dashboard", "Sales", "Purchases"
        ])

    if selection == "Dashboard":
        if role == "admin":
            admin_dashboard()
        elif role == "pharmacist":
            pharmacist_dashboard()
        else:
            st.warning("Unknown role. Please contact system administrator.")

    elif selection == "Manage Users":
        if role == "admin":
            manage_users()
        else:
            st.error("🚫 You do not have permission to manage users.")

    elif selection == "Reports":
        if role in ["admin", "supervisor"]:
            st.title("📊 Reports")
            st.info("Report module coming soon... 🚧")
        else:
            st.error("🚫 You do not have permission to view reports.")

    elif selection == "Sales":
        if role in ["admin", "pharmacist"]:
            view_sales()
        else:
            st.error("🚫 You do not have permission to view sales.")

    elif selection == "Purchases":
        if role in ["admin", "pharmacist"]:
            view_purchases()
        else:
            st.error("🚫 You do not have permission to view purchases.")

# ------------------ Entry Point ------------------ #
def run():
    show_dashboard()
