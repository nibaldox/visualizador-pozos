import streamlit as st

from ui.data_context import cargar_y_filtrar_datos, formatear_tabla
from ui.styles import aplicar_estilos_base

st.set_page_config(page_title="Visualizador de Pozos", layout="wide")
aplicar_estilos_base()

st.title("Visualizador de Pozos de Tronadura")

st.markdown(
    """
    Carga un archivo Excel con los resultados de perforación y tronadura para habilitar
    los tableros especializados. La aplicación ahora está organizada en páginas para
    separar el análisis de desempeño, la revisión geotécnica, los mapas espaciales y la
    visualización 3D.
    """
)

datos = cargar_y_filtrar_datos()
if datos is None:
    st.info(
        "Sube un archivo Excel para comenzar. Una vez cargado podrás navegar por las páginas "
        "de Dashboard, Mapas, Geotecnia y 3D."
    )
    st.stop()

st.success("Datos cargados correctamente. Usa el menú lateral para ajustar filtros.")

st.divider()

with st.expander("Vista previa del subconjunto filtrado", expanded=False):
    st.caption("Se muestran hasta 50 registros para mantener la interfaz ágil.")
    df_vista = formatear_tabla(datos.filtrados)
    st.dataframe(df_vista.head(50), use_container_width=True, height=360)

st.divider()
st.markdown("### Páginas disponibles")

col_a, col_b = st.columns(2)
with col_a:
    st.markdown(
        """
        **Dashboard de indicadores**
        
        • Métricas rápidas y distribución del factor de carga.
        
        • Histogramas, boxplots y análisis categórico.
        """
    )
    st.markdown(
        """
        **Geotecnia y control de calidad**
        
        • Seguimiento de longitudes reales vs. teóricas.
        
        • Variabilidad de diámetro y uniformidad de carga.
        """
    )
with col_b:
    st.markdown(
        """
        **Mapa y segmentación espacial**
        
        • Dispersión UTM con color continuo o por categorías.
        
        • Tablas de resumen por zona crítica.
        """
    )
    st.markdown(
        """
        **Visualización 3D**
        
        • Nube de puntos 3D coloreada por métricas clave.
        
        • Exploración espacial para identificar anomalías.
        """
    )

st.caption("Los filtros aplicados aquí impactan en todas las páginas de análisis.")
