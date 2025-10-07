import src.funciones.general as fg
import src.sql.conect as c_sql
import streamlit as st
import datetime
import time
import os


def hacer_commit() -> None:
    with st.status("Guardando cambios ...", expanded=True) as status:
        os.chdir(c_sql.obtener_ajuste("path programa", False))

        st.write("Subiendo archivos ...")
        fg.ejecutar_comando_git(["git", "add", "."])

        st.write("Guardando cambios ...")

        ahora = datetime.datetime.now()
        fecha_hora_str = ahora.strftime("%Y-%m-%d_%H:%M:%S")
        commits_hechos = c_sql.obtener_ajuste("commits hechos")

        commits_hechos += 1
        mensaje_de_comit = f"{commits_hechos}_{fecha_hora_str}"

        fg.ejecutar_comando_git(["git", "commit", "-m", mensaje_de_comit])

        st.write("Guardando en GitHub ...")
        fg.ejecutar_comando_git(["git", "push"])

        c_sql.guardar_ajuste("commits hechos", commits_hechos)

        status.update(
            label="Los datos han sido cargados!", state="complete", expanded=False
        )
        time.sleep(1)
        st.rerun()
