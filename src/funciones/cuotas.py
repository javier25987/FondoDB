import src.funciones.general as fg
import src.funciones.anotaciones as fa
import src.msql as msql
import streamlit as st
import sqlite3 as sql
import polars as pl
import datetime
import time

# ========================================================= Funciones generales

def descomprimir_to_list(comp: str) -> list[list[int, ], ]:
    if comp == "n":
        return []

    return list( # hacemos una lista con todos los elementos
        map(
            lambda x: list( # `list()` para convertir a lista
                map(
                    int,
                    x.split(":") # separamos cada llave entre index:valor
                )
            ),
            comp.split("_") # separamos todos los valores para indentalos
        )
    ) # -> [[2, 3], [2, 3], ...] ejemplo de la salida de esto


def descomprimir_to_array(comp: str) -> list[int]:
    result: list[int] = [0]*50

    if comp == "n":
        return result

    for idx, value in descomprimir_to_list(comp):
        result[idx] = value

    return result


def comprimir_of_array(array: list[int]) -> str:
    if sum(array) == 0:
        return "n"
    
    return "_".join(
        [
            f"{idx}:{value}"
            for idx, value in enumerate(array)
            if value != 0
        ]
    )


def obtener_bloqueos(index) -> list[int]:
    bloqueos = msql.obtener_valor("cuotas", "bloqueos", index)

    if bloqueos == "n":
        return []
    
    return [int(i) for i in bloqueos.split("_")]


def multas_gen(diff: int):
    count: int = 1
    while True:
        yield count
        if count < diff:
            count += 1


def rectificar_cuotas(index: int) -> None:
    semanas_revisadas: int = msql.obtener_valor("cuotas", "revisiones", index)

    if semanas_revisadas >= 50:
        return # no hacemos nada  si ya se revisaron todas las semanas

    calendario: list[datetime.datetime] = list(
        map(
            lambda x: datetime.datetime(*x),
            map(
                lambda y: map(int, y.split("/")),
                msql.obtener_ajuste("calendario", False).split("_"),
            ),
        )
    )
    fecha_actual = datetime.datetime.now()
    semanas_a_revisar: int = sum(map(lambda x: int(x < fecha_actual), calendario))

    if semanas_a_revisar > semanas_revisadas:
        # creamos una lista para registrar todas las semanas pagas
        array_semanas: list[int] = [0]*50
        # 1: pagas
        # 0: bloquedas o deudas (de igual manera multa)
        bloqueos: set[int,] = set(obtener_bloqueos(index))
        pagas: int = msql.obtener_valor("cuotas", "pagas", index)
        idx: int = 0

        while pagas > 0:
            if idx not in bloqueos:
                array_semanas[idx] = 1
                pagas -= 1

            idx += 1

        #contamos todas las deudas que debe tener la persona
        deudas: int = 0
        for i in range(semanas_a_revisar):
            if array_semanas[i] == 0:
                deudas += 1

        for i in bloqueos:
            if i < semanas_a_revisar:
                deudas -= 1

        # nos preparamos para contar todas las multas
        multas: list[int] = descomprimir_to_array(
            msql.obtener_valor("cuotas", "multas", index)
        )
        gen_multas = multas_gen(semanas_a_revisar - semanas_revisadas)
        cobrar_multas: bool = bool(msql.obtener_ajuste("cobrar multas"))

        # contamos todas las multas desde la semana actual hacia atras
        for i in range(semanas_a_revisar-1, -1, -1):
            if array_semanas[i] == 0 and cobrar_multas:
                multas[i] += next(gen_multas)

        # guardamos todos los valores
        msql.guardar_valor_n("cuotas", "adeudas", index, deudas)
        msql.guardar_valor_n("cuotas", "revisiones", index, semanas_a_revisar)

        msql.guardar_valor_t(
            "cuotas", "multas", index, comprimir_of_array(multas)
        )

# ========================================================= Inicio de la pagina

def abrir_usuario(index: int) -> tuple[bool, str]:
    if index < 0 or index > msql.obtener_ajuste("usuarios"):
        return False, "El numero de usuario esta fuera de rango"

    deudas: int = msql.obtener_valor("cuotas", "adeudas", index)
    if deudas > 3 and bool(msql.obtener_ajuste("anular usuarios")):
        msql.guardar_valor_n("informacion_general", "estado", index, 0)

    return True, ""


# ========================================================= Envio de datos para graficos

