# Predicción de Siniestros Viales — Proyecto de Aprendizaje Automático (PAA)

**UTEC · LIDIA · Proyecto de Aprendizaje Automático 2026**

Este repositorio corresponde al Proyecto de Aprendizaje Automático (PAA), continuación
del Proyecto de Ingeniería de Datos (PID) del mismo equipo. Su objetivo es formular y
resolver un problema de aprendizaje automático relacionado con la **predicción de
siniestros viales**, reutilizando los datos y activos útiles del proyecto anterior.

El problema se aborda como un **pronóstico de series temporales**: estimar la cantidad
esperada de siniestros por zona y período a partir de la serie histórica de siniestros de
Uruguay (UNASEV) y de variables exógenas de clima y calendario. Los resultados se
integran en una nueva pestaña del dashboard existente, que representa sobre un mapa las
zonas y períodos con mayor cantidad pronosticada de siniestros.

## Proyecto de origen (PID)

- **Repositorio PID:** https://git.utec.edu.uy/juan.pimentel/siniestros-viales-grp4
- **Componentes reutilizados:** Script de extracción, transformación, carga y dataset unificado de siniestros en Uruguay (UNASEV), ya depurado, geolocalizado (coordenadas X/Y y Departamento/Localidad) y trazable; enriquecimiento climático histórico de Open-Meteo previamente cacheado; y el dashboard en Streamlit sobre el que se integrará la nueva funcionalidad.
- **Modificaciones en el PAA:**
  - Adaptación del proceso ETL para producir series temporales agregadas por zona y período, con la granularidad temporal y territorial que se defina tras el análisis de densidad y cobertura de los datos.
  - Construcción de variables predictoras: rezagos y agregados móviles de la serie, variables de calendario (día de la semana, mes, feriados) y variables climáticas (temperatura, precipitación, viento) tomadas de la caché histórica, sin llamadas recurrentes a la API externa.
  - Incorporación de un módulo de modelado, evaluación con validación temporal y artefactos de inferencia (modelo serializado y pipeline de preprocesamiento).
  - Ampliación del dashboard con una nueva pestaña de visualización georreferenciada de las predicciones.

## Estructura del repositorio

```
README.md              Este archivo: propósito, requisitos, datos, ejecución y resultados
data/                  Datos (o mecanismo de acceso; no se versionan datos restringidos)
notebooks/             Notebooks de exploración y análisis
src/                   Código fuente de la solución (preprocesamiento, modelado, inferencia)
train/                 Scripts .py para enviar al servidor institucional (ver train/README.md)
models/                Modelos entrenados y artefactos necesarios para la inferencia
experiments/           Registro de experimentos, configuraciones y resultados
app/                   Prototipo / dashboard integrado (TRL 5)
documentacion/         Documentación del proyecto
    registro_uso_IA.md Registro incremental del uso de IA generativa
tests/                 Pruebas del pipeline de inferencia
requirements.txt       Dependencias directas del entorno, con versión exacta
requirements-lock.txt  Versiones exactas de todo el entorno (pip freeze), usadas como constraints
```

## Requisitos e instalación

**Versión de Python: 3.13.2.** Fijarla evita diferencias entre integrantes.
**Corrección (2026-09-24):** desde el 2026-09-20 este documento decía 3.13.15; esa versión no
existe (`uv python install 3.13.15` no la encuentra) — fue un error de tipeo que nadie había
vuelto a verificar. El `.venv` del proyecto y las últimas corridas ya usan 3.13.2; el estándar
pasa a ser ese. Los `00_entorno.csv` / `00b_entorno.csv` de corridas anteriores a esta fecha
quedan como registro histórico de lo que se documentó en su momento, no se reescriben.

```powershell
# Windows (PowerShell) — el selector "py" permite fijar la versión
py -3.13 -m venv .venv
.venv\Scripts\Activate.ps1
python --version                 # debe decir Python 3.13.2

python -m pip install --upgrade pip
pip install -r requirements.txt -c requirements-lock.txt
pip check                        # debe decir: No broken requirements found.
```

```bash
# Linux/Mac — no verificado: el lock se generó en Windows
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt -c requirements-lock.txt
```

Si `py -3.13` no encuentra Python 3.13.2, instalarlo desde python.org o con
`uv python install 3.13.2`, y crear el entorno con ese intérprete
(`uv python find 3.13.2` da la ruta; luego `<ruta>\python.exe -m venv .venv`). En Windows, crear
un entorno en una ruta muy larga falló una vez (2026-09-20, unos 200 caracteres de ruta,
probablemente por el límite de 260 caracteres): si pasa, crear el entorno en una ruta más corta.

