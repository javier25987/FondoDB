import funciones.prestamos as fp
import funciones.general as fg
import streamlit as st
import pandas as pd
import datetime
import time


def crear_listado_de_fechas(primera_fecha: str, dobles: list[str]) -> str:
    """
    para este formato es obligatorio que las fechas esten en el formato
    anio/mes/dia/hora (la hora tiene que estar en formato 24 horas)
    """
    fecha = fg.string_a_fecha(primera_fecha)
    fechas = []

    i: int = 0
    while len(fechas) < 50:
        new_f = fecha + datetime.timedelta(days=7 * i)
        f_new = new_f.strftime("%Y/%m/%d/%H")
        if f_new in dobles:
            fechas.append(f_new)
        fechas.append(f_new)
        i += 1

    for i in dobles:
        if i not in fechas:
            return "n"

    return "_".join(fechas)


def guardar_y_avisar(ajustes: dict, rerun: bool = True):
    fg.guardar_ajustes(ajustes)
    if rerun:
        st.success("Valor modificado", icon="✅")
        time.sleep(1)
        st.rerun()


def crear_tablas_rifas(ajustes: dict, rifa: str) -> list:
    return [
        pd.DataFrame(
            {
                "Numero de boletas": [
                    "{:,}".format(ajustes[f"r{rifa} numero de boletas"])
                ],
                "Numeros por boleta": [str(ajustes[f"r{rifa} numeros por boleta"])],
                "Boletas por talonario": [
                    str(ajustes[f"r{rifa} boletas por talonario"])
                ],
            }
        ),
        pd.DataFrame(
            {
                "Costo por boleta": [
                    "{:,}".format(ajustes[f"r{rifa} costo de boleta"])
                ],
                "Costos de administracion": [
                    "{:,}".format(ajustes[f"r{rifa} costos de administracion"])
                ],
                "Ganancias por boleta": [
                    "{:,}".format(ajustes[f"r{rifa} ganancia por boleta"])
                ],
            }
        ),
        pd.DataFrame({"Fecha de cierre": [str(ajustes[f"r{rifa} fecha de cierre"])]}),
        pd.DataFrame({"Premios": str(ajustes[f"r{rifa} premios"]).split("_")}),
    ]


def cargar_datos_de_rifa(
    ajustes: dict, rifa: str, numero_de_boletas: int,
    numeros_por_boleta: int, boletas_por_talonario: int,
    costo_de_boleta: int, costo_de_administracion: int,
    fecha_de_cierre, premios: list[int],
) -> None:
    suma_de_premios = sum(premios)
    ganancias_por_boleta = (numero_de_boletas * costo_de_boleta) - (
        costo_de_administracion + suma_de_premios
    )
    ganancias_por_boleta /= numero_de_boletas
    ganancias_por_boleta = int(ganancias_por_boleta)

    premios = "_".join([str(i) for i in premios])

    ajustes[f"r{rifa} numero de boletas"] = numero_de_boletas
    ajustes[f"r{rifa} numeros por boleta"] = numeros_por_boleta
    ajustes[f"r{rifa} premios"] = premios
    ajustes[f"r{rifa} costo de boleta"] = costo_de_boleta
    ajustes[f"r{rifa} boletas por talonario"] = boletas_por_talonario
    ajustes[f"r{rifa} costos de administracion"] = costo_de_administracion
    ajustes[f"r{rifa} ganancia por boleta"] = ganancias_por_boleta
    ajustes[f"r{rifa} fecha de cierre"] = fecha_de_cierre.strftime("%Y/%m/%d")

    fg.guardar_ajustes(ajustes)
    st.success("Datos cargados", icon="✅")
    time.sleep(1)
    st.rerun()


def cerrar_una_rifa(rifa: str, ajustes: dict):
    df = pd.read_csv(ajustes["nombre df"])

    if ajustes[f"r{rifa} estado"]:
        fecha_de_cierre = fg.string_a_fecha(ajustes[f"r{rifa} fecha de cierre"])

        if fecha_de_cierre < datetime.datetime.now():
            numeros = tuple(df["numero"])
            nombres = tuple(df["nombre"])
            deudas = tuple(df[f"r{rifa} deudas"])

            progres_text: str = "Rectificando deudas de usuarios ..."
            func = lambda x: int(x * (100 / len(numeros)))
            bar = st.progress(0, text=progres_text)

            for i in range(len(nombres)):
                if deudas[i] > 0:
                    fp.escribir_prestamo(
                        numeros[i], "16", deudas[i], ajustes, df, [], []
                    )
                    df.loc[numeros[i], f"r{rifa} deudas"] = 0

                    st.toast(
                        f"💵 Se genero un prestamo por {deudas[i]:,}"
                        f"para el usuario № {numeros[i]}"
                    )
                    bar.progress(func(i), text=progres_text)

            bar.empty()
            ajustes[f"r{rifa} estado"] = False

            df = df.loc[:, ~df.columns.str.contains("^Unnamed")]
            df.to_csv(ajustes["nombre df"])

            guardar_y_avisar(ajustes, rerun=False)
        else:
            st.error("No se cumple la fecha de cierre", icon="🚨")
    else:
        st.error("La rifa no esta activa", icon="🚨")
