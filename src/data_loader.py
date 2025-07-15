import pandas as pd
import utm
from typing import Any, Dict, List

# =============================
# Diccionario de columnas esperadas y descripción
# =============================
COLUMN_DESCRIPTIONS: Dict[str, str] = {
    "uniqid": "ID único",
    "id_rajo": "ID del rajo",
    "id_malla_opit": "ID de la malla de tronadura en opit",
    "nombre_malla_original": "ID de las mallas involucradas en la tronadura incluyendo la fecha",
    "nombre_rajo": "Nombre del rajo",
    "blast": "Mallas involucradas en la tronadura",
    "nombre_banco": "Nombre/cota del banco (puede usarse como Z si no hay otra)",
    "nombre_fase": "Nombre de la fase",
    "id_pozo": "ID del pozo perforado en opit",
    "numero": "ID del pozo real",
    "label_pozo": "ID combinado de pozo y malla",
    "label2_pozo": "",
    "latitud_geo": "Coordenada X (Este)",
    "longitud_geo": "Coordenada Y (Norte)",
    "kilos_cargados_real": "Kg de explosivo cargados en el pozo",
    "nombre": "Nombre del explosivo",
    "fecha_tronadura": "Fecha de la tronadura",
    "inclinacion_real": "Inclinación real",
    "azimuth_real": "Azimuth real",
    "diametro": "Diámetro del pozo en mm",
    "diametro_pulgada": "Diámetro del pozo en pulgadas",
    "longitud_real": "Longitud/profundidad real del pozo",
    "stemming_real": "Taco real del pozo",
    "longitud_teo": "Longitud/profundidad teórica del pozo",
    "water_level": "¿Hay agua en el pozo?",
    "number_primes": "Cantidad de primas instaladas",
    "camion": "ID del camión que cargó explosivo",
    "holes_dateupdated": "Fecha de actualización",
    "holes_polygon": "ID de la malla cargada",
    "mes_tronadura": "Mes de la tronadura"
}

# =============================
# Funciones utilitarias de normalización
# =============================
def normalize_column_name(name: str) -> str:
    """Normaliza el nombre de columna: minúsculas, sin espacios, sin guiones bajos duplicados."""
    return name.strip().lower().replace(" ", "_").replace("-", "_")

# =============================
def cargar_datos(ruta_archivo: Any) -> pd.DataFrame:
    """
    Carga datos de pozos desde un archivo Excel, normaliza nombres de columnas y mapea a nombres estándar.
    Args:
        ruta_archivo: Ruta o buffer del archivo Excel.
    Returns:
        DataFrame con nombres de columnas normalizados y mapeados.
    """
    import warnings
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message="Workbook contains no default style, apply openpyxl's default")
        df = pd.read_excel(ruta_archivo)
    # Normalizar nombres de columnas
    # Forzar nombres de columnas a minúsculas antes de cualquier mapeo
    df.columns = [col.lower() for col in df.columns]
    df.columns = [normalize_column_name(col) for col in df.columns]

    # Mapeo robusto de nombres de columnas a estándar interno
    column_mapping = {
        'nombre_banco': 'cota',
        'latitud_geo': 'este',
        'longitud_geo': 'norte',
        'longitud_real': 'longitud_real',
        'kilos_cargados_real': 'kilos_cargados_real',
        'nombre_real_profundidad': 'profundidad',
        # Agregar aquí otros mapeos si es necesario
    }
    # Normalización adicional para variantes de nombres
    for col in df.columns:
        if col.lower() == 'kilos_cargados_real':
            df = df.rename(columns={col: 'kilos_cargados_real'})
        if col.lower() == 'longitud_real':
            df = df.rename(columns={col: 'longitud_real'})
        if col.lower() == 'longitud_teo':
            # Si no existe longitud_real, usar longitud_teo como longitud_real
            if 'longitud_real' not in df.columns:
                df = df.rename(columns={col: 'longitud_real'})
    df = df.rename(columns=column_mapping)
    return df

# =============================
def procesar_datos(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpia y procesa los datos de pozos.
    - Garantiza la existencia de columnas x, y, z (coordenadas y profundidad).
    - Elimina filas con valores nulos en columnas críticas.
    Args:
        df: DataFrame de entrada.
    Returns:
        DataFrame procesado.
    """
    # Asignar x, y, z según disponibilidad
    if 'x' not in df.columns and 'este' in df.columns:
        df['x'] = df['este']
    if 'y' not in df.columns and 'norte' in df.columns:
        df['y'] = df['norte']
    if 'z' not in df.columns and 'cota' in df.columns:
        df['z'] = df['cota']
    if 'z' not in df.columns and 'profundidad' in df.columns:
        df['z'] = df['profundidad']

    # Validar columnas requeridas
    required_columns: List[str] = ['x', 'y', 'z']
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"Columna requerida '{col}' no encontrada en los datos.")
    # Eliminar filas con valores nulos en columnas críticas
    df = df.dropna(subset=required_columns)

    # Convertir fecha si existe
    if 'fecha_tronadura' in df.columns:
        df['fecha_tronadura'] = pd.to_datetime(df['fecha_tronadura'], errors='coerce')

    return df

# =============================
def convertir_coordenadas(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convierte coordenadas UTM a latitud y longitud y las agrega al DataFrame.
    Args:
        df: DataFrame con columnas 'x' y 'y'.
    Returns:
        DataFrame con columnas 'latitud' y 'longitud' añadidas.
    """
    if 'x' not in df.columns or 'y' not in df.columns:
        raise ValueError("DataFrame debe tener columnas 'x' y 'y' para la conversión UTM")

    latitudes: List[float] = []
    longitudes: List[float] = []
    for _, row in df.iterrows():
        # Asumimos zona UTM fija (18S) si no se especifica
        zona = 18
        letra_zona = 'S'
        if 'zona' in df.columns and 'letra_zona' in df.columns:
            zona = int(row['zona'])
            letra_zona = str(row['letra_zona'])
        lat, lon = utm.to_latlon(row['x'], row['y'], zona, letra_zona)
        latitudes.append(lat)
        longitudes.append(lon)
    df['latitud'] = latitudes
    df['longitud'] = longitudes
    return df

# =============================
# NOTA: Si se agregan funciones nuevas, documentarlas aquí y mantener el código limpio y ordenado.
