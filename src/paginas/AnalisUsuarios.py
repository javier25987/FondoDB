import streamlit as st
import src.funciones.analis_usuarios as f_au

index: int = st.session_state.usuario

index_de_usuario: int = st.sidebar.number_input("Numero de usuario:", value=0, step=1)

if st.sidebar.button("Buscar"):
    estado: tuple[bool, str] = f_au.abrir_usuario(index_de_usuario)
    if estado[0]:
        st.session_state.usuario = index_de_usuario
        st.rerun()
    else:
        st.toast(estado[1], icon="🚨")

tab_general, tab_usuario = st.tabs(["General", "Usuario"])

with tab_general:
    st.table(f_au.obtener_informacion_general(index))

with tab_usuario:
    if index == -1:
        st.title("Usuario indeterminado")
        st.stop()
