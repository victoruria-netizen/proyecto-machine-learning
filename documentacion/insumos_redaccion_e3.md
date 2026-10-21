# Insumos para la redacción del informe del Entregable 3 (fase 6)

**Generado:** 2026-10-21, rama `e3/fase-6-informe`. Complementa `documentacion/cambios_informe.md`. Solo lectura de archivos versionados; no se ejecutó nada, no se calculó nada nuevo y no se leyó `data/` ni el bloque final.
**Regla:** lo que no tiene artefacto versionado dice `SIN ARTEFACTO`; no se infirió. Las fechas de commit son las de git (`git log --date=short`); donde la fecha de un archivo y la de su commit difieren, se dice.
**Rutas abreviadas:** `MC##`/`EF##` = `experiments/modelos_candidatos/tablas/##_*.csv` / `experiments/evaluacion_final/tablas/##_*.csv`; `INF` = `documentacion/informe/Informe_PAA_Actualizado_el_12-10-26.md`; `E1` = `documentacion/Entrega1_Proyecto_Aprendizaje_Automatico_08-17-26.md`; `GUIA` = `documentacion/Guia_estudiantes_PAA_2026.md`; `HO` = `HANDOFF.md`; `RMC`/`REF` = `documentacion/resumen_modelos_candidatos.md`/`resumen_evaluacion_final.md`.

---

## 1. Cronología verificable

### 1.1 Períodos (`MC02`, `EF03`)

| Bloque | Desde | Hasta | Días | Fuente |
| --- | --- | --- | --- | --- |
| Período de estudio | 2021-07-01 | 2025-12-31 | 1.645 | `EF03` fila «1.645 días, de 2021-07-01 a 2025-12-31, sin huecos» |
| Desarrollo | 2021-07-01 | 2025-02-05 | 1.316 (987 + 329) | `MC02` |
| Entrenamiento inicial | 2021-07-01 | 2024-03-13 | 987 | `MC02` |
| Validación (47 cortes de 7 días) | 2024-03-14 | 2025-02-05 | 329 | `MC02` |
| Bloque final | 2025-02-06 | 2025-12-31 | 329 | `MC02` («no cargado»); `EF03` fila «bloque final: 329 días» |

- **Primer origen de validación:** 2024-03-14 (`RMC` §1.3). **Último origen de validación:** 2025-01-30 (corte 47, `MC40` columna `desde`; el horizonte termina el 2025-02-05).
- **Primer origen del bloque final:** 2025-02-06 (`REF` §1.4: orígenes 2025-02-06 + 7k). **Último origen del bloque final:** 2025-12-25 (corte 47, `EF18` columna `origen`); el horizonte termina el 2025-12-31 (`EF03`).

### 1.2 Hitos

