import streamlit as st

# ✅ Import modules from folders
from auth import login, session
from dashboard_modules import dashboard, drug_inventory_dashboard, finance, inventory, summary
from components import navbar, sidebar, metrics
from utils import validators, logger

# ✅ Import modules from root directory
import auth_app
import add_drug_app
import record_sale_app
import record_purchase_app
import summary_dashboard  # Or use summary.run() if preferred
import home_app  # ✅ New Home module

def run():
    st.set_page_config(page_title="Real Crown Pharmacy", layout="wide")

    # 🏷️ Branding Header
    st.title("💊 Real Crown Pharmacy Management System")
    st.markdown("Welcome to the central dashboard. Choose an action below:")

    # 📂 Navigation options
    if "user" in st.session_state:
        option = st.selectbox("📂 Select Module", [
            "Home",
            "Dashboard",
            "Add Drug",
            "Record Sale",
            "Record Purchase",
            "Inventory",
            "Summary"
        ])
    else:
        option = "Login"

    # 🔐 Login and Role Checks
    def require_login():
        if "user" not in st.session_state:
            st.warning("🔐 Please log in to access this section.")
            return False
        return True

    def require_role(allowed_roles):
        if not require_login():
            return False
        user = st.session_state.get("user")
        if user["role"] not in allowed_roles:
            st.error("🚫 You do not have permission to access this section.")
            return False
        return True

    # 🚀 Route to selected module
    if option == "Login":
        auth_app.run()
        if "user" in st.session_state:
            st.success("✅ Login successful! Redirecting to Home...")
            st.experimental_rerun()

    elif option == "Home":
        if require_login():
            home_app.run()

    elif option == "Dashboard":
        if require_role(["admin", "supervisor"]):
            dashboard.run()

    elif option == "Add Drug":
        if require_role(["pharmacist", "admin"]):
            add_drug_app.run()

    elif option == "Record Sale":
        if require_role(["cashier", "pharmacist", "admin"]):
            record_sale_app.run()

    elif option == "Record Purchase":
        if require_role(["procurement", "admin"]):
            record_purchase_app.run()

    elif option == "Inventory":
        if require_role(["pharmacist", "admin"]):
            drug_inventory_dashboard.run()

    elif option == "Summary":
        if require_role(["admin", "supervisor"]):
            summary_dashboard.run()

    # 📌 Footer with branding
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; font-size: 14px;'>
        Developed by <strong>Sseguya Stephen Jonathan</strong>  
        <br>📞 Phone: +256788739050  
        <br>🏢 Powered by <strong>Real Crown Cyber House</strong>  
        <br>🎯 Sponsored by <strong>Real Crown Initiative</strong>  
        <br>📧 Email: <a href='mailto:realcrowninitiative@gmail.com'>realcrowninitiative@gmail.com</a>
    </div>
    """, unsafe_allow_html=True)

# 🏁 Run immediately if this is the main file
if __name__ == "__main__":
    run()
