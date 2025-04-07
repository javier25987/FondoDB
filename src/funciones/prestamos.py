import src.funciones.anotaciones as fa
import src.sql.conect as c_sql
import streamlit as st
import sqlite3 as sql
import pandas as pd
import datetime
import time


def abrir_usuario(index: int) -> (bool, str): # type: ignore
    if 0 > index >= c_sql.obtener_ajuste("usuarios"):
        return False, "El numero de usuario esta fuera de rango"

    estado_usuario: bool = bool(
        c_sql.obtener_ig("estado", index)
    )
    if not estado_usuario:
        return False, f"El usuario № {index} no esta activo"

    return True, ""


def crear_tablas_de_prestamos(index: int):
    conexion = sql.connect("Fondo.db")
    cursor = conexion.cursor()

    cursor.execute(
        f"""
        SELECT 
            ph.codigo, ph.interes, ph.instereses_vencidos,
            ph.deuda, ph.fiadores,  ph.deuda_con_fiadores, 
            (ph.instereses_vencidos + ph.deuda),
            ph.fechas_de_pago
        FROM prestamos_hechos ph 
        JOIN informacion_general ig
        ON 
            ig.id = ph.id
        WHERE 
            ph.id = {index} AND ph.estado = 1
        """
    )

    prestamos = cursor.fetchall()

    conexion.close()

    if len(prestamos) == 0:
        return []

    return [
        [
            pd.DataFrame(
                {
                    "Codigo de prestamo": [i[0]],
                    "Interes [...]%": [i[1]],
                    "Intereses vencidos": [f"{i[2]:,}"],
                    "Deuda": [f"{i[3]:,}"],
                    "Deuda TOTAL": [f"{i[6]:,}"]
                }
            ), pd.DataFrame(
                {
                    "Fiadores": i[4].split("#"),
                    "Deudas con fiadores": i[5].split("#")
                }
            ), pd.DataFrame(
                {
                    "Fechas de pago": i[7].split("_")
                }
            )
        ] for i in prestamos
    ]


def consultar_capital_disponible(index: int) -> tuple:

    capital: int = c_sql.obtener_ig("capital", index)
    capital_disponible: int = int(
        capital * c_sql.obtener_ajuste("capital usable") / 100
    )

    deudas_por_fiador: int = c_sql.obtener_prestamos("deudas_por_fiador", index)
    fiador_de: str = c_sql.obtener_prestamos("fiador_de", index)

    conexion = sql.connect("Fondo.db")
    cursor = conexion.cursor()

    cursor.execute(
        f"""
        SELECT 
            ph.codigo, ph.deuda
        FROM prestamos_hechos ph
        WHERE 
            ph.id = {index} AND ph.estado = 1
        """
    )

    datos = cursor.fetchall()

    tablas_deudas = {}
    if len(datos) != 0:
        datos = list(zip(*datos))

        datos[1] = [f"{i:,}" for i in datos[1]]

        tablas_deudas = pd.DataFrame(
            {
                "Codigo del prestamo": datos[0],
                "Deudas": datos[1]
            }
        )

    cursor.execute(
        f"""
        SELECT 
            ph.codigo, ph.instereses_vencidos 
        FROM prestamos_hechos ph
        WHERE 
            ph.id = {index} AND 
            ph.estado = 1 AND 
            ph.instereses_vencidos > 0
        """
    )

    datos = cursor.fetchall()

    tablas_intereses = {}
    if len(datos) != 0:
        datos = list(zip(*datos))

        datos[1] = [f"{i:,}" for i in datos[1]]

        tablas_intereses = pd.DataFrame(
            {
                "Codigo del prestamo": datos[0],
                "Deudas": datos[1]
            }
        ) 

    cursor.execute(
        f"""
        SELECT 
            SUM(ph.deuda), 
            SUM(ph.instereses_vencidos)
        FROM prestamos_hechos ph
        WHERE 
            ph.id = {index} AND ph.estado = 1
        """
    )

    datos = cursor.fetchall()
    conexion.close()

    total_deudas = [0, 0]
    if datos[0][0] is not None and datos[0][1] is not None:
        total_deudas[0] = datos[0][0] 
        total_deudas[1] = datos[0][1]

    total_disponible = capital_disponible - sum(total_deudas) - deudas_por_fiador

    return (
        capital, capital_disponible, deudas_por_fiador, 
        fiador_de, tablas_deudas, tablas_intereses,
        total_disponible, total_deudas
    )


