import src.funciones.registros as fr
import streamlit as st
import pandas as pd

st.title("Dinero ingresado y egresado por mes")

st.pills("Mes que desea ver:", range(1, 13),
        key="mes_registro")

st.divider()

chart_data = pd.DataFrame(
    fr.solicitar_registro(
        st.session_state.mes_registro
    )
)
st.line_chart(chart_data, x="fechas")