| Fecha | Hito | Commit o artefacto |
| --- | --- | --- |
| 2026-08-17 | Fecha del documento de la propuesta (E1) | `E1` línea 213 («Rivera, 17 de agosto de 2026»); versionado el 2026-08-28 en `f097e32` |
| 2026-08-24 11:21 | Última modificación del archivo crudo de UNASEV (`uru_siniestros_unificado.csv`, 26,19 MB, sha256 `48a8a7e8…`). **No es una fecha de descarga**: el archivo viene heredado del PID | `experiments/diagnostico_municipios/tablas/00_procedencia.csv`, columna `modificado`. Fecha de descarga: SIN ARTEFACTO |
| 2026-09-04 | Capa de **barrios** descargada (62 polígonos; luego descartada) | `HO` línea 435 («Descargada: 2026-09-04») |
| 2026-09-07 | Capa de **municipios** descargada por WFS (8 polígonos) | `documentacion/resumen_preparacion_montevideo.md` línea 136; `experiments/etl_montevideo/tablas/03b_procedencia_capa_zonas.csv` columna `modificado` = 2026-09-07 12:36 (el diagnóstico registra 13:36 para el mismo archivo y sha256, `00_procedencia.csv`) |
| Sin fecha | Serie de **Open-Meteo** (1.826 días, cacheada en `data/raw/clima_montevideo.csv`, sha256 `f40e6c3c…`) | `HO` línea 492; `INF` Tabla A1. Fecha de descarga: SIN ARTEFACTO |
| 2026-09-18 | Jobs 104 y 108 en el servidor (`train_base.py`, `train_base_2.py`) | `documentacion/logs/log_servidor_base.txt`, `log_servidor_base2.txt` |
| 2026-09-20 | Entregable 2 | `INF` encabezado; `HO` línea 2304; versionado el 2026-09-24 en `74bcfb5` |
| 2026-09-25 | **Última ejecución de `linea_base.ipynb`**, que evalúa en el bloque final (última consulta del bloque final en el E2 con artefacto) | `documentacion/resumen_linea_base.md` línea 7; commits `50df223` y `a261d1d` (2026-09-25) |
| 2026-10-05 (mañana) | Primera versión de `diagnostico_municipios.ipynb`: usó el período completo en las secciones 2 a 6, es decir, **calculó cifras sobre el bloque final**; se corrigió el mismo día. Esa versión **no está en git** | `documentacion/resumen_diagnostico_municipios.md` líneas 10–16. Versión anterior: SIN ARTEFACTO |
| 2026-10-05 | **Corte**: versión corregida (solo desarrollo), ejecutada ese día; la decisión del equipo de no consultar el bloque final desde entonces consta en `HO` (sección «Decisiones del equipo y diagnóstico ampliado», línea 1599) | `resumen_diagnostico_municipios.md` línea 5; `INF` L255, L599. Primer commit que contiene el notebook: `c0681b8` (2026-10-08) |
| 2026-10-14 | Decisión del equipo de retirar el conjunto (d) (lluvia) | Notebook `modelos_candidatos.ipynb`, sección 1, celda 3 en `74eafbd` |
| 2026-10-16 | Sección 1 de `modelos_candidatos.ipynb` y fases 0–1 | `74eafbd` («E3») |
| 2026-10-19 | Adenda, precisiones y pasos A, B y C | `cf76a36`, `2936c72`, `dec597d`, `624b7e3`, `80bedb7`, `2cd97dc`, `5f207e2` |
| 2026-10-19 | `solucion_seleccionada.json` (D42) | `1560a5b`; `EF01` verifica que es su único commit |
| 2026-10-20 | Notebook de evaluación escrito y pusheado **antes** de leer el bloque final | `86630a3` |
| 2026-10-20 19:28:50 | **Primera ejecución completa de `evaluacion_final.ipynb`** | `experiments/evaluacion_final/registro_ejecucion.csv` columna `fecha_hora`; commiteada en `3852498` |
| 2026-10-20 | Informe actualizado al 12/10 subido al repositorio | `24b790e` (el archivo se titula «12-10-26»; la fecha de commit es posterior al 19/10) |
| 2026-10-21 | **Modelo exportado** (`models/modelo_final.json`, `metadata.json`) | `d93cf0c`; versión vigente con fin de línea LF en `6be0383`; fecha de corte de los datos 2025-12-31 (`models/metadata.json`) |
| 2026-10-21 09:27:03 | **Job 135** (primer intento): se detuvo porque no existía el panel; terminó con código 1 | `documentacion/logs/log_servidor_modelo_final_intento1_job135.txt` (líneas 14 y última); no trae hora de fin |
| 2026-10-21 09:44:02–09:44:04 | **Job 136**: cumple el criterio ≤ 1e-6 | `documentacion/logs/log_servidor_modelo_final.txt` líneas 14 y 138; `documentacion/logs/servidor_modelo_final/resumen_corrida.json` |
| — | **Job 137** | SIN ARTEFACTO (ver §7) |
| 2026-10-21 | Prototipo: copia del dashboard, pestaña, pruebas | `d5d1726`, `324fc91`, `935de76`, `5148c0c`; merge `0142520` |
| 2026-10-21 | **Última corrida de `pytest` registrada**: 76 pasadas, 0 fallidas, 0 saltadas (repositorio de trabajo); 66 pasadas y 10 saltadas en clon limpio | `documentacion/pruebas_pipeline.md` §2 (commit `5148c0c`). Hora: SIN ARTEFACTO. En esta sesión `pytest` no se ejecutó (el contenedor no tiene el entorno) |

---

## 2. Población y participantes

### 2.1 Las 11 columnas del registro de UNASEV

