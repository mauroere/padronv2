import sqlite3
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

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

def init_db():
    """Inicializa la base de datos y crea las tablas si no existen"""
    db_path = 'padron.db'
    engine = create_engine(f'sqlite:///{db_path}')
    Base.metadata.create_all(engine)
    return engine

def get_session():
    """Retorna una sesión de base de datos"""
    engine = init_db()
    Session = sessionmaker(bind=engine)
    return Session()

def crear_usuario_admin():
    """Crea un usuario administrador por defecto si no existe"""
    import bcrypt
    
    session = get_session()
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
    
    session.close()

if __name__ == '__main__':
    init_db()
    crear_usuario_admin() 