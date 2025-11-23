import src.funciones.registros as fr
import streamlit as st
import pandas as pd

st.title("Dinero ingresado y egresado por mes")

cols = st.columns([2, 8])

with cols[0]:
    mes = st.selectbox("Mes que desea ver:", range(13))

    if st.button("Cargar mes"):
        st.session_state.mes_registro = mes
        st.rerun()

with cols[1]:
    if st.session_state.mes_registro != 0:
        chart_data = pd.DataFrame(fr.solicitar_registro(st.session_state.mes_registro))
        st.line_chart(chart_data, x="fechas")
    else:
        pass
