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
    columnas_excluir = [
        "x", "y", "z", "holes_dateupdated", "camion", "longitud_teo", "uniqid", "fecha_tronadura",
        "numero", "id_pozo", "este", "norte", "kilos_cargados_real", "nombre", "inclinacion_real", "azimuth_real", "diametro", "stemming_real", "water_level", "number_primes"
    ]
    columnas_filtrables = [col for col in df_procesado.columns if df_procesado[col].nunique() > 1 and col.lower() not in columnas_excluir]

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
        valores = df_procesado[col].dropna().unique()
        if len(valores) > 1:
            selected = st.sidebar.multiselect(f"{col}", sorted(valores), default=[])
            if selected:
                df_procesado = df_procesado[df_procesado[col].isin(selected)]

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
    # Redondear todos los campos numéricos a 2 decimales para visualización y hover
    df_vista = df_procesado.copy()
    for col in df_vista.select_dtypes(include=[float, int]).columns:
        df_vista[col] = df_vista[col].round(2)
    st.dataframe(df_vista.head())

    # =============================
    # Visualización en plano UTM (Plotly para hover personalizado)
    # =============================
    import plotly.express as px
    st.subheader("Pozos en Coordenadas UTM (Este vs Norte)")
    # Definir las columnas informativas para el hover
    # Preparar columna de diámetro en pulgadas para el hover
    from fractions import Fraction
    def pulgadas_a_mixto(valor):
        entero = int(valor)
        fraccion = valor - entero
        fraccion_str = ""
        if fraccion > 0:
            frac = Fraction(fraccion).limit_denominator(16)
            if frac.numerator != 0:
                fraccion_str = f" {frac.numerator}/{frac.denominator}"
        return f"{entero}{fraccion_str}" if fraccion_str else f"{entero}"

    if "diametro" in df_vista.columns:
        df_vista["diametro_pulgadas"] = df_vista["diametro"] / 25.4
        df_vista["diametro_pulgadas_str"] = df_vista["diametro_pulgadas"].apply(pulgadas_a_mixto)
    # Formatear fecha para hover
    if "fecha_tronadura" in df_vista.columns:
        df_vista["fecha_tronadura_str"] = df_vista["fecha_tronadura"].dt.strftime("%d-%m-%Y")
    # Función auxiliar para generar campos y etiquetas de hover
    def obtener_hover(df):
        campos = []
        etiquetas = {}
        if "numero" in df.columns:
            campos.append("numero"); etiquetas["numero"] = "Pozo"
        if "nombre_banco" in df.columns:
            campos.append("nombre_banco"); etiquetas["nombre_banco"] = "Banco"
        if "kilos_cargados_real" in df.columns:
            campos.append("kilos_cargados_real"); etiquetas["kilos_cargados_real"] = "Kg"
        if "longitud_real" in df.columns:
            campos.append("longitud_real"); etiquetas["longitud_real"] = "L(m)"
        if "factor_carga" in df.columns:
            campos.append("factor_carga"); etiquetas["factor_carga"] = "FC"
        if "fecha_tronadura" in df.columns and "fecha_tronadura_str" in df.columns:
            campos.append("fecha_tronadura_str"); etiquetas["fecha_tronadura_str"] = "Fecha"
        if "holes_polygon" in df.columns:
            campos.append("holes_polygon"); etiquetas["holes_polygon"] = "Malla"
        if "diametro_pulgadas_str" in df.columns:
            campos.append("diametro_pulgadas_str"); etiquetas["diametro_pulgadas_str"] = "Ø (pulg)"
        return campos, etiquetas

    # --- Preparar columnas auxiliares para todos los dataframes usados en gráficos interactivos ---
    def preparar_columnas_aux(df):
        df = df.copy()
        # Redondear todos los campos numéricos a 2 decimales
        for col in df.select_dtypes(include=[float, int]).columns:
            df[col] = df[col].round(2)
        if "fecha_tronadura" in df.columns and "fecha_tronadura_str" not in df.columns:
            df["fecha_tronadura_str"] = df["fecha_tronadura"].dt.strftime("%d-%m-%Y")
        if "diametro" in df.columns and "diametro_pulgadas_str" not in df.columns:
            df["diametro_pulgadas"] = df["diametro"] / 25.4
            from fractions import Fraction
            def pulgadas_a_mixto(valor):
                entero = int(valor)
                fraccion = valor - entero
                fraccion_str = ""
                if fraccion > 0:
                    frac = Fraction(fraccion).limit_denominator(16)
                    if frac.numerator != 0:
                        fraccion_str = f" {frac.numerator}/{frac.denominator}"
                return f"{entero}{fraccion_str}" if fraccion_str else f"{entero}"
            df["diametro_pulgadas_str"] = df["diametro_pulgadas"].apply(pulgadas_a_mixto)
        return df

    df_vista = preparar_columnas_aux(df_vista)
    campos_hover, etiquetas = obtener_hover(df_vista)
    custom_data = campos_hover
    hovertemplate = "<br>".join([
        f"{etiquetas[campo]}: <b>%{{customdata[{i}]}}</b>" for i, campo in enumerate(campos_hover)
    ]) + "<extra></extra>"

    color_col = None
    color_scale = None
    if "kilos_cargados_real" in df_vista.columns:
        color_col = "kilos_cargados_real"
        color_scale = "RdYlGn_r"  # Escala verde (bajo) a rojo (alto)
    fig = px.scatter(
        df_vista,
        x="este",
        y="norte",
        color=color_col,
        color_continuous_scale=color_scale if color_scale else None,
        custom_data=custom_data,
        title="Mapa de calor de pozos según kilos de explosivo",
        labels={"este": "Este (X)", "norte": "Norte (Y)", "kilos_cargados_real": "Kg Explosivo"}
    )
    fig.update_traces(hovertemplate=hovertemplate)
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
            df_factor = preparar_columnas_aux(df_factor)
            campos_hover_factor, etiquetas_factor = obtener_hover(df_factor)
            custom_data_factor = campos_hover_factor
            hovertemplate_factor = "<br>".join([
                f"{etiquetas_factor[campo]}: <b>%{{customdata[{i}]}}</b>" for i, campo in enumerate(campos_hover_factor)
            ]) + "<extra></extra>"

            fig_factor = px.scatter(
                df_factor,
                x="este",
                y="norte",
                color="factor_carga",
                color_continuous_scale="RdYlGn_r",
                custom_data=custom_data_factor,
                title="Mapa de calor de pozos según factor de carga (kg/m)",
                labels={"este": "Este (X)", "norte": "Norte (Y)", "factor_carga": "Factor de carga (kg/m)"}
            )
            fig_factor.update_traces(hovertemplate=hovertemplate_factor)
            st.plotly_chart(fig_factor, use_container_width=True)
            if df_factor["factor_carga"].nunique() <= 1:
                st.info("Todos los pozos tienen el mismo factor de carga. El color será uniforme.")
        else:
            st.info("No hay datos válidos de factor de carga para graficar.")

    # =============================
    # Agregar columna mes_tronadura calculada
    # =============================
    if "fecha_tronadura" in df_procesado.columns:
        try:
            df_procesado["mes_tronadura"] = df_procesado["fecha_tronadura"].dt.month_name(locale="es_ES")
        except:
            df_procesado["mes_tronadura"] = df_procesado["fecha_tronadura"].dt.month

    # =============================
    # PESTAÑAS DE VISUALIZACIÓN
    # =============================
    import plotly.graph_objects as go
    import plotly.express as px
    tab_dashboard, tab_mapa, tab_3d = st.tabs(["Dashboard", "Mapa de calor", "3D"])

    with tab_dashboard:
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

        # Boxplot de kilos de explosivo por cota
        if "kilos_cargados_real" in df_procesado.columns and "cota" in df_procesado.columns:
            st.markdown("**Boxplot de Kilos de Explosivo por Cota:**")
            fig_box = px.box(df_procesado, x="cota", y="kilos_cargados_real", points="all", title="Boxplot de Kilos de Explosivo por Cota", labels={"cota": "Cota (msnm)", "kilos_cargados_real": "Kg Explosivo"})
            st.plotly_chart(fig_box, use_container_width=True)
        else:
            st.info("No se puede mostrar el boxplot: faltan las columnas 'cota' y/o 'kilos_cargados_real' en los datos.")

        # Gráfico de pie: selección dinámica de columna categórica
        columnas_categoricas = [col for col in df_procesado.columns if df_procesado[col].nunique() > 1 and df_procesado[col].nunique() <= 20 and col not in ["este", "norte", "cota", "x", "y", "z", "factor_carga", "kilos_cargados_real", "longitud_real"] and not pd.api.types.is_numeric_dtype(df_procesado[col])]
        st.markdown("**Gráfico de Torta (Pie Chart):**")
        if columnas_categoricas:
            col_pie = st.selectbox("Selecciona la columna categórica para el pie chart", columnas_categoricas, key="piechart_dashboard")
            pie_counts = df_procesado[col_pie].value_counts().reset_index()
            pie_counts.columns = [col_pie, "Cantidad"]
            fig_pie = px.pie(pie_counts, names=col_pie, values="Cantidad", title=f"Distribución por {col_pie}", hole=0.3)
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No hay columnas categóricas adecuadas para graficar en torta (pie chart). Asegúrate de tener columnas tipo categoría con pocos valores únicos.")

    with tab_mapa:
        st.subheader("Mapa de calor y visualización geográfica")
        # Scatterplot por variable categórica seleccionable
        columnas_categoricas_scatter = [col for col in df_procesado.columns if df_procesado[col].nunique() > 1 and df_procesado[col].nunique() <= 20 and col not in ["este", "norte", "cota", "x", "y", "z", "factor_carga", "kilos_cargados_real", "longitud_real"] and not pd.api.types.is_numeric_dtype(df_procesado[col])]
        st.markdown("**Mapa de pozos por variable categórica:**")
        if columnas_categoricas_scatter:
            col_scatter = st.selectbox("Selecciona la variable para colorear el scatter", columnas_categoricas_scatter, key="scatter_categorica_mapa")
            fig_scatter_polygon = px.scatter(
                df_procesado,
                x="este",
                y="norte",
                color=col_scatter,
                hover_data=[col for col in ["numero", "id_pozo", "cota", "kilos_cargados_real", "factor_carga", col_scatter] if col in df_procesado.columns],
                title=f"Pozos coloreados por {col_scatter}",
                labels={"este": "Este (X)", "norte": "Norte (Y)", col_scatter: col_scatter},
                color_discrete_sequence=px.colors.qualitative.Set1
            )
            st.plotly_chart(fig_scatter_polygon, use_container_width=True)
        else:
            st.info("No hay columnas categóricas adecuadas para colorear el scatterplot.")

    with tab_3d:
        st.subheader("Visualización 3D de Pozos")
        columnas_3d = [col for col in ["este", "norte", "cota", "factor_carga", "kilos_cargados_real"] if col in df_procesado.columns]
        if all(col in df_procesado.columns for col in ["este", "norte", "cota"]):
            color_col = "factor_carga" if "factor_carga" in df_procesado.columns else ("kilos_cargados_real" if "kilos_cargados_real" in df_procesado.columns else None)
            fig_3d = px.scatter_3d(
                df_procesado,
                x="este",
                y="norte",
                z="cota",
                color=color_col,
                color_continuous_scale="RdYlGn_r",
                hover_data=columnas_3d,
                title="Pozos de Tronadura en 3D (Cota)",
                labels={"este": "Este (UTM)", "norte": "Norte (UTM)", "cota": "Cota (msnm)", "factor_carga": "Factor de carga (kg/m)", "kilos_cargados_real": "Kg explosivo"}
            )
            fig_3d.update_traces(marker=dict(size=5))
            st.plotly_chart(fig_3d, use_container_width=True)
        else:
            st.info("No se puede mostrar el gráfico 3D: faltan las columnas 'este', 'norte' y/o 'cota' en los datos.")

    # Gráfico 3D de pozos
    st.markdown("**Visualización 3D de Pozos:**")
    columnas_3d = [col for col in ["este", "norte", "cota", "factor_carga", "kilos_cargados_real"] if col in df_procesado.columns]
    if all(col in df_procesado.columns for col in ["este", "norte", "cota"]):
        color_col = "factor_carga" if "factor_carga" in df_procesado.columns else ("kilos_cargados_real" if "kilos_cargados_real" in df_procesado.columns else None)
        df_3d = preparar_columnas_aux(df_procesado)
        campos_hover_3d, etiquetas_3d = obtener_hover(df_3d)
        custom_data_3d = campos_hover_3d
        hovertemplate_3d = "<br>".join([
            f"{etiquetas_3d[campo]}: <b>%{{customdata[{i}]}}</b>" for i, campo in enumerate(campos_hover_3d)
        ]) + "<extra></extra>"
        fig_3d = px.scatter_3d(
            df_3d,
            x="este",
            y="norte",
            z="cota",
            color=color_col,
            color_continuous_scale="RdYlGn_r",
            custom_data=custom_data_3d,
            hover_data=columnas_3d,
            title="Pozos de Tronadura en 3D (Cota)",
            labels={"este": "Este (UTM)", "norte": "Norte (UTM)", "cota": "Cota (msnm)", "factor_carga": "Factor de carga (kg/m)", "kilos_cargados_real": "Kg explosivo"}
        )
        fig_3d.update_traces(hovertemplate=hovertemplate_3d, marker=dict(size=5))
        st.plotly_chart(fig_3d, use_container_width=True)
    else:
        st.info("No se puede mostrar el gráfico 3D: faltan las columnas 'este', 'norte' y/o 'cota' en los datos.")

else:
    st.warning("Por favor sube un archivo Excel válido para comenzar.")
    st.stop()
