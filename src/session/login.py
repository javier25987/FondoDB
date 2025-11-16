from src.msql import obtener_ajuste
import streamlit as st
import time

st.title("Ingresar como administrador")

st.markdown(
    """
    Por favor ingrese su contraseña de administrador para acceder
    a las funciones extra de el programa
    """
)

clave: str = st.text_input("Contraseña de administrador:", type="password")

if st.button("Ingresar"):
    if clave == obtener_ajuste("clave acceso", False):
        st.toast("Ha obtenido acceso de administador", icon="🎉")
        st.session_state.admin = True
        time.sleep(1)
        st.rerun()
    elif clave == "":
        st.error("La contraseña esta vacia", icon="🚨")
    else:
        st.error("La contraseña es incorrecta", icon="🚨")
