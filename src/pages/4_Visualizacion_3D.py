import plotly.express as px
import streamlit as st

from ui.data_context import obtener_datos_en_sesion
from ui.plots import aplicar_estilo_figura, preparar_columnas_aux

st.title("Visualización 3D de pozos")

st.markdown(
    """
    Explora la distribución espacial completa de los pozos utilizando la cota como eje Z.
    Puedes colorear el gráfico por factor de carga o kilos de explosivo para identificar
    sectores críticos desde otra perspectiva.
    """
)

datos = obtener_datos_en_sesion()
df = datos.filtrados

if not {"este", "norte", "cota"}.issubset(df.columns):
    st.warning("Se requieren las columnas 'este', 'norte' y 'cota' para generar la nube de puntos 3D.")
    st.stop()

df_3d = preparar_columnas_aux(df)
color_col = None
if "factor_carga" in df_3d.columns:
    color_col = "factor_carga"
elif "kilos_cargados_real" in df_3d.columns:
    color_col = "kilos_cargados_real"

fig_3d = px.scatter_3d(
    df_3d,
    x="este",
    y="norte",
    z="cota",
    color=color_col,
    color_continuous_scale="RdYlGn_r" if color_col else None,
    hover_data=[col for col in ["numero", "factor_carga", "kilos_cargados_real", "cota"] if col in df_3d.columns],
    title="Pozos de tronadura en 3D",
    labels={
        "este": "Este (UTM)",
        "norte": "Norte (UTM)",
        "cota": "Cota (msnm)",
        "factor_carga": "Factor de carga (kg/m)",
        "kilos_cargados_real": "Kg explosivo",
    },
)
fig_3d.update_traces(marker=dict(size=5))
aplicar_estilo_figura(fig_3d, is_3d=True)
st.plotly_chart(fig_3d, use_container_width=True)
