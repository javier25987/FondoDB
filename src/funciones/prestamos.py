import funciones.general as fg
import streamlit as st
import pandas as pd
import datetime


def abrir_usuario(index: int, ajustes: dict, df) -> (bool, str):
    if 0 > index >= ajustes["usuarios"]:
        return False, "El numero de usuario esta fuera de rango"

    if df["estado"][index] != "activo":
        return False, "fEl usuario № {index} no esta activo",

    return True, ""


def crear_tablas_de_ranura(prestamo: str, fechas: str) -> (
    pd.DataFrame, pd.DataFrame, pd.DataFrame, bool, int
):
    prestamo: list[str] = prestamo.split("_")
    deudas = int(prestamo[3]) + int(prestamo[1])
    return (
        pd.DataFrame(
            {
                "Deuda": ["{:,}".format(int(prestamo[3]))],
                "Interes": [f"{prestamo[0]} %"],
                "Intereses Vencidos": ["{:,}".format(int(prestamo[1]))],
            }
        ),
        pd.DataFrame({"Fechas": fechas.split("_")}),
        pd.DataFrame(
            {
                "Fiadores": prestamo[4].split("#"),
                "Deuda Con fiadores": prestamo[5].split("#"),
            }
        ),
        True if deudas == 0 else False,
        deudas,
    )


def ranuras_disponibles(index: int, df) -> pd.DataFrame:
    funct = lambda x: "✅" if x == "activo" else "🚨"

    estado_ranuras: list[str] = list(
        map(funct, [df[f"p{i} estado"][index] for i in range(1, 16)])
    )
    dict_tabla: dict = {}

    for i in range(1, 16):
        dict_tabla[str(i)] = list(estado_ranuras[i - 1])

    return pd.DataFrame(dict_tabla)


def activar_ranura(index: int, df, ajustes: dict, ranura: str) -> None:
    estado: str = f"p{ranura} estado"
    prestamo: str = f"p{ranura} prestamo"
    fechas: str = f"p{ranura} fechas de pago"

    if df[estado][index] != "activo":
        df.loc[index, estado] = "activo"
        df.loc[index, prestamo] = "0_0_0_0_n_n"
        df.loc[index, fechas] = "n"

        df = df.loc[:, ~df.columns.str.contains("^Unnamed")]
        df.to_csv(ajustes["nombre df"])
        st.rerun()
    else:
        st.info("La ranura esta activa", icon="ℹ️")


def consultar_capital_disponible(index: int, ajustes: dict, df) -> tuple:
    capital: int = int(df["capital"][index])
    capital_disponible: int = int(capital * ajustes["capital usable"] / 100)

    deudas_por_fiador: int = int(df["deudas por fiador"][index])

    deudas_en_prestamos_tabla: dict = {"Ranuras": [], "Deudas": []}
    deudas_en_prestamos: int = 0

    deudas_por_intereses_tabla: dict = {"Ranuras": [], "Deudas": []}
    deudas_por_intereses: int = 0

    for i in range(1, 17):
        if df[f"p{i} estado"][index] != "activo":
            prestamo: list[str] = df[f"p{i} prestamo"][index].split("_")

            deuda_prestamo: int = int(prestamo[3])
            if deuda_prestamo > 0:
                deudas_en_prestamos_tabla["Ranuras"].append(f"Ranura {i}")
                deudas_en_prestamos_tabla["Deudas"].append(
                    "{:,}".format(deuda_prestamo)
                )
                deudas_en_prestamos += deuda_prestamo

            deuda_intereses: int = int(prestamo[1])
            if deuda_intereses > 0:
                deudas_por_intereses_tabla["Ranuras"].append(f"Ranura {i}")
                deudas_por_intereses_tabla["Deudas"].append(
                    "{:,}".format(deuda_intereses)
                )
                deudas_por_intereses += deuda_intereses

    deudas_en_prestamos_tabla["Ranuras"].append("TOTAL:")
    deudas_en_prestamos_tabla["Deudas"].append("{:,}".format(deudas_en_prestamos))

    deudas_por_intereses_tabla["Ranuras"].append("TOTAL:")
    deudas_por_intereses_tabla["Deudas"].append("{:,}".format(deudas_por_intereses))

    capital_total: int = capital_disponible - (
        deudas_por_fiador + deudas_en_prestamos + deudas_por_intereses
    )

    return (
        "{:,}".format(capital_total),  # 0
        "{:,}".format(capital),  # 1
        "{:,}".format(capital_disponible),  # 2
        "{:,}".format(deudas_por_fiador),  # 3
        pd.DataFrame(deudas_en_prestamos_tabla),  # 4
        pd.DataFrame(deudas_por_intereses_tabla),  # 5
    )


