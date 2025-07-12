import streamlit as st
import src.sql.conect as c_sql
import pandas as pd
import datetime


def abrir_usuario(index: int) -> (bool, str):
    if 0 > index >= c_sql.obtener_ajuste("usuarios"):
        return False, "El numero de usuario esta fuera de rango"

    return True, ""


@st.dialog("Entrega de talonario")
def cargar_talonario(index: int, rifa: str):
    st.header(
        f"№ {index} - {c_sql.obtener_ig("nombre", index).title()}"
    )
    st.divider()

    columnas: int = c_sql.obtener_datos_rifas(rifa, "numeros_por_boleta")
    filas: int = c_sql.obtener_datos_rifas(rifa, "boletas_por_talonario")

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

        c_sql.increment_str(
            "rifas", f"r{rifa}_boletas", index, talonario
        )

        deuda_talo = (
            c_sql.obtener_datos_rifas(rifa, "costo_de_boleta") *
            c_sql.obtener_datos_rifas(rifa, "boletas_por_talonario")
        )

        c_sql.increment(
            "rifas", f"r{rifa}_deudas", index, deuda_talo
        )

        st.rerun()


@st.dialog("Pago de boletas")
def pago_de_boletas(index: int, pago: int, rifa: str):
    st.header(
        f"№ {index} - {c_sql.obtener_ig("nombre", index).title()}"
    )
    st.divider()

    deuda_act: int = c_sql.obtener_rifas(f"r{rifa}_deudas", index)

    st.write(f"Deuda por boletas: {deuda_act:,}")
    st.write(f"Pago que se realiza: {pago:,}")

    st.subheader(f"Deuda restante: {deuda_act - pago:,}")
    st.divider()

    if st.button("Aceptar pago"):
        c_sql.increment(
            "rifas", f"r{rifa}_deudas", index, -pago
        )

        # ACA SE TIENE QUE PONER LA FUNCION PARA LA ANOTACION

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