- Total: **11 columnas** y **224.694 registros** (`experiments/etl_montevideo/tablas/00_procedencia.csv`; `documentacion/resumen_preparacion_montevideo.md` línea 131). Sin nulos en el archivo salvo 1 en `Calle` (`experiments/diagnostico_municipios/tablas/05b_faltantes_codificados.csv`).
- Nombres que constan en los documentos versionados (`resumen_preparacion_montevideo.md` líneas 161–169; `05b_faltantes_codificados.csv`): `Fecha`, `Hora`, `Dia Semana`, `Departamento`, `Localidad`, `Calle`, `X`, `Y`, `Tipo de Siniestro`, `Gravedad`, `fixed`. Lista completa con orden y tipo: SIN ARTEFACTO en HEAD (el CSV crudo no se versiona).
- **Clasifica el tipo de siniestro:** `Tipo de Siniestro`. **Clasifica la gravedad:** `Gravedad` (`FATAL`, `GRAVE`, `LEVE`, `SIN LESIONADOS`; `resumen_preparacion_montevideo.md` línea 175). **Ninguna columna clasifica el tipo de vehículo ni el tipo de participante** entre las 11 nombradas.
- **Conteos por categoría para el recorte (36.612 hechos): SIN ARTEFACTO.** Los únicos conteos versionados son del **archivo completo (país, 224.694)**, en una tabla que ya no está en HEAD: `experiments/diagnostico_datos/tablas/01b_composicion_descriptiva.csv`, commit `8de1454` (2026-08-31), borrada después. Se copian con esa advertencia (suman 224.694):

| Columna | Categoría | Registros | % |
| --- | --- | --- | --- |
| Gravedad | LEVE | 134.706 | 59,95 |
| Gravedad | SIN LESIONADOS | 63.173 | 28,12 |
| Gravedad | GRAVE | 23.567 | 10,49 |
| Gravedad | FATAL | 3.248 | 1,45 |
| Tipo de Siniestro | COLISIÓN ENTRE VEHÍCULOS | 146.010 | 64,98 |
| Tipo de Siniestro | CAÍDA | 25.942 | 11,55 |
| Tipo de Siniestro | DESPISTE | 25.187 | 11,21 |
| Tipo de Siniestro | ATROPELLO DE PEATÓN | 12.751 | 5,67 |
| Tipo de Siniestro | ATROPELLO DE ANIMALES | 7.987 | 3,55 |
| Tipo de Siniestro | COLISIÓN CON OBSTÁCULO EN CALZADA | 6.792 | 3,02 |
| Tipo de Siniestro | SIN DATOS | 23 | 0,01 |
| Tipo de Siniestro | VUELCO; COLISIÓN CON OBSTACULO EN CALZADA (sin tilde) | 1 y 1 | 0,00 |

- **Choque con el informe:** `INF` L523 y L429 dicen que el registro contiene «todos con personas lesionadas», pero esa tabla da 63.173 registros (28,12 %) con `Gravedad` = `SIN LESIONADOS` en el archivo completo. Para el recorte no hay conteo. Señalado para el equipo; no se corrigió.
- Faltantes codificados en el recorte de Montevideo (`05b`, columna `registros del recorte`): `Localidad` 1.281, `Calle` 663, `Tipo de Siniestro` 10.

### 2.2 Verificación de la Tabla A2 del informe (L867–876) contra su artefacto

Fuente que cita la tabla: `experiments/etl_montevideo/tablas/01_duplicados.csv`, `02_recorte.csv` y `03c_asignacion_zonas.csv`.