**Qué es cada archivo**

- `requirements.txt` lista las dependencias directas con versión exacta: lo que importan los
  notebooks (numpy, pandas, scipy, scikit-learn, statsmodels, xgboost, matplotlib, holidays,
  geopandas, pyproj, pyshp, folium, branca, requests), `pytest` para `tests/` y lo necesario
  para ejecutarlos (jupyter, ipykernel, ipython).
- `requirements-lock.txt` es el `pip freeze` del entorno verificado. Se usa como
  *constraints* (`-c`): fija la versión de todo el árbol de dependencias sin agregar paquetes.
  Se validó instalando en un entorno limpio con `-r requirements.txt -c requirements-lock.txt`: dio
  el mismo `pip freeze`.

**Verificación de entorno en los notebooks.** `notebooks/linea_base.ipynb` (y los demás
notebooks del pipeline) tienen una celda que lee `requirements.txt` en vivo y compara la
versión de Python y la de cada dependencia directa contra el entorno donde corren; si algo
no coincide, **detiene la ejecución** con un error explícito (no es un aviso). Responde a un
problema real: las corridas del Entregable 2 se hicieron con tres combinaciones distintas de
intérprete y bibliotecas antes de que nadie lo notara.

**`skforecast` se quitó (2026-09-24).** Dejó de usarse al retirar `base_2.ipynb` —reemplazado por
`notebooks/linea_base.ipynb`, que arma el árbol candidato a mano, sin `skforecast`— y ya no lo
importa ningún notebook del pipeline (sí lo sigue usando, sólo como tutorial de referencia,
`notebooks/Ejemplos/Series_temporales_y_pronóstico_ejemplo.ipynb`; ver la nota en esa carpeta).
Las restricciones que existían por `skforecast` 0.25.0 (pandas `<3.0`, statsmodels `<0.15`,
matplotlib `<3.12`) **ya no aplican**, pero los pines no se tocaron: subir esas versiones obliga a
reejecutar y revalidar todos los notebooks, y es una decisión aparte, pendiente para el
Entregable 3. Cambiar la versión de pandas, en particular, exige comparar las salidas: el
2026-09-20 se comprobó que pandas 3.0.5 y 2.3.3 no dan lo mismo en un caso (`.astype(str)`
convierte un nulo en el texto `"nan"` en pandas 2.x; el caso está documentado en la entrada del 2026-09-20 de `HANDOFF.md`).

**Dependencias que hoy no están.** El 2026-09-20 se retiraron de `requirements.txt` las que
ningún notebook importaba: pyarrow, seaborn, xgboost, lightgbm, streamlit, streamlit-folium,
python-dotenv y pytest. **El 2026-10-13 volvieron `xgboost==3.4.1` y `pytest==9.1.1`** (Entregable 3:
candidato XGBoost y pruebas de `tests/`); el lock se regeneró en un entorno limpio y ningún otro pin
cambió. **El 2026-10-21 (fase 5) volvieron** `streamlit`, `plotly`, `pydeck`, `psycopg2-binary`, `pymongo`,
`SQLAlchemy` y `python-dotenv`, que importa el dashboard heredado en `app/`; el lock se regeneró en un entorno
limpio (con Python 3.13.9, no 3.13.2) y solo agregó paquetes. `streamlit-option-menu` no se agregó: nada lo importa.

**Agregar una dependencia.** Instalarla con versión exacta, anotarla en `requirements.txt` con un
comentario de para qué se usa, reejecutar lo que dependa de ella y regenerar
`requirements-lock.txt` con `pip freeze` (guardado en UTF-8, conservando su encabezado).

**Otros entornos.** El servidor institucional (`submit_cpu`) corre los scripts de `train/` en un
contenedor con su propio entorno (Python 3.10, pandas 1.5.3, scikit-learn 1.2.0), distinto de este;
ver `train/README.md`. Los notebooks de `notebooks/Ejemplos/` son material de ejemplo pensado para
Colab (usan seaborn, tensorflow y cv2) y no se ejecutan con este entorno.

