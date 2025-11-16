import src.funciones.cuotas as fc
import src.msql as msql
import streamlit as st
import webbrowser

if msql.obtener_ajuste("calendario", False) == "n":
    st.info("El calendario aun no ha sido creado", icon="ℹ️")
    st.stop()

index: int = st.session_state.usuario

index_de_usuario: int = st.sidebar.number_input("Numero de usuario:", value=0, step=1)

if st.sidebar.button("Buscar"):
    estado: tuple[bool, str] = fc.abrir_usuario(index_de_usuario)
    if estado[0]:
        st.session_state.usuario = index_de_usuario
        st.rerun()
    else:
        st.toast(estado[1], icon="🚨")

if index == -1:
    st.title("Usuario indeterminado")
    st.stop()

user = fc.obtener_datos_usuario(index)

st.title(
    f"№ {index} - {user["nombre"]} : {user["puestos"]} puesto(s)"
)

st.header(f"Numero de telefono: {user["telefono"]}")

st.divider()

cols_tab = st.columns(2)

with cols_tab[0]:
    st.table(user["tabla1"])

with cols_tab[1]:
    st.table(user["tabla2"])

cols_1 = st.columns(2)

with cols_1[0]:
    cuotas_a_pagar: int = st.selectbox(
        "Numero de cuotas a pagar:", range(user["cuotas"] + 1)
    )

with cols_1[1]:
    multas_a_pagar: int = st.selectbox(
        "Numero de multas a pagar:", range(user["multas"] + 1)
    )


cols_2 = st.columns(2, vertical_alignment="bottom")

with cols_2[0]:
    modo_de_pago: str = st.selectbox("Modo de pago:", ("Efectivo", "Transferencia"))

if cols_2[1].button("Iniciar proceso de pago"):
    boton_iniciar_pago = fc.rectificar_boton_iniciar_pago(
        cuotas_a_pagar, multas_a_pagar, index
    )
    if not boton_iniciar_pago[0]:
        st.toast(boton_iniciar_pago[1], icon="🚨")
    else:
        st.balloons()
        fc.formulario_de_pago(index, cuotas_a_pagar, multas_a_pagar, modo_de_pago, user)

st.divider()
if st.button("Ver ultimo cheque"):
    webbrowser.open_new("./src/text/cheque.pdf")

if not st.session_state.admin:
    st.stop()

st.divider()

st.subheader("🔒 Cuotas a (des)bloquear")

bloc_col = st.columns(2, vertical_alignment="bottom")

with bloc_col[0]:
    sem_bloc: int = st.selectbox("Semanas que desea (des)bloquear:", range(1, 51))

with bloc_col[1]:
    if st.button("(Des)Bloquear"):
        fc.des_bloquear_semanas(index, sem_bloc)
        st.rerun()
