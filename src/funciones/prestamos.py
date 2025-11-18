import src.funciones.anotaciones as fa
import src.funciones.general as fg
import src.msql as msql
import streamlit as st
import sqlite3 as sql
import polars as pl
import datetime


def abrir_usuario(index: int) -> tuple[bool, str]:
    if index < 0 or index > msql.obtener_ajuste("usuarios"):
        return False, "El numero de usuario esta fuera de rango"

    return True, ""


def rectificar_prestamos(index: int) -> None:
    conexion = sql.connect("Fondo.db")
    cursor = conexion.cursor()

    cursor.execute(
        """
        SELECT
            ph.codigo,
            ph.fechas_de_pago,
            ph.revisiones
        FROM prestamos_hechos ph
        WHERE ph.idx = ? AND ph.estado_de_pago = 1
        """,
        (index, )
    )

    datos = cursor.fetchall()

    if len(datos) == 0:
        conexion.close()
        return

    fecha_actual = datetime.datetime.now()

    for codigo, fechas, revisiones in datos:
        fechas_pasadas: int = sum(
            map(
                lambda x: x < fecha_actual,
                map(
                    lambda y: datetime.datetime(*map(int, y.split("/"))),
                    fechas.split("_")
                ),
            )
        )

        if fechas_pasadas > revisiones:
            print(f"prestamo {codigo}")
            for _ in range(fechas_pasadas - revisiones):
                cursor.execute(
                    """
                    UPDATE prestamos_hechos
                    SET
                        interes_vencido = interes_vencido + (
                            deuda * interes
                        ) / 100,
                        revisiones = ?
                    WHERE codigo = ?
                    """,
                    (fechas_pasadas, codigo)
                )

    conexion.commit()
    conexion.close()

# ======================================================================================================================
# ENVIO DE DATOS

def obtener_datos_usuario(index: int) -> dict:
    return {
        "nombre": msql.obtener_valor("informacion_general", "nombre", index).title(),
    }


def crear_tablas_de_prestamos(index: int):
    conexion = sql.connect("Fondo.db")
    cursor = conexion.cursor()

    cursor.execute(
        """
        SELECT 
            ph.codigo, ph.estado_de_pago, ph.interes,
            ph.interes_vencido, ph.interes_generado,
            ph.deuda, ph.monto, ph.fechas_de_pago,
            ph.fiadores, ph.deuda_con_fiadores,
            ph.motivo 
        FROM prestamos_hechos ph
        WHERE ph.idx = ?
        """,
        (index, )
    )

    prestamos = cursor.fetchall()
    conexion.close()

    return [
        {
            "codigo": prestamo[0],
            "estado": "ACTIVO ⏳" if bool(prestamo[1]) else "PAGO ✅",
            "tabla_interes": pl.DataFrame({
                "Interes": [f"{prestamo[2]}%"],
                "Intereses vencidos": [f"{prestamo[3]:,}"],
                "Interes generado": [f"{prestamo[4]:,}"],
            }),
            "tabla_deuda": pl.DataFrame({
                "Deuda": [f"{prestamo[5]:,}"],
                "Monto": [f"{prestamo[6]:,}"],
                "% Pago": [f"{int((1 - prestamo[5]/prestamo[6])*100)}%"],
            }),
            "fechas": pl.DataFrame({"Fechas de pago": prestamo[7].split("_")}),
            "tabla_fiadores": pl.DataFrame(
                {"Fiadores": prestamo[8].split("#"), "Deudas con fiadores": prestamo[9].split("#")}
            ),
            "deuda": prestamo[3] + prestamo[5],
            "motivo": prestamo[10]
        }
        for prestamo in prestamos # esto es solo un list conprention
    ]


def obtener_codigos(index: int) -> list[int]:
    conexion = sql.connect("Fondo.db")
    cursor = conexion.cursor()

    cursor.execute(
        f"""
        SELECT 
            ph.codigo
        FROM prestamos_hechos ph
        WHERE 
            ph.idx = {index} AND 
            ph.deuda + ph.interes_vencido != 0
        """
    )

    datos = cursor.fetchall()
    conexion.close()

    return [i[0] for i in datos]


