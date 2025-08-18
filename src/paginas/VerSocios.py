import src.funciones.versocios as fv
import src.sql.conect as c_sql
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
        "Seleccione la rifa en la que desea buscar:", ("1", "2", "3", "4")
    )

    col4_1 = st.columns(2)

    with col4_1[0]:
        boleta_a_buscar: str = st.text_input("Numero que desea buscar en la boleta:")

    with col4_1[1]:
        numeros_boleta: int = c_sql.obtener_datos_rifas(
            rifa_a_buscar, "numeros_por_boleta"
        )

        poscion_boleta: str = st.selectbox(
            "Posicion de el numero en la boleta:", range(1, numeros_boleta + 1)
        )

    if st.button("Buscar", key="00010"):
        if fv.rectificar_numero(boleta_a_buscar, poscion_boleta):
            st.session_state.numero_buscar_boleta = fv.buscar_boleta(
                rifa_a_buscar, boleta_a_buscar, poscion_boleta
            )
        else:
            st.session_state.numero_buscar_boleta = -1

    st.divider()

    if st.session_state.numero_buscar_boleta < 0:
        st.table(fv.mostrar_boletas_todo(rifa_a_buscar))
    else:
        st.table(
            fv.mostrar_boletas(st.session_state.numero_buscar_boleta, rifa_a_buscar)
        )
