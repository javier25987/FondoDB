import src.funciones.deudas as fd
import streamlit as st

index: int = st.session_state.usuario

index_de_usuario: int = st.sidebar.number_input("Numero de usuario:", value=0, step=1)

if st.sidebar.button("Buscar"):
    estado: tuple[bool, str] = fd.abrir_usuario(index_de_usuario)
    if estado[0]:
        st.session_state.usuario = index_de_usuario
        st.rerun()
    else:
        st.toast(estado[1], icon="🚨")

if index == -1:
    st.title("Usuario indeterminado")
    st.stop()

user: dict = fd.obtener_datos_usuario(index)

st.title(f"№ {index} - {user["nombre"]}")
st.divider()

st.header("Crear deudas:")

motivo_create: str = st.text_input("Motivo de la deuda")

cols = st.columns([5, 1, 2, 1, 2], vertical_alignment="bottom")

with cols[0]:
    monto_create: int = st.number_input("Monto de la deuda:", value=0, step=1)

with cols[2]:
    is_multa: bool = st.toggle("Aportar a multas")

with cols[4]:
    if st.button("Crear"):
        estado: tuple[bool, str] = fd.rectificar_creacion(index, monto_create)

        if estado[0]:
            st.balloons()
            fd.formulario_de_crecion(index, motivo_create, monto_create, is_multa)
        else:
            st.toast(estado[1], icon="🚨")

st.divider()

st.header("Deudas hechas:")
for deuda in fd.obtener_deudas_usr(index):
    st.divider()
    st.subheader(f"codigo: {deuda["codigo"]}")

    cols = st.columns(2)

    with cols[0]:
        st.markdown(f"**Monto:** {deuda["monto"]:,}")
        st.markdown(f"**Fecha de creacion:** {deuda["creacion"]}")
        st.markdown(f"**Fecha de pago:** {deuda["pago"]}")


    with cols[1]:
        st.markdown(f"**Motivo:** {deuda["motivo"]}")

        if deuda["is_multa"]:
            st.info("Esta deuda aporta a multas", icon="ℹ️")

        if deuda["estado"]:
            st.success("Deuda Paga", icon=":material/check:")

    if not deuda["estado"]:
        if st.button(f"Pagar {deuda["codigo"]}"):
            fd.confirmar_pago(index, deuda)

