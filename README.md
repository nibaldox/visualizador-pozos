# Visualizador de Pozos de Tronadura

Aplicación en Python para visualizar y analizar datos de pozos de tronadura.

## Requisitos

- Python 3.10+
- Dependencias: ver `requirements.txt`

## Instalación

1. Clonar el repositorio
2. Crear entorno virtual:
```bash
python -m venv venv
```
3. Activar entorno virtual (Windows):
```bash
.\\venv\\Scripts\\activate
```
4. Instalar dependencias:
```bash
pip install -r requirements.txt
```

## Uso

```bash
# Activar entorno virtual (Windows)
.\\venv\\Scripts\\activate

# Ejecutar aplicación
streamlit run src/main.py
```

## Funcionalidades

- Carga de datos desde archivo Excel
- Filtros avanzados por estado y profundidad
- Mapa interactivo de ubicación de pozos

## Licencia

MIT