| Fila de la Tabla A2 | Cifra del informe | Artefacto | ¿Coincide? |
| --- | --- | --- | --- |
| Registros del archivo original | 224.694 (100,0 %) | `01_duplicados.csv` «registros antes» 224.694 | Sí |
| Tras retener Montevideo | 62.427 (27,8 %) | `02_recorte.csv` «tras filtrar MONTEVIDEO» **62.288** (27,8 %) | **No**: 62.427 no está en ningún artefacto |
| Tras retener las fechas desde el 1.º de enero de 2021 | 39.676 (17,7 %) | SIN ARTEFACTO (`02_recorte.csv` filtra desde 2021-07-01) | **No** |
| Tras excluir el primer semestre de 2021 | 36.713 (16,3 %) | SIN ARTEFACTO | **No** |
| Tras eliminar 90 duplicados exactos | 36.623 (16,3 %) | 36.623 está en `02_recorte.csv`, pero la deduplicación del artefacto es **347 filas sobre el país completo, antes de filtrar** (`01_duplicados.csv`: 224.694 → 224.347) | Cifra sí; «90 duplicados» y el orden de los pasos **no** |
| Tras descartar 11 hechos fuera de todo polígono | 36.612 (16,3 %) | `03c_asignacion_zonas.csv` 36.612 asignados y 11 fuera | Sí |

- El artefacto vigente ordena: 224.694 → (−347 duplicados) 224.347 → Montevideo 62.288 → desde 2021-07-01 36.623 → (−11) 36.612. `resumen_preparacion_montevideo.md` §4 (líneas 227–230) coincide con el artefacto, no con la Tabla A2. `HO` línea 2175 conserva «90 duplicados exactos» de una versión anterior del recorte. Texto de L527 («62.427 registros», «90 duplicados») también discrepa.
- Cifras que sí coinciden: 36.612 siniestros, 13.160 filas, 1.645 días (`EF03`), 8 municipios.

---

## 3. Alcance comprometido (pasajes textuales)

**E1** (`documentacion/Entrega1_Proyecto_Aprendizaje_Automatico_08-17-26.md`, fechado 17/08/2026, commit `f097e32` del 2026-08-28; no hay sección de hipótesis ni de criterios de aceptación; el tutor «recomienda aprobar»):
- L75, pregunta: «El proyecto busca responder: ¿es posible estimar, a partir de la serie histórica de siniestros y de variables exógenas (clima y calendario), la cantidad esperada de siniestros por zona y período?»
- L84, objetivo general: «Desarrollar un modelo de aprendizaje automático para la predicción de siniestros de tránsito a partir de series temporales e integrar sus resultados en una interfaz que permita visualizar las zonas y períodos con mayor cantidad esperada de siniestros.»
- L84, específicos: «Adaptar el proceso ETL del Proyecto de Ingeniería de Datos … Evaluar y comparar estrategias de entrenamiento y validación (con y sin variables exógenas, ventana expansiva y ventana deslizante) mediante métricas de error estandarizadas. Seleccionar el modelo con mejor desempeño y solidez, documentando sus limitaciones y sesgos previsibles. Implementar en el dashboard una nueva pestaña con interfaz gráfica intuitiva que permita visualizar las predicciones y la distribución territorial de la cantidad esperada de siniestros sobre un mapa.»
- L102, validación: «Reservar un tramo temporal final como conjunto de prueba, que no sea utilizado para seleccionar modelos, ajustar hiperparámetros ni tomar decisiones metodológicas.»
- L120, producto: «No se anticipan métricas de desempeño; se documentarán una vez obtenidas durante el desarrollo.» Dentro del alcance: «El modelo predictivo, sus artefactos de inferencia, su evaluación y su incorporación visual como una nueva pestaña del dashboard existente en Streamlit».
- L102, modelado: «Explorar dos familias de enfoques … modelos estadísticos clásicos de series temporales, como SARIMA, y modelos de aprendizaje automático supervisado con variables de rezago, como los de boosting.»
- L139, riesgo con plan alternativo: «Entrenar y evaluar una variante del modelo sin variables meteorológicas».
- L167–170, cronograma: E3 «25/10-26/10»; E4 «15/11».

