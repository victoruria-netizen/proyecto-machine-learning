"""
extractor.py — Extracción de datos
Proyecto LIDIA · Grupo 04 · UTEC ITR Norte

Archivos esperados en RAW_PATH:
  Uruguay: uru_siniestros_unificado.csv       (sep=',',  encoding='latin-1')
  Brasil:  Acidentes_DadosAbertos_20260412_Brasil.csv (sep=';', encoding='latin-1') — 2.5 GB
  España:  espana_unificado.csv               (sep=',',  encoding='latin-1')

Brasil pesa 2.5 GB — extraer_brasil() devuelve solo la ruta.
La lectura en chunks la hace extract_brasil_chunks.py directamente.
"""

import pandas as pd
import os
import logging
from dotenv import load_dotenv

load_dotenv('/app/config/.env')

RAW_PATH = os.getenv('RAW_PATH', '/app/data/raw')
LOG_PATH  = os.getenv('LOG_PATH', '/app/logs')

logging.basicConfig(
    filename=LOG_PATH + '/etl.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# ── Uruguay ──────────────────────────────────────────────────────────────────

def extraer_uruguay():
    """
    Lee uru_siniestros_unificado.csv.
    Encoding latin-1 (el CSV tiene caracteres especiales del español).
    La fecha viene en formato mixto M/D/YYYY — el transformer la parsea.
    ETL_MAX_ROWS limita filas para pruebas locales (0 = sin límite).
    """
    try:
        path = f'{RAW_PATH}/uru_siniestros_unificado.csv'
        max_rows = int(os.getenv('ETL_MAX_ROWS', 0)) or None
        df = pd.read_csv(path, encoding='latin-1', sep=',', low_memory=False, nrows=max_rows)
        df['pais'] = 'Uruguay'
        logging.info(f"[EXTRACT] Uruguay: {len(df)} registros, {df.shape[1]} columnas")
        print(f"✅ Uruguay: {len(df):,} registros | {df.shape[1]} columnas")
        return df
    except Exception as e:
        logging.error(f"[EXTRACT] Error Uruguay: {e}")
        print(f"❌ Error Uruguay: {e}")
        return pd.DataFrame()


# ── Brasil ───────────────────────────────────────────────────────────────────

def extraer_brasil():
    """
    Brasil — RENAEST (archivo único por accidente, sep=';', 2.5 GB).
    Esta función NO lee el archivo completo en memoria.
    Retorna un dict {'ruta': path} que main_por_pais.py le pasa a
    extract_brasil_chunks.py, que lo procesa en chunks de 200k filas.

    Para main.py (carga completa en memoria — solo con RAM >= 16 GB):
    se leen los primeros MAX_ROWS_BRASIL registros como muestra local.
    """
    path = f'{RAW_PATH}/Acidentes_DadosAbertos_20260412_Brasil.csv'

    if not os.path.exists(path):
        logging.error(f"[EXTRACT] Archivo Brasil no encontrado: {path}")
        print(f"❌ Archivo Brasil no encontrado: {path}")
        return {}

    # Retornar solo la ruta — la lectura en chunks la gestiona extract_brasil_chunks.py
    logging.info(f"[EXTRACT] Brasil: ruta registrada para carga por chunks → {path}")
    print(f"✅ Brasil: archivo localizado ({path})")
    print(f"   ⚠️  Archivo de 2.5 GB — usar main_por_pais.py para carga por chunks.")

    # ETL_MAX_ROWS tiene prioridad; si no está, usa ETL_BRASIL_MAX_ROWS
    max_rows = int(os.getenv('ETL_MAX_ROWS', 0)) or int(os.getenv('ETL_BRASIL_MAX_ROWS', 500_000))
    print(f"   Leyendo muestra de {max_rows:,} filas para main.py...")
    try:
        df = pd.read_csv(
            path,
            sep=';', encoding='latin-1', low_memory=False,
            nrows=max_rows
        )
        logging.info(f"[EXTRACT] Brasil muestra: {len(df):,} registros")
        print(f"✅ Brasil (muestra): {len(df):,} registros | {df.shape[1]} columnas")
        return {'combinado': df}
    except Exception as e:
        logging.error(f"[EXTRACT] Error Brasil: {e}")
        print(f"❌ Error Brasil: {e}")
        return {}


# ── España ───────────────────────────────────────────────────────────────────

def extraer_espana():
    """
    Lee espana_unificado.csv — DGT nacional 2018-2024, ya unificado.
    NO tiene columna 'fecha' directa: el transformer construye la fecha
    desde las columnas ANYO + MES.
    sep=',', encoding='latin-1' (caracteres especiales del español).
    ETL_MAX_ROWS limita filas para pruebas locales (0 = sin límite).
    """
    try:
        path = f'{RAW_PATH}/espana_unificado.csv'
        max_rows = int(os.getenv('ETL_MAX_ROWS', 0)) or None
        df = pd.read_csv(path, encoding='latin-1', sep=',', low_memory=False, nrows=max_rows)
        df['pais'] = 'España'
        logging.info(f"[EXTRACT] España: {len(df)} registros, {df.shape[1]} columnas")
        print(f"✅ España: {len(df):,} registros | {df.shape[1]} columnas")
        return df
    except Exception as e:
        logging.error(f"[EXTRACT] Error España: {e}")
        print(f"❌ Error España: {e}")
        return pd.DataFrame()


# ── Orquestador ──────────────────────────────────────────────────────────────

def extraer_todos():
    print("\n📦 Iniciando extracción...")
    datos = {
        'uruguay': extraer_uruguay(),
        'brasil':  extraer_brasil(),
        'espana':  extraer_espana(),
    }
    print("\n📊 Resumen extracción:")
    uy = datos['uruguay']
    br = datos['brasil']
    es = datos['espana']
    print(f"   URUGUAY: {len(uy):,} registros")
    print(f"   BRASIL:  {len(br.get('combinado', [])):,} registros (muestra)")
    print(f"   ESPAÑA:  {len(es):,} registros")
    return datos
