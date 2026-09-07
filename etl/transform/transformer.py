"""
transformer.py — Transformación y normalización
Proyecto LIDIA · Grupo 04 · UTEC ITR Norte

Vocabulario de gravedad (4 categorías):
  fatal      → hay muertos
  grave      → heridos graves, sin muertos
  leve       → heridos leves, sin muertos ni graves
  solo_danos → sin víctimas personales
  NULL       → dato faltante (no es una categoría de gravedad)

Reglas por fuente:
  UNASEV (UY)  → FATAL→fatal | GRAVE→grave | LEVE→leve | SIN LESIONADOS→solo_danos
  RENAEST (BR) → qtde_obitos>0→fatal | qtde_feridos>0→leve | resto→solo_danos
                 LIMITACIÓN: BR no distingue grave/leve → grave siempre NULL
  DGT (ES)     → TOTAL_MU24H→fatal | TOTAL_HG24H→grave | TOTAL_HL24H→leve | resto→solo_danos
"""

import pandas as pd
import numpy as np
import logging
import os
from dotenv import load_dotenv

# Singleton: el Transformer pyproj es caro de instanciar — se crea una sola vez
_TRANSFORMER_UY = None

def _get_transformer_uy():
    global _TRANSFORMER_UY
    if _TRANSFORMER_UY is None:
        from pyproj import Transformer
        _TRANSFORMER_UY = Transformer.from_crs("epsg:32721", "epsg:4326", always_xy=True)
    return _TRANSFORMER_UY

load_dotenv('/app/config/.env')
LOG_PATH = os.getenv('LOG_PATH', '/app/logs')

