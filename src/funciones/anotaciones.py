import src.funciones.general as fg
import src.msql as msql
import sqlite3 as sql
import datetime


def abrir_usuario(index: int) -> (bool, str):  # type: ignore
    if 0 > index >= msql.obtener_ajuste("usuarios"):
        return False, "El numero de usuario esta fuera de rango"

    return True, ""


def obtener_datos(index) -> dict[str, int | str]:
    return {
        "nombre": msql.obtener_valor("informacion_general", "nombre", index).title(),
        "multas": msql.obtener_valor("multas", "extras", index)
    }


def certificar_anotacion(anotacion: str, motivo: str, monto: int, index) -> tuple[bool, str]:
    if not fg.rect_estado(index):
        return False, "El usuario no esta activo"

    if anotacion == "":
        return False, "La anotacion esta vacia"

    if motivo == "MONETARIA" and monto == 0:
        return (
            False,
            "No se puede hacer una anotacion MONETARIA con monto igual a cero",
        )

    for i in ["$", "."]:
        if i in anotacion:
            return False, f"El simbolo '{i}' no puede estar en la anotacion"

    return True, ""


def realizar_anotacion(index: int, anotacion: str, monto: int, motivo: str) -> None:
    # sumatoria a "multas, extras"
    if motivo == "MONETARIA":
        msql.increment_int("multas", "extras", index, monto)

    fecha: str = datetime.datetime.now().strftime('%Y/%m/%d %H:%M')

    if motivo == "MONETARIA":
        anotacion += f". $ {monto}"

    motivo_cargar: str = motivo[0].upper()

    #cargamos anotacion
    cargar_anotacion(index, anotacion, motivo_cargar, fecha)


def cargar_anotacion(idx: int, anotacion: str, motivo: str, fecha: str) -> None:
    conexion = sql.connect("Fondo.db")
    cursor = conexion.cursor()

    cursor.execute(
        """
        INSERT INTO anotaciones (idx, anotacion, tipo, fecha)
        VALUES (?,?,?,?)
        """,
        (idx, anotacion, motivo, fecha),
    )

    conexion.commit()
    conexion.close()


def obtener_anotaciones(index: int, tipo: str) -> list[str]:
    tipo_busqueda: str = tipo[0].upper()

    conexion = sql.connect("Fondo.db")
    cursor = conexion.cursor()

    cursor.execute(
        """
        SELECT anotacion, fecha
        FROM anotaciones
        WHERE tipo = ? and idx = ?
        """,
        (tipo_busqueda, index)
    )

    datos: list[tuple[str]] = cursor.fetchall()

    conexion.commit()
    conexion.close()

    anotaciones: list[str] = [
        f"[{anot[1]}] {anot[0]}" for anot in datos
    ]

    return anotaciones
