import src.sql.conect as c_sql
import sqlite3 as sql
import pandas as pd


def mostrar_transferencias_todo():
    conexion = sql.connect("Fondo.db")
    cursor = conexion.cursor()

    cursor.execute(
        """
        SELECT *
        From transferencias
        """
    )

    datos = cursor.fetchall()

    conexion.close()

    datos = list(zip(*datos))

    nombres = [
        c_sql.obtener_ig("nombre", i) for i in datos[0]
    ]

    datos[2] = map(lambda x: f"{x:,}", datos[2])

    resultado = {
        "Numero": datos[0],
        "Nombre": nombres,
        "Fecha y Hora": datos[1],
        "Monto": datos[2]
    }

    return pd.DataFrame(resultado)


def obtener_usuarios() -> tuple[int, ...]:
    conexion = sql.connect("Fondo.db")
    cursor = conexion.cursor()

    cursor.execute(
        """
        SELECT DISTINCT id
        From transferencias
        ORDER BY id
        """
    )

    datos = cursor.fetchall()

    conexion.close()

    return [i[0] for i in datos]

def mostrar_transferencias(index: int):
    conexion = sql.connect("Fondo.db")
    cursor = conexion.cursor()

    cursor.execute(
        f"""
        SELECT *
        From transferencias
        WHERE id = {index}
        """
    )

    datos = cursor.fetchall()

    conexion.close()

    datos = list(zip(*datos))

    nombres = [
        c_sql.obtener_ig("nombre", i) for i in datos[0]
    ]

    datos[2] = map(lambda x: f"{x:,}", datos[2])

    resultado = {
        "Numero": datos[0],
        "Nombre": nombres,
        "Fecha y Hora": datos[1],
        "Monto": datos[2]
    }

    return pd.DataFrame(resultado)