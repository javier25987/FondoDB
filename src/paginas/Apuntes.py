import src.funciones.apuntes as fa
import streamlit as st

columnas = st.columns(2, vertical_alignment="bottom")

with columnas[0]:
    fechas_disponibles = ["NoData"]
    fechas_disponibles += fa.fechas_disponibles()

    fecha_elegida = st.selectbox(
        "fecha a consultar:", fechas_disponibles, key="fecha_a_mostar"
    )

with columnas[1]:
    if st.button("Consultar fecha"):
        st.session_state.fecha_a_mostrar = fecha_elegida

if st.session_state.fecha_a_mostrar != "NoData":
    for fch, hor, sec, apt in fa.consultar_anotaciones(st.session_state.fecha_a_mostrar):
        st.markdown(f"* [{fch} {hor} **{sec}**] {apt}")
