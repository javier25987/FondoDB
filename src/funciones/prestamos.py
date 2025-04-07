import src.funciones.general as fg
import src.sql.conect as c_sql
import sqlite3 as sql
import streamlit as st
import pandas as pd
import datetime


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
    
    result: list[list[pd.DataFrame]] = [
        [
            pd.DataFrame(
                {
                    "Codigo de prestamo": [i[0]],
                    "Interes [.]%": [i[1]],
                    "Intereses vencidos": [f"{i[2]:,}"],
                    "Deuda": [f"{i[3]:,}"],
                    "Deuda TOTAL": [f"{i[6]:,}"]
                }
            ), pd.DataFrame(
                {
                    "Fiadores": [i[4]],
                    "Deudas con fiadores": [i[5]]
                }
            ), pd.DataFrame(
                {
                    "Fechas de pago": i[7].split("_")
                }
            )
        ] for i in prestamos
    ]

    return result


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
            (
                (
                    ig.capital * (
                        SELECT a.valor_n
                        FROM ajustes a
                        WHERE a.ajuste = 'capital usable'
                    )
                ) - (
                    (
                        SELECT 
                            SUM(ph.instereses_vencidos + ph.deuda)
                        FROM prestamos_hechos ph
                        WHERE 
                            ph.id = {index} AND 
                            ph.estado = 1
                    ) + p.deudas_por_fiador
                ) * 100
            ) / 100
        FROM informacion_general ig
        JOIN prestamos p 
        ON 
            ig.id = p.id
        WHERE ig.id = {index}
        """
    )

    dato = cursor.fetchall[0][0]
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
        nota_a_incluir: str = (
            f"({datetime.datetime.now().strftime('%Y/%m/%d %H:%M')}) la"
            f" revison para solicitud de un prestamo ha sido saltada"
        )
        realizar_anotacion(index, nota_a_incluir, ajustes, df)
        st.toast(
            "⚠️ ADVERTENCIA: se ha saltado la revision de viavilidad del "
            "prestamo LO QUE PASE YA ES SU CULPA"
        )
        return True, ""

    if index in fiadores:
        return False, "Un usuario no puede ser su propio fiador"
    if len(fiadores) != len(set(fiadores)):
        return False, "No se permiten fiadores repetidos"

    capital_disponible: int = consultar_capital_usuario(index, ajustes, df)
    sum_deudas: int = sum(deudas_con_fiadores)
    if valor == 0:
        return False, "Para que hacer un prestamo?"
    if sum_deudas > valor:
        return False, "La deuda con fiadores supera el valor de el prestamo"

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
        capital_de_fiador: int = consultar_capital_usuario(i, ajustes, df)
        if capital_de_fiador < deudas_con_fiadores[count]:
            return False, f"El fiador con puesto №{i} no cuenta con el dinero"
        if df["estado"][i] != "activo":
            return False, f"El fiador con puesto №{i} no esta activo"
        count += 1

    return True, ""


def calendario_de_meses(fecha_de_cierre: str) -> str:
    fecha_de_cierre: datetime = datetime.datetime(*map(int, fecha_de_cierre.split("/")))
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
    index: int,
    ranura: str,
    valor: int,
    ajustes: dict,
    df,
    fiadores: list[int] = list,
    deudas_fiadores: list[int] = list,
) -> None:
    anotacion_final: str = (
        f"( {datetime.datetime.now().strftime('%Y/%m/%d %H:%M')} )"
        f" Se ha concedido un prestamo por {valor:,} (de) pesos, el "
        f"prestamo esta almacenado en la ranura № {ranura} se cuenta "
        f"como fiadores a ({','.join(map(str, fiadores))}) con deudas"
        f" de ({','.join(map(str, deudas_fiadores))})."
    )

    interes: int = ajustes["interes < tope"]

    if valor > ajustes["tope de intereses"]:
        interes = ajustes["interes > tope"]

    intereses_vencidos: int = int(df["dinero por intereses vencidos"][index])
    intereses_vencidos += int(valor * (interes / 100))
    df.loc[index, "dinero por intereses vencidos"] = intereses_vencidos

    info_general: str = "_".join(
        (
            str(interes),
            "0",
            "0",
            str(valor),
            "#".join(map(str, fiadores)) if fiadores else "n",
            "#".join(map(str, deudas_fiadores)) if deudas_fiadores else "n",
        )
    )
    count: int = 0
    for i in fiadores:
        if i != 1976:
            deudas_de_el_fiador: int = int(df["deudas por fiador"][i])
            deudas_de_el_fiador += deudas_fiadores[count]
            df.loc[i, "deudas por fiador"] = deudas_de_el_fiador

            fiador_de: str = df["fiador de"][i]
            if fiador_de == "n":
                fiador_de = str(index)
            else:
                fiador_de += f"_{index}"
            df.loc[i, "fiador de"] = fiador_de

        count += 1

    prestamos_hechos: int = int(df["prestamos hechos"][index])
    prestamos_hechos += 1
    df.loc[index, "prestamos hechos"] = prestamos_hechos

    dinero_en_prestamos: int = int(df["dinero en prestamos"][index])
    dinero_en_prestamos += valor
    df.loc[index, "dinero en prestamos"] = dinero_en_prestamos

    dinero_por_si: int = int(df["dinero por si mismo"][index])
    dinero_por_si += valor - sum(fiadores)
    df.loc[index, "dinero por si mismo"] = dinero_por_si

    df.loc[index, f"p{ranura} estado"] = "no activo"
    df.loc[index, f"p{ranura} prestamo"] = info_general
    df.loc[index, f"p{ranura} fechas de pago"] = calendario_de_meses(
        ajustes["fecha de cierre"]
    )

    realizar_anotacion(index, anotacion_final, ajustes, df)


@st.dialog("Formulario de prestamo")
def formulario_de_prestamo(
    index: int, valor: int, fiadores: list[int] = list,
    deudas_fiadores: list[int] = list,
) -> None:
    
    st.header(f"№ {index}: {df['nombre'][index].title()}")
    st.divider()

    st.subheader(f"Valor de el prestamo: {valor:,}")
    st.subheader(f"Guardar en la ranura: {ranura}")

    st.table(
        pd.DataFrame(
            {
                "Fiadores": fiadores,
                "Deudas con fiadores": list(
                    map(lambda x: "{:,}".format(x), deudas_fiadores)
                ),
            }
        )
    )
    st.divider()

    if st.button("Realizar prestamo", key="BotonNoSe"):
        escribir_prestamo(index, ranura, valor, ajustes, df, fiadores, deudas_fiadores)
        st.rerun()

def pagar_un_prestamo(index: int, ranura: str, monto: int, ajustes: dict, df):
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
            "Valor": ["{:,}".format(deuda), "{:,}".format(monto)],
        }
    )

    st.subheader("Deuda despues de el pago:")
    st.markdown(f"### *{deuda - monto:,}*")

    st.divider()
    if st.button("Pagar", key="que haces aca?"):
        pagar_un_prestamo(index, ranura, monto, ajustes, df)
        st.rerun()


def arreglar_asuntos(index: int) -> None:
    ranuras: list[str] = list(map(str, range(1, 17)))

    guardar: bool = False

    for i in ranuras:
        if df[f"p{i} estado"][index] != "activo":
            prestamo: list[str] = df[f"p{i} prestamo"][index].split("_")
            fechas: str = df[f"p{i} fechas de pago"][index]

            fecha_actual = datetime.datetime.now()

            fechas_pasadas: int = sum(
                map(
                    lambda x: x < fecha_actual,
                    map(fg.string_a_fecha, fechas.split("_")),
                )
            )

            revisiones: int = int(prestamo[2])

            if fechas_pasadas > revisiones:
                intereses: int = int(prestamo[1])
                interes: float = int(prestamo[0]) / 100
                deuda: int = int(prestamo[3])

                for _ in range(fechas_pasadas - revisiones):
                    intereses += (deuda + intereses) * interes

                revisiones = fechas_pasadas

                prestamo[2] = str(revisiones)
                prestamo[1] = str(int(intereses))

                df.loc[index, f"p{i} prestamo"] = "_".join(prestamo)

                guardar = True

    if guardar:
        df = df.loc[:, ~df.columns.str.contains("^Unnamed")]
        df.to_csv(ajustes["nombre df"])
