import sqlite3 as sql
import datetime

def obtener_ajuste(nombre: str, is_num: bool = True):
    conexion = sql.connect("Fondo.db")
    cursor = conexion.cursor()

    cursor.execute(
        f"""
        SELECT {"valor_n" if is_num else "valor_t"}
        FROM ajustes
        WHERE ajuste = '{nombre}'
        """
    )

    resultado = cursor.fetchall()[0][0]
    conexion.close()

    return resultado


def guardar_ajuste_n(nombre: str, nuevo_valor: int) -> None:
    conexion = sql.connect("Fondo.db")
    cursor = conexion.cursor()

    cursor.execute(
        f"""
        UPDATE ajustes
        SET valor_n = {nuevo_valor}
        WHERE ajuste = '{nombre}'
        """
    )

    conexion.commit()
    conexion.close()


def guardar_ajuste_t(nombre: str, nuevo_valor: int | str) -> None:
    conexion = sql.connect("Fondo.db")
    cursor = conexion.cursor()

    cursor.execute(
        f"""
        UPDATE ajustes
        SET valor_t = '{nuevo_valor}'
        WHERE ajuste = '{nombre}'
        """
    )

    conexion.commit()
    conexion.close()


def obtener_valor(tabla: str, columna: str, index: int): # -> str | int:
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


def guardar_valor_n(tabla: str, columna: str, index: int, nuevo_valor: int) -> None:
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


def guardar_valor_t(tabla: str, columna: str, index: int, nuevo_valor: str) -> None:
    conexion = sql.connect("Fondo.db")
    cursor = conexion.cursor()

    cursor.execute(
        f"""
        UPDATE {tabla}
        SET {columna} = '{nuevo_valor}'
        WHERE id = {index}
        """
    )

    conexion.commit()
    conexion.close()


def increment_int(tabla: str, columna: str, index: int, incremento: int) -> None:
    conexion = sql.connect("Fondo.db")
    cursor = conexion.cursor()

    cursor.execute(
        f"""
        UPDATE {tabla}
        SET {columna} = {columna} + {incremento}
        WHERE id = {index}
        """
    )

    conexion.commit()
    conexion.close()


def increment_str(tabla: str, columna: str, index: int, incremento: str) -> None:
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

    if valor == "n" or valor == "nan":
        valor = incremento
    else:
        valor += f"_{incremento}"

    cursor.execute(
        f"""
        UPDATE {tabla}
        SET {columna} = '{valor}'
        WHERE id = {index}
        """
    )

    conexion.commit()
    conexion.close()


def registo(incremento: int, is_ingeso: bool = True) -> None:
    fecha: str = datetime.datetime.now().strftime("%Y-%m-%d")

    columna: str = "ingreso" if is_ingeso else "egreso"

    conexion = sql.connect("Fondo.db")
    cursor = conexion.cursor()

    cursor.execute(
        f"""
        UPDATE registros
        SET {columna} = {columna} + {incremento}
        WHERE fecha = '{fecha}'
        """
    )

    conexion.commit()
    conexion.close()
