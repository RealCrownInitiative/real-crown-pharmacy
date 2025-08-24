import streamlit as st

# ✅ Folder-level imports
from auth import login, session
from dashboard_modules import dashboard, drug_inventory_dashboard, finance, inventory, summary
from components import navbar, sidebar, metrics
from utils import validators, logger

# ✅ Root-level imports
import auth_app
import add_drug_app
import record_sale_app
import record_purchase_app
import summary_dashboard
import home_app
import manage_users_app  # ✅ Admin-only module

# ------------------ App Entry Point ------------------ #
def run():
    st.set_page_config(page_title="Real Crown Pharmacy", layout="wide")

    # 🏷️ Branding Header
    st.title("💊 RCCLINIC PMS")
    st.markdown("Choose an action below:")

    # ------------------ Session Initialization ------------------ #
    if "user" not in st.session_state:
        st.session_state.user = None
    if "option" not in st.session_state:
        st.session_state.option = "Login"
    if "redirect_to_home" not in st.session_state:
        st.session_state.redirect_to_home = False

    # ------------------ Navigation Modules ------------------ #
    modules = [
        "Home",
        "Dashboard",
        "Add Drug",
        "Record Sale",
        "Record Purchase",
        "Inventory",
        "Summary",
        "Manage Users"
    ]

    # ------------------ Authenticated View ------------------ #
    if st.session_state.user:
        if st.session_state.redirect_to_home:
            st.session_state.redirect_to_home = False
            st.session_state.option = "Home"

        selected = st.selectbox("📂 Select Module", modules, index=modules.index(st.session_state.option))
        st.session_state.option = selected

        # 🚪 Logout Button
        if st.button("🔓 Logout"):
            st.session_state.clear()
            st.success("You have been logged out.")
            st.experimental_rerun()
    else:
        st.session_state.option = "Login"

    # ------------------ Access Control ------------------ #
    def require_login():
        if not st.session_state.user:
            st.warning("🔐 Please log in to access this section.")
            return False
        return True

    def require_role(allowed_roles):
        if not require_login():
            return False
        user = st.session_state.user
        if user["role"] not in allowed_roles:
            st.error("🚫 You do not have permission to access this section.")
            return False
        return True

    # ------------------ Module Routing ------------------ #
    option = st.session_state.option

    if option == "Login":
        auth_app.run()
        if st.session_state.user and not st.session_state.redirect_to_home:
            st.success("✅ Login successful! Redirecting to Home...")
            st.session_state.redirect_to_home = True
            st.stop()  # ⛔ Prevents further execution, avoids rerun error

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

    elif option == "Manage Users":
        if require_role(["admin"]):
            manage_users_app.run()

    else:
        st.error("⚠️ Unknown module selected. Returning to Home.")
        st.session_state.option = "Home"
        st.experimental_rerun()

    # ------------------ Footer Branding ------------------ #
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; font-size: 14px;'>
        Developed by <strong>Sseguya Stephen Jonathan</strong>  
        <br>📞 Phone: (+256)788739050   
        <br>🏢 Powered by <strong>Real Crown Cyber House</strong>  
        <br>🎯 Sponsored by <strong>Real Crown Initiative</strong>  
        <br>📧 Email: <a href='mailto:realcrowninitiative@gmail.com'>realcrowninitiative@gmail.com</a>
    </div>
    """, unsafe_allow_html=True)

# 🏁 Execute if run directly
if __name__ == "__main__":
    run()