def obtener_datos_usuario(index) -> dict[str, any]: # type: ignore
    # obtenemos todos los datos necesarios
    calendario: list[str] = list(
        map(
            lambda x: x[:-3], # eliminamos la hoora de corte en el calendario
            msql.obtener_ajuste("calendario", False).split("_")
            # llamamos el calendario y lo separamos por semanas
        )
    )
    numeros: list[str] = list(map(str, range(1, 51)))
    cuotas_pagas: int = msql.obtener_valor("cuotas", "pagas", index)
    cuotas_adeud: int = msql.obtener_valor("cuotas", "adeudas", index)
    bloqueos: set[int, ] = set(obtener_bloqueos(index))

    cuotas_a_pagar: int = 50 - (cuotas_pagas + len(bloqueos))

    if cuotas_a_pagar > 10:
        cuotas_a_pagar = 10
    if cuotas_a_pagar < 0:
        cuotas_a_pagar = 0
    
    cuotas: list[str, ] = [""]*50

    for i in bloqueos:
        cuotas[i] = "🔒 bloc"

    cdx = 0

    while cuotas_pagas > 0:
        if cdx >= 50: # esto es por si se bloquea una semana cuando ya estan todas pagas o en deudas
            break
        if cuotas[cdx] == "":
            cuotas[cdx] = "✅ pago"

            cuotas_pagas -= 1
        cdx += 1

    while cuotas_adeud > 0:
        if cdx >= 50: # esto es por si se bloquea una semana cuando ya estan todas pagas o en deudas
            break
        if cuotas[cdx] == "":
            cuotas[cdx] = "🚨 debe"

            cuotas_adeud -= 1
        cdx += 1
    
    multas_list: list[list[int, ], ] = descomprimir_to_list(
        msql.obtener_valor("cuotas", "multas", index)
    )

    multas_pagas_list: list[list[int, ]] = descomprimir_to_list(
        msql.obtener_valor("cuotas", "multas_pagas", index)
    )

    multas: list[str, ] = [""]*50
    multas_pagas: list[str, ] = [""]*50

    multas_a_pagar: int = 0

    for idx, value in multas_list:
        multas[idx] = str(value)
        multas_a_pagar += value

    for idx, value in multas_pagas_list:
        multas_pagas[idx] = str(value)

    return {
        "nombre": msql.obtener_valor("informacion_general", "nombre", index).title(),
        "telefono": msql.obtener_valor("informacion_general", "telefono", index),
        "puestos": msql.obtener_valor("informacion_general", "puestos", index),
        "tabla1": pl.DataFrame(
            {
                "cuota №": numeros[:25],
                "fechas": calendario[:25],
                "cuotas": cuotas[:25],
                "multas vigentes": multas[:25],
                "multas pagas": multas_pagas[:25],
            }
        ),
        "tabla2": pl.DataFrame(
            {
                "cuota №": numeros[25:],
                "fechas": calendario[25:],
                "cuotas": cuotas[25:],
                "multas vigentes": multas[25:],
                "multas pagas": multas_pagas[25:],
            }
        ),
        "cuotas": cuotas_a_pagar,
        "multas": multas_a_pagar,
    }

# ========================================================= Pago de cuotas y multas

@st.dialog("Formulario de pago")
def formulario_de_pago(
    index: int, cuotas: int, multas: int, metodo_de_pago: str, usr_data: dict
) -> None:

    st.header(f"№ {index} - {usr_data["nombre"]}")
    st.divider()

    puestos: int = usr_data["puestos"]

    valor_cuota = msql.obtener_ajuste("valor cuota")
    valor_multa = msql.obtener_ajuste("valor multa")

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
        proceso_de_pago(
            index, cuotas, multas, usr_data, metodo_de_pago,
            total_cuotas, total_multas, total_a_pagar
        )
        time.sleep(1)
        st.rerun()
    

def proceso_de_pago(
        index: int, cuotas_a_pagar: int, multas_a_pagar: int, usr_data: dict,
        metodo_de_pago: str, total_cuotas: int, total_multas: int, total: int
) -> None:
    # pagar cuotas
        if cuotas_a_pagar != 0:
            pagar_n_cuotas(index, cuotas_a_pagar, total_cuotas)

        # pagar multas
        if multas_a_pagar != 0:
            pagar_n_multas(index, multas_a_pagar, total_multas)

        efect: bool = metodo_de_pago == "Efectivo"

        # hacer el cheque
        crear_nuevo_cheque(index, multas_a_pagar, cuotas_a_pagar, efect, usr_data)

        # revisar el metodo de pago
        if not efect:
            registrar_transferencia(index, total)

        # guardar el registro
        msql.registo(total)

        # hacer la nota
        anotacion: str = f"pago {cuotas_a_pagar} cuota(s) y {multas_a_pagar} multa(s), TOTAL:{total:,}"
        fa.realizar_anotacion(index, anotacion, 0, "GENERAL")


