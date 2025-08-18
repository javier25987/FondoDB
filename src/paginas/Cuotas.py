import src.funciones.cuotas as fc
import src.sql.conect as c_sql
import streamlit as st

if c_sql.obtener_ajuste("calendario", False) == "n":
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

nombre_usuario: str = c_sql.obtener_ig("nombre", index).title()

st.title(
    f"№ {index} - {nombre_usuario} : {c_sql.obtener_ig('puestos', index)} puesto(s)"
)

st.header(f"Numero de telefono: {c_sql.obtener_ig('telefono', index)}")

st.divider()

tablas_usr = fc.tablas_para_cuotas_y_multas(index)

for col, tab in zip(st.columns(2), tablas_usr):
    col.table(tab)

numero_cuotas_a_pagar = 50 - c_sql.obtener_cuotas("pagas", index)

if numero_cuotas_a_pagar > 10:
    numero_cuotas_a_pagar = 10

numero_multas_a_pagar: int = fc.contar_multas(c_sql.obtener_cuotas("multas", index))

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
    modo_de_pago: str = st.selectbox("Modo de pago:", ("Efectivo", "Transferencia"))

if cols_2[1].button("Iniciar proceso de pago"):
    boton_iniciar_pago = fc.rectificar_boton_iniciar_pago(
        cuotas_a_pagar, multas_a_pagar, index
    )
    if not boton_iniciar_pago[0]:
        st.toast(boton_iniciar_pago[1], icon="🚨")
    else:
        st.balloons()
        fc.formulario_de_pago(index, cuotas_a_pagar, multas_a_pagar, modo_de_pago)

st.divider()
if st.button("Solicitar ultimo cheque"):
    with open("src/text/cheque_de_cuotas.txt", "r", encoding="utf_8") as f:
        archivo = f.readlines()
        f.close()

    with open("src/text/index.txt", "w", encoding="utf_8") as f:
        f.write("".join(archivo))
        f.close()

    st.toast(
        "El documento ha sido creado, lo puede consultar en la seccion 'Documentos'",
        icon="✏️",
    )
