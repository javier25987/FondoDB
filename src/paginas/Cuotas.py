import src.funciones.general as fg
import src.funciones.cuotas as fc
import streamlit as st
import pandas as pd
import os

if fg.obtener_ajuste("calendario", False) == "n":
    st.info("El calendario aun no ha sido creado", icon="ℹ️")
    st.stop()

index: int = st.session_state.usuario_actual_cuotas

index_de_usuario: int = st.sidebar.number_input("Numero de usuario:", value=0, step=1)

if st.sidebar.button("Buscar"):
    estado: list[bool, str] = fc.abrir_usuario(index_de_usuario)
    if estado[0]:
        st.session_state.usuario_actual_cuotas = index_de_usuario
        st.rerun()
    else:
        st.error(estado[1], icon="🚨")

if index == -1:
    st.title("Usuario indeterminado")
    st.stop()

nombre_usuario: str = df["nombre"][index].title()
st.title(
    f"№ {index} - {df['nombre'][index].title()} : {df['puestos'][index]} puesto(s)"
)

tabs = st.tabs(["Pagar cuotas y multas", "Pagos por transferencia", "Anotaciones"])

with tabs[0]:
    st.header(f"Numero de telefono: {df['numero celular'][index]}")

    st.divider()

    df1, df2 = fc.tablas_para_cuotas_y_multas(index, ajustes, df)
    col2_1, col2_2 = st.columns(2)

    with col2_1:
        st.table(df1)

    with col2_2:
       st.table(df2)

    numero_cuotas_a_pagar: int = 50 - df["cuotas"][index].count("p")

    if numero_cuotas_a_pagar > 10:
        numero_cuotas_a_pagar = 10

    numero_multas_a_pagar: int = fc.contar_multas(df["multas"][index])

    cols_1 = st.columns(2)

    with cols_1[0]:
        cuotas_a_pagar: int = st.selectbox(
            "Numero de cuotas a pagar:", range(numero_cuotas_a_pagar + 1)
        )

        tesorero_a_pagar: str = st.selectbox("Tesorero:", ("1", "2", "3", "4"))

    with cols_1[1]:
        multas_a_pagar: int = st.selectbox(
            "Numero de multas a pagar:", range(numero_multas_a_pagar + 1)
        )

        modo_de_pago: str = st.selectbox(
            "Modo de pago:", ("Efecctivo", "Transferencia")
        )

    if cols_1[0].button("Iniciar proceso de pago"):
        if cuotas_a_pagar == 0 and multas_a_pagar == 0:
            st.error("No se que desea pagar", icon="🚨")
        else:
            st.balloons()
            fc.formulario_de_pago(
                index, cuotas_a_pagar, multas_a_pagar, tesorero_a_pagar,
                modo_de_pago, ajustes, banco, df,
            )

    st.divider()
    if st.button("Abrir ultimo cheque"):
        with st.spinner("Abriendo cheque..."):
            os.system("notepad.exe src/text/cheque_de_cuotas.txt")