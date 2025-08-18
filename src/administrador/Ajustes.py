import src.funciones.ajustes as fa
import src.sql.conect as c_sql
import streamlit as st
import pandas as pd
import os

from datetime import datetime

st.title("Ajustes")

tab = list(
    st.tabs(
        [
            "Calendario", "Cuotas y multas", "Contraseñas",
            "Prestamos", "Usuarios", "Fechas",
            "Guardado de datos", "Rifas"
        ]
    )
)

key: int = 1

with tab[0]:
    st.header("Calendario:")

    calendario: str = c_sql.obtener_ajuste("calendario", False)

    if calendario == "n":
        st.error("No hay un calendario", icon="🚨")
        st.subheader("Crear calendario:")
    else:
        calendario: list[str] = calendario.split("_")
        hora_de_corte: str = calendario[1][-2:]
        calendario = list(map(lambda x: x[:-3], calendario))
        # calendario += ['____/__/__']

        st.markdown(f"##### Hora de cierre: {hora_de_corte}")
        st.table(
            pd.DataFrame(
                {
                    "1 ~ 10": calendario[:10],
                    "11 ~ 20": calendario[10:20],
                    "21 ~ 30": calendario[20:30],
                    "31 ~ 40": calendario[30:40],
                    "41 ~ 50": calendario[40:],
                }
            )
        )
        st.subheader("Modificar calendario:")

    col0 = st.columns(4)

    with col0[0]:
        n_hora: int = st.number_input("Hora de cierre: ", value=19, step=1)

    with col0[1]:
        n_fecha_inicial = st.date_input("Fecha inicial: ")
    with col0[2]:
        cantidad_dobles: int = st.number_input("Fechas dobles:", value=1, step=1)
    with col0[3]:
        for f in range(1, cantidad_dobles + 1):
            st.date_input(f"Fecha doble № {f}:", key=f"fecha_{f}")

    if st.button("Crear calendario", key=f"key: {key}"):
        n_hora: str = str(n_hora)

        n_fecha_inicial: str = n_fecha_inicial.strftime("%Y/%m/%d") + "/" + n_hora

        fechas_dobles: list[str] = [
            st.session_state[f"fecha_{x}"].strftime("%Y/%m/%d") + "/" + n_hora
            for x in range(1, cantidad_dobles + 1)
        ]

        if len(set(fechas_dobles)) != len(fechas_dobles):
            st.error("Hay fechas dobles repetidas", icon="🚨")
        else:
            c_sql.guardar_ajuste_t(
                "calendario",
                fa.crear_listado_de_fechas(
                    n_fecha_inicial, fechas_dobles
                )
            )
            fa.avisar()
    key += 1

    st.divider()

    col0_1 = st.columns(2)

    with col0_1[0]:
        st.subheader("Eliminar calendario:")

    with col0_1[1]:
        if st.button("Eliminar calendario", key=f"key: {key}"):
            c_sql.guardar_ajuste_t("calendario", "n")
            fa.avisar()
        key += 1

with tab[1]:
    st.header("Valor de la cuota por puesto y por multa:")

    st.markdown(
        "> **NOTA:** por favor no ingrese comas o puntos separadores de miles"
    )  # icon="ℹ️"

    col1 = st.columns(2)

    with col1[0]:
        st.subheader("Por puesto:")

        st.write(
            f"Valor de la cuota por puesto: {c_sql.obtener_ajuste("valor cuota"):,}"
        )

        n_cuota_puesto = st.number_input(
            "Nuevo valor de la cuota:", value=10000, step=1
        )

        if st.button("Modificar", key=f"key: {key}"):
            c_sql.guardar_ajuste("valor cuota", n_cuota_puesto)
            fa.avisar()
        key += 1

    with col1[1]:
        st.subheader("Por multa:")
        st.write(
            f"Valor de la multa por puesto: {c_sql.obtener_ajuste("valor multa"):,}"
        )
        n_cuota_multa = st.number_input("Nuevo valor de la multa:", value=3000, step=1)

        if st.button("Modificar", key=f"key: {key}"):
            c_sql.guardar_ajuste("valor multa", n_cuota_multa)
            fa.avisar()
        key += 1

with tab[2]:
    col2 = st.columns(2)

    with col2[0]:
        st.subheader("Contraseña actual: ")

        st.caption(f"# {c_sql.obtener_ajuste("clave acceso", False)}")

    with col2[1]:
        nueva_clave = st.text_input("Nueva contraseña:")

        if st.button("Modificar", key=f"key: {key}"):
            c_sql.guardar_ajuste_t("clave acceso", nueva_clave)
            fa.avisar()
        key += 1

