import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from crud import listar_empleados, obtener_empleado
from utils import formatear_fecha
from sqlalchemy import text
from db import get_engine

def mostrar_pagina_dashboard():
    """Muestra la página del dashboard"""
    col_logo, col_title = st.columns([1, 8])
    with col_logo:
        st.image("logo.png", width=80)
    with col_title:
        st.title("Dashboard")
    
    # --- Botón de migración solo para admin ---
    if hasattr(st.session_state, 'rol') and st.session_state.rol == 'admin':
        st.warning("Botón solo para administradores. Ejecuta la migración de nuevos campos en la tabla empleados.")
        if st.button("Ejecutar migración de nuevos campos empleados 🛠️"):
            alter_statements = [
                # Renombrar mail a email si existe
                "DO $$ BEGIN IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='empleados' AND column_name='mail') THEN EXECUTE 'ALTER TABLE empleados RENAME COLUMN mail TO email'; END IF; END $$;",
                # Agregar solo las columnas faltantes
                "ALTER TABLE empleados ADD COLUMN IF NOT EXISTS telefono VARCHAR;",
                "ALTER TABLE empleados ADD COLUMN IF NOT EXISTS direccion VARCHAR;",
                "ALTER TABLE empleados ADD COLUMN IF NOT EXISTS area VARCHAR;",
                "ALTER TABLE empleados ADD COLUMN IF NOT EXISTS proyecto VARCHAR;",
                "ALTER TABLE empleados ADD COLUMN IF NOT EXISTS usuario_nt VARCHAR;",
                "ALTER TABLE empleados ADD COLUMN IF NOT EXISTS usuario_hada VARCHAR;",
                "ALTER TABLE empleados ADD COLUMN IF NOT EXISTS usuario_remedy VARCHAR;",
                "ALTER TABLE empleados ADD COLUMN IF NOT EXISTS usuario_t3 VARCHAR;",
                "ALTER TABLE empleados ADD COLUMN IF NOT EXISTS campos_personalizados JSONB;"
            ]
            try:
                engine = get_engine()
                with engine.connect() as conn:
                    for stmt in alter_statements:
                        try:
                            conn.execute(text(stmt))
                        except Exception as e:
                            st.info(f"Aviso: {str(e)}")
                st.success("Migración ejecutada correctamente. Ya puedes usar los nuevos campos.")
            except Exception as e:
                st.error(f"Error al ejecutar la migración: {str(e)}")
        # Botón para inspeccionar columnas actuales
        if st.button("Mostrar columnas actuales de empleados"):
            try:
                engine = get_engine()
                with engine.connect() as conn:
                    result = conn.execute(text("""
                        SELECT column_name, data_type
                        FROM information_schema.columns
                        WHERE table_name = 'empleados'
                        ORDER BY ordinal_position;
                    """))
                    columns = result.fetchall()
                    df_cols = pd.DataFrame(columns, columns=["Columna", "Tipo de dato"])
                    st.dataframe(df_cols, use_container_width=True)
            except Exception as e:
                st.error(f"Error al consultar columnas: {str(e)}")
    
    # Obtener datos
    empleados = listar_empleados()
    if not empleados:
        st.info("No hay datos para mostrar")
        return
    
    # Convertir a DataFrame
    df = pd.DataFrame([{
        'DNI': e.dni,
        'Nombre': e.nombre,
        'Apellido': e.apellido,
        'Fecha Ingreso': e.fecha_ingreso,
        'Estado': e.estado,
        'Skill': e.skill,
        'Es Líder': e.es_lider
    } for e in empleados])
    
    # Métricas principales
    st.subheader("Métricas Principales")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_empleados = len(df)
        st.metric("Total Empleados", total_empleados)
    
    with col2:
        empleados_activos = len(df[df['Estado'] == 'activo'])
        st.metric("Empleados Activos", empleados_activos)
    
    with col3:
        total_lideres = len(df[df['Es Líder'] == True])
        st.metric("Total Líderes", total_lideres)
    
    with col4:
        skills_unicos = df['Skill'].nunique()
        st.metric("Skills Únicos", skills_unicos)
    
    # Gráficos
    st.subheader("Visualizaciones")
    
    # Gráfico de torta - Estado
    col1, col2 = st.columns(2)
    
    with col1:
        estado_counts = df['Estado'].value_counts()
        fig_estado = px.pie(
            values=estado_counts.values,
            names=estado_counts.index,
            title="Distribución por Estado"
        )
        st.plotly_chart(fig_estado, use_container_width=True)
    
    # Sección de verificación
    st.subheader("🔍 Verificación de Empleados")
    dni_verificar = st.text_input("Ingrese el DNI a verificar")
    if dni_verificar:
        empleado = obtener_empleado(dni_verificar)
        if empleado:
            st.success("✅ Empleado encontrado")
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Datos del empleado:**")
                st.write(f"- DNI: {empleado.dni}")
                st.write(f"- Nombre: {empleado.nombre}")
                st.write(f"- Apellido: {empleado.apellido}")
                st.write(f"- Estado: {empleado.estado}")
                st.write(f"- Skill: {empleado.skill}")
                st.write(f"- Es Líder: {'Sí' if empleado.es_lider else 'No'}")
                st.write(f"- Fecha de ingreso: {formatear_fecha(empleado.fecha_ingreso)}")
        else:
            st.error("❌ No se encontró ningún empleado con ese DNI")
            st.info("Sugerencias:")
            st.write("1. Verifique que el DNI esté correctamente escrito")
            st.write("2. Intente importar el empleado nuevamente")
            st.write("3. Verifique que el archivo de importación tenga el formato correcto")
    
    # Gráfico de barras - Ingresos por mes
    with col2:
        df['Mes Ingreso'] = pd.to_datetime(df['Fecha Ingreso']).dt.strftime('%Y-%m')
        ingresos_por_mes = df['Mes Ingreso'].value_counts().sort_index()
        
        fig_ingresos = px.bar(
            x=ingresos_por_mes.index,
            y=ingresos_por_mes.values,
            title="Ingresos por Mes",
            labels={'x': 'Mes', 'y': 'Cantidad'}
        )
        st.plotly_chart(fig_ingresos, use_container_width=True)
    
    # Gráfico de barras - Top Skills
    col1, col2 = st.columns(2)
    
    with col1:
        top_skills = df['Skill'].value_counts().head(10)
        fig_skills = px.bar(
            x=top_skills.index,
            y=top_skills.values,
            title="Top 10 Skills",
            labels={'x': 'Skill', 'y': 'Cantidad'}
        )
        st.plotly_chart(fig_skills, use_container_width=True)
    
    # Gráfico de dispersión - Antigüedad vs Líderes
    with col2:
        df['Antigüedad'] = (datetime.now() - pd.to_datetime(df['Fecha Ingreso'])).dt.days / 365
        fig_antiguedad = px.scatter(
            df,
            x='Antigüedad',
            y='Es Líder',
            title="Antigüedad vs Líderes",
            labels={'x': 'Años', 'y': 'Es Líder'}
        )
        st.plotly_chart(fig_antiguedad, use_container_width=True)
    
    # Filtros personalizados
    st.subheader("Filtros Personalizados")
    
    col1, col2 = st.columns(2)
    
    with col1:
        skill_filtro = st.multiselect(
            "Filtrar por Skills",
            options=sorted(df['Skill'].unique())
        )
        
        estado_filtro = st.multiselect(
            "Filtrar por Estado",
            options=sorted(df['Estado'].unique())
        )
    
    with col2:
        fecha_desde = st.date_input(
            "Fecha de ingreso desde",
            value=df['Fecha Ingreso'].min()
        )
        
        fecha_hasta = st.date_input(
            "Fecha de ingreso hasta",
            value=df['Fecha Ingreso'].max()
        )
    
    # Aplicar filtros
    df_filtrado = df.copy()
    
    if skill_filtro:
        df_filtrado = df_filtrado[df_filtrado['Skill'].isin(skill_filtro)]
    
    if estado_filtro:
        df_filtrado = df_filtrado[df_filtrado['Estado'].isin(estado_filtro)]
    
    df_filtrado = df_filtrado[
        (df_filtrado['Fecha Ingreso'] >= pd.to_datetime(fecha_desde)) &
        (df_filtrado['Fecha Ingreso'] <= pd.to_datetime(fecha_hasta))
    ]
    
    # Mostrar datos filtrados
    st.subheader("Datos Filtrados")
    st.dataframe(df_filtrado, use_container_width=True)
    
    # Exportar a Excel
    if st.button("Exportar a Excel"):
        nombre_archivo = f"dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        df_filtrado.to_excel(nombre_archivo, index=False)
        
        with open(nombre_archivo, 'rb') as f:
            st.download_button(
                "Descargar Excel",
                f,
                file_name=nombre_archivo,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    # --- Sección de depuración: Listar todos los DNIs y nombres ---
    st.subheader("🛠️ Depuración: Lista completa de DNIs y nombres")
    empleados_todos = listar_empleados()
    if empleados_todos:
        data = [{'DNI': e.dni, 'Nombre': e.nombre, 'Apellido': e.apellido} for e in empleados_todos]
        st.dataframe(pd.DataFrame(data), use_container_width=True)
    else:
        st.info("No hay empleados en la base de datos.") 