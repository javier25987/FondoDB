import sqlite3 as sql

def solicitar_registro(mes: int) -> dict:
    conexion = sql.connect("Fondo.db")
    cursor = conexion.cursor()

    cursor.execute(
        f"""
        SELECT
            STRFTIME('%d', fecha),
            ingreso,
            egreso
        FROM registros
        WHERE STRFTIME('%m', fecha) = '{str(mes) if mes > 9 else f"0{mes}"}'
        """
    )

    datos = cursor.fetchall()
    conexion.close()

    datos = list(zip(*datos))

    result = {
        "fechas": list(map(int, datos[0])),
        "ingesos": datos[1],
        "egresos": datos[2]
    }

    return result