**Guía** (`documentacion/Guia_estudiantes_PAA_2026.md`, sección 5.3, líneas 422–510; sin fecha propia; los entregables: E3 25 de octubre, E4 15 de noviembre, líneas 156–158):
- L422–427: «El equipo deberá realizar experimentación sistemática, seleccionar una solución con evidencia válida, analizar críticamente sus resultados e integrarla en un prototipo funcional.»
- Resultados esperados (L430–452): comparación de alternativas; «El ajuste y la validación sin utilizar el conjunto de prueba para tomar decisiones»; «La selección de la solución final mediante criterios explícitos y no solo por una única métrica»; «La evaluación final sobre el conjunto de prueba una vez fijada la solución»; comparación con la línea base y cumplimiento de objetivos; explicación e interpretación; análisis de errores, limitaciones, robustez, generalización y sesgos; modelo y artefactos reproducibles; «La comprobación del pipeline de inferencia mediante pruebas»; «Un prototipo integrado, funcional y demostrable de nivel TRL 5».
- Prototipo (L462–474): «no se exige despliegue productivo ni alojamiento permanente»; debe «Incluir instrucciones para ejecutar la solución sin volver a entrenar».
- Evidencias obligatorias (L476–490) incluyen «Informe acumulativo con experimentación, resultados, discusión preliminar y descripción del prototipo» y «constancia del tutor».
- Ponderación del E3 (L496–510, tabla de pesos incluida): 50 % del proceso; metodología 30 %, selección y evaluación final 25 %, análisis crítico 20 %, reproducibilidad 15 %, prototipo 10 %.

---

## 4. Hipótesis previas a los resultados (textos anteriores al 19/10/2026)

Los resultados de validación del E3 se ejecutaron desde el 2026-10-19 (`HO`, «Fase 2, paso A»). Todo lo siguiente se escribió antes.

| N.º | Texto literal | Ruta | Commit y fecha |
| --- | --- | --- | --- |
| H1 | «Un solo modelo con una variable de nivel por municipio es la primera hipótesis a probar; modelos separados por municipio **no están respaldados** por estos datos, con la posible excepción de A, y eso se resuelve primero con un término propio para A dentro del modelo común, no con un modelo aparte.» | `notebooks/diagnostico_municipios.ipynb`, celda 75 | `c0681b8`, 2026-10-08 (ejecución del 2026-10-05) |
| H2 | «Qué probar en el Entregable 3, en este orden: (1) modelo común con variable de nivel por municipio, calculada sólo con entrenamiento y con recalibración; (2) un término propio para A (municipio × día de la semana), midiendo si cierra la brecha sin perjudicar a los otros siete; (3) sólo si no alcanza, un modelo separado para A como desafiante.» | `documentacion/resumen_diagnostico_municipios.md` §8 (líneas 572–575) | `c0681b8`, 2026-10-08 |
| H3 | «El equipo infiere que **un solo modelo con una variable de nivel por municipio** es la primera hipótesis a probar; los datos no respaldan modelos separados, salvo quizá para A, que se abordará primero con un término propio.» | `INF` L731 (archivo titulado «12-10-26») | `24b790e`, 2026-10-20: la fecha de commit es posterior al 19/10; la fecha del archivo es la del título |
| H4 | «Para el Entregable 3, con decisiones tomadas solo sobre la validación interna, se prevé fijar la profundidad y el tamaño mínimo de hoja de los árboles con la desvianza como criterio, revisar la ventana de L0, incorporar el calendario y la tasa del municipio, tratar la deriva de nivel, comparar con familias propias de datos de conteo —la regresión de Poisson y los métodos de conjunto con pérdida de Poisson— y extender la evaluación al panel de ocho municipios … En el panel se probará primero un modelo común con nivel por municipio, estimado solo con entrenamiento y recalibrado; luego un término propio para A y, si no alcanza, un modelo separado … Con los candidatos finales se comparará la ventana expansiva con la deslizante.» | `INF` L821 | `24b790e`, 2026-10-20 (misma salvedad). La versión del E2 (L782 de `Entregable2_PAA_20-09-26.md`) es anterior; `git log` la atribuye a `c0681b8`, 2026-10-08 |
| H5 | «El tercero es que **tratar la deriva de nivel es una condición del modelado**.» Tratamiento: «recalibración del nivel por municipio, ponderación de datos recientes o normalización del objetivo» | `INF` L819 y L741 | `24b790e`, 2026-10-20 (misma salvedad). Cuadro análogo en `Entregable2_PAA_20-09-26.md` L706 |
| H6 | «**Tratar la tendencia creciente** (+11,0 % entre mitades): recalibrar nivel, incluir tendencia o ponderar los datos recientes. Decisión abierta.» «Agregar la variable de nivel de zona … Sigue siendo el bloque más útil fuera de muestra (−7,5 %)» | `HO` sección 4.2, líneas 2249–2252 | Primera aparición del texto `e5b9a04`, 2026-09-07; la sección se reorganizó el 2026-09-25 |
| H7 | «Evaluar el rezago de 1 día como variable candidata … Tratar la tendencia creciente de forma explícita (el árbol candidato no la extrapola).» | `documentacion/resumen_linea_base.md` §6, líneas 224–240 | `c0681b8`, 2026-10-08 (ejecución del 2026-09-25) |
| H8 | «Binomial negativa. Se reporta la dispersión de Pearson del GLM Poisson y el α estimado. Su papel declarado son los intervalos de predicción y la inferencia sobre coeficientes, no mejorar la desvianza.» «Sesgo declarado. La búsqueda de hiperparámetros y la selección usan los mismos 47 cortes; el desempeño del ganador en validación es optimista.» | `notebooks/modelos_candidatos.ipynb`, sección 1 (celda 3) | `74eafbd`, 2026-10-16 |
| H9 | «Cada paso agrega un bloque que el diagnóstico motivó» (conjuntos anidados (0), (a), (b), (c)); conjunto (d) retirado porque «el diagnóstico no le encontró aporte fuera de muestra» | `notebooks/modelos_candidatos.ipynb` sección 1; `RMC` §1.1 | `74eafbd`, 2026-10-16 |

