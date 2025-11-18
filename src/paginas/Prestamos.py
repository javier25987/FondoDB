import src.funciones.prestamos as fp
import src.funciones.general as fg
import streamlit as st
import webbrowser

index: int = st.session_state.usuario

index_de_usuario: int = st.sidebar.number_input("Numero de usuario: ", value=0, step=1)

if st.sidebar.button("Buscar"):
    estado = fp.abrir_usuario(index_de_usuario)

    if estado[0]:
        st.session_state.usuario = index_de_usuario
        st.rerun()
    else:
        st.toast(estado[1], icon="🚨")

if index == -1:
    st.title("Usuario indeterminado")
    st.stop()

fp.rectificar_prestamos(index)
user = fp.obtener_datos_usuario(index)

st.title(f"№ {index} - {user["nombre"]}")

tab = st.tabs(["Prestamos", "Solicitar Prestamo", "Consultar Capital"])

with tab[0]:
    tablas_de_prestamos: list[dict] = fp.crear_tablas_de_prestamos(index)

    mostrar_opcion_pago: bool = False
    no_hay_prestamos: bool = True

    if tablas_de_prestamos:
        mostrar_opcion_pago = True
        no_hay_prestamos = False

    for p in tablas_de_prestamos:
        st.subheader(f"Codigo: {p["codigo"]}")

        cols_t = st.columns([8, 2])

        with cols_t[0]:
            st.table(p["tabla_interes"])
            st.table(p["tabla_deuda"])
            st.subheader(f"Deuda actual: {p["deuda"]:,}")
            st.table(p["tabla_fiadores"])

        with cols_t[1]:
            st.table(p["fechas"])
            st.subheader(f"Estado: {p["estado"]}")
            st.subheader(f"Motivo: {p["motivo"]}")

        st.divider()

    if no_hay_prestamos:
        st.info("No se han solicitado prestamos", icon="ℹ️")

    if mostrar_opcion_pago:
        cols = st.columns([4, 4, 2], vertical_alignment="bottom")

        with cols[0]:
            monto_a_pagar: int = st.number_input("Monto a pagar:", value=0, step=1)

        with cols[1]:
            codigo: int = st.selectbox(
                "Codigo del prestamo:", fp.obtener_codigos(index)
            )

        with cols[2]:
            if st.button("Pagar"):
                if st.session_state.admin:
                    estado_pago: tuple[bool, str] = fp.rectificar_pago(
                        codigo, monto_a_pagar, index
                    )

                    if estado_pago[0]:
                        st.balloons()
                        fp.formato_de_abono(index, monto_a_pagar, codigo)
                    else:
                        st.toast(estado_pago[1], icon="🚨")
                else:
                    fg.advertencia()

with tab[1]:
    st.subheader("Carta de solicitud: ")
    if st.button("Abrir carta"):
        webbrowser.open_new("./src/text/carta.pdf")
    st.divider()

    st.subheader("Formato de solicitud: ")
    col2_1, col2_2 = st.columns(2)

    with col2_1:
        valor_prestamo: int = st.number_input("Valor de el prestamo: ", value=0, step=1)
        motivo_prestamo: str = st.selectbox("Motivo del prestamo:", ("PG", "ACUERDO"))

    with col2_2:
        numero_de_fiadores: int = st.number_input(
            "Cantidad de fiadores: ", value=0, step=1
        )

        col3_1, col3_2 = st.columns(2)
        key_f: int = 0
        key_d: int = 0

        for i in range(numero_de_fiadores):
            with col3_1:
                st.number_input(
                    "Numero de el fiador: ",
                    value=0,
                    step=1,
                    key=f"numero_fiador_{key_f}",
                )
                key_f += 1
            with col3_2:
                st.number_input(
                    "Deuda con el fiador: ",
                    value=0,
                    step=1,
                    key=f"deuda_fiador_{key_d}",
                )
                key_d += 1

    if st.button("Realizar prestamo"):
        if st.session_state.admin:
            fiadores_prestamo: list[int] = [
                st.session_state[f"numero_fiador_{i}"]
                for i in range(numero_de_fiadores)
            ]
            deudas_prestamo: list[int] = [
                st.session_state[f"deuda_fiador_{i}"]
                for i in range(numero_de_fiadores)
            ]

            estado_prestamo: tuple[bool, str] = fp.rectificar_viavilidad(
                index, valor_prestamo, fiadores_prestamo, deudas_prestamo,
            )

            if estado_prestamo[0]:
                st.balloons()
                fp.formulario_de_prestamo(
                    index, valor_prestamo, user, motivo_prestamo,
                    fiadores_prestamo, deudas_prestamo,
                )
            else:
                st.toast(estado_prestamo[1], icon="🚨")
        else:
            fg.advertencia()

with (tab[2]):
    data: dict = fp.capital_disponible_mostrar(index)

    st.subheader("Capital")
    st.write(f"capital pagado: {data["capital"]:,}")
    st.write(f"Capital disponible para retirar: {data["capital_disponible"]:,}")

    st.subheader("Deudas por fiador:")

    st.write(f"Deudas por fiador: {data["deudas_por_fiador"]:,}.")
    st.write(f"Fiador de: {data["fiador_de"]}")

    st.subheader("Deudas en prestamos:")
    st.table(data["tabla"])
    st.markdown(f"##### Total Deudas: {data["total_deuda"]:,}")
    st.markdown(f"##### Total Intereses: {data["total_interes"]:,}")

    st.divider()

    st.header(f"Dinero disponible para retirar: {data["total_disponible"]:,}")
