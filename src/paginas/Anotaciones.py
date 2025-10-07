import src.funciones.anotaciones as fa
import src.sql.conect as c_sql
import streamlit as st
import time

index: int = st.session_state.usuario

index_de_usuario: int = st.sidebar.number_input("Numero de usuario.", value=0, step=1)

if st.sidebar.button("Buscar", key="00011"):
    estado = fa.abrir_usuario(index_de_usuario)
    if estado[0]:
        st.session_state.usuario = index_de_usuario
        st.rerun()
    else:
        st.error(estado[1], icon="🚨")

if index == -1:
    st.title("Usuario indeterminado")
    st.stop()

st.title(f"№ {index} - {c_sql.obtener_ig('nombre', index).title()}")

st.subheader("Realizar una anotacion:")

anotacion: str = st.text_input("Nueva anotacion:")

cols_2: st.columns = st.columns([5, 3, 2], vertical_alignment="bottom")  # type: ignore

with cols_2[0]:
    monto_anotacion: int = st.number_input("Monto de la anotacion:", value=0, step=1)

with cols_2[1]:
    motivo: str = st.selectbox(
        "Motivo de la anotacion:", ("GENERAL", "MONETARIA", "MULTA", "ACUERDO")
    )

with cols_2[2]:
    if st.button("Realizar anotacion"):
        estado_anotacion: (bool, str) = fa.certificar_anotacion(  # type: ignore
            anotacion, motivo, monto_anotacion, index
        )
        if estado_anotacion[0]:
            fa.realizar_anotacion(index, anotacion, monto_anotacion, motivo)
            st.toast("Anotacion hecha", icon="✅")
            time.sleep(1)
            st.rerun()
        else:
            st.toast(estado_anotacion[1], icon="🚨")
# with cols_2[2]:
#     st.info("Para mas informacion lea abajo", icon="ℹ️")

st.divider()

st.subheader("Anotaciones hechas:")

deuda_actual: int = c_sql.obtener_ig("multas_extra", index)

st.markdown(f"> ##### Deuda en anotaciones: {deuda_actual:,}")

tabs = st.tabs(["Generales", "Monetarias", "Multas", "Acuerdos"])

for i, j in zip(tabs, ("general", "monetaria", "multa", "acuerdo")):
    with i:
        for k in fa.obtener_anotaciones(index, j):
            st.markdown(f"> {k}")