- Ninguno de esos textos fija un umbral cuantitativo de resultado esperado. No hay ninguna hipótesis formulada como tal (`hipótesis nula/alternativa`) en E1 ni en la Guía; la palabra «hipótesis» solo aparece en H1, H3 y en `GUIA` línea 600 («registrar las hipótesis que orientan los experimentos»).
- Salvedad de H3–H5: el informe se subió el 2026-10-20; el texto idéntico de H1 existe desde `c0681b8` (2026-10-08).

---

## 5. Prototipo

**Cómo se ejecuta sin reentrenar** (`README.md` líneas 206–225, commit `5148c0c`, 2026-10-21):
- Desde la raíz del repositorio, con el entorno activado: `streamlit run app/app.py` (bloque `powershell`). Se abre en `http://localhost:8501`; elegir la pestaña **Predicción (PAA)** (la última de la barra). «No hace falta `data/`, ni bases de datos, ni `.env`, ni reentrenar.»
- Clon limpio: `pip install -r requirements.txt -c requirements-lock.txt` (`documentacion/pruebas_pipeline.md` §2); `streamlit run app/app.py --server.headless true` arranca y `/_stcore/health` responde 200.
- Pruebas: `pytest` (`README.md` línea 249).

**Qué muestra cada modo** (`README.md` líneas 217–220):
- **Próxima semana:** cantidad esperada de siniestros registrados por municipio y día, del 01/01/2026 al 07/01/2026, con intervalos del 80 % y 95 %; lee `models/modelo_final.json` vía `src/modelo.py`.
- **Histórico:** predicho contra observado, por semana, en el bloque final (06/02/2025 a 31/12/2025), «tal como está en el archivo, sin recalcular»; lee `experiments/evaluacion_final/predicciones_bloque_final.csv`. Las predicciones son del **reentrenamiento semanal**, no del modelo exportado (`documentacion/pruebas_pipeline.md` §5).
- Las demás pestañas son el dashboard heredado del PID y muestran su error de conexión a PostgreSQL y MongoDB (`README.md` línea 222; D67).

**Procedencia** (`app/ORIGEN.md`): repositorio `https://git.utec.edu.uy/juan.pimentel/siniestros-viales-grp4`, commit de origen `f803bd6` (D66), copiado en `d5d1726`; cambios al código heredado solo en `app/app.py` (3 cambios).

**Capa de municipios** (`app/ORIGEN.md` líneas 42–54): GeoServer de la Intendencia de Montevideo, capa `mapstore-tematicas:zon_v_sig_municipios`, WFS `GetFeature` en GeoJSON EPSG:4326; licencia: el `GetCapabilities` declara `Fees: none` y `AccessConstraints: none`; archivo de partida con sha256 `c5d9f651aa6d88d6ff5bb32b831664b5850b275bfe562bed9e68246492c48d4a`, **distinto** del registrado por el ETL (`ed0ba13e…`, `03b_procedencia_capa_zonas.csv`); simplificada con `simplify(0.0003, preserve_topology=True)` (unos 30 m) y `set_precision(…, 1e-5)`; archivo resultante de 38,8 kB. Sirve para colorear, no para medir.

