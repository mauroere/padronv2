import streamlit as st
import bcrypt
from db import get_session, Usuario

def login(usuario, password):
    """Autentica un usuario y retorna el objeto usuario si es válido"""
    session = get_session()
    user = session.query(Usuario).filter_by(usuario=usuario).first()
    session.close()
    
    if user and bcrypt.checkpw(password.encode('utf-8'), user.hash_password.encode('utf-8')):
        return user
    return None

def init_session_state():
    """Inicializa las variables de sesión de Streamlit"""
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'rol' not in st.session_state:
        st.session_state.rol = None

def login_form():
    """Muestra el formulario de login y maneja la autenticación"""
    st.title("Login")
    
    with st.form("login_form"):
        usuario = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        submit = st.form_submit_button("Ingresar")
        
        if submit:
            user = login(usuario, password)
            if user:
                st.session_state.logged_in = True
                st.session_state.user = user
                st.session_state.rol = user.rol
                st.success("Login exitoso!")
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos")

def logout():
    """Cierra la sesión del usuario"""
    st.session_state.logged_in = False
    st.session_state.user = None
    st.session_state.rol = None
    st.rerun()

def require_auth():
    """Decorador para requerir autenticación en una página"""
    if not st.session_state.get('logged_in'):
        st.warning("Por favor inicie sesión para acceder a esta página")
        login_form()
        st.stop()

def require_admin():
    """Decorador para requerir rol de administrador"""
    require_auth()
    if st.session_state.rol != 'admin':
        st.error("Se requiere rol de administrador para acceder a esta página")
        st.stop() 