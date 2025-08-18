import sqlite3 as sql


def fechas_disponibles() -> list:
    conexion = sql.connect("Fondo.db")
    cursor = conexion.cursor()
    cursor.execute("SELECT DISTINCT(a.fecha) FROM apuntes a")
    datos = cursor.fetchall()
    conexion.close()

    return list(map(lambda x: x[0], datos))


def consultar_anotaciones(fecha: str) -> list:
    conexion = sql.connect("Fondo.db")
    cursor = conexion.cursor()
    cursor.execute(f"SELECT * FROM apuntes WHERE fecha = '{fecha}'")
    datos = cursor.fetchall()
    conexion.close()

    return datos