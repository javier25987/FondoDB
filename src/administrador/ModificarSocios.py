import src.funciones.modificarsocios as fm
import streamlit as st
import time

st.title("Modificar Usuarios")

key: int = 0

tabs = st.tabs(
    [
        "Añadir usuario", "Realizar consultas", "Ver estructura DB",
        "Comandos SQL", "Fechas de Prestamos"
    ]
)

with tabs[0]:
    st.header("Datos de el nuevo usuario:")

    col1 = st.columns([6, 4])

    with col1[0]:
        nombre: str = st.text_input("Nombre:")
        telefono: str = st.text_input("Numero celular:")
        puestos: int = st.number_input("Numero de puestos:", value=0, step=1)

        if st.button("Añadir"):
            paso_1: bool = False
            paso_2: bool = False

            if nombre == "":
                st.error("El nombre de usuario no puede estar vacio", icon="🚨")
            else:
                paso_1 = True

            if puestos < 1:
                st.error("Para que un usuario tendria menos de un puesto?", icon="🚨")
            else:
                paso_2 = True

            if paso_1 and paso_2:
                st.toast("Por ahora esta funcion no esta activa", icon="🚨")
                # fm.menu_para_insertar_socio(nombre, puestos, telefono)

    with col1[1]:
        st.table(fm.mostrar_usuarios())


with tabs[1]:
    col2 = st.columns([8, 2], vertical_alignment="bottom")

    with col2[0]:
        consulta = st.text_area("Consulta SQL", height=220)

    with col2[1]:
        commit = st.toggle("Hacer commit")

        if st.button("SQL run"):
            if consulta == "":
                st.session_state.tabla_modificar = {}
            else:
                st.session_state.tabla_modificar = fm.realizar_consulta(
                    consulta, commit
                )

    st.divider()

    st.table(st.session_state.tabla_modificar)


with tabs[2]:
    st.markdown(fm.leer_estructura())

with tabs[3]:
    st.markdown(fm.leer_comandos())

with tabs[4]:
    col_fechas = st.columns(2)

    with col_fechas[0]:
        codigo_de_prestamo = st.selectbox(
            "Codigo del prestamo a modificar:",
            fm.consultar_codigos()
        )

    with col_fechas[1]:
        nueva_fecha = st.date_input(
            "Fecha de inicio del prestamo:"
        )

    if st.button("Corregir fechas"):
        fm.corregir_fecha(codigo_de_prestamo, nueva_fecha)
        st.balloons()
        time.sleep(1)
        st.rerun()
