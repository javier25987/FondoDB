# import src.funciones.general as fg
import src.sql.conect as c_sql
import src.funciones.rifas as fr
import streamlit as st

key = 0

rifa_actual: str = "boletas_rifa_2"

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

    # 
    with cols_act[0]:
        st.subheader("Entrega de boletas:")

        boletas_selecionadas = st.multiselect(
            "boletas disponibles:", fr.consultar_boletas_libres(-1, rifa_actual)
        )

        if st.button("Entregar boletas"):
            if len(boletas_selecionadas) != 0:
                st.balloons()
                fr.entregar_boletas(index, boletas_selecionadas, rifa_actual)
            else:
                st.toast("No hay boletas", icon="🚨")

    with cols_act[1]:
        st.subheader("Pagos por boletas:")

        total_adeudado = c_sql.obtener_valor("deudas_rifa", "deuda", index)

        total_a_pagar = st.number_input(
            "Cantidad que desea pagar:",
            step=1, value=0
        )

        if st.button("Pagar"):
            estado_pago = fr.rectificar_pago(index, total_a_pagar, total_adeudado)

            if estado_pago[0]:
                fr.formlario_de_pago(index, total_a_pagar, total_adeudado)
            else:
                st.toast(estado_pago[1], icon="🚨")

    st.markdown(f"#### Deuda actual: `{total_adeudado:,}`")

    st.divider()

    boletas_act = fr.consultar_boletas_usr(index, rifa_actual)
    cols_act = st.columns(4)
    count_act = 0

    for i in boletas_act:
        with cols_act[count_act % 4]:
            st.markdown(f"#### `{i}`")
        count_act += 1


with tabs[1]:
    boletas_1 = fr.consultar_boletas_usr(index, "boletas_rifa_1")
    cols_1 = st.columns(4)
    count_1 = 0

    for i in boletas_1:
        with cols_1[count_1 % 4]:
            st.markdown(f"#### `{i}`")
        count_1 += 1



# st.title("🚨 La rifa no esta activa")
