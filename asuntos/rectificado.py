import funciones.general as fg
import funciones.cuotas as fc
from tqdm import tqdm
import pandas as pd
import datetime


def abrir_fecha() -> dict:
    with open("asuntos/fecha.txt", "r") as f:
        fecha: str = f.read()
        f.close()

    fecha = datetime.datetime(
        *map(int, fecha.split("/"))
    )

    return fecha


def cargar_ultimo_lunes() -> None:
    with open("asuntos/fecha.txt", "w") as f:
        f.write(obtener_ultimo_lunes().strftime("%Y/%m/%d"))
        f.close()


def obtener_ultimo_lunes():
    hoy = datetime.datetime.now()

    diferencia_dias = hoy.weekday()
    '''
    .weekday() devueleve el dia de la semana numerado como un array, ejm:
    lun _ 0 , mar _ 1, mie _ 2, ...
    '''

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
        ajustes: dict = fg.abrir_ajustes()
        df = pd.read_csv(ajustes["nombre df"])

        ranuras: list[str] = list(map(str, range(1, 17)))
        
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

        for index in tqdm(range(ajustes["usuarios"])): # iteramos sobre todos los usuarios

            # rectificamos para cuotas
            cuotas: list = list(df["cuotas"][index])
            multas: list = list(df["multas"][index])

            semanas_revisadas: int = int(df["revisiones"][index])

            if semanas_a_revisar > semanas_revisadas:
                for i in range(50):
                    if calendario[i] <= fecha_actual:
                        if cuotas[i] != "p":
                            if ajustes["cobrar multas"]:
                                multas = fc.sumar_una_multa(multas, i)
                            cuotas[i] = "d"
                    else:
                        break

                df.loc[index, "cuotas"] = "".join(cuotas)
                df.loc[index, "multas"] = "".join(multas)
                df.loc[index, "revisiones"] = semanas_a_revisar


            for i in ranuras: # iteramos sobre prestamos hechos

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

        df = df.loc[:, ~df.columns.str.contains("^Unnamed")]
        df.to_csv(ajustes["nombre df"])

        cargar_ultimo_lunes()
        print("Proceso finalizado.")
