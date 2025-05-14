import streamlit as st
import pandas as pd
from datetime import datetime
from crud import crear_empleado, actualizar_empleado, eliminar_empleado, obtener_empleado, listar_empleados
from utils import validar_dni, normalizar_fecha, normalizar_estado, normalizar_boolean, formatear_fecha

def mostrar_formulario_empleado(empleado=None):
    """Muestra el formulario para crear/editar empleado"""
    with st.form("form_empleado"):
        dni = st.text_input("DNI", value=empleado.dni if empleado else "")
        nombre = st.text_input("Nombre", value=empleado.nombre if empleado else "")
        apellido = st.text_input("Apellido", value=empleado.apellido if empleado else "")
        fecha_ingreso = st.date_input(
            "Fecha de Ingreso",
            value=empleado.fecha_ingreso if empleado else datetime.now()
        )
        estado = st.selectbox(
            "Estado",
            options=['activo', 'inactivo'],
            index=0 if not empleado or empleado.estado == 'activo' else 1
        )
        skill = st.text_input("Skill", value=empleado.skill if empleado else "")
        es_lider = st.checkbox("Es Líder", value=empleado.es_lider if empleado else False)
        
        submit = st.form_submit_button("Guardar")
        
        if submit:
            if not validar_dni(dni):
                st.error("DNI inválido")
                return False
                
            datos = {
                'nombre': nombre,
                'apellido': apellido,
                'fecha_ingreso': normalizar_fecha(fecha_ingreso),
                'estado': normalizar_estado(estado),
                'skill': skill,
                'es_lider': normalizar_boolean(es_lider)
            }
            
            try:
                if empleado:
                    actualizar_empleado(dni, datos, st.session_state.user.id)
                    st.success("Empleado actualizado correctamente")
                else:
                    crear_empleado(dni, **datos, usuario_id=st.session_state.user.id)
                    st.success("Empleado creado correctamente")
                return True
            except Exception as e:
                st.error(f"Error al guardar: {str(e)}")
                return False

def mostrar_lista_empleados():
    """Muestra la lista de empleados con filtros"""
    st.subheader("Filtros")
    col1, col2 = st.columns(2)
    
    with col1:
        filtro_dni = st.text_input("Filtrar por DNI")
        filtro_nombre = st.text_input("Filtrar por Nombre")
    
    with col2:
        filtro_estado = st.selectbox("Filtrar por Estado", ['', 'activo', 'inactivo'])
        filtro_lider = st.selectbox("Filtrar por Líder", ['', 'Sí', 'No'])
    
    filtros = {}
    if filtro_dni:
        filtros['dni'] = filtro_dni
    if filtro_nombre:
        filtros['nombre'] = filtro_nombre
    if filtro_estado:
        filtros['estado'] = filtro_estado
    if filtro_lider:
        filtros['es_lider'] = filtro_lider == 'Sí'
    
    empleados = listar_empleados(filtros)
    
    if not empleados:
        st.info("No se encontraron empleados")
        return
    
    # Convertir a DataFrame para mostrar
    df = pd.DataFrame([{
        'DNI': e.dni,
        'Nombre': e.nombre,
        'Apellido': e.apellido,
        'Fecha Ingreso': formatear_fecha(e.fecha_ingreso),
        'Estado': e.estado,
        'Skill': e.skill,
        'Es Líder': 'Sí' if e.es_lider else 'No'
    } for e in empleados])
    
    st.dataframe(df, use_container_width=True)
    
    # Botones de acción
    st.subheader("Acciones")
    col1, col2 = st.columns(2)
    
    with col1:
        dni_editar = st.text_input("DNI a editar")
        if dni_editar and st.button("Editar"):
            empleado = obtener_empleado(dni_editar)
            if empleado:
                if mostrar_formulario_empleado(empleado):
                    st.rerun()
            else:
                st.error("Empleado no encontrado")
    
    with col2:
        dni_eliminar = st.text_input("DNI a eliminar")
        if dni_eliminar and st.button("Eliminar"):
            if st.session_state.rol != 'admin':
                st.error("Solo los administradores pueden eliminar empleados")
            else:
                if eliminar_empleado(dni_eliminar, st.session_state.user.id):
                    st.success("Empleado eliminado correctamente")
                    st.rerun()
                else:
                    st.error("Empleado no encontrado")

def mostrar_pagina_abm():
    """Muestra la página principal de ABM"""
    st.title("Gestión de Empleados")
    
    tab1, tab2 = st.tabs(["Lista de Empleados", "Nuevo Empleado"])
    
    with tab1:
        mostrar_lista_empleados()
    
    with tab2:
        if mostrar_formulario_empleado():
            st.rerun() 