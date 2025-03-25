import src.sql.conect as c_sql
import streamlit as st
import pandas as pd
import datetime


def contar_multas(s: str) -> int:
    return sum(int(i) for i in s if i != "n")


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


def abrir_usuario(index: int) -> (bool, str):
    if 0 > index >= c_sql.obtener_ajuste("usuarios"):
        return False, "El numero de usuario esta fuera de rango"

    estado_usuario: bool = bool(
        c_sql.obtener_ig("estado", index)
    )
    if not estado_usuario:
        return False, f"El usuario № {index} no esta activo"

    return True, ""


def tablas_para_cuotas_y_multas(index: int):
    funct = lambda x: " " if x == "n" else x

    calendario: list[str] = list(
        map(
            lambda x: x[:-3],
            c_sql.obtener_ajuste("calendario", False).split("_")
        )
    )

    multas: str = c_sql.obtener_cuotas( "multas", index)
    cuotas_pagas: int = c_sql.obtener_cuotas( "pagas", index)
    cuotas_adeud: int = c_sql.obtener_cuotas( "adeudas", index)

    cuotas: str = ["✅ pago"] * cuotas_pagas + ["🚨 debe"] * cuotas_adeud

    cuotas += [""]*(50 - len(cuotas))

    numeros: list[str] = list(map(str, range(1, 51)))
    multas: list[str] = list(map(funct, list(multas)))

    print(
        f"numeros: {len(numeros)} _ fechas: {len(calendario)} _ cuotas: {len(cuotas)} _ multas: {len(multas)}"
    )

    return pd.DataFrame(
        {
            "cuota №": numeros[:25],
            "fechas": calendario[:25],
            "cuotas": cuotas[:25],
            "multas": multas[:25],
        }
    ), pd.DataFrame(
        {
            "cuota №": numeros[25:],
            "fechas": calendario[25:],
            "cuotas": cuotas[25:],
            "multas": multas[25:],
        }
    )


def crear_nuevo_cheque(
    index: int, multas_pagadas: int,
    cuotas_pagadas: int, pago_efect: bool
) -> None:

    nombre: str = c_sql.obtener_ig("nombre", index)
    if len(nombre) > 17:
        nombre = nombre[:17]

    puestos: int = c_sql.obtener_ig("puestos", index)

    valor_cuota = c_sql.obtener_ajuste("valor cuota")
    valor_multa = c_sql.obtener_ajuste("valor multa")

    total_multas: int = multas_pagadas * valor_multa * puestos
    total_cuotas: int = cuotas_pagadas * valor_cuota * puestos

    cheque: list[str, ...] = [
        "===========================\n",
        "=                         =\n",
        "=    FONDO SAN JAVIER     =\n",
        "=                         =\n",
        "===========================\n",
        f"> Nombre:{nombre}\n",
        f"> Numero:{index}\n",
        f"> Puestos:{puestos}\n",
        "===========================\n",
        f"> Multas pagadas:{multas_pagadas}\n",
        f"> Valor multa:{valor_multa:,}\n",
        f"> TOTAL multas:{total_multas:,}\n",
        "===========================\n",
        f"> Cuotas pagadas:{cuotas_pagadas}\n",
        f"> Valor cuota:{valor_cuota}\n",
        f"> TOTAL cuotas:{total_cuotas:,}\n",
        "===========================\n",
        f"> Metodo de pago:{"Efect" if pago_efect else "Transf"}\n",
        f"> Total pagado:{total_multas + total_cuotas:,}\n",
        "===========================\n",
        f"> Fecha:{datetime.datetime.now().strftime("%Y/%m/%d")}\n",
        f"> Hora:{datetime.datetime.now().strftime("%H:%M")}\n",
        "===========================",
    ]

    with open("src/text/cheque_de_cuotas.txt", "w", encoding="utf_8") as f:
        f.write("".join(cheque))
        f.close()


@st.dialog("Formulario de pago")
def formulario_de_pago(
    index: int, cuotas: int, multas: int, metodo_de_pago: str
) -> None:
    st.header(f"№ {index} - {
        c_sql.obtener_ig("nombre", index)
    }")
    st.divider()

    puestos: int = c_sql.obtener_ig("puestos", index)

    valor_cuota = c_sql.obtener_ajuste("valor cuota")
    valor_multa = c_sql.obtener_ajuste("valor multa")

    st.write(f"Puestos: {puestos}")
    st.divider()

    st.write(f"Cuotas a pagar: {cuotas}")
    st.write(f"Valor de cuota por puesto: {valor_cuota:,}")

    total_cuotas: int = cuotas * valor_cuota * puestos
    st.write(f"Total en cuotas: {total_cuotas:,}")
    st.divider()

    st.write(f"Multas a pagar: {multas}")
    st.write(f"Valor de multa por puesto: {valor_multa:,}")
    total_multas = multas * valor_multa * puestos
    st.write(f"Total en multas: {total_multas:,}")
    st.divider()

    total_a_anotar: int = total_multas + total_cuotas

    st.write(f"Total neto a pagar: {'{:,}'.format(total_a_anotar)}")
    st.divider()

    if st.button("Aceptar pago"):
        # pagar cuotas
        # pagar multas
        # hacer el cheque
        # revisar el metodo de pago
        st.rerun()
