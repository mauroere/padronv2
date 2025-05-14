from db import get_session, Empleado, LogCambio

def verificar_empleado(dni):
    session = get_session()
    try:
        # Verificar empleado
        print('Verificando empleado...')
        empleado = session.query(Empleado).filter_by(dni=dni).first()
        print(f'Empleado existe: {empleado is not None}')
        if empleado:
            print(f'Datos del empleado:')
            print(f'- DNI: {empleado.dni}')
            print(f'- Nombre: {empleado.nombre}')
            print(f'- Apellido: {empleado.apellido}')
            print(f'- Estado: {empleado.estado}')
            print(f'- Skill: {empleado.skill}')
            print(f'- Es Líder: {empleado.es_lider}')
        
        # Verificar logs
        print('\nVerificando logs...')
        logs = session.query(LogCambio).filter_by(empleado_dni=dni).all()
        print(f'Cantidad de logs: {len(logs)}')
        for log in logs:
            print(f'- {log.accion}: {log.detalle} ({log.timestamp})')
        
        # Verificar total de empleados
        print('\nTotal de empleados en la base de datos:', session.query(Empleado).count())
        
    finally:
        session.close()

if __name__ == '__main__':
    verificar_empleado('21781599') 