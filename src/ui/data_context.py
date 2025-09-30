"""Utilidades para compartir datos y filtros entre páginas de Streamlit."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from typing import Optional, Sequence

import numpy as np
import pandas as pd
import streamlit as st

from data_loader import cargar_datos, procesar_datos

# Columnas que no deben exponerse en los filtros dinámicos
_COLUMNAS_EXCLUIR: Sequence[str] = (
    "x",
    "y",
    "z",
    "holes_dateupdated",
    "camion",
    "longitud_teo",
    "uniqid",
    "fecha_tronadura",
    "numero",
    "id_pozo",
    "este",
    "norte",
    "kilos_cargados_real",
    "nombre",
    "inclinacion_real",
    "azimuth_real",
    "diametro",
    "stemming_real",
    "water_level",
    "number_primes",
)


@dataclass
class DatosPozos:
    """Contenedor de datos compartidos entre páginas."""

    procesados: pd.DataFrame
    filtrados: pd.DataFrame


def _aplicar_filtros_basicos(df: pd.DataFrame) -> pd.DataFrame:
    """Aplica filtros de fecha y columnas categóricas utilizando la barra lateral."""

    df_filtrado = df.copy()

    if "fecha_tronadura" in df_filtrado.columns:
        fechas_validas = df_filtrado["fecha_tronadura"].dropna().dt.date
        if not fechas_validas.empty:
            min_fecha = fechas_validas.min()
            max_fecha = fechas_validas.max()
            if min_fecha != max_fecha:
                limite_inferior = max(min_fecha, max_fecha - timedelta(days=30))
                rango_defecto = (limite_inferior, max_fecha)
            else:
                rango_defecto = min_fecha

            rango_fecha = st.sidebar.date_input(
                "Filtrar por fecha de tronadura (selecciona una o un rango)",
                value=rango_defecto,
                min_value=min_fecha,
                max_value=max_fecha,
            )

            if isinstance(rango_fecha, tuple) and len(rango_fecha) == 2:
                df_filtrado = df_filtrado[
                    (df_filtrado["fecha_tronadura"].dt.date >= rango_fecha[0])
                    & (df_filtrado["fecha_tronadura"].dt.date <= rango_fecha[1])
                ]
            elif rango_fecha:
                df_filtrado = df_filtrado[
                    df_filtrado["fecha_tronadura"].dt.date == rango_fecha
                ]

            st.sidebar.caption(
                "Se muestran por defecto los últimos 30 días de datos disponibles."
            )

    columnas_filtrables = [
        col
        for col in df_filtrado.columns
        if df_filtrado[col].nunique() > 1 and col.lower() not in _COLUMNAS_EXCLUIR
    ]

    for col in columnas_filtrables:
        valores = df_filtrado[col].dropna().unique()
        if len(valores) > 1:
            seleccion = st.sidebar.multiselect(
                f"{col}", sorted(valores), default=[], key=f"filtro_{col}"
            )
            if seleccion:
                df_filtrado = df_filtrado[df_filtrado[col].isin(seleccion)]

    return df_filtrado


def cargar_y_filtrar_datos() -> Optional[DatosPozos]:
    """Carga los datos desde un archivo subido y aplica filtros estándar."""

    with st.sidebar:
        st.header("Cargar datos")
        archivo = st.file_uploader("Subir archivo Excel", type=["xlsx"], key="archivo_excel")

    if archivo is None and "datos_pozos" not in st.session_state:
        return None

    if archivo is not None:
        try:
            df_original = cargar_datos(archivo)
            df_procesado = procesar_datos(df_original)
        except Exception as exc:  # pragma: no cover - mostrado al usuario
            st.error(f"Error al cargar o procesar el archivo: {exc}")
            st.stop()

        st.session_state["datos_pozos"] = df_procesado
    else:
        df_procesado = st.session_state["datos_pozos"]

    for columna in ("este", "norte"):
        if columna not in df_procesado.columns:
            st.error(f"La columna '{columna}' no está presente en los datos procesados.")
            st.stop()

    st.sidebar.subheader("Filtros de columnas")
    df_filtrado = _aplicar_filtros_basicos(df_procesado)

    # Calcular factor de carga de forma robusta
    if "kilos_cargados_real" in df_filtrado.columns and "longitud_real" in df_filtrado.columns:
        factor = df_filtrado["kilos_cargados_real"] / df_filtrado["longitud_real"].replace(0, np.nan)
        df_filtrado = df_filtrado.assign(
            factor_carga=pd.to_numeric(factor, errors="coerce")
        )
    elif "factor_carga" in df_filtrado.columns:
        df_filtrado = df_filtrado.assign(
            factor_carga=pd.to_numeric(df_filtrado["factor_carga"], errors="coerce")
        )

    datos = DatosPozos(procesados=df_procesado, filtrados=df_filtrado)
    st.session_state["datos_filtrados"] = datos
    return datos


def obtener_datos_en_sesion() -> DatosPozos:
    """Recupera los datos filtrados desde el estado de sesión o muestra un aviso."""

    datos: Optional[DatosPozos] = st.session_state.get("datos_filtrados")
    if datos is None:
        st.warning("Carga un archivo en la página de inicio para habilitar las visualizaciones.")
        st.stop()
    return datos


def formatear_tabla(df: pd.DataFrame) -> pd.DataFrame:
    """Redondea las columnas numéricas a dos decimales para visualización."""

    df_vista = df.copy()
    for columna in df_vista.select_dtypes(include=["float", "int", "float64", "int64"]).columns:
        df_vista[columna] = df_vista[columna].round(2)
    return df_vista
