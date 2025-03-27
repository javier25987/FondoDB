import src.sql.conect as c_sql
import streamlit as st
import sqlite3 as sql
import pandas as pd
import datetime


# NOTA: ES IMPERATIVO HACER UNA FUNCION DE RECTIFICACION EN ESTE APARTADO


def contar_multas(s: str) -> int:
    return sum(int(i) for i in s if i != "n")


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


def pagar_n_cuotas(index: int, n: int) -> None:
    # pagar las cuotas
    c_sql.increment("cuotas", "pagas", index, n)

    # descontal las deudas
    cuotas_deuda: int = c_sql.obtener_cuotas("adeudas", index)

    if cuotas_deuda > 0:
        if n > cuotas_deuda:
            cuotas_deuda = 0
        else:
            cuotas_deuda -= n

        c_sql.guardar_valor("cuotas", "adeudas", index, cuotas_deuda)

    # cargamos a capital
    valor_cuota: int = c_sql.obtener_ajuste("valor cuota")
    puestos: int = c_sql.obtener_ig("puestos", index)

    total: int = valor_cuota * puestos * n
    c_sql.increment("informacion_general", "capital", index, total)


def descontar_n_multas(s: str, n: int):
    s: list[int, ...] = [
        int(i) if i != "n" else 0 for i in s
    ]
    i: int = 0

    for value in s:
        if n <= 0:
            break

        if value != 0:
            if value > n:
                value -= n
                n = 0
            else:
                n -= value
                value = 0

            s[i] = value

        i += 1

    return "".join(
        [str(i) if i != 0 else "n" for i in s]
    )


def pagar_n_multas(index: int, n: int) -> None:
    # NOTA: aca evito hacer una rectificacion de las multas a
    # pagar ya que por defecto el programa muestra solo los
    # valores permitidos

    # pagamos las multas
    multas: str = c_sql.obtener_cuotas("multas", index)
    multas = descontar_n_multas(multas, n)
    c_sql.guardar_valor_t("cuotas", "multas", index, multas)

    # sumamos a 'aporte_a_multas'
    valor_multa: int = c_sql.obtener_ajuste("valor multa")
    puestos: int = c_sql.obtener_ig("puestos", index)

    total: int = valor_multa * puestos * n
    c_sql.increment("informacion_general", "aporte_a_multas", index, total)


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
        f"> Valor cuota:{valor_cuota:,}\n",
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


def registrar_transferencia(index: int, total: int) -> None:
    fecha: str = datetime.datetime.now().strftime("%Y/%m/%d - %H:%M")

    conexion = sql.connect("Fondo.db")
    cursor = conexion.cursor()

    cursor.execute(
        """
        INSERT INTO transferencias (id, fecha, monto)
        VALUES (?, ?, ?)
        """, (index, fecha, total)
    )

    conexion.commit()
    conexion.close()


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

    total_a_pagar: int = total_multas + total_cuotas

    st.write(f"Total neto a pagar: {total_a_pagar:,}")
    st.divider()

    if st.button("Aceptar pago"):
        # pagar cuotas
        if cuotas != 0:
            pagar_n_cuotas(index, cuotas)

        # pagar multas
        if multas != 0:
            pagar_n_multas(index, multas)

        efect: bool = metodo_de_pago == "Efectivo"

        # hacer el cheque
        crear_nuevo_cheque(index, multas, cuotas, efect)

        # revisar el metodo de pago
        if not efect:
            registrar_transferencia(index, total_a_pagar)

        # guardar el registro
        c_sql.registo(total_a_pagar)

        st.rerun()
