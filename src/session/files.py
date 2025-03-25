import src.funciones.general as fg
import streamlit as st

st.header("Creacion de archivos elementales")
st.markdown(
    """
        > **NOTA:** En caso de haber creado el archivo de ajustes ingrese al
        modo administrador y dirijase a la seccion 'ajustes', aqui configure
        todo lo necesario para el programa.
    """
)

if not st.session_state.ajustes_exist:
    if st.button("crear ajustes"):
        fg.crear_ajustes_de_el_programa()
        st.rerun()

if st.session_state.ajustes_exist and not st.session_state.df_exist:
    if st.button("Crear tabla"):
        fg.crear_tabla_principal()
        st.rerun()

if not st.session_state.banco_exist:
    if st.button("Crear banco"):
        fg.crear_banco()
        st.rerun()