def capital_disponible_mostrar(index: int) -> dict[str, int|str|pl.DataFrame]:
    capital: int = msql.obtener_valor("capital", "pago", index)
    capital_disponible: int = int(
        capital * msql.obtener_ajuste("capital usable") / 100
    )

    deudas_por_fiador: int = msql.obtener_valor("prestamos", "deudas_por_fiador", index)
    fiador_de: str = msql.obtener_valor("prestamos", "fiador_de", index)

    conexion = sql.connect("Fondo.db")
    query: str = f"""
    SELECT 
        ph.codigo AS Codigo,
        ph.interes_vencido AS Interes,
        ph.deuda AS Deuda
    FROM prestamos_hechos ph
    WHERE ph.idx = {index}
    """

    df: pl.DataFrame = pl.read_database(query, conexion)
    conexion.close()

    total_interes: int = df["Interes"].sum()
    total_deuda: int = df["Deuda"].sum()

    if total_interes is None:
        total_interes = 0

    if total_deuda is None:
        total_deuda = 0

    total_disponible: int = capital_disponible - (
        deudas_por_fiador + total_deuda + total_interes
    )

    return {
        "capital": capital,
        "capital_disponible": capital_disponible,
        "deudas_por_fiador": deudas_por_fiador,
        "fiador_de": fiador_de,
        "tabla": df,
        "total_deuda": total_deuda,
        "total_interes": total_interes,
        "total_disponible": total_disponible
    }

# ======================================================================================================================
# PAGAR PRESTAMOS

def obtener_deuda_total(codigo: int) -> int:
    conexion = sql.connect("Fondo.db")
    cursor = conexion.cursor()

    cursor.execute(
        """
        SELECT
            (ph.interes_vencido + ph.deuda)
        FROM prestamos_hechos ph
        WHERE ph.codigo = ?
        """, (codigo, )
    )
    dato = cursor.fetchall()[0][0]
    conexion.close()

    return dato


def obtener_datos_prestamo(codigo: int) -> list[str|int]:
    conexion = sql.connect("Fondo.db")
    cursor = conexion.cursor()

    cursor.execute(
        """
        SELECT 
            ph.deuda,
            ph.interes_vencido,
            ph.fiadores,
            ph.deuda_con_fiadores 
        FROM prestamos_hechos ph
        WHERE ph.codigo = ?
        """, (codigo, )
    )
    dato = cursor.fetchall()[0]
    conexion.close()

    return dato


def obtener_valor(columna: str, codigo: int) -> str | int:
    conexion = sql.connect("Fondo.db")
    cursor = conexion.cursor()

    cursor.execute(
        f"""
        SELECT {columna}
        FROM prestamos_hechos
        WHERE codigo = {codigo}
        """
    )

    valor = cursor.fetchall()[0][0]
    conexion.close()

    return valor


def guardar_valor(columna: str, codigo: int, nuevo_valor: int | str) -> None:
    conexion = sql.connect("Fondo.db")
    cursor = conexion.cursor()

    cursor.execute(
        f"""
        UPDATE prestamos_hechos
        SET {columna} = ?
        WHERE codigo = {codigo}
        """, (nuevo_valor, )
    )

    conexion.commit()
    conexion.close()


def increment_int(columna: str, codigo: int, incremento: int) -> None:
    conexion = sql.connect("Fondo.db")
    cursor = conexion.cursor()

    cursor.execute(
        f"""
        UPDATE prestamos_hechos
        SET {columna} = {columna} + {incremento}
        WHERE codigo = {codigo}
        """
    )

    conexion.commit()
    conexion.close()


def rectificar_pago(codigo: int, monto: int, idx: int) -> tuple[bool, str]:
    deuda = obtener_deuda_total(codigo)

    if monto <= 0:
        return False, "No se puede pagar cero o menos"

    if monto > deuda:
        return False, "No se puede pagar mas de lo que se debe"

    if not fg.rect_estado(idx):
        return False, "El usuario no esta activo"

    return True, ""


@st.dialog("Pago de prestamo")
def formato_de_abono(index: int, monto: int, codigo: int) -> None:
    deuda: int = obtener_deuda_total(codigo)

    st.title(f"Codigo del prestamo: {codigo}")

    st.divider()
    st.subheader("Resumen:")
    st.table(
        {
            "Concepto": ["Deuda actual", "Monto a pagar"],
            "Valor": [f"{deuda:,}", f"{monto:,}"],
        }
    )

    st.markdown(f"## Deuda despues del pago: *{deuda - monto:,}*")

    st.divider()
    if st.button("Pagar", key="que haces aca?"):
        abonar_a_prestamo(index, monto, codigo)
        st.rerun()


