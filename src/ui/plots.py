"""Componentes reutilizables para construir gráficos y tablas."""
from __future__ import annotations

from fractions import Fraction
from typing import Dict, Iterable, List, Sequence, Tuple

import pandas as pd
import plotly.express as px


def pulgadas_a_mixto(valor) -> str:
    """Convierte un valor numérico en pulgadas a formato mixto fraccionario."""

    if pd.isna(valor):
        return ""

    try:
        valor_float = float(valor)
    except (TypeError, ValueError):
        return ""

    entero = int(valor_float)
    fraccion = max(valor_float - entero, 0)

    if fraccion == 0:
        return f"{entero}" if entero != 0 else "0"

    frac = Fraction(fraccion).limit_denominator(16)
    if frac.numerator == 0:
        return f"{entero}" if entero != 0 else "0"

    if entero == 0:
        return f"{frac.numerator}/{frac.denominator}"

    return f"{entero} {frac.numerator}/{frac.denominator}"


def agregar_diametro_pulgadas(df: pd.DataFrame) -> pd.DataFrame:
    """Agrega columnas de diámetro en pulgadas y mixto."""

    if "diametro" not in df.columns:
        return df

    df_salida = df.copy()
    df_salida["diametro"] = pd.to_numeric(df_salida["diametro"], errors="coerce")
    df_salida["diametro_pulgadas"] = df_salida["diametro"] / 25.4
    df_salida["diametro_pulgadas_str"] = df_salida["diametro_pulgadas"].apply(pulgadas_a_mixto)
    return df_salida


def preparar_columnas_aux(df: pd.DataFrame) -> pd.DataFrame:
    """Genera columnas auxiliares para mejorar la lectura de los gráficos."""

    df_aux = agregar_diametro_pulgadas(df)
    for col in df_aux.select_dtypes(include=[float, int]).columns:
        df_aux[col] = df_aux[col].round(2)

    if "fecha_tronadura" in df_aux.columns and "fecha_tronadura_str" not in df_aux.columns:
        df_aux["fecha_tronadura_str"] = df_aux["fecha_tronadura"].dt.strftime("%d-%m-%Y")

    return df_aux


def obtener_hover(df: pd.DataFrame) -> Tuple[List[str], Dict[str, str]]:
    """Construye listas de campos y etiquetas a mostrar en el hover de Plotly."""

    campos: List[str] = []
    etiquetas: Dict[str, str] = {}

    def agregar_si_existe(columna: str, etiqueta: str) -> None:
        if columna in df.columns:
            campos.append(columna)
            etiquetas[columna] = etiqueta

    agregar_si_existe("numero", "Pozo")
    agregar_si_existe("nombre_banco", "Banco")
    agregar_si_existe("kilos_cargados_real", "Kg")
    agregar_si_existe("longitud_real", "L (m)")
    agregar_si_existe("factor_carga", "FC")
    agregar_si_existe("fecha_tronadura_str", "Fecha")
    agregar_si_existe("holes_polygon", "Malla")
    agregar_si_existe("diametro_pulgadas_str", "Ø (pulg)")

    return campos, etiquetas


def aplicar_estilo_figura(fig, scatter_xy: bool = False, is_3d: bool = False):
    """Aplica estilos comunes a las figuras de Plotly."""

    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")

    if scatter_xy:
        fig.update_xaxes(showgrid=False, zeroline=False)
        fig.update_yaxes(showgrid=False, zeroline=False, scaleanchor="x", scaleratio=1)

    if is_3d:
        fig.update_layout(
            scene=dict(
                xaxis=dict(showbackground=False, showgrid=False, zeroline=False),
                yaxis=dict(showbackground=False, showgrid=False, zeroline=False),
                zaxis=dict(showbackground=False, showgrid=False, zeroline=False),
            )
        )

    return fig


def scatter_base(
    df: pd.DataFrame,
    color: str | None = None,
    custom_data: Sequence[str] | None = None,
    title: str = "",
    labels: Dict[str, str] | None = None,
    color_scale: str | Sequence[str] | None = None,
):
    """Crea un scatter 2D en coordenadas UTM con formato uniforme."""

    fig = px.scatter(
        df,
        x="este",
        y="norte",
        color=color,
        color_continuous_scale=color_scale,
        custom_data=custom_data,
        title=title,
        labels=labels or {"este": "Este (X)", "norte": "Norte (Y)"},
    )

    return aplicar_estilo_figura(fig, scatter_xy=True)