def pagar_n_cuotas(index: int, n: int, total: int) -> None:
    # pagar las cuotas
    msql.increment_int("cuotas", "pagas", index, n)

    # descontar las deudas
    cuotas_deuda: int = msql.obtener_valor("cuotas", "adeudas", index)

    if cuotas_deuda > 0:
        if n > cuotas_deuda:
            cuotas_deuda = 0
        else:
            cuotas_deuda -= n

        msql.guardar_valor_n("cuotas", "adeudas", index, cuotas_deuda)

    # cargamos a capital
    msql.increment_int("capital", "pago", index, total)


def descontar_n_multas(comp_multas: str, comp_multas_pagas, n: int) -> tuple[str, str]:
    multas = descomprimir_to_array(comp_multas)
    multas_pagas = descomprimir_to_array(comp_multas_pagas)

    for i in range(50):
        if multas[i] == 0:
            continue
        if n < 1:
            break

        if n >= multas[i]:
            multas_pagas[i] += multas[i]
            n -= multas[i]
            multas[i] = 0
        else:
            multas[i] -= n
            multas_pagas[i] += n
            break

    return comprimir_of_array(multas), comprimir_of_array(multas_pagas)


def pagar_n_multas(index: int, n: int, total: int) -> None:
    # NOTA: aca evito hacer una rectificacion de las multas a
    # pagar, ya que por defecto el programa muestra solo los
    # valores permitidos

    # pagamos las multas
    multas: str = msql.obtener_valor("cuotas", "multas", index)
    multas_pagas: str = msql.obtener_valor("cuotas", "multas_pagas", index)

    multas, multas_pagas = descontar_n_multas(multas, multas_pagas, n)

    msql.guardar_valor_t("cuotas", "multas", index, multas)
    msql.guardar_valor_t("cuotas", "multas_pagas", index, multas_pagas)

    # sumamos a 'aporte_a_multas'
    msql.increment_int("multas", "semanales", index, total)


def crear_nuevo_cheque(
    index: int, multas_pagadas: int, cuotas_pagadas: int, pago_efect: bool,
    usr_data: dict
) -> None:
    valor_cuota = msql.obtener_ajuste("valor cuota")
    valor_multa = msql.obtener_ajuste("valor multa")

    total_multas: int = multas_pagadas * valor_multa * usr_data["puestos"]
    total_cuotas: int = cuotas_pagadas * valor_cuota * usr_data["puestos"]

    cheque: str = f"""#let nombre = "{usr_data["nombre"]}"
#let numero = "{index}"
#let puestos = "{usr_data["puestos"]}"
#let multas_pagadas = "{multas_pagadas}"
#let valor_multa = "{valor_multa:,}"
#let total_multas = "{total_multas:,}"
#let cuotas_pagadas = "{cuotas_pagadas}"
#let valor_cuota = "{valor_cuota:,}"
#let total_cuotas = "{total_cuotas:,}"
#let Metodo_de_pago = "{"Efect" if pago_efect else "Transf"}"
#let total_pagado = "{total_multas + total_cuotas:,}"
#let fecha = "{datetime.datetime.now().strftime("%Y/%m/%d")}"
#let hora = "{datetime.datetime.now().strftime("%H:%M")}"
    """

    with open("src/text/var_cheque.typ", "w", encoding="utf_8") as f:
        f.write(cheque)
        f.close()

    fg.ejecutar_comando_git(["typst", "compile", "./src/text/cheque.typ"])

    # st.toast(
    #     "El documento ha sido creado, lo puede consultar en la seccion 'Documentos'",
    #     icon="✏️",
    # )


def registrar_transferencia(index: int, total: int) -> None:
    fecha: str = datetime.datetime.now().strftime("%Y/%m/%d - %H:%M")

    conexion = sql.connect("Fondo.db")
    cursor = conexion.cursor()

    cursor.execute(
        """
        INSERT INTO transferencias (id, fecha, monto)
        VALUES (?, ?, ?)
        """,
        (index, fecha, total),
    )

    conexion.commit()
    conexion.close()


def rectificar_boton_iniciar_pago(cuotas: int, multas: int, index: int):
    if cuotas == 0 and multas == 0:
        return False, "No se va a pagar nada"

    if not fg.rect_estado(index):
        return False, "El usuario no esta activo"

    return True, ""


def des_bloquear_semanas(index: int, bloc: int) -> None:
    bloqueos: list[int] = obtener_bloqueos(index)

    bloc -= 1

    if bloc in bloqueos:
        bloqueos.remove(bloc)
    else:
        bloqueos.append(bloc)

    bloqueos_guardar: str = "n"

    if len(bloqueos) > 0:
        bloqueos_guardar = "_".join(map(str, bloqueos))
        
    msql.guardar_valor_t("cuotas", "bloqueos", index, bloqueos_guardar)
