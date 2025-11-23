import sqlite3 as sql
import pandas as pd

def insert_boleta(numeros: list, nombre_tabla: str):
    primer_numero = int(numeros[0])
    boleta_str = "_".join(numeros)

    conexion = sql.connect("Fondo.db")
    cursor = conexion.cursor()

    cursor.execute(
        f"""
        INSERT INTO {nombre_tabla} (idx, boleta, dada_a) VALUES (?, ?, ?)
        """, 
        (primer_numero, boleta_str, -1)
    )

    conexion.commit()
    conexion.close()


def consultar_boletas_rifa(nombre_tabla: str):
    query: str = f"""
    SELECT 
        tb.idx AS Id
        tb.boleta AS Boleta
        tb.dada_a AS Dada_a
    FROM {nombre_tabla} tb
    """

    with sql.connect("Fondo.db") as conexion:
        df = pd.read_sql_query(query, conexion)

    return df


def rectificar_boleta(boletas) -> bool:
    for i in boletas:
        if i == "":
            return False
        
        try:
            int(i)
        except ValueError:
            return False
        
        numero = int(i)
        
        if 0 > numero or numero > 1000:
            return False
        
    return True


def eliminar_boleta(boleta: int, rifa_eliminar: str):
    connexion = sql.connect("Fondo.db")
    cursor = connexion.cursor()

    cursor.execute(f"DELETE FROM {rifa_eliminar} WHERE idx = {boleta}")

    connexion.commit()
    connexion.close()


    