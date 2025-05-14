import streamlit as st
from auth import init_session_state, login_form, logout, require_auth
from ui_abm import mostrar_pagina_abm
from ui_import import mostrar_pagina_importacion
from ui_log import mostrar_pagina_log
from ui_dashboard import mostrar_pagina_dashboard
from db import get_engine, crear_usuario_admin
import time
import os

# Configuración de la página
st.set_page_config(
    page_title="Sistema de Gestión de Empleados",
    page_icon="👥",
    layout="wide"
)

# Inicializar estado y base de datos
init_session_state()
try:
    get_engine()
    if st.session_state.get('show_db_success', True):
        print("✅ Conexión a la base de datos y tablas creadas correctamente")
        st.session_state['show_db_success'] = False
except Exception as e:
    st.error(f"⚠️ Error al conectar con la base de datos: {e}")
    st.stop()
crear_usuario_admin()

# Barra lateral
with st.sidebar:
    # Mostrar logo arriba a la izquierda
    if os.path.exists("logo.png"):
        st.image("logo.png", width=80)
    else:
        st.write("")  # Espacio reservado si no hay logo

    st.markdown("---")
    st.title("👥 Sistema de Gestión")
    if st.session_state.logged_in:
        st.write(f"**Usuario:** {st.session_state.user.usuario}")
        st.write(f"**Rol:** {st.session_state.rol}")
        if st.button("Cerrar Sesión"):
            logout()
    else:
        st.write("Por favor inicie sesión")

    st.markdown("---")
    st.markdown("## 📋 Menú de Navegación")
    # Botones de navegación visuales
    menu = None
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🏠 Dashboard"):
            st.session_state['menu'] = "Dashboard"
        if st.button("👥 Empleados"):
            st.session_state['menu'] = "Gestión de Empleados"
    with col2:
        if st.button("⬆️ Importación"):
            st.session_state['menu'] = "Importación"
        if st.button("🕑 Historial"):
            st.session_state['menu'] = "Historial"
    # Valor por defecto
    if 'menu' not in st.session_state:
        st.session_state['menu'] = "Dashboard"
    menu = st.session_state['menu']

    # Opciones de admin
    is_admin = st.session_state.get("rol") == "admin"
    if is_admin:
        st.markdown("---")
        st.markdown("<div style='text-align:center;'><b>⚙️ Opciones de Admin</b></div>", unsafe_allow_html=True)
        if st.button("🚀 Cargar datos de ejemplo", help="Agrega empleados de ejemplo a la base de datos"):
            try:
                from seed_data import crear_empleados_ejemplo
                crear_empleados_ejemplo()
                st.success("Datos de ejemplo cargados correctamente.")
            except Exception as e:
                st.error(f"Error al cargar datos de ejemplo: {e}")

# Navegación
if not st.session_state.logged_in:
    login_form()
else:
    # Mostrar página según selección
    if menu == "Dashboard":
        mostrar_pagina_dashboard()
    elif menu == "Gestión de Empleados":
        mostrar_pagina_abm()
    elif menu == "Importación":
        mostrar_pagina_importacion()
    elif menu == "Historial":
        mostrar_pagina_log()

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("Desarrollado por [Mauro Rementeria - mauroere@gmail.com]") 