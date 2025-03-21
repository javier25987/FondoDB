import funciones.general as fg
import funciones.menu as fm
import streamlit as st

ajustes: dict = fg.abrir_ajustes()

st.title("Menu de inicio")

st.markdown(
    """
    Honestamente ya no se que hace con el menu, lo voy a dejar 
    para almacenar las funciones de guardado en internet y 
    cargar las multas a todos ya que no se donde poner eso, pero 
    el menu ya perdio todas las funciones que tenia en la anterior
    version
    """
)
st.divider()

col1, col2 = st.columns(2)

with col1:
    st.header("Guardar tabla")
    st.divider()
    if st.button("📤 Guardar En GitHub"):
        fm.hacer_commit(ajustes)

    st.link_button("🔗 Abrir GitHub", ajustes["enlace repo"])

with col2:
    st.header("Cargar multas")
    st.markdown(
        """
        Actualmente el programa automaticamente carga las multas y los
        intereses no es necesario oprimir ningun boton periodicamente
        """
    )
