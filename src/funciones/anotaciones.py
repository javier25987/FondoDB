import src.sql.conect as c_sql
import streamlit as st
import datetime


def abrir_usuario(index: int) -> (bool, str): # type: ignore
    if 0 > index >= c_sql.obtener_ajuste("usuarios"):
        return False, "El numero de usuario esta fuera de rango"

    return True, ""


def certificar_anotacion(
        anotacion: str, motivo: str, monto: int
) -> (bool, str): # type: ignore
    
    if anotacion == "":
        return False, "La anotacion esta vacia"

    if motivo in {"MULTA", "ACUERDO"} and monto <= 0:
        return False, "No se puede hacer una anotacion con tal motivo y monto menor a cero"

    simbolos: list[str, ...] = ["_", "$", "."] # type: ignore

    for i in simbolos:
        if i in anotacion:
            return False, f"El simbolo '{i}' no puede estar en la anotacion"
        
    return True, ""



def realizar_anotacion(
    index: int, anotacion: str, monto: int, motivo: str
) -> None:

    # sumatoria a "aporte a multas"
    if motivo in {"MULTA", "ACUERDO"}:
        c_sql.increment(
            "informacion_general", "aporte_a_multas", index, monto
        )

    # creacion de la anotacion
    anotacion: str = (
        f"[{datetime.datetime.now().strftime('%Y/%m/%d %H:%M')}] "
        + anotacion
    )

    if motivo != "GENERAL":
        anotacion += f". $ {monto}"

    # escritura de la anotacion

    columna_anotacion = motivo.lower()
    c_sql.increment_str("anotaciones", columna_anotacion, index, anotacion)

    # escritura del valor
    if motivo != "GENERAL":
        c_sql.increment(
            "informacion_general", "multas_extra", index, monto
        )


def obtener_anotaciones(index: int, motivo: str) -> list[str, ...]: #type: ignore

    anotaciones = c_sql.obtener_valor("anotaciones", motivo, index)

    return anotaciones.split("_") if anotaciones != "n" else [] 