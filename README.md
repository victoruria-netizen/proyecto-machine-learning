# Predicción de Siniestros Viales — Proyecto de Aprendizaje Automático (PAA)

**UTEC · LIDIA · Proyecto de Aprendizaje Automático 2026**

Este repositorio corresponde al Proyecto de Aprendizaje Automático (PAA), continuación
del Proyecto de Ingeniería de Datos (PID) del mismo equipo. Su objetivo es formular y
resolver un problema de aprendizaje automático relacionado con la **predicción de
siniestros viales**, reutilizando los datos y activos útiles del proyecto anterior.

El problema se aborda como un **pronóstico de series temporales de conteos**: estimar la
cantidad esperada de siniestros registrados por municipio de Montevideo (8 municipios) y día, con un
horizonte de 7 días, a partir de la serie histórica de siniestros de UNASEV. La solución final es un GLM
Poisson que usa solo el municipio y el calendario de 8 niveles (lunes a domingo y feriado): es el
conjunto de variables (a). **No usa clima ni rezagos de la serie**: la lluvia se retiró de la lista de
candidatos antes de ejecutar (decisión del equipo del 14/10/2026; ver `documentacion/resumen_modelos_candidatos.md`,
§1.1). Los resultados se integran en una nueva pestaña del dashboard existente, que muestra sobre un mapa
de los municipios la cantidad esperada de siniestros registrados (ver «Prototipo / dashboard»).

## Proyecto de origen (PID)

- **Repositorio PID:** https://git.utec.edu.uy/juan.pimentel/siniestros-viales-grp4
- **Componentes reutilizados:** Script de extracción, transformación, carga y dataset unificado de siniestros en Uruguay (UNASEV), ya depurado, geolocalizado (coordenadas X/Y y Departamento/Localidad) y trazable; enriquecimiento climático histórico de Open-Meteo previamente cacheado; y el dashboard en Streamlit sobre el que se integró la pestaña de predicción.
- **Modificaciones en el PAA:**
  - ETL adaptado (`notebooks/preparacion_montevideo.ipynb`): produce en `data/processed/` el panel diario por municipio
    (`panel_diario_montevideo.csv`, 8 municipios, 2021-07-01 a 2025-12-31) y los paneles por zona del Entregable 2. La unidad de
    análisis del Entregable 3 es municipio × día.
  - Variables (`src/variables.py`, única implementación compartida por notebooks, pruebas y prototipo): calendario de 8 niveles y
    municipio. La solución final no usa rezagos, nivel reciente ni clima; los rezagos y el nivel reciente se evaluaron en otros
    conjuntos de la validación, y el clima (lluvia) se retiró antes de ejecutar.
  - Módulo de modelado y evaluación con validación temporal: `src/modelo.py` (entrenar, predecir con intervalos del 80 % y 95 %,
    guardar y cargar el modelo en JSON, sin pickle); candidatos GLM Poisson, binomial negativa (para los intervalos) y XGBoost,
    comparados con referencias en 47 cortes de 7 días (`notebooks/modelos_candidatos.ipynb`) y evaluados una vez en el bloque final
    (`notebooks/evaluacion_final.ipynb`).
  - Artefactos de inferencia: `models/modelo_final.json` y `models/metadata.json`. El entrenamiento del modelo final se
    reprodujo en el servidor institucional con `train/train_modelo_final.py`.
  - Dashboard: pestaña «Predicción (PAA)» en `app/`, sobre el código heredado del PID (ver `app/ORIGEN.md`); no usa bases de datos.

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
contenedor con su propio entorno, distinto de este (según el log del job 136: Python 3.10.12, numpy 1.26.4,
pandas 2.3.3, scikit-learn 1.7.2, scipy 1.12.0, sin statsmodels ni `holidays`); ver `train/README.md`. Los notebooks de `notebooks/Ejemplos/` son material de ejemplo pensado para
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
| Open-Meteo — Historical Weather API | Variables meteorológicas históricas (temperatura, precipitación, viento) por ubicación y fecha/hora | API pública con límite de uso; carga histórica puntual ya cacheada, con clave única por latitud, longitud, fecha y hora. La lee el ETL, pero **la solución final no usa variables climáticas** | JSON → CSV cacheado |
| Calendario de feriados de Uruguay | Feriados y días no laborables utilizados como variable exógena | Fuente pública | CSV |

