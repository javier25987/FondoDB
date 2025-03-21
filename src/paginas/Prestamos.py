import funciones.prestamos as fp
import funciones.general as fg
import streamlit as st
import pandas as pd
import os

ranura_actual: str = st.session_state.ranura_actual

ajustes: dict = fg.abrir_ajustes()
df = pd.read_csv(ajustes["nombre df"])

index: int = st.session_state.usuario_actual_prestamos

index_de_usuario: int = st.sidebar.number_input("Numero de usuario: ", value=0, step=1)

if st.sidebar.button("Buscar"):
    estado = fp.abrir_usuario(index_de_usuario, ajustes, df)

    if estado[0]:
        fp.arreglar_asuntos(index_de_usuario, ajustes, df)
        st.session_state.usuario_actual_prestamos = index_de_usuario
        st.rerun()
    else:
        st.error(estado[1], icon="🚨")

if index == -1:
    st.title("Usuario indeterminado")
    st.stop()

st.title(
    f"№ {index} - {df['nombre'][index].title()} : {df['puestos'][index]} puesto(s)"
)

tab1, tab2, tab3, tab4 = st.tabs(
    ["Prestamos", "Solicitar Prestamo", "Consultar Capital", "Anotaciones"]
)

with tab1:
    col1_1, col1_2 = st.columns(2, vertical_alignment="bottom")
    ranura_escojida: str = col1_1.selectbox(
        "Ranura a abrir:", [str(i) for i in range(1, 17)]
    )

    if col1_2.button("Abrir ranura"):
        st.session_state.ranura_actual = ranura_escojida
        st.rerun()

    st.divider()

    tablas_ranura: tuple = fp.crear_tablas_de_ranura(
        df[f"p{ranura_actual} prestamo"][index],
        df[f"p{ranura_actual} fechas de pago"][index],
    )

    st.header(f"Ranura abierta: {ranura_actual}")
    st.subheader("Informacion de el prestamo: ")
    st.table(tablas_ranura[0])
    st.table(tablas_ranura[2])
    st.subheader("Fechas de pago: ")
    st.table(tablas_ranura[1])

    if tablas_ranura[3]:
        if df[f"p{ranura_actual} estado"][index] == "activo":
            st.markdown("> **NOTA:** La ranura esta activa")
        else:
            if st.button("Activar Ranura"):
                fp.activar_ranura(index, df, ajustes, ranura_actual)
    else:
        st.subheader("Pago de prestamo:")
        col1_3 = st.columns(2, vertical_alignment="bottom")

        with col1_3[0]:
            monto_a_pagar: int = st.number_input("Monto a pagar:", value=0, step=1)
        with col1_3[1]:
            if st.button("Pagar"):
                if monto_a_pagar <= 0:
                    st.error("Desea pagar 0 o menos?", icon="🚨")
                elif monto_a_pagar > tablas_ranura[4]:
                    st.error("No se puede pagar mas de lo que se debe", icon="🚨")
                else:
                    fp.formato_de_abono(
                        index, monto_a_pagar, tablas_ranura[4], ranura_actual,
                        ajustes, df,
                    )
        st.markdown(f"> Deuda actual: {'{:,}'.format(tablas_ranura[4])}")

with tab2:
    st.subheader("Ranuras disponibles: ")
    st.table(fp.ranuras_disponibles(index, df))
    st.divider()

    st.subheader("Carta de solicitud: ")
    if st.button("Hacer carta"):
        with st.spinner("Abriendo carta"):
            fp.hacer_carta_de_prestamo()
            os.system("notepad.exe text/carta_prestamo.txt")
    st.divider()

    st.subheader("Formato de solicitud: ")
    col2_1, col2_2 = st.columns(2)

    with col2_1:
        ranura_prestamo: str = st.selectbox(
            "Ranura en la que guardar el prestamo: ", [str(i) for i in range(1, 16)]
        )
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
                    "Numero de el fiador: ", value=0, step=1,
                    key=f"numero_fiador_{key_f}",
                )
                key_f += 1
            with col3_2:
                st.number_input(
                    "Deuda con el fiador: ", value=0, step=1,
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
                index, ranura_prestamo, valor_prestamo, ajustes, df,
                fiadores_prestamo, deudas_prestamo,
            )
            if estado_prestamo[0]:
                st.balloons()
                fp.formulario_de_prestamo(
                    index, ranura_prestamo, valor_prestamo, ajustes, df,
                    fiadores_prestamo, deudas_prestamo,
                )
            else:
                st.error(estado_prestamo[1], icon="🚨")
        else:
            fg.advertencia()

with tab3:
    capital: list = fp.consultar_capital_disponible(index, ajustes, df)
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

with tab4:
    st.subheader("Realizar una anotacion:")
    anotacion: str = st.text_input("Nueva anotacion:")

    if st.button("Realizar anotacion"):
        estado_anotacion: (bool, str) = fp.realizar_anotacion(
            index, anotacion, ajustes, df
        )
        if estado_anotacion[0]:
            st.rerun()
        else:
            st.error(estado_anotacion[1], icon="🚨")

    st.divider()
    st.subheader("Anotaciones hechas:")

    anotaciones: str = df["anotaciones de prestamos"][index].split("_")

    count: int = 0
    numero_de_anotaciones: list[int] = []
    for i in anotaciones:
        st.markdown(f"> **№ {count}:** {i}")
        numero_de_anotaciones.append(count)
        count += 1

    if ajustes["mostrar MyE"]:
        st.divider()

        st.subheader("Modificar anotaciones:")
        new_anotacion: str = st.text_input("Nueva anotacion modificada:")
        cols_a_1 = st.columns(2, vertical_alignment="bottom")

        with cols_a_1[0]:
            pos_mod_anotacion: int = st.selectbox(
                "Anotacion que desea modificar:", numero_de_anotaciones
            )
        with cols_a_1[1]:
            if st.button("Modificar"):
                if st.session_state.admin:
                    fp.modificar_anotacion(
                        index, pos_mod_anotacion, new_anotacion, ajustes, df
                    )
                    st.rerun()
                else:
                    fg.advertencia()

        st.divider()
        st.subheader("Eliminar anotaciones:")

        cols_a_2 = st.columns(2, vertical_alignment="bottom")

        with cols_a_2[0]:
            pos_eli_anotacion: int = st.selectbox(
                "Anotacion que desea eliminar:", numero_de_anotaciones
            )
        with cols_a_2[1]:
            if st.button("Eliminar"):
                if st.session_state.admin:
                    fp.eliminar_anotacion(index, pos_eli_anotacion, ajustes, df)
                    st.rerun()
                else:
                    fg.advertencia()