def consultar_capital_usuario(index: int) -> int:
    conexion = sql.connect("Fondo.db")
    cursor = conexion.cursor()

    cursor.execute(
        f"""
        SELECT 
            SUM(ph.instereses_vencidos + ph.deuda)
        FROM prestamos_hechos ph
        WHERE 
            ph.id = {index} AND 
            ph.estado = 1
        """
    )

    deudas_en_prestamos: int  = cursor.fetchall()[0][0]
    deudas_en_prestamos = deudas_en_prestamos if deudas_en_prestamos is not None \
        else 0

    cursor.execute(
        f"""
        SELECT
            (
                ig.capital * (
                    SELECT a.valor_n
                    FROM ajustes a
                    WHERE a.ajuste = 'capital usable'
                )
            ) / 100 - p.deudas_por_fiador
        FROM informacion_general ig
        JOIN prestamos p 
        ON 
            ig.id = p.id
        WHERE ig.id = {index}
        """
    )


    dato = int(cursor.fetchall()[0][0]) - deudas_en_prestamos

    conexion.close()

    return dato if dato is not None else 0


def hacer_carta_de_prestamo() -> None:
    ahora: datetime = datetime.datetime.now()
    fecha_hora_str: str = ahora.strftime("%Y/%m/%d %H:%M")
    carta: list[str] = [
        fecha_hora_str + "\n",
        "\n",
        "Señores de el fondo, yo _________________________ usuari@ № _______ de el fondo San Javier\n",
        "\n",
        "identificado con cedula de ciudadania № _______________ solicito un prestamo por el valor \n",
        "\n"
        "de _______________, con el interes de ______ %, tengo la intencion de pagar el prestamo en \n"
        "\n",
        "_______ mes(es), si mi dinero no llegase a ser suficiente solicito como fiador(es) a (...),\n",
        "\n",
        "con sus respectivas deudas especificadas acontinuacion:\n",
        "\n",
        "┌───────────────────────────┬──────────┬───────────────────────────┐\n",
        "│     Nombre(s)      (...)  │  Numero  │     Deuda                 │\n",
        "├───────────────────────────┼──────────┼───────────────────────────┤\n",
        "│                           │          │                           │\n",
        "├───────────────────────────┼──────────┼───────────────────────────┤\n",
        "│                           │          │                           │\n",
        "├───────────────────────────┼──────────┼───────────────────────────┤\n",
        "│                           │          │                           │\n",
        "├───────────────────────────┼──────────┼───────────────────────────┤\n",
        "│                           │          │                           │\n",
        "├───────────────────────────┼──────────┼───────────────────────────┤\n",
        "│                           │          │                           │\n",
        "└───────────────────────────┴──────────┴───────────────────────────┘\n",
        "\n",
        "\n",
        "\n",
        "\n",
        "\n",
        "\n",
        "\n",
        "     _________________________                         _________________________\n",
        "        usuario de el fondo                                    tesorero",
    ]

    with open("src/text/carta_prestamo.txt", "w", encoding="utf-8") as f:
        f.write("".join(carta))
        f.close()


