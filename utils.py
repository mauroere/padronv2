import pandas as pd
from datetime import datetime
import re

def normalizar_texto(texto):
    """Normaliza un texto eliminando acentos y convirtiendo a minúsculas"""
    if not texto:
        return ""
    texto = texto.lower()
    texto = re.sub(r'[áàäâ]', 'a', texto)
    texto = re.sub(r'[éèëê]', 'e', texto)
    texto = re.sub(r'[íìïî]', 'i', texto)
    texto = re.sub(r'[óòöô]', 'o', texto)
    texto = re.sub(r'[úùüû]', 'u', texto)
    texto = re.sub(r'[ñ]', 'n', texto)
    return texto

def validar_dni(dni):
    """Valida que el DNI tenga el formato correcto"""
    if not dni:
        return False
    dni = str(dni).strip()
    return bool(re.match(r'^\d{7,8}$', dni))

def normalizar_fecha(fecha):
    """Normaliza diferentes formatos de fecha a datetime"""
    if isinstance(fecha, datetime):
        return fecha
    try:
        return pd.to_datetime(fecha)
    except:
        return None

def normalizar_estado(estado):
    """Normaliza el estado del empleado"""
    if not estado:
        return 'activo'
    estado = normalizar_texto(estado)
    if estado in ['activo', 'inactivo']:
        return estado
    return 'activo'

def normalizar_boolean(valor):
    """Normaliza valores booleanos"""
    if isinstance(valor, bool):
        return valor
    if isinstance(valor, str):
        valor = normalizar_texto(valor)
        return valor in ['si', 'sí', 'true', 'verdadero', '1']
    return bool(valor)

def validar_archivo_importacion(df):
    """Valida que el DataFrame tenga las columnas requeridas"""
    columnas_requeridas = ['dni', 'nombre', 'apellido', 'fecha_ingreso']
    columnas_faltantes = [col for col in columnas_requeridas if col not in df.columns]
    
    if columnas_faltantes:
        raise ValueError(f"Faltan columnas requeridas: {', '.join(columnas_faltantes)}")
    
    # Validar DNI
    dni_invalidos = df[~df['dni'].astype(str).str.match(r'^\d{7,8}$')]
    if not dni_invalidos.empty:
        raise ValueError(f"DNIs inválidos en las filas: {', '.join(map(str, dni_invalidos.index + 1))}")
    
    # Validar fechas
    try:
        pd.to_datetime(df['fecha_ingreso'])
    except:
        raise ValueError("Formato de fecha inválido en la columna 'fecha_ingreso'")
    
    return True

def generar_nombre_archivo(prefix='export', extension='xlsx'):
    """Genera un nombre de archivo único con timestamp"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return f"{prefix}_{timestamp}.{extension}"

def formatear_fecha(fecha):
    """Formatea una fecha para mostrar"""
    if not fecha:
        return ""
    return fecha.strftime('%d/%m/%Y')

def formatear_detalle_cambio(cambio):
    """Formatea el detalle de un cambio para mostrar"""
    if not cambio:
        return ""
    return f"{formatear_fecha(cambio.timestamp)} - {cambio.usuario.usuario}: {cambio.detalle}" 