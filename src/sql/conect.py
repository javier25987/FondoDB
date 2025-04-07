import sqlite3 as sql
import datetime


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


def guardar_ajuste(nombre: str, nuevo_valor: int) -> None:
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
        SET valor_a = '{nuevo_valor}'
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


def guardar_valor(tabla: str, columna: str, index: int, nuevo_valor: int) -> None:
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


def increment(tabla: str, columna: str, index: int, incremento: int) -> None:
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

    valor += incremento

    cursor.execute(
        f"""
        UPDATE {tabla}
        SET {columna} = {valor}
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
        SELECT {columna}
        FROM registros
        WHERE fecha = '{fecha}'
        """
    )

    valor = cursor.fetchall()
    valor = valor[0][0]

    valor += incremento

    cursor.execute(
        f"""
        UPDATE registros
        SET {columna} = {valor}
        WHERE fecha = '{fecha}'
        """
    )

    conexion.commit()
    conexion.close()


def obtener_datos_rifas(rifa: str, colum: str) -> str | int:
    conexion = sql.connect("Fondo.db")
    cursor = conexion.cursor()

    cursor.execute(
        f"""
        SELECT {colum}
        FROM datos_de_rifas
        WHERE id = 'r{rifa}'
        """
    )

    dato = cursor.fetchall()[0][0]
    conexion.close()

    return dato
