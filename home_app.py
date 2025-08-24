import streamlit as st

def run():
    st.markdown("<h2 style='text-align:center;'>🏠 Welcome to Real Crown Pharmacy Manager</h2>", unsafe_allow_html=True)

    # 🙏 Salvation Prayer Image
    st.markdown("""
    <div style='text-align:center;'>
        <img src='https://i.pinimg.com/originals/5e/3b/2d/5e3b2d3f8f6e3e6a6c4e6b6e6f6e6e6e.jpg' width='300'>
        <h3 style='color:#4B8BFF;'>🕊️ Prayer of Salvation</h3>
        <p style='font-size:16px;'>"Lord Jesus, I believe You died for me and rose again. I accept You as my Lord and Savior. Come into my heart and guide me forever."</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 📂 Choose action from the dropdown menu.")
    st.success("You're logged in as: **{}**".format(st.session_state["user"]["name"]))
