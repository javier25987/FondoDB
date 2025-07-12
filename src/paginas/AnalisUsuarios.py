import src.funciones.analis_usuarios as fa
import src.funciones.general as fg
import src.funciones.cuotas as fc
import streamlit as st
import pandas as pd
import datetime
import os

ajustes: dict = fg.abrir_ajustes()
df = pd.read_csv(ajustes["nombre df"])

index: int = st.session_state.usuario_actual_analis

index_de_usuario: int = st.sidebar.number_input("Numero de usuario:", value=0, step=1)
if st.sidebar.button("Buscar"):
    if 0 <= index_de_usuario < ajustes["usuarios"]:
        st.session_state.usuario_actual_analis = index_de_usuario
        st.rerun()
    else:
        st.toast("Usuario fuera de rango", icon="🚨")

tabs = st.tabs(["Informacion General", "Usuario En Concreto"])

with tabs[0]:
    st.title("Informacion general")
    st.markdown(f"> ### {datetime.datetime.now().strftime('%Y/%m/%d %H:%M')}")

    # obtener dinero adeudado en presamos

    dinero_adeudado_prestamos: int = 0

    for i in range(ajustes["usuarios"]):
        for j in range(1, 17):
            dinero_adeudado_prestamos += int(df[f"p{j} prestamo"][i].split("_")[3])

    # esto es para las opciones generales

    options: list[str] = [
        "Capital",
        "Pagos en multas",
        "Anotaciones generales",
        "Prestamos solicitados",
        "Dinero adeudado en prestamos",
        "Intereses generados",
    ]

    values: list[int] = [
        df["capital"].sum(),
        df["aporte a multas"].sum(),
        df["multas extra"].sum(),
        df["prestamos hechos"].sum(),
        dinero_adeudado_prestamos,
        df["dinero por intereses vencidos"].sum(),
    ]

    informacion_general = pd.DataFrame(
        {"Item": options, "Monto": [f"{x:,}" for x in values]}
    )
    st.table(informacion_general)

    st.divider()
    cols_1 = st.columns(2)
    TOTAL: int = 0

    with cols_1[0]:
        st.markdown("##### Valores a sumar:")
        valores_sumar = st.pills(
            "sumar:", options, key="de las bolas", selection_mode="multi"
        )
        if valores_sumar:
            for i in valores_sumar:
                TOTAL += values[options.index(i)]

    with cols_1[1]:
        st.markdown("##### Valores a restar:")
        valores_restar = st.pills(
            "restar:", options, key="las bolas de", selection_mode="multi"
        )
        if valores_restar:
            for i in valores_restar:
                TOTAL -= values[options.index(i)]

    st.markdown(f"> #### TOTAL = {TOTAL:,}")

with tabs[1]:
    if index == -1:
        st.title("Usuario indeterminado")
        st.stop()

    st.title(
        f"№ {index} - {df['nombre'][index].title()} : {df['puestos'][index]} puesto(s)"
    )
    st.markdown(f"> ### {datetime.datetime.now().strftime('%Y/%m/%d %H:%M')}")

    prestamos_activos: int = 0
    for i in range(1, 17):
        if df[f"p{i} estado"][index] != "activo":
            prestamos_activos += 1

    deudas_de_prestamos: int = 0
    for i in range(1, 17):
        deudas_de_prestamos += int(df[f"p{i} prestamo"][index].split("_")[3])

    usuario_options: list[str] = [
        "Cuotas pagas",
        "Cuotas que se deben",
        "Multas pendientes",
        "Estado",
        "Capital",
        "Dinero pagado en multas",
        "Multas extra",
        "Prestamos solitados",
        "Dinero retirado en prestamos",
        "Prestamos activos",
        "Deudas en prestamos",
        "Deudas por fiador",
        "Fiador de",
    ]
    usuario_values: list[int | str] = [
        df["cuotas"][index].count("p"),
        df["cuotas"][index].count("d"),
        fc.contar_multas(df["multas"][index]),
        df["estado"][index],
        df["capital"][index],
        df["aporte a multas"][index],
        df["multas extra"][index],
        df["prestamos hechos"][index],
        df["dinero en prestamos"][index],
        prestamos_activos,
        deudas_de_prestamos,
        df["deudas por fiador"][index],
        df["fiador de"][index],
    ]

    def funct(x: int | str) -> str:
        try:
            return f"{int(x):,}"
        except ValueError:
            return x

    st.table(
        pd.DataFrame(
            {
                "Concepto": usuario_options,
                "valor": [funct(x) for x in usuario_values],
            }
        )
    )

    st.divider()
    if st.button("Estado de cuenta"):
        with st.spinner("Obteniendo estado de cuenta..."):
            fa.obtener_estado_de_cuenta(
                index, prestamos_activos, deudas_de_prestamos, df
            )
            os.system("notepad.exe text/estado_de_cuenta.txt")
