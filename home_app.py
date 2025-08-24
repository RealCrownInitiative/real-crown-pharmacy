import streamlit as st

def run():
    st.markdown("<h2 style='text-align:center;'>🏠 Welcome to Real Crown Pharmacy Manager</h2>", unsafe_allow_html=True)

    # 🙏 Sliding Bible Verses Preaching Jesus
    st.markdown("""
    <div style='text-align:center;'>
        <iframe width="325" height="575" 
                src="https://www.youtube.com/embed/dQssVLcV_OU" 
                frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
                allowfullscreen></iframe>
        <h3 style='color:#4B8BFF;'>📖 Jesus in the Psalms</h3>
        <p style='font-size:16px;'>Discover how Jesus is revealed through Scripture. Let the Word speak life into your mission.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 📂 Choose action from the dropdown menu.")
    st.success("You're logged in as: **{}**".format(st.session_state["user"]["name"]))
