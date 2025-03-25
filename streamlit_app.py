# importamos las bibliotecas
import src.asuntos.rectificado as a_r
import streamlit as st

# miramos si hay que rectificar
# if "todo_rectificado" not in st.session_state:
#     st.session_state.todo_rectificado = 1
#     a_r.rectificar_todo()

# configuracion de el tamanio de la pagina
st.set_page_config(layout="wide")

# creacion de variables para la gestion
if "admin" not in st.session_state:
    st.session_state.admin = False

if "db_exist" not in st.session_state:
    st.session_state.db_exist = False

if "usuario_cuotas" not in st.session_state:
    st.session_state.usuario_cuotas = -1

if "usuario_actual_prestamos" not in st.session_state:
    st.session_state.usuario_actual_prestamos = -1

if "usuario_actual_anotaciones" not in st.session_state:
    st.session_state.usuario_actual_anotaciones = -1

if "usuario_actual_rifas" not in st.session_state:
    st.session_state.usuario_actual_rifas = -1

if "usuario_actual_analis" not in st.session_state:
    st.session_state.usuario_actual_analis = -1

if "ranura_actual" not in st.session_state:
    st.session_state.ranura_actual = "1"

if "mes_registro" not in st.session_state:
    st.session_state.mes_registro = 1

# paginas de usuario general
paginas_generales: list = [
    st.Page("src/paginas/Menu.py", title="Menu", icon="🏠"),
    st.Page("src/paginas/Cuotas.py", title="Cuotas", icon="📆"),
    st.Page("src/paginas/Prestamos.py", title="Prestamos", icon="💵"),
    st.Page("src/paginas/AnalisUsuarios.py", title="Analizar Ususarios", icon="📈"),
    st.Page("src/paginas/Transferencias.py", title="Transferencias", icon="🏛️"),
    st.Page("src/paginas/Rifas.py", title="Rifas", icon="🗒️"),
    st.Page("src/paginas/Anotaciones.py", title="Anotaciones", icon="📘"),
    st.Page("src/paginas/VerSocios.py", title="Ver Usuarios", icon="🔎"),
    st.Page("src/paginas/Registros.py", title="Registros", icon="📚")
]

# paginas de el modo administardor
paginas_de_adiministrador: list = [
    st.Page(
        "src/administrador/ModificarSocios.py", title="Modificar Usuarios", icon="📖"
    ),
    st.Page("src/administrador/Ajustes.py", title="Ajustes", icon="⚙️"),
    st.Page("src/session/logout.py", title="Salir", icon=":material/logout:"),
]

# pagina para ingresar como administrador
ingresar_admin: list = [
    st.Page("src/session/login.py", title="Ingresar", icon=":material/login:")
]

# pagina para crear los archivos
archivos_elementales: list = [
    st.Page("src/session/files.py", title="Crear Archivos", icon=":material/settings:")
]

# revisar si existen los ajustes
try:
    with open("Fondo.db", "r") as f:
        f.close()
    st.session_state.db_exist = True
except FileExistsError:
    pass

# diccionario de paginas que se van a mostrar
dict_general: dict = {}

# cargar las paginas a el diccionario
if st.session_state.db_exist:
    dict_general["Paginas Generales"] = paginas_generales

    if st.session_state.admin:
        dict_general["Paginas Administrativas"] = paginas_de_adiministrador
    else:
        dict_general["Paginas Administrativas"] = ingresar_admin
else:
    dict_general["Paginas Generales"] = archivos_elementales

# cargar las paginas para la vista
pg = st.navigation(dict_general)
pg.run()
