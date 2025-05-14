import os
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, ForeignKey, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import streamlit as st
from dotenv import load_dotenv
from urllib.parse import quote_plus

# Cargar variables de entorno
load_dotenv()

Base = declarative_base()

class Usuario(Base):
    __tablename__ = 'usuarios'
    
    id = Column(Integer, primary_key=True)
    usuario = Column(String, unique=True, nullable=False)
    hash_password = Column(String, nullable=False)
    rol = Column(String, nullable=False)  # 'admin' o 'usuario'
    fecha_creacion = Column(DateTime, default=datetime.now)

class Empleado(Base):
    __tablename__ = 'empleados'
    
    id = Column(Integer, primary_key=True)
    dni = Column(String, unique=True, nullable=False)
    nombre = Column(String, nullable=False)
    apellido = Column(String, nullable=False)
    fecha_ingreso = Column(DateTime)
    estado = Column(String)  # 'activo', 'inactivo'
    skill = Column(String)
    es_lider = Column(Boolean, default=False)
    fecha_creacion = Column(DateTime, default=datetime.now)
    fecha_actualizacion = Column(DateTime, onupdate=datetime.now)

class LogCambio(Base):
    __tablename__ = 'log_cambios'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.now)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'))
    empleado_dni = Column(String, ForeignKey('empleados.dni'))
    accion = Column(String)  # 'alta', 'baja', 'modificacion'
    detalle = Column(String)
    
    usuario = relationship("Usuario")
    empleado = relationship("Empleado")

def get_database_url():
    """Obtiene la URL de la base de datos desde las variables de entorno"""
    if 'DATABASE_URL' in os.environ:
        return os.environ['DATABASE_URL']
    else:
        st.error("""
        ⚠️ Error de configuración: No se encontró la variable de entorno DATABASE_URL.

        Ejemplo de configuración:
        DATABASE_URL = "postgresql://postgres.rujoykekjejmanavdfvl:Suj73hv)))9@aws-0-us-east-2.pooler.supabase.com:5432/postgres"
        """)
        st.stop()
        return None

@st.cache_resource
def get_engine():
    """Inicializa la base de datos y crea las tablas si no existen (solo una vez por sesión)."""
    try:
        database_url = get_database_url()
        if not database_url:
            raise Exception("No se encontró la URL de la base de datos.")
        engine = create_engine(
            database_url,
            pool_pre_ping=True,
            pool_recycle=3600,
            pool_size=5,
            max_overflow=10,
            connect_args={
                "connect_timeout": 30,
                "application_name": "padron_app",
                "options": "-c timezone=UTC",
                "keepalives": 1,
                "keepalives_idle": 30,
                "keepalives_interval": 10,
                "keepalives_count": 5,
                "tcp_user_timeout": 30000,
                "target_session_attrs": "read-write"
            }
        )
        # Probar la conexión
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        # Crear tablas si no existen
        Base.metadata.create_all(engine)
        # Crear usuario admin por defecto
        crear_usuario_admin(engine)
        # Eliminar la carga automática de datos de ejemplo
        return engine
    except Exception as e:
        raise e

def get_session():
    """Retorna una sesión de base de datos"""
    engine = get_engine()
    if engine is None:
        return None
    Session = sessionmaker(bind=engine)
    return Session()

def crear_usuario_admin(engine=None):
    """Crea un usuario administrador por defecto si no existe"""
    import bcrypt
    
    if engine is None:
        engine = get_engine()
        if engine is None:
            return
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        admin = session.query(Usuario).filter_by(usuario='admin').first()
        
        if not admin:
            password = 'admin123'  # Contraseña por defecto
            hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            admin = Usuario(
                usuario='admin',
                hash_password=hashed.decode('utf-8'),
                rol='admin'
            )
            session.add(admin)
            session.commit()
    finally:
        session.close()

if __name__ == '__main__':
    get_engine() 