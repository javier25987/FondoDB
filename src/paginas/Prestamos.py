import src.funciones.prestamos as fp
import src.funciones.general as fg
import src.sql.conect as c_sql
import streamlit as st
import pandas as pd
import os

ranura_actual: str = st.session_state.ranura_actual

index: int = st.session_state.usuario_actual_prestamos

index_de_usuario: int = st.sidebar.number_input("Numero de usuario: ", value=0, step=1)

if st.sidebar.button("Buscar"):
    estado = fp.abrir_usuario(index_de_usuario)

    if estado[0]:
        st.session_state.usuario_actual_prestamos = index_de_usuario
        st.rerun()
    else:
        st.error(estado[1], icon="🚨")

if index == -1:
    st.title("Usuario indeterminado")
    st.stop()

st.title(
    f"№ {index} - {c_sql.obtener_ig("nombre", index).title()}"
)

tab = st.tabs(
    ["Prestamos", "Solicitar Prestamo", "Consultar Capital"]
)

with tab[0]:

    tablas_de_prestamos: list = fp.crear_tablas_de_prestamos(index)

    mostrar_opcion_pago: bool = False
    no_hay_prestamos: bool = True

    for i, j, k in tablas_de_prestamos:
        cols_t = st.columns([8, 2])

        with cols_t[0]:
            st.table(i)
            st.table(j)
        
        with cols_t[1]:
            st.table(k)

        no_hay_prestamos = False
        mostrar_opcion_pago = True

        st.divider()

    if no_hay_prestamos:
        st.info(
            "No se han solicitado prestamos",
            icon="ℹ️"
        )
        
    if mostrar_opcion_pago:
        st.write("aca se paga")

        # if st.button("Pagar"):
        #     if monto_a_pagar <= 0:
        #         st.error("Desea pagar 0 o menos?", icon="🚨")
        #     elif monto_a_pagar > tablas_ranura[4]:
        #         st.error("No se puede pagar mas de lo que se debe", icon="🚨")
        #     else:
        #         fp.formato_de_abono(
        #             index,
        #             monto_a_pagar,
        #             tablas_ranura[4],
        #             ranura_actual,
        #             ajustes,
        #             df,
        #         )

with tab[1]:

    st.subheader("Carta de solicitud: ")
    if st.button("Hacer carta"):
        with st.spinner("Abriendo carta"):
            fp.hacer_carta_de_prestamo()
            os.system("notepad.exe src/text/carta_prestamo.txt")
    st.divider()

    st.subheader("Formato de solicitud: ")
    col2_1, col2_2 = st.columns(2)

    with col2_1:
        valor_prestamo: int = st.number_input(
            "Valor de el prestamo: ", value=0, step=1
        )

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

            fiadores_prestamo: list[int] = []
            deudas_prestamo: list[int] = []

            for i in range(numero_de_fiadores):
                fiadores_prestamo.append(st.session_state[f"numero_fiador_{i}"])
                deudas_prestamo.append(st.session_state[f"deuda_fiador_{i}"])

            estado_prestamo: tuple[bool, str] = fp.rectificar_viavilidad(
                index,
                valor_prestamo,
                fiadores_prestamo,
                deudas_prestamo,
            )

            if estado_prestamo[0]:
                st.balloons()
                fp.formulario_de_prestamo(
                    index, valor_prestamo,
                    fiadores_prestamo, deudas_prestamo,
                )
            else:
                st.error(estado_prestamo[1], icon="🚨")
        else:
            fg.advertencia()

with tab[2]:
    capital: list = fp.consultar_capital_disponible(index)

    st.subheader("Capital")
    st.write(f"capital guardado: {capital[1]}")
    st.write(f"Capital disponible para retirar: {capital[2]}")

    st.subheader("Deudas")

    st.write(f"Deudas por fiador: {capital[3]}.")
    st.write(f"Fiador de: {df['fiador de'][index]}")

    st.write("Deudas en prestamos:")
    st.table(capital[4])

    st.write("Deudas por intereses vencidos:")
    st.table(capital[5])

    st.header(f"Dinero disponible para retirar: {capital[0]}")