"""
geocodificar_espana.py
Asigna coordenadas a accidentes de España usando centroide de provincia.
52 provincias → Nominatim → UPDATE en PostgreSQL.
"""
import time
import requests
import psycopg2
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

# Coordenadas de capitales/centroides de provincias españolas
# Usamos tabla hardcodeada para evitar depender de Nominatim
COORDS_PROVINCIAS = {
    'Álava':                    (42.8467, -2.6726),
    'Albacete':                 (38.9943, -1.8585),
    'Alicante':                 (38.3452, -0.4810),
    'Almería':                  (36.8340, -2.4637),
    'Ávila':                    (40.6566, -4.6814),
    'Badajoz':                  (38.8794, -6.9707),
    'Balears (Illes)':          (39.5696, 2.6502),
    'Barcelona':                (41.3851, 2.1734),
    'Burgos':                   (42.3440, -3.6969),
    'Cáceres':                  (39.4753, -6.3723),
    'Cádiz':                    (36.5271, -6.2886),
    'Castellón':                (39.9864, -0.0513),
    'Ciudad Real':              (38.9848, -3.9274),
    'Córdoba':                  (37.8882, -4.7794),
    'Coruña (A)':               (43.3623, -8.4115),
    'Cuenca':                   (40.0704, -2.1374),
    'Girona':                   (41.9794, 2.8214),
    'Granada':                  (37.1773, -3.5986),
    'Guadalajara':              (40.6321, -3.1667),
    'Gipuzkoa':                 (43.3128, -1.9754),
    'Huelva':                   (37.2614, -6.9447),
    'Huesca':                   (42.1401, -0.4089),
    'Jaén':                     (37.7796, -3.7849),
    'León':                     (42.5987, -5.5671),
    'Lleida':                   (41.6176, 0.6200),
    'Rioja (La)':               (42.2871, -2.5396),
    'Lugo':                     (43.0097, -7.5567),
    'Madrid':                   (40.4168, -3.7038),
    'Málaga':                   (36.7213, -4.4214),
    'Murcia':                   (37.9922, -1.1307),
    'Navarra':                  (42.6954, -1.6761),
    'Ourense':                  (42.3359, -7.8639),
    'Asturias':                 (43.3614, -5.8593),
    'Palencia':                 (42.0096, -4.5288),
    'Palmas (Las)':             (28.1235, -15.4363),
    'Pontevedra':               (42.4336, -8.6477),
    'Salamanca':                (40.9701, -5.6635),
    'Santa Cruz de Tenerife':   (28.4636, -16.2518),
    'Cantabria':                (43.1828, -3.9878),
    'Segovia':                  (40.9429, -4.1088),
    'Sevilla':                  (37.3891, -5.9845),
    'Soria':                    (41.7640, -2.4647),
    'Tarragona':                (41.1189, 1.2445),
    'Teruel':                   (40.3456, -1.1065),
    'Toledo':                   (39.8628, -4.0273),
    'Valencia':                 (39.4699, -0.3763),
    'Valladolid':               (41.6523, -4.7245),
    'Bizkaia':                  (43.2630, -2.9350),
    'Zamora':                   (41.5034, -5.7447),
    'Zaragoza':                 (41.6488, -0.8891),
    'Ceuta':                    (35.8894, -5.3198),
    'Melilla':                  (35.2923, -2.9381),
}

def geocodificar_espana():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    # Obtener regiones únicas de España sin coordenadas
    cur.execute("""
        SELECT DISTINCT u.region
        FROM proyecto.accidentes a
        JOIN proyecto.ubicacion u ON a.id_ubicacion = u.id_ubicacion
        WHERE u.pais = 'España'
          AND a.latitud IS NULL
          AND u.region IS NOT NULL
        ORDER BY u.region
    """)
    regiones = [r[0] for r in cur.fetchall()]
    print(f"Regiones a geocodificar: {len(regiones)}")

    actualizados = 0
    no_encontrados = []

    for region in regiones:
        coords = COORDS_PROVINCIAS.get(region)
        if coords:
            lat, lon = coords
            cur.execute("""
                UPDATE proyecto.accidentes a
                SET latitud = %s, longitud = %s
                FROM proyecto.ubicacion u
                WHERE a.id_ubicacion = u.id_ubicacion
                  AND u.pais = 'España'
                  AND u.region = %s
                  AND a.latitud IS NULL
            """, (lat, lon, region))
            n = cur.rowcount
            conn.commit()
            actualizados += n
            print(f"   ✅ {region}: {n:,} registros → ({lat}, {lon})")
        else:
            no_encontrados.append(region)
            print(f"   ⚠️  {region}: sin coordenadas hardcodeadas")

    cur.close()
    conn.close()

    print(f"\n✅ Total actualizados: {actualizados:,}")
    if no_encontrados:
        print(f"⚠️  Sin coordenadas: {no_encontrados}")

if __name__ == '__main__':
    geocodificar_espana()
