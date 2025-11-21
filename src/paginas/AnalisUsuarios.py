#import src.funciones.analis_usuarios as f_au
import streamlit as st

st.title("En espera de una implementacion")
st.write("""
Esta pagina aun no ha sido implementada el motivo es la conectividad entre la informacion y los
archivos pdf que deben ser mostrados al usuario para la obtencion de un certificado personal o
general para el adimistrador del fondo, estos porblemas estan siendo resueltos y la implemetacion
sera prevista dentro de un tiempo, gracias por la compresion.
""")

st.write("""
Atentamente equipo de desarrollo del fondo san javier.
""")

# index: int = st.session_state.usuario
#
# index_de_usuario: int = st.sidebar.number_input("Numero de usuario:", value=0, step=1)
#
# if st.sidebar.button("Buscar"):
#     estado: tuple[bool, str] = f_au.abrir_usuario(index_de_usuario)
#     if estado[0]:
#         st.session_state.usuario = index_de_usuario
#         st.rerun()
#     else:
#         st.toast(estado[1], icon="🚨")
#
# tab_general, tab_usuario = st.tabs(["General", "Usuario"])
#
# with tab_general:
#     st.table(f_au.obtener_informacion_general(index))
#
# with tab_usuario:
#     if index == -1:
#         st.title("Usuario indeterminado")
#         st.stop()
