import funciones.general as fg
import funciones.rifas as fr
import streamlit as st
import pandas as pd

ajustes: dict = fg.abrir_ajustes()
df = pd.read_csv(ajustes["nombre df"])
key: int = 0

index = st.session_state.usuario_actual_rifas

index_de_usuario = st.sidebar.number_input("Numero de usuario:", value=0, step=1)
if st.sidebar.button("Buscar"):
    estado: tuple[bool, str] = fr.abrir_usuario(index_de_usuario, ajustes, df)
    if estado[0]:
        st.session_state.usuario_actual_rifas = index_de_usuario
        st.rerun()
    else:
        st.error(estado[1], icon="🚨")

if index == -1:
    st.title("Usuario indeterminado")
    st.stop()

st.title(f"№ {index} - {df['nombre'][index].title()}")

tabs = st.tabs(["Rifa 1", "Rifa 2", "Rifa 3", "Rifa 4", "Anotaciones"])
rifas: list[str] = ["1", "2", "3", "4"]

for i, j in zip(tabs[:-1], rifas):
    with i:
        if ajustes[f"r{j} estado"]:
            cols = st.columns(2)
            with cols[0]:
                st.header("Entregar talonarios:")
                if st.button("Entregar talonario", key=f"key: {key}"):
                    fr.cargar_talonario(index, j, ajustes, df)
                key += 1

            with cols[1]:
                st.header("Deudas en boletas:")
                deuda_act: int = df[f"r{j} deudas"][index]
                st.write(f"Deudas en boletas: {'{:,}'.format(deuda_act)}")
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
                            fr.pago_de_boletas(index, n_pago, j, ajustes, df)
                key += 1

            st.divider()

            st.header("Talonarios entregados:")
            boletas: str = df[f"r{j} boletas"][index]
            if boletas == "n":
                st.subheader("🚨 No se han entregado boletas")
            else:
                talonarios: list = fr.crear_tablas_talonarios(boletas)
                for l_boleta in talonarios:
                    st.table(l_boleta)
        else:
            st.title("Rifas")
            st.title("🚨 La rifa no esta activa")

with tabs[4]:
    st.subheader("Realizar una anotacion:")
    anotacion: str = st.text_input("Nueva anotacion:")

    if st.button("Realizar anotacion"):
        estado_anotacion: (bool, str) = fr.realizar_anotacion(
            index, anotacion, ajustes, df
        )
        if estado_anotacion[0]:
            st.rerun()
        else:
            st.error(estado_anotacion[1], icon="🚨")

    st.divider()
    st.subheader("Anotaciones hechas:")

    anotaciones: str = df["anotaciones de rifas"][index].split("_")

    count: int = 0
    numero_de_anotaciones: list[int] = []
    for i in anotaciones:
        st.markdown(f"> **№ {count}:** {i}")
        numero_de_anotaciones.append(count)
        count += 1

    if ajustes["mostrar MyE"]:
        st.divider()

        st.subheader("Modificar anotaciones:")
        new_anotacion: str = st.text_input("Nueva anotacion modificada:")
        cols_a_1 = st.columns(2, vertical_alignment="bottom")

        with cols_a_1[0]:
            pos_mod_anotacion: int = st.selectbox(
                "Anotacion que desea modificar:", numero_de_anotaciones
            )
        with cols_a_1[1]:
            if st.button("Modificar"):
                if st.session_state.admin:
                    fr.modificar_anotacion(
                        index, pos_mod_anotacion, new_anotacion, ajustes, df
                    )
                    st.rerun()
                else:
                    fg.advertencia()

        st.divider()
        st.subheader("Eliminar anotaciones:")

        cols_a_2 = st.columns(2, vertical_alignment="bottom")

        with cols_a_2[0]:
            pos_eli_anotacion: int = st.selectbox(
                "Anotacion que desea eliminar:", numero_de_anotaciones
            )
        with cols_a_2[1]:
            if st.button("Eliminar"):
                if st.session_state.admin:
                    fr.eliminar_anotacion(index, pos_eli_anotacion, ajustes, df)
                    st.rerun()
                else:
                    fg.advertencia()
