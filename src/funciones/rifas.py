import streamlit as st
import pandas as pd
import datetime


def abrir_usuario(index: int, ajustes: dict, df) -> (bool, str):
    if 0 > index >= ajustes["usuarios"]:
        return False, "El numero de usuario esta fuera de rango"
    if df["estado"][index] != "activo":
        return False, f"El usuario № {index} no esta activo"

    return True, ""


@st.dialog("Entrega de talonario")
def cargar_talonario(index: int, rifa: str, ajustes: dict, df):
    st.header(f"№ {df['numero'][index]}: {df['nombre'][index].title()}")
    st.divider()

    columnas: int = ajustes[f"r{rifa} numeros por boleta"]
    filas: int = ajustes[f"r{rifa} boletas por talonario"]

    l_col: list[str] = [str(i) for i in range(1, columnas + 1)]
    l_fil: list[str] = [str(i) for i in range(1, filas + 1)]

    for i in l_fil:
        st.write(f"Boleta № {i} de el talonario:")
        for col_j, j in zip(st.columns(columnas), l_col):
            with col_j:
                st.text_input(f"№ {j}", key=f"{i},{j}")
    st.divider()

    if st.button("Entregar talonario"):
        talonario: list[str] = []
        for i in l_fil:
            boleta = []
            for j in l_col:
                boleta.append(st.session_state[f"{i},{j}"])

            talonario.append("?".join(boleta))

        talonario = "#".join(talonario)

        boletas_act = df[f"r{rifa} boletas"][index]
        if boletas_act == "n":
            boletas_act = talonario
        else:
            boletas_act += f"_{talonario}"
        df.loc[index, f"r{rifa} boletas"] = boletas_act

        deuda_act = df[f"r{rifa} deudas"][index]
        deuda_act += (
            ajustes[f"r{rifa} costo de boleta"]
            * ajustes[f"r{rifa} boletas por talonario"]
        )
        df.loc[index, f"r{rifa} deudas"] = deuda_act

        df = df.loc[:, ~df.columns.str.contains("^Unnamed")]
        df.to_csv(ajustes["nombre df"])

        st.rerun()


@st.dialog("Pago de boletas")
def pago_de_boletas(index: int, pago: int, rifa: str, ajustes: dict, df):
    pago_anotacion: int = pago

    st.header(f"№ {df['numero'][index]}: {df['nombre'][index].title()}")
    st.divider()

    deuda_act = df[f"r{rifa} deudas"][index]

    st.write(f"Deuda por boletas: {deuda_act:,}")
    st.write(f"Pago que se realiza: {pago:,}")
    st.divider()

    if st.button("Aceptar pago"):
        deuda_act -= pago
        df.loc[index, f"r{rifa} deudas"] = deuda_act

        anotacion: str = (
            f" ( {datetime.datetime.now().strftime('%Y/%m/%d - %H:%M')} ) "
            f"Se pago {pago_anotacion:,} pesos en talonarios de la rifa № "
            f"{rifa}."
        )

        realizar_anotacion(index, anotacion, ajustes, df)

        st.rerun()


def crear_tablas_talonarios(boletas: str):
    talonarios: list = boletas.split("_")
    lista_r: list = []
    for i in talonarios:
        i_b = list(map(lambda x: x.split("?"), i.split("#")))
        dict_t: dict = dict()

        dict_t["Boletas"] = [f"Boleta № {k + 1}" for k in range(len(i_b))]

        i_b = list(map(list, zip(*i_b)))

        for j in range(len(i_b)):
            dict_t[f"№ {j + 1}"] = i_b[j]

        lista_r.append(pd.DataFrame(dict_t))

    return lista_r


def realizar_anotacion(
    index: int, anotacion: str, ajustes: dict, df
) -> tuple[bool, str]:
    anotaciones: str = df["anotaciones de rifas"][index]

    if "_" in anotacion:
        return False, "El simbolo '_' no puede estar en la anotacion"
    if anotacion == "":
        return False, "La anotacion esta vacia"

    if anotaciones == "n":
        anotaciones = anotacion
    else:
        anotacion = "_" + anotacion
        anotaciones += anotacion

    df.loc[index, "anotaciones de rifas"] = anotaciones

    df = df.loc[:, ~df.columns.str.contains("^Unnamed")]
    df.to_csv(ajustes["nombre df"])

    return True, ""


def eliminar_anotacion(index: int, pos: int, ajustes: dict, df):
    anotaciones: str = df["anotaciones de rifas"][index]
    anotaciones: list[str] = anotaciones.split("_")

    if len(anotaciones) == 1:
        anotaciones = "n"
    else:
        anotaciones.pop(pos)
        anotaciones = "_".join(anotaciones)

    df.loc[index, "anotaciones de rifas"] = anotaciones
    df = df.loc[:, ~df.columns.str.contains("^Unnamed")]
    df.to_csv(ajustes["nombre df"])


def modificar_anotacion(index: int, pos: int, new_elem: str, ajustes: dict, df):
    anotaciones: str = df["anotaciones de rifas"][index]
    anotaciones: list[str] = anotaciones.split("_")

    if new_elem == "":
        anotaciones[pos] = "n"
    elif "_" in new_elem:
        st.error("El simbolo '_' no puede estar en la anotacion", icon="🚨")
        return 0
    else:
        anotaciones[pos] = new_elem

    anotaciones = "_".join(anotaciones)

    df.loc[index, "anotaciones de rifas"] = anotaciones
    df = df.loc[:, ~df.columns.str.contains("^Unnamed")]
    df.to_csv(ajustes["nombre df"])
