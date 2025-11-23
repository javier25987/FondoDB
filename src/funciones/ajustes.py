import src.funciones.prestamos as fp
import src.funciones.general as fg
import streamlit as st
import sqlite3 as sql
import pandas as pd
import datetime
import time


def crear_listado_de_fechas(primera_fecha: str, dobles: list[str]) -> str:
    """
    para este formato es obligatorio que las fechas esten en el formato
    anio/mes/dia/hora (la hora tiene que estar en formato 24 horas)
    """
    fecha = fg.string_a_fecha(primera_fecha) # type: ignore
    fechas = []

    i: int = 0
    while len(fechas) < 50:
        new_f = fecha + datetime.timedelta(days=7 * i)
        f_new = new_f.strftime("%Y/%m/%d/%H")
        if f_new in dobles:
            fechas.append(f_new)
        fechas.append(f_new)
        i += 1

    for i in dobles: # type: ignore
        if i not in fechas:
            return "n"

    return "_".join(fechas)


def avisar(rerun: bool = True):
    if rerun:
        st.success("Valor modificado", icon="✅")
        time.sleep(1)
        st.rerun()


def obtener_tabla_rifas():
    conexion = sql.connect("Fondo.db")
    cursor = conexion.cursor()

    cursor.execute("SELECT * FROM datos_de_rifas")

    datos = cursor.fetchall()
    conexion.close()

    dict_table = {
        "id": [],
        "numero_de_boletas": [],
        "premios": [],
        "costos_de_boleta": [],
        "costos_de_administracion": [],
        "ganancia_por_boleta": []
    }

    for _id, n_boletas, pemios, c_boleta, c_admis, g_boleta in datos:
        dict_table["id"].append(_id)
        dict_table["numero_de_boletas"].append(n_boletas)
        dict_table["premios"].append(pemios)
        dict_table["costos_de_boleta"].append(c_boleta)
        dict_table["costos_de_administracion"].append(c_admis)
        dict_table["ganancia_por_boleta"].append(g_boleta)

    return pd.DataFrame(dict_table)


def cargar_datos_de_rifa(
    numero_de_boletas: int, costo_de_boleta: int,
    costo_de_administracion: int, premios: list[int]
):
    suma_de_premios = sum(premios)
    ganancias_por_boleta = (numero_de_boletas * costo_de_boleta) - (
        costo_de_administracion + suma_de_premios
    )
    ganancias_por_boleta /= numero_de_boletas
    ganancias_por_boleta = int(ganancias_por_boleta)

    premios = "_".join([str(i) for i in premios]) # type: ignore

    _id: int = 1

    conexion = sql.connect("Fondo.db")
    cursor = conexion.cursor()

    cursor.execute("SELECT MAX(id) FROM datos_de_rifas")

    _id: int = cursor.fetchall()[0][0]

    if _id is None:
        _id = 0

    _id += 1

    cursor.execute(
        f"""
        INSERT INTO datos_de_rifas (
            id, numero_de_boletas, premios, costo_de_boleta,
            costos_de_administracion, ganancia_por_boleta 
        ) VALUES (
            {_id}, {numero_de_boletas}, '{premios}', {costo_de_boleta},
            {costo_de_administracion}, {ganancias_por_boleta}
        )
        """
    )

    conexion.commit()
    conexion.close()

    st.success("Datos cargados", icon="✅")
    time.sleep(1)
    st.rerun()


def cerrar_una_rifa():
    """
    Esta funcion mira todas las deudas vigentes en la tabla `deudas_rifa`
    y las carga como un prestamo a cada usuario, 
    """

    # obtener todas las deudas mayores a cero

    conexion = sql.connect("Fondo.db")
    cursor = conexion.cursor()

    cursor.execute("SELECT * FROM deudas_rifa WHERE deuda > 0")

    datos = cursor.fetchall()

    # hacer todos los prestamos

    for idx, deuda in datos:
        fp.escribir_prestamo(idx, deuda, "BOLETAS",[], [])

    # limpiar toda la tabla de `deudas_rifa`\

    cursor.execute("UPDATE deudas_rifa SET deuda = 0")

    conexion.commit()
    conexion.close()

    