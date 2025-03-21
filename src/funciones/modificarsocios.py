import funciones.general as fg
import streamlit as st
import pandas as pd
import time


def insertar_socios(
    ajustes: dict, df, nombre: str = "", puestos: int = 1, numero_celular: str = ""
):
    if numero_celular == "":
        numero_celular = "n"

    nombre = nombre.lower()

    nuevo_usuario = pd.DataFrame(
        {
            # informacion general
            "numero": [ajustes["usuarios"]],
            "nombre": [nombre],
            "puestos": [puestos],
            "numero celular": numero_celular,
            "estado": ["activo"],
            "capital": [0],
            "aporte a multas": [0],
            "multas extra": [0],
            "anotaciones generales": ["n"],
            # cuotas
            "cuotas": ["n" * 50],
            "multas": ["n" * 50],
            "tesorero": ["n" * 50],
            "revisiones": [0],
            "anotaciones de cuotas": ["n"],
            # rifas
            "r1 boletas": ["n"],
            "r1 deudas": [0],
            "r2 boletas": ["n"],
            "r2 deudas": [0],
            "r3 boletas": ["n"],
            "r3 deudas": [0],
            "r4 boletas": ["n"],
            "r4 deudas": [0],
            "anotaciones de rifas": ["n"],
            # prestamos
            "prestamos hechos": [0],
            "dinero en prestamos": [0],
            "dinero por si mismo": [0],
            "dinero por intereses vencidos": [0],
            "p1 estado": ["activo"],
            "p1 prestamo": ["0_0_0_0_n_n"],
            "p1 fechas de pago": ["n"],
            "p2 estado": ["activo"],
            "p2 prestamo": ["0_0_0_0_n_n"],
            "p2 fechas de pago": ["n"],
            "p3 estado": ["activo"],
            "p3 prestamo": ["0_0_0_0_n_n"],
            "p3 fechas de pago": ["n"],
            "p4 estado": ["activo"],
            "p4 prestamo": ["0_0_0_0_n_n"],
            "p4 fechas de pago": ["n"],
            "p5 estado": ["activo"],
            "p5 prestamo": ["0_0_0_0_n_n"],
            "p5 fechas de pago": ["n"],
            "p6 estado": ["activo"],
            "p6 prestamo": ["0_0_0_0_n_n"],
            "p6 fechas de pago": ["n"],
            "p7 estado": ["activo"],
            "p7 prestamo": ["0_0_0_0_n_n"],
            "p7 fechas de pago": ["n"],
            "p8 estado": ["activo"],
            "p8 prestamo": ["0_0_0_0_n_n"],
            "p8 fechas de pago": ["n"],
            "p9 estado": ["activo"],
            "p9 prestamo": ["0_0_0_0_n_n"],
            "p9 fechas de pago": ["n"],
            "p10 estado": ["activo"],
            "p10 prestamo": ["0_0_0_0_n_n"],
            "p10 fechas de pago": ["n"],
            "p11 estado": ["activo"],
            "p11 prestamo": ["0_0_0_0_n_n"],
            "p11 fechas de pago": ["n"],
            "p12 estado": ["activo"],
            "p12 prestamo": ["0_0_0_0_n_n"],
            "p12 fechas de pago": ["n"],
            "p13 estado": ["activo"],
            "p13 prestamo": ["0_0_0_0_n_n"],
            "p13 fechas de pago": ["n"],
            "p14 estado": ["activo"],
            "p14 prestamo": ["0_0_0_0_n_n"],
            "p14 fechas de pago": ["n"],
            "p15 estado": ["activo"],
            "p15 prestamo": ["0_0_0_0_n_n"],
            "p15 fechas de pago": ["n"],
            "p16 estado": ["activo"],
            "p16 prestamo": ["0_0_0_0_n_n"],
            "p16 fechas de pago": ["n"],
            "deudas por fiador": [0],
            "fiador de": ["n"],
            "anotaciones de prestamos": ["n"],
        }
    )
    df = pd.concat([df, nuevo_usuario], ignore_index=True)
    df = df.loc[:, ~df.columns.str.contains("^Unnamed")]
    df.to_csv(ajustes["nombre df"])

    ajustes["usuarios"] += 1

    fg.guardar_ajustes(ajustes)


@st.dialog("Añadir un nuevo usuario:")
def menu_para_insertar_socio(
    ajustes: dict, df, nombre: str = "", puestos: int = 0, telefono: str = ""
) -> None:
    cols = st.columns([7, 3], vertical_alignment="bottom")

    with cols[0]:
        st.subheader("Nombre:")
        st.write(nombre.title())
        st.subheader("Puestos:")
        st.write(puestos)
        st.subheader("Telefono:")
        st.write(telefono)

    with cols[1]:
        if st.button("Añadir", key="nosequeputas"):
            insertar_socios(ajustes, df, nombre, puestos, telefono)
            st.toast("Nuevo usuario añadido", icon="🎉")
            time.sleep(1.5)
            st.rerun()


def modificar_columna(index: int, columna: str, nuevo: str | int, ajustes: dict, df):
    df.loc[index, columna] = nuevo
    df = df.loc[:, ~df.columns.str.contains("^Unnamed")]
    df.to_csv(ajustes["nombre df"])


def sumar_multas(s, n) -> str:
    numero = lambda x: int(x) if x != "n" else 0
    s = [numero(i) for i in s]

    for i in range(50):
        if s[i] < 9:
            diferencia = 9 - s[i]
            if n - diferencia > 0:
                n -= diferencia
                s[i] = 9
            else:
                s[i] += n
                n = 0
        if n <= 0:
            break

    return "".join(map(lambda x: "n" if x == 0 else str(x), s))


def restar_multas(s, n) -> str:
    numero = lambda x: int(x) if x != "n" else 0
    s = [numero(i) for i in s]

    for i in range(50):
        if n >= s[i]:
            n -= s[i]
            s[i] = 0
        else:
            s[i] -= n
            n = 0
        if n <= 0:
            break

    return "".join(map(lambda x: "n" if x == 0 else str(x), s))


def contar_multas(index: int, df):
    count: int = 0

    for i in df["multas"][index]:
        if i != "n":
            count += int(i)

    return count


def sumar_cuotas(s, n) -> str:
    s = list(s)

    for i in range(50):
        if s[i] != "p":
            s[i] = "p"
            n -= 1
        if n <= 0:
            break

    return "".join(s)


def quitar_cuotas(s, n) -> str:
    s = list(s)

    for i in range(49, -1, -1):
        if s[i] == "p":
            s[i] = "n"
            n -= 1
        if n <= 0:
            break

    return "".join(s)


def sumar_deudas(s, n) -> str:
    s = list(s)

    for i in range(50):
        if s[i] == "n":
            s[i] = "d"
            n -= 1
        if n <= 0:
            break

    return "".join(s)


def quitar_deudas(s, n) -> str:
    s = list(s)

    for i in range(49, -1, -1):
        if s[i] == "d":
            s[i] = "n"
            n -= 1
        if n <= 0:
            break

    return "".join(s)
