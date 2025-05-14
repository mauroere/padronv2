# Sistema de Gestión de Empleados

Aplicación de escritorio desarrollada con Streamlit para la gestión de empleados, con enfoque tipo dashboard administrativo.

## Características

- 🔐 Autenticación de usuarios con roles (admin/usuario)
- 👥 ABM completo de empleados
- 📤 Importación masiva desde Excel/CSV
- 📊 Dashboard con métricas y visualizaciones
- 📝 Historial de cambios
- 🔍 Filtros dinámicos
- 📥 Exportación de reportes

## Requisitos

- Python 3.8+
- Dependencias listadas en `requirements.txt`

## Instalación

1. Clonar el repositorio:

```bash
git clone [url-del-repositorio]
cd padron_app
```

2. Crear entorno virtual:

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Instalar dependencias:

```bash
pip install -r requirements.txt
```

4. Inicializar la base de datos:

```bash
python db.py
```

## Uso

1. Iniciar la aplicación:

```bash
streamlit run main.py
```

2. Acceder a la aplicación en el navegador:

```
http://localhost:8501
```

3. Credenciales por defecto:

- Usuario: admin
- Contraseña: admin123

## Estructura del Proyecto

```
padron_app/
├── main.py                # Punto de entrada
├── db.py                  # Base de datos
├── auth.py                # Autenticación
├── crud.py                # Operaciones CRUD
├── utils.py               # Utilidades
├── ui_abm.py              # Interfaz ABM
├── ui_import.py           # Importación
├── ui_log.py              # Historial
├── ui_dashboard.py        # Dashboard
├── requirements.txt       # Dependencias
└── README.md             # Documentación
```

## Características Técnicas

- **Base de Datos**: SQLite con SQLAlchemy
- **Frontend**: Streamlit
- **Visualizaciones**: Plotly
- **Procesamiento de Datos**: Pandas
- **Autenticación**: bcrypt

## Contribuir

1. Fork el repositorio
2. Crear una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## Contacto

[Tu Nombre] - [@tutwitter](https://twitter.com/tutwitter) - email@example.com

Link del Proyecto: [https://github.com/tuusuario/padron_app](https://github.com/tuusuario/padron_app)
