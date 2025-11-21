import src.funciones.anotaciones as fa
import src.funciones.general as fg
import src.msql as msql
import streamlit as st
import sqlite3


def abrir_usuario(index: int):
    if index < 0 or index > msql.obtener_ajuste("usuarios"):
        return False, "El numero de usuario esta fuera de rango"

    return True, ""


def obtener_datos_usuario(index: int) -> dict:
    return {
        "nombre": msql.obtener_valor("informacion_general", "nombre", index).title(),
    }


def cargar_usuarios_a_boletas(index: int, boletas: list, rifa: str):
    conexion = sqlite3.connect("Fondo.db")
    cursor = conexion.cursor()

    for boleta in boletas:
        cursor.execute(f"UPDATE {rifa} SET dada_a = {index} WHERE idx = {boleta}")

    conexion.commit()
    conexion.close()

    precio_boleta = msql.obtener_valor("datos_de_rifas", "costo_de_boletas", int(rifa[-1]))
    total_boletas = precio_boleta * len(boletas)
    msql.increment_int("deudas_rifa", "deuda", index, total_boletas)

    fa.realizar_anotacion(
        index,
        f"Recibio boletas: {",".join(map(str, boletas))}. en `{rifa}`",
        0,
        "GENERAL"
    )


@st.dialog("Entrega de talonario")
def entregar_boletas(index: int, boletas: list, rifa: str, usr_data: dict):
    """
    Falta incluir las deudas por entregar una boleta
    """
    st.header(f"№ {index} - {usr_data["nombre"]}")
    st.divider()

    st.write(
        "Tenga en cuenta que los numeros que estan aca son el primer numero "
        + "de la boleta que se usa como identificador para referenciar "
        + "internamente a la boleta completa"
    )

    st.subheader("Boletas a entregar:")

    for boleta in boletas:
        st.markdown(f"* {boleta}")

    st.divider()

    if st.button("Entregar"):
        cargar_usuarios_a_boletas(index, boletas, rifa)
        st.rerun()


def consultar_boletas_usr(index: int, tabla_de_rifa: str) -> list[str]:
    conexion = sqlite3.connect("Fondo.db")
    cursor = conexion.cursor()

    cursor.execute(f"SELECT boleta FROM {tabla_de_rifa} WHERE dada_a = {index}")

    boletas = cursor.fetchall()
    conexion.close()

    return list(map(lambda x: x[0], boletas))


def consultar_boletas_libres(index: int, tabla_de_rifa: str) -> list[str]:
    conexion = sqlite3.connect("Fondo.db")
    cursor = conexion.cursor()

    cursor.execute(f"SELECT idx FROM {tabla_de_rifa} WHERE dada_a = ?", (index,))

    boletas = cursor.fetchall()
    return list(map(lambda x: x[0], boletas))


def rectificar_pago(index: int, monto: int, monto_d: int) -> tuple[bool, str]:
    if not fg.rect_estado(index):
        return False, "El usuario no esta activo"

    if monto > monto_d:
        return False, "No se puede pagar mas de lo que se debe."

    if monto <= 0:
        return False, "Para que pagar cero o menos?."

    return True, ""


@st.dialog("Pago de boletas:")
def formlario_de_pago(index: int, monto: int, monto_d: int, usr_data: dict):
    st.header(f"№ {index} - {usr_data["nombre"]}")
    st.divider()

    st.table(
        {
            "Concepto": ["Deuda actual", "Dinero a pagar", "Nueva deuda"],
            "Monto": [f"{monto_d:,}", f"{monto:,}", f"{monto_d - monto:,}"],
        }
    )

    st.divider()
    if st.button("Confirmar pago"):
        msql.registo(monto)
        fa.realizar_anotacion(index, f"se pago: {monto} por boletas", 0, "GENERAL")
        msql.increment_int("deudas_rifa", "deuda", index, -monto)
        st.rerun()


def rectificar_entrega(index: int, boletas: list[int]) -> tuple[bool, str]:
    if not fg.rect_estado(index):
        return False, "El usuario no esta activo"

    if len(boletas) == 0:
        return False, "No hay boletas selecionadas"

    return True, ""