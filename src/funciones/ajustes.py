import src.funciones.general as fg
import src.funciones.prestamos as fp
import src.sql.conect as c_sql
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
    fecha = fg.string_a_fecha(primera_fecha)
    fechas = []

    i: int = 0
    while len(fechas) < 50:
        new_f = fecha + datetime.timedelta(days=7 * i)
        f_new = new_f.strftime("%Y/%m/%d/%H")
        if f_new in dobles:
            fechas.append(f_new)
        fechas.append(f_new)
        i += 1

    for i in dobles:
        if i not in fechas:
            return "n"

    return "_".join(fechas)


def avisar(rerun: bool = True):
    if rerun:
        st.success("Valor modificado", icon="✅")
        time.sleep(1)
        st.rerun()


def crear_tablas_rifas(rifa: str) -> list:
    conexion = sql.connect("Fondo.db")
    cursor = conexion.cursor()

    cursor.execute(
        f"""
        SELECT *
        FROM datos_de_rifas
        WHERE id = 'r{rifa}'
        """
    )

    datos = cursor.fetchall()[0]

    conexion.close()

    return [
        pd.DataFrame(
            {
                "Numero de boletas": [f"{datos[2]:,}"],
                "Numeros por boleta": [f"{datos[3]:,}"],
                "Boletas por talonario": [f"{datos[6]:,}"],
            }
        ),
        pd.DataFrame(
            {
                "Costo de boleta": [f"{datos[5]:,}"],
                "Costos de administracion": [f"{datos[7]:,}"],
                "Ganancias por boleta": [f"{datos[8]:,}"],
            }
        ),
        pd.DataFrame({"Fecha de cierre": [datos[9]]}),
        pd.DataFrame(
            {
                "Premios": map(
                    lambda x: f"{int(x):,}" if x not in {"n", "", None} else x,
                    datos[4].split("_"),
                )
            }
        ),
    ]


def cargar_datos_de_rifa(
    rifa: str,
    numero_de_boletas: int,
    numeros_por_boleta: int,
    boletas_por_talonario: int,
    costo_de_boleta: int,
    costo_de_administracion: int,
    fecha_de_cierre,
    premios: list[int],
) -> None:
    suma_de_premios = sum(premios)
    ganancias_por_boleta = (numero_de_boletas * costo_de_boleta) - (
        costo_de_administracion + suma_de_premios
    )
    ganancias_por_boleta /= numero_de_boletas
    ganancias_por_boleta = int(ganancias_por_boleta)

    premios = "_".join([str(i) for i in premios])

    conexion = sql.connect("Fondo.db")
    cursor = conexion.cursor()

    cursor.execute(
        f"""
        UPDATE datos_de_rifas
        SET 
            numero_de_boletas = ?, numeros_por_boleta = ?,
            premios = ?, costo_de_boleta = ?, 
            boletas_por_talonario = ?, costos_de_administracion = ?,
            ganancia_por_boleta = ?, fecha_de_cierre = ?
        WHERE rid = 'r{rifa}'
        """,
        (
            numero_de_boletas,
            numeros_por_boleta,
            premios,
            costo_de_boleta,
            boletas_por_talonario,
            costo_de_administracion,
            ganancias_por_boleta,
            fecha_de_cierre.strftime("%Y/%m/%d"),
        ),
    )

    conexion.commit()
    conexion.close()

    st.success("Datos cargados", icon="✅")
    time.sleep(1)
    st.rerun()


def cerrar_una_rifa(rifa: str):
    """
    aca estoy haciendo la rectificacion y el proceso de una en ves de usar 2 funciones
    """

    if not bool(c_sql.obtener_datos_rifas(rifa, "estado")):
        return False, "La rifa no esta activa"

    fecha_de_cierre = fg.string_a_fecha(
        c_sql.obtener_datos_rifas(rifa, "fecha_de_cierre")
    )

    if fecha_de_cierre > datetime.datetime.now():
        return False, "No se cumple la fecha de cierre"

    conexion = sql.connect("Fondo.db")
    cursor = conexion.cursor()

    cursor.execute(
        f"""
        SELECT id, r{rifa}_deudas
        FROM rifas
        WHERE r{rifa}_deudas > 0

        """
    )

    datos = cursor.fetchall()

    for i in datos:
        fp.escribir_prestamo(i[0], i[1], [], [])

        st.toast(f"💵 Se genero un prestamo por {i[1]:,}para el usuario № {i[0]}")

    cursor.execute(
        f"""
        UPDATE datos_de_rifas
        SET estado = 0
        WHERE id = 'r{rifa}'
        """
    )

    conexion.commit()
    conexion.close()

    return True, "Rifa cerrada correctamente"