**Variable objetivo y predictoras.** La variable objetivo es la cantidad de siniestros registrados por
municipio de Montevideo y día. La solución final usa el conjunto (a): indicadoras de municipio más el
calendario de 8 niveles (lunes a domingo y feriado). No usa clima ni rezagos de la serie. Los otros
conjuntos que se evaluaron en la validación (con rezagos y nivel reciente) y el motivo del retiro de la
lluvia están en `documentacion/resumen_modelos_candidatos.md`.

**Disponibilidad y versionado.** Los datos de siniestros ya integrados y depurados
provienen del PID. Los archivos de datos no se versionan en este repositorio: `data/`
contiene únicamente la estructura de carpetas y la caché climática se obtiene o se
restaura con `notebooks/preparacion_montevideo.ipynb`. Para reproducir el conjunto de trabajo, ubicar los
archivos fuente en `data/raw/` y ejecutar los notebooks en el orden de la sección «Ejecución», que deja el
panel diario por municipio en `data/processed/`. Para usar el prototipo no hace falta nada de eso.

**Calidad y limitaciones conocidas.** La granularidad (municipio × día) sale del diagnóstico por
municipio (`documentacion/resumen_diagnostico_municipios.md`). La completitud de las variables
climáticas ya no se verifica para la solución, que no las usa. El pipeline utiliza únicamente información
disponible al momento de generar el pronóstico, evitando fugas de información.

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
| 5 | `evaluacion_final` | `data/processed/panel_diario_montevideo.csv` **completo, con el bloque final**; `experiments/modelos_candidatos/solucion_seleccionada.json` y tablas de validación de `experiments/modelos_candidatos/tablas/`; `experiments/diagnostico_municipios/tablas/00_procedencia.csv` | `experiments/evaluacion_final/` (`tablas/`, `figuras/`, `predicciones_bloque_final.csv`, `registro_ejecucion.csv`) y `models/` (`modelo_final.json`, `metadata.json`) |

```powershell
jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=3600 notebooks/preparacion_montevideo.ipynb
```

`--inplace` reemplaza el notebook por su versión con las salidas nuevas. Repetir el comando con
cada notebook de la tabla, en ese orden. Para abrirlos en Jupyter o VS Code, elegir el
intérprete de `.venv` (Python 3.13.2).

**`evaluacion_final` es el único notebook que lee el bloque final** (2025-02-06 a 2025-12-31), además de
`train/train_modelo_final.py` (excepción declarada). Ya está ejecutado y sus salidas están versionadas: **no hace falta reejecutarlo
para usar el prototipo**, que lee solo `models/` y `experiments/evaluacion_final/predicciones_bloque_final.csv`. Si se reejecuta,
sus tablas tienen que reproducir `experiments/evaluacion_final/registro_ejecucion.csv`; `metadata.json` cambia solo en
`commit_base` y `fecha_generacion` (detalle en `documentacion/resumen_evaluacion_final.md`, §1.6 y §5).

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
  `experiments/modelos_candidatos/tablas/00_entorno.csv`, y `evaluacion_final` en
  `experiments/evaluacion_final/tablas/00_entorno.csv`; cada uno registra solo las bibliotecas que
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
con el sistema en modo oscuro los textos del dashboard casi no se leen sobre el fondo claro del CSS heredado (ver `app/ORIGEN.md`).

Se abre en `http://localhost:8501`. Elegir la pestaña **Predicción (PAA)** (la última de la barra). No hace falta
`data/`, ni bases de datos, ni `.env`, ni reentrenar: la pestaña usa solo archivos versionados.

| Modo | Qué muestra | De dónde lo lee |
| --- | --- | --- |
| Semana posterior al corte | Entorno simulado con corte al 31/12/2025, el último día con datos: cantidad esperada de siniestros registrados por municipio y día, del 01/01/2026 al 07/01/2026, con intervalos del 80 % y 95 %. No es la semana actual y no hay observados para compararla | `models/modelo_final.json` (vía `src/modelo.py`) |
| Histórico | Predicho contra observado, por semana, en el bloque final (06/02/2025 a 31/12/2025). Se muestra tal como está en el archivo, sin recalcular. Agrega métricas descriptivas de la semana (desvianza de Poisson, comparada con la referencia L1, y pares fuera del intervalo del 80 %) y el recorrido de las 47 semanas | `experiments/evaluacion_final/predicciones_bloque_final.csv` (la referencia L1 sale del mismo archivo) |

