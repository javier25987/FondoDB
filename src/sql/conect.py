import sqlite3 as sql


def obtener_ig(colum: str, index: int) -> str | int:
    conexion = sql.connect("Fondo.db")
    cursor = conexion.cursor()

    cursor.execute(
        f"""
        SELECT {colum}
        FROM informacion_general
        WHERE id = {index}
        """
    )

    dato = cursor.fetchall()[0][0]
    conexion.close()

    return dato


def obtener_cuotas(colum: str, index: int) -> str | int:
    conexion = sql.connect("Fondo.db")
    cursor = conexion.cursor()

    cursor.execute(
        f"""
        SELECT {colum}
        FROM cuotas
        WHERE id = {index}
        """
    )

    dato = cursor.fetchall()[0][0]
    conexion.close()

    return dato


def obtener_rifas(colum: str, index: int) -> str | int:
    conexion = sql.connect("Fondo.db")
    cursor = conexion.cursor()

    cursor.execute(
        f"""
        SELECT {colum}
        FROM rifas
        WHERE id = {index}
        """
    )

    dato = cursor.fetchall()[0][0]
    conexion.close()

    return dato


def obtener_prestamos(colum: str, index: int) -> str | int:
    conexion = sql.connect("Fondo.db")
    cursor = conexion.cursor()

    cursor.execute(
        f"""
        SELECT {colum}
        FROM prestamos
        WHERE id = {index}
        """
    )

    dato = cursor.fetchall()[0][0]
    conexion.close()

    return dato


def obtener_ajuste(nombre: str, is_num: bool = True) -> str | int:
    conexion = sql.connect("Fondo.db")
    cursor = conexion.cursor()

    cursor.execute(
        f"""
        SELECT {"valor_n" if is_num else "valor_a"}
        FROM ajustes
        WHERE ajuste = '{nombre}'
        """
    )

    resultado = cursor.fetchall()[0][0]
    conexion.close()

    return resultado


def guardar_ajuste(nombre: str, nuevo_valor: int | str, is_num: bool = True) -> None:
    conexion = sql.connect("Fondo.db")
    cursor = conexion.cursor()

    cursor.execute(
        f"""
        UPDATE ajustes
        SET {"valor_n" if is_num else "valor_a"} = {nuevo_valor}
        WHERE ajuste = '{nombre}'
        """
    )

    conexion.commit()
    conexion.close()


def obtener_valor(tabla: str, columna: str, index: int) -> str | int:
    conexion = sql.connect("Fondo.db")
    cursor = conexion.cursor()

    cursor.execute(
        f"""
        SELECT {columna}
        FROM {tabla}
        WHERE id = {index}
        """
    )

    valor = cursor.fetchall()[0][0]
    conexion.close()

    return valor


def guardar_valor(tabla: str, columna: str, index: int, nuevo_valor: int | str) -> None:
    conexion = sql.connect("Fondo.db")
    cursor = conexion.cursor()

    cursor.execute(
        f"""
        UPDATE {tabla}
        SET {columna} = {nuevo_valor}
        WHERE id = {index}
        """
    )

    conexion.commit()
    conexion.close()
