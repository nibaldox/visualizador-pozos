"""Funciones de apoyo para aplicar estilos visuales consistentes."""
from __future__ import annotations

import streamlit as st


_BASE_CSS = """
<style>
/* Ajustes generales de espaciado */
section.main > div {
    padding-top: 1rem;
}

/* Contenedores de métricas con fondo suave y bordes redondeados */
div[data-testid="stMetric"] {
    background: rgba(15, 23, 42, 0.05);
    border: 1px solid rgba(148, 163, 184, 0.25);
    border-radius: 0.75rem;
    padding: 1rem;
    box-shadow: 0 8px 20px rgba(15, 23, 42, 0.05);
}

/* Estilo del valor de las métricas */
[data-testid="stMetricValue"] {
    color: #0f172a;
    font-weight: 600;
}

/* Ajustes para gráficos Plotly */
div[data-testid="stPlotlyChart"] > div {
    border-radius: 0.75rem;
    background: rgba(15, 23, 42, 0.02);
    padding: 0.5rem 0.75rem 0.25rem;
}

/* Tablas con bordes redondeados y borde suave */
div[data-testid="stDataFrameContainer"] {
    border-radius: 0.75rem;
    border: 1px solid rgba(148, 163, 184, 0.25);
    overflow: hidden;
}

div[data-testid="stDataFrameContainer"] > div:nth-child(2) {
    background: rgba(15, 23, 42, 0.02);
}

/* Expanders más redondeados */
div.streamlit-expanderHeader {
    background: rgba(15, 23, 42, 0.05);
    border-radius: 0.75rem 0.75rem 0 0;
}

div.streamlit-expanderContent {
    border-radius: 0 0 0.75rem 0.75rem;
    border: 1px solid rgba(148, 163, 184, 0.25);
    border-top: none;
}

/* Tabs con borde inferior sutil */
button[data-baseweb="tab"] {
    font-weight: 500;
}

button[data-baseweb="tab"]:not(:disabled) {
    border-bottom: 3px solid transparent;
}

button[data-baseweb="tab"][aria-selected="true"] {
    border-color: #0ea5e9;
    color: #0f172a;
}
</style>
"""


def aplicar_estilos_base() -> None:
    """Inyecta CSS base para armonizar los componentes visuales."""

    st.markdown(_BASE_CSS, unsafe_allow_html=True)
