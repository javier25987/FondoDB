import sqlite3 as sql
import pandas as pd


def buscar_nombre(nombre: str) -> pd.DataFrame:
    conexion = sql.connect("Fondo.db")
    querry: str = f"""
        SELECT
            ig.id,
            ig.nombre,
            ig.telefono,
            ig.estado
        From informacion_general ig
        WHERE ig.nombre LIKE '%{nombre}%'
    """
    datos = pd.read_sql_query(querry, conexion)
    conexion.close()

    return datos # lambda x: "✅ activo" if bool(x) else "🚨 desactivado", datos[3])


def tabla_acuerdo() -> pd.DataFrame:
    conexion = sql.connect("Fondo.db")
    querry: str = """
    SELECT
        c.id AS Id, 
        ig.nombre AS Nombre,
        c.pago AS Pago,
        c.retirado AS Retirado,
        c.pago/2 AS Necesario_Retirar
    FROM capital c 
    JOIN informacion_general ig
    ON c.id = ig.id
    WHERE c.retirado < c.pago/2
    """

    df = pd.read_sql_query(querry, conexion)
    conexion.close()

    return df


def rectificar_numero(boleta_a_buscar: str) -> bool:
    if boleta_a_buscar == "":
        return False

    return True


def buscar_boleta(rifa_a_buscar: str, boleta_a_buscar: str) -> pd.DataFrame:
    conexion = sql.connect("Fondo.db")

    query: str = f"""
        SELECT ig.id, ig.nombre, br.boleta
        FROM {rifa_a_buscar} br
        JOIN informacion_general ig 
        ON br.dada_a = ig.id 
        WHERE br.boleta LIKE '%{boleta_a_buscar}%'
    """

    df: pd.DataFrame = pd.read_sql_query(query, conexion)
    conexion.close()

    df.rename({
        "id": "Puesto",
        "nombre": "Nombre",
        "boleta": "Boleta"
    })

    return df


def mostrar_todas_boletas(rifa_a_buscar: str) -> pd.DataFrame:
    query = f"""
    SELECT 
        ig.id AS ID,
        ig.nombre AS Nombre,
        br.boleta AS Boleta
    FROM {rifa_a_buscar} br 
    JOIN informacion_general ig 
    ON br.dada_a = ig.id
    """
    
    with sql.connect("Fondo.db") as conexion:
        df = pd.read_sql_query(query, conexion)

    return df
