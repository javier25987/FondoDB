import src.funciones.modificarsocios as fm
import streamlit as st
import time

index: int = st.session_state.usuario

index_de_usuario: int = st.sidebar.number_input("Numero de usuario:", value=0, step=1)

if st.sidebar.button("Buscar"):
    estado: tuple[bool, str] = fm.abrir_usuario(index_de_usuario)
    if estado[0]:
        st.session_state.usuario = index_de_usuario
        st.rerun()
    else:
        st.toast(estado[1], icon="🚨")


st.title("Modificar Usuarios")

tabs = st.tabs(
    [
        "Añadir usuario", "Ver estructura DB", "Comandos SQL",
        "Fechas de Prestamos", "Modificar multas"
    ]
)

with tabs[0]:
    st.header("Datos del nuevo usuario:")

    col1 = st.columns([5, 5])

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
    st.markdown(fm.leer_estructura())


with tabs[2]:
    st.markdown(fm.leer_comandos())


with tabs[3]:
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


with tabs[4]:
    user = fm.obtener_datos_usuario(index)
    cols_m = st.columns(2)

    with cols_m[0]:
        st.subheader(f"№ {index} - {user["nombre"]}")
        semana: int = st.selectbox("Semana a modificar:", range(1, 51))
        tipo: str = st.selectbox("Tipo de multa:", ("Multas activas", "Multas pagas"))
        valor: int = st.number_input("Nuevo valor:", step=1, value=1)

        if st.button("Guardar valor"):
            estado: tuple[bool, str] = fm.rectificar_datos(valor)

            if estado[0]:
                fm.agregar_nuevo_valor(index, semana, tipo, valor, user)
                st.rerun()
            else:
                st.toast(estado[1], icon="🚨")


    with cols_m[1]:
        st.table(user["multas"])
