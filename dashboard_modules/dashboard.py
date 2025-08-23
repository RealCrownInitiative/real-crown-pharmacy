import streamlit as st

# ------------------ Admin Dashboard ------------------ #
def admin_dashboard():
    st.title("🧑‍⚕️ Admin Dashboard")
    st.markdown("Welcome to the admin dashboard. Here you can:")
    st.markdown("""
    - 👥 Manage users  
    - 📦 Oversee inventory  
    - 📊 View system reports  
    """)
    st.markdown("---")

# ------------------ Pharmacist Dashboard ------------------ #
def pharmacist_dashboard():
    st.title("💊 Pharmacist Dashboard")
    st.markdown("Welcome to the pharmacist dashboard. Here you can:")
    st.markdown("""
    - 🧾 View prescriptions  
    - 💉 Dispense medications  
    - 📦 Track stock levels  
    """)
    st.markdown("---")

# ------------------ Role Check Helper ------------------ #
def require_login():
    user = st.session_state.get("user")
    if not user:
        st.error("🔐 Access denied. Please log in.")
        return None
    return user

# ------------------ Main Dashboard Router ------------------ #
def show_dashboard():
    user = require_login()
    if not user:
        return

    role = user["role"]

    st.sidebar.title("🔍 Navigation")
    selection = st.sidebar.radio("Choose a section:", ["Dashboard", "Reports", "Inventory"])

    if selection == "Dashboard":
        if role == "admin":
            admin_dashboard()
        elif role == "pharmacist":
            pharmacist_dashboard()
        else:
            st.warning("Unknown role. Please contact system administrator.")

    elif selection == "Reports":
        if role in ["admin", "supervisor"]:
            st.title("📊 Reports")
            st.info("Report module coming soon... 🚧")
        else:
            st.error("🚫 You do not have permission to view reports.")

    elif selection == "Inventory":
        if role in ["admin", "pharmacist"]:
            st.title("📦 Inventory")
            st.info("Inventory module coming soon... 🚧")
        else:
            st.error("🚫 You do not have permission to view inventory.")

# ------------------ Entry Point ------------------ #
def run():
    show_dashboard()
