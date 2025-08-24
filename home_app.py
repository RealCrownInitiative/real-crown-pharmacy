import streamlit as st

def run():
    st.markdown("<h2 style='text-align:center;'>🏠 Welcome to Real Crown Home</h2>", unsafe_allow_html=True)

    st.markdown("""
    <div style='text-align:center;'>
        <img src='https://media.giphy.com/media/3o7aD2saalBwwftBIY/giphy.gif' width='200'>
        <p style='font-size:18px;'>Your central hub for pharmacy operations, insights, and impact.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 📂 Choose a module from the sidebar to begin.")
    st.success("You're logged in as: **{}**".format(st.session_state["user"]["name"]))
