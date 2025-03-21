import streamlit as st
import pandas as pd
import datetime
import json


def sumar_una_multa(s: list, semana: int = 0) -> list:
    valor_semana: str = s[semana]

    if valor_semana == "n":
        s[semana] = "1"
    else:
        k: str = str(int(valor_semana) + 1)
        s[semana] = k
    return s


def arreglar_asuntos(index: int, ajustes: dict, df) -> None:
    cuotas: list = list(df["cuotas"][index])
    multas: list = list(df["multas"][index])

    semanas_revisadas: int = int(df["revisiones"][index])

    calendario: list[datetime.datetime] = list(
        map(
            lambda x: datetime.datetime(*x),
            map(lambda y: map(int, y.split("/")), ajustes["calendario"].split("_")),
        )
    )

    fecha_actual: datetime = datetime.datetime.now()

    semanas_a_revisar: int = sum(
        map(lambda x: 1 if x < fecha_actual else 0, calendario)
    )

    if semanas_a_revisar > semanas_revisadas:
        for i in range(50):
            if calendario[i] <= fecha_actual:
                if cuotas[i] != "p":
                    if ajustes["cobrar multas"]:
                        multas = sumar_una_multa(multas, i)
                    cuotas[i] = "d"
            else:
                break

        df.loc[index, "cuotas"] = "".join(cuotas)
        df.loc[index, "multas"] = "".join(multas)
        df.loc[index, "revisiones"] = semanas_a_revisar

        df = df.loc[:, ~df.columns.str.contains("^Unnamed")]

        df.to_csv(ajustes["nombre df"])


def contar_multas(s: str) -> int:
    return sum(int(i) for i in s if i != "n")


def pagar_n_cuotas_terorero(s_c: str, n: int, s_t: str, t: str) -> str:
    cuotas_pagas: int = s_c.count("p")

    if cuotas_pagas == 50:
        return s_c

    if 50 - cuotas_pagas < n:
        return s_c

    s_c: list[str] = list(s_c)
    s_t: list[str] = list(s_t)
    i: int = 0
    while n > 0:
        if s_c[i] != "p":
            s_c[i] = "p"
            s_t[i] = t
            n -= 1
        i += 1

    return "".join(s_c), "".join(s_t)


def pagar_n_multas(s: str, n: int):
    multas_a_pagar: int = contar_multas(s)

    if multas_a_pagar == 0:
        return s

    if n > multas_a_pagar:
        return s

    s: list[str] = list(s)
    i: int = 0
    for value in s:
        if n <= 0:
            break
        if value != "n":
            value: int = int(value)
            if value > n:
                value -= n
                n = 0
                s[i] = str(value)
            else:
                n -= value
                value = "n"
                s[i] = value
        i += 1

    return "".join(s)


def abrir_usuario(index: int, ajustes: dict, df) -> (bool, str):
    if 0 > index >= ajustes["usuarios"]:
        return False, "El numero de usuario esta fuera de rango"

    if df["estado"][index] != "activo":
        return False, f"El usuario № {index} no esta activo"

    arreglar_asuntos(index, ajustes, df)

    df = pd.read_csv(ajustes["nombre df"])

    if ajustes["anular usuarios"] and (df["multas"][index].count("n") < 47):
        df.loc[index, "estado"] = "no activo"
        df = df.loc[:, ~df.columns.str.contains("^Unnamed")]
        df.to_csv(st.session_state.nombre_df)
        return False, "El usuario ha sido desactivado"

    return True, ""


def r_cuotas(s: str) -> str:
    match s:
        case "p":
            return "✅ pago"
        case "d":
            return "🚨 debe"
        case _:
            return " "


def tablas_para_cuotas_y_multas(index: int, ajustes: dict, df):
    funct = lambda x: " " if x == "n" else x

    calendario: list[str] = list(
        map(lambda x: x[:-3], ajustes["calendario"].split("_"))
    )
    numeros: list[str] = list(map(str, range(1, 51)))
    multas: list[str] = list(map(funct, list(df["multas"][index])))
    cuotas: list[str] = list(map(r_cuotas, list(df["cuotas"][index])))
    tesoreros: list[str] = list(map(funct, list(df["tesorero"][index])))
    return pd.DataFrame(
        {
            "cuota №": numeros[:25],
            "fechas": calendario[:25],
            "cuotas": cuotas[:25],
            "tesorero": tesoreros[:25],
            "multas": multas[:25],
        }
    ), pd.DataFrame(
        {
            "cuota №": numeros[25:],
            "fechas": calendario[25:],
            "cuotas": cuotas[25:],
            "tesorero": tesoreros[25:],
            "multas": multas[25:],
        }
    )


