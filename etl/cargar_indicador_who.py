"""
Carga el indicador WHO SA_0000001688 (Alcohol consumption, age 15+)
desde EE6F72A_ALL_LATEST_WHO.csv hacia proyecto.indicador_who.

Idempotente: usa INSERT ... ON CONFLICT DO UPDATE.
Ejecutar después de que init.sql y ddl_indicador_who.sql ya corrieron.
"""

import logging
import os
from datetime import datetime
from pathlib import Path

import pandas as pd
import psycopg2
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s [WHO] %(levelname)s — %(message)s",
)
log = logging.getLogger(__name__)

RAW_PATH = os.getenv("RAW_PATH", "data/raw")
CSV_FILENAME = "EE6F72A_ALL_LATEST_WHO.csv"

INDICATOR_CODE = "SA_0000001688"
INDICATOR_NAME = "Alcohol consumption (age 15+)"
UNIT = "litros_alcohol_puro_per_capita"

# Mapa ISO → nombre usado en proyecto.ubicacion
PAIS_MAP = {
    "Uruguay": "Uruguay",
    "Brazil":  "Brasil",
    "Spain":   "España",
}

UPSERT_SQL = """
INSERT INTO proyecto.indicador_who
    (pais, anio, indicador_cod, indicador_nombre, valor, valor_ic_inf, valor_ic_sup,
     unidad, sexo, fuente, fecha_extraccion)
VALUES
    (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
ON CONFLICT (pais, anio, indicador_cod, sexo)
DO UPDATE SET
    valor            = EXCLUDED.valor,
    valor_ic_inf     = EXCLUDED.valor_ic_inf,
    valor_ic_sup     = EXCLUDED.valor_ic_sup,
    indicador_nombre = EXCLUDED.indicador_nombre,
    fecha_extraccion = EXCLUDED.fecha_extraccion;
"""


def _pg_conn():
    return psycopg2.connect(
        host=os.getenv("PG_HOST", "localhost"),
        port=int(os.getenv("PG_PORT", 5432)),
        dbname=os.getenv("PG_DB", "siniestros_db"),
        user=os.getenv("PG_USER", "siniestros_user"),
        password=os.getenv("PG_PASSWORD", ""),
    )


def cargar_indicador_who():
    csv_path = Path(RAW_PATH) / CSV_FILENAME
    if not csv_path.exists():
        raise FileNotFoundError(f"No se encontró {csv_path}")

    log.info("Leyendo %s", csv_path)
    df = pd.read_csv(csv_path, encoding="utf-8")
    log.info("Total filas en CSV: %d", len(df))

    # Filtrar indicador y países
    df = df[
        (df["IND_CODE"] == INDICATOR_CODE) &
        (df["DIM_GEO_CODE_TYPE"] == "COUNTRY") &
        (df["GEO_NAME_SHORT"].isin(PAIS_MAP.keys()))
    ].copy()
    log.info("Filas tras filtrado (3 países, indicador alcohol): %d", len(df))

    # Normalizar nombre de país
    df["pais_dw"] = df["GEO_NAME_SHORT"].map(PAIS_MAP)

    now = datetime.utcnow()
    filas_ok = 0
    filas_err = 0

    with _pg_conn() as conn, conn.cursor() as cur:
        for _, row in df.iterrows():
            try:
                cur.execute(UPSERT_SQL, (
                    row["pais_dw"],
                    int(row["DIM_TIME"]),
                    INDICATOR_CODE,
                    INDICATOR_NAME,
                    float(row["RATE_PER_CAPITA_N"]) if pd.notna(row["RATE_PER_CAPITA_N"]) else None,
                    float(row["RATE_PER_CAPITA_NL"]) if pd.notna(row["RATE_PER_CAPITA_NL"]) else None,
                    float(row["RATE_PER_CAPITA_NU"]) if pd.notna(row["RATE_PER_CAPITA_NU"]) else None,
                    UNIT,
                    str(row["DIM_SEX"]),
                    "WHO GHO",
                    now,
                ))
                filas_ok += 1
            except Exception as exc:
                log.warning("Error en fila %s/%s: %s", row["pais_dw"], row["DIM_TIME"], exc)
                conn.rollback()
                filas_err += 1
                continue
        conn.commit()

    log.info("Carga completada — insertados/actualizados: %d | errores: %d", filas_ok, filas_err)

    # Reporte de cobertura por país
    cobertura = (
        df.groupby("pais_dw")["DIM_TIME"]
        .agg(["min", "max", "count"])
        .rename(columns={"min": "anio_min", "max": "anio_max", "count": "n_anios"})
    )
    log.info("Cobertura cargada:\n%s", cobertura.to_string())


if __name__ == "__main__":
    cargar_indicador_who()
