import funciones.modificarsocios as fm
import funciones.general as fg
import streamlit as st
import pandas as pd

st.title("Modificar Usuarios")

ajustes: dict = fg.abrir_ajustes()
df = pd.read_csv(ajustes["nombre df"])

key: int = 0

tabs = st.tabs(["Ver datos", "Modificar datos", "Añadir usuario"])

with tabs[0]:
    col1 = st.columns(2)

    with col1[0]:
        datos: str = st.selectbox(
            "Datos que desea ver:",
            ("TODO", "informacion general", "pago de cuotas", "rifas", "prestamos"),
        )
    with col1[1]:
        if datos == "prestamos":
            lista_elecciones: list[str] = ["TODAS"] + [
                f"ranura {i}" for i in range(1, 17)
            ]

            prestamo: str = st.selectbox("Ranura(s) que desea ver:", lista_elecciones)
    match datos:
        case "TODO":
            st.table(df)
        case "informacion general":
            st.table(
                df[
                    [
                        "numero",
                        "nombre",
                        "puestos",
                        "numero celular",
                        "estado",
                        "capital",
                        "aporte a multas",
                        "multas extra",
                        "anotaciones generales",
                    ]
                ]
            )
        case "pago de cuotas":
            st.table(
                df[
                    [
                        "numero",
                        "nombre",
                        "cuotas",
                        "multas",
                        "tesorero",
                        "revisiones",
                        "anotaciones de cuotas",
                    ]
                ]
            )
        case "rifas":
            st.table(
                df[
                    [
                        "numero",
                        "nombre",
                        "r1 boletas",
                        "r1 deudas",
                        "r2 boletas",
                        "r2 deudas",
                        "r3 boletas",
                        "r3 deudas",
                        "r4 boletas",
                        "r4 deudas",
                        "anotaciones de rifas",
                    ]
                ]
            )
        case "prestamos":
            if prestamo == "TODAS":
                lista_columnas: list[str] = [
                    "numero",
                    "nombre",
                    "prestamos hechos",
                    "dinero en prestamos",
                    "dinero por si mismo",
                    "dinero por intereses vencidos",
                ]
                for i in range(1, 17):
                    lista_columnas += [
                        f"p{i} estado",
                        f"p{i} prestamo",
                        f"p{i} fechas de pago",
                    ]
                lista_columnas += [
                    "deudas por fiador",
                    "fiador de",
                    "anotaciones de prestamos",
                ]
                st.table(df[lista_columnas])
            else:
                ranura: str = int(prestamo[-2:])
                st.table(
                    df[
                        [
                            "numero",
                            "nombre",
                            "prestamos hechos",
                            "dinero en prestamos",
                            "dinero por si mismo",
                            f"p{ranura} estado",
                            f"p{ranura} prestamo",
                            f"p{ranura} fechas de pago",
                            "deudas por fiador",
                            "fiador de",
                            "anotaciones de prestamos",
                        ]
                    ]
                )

with tabs[2]:
    st.header("Datos de el nuevo usuario:")

    col5 = st.columns([6, 4])

    with col5[0]:
        nombre: str = st.text_input("Nombre:")
        telefono: str = st.text_input("Numero celular:")
        puestos: int = st.number_input("Numero de puestos:", value=0, step=1)
        if st.button("Añadir"):
            paso_1: bool = False
            paso_2: bool = False

            if nombre == "":
                st.error("El nombre de usuario no puede estar vacio", icon="🚨")
            else:
                paso_1 = True

            if puestos < 1:
                st.error("Para que un usuario tendria menos de un puesto?", icon="🚨")
            else:
                paso_2 = True

            if paso_1 and paso_2:
                fm.menu_para_insertar_socio(ajustes, df, nombre, puestos, telefono)

    with col5[1]:
        st.table(df[["numero", "nombre", "puestos"]][::-1])

