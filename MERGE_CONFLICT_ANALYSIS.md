# Posibles causas del conflicto de fusión

GitHub reporta que la rama no puede fusionarse automáticamente con la base. A falta de la rama remota para reproducir el conflicto, revisé los cambios locales y detecté varios puntos que pueden chocar con la rama principal si ésta también evolucionó en paralelo:

## 1. Reescritura completa de `src/main.py`
El commit actual reemplaza el `main.py` monolítico por una versión mínima que sólo carga datos y delega el contenido a páginas secundarias. Pasamos de cientos de líneas a ~40, con una estructura nueva basada en `ui.data_context`.【F:src/main.py†L1-L38】

Si la rama principal incorporó mejoras recientes en el antiguo `main.py` (métricas, gráficos o filtros), Git las verá como ediciones sobre las mismas líneas que aquí fueron eliminadas, generando un conflicto directo.

## 2. Cambios en el normalizado de columnas
`src/data_loader.py` ahora fuerza el mapeo `latitud_geo -> norte` y `longitud_geo -> este`, además de normalizar nombres antes del mapeo.【F:src/data_loader.py†L42-L87】 Si el archivo en la rama base tiene otra lógica para las mismas columnas, GitHub marcará conflicto en ese archivo.

## 3. Nueva estructura de páginas y utilidades
Se añadieron módulos `src/ui/data_context.py` y `src/ui/plots.py`, junto con las subpáginas en `src/pages/`. Estos archivos no existen en la rama base y dependen del nuevo `main.py`. Cualquier ajuste hecho en la base sobre la antigua lógica (por ejemplo, gráficos directamente en `main.py`) no tendrá equivalencia aquí, lo que obliga a resolver manualmente qué enfoque conservar.

## Recomendación
Antes de reintentar la fusión:
1. Traer los últimos cambios de la rama base (`git fetch` / `git pull`).
2. Combinar manualmente los cambios en `src/main.py` y `src/data_loader.py`, asegurando que la funcionalidad agregada en la base se integre en la nueva arquitectura multipágina.
3. Ejecutar nuevamente las pruebas o el flujo de Streamlit para verificar que los gráficos sigan cargando con los 30 días por defecto.

Así se eliminarán los conflictos y la rama quedará lista para fusionarse.
