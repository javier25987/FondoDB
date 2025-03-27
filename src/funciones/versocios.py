import pandas as pd
import sqlite3 as sql
import src.sql.to_table as to_t


def buscar_boleta(df, rifa_a_buscar: str, boleta_a_buscar: str, poscion_boleta: int):
    tabla_prueva = df[
        df[f"r{rifa_a_buscar} boletas"].str.contains(
            boleta_a_buscar, case=False, na=False
        )
    ]

    numeros = list(tabla_prueva["numero"])

    if len(numeros) <= 0:
        return -1
    if len(numeros) == 1:
        return numeros[0]

    for i in numeros:
        objetos: list[str] = df[f"r{rifa_a_buscar} boletas"][i].split("_")
        new_objetos: list = []

        for n in objetos:
            new_objetos += [m.split("?") for m in n.split("#")]

        for k in new_objetos:
            if k[poscion_boleta - 1] == boleta_a_buscar:
                return i

    return -1  # esto solo se activa si hay algun error


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
        "Dinero por si mismo": datos[3]
    }

    return pd.DataFrame(resultado)


def tabla_ranura() -> pd.DataFrame:
    conexion = sql.connect("Fondo.db")
    cursor = conexion.cursor()

    cursor.execute(
        """
        SELECT
            ig.id,
            ig.nombre,
            rp.p16_estado
        From informacion_general ig
        JOIN ranuras_p rp
        ON
            ig.id = rp.id
        """
    )

    datos = cursor.fetchall()
    conexion.close()

    datos = list(zip(*datos))

    datos[2] = map(
        lambda x: "✅ libre" if bool(x) else "🚨 ocupada",
        datos[2]
    )

    resultado = {
        "Numero": datos[0],
        "Nombre": datos[1],
        "Ranura": datos[2]
    }

    return pd.DataFrame(resultado)

