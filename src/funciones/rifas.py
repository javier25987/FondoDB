import src.funciones.general as fg
import src.msql as msql
import streamlit as st
import sqlite3


def abrir_usuario(index: int):
    if index < 0 or index > msql.obtener_ajuste("usuarios"):
        return False, "El numero de usuario esta fuera de rango"

    return True, ""


def cargar_usuarios_a_boletas(usr: int, boletas: list, rifa: str):
    conexion = sqlite3.connect("Fondo.db")
    cursor = conexion.cursor()

    for i in boletas:
        cursor.execute(
            f"""
            UPDATE {rifa}
            SET dada_a = ?
            WHERE idx = ?
            """,
            (usr, i),
        )

    cursor.execute(f"SELECT costo_de_boleta FROM datos_de_rifas WHERE id = {rifa[-1]}")

    precio_boleta = cursor.fetchall()[0][0]

    total_boletas = precio_boleta * len(boletas)

    cursor.execute(
        f"UPDATE deudas_rifa SET deuda = deuda + {total_boletas} WHERE id = {usr}"
    )

    conexion.commit()
    conexion.close()


@st.dialog("Entrega de talonario")
def entregar_boletas(index: int, boletas: list, rifa: str):
    """
    Falta incluir las deudas por entregar una boleta
    """
    st.header(f"№ {index} - {msql.obtener_ig('nombre', index).title()}")
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
        fg.hacer_apunte(
            "RIFAS", f"las boletas: {','.join(boletas)} fueron entregadas a {index}"
        )
        st.rerun()


@st.dialog("Pago de boletas")
def pago_de_boletas(index: int, pago: int, rifa: str):
    st.header(f"№ {index} - {msql.obtener_ig('nombre', index).title()}")
    st.divider()

    deuda_act: int = msql.obtener_rifas(f"r{rifa}_deudas", index)

    st.write(f"Deuda por boletas: {deuda_act:,}")
    st.write(f"Pago que se realiza: {pago:,}")

    st.subheader(f"Deuda restante: {deuda_act - pago:,}")
    st.divider()

    if st.button("Aceptar pago"):
        msql.increment("rifas", f"r{rifa}_deudas", index, -pago)

        # ACA SE TIENE QUE PONER LA FUNCION PARA LA ANOTACION

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


def rectificar_pago(monto: int, monto_d: int) -> tuple[bool, str]:
    if monto > monto_d:
        return False, "No se puede pagar mas de lo que se debe."
    if monto <= 0:
        return False, "Para que pagar cero o menos?."

    return True, ""


@st.dialog("Pago de boletas:")
def formlario_de_pago(usr: int, monto: int, monto_d: int):
    st.header(f"№ {usr} - {msql.obtener_ig('nombre', usr).title()}")
    st.divider()

    st.table(
        {
            "Concepto": ["Deuda actual", "Dinero a pagar", "Nueva deuda"],
            "Monto": [f"{monto_d:,}", f"{monto:,}", f"{monto_d - monto:,}"],
        }
    )

    st.divider()
    if st.button("Confirmar pago"):
        fg.hacer_apunte(
            "RIFAS",
            f"El usuario {usr} ha pagado {monto}, en boletas. {monto_d:,} -> {
                monto_d - monto:,}",
        )
        msql.increment("deudas_rifa", "deuda", usr, -monto)
        st.rerun()