def crear_nuevo_cheque(
    nombre: str = "",
    numero: int = 0,
    multas_pagadas: int = 0,
    valor_multas: int = 0,
    cuotas_pagadas: int = 0,
    valor_cuotas: int = 0,
    puestos: int = 0,
    tesorero: int = 1,
) -> None:
    cheque: list[str] = [
        "===========================",
        "=                         =",
        "=    FONDO SAN JAVIER     =",
        "=                         =",
        "===========================",
        "> Nombre:",
        "> Numero:",
        "> Puestos:",
        "===========================",
        "> Multas pagadas:",
        "> Valor multa:",
        "> TOTAL multas:",
        "===========================",
        "> Cuotas pagadas:",
        "> Valor cuota:",
        "> TOTAL cuotas:",
        "===========================",
        "> Tesorero:",
        "> Total pagado:",
        "===========================",
        "> Fecha:",
        "> Hora:",
        "===========================",
    ]

    with open("text/cheque_de_cuotas.txt", "w", encoding="utf_8") as f:
        f.write("")
        f.close()

    if len(nombre) > 17:
        nombre = nombre[:18]

    cheque[5] += nombre
    cheque[6] += str(numero)
    cheque[9] += str(multas_pagadas)
    cheque[10] += str("{:,}".format(valor_multas))

    total_multas = multas_pagadas * valor_multas * puestos
    cheque[11] += str("{:,}".format(total_multas))

    cheque[13] += str(cuotas_pagadas)
    cheque[14] += str("{:,}".format(valor_cuotas))
    cheque[7] += str(puestos)

    total_cuotas = cuotas_pagadas * valor_cuotas * puestos
    cheque[15] += str("{:,}".format(total_cuotas))

    cheque[17] += str(tesorero)

    total_pagado = total_cuotas + total_multas
    cheque[18] += str("{:,}".format(total_pagado))

    cheque[20] += str(datetime.datetime.now().strftime("%Y.%m.%d"))
    cheque[21] += str(datetime.datetime.now().strftime("%H:%M"))

    cheque = list(map(lambda x: x + "\n", cheque))
    cheque[-1] = cheque[-1].strip()

    with open("text/cheque_de_cuotas.txt", "w", encoding="utf_8") as f:
        f.write("".join(cheque))
        f.close()


@st.dialog("Formulario de pago")
def formulario_de_pago(
    index: int, cuotas: int, multas: int, tesorero: str,
    modo_de_pago: str, ajustes: dict, banco: dict, df
) -> None:
    st.header(f"№ {index} - {df['nombre'][index].title()}")
    st.divider()

    puestos: int = int(df["puestos"][index])
    capital_actual: int = int(df["capital"][index])
    multas_aportes_actual: int = int(df["aporte a multas"][index])
    cuotas_actual: str = df["cuotas"][index]
    multas_actual: str = df["multas"][index]
    tesorero_actual: str = df["tesorero"][index]

    st.write(f"Puestos: {puestos}")
    st.divider()

    st.write(f"Cuotas a pagar: {cuotas}")
    st.write(f"Valor de cuota por puesto: {'{:,}'.format(ajustes['valor cuota'])}")

    total_cuotas: int = cuotas * ajustes["valor cuota"] * puestos
    st.write(f"Total en cuotas: {'{:,}'.format(total_cuotas)}")
    st.divider()

    st.write(f"Multas a pagar: {multas}")
    st.write(f"Valor de multa por puesto: {'{:,}'.format(ajustes['valor multa'])}")
    total_multas = multas * ajustes["valor multa"] * puestos
    st.write(f"Total en multas: {'{:,}'.format(total_multas)}")
    st.divider()

    total_a_anotar: int = total_multas + total_cuotas

    st.write(f"Total neto a pagar: {'{:,}'.format(total_a_anotar)}")
    st.write(f"Se paga a el tesorero: {tesorero}")
    st.divider()

    if st.button("Aceptar pago"):
        cuotas_actual, tesorero_actual = pagar_n_cuotas_terorero(
            cuotas_actual, cuotas, tesorero_actual, tesorero
        )
        multas_actual = pagar_n_multas(multas_actual, multas)
        capital_actual += total_cuotas
        multas_aportes_actual += total_multas

        df.loc[index, "cuotas"] = cuotas_actual
        df.loc[index, "multas"] = multas_actual
        df.loc[index, "tesorero"] = tesorero_actual
        df.loc[index, "capital"] = capital_actual
        df.loc[index, "aporte a multas"] = multas_aportes_actual

        crear_nuevo_cheque(
            df["nombre"][index].title(),
            index,
            multas,
            ajustes["valor multa"],
            cuotas,
            ajustes["valor cuota"],
            puestos,
            tesorero,
        )

        if modo_de_pago == "Transferencia":
            anotar_pago_por_banco(index, total_a_anotar, banco, df)

        df = df.loc[:, ~df.columns.str.contains("^Unnamed")]
        df.to_csv(ajustes["nombre df"])

        st.rerun()