**Prueba manual y capturas:** fecha de la prueba manual: **SIN ARTEFACTO** (`HO` líneas 2127 y 2146 la dan por pendiente, D63). Capturas de pantalla: **no existen** (ningún `.png` o `.jpg` versionado fuera de `experiments/`).

---

## 6. Desempeño técnico (solo lo registrado)

| Medida | Valor | Fuente |
| --- | --- | --- |
| Job 136 (entrenamiento del modelo final, 4 CPU, 12G) | Inicio 09:44:02, fin 09:44:04 del 21/10/2026 (marcas del log; la duración no está registrada como tal) | `documentacion/logs/log_servidor_modelo_final.txt` líneas 14 y 138 |
| Job 104 (`train_base.py`) | Inicio 12:42:01, fin 12:42:11 del 18/09/2026 | `log_servidor_base.txt` líneas 14 y 268 |
| Job 108 (`train_base_2.py`) | Inicio 13:26:02, fin 13:26:10 del 18/09/2026 | `log_servidor_base2.txt` líneas 14 y 197 |
| Job 135 | Inicio 09:27:03; sin hora de fin | `log_servidor_modelo_final_intento1_job135.txt` |
| Tiempo máximo solicitado por job | 04:00:00 | línea 13 de cada log |
| `modelos_candidatos.ipynb` con `nbconvert` | «unos 16 min» | `HO` línea 1985 (corrida del fix de R2) |
| Seis notebooks del E2 en secuencia | «unos 75 segundos» (2026-09-20) | `README.md` línea 188 |
| Tiempo de inferencia del prototipo o de `predecir_semana` | **SIN ARTEFACTO** | — |
| Tiempo de ejecución de `evaluacion_final.ipynb` | **SIN ARTEFACTO** | — |

---

## 7. Job 137

El log del job 137 **no está versionado**: `git ls-files documentacion/logs` lista solo los logs de los jobs 104, 108, 135 y 136 y los archivos de `servidor_modelo_final/` (job 136), y `grep` de «137» en `documentacion/logs/`, `train/README.md` y `HANDOFF.md` no lo menciona como job. La observación de «dos versiones instaladas de numpy, pandas y scikit-learn» queda **SIN ARTEFACTO**.

---

## 8. Figuras (dimensiones leídas del encabezado PNG, tamaño en bytes)

| Figura | Existe | Píxeles (ancho × alto) | Bytes |
| --- | --- | --- | --- |
| `experiments/modelos_candidatos/figuras/fig7_coeficientes_glm.png` | Sí | 1199 × 458 | 43.674 |
| `experiments/evaluacion_final/figuras/fig1_desvianza_por_corte.png` | Sí | 1303 × 484 | 139.812 |
| `experiments/evaluacion_final/figuras/fig4_calibracion_y_residuos.png` | Sí | 1309 × 451 | 137.072 |
| `experiments/evaluacion_final/figuras/fig5_cobertura_intervalos.png` | Sí | 1309 × 407 | 47.383 |

---

## 9. Otras discrepancias halladas al leer (para el equipo; sin corregir)

- `README.md` líneas 261–292 («Resultados esperados»: «Lo previsto para el Entregable 3 … todavía no ejecutado», SARIMA y boosting con rezagos, hold-out de un municipio) **sigue describiendo el E3 como futuro**; el E3 ya se ejecutó.
- `INF` L523: «todos con personas lesionadas» contra §2.1 de este documento.
- Tabla A2 contra su artefacto (§2.2).
- La fecha de commit del informe (`24b790e`, 2026-10-20) es posterior al 19/10; solo el título del archivo («12-10-26») ubica sus textos antes de esa fecha (§4).
- `experiments/diagnostico_municipios/tablas/00_procedencia.csv` y `etl_montevideo/tablas/03b_procedencia_capa_zonas.csv` dan horas distintas (13:36 y 12:36) para la misma capa y el mismo sha256.
