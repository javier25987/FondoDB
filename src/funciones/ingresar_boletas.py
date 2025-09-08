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


def consultar_boletas_rifa(nombre_tabla: str) -> list[str]:
    conexion = sql.connect("Fondo.db")
    cursor = conexion.cursor()

    cursor.execute(f"SELECT * FROM {nombre_tabla}")

    boletas = cursor.fetchall()
    conexion.close()

    if not boletas:
        return pd.DataFrame(), False
    
    numero = []
    boleta = []
    dada_a = []

    for i, j, k in boletas:
        numero.append(i)
        boleta.append(j)
        dada_a.append(k)

    return pd.DataFrame(
        {
            "Numero": numero,
            "Boleta": boleta,
            "Dada a": dada_a,
        }
    ), True


def rectificar_boleta(boletas) -> bool:
    for i in boletas:
        try:
            numero = int(i)
        except TypeError:
            return False
        
        if 0 > numero or numero > 1000:
            return False
        
    return True


def eliminar_boleta(boleta: int, rifa_eliminar: str):
    connexion = sql.connect("Fondo.db")
    cursor = connexion.cursor()

    cursor.execute(f"DELETE FROM {rifa_eliminar} WHERE idx = {boleta}")

    connexion.commit()
    connexion.close()


    