def abonar_a_prestamo(index: int, monto: int, codigo: int) -> None:
    # hacer anotacion
    fa.realizar_anotacion(
        index,
        f"se ha pagado {monto:,} al prestamo numero {codigo}",
        0,
        "GENERAL"
    )

    # obtener datos
    deuda, interes, fiadores, deuda_con_fiadores = obtener_datos_prestamo(codigo)

    # rectificar_inactividad
    if deuda + interes <= monto:
        guardar_valor("estado_de_pago", codigo, 0)

    # pagar intereses
    if interes > 0:
        if monto > interes:
            guardar_valor("interes_vencido", codigo, 0)
            increment_int("interes_generado", codigo, interes)
            monto -= interes
        else:
            increment_int("interes_vencido", codigo, -monto)
            increment_int("interes_generado", codigo, monto)
            return

    # pago de fiadores
    monto_a_fiadores = monto

    if fiadores != "n":
        fiadores_l: list[int] = list(map(int, fiadores.split("#")))
        deuda_con_fiadores_l: list[int] = list(map(int, deuda_con_fiadores.split("#")))

        for idx, fiador in enumerate(fiadores_l):
            if fiador != 1976:
                if deuda_con_fiadores_l[idx] > monto_a_fiadores:
                    deuda_con_fiadores_l[idx] -= monto_a_fiadores
                    descuento = monto_a_fiadores
                else:
                    descuento = deuda_con_fiadores_l[idx]
                    monto_a_fiadores -= deuda_con_fiadores_l[idx]
                    deuda_con_fiadores_l[idx] = 0

                msql.increment_int("prestamos", "deudas_por_fiador", fiador, -descuento)

            if monto_a_fiadores <= 0:
                break

        deuda_con_fiadores = "#".join(map(str, deuda_con_fiadores_l))
        guardar_valor("deuda_con_fiadores", codigo, deuda_con_fiadores)

    # pago de deuda
    increment_int("deuda", codigo, -monto)

# ======================================================================================================================
# HACER PRESTAMOS

def capital_disponible_usr(index: int) -> int:
    if index == 1976:
        return 1_000_000_000

    conexion = sql.connect("Fondo.db")
    cursor = conexion.cursor()

    cursor.execute(
        f"""
        SELECT
            c.pago * (
                SELECT a.valor_n
                FROM ajustes a 
                WHERE a.ajuste = 'capital usable'
            )/100 - (
                SELECT 
                    IFNULL(SUM(ph.deuda + ph.interes_vencido), 0)
                FROM prestamos_hechos ph
                WHERE ph.idx = {index}
            ) - (
                SELECT p.deudas_por_fiador
                FROM prestamos p
                WHERE p.id = {index}
            )
        FROM capital c
        WHERE c.id = {index}
        """
    )
    capital: int = cursor.fetchall()[0][0]
    conexion.close()

    return capital


def calendario_de_meses(fecha_actual: datetime.datetime = datetime.datetime.now()) -> str:
    fecha_de_cierre: datetime.datetime = datetime.datetime(
        *map(
            int,
            msql.obtener_ajuste("fecha de cierre", False).split("/")
        )
    )

    fechas: list = []

    dias_memoria: int = fecha_actual.day
    while True:
        dias_uso: int = dias_memoria
        while True:
            try:
                temporal_ahora: datetime.datetime = datetime.datetime(
                    fecha_actual.year + (fecha_actual.month + 1 > 12),
                    fecha_actual.month % 12 + 1,
                    dias_uso
                )
                fecha_actual = temporal_ahora
                break
            except ValueError:
                dias_uso -= 1

        if fecha_actual < fecha_de_cierre:
            fechas.append(fecha_actual.strftime("%Y/%m/%d"))
        else:
            break

    if not fechas:
        return fecha_de_cierre.strftime("%Y/%m/%d")

    return "_".join(fechas)


