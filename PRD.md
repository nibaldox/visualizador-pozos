# Documento de Requerimientos del Producto (PRD)

## Proyecto: Visualizador de Pozos de Tronadura (Open Pit Blast Hole Visualization)

---

### 1. **Resumen Ejecutivo**

Aplicación interactiva para la visualización, análisis y control de datos de pozos de tronadura en minería a cielo abierto. Permite a usuarios geotécnicos, ingenieros y analistas entender la calidad de la perforación, la distribución de explosivos y los riesgos asociados a la estabilidad de taludes, facilitando la toma de decisiones y el control operacional.

---

### 2. **Objetivos del Producto**

- Visualizar espacialmente pozos de tronadura y sus atributos principales.
- Calcular y mostrar métricas clave para control de calidad y estabilidad de taludes.
- Permitir filtrado avanzado y análisis interactivo de la data cargada.
- Facilitar la identificación de desviaciones y riesgos geotécnicos.

---

### 3. **Requerimientos Funcionales**

- Carga de datos desde archivos Excel con normalización automática de columnas.
- Visualización en tabs: dashboard, mapas de calor, análisis 3D y sección geotécnica.
- Filtros multiselección y por fecha.
- Hover personalizado con nombres cortos y datos en negrita (máx. 2 decimales).
- Cálculo de métricas geotécnicas:
  - Uniformidad del factor de carga (kg/m) y su mapa de calor.
  - Análisis de longitud real vs teórica (desviación estándar, % sub/sobre-perforados).
  - Variabilidad de diámetro de pozos y % fuera de tolerancia.
  - Carga total y específica en zonas críticas (por polígono/banco/zona).
- Exportación de reportes y tablas (futuro).

---

### 4. **Requerimientos No Funcionales**

- Código limpio, modular y documentado (principios clean code).
- Interfaz intuitiva y responsiva (Streamlit + Plotly).
- Soporte para grandes volúmenes de datos.
- Documentación clara para onboarding de nuevos desarrolladores.
- No almacenar ni subir archivos de datos sensibles al repositorio.

---

### 5. **Criterios de Éxito**

- El usuario puede cargar cualquier archivo Excel válido y visualizar la información sin errores.
- Las métricas geotécnicas clave aparecen siempre, incluso si los valores son homogéneos.
- Los filtros y visualizaciones permiten identificar desviaciones relevantes para la estabilidad de taludes.
- El código es fácilmente mantenible y extensible.

---

### 6. **Stakeholders**

- Geotécnicos
- Ingenieros de tronadura
- Analistas de datos mineros
- Desarrolladores de software

---

### 7. **Supuestos y Limitaciones**

- Se asume que los archivos de entrada contienen las columnas mínimas requeridas (UTM, kilos, longitud, diámetro, polígono/zona).
- El sistema no realiza cálculos de estabilidad numérica, solo métricas y visualización para soporte de decisiones.

---

### 8. **Roadmap y Mejoras Futuras**

- Exportación de reportes automáticos.
- Integración con sistemas de gestión minera.
- Análisis temporal y comparativo entre campañas.
- Alertas automáticas ante desviaciones críticas.

---

*Última actualización: 2025-07-15*
