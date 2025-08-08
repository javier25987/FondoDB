# import src.funciones.general as fg
import src.sql.conect as c_sql
import src.funciones.rifas as fr
import streamlit as st

key: int = 0

index = st.session_state.usuario

index_de_usuario = st.sidebar.number_input("Numero de usuario:", value=0, step=1)
if st.sidebar.button("Buscar"):
    estado: tuple[bool, str] = fr.abrir_usuario(index_de_usuario)
    if estado[0]:
        st.session_state.usuario = index_de_usuario
        st.rerun()
    else:
        st.error(estado[1], icon="🚨")

if index == -1:
    st.title("Usuario indeterminado")
    st.stop()

st.title(f"№ {index} - {c_sql.obtener_ig('nombre', index).title()}")

tabs = st.tabs(["Rifa Actual", "Rifa 1"])

with tabs[0]:
    cols_act = st.columns(2)

    with cols_act[0]:
        boletas_selecionadas = st.multiselect(
            "boletas disponibles:", fr.consultar_boletas_libres(16, "1")
        )

        if st.button("Entregar boletas"):
            fr.entregar_boletas(index, boletas_selecionadas, "1")


with tabs[1]:
    boletas_1 = fr.consultar_boletas_usr(index, "1")
    cols_1 = st.columns(4)
    count_1 = 0

    for i in boletas_1:
        with cols_1[count_1 % 4]:
            st.markdown(f"#### `{i}`")
        count_1 += 1

# st.title("🚨 La rifa no esta activa")