with tabs[1]:
    st.header("Modificar datos:")

    col4_1 = st.columns([4, 1, 5], vertical_alignment="center")

    with col4_1[0]:
        index_modificar: int = st.number_input(
            "Numero de el usuario que desea modificar:", value=0, step=1
        )
        index_modificar: int = abs(index_modificar)
        if index_modificar >= ajustes["usuarios"]:
            st.error("El numero de usuario esta fuera de rango", icon="🚨")
            st.stop()

    with col4_1[2]:
        st.caption(f"# **{df['nombre'][index_modificar]}**")
        st.divider()

    col4_2 = st.columns(2)

    with col4_2[0]:
        seccion_modificar: str = st.selectbox(
            "Seccion que desea modificar: ",
            ("Informacion General", "Cuotas", "Rifas", "Prestamos"),
        )
        st.divider()

    with col4_2[1]:
        match seccion_modificar:
            case "Informacion General":
                columna_modificar: str = st.selectbox(
                    "Columna a modificar:",
                    (
                        "nombre",
                        "puestos",
                        "numero celular",
                        "estado",
                        "capital",
                        "aporte a multas",
                    ),
                    key=f"key: {key}",
                )
                key += 1
            case "Cuotas":
                columna_modificar: str = st.selectbox(
                    "Columna a modificar:",
                    (
                        "cuotas",
                        "multas",
                        "revisiones",
                    ),
                    key=f"key: {key}",
                )
                key += 1
            case "Rifas":
                columna_modificar: str = st.selectbox(
                    "Columna a modificar:",
                    ("r1 deudas", "r2 deudas", "r3 deudas", "r4 deudas"),
                    key=f"key: {key}",
                )
                key += 1
            case "Prestamos":
                columna_modificar: str = st.selectbox(
                    "Columna a modificar:",
                    (
                        "prestamos hechos",
                        "dinero en prestamos",
                        "dinero por si mismo",
                        "dinero por intereses vencidos",
                        # "prestamo en ranura",
                        "deudas por fiador",
                        "fiador de",
                    ),
                    key=f"key: {key}",
                )
                key += 1
            case _:
                st.error("Me temo que hay un error", icon="🚨")

    # with col4_2[2]:
    #     if columna_modificar == "prestamo en ranura":
    #         ranura_modificar: str = st.selectbox(
    #             "Ranura que desea modificar:",
    #             (map(str, range(1, 17)))
    #         )

    columnas_texto: list[str] = [
        "nombre",
        "numero celular",
        "fiador de",
    ]

    columnas_numeros: list[str] = [
        "capital",
        "puestos",
        "aporte a multas",
        "revisiones",
        "r1 deudas",
        "r2 deudas",
        "r3 deudas",
        "r4 deudas",
        "prestamos hechos",
        "dinero en prestamos",
        "dinero por si mismo",
        "deudas por fiador",
        "dinero por intereses vencidos",
    ]

    columnas_especiales: list[str] = [
        "cuotas",
        "multas",
        "estado",  # "prestamo en ranura"
    ]

    if columna_modificar in columnas_texto:
        col4_3 = st.columns(2)

        with col4_3[0]:
            st.write(f"#### Valor actual de la columna '{columna_modificar}': ")
            st.caption(f"### **{df[columna_modificar][index_modificar]}**")

        with col4_3[1]:
            nuevo_valor_texto: str = st.text_input(
                "Nuevo valor de la columna:", key=f"key: {key}"
            )
            key += 1

            if st.button("Modificar", key=f"key: {key}"):
                fm.modificar_columna(
                    index_modificar, columna_modificar, nuevo_valor_texto, ajustes, df
                )
                st.rerun()
            key += 1

    elif columna_modificar in columnas_numeros:
        col4_4 = st.columns(2)

        with col4_4[0]:
            st.write(f"#### Valor actual de la columna '{columna_modificar}': ")
            st.caption(f"### **{df[columna_modificar][index_modificar]:,}**")

        with col4_4[1]:
            nuevo_valor_numero: str = st.number_input(
                "Nuevo valor de la columna:", value=0, step=1, key=f"key: {key}"
            )
            key += 1

            if st.button("Modificar", key=f"key: {key}"):
                fm.modificar_columna(
                    index_modificar, columna_modificar, nuevo_valor_numero, ajustes, df
                )
                st.rerun()
            key += 1

    elif columna_modificar in columnas_especiales:
        match columna_modificar:
            case "multas":
                col4_5 = st.columns(2)

                with col4_5[0]:
                    st.write("#### Multas que tiene el usuario: ")
                    st.caption(f"## **{fm.contar_multas(index_modificar, df)}**")

                with col4_5[1]:
                    usuario_multas: str = df["multas"][index_modificar]
                    multas_modificar: int = st.number_input(
                        "Multas que desea añadir o quitar:", value=0, step=1
                    )
                    col4_6 = st.columns(2)

                    with col4_6[0]:
                        if st.button("Añadir multas"):
                            fm.modificar_columna(
                                index_modificar,
                                columna_modificar,
                                fm.sumar_multas(usuario_multas, multas_modificar),
                                ajustes,
                                df,
                            )
                            st.rerun()

                    with col4_6[1]:
                        if st.button("Quitar multas"):
                            fm.modificar_columna(
                                index_modificar,
                                columna_modificar,
                                fm.restar_multas(usuario_multas, multas_modificar),
                                ajustes,
                                df,
                            )
                            st.rerun()

            case "cuotas":
                col4_7 = st.columns(2)
                usuario_cuotas: str = df["cuotas"][index_modificar]

                with col4_7[0]:
                    st.write("#### Cuotas pagas: ")
                    st.caption(f"## **{df['cuotas'][index_modificar].count('p')}**")

                with col4_7[1]:
                    cuotas_modificar: int = st.number_input(
                        "Cuotas pagas que desea añadir o quitar:", value=0, step=1
                    )
                    col4_8 = st.columns(2)

                    with col4_8[0]:
                        if st.button("Añadir cuotas"):
                            fm.modificar_columna(
                                index_modificar,
                                columna_modificar,
                                fm.sumar_cuotas(usuario_cuotas, cuotas_modificar),
                                ajustes,
                                df,
                            )
                            st.rerun()

                    with col4_8[1]:
                        if st.button("Quitar cuotas"):
                            fm.modificar_columna(
                                index_modificar,
                                columna_modificar,
                                fm.quitar_cuotas(usuario_cuotas, cuotas_modificar),
                                ajustes,
                                df,
                            )
                            st.rerun()
                    st.divider()

                col4_9 = st.columns(2)

                with col4_9[0]:
                    st.write("#### Cuotas adeudadas: ")
                    st.caption(f"## **{df['cuotas'][index_modificar].count('d')}**")

                with col4_9[1]:
                    deudas_modificar: int = st.number_input(
                        "Cuotas adeudadas que desea añadir o quitar:", value=0, step=1
                    )
                    col4_10 = st.columns(2)

                    with col4_10[0]:
                        if st.button("Añadir deudas"):
                            fm.modificar_columna(
                                index_modificar,
                                columna_modificar,
                                fm.sumar_deudas(usuario_cuotas, deudas_modificar),
                                ajustes,
                                df,
                            )
                            st.rerun()

                    with col4_10[1]:
                        if st.button("Quitar deudas"):
                            fm.modificar_columna(
                                index_modificar,
                                columna_modificar,
                                fm.quitar_deudas(usuario_cuotas, deudas_modificar),
                                ajustes,
                                df,
                            )
                            st.rerun()
            case "estado":
                col4_11 = st.columns(2, vertical_alignment="center")

                with col4_11[0]:
                    st.write("#### Estado actual de el usuario: ")
                    st.caption(f"### **{df['estado'][index_modificar]}**")

                with col4_11[1]:
                    if df["estado"][index_modificar] == "activo":
                        new_estado = "no activo"
                        mensaje_1 = "Desactivar"
                    else:
                        new_estado = "activo"
                        mensaje_1 = "Activar"

                    if st.button(mensaje_1):
                        fm.modificar_columna(
                            index_modificar, columna_modificar, new_estado, ajustes, df
                        )
                        st.rerun()

    st.divider()
    st.subheader("Cosas a tener en cuenta:")
    st.markdown(
        """
        > No se puede eliminar la cantidad de talonarios entregados
        y los numeros en los talonarios no pueden ser modificados, 
        puesto que reescribir los datos por este metodo puede generar 
        errores a futuro y lo mejor es prevenir errores.
        """
    )
