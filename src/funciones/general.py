import src.sql.conect as c_sql
import streamlit as st
import subprocess
import datetime
import time


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
    st.page_link("src/session/login.py", label="Ingresar", icon=":material/login:")


def rect_estado(idx: int) -> bool:
    return bool(c_sql.obtener_ig("estado", idx))
