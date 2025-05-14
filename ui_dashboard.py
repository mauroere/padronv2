import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from crud import listar_empleados
from utils import formatear_fecha

def mostrar_pagina_dashboard():
    """Muestra la página del dashboard"""
    st.title("Dashboard")
    
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