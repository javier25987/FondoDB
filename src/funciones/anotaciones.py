import streamlit as st
import datetime

def ingresar_usuario(index: int, ajustes: dict, df) -> (bool, str):
    if (0 > index) or (index >= ajustes["usuarios"]):
        return False, "Numero de usuario fuera de rango"

    if df["estado"][index] != "activo":
        return False, f"El usuario № {index} esta desactivado"

    return True, ""


def realizar_anotacion(
    index: int, anotacion: str, monto: int, motivo: str, ajustes: dict, df
) -> tuple[bool, str]:
    if "_" in anotacion:
        return False, "El simbolo '_' no puede estar en la anotacion"
    if "$" in anotacion:
        return False, "El simbolo '$' no puede estar en la anotacion"
    if ":" in anotacion:
        return False, "El simbolo ':' no puede estar en la anotacion"
    if anotacion == "":
        return False, "La anotacion esta vacia"

    # sumatoria a "aporte a multas"
    if (motivo != "GENERAL") and (monto > 0):
        monto_de_aporte: int = df["aporte a multas"][index]
        monto_de_aporte += monto
        df.loc[index, "aporte a multas"] = monto_de_aporte

    # creacion de la anotacion
    anotacion: str = f"{motivo} -" + \
        f"{datetime.datetime.now().strftime('%Y/%m/%d - %H;%M')} " + \
        anotacion + \
        f": $ {monto}"

    # escritura de la anotacion
    anotaciones: str = df["anotaciones generales"][index]
    if anotaciones == "n":
        anotaciones = anotacion
    else:
        anotacion = "_" + anotacion
        anotaciones += anotacion
    df.loc[index, "anotaciones generales"] = anotaciones

    # escritura del valor
    multas_actuales: int = df["multas extra"][index]
    multas_actuales += monto
    df.loc[index, "multas extra"] = multas_actuales

    # escritura de la tabla
    df = df.loc[:, ~df.columns.str.contains("^Unnamed")]
    df.to_csv(ajustes["nombre df"])

    return True, ""


def modificar_anotacion(index: int, pos: int, new_elem: str, ajustes: dict, df):
    # confiramcion permisos de administrador
    if not st.session_state.admin:
        return False, "Se necesitan permisos de administrador"

    if "_" in new_elem:
        return False, "El simbolo '_' no puede estar en la anotacion"
    if "$" in new_elem:
        return False, "El simbolo '$' no puede estar en la anotacion"
    if ":" in new_elem:
        return False, "El simbolo ':' no puede estar en la anotacion"

    anotaciones: str = df["anotaciones generales"][index]
    anotaciones: list[str] = anotaciones.split("_")

    anotacion: str = anotaciones[pos]
    monto: str = anotacion[anotacion.find(":") :]

    if new_elem == "":
        anotaciones[pos] = "n" + monto
    else:
        anotaciones[pos] = new_elem + monto

    anotaciones = "_".join(anotaciones)
    df.loc[index, "anotaciones generales"] = anotaciones

    df = df.loc[:, ~df.columns.str.contains("^Unnamed")]
    df.to_csv(ajustes["nombre df"])

    return True, ""