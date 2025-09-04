import streamlit as st
import src.funciones.ingresar_boletas as fi

tabla_de_boletas: str = "boletas_rifa_2"
ultimo_numero = [] # esto en teoria tiene que ser un stack pero me da pereza implementarlo

st.info(
    f"Todas las boletas que se deseen ingresar se guardaran en la tabla {tabla_de_boletas}",
    icon="ℹ️"
)

cols = st.columns(2)

with cols[0]:
    cols_boletas = st.columns(4)

    for columna, numero in zip(cols_boletas, range(1, 5)):
        with columna:
            st.text_input(
                f"Numero {numero}:",
                key=f"boleta_numero_{numero}"
            )

    if st.button("Guardar boleta"):
        boletas = []

        for i in range(1, 5):
            boletas.append(st.session_state[f"boleta_numero_{i}"])

        viavilidad = fi.rectificar_boleta(boletas)

        if viavilidad:
            fi.insert_boleta(boletas, tabla_de_boletas)
            ultimo_numero.append(int(boletas[0]))
            st.rerun()
        else:
            st.toast("El formato de las boletas no es el correcto, por favor rectifique que sea correcto.", icon="🚨")

        


with cols[1]:
    boletas_a_mostrar = fi.consultar_boletas_rifa(tabla_de_boletas)
    if boletas_a_mostrar[1]:
        st.write(boletas_a_mostrar[0])

