import src.funciones.general as fg
import src.sql.conect as c_sql
import src.funciones.rifas as fr
import streamlit as st
import pandas as pd

key: int = 0

index = st.session_state.usuario_actual_rifas

index_de_usuario = st.sidebar.number_input("Numero de usuario:", value=0, step=1)
if st.sidebar.button("Buscar"):
    estado: tuple[bool, str] = fr.abrir_usuario(index_de_usuario)
    if estado[0]:
        st.session_state.usuario_actual_rifas = index_de_usuario
        st.rerun()
    else:
        st.error(estado[1], icon="🚨")

if index == -1:
    st.title("Usuario indeterminado")
    st.stop()

st.title(
    f"№ {index} - {c_sql.obtener_ig("nombre", index).title()}"
)

tabs = st.tabs(["Rifa 1", "Rifa 2", "Rifa 3", "Rifa 4"])
rifas: list[str] = ["1", "2", "3", "4"]

for i, j in zip(tabs, rifas):
    with i:
        if bool(c_sql.obtener_datos_rifas(j, "estado")):
            cols = st.columns(2)

            with cols[0]:
                st.header("Entregar talonarios:")
                if st.button("Entregar talonario", key=f"key: {key}"):
                    fr.cargar_talonario(index, j)
                key += 1

            with cols[1]:
                st.header("Deudas en boletas:")
                deuda_act: int = c_sql.obtener_rifas(f"r{j}_deudas", index)
                st.write(f"Deudas en boletas: {deuda_act:,}")
                n_pago: int = st.number_input(
                    "Pago por boletas:", step=1, value=0, key=f"key: {key}"
                )
                key += 1

                if st.button("Pagar", key=f"key: {key}"):
                    if deuda_act <= 0:
                        st.error("No entiendo que desea pagar", icon="🚨")
                    else:
                        if n_pago > deuda_act:
                            st.error(
                                "No se puede pagar mas de lo que se debe", icon="🚨"
                            )
                        elif n_pago <= 0:
                            st.error("No se puede pagar cero o menos", icon="🚨")
                        else:
                            fr.pago_de_boletas(index, n_pago, j)
                key += 1

            st.divider()

            st.header("Talonarios entregados:")
            boletas: str = c_sql.obtener_rifas(f"r{j}_boletas", index)
            if boletas == "n":
                st.subheader("🚨 No se han entregado boletas")
            else:
                count_t = 0
                talonarios: list = fr.crear_tablas_talonarios(boletas)
                for l_boleta in talonarios:
                    st.text(f"talonario: {count_t}")
                    st.table(l_boleta)
                    count_t += 1
        else:
            # st.title("Rifas")
            st.title("🚨 La rifa no esta activa")
