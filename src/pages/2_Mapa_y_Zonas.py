import streamlit as st

from ui.data_context import obtener_datos_en_sesion
from ui.plots import obtener_hover, preparar_columnas_aux, scatter_base
from ui.styles import aplicar_estilos_base

st.title("Mapa de calor y segmentación espacial")

aplicar_estilos_base()

st.markdown(
    """
    Visualiza la distribución espacial de los pozos utilizando coordenadas UTM y
    resalta variaciones por carga, zona o variables categóricas seleccionadas.
    """
)

datos = obtener_datos_en_sesion()
df = preparar_columnas_aux(datos.filtrados)

campos_hover, etiquetas = obtener_hover(df)
custom_data = campos_hover
hovertemplate = "<br>".join(
    [f"{etiquetas[campo]}: <b>%{{customdata[{i}]}}</b>" for i, campo in enumerate(campos_hover)]
) + "<extra></extra>"

st.divider()

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
    and not df[col].dtype.kind in "ifc"
]

tab_continuo, tab_categorico = st.tabs(["Color continuo", "Color por categorías"])

with tab_continuo:
    color_col = "kilos_cargados_real" if "kilos_cargados_real" in df.columns else None
    color_scale = "RdYlGn_r" if color_col else None

    fig_principal = scatter_base(
        df,
        color=color_col,
        custom_data=custom_data,
        title="Pozos según kilos de explosivo cargados",
        labels={"este": "Este (X)", "norte": "Norte (Y)", "kilos_cargados_real": "Kg explosivo"},
        color_scale=color_scale,
    )
    fig_principal.update_traces(hovertemplate=hovertemplate)
    st.plotly_chart(fig_principal, use_container_width=True)

with tab_categorico:
    if columnas_categoricas:
        columna_categoria = st.selectbox(
            "Selecciona la variable para colorear",
            columnas_categoricas,
            key="scatter_categorico",
        )
        fig_categoria = scatter_base(
            df,
            color=columna_categoria,
            custom_data=[
                campo for campo in ["numero", columna_categoria, "kilos_cargados_real"] if campo in df.columns
            ],
            title=f"Pozos coloreados por {columna_categoria}",
            labels={"este": "Este (X)", "norte": "Norte (Y)", columna_categoria: columna_categoria},
        )
        st.plotly_chart(fig_categoria, use_container_width=True)
    else:
        st.info("No hay columnas categóricas con pocos valores para el scatter.")

col_zona = None
for opcion in ["holes_polygon", "banco", "zona"]:
    if opcion in df.columns:
        col_zona = opcion
        break

if col_zona and "kilos_cargados_real" in df.columns:
    st.divider()
    st.markdown("### Carga total y específica por zona crítica")
    df_zona = df[[col_zona, "kilos_cargados_real", "longitud_real", "este", "norte"]].copy()
    resumen = df_zona.groupby(col_zona).agg(
        total_kg=("kilos_cargados_real", "sum"),
        total_long=("longitud_real", "sum"),
        n_pozos=("kilos_cargados_real", "count"),
    )
    resumen["kg_por_m"] = resumen["total_kg"] / resumen["total_long"].replace(0, float("nan"))
    resumen = resumen.round(2)

    col_tabla, col_fig = st.columns([1, 1.6])
    with col_tabla:
        st.caption("Resumen por zona")
        st.dataframe(resumen, use_container_width=True, height=320)

    with col_fig:
        fig_zona = scatter_base(
            df_zona,
            color=col_zona,
            custom_data=[col_zona, "kilos_cargados_real"],
            title=f"Distribución de carga por {col_zona}",
            labels={"este": "Este (X)", "norte": "Norte (Y)", "kilos_cargados_real": "Kg explosivo"},
        )
        fig_zona.update_traces(
            marker=dict(size=12, line=dict(width=0)),
            hovertemplate=(
                f"Zona: <b>%{{customdata[0]}}</b><br>Kg explosivo: <b>%{{customdata[1]}}</b><extra></extra>"
            ),
        )
        st.plotly_chart(fig_zona, use_container_width=True)
else:
    st.info("No se encontró una columna de zonas (holes_polygon, banco o zona) con datos de carga.")
