import src.funciones.anotaciones as fa
import src.funciones.general as fg
import src.msql as msql
import streamlit as st
import sqlite3 as sql
import datetime


# ======================================================================================================================
# GESTION

def abrir_usuario(index: int) -> tuple[bool, str]:
    if index < 0 or index > msql.obtener_ajuste("usuarios"):
        return False, "El numero de usuario esta fuera de rango"

    return True, ""


def obtener_datos_usuario(index: int) -> dict:
    return {
        "nombre": msql.obtener_valor("informacion_general", "nombre", index).title(),
    }

# ======================================================================================================================
# CREACION

def rectificar_creacion(index: int, monto: int) -> tuple[bool, str]:
    if not fg.rect_estado(index):
        return False, "El usuario no esta activo"

    if monto <= 0:
        return False, "El monto no puede ser menor o igual a cero"

    return True, ""


def crear_deuda(index: int, motivo: str, monto: int, is_multa: bool) -> None:
    """
    en esta funcion en teoria deberia solo guardar los datos y los
    datos ser creados en otra funcion pero como no son muchos datos
    decidi hacerlo en una unica funcion
    """

    conexion = sql.connect("Fondo.db")
    cursor = conexion.cursor()

    fecha_actual: str = datetime.datetime.now().strftime("%Y/%m/%d")

    cursor.execute(
        """
        INSERT INTO deudas (
            idx, monto, fecha_de_creacion, 
            fecha_de_pago, is_multa, motivo, estado
        ) VALUES (?,?,?,?,?,?,?)
        """, (index, monto, fecha_actual, "n", is_multa, motivo, False)
    )

    conexion.commit()
    conexion.close()


@st.dialog("Confirmacion de multa:")
def formulario_de_crecion(index: int, motivo: str, monto: int, is_multa: bool) -> None:
    st.subheader("Motivo:")
    st.markdown(f"> {motivo}")
    st.subheader(f"Monto: {monto:,}")

    if is_multa:
        st.info(
            """
            Ha activado la opcion `Aportar a multas`, esto quiere decir que al ser pagada 
            esta deuda el monto de la deuda sera sumado a la columna de multas del usuario
            """ ,
            icon="ℹ️"
        )

    st.divider()
    if st.button("Confirmar"):
        crear_deuda(index, motivo, monto, is_multa)
        st.rerun()

# ======================================================================================================================
# VISTA

def obtener_deudas_usr(index: int) -> list[dict[str, str | bool | int]]:
    conexion = sql.connect("Fondo.db")
    cursor = conexion.cursor()

    cursor.execute("SELECT * FROM deudas d WHERE d.idx = ?", (index, ))

    datos = cursor.fetchall()
    conexion.close()

    return [
        {
            "codigo": dato[0],
            "monto": dato[2],
            "creacion": dato[3],
            "pago": dato[4],
            "is_multa": bool(dato[5]),
            "motivo": dato[6],
            "estado": bool(dato[7])
        }
        for dato in datos
    ]

# ======================================================================================================================
# PAGO

@st.dialog("Confirmacion de pago:")
def confirmar_pago(index: int, deuda: dict) -> None:
    st.subheader(f"Codigo: {deuda["codigo"]}")
    st.subheader(f"Monto: {deuda["monto"]:,}")

    st.divider()

    if st.button("Confirmar"):
        pagar_deuda(index, deuda)
        st.rerun()

def pagar_deuda(index: int, deuda: dict) -> None:
    conexion = sql.connect("Fondo.db")
    cursor = conexion.cursor()

    fecha_actual: str = datetime.datetime.now().strftime("%Y/%m/%d")

    cursor.execute(
        "UPDATE deudas SET fecha_de_pago = ?, estado = 1 WHERE codigo = ?",
        (fecha_actual, deuda["codigo"])
    )
    conexion.commit()
    conexion.close()

    if deuda["is_multa"]:
        fa.realizar_anotacion(
            index,
            f"Pago de deuda №:{deuda["codigo"]}",
            deuda["monto"],
            "MONETARIA"
        )
