import src.funciones.anotaciones as fa
import src.funciones.general as fg
import streamlit as st
import pandas as pd

index: int = st.session_state.usuario_actual_anotaciones

index_de_usuario: int = st.sidebar.number_input("Numero de usuario.", value=0, step=1)

if st.sidebar.button("Buscar", key="00011"):
    estado: (bool, str) = fa.ingresar_usuario(index_de_usuario) # type: ignore
    if estado[0]:
        st.session_state.usuario_actual_anotaciones = index_de_usuario
        st.rerun()
    else:
        st.error(estado[1], icon="🚨")

if index == -1:
    st.title("Usuario indeterminado")
    st.stop()

st.title(f"№ {index} - {df['nombre'][index].title()}")

st.subheader("Realizar una anotacion:")

cols_1: st.columns = st.columns([0.8, 0.2]) # type: ignore
with cols_1[0]:
    anotacion: str = st.text_input("Nueva anotacion:")
with cols_1[1]:
    motivo: str = st.selectbox(
        "Motivo de la anotacion:", ("GENERAL", "MULTA", "ACUERDO")
    )

cols_2: st.columns = st.columns([0.5, 0.2, 0.3], vertical_alignment="bottom") # type: ignore
with cols_2[0]:
    monto_anotacion: int = st.number_input("Monto de la anotacion:", value=0, step=1)
with cols_2[1]:
    if st.button("Realizar anotacion"):
        estado_anotacion: (bool, str) = fa.realizar_anotacion( # type: ignore
            index, anotacion, monto_anotacion, motivo, ajustes, df
        )
        if estado_anotacion[0]:
            st.rerun()
        else:
            st.toast(estado_anotacion[1], icon="🚨")
with cols_2[2]:
    st.info("Para mas informacion lea abajo", icon="ℹ️")

st.divider()
st.subheader("Anotaciones hechas:")

anotaciones: str = df["anotaciones generales"][index].split("_")

count: int = 0
for i in anotaciones:
    st.markdown(f"> **№ {count}:** {i}")
    count += 1

st.markdown(f"> ##### Total de anotaciones: {df['multas extra'][index]:,}")
st.divider()
st.markdown(
    """
    > ℹ️ NOTA: este apartado esta hecho para:
    > * almacenar posibles deudas de un socio 
    > * cargar multas al sistema
    > * pagar el acuerdo de prestamos
    >
    > en el apartado de "motivo de la anotacion" se especifica esto,
    > tenga en cuenta que los apartados de "MULTA" y "ACUERDO" suman
    > a la columna de multas (a la ganancia final del fondo que se
    > reparte entre todos) asi que si es una anotacion venidera que no 
    > influye en las ganancias finales incluyala como "GENERAL".
    """
)
