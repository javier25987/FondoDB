import sqlite3 as sql
import polars as pl


def mostrar_transferencias_todo():
    conexion = sql.connect("Fondo.db")
    querry: str = """
    SELECT 
        t.id,
        ig.nombre,
        t.fecha,
        t.monto
    FROM transferencias t 
    JOIN informacion_general ig 
    ON t.id = ig.id 
    """

    datos = pl.read_database(querry, conexion)
    conexion.close()

    return datos


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

    datos = pl.read_database(querry, conexion)
    conexion.close()

    return datos
