import streamlit as st
import pandas as pd
import datetime
import psycopg2
import time
from crud import crear_empleado, actualizar_empleado, eliminar_empleado, obtener_empleado, listar_empleados
from utils import validar_dni, normalizar_fecha, normalizar_estado, normalizar_boolean, formatear_fecha

def mostrar_formulario_empleado(empleado=None):
    """Muestra el formulario para crear/editar empleado con validación avanzada y mejor UX/UI"""
    st.markdown("### {} Empleado {}".format(
        "Editar" if empleado else "Nuevo",
        f"<span style='color:#888'>({empleado.dni})</span>" if empleado else ""
    ), unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    errores = {}

    # Limpiar campos si se acaba de crear un empleado
    if not empleado and st.session_state.get('reset_form'):
        dni = ""
        nombre = ""
        apellido = ""
        skill = ""
        fecha_ingreso = datetime.datetime.now()
        estado = "activo"
        es_lider = False
        st.session_state['reset_form'] = False
    else:
        dni = empleado.dni if empleado else ""
        nombre = empleado.nombre if empleado else ""
        apellido = empleado.apellido if empleado else ""
        skill = empleado.skill if empleado else ""
        fecha_ingreso = empleado.fecha_ingreso if empleado else datetime.datetime.now()
        estado = empleado.estado if empleado else "activo"
        es_lider = empleado.es_lider if empleado else False

    with st.form("form_empleado"):
        with col1:
            dni = st.text_input("🆔 DNI", value=dni, disabled=bool(empleado))
            nombre = st.text_input("👤 Nombre", value=nombre)
            apellido = st.text_input("👥 Apellido", value=apellido)
            skill = st.text_input("💡 Skill", value=skill)
        with col2:
            fecha_ingreso = st.date_input(
                "📅 Fecha de Ingreso",
                value=fecha_ingreso
            )
            estado = st.selectbox(
                "🔄 Estado",
                options=['activo', 'inactivo'],
                index=0 if estado == 'activo' else 1
            )
            es_lider = st.checkbox("⭐ Es Líder", value=es_lider)
        
        # Validaciones
        if not dni or not validar_dni(dni):
            errores['dni'] = "DNI inválido. Debe tener 7 u 8 dígitos numéricos."
        if not nombre.strip():
            errores['nombre'] = "El nombre es obligatorio."
        if not apellido.strip():
            errores['apellido'] = "El apellido es obligatorio."
        if not skill.strip():
            errores['skill'] = "El skill es obligatorio."
        if not isinstance(fecha_ingreso, (datetime.date, datetime.datetime)):
            errores['fecha_ingreso'] = "Fecha inválida."
        
        # Mostrar errores debajo de cada campo
        for campo, mensaje in errores.items():
            st.markdown(f"<span style='color:red;font-size:12px;'>{mensaje}</span>", unsafe_allow_html=True)
        
        submit = st.form_submit_button("💾 Guardar", disabled=bool(errores))
        
        if submit and not errores:
            # Convertir fecha a datetime.datetime si es necesario
            fecha_dt = (
                datetime.datetime.combine(fecha_ingreso, datetime.datetime.min.time())
                if isinstance(fecha_ingreso, datetime.date) and not isinstance(fecha_ingreso, datetime.datetime)
                else fecha_ingreso
            )
            datos = {
                'nombre': nombre.strip(),
                'apellido': apellido.strip(),
                'fecha_ingreso': normalizar_fecha(fecha_dt),
                'estado': normalizar_estado(estado),
                'skill': skill.strip(),
                'es_lider': normalizar_boolean(es_lider)
            }
            try:
                if empleado:
                    actualizado = actualizar_empleado(dni, datos, st.session_state.user.id)
                    if actualizado:
                        st.success("✅ Empleado actualizado correctamente")
                        return True
                    else:
                        st.error("No se pudo actualizar el empleado.")
                else:
                    creado = crear_empleado(dni, **datos, usuario_id=st.session_state.user.id)
                    if creado:
                        st.session_state['reset_form'] = True
                        st.success("✅ Empleado creado correctamente")
                        time.sleep(2)
                        st.rerun()
                        return True
                    else:
                        st.error("No se pudo crear el empleado.")
            except Exception as e:
                if hasattr(e, 'orig') and isinstance(e.orig, psycopg2.errors.UniqueViolation):
                    st.error("Ya existe un empleado con ese DNI.")
                else:
                    st.error(f"Error al guardar: {str(e)}")
        return False

def mostrar_lista_empleados():
    """Muestra la lista de empleados con filtros y acciones mejoradas"""
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
    # Botones de acción mejorados
    st.subheader("Acciones")
    col1, col2 = st.columns(2)
    with col1:
        dni_editar = st.text_input("DNI a editar")
        if dni_editar and st.button("✏️ Editar"):
            empleado = obtener_empleado(dni_editar)
            if empleado:
                if mostrar_formulario_empleado(empleado):
                    st.rerun()
            else:
                st.error("Empleado no encontrado")
    with col2:
        dni_eliminar = st.text_input("DNI a eliminar")
        if dni_eliminar and st.button("🗑️ Eliminar"):
            if st.session_state.rol != 'admin':
                st.error("Solo los administradores pueden eliminar empleados")
            else:
                empleado = obtener_empleado(dni_eliminar)
                if not empleado:
                    st.error("Empleado no encontrado")
                else:
                    if st.confirm(f"¿Estás seguro de que deseas eliminar al empleado {empleado.nombre} {empleado.apellido} (DNI: {empleado.dni})? Esta acción no se puede deshacer."):
                        if eliminar_empleado(dni_eliminar, st.session_state.user.id):
                            st.success("Empleado eliminado correctamente")
                            st.rerun()
                        else:
                            st.error("No se pudo eliminar el empleado.")

def mostrar_pagina_abm():
    """Muestra la página principal de ABM"""
    st.title("Gestión de Empleados")
    tab1, tab2 = st.tabs(["Lista de Empleados", "Nuevo Empleado"])
    with tab1:
        mostrar_lista_empleados()
    with tab2:
        if mostrar_formulario_empleado():
            st.rerun() 