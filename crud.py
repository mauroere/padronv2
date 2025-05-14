from db import get_session, Empleado, LogCambio
from datetime import datetime
import pandas as pd
from sqlalchemy import String, Boolean, Integer

def crear_empleado(dni, nombre, apellido, fecha_ingreso, estado, skill, es_lider, usuario_id):
    """Crea un nuevo empleado y registra el cambio en el log"""
    session = get_session()
    try:
        empleado = Empleado(
            dni=dni,
            nombre=nombre,
            apellido=apellido,
            fecha_ingreso=fecha_ingreso,
            estado=estado,
            skill=skill,
            es_lider=es_lider
        )
        session.add(empleado)
        
        # Registrar en log
        log = LogCambio(
            usuario_id=usuario_id,
            empleado_dni=dni,
            accion='alta',
            detalle=f"Alta de empleado: {nombre} {apellido}"
        )
        session.add(log)
        
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def actualizar_empleado(dni, datos, usuario_id):
    """Actualiza los datos de un empleado y registra los cambios"""
    session = get_session()
    try:
        empleado = session.query(Empleado).filter_by(dni=dni).first()
        if not empleado:
            return False
            
        cambios = []
        for key, value in datos.items():
            if hasattr(empleado, key) and getattr(empleado, key) != value:
                cambios.append(f"{key}: {getattr(empleado, key)} -> {value}")
                setattr(empleado, key, value)
        
        if cambios:
            log = LogCambio(
                usuario_id=usuario_id,
                empleado_dni=dni,
                accion='modificacion',
                detalle="Cambios: " + ", ".join(cambios)
            )
            session.add(log)
            
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def eliminar_empleado(dni, usuario_id):
    """Elimina un empleado y registra el cambio"""
    session = get_session()
    try:
        empleado = session.query(Empleado).filter_by(dni=dni).first()
        if not empleado:
            return False
            
        log = LogCambio(
            usuario_id=usuario_id,
            empleado_dni=dni,
            accion='baja',
            detalle=f"Baja de empleado: {empleado.nombre} {empleado.apellido}"
        )
        session.add(log)
        
        session.delete(empleado)
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def obtener_empleado(dni):
    """Obtiene los datos de un empleado por DNI"""
    session = get_session()
    try:
        return session.query(Empleado).filter_by(dni=dni).first()
    finally:
        session.close()

def listar_empleados(filtros=None):
    """Lista todos los empleados con filtros opcionales"""
    session = get_session()
    try:
        query = session.query(Empleado)
        
        if filtros:
            for key, value in filtros.items():
                if value is not None and value != "":
                    column = getattr(Empleado, key)
                    # Si el campo es string, usar ilike
                    if isinstance(column.type, String):
                        query = query.filter(column.ilike(f"%{value}%"))
                    # Si el campo es booleano, comparar directamente
                    elif isinstance(column.type, Boolean):
                        query = query.filter(column == value)
                    # Si el campo es numérico, comparar directamente
                    elif isinstance(column.type, Integer):
                        query = query.filter(column == value)
                    else:
                        query = query.filter(column == value)
        
        return query.all()
    finally:
        session.close()

def importar_empleados(df, usuario_id):
    """Importa empleados desde un DataFrame"""
    session = get_session()
    try:
        for _, row in df.iterrows():
            empleado = Empleado(
                dni=str(row['dni']),
                nombre=row['nombre'],
                apellido=row['apellido'],
                fecha_ingreso=pd.to_datetime(row['fecha_ingreso']),
                estado=row.get('estado', 'activo'),
                skill=row.get('skill', ''),
                es_lider=row.get('es_lider', False)
            )
            session.add(empleado)
            
            log = LogCambio(
                usuario_id=usuario_id,
                empleado_dni=str(row['dni']),
                accion='alta',
                detalle=f"Importación masiva: {row['nombre']} {row['apellido']}"
            )
            session.add(log)
        
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def obtener_log_cambios(filtros=None):
    """Obtiene el historial de cambios con filtros opcionales"""
    session = get_session()
    try:
        query = session.query(LogCambio)
        
        if filtros:
            if 'usuario_id' in filtros:
                query = query.filter_by(usuario_id=filtros['usuario_id'])
            if 'empleado_dni' in filtros:
                query = query.filter_by(empleado_dni=filtros['empleado_dni'])
            if 'accion' in filtros:
                query = query.filter_by(accion=filtros['accion'])
            if 'fecha_desde' in filtros:
                query = query.filter(LogCambio.timestamp >= filtros['fecha_desde'])
            if 'fecha_hasta' in filtros:
                query = query.filter(LogCambio.timestamp <= filtros['fecha_hasta'])
        
        return query.order_by(LogCambio.timestamp.desc()).all()
    finally:
        session.close() 