def consultar_capital_usuario(index: int, ajustes: dict, df) -> int:
    capital: int = int(df["capital"][index])
    capital_disponible: int = int(capital * ajustes["capital usable"] / 100)

    deudas_por_fiador: int = int(df["deudas por fiador"][index])

    deudas_en_prestamos: int = 0
    deudas_por_intereses: int = 0

    for i in range(1, 16):
        if df[f"p{i} estado"][index] != "activo":
            prestamo: list[str] = df[f"p{i} prestamo"][index].split("_")

            deuda_prestamo: int = int(prestamo[3])
            if deuda_prestamo > 0:
                deudas_en_prestamos += deuda_prestamo

            deuda_intereses: int = int(prestamo[1])
            if deuda_intereses > 0:
                deudas_por_intereses += deuda_intereses

    capital_total: int = capital_disponible - (
        deudas_por_fiador + deudas_en_prestamos + deudas_por_intereses
    )
    return capital_total


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
        "           usuario de el fondo                               tesorero",
    ]

    with open("text/carta_prestamo.txt", "w", encoding="utf-8") as f:
        f.write("".join(carta))
        f.close()


def rectificar_viavilidad(
    index: int, ranura: str, valor: int, ajustes: dict, df,
    fiadores: list[int] = list, deudas_con_fiadores: list[int] = list,
) -> (bool, str):
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

    if df[f"p{ranura} estado"][index] != "activo":
        return False, f"La ranura {ranura} no esta activa"
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
    index: int, ranura: str, valor: int, ajustes: dict, df,
    fiadores: list[int] = list, deudas_fiadores: list[int] = list,
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
    index: int, ranura: str, valor: int, ajustes: dict, df,
    fiadores: list[int] = list, deudas_fiadores: list[int] = list,
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


def realizar_anotacion(
    index: int, anotacion: str, ajustes: dict, df
) -> tuple[bool, str]:
    anotaciones: str = df["anotaciones de prestamos"][index]

    if "_" in anotacion:
        return False, "El simbolo '_' no puede estar en la anotacion"
    elif anotacion == "":
        return False, "La anotacion esta vacia"
    else:
        if anotaciones == "n":
            anotaciones = anotacion
        else:
            anotacion = "_" + anotacion
            anotaciones += anotacion

        df.loc[index, "anotaciones de prestamos"] = anotaciones

        df = df.loc[:, ~df.columns.str.contains("^Unnamed")]
        df.to_csv(ajustes["nombre df"])

        return True, ""


def eliminar_anotacion(index: int, pos: int, ajustes: dict, df):
    anotaciones: str = df["anotaciones de prestamos"][index]
    anotaciones: list[str] = anotaciones.split("_")

    if len(anotaciones) == 1:
        anotaciones = "n"
    else:
        anotaciones.pop(pos)
        anotaciones = "_".join(anotaciones)

    df.loc[index, "anotaciones de prestamos"] = anotaciones
    df = df.loc[:, ~df.columns.str.contains("^Unnamed")]
    df.to_csv(ajustes["nombre df"])


def modificar_anotacion(index: int, pos: int, new_elem: str, ajustes: dict, df):
    anotaciones: str = df["anotaciones de prestamos"][index]
    anotaciones: list[str] = anotaciones.split("_")

    if new_elem == "":
        anotaciones[pos] = "n"
    elif "_" in new_elem:
        st.error("El simbolo '_' no puede estar en la anotacion", icon="🚨")
        return 0
    else:
        anotaciones[pos] = new_elem

    anotaciones = "_".join(anotaciones)

    df.loc[index, "anotaciones de prestamos"] = anotaciones
    df = df.loc[:, ~df.columns.str.contains("^Unnamed")]
    df.to_csv(ajustes["nombre df"])


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

    realizar_anotacion(index, anotacion, ajustes, df)


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


def arreglar_asuntos(index: int, ajustes: dict, df) -> None:
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