Las credenciales y rutas sensibles se gestionan mediante variables de entorno.
`.env.example` documenta las que el código lee hoy: `PAA_DIR` (raíz del proyecto) y `PAA_CSV`
(ruta al CSV crudo de siniestros), ambas opcionales y leídas por
`notebooks/preparacion_montevideo.ipynb`. **Ningún notebook carga un archivo `.env`**: hay que
definirlas en la terminal antes de abrir Jupyter (por ejemplo, `$env:PAA_CSV = "D:\datos\..."` en
PowerShell). `python-dotenv` está instalado solo porque lo importa `app/config.py` (heredado del PID), que busca
`app/config/.env`; esa carpeta no existe y la pestaña de predicción no la necesita.

## Datos

**Fuentes**

| Fuente | Contenido | Acceso | Formato |
| ----- | ----- | ----- | ----- |
| UNASEV (Unidad Nacional de Seguridad Vial, Uruguay) | Registros históricos de siniestros de tránsito, con fecha, hora, ubicación (coordenadas X/Y, departamento y localidad) y características del evento | Datos abiertos gubernamentales; no requiere autorizaciones adicionales a las obtenidas en el PID | CSV / TXT |
| Open-Meteo — Historical Weather API | Variables meteorológicas históricas (temperatura, precipitación, viento) por ubicación y fecha/hora | API pública con límite de uso; se emplea como carga histórica puntual ya cacheada, con clave única por latitud, longitud, fecha y hora | JSON → CSV cacheado |
| Calendario de feriados de Uruguay | Feriados y días no laborables utilizados como variable exógena | Fuente pública | CSV |

**Variable objetivo y predictoras.** La variable objetivo es la cantidad de siniestros
agregada por zona y período. Como predictoras se emplean variables temporales (día de la
semana, mes, feriados), rezagos de la propia serie y variables climáticas.

**Disponibilidad y versionado.** Los datos de siniestros ya integrados y depurados
provienen del PID. Los archivos de datos no se versionan en este repositorio: `data/`
contiene únicamente la estructura de carpetas y la caché climática se obtiene o se
restaura mediante el script de ingesta. Para reproducir el conjunto de trabajo, ubicar los
archivos fuente en `data/raw/` y ejecutar el pipeline descrito en la sección siguiente,
que deja el dataset consolidado en `data/processed/`.

**Calidad y limitaciones conocidas.** Antes de fijar la granularidad definitiva se evalúa
la densidad de observaciones por zona y período, dado el riesgo de series con exceso de
períodos en cero, y se verifica la completitud de las variables climáticas para las zonas
y fechas de interés. El pipeline se diseña para utilizar únicamente información disponible
al momento de generar el pronóstico, evitando fugas de información.

**Protección.** Los datos son públicos y agregados, sin información personal
identificable. Las credenciales de acceso se gestionan mediante variables de entorno y no
se versionan. Se evita exponer coordenadas exactas que puedan identificar domicilios
particulares en las visualizaciones públicas.

## Ejecución

### Notebooks (lo que se puede ejecutar hoy)

Con el entorno activado y desde la raíz del repositorio. Se ejecutan **en este orden**, porque
varios leen lo que escribe uno anterior:

| # | Notebook | Lee | Escribe |
| --- | --- | --- | --- |
| 1 | `preparacion_montevideo` | `data/raw/` (siniestros, capas de zonas y caché de clima) | `data/processed/` y `experiments/etl_montevideo/` |
| 2 | `diagnostico_municipios` | `data/processed/` y, para 2.4/2.5/2.7, `data/raw/` (siniestros crudos y capa de municipios). **Sólo el bloque de desarrollo: el test se descarta al leer** | `experiments/diagnostico_municipios/` |
| 3 | `linea_base` | `data/processed/panel_zona_top.csv` | `experiments/linea_base/` |
| 4 | `modelos_candidatos` | `data/processed/panel_diario_montevideo.csv` **sólo hasta 2025-02-05** (el test se descarta al leer, con `assert`) y `experiments/linea_base/tablas/04_desarrollo_backtesting.csv` | `experiments/modelos_candidatos/` |

```powershell
jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=3600 notebooks/preparacion_montevideo.ipynb
```

`--inplace` reemplaza el notebook por su versión con las salidas nuevas. Repetir el comando con
cada notebook de la tabla, en ese orden. Para abrirlos en Jupyter o VS Code, elegir el
intérprete de `.venv` (Python 3.13.2).

**Nota (2026-09-24):** hasta esta fecha la tabla tenía seis filas: `base` y `base_2` leían el
mismo `panel_zona_top.csv` y corrían en los puestos 5 y 6 (el 2026-09-20 los seis corrieron en
secuencia en unos 75 segundos, sin errores). Se unificaron en `linea_base`, que queda en el
puesto 5; `base.ipynb` y `base_2.ipynb` quedaron preservados en la rama `entregable_2`. Ver
`documentacion/cambios_para_informe.md`.

