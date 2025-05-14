import os
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import streamlit as st
from dotenv import load_dotenv

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
        # Fallback a SQLite local para desarrollo
        return 'sqlite:///padron.db'

def init_db():
    """Inicializa la base de datos y crea las tablas si no existen"""
    database_url = get_database_url()
    engine = create_engine(database_url)
    
    # Crear tablas si no existen
    Base.metadata.create_all(engine)
    
    # Crear usuario admin por defecto
    crear_usuario_admin(engine)
    
    # Crear datos de ejemplo
    try:
        from seed_data import crear_empleados_ejemplo
        crear_empleados_ejemplo()
    except Exception as e:
        st.warning(f"No se pudieron crear los datos de ejemplo: {str(e)}")
    
    return engine

def get_session():
    """Retorna una sesión de base de datos"""
    engine = init_db()
    Session = sessionmaker(bind=engine)
    return Session()

def crear_usuario_admin(engine=None):
    """Crea un usuario administrador por defecto si no existe"""
    import bcrypt
    
    if engine is None:
        engine = init_db()
    
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
    init_db() 