logging.basicConfig(
    filename=LOG_PATH + '/etl.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# ── Mapa UF → Región (Brasil) ───────────────────────────────────────────────

UF_REGIAO = {
    'AC':'Norte','AM':'Norte','AP':'Norte','PA':'Norte',
    'RO':'Norte','RR':'Norte','TO':'Norte',
    'AL':'Nordeste','BA':'Nordeste','CE':'Nordeste','MA':'Nordeste',
    'PB':'Nordeste','PE':'Nordeste','PI':'Nordeste','RN':'Nordeste','SE':'Nordeste',
    'DF':'Centro-Oeste','GO':'Centro-Oeste','MS':'Centro-Oeste','MT':'Centro-Oeste',
    'ES':'Sudeste','MG':'Sudeste','RJ':'Sudeste','SP':'Sudeste',
    'PR':'Sul','RS':'Sul','SC':'Sul',
}

# ── Mapa Provincias España (COD_PROVINCIA → nombre) ─────────────────────────

PROVINCIAS = {
    '1':'Álava','2':'Albacete','3':'Alicante','4':'Almería','5':'Ávila',
    '6':'Badajoz','7':'Balears (Illes)','8':'Barcelona','9':'Burgos',
    '10':'Cáceres','11':'Cádiz','12':'Castellón','13':'Ciudad Real',
    '14':'Córdoba','15':'Coruña (A)','16':'Cuenca','17':'Girona',
    '18':'Granada','19':'Guadalajara','20':'Gipuzkoa','21':'Huelva',
    '22':'Huesca','23':'Jaén','24':'León','25':'Lleida','26':'Rioja (La)',
    '27':'Lugo','28':'Madrid','29':'Málaga','30':'Murcia','31':'Navarra',
    '32':'Ourense','33':'Asturias','34':'Palencia','35':'Palmas (Las)',
    '36':'Pontevedra','37':'Salamanca','38':'Santa Cruz de Tenerife',
    '39':'Cantabria','40':'Segovia','41':'Sevilla','42':'Soria',
    '43':'Tarragona','44':'Teruel','45':'Toledo','46':'Valencia',
    '47':'Valladolid','48':'Bizkaia','49':'Zamora','50':'Zaragoza',
    '51':'Ceuta','52':'Melilla',
}

# ── Utilidades ───────────────────────────────────────────────────────────────

def utm_a_wgs84_vectorizado(xs, ys):
    """
    Reproyecta arrays de coordenadas UTM zona 21S → WGS84 (EPSG 32721 → 4326).
    Usa el Transformer singleton — se crea una sola vez por proceso.
    Retorna (lats, lons) como arrays float (np.nan donde la coord es inválida).
    """
    transformer = _get_transformer_uy()
    xs = np.asarray(xs, dtype=float)
    ys = np.asarray(ys, dtype=float)
    lons, lats = transformer.transform(xs, ys)
    valido = (-90 <= lats) & (lats <= 90) & (-180 <= lons) & (lons <= 180)
    lats = np.where(valido, np.round(lats, 6), np.nan)
    lons = np.where(valido, np.round(lons, 6), np.nan)
    return lats, lons


def parsear_fecha_mixta(valor):
    """Intenta parsear fecha con múltiples formatos (UY mezcla M/D/YYYY y D/M/YYYY)."""
    for fmt in ['%m/%d/%Y', '%d/%m/%Y', '%Y-%m-%d']:
        try:
            return pd.to_datetime(valor, format=fmt)
        except Exception:
            pass
    return pd.NaT


def normalizar_vehiculo(valor):
    """Normaliza tipo de vehículo a categoría canónica."""
    if valor is None or pd.isna(valor):
        return 'Desconocido'
    v = str(valor).strip().upper()
    if any(x in v for x in ['MOTO', 'MOTOCI', 'CICLOMOTOR']):
        return 'Moto'
    if any(x in v for x in ['BICI', 'BICYCLE', 'CICLO']):
        return 'Bicicleta'
    if any(x in v for x in ['CAMION', 'CAMINHAO', 'TRUCK', 'FURG']):
        return 'Camión'
    if any(x in v for x in ['BUS', 'ONIBUS', 'AUTOBUS', 'COLECT']):
        return 'Bus'
    if any(x in v for x in ['AUTO', 'TURISMO', 'CARRO', 'CAR', 'SEDAN']):
        return 'Auto'
    if any(x in v for x in ['PEAT', 'PEDEST']):
        return 'Peatón'
    if 'NAO INFORMADO' in v or 'NO INFORMADO' in v or 'DESCONOCIDO' in v:
        return 'Desconocido'
    return str(valor).strip()[:50]


# ── Uruguay ──────────────────────────────────────────────────────────────────

# Mapeo directo UNASEV → vocabulario controlado
MAPA_GRAVEDAD_UY = {
    'FATAL':          'fatal',
    'GRAVE':          'grave',
    'LEVE':           'leve',
    'SIN LESIONADOS': 'solo_danos',
}


def transformar_uruguay(df_raw):
    """
    Uruguay — UNASEV.
    Coordenadas en UTM zona 21S → reproyectar a WGS84 con pyproj.
    Gravedad derivada del campo 'Gravedad' del CSV.
    """
    logging.info("[TRANSFORM] Iniciando Uruguay...")
    df = df_raw.copy()
    rechazados = []

    # Normalizar nombres de columnas (quita espacios y acentos del header)
    df.columns = df.columns.str.strip()

    df = df.rename(columns={
        'Fecha':             'fecha',
        'Hora':              'hora',
        'Departamento':      'region',
        'Localidad':         'municipio',
        'Tipo de Siniestro': 'tipo_accidente',
        'Gravedad':          'gravedad_raw',
        'X':                 'coord_x',
        'Y':                 'coord_y',
    })

    # Gravedad → vocabulario controlado (NULL si no mapea)
    df['gravedad'] = (
        df['gravedad_raw'].astype(str).str.strip().str.upper()
        .map(MAPA_GRAVEDAD_UY)
    )

    # Fecha (formato mixto M/D/YYYY en años tempranos)
    df['fecha'] = df['fecha'].apply(parsear_fecha_mixta)
    mask_sin_fecha = df['fecha'].isna()
    rechazados.append(df[mask_sin_fecha].assign(motivo_rechazo='Fecha inválida'))
    df = df[~mask_sin_fecha]

    # Coordenadas UTM zona 21S → WGS84 (vectorizado — 1 llamada sobre arrays)
    df['latitud']  = np.nan
    df['longitud'] = np.nan
    mask_coord = df['coord_x'].notna() & df['coord_y'].notna()
    if mask_coord.any():
        lats, lons = utm_a_wgs84_vectorizado(
            df.loc[mask_coord, 'coord_x'].values,
            df.loc[mask_coord, 'coord_y'].values,
        )
        df.loc[mask_coord, 'latitud']  = lats
        df.loc[mask_coord, 'longitud'] = lons

    mask_sin_coord = df['latitud'].isna()
    rechazados.append(df[mask_sin_coord].assign(motivo_rechazo='Coordenadas inválidas'))
    df = df[~mask_sin_coord]

    # Hora
    df['hora'] = pd.to_numeric(df['hora'], errors='coerce').apply(
        lambda x: f"{int(x):02d}:00" if pd.notna(x) and 0 <= x <= 23 else None
    )

    df['tipo_vehiculo'] = 'Desconocido'
    df['pais']          = 'Uruguay'

    # Columnas finales garantizadas (sin sexo / edad_min / edad_max)
    df = df[['fecha', 'hora', 'tipo_accidente', 'gravedad',
             'latitud', 'longitud', 'region', 'municipio',
             'tipo_vehiculo', 'pais']].copy()

    rech_df = pd.concat(rechazados, ignore_index=True) if rechazados else pd.DataFrame()
    logging.info(f"[TRANSFORM] Uruguay: {len(df)} válidos | {len(rech_df)} rechazados")
    print(f"✅ Uruguay transformado: {len(df):,} válidos | {len(rech_df):,} rechazados")
    return df, rech_df


# ── Brasil ───────────────────────────────────────────────────────────────────

def transformar_brasil(datos_raw):
    """
    Brasil — RENAEST (archivo único por accidente).
    Columnas clave: qtde_obitos, qtde_feridosilesos, latitude_acidente,
    longitude_acidente, tp_acidente, bairro_acidente, uf_acidente.
    Gravedad derivada de conteos numéricos (4b, 4d).
    """
    logging.info("[TRANSFORM] Iniciando Brasil...")
    rechazados = []

    # Acepta tanto dict {'combinado': df} como DataFrame directo
    if isinstance(datos_raw, dict):
        df = datos_raw['combinado'].copy()
    else:
        df = datos_raw.copy()

    # Fecha (4d)
    df['fecha'] = pd.to_datetime(df['data_acidente'], errors='coerce')
    mask_sin_fecha = df['fecha'].isna()
    rechazados.append(df[mask_sin_fecha].assign(motivo_rechazo='Fecha inválida'))
    df = df[~mask_sin_fecha]

    # Coordenadas (4d — latitude_acidente / longitude_acidente)
    df['latitud']  = pd.to_numeric(df['latitude_acidente'],  errors='coerce')
    df['longitud'] = pd.to_numeric(df['longitude_acidente'], errors='coerce')

    # Filtrar coords fuera del rango físico de Brasil
    mask_coord_invalida = (
        df['latitud'].notna() & (
            (df['latitud']  < -35) | (df['latitud']  > 5) |
            (df['longitud'] < -75) | (df['longitud'] > -30)
        )
    )
    rechazados.append(df[mask_coord_invalida].assign(motivo_rechazo='Coordenadas fuera de rango'))
    df.loc[mask_coord_invalida, ['latitud', 'longitud']] = None

    # Hora — hora_acidente viene en formato HHMMSS (ej: 210000 → "21:00")
    def _parsear_hora_br(x):
        if x is None or (isinstance(x, float) and pd.isna(x)):
            return None
        s = str(x).strip().replace('.0', '')
        if not s.isdigit():
            return None
        s = s.zfill(6)
        h, m = int(s[:2]), int(s[2:4])
        return f"{h:02d}:{m:02d}" if 0 <= h <= 23 and 0 <= m <= 59 else None

    df['hora'] = df['hora_acidente'].apply(_parsear_hora_br)

    # Tipo accidente (4d — tp_acidente)
    df['tipo_accidente'] = df['tp_acidente'].fillna('Sin datos')

    # Municipio (4d — bairro_acidente)
    df['municipio'] = df['bairro_acidente'].fillna('Sin datos') if 'bairro_acidente' in df.columns else 'Sin datos'

    # Región desde UF (4d — uf_acidente)
    if 'uf_acidente' in df.columns:
        df['region'] = df['uf_acidente'].map(UF_REGIAO).fillna(df['uf_acidente']).fillna('Sin datos')
    else:
        df['region'] = 'Sin datos'

    # Gravedad desde conteos numéricos
    # LIMITACIÓN BR: RENAEST no distingue grave/leve → grave siempre NULL para Brasil
    qtde_obitos  = pd.to_numeric(df.get('qtde_obitos',  0), errors='coerce').fillna(0)
    qtde_feridos = pd.to_numeric(df.get('qtde_feridosilesos', 0), errors='coerce').fillna(0)
    df['gravedad'] = 'solo_danos'
    df.loc[qtde_feridos > 0, 'gravedad'] = 'leve'
    df.loc[qtde_obitos  > 0, 'gravedad'] = 'fatal'

    # Tipo vehículo no disponible en archivo único RENAEST
    df['tipo_vehiculo'] = 'Desconocido'
    df['pais']          = 'Brasil'

    # Columnas finales (sin sexo / edad_min / edad_max)
    cols_out = ['fecha', 'hora', 'tipo_accidente', 'gravedad',
                'latitud', 'longitud', 'region', 'municipio',
                'tipo_vehiculo', 'pais']
    df = df[[c for c in cols_out if c in df.columns]].copy()

    rech_df = pd.concat(rechazados, ignore_index=True) if rechazados else pd.DataFrame()
    logging.info(f"[TRANSFORM] Brasil: {len(df)} válidos | {len(rech_df)} rechazados")
    print(f"✅ Brasil transformado: {len(df):,} válidos | {len(rech_df):,} rechazados")
    return df, rech_df


# ── España ───────────────────────────────────────────────────────────────────

def transformar_espana(df_raw):
    """
    España — DGT nacional (archivo CSV unificado 2018-2024).
    Fecha construida desde ANYO + MES (no hay columna fecha directa).
    Expansión: 1 fila por víctima según TOTAL_MU24H / HG24H / HL24H (4c, 4b).
    """
    logging.info("[TRANSFORM] Iniciando España...")
    df = df_raw.copy()
    rechazados = []

    # Convertir numéricos ANTES de construir fecha (4c)
    for col in ['ANYO', 'MES', 'HORA', 'TOTAL_MU24H', 'TOTAL_HG24H', 'TOTAL_HL24H',
                'TOTAL_VICTIMAS_24H', 'TOTAL_VEHICULOS', 'COD_PROVINCIA', 'COD_MUNICIPIO']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # Fecha desde ANYO + MES (4c — construir antes de filtrar)
    df['fecha'] = pd.to_datetime(
        df['ANYO'].astype(str) + '-' + df['MES'].astype(str).str.zfill(2) + '-01',
        errors='coerce'
    )
    mask_sin_fecha = df['fecha'].isna()
    rechazados.append(df[mask_sin_fecha].assign(motivo_rechazo='Fecha inválida'))
    df = df[~mask_sin_fecha]

    # Hora
    df['hora'] = df['HORA'].apply(
        lambda x: f"{int(x):02d}:00" if pd.notna(x) else None
    )

    # Región desde COD_PROVINCIA (52 provincias)
    df['region'] = df['COD_PROVINCIA'].apply(
        lambda x: PROVINCIAS.get(str(int(x)), f'Provincia {int(x)}') if pd.notna(x) else 'Sin datos'
    )
    df['municipio'] = df['COD_MUNICIPIO'].apply(
        lambda x: f"Municipio {int(x)}" if pd.notna(x) else 'Sin datos'
    )

    # Tipo accidente
    df['tipo_accidente'] = df['TIPO_ACCIDENTE'].fillna('Sin datos') if 'TIPO_ACCIDENTE' in df.columns else 'Sin datos'

    # 1 fila por accidente — gravedad según peor resultado registrado
    df['latitud']       = None
    df['longitud']      = None
    df['tipo_vehiculo'] = None

    mu = df['TOTAL_MU24H'].fillna(0).astype(int).clip(lower=0)
    hg = df['TOTAL_HG24H'].fillna(0).astype(int).clip(lower=0)
    hl = df['TOTAL_HL24H'].fillna(0).astype(int).clip(lower=0)

    df['gravedad'] = np.select(
        [mu > 0, hg > 0, hl > 0],
        ['fatal', 'grave', 'leve'],
        default='solo_danos'
    )

    COLS_OUT = ['fecha', 'hora', 'tipo_accidente', 'gravedad', 'region',
                'municipio', 'latitud', 'longitud', 'pais', 'tipo_vehiculo']
    df_out = df[COLS_OUT].copy().reset_index(drop=True)

    rech_df = pd.concat(rechazados, ignore_index=True) if rechazados else pd.DataFrame()
    logging.info(f"[TRANSFORM] España: {len(df_out)} válidos | {len(rech_df)} rechazados")
    print(f"✅ España transformado: {len(df_out):,} válidos | {len(rech_df):,} rechazados")
    return df_out, rech_df


# ── Orquestador ──────────────────────────────────────────────────────────────

def transformar_todos(datos_raw):
    print("\n🔄 Iniciando transformación...")
    uy, rech_uy = transformar_uruguay(datos_raw['uruguay'])
    br, rech_br = transformar_brasil(datos_raw['brasil'])
    es, rech_es = transformar_espana(datos_raw['espana'])

    rechazados_lista = [r for r in [rech_uy, rech_br, rech_es] if len(r) > 0]
    rechazados = (
        pd.concat(rechazados_lista, ignore_index=True)
        if rechazados_lista else pd.DataFrame()
    )
    rechazados['fecha_procesamiento'] = pd.Timestamp.now()

    print(f"\n📊 Resumen transformación:")
    print(f"   URUGUAY: {len(uy):,} válidos")
    print(f"   BRASIL:  {len(br):,} válidos")
    print(f"   ESPAÑA:  {len(es):,} válidos")
    print(f"   RECHAZADOS TOTAL: {len(rechazados):,}")

    return {
        'uruguay':    uy,
        'brasil':     br,
        'espana':     es,
        'rechazados': rechazados,
    }