def rectificar_viavilidad(
    index: int, valor: int,
    fiadores: list[int] = list,  deudas_con_fiadores: list[int] = list
) -> tuple[bool, str]:
    # rectificar administrador
    if not fg.rect_estado(index):
        return False, "El usuario no esta activo"

    if index in fiadores:
        return False, "Un usuario no puede ser su propio fiador"
    if len(fiadores) != len(set(fiadores)):
        return False, "No se permiten fiadores repetidos"

    sum_deudas: int = sum(deudas_con_fiadores)
    if valor == 0:
        return False, "Hay razon para hacer un prestamo?"
    if sum_deudas > valor:
        return False, "La deuda con fiadores supera el valor de el prestamo"

    capital_disponible: int = capital_disponible_usr(index)

    # rectificar para capital negativo o positivo
    if capital_disponible > 0:
        if valor - sum_deudas > capital_disponible:
            return False, "El dinero de el usuario no alcanza para el prestamo"
        if sum_deudas + capital_disponible < valor:
            return False, "No alcanza para solitar el prestamo, solicite mas fiadores"
    else:
        if len(fiadores) == 0:
            return False, "El usuario no tiene el capital disponible, solicite fiadores"
        if sum_deudas < valor:
            return (
                False,
                "No alcanza para solitar el prestamo, rectifique que el "
                "dinero de los fiadores alcance para el prestamo",
            )

    for idx, fiador in enumerate(fiadores):
        capital_de_fiador: int = capital_disponible_usr(fiador)
        if capital_de_fiador < deudas_con_fiadores[idx]:
            return False, f"El fiador con puesto №{fiador} no cuenta con el dinero"
        if not fg.rect_estado(fiador):
            return False, f"El fiador con puesto №{fiador} no esta activo"

    return True, ""


def escribir_prestamo(
    index: int, valor: int, motivo: str,
    fiadores: list[int] = list, deudas_fiadores: list[int] = list
) -> None:
    anotacion_final: str = (
        f"Se ha hecho un prestamo por {valor:,}. "
        f"fiadores: {','.join(map(str, fiadores))}, "
        f"deudas con ellos: {','.join(map(str, deudas_fiadores))}."
    )
    fa.realizar_anotacion(index, anotacion_final, 0, "GENERAL")

    interes: int = msql.obtener_ajuste("interes m tope")

    if valor > msql.obtener_ajuste("tope intereses"):
        interes = msql.obtener_ajuste("interes M tope")

    interes_inicial: int = int(valor * interes / 100)

    for fiador, deuda in zip(fiadores, deudas_fiadores):
        if fiador != 1976:
            msql.increment_int("prestamos", "deudas_por_fiador", fiador, deuda)
            msql.increment_str("prestamos", "fiador_de", fiador, str(index))

    capital_retirado = valor - sum(deudas_fiadores)
    msql.increment_int("capital", "retirado", index, capital_retirado)

    fiadores = "#".join(map(str, fiadores)) if fiadores else "n"
    deudas_fiadores = "#".join(map(str, deudas_fiadores)) if deudas_fiadores else "n"
    calendario = calendario_de_meses()

    conexion = sql.connect("Fondo.db")
    cursor = conexion.cursor()
    cursor.execute(
        """
        INSERT INTO prestamos_hechos (
            idx, estado_de_pago, interes,
            interes_vencido, interes_generado,
            deuda, monto, fechas_de_pago,
            revisiones, fiadores, deuda_con_fiadores,
            motivo
        )
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            index, 1, interes, 0, interes_inicial, valor, valor, calendario,
            0, fiadores, deudas_fiadores, motivo
        )
    )
    conexion.commit()
    conexion.close()


@st.dialog("Formulario de prestamo")
def formulario_de_prestamo(
    index: int, valor: int , usr_data: dict, motivo: str,
    fiadores: list[int] = list, deudas_fiadores: list[int] = list
) -> None:
    st.header(f"№ {index}: {usr_data["nombre"]}")
    st.divider()

    st.subheader(f"Valor de el prestamo: {valor:,}")

    st.table(
        pl.DataFrame({
            "Fiadores": fiadores,
            "Deudas con fiadores": list(map(lambda x: f"{x:,}", deudas_fiadores)),
        })
    )
    st.divider()

    if st.button("Realizar prestamo", key="BotonNoSe"):
        escribir_prestamo(index, valor, motivo, fiadores, deudas_fiadores)
        st.rerun()