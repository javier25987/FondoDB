import streamlit as st
import sqlite3 as sql
import pandas as pd
import time


def insertar_socios(nombre: str = "", puestos: int = 1, numero_celular: str = ""):
    if numero_celular == "":
        numero_celular = "n"

    nombre = nombre.lower()


@st.dialog("Añadir un nuevo usuario:")
def menu_para_insertar_socio(
    nombre: str = "", puestos: int = 0, telefono: str = ""
) -> None:
    cols = st.columns([7, 3], vertical_alignment="bottom")

    with cols[0]:
        st.subheader("Nombre:")
        st.write(nombre.title())
        st.subheader("Puestos:")
        st.write(puestos)
        st.subheader("Telefono:")
        st.write(telefono)

    with cols[1]:
        if st.button("Añadir", key="nosequeputas"):
            insertar_socios(nombre, puestos, telefono)
            st.toast("Nuevo usuario añadido", icon="🎉")
            time.sleep(1.5)
            st.rerun()


def mostrar_usuarios() -> pd.DataFrame:
    conexion = sql.connect("Fondo.db")
    cursor = conexion.cursor()

    cursor.execute(
        """
        SELECT 
            id, nombre, puestos
        FROM informacion_general
        ORDER BY id DESC 
        """
    )

    datos = cursor.fetchall()
    conexion.close()

    datos = list(zip(*datos))

    return pd.DataFrame({"ID": datos[0], "Nombre": datos[1], "Telefono": datos[2]})


def realizar_consulta(consulta: str, commit: bool) -> pd.DataFrame:
    conexion = sql.connect("Fondo.db")
    cursor = conexion.cursor()

    try:
        cursor.execute(consulta)
    except SyntaxError:
        st.toast("🚨 Hay un error con el formato o valores en la consulta")
        return {}

    datos = cursor.fetchall()

    if commit:
        conexion.commit()

    conexion.close()

    datos = list(zip(*datos))

    tabla = {}

    count: int = 0
    for i in datos:
        tabla[count] = i
        count += 1

    return tabla


def leer_estructura() -> str:
    with open("src/datos_tablas.md", "r") as f:
        archivos: str = f.readlines()
        f.close()

    return "".join(archivos)


def leer_comandos() -> str:
    with open("src/comandos.md", "r") as f:
        archivos: str = f.readlines()
        f.close()

    return "".join(archivos)
