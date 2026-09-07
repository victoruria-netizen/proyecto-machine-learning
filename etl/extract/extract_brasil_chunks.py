"""
extract_brasil_chunks.py — Brasil usando solo Acidentes_DadosAbertos
Cada fila = 1 accidente con totales de víctimas agregados.
Se procesa en chunks de 200k para evitar OOM.
"""
import pandas as pd
import psycopg2
import gc
import os
import re
import logging
from dotenv import load_dotenv

load_dotenv('/app/config/.env')

DB_CONFIG = {
    'host':     os.getenv('PG_HOST'),
    'port':     int(os.getenv('PG_PORT', 5432)),
    'user':     os.getenv('PG_USER'),
    'password': os.getenv('PG_PASSWORD'),
    'dbname':   os.getenv('PG_DB'),
}
RAW_PATH = os.getenv('RAW_PATH', '/app/data/raw')
LOG_PATH  = os.getenv('LOG_PATH', '/app/logs')

logging.basicConfig(
    filename=LOG_PATH + '/etl.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def get_conn():
    return psycopg2.connect(**DB_CONFIG)

def normalizar_gravedad_br(obitos, feridos):
    """Deriva gravedad RENAEST — LIMITACIÓN: BR no distingue grave/leve → grave=NULL."""
    try:
        o = int(obitos) if pd.notna(obitos) else 0
        f = int(feridos) if pd.notna(feridos) else 0
    except Exception:
        o, f = 0, 0
    if o > 0:   return 'fatal'
    if f > 0:   return 'leve'
    return 'solo_danos'

def parsear_hora_br(x):
    if pd.isna(x): return None
    s = str(x).strip().replace('.0','')
    if not s.isdigit(): return None
    s = s.zfill(6)
    h, m = int(s[:2]), int(s[2:4])
    if 0 <= h <= 23 and 0 <= m <= 59:
        return f"{h:02d}:{m:02d}"
    return None

def normalizar_vehiculo_br(v):
    return 'Desconocido'

# Mapeo de UF → región
UF_REGIAO = {
    'AC':'Norte','AM':'Norte','AP':'Norte','PA':'Norte','RO':'Norte','RR':'Norte','TO':'Norte',
    'AL':'Nordeste','BA':'Nordeste','CE':'Nordeste','MA':'Nordeste','PB':'Nordeste',
    'PE':'Nordeste','PI':'Nordeste','RN':'Nordeste','SE':'Nordeste',
    'DF':'Centro-Oeste','GO':'Centro-Oeste','MS':'Centro-Oeste','MT':'Centro-Oeste',
    'ES':'Sudeste','MG':'Sudeste','RJ':'Sudeste','SP':'Sudeste',
    'PR':'Sul','RS':'Sul','SC':'Sul',
}

def cargar_brasil_chunks(chunk_size=200000):
    from load.loader_postgres import get_conn as pg_conn, cargar_pais, cargar_fuentes
    from load.loader_mongo import get_client, cargar_pais_mongo

    MONGO_DB = os.getenv('MONGO_DB')
    COLS = ['num_acidente','data_acidente','uf_acidente','tp_acidente',
            'fase_dia','cond_meteorologica','latitude_acidente','longitude_acidente',
            'hora_acidente','qtde_obitos','qtde_feridosilesos','qtde_envolvidos',
            'bairro_acidente','municipio' if False else 'bairro_acidente']

    COLS_USE = ['num_acidente','data_acidente','uf_acidente','tp_acidente',
                'latitude_acidente','longitude_acidente','hora_acidente',
                'qtde_obitos','qtde_feridosilesos','bairro_acidente']

    total_sql   = 0
    total_mongo = 0
    chunk_num   = 0

    client = get_client()
    db = client[MONGO_DB]

    print("   Procesando Acidentes en chunks...")

    # Nombre canónico del archivo RENAEST (archivo único por accidente)
    archivo_brasil = f'{RAW_PATH}/Acidentes_DadosAbertos_20260412_Brasil.csv'

    for chunk in pd.read_csv(
        archivo_brasil,
        sep=';', encoding='latin-1',
        low_memory=False,
        chunksize=chunk_size
    ):
        chunk_num += 1

        # Fecha
        chunk['fecha'] = pd.to_datetime(chunk['data_acidente'], errors='coerce')
        chunk = chunk[chunk['fecha'].notna()]
        if len(chunk) == 0:
            continue

        # Hora
        chunk['hora'] = chunk['hora_acidente'].apply(parsear_hora_br)

        # Coordenadas (4d — latitude_acidente / longitude_acidente)
        chunk['latitud']  = pd.to_numeric(chunk['latitude_acidente'],  errors='coerce')
        chunk['longitud'] = pd.to_numeric(chunk['longitude_acidente'], errors='coerce')

        # Filtrar coords inválidas de Brasil
        mask_inv = (
            chunk['latitud'].notna() & (
                (chunk['latitud']  < -35) | (chunk['latitud']  > 5)  |
                (chunk['longitud'] < -75) | (chunk['longitud'] > -30)
            )
        )
        chunk.loc[mask_inv, ['latitud', 'longitud']] = None

        # Gravedad — 3 categorías desde conteos numéricos
        chunk['gravedad'] = chunk.apply(
            lambda r: normalizar_gravedad_br(r['qtde_obitos'], r['qtde_feridosilesos']),
            axis=1
        )

        # Región y municipio (4d — bairro_acidente / uf_acidente)
        chunk['region']    = chunk['uf_acidente'].map(UF_REGIAO).fillna('Sin datos')
        chunk['municipio'] = chunk['bairro_acidente'].fillna('Sin datos') if 'bairro_acidente' in chunk.columns else 'Sin datos'

        # Campos fijos — sin sexo / edad_min / edad_max
        chunk['tipo_accidente'] = chunk['tp_acidente'].fillna('Sin datos')
        chunk['tipo_vehiculo']  = 'Desconocido'
        chunk['pais']           = 'Brasil'

        conn_sql = pg_conn()
        ins, err = cargar_pais(conn_sql, chunk, 2)
        conn_sql.close()

        ins_m, _ = cargar_pais_mongo(db, chunk, 'brasil', id_fuente=2)

        total_sql   += ins
        total_mongo += ins_m
        print(f"   Chunk {chunk_num}: {ins:,} SQL | total: {total_sql:,}")
        del chunk
        gc.collect()

    client.close()
    logging.info(f"[BRASIL] {total_sql} SQL | {total_mongo} MongoDB")
    print(f"✅ Brasil: {total_sql:,} SQL | {total_mongo:,} MongoDB")
    return total_sql, total_mongo

if __name__ == '__main__':
    cargar_brasil_chunks()
