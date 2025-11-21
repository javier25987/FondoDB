import src.funciones.prestamos as fp
import src.funciones.general as fg
import src.funciones.cuotas as fc
import src.msql as msql
import streamlit as st
import sqlite3 as sql
import polars as pl
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


def mostrar_usuarios() -> pl.DataFrame:
    conexion = sql.connect("Fondo.db")
    query: str = """
    SELECT 
        ig.id AS ID,
        ig.nombre AS Nombre,
        ig.puestos AS Puestos,
        ig.telefono AS Telefono
    FROM informacion_general ig
    ORDER BY ig.id DESC
    """
    df: pl.DataFrame = pl.read_database(query, conexion)

    conexion.close()
    return df


def leer_estructura() -> str:
    with open("src/datos_tablas.md", "r") as f:
        archivos: list[str] = f.readlines()
        f.close()

    return "".join(archivos)


def leer_comandos() -> str:
    with open("src/comandos.md", "r") as f:
        archivos: list[str] = f.readlines()
        f.close()

    return "".join(archivos)


def consultar_codigos() -> list[str]:
    conexion = sql.connect("Fondo.db")
    cursor = conexion.cursor()

    cursor.execute("SELECT codigo FROM prestamos_hechos")
    codigos = cursor.fetchall()

    conexion.close()

    return [i[0] for i in codigos]


def corregir_fecha(codigo: str, fecha) -> None:
    conexion = sql.connect("Fondo.db")
    cursor = conexion.cursor()

    nuevas_fechas = fp.calendario_de_meses(fecha)

    cursor.execute(
        """
        UPDATE prestamos_hechos
        SET fechas_de_pago = ?
        WHERE codigo = ?
        """, (nuevas_fechas, codigo)
    )
    
    conexion.commit()
    conexion.close()


def abrir_usuario(index: int) -> tuple[bool, str]:
    if index < 0 or index > msql.obtener_ajuste("usuarios"):
        return False, "El numero de usuario esta fuera de rango"

    return True, ""


def obtener_datos_usuario(index: int) -> dict:
    multas: str = msql.obtener_valor("cuotas", "multas", index, )
    multas_pagas: str = msql.obtener_valor("cuotas", "multas_pagas", index)

    return {
        "nombre": msql.obtener_valor("informacion_general", "nombre", index).title(),
        "multas": {
            "Semana": range(1, 51),
            "Multas activas": fc.descomprimir_to_array(multas),
            "Multas pagas": fc.descomprimir_to_array(multas_pagas)
        }
    }


def rectificar_datos(index: int, valor: int) -> tuple[bool, str]:
    if not fg.rect_estado(index):
        return False, "El usuario no esta activo"

    if valor < 0:
        return False, "El nuevo valor no puede ser menor a cero"

    return True, ""


def agregar_nuevo_valor(
    index: int, semana: int, tipo_de_multa: str, nuevo_valor: int, usr_data: dict
) -> None:
    nuevo_array: list[int] = usr_data["multas"][tipo_de_multa]
    nuevo_array[semana-1] = nuevo_valor

    if tipo_de_multa == "Multas activas":
        columna: str = "multas"
    else:
        columna: str = "multas_pagas"

    msql.guardar_valor_t(
        "cuotas", columna, index,
        fc.comprimir_of_array(nuevo_array)
    )