Los dos modos incluyen la descarga de la tabla de la semana en CSV y el panel «Sobre el modelo», que lee `models/metadata.json` y
comprueba en vivo el sha256 de `models/modelo_final.json`. Las métricas son descriptivas y no deciden nada.

Las demás pestañas son el dashboard heredado del PID (ver `app/ORIGEN.md`): consultan PostgreSQL y MongoDB, que este
repositorio no incluye, así que **muestran su error de conexión**. Es lo esperado y no afecta a la pestaña nueva.

**Despliegue en el dashboard del servidor.** La pestaña también corre dentro del dashboard que ya está en el servidor institucional, mediante un puente
(`app/servidor/pagina_prediccion_puente.py`) que carga `app/pagina_prediccion.py` de un clon de este repositorio fijado en un commit. El diagnóstico del
servidor, el diseño, los comandos de instalación y la vuelta atrás están en `documentacion/despliegue_servidor.md`; las pruebas, en `documentacion/pruebas_pipeline.md` (§7).
En el servidor se ve como la pestaña «Predicción (PAA)» del dashboard, con un pie que muestra el commit desplegado («Versión desplegada: `c1c40c3`» el 26/10/2026).

Si falta `models/modelo_final.json` o `predicciones_bloque_final.csv`, la pestaña lo avisa con un mensaje (`git pull`).

### Código de la solución (`src/`, `train/` y prototipo)

- **`src/datos.py`**: `cargar_panel_desarrollo()` lee `data/processed/panel_diario_montevideo.csv` y descarta el bloque final al
  leer, de modo que el código de desarrollo no puede verlo.
- **`src/variables.py`**: variables de la solución y de los otros conjuntos evaluados: calendario de 8 niveles (`tipo_dia`,
  `calendario_8`), nivel del municipio, nivel reciente, rezagos y las matrices de entrenamiento y de horizonte. La solución usa solo
  el municipio y el calendario.
- **`src/modelo.py`**: `entrenar` (GLM Poisson o XGBoost, con α de la binomial negativa para los intervalos), `predecir_semana`
  (56 filas, 7 días × 8 municipios, con la cantidad esperada y los intervalos del 80 % y 95 %), y `guardar_modelo` / `cargar_modelo`
  (JSON, sin pickle). Cargar y predecir no necesitan statsmodels ni xgboost: solo `entrenar` los importa.
- **`train/train_modelo_final.py`**: reentrena la solución con los datos hasta el 2025-12-31 en el servidor institucional
  (`submit_cpu`) y compara con `models/modelo_final.json`. No importa `src/`, porque el contenedor no tiene statsmodels ni `holidays`.
  Instrucciones de envío y evidencia de la corrida en `train/README.md`.
- **Prototipo**: `app/` (ver «Prototipo / dashboard»). Carga `models/modelo_final.json` con `src/modelo.py` y lee las predicciones del
  bloque final; no reentrena nada.

Todo lo anterior es lo que existe hoy. Un diseño anterior de este README proponía comandos `python -m src.data.*`, `src.features.*` y
`src.models.*`: nunca se implementaron y se quitaron.

### Pruebas

```powershell
pytest
```

Incluye las del pipeline de inferencia (`tests/test_pipeline_inferencia.py`), las de la interfaz con
`streamlit.testing` (`tests/test_app.py`) y las del modelo (`tests/test_modelo.py`); el detalle de qué se probó y
qué se encontró está en `documentacion/pruebas_pipeline.md`. Las pruebas con el panel real se saltan si
`data/processed/` no está generado y siempre lo leen por `src.datos.cargar_panel_desarrollo()`, que descarta el
bloque final al leer. Con un clon sin `data/`, las que no necesitan el panel igual corren.

## Resultados

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

**Entregable 3: la solución final en el bloque final** (2025-02-06 a 2025-12-31: 47 cortes de 7 días, 2.632 pares día-municipio,
con reentrenamiento en cada corte). Desvianza de Poisson media, tal como sale de
`experiments/evaluacion_final/tablas/06_globales.csv` (menor valor, menor desvianza):

