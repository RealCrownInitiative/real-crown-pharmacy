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

# ------------------ Safe Extractors ------------------ #
def extract_name(obj):
    try:
        return obj.get("name", "Unknown") if isinstance(obj, dict) else "Unknown"
    except Exception:
        return "Unknown"

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
        df["Drug Name"] = df["drugs"].apply(extract_name)
        df["Sold By"] = df["sold_by"].apply(extract_name)

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
        df["Drug Name"] = df["drugs"].apply(extract_name)
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

# ------------------ Summary Reports ------------------ #
def view_reports():
    st.subheader("📊 Summary Reports")
    report_type = st.selectbox("Choose report type", ["Daily", "Weekly", "Monthly"])

    if report_type == "Daily":
        selected_date = st.date_input("Select date for daily summary")
        start = datetime.combine(selected_date, datetime.min.time())
        end = start + timedelta(days=1)
        label = selected_date.strftime("%B %d, %Y")

    elif report_type == "Weekly":
        selected_week = st.date_input("Select start date of week")
        start = datetime.combine(selected_week, datetime.min.time())
        end = start + timedelta(days=7)
        label = f"Week of {selected_week.strftime('%B %d, %Y')}"

    elif report_type == "Monthly":
        selected_month = st.date_input("Select any date in the month")
        start = datetime(selected_month.year, selected_month.month, 1)
        if selected_month.month == 12:
            end = datetime(selected_month.year + 1, 1, 1)
        else:
            end = datetime(selected_month.year, selected_month.month + 1, 1)
        label = selected_month.strftime("%B %Y")

    # 🔹 Fetch Sales
    sales_query = supabase.table("sales").select("total_price") \
        .gte("date_sold", start.isoformat()) \
        .lt("date_sold", end.isoformat()) \
        .execute()
    sales_data = sales_query.data
    total_sales = sum(item["total_price"] for item in sales_data) if sales_data else 0

    # 🔹 Fetch Purchases
    purchase_query = supabase.table("purchases").select("quantity_purchased", "unit_cost") \
        .gte("created_at", start.isoformat()) \
        .lt("created_at", end.isoformat()) \
        .execute()
    purchase_data = purchase_query.data
    total_purchases = sum(item["quantity_purchased"] * item["unit_cost"] for item in purchase_data) if purchase_data else 0

    # 📋 Display Summary
    st.markdown(f"### 📅 Summary for {label}")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("💰 Total Sales", f"UGX {total_sales:,.0f}")
    with col2:
        st.metric("📦 Total Purchases", f"UGX {total_purchases:,.0f}")

    net = total_sales - total_purchases
    st.markdown("---")
    st.metric("📊 Net Flow (Sales - Purchases)", f"UGX {net:,.0f}", delta=net)

import streamlit as st
import pandas as pd
from auth.supabase_client import create_user  # Ensure this import is valid
from auth.supabase_client import supabase     # Add this if supabase isn't already imported

def manage_users():
    st.markdown("---")  # 🔹 Top separator for visibility
    st.title("👥 Manage Users")

    # ------------------ Register New User ------------------ #
    st.markdown("### 🆕 Register New User")
    with st.form("register_user_form"):
        name = st.text_input("Full Name")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        role = st.selectbox("Role", ["admin", "pharmacist", "cashier", "procurement", "supervisor"])  # Founder excluded
        submitted = st.form_submit_button("Register User")
        if submitted:
            result = create_user(email=email, password=password, role=role, name=name)
            if result.get("success"):
                st.success("✅ User registered successfully.")
            else:
                st.error(f"❌ Registration failed: {result.get('error')}")

    st.markdown("---")

    # ------------------ View & Manage Existing Users ------------------ #
    query = supabase.table("users").select("*").execute()
    users = query.data

    # ✅ One-time founder creation check
    founder_exists = any(user["role"] == "founder" for user in users)
    if not founder_exists:
        founder_result = create_user(
            email="realcrowninitiative@gmail.com",
            password="rc@admin",
            role="founder",
            name="Real Crown Initiative"
        )
        if founder_result.get("success"):
            st.success("👑 Founder account created successfully.")
        else:
            st.error(f"❌ Failed to create founder: {founder_result.get('error')}")

    if not users:
        st.info("No users found.")
        return

    df = pd.DataFrame(users)
    st.dataframe(df[["id", "name", "email", "role", "verified"]])

    st.markdown("### 🔧 Admin Controls")

    role_options = ["admin", "pharmacist", "cashier", "procurement", "supervisor"]

    for user in users:
        if user["role"] == "founder":
            st.markdown(f"👑 **{user['name']}** ({user['email']}) — *Founder* 🔒 Protected")
            continue  # Skip all controls for founder

        col1, col2, col3, col4 = st.columns([3, 2, 2, 3])
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

        with col4:
            index = role_options.index(user["role"]) if user["role"] in role_options else 0
            new_role = st.selectbox("Change Role", role_options, index=index, key=f"role_{user['id']}")
            if new_role != user["role"]:
                supabase.table("users").update({"role": new_role}).eq("id", user["id"]).execute()
                st.success(f"{user['name']}'s role updated to {new_role}.")


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
            view_reports()
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
