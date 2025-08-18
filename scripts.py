import sqlite3 as sql


def pasar_boletas() -> None:
    conexion = sql.Connection("Fondo.db")
    cursor = conexion.cursor()

    cursor.execute("SELECT r.id, r.r1_boletas FROM rifas r")

    datos = cursor.fetchall()

    for usr, talonarios in datos:
        if talonarios == "n":
            continue
        for talonario in talonarios.split("_"):
            for boleta in talonario.split("#"):
                numeros = boleta.split("?")
                boleta_replace = boleta.replace("?", "_")
                cursor.execute(
                    """
                    INSERT INTO boletas_rifa_1 (idx, boleta, dada_a)
                    VALUES (?, ?, ?)
                    """,
                    (int(numeros[0]), boleta_replace, usr),
                )

    conexion.commit()
    conexion.close()


def transferir_las_deudas() -> None:
    conexion = sql.connect("Fondo.db")
    cursor = conexion.cursor()

    cursor.execute("SELECT id, r1_deudas FROM rifas")

    datos = cursor.fetchall()

    for idx, deuda in datos:
        cursor.execute(
            "INSERT INTO deudas_rifa (id, deuda) VALUES (?, ?)", (idx, deuda)
        )

    conexion.commit()
    conexion.close()


if __name__ == "__main__":
    # pasar_boletas()
    transferir_las_deudas()
