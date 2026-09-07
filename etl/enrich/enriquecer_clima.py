"""
enriquecer_clima.py — Enriquecimiento con Open-Meteo API
Grupo 04 · LIDIA · UTEC ITR Norte
Consulta datos meteorológicos históricos para cada combinación única
lat/lon + fecha + hora y los guarda en condicion_climatica.
"""
import requests
import psycopg2
import pandas as pd
import time
import logging
import os
from dotenv import load_dotenv

load_dotenv('/app/config/.env')

DB_CONFIG = {
    'host':     os.getenv('PG_HOST'),
    'port':     int(os.getenv('PG_PORT', 5432)),
    'user':     os.getenv('PG_USER'),
    'password': os.getenv('PG_PASSWORD'),
    'dbname':   os.getenv('PG_DB'),
}
LOG_PATH = os.getenv('LOG_PATH', '/app/logs')

logging.basicConfig(
    filename=LOG_PATH + '/clima.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

WMO_TRADUCCION = {
    0:'Despejado',1:'Mayormente despejado',2:'Parcialmente nublado',3:'Nublado',
    10:'Neblina',45:'Niebla',48:'Niebla con escarcha',
    51:'Llovizna ligera',53:'Llovizna moderada',55:'Llovizna densa',
    56:'Llovizna helada ligera',57:'Llovizna helada densa',
    61:'Lluvia leve',63:'Lluvia moderada',65:'Lluvia fuerte',
    66:'Lluvia helada leve',67:'Lluvia helada fuerte',
    71:'Nieve leve',73:'Nieve moderada',75:'Nieve fuerte',77:'Granos de nieve',
    80:'Chubascos leves',81:'Chubascos moderados',82:'Chubascos violentos',
    85:'Chubascos de nieve leves',86:'Chubascos de nieve fuertes',
    95:'Tormenta eléctrica',96:'Tormenta con granizo leve',99:'Tormenta con granizo fuerte'
}

def consultar_openmeteo(lat, lon, fecha):
    """Consulta Open-Meteo para un día completo (24 horas)."""
    url = (
        f"https://archive-api.open-meteo.com/v1/archive?"
        f"latitude={lat}&longitude={lon}&"
        f"start_date={fecha}&end_date={fecha}&"
        f"hourly=temperature_2m,precipitation,wind_speed_10m,weather_code"
    )
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        logging.warning(f"[CLIMA] Error API lat={lat} lon={lon} fecha={fecha}: {e}")
        return None

def procesar_respuesta(datos, hora, lat, lon, fecha, pais):
    """Extrae datos de la hora específica de la respuesta."""
    target = f"{fecha}T{hora:02d}:00"
    tiempos = datos.get('hourly', {}).get('time', [])
    if target not in tiempos:
        return None
    i = tiempos.index(target)
    h = datos['hourly']
    codigo = h['weather_code'][i]
    return {
        'latitud':          round(lat, 2),
        'longitud':         round(lon, 2),
        'fecha':            fecha,
        'hora':             hora,
        'temperatura_c':    h['temperature_2m'][i],
        'precipitacion_mm': h['precipitation'][i],
        'velocidad_viento_kmh': h['wind_speed_10m'][i],
        'codigo_wmo':       codigo,
        'estado_climatico': WMO_TRADUCCION.get(codigo, 'Desconocido'),
    }

def guardar_clima(conn, datos_clima):
    """Inserta en condicion_climatica y retorna id_clima."""
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO proyecto.condicion_climatica
            (latitud, longitud, fecha, hora, temperatura_c, precipitacion_mm,
             velocidad_viento_kmh, codigo_wmo, estado_climatico, timestamp_consulta)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,NOW())
        RETURNING id_clima
    """, (
        datos_clima['latitud'],           datos_clima['longitud'],
        datos_clima['fecha'],             datos_clima['hora'],
        datos_clima['temperatura_c'],     datos_clima['precipitacion_mm'],
        datos_clima['velocidad_viento_kmh'], datos_clima['codigo_wmo'],
        datos_clima['estado_climatico'],
    ))
    id_clima = cur.fetchone()[0]
    conn.commit()
    cur.close()
    return id_clima

def actualizar_accidentes(conn, lat, lon, fecha, hora, id_clima):
    """Vincula id_clima a todos los accidentes de esa combinación."""
    cur = conn.cursor()
    cur.execute("""
        UPDATE proyecto.accidentes a
        SET id_clima = %s
        FROM proyecto.ubicacion u
        WHERE a.id_ubicacion = u.id_ubicacion
          AND ROUND(a.latitud::numeric, 1) = ROUND(%s::numeric, 1)
          AND ROUND(a.longitud::numeric, 1) = ROUND(%s::numeric, 1)
          AND DATE(a.fecha) = %s
          AND EXTRACT(HOUR FROM a.fecha::timestamp) = %s
          AND a.id_clima IS NULL
    """, (id_clima, lat, lon, fecha, hora))
    n = cur.rowcount
    conn.commit()
    cur.close()
    return n

def enriquecer_pais(pais, max_combinaciones=None):
    """Enriquece todos los accidentes de un país con datos climáticos."""
    conn = psycopg2.connect(**DB_CONFIG)
    # Deshabilitar parallel workers — evita ENOSPC en /dev/shm del contenedor Docker
    conn.cursor().execute("SET max_parallel_workers_per_gather = 0")
    conn.commit()

    # Obtener combinaciones únicas lat/lon/fecha/hora
    sql = """
        SELECT
            ROUND(a.latitud::numeric, 1)  AS lat,
            ROUND(a.longitud::numeric, 1) AS lon,
            DATE(a.fecha)                 AS fecha,
            EXTRACT(HOUR FROM a.fecha::timestamp)::int AS hora,
            COUNT(*)                      AS total_accidentes
        FROM proyecto.accidentes a
        JOIN proyecto.ubicacion u ON a.id_ubicacion = u.id_ubicacion
        WHERE u.pais = %s
          AND a.latitud  IS NOT NULL
          AND a.longitud IS NOT NULL
          AND a.fecha    IS NOT NULL
          AND a.id_clima IS NULL
        GROUP BY lat, lon, fecha, hora
        ORDER BY total_accidentes DESC
    """
    if max_combinaciones:
        sql += f" LIMIT {max_combinaciones}"

    df = pd.read_sql(sql, conn, params=(pais,))
    conn.close()

    total = len(df)
    print(f"\n🌤️  Enriqueciendo {pais}: {total} combinaciones únicas")
    logging.info(f"[CLIMA] {pais}: {total} combinaciones")

    ok = 0
    errores = 0
    cache_dia = {}  # Cache por (lat,lon,fecha) para no re-consultar la API

    for i, row in df.iterrows():
        lat   = float(row['lat'])
        lon   = float(row['lon'])
        fecha = str(row['fecha'])
        hora  = int(row['hora'])

        clave_dia = (round(lat,1), round(lon,1), fecha)

        # Consultar API solo si no está en caché
        if clave_dia not in cache_dia:
            datos_api = consultar_openmeteo(lat, lon, fecha)
            cache_dia[clave_dia] = datos_api
            time.sleep(0.5)  # Respetar rate limit de Nominatim

        datos_api = cache_dia[clave_dia]
        if not datos_api:
            errores += 1
            continue

        clima = procesar_respuesta(datos_api, hora, lat, lon, fecha, pais)
        if not clima:
            errores += 1
            continue

        conn = psycopg2.connect(**DB_CONFIG)
        id_clima = guardar_clima(conn, clima)
        n_act = actualizar_accidentes(conn, lat, lon, fecha, hora, id_clima)
        conn.close()

        ok += 1
        if ok % 50 == 0:
            print(f"   ... {ok}/{total} combinaciones procesadas ({n_act} accidentes actualizados)")
        logging.info(f"[CLIMA] {pais} {fecha} {hora}h: id_clima={id_clima}, {n_act} accidentes")

    print(f"✅ {pais}: {ok} OK | {errores} errores")
    logging.info(f"[CLIMA] {pais} completado: {ok} OK | {errores} errores")

def ejecutar_enriquecimiento():
    print("🌤️  INICIANDO ENRIQUECIMIENTO CLIMÁTICO")
    print("="*50)

    # Límite de 2000 combinaciones más frecuentes por país — rate limit de Open-Meteo
    enriquecer_pais('Brasil',  max_combinaciones=2000)
    enriquecer_pais('España',  max_combinaciones=2000)
    enriquecer_pais('Uruguay', max_combinaciones=2000)

    # Resumen final
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("SET max_parallel_workers_per_gather = 0")
    cur.execute("""
        SELECT u.pais,
               COUNT(*) as total,
               COUNT(a.id_clima) as con_clima,
               ROUND(COUNT(a.id_clima)*100.0/COUNT(*),1) as pct
        FROM proyecto.accidentes a
        JOIN proyecto.ubicacion u ON a.id_ubicacion = u.id_ubicacion
        GROUP BY u.pais ORDER BY u.pais
    """)
    print("\n📊 Cobertura climática:")
    for r in cur.fetchall():
        print(f"   {r[0]}: {r[2]:,}/{r[1]:,} ({r[3]}%)")
    cur.close()
    conn.close()

if __name__ == '__main__':
    ejecutar_enriquecimiento()
