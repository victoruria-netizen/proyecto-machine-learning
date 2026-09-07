import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
import os
import logging
import numpy as np
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
    filename=LOG_PATH + '/etl.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def get_conn():
    return psycopg2.connect(**DB_CONFIG)

def limpiar(valor):
    """Convierte tipos numpy a tipos nativos de Python."""
    if valor is None or (isinstance(valor, float) and np.isnan(valor)):
        return None
    if isinstance(valor, (np.integer,)):
        return int(valor)
    if isinstance(valor, (np.floating,)):
        return float(valor)
    if isinstance(valor, pd.NaT.__class__):
        return None
    return valor

FUENTES = [
    (1, 'UNASEV',  'Uruguay', 'CSV',  'https://unasev.gub.uy',                           'Anual'),
    (2, 'RENAEST', 'Brasil',  'CSV',  'https://dados.transportes.gov.br/dataset/renaest', 'Anual'),
    (3, 'DGT',     'España',  'CSV',  'https://www.dgt.es',                               'Anual'),
]

def cargar_fuentes(conn):
    cur = conn.cursor()
    for f in FUENTES:
        cur.execute("""
            INSERT INTO proyecto.fuente_dato
                (id_fuente, nombre_organismo, pais_origen, formato, url_oficial, frecuencia_actualizacion)
            VALUES (%s,%s,%s,%s,%s,%s)
            ON CONFLICT (id_fuente) DO UPDATE
                SET nombre_organismo         = EXCLUDED.nombre_organismo,
                    formato                  = EXCLUDED.formato,
                    url_oficial              = EXCLUDED.url_oficial
        """, f)
    conn.commit()
    cur.close()
    logging.info("[LOAD_SQL] Fuentes insertadas/actualizadas")
    print("✅ Fuentes cargadas")

def cargar_rechazados(conn, df_rechazados):
    cur = conn.cursor()
    # La tabla proyecto.rechazados ya existe (creada por init.sql)
    for _, row in df_rechazados.iterrows():
        cur.execute("""
            INSERT INTO proyecto.rechazados (motivo_rechazo, fecha_procesamiento, datos_raw)
            VALUES (%s, %s, %s)
        """, (
            row.get('motivo_rechazo', 'Desconocido'),
            row.get('fecha_procesamiento', pd.Timestamp.now()),
            str(row.to_dict())[:500]
        ))
    conn.commit()
    cur.close()
    logging.info(f"[LOAD_SQL] Rechazados: {len(df_rechazados)}")
    print(f"✅ Rechazados cargados: {len(df_rechazados)}")

def _prep_col(df, col, default=None):
    """Extrae una columna del DF como lista de tipos nativos Python (None donde hay NaN/NaT)."""
    if col not in df.columns:
        return [default] * len(df)
    out = []
    for v in df[col]:
        if v is None:
            out.append(default)
        elif isinstance(v, float) and np.isnan(v):
            out.append(default)
        elif isinstance(v, type(pd.NaT)) or v is pd.NaT:
            out.append(default)
        elif isinstance(v, np.integer):
            out.append(int(v))
        elif isinstance(v, np.floating):
            out.append(float(v))
        elif isinstance(v, pd.Timestamp):
            out.append(v.to_pydatetime())
        else:
            out.append(v)
    return out


