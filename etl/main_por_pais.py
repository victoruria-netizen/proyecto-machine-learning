"""
main_por_pais.py — Pipeline completo país por país
Brasil usa staging en PostgreSQL para evitar OOM con archivos grandes.
"""
import gc
import os
import time
import datetime
import pandas as pd
from dotenv import load_dotenv
load_dotenv('/app/config/.env')

def _ts():
    return datetime.datetime.now().strftime('%H:%M:%S')

def _lap(label, t0):
    elapsed = time.perf_counter() - t0
    print(f"   ⏱  {label}: {elapsed:.1f}s")
    return elapsed

_INICIO_TOTAL = time.perf_counter()
print(f"\n{'='*60}")
print(f"INICIO main_por_pais.py  [{_ts()}]")
print(f"ETL_MAX_ROWS={os.getenv('ETL_MAX_ROWS','0')} (0=sin límite)")
print(f"{'='*60}\n")

from extract.extractor import extraer_uruguay, extraer_espana
from transform.transformer import transformar_uruguay, transformar_espana
from extract.extract_brasil_chunks import cargar_brasil_chunks
from load.loader_postgres import get_conn, cargar_fuentes, cargar_pais, limpiar_tablas, cargar_rechazados
from load.loader_mongo import get_client, cargar_pais_mongo

MONGO_DB = os.getenv('MONGO_DB')

# ── Inicializar bases ──────────────────────────────────────────────────────
conn = get_conn()
limpiar_tablas(conn)
cargar_fuentes(conn)
conn.close()

client = get_client()
db = client[MONGO_DB]
db['accidentes'].drop()
print("🧹 Tablas y colección limpiadas\n")

rechazados_total = []

# ══════════════════════════════════════════════════════════════════
# URUGUAY
# ══════════════════════════════════════════════════════════════════
print(f"📌 URUGUAY  [{_ts()}]")
t0 = time.perf_counter()
df_raw_uy = extraer_uruguay()
_lap("extract UY", t0)

t0 = time.perf_counter()
df_uy, rech_uy = transformar_uruguay(df_raw_uy)
t_tr_uy = _lap("transform UY", t0)
del df_raw_uy; gc.collect()

t0 = time.perf_counter()
conn = get_conn()
ins_uy, err_uy = cargar_pais(conn, df_uy, 1)
t_sql_uy = _lap("load SQL UY", t0)
print(f"   SQL: {ins_uy:,} insertados | {err_uy} errores")
conn.close()

t0 = time.perf_counter()
ins_m_uy, _ = cargar_pais_mongo(db, df_uy, 'uruguay', id_fuente=1)
_lap("load Mongo UY", t0)
print(f"   MongoDB: {ins_m_uy:,} insertados")
rechazados_total.append(rech_uy)
del df_uy; gc.collect()

# ══════════════════════════════════════════════════════════════════
# BRASIL — chunks directos sin staging
# ══════════════════════════════════════════════════════════════════
print(f"\n📌 BRASIL (chunks)  [{_ts()}]")
t0 = time.perf_counter()
total_sql_br, total_mongo_br = cargar_brasil_chunks()
_lap("carga total BR", t0)

# ══════════════════════════════════════════════════════════════════
# ESPAÑA
# ══════════════════════════════════════════════════════════════════
print(f"\n📌 ESPAÑA  [{_ts()}]")
t0 = time.perf_counter()
df_raw_es = extraer_espana()
_lap("extract ES", t0)

t0 = time.perf_counter()
df_es, rech_es = transformar_espana(df_raw_es)
_lap("transform ES", t0)
del df_raw_es; gc.collect()

t0 = time.perf_counter()
conn = get_conn()
ins_es, err_es = cargar_pais(conn, df_es, 3)
_lap("load SQL ES", t0)
print(f"   SQL: {ins_es:,} insertados | {err_es} errores")
conn.close()

t0 = time.perf_counter()
ins_m_es, _ = cargar_pais_mongo(db, df_es, 'espana', id_fuente=3)
_lap("load Mongo ES", t0)
print(f"   MongoDB: {ins_m_es:,} insertados")
rechazados_total.append(rech_es)
del df_es; gc.collect()

# ══════════════════════════════════════════════════════════════════
# RECHAZADOS
# ══════════════════════════════════════════════════════════════════
conn = get_conn()
df_rech = pd.concat([r for r in rechazados_total if len(r) > 0], ignore_index=True)
cargar_rechazados(conn, df_rech)
conn.close()
client.close()

_total = time.perf_counter() - _INICIO_TOTAL
print(f"\n{'='*60}")
print(f"✅ Pipeline completado  [{_ts()}]")
print(f"   Uruguay SQL : {ins_uy:,}  |  Mongo: {ins_m_uy:,}")
print(f"   Brasil  SQL : {total_sql_br:,}  |  Mongo: {total_mongo_br:,}")
print(f"   España  SQL : {ins_es:,}  |  Mongo: {ins_m_es:,}")
print(f"   Rechazados  : {len(df_rech):,}")
print(f"   TIEMPO TOTAL: {_total:.1f}s  ({_total/60:.1f} min)")
print(f"{'='*60}")
