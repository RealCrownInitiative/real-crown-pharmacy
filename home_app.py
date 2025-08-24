import streamlit as st

def run():
    st.markdown("<h2 style='text-align:center;'>🏠 Welcome to Real Crown Pharmacy Manager</h2>", unsafe_allow_html=True)

    # 🎞️ Animated Ad Space
    st.markdown("""
    <div style='text-align:center;'>
        <img src='https://media.giphy.com/media/l0MYt5jPR6QX5pnqM/giphy.gif' width='300'>
        <h3 style='color:#FF4B4B;'>📢 ADVERTISE HERE</h3>
        <p style='font-size:16px;'>Promote your health brand, service, or product.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 📂 Choose action from the dropdown menu.")
    st.success("You're logged in as: **{}**".format(st.session_state["user"]["name"]))