def _insertar_fila_a_fila(cur, conn, slice_data, id_fuente):
    """Fallback fila-a-fila cuando un batch falla (e.g. constraint violation)."""
    ins = err = 0
    pais_v, region_v, muni_v, tveh_v, fecha_v, hora_v, tacc_v, grav_v, lat_v, lon_v = slice_data
    for j in range(len(pais_v)):
        try:
            cur.execute(
                "INSERT INTO proyecto.ubicacion (pais, region, municipio) VALUES (%s,%s,%s) RETURNING id_ubicacion",
                (pais_v[j], region_v[j], muni_v[j]))
            id_ub = cur.fetchone()[0]
            cur.execute(
                "INSERT INTO proyecto.vehiculo (tipo_vehiculo) VALUES (%s) RETURNING id_vehiculo",
                (tveh_v[j],))
            id_veh = cur.fetchone()[0]
            cur.execute("""
                INSERT INTO proyecto.accidentes
                    (fecha, hora, tipo_accidente, gravedad, latitud, longitud,
                     id_ubicacion, id_vehiculo, id_fuente)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, (fecha_v[j], hora_v[j], tacc_v[j], grav_v[j],
                  lat_v[j], lon_v[j], id_ub, id_veh, id_fuente))
            conn.commit()
            ins += 1
        except Exception as exc:
            conn.rollback()
            err += 1
            if err <= 3:
                logging.warning(f"[LOAD_SQL] Error fila: {exc}")
    return ins, err


def cargar_pais(conn, df, id_fuente, batch_size=5000):
    """
    Carga en batch con execute_values (3 INSERT por lote, no por fila).
    Fallback automático a fila-a-fila si un lote falla.
    """
    if df is None or len(df) == 0:
        return 0, 0

    # Preparar arrays una sola vez (evita overhead de iterrows por fila)
    pais_v  = _prep_col(df, 'pais', 'Desconocido')
    region_v = _prep_col(df, 'region')
    muni_v  = _prep_col(df, 'municipio')
    tveh_v  = _prep_col(df, 'tipo_vehiculo', 'Desconocido')
    fecha_v = _prep_col(df, 'fecha')
    hora_v  = _prep_col(df, 'hora')
    tacc_v  = _prep_col(df, 'tipo_accidente')
    grav_v  = _prep_col(df, 'gravedad')
    lat_v   = _prep_col(df, 'latitud')
    lon_v   = _prep_col(df, 'longitud')

    n = len(df)
    insertados = 0
    errores    = 0
    cur = conn.cursor()

    for i in range(0, n, batch_size):
        j = min(i + batch_size, n)
        sl = slice(i, j)

        datos_ub  = list(zip(pais_v[sl], region_v[sl], muni_v[sl]))
        datos_veh = [(v,) for v in tveh_v[sl]]

        try:
            # page_size=len(datos) fuerza una sola sentencia SQL por lote
            # → cur.fetchall() captura todos los RETURNING ids, no solo la última página
            execute_values(cur,
                "INSERT INTO proyecto.ubicacion (pais, region, municipio) VALUES %s RETURNING id_ubicacion",
                datos_ub, page_size=len(datos_ub))
            ids_ub = [r[0] for r in cur.fetchall()]

            execute_values(cur,
                "INSERT INTO proyecto.vehiculo (tipo_vehiculo) VALUES %s RETURNING id_vehiculo",
                datos_veh, page_size=len(datos_veh))
            ids_veh = [r[0] for r in cur.fetchall()]

            datos_acc = list(zip(
                fecha_v[sl], hora_v[sl], tacc_v[sl], grav_v[sl],
                lat_v[sl], lon_v[sl],
                ids_ub, ids_veh, [id_fuente] * len(ids_ub),
            ))
            execute_values(cur, """
                INSERT INTO proyecto.accidentes
                    (fecha, hora, tipo_accidente, gravedad, latitud, longitud,
                     id_ubicacion, id_vehiculo, id_fuente)
                VALUES %s
            """, datos_acc, page_size=2000)

            conn.commit()
            insertados += len(ids_ub)
            if insertados % 50000 == 0:
                print(f"   ... {insertados:,} registros insertados")

        except Exception as exc:
            conn.rollback()
            logging.warning(f"[LOAD_SQL] Lote {i}:{j} falló ({exc}), reintento fila-a-fila")
            slice_data = (pais_v[sl], region_v[sl], muni_v[sl], tveh_v[sl],
                          fecha_v[sl], hora_v[sl], tacc_v[sl], grav_v[sl],
                          lat_v[sl], lon_v[sl])
            ins_f, err_f = _insertar_fila_a_fila(cur, conn, slice_data, id_fuente)
            insertados += ins_f
            errores    += err_f

    cur.close()
    return insertados, errores

def limpiar_tablas(conn):
    """Limpia todas las tablas para re-ejecución idempotente."""
    cur = conn.cursor()
    # DELETE en vez de TRUNCATE — etl_user tiene DELETE pero no TRUNCATE
    for tabla in ['proyecto.accidentes', 'proyecto.vehiculo',
                  'proyecto.ubicacion', 'proyecto.rechazados']:
        cur.execute(f"DELETE FROM {tabla}")
    conn.commit()
    cur.close()
    print("🧹 Tablas limpiadas")
    logging.info("[LOAD_SQL] Tablas limpiadas")

def cargar_todos(datos_transformados, limpiar=False):
    print("\n📥 Iniciando carga en PostgreSQL...")
    logging.info("=== INICIO CARGA SQL ===")
    conn = get_conn()

    if limpiar:
        limpiar_tablas(conn)

    cargar_fuentes(conn)

    paises = [
        ('uruguay', 1),
        ('brasil',  2),
        ('espana',  3),
    ]

    for nombre, id_fuente in paises:
        df = datos_transformados[nombre]
        print(f"\n⏳ Cargando {nombre.upper()} ({len(df)} registros)...")
        ins, err = cargar_pais(conn, df, id_fuente)
        logging.info(f"[LOAD_SQL] {nombre.upper()}: {ins} insertados, {err} errores")
        print(f"✅ {nombre.upper()}: {ins} insertados | {err} errores")

    cargar_rechazados(conn, datos_transformados['rechazados'])
    conn.close()
    logging.info("=== FIN CARGA SQL ===")
    print("\n✅ Carga SQL completada")

if __name__ == '__main__':
    from extract import extraer_todos
    from transform import transformar_todos
    datos_raw = extraer_todos()
    datos_tf  = transformar_todos(datos_raw)
    cargar_todos(datos_tf, limpiar=True)