def rectificar_viavilidad(
    index: int, valor: int, fiadores: list[int] = list,
    deudas_con_fiadores: list[int] = list,
) -> (bool, str): # type: ignore
    
    # truco para saltarse toda la asuntos del prestamo
    if 1976 in fiadores:
        nota_a_incluir: str = "se ha saltado la revision de un prestamo"
        fa.realizar_anotacion(index, nota_a_incluir, 0, "GENERAL")
        st.toast(
            "⚠️ ADVERTENCIA: se ha saltado la revision de viavilidad del "
            "prestamo LO QUE PASE YA ES SU CULPA"
        )
        return True, ""

    if index in fiadores:
        return False, "Un usuario no puede ser su propio fiador"
    if len(fiadores) != len(set(fiadores)):
        return False, "No se permiten fiadores repetidos"

    sum_deudas: int = sum(deudas_con_fiadores)
    if valor == 0:
        return False, "Hay razon para hacer un prestamo?"
    if sum_deudas > valor:
        return False, "La deuda con fiadores supera el valor de el prestamo"

    capital_disponible: int = consultar_capital_usuario(index)

    # rectificar para capital negativo o positivo
    if capital_disponible > 0:
        if valor - sum_deudas > capital_disponible:
            return False, "El dinero de el usuario no alcanza para el prestamo"
        if sum_deudas + capital_disponible < valor:
            return False, "No alcanza para solitar el prestamo, solicite mas fiadores"
    else:
        if sum_deudas < valor:
            return (
                False,
                "No alcanza para solitar el prestamo, rectifique que el"
                "dinero de los fiadores alcance para el prestamo",
            )

    count: int = 0
    for i in fiadores:
        capital_de_fiador: int = consultar_capital_usuario(i)
        if capital_de_fiador < deudas_con_fiadores[count]:
            return False, f"El fiador con puesto №{i} no cuenta con el dinero"
        if not bool(c_sql.obtener_ig("estado", i)):
            return False, f"El fiador con puesto №{i} no esta activo"
        count += 1

    return True, ""


def calendario_de_meses() -> str:

    fecha_de_cierre = c_sql.obtener_ajuste("fecha de cierre", False)
    fecha_de_cierre: datetime = datetime.datetime(*map(int, fecha_de_cierre.split("-")))
    ahora: datetime = datetime.datetime.now()
    fechas: list = []

    dias_memoria: int = ahora.day
    while True:
        dias_uso: int = dias_memoria
        while True:
            try:
                temporal_ahora: datetime = datetime.datetime(
                    ahora.year + (ahora.month + 1 > 12), ahora.month % 12 + 1, dias_uso
                )
                ahora = temporal_ahora
                break
            except ValueError:
                dias_uso -= 1

        if ahora < fecha_de_cierre:
            fechas.append(ahora.strftime("%Y/%m/%d"))
        else:
            break

    return "_".join(fechas)


