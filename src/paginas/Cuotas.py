import src.funciones.cuotas as fc
import src.sql.conect as c_sql
import streamlit as st
import os

if c_sql.obtener_ajuste("calendario", False) == "n":
    st.info("El calendario aun no ha sido creado", icon="ℹ️")
    st.stop()

index: int = st.session_state.usuario_cuotas

index_de_usuario: int = st.sidebar.number_input("Numero de usuario:", value=0, step=1)

if st.sidebar.button("Buscar"):
    estado: list[bool, str] = fc.abrir_usuario(index_de_usuario)
    if estado[0]:
        st.session_state.usuario_cuotas = index_de_usuario
        st.rerun()
    else:
        st.toast(estado[1], icon="🚨")

if index == -1:
    st.title("Usuario indeterminado")
    st.stop()

nombre_usuario: str = c_sql.obtener_ig("nombre", index).title()

st.title(
    f"№ {index} - {nombre_usuario} : {
        c_sql.obtener_ig("puestos", index)
    } puesto(s)"
)

st.header(f"Numero de telefono: {c_sql.obtener_ig("telefono", index)}")

st.divider()

df1, df2 = fc.tablas_para_cuotas_y_multas(index)
col2_1, col2_2 = st.columns(2)

with col2_1:
    st.table(df1)

with col2_2:
    st.table(df2)

numero_cuotas_a_pagar: int = 50 - c_sql.obtener_cuotas("pagas", index)

if numero_cuotas_a_pagar > 10:
    numero_cuotas_a_pagar = 10

numero_multas_a_pagar: int = fc.contar_multas(
    c_sql.obtener_cuotas("multas", index)
)

cols_1 = st.columns(2)

with cols_1[0]:
    cuotas_a_pagar: int = st.selectbox(
        "Numero de cuotas a pagar:", range(numero_cuotas_a_pagar + 1)
    )

with cols_1[1]:
    multas_a_pagar: int = st.selectbox(
        "Numero de multas a pagar:", range(numero_multas_a_pagar + 1)
    )


cols_2 = st.columns(2, vertical_alignment="bottom")

with cols_2[0]:
    modo_de_pago: str = st.selectbox(
        "Modo de pago:", ("Efectivo", "Transferencia")
    )

if cols_2[1].button("Iniciar proceso de pago"):
    if cuotas_a_pagar == 0 and multas_a_pagar == 0:
        st.error("No se va a pagar nada", icon="🚨")
    else:
        st.balloons()
        fc.formulario_de_pago(
            index, cuotas_a_pagar, multas_a_pagar, modo_de_pago
        )

st.divider()
if st.button("Abrir ultimo cheque"):
    with st.spinner("Abriendo cheque..."):
        os.system("notepad.exe src/text/cheque_de_cuotas.txt")
