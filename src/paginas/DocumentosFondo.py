import streamlit as st

# <fieldset>
#     <h1>Fondo San Javier</h1>
# </fieldset>

st.html("src/text/index.txt")

if st.sidebar.button("Refrescar"):
    st.rerun()