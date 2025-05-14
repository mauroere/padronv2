import streamlit as st
import pandas as pd
from crud import importar_empleados
from utils import validar_archivo_importacion, generar_nombre_archivo
import time

def mostrar_pagina_importacion():
    """Muestra la página de importación de datos"""
    st.title("Importación de Empleados")
    
    st.info("""
    El archivo debe contener las siguientes columnas:
    - dni (obligatorio)
    - nombre (obligatorio)
    - apellido (obligatorio)
    - fecha_ingreso (obligatorio)
    - estado (opcional, por defecto 'activo')
    - skill (opcional)
    - es_lider (opcional, por defecto False)
    """)
    
    archivo = st.file_uploader(
        "Seleccione un archivo Excel o CSV",
        type=['xlsx', 'csv']
    )
    
    if archivo:
        try:
            # Leer archivo según extensión
            if archivo.name.endswith('.csv'):
                df = pd.read_csv(archivo)
            else:
                df = pd.read_excel(archivo)
            
            # Mostrar vista previa
            st.subheader("Vista previa de datos")
            st.dataframe(df.head(), use_container_width=True)
            
            # Validar archivo
            validacion = validar_archivo_importacion(df)
            columnas_faltantes = validacion if isinstance(validacion, list) else []
            puede_importar = True
            if columnas_faltantes:
                st.warning(f"Faltan columnas requeridas: {', '.join(columnas_faltantes)}. Puedes continuar, pero solo se importarán los campos presentes.")
                puede_importar = st.checkbox("Entiendo y deseo continuar con la importación parcial.")
            
            # Botón de importación
            if st.button("Importar Datos"):
                if columnas_faltantes and not puede_importar:
                    st.error("Debes confirmar que deseas continuar con la importación parcial.")
                else:
                    with st.spinner("Importando datos..."):
                        try:
                            importar_empleados(df, st.session_state.user.id)
                            st.success("Datos importados correctamente")
                            time.sleep(2)  # Dar tiempo para ver el mensaje de éxito
                            st.rerun()  # Actualizar la vista
                        except Exception as e:
                            st.error(f"Error al importar: {str(e)}")
        
        except Exception as e:
            st.error(f"Error al procesar el archivo: {str(e)}")
    
    # Sección de ayuda
    with st.expander("Ayuda para la importación"):
        st.markdown("""
        ### Formato de archivo
        
        El archivo debe ser Excel (.xlsx) o CSV con las siguientes columnas:
        
        | Columna | Tipo | Obligatorio | Descripción |
        |---------|------|-------------|-------------|
        | dni | texto | Sí | DNI del empleado (7 u 8 dígitos) |
        | nombre | texto | Sí | Nombre del empleado |
        | apellido | texto | Sí | Apellido del empleado |
        | fecha_ingreso | fecha | Sí | Fecha de ingreso (formato: DD/MM/YYYY) |
        | estado | texto | No | Estado del empleado ('activo' o 'inactivo') |
        | skill | texto | No | Habilidad o especialidad |
        | es_lider | booleano | No | Indica si es líder (true/false) |
        
        ### Ejemplo de archivo
        
        Puede descargar un archivo de ejemplo [aquí](ejemplo_importacion.xlsx)
        """)
        
        # Generar y mostrar archivo de ejemplo
        if st.button("Generar archivo de ejemplo"):
            df_ejemplo = pd.DataFrame({
                'dni': ['12345678', '87654321'],
                'nombre': ['Juan', 'María'],
                'apellido': ['Pérez', 'González'],
                'fecha_ingreso': ['01/01/2024', '15/01/2024'],
                'estado': ['activo', 'activo'],
                'skill': ['Python', 'Java'],
                'es_lider': [True, False]
            })
            
            nombre_archivo = generar_nombre_archivo('ejemplo_importacion', 'xlsx')
            df_ejemplo.to_excel(nombre_archivo, index=False)
            
            with open(nombre_archivo, 'rb') as f:
                st.download_button(
                    "Descargar ejemplo",
                    f,
                    file_name=nombre_archivo,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                ) 