import src.funciones.anotaciones as fa
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

user = fa.obtener_datos(index)

st.title(f"№ {index} - {user["nombre"]}")

st.subheader("Realizar una anotacion:")

anotacion: str = st.text_input("Nueva anotacion:")

cols_2: st.columns = st.columns([5, 3, 2], vertical_alignment="bottom")

with cols_2[0]:
    monto_anotacion: int = st.number_input("Monto de la anotacion:", value=0, step=1)

with cols_2[1]:
    motivo: str = st.selectbox(
        "Motivo de la anotacion:", ("GENERAL", "MONETARIA")
    )

with cols_2[2]:
    if st.button("Realizar anotacion"):
        estado_anotacion: tuple[bool, str] = fa.certificar_anotacion(
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

deuda_actual: int = user["multas"]

st.markdown(f"> ##### multas extras: {deuda_actual:,}")

tabs = st.tabs(["Generales", "Monetarias"])

for tab, tipo in zip(tabs, ("general", "monetaria")):
    with tab:
        for anotacion in fa.obtener_anotaciones(index, tipo):
            st.markdown(f"+ {anotacion}")
