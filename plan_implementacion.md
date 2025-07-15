# Visualizador de Pozos de Tronadura - PLAN DE IMPLEMENTACIÓN Y REGISTRO DE CAMBIOS

## Resumen
Este proyecto es un visualizador de datos de pozos de tronadura para minería open pit, desarrollado en Python usando Streamlit. Permite cargar archivos Excel, aplicar filtros avanzados y visualizar los pozos en coordenadas UTM con mapas de calor según kilos de explosivo y factor de carga. El código sigue principios de clean code y está documentado.

---

## Cambios recientes
- Se corrigió la normalización y mapeo de nombres de columna para soportar variantes como `Kilos_Cargados_real`, `Longitud_real` y `Longitud_teo`.
- El cálculo del factor de carga ahora es robusto y siempre se muestra el gráfico, aunque todos los valores sean iguales.
- Se suprime la advertencia de openpyxl sobre estilos.
- Se mejoró la documentación y anotación del código.
- Se agregaron validaciones y manejo de errores en la carga y procesamiento de datos.

---

## Siguiente pasos
- Verificar y actualizar el archivo README.md para reflejar los cambios y explicar el flujo de columnas.
- Verificar y actualizar el archivo .gitignore.

---

## Observaciones
- Si tienes columnas con nombres distintos en tu Excel, puedes agregarlas fácilmente al mapeo en `data_loader.py`.
- El factor de carga se calcula como `kilos_cargados_real / longitud_real` o, si no existe longitud_real, se usa `longitud_teo`.

---

## Última actualización
- Fecha: 2025-07-14
- Cambios realizados por Cascade AI

## Objetivo
Crear una aplicación Python para visualizar pozos de tronadura con sus propiedades...

[Contenido completo del plan detallado]
