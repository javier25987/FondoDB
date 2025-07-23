import src.funciones.general as fg
import src.sql.conect as c_sql
import streamlit as st
import sqlite3 as sql
import pandas as pd
import datetime


def sumar_una_multa(s: str, i: int) -> str:
    s = list(s)

    value = 0 if s[i] == "n" else int(s[i])
    value += 1

    s[i] = str(value)

    return "".join(s)


def rectificar_cuotas(index: int) -> None:
    calendario: list[datetime.datetime] = list(
        map(
            lambda x: datetime.datetime(*x),
            map(
                lambda y: map(int, y.split("/")),
                c_sql.obtener_ajuste("calendario", False).split("_")
            ),
        )
    )

    fecha_actual = datetime.datetime.now()

    semanas_a_revisar: int = sum(
        map(lambda x: int(x < fecha_actual), calendario)
    )

    semanas_revisadas: int = c_sql.obtener_cuotas("revisiones", index)

    if semanas_a_revisar > semanas_revisadas:
        multas: str = c_sql.obtener_cuotas("multas", index)
        multas = multas_comp_str(multas)

        cobrar_multas: bool = bool(c_sql.obtener_ajuste("cobrar multas"))
        #anular_usuarios: bool = bool(c_sql.obtener_ajuste("anular usuarios"))
        pagas: int = c_sql.obtener_cuotas("pagas", index)
        deudas: int = 0

        for i in range(50):
            if calendario[i] <= fecha_actual:
                if i >= pagas:
                    if cobrar_multas:
                        multas = sumar_una_multa(multas, i)
                    deudas += 1
            else:
                break

        c_sql.guardar_valor("cuotas", "adeudas", index, deudas)
        c_sql.guardar_valor("cuotas", "revisiones", index, semanas_a_revisar)

        multas = multas_str_comp(multas)
        c_sql.guardar_valor_t("cuotas", "multas", index, multas)


def contar_multas(comp: str) -> int:
    if comp == "n":
        return 0

    des_comp = list(
        map(
            lambda x: list(
                map(int, x.split(":"))
            ),
        comp.split("_")
        )
    )

    return sum(j for _, j in des_comp)


def abrir_usuario(index: int) -> tuple[bool, str]:
    if 0 > index >= c_sql.obtener_ajuste("usuarios"):
        return False, "El numero de usuario esta fuera de rango"

    rectificar_cuotas(index)

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
    multas = multas_comp_str(multas)

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


def descontar_n_multas(comp: str, n: int) -> str:

    des_comp = list(
        map(
            lambda x: list(
                map(int, x.split(":"))
            ),
        comp.split("_")
        )
    )

    for i in range(len(des_comp)):
        if des_comp[i][1] > n:
            des_comp[i][1] -= n
            break
        else:
            n -= des_comp[i][1]
            des_comp[i][1] = 0

    salida = [
        f"{i}:{j}" for i, j in des_comp if j != 0
    ]

    return "_".join(salida) if len(salida) != 0 else "n"


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

    cheque: list[str] = [
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


def multas_comp_str(comp: str) -> str:

    if comp == "n":
        return "n"*50

    des_comp = list(
        map(
            lambda x: list(
                map(int, x.split(":"))
            ),
            comp.split("_")
        )
    )

    result = ["n"]*50

    for i, j in des_comp:
        result[i] = str(j)

    return "".join(result)


def multas_str_comp(multas: str) -> dict[int: int]:

    result = [
        f"{i}:{multas[i]}"
        for i in range(len(multas))
        if multas[i] != "n"
    ]

    return "_".join(result) if len(result) != 0 else "n"

def rectificar_boton_iniciar_pago(cuotas: int, multas: int, index: int):
    if cuotas == 0 and multas == 0:
        return False, "No se va a pagar nada"

    if not fg.rect_estado(index):
        return False, "El usuario no esta activo"

    return True, ""
