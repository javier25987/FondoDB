import src.funciones.general as fg
import streamlit as st
import src.sql.conect as c_sql
import sqlite3


def abrir_usuario(index: int):
    if 0 > index >= c_sql.obtener_ajuste("usuarios"):
        return False, "El numero de usuario esta fuera de rango"

    return True, ""


def cargar_usuarios_a_boletas(usr: int, boletas: list, rifa: str):
    conexion = sqlite3.connect("Fondo.db")
    cursor = conexion.cursor()

    for i in boletas:
        cursor.execute(
            f"""
            UPDATE boletas_rifa_{rifa}
            SET dada_a = ?
            WHERE idx = ?
            """,
            (usr, i),
        )

    conexion.commit()
    conexion.close()


@st.dialog("Entrega de talonario")
def entregar_boletas(index: int, boletas: list, rifa: str):
    st.header(f"№ {index} - {c_sql.obtener_ig('nombre', index).title()}")
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

    if st.button("Entregar boletas"):
        cargar_usuarios_a_boletas(index, boletas, rifa)
        fg.hacer_apunte(
            "RIFAS", f"las boletas [{boletas}] fueron entregadas al usuario {index}"
        )


@st.dialog("Pago de boletas")
def pago_de_boletas(index: int, pago: int, rifa: str):
    st.header(f"№ {index} - {c_sql.obtener_ig('nombre', index).title()}")
    st.divider()

    deuda_act: int = c_sql.obtener_rifas(f"r{rifa}_deudas", index)

    st.write(f"Deuda por boletas: {deuda_act:,}")
    st.write(f"Pago que se realiza: {pago:,}")

    st.subheader(f"Deuda restante: {deuda_act - pago:,}")
    st.divider()

    if st.button("Aceptar pago"):
        c_sql.increment("rifas", f"r{rifa}_deudas", index, -pago)

        # ACA SE TIENE QUE PONER LA FUNCION PARA LA ANOTACION

        st.rerun()


def consultar_boletas_usr(index: int, rifa: str) -> list[str]:
    conexion = sqlite3.connect("Fondo.db")
    cursor = conexion.cursor()

    cursor.execute(f"SELECT boleta FROM boletas_rifa_{rifa} WHERE dada_a = {index}")

    boletas = cursor.fetchall()

    return list(map(lambda x: x[0], boletas))


def consultar_boletas_libres(index: int, rifa: str) -> list[str]:
    conexion = sqlite3.connect("Fondo.db")
    cursor = conexion.cursor()

    cursor.execute(f"SELECT idx FROM boletas_rifa_{rifa} WHERE dada_a = ?", (index,))
    boletas = cursor.fetchall()
    return list(map(lambda x: x[0], boletas))
