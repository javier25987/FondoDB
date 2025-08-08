import src.funciones.cuotas as fc
import src.sql.conect as c_sql
import sqlite3 as sql
from tqdm import tqdm
import datetime


def abrir_fecha() -> dict:
    with open("src/asuntos/fecha.txt", "r") as f:
        fecha: str = f.read()
        f.close()

    fecha = datetime.datetime(*map(int, fecha.split("/")))

    return fecha


def cargar_ultimo_lunes() -> None:
    with open("src/asuntos/fecha.txt", "w") as f:
        f.write(obtener_ultimo_lunes().strftime("%Y/%m/%d"))
        f.close()


def obtener_ultimo_lunes():
    hoy = datetime.datetime.now()

    diferencia_dias = hoy.weekday()
    """
    .weekday() devueleve el dia de la semana numerado como un array, ejm:
    lun _ 0 , mar _ 1, mie _ 2, ...
    """

    ultimo_lunes = hoy - datetime.timedelta(days=diferencia_dias)

    return ultimo_lunes


def hoy_no_es_lunes() -> bool:
    hoy = datetime.datetime.now()
    dia_semana = hoy.weekday()
    return dia_semana != 0


def rectificar_todo() -> None:
    # obtener las fechas
    lunes_guardado = abrir_fecha().date()
    ultimo_lunes = obtener_ultimo_lunes().date()

    # rectificar si ya paso el lunes
    if (ultimo_lunes > lunes_guardado) and hoy_no_es_lunes():
        print("Es necesario cargar multas e intereses:")

        # cargamos datos

        conexion = sql.connect("Fondo.db")
        cursor = conexion.cursor()

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

        cobrar_multas = bool(c_sql.obtener_ajuste("cobrar multas"))
        anular_usuarios = bool(c_sql.obtener_ajuste("anular usuarios"))

        print("Rectificando multas")
        for index in tqdm(range(c_sql.obtener_ajuste("usuarios"))):  # iteramos sobre todos los usuarios

            # rectificamos para cuotas
            semanas_revisadas: int = c_sql.obtener_cuotas("revisiones", index)

            if semanas_a_revisar > semanas_revisadas:
                multas: str = c_sql.obtener_cuotas("multas", index)
                multas = fc.multas_comp_str(multas)
                pagas: int = c_sql.obtener_cuotas("pagas", index)
                deudas: int = 0

                for i in range(50):
                    if calendario[i] <= fecha_actual:
                        if i >= pagas:
                            if cobrar_multas:
                                multas = fc.sumar_una_multa(multas, i)
                            deudas += 1
                    else:
                        break

                multas = fc.multas_str_comp(multas)
                c_sql.guardar_valor_t("cuotas", "multas", index, multas)
                c_sql.guardar_valor("cuotas", "adeudas", index, deudas)
                c_sql.guardar_valor("cuotas", "revisiones", index, semanas_a_revisar)

        # revisamos para todos los prestamos
        cursor.execute(
            f"""
            SELECT
                ph.codigo,
                ph.fechas_de_pago,
                ph.revisiones
            FROM prestamos_hechos ph
            WHERE ph.estado = 1
            """
        )

        datos = cursor.fetchall()

        print("Rectificando prestamos")
        for i, j, k in tqdm(datos):
            fechas_pasadas: int = sum(
                map(
                    lambda x: x < fecha_actual,
                    map(
                        lambda y: datetime.datetime(*map(int, y.split("/"))),
                        j.split("_")
                    ),
                )
            )
            if fechas_pasadas > k:
                for _ in range(fechas_pasadas - k):
                    cursor.execute(
                        f"""
                        UPDATE prestamos_hechos
                        SET
                            intereses_vencidos = intereses_vencidos + (
                                deuda * interes
                            ) / 100,
                            revisiones = {fechas_pasadas}
                        WHERE codigo = {i}
                        """
                    )
        conexion.commit()
        conexion.close()
        cargar_ultimo_lunes()
        print("Proceso finalizado.")
    else:
        print("No fue necesario rectificar multas o intereses.")
