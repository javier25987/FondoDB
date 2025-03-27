import streamlit as st
import src.funciones.transferencias as ft

st.title("Transferencias hechas")

st.subheader("Buscar:")

cols = st.columns(2, vertical_alignment="bottom")

with cols[0]:
    usuario_buscar: int = st.selectbox(
        "Numero de usuario:",
        ft.obtener_usuarios()
    )

with cols[1]:
    cols_1 = st.columns(2)
    with cols_1[0]:
        if st.button("Buscar"):
            st.session_state.numero_transf = usuario_buscar
            st.rerun()

    with cols_1[1]:
        if st.button("Mostrar todo"):
            st.session_state.numero_transf = -1

st.divider()

if st.session_state.numero_transf < 0:
    st.table(
        ft.mostrar_transferencias_todo()
    )
else:
    st.table(
        ft.mostrar_transferencias(
            st.session_state.numero_transf
        )
    )