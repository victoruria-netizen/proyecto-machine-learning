"""
config.py — Configuración centralizada del proyecto LIDIA (Siniestros Viales).
UTEC ITR Norte 2026 · Lucas Pimentel · Víctor Uría · Boris Furtado

Punto ÚNICO de carga de variables de entorno y construcción de conexiones.
Reemplaza los antiguos load_dotenv con ruta absoluta del servidor dispersos por
el repo y elimina toda ruta absoluta del código: todo se resuelve vía BASE_DIR.

Perfiles por entorno (variable APP_ENV):
    local   → desarrollo en la máquina del equipo (Windows)        [por defecto]
    server  → Servidor Institucional UTEC (Linux, nativo, repo en /app)

Orden de carga (la PRIMERA definición de cada variable gana, override=False):
    1. Variables ya presentes en el entorno del SISTEMA   (máxima prioridad)
    2. config/.env.<APP_ENV>     (perfil específico del entorno)
    3. config/.env               (valores comunes / fallback)

Gracias a override=False, en Docker las variables inyectadas por docker-compose
siguen mandando y los archivos .env nativos sólo aplican fuera del contenedor.

Uso:
    import config
    from config import PG_HOST, MONGO_URI, get_pg_conn, get_mongo_client
"""
from pathlib import Path
import os

from dotenv import load_dotenv

# ── Rutas base (relativas a este archivo — NUNCA absolutas) ──────────────────
# config.py vive en la raíz del repositorio → .parent es esa raíz.
BASE_DIR   = Path(__file__).resolve().parent
CONFIG_DIR = BASE_DIR / "config"
DATA_DIR   = BASE_DIR / "data"
LOG_DIR    = BASE_DIR / "logs"
RAW_DIR    = DATA_DIR / "raw"

# ── Perfil de entorno ────────────────────────────────────────────────────────
APP_ENV = os.getenv("APP_ENV", "local")

# ── Carga de .env  (sistema > .env.<perfil> > .env) ──────────────────────────
# override=False ⇒ nunca pisa una variable ya definida; por eso el perfil
# específico se carga primero y el .env genérico sólo rellena lo que falte.
load_dotenv(CONFIG_DIR / f".env.{APP_ENV}", override=False)
load_dotenv(CONFIG_DIR / ".env",            override=False)

# ── Crear directorios de trabajo al importar ─────────────────────────────────
LOG_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

# ── PostgreSQL ───────────────────────────────────────────────────────────────
PG_HOST     = os.getenv("PG_HOST", "localhost")
PG_PORT     = int(os.getenv("PG_PORT", "5432"))
PG_DB       = os.getenv("PG_DB", os.getenv("POSTGRES_DB", "siniestros_db"))
PG_USER     = os.getenv("PG_USER", "siniestros_user")
PG_PASSWORD = os.getenv("PG_PASSWORD", "")

# ── MongoDB ──────────────────────────────────────────────────────────────────
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
MONGO_DB  = os.getenv("MONGO_DB", "siniestros_nosql")

# ── ETL / rutas de datos ─────────────────────────────────────────────────────
ETL_MAX_ROWS       = int(os.getenv("ETL_MAX_ROWS", "0"))          # 0 = sin límite
RAW_PATH           = os.getenv("RAW_PATH", str(RAW_DIR))
LOG_LEVEL          = os.getenv("LOG_LEVEL", "INFO")
OPENMETEO_BASE_URL = os.getenv(
    "OPENMETEO_BASE_URL", "https://archive-api.open-meteo.com/v1/archive"
)


def get_pg_conn():
    """Conexión psycopg2 centralizada. Ningún módulo debe construir la suya.

    Lee las credenciales resueltas en este archivo (PG_HOST/PG_PORT/PG_DB/
    PG_USER/PG_PASSWORD). El import de psycopg2 es perezoso para que `config`
    sea importable incluso donde la librería no esté instalada (p. ej. tooling).
    """
    import psycopg2
    return psycopg2.connect(
        host=PG_HOST,
        port=PG_PORT,
        dbname=PG_DB,
        user=PG_USER,
        password=PG_PASSWORD,
    )


def get_mongo_client(**kwargs):
    """Cliente pymongo centralizado a partir de MONGO_URI.

    `kwargs` se reenvían a MongoClient (p. ej. serverSelectionTimeoutMS=5000).
    """
    from pymongo import MongoClient
    return MongoClient(MONGO_URI, **kwargs)
