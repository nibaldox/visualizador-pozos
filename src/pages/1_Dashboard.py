import pandas as pd
import plotly.express as px
import streamlit as st

from ui.data_context import obtener_datos_en_sesion
from ui.plots import aplicar_estilo_figura

st.title("Dashboard de indicadores")

st.markdown(
    """
    Esta página resume el comportamiento del conjunto filtrado con métricas rápidas,
    distribuciones de factor de carga y análisis categóricos.
    """
)

datos = obtener_datos_en_sesion()
df = datos.filtrados

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total de pozos", len(df))
with col2:
    if "factor_carga" in df.columns:
        promedio_fc = df["factor_carga"].dropna().mean()
        st.metric("Promedio factor de carga", f"{promedio_fc:.2f} kg/m")
with col3:
    if "factor_carga" in df.columns:
        min_fc = df["factor_carga"].dropna().min()
        max_fc = df["factor_carga"].dropna().max()
        st.metric("Rango factor de carga", f"{min_fc:.2f} - {max_fc:.2f} kg/m")

if "factor_carga" in df.columns:
    st.markdown("**Distribución del factor de carga (kg/m):**")
    fig_hist = px.histogram(
        df.dropna(subset=["factor_carga"]),
        x="factor_carga",
        nbins=20,
        title="Histograma de factor de carga",
        labels={"factor_carga": "Factor de carga (kg/m)"},
    )
    aplicar_estilo_figura(fig_hist)
    st.plotly_chart(fig_hist, use_container_width=True)
else:
    st.info("Carga columnas de kilos cargados y longitud real para calcular el factor de carga.")

if "kilos_cargados_real" in df.columns and "cota" in df.columns:
    st.markdown("**Kilos de explosivo por cota:**")
    fig_box = px.box(
        df,
        x="cota",
        y="kilos_cargados_real",
        points="all",
        title="Boxplot de kilos de explosivo por cota",
        labels={"cota": "Cota (msnm)", "kilos_cargados_real": "Kg explosivo"},
    )
    aplicar_estilo_figura(fig_box)
    st.plotly_chart(fig_box, use_container_width=True)
else:
    st.info("No se puede mostrar el boxplot: faltan las columnas 'cota' y/o 'kilos_cargados_real'.")

columnas_categoricas = [
    col
    for col in df.columns
    if df[col].nunique() > 1
    and df[col].nunique() <= 20
    and col not in [
        "este",
        "norte",
        "cota",
        "x",
        "y",
        "z",
        "factor_carga",
        "kilos_cargados_real",
        "longitud_real",
    ]
    and not pd.api.types.is_numeric_dtype(df[col])
]

if columnas_categoricas:
    st.markdown("**Distribución por variable categórica (pie chart):**")
    columna_seleccionada = st.selectbox(
        "Selecciona la columna", columnas_categoricas, key="piechart_dashboard"
    )
    pie_counts = df[columna_seleccionada].value_counts().reset_index()
    pie_counts.columns = [columna_seleccionada, "Cantidad"]
    fig_pie = px.pie(
        pie_counts,
        names=columna_seleccionada,
        values="Cantidad",
        title=f"Distribución por {columna_seleccionada}",
        hole=0.3,
    )
    aplicar_estilo_figura(fig_pie)
    st.plotly_chart(fig_pie, use_container_width=True)
else:
    st.info(
        "No hay columnas categóricas adecuadas (<=20 valores) para construir un gráfico de torta."
    )
