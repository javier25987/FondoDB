import src.funciones.versocios as fv
import streamlit as st

tabs = st.tabs(["Buscar Usuarios", "Ver si necesita acuerdo", "Buscar boleta"])

with tabs[0]:
    cols = st.columns([6, 4], vertical_alignment="bottom")

    with cols[0]:
        nombre_a_buscar = st.text_input("Nombre apellido o segmento a buscar:")
    with cols[1]:
        if st.button("Buscar"):
            st.session_state.nombre_para_busqueda = nombre_a_buscar
            st.rerun()

    st.divider()

    st.table(fv.buscar_nombre(st.session_state.nombre_para_busqueda))


with tabs[1]:
    st.info(
        "Todos los usuarios en esta tabla para la "
        "fecha actual tienen que firmar acuerdo",
        icon="ℹ️",
    )
    st.table(fv.tabla_acuerdo())

with tabs[2]:
    rifa_a_buscar: str = st.selectbox(
        "Seleccione la tabla en la que desea buscar:", ("boletas_rifa_1", "boletas_rifa_2")
    )

    col4_1 = st.columns(2, vertical_alignment="bottom")

    with col4_1[0]:
        boleta_a_buscar: str = st.text_input("Numero que desea buscar en la boleta:")

    with col4_1[1]:
        if st.button("Buscar", key="00010"):
            if boleta_a_buscar == "":
                st.session_state.numero_buscar_boleta = True
            else:
                st.session_state.numero_buscar_boleta = False

    st.divider()

    if not st.session_state.numero_buscar_boleta:
        st.table(fv.buscar_boleta(rifa_a_buscar, boleta_a_buscar))
