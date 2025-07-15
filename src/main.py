import streamlit as st
from data_loader import cargar_datos, procesar_datos, convertir_coordenadas
import pandas as pd
from typing import Optional

# =============================
# Configuración de la aplicación
# =============================
st.set_page_config(page_title="Visualizador de Pozos", layout="wide")

st.title("Visualizador de Pozos de Tronadura")

# =============================
# Sidebar para carga de datos
# =============================
with st.sidebar:
    st.header("Cargar datos")
    archivo: Optional[object] = st.file_uploader("Subir archivo Excel", type=["xlsx"])

if archivo is not None:
    try:
        # Cargar y procesar datos
        df = cargar_datos(archivo)
        df_procesado = procesar_datos(df)
        # df_procesado = convertir_coordenadas(df_procesado)  # Eliminada conversión a lat/lon
    except Exception as e:
        st.error(f"Error al cargar o procesar el archivo: {e}")
        st.stop()

    # Validar existencia de columnas UTM
    columnas_utm = ["este", "norte"]
    for col in columnas_utm:
        if col not in df_procesado.columns:
            st.error(f"La columna '{col}' no está presente en los datos procesados.")
            st.stop()

    # =============================
    # Filtros dinámicos y de fecha
    # =============================
    st.sidebar.subheader("Filtros de columnas")
    # Excluir solo columnas técnicas (coordenadas y fecha)
    columnas_filtrables = [col for col in df_procesado.columns if col not in ["este", "norte", "fecha_tronadura"]]

    # Filtro de fecha con calendario independiente
    if "fecha_tronadura" in df_procesado.columns:
        fechas_validas = df_procesado["fecha_tronadura"].dropna().dt.date
        if not fechas_validas.empty:
            min_fecha = fechas_validas.min()
            max_fecha = fechas_validas.max()
            rango_fecha = st.sidebar.date_input(
                "Filtrar por fecha de tronadura (selecciona una o un rango)",
                value=(min_fecha, max_fecha) if min_fecha != max_fecha else min_fecha,
                min_value=min_fecha,
                max_value=max_fecha
            )
            if isinstance(rango_fecha, tuple) and len(rango_fecha) == 2:
                df_procesado = df_procesado[(df_procesado["fecha_tronadura"].dt.date >= rango_fecha[0]) & (df_procesado["fecha_tronadura"].dt.date <= rango_fecha[1])]
            elif isinstance(rango_fecha, (str, pd.Timestamp)) or rango_fecha:
                df_procesado = df_procesado[df_procesado["fecha_tronadura"].dt.date == rango_fecha]

    # Filtros multiselección para todas las columnas (excepto coordenadas y fecha)
    for col in columnas_filtrables:
        if col == "fecha_tronadura":
            continue  # Ya filtrada arriba
        opciones = df_procesado[col].dropna().unique().tolist()
        if len(opciones) > 1:
            seleccion = st.sidebar.multiselect(f"{col}", opciones, default=[])
            if seleccion:
                df_procesado = df_procesado[df_procesado[col].isin(seleccion)]


    # =============================
    # Calcular factor de carga (kg/m)
    # =============================
    if "kilos_cargados_real" in df_procesado.columns and "longitud_real" in df_procesado.columns:
        df_procesado["factor_carga"] = df_procesado["kilos_cargados_real"] / df_procesado["longitud_real"]
    else:
        df_procesado["factor_carga"] = None

    st.markdown("""
    **Factor de carga (kg/m):**
    Se calcula como `kilos_cargados_real / longitud_real` para cada pozo.
    """)
    # =============================
    # Visualización de datos
    # =============================
    st.subheader("Datos de Pozos")
    st.dataframe(df_procesado.head())

    # =============================
    # Visualización en plano UTM (Plotly para hover personalizado)
    # =============================
    import plotly.express as px
    st.subheader("Pozos en Coordenadas UTM (Este vs Norte)")
    # Definir las columnas informativas para el hover
    hover_data = [col for col in ["numero", "id_pozo", "nombre_banco", "kilos_cargados_real", "longitud_real", "factor_carga", "fecha_tronadura", "diametro", "nombre"] if col in df_procesado.columns]
    color_col = None
    color_scale = None
    if "kilos_cargados_real" in df_procesado.columns:
        color_col = "kilos_cargados_real"
        color_scale = "RdYlGn_r"  # Escala verde (bajo) a rojo (alto)
    fig = px.scatter(
        df_procesado,
        x="este",
        y="norte",
        color=color_col,
        color_continuous_scale=color_scale if color_scale else None,
        hover_data=hover_data,
        title="Mapa de calor de pozos según kilos de explosivo",
        labels={"este": "Este (X)", "norte": "Norte (Y)", "kilos_cargados_real": "Kg Explosivo"}
    )
    st.plotly_chart(fig, use_container_width=True)

    # =============================
    # Gráfico de factor de carga
    # =============================
    if "factor_carga" in df_procesado.columns:
        st.subheader("Mapa de calor de factor de carga (kg/m)")
        # Forzar tipo float y eliminar nulos/infs
        df_factor = df_procesado.copy()
        df_factor["factor_carga"] = pd.to_numeric(df_factor["factor_carga"], errors="coerce")
        df_factor = df_factor[df_factor["factor_carga"].notnull() & df_factor["factor_carga"].apply(lambda x: x != float('inf') and x != float('-inf'))]
        if not df_factor.empty:
            fig_factor = px.scatter(
                df_factor,
                x="este",
                y="norte",
                color="factor_carga",
                color_continuous_scale="RdYlGn_r",
                hover_data=hover_data,
                title="Mapa de calor de pozos según factor de carga (kg/m)",
                labels={"este": "Este (X)", "norte": "Norte (Y)", "factor_carga": "Factor de carga (kg/m)"}
            )
            st.plotly_chart(fig_factor, use_container_width=True)
            if df_factor["factor_carga"].nunique() <= 1:
                st.info("Todos los pozos tienen el mismo factor de carga. El color será uniforme.")
        else:
            st.info("No hay datos válidos de factor de carga para graficar.")

    # =============================
    # DASHBOARD DE INDICADORES Y GRÁFICOS
    # =============================
    import plotly.graph_objects as go
    import plotly.express as px
    st.subheader("Dashboard de Indicadores y Gráficos")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total de Pozos", len(df_procesado))
    with col2:
        if "factor_carga" in df_procesado.columns:
            promedio_fc = df_procesado["factor_carga"].mean()
            st.metric("Promedio Factor de Carga", f"{promedio_fc:.2f} kg/m")
    with col3:
        if "factor_carga" in df_procesado.columns:
            min_fc = df_procesado["factor_carga"].min()
            max_fc = df_procesado["factor_carga"].max()
            st.metric("Rango Factor de Carga", f"{min_fc:.2f} - {max_fc:.2f} kg/m")

    # Histograma de factor de carga
    if "factor_carga" in df_procesado.columns:
        st.markdown("**Distribución del Factor de Carga (kg/m):**")
        fig_hist = px.histogram(df_procesado, x="factor_carga", nbins=20, title="Histograma de Factor de Carga", labels={"factor_carga": "Factor de Carga (kg/m)"})
        st.plotly_chart(fig_hist, use_container_width=True)

    # Boxplot de kilos de explosivo por banco
    if "kilos_cargados_real" in df_procesado.columns and "nombre_banco" in df_procesado.columns:
        st.markdown("**Boxplot de Kilos de Explosivo por Banco:**")
        fig_box = px.box(df_procesado, x="nombre_banco", y="kilos_cargados_real", points="all", title="Boxplot de Kilos de Explosivo por Banco", labels={"nombre_banco": "Banco", "kilos_cargados_real": "Kg Explosivo"})
        st.plotly_chart(fig_box, use_container_width=True)
    else:
        st.info("No se puede mostrar el boxplot: faltan las columnas 'nombre_banco' y/o 'kilos_cargados_real' en los datos.")

    # Gráfico de pie: distribución de pozos por estado
    if "Estado" in df_procesado.columns:
        st.markdown("**Distribución de Pozos por Estado:**")
        estado_counts = df_procesado["Estado"].value_counts().reset_index()
        estado_counts.columns = ["Estado", "Cantidad"]
        fig_pie = px.pie(estado_counts, names="Estado", values="Cantidad", title="Distribución de Pozos por Estado", hole=0.3)
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.info("No se puede mostrar el gráfico de torta: falta la columna 'Estado' en los datos.")

else:
    st.warning("Por favor sube un archivo Excel válido para comenzar.")
    st.stop()