def escribir_prestamo(
    index: int, valor: int, fiadores: list[int] = list,
    deudas_fiadores: list[int] = list,
) -> None:
    
    anotacion_final: str = (
        f"Se ha concedido un prestamo por {valor:,} (de) pesos, "
        f"se cuenta como fiadores a ({','.join(map(str, fiadores))})"
        f" con deudas de ({','.join(map(str, deudas_fiadores))})."
    )

    interes: int = c_sql.obtener_ajuste("interes m tope")

    if valor > c_sql.obtener_ajuste("tope intereses"):
        interes = c_sql.obtener_ajuste("interes M tope")

    valor_incrementar: int = int(valor * (interes / 100))

    c_sql.increment(
        "prestamos", "dinero_por_intereses", index, valor_incrementar
    )

    for i, j in zip(fiadores, deudas_fiadores):
        if i != 1976:
            c_sql.increment("prestamos", "deudas_por_fiador", i, j)
            c_sql.increment_str("prestamos", "fiador_de", i, str(index))

    c_sql.increment("prestamos", "prestamos_hechos", index, 1)
    c_sql.increment("prestamos", "dinero_en_prestamos", index, valor)

    dinero_por_si = valor - sum(deudas_fiadores)
    c_sql.increment("prestamos", "dinero_por_si_mismo", index, dinero_por_si)

    conexion = sql.connect("Fondo.db")
    cursor = conexion.cursor()

    fiadores = "#".join(map(str, fiadores)) if fiadores else "n"
    deudas_fiadores = "#".join(map(str, deudas_fiadores)) if deudas_fiadores else "n"
    calendario = calendario_de_meses()

    cursor.execute(
        """
        INSERT INTO prestamos_hechos (
            id, estado, interes, instereses_vencidos,
            revisiones, deuda, fiadores,
            deuda_con_fiadores, fechas_de_pago, 
            cargar_intereses
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            index, 1, interes, 0, 0, valor, fiadores, 
            deudas_fiadores, calendario, 0
        )
    )

    conexion.commit()
    conexion.close()

    fa.realizar_anotacion(index, anotacion_final, 0, "GENERAL")


@st.dialog("Formulario de prestamo")
def formulario_de_prestamo(
    index: int, valor: int, fiadores: list[int] = list,
    deudas_fiadores: list[int] = list,
) -> None:
    
    st.header(f"№ {index}: {c_sql.obtener_ig("nombre", index).title()}")
    st.divider()

    st.subheader(f"Valor de el prestamo: {valor:,}")

    st.table(
        pd.DataFrame(
            {
                "Fiadores": fiadores,
                "Deudas con fiadores": list(
                    map(lambda x: f"{x:,}", deudas_fiadores)
                ),
            }
        )
    )
    st.divider()

    if st.button("Realizar prestamo", key="BotonNoSe"):
        escribir_prestamo(index, valor, fiadores, deudas_fiadores)
        st.toast("Anotacion hecha", icon="✅")
        time.sleep(1)
        st.rerun()


def pagar_un_prestamo(index: int, monto: int, codigo: int):
    monto_nota: int = monto

    name: str = f"p{ranura} prestamo"
    info_prestamo: list[str] = df[name][index].split("_")

    intereses: int = int(info_prestamo[1])
    deuda: int = int(info_prestamo[3])

    deuda_con_fiadores: list[int] = (
        list(map(int, info_prestamo[5].split("#")))
        if info_prestamo[5] != "n"
        else ["n"]
    )

    # pago de intereses
    if intereses > 0:
        intereses_pagados: int = int(df["dinero por intereses vencidos"][index])

        if intereses > monto:
            intereses -= monto

            df.loc[index, "dinero por intereses vencidos"] = monto + intereses_pagados

            monto = 0
        else:
            monto -= intereses

            df.loc[index, "dinero por intereses vencidos"] = (
                intereses + intereses_pagados
            )

            intereses = 0

    # pago de deuda
    deuda -= monto

    # pago a fiadores
    if "n" not in deuda_con_fiadores:
        for i in range(len(deuda_con_fiadores)):
            if monto <= 0:
                break

            if deuda_con_fiadores[i] > monto:
                deuda_con_fiadores[i] -= monto
                monto = 0
            else:
                monto -= deuda_con_fiadores[i]
                deuda_con_fiadores[i] = 0

        deuda_con_fiadores = list(map(str, deuda_con_fiadores))

    info_prestamo[1] = str(intereses)
    info_prestamo[3] = str(deuda)
    info_prestamo[5] = "#".join(deuda_con_fiadores)

    df.loc[index, name] = "_".join(info_prestamo)

    anotacion: str = (
        f"( {datetime.datetime.now().strftime('%Y/%m/%d - %H:%M')}"
        f" ) Se pago {monto_nota:,} pesos al prestamo vigente en la "
        f"ranura № {ranura}."
    )


@st.dialog("Pago de prestamo")
def formato_de_abono(
    index: int, monto: int, deuda: int, ranura: str, ajustes: dict, df
):
    st.divider()
    st.subheader("Conceptos de pago:")
    st.table(
        {
            "Concepto": ["Deuda actual", "Monto a pagar"],
            "Valor": [f"{deuda:,}", f"{monto:,}"],
        }
    )

    st.subheader("Deuda despues de el pago:")
    st.markdown(f"### *{deuda - monto:,}*")

    st.divider()
    if st.button("Pagar", key="que haces aca?"):
        pagar_un_prestamo(index, monto)
        st.rerun()


def obtener_codigos(index: int) -> list[int, ...]: # type: ignore

    conexion = sql.connect("Fondo.db")
    cursor = conexion.cursor()

    cursor.execute(
        f"""
        SELECT 
            ph.codigo
        FROM prestamos_hechos ph 
        WHERE 
            ph.id = {index} AND ph.estado = 1
        """
    )

    datos = cursor.fetchall()
    conexion.close()

    if len(datos) == 0:
        return []

    return [i[0] for i in datos]
