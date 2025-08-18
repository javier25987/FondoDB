import pandas as pd


def fetchall_to_table(contenido, columnas):
    tabla = list(zip(*contenido))

    if len(tabla) != len(columnas):
        raise "las columnas y sus nombres no coinciden"

    resultado = {}

    for i in range(len(tabla)):
        resultado[columnas[i]] = tabla[i]

    return pd.DataFrame(resultado)
