import src.funciones.versocios as fv
import src.funciones.general as fg
import streamlit as st
import pandas as pd

tabs = st.tabs(
    [
        "Buscar Usuarios",
        "Ver si necesita acuerdo",
        "Verificar ranura 16",
        "Buscar boleta"
    ]
)

with tabs[0]:
    cols = st.columns([6, 4], vertical_alignment="bottom")

    with cols[0]:
        nombre_a_buscar = st.text_input("Nombre apellido o segmento a buscar:")
    with cols[1]:
        if st.button("Buscar"):
            st.session_state.nombre_para_busqueda = nombre_a_buscar
            st.rerun()
    st.divider()


with tabs[1]:
    st.table(fv.tabla_acuerdo())

with tabs[2]:
    st.table(fv.tabla_ranura())

with tabs[3]:
    pass
    # rifa_a_buscar: str = st.selectbox(
    #     "Seleccione la rifa en la que desea buscar:", ("1", "2", "3", "4")
    # )
    #
    # col4_1 = st.columns(2)
    #
    # with col4_1[0]:
    #     boleta_a_buscar: str = st.text_input("Numero que desea buscar en la boleta:")
    #
    # with col4_1[1]:
    #     numeros_boleta: str = ajustes[f"r{rifa_a_buscar} numeros por boleta"]
    #
    #     poscion_boleta: str = st.selectbox(
    #         "Posicion de el numero en la boleta:", range(1, numeros_boleta + 1)
    #     )
    #
    # tabla_boletas = df
    #
    # if st.button("Buscar", key="00010"):
    #     if boleta_a_buscar != "":
    #         if poscion_boleta is not None:
    #             numero_usuario_boleta: int = fv.buscar_boleta(
    #                 df, rifa_a_buscar, boleta_a_buscar, poscion_boleta
    #             )
    #             if numero_usuario_boleta >= 0:
    #                 tabla_boletas = df[df["numero"] == numero_usuario_boleta]
    #
    # st.divider()
    # st.table(tabla_boletas[["numero", "nombre", f"r{rifa_a_buscar} boletas"]])