def realizar_anotacion(
    index: int, anotacion: str, ajustes: dict, df
) -> tuple[bool, str]:
    anotaciones: str = df["anotaciones de cuotas"][index]

    if "_" in anotacion:
        return False, "El simbolo '_' no puede estar en la anotacion"
    if anotacion == "":
        return False, "La anotacion esta vacia"

    if anotaciones == "n":
        anotaciones = anotacion
    else:
        anotacion = "_" + anotacion
        anotaciones += anotacion

    df.loc[index, "anotaciones de cuotas"] = anotaciones
    df = df.loc[:, ~df.columns.str.contains("^Unnamed")]
    df.to_csv(ajustes["nombre df"])

    return True, ""


def eliminar_anotacion(index: int, pos: int, ajustes: dict, df):
    anotaciones: str = df["anotaciones de cuotas"][index]
    anotaciones: list[str] = anotaciones.split("_")

    if len(anotaciones) == 1:
        anotaciones = "n"
    else:
        anotaciones.pop(pos)
        anotaciones = "_".join(anotaciones)

    df.loc[index, "anotaciones de cuotas"] = anotaciones
    df = df.loc[:, ~df.columns.str.contains("^Unnamed")]
    df.to_csv(ajustes["nombre df"])


def modificar_anotacion(index: int, pos: int, new_elem: str, ajustes: dict, df):
    anotaciones: str = df["anotaciones de cuotas"][index]
    anotaciones: list[str] = anotaciones.split("_")

    if new_elem == "":
        anotaciones[pos] = "n"
    elif "_" in new_elem:
        st.error("El simbolo '_' no puede estar en la anotacion", icon="🚨")
        return 0
    else:
        anotaciones[pos] = new_elem

    anotaciones = "_".join(anotaciones)

    df.loc[index, "anotaciones de cuotas"] = anotaciones
    df = df.loc[:, ~df.columns.str.contains("^Unnamed")]
    df.to_csv(ajustes["nombre df"])


def anotar_pago_por_banco(index: int, monto: int, banco: dict, df) -> None:
    anotacion: dict = {
        "fecha": datetime.datetime.now().strftime("%Y/%m/%d - %H:%M"),
        "quien": index,
        "cuanto": monto,
    }

    id_anotacion: str = f"ID: {index}_{banco['id']}"

    banco["id"] += 1
    banco[id_anotacion] = anotacion
    banco["dinero pagado"] += monto

    with open("banco.json", "w") as f:
        json.dump(banco, f)
        f.close()


def buscar_transferencia(index: int, banco: dict) -> dict:
    referencia: str = f"{index}_"
    resultado: dict = {}

    for key in banco:
        if referencia in key:
            resultado[key] = banco[key]

    return resultado


def escribir_cuotas_y_multas(index: int, ajustes: dict, df):
    funct = lambda x: " " if x == "n" else x

    general_list: list[list[str]] = [
        list(  # numero
            map(str, range(1, 51))
        ),
        list(  # fecha
            map(lambda x: x[:-3], ajustes["calendario"].split("_"))
        ),
        list(  # cuotas
            map(r_cuotas, list(df["cuotas"][index]))
        ),
        list(  # tesorero
            map(funct, list(df["tesorero"][index]))
        ),
        list(  # multas
            map(funct, list(df["multas"][index]))
        ),
    ]

    names_list: list[str] = ["Cuota №", "Fechas", "Cuotas", "Tesorero", "Multas"]

    cols_w = st.columns([0.49, 0.02, 0.49])
    step: int = 0
    for col in [cols_w[0], cols_w[2]]:
        with col:
            col_count: int = 0
            for sub_col in st.columns(5):
                with sub_col:
                    st.markdown(f"**{names_list[col_count]}**")
                    for i in range(25):
                        st.markdown(f"{general_list[col_count][i + step]}")
                    col_count += 1
        step += 25
