import streamlit as st
from auth import init_session_state, login_form, logout, require_auth
from ui_abm import mostrar_pagina_abm
from ui_import import mostrar_pagina_importacion
from ui_log import mostrar_pagina_log
from ui_dashboard import mostrar_pagina_dashboard
from db import get_engine, crear_usuario_admin

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
    # Menú de navegación
    menu = st.sidebar.radio(
        "Navegación",
        ["Dashboard", "Gestión de Empleados", "Importación", "Historial"]
    )
    
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
st.sidebar.markdown("Desarrollado con ❤️ por [Tu Nombre]") 