- **Datos de entrada.** `data/raw/` no se versiona: hay que copiar ahí los archivos fuente
  (`uru_siniestros_unificado.csv`, las capas geojson y `clima_montevideo.csv`). Si la caché de
  clima cubre el período, `preparacion_montevideo` no consulta Open-Meteo.
- **Registro del entorno.** `linea_base` guarda las versiones en
  `experiments/linea_base/tablas/00_entorno.csv`, y `diagnostico_municipios` en
  `experiments/diagnostico_municipios/tablas/00b_entorno.csv`, y `modelos_candidatos` en
  `experiments/modelos_candidatos/tablas/00_entorno.csv`; cada uno registra solo las bibliotecas que
  importa. `preparacion_montevideo` no las registra.
- **Cómo leer una reejecución.** La del 2026-09-20 dejó idénticas byte a byte todas las tablas de
  resultados; las diferencias fueron solo de versiones, fechas, tamaños de archivo, etiquetas de tipo
  (`str` frente a `object`) e identificadores aleatorios del mapa HTML (detalle en cada
  `documentacion/resumen_*.md`). Si una reejecución cambia una cifra de resultados, no darla por
  buena: investigar antes de commitear.

### Prototipo / dashboard (sin reentrenar)

Desde la raíz del repositorio, con el entorno activado (ver «Requisitos e instalación»):

```powershell
streamlit run app/app.py
```

Hay que lanzarlo desde la raíz: así Streamlit toma `.streamlit/config.toml`, que fija el tema claro (`base = "light"`). Sin él,
con el sistema en modo oscuro los textos del dashboard casi no se leen sobre el fondo claro del CSS heredado (D80; ver `app/ORIGEN.md`).

Se abre en `http://localhost:8501`. Elegir la pestaña **Predicción (PAA)** (la última de la barra). No hace falta
`data/`, ni bases de datos, ni `.env`, ni reentrenar: la pestaña usa solo archivos versionados.

| Modo | Qué muestra | De dónde lo lee |
| --- | --- | --- |
| Semana posterior al corte | Entorno simulado con corte al 31/12/2025, el último día con datos: cantidad esperada de siniestros registrados por municipio y día, del 01/01/2026 al 07/01/2026, con intervalos del 80 % y 95 %. No es la semana actual y no hay observados para compararla | `models/modelo_final.json` (vía `src/modelo.py`) |
| Histórico | Predicho contra observado, por semana, en el bloque final (06/02/2025 a 31/12/2025). Se muestra tal como está en el archivo, sin recalcular | `experiments/evaluacion_final/predicciones_bloque_final.csv` |

Las demás pestañas son el dashboard heredado del PID (ver `app/ORIGEN.md`): consultan PostgreSQL y MongoDB, que este
repositorio no incluye, así que **muestran su error de conexión**. Es lo esperado y no afecta a la pestaña nueva.

Si falta `models/modelo_final.json` o `predicciones_bloque_final.csv`, la pestaña lo avisa con un mensaje (`git pull`).

### Pipeline previsto

> **Estado (2026-10-21):** el entrenamiento y la evaluación final viven en los notebooks y en `train/`
> (`train/train_modelo_final.py`, ver `train/README.md`); `src/` tiene `datos.py`, `variables.py` y `modelo.py`. Los
> comandos de abajo (`src.data.*`, `src.features.*`, `src.models.*`) son un diseño anterior y **no existen**.

```bash
# 1. Ingesta y consolidación: construye el dataset unificado a partir de las fuentes
python -m src.data.ingesta

# 2. Construcción del dataset temporal: agregación por zona y período,
#    incorporación de variables exógenas (clima cacheado, calendario, feriados) y rezagos
python -m src.features.construir_dataset

# 3. Entrenamiento y evaluación: línea base y modelos candidatos con validación temporal.
#    Guarda métricas y configuraciones en experiments/ y los artefactos en models/
python -m src.models.entrenar

# 4. Inferencia con el modelo ya entrenado (no requiere reentrenar)
python -m src.models.predecir --horizonte 4
```

### Pruebas

```powershell
pytest
```

