import numpy as np
import streamlit as st

from ui.data_context import obtener_datos_en_sesion
from ui.plots import obtener_hover, preparar_columnas_aux, scatter_base
from ui.styles import aplicar_estilos_base

st.title("Geotecnia y control de calidad")

aplicar_estilos_base()

st.markdown(
    """
    Evalúa la uniformidad del factor de carga, compara longitudes reales versus teóricas y
    revisa la variabilidad de diámetros para tomar decisiones geotécnicas.
    """
)

datos = obtener_datos_en_sesion()
df = datos.filtrados.copy()

if "factor_carga" in df.columns:
    st.subheader("Uniformidad del factor de carga (kg/m)")
    df_factor = df[df["factor_carga"].notnull()].copy()

    if not df_factor.empty:
        col_stats, col_chart = st.columns([1, 2])
        with col_stats:
            st.markdown("**Estadísticos del factor de carga:**")
            st.write(
                df_factor["factor_carga"].describe()[["mean", "std", "min", "max"]]
                .rename({"mean": "Media", "std": "Desv. Est.", "min": "Mínimo", "max": "Máximo"})
                .round(2)
            )
            st.caption(
                "Un bajo desvío estándar indica buena uniformidad de carga, reduciendo riesgos en el talud."
            )

        with col_chart:
            df_factor_aux = preparar_columnas_aux(df_factor)
            campos_hover, etiquetas = obtener_hover(df_factor_aux)
            hovertemplate = "<br>".join(
                [
                    f"{etiquetas[campo]}: <b>%{{customdata[{i}]}}</b>"
                    for i, campo in enumerate(campos_hover)
                ]
            ) + "<extra></extra>"

            fig_factor = scatter_base(
                df_factor_aux,
                color="factor_carga",
                custom_data=campos_hover,
                title="Mapa de calor del factor de carga",
                labels={
                    "este": "Este (X)",
                    "norte": "Norte (Y)",
                    "factor_carga": "Factor de carga (kg/m)",
                },
                color_scale="RdYlGn_r",
            )
            fig_factor.update_traces(hovertemplate=hovertemplate)
            st.plotly_chart(fig_factor, use_container_width=True)

        if df_factor["factor_carga"].nunique() <= 1:
            st.info("Todos los pozos tienen el mismo factor de carga. El color será uniforme.")
    else:
        st.info("No hay datos válidos de factor de carga para graficar.")
else:
    st.info("Agrega kilos cargados y longitud real para evaluar el factor de carga.")

st.divider()

if {"longitud_real", "longitud_teo"}.issubset(df.columns):
    st.subheader("Control de longitud real vs teórica")
    df_long = df[["numero", "longitud_real", "longitud_teo", "este", "norte"]].dropna()

    if not df_long.empty:
        df_long = df_long.copy()
        df_long["desviacion_%"] = 100 * (df_long["longitud_real"] - df_long["longitud_teo"]) / df_long["longitud_teo"].replace(0, np.nan)

        col_stats, col_chart = st.columns([1, 2])

        with col_stats:
            st.markdown("**Estadísticos de longitud real:**")
            st.write(
                df_long["longitud_real"].describe()[["mean", "std", "min", "max"]]
                .rename({"mean": "Media", "std": "Desv. Est.", "min": "Mínimo", "max": "Máximo"})
                .round(2)
            )

            df_long["clasificacion"] = "Dentro de tolerancia"
            df_long.loc[df_long["desviacion_%"] < -5, "clasificacion"] = "Sub-perforado (<-5%)"
            df_long.loc[df_long["desviacion_%"] > 5, "clasificacion"] = "Sobre-perforado (>+5%)"

            total_pozos = len(df_long)
            n_sub = (df_long["clasificacion"] == "Sub-perforado (<-5%)").sum()
            n_sobre = (df_long["clasificacion"] == "Sobre-perforado (>+5%)").sum()
            st.markdown(f"- **% Sub-perforados:** {100 * n_sub / total_pozos:.1f}%")
            st.markdown(f"- **% Sobre-perforados:** {100 * n_sobre / total_pozos:.1f}%")

        with col_chart:
            fig_long = scatter_base(
                df_long,
                color="clasificacion",
                custom_data=[
                    "numero",
                    "longitud_real",
                    "longitud_teo",
                    "desviacion_%",
                    "clasificacion",
                ],
                title="Distribución espacial por desviación de longitud",
                labels={"este": "Este (X)", "norte": "Norte (Y)", "clasificacion": "Clasificación"},
            )
            fig_long.update_traces(
                hovertemplate=(
                    "Pozo: <b>%{customdata[0]}</b><br>"
                    "Long. real: <b>%{customdata[1]} m</b><br>"
                    "Long. teórica: <b>%{customdata[2]} m</b><br>"
                    "Desviación: <b>%{customdata[3]:.2f}%</b><br>"
                    "Estado: <b>%{customdata[4]}</b><extra></extra>"
                )
            )
            st.plotly_chart(fig_long, use_container_width=True)
    else:
        st.info("No hay pares de longitud real y teórica para analizar.")
else:
    st.info("Agrega columnas de longitud real y teórica para este análisis.")

st.divider()

if "diametro" in df.columns:
    st.subheader("Variabilidad de diámetro de pozos")
    df_var = df[["numero", "este", "norte", "diametro"]].dropna()

    if not df_var.empty:
        col_stats, col_chart = st.columns([1, 2])

        with col_stats:
            st.markdown("**Estadísticos de diámetro:**")
            st.write(
                df_var["diametro"].describe()[["mean", "std", "min", "max"]]
                .rename({"mean": "Media", "std": "Desv. Est.", "min": "Mínimo", "max": "Máximo"})
                .round(2)
            )

            tolerancia_diam = st.number_input(
                "Tolerancia (±mm) para marcar pozos fuera de rango",
                min_value=0.0,
                max_value=20.0,
                value=3.0,
                step=0.5,
            )
            nominal = (
                df_var["diametro"].mode().iloc[0]
                if not df_var["diametro"].mode().empty
                else df_var["diametro"].mean()
            )
            df_var = preparar_columnas_aux(df_var)
            df_var["diametro_fuera_tol"] = (
                df_var["diametro"].sub(nominal).abs() > tolerancia_diam
            )
            pct_fuera = 100 * df_var["diametro_fuera_tol"].sum() / len(df_var)
            st.markdown(
                f"- **% pozos fuera de tolerancia (±{tolerancia_diam:.1f} mm):** {pct_fuera:.1f}%"
            )

        with col_chart:
            fig_diam = scatter_base(
                df_var,
                color="diametro",
                custom_data=["numero", "diametro"],
                title="Mapa de variabilidad de diámetro",
                labels={"este": "Este (X)", "norte": "Norte (Y)", "diametro": "Diámetro (mm)"},
                color_scale="Blues",
            )
            fig_diam.update_traces(
                hovertemplate="Pozo: <b>%{customdata[0]}</b><br>Diámetro: <b>%{customdata[1]} mm</b><extra></extra>"
            )
            st.plotly_chart(fig_diam, use_container_width=True)
    else:
        st.info("No hay datos válidos de diámetro para analizar.")
else:
    st.info("Incluye la columna de diámetro para revisar este indicador.")
