import pandas as pd
import sqlite3 as sql


def buscar_nombre(nombre: str) -> pd.DataFrame:
    conexion = sql.connect("Fondo.db")
    cursor = conexion.cursor()

    cursor.execute(
        f"""
        SELECT
            ig.id,
            ig.nombre,
            ig.telefono,
            ig.estado
        From informacion_general ig
        WHERE ig.nombre LIKE '%{nombre}%'
        """
    )

    datos = cursor.fetchall()
    conexion.close()

    if not datos:
        return pd.DataFrame({})

    datos = list(zip(*datos))

    datos[3] = map(lambda x: "✅ activo" if bool(x) else "🚨 desactivado", datos[3])

    resultado = {
        "Numero": datos[0],
        "Nombre": datos[1],
        "telefono": datos[2],
        "estado": datos[3],
    }

    return pd.DataFrame(resultado)


def tabla_acuerdo() -> pd.DataFrame:
    conexion = sql.connect("Fondo.db")
    cursor = conexion.cursor()

    cursor.execute(
        """
        SELECT
            ig.id,
            ig.nombre,
            ig.capital,
            p.dinero_por_si_mismo
        From informacion_general ig
        JOIN prestamos p
        ON
            ig.id = p.id
        WHERE
            p.dinero_por_si_mismo < ig.capital/2
        """
    )

    datos = cursor.fetchall()
    conexion.close()

    datos = list(zip(*datos))

    datos[2] = map(lambda x: f"{x:,}", datos[2])
    datos[3] = map(lambda x: f"{x:,}", datos[3])

    resultado = {
        "Numero": datos[0],
        "Nombre": datos[1],
        "Capital": datos[2],
        "Dinero por si mismo": datos[3],
    }

    return pd.DataFrame(resultado)


def rectificar_numero(boleta_a_buscar: str, poscion_boleta: str) -> bool:
    if boleta_a_buscar == "":
        return False

    return True


def buscar_boleta(rifa_a_buscar: str, boleta_a_buscar: str):
    conexion = sql.connect("Fondo.db")
    cursor = conexion.cursor()

    cursor.execute(
        f"""
        SELECT ig.id, ig.nombre, br.boleta
        FROM {rifa_a_buscar} br
        JOIN informacion_general ig 
        ON br.dada_a = ig.id 
        WHERE br.boleta LIKE '%{boleta_a_buscar}%'
        """
    )

    datos = cursor.fetchall()
    conexion.close()

    tabla = {
        "Puesto": [],
        "Nombre": [],
        "Boleta": []
    }

    for p, n, b in datos:
        tabla["Puesto"].append(p)
        tabla["Nombre"].append(n)
        tabla["Boleta"].append(b)

    return pd.DataFrame(tabla)


def mostrar_todas_boletas(rifa_a_buscar: str) -> pd.DataFrame:
    query = f"SELECT ig.id, ig.nombre, br.boleta FROM {rifa_a_buscar} br JOIN informacion_general ig ON br.dada_a = ig.id"
    
    with sql.connect("Fondo.db") as conexion:
        df = pd.read_sql_query(query, conexion)

    if df.empty:
        return pd.DataFrame()
    
    # Renombrar columnas si quieres mantener nombres personalizados
    df.columns = ["Puesto", "Nombre", "Boleta"]
    return df