Incluye las del pipeline de inferencia (`tests/test_pipeline_inferencia.py`), las de la interfaz con
`streamlit.testing` (`tests/test_app.py`) y las del modelo (`tests/test_modelo.py`); el detalle de qué se probó y
qué se encontró está en `documentacion/pruebas_pipeline.md`. Las pruebas con el panel real se saltan si
`data/processed/` no está generado y siempre lo leen por `src.datos.cargar_panel_desarrollo()`, que descarta el
bloque final al leer. Con un clon sin `data/`, las que no necesitan el panel igual corren.

## Resultados esperados

Los resultados se completan de forma acumulativa según avancen los entregables.

**Lo que ya existe (Entregable 2, sobre una única serie — Municipio C, no representativa
del proyecto):** tres líneas base (media constante, promedio de las últimas 4 semanas,
tasa × factor de calendario) y un árbol de decisión como modelo candidato preliminar, con
hiperparámetros fijados a mano, sin selección por validación interna. En el bloque final,
la referencia con calendario (L1) tiene la menor desvianza de Poisson de las cuatro; el
árbol candidato es el peor de las cuatro y no extrapola la tendencia creciente de la
serie. Ese bloque final fue evaluado preliminarmente en el Entregable 2, no es una prueba
reservada e independiente. Detalle completo, tablas y limitaciones en
`experiments/linea_base/` y `documentacion/resumen_linea_base.md`.

**Lo previsto para el Entregable 3** (protocolo de evaluación, todavía no ejecutado):

- **Modelos candidatos.** Dos familias de enfoques: modelos estadísticos clásicos de
  series temporales (por ejemplo SARIMA) y modelos de aprendizaje automático supervisado
  con variables de rezago (por ejemplo modelos de boosting).
- **Estrategias comparadas.** Con y sin variables exógenas, y esquemas de ventana
  expansiva frente a ventana deslizante.
- **Alcance.** El panel completo de 8 municipios, con métricas desagregadas por municipio
  y hold-out dejando un municipio afuera por vez — no la serie única del Entregable 2.
- **Validación.** Particiones que respetan el orden cronológico de los datos; el diseño
  de la evaluación final todavía es una decisión pendiente (ver
  `documentacion/cambios_para_informe.md`).
- **Métricas.** Métricas de error estandarizadas para pronóstico, definidas según las
  características y la distribución de la serie una vez completado el análisis
  exploratorio.

El registro detallado de configuraciones y resultados se mantiene en `experiments/`.

## Equipo y tutoría

- **Integrantes:**
  - Victor Samuel Uría Padilla — victor.uria@estudiantes.utec.edu.uy
  - Juan Lucas Pimentel Barreto — juan.pimentel@estudiantes.utec.edu.uy
- **Docente (asignatura):** Pablo D. Cuña.
- **Tutor (seguimiento del proyecto):** Mag. Matias Leonardo López Pérez — Universidad Tecnológica (UTEC) — matias.lopez@utec.edu.uy

## Uso de inteligencia artificial

El uso de herramientas de IA generativa se registra en
[`documentacion/registro_uso_IA.md`](documentacion/registro_uso_IA.md).

## Referencias

- Deretić, N., Stanimirović, D., Awadh, M. A., Vujanović, N., & Djukić, A. (2022). *SARIMA modelling approach for forecasting of traffic accidents*. Sustainability, 14(8), 4403. https://doi.org/10.3390/su14084403
- Géron, A. (2023). *Aprende Machine Learning con Scikit-Learn, Keras y TensorFlow* (3.ª ed.). Marcombo.
- Hyndman, R. J., & Athanasopoulos, G. (2021). *Forecasting: Principles and practice* (3rd ed.). OTexts. https://otexts.com/fpp3/
- Hyndman, R. J., & Koehler, A. B. (2006). *Another look at measures of forecast accuracy*. International Journal of Forecasting, 22(4), 679–688. https://doi.org/10.1016/j.ijforecast.2006.03.001
- Open-Meteo. *Historical Weather API*. https://open-meteo.com
- UNASEV. (2025). *Informe Anual de Siniestralidad Vial 2025*. https://www.gub.uy/unidad-nacional-seguridad-vial/datos-y-estadisticas/estadisticas/2025-informe-anual-siniestralidad-vial
- UNASEV. (2025). *Modelos SARIMA para la predicción de lesionados en siniestros de tránsito en Uruguay*. https://www.gub.uy/unidad-nacional-seguridad-vial/datos-y-estadisticas/estadisticas/modelos-sarima-para-prediccion-lesionados-siniestros-transito
- World Health Organization. (2023). *Global status report on road safety 2023*. https://www.who.int/publications/i/item/9789240086517
