import sqlite3 as sql
import pandas as pd


def mostrar_transferencias_todo():
    query: str = """
    SELECT 
        t.id,
        ig.nombre,
        t.fecha,
        t.monto
    FROM transferencias t 
    JOIN informacion_general ig 
    ON t.id = ig.id 
    """

    with sql.connect("Fondo.db") as conexion:
        df = pd.read_sql_query(query, conexion)

    return df


def obtener_usuarios() -> list[int]:
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
    querry: str = f"""
    SELECT 
        t.id,
        ig.nombre,
        t.fecha,
        t.monto
    FROM transferencias t 
    JOIN informacion_general ig 
    ON t.id = ig.id
    WHERE t.id = {index}
    """

    datos = pd.read_sql_query(querry, conexion)
    conexion.close()

    return datos
