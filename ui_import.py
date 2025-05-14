import streamlit as st
import pandas as pd
from crud import importar_empleados, listar_empleados
from utils import validar_archivo_importacion, generar_nombre_archivo
import time
import re

CAMPOS_BD = [
    'dni', 'nombre', 'apellido', 'fecha_ingreso', 'estado', 'skill', 'es_lider'
]

CAMPOS_BD_LABELS = {
    'dni': 'DNI',
    'nombre': 'Nombre',
    'apellido': 'Apellido',
    'fecha_ingreso': 'Fecha de Ingreso',
    'estado': 'Estado',
    'skill': 'Skill',
    'es_lider': 'Es Líder'
}

def mostrar_pagina_importacion():
    """Muestra la página de importación de datos"""
    st.title("Importación de Empleados (Asistida)")
    
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
            
            columnas_archivo = list(df.columns)
            st.subheader("Mapeo de columnas")
            mapeo = {}
            opciones = ["No importar"] + [CAMPOS_BD_LABELS[c] for c in CAMPOS_BD]
            for col in columnas_archivo:
                mapeo[col] = st.selectbox(f"¿A qué campo de la base de datos corresponde '{col}'?", opciones, key=f"map_{col}")

            # Opción para dividir columnas
            columnas_dividir = [col for col in columnas_archivo if st.checkbox(f"¿Dividir '{col}' en varios campos?", key=f"div_{col}")]
            divisiones = {}
            for col in columnas_dividir:
                criterio = st.text_input(f"Separador para dividir '{col}' (ej: espacio, coma, etc.)", value=" ", key=f"sep_{col}")
                divisiones[col] = criterio
                subcampos = st.multiselect(f"¿A qué campos asignar las partes de '{col}'? (en orden)", [CAMPOS_BD_LABELS[c] for c in CAMPOS_BD if c != 'dni'], key=f"sub_{col}")
                mapeo[col] = subcampos

            # --- DEBUG VISUAL: Mostrar DNIs y existencia ---
            st.subheader("Debug: Estado de los DNIs a importar")
            empleados_existentes = {e.dni for e in listar_empleados()}
            resumen = []
            for _, row in df.iterrows():
                dni = str(row['dni']).strip() if 'dni' in row and pd.notna(row['dni']) else None
                if not dni:
                    continue
                existe = dni in empleados_existentes
                resumen.append({'DNI': dni, 'Ya existe': 'Sí' if existe else 'No'})
            st.dataframe(pd.DataFrame(resumen), use_container_width=True)

            # Botón de importación
            if st.button("Importar Datos"):
                # Construir nuevo DataFrame normalizado
                data = {c: [None]*len(df) for c in CAMPOS_BD}
                for col, destino in mapeo.items():
                    if destino == "No importar" or (isinstance(destino, list) and not destino):
                        continue
                    if isinstance(destino, list):
                        # División de columna
                        sep = divisiones.get(col, " ")
                        for i, val in enumerate(df[col].astype(str)):
                            partes = re.split(sep, val, maxsplit=len(destino)-1)
                            for idx, campo_label in enumerate(destino):
                                campo = [k for k, v in CAMPOS_BD_LABELS.items() if v == campo_label][0]
                                data[campo][i] = partes[idx] if idx < len(partes) else None
                    else:
                        # Mapeo directo
                        campo = [k for k, v in CAMPOS_BD_LABELS.items() if v == destino][0]
                        data[campo] = df[col].astype(str).tolist()
                df_normalizado = pd.DataFrame(data)
                # Validar y limpiar datos mínimos
                df_normalizado = df_normalizado.dropna(subset=['dni', 'nombre', 'apellido', 'fecha_ingreso'], how='any')
                st.subheader("Datos normalizados a importar")
                st.dataframe(df_normalizado, use_container_width=True)
                try:
                    importar_empleados(df_normalizado, st.session_state.user.id)
                    st.success("Datos importados correctamente")
                    st.rerun()
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