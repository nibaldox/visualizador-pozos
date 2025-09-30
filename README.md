# Visualizador de Pozos de Tronadura - Open Pit Blast Hole Visualization

## Descripción
Esta aplicación permite visualizar y analizar datos de pozos de tronadura en minería a cielo abierto, facilitando la exploración de información clave mediante mapas de calor, gráficos 3D y dashboards interactivos. El objetivo es proporcionar una herramienta clara, eficiente y fácilmente extensible para ingenieros, geólogos y analistas.

## Características principales
- **Carga flexible de datos** desde archivos Excel, con normalización automática de nombres de columnas.
- **Visualización en pestañas**: Dashboard, mapa de calor, scatter categórico y gráfico 3D.
- **Filtros avanzados**: Multiselección, filtro por fecha y limpieza de filtros irrelevantes.
- **Carga inicial optimizada**: Al cargar nuevos datos la aplicación muestra, por defecto, solo los últimos 30 días para acelerar el renderizado sin perder contexto.
- **Mapa de calor**: Representa kilos de explosivo o factor de carga, con escalas de color verde-rojo.
- **Hover personalizado**: Nombres cortos y datos en negrita, con máximo 2 decimales en todos los valores numéricos.
- **Estética consistente**: Todos los gráficos de Plotly usan fondos transparentes y los dispersogramas de coordenadas mantienen relación 1:1 sin líneas de cuadrícula para mejorar la lectura.
- **Visualización 3D**: Pozos en UTM y cota, con color por variable seleccionable.
- **Código limpio y modular**: Funciones auxiliares reutilizables para hover y redondeo.

## Estructura del proyecto
```
visualizador_pozos/
├── src/
│   ├── main.py           # App principal Streamlit
│   ├── data_loader.py    # Utilidades de carga y limpieza de datos
│   └── ...
├── requirements.txt      # Dependencias Python
├── .gitignore            # Exclusiones para el repo
└── README.md             # Este archivo
```

## Requisitos
- Python 3.10+
- Paquetes: ver `requirements.txt` (incluye streamlit, pandas, plotly, openpyxl, etc.)

## Instalación
1. Clona el repositorio:
   ```bash
   git clone https://github.com/nibaldox/visualizador-pozos.git
   cd visualizador-pozos
   ```
2. Crea un entorno virtual (opcional pero recomendado):
   ```bash
   python -m venv venv
   # En Windows:
   .\venv\Scripts\activate
   # En Linux/Mac:
   source venv/bin/activate
   ```
3. Instala dependencias:
   ```bash
   pip install -r requirements.txt
   ```

## Ejecución
1. Coloca tu archivo de datos Excel en la carpeta adecuada (ver instrucciones en la app).
2. Ejecuta la app:
   ```bash
   streamlit run src/main.py
   ```
3. Abre tu navegador en [http://localhost:8501](http://localhost:8501)

## Lineamientos de código y contribución
- Sigue los **principios de clean code**: funciones pequeñas, bien nombradas, con docstrings y anotaciones de tipo.
- Documenta cualquier función, clase o variable pública.
- Usa las utilidades `preparar_columnas_aux` y `obtener_hover` para hover y redondeo en nuevos gráficos.
- No mezcles lógica de UI y procesamiento de datos en una sola función.
- Si agregas nuevas visualizaciones, reutiliza la lógica de hover y asegúrate de redondear los datos a 2 decimales.
- Toda mejora debe estar documentada en el archivo `plan_implementacion.md`.

## ¿Cómo continuar las mejoras?
- Puedes agregar nuevos tipos de visualización (mapas, histogramas, exportación de reportes, etc.).
- Mejora la performance optimizando el filtrado y la carga de datos.
- Integra validaciones adicionales para archivos de entrada.
- Agrega tests unitarios para funciones clave.
- Si implementas nuevas pestañas o dashboards, sigue la estructura modular y reutiliza componentes auxiliares.
- Consulta los issues y tareas pendientes en el archivo `plan_implementacion.md`.

## Contacto y soporte
Para dudas, sugerencias o reportar bugs, abre un issue en el repositorio o contacta a los mantenedores.

---

*Este proyecto está en evolución continua. ¡Tu colaboración y sugerencias son bienvenidas!*
