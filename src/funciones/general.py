import streamlit as st
import pandas as pd
import subprocess
import datetime
import sqlite3
import time


def obtener_ajuste(nombre: str, is_num: bool = True) -> str | int:
    conexion = sqlite3.connect("Fondo.db")
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


def guardar_ajuste(
    nombre: str, nuevo_valor: int | str, is_num: bool = True
) -> None:
    conexion = sqlite3.connect("Fondo.db")
    cursor = conexion.cursor()

    cursor.execute(
        f"""
        UPDATE ajustes
        SET {"valor_n" if is_num else "valor_a"} = {nuevo_valor}
        WHERE ajuste = '{nombre}'
        """
    )

    conexion.commit()
    conexion.close()


def obtener_valor(
    tabla: str, columna: str, index: int
) -> str | int:
    conexion = sqlite3.connect("Fondo.db")
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


def cargar_valor(
    tabla: str, columna: str, index: int, nuevo_valor: int | str
) -> None:
    conexion = sqlite3.connect("Fondo.db")
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


def fetchall_to_table(contenido, columnas):
    tabla = list(zip(*contenido))

    if len(tabla) != len(columnas):
        raise "las columnas y sus nombres no coinciden"

    resultado = {}

    for i in range(len(tabla)):
        resultado[columnas[i]] = tabla[i]

    return pd.DataFrame(resultado)


def string_a_fecha(fecha: str):
    return datetime.datetime(*map(int, fecha.split("/")))


@st.dialog("🚨  Error!!  🚨")
def error_commit() -> None:
    st.markdown(
        """
        Los nuevos cambios fueron guardados en el computador pero
        no fueron guardados en internet por favor revise si GitHub
        esta correctamente abierto, si cuenta con conexion a internet
        o si es la primera vez que se guarda cambios que el repositorio
        remoto esta correctamente configurado  🚨
        
        > **NOTA:** Este proceso puede demorar un poco, por favor
        > espere 10 segundos
        """  # , icon="🚨"
    )

    time.sleep(15)


def ejecutar_comando_git(comando):
    proceso = subprocess.Popen(comando, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    salida, error = proceso.communicate()

    if proceso.returncode != 0:
        print(f"Error: {error.decode('utf-8')}")
        if "remote:" in error.decode("utf-8"):
            error_commit()
        if "fatal: unable to access" in error.decode("utf-8"):
            error_commit()
    else:
        print(f"Salida: {salida.decode('utf-8')}")


@st.dialog("🚨 Advertencia 🚨")
def advertencia():
    st.write(
        "Para poder continuar con este proceso es necesario "
        " ingresar como administrador, de lo contrario no sera"
        " posible."
    )
    st.page_link("session/login.py", label="Ingresar", icon=":material/login:")