with tab[3]:
    st.markdown("## Tope de intereses:")

    st.markdown(
        """
        > **NOTA:** el tope de intereses determina que interes va
        a tener un prestamo dependiendo si pasa el tope o no
        """
    )
    col3_1 = st.columns(2)

    with col3_1[0]:
        st.markdown(f"##### Tope actual: {c_sql.obtener_ajuste("tope intereses"):,}")

    with col3_1[1]:
        nuevo_tope: int = st.number_input("Nuevo tope:", value=20000000, step=1)
        if st.button("Modificar", key=f"key: {key}"):
            c_sql.guardar_ajuste("tope intereses", nuevo_tope)
            fa.avisar()
        key += 1
    st.divider()
    st.markdown("## Interes por prestamo:")

    st.markdown(
        """
        > **NOTA:** los intereses son un numero entero entre 0 y 100
        por favor no introduzca numeros decimales, el programa no los
        puede trabajar bien y puede generar errores en el futuro
        """
    )
    col3_2 = st.columns(2)

    with col3_2[0]:
        st.markdown("### Menos de el tope:")
        st.markdown(
            f"##### el interes actual por prestamo es: {
                c_sql.obtener_ajuste("interes m tope")
            } %"
        )
    with col3_2[1]:
        nuevo_interes_m_tope: int = st.number_input(
            "Nuevo interes menor a el tope:", value=3, step=1
        )
        if st.button("Modificar", key=f"key: {key}"):
            c_sql.guardar_ajuste("interes m tope", nuevo_interes_m_tope)
            fa.avisar()
        key += 1
        st.divider()

    col3_3 = st.columns(2)

    with col3_3[0]:
        st.markdown("### Mas de el tope:")
        st.markdown(
            f"##### el interes actual por prestamo es: {
                c_sql.obtener_ajuste("interes M tope")
            } %"
        )
    with col3_3[1]:
        nuevo_interes_M_tope: int = st.number_input(
            "Nuevo interes mayor a el tope:", value=2, step=1
        )
        if st.button("Modificar", key=f"key: {key}"):
            c_sql.guardar_ajuste("interes M tope", nuevo_interes_M_tope)
            fa.avisar()
        key += 1

    st.divider()

    st.markdown("## Capital usable para solicitud:")

    col3_4 = st.columns(2)

    with col3_4[0]:
        st.markdown(
            f"##### Actual mente se puede usar un `{
                c_sql.obtener_ajuste("capital usable")
            }%` del capital guardado."
        )

        st.markdown(
            "> **NOTA:** el nuevo valor debe ingresarse como un "
            "numero de 1 a 100 que representa el porcentage no "
            "introduzca simbolos extra, comas o puntos ya que"
            " esto puede afectar al programa"
        )

    with col3_4[1]:
        nuevo_capital_usable: int = st.number_input(
            "Nuevo capital usable [...]%:", value=2, step=1
        )

        if st.button("Modificar", key=f"key: {key}"):
            c_sql.guardar_ajuste("capital usable", nuevo_capital_usable)
            fa.avisar()
        key += 1

with tab[4]:
    st.header("Usuarios:")

    col4_1 = st.columns(2)

    with col4_1[0]:
        st.markdown("### Numero de usuarios:")

        st.write(f"actualmete en el programa hay [ {
            c_sql.obtener_ajuste("usuarios")
        } ] usuarios")
    with col4_1[1]:
        nuevo_usuarios: int = st.number_input(
            "Nuevo numero de usuarios:", value=0, step=1
        )
        if st.button("Modificar", key=f"key: {key}"):
            c_sql.guardar_ajuste("usuarios", nuevo_usuarios)
            fa.avisar()
        key += 1
    st.divider()

    col4_2 = st.columns(2)

    with col4_2[0]:
        st.subheader("Desactivar usuarios:")
        desactivar_usuarios: bool = bool(c_sql.obtener_ajuste("anular usuarios"))
        if desactivar_usuarios:
            st.write("Los usuarios seran desactivados")
        else:
            st.write("Los usuarios NO seran desactivados")

        if st.button("Invertir", key=f"key: {key}"):
            c_sql.guardar_ajuste(
                "anular usuarios", int(not desactivar_usuarios)
            )
            fa.avisar()
        key += 1

    with col4_2[1]:
        st.subheader("Cobrar multas:")
        cobrar_multas: bool = bool(c_sql.obtener_ajuste("cobrar multas"))
        if cobrar_multas:
            st.write("Actualmente se generan multas")
        else:
            st.write("Actualmete NO se generan multas")

        if st.button("Invertir", key=f"key: {key}"):
            c_sql.guardar_ajuste(
                "cobrar multas", int(not cobrar_multas)
            )
            fa.avisar()
        key += 1

with tab[5]:
    col5 = st.columns(2)

    with col5[0]:
        st.subheader("Fecha de cierre: ")

        st.write(f"fecha de cierre actual: {
            c_sql.obtener_ajuste("fecha de cierre", False)
        }")

    with col5[1]:
        n_fecha: datetime = st.date_input("Nueva fecha de cierre:")

        if st.button("Modificar", key=f"key: {key}"):
            c_sql.guardar_ajuste_t(
                "fecha de cierre", n_fecha.strftime("%Y/%m/%d")
            )
            fa.avisar()
        key += 1

    st.markdown(
        """
        > **NOTA:** la fecha de cierre es la que dice hasta cuando hay
        plazo de pagar los prestamos, todas las fechas de pago de un 
        prestamo se generan hasta la fecha de cierre
        """
    )

with tab[6]:
    col7_1 = st.columns(2, vertical_alignment="center")

    with col7_1[0]:
        st.subheader("Ruta de el programa: ")
        st.write(f"Ruta de el programa: {
            c_sql.obtener_ajuste("path programa", False)
        }")

    with col7_1[1]:
        if st.button("Configurar path", key=f"key: {key}"):
            print("path: ", os.getcwd())
            c_sql.guardar_ajuste_t("path programa", os.getcwd())
            fa.avisar()
        key += 1
    st.divider()

    col7_2 = st.columns(2)

    with col7_2[0]:
        st.subheader("Enlace de el repositorio")
        st.write(f"Enlace actual: {c_sql.obtener_ajuste("enlace repo", False)}")

    with col7_2[1]:
        n_enlace: str = st.text_input("Nuevo enlace:")

        if st.button("Modificar", key=f"key: {key}"):
            c_sql.guardar_ajuste_t("enlace repo", n_enlace)
            fa.avisar()
        key += 1
    st.divider()

    col7_3 = st.columns(2)

    with col7_3[0]:
        st.subheader("Commits hechos")
        st.write(f"Commits realizados: {c_sql.obtener_ajuste("commits hechos")}")

    with col7_3[1]:
        n_comits: int = st.number_input("Nuevos commits:", value=0, step=1)

        if st.button("Modificar", key=f"key: {key}"):
            c_sql.guardar_ajuste("commits hechos", n_comits)
            fa.avisar()
        key += 1

with tab[7]:
    n_rifas = ("1", "2", "3", "4")
    st.header("Ver rifas:")
    tab_8 = st.tabs(["Rifa 1", "Rifa 2", "Rifa 3", "Rifa 4"])
    count: int = 0
    for i in n_rifas:
        with tab_8[count]:
            for j in fa.crear_tablas_rifas(i):
                st.table(j)
        count += 1

    st.divider()
    st.header("Modificar rifas:")

    col8_1 = st.columns(3)

    with col8_1[0]:
        r_numero_de_boletas: int = st.number_input(
            "Numero de boletas:", step=1, value=0
        )
        r_costo_de_boleta: int = st.number_input("Costo por boleta:", value=0, step=1)

    with col8_1[1]:
        r_numeros_por_boleta: int = st.number_input(
            "Numeros por boleta:", step=1, value=0
        )
        r_costos_de_administracion: int = st.number_input(
            "Costos de administracion:", step=1, value=0
        )

    with col8_1[2]:
        r_boletas_por_talonario: int = st.number_input(
            "Boletas por talonario:", value=0, step=1
        )
        r_fecha_de_cierre = st.date_input("Fecha de cierre:")

    for i in range(1, r_numeros_por_boleta + 1):
        with col8_1[(i - 1) % 3]:
            st.number_input(f"Premio № {i}:", value=0, step=1, key=f"premio: {i}")

    col8_2 = st.columns(2, vertical_alignment="bottom")

    with col8_2[0]:
        st.divider()
        r_rifa = st.selectbox("Rifa que desea modificar:", n_rifas)

    with col8_2[1]:
        if st.button("Modificar rifa"):
            premios: list[int] = []
            for i in range(1, r_numeros_por_boleta + 1):
                premios.append(st.session_state[f"premio: {i}"])
            fa.cargar_datos_de_rifa(
                r_rifa, r_numero_de_boletas, r_numeros_por_boleta,
                r_boletas_por_talonario, r_costo_de_boleta,
                r_costos_de_administracion, r_fecha_de_cierre,
                premios,
            )
    st.divider()
    st.header("(Des)Activar rifas:")

    for i, j in zip(st.columns(4), n_rifas):
        with i:
            st.subheader(f"Rifa {j}:")
            if c_sql.obtener_datos_rifas(j,"estado"):
                st.write(f"La rifa {j} esta activa")
            else:
                st.write(f"La rifa {j} NO esta activa")

            if st.button("Modificar", key=f"key: {key}"):
                c_sql.guardar_valor(
                    "datos_de_rifas",
                    "estado",
                    f"r{j}",
                    not bool(c_sql.obtener_datos_rifas(j, "estado"))
                )
                fa.avisar()
            key += 1

    st.divider()
    st.header("Cerrar rifas:")
    
    for i, j in zip(st.columns(4), n_rifas):
        with i:
            st.subheader(f"Rifa {j}:")
            if st.button("Cerrar rifa", key=f"key: {key}"):
                cerrar_rifa = fa.cerrar_una_rifa(j)

                if cerrar_rifa[0]:
                    st.toast(cerrar_rifa[1], icon="✅")
                else:
                    st.toast(cerrar_rifa[1], icon="🚨")
                    
            key += 1
