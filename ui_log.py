import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from crud import obtener_log_cambios
from utils import formatear_fecha, formatear_detalle_cambio

def mostrar_pagina_log():
    """Muestra la página de historial de cambios"""
    st.title("Historial de Cambios")
    
    # Filtros
    st.subheader("Filtros")
    col1, col2 = st.columns(2)
    
    with col1:
        dni = st.text_input("Filtrar por DNI")
        accion = st.selectbox(
            "Filtrar por Acción",
            ['', 'alta', 'baja', 'modificacion']
        )
    
    with col2:
        fecha_desde = st.date_input(
            "Fecha desde",
            value=datetime.now() - timedelta(days=30)
        )
        fecha_hasta = st.date_input(
            "Fecha hasta",
            value=datetime.now()
        )
    
    # Aplicar filtros
    filtros = {}
    if dni:
        filtros['empleado_dni'] = dni
    if accion:
        filtros['accion'] = accion
    if fecha_desde:
        filtros['fecha_desde'] = datetime.combine(fecha_desde, datetime.min.time())
    if fecha_hasta:
        filtros['fecha_hasta'] = datetime.combine(fecha_hasta, datetime.max.time())
    
    # Obtener y mostrar cambios
    cambios = obtener_log_cambios(filtros)
    
    if not cambios:
        st.info("No se encontraron cambios en el período seleccionado")
        return
    
    # Convertir a DataFrame para mostrar
    df = pd.DataFrame([{
        'Fecha': formatear_fecha(c.timestamp),
        'Usuario': c.usuario.usuario,
        'DNI': c.empleado_dni,
        'Acción': c.accion,
        'Detalle': c.detalle
    } for c in cambios])
    
    # Mostrar tabla
    st.dataframe(df, use_container_width=True)
    
    # Estadísticas
    st.subheader("Estadísticas")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_cambios = len(cambios)
        st.metric("Total de cambios", total_cambios)
    
    with col2:
        cambios_por_accion = df['Acción'].value_counts()
        st.write("Cambios por acción:")
        st.write(cambios_por_accion)
    
    with col3:
        cambios_por_usuario = df['Usuario'].value_counts()
        st.write("Cambios por usuario:")
        st.write(cambios_por_usuario)
    
    # Exportar a Excel
    if st.button("Exportar a Excel"):
        nombre_archivo = f"historial_cambios_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        df.to_excel(nombre_archivo, index=False)
        
        with open(nombre_archivo, 'rb') as f:
            st.download_button(
                "Descargar Excel",
                f,
                file_name=nombre_archivo,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            ) 