import streamlit as st
from auth import init_session_state, login_form, logout, require_auth
from ui_abm import mostrar_pagina_abm
from ui_import import mostrar_pagina_importacion
from ui_log import mostrar_pagina_log
from ui_dashboard import mostrar_pagina_dashboard
from db import get_engine, crear_usuario_admin
import time

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
    if not st.session_state.get('show_db_success'):
        st.session_state['show_db_success'] = True
        st.success("✅ Conexión a la base de datos y tablas creadas correctamente")
        time.sleep(2)
        st.session_state['show_db_success'] = False
        st.rerun()
    elif st.session_state.get('show_db_success'):
        st.success("✅ Conexión a la base de datos y tablas creadas correctamente")
except Exception as e:
    st.error(f"⚠️ Error al conectar con la base de datos: {e}")
    st.stop()
crear_usuario_admin()

# Barra lateral
with st.sidebar:
    st.title("👥 Sistema de Gestión")
    
    if st.session_state.logged_in:
        st.write(f"Usuario: {st.session_state.user.usuario}")
        st.write(f"Rol: {st.session_state.rol}")
        
        if st.button("Cerrar Sesión"):
            logout()
    else:
        st.write("Por favor inicie sesión")

# Navegación
if not st.session_state.logged_in:
    login_form()
else:
    # Menú de navegación mejorado para admin
    is_admin = st.session_state.get("rol") == "admin"
    st.sidebar.markdown("---")
    st.sidebar.markdown("## 📋 Menú de Navegación")
    menu = st.sidebar.radio(
        "",
        [
            "🏠 Dashboard",
            "👥 Gestión de Empleados",
            "⬆️ Importación",
            "🕑 Historial"
        ],
        format_func=lambda x: x.split(' ', 1)[-1]  # Solo muestra el texto sin emoji en el radio
    )
    
    # Botón destacado solo para administradores
    if is_admin:
        st.sidebar.markdown("---")
        st.sidebar.markdown(
            "<div style='text-align:center;'><b>⚙️ Opciones de Admin</b></div>", unsafe_allow_html=True)
        if st.sidebar.button("🚀 Cargar datos de ejemplo", help="Agrega empleados de ejemplo a la base de datos"):
            try:
                from seed_data import crear_empleados_ejemplo
                crear_empleados_ejemplo()
                st.sidebar.success("Datos de ejemplo cargados correctamente.")
            except Exception as e:
                st.sidebar.error(f"Error al cargar datos de ejemplo: {e}")
    
    # Mostrar página según selección
    if menu.endswith("Dashboard"):
        mostrar_pagina_dashboard()
    elif menu.endswith("Gestión de Empleados"):
        mostrar_pagina_abm()
    elif menu.endswith("Importación"):
        mostrar_pagina_importacion()
    elif menu.endswith("Historial"):
        mostrar_pagina_log()

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("Desarrollado por [Mauro Rementeria - mauroere@gmail.com]") 