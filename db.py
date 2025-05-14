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
        # Codificar caracteres especiales en la URL
        db_url = os.environ['DATABASE_URL']
        # Extraer las partes de la URL
        parts = db_url.split('@')
        if len(parts) == 2:
            auth, host = parts
            # Codificar la parte de autenticación
            auth_parts = auth.split('://')
            if len(auth_parts) == 2:
                protocol, credentials = auth_parts
                user_pass = credentials.split(':')
                if len(user_pass) == 2:
                    user, password = user_pass
                    # Codificar la contraseña manualmente para caracteres especiales
                    encoded_password = password.replace('(', '%28').replace(')', '%29')
                    # Forzar el uso del project ref correcto
                    project_ref = "rujoykekjejmanavdfvl"  # Tu project ref específico
                    # Reconstruir la URL con el formato correcto y parámetros adicionales
                    return f"{protocol}://postgres:{encoded_password}@db.{project_ref}.supabase.co:5432/postgres?hostaddr=db.{project_ref}.supabase.co"
        return db_url
    else:
        st.error("""
        ⚠️ Error de configuración: No se encontró la variable de entorno DATABASE_URL.
        
        Para configurar la base de datos:
        1. Ve a tu proyecto en Streamlit Cloud
        2. Haz clic en 'Manage app' en la esquina inferior derecha
        3. Ve a la pestaña 'Secrets'
        4. Agrega la siguiente configuración:
        
        DATABASE_URL = "postgresql://postgres:Suj73hv)))9@db.rujoykekjejmanavdfvl.supabase.co:5432/postgres"
        
        Nota: La contraseña debe ser exactamente: Suj73hv)))9
        """)
        st.stop()
        return None

def init_db():
    """Inicializa la base de datos y crea las tablas si no existen"""
    try:
        database_url = get_database_url()
        if not database_url:
            return None
            
        # Configurar el engine con parámetros adicionales
        engine = create_engine(
            database_url,
            pool_pre_ping=True,  # Verificar conexión antes de usar
            pool_recycle=3600,   # Reciclar conexiones cada hora
            pool_size=5,         # Número máximo de conexiones en el pool
            max_overflow=10,     # Número máximo de conexiones adicionales
            connect_args={
                "connect_timeout": 30,  # Aumentado a 30 segundos
                "application_name": "padron_app",
                "options": "-c timezone=UTC",
                "keepalives": 1,
                "keepalives_idle": 30,
                "keepalives_interval": 10,
                "keepalives_count": 5,
                "tcp_user_timeout": 30000,  # 30 segundos en milisegundos
                "target_session_attrs": "read-write"  # Asegura conexión a un nodo primario
            }
        )
        
        # Probar la conexión
        with engine.connect() as conn:
            # Ejecutar una consulta simple para verificar la conexión
            conn.execute(text("SELECT 1"))
            st.success("✅ Conexión a la base de datos establecida correctamente")
            
        # Crear tablas si no existen
        Base.metadata.create_all(engine)
        st.success("✅ Tablas creadas correctamente")
        
        # Crear usuario admin por defecto
        crear_usuario_admin(engine)
        
        # Crear datos de ejemplo
        try:
            from seed_data import crear_empleados_ejemplo
            crear_empleados_ejemplo()
            st.success("✅ Datos de ejemplo creados correctamente")
        except Exception as e:
            st.warning(f"⚠️ No se pudieron crear los datos de ejemplo: {str(e)}")
        
        return engine
        
    except Exception as e:
        st.error(f"""
        ⚠️ Error al conectar con la base de datos:
        
        {str(e)}
        
        Por favor, verifica que:
        1. La URL de la base de datos es correcta
        2. Las credenciales son válidas
        3. La base de datos está accesible
        4. El firewall permite conexiones desde Streamlit Cloud
        5. La base de datos está configurada para aceptar conexiones externas
        
        URL actual: {database_url if 'database_url' in locals() else 'No disponible'}
        """)
        st.stop()
        return None

def get_session():
    """Retorna una sesión de base de datos"""
    engine = init_db()
    if engine is None:
        return None
    Session = sessionmaker(bind=engine)
    return Session()

def crear_usuario_admin(engine=None):
    """Crea un usuario administrador por defecto si no existe"""
    import bcrypt
    
    if engine is None:
        engine = init_db()
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
    init_db() 