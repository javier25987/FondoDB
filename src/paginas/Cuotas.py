import funciones.general as fg
import funciones.cuotas as fc
import streamlit as st
import pandas as pd
import os

ajustes: dict = fg.abrir_ajustes()
banco: dict = fg.abrir_banco()
df = pd.read_csv(ajustes["nombre df"])

if ajustes["calendario"] == "n":
    st.info("El calendario aun no ha sido creado", icon="ℹ️")
    st.stop()

index: int = st.session_state.usuario_actual_cuotas

index_de_usuario: int = st.sidebar.number_input("Numero de usuario:", value=0, step=1)
if st.sidebar.button("Buscar"):
    estado: list[bool, str] = fc.abrir_usuario(index_de_usuario, ajustes, df)
    if estado[0]:
        st.session_state.usuario_actual_cuotas = index_de_usuario
        st.rerun()
    else:
        st.error(estado[1], icon="🚨")

if index == -1:
    st.title("Usuario indeterminado")
    st.stop()

nombre_usuario: str = df["nombre"][index].title()
st.title(
    f"№ {index} - {df['nombre'][index].title()} : {df['puestos'][index]} puesto(s)"
)

tabs = st.tabs(["Pagar cuotas y multas", "Pagos por transferencia", "Anotaciones"])

with tabs[0]:
    st.header(f"Numero de telefono: {df['numero celular'][index]}")

    st.divider()
    # fc.escribir_cuotas_y_multas(index, ajustes, df)
    # st.divider()

    df1, df2 = fc.tablas_para_cuotas_y_multas(index, ajustes, df)
    col2_1, col2_2 = st.columns(2)

    with col2_1:
        st.table(df1)

    with col2_2:
       st.table(df2)

    numero_cuotas_a_pagar: int = 50 - df["cuotas"][index].count("p")

    if numero_cuotas_a_pagar > 10:
        numero_cuotas_a_pagar = 10

    numero_multas_a_pagar: int = fc.contar_multas(df["multas"][index])

    cols_1 = st.columns(2)

    with cols_1[0]:
        cuotas_a_pagar: int = st.selectbox(
            "Numero de cuotas a pagar:", range(numero_cuotas_a_pagar + 1)
        )

        tesorero_a_pagar: str = st.selectbox("Tesorero:", ("1", "2", "3", "4"))

    with cols_1[1]:
        multas_a_pagar: int = st.selectbox(
            "Numero de multas a pagar:", range(numero_multas_a_pagar + 1)
        )

        modo_de_pago: str = st.selectbox(
            "Modo de pago:", ("Efecctivo", "Transferencia")
        )

    if cols_1[0].button("Iniciar proceso de pago"):
        if cuotas_a_pagar == 0 and multas_a_pagar == 0:
            st.error("No se que desea pagar", icon="🚨")
        else:
            st.balloons()
            fc.formulario_de_pago(
                index, cuotas_a_pagar, multas_a_pagar, tesorero_a_pagar,
                modo_de_pago, ajustes, banco, df,
            )

    st.divider()
    if st.button("Abrir ultimo cheque"):
        with st.spinner("Abriendo cheque..."):
            os.system("notepad.exe text/cheque_de_cuotas.txt")

with tabs[2]:
    st.subheader("Realizar una anotacion:")
    anotacion: str = st.text_input("Nueva anotacion:")

    if st.button("Realizar anotacion"):
        estado_anotacion: (bool, str) = fc.realizar_anotacion(
            index, anotacion, ajustes, df
        )
        if estado_anotacion[0]:
            st.rerun()
        else:
            st.error(estado_anotacion[1], icon="🚨")

    st.divider()
    st.subheader("Anotaciones hechas:")

    anotaciones: str = df["anotaciones de cuotas"][index].split("_")

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
                fc.modificar_anotacion(
                    index, pos_mod_anotacion, new_anotacion, ajustes, df
                )
                st.rerun()

        st.divider()
        st.subheader("Eliminar anotaciones:")

        cols_a_2 = st.columns(2, vertical_alignment="bottom")

        with cols_a_2[0]:
            pos_eli_anotacion: int = st.selectbox(
                "Anotacion que desea eliminar:", numero_de_anotaciones
            )
        with cols_a_2[1]:
            if st.button("Eliminar"):
                fc.eliminar_anotacion(index, pos_eli_anotacion, ajustes, df)
                st.rerun()

with tabs[1]:
    col2_3 = st.columns([4, 6], vertical_alignment="center")

    with col2_3[0]:
        st.caption(f"# ***{banco['dinero pagado']:,}***")

    with col2_3[1]:
        st.info(
            "Todo este dinero ha sido pagado por transferencia"
            " bancaria entre todos los respectivos usuarios",
            icon="ℹ️"
        )
    st.divider()

    col2_1 = st.columns([3, 5, 2], vertical_alignment="bottom")

    if st.session_state.buscar_banco:
        with col2_1[1]:
            buscar_usuario: int = st.number_input(
                "Buscar usuario:", value=0, step=1
            )

    with col2_1[0]:
        if not st.session_state.buscar_banco:
            mensaje_boton: str = "Buscar"
        else:
            mensaje_boton: str = "Ver todo"

        if st.button(mensaje_boton, key="mi boton"):
            st.session_state.buscar_banco = not st.session_state.buscar_banco
            st.rerun()

    st.divider()
    if st.session_state.buscar_banco:
        diccionario: dict = fc.buscar_transferencia(buscar_usuario, banco)
    else:
        diccionario: dict = banco

    for key_dict in diccionario:
        if key_dict in ("dinero pagado", "id"):
            continue

        st.markdown(
            f"""
            > ***{key_dict}***: 
            >      
            > **fecha:** {diccionario[key_dict]["fecha"]}  
            > **quien:** № {diccionario[key_dict]["quien"]} _ {df["nombre"][diccionario[key_dict]["quien"]].title()}  
            > **cuanto:** {diccionario[key_dict]["cuanto"]:,}  
            """
        )
