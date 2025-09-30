import streamlit as st

from ui.data_context import cargar_y_filtrar_datos, formatear_tabla

st.set_page_config(page_title="Visualizador de Pozos", layout="wide")

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

st.subheader("Vista previa de los datos filtrados")

df_vista = formatear_tabla(datos.filtrados)
st.dataframe(df_vista.head(50), use_container_width=True)

st.markdown(
    """
    ### Páginas disponibles
    - **Dashboard de indicadores:** métricas clave, histogramas y análisis categórico.
    - **Mapa y segmentación espacial:** dispersión UTM y análisis por zonas o polígonos.
    - **Geotecnia y control de calidad:** uniformidad de carga, desviaciones de longitud y variabilidad de diámetro.
    - **Visualización 3D:** perspectiva espacial de los pozos con coloración por métricas relevantes.

    Ajusta los filtros en esta página para que las demás secciones utilicen el mismo subconjunto de datos.
    """
)