| Modelo | Papel | Desvianza | Error estándar (47 cortes) | Total predicho / observado |
| --- | --- | --- | --- | --- |
| GLM Poisson (a), ventana deslizante de 364 días | solución | 1,1063 | 0,0335 | 0,9606 |
| XGBoost (a), ventana deslizante de 364 días | contraste | 1,1198 | 0,0341 | 0,9608 |
| GLM Poisson (a), ventana expansiva | sensibilidad | 1,1329 | 0,0355 | 0,8989 |
| L1 (nivel × calendario de 8 niveles) | referencia | 1,1359 | 0,0357 | 0,8952 |
| L0 (8 semanas) | referencia | 1,2432 | 0,0387 | 0,9785 |
| Media constante | referencia | 1,3152 | 0,0401 | 0,8944 |

- **Lo que muestran los datos.** La solución tiene la menor desvianza de los seis modelos. Frente a L1, su diferencia media es
  de −0,0295 y tiene menor desvianza en 33 de los 47 cortes (columnas `dif_vs_su_referencia` y `cortes_que_gana_a_su_referencia` de
  la misma tabla). Esas comparaciones son descriptivas: los 47 cortes son semanas consecutivas de una sola serie y no se fijó una
  prueba de significación (`tablas/09_pareado.csv`). Además, **todos** los modelos, incluida la media constante, tienen menor
  desvianza en el bloque final que en la validación (columna `desvianza_validacion`), así que la mejora respecto de la validación no
  se atribuye a ningún modelo.
- **Configuración elegida.** GLM Poisson (a) con ventana deslizante de 364 días. **Se apartó de la regla de selección** fijada antes de
  ejecutar. La regla había elegido la ventana expansiva: las cuatro ventanas del GLM empataban a menos de un error estándar y la
  expansiva las desempató por el menor desvío entre cortes (0,246353, contra 0,246801 de la segunda, la de 728 días: una diferencia de
  0,00045; la de 364 días tenía 0,249505; `experiments/modelos_candidatos/tablas/29_paso_c_eleccion.csv`). El equipo eligió 364 días
  porque tiene menor desvianza media en validación (1,2205 contra 1,2302; `tablas/26_paso_c_globales.csv`), gana a la expansiva en 30
  de los 47 cortes (`tablas/28_paso_c_por_corte.csv`) y calibra mejor el total (predicho / observado 0,9717 contra 0,9341;
  `tablas/26`). Ninguna de las dos diferencias de desvianza supera un error estándar. La decisión se tomó con la validación y sin leer
  el bloque final; la expansiva quedó como sensibilidad y XGBoost como contraste, sin competir. Detalle en
  `documentacion/resumen_modelos_candidatos.md` (§3e) y en `documentacion/resumen_evaluacion_final.md` (§6, puntos 5 y 8).
- **Evidencia del servidor (job 136, 21/10/2026).** El entrenamiento del modelo final en el servidor institucional, con otra
  implementación (IRLS en numpy, α por momentos) y otras versiones de las bibliotecas, coincidió con `models/modelo_final.json` con
  una diferencia relativa máxima de 4,25e-12 en los coeficientes, 3,42e-12 en las 56 predicciones de la semana del 01/01/2026 y
  5,26e-13 en α (criterio fijado de antemano: ≤ 1e-6, **CUMPLE**); el sha256 del modelo coincide con `models/metadata.json`. Fuente:
  `documentacion/logs/log_servidor_modelo_final.txt` y `documentacion/logs/servidor_modelo_final/resumen_corrida.json`. Verifica que el
  entrenamiento es reproducible, no el desempeño del modelo.
- **Despliegue del prototipo en el servidor (26/10/2026).** El prototipo está desplegado en el dashboard del servidor institucional (puerto 18504)
  desde el 26/10/2026, en el commit `c1c40c3`: la pestaña «Predicción (PAA)» funciona en los dos modos y su pie muestra el commit desplegado. Es un despliegue
  distinto del entrenamiento del job 136 de arriba. Procedimiento, qué se verificó en el servidor y qué no, en `documentacion/despliegue_servidor.md`.
- **Límites declarados.**
  - El bloque final **no es una prueba independiente**: se consultó preliminarmente en el Entregable 2 (aunque la solución se fijó
    antes de la evaluación final, ver `documentacion/resumen_evaluacion_final.md`, §5, puntos 1 y 2).
  - La solución predice el 96,06 % del total observado (subestima), y la meteorología no se evaluó (objetivo 2 incumplido en esa
    dimensión; `tablas/19_cumplimiento_objetivos.csv`).

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
