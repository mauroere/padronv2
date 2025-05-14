from db import get_session, Empleado, Usuario, LogCambio
from datetime import datetime, timedelta
import random
import bcrypt

# Datos de ejemplo
nombres = [
    "Juan", "María", "Carlos", "Ana", "Pedro", "Laura", "Miguel", "Sofía",
    "José", "Lucía", "Fernando", "Carmen", "Roberto", "Isabel", "Diego"
]

apellidos = [
    "González", "Rodríguez", "López", "Martínez", "García", "Pérez", "Sánchez",
    "Ramírez", "Torres", "Flores", "Rivera", "Morales", "Castro", "Ortiz"
]

skills = [
    "Python", "Java", "JavaScript", "C#", "PHP", "Ruby", "Go", "Swift",
    "Kotlin", "TypeScript", "React", "Angular", "Vue", "Node.js", "Django",
    "Flask", "Spring", "Laravel", "SQL", "NoSQL", "DevOps", "AWS", "Azure",
    "Docker", "Kubernetes"
]

def generar_dni():
    """Genera un DNI aleatorio de 7 u 8 dígitos"""
    return str(random.randint(1000000, 99999999))

def generar_fecha_ingreso():
    """Genera una fecha de ingreso aleatoria en los últimos 5 años"""
    hoy = datetime.now()
    dias_atras = random.randint(0, 365 * 5)
    return hoy - timedelta(days=dias_atras)

def crear_empleados_ejemplo():
    """Crea empleados de ejemplo en la base de datos"""
    session = get_session()
    
    try:
        # Crear usuario admin si no existe
        admin = session.query(Usuario).filter_by(usuario='admin').first()
        if not admin:
            password = 'admin123'
            hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            admin = Usuario(
                usuario='admin',
                hash_password=hashed.decode('utf-8'),
                rol='admin'
            )
            session.add(admin)
            session.commit()
        
        # Crear empleados de ejemplo
        for _ in range(20):  # Crear 20 empleados
            empleado = Empleado(
                dni=generar_dni(),
                nombre=random.choice(nombres),
                apellido=random.choice(apellidos),
                fecha_ingreso=generar_fecha_ingreso(),
                estado=random.choice(['activo', 'inactivo']),
                skill=random.choice(skills),
                es_lider=random.choice([True, False])
            )
            session.add(empleado)
            
            # Registrar en log
            log = LogCambio(
                usuario_id=admin.id,
                empleado_dni=empleado.dni,
                accion='alta',
                detalle=f"Alta de empleado: {empleado.nombre} {empleado.apellido}"
            )
            session.add(log)
        
        session.commit()
        print("Datos de ejemplo creados exitosamente")
        
    except Exception as e:
        session.rollback()
        print(f"Error al crear datos de ejemplo: {str(e)}")
    finally:
        session.close()

if __name__ == '__main__':
    crear_empleados_ejemplo() 