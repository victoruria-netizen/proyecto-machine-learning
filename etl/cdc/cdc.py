import pandas as pd
import psycopg2
import os
import logging
import time
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv('/app/config/.env')

DB_CONFIG = {
    'host':     os.getenv('PG_HOST'),
    'port':     int(os.getenv('PG_PORT', 5432)),
    'user':     os.getenv('PG_USER'),
    'password': os.getenv('PG_PASSWORD'),
    'dbname':   os.getenv('PG_DB'),
}

MONGO_URI = os.getenv('MONGO_URI')
MONGO_DB  = os.getenv('MONGO_DB')
LOG_PATH  = os.getenv('LOG_PATH', '/app/logs')

logging.basicConfig(
    filename=LOG_PATH + '/cdc.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def crear_tabla_control(conn):
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS proyecto.cdc_control (
            id             SERIAL PRIMARY KEY,
            pais           VARCHAR(50),
            ultima_fecha   DATE,
            ultima_ejecucion TIMESTAMP DEFAULT NOW(),
            registros_procesados INT
        )
    """)
    conn.commit()
    cur.close()
    print("✅ Tabla CDC control creada")
    logging.info("[CDC] Tabla control creada")

def get_ultima_fecha(conn, pais):
    cur = conn.cursor()
    cur.execute("""
        SELECT ultima_fecha FROM proyecto.cdc_control
        WHERE pais = %s
        ORDER BY ultima_ejecucion DESC
        LIMIT 1
    """, (pais,))
    row = cur.fetchone()
    cur.close()
    return row[0] if row else None

def actualizar_control(conn, pais, ultima_fecha, registros):
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO proyecto.cdc_control (pais, ultima_fecha, registros_procesados)
        VALUES (%s, %s, %s)
    """, (pais, ultima_fecha, registros))
    conn.commit()
    cur.close()

def carga_incremental_sql(conn, df, pais, id_fuente):
    from load.loader_postgres import cargar_pais
    import numpy as np

    ultima_fecha = get_ultima_fecha(conn, pais)

    if ultima_fecha:
        df_nuevo = df[df['fecha'] > pd.Timestamp(ultima_fecha)]
        print(f"   📅 Última fecha procesada: {ultima_fecha}")
        print(f"   📊 Registros nuevos: {len(df_nuevo)}")
    else:
        df_nuevo = df
        print(f"   📅 Primera ejecución — cargando todo")
        print(f"   📊 Registros: {len(df_nuevo)}")

    if len(df_nuevo) == 0:
        print(f"   ℹ️  No hay registros nuevos para {pais}")
        logging.info(f"[CDC] {pais}: sin registros nuevos")
        return 0

    ins, err = cargar_pais(conn, df_nuevo, id_fuente)

    if len(df_nuevo) > 0:
        max_fecha = df_nuevo['fecha'].max()
        actualizar_control(conn, pais, max_fecha, ins)

    logging.info(f"[CDC] {pais}: {ins} nuevos registros insertados")
    return ins

def carga_incremental_mongo(db, df, pais, ultima_fecha):
    from load.loader_mongo import cargar_pais_mongo

    if ultima_fecha:
        df_nuevo = df[df['fecha'] > pd.Timestamp(ultima_fecha)]
    else:
        df_nuevo = df

    if len(df_nuevo) == 0:
        print(f"   ℹ️  No hay documentos nuevos para {pais} en MongoDB")
        return 0

    ins, err = cargar_pais_mongo(db, df_nuevo, pais)
    logging.info(f"[CDC] MongoDB {pais}: {ins} documentos insertados")
    return ins

def simular_nuevos_registros():
    """Registros sintéticos para prueba CDC — modelo sin persona, gravedad 4 categorías."""
    nuevos = pd.DataFrame([
        {
            'fecha':          pd.Timestamp('2025-12-01'),
            'hora':           '08:00',
            'tipo_accidente': 'Choque frontal',
            'gravedad':       'leve',
            'latitud':        -34.9011,
            'longitud':       -56.1645,
            'pais':           'Uruguay',
            'region':         'Montevideo',
            'municipio':      'Montevideo',
            'tipo_vehiculo':  'Auto',
        },
        {
            'fecha':          pd.Timestamp('2025-12-02'),
            'hora':           '14:00',
            'tipo_accidente': 'Atropello',
            'gravedad':       'grave',
            'latitud':        -34.8900,
            'longitud':       -56.1700,
            'pais':           'Uruguay',
            'region':         'Montevideo',
            'municipio':      'Montevideo',
            'tipo_vehiculo':  'Moto',
        },
        {
            'fecha':          pd.Timestamp('2025-12-03'),
            'hora':           '22:00',
            'tipo_accidente': 'Despiste',
            'gravedad':       'fatal',
            'latitud':        -34.8800,
            'longitud':       -56.1800,
            'pais':           'Uruguay',
            'region':         'Canelones',
            'municipio':      'Las Piedras',
            'tipo_vehiculo':  'Auto',
        },
    ])
    return nuevos

def ejecutar_cdc(datos_transformados):
    print("\n" + "=" * 50)
    print("🔄 INICIANDO CDC — CARGA INCREMENTAL")
    print("=" * 50)
    logging.info("=== INICIO CDC ===")
    inicio = time.time()

    conn   = psycopg2.connect(**DB_CONFIG)
    client = MongoClient(MONGO_URI)
    db     = client[MONGO_DB]

    crear_tabla_control(conn)

    paises = [
        ('uruguay', datos_transformados['uruguay'], 1),
        ('brasil',  datos_transformados['brasil'],  2),
        ('espana',  datos_transformados['espana'],  3),
    ]

    total_nuevos_sql   = 0
    total_nuevos_mongo = 0

    for nombre, df, id_fuente in paises:
        print(f"\n📌 CDC {nombre.upper()}:")
        ultima = get_ultima_fecha(conn, nombre)
        ins_sql   = carga_incremental_sql(conn, df, nombre, id_fuente)
        ins_mongo = carga_incremental_mongo(db, df, nombre, ultima)
        total_nuevos_sql   += ins_sql
        total_nuevos_mongo += ins_mongo

    # Simulación de registros nuevos — LÍNEA CORREGIDA
    print("\n🧪 Simulando 3 registros nuevos de prueba...")
    nuevos = simular_nuevos_registros()
    ins_sim_sql   = carga_incremental_sql(conn, nuevos, 'uruguay_sim', 1)
    ins_sim_mongo = carga_incremental_mongo(db, nuevos, 'uruguay', None)
    print(f"✅ Simulación: {ins_sim_sql} en SQL | {ins_sim_mongo} en MongoDB")

    fin = time.time()
    duracion = round(fin - inicio, 2)

    print(f"\n📊 Resumen CDC:")
    print(f"   Nuevos en SQL:   {total_nuevos_sql}")
    print(f"   Nuevos en Mongo: {total_nuevos_mongo}")
    print(f"   Tiempo:          {duracion} segundos")
    print("=" * 50)
    logging.info(f"=== FIN CDC: {duracion}s ===")

    conn.close()
    client.close()

if __name__ == '__main__':
    from extract import extraer_todos
    from transform import transformar_todos
    datos_raw = extraer_todos()
    datos_tf  = transformar_todos(datos_raw)
    ejecutar_cdc(datos_tf)
