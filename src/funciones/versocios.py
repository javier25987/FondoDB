def buscar_boleta(df, rifa_a_buscar: str, boleta_a_buscar: str, poscion_boleta: int):
    tabla_prueva = df[
        df[f"r{rifa_a_buscar} boletas"].str.contains(
            boleta_a_buscar, case=False, na=False
        )
    ]

    numeros = list(tabla_prueva["numero"])

    if len(numeros) <= 0:
        return -1
    if len(numeros) == 1:
        return numeros[0]

    for i in numeros:
        objetos: list[str] = df[f"r{rifa_a_buscar} boletas"][i].split("_")
        new_objetos: list = []

        for n in objetos:
            new_objetos += [m.split("?") for m in n.split("#")]

        for k in new_objetos:
            if k[poscion_boleta - 1] == boleta_a_buscar:
                return i

    return -1  # esto solo se activa si hay algun error
