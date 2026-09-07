import pandas as pd
import os
import logging
import numpy as np
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv('/app/config/.env')

MONGO_URI = os.getenv('MONGO_URI')
MONGO_DB  = os.getenv('MONGO_DB', 'grp04db')
LOG_PATH  = os.getenv('LOG_PATH', '/app/logs')

logging.basicConfig(
    filename=LOG_PATH + '/etl.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def get_client():
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    client.server_info()
    print("✅ Conectado a MongoDB")
    return client

def limpiar_valor(v):
    if v is None:
        return None
    if isinstance(v, float) and np.isnan(v):
        return None
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.floating,)):
        return float(v)
    if isinstance(v, pd.Timestamp):
        return v.to_pydatetime()
    if hasattr(v, 'item'):
        return v.item()
    return v

def fila_a_documento(row, pais, id_fuente):
    lat = limpiar_valor(row.get('latitud'))
    lon = limpiar_valor(row.get('longitud'))
    pais_val = limpiar_valor(row.get('pais', pais))

    coordenadas = (
        {'type': 'Point', 'coordinates': [lon, lat]}
        if lat is not None and lon is not None
        else None
    )

    return {
        'pais':           pais_val,
        'fecha':          limpiar_valor(row.get('fecha')),
        'hora':           limpiar_valor(row.get('hora')),
        'tipo_accidente': limpiar_valor(row.get('tipo_accidente')),
        'gravedad':       limpiar_valor(row.get('gravedad')),
        'id_fuente':      id_fuente,
        'ubicacion': {
            'pais':        pais_val,
            'region':      limpiar_valor(row.get('region')),
            'municipio':   limpiar_valor(row.get('municipio')),
            'coordenadas': coordenadas,
        },
    }

def cargar_pais_mongo(db, df, pais, id_fuente, batch_size=5000):
    collection = db.accidentes
    insertados = 0
    errores    = 0

    for i in range(0, len(df), batch_size):
        batch = df.iloc[i:i+batch_size]
        documentos = []
        for _, row in batch.iterrows():
            try:
                doc = fila_a_documento(row, pais, id_fuente)
                documentos.append(doc)
            except Exception as e:
                errores += 1
                logging.warning(f"[LOAD_NOSQL] Error doc: {e}")

        if documentos:
            try:
                result = collection.insert_many(documentos, ordered=False)
                insertados += len(result.inserted_ids)
            except Exception as e:
                errores += len(documentos)
                logging.error(f"[LOAD_NOSQL] Error batch: {e}")

        if insertados % 50000 == 0 and insertados > 0:
            print(f"   ... {insertados} documentos insertados")

    return insertados, errores

def cargar_todos_mongo(datos_transformados, limpiar=False):
    print("\n📥 Iniciando carga en MongoDB...")
    logging.info("=== INICIO CARGA NOSQL ===")

    client = get_client()
    db     = client[MONGO_DB]

    if limpiar:
        db.accidentes.drop()
        print("🧹 Colección limpiada")

    # Crear índices
    db.accidentes.create_index([('pais', 1)])
    db.accidentes.create_index([('fecha', 1)])
    db.accidentes.create_index([('pais', 1), ('fecha', 1)])
    print("✅ Índices creados")

    paises = [
        ('uruguay', datos_transformados['uruguay']),
        ('brasil',  datos_transformados['brasil']),
        ('espana',  datos_transformados['espana']),
    ]

    for nombre, df in paises:
        print(f"\n⏳ Cargando {nombre.upper()} en MongoDB ({len(df)} docs)...")
        ins, err = cargar_pais_mongo(db, df, nombre)
        logging.info(f"[LOAD_NOSQL] {nombre.upper()}: {ins} insertados, {err} errores")
        print(f"✅ {nombre.upper()}: {ins} insertados | {err} errores")

    total = db.accidentes.count_documents({})
    print(f"\n📊 Total documentos en MongoDB: {total:,}")
    logging.info(f"[LOAD_NOSQL] Total documentos: {total}")

    client.close()
    logging.info("=== FIN CARGA NOSQL ===")
    print("\n✅ Carga MongoDB completada")

if __name__ == '__main__':
    from extract import extraer_todos
    from transform import transformar_todos
    datos_raw = extraer_todos()
    datos_tf  = transformar_todos(datos_raw)
    cargar_todos_mongo(datos_tf, limpiar=True)
