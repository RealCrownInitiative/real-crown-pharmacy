import os
from dotenv import load_dotenv
from supabase import create_client, Client
import streamlit as st
import pandas as pd

# 🔐 Load environment variables and initialize Supabase
load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

# 🔐 Role check helper
def require_role(allowed_roles):
    user = st.session_state.get("user")
    if not user:
        st.warning("🔐 Please log in to view summary reports.")
        return None
    if user["role"] not in allowed_roles:
        st.error("🚫 You do not have permission to view this dashboard.")
        return None
    return user

def run():
    st.title("📊 Purchase & Sales Summary Dashboard")

    # 🔒 Enforce access control
    user = require_role(["admin", "supervisor"])
    if not user:
        st.stop()

    # 📥 Fetch data
    sales_data = supabase.table("sales").select("*").execute().data
    purchase_data = supabase.table("purchases").select("*").execute().data

    # 🧾 Convert to DataFrames
    sales_df = pd.DataFrame(sales_data)
    purchase_df = pd.DataFrame(purchase_data)

    # 🗓️ Format date columns safely
    def format_date_column(df, possible_columns):
        for col in possible_columns:
            if col in df.columns:
                try:
                    df[col] = pd.to_datetime(df[col])
                    return col
                except:
                    continue
        return None

    sales_date_col = format_date_column(sales_df, ["date_sold", "created_at", "timestamp"])
    purchase_date_col = format_date_column(purchase_df, ["created_at", "date_purchased", "timestamp"])

    # 📅 Time period selector
    period = st.selectbox("Select Time Period", ["Daily", "Monthly", "Yearly"])

    # 📊 Generate summaries only if date columns are found
    if sales_date_col and purchase_date_col:
        # 💸 Calculate total cost for purchases
        if "unit_cost" in purchase_df.columns:
            purchase_df["total_cost"] = purchase_df["unit_cost"] * purchase_df["quantity_purchased"]
        else:
            purchase_df["total_cost"] = 0

        # ⏱️ Group by selected period
        if period == "Daily":
            sales_summary = sales_df.groupby(sales_df[sales_date_col].dt.date)["total_price"].sum().reset_index()
            purchase_summary = purchase_df.groupby(purchase_df[purchase_date_col].dt.date)["total_cost"].sum().reset_index()
        elif period == "Monthly":
            sales_summary = sales_df.groupby(sales_df[sales_date_col].dt.to_period("M"))["total_price"].sum().reset_index()
            purchase_summary = purchase_df.groupby(purchase_df[purchase_date_col].dt.to_period("M"))["total_cost"].sum().reset_index()
        else:  # Yearly
            sales_summary = sales_df.groupby(sales_df[sales_date_col].dt.year)["total_price"].sum().reset_index()
            purchase_summary = purchase_df.groupby(purchase_df[purchase_date_col].dt.year)["total_cost"].sum().reset_index()

        # 🧾 Rename columns for clarity
        sales_summary.columns = ["Period", "Total Sales (UGX)"]
        purchase_summary.columns = ["Period", "Total Purchases (UGX)"]

        # 📈 Display charts
        st.subheader("💰 Sales Summary")
        st.bar_chart(sales_summary.set_index("Period"))

        st.subheader("💸 Purchase Summary")
        st.bar_chart(purchase_summary.set_index("Period"))

        # 📊 Financial Overview
        total_income = sales_df["total_price"].sum()
        total_expenditure = purchase_df["total_cost"].sum()
        net_profit = total_income - total_expenditure

        st.subheader("📋 Financial Overview")
        st.metric("Total Income (UGX)", f"{total_income:,.0f}")
        st.metric("Total Expenditure (UGX)", f"{total_expenditure:,.0f}")
        st.metric("Net Profit (UGX)", f"{net_profit:,.0f}")
    else:
        st.warning("⚠️ Could not detect valid date columns in your data.")
