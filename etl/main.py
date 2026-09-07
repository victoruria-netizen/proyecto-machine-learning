import sys
import os
import logging
import time
from dotenv import load_dotenv

load_dotenv('/app/config/.env')
LOG_PATH = os.getenv('LOG_PATH', '/app/logs')

logging.basicConfig(
    filename=LOG_PATH + '/etl.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def main(limpiar=True):
    inicio = time.time()
    print("=" * 50)
    print("🚀 INICIANDO PIPELINE ETL COMPLETO")
    print("=" * 50)
    logging.info("=== INICIO PIPELINE COMPLETO ===")

    # 1. EXTRACCIÓN
    print("\n📦 ETAPA 1: EXTRACCIÓN")
    from extract.extractor import extraer_todos
    datos_raw = extraer_todos()

    # 2. TRANSFORMACIÓN
    print("\n🔄 ETAPA 2: TRANSFORMACIÓN")
    from transform.transformer import transformar_todos
    datos_tf = transformar_todos(datos_raw)

    # 3. CARGA SQL
    print("\n📥 ETAPA 3: CARGA PostgreSQL")
    from load.loader_postgres import cargar_todos
    cargar_todos(datos_tf, limpiar=limpiar)

    # 4. CARGA NOSQL
    print("\n📥 ETAPA 4: CARGA MongoDB")
    from load.loader_mongo import cargar_todos_mongo
    cargar_todos_mongo(datos_tf, limpiar=limpiar)

    # 5. RESUMEN
    fin = time.time()
    duracion = round((fin - inicio) / 60, 2)
    print("\n" + "=" * 50)
    print(f"✅ PIPELINE COMPLETADO EN {duracion} MINUTOS")
    print("=" * 50)
    logging.info(f"=== FIN PIPELINE: {duracion} minutos ===")

if __name__ == '__main__':
    # Si se pasa argumento 'incremental' no limpia las tablas
    limpiar = '--incremental' not in sys.argv
    main(limpiar=limpiar)
