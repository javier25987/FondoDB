import streamlit as st
import src.funciones.ingresar_boletas as fi
import src.funciones.rifas as fr

tabla_de_boletas: str = "boletas_rifa_2"
ultimo_numero = [] # esto en teoria tiene que ser un stack pero me da pereza implementarlo

st.info(
    f"Todas las boletas que se deseen ingresar se guardaran en la tabla `{tabla_de_boletas}`",
    icon="ℹ️"
)

cols = st.columns(2)

with cols[0]:
    st.subheader("Agregar boleta")

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

    st.divider()

    st.subheader("Eliminar boleta")

    cols_eli = st.columns(2, vertical_alignment="bottom")

    with cols_eli[0]:
        boleta_eli = st.selectbox(
            "seleccione la boleta a eliminar:",
            fr.consultar_boletas_libres(-1, tabla_de_boletas)
        )

    with cols_eli[1]:
        if st.button("Eliminar boleta"):
            fi.eliminar_boleta(boleta_eli, tabla_de_boletas)
            st.rerun()


with cols[1]:
    boletas_a_mostrar = fi.consultar_boletas_rifa(tabla_de_boletas)
    if boletas_a_mostrar[1]:
        st.write(boletas_a_mostrar[0])

