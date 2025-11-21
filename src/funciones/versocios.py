import sqlite3 as sql
import polars as pl


def buscar_nombre(nombre: str) -> pl.DataFrame:
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
    datos = pl.read_database(querry, conexion)
    conexion.close()

    return datos # lambda x: "✅ activo" if bool(x) else "🚨 desactivado", datos[3])


def tabla_acuerdo() -> pl.DataFrame:
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

    df = pl.read_database(querry, conexion)
    conexion.close()

    return df


def rectificar_numero(boleta_a_buscar: str) -> bool:
    if boleta_a_buscar == "":
        return False

    return True


def buscar_boleta(rifa_a_buscar: str, boleta_a_buscar: str) -> pl.DataFrame:
    conexion = sql.connect("Fondo.db")

    query: str = f"""
        SELECT ig.id, ig.nombre, br.boleta
        FROM {rifa_a_buscar} br
        JOIN informacion_general ig 
        ON br.dada_a = ig.id 
        WHERE br.boleta LIKE '%{boleta_a_buscar}%'
    """

    df: pl.DataFrame = pl.read_database(query, conexion)
    conexion.close()

    df.rename({
        "id": "Puesto",
        "nombre": "Nombre",
        "boleta": "Boleta"
    })

    return df


def mostrar_todas_boletas(rifa_a_buscar: str) -> pl.DataFrame:
    query = f"SELECT ig.id, ig.nombre, br.boleta FROM {rifa_a_buscar} br JOIN informacion_general ig ON br.dada_a = ig.id"
    
    with sql.connect("Fondo.db") as conexion:
        df = pl.read_database(query, conexion)

    if df.is_empty():
        return pl.DataFrame()
    
    # Renombrar columnas si quieres mantener nombres personalizados
    df.columns = ["Puesto", "Nombre", "Boleta"]
    return df
