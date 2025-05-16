import streamlit as st
import pandas as pd
import datetime
import psycopg2
import time
import random
from crud import crear_empleado, actualizar_empleado, eliminar_empleado, obtener_empleado, listar_empleados
from utils import validar_dni, normalizar_fecha, normalizar_estado, normalizar_boolean, formatear_fecha

def mostrar_formulario_empleado(empleado=None, form_key=None):
    """Muestra el formulario para crear/editar empleado con validación avanzada y mejor UX/UI"""
    st.markdown("### {} Empleado {}".format(
        "Editar" if empleado else "Nuevo",
        f"<span style='color:#888'>({empleado.dni})</span>" if empleado else ""
    ), unsafe_allow_html=True)
    
    # Inicializar campos personalizados en session_state
    if 'campos_personalizados' not in st.session_state:
        st.session_state['campos_personalizados'] = []
    if 'agregar_campo' not in st.session_state:
        st.session_state['agregar_campo'] = False
    if 'eliminar_campo' not in st.session_state:
        st.session_state['eliminar_campo'] = None

    # Obtener valores existentes para autocompletado
    empleados = listar_empleados()
    skills_unicos = sorted(list(set(e.skill for e in empleados if e.skill)))
    areas_unicas = sorted(list(set(getattr(e, 'area', '') for e in empleados if getattr(e, 'area', ''))))
    proyectos_unicos = sorted(list(set(getattr(e, 'proyecto', '') for e in empleados if getattr(e, 'proyecto', ''))))

    # Datos iniciales
    if not empleado and st.session_state.get('reset_form'):
        dni = ""
        nombre = ""
        apellido = ""
        email = ""
        telefono = ""
        direccion = ""
        fecha_ingreso = datetime.datetime.now()
        estado = "activo"
        skill = ""
        area = ""
        proyecto = ""
        es_lider = False
        usuario_nt = ""
        usuario_hada = ""
        usuario_remedy = ""
        usuario_t3 = ""
        st.session_state['reset_form'] = False
        st.session_state['campos_personalizados'] = []
    else:
        dni = empleado.dni if empleado else ""
        nombre = empleado.nombre if empleado else ""
        apellido = empleado.apellido if empleado else ""
        email = getattr(empleado, 'email', "") if empleado else ""
        telefono = getattr(empleado, 'telefono', "") if empleado else ""
        direccion = getattr(empleado, 'direccion', "") if empleado else ""
        fecha_ingreso = empleado.fecha_ingreso if empleado else datetime.datetime.now()
        estado = empleado.estado if empleado else "activo"
        skill = empleado.skill if empleado else ""
        area = getattr(empleado, 'area', "") if empleado else ""
        proyecto = getattr(empleado, 'proyecto', "") if empleado else ""
        es_lider = empleado.es_lider if empleado else False
        usuario_nt = getattr(empleado, 'usuario_nt', "") if empleado else ""
        usuario_hada = getattr(empleado, 'usuario_hada', "") if empleado else ""
        usuario_remedy = getattr(empleado, 'usuario_remedy', "") if empleado else ""
        usuario_t3 = getattr(empleado, 'usuario_t3', "") if empleado else ""
        st.session_state['campos_personalizados'] = getattr(empleado, 'campos_personalizados', []) if empleado else []

    # Usar clave única para cada formulario
    if form_key is None:
        form_key = f"form_empleado_nuevo_{st.session_state['form_key']}" if not empleado else f"form_empleado_edit_{dni}_{st.session_state['form_key']}"

    # Manejar acciones de campos personalizados fuera del formulario
    if st.session_state.get('agregar_campo'):
        st.session_state['campos_personalizados'].append({"nombre": "", "valor": ""})
        st.session_state['agregar_campo'] = False
        st.rerun()
    
    if st.session_state.get('eliminar_campo') is not None:
        st.session_state['campos_personalizados'].pop(st.session_state['eliminar_campo'])
        st.session_state['eliminar_campo'] = None
        st.rerun()

    with st.form(key=form_key):
        # Sección: Datos personales
        with st.expander("👤 Datos personales", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                dni = st.text_input("🆔 DNI*", value=dni, disabled=bool(empleado), 
                                  help="DNI del empleado (7 u 8 dígitos)")
                nombre = st.text_input("👤 Nombre*", value=nombre,
                                     help="Nombre del empleado")
                apellido = st.text_input("👥 Apellido*", value=apellido,
                                       help="Apellido del empleado")
                email = st.text_input("✉️ Email", value=email,
                                    help="Correo electrónico del empleado")
            with col2:
                telefono = st.text_input("📞 Teléfono", value=telefono,
                                       help="Número de teléfono")
                direccion = st.text_input("🏠 Dirección", value=direccion,
                                        help="Dirección completa")

        # Sección: Datos laborales
        with st.expander("💼 Datos laborales", expanded=True):
            col3, col4 = st.columns(2)
            with col3:
                fecha_ingreso = st.date_input("📅 Fecha de ingreso*", value=fecha_ingreso,
                                            help="Fecha de ingreso del empleado")
                estado = st.selectbox("🔄 Estado*", ["activo", "inactivo"], 
                                    index=0 if estado == "activo" else 1,
                                    help="Estado actual del empleado")
                skill = st.selectbox("💡 Skill*", options=[""] + skills_unicos,
                                   index=0 if not skill else skills_unicos.index(skill) + 1,
                                   help="Habilidad o especialidad del empleado")
                if skill == "":
                    skill = st.text_input("💡 Nuevo Skill", help="Agregar un nuevo skill")
            with col4:
                area = st.selectbox("🏢 Área", options=[""] + areas_unicas,
                                  index=0 if not area else areas_unicas.index(area) + 1,
                                  help="Área o departamento")
                if area == "":
                    area = st.text_input("🏢 Nueva Área", help="Agregar una nueva área")
                proyecto = st.selectbox("📁 Proyecto", options=[""] + proyectos_unicos,
                                     index=0 if not proyecto else proyectos_unicos.index(proyecto) + 1,
                                     help="Proyecto asignado")
                if proyecto == "":
                    proyecto = st.text_input("📁 Nuevo Proyecto", help="Agregar un nuevo proyecto")
                es_lider = st.checkbox("⭐ ¿Es líder?", value=es_lider,
                                     help="Indica si el empleado es líder de equipo")

        # Sección: Acceso/Sistemas
        with st.expander("🔑 Acceso / Sistemas", expanded=False):
            col5, col6 = st.columns(2)
            with col5:
                usuario_nt = st.text_input("🔑 Usuario NT", value=usuario_nt,
                                         help="Usuario de Windows NT")
                usuario_hada = st.text_input("🔑 Usuario HADA", value=usuario_hada,
                                           help="Usuario del sistema HADA")
            with col6:
                usuario_remedy = st.text_input("🔑 Usuario Remedy", value=usuario_remedy,
                                             help="Usuario del sistema Remedy")
                usuario_t3 = st.text_input("🔑 Usuario T3", value=usuario_t3,
                                         help="Usuario del sistema T3")

        # Sección: Campos personalizados
        with st.expander("➕ Campos personalizados", expanded=False):
            if st.form_submit_button("➕ Agregar campo personalizado"):
                st.session_state['agregar_campo'] = True
                st.rerun()
            
            campos_personalizados = []
            for i, campo in enumerate(st.session_state['campos_personalizados']):
                col1, col2, col3 = st.columns([2, 2, 1])
                with col1:
                    campo["nombre"] = st.text_input(f"Nombre campo {i+1}", value=campo["nombre"],
                                                  key=f"nombre_campo_{form_key}_{i}")
                with col2:
                    campo["valor"] = st.text_input(f"Valor campo {i+1}", value=campo["valor"],
                                                 key=f"valor_campo_{form_key}_{i}")
                with col3:
                    if st.form_submit_button("🗑️", key=f"del_campo_{form_key}_{i}"):
                        st.session_state['eliminar_campo'] = i
                        st.rerun()
                campos_personalizados.append(campo)

        # Validaciones
        errores = []
        if not dni or not dni.isdigit() or not (7 <= len(dni) <= 8):
            errores.append("DNI inválido. Debe tener 7 u 8 dígitos numéricos.")
        if not nombre.strip():
            errores.append("El nombre es obligatorio.")
        if not apellido.strip():
            errores.append("El apellido es obligatorio.")
        if not skill.strip():
            errores.append("El skill es obligatorio.")
        if not isinstance(fecha_ingreso, (datetime.date, datetime.datetime)):
            errores.append("Fecha inválida.")
        if email and not '@' in email:
            errores.append("El email debe ser válido (contener @).")
        if telefono and not telefono.replace('+', '').replace('-', '').replace(' ', '').isdigit():
            errores.append("El teléfono debe contener solo números, +, - o espacios.")

        # Mostrar errores con estilo
        if errores:
            st.markdown("""
            <style>
            .error-box {
                background-color: #ffebee;
                border: 1px solid #ffcdd2;
                border-radius: 4px;
                padding: 10px;
                margin: 10px 0;
            }
            </style>
            """, unsafe_allow_html=True)
            st.markdown('<div class="error-box">', unsafe_allow_html=True)
            for err in errores:
                st.markdown(f"❌ {err}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Botones de acción
        col1, col2 = st.columns([1, 4])
        with col1:
            submit = st.form_submit_button("💾 Guardar", disabled=bool(errores))
        with col2:
            limpiar = st.form_submit_button("🔄 Limpiar formulario")
            if limpiar:
                st.session_state['reset_form'] = True
                st.rerun()
        
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
                'es_lider': normalizar_boolean(es_lider),
                'email': email.strip(),
                'telefono': telefono.strip(),
                'direccion': direccion.strip(),
                'area': area.strip(),
                'proyecto': proyecto.strip(),
                'usuario_nt': usuario_nt.strip(),
                'usuario_hada': usuario_hada.strip(),
                'usuario_remedy': usuario_remedy.strip(),
                'usuario_t3': usuario_t3.strip(),
                'campos_personalizados': campos_personalizados
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
                        st.session_state['form_key'] = random.randint(0, 1_000_000)
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
    # Controlar edición con variable de sesión
    if 'edit_dni' not in st.session_state:
        st.session_state['edit_dni'] = None
    st.subheader("Empleados")
    for e in empleados:
        cols = st.columns([2, 2, 2, 2, 2, 2, 1, 1])
        cols[0].write(f"**DNI:** {e.dni}")
        cols[1].write(f"**Nombre:** {e.nombre}")
        cols[2].write(f"**Apellido:** {e.apellido}")
        cols[3].write(f"**Fecha Ingreso:** {formatear_fecha(e.fecha_ingreso)}")
        cols[4].write(f"**Estado:** {e.estado}")
        cols[5].write(f"**Skill:** {e.skill}")
        if cols[6].button("✏️", key=f"edit_{e.dni}", help="Editar"):
            st.session_state['edit_dni'] = e.dni
        if cols[7].button("🗑️", key=f"delete_{e.dni}", help="Eliminar"):
            if st.session_state.rol != 'admin':
                st.error("Solo los administradores pueden eliminar empleados")
            else:
                st.session_state['delete_dni'] = e.dni
        # Confirmación de eliminación
        if st.session_state.get('delete_dni') == e.dni:
            st.warning(f"¿Estás seguro de que deseas eliminar al empleado {e.nombre} {e.apellido} (DNI: {e.dni})? Esta acción no se puede deshacer.")
            col_conf, col_cancel = st.columns([1, 1])
            with col_conf:
                if st.button("✅ Confirmar eliminación", key=f"confirm_delete_{e.dni}"):
                    resultado = eliminar_empleado(e.dni, st.session_state.user.id)
                    if resultado == "inactivo":
                        st.info("El empleado tiene historial y fue marcado como inactivo. No se eliminó físicamente para preservar la auditoría.")
                        st.session_state['delete_dni'] = None
                        st.rerun()
                    elif resultado:
                        st.success("Empleado eliminado correctamente")
                        st.session_state['delete_dni'] = None
                        st.rerun()
                    else:
                        st.error("No se pudo eliminar el empleado.")
                        st.session_state['delete_dni'] = None
            with col_cancel:
                if st.button("❌ Cancelar", key=f"cancel_delete_{e.dni}"):
                    st.session_state['delete_dni'] = None
        # Mostrar formulario de edición solo para el empleado seleccionado
        if st.session_state['edit_dni'] == e.dni:
            if mostrar_formulario_empleado(e, form_key=f"form_empleado_edit_{e.dni}_{st.session_state['form_key']}"):
                st.session_state['edit_dni'] = None
                st.rerun()

def mostrar_pagina_abm():
    """Muestra la página principal de ABM"""
    # Inicializar form_key si no existe
    if 'form_key' not in st.session_state:
        st.session_state['form_key'] = random.randint(0, 1_000_000)
        
    st.title("Gestión de Empleados")
    tab1, tab2 = st.tabs(["Lista de Empleados", "Nuevo Empleado"])
    with tab1:
        mostrar_lista_empleados()
    with tab2:
        if mostrar_formulario_empleado(form_key=f"form_empleado_nuevo_{st.session_state['form_key']}"):
            st.rerun() 