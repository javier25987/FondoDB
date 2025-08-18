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

    if poscion_boleta is None:
        return False

    return True


def buscar_boleta(rifa_a_buscar: str, boleta_a_buscar: str, poscion_boleta: int):
    """
    esta funcion tan solo devuelve el usuario poeedor de la boleta
    :param rifa_a_buscar:
    :param boleta_a_buscar:
    :param poscion_boleta:
    :return:
    """
    conexion = sql.connect("Fondo.db")
    cursor = conexion.cursor()

    cursor.execute(
        f"""
            SELECT r.id, ig.nombre, r.r{rifa_a_buscar}_boletas
            From rifas r
            JOIN informacion_general ig
            ON
                ig.id = r.id
            WHERE 
                r.r{rifa_a_buscar}_boletas LIKE '%{boleta_a_buscar}%'
            """
    )

    datos = cursor.fetchall()
    conexion.close()

    datos = list(zip(*datos))

    if len(datos[0]) <= 0:
        return -1
    if len(datos[0]) == 1:
        return datos[0][0]

    for i in datos[0]:
        objetos: list[str] = datos[2][i].split("_")
        new_objetos: list = []

        for n in objetos:
            new_objetos += [m.split("?") for m in n.split("#")]

        for k in new_objetos:
            if k[poscion_boleta - 1] == boleta_a_buscar:
                return i

    return -1  # esto solo se activa si hay algun error


def mostrar_boletas(index: int, rifa_a_buscar: str) -> pd.DataFrame:
    conexion = sql.connect("Fondo.db")
    cursor = conexion.cursor()

    cursor.execute(
        f"""
        SELECT r.id, ig.nombre, r.r{rifa_a_buscar}_boletas
        From rifas r
        JOIN informacion_general ig
        ON
            ig.id = r.id
        WHERE
            r.id = {index}
        """
    )

    datos = cursor.fetchall()
    conexion.close()

    datos = list(zip(*datos))

    resultado = {"Numero": datos[0], "Nombre": datos[1], "Boletas": datos[2]}

    return pd.DataFrame(resultado)


def mostrar_boletas_todo(rifa_a_buscar: str) -> pd.DataFrame:
    conexion = sql.connect("Fondo.db")
    cursor = conexion.cursor()

    cursor.execute(
        f"""
            SELECT r.id, ig.nombre, r.r{rifa_a_buscar}_boletas
            From rifas r
            JOIN informacion_general ig
            ON
                ig.id = r.id
            """
    )

    datos = cursor.fetchall()
    conexion.close()

    datos = list(zip(*datos))

    resultado = {"Numero": datos[0], "Nombre": datos[1], "Boletas": datos[2]}

    return pd.DataFrame(resultado)
