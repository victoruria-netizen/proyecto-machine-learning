# Cambios al informe — insumo para la redacción (Entregable 3, fase 6, D64)

**Informe vigente:** `documentacion/informe/Informe_PAA_Actualizado_el_12-10-26.md`. Las `L<n>` son líneas de ese archivo y cambian si se edita.
**Generado:** 2026-10-21, rama `e3/fase-6-informe`. **No es texto para pegar:** son hechos, con su artefacto y su ID de decisión, para redactar en Claude web.
**No distinguir con** `documentacion/cambios_para_informe.md`: ese es el documento del E2 (diagnóstico recalculado); el informe vigente ya lo incorpora (p. ej. 21,42 % y 19,94 % en L533).
**Qué se leyó:** el informe vigente, `resumen_modelos_candidatos.md`, `resumen_evaluacion_final.md`, `pruebas_pipeline.md`, `app/ORIGEN.md`, `HANDOFF.md`, los otros resúmenes (solo sus frases prohibidas) y las tablas ya commiteadas de `experiments/`. **No se ejecutó ningún notebook ni se leyó el bloque final** (ni `data/`, ni `predicciones_bloque_final.csv`): las cifras del bloque final salen de `ef/` ya commiteado.

## 0. Cómo usar este documento

1. **Ninguna cifra sin artefacto.** Cada cifra lleva el código de su fuente (tabla de abajo) y, si hace falta, la fila o columna. Lo que no tiene artefacto versionado está marcado `<!-- SIN ARTEFACTO -->`.
2. **Evidencia ≠ inferencia.** En las secciones nuevas: «Los datos muestran» (lo que dice la tabla) y «Lectura del equipo» (inferencia **ya rotulada en los resúmenes como a validar**; el equipo la valida o la reescribe).
3. **No redactar Introducción ni Marco teórico** a partir de este documento: lo que toca a esas secciones va solo en §5, para el equipo.
4. Cuando algo choca con otra fuente, se dice (§5 y §7). Nada se resolvió por cuenta propia.

**Aviso sobre IDs.** D2 («ajuste congelado»), D4 (árbol retirado), D14 (lluvia excluida) y D69 (despliegue en el servidor) **vienen de la tabla de cambios del prompt de la fase**: `grep` no los encuentra definidos en ningún archivo versionado (D17 a D20, D27 a D29, D31 a D40, D42 a D45, D48 a D58, D60 a D68 y D70 sí están). Se citan tal como se dieron; el equipo debe confirmar su contenido o escribirlos en `HANDOFF.md` antes de citarlos en el informe. En los archivos, la exclusión de la lluvia consta como «decisión del equipo, 2026-10-14» (RMC §1.1) y el árbol como «retirado antes de ejecutar».

### Códigos de fuente

| Código | Ruta |
| --- | --- |
| `MC##` | `experiments/modelos_candidatos/tablas/##_*.csv` (p. ej. `MC26` = `26_paso_c_globales.csv`) |
| `EF##` | `experiments/evaluacion_final/tablas/##_*.csv` (p. ej. `EF06` = `06_globales.csv`) |
| `MCF##`, `EFF##` | `experiments/modelos_candidatos/figuras/fig##_*.png`; `experiments/evaluacion_final/figuras/fig##_*.png` |
| `SOL` | `experiments/modelos_candidatos/solucion_seleccionada.json` |
| `REG` | `experiments/modelos_candidatos/registro_experimentos.csv` (38 filas) |
| `META`, `MOD` | `models/metadata.json`, `models/modelo_final.json` |
| `RMC`, `REF`, `PIP` | `documentacion/resumen_modelos_candidatos.md`, `resumen_evaluacion_final.md`, `pruebas_pipeline.md` (con §) |
| `ORI` | `app/ORIGEN.md` |
| `HO` | `HANDOFF.md` |
| `L136`, `RC136` | `documentacion/logs/log_servidor_modelo_final.txt`; `documentacion/logs/servidor_modelo_final/resumen_corrida.json` |
| `INF` | el informe vigente (`L<n>`) |

Cifras de `RMC`/`REF` que no están en una tabla (por ejemplo, la verificación de fuga) se citan con su sección: son verificaciones del código, no resultados.

---

## 1. Secciones del informe vigente que cambian

### 1.1 Sección 2.3.4 — Árboles de decisión (L479–483) · Quién: Equipo

**Hoy dice:** (L481) el modelo base es un árbol con el criterio por omisión; (L483) se eligió un árbol único y no conjuntos, por explicabilidad, y los métodos de conjunto «se señalan como trabajo futuro».
**Tiene que decir:** el candidato aprendido del E3 es XGBoost con pérdida Poisson; el árbol único se retiró (D4).
**Hechos:**
- Árbol retirado **antes de ejecutar** candidatos (D4); motivo de la sección 1 del notebook: en el E2 no extrapoló la tendencia (RMC §1.1, fila «Árbol de decisión»; `INF` L811: árbol B subestima 28 %).
- Candidato: XGBoost `objective="count:poisson"`; paso A con `max_depth=3`, `n_estimators=300`, `learning_rate=0,05` (D19); resto, valores por defecto de xgboost 3.4.1, `random_state=20260910`, `n_jobs=1` (RMC §1.1; `SOL`, campo `semilla`; `MC00`).
- Paso B, grilla de 12 combinaciones (`max_depth` {2, 3, 4} × `n_estimators` {100, 300} × `learning_rate` {0,05; 0,1}): mejor en desvianza `d=4 n=300 lr=0,05`, **1,2197**; la regla eligió la más simple (D37), `d=2 n=100 lr=0,1`, **1,2375**, por encima de L1 (**1,2319**) (`MC18`, columna `desvianza`).
- XGBoost es **contraste** en la solución final y no compite (D42, D48): deslizante 364 d, **1,2280** en validación (`MC26`) y **1,1198** en el bloque final (`EF06`, fila «contraste»).
- Ningún candidato del E3 usa tiempo transcurrido (`t_anios`): los conjuntos (0), (a), (b) y (c) no lo tienen (RMC §1.1). La extrapolación de la tendencia no se evaluó con árboles en el E3.
- Fuente de XGBoost: la aporta el equipo (ver 1.9).

### 1.2 Sección 2.3.2 — Respuesta al Comité (L473) · Quién: Equipo

**Hoy dice:** «La lista de modelos y variantes … quedará cerrada antes de comenzar esa comparación».
**Tiene que decir:** que se cerró antes de comparar, y cuál fue.
**Hechos:**
- **Lista cerrada de candidatos:** GLM Poisson, GLM binomial negativa (NB2) y XGBoost `count:poisson` (RMC §1.1, fila «Candidatos»). **Referencias:** media constante, L0 y L1. **Retirados antes de ejecutar:** árbol de decisión (D4) y el conjunto (d) con lluvia (D14). SARIMA/SARIMAX no se evaluó (`INF` L473).
- **Orden verificable en git:** sección 1 del notebook en `74eafbd` (2026-10-16, mensaje «E3»); adenda previa a candidatos en `cf76a36`; precisiones de la fase 2 en `2936c72`, del paso B en `624b7e3`, del paso C en `2cd97dc`; candidatos ejecutados desde el 2026-10-19 (HO, «Fase 2, paso A»).
- **Matices que el informe debe declarar:** (i) la review R1 halló que la sección 1 no coincidía con la lista del plan en «L0 de 8 semanas» y «NB2»; se resolvió con adenda (D17, D27), sin tocar la sección 1 (HO, «review R1»); (ii) la L0 de 8 semanas se eligió **mirando los 47 cortes de validación** (D17; `MC05`); (iii) git no prueba que la sección 1 precediera a la ejecución de las referencias: las fases 0 y 1 se commitearon juntas en `74eafbd` (riesgo R1 abierto en HO).
- Tamaño de la comparación: 38 configuraciones evaluadas (16 del paso A, 13 del B, 8 del C y NB2 364 d) (`REG`, columna `paso`: A 16, B 13, C 8, «3c» 1).

### 1.3 Sección 3.4.2 — Variables (L539–551) · Quién: Claude

**Hoy dice:** tres bloques (historia con rezagos 1, 7, 14, 21 del árbol; calendario de tres niveles; meteorología sin uso); «la tasa histórica de cada municipio … se incorporará en el Entregable 3».
**Tiene que decir:** calendario de 8 niveles derivado de la fecha, nivel del municipio, nivel reciente, rezagos de 7 días o más; lluvia excluida por no estar disponible al predecir (D14).
**Hechos:**
- **Calendario de 8 niveles:** lunes a domingo + `feriado`, derivado de `fecha`; el feriado **tiene prioridad** sobre el día de la semana (`src/variables.py`: `calendario_8`, `NIVELES_CALENDARIO`). Para fechas dentro del panel el feriado sale de `tipo_dia` del ETL; para fechas fuera, de `var.tipo_dia` con `holidays` y categorías `("public", "bank")` (D50). `var.tipo_dia` coincide con el del ETL en los 1.316 días de desarrollo (REF §1.3).
- **Nivel del municipio:** media de cada municipio en la ventana de entrenamiento (constante por municipio); en el GLM, 8 indicadoras de municipio **sin constante** (D31).
- **Nivel reciente:** media de los últimos N ∈ {28, 56, 91} días antes del origen, fijo para los 7 días del horizonte; solo en los conjuntos (0) y (c) (D18; RMC §1.2).
- **Rezagos:** `y(d − k)`, k ∈ {7, 14, 21, 28}; siempre observados con horizonte de 7 días: la función falla si un rezago cae en el origen o después, no hay recursión (RMC §1.2). El rezago de **1 día no se evaluó** en el E3.
- **Conjuntos anidados:** (0) municipio + log(nivel reciente) + rezagos; (a) municipio + calendario; (b) (a) + término propio de calendario para A; (c) (b) + nivel reciente (RMC §1.1; D34).
- **La solución final usa el conjunto (a):** 15 columnas, 8 de municipio y 7 de calendario (lunes de referencia); **sin nivel reciente ni rezagos** (`SOL`, `solucion.conjunto_de_variables.columnas`).
- **Lluvia excluida (D14),** conjunto (d) retirado antes de ejecutar (2026-10-14): (i) la lluvia del día a predecir no está disponible con horizonte de 7 días; (ii) el diagnóstico no le encontró aporte fuera de muestra: −0,36 % y −0,01 % (`INF` L725; RMC §1.1). **No se probó en el E3** (RMC §5). La serie meteorológica sigue en el conjunto preparado y ningún modelo la usa.
- **Evidencia sobre los bloques:** el conjunto (0) (rezagos + nivel reciente, sin calendario) es peor que L1 en las dos familias (`MC11`, `diferencia_vs_L1` entre +0,0438 y +0,0581 → frase «los rezagos semanales aportan» prohibida, §6).
- **Construcción de filas de entrenamiento:** bloques de 7 días alineados hacia atrás desde el origen; mismas filas para todos los conjuntos (se descartan los primeros ~91 días); el nivel del municipio incluye el objetivo de entrenamiento en su media (RMC §1.2).
- **Pruebas:** `tests/test_variables.py`, 15 pasan: con el objetivo futuro reemplazado por un valor imposible las variables no cambian; con la compuerta abierta, fallan 5 (RMC §1.2).
- **Rezagos del árbol (1, 7, 14, 21)** y la ACF del Municipio C (L543): pertenecen al E2; el árbol está retirado (D4).
- **L551** («se incorporará en el Entregable 3»): ya incorporado (nivel del municipio) con entrenamiento solamente.

### 1.4 Sección 3.4.3 — Evaluación (L553–583) · Quién: Claude

**Hoy dice:** Tabla 1 con «Validación por origen móvil (ventana expansiva)»; L567: la evaluación del bloque final reproduce el esquema «con el ajuste congelado en el desarrollo»; la validación de los modelos sin exógenas «se hará en el Entregable 3».
**Tiene que decir:** panel de 8 municipios; reentrenamiento semanal también en el bloque final, en lugar de «ajuste congelado» (D2); ventanas.
**Hechos:**
- **Panel:** 8 municipios, 47 cortes × 56 filas = **2.632** pares día-municipio por modelo, en validación y en el bloque final (`MC05`, `n`; `EF06`).
- **Particiones** (sin cambio): 987 días de entrenamiento inicial, 329 de validación, 329 del bloque final (`MC02`, columna `dias`; `EF03`).
- **Reentrenamiento semanal en el bloque final (D2):** 47 cortes de 7 días, orígenes 2025-02-06 + 7k, el último horizonte termina el 2025-12-31 (`EF03`, fila «47 cortes»). En cada corte cada modelo se **reentrena** con todo lo observado antes del origen (desarrollo + semanas transcurridas) y su ventana; el objetivo de los días ≥ origen no llega al modelo (vista con NaN) (REF §1.4, D48 y D52). Motivo: es el procedimiento de la validación (`SOL`, `reentrenamiento_cada_dias` = 7) y el del uso previsto. «Ajuste congelado» (L567, L608) describe el protocolo del E2 (REF §6, punto 1).
- **Ventanas:** en validación se evaluaron expansiva y deslizante de 364, 546 y 728 días (`MC26`); la solución final usa **364 días** y la expansiva queda como sensibilidad (D42). Las referencias usan expansiva.
- **Filas de entrenamiento por corte** en el paso A (expansiva): de **7.168** a **9.744** (`MC16`, columna `filas_entrenamiento`). Primer origen de validación: 2024-03-14 (RMC §1.3).
- **Métricas:** desvianza de Poisson media (principal, EPS = 1e-6, `RMC` §1.3), error estándar sobre los 47 cortes (desvío ddof=1 ÷ √47), MAE, RMSE, total predicho/observado, días con predicción cero, desvío entre cortes, peor municipio (`MC08`, `EF06`). Nuevas respecto del E2: calibración por deciles (`EF14`), tendencia del residuo (MCO con EE HAC de Newey-West, 4 rezagos; `EF16`) y cobertura de intervalos **contra la esperada por el modelo** (`EF17`). L451 dice que la calibración «queda para el Entregable 3»: se hizo.
- **Comparaciones pareadas** corte a corte: **descriptivas**, posteriores a ver los resultados (D35, D52 ítem 4); no son pruebas (`EF09`, `MC47`).
- **Control del motor:** reproduce `linea_base` en el Municipio C con diferencias < 0,0001 (`MC04`, columna `diferencia`; `RMC` §1.4); 35 comprobaciones en validación antes de leer el bloque final, diferencia máxima 5e-7 (`EF02`; REF §1.4).
- **Sesgo declarado:** la búsqueda de hiperparámetros y la selección usan los mismos 47 cortes; la validación del ganador es optimista (RMC §1.1).
- **Se mantiene del E2** el control cruzado de L583 (1,2625 y 1,2620): es de la serie del Municipio C.

### 1.5 Cuadro 3 — Medidas contra la fuga (L603–614) · Quién: Claude

**Hoy dice:** seis filas del protocolo del E2 (ajuste congelado; árbol recursivo; rezagos 1, 7, 14, 21).
**Tiene que decir:** dos notebooks, carga con recorte y `assert`, configuración commiteada antes de leer el test.
**Hechos por fila:**
- **Fila «Estimar parámetros con información futura» (L608):** reemplazar «ajuste congelado» por reentrenamiento en cada corte con la ventana del modelo (D2; ver 1.4).
- **Fila «Realimentar predicciones» (L609):** ningún modelo del E3 es recursivo; los rezagos son ≥ 7 días y la función falla si no son anteriores al origen (RMC §1.2). La solución (a) no usa rezagos.
- **Fila «Dar a un modelo variables que no debe usar» (L610):** las variables salen solo de `src/variables.py` (única implementación, compartida con el prototipo) y la solución usa 15 columnas (`SOL`).
- **Fila nueva, «Dos notebooks»:** `notebooks/modelos_candidatos.ipynb` **nunca** carga el bloque final; `notebooks/evaluacion_final.ipynb` es el **único** que lo lee, más `train/train_modelo_final.py` como excepción declarada (D51) (REF §0 y §4.2). En cualquier otro código el panel entra por `src/datos.py:cargar_panel_desarrollo()`.
- **Fila nueva, «Carga con recorte y `assert`»:** el CSV se lee por tramos y cada tramo se recorta a `fecha <= 2025-02-05` **antes de acumularse**; `assert` de que no sobrevive ninguna fila posterior, de 8 municipios, 1.316 días × 8 y sin pares repetidos (`src/datos.py`). El límite sale del calendario (80 % de 1.645 días), no de los datos. Verificado: 10.528 filas = 1.316 × 8 (RMC §2; `MC01`).
- **Fila nueva, «Configuración commiteada antes de leer el test»:** `SOL` en `1560a5b` (2026-10-19), sin cambios después; el notebook de evaluación se commiteó y pusheó en `86630a3` (2026-10-20) **antes** de ejecutarse; primera ejecución completa 2026-10-20T19:28:50, commiteada en `3852498` (D53). `EF01` verifica 6 puntos: el JSON tiene un único commit y es `1560a5b`; árbol idéntico a ese commit; es antecesor de HEAD; todo commit del notebook es posterior; `bloque_final_leido = false`; decisión D42.
- **Fila nueva, «El modelo no ve el futuro»:** vista con el objetivo de los días ≥ origen en NaN, comprobada con un «modelo sonda» (`MC03`). Verificación de fuga **fuera del repo**, sin artefacto: objetivo futuro alterado a 10⁶, diferencia máxima entre predicciones **0** en 20 combinaciones (4 configuraciones × 5 cortes) en el paso A y otra vez en 3a; con la compuerta abierta, el control GLM (c) cambia entre 11,41 y 44,86 (RMC §3b.7 y §3e.4) `<!-- SIN ARTEFACTO: verificación del código, no resultado -->`.
- **Fila «Usar el bloque final para ajustar parámetros» (L611) y «Elegir … con información del bloque final» (L612):** el riesgo del E2 **sigue declarado**; en el E3 las decisiones se tomaron con validación. D42 se tomó **después de ver el paso C y con los mismos 47 cortes** (RMC §5).
- **Texto de L589–599 (uso del bloque final):** agregar que la evaluación final se hizo **una sola vez**; las reejecuciones reprodujeron el registro con diferencia relativa máxima de **2,51e-15** (REF §1.6); `registro_ejecucion.csv` conserva `arbol_limpio = False` (explicado en REF §1.6; en `META`, `fuentes_limpias` = true); `predicciones_bloque_final.csv` versiona los conteos observados del bloque final (D65, confirmado por el equipo el 21/10/2026).

### 1.6 Sección 3.4.5 y Cuadro 4 (L616–636) · Quién: Claude

**Hoy dice:** L0 = promedio de las últimas cuatro semanas «fijada antes de ejecutar»; L1 con tres niveles; Cuadro 4 con árboles A y B, repetir la semana anterior y media móvil de 56 días.
**Tiene que decir:** lista nueva; L0 de 8 semanas (D17); árbol retirado (D4).
**Hechos:**
- **Referencias del E3:** media constante (global); **L0** = promedio de `y(d − 7j)`, j = 1…N semanas (`modelo_L0` en el notebook, `lags = 7·j`); **L1** = nivel del municipio × factor de calendario de 8 niveles (el M2 del diagnóstico).
- **L0 de 8 semanas (D17):** desvianza **1,3626** (8 sem.), **1,5210** (4 sem., la del E2), **2,4384** (2 sem.); media constante **1,3967** (`MC05`, `desvianza_poisson`). La de 8 semanas queda por debajo de la media constante por 0,0341 (diferencia de dos celdas de `MC05`; `RMC` §1.1, adenda ítem 1), **menos de 1 EE** (0,0447, `MC08`, `error_estandar_47_cortes`). La L0 de 4 semanas queda **por detrás** de la media constante. L0 de 2 semanas: **27** predicciones cero (`MC05`, `dias_prediccion_cero`).
- **L1 en el panel:** 1,2319, EE 0,0358 (`MC08`); es la mejor referencia, no el mejor modelo.
- **Candidatos evaluados:** GLM Poisson (a) deslizante 364 d (**solución**); GLM Poisson (a) expansiva (**sensibilidad**); XGBoost (a) d=2 n=100 lr=0,1 deslizante 364 d (**contraste**, no compite); NB2 (a) 364 d solo para intervalos (no compite) (D42, D44, D48).
- **Se retiran del Cuadro 4:** árbol A y árbol B (D4); «repetir la semana anterior» y «media móvil de 56 días» (REF §6, punto 7: D48 fijó las referencias del bloque final); L0 de cuatro semanas.
- **L620** («L1 usa los tres niveles»): en el E3 son 8 (REF §6, punto 4).
- **Decisión que queda al equipo:** las Tablas 4 y 5 (una serie, árboles, ajuste congelado) siguen siendo del E2; conservarlas como antecedente, moverlas a anexo o retirarlas.

### 1.7 Sección 3.4.6, Anexo F.1 y corrida en el servidor (L638–648, L1107) · Quién: Claude

**Hoy dice:** L648: el contenedor del servidor tiene Python 3.10.12, pandas 1.5.3, scikit-learn 1.2.0 y «las cifras provienen de las corridas locales»; L642: entorno único con Python 3.13.15 y 17 dependencias directas. El Anexo F.1 documenta solo `train_base.py`.
**Tiene que decir:** las versiones del log del job 136; no pandas 1.5.3.
**Hechos:**
- **Job 136** (`grp04_cpu_train_modelo_final`, RUN_ID `20261021_094404`, 21/10/2026, 4 CPU, 12G): Python **3.10.12**, numpy **1.26.4**, pandas **2.3.3**, scikit-learn **1.7.2**, scipy **1.12.0**, **sin statsmodels ni `holidays`** (`L136`, línea 36; `RC136`).
- **Job 137:** muestra que el contenedor tiene instaladas **dos versiones** de numpy, pandas y scikit-learn; D56 suponía pandas 1.5.3 (versiones del 18/09, job 104, `log_servidor_base.txt`). **El log del job 137 no está versionado** `<!-- SIN ARTEFACTO: el equipo debe commitear el log del job 137 en documentacion/logs/ antes de citarlo -->`.
- **El resultado no cambia:** el modelo entrenado en el servidor (IRLS en numpy, α por momentos, calendario constante) coincide con la exportación local: diferencia relativa máxima **4,25e-12** en coeficientes, **3,42e-12** en μ de las 56 filas y **5,26e-13** en α, contra un criterio de ≤ 1e-6 (D56: CUMPLE) (`RC136`; `L136` líneas 129–132). Los sha256 del panel y del modelo coinciden.
- **Qué prueba y qué no:** el entrenamiento es reproducible con otra implementación y otro entorno; **no evalúa** desempeño (REF §4.3, punto 8).
- **Job 135** (intento fallido): el panel figuraba como inexistente porque la carpeta se subió como `processed ` (con un espacio al final); no entrenó (`documentacion/logs/log_servidor_modelo_final_intento1_job135.txt`).
- **Entorno local del E3:** Python **3.13.2** y **18** dependencias directas en la fase 4 (`EF00`; REF §6, punto 9); hoy `requirements.txt` tiene 25 pines por las 7 dependencias de `app/` (HO, fase 5). El informe dice 3.13.15 y 17: el README documenta que 3.13.15 no existe (`README.md`, líneas 46–49).
- **Anexo F.1:** agregar `train/train_modelo_final.py` (job 136) y el intento job 135; las instrucciones de envío están en `train/README.md`.

### 1.8 Glosario (L243–307) · Quién: Claude

**Entradas nuevas — hechos para definirlas:**
- **GLM Poisson:** `statsmodels.api.GLM(..., family=Poisson())`, enlace log, IRLS por defecto, sin regularización y sin constante (`SOL`, `solucion`).
- **Binomial negativa (NB2):** varianza μ + αμ², α por máxima verosimilitud en cada corte (`NegativeBinomial`, `loglike_method="nb2"`, método `newton`, `maxiter=100`; D27, D29); plan B: α por momentos (D28). En el E3 sirve para intervalos y para inferencia de coeficientes, no para mejorar la desvianza (RMC §1.1, fila «Binomial negativa»).
- **XGBoost:** `objective="count:poisson"`, xgboost 3.4.1 (`MC00`).
- **Importancia por permutación:** en cada corte se permutan juntas las columnas de un grupo (municipio, 8 columnas; calendario, 7) entre las 56 filas del horizonte y se recalcula la desvianza; 5 repeticiones con `np.random.default_rng(SEMILLA)` (RMC §3f.1; `MC36`).
- Candidatas: error estándar de la desvianza (47 cortes); cobertura empírica y **cobertura esperada por el modelo** (REF §3.4); ventana deslizante (el glosario solo define la expansiva); sensibilidad y contraste (roles de D42).
- **Entrada vigente a corregir:** «Bloque final» (L255) dice que «se reserva para la evaluación final»: ya se evaluó (REF §2.1).

### 1.9 Referencias (L823–849) · Quién: Equipo

- Solo fuentes consultadas por el equipo, APA 7. **Claude no agrega ni inventa referencias.**
- Fuentes que **el equipo aporta si las cita**: XGBoost, binomial negativa (NB2), α por momentos (los archivos mencionan «Cameron y Trivedi, 1990», RMC §1.1 fila 5, sin más datos), errores HAC de Newey-West, importancia por permutación, IRLS.
- Recursos de terceros que el informe debe identificar: dashboard del PID (repositorio `git.utec.edu.uy/juan.pimentel/siniestros-viales-grp4`, commit `f803bd6`, `ORI`); capa `mapstore-tematicas:zon_v_sig_municipios` (Intendencia de Montevideo; `Fees: none`, `AccessConstraints: none`, `ORI`); statsmodels 0.14.6, xgboost 3.4.1 (`MC00`); streamlit 1.65.0, plotly 7.1.0, pydeck 0.9.3 (HO, fase 5).

### 1.10 Discusión preliminar y conclusiones · Quién: borrador de Claude, reescritura del equipo

**Cumplimiento de objetivos** (`EF19`, estados fijados **antes** de leer el bloque final, D52 ítem 8):
- Obj. 1 (ETL): cumplido en el E2.
- Obj. 2 (estrategias, exógenas y ventanas): **cumplido en calendario y ventanas; no cumplido en meteorología** (conjunto (d) retirado).
- Obj. 3 (seleccionar con solidez): **cumplido en el procedimiento, con la salvedad de D42**.
- Obj. 4 (pestaña del dashboard): `EF19` dice «no cumplido en esta fase»; **la fase 5 lo implementó** (§2.5). Actualizar el estado con `PIP`; la prueba manual en el navegador (D63) queda pendiente del equipo.
- Cifras de respaldo (`EF06`): solución **1,1063**, L1 **1,1359**, media constante **1,3152**; solución − L1 **−0,0295** (gana 33 de 47).

**Limitaciones:** ver §4. **Trabajo futuro** (hechos que lo sostienen, no propuestas):
- Meteorología: exigiría un pronóstico a 7 días (HO, «Lluvia en el prototipo»).
- Nivel creciente: la solución sigue subestimando (0,9606; `EF06`); qué explica el resto de la subestimación no se investigó (RMC §3b.6).
- Exposición y subregistro: sin resolver (INF 4.1.4).
- Generalización a otros departamentos o a datos de 2026: no evaluada (REF §5). El primer semestre de 2026 de UNASEV no se descargó (L601).
- Mapa y gráficos del prototipo: sin verificación visual automática (`PIP` §5).
- Cobertura de intervalos: sin incertidumbre asociada (RMC §5).

### 1.11 Otros cambios por arrastre (no están en la tabla del prompt; confirmar)

- **L658** («resultados del segundo hito»): el capítulo 4 pasa a incluir E3. **L821** («Para el Entregable 3 … se prevé … fijar la profundidad de los árboles …»): ahora hay resultados; el párrafo se reemplaza.
- **L451, L551, L567:** frases prospectivas que el E3 cumplió o cambió (ver 1.3 y 1.4).
- **Tabla 1 (L563):** «Bloque final (evaluado preliminarmente en E2)» → agregar «evaluación final del E3 (una vez)».
- **3.5 Aspectos éticos:** D65 (versionar los conteos observados del bloque final, confirmado por el equipo). El resto del texto no cambia.
- **L169** (índice): «Anexo F – Entorno, reproducibilidad y ejecución en el servidor» no coincide con el título real (L1042: «Resultados complementarios de la línea base»).
- **Tablas F1–F4 e Ilustraciones F1–F2** (árbol B): describen el E2; decisión del equipo (conservar como antecedente).

---

## 2. Secciones nuevas de resultados

Numeración propuesta: 4.4 Experimentación; 4.5 Solución seleccionada y regla; 4.6 Evaluación final; 4.7 Análisis crítico y explicabilidad; 4.8 Prototipo y pruebas; 5 Discusión; 6 Conclusiones. **Confirmar con la guía institucional de informes** (CLAUDE.md: no asumir formato).

### 2.1 Experimentación (pasos A, B y C) — respaldo `RMC` §3 a §3d, tablas `MC05` a `MC31`, `REG`

**Qué se hizo:** referencias (sección 1 del notebook), paso A (conjuntos de variables con GLM Poisson y XGBoost, ventana expansiva), paso B (grilla de XGBoost y NB2), paso C (ventanas). Un solo protocolo, 47 cortes (RMC §1.3, §2).

**Los datos muestran — referencias (`MC05`, `MC08`):**
- L1 **1,2319** (EE 0,0358), L0 8 sem. **1,3626**, media constante **1,3967** (EE 0,0447), L0 4 sem. **1,5210**, L0 2 sem. **2,4384**.
- L1 es el único dentro de 1 EE de sí mismo (`MC08`, `a_menos_de_1_ee_del_mejor`). Total predicho/observado de L1 y de la media constante: **0,9305** (subestiman ~7 %); L0 ≈ 1,00 (`MC05`, `razon_total`).
- L1 gana a la media constante en 44 de 47 cortes, a L0 2 sem. en 47, a 4 sem. en 45 y a 8 sem. en 38 (`MC07`, conteo por corte).
- Por municipio L1 es la mejor en siete de ocho; en F la media constante gana por poco (1,0755 contra 1,0856) (`MC06`, `desvianza_poisson`).

**Los datos muestran — paso A (`MC11`, `MC14`, `MC15`):**
- Mejor: GLM Poisson (c) N=28, **1,2150** (EE 0,0363); GLM (a) **1,2302**; XGBoost (a) **1,2217**; XGBoost (b) **1,2200**. Umbrales de 1 EE: GLM **1,2513**, XGBoost **1,2562** (`MC14`).
- (a), (b) y (c) quedan a menos de 1 EE; la regla elige **(a) por simplicidad** en las dos familias. El conjunto (0) no reemplaza: GLM −0,0454 ≤ 0,0389; XGBoost −0,0648 ≤ 0,0395 (`MC14`).
- Ninguna configuración de (a), (b) o (c) se distingue de L1 por 1 EE. GLM (c) N=28 le gana en 38 de 47 cortes (`MC11`, `cortes_que_gana_a_L1`).
- (c) corrige la subestimación **en parte**: total pred./obs. 0,9341 (GLM (a)) → 0,9523 (GLM (c) N=28); A queda en 0,9001 (`MC11`; `MC12`).
- Término de A: desvianza de A 1,2950 → 1,2388 con (b), **−4,34 %** (`MC12`; `RMC` §3b.6); global: ninguno supera 1 EE.
- Dispersión de Pearson del GLM (a): mínimo **1,1035**, mediana **1,1109**, máximo **1,1171** (`MC15`).
- Los 376 GLM convergieron; sin avisos (`MC16`).

**Los datos muestran — paso B (`MC18`, `MC21`, `MC22`, `MC23`):**
- NB2 (a) **1,2301** contra GLM Poisson (a) **1,2302**; diferencia máxima entre predicciones **0,0071**; NB2 gana en 27 de 47 cortes (`MC22`).
- α por MV: mínimo **0,0349**, mediana **0,0377**, máximo **0,0400**; 47 de 47 cortes convergieron; **0** plan B (`MC22`, `MC21`).
- Grilla XGBoost: de **1,2197** (d=4 n=300 lr=0,05) a **1,2671** (d=2 n=100 lr=0,05); 11 de 12 a menos de 1 EE (umbral **1,2555**); elegida (D37) d=2 n=100 lr=0,1, **1,2375**, décima de doce, **+0,0056** sobre L1, gana a L1 en 20 de 47 cortes (`MC18`, `MC23`).
- Total pred./obs. por municipio de la XGBoost elegida: de **0,8378** (A) a **1,0727** (CH) (`MC19`).

**Los datos muestran — paso C (`MC26`, `MC29`, `MC27`):**

| Configuración | Desvianza | Total pred./obs. | Total en A | Cortes que gana a L1 |
| --- | --- | --- | --- | --- |
| GLM Poisson (a), deslizante 364 d | 1,2205 | 0,9717 | 0,9330 | 32 |
| GLM Poisson (a), deslizante 546 d | 1,2242 | 0,9588 | 0,9151 | 31 |
| GLM Poisson (a), deslizante 728 d | 1,2263 | 0,9495 | 0,8939 | 34 |
| GLM Poisson (a), expansiva | 1,2302 | 0,9341 | 0,8695 | 36 |
| XGBoost d=2 n=100 lr=0,1, deslizante 364 d | 1,2280 | 0,9712 | 0,9030 | 26 |
| XGBoost d=2 n=100 lr=0,1, expansiva | 1,2375 | 0,9336 | 0,8378 | 20 |

(`MC26`, columnas `desvianza`, `total_pred_obs`, `total_pred_obs_municipio_A`, `cortes_que_gana_a_L1`.)
- Las 8 configuraciones empatan a menos de 1 EE (umbral **1,2569**). En las dos familias todas las deslizantes tienen menor desvianza que la expansiva.
- El total pred./obs. del GLM sube hacia 1 al acortar la ventana: 0,9341 → 0,9495 → 0,9588 → 0,9717 (`MC26`).

**Resultados negativos o descartados** (explican decisiones): árbol (D4); conjunto (d) con lluvia (D14); L0 de 2 semanas (27 ceros, 2,4384, `MC05`); XGBoost elegida peor que L1 (`MC18`); conjunto (0) peor que L1 (`MC11`); NB2 sin aporte en la media (`MC22`).

**Lectura del equipo (inferencia del resumen; validar):**
- El EE entre cortes (~0,036) recoge semanas difíciles que afectan a todos por igual, así que el umbral de 1 EE no distingue entre conjuntos anidados ni de L1; las comparaciones corte a corte (38 de 47) son más consistentes (RMC §3b.6). Es propiedad de la regla, no hallazgo sobre los datos.
- Con α ≈ 0,04 la media de NB2 es casi la de Poisson: su aporte posible está en los intervalos, no en la desvianza.
- Las ventanas cortas siguen mejor el nivel creciente y calibran mejor (RMC §3d.6).
- XGBoost d=2 n=100 «todavía no terminó de ajustar los niveles por municipio»: **no se verificó**.

### 2.2 Solución seleccionada y regla (D42) — `RMC` §3d.3, §3e; `MC29`, `MC32`, `SOL`

**Los datos muestran:**
- **Regla fijada antes de ver resultados** (sección 1 y adendas; D36 a D40): 1) desvianza media; 2) empate a menos de 1 EE; 3) simplicidad (GLM antes que XGBoost; la ventana no cuenta, D40); 4) estabilidad con tolerancia de 1 EE (peor municipio → desvío entre cortes → calibración, D38).
- **La regla eligió GLM Poisson (a), ventana expansiva:** pasan las 4 ventanas del GLM; en el desvío entre cortes gana la expansiva con **0,246353** contra **0,246801** (728 d), **0,247608** (546 d) y **0,249505** (364 d). Diferencia con la segunda: **0,00045** (resta de dos celdas de `MC29`; `RMC` §3d.6).
- **Decisión D42 del equipo, apartándose de la regla:** GLM Poisson (a), **deslizante 364 d**. Motivos: desvianza media **1,2205** contra **1,2302**; gana en **30 de 47** cortes; total pred./obs. **0,9717** contra **0,9341** (en A, **0,9330** contra **0,8695**). **Ninguna diferencia de desvianza supera 1 EE** (≈ 0,036) (`MC26`, `MC28`, `MC32`).
- **Roles fijados (D42, D48):** solución; sensibilidad = GLM (a) expansiva (**no puede reemplazar** a la solución aunque gane en el test); contraste = XGBoost (a) d=2 n=100 lr=0,1 deslizante 364 d (**no compite**).
- `SOL`: no cambia después de `1560a5b`; `semilla` 20260910; `bloque_final_leido` false; el campo `commit_del_repositorio` dice `5f207e2` pero el commit que lo contiene es `1560a5b` (RMC §5; usar `git log` del archivo).
- Configuración exportada: GLM Poisson, 8 indicadoras de municipio + 7 de calendario, reentrenamiento cada 7 días, horizonte de 7 días (`SOL`).

**Lectura del equipo (a validar):** D42 antepone calibración y desvianza media a un margen de estabilidad de 0,00045, unas 80 veces menor que el EE. El informe debe contar **los dos hechos**: la regla se aplicó y eligió la expansiva; la configuración final la fijó el equipo después de ver el paso C, con los mismos 47 cortes (frases prohibidas, §6).

### 2.3 Evaluación final — `REF` §2 a §4; `EF05` a `EF18`, `META`

**Los datos muestran (`EF06`, desvianza; EE; total pred./obs.; validación):**

| Modelo | Papel | Desvianza | EE | Total pred./obs. | En validación |
| --- | --- | --- | --- | --- | --- |
| GLM Poisson (a) 364 d | solución | **1,1063** | 0,0335 | 0,9606 | 1,2205 |
| XGBoost (a) 364 d | contraste | 1,1198 | 0,0341 | 0,9608 | 1,2280 |
| GLM Poisson (a) expansiva | sensibilidad | 1,1329 | 0,0355 | 0,8989 | 1,2302 |
| L1 | referencia | 1,1359 | 0,0357 | 0,8952 | 1,2319 |
| L0 (8 semanas) | referencia | 1,2432 | 0,0387 | 0,9785 | 1,3626 |
| Media constante | referencia | 1,3152 | 0,0401 | 0,8944 | 1,3967 |

- Solución − L1 **−0,0295** (gana 33 de 47); contraste **−0,0161** (22); sensibilidad **−0,0030** (40); L0 frente a la media constante **−0,0720** (34); solución frente a la media constante gana 46 de 47 (`EF06`, columnas `dif_vs_su_referencia` y `cortes_que_gana_a_su_referencia`).
- **Todos** los modelos bajan su desvianza entre validación y bloque final, incluida la media constante: de **−0,0815** (media constante) a **−0,1195** (L0); solución **−0,1142** (`EF06`, `dif_final_menos_validacion`).
- Pareado, **descriptivo** (`EF09`): solución − L1 −0,0295, EE 0,0071, 33/14; sensibilidad − L1 −0,0030, EE 0,0005, 40/7; contraste − L1 −0,0161, EE 0,0084, 22/25; solución − sensibilidad −0,0265, EE 0,0067, 33/14; solución − media constante −0,2088, EE 0,0200, 46/1. Las razones media/EE (−4,13; −5,53; −1,91; −3,94; −10,46) **no son pruebas de significación** (D35, D52).
- Por municipio (`EF07`): la solución tiene menor desvianza que L1 en los ocho; contraste mejor en CH, E y F; solución mejor en A, B, C, D y G. Solución: A 1,0614, B 1,1401, C 1,0448, CH 1,2777, D 1,0989, E 1,1150, F 1,0701, G 1,0427. **CH** es el peor para todos salvo la media constante (C, 1,6149) (`EF06`).
- Ajustes (`EF05`): 141 de candidatos (3 × 47), sin avisos; GLM todos convergidos. Origen de α de la solución: NB2 en **45** cortes, **momentos en 2** (cortes 45 y 47, orígenes 2025-12-11 y 2025-12-25), Poisson en 0 (`EF18`, `origen_alpha`); α entre **0,0093** y **0,0339**.
- **Modelo exportado** (`META`): entrenado 2025-01-02 a 2025-12-31 (364 días, 2.912 filas, 4 iteraciones); origen de la primera predicción 2026-01-01; **α = 0,00939508767764091 por momentos** (NB2 no convergió en esa ventana; aviso «RuntimeWarning: invalid value encountered in log»); `fuentes_limpias` true; commit que contiene el modelo: `d93cf0c`.
- Sha256 del panel `82467fc8…114a1b06`, igual al del diagnóstico (`EF04`, `EF03`).

**Lectura del equipo (a validar, REF §2.1 y §3.3):**
- Como la desvianza baja para todos los modelos, la mejora final − validación refleja en buena parte un bloque más fácil de predecir; las comparaciones informativas son las hechas **dentro del mismo bloque**.
- La deslizante subestima menos el total que la expansiva, como en validación; una explicación posible, **no verificada**, es que la expansiva promedia un nivel anterior más bajo.

### 2.4 Análisis crítico y explicabilidad — `RMC` §3f, §3g; `REF` §3; `MC33` a `MC49`, `EF10` a `EF17`

**Los datos muestran — explicabilidad (validación, últimos 364 días del desarrollo, 2.912 filas):**
- Razones respecto del lunes (`MC34`, columna `razon`, IC95 de Wald): sábado **0,8467** (0,7786–0,9207), domingo **0,7001** (0,6415–0,7640), feriado **0,6537** (0,5748–0,7434); martes 1,0015, miércoles 1,0282, jueves 1,0080, viernes **1,0529** (0,9734–1,1390): de martes a viernes el IC95 incluye 1.
- Municipios respecto de A: CH **0,6118**, E **0,6908**, G **0,7294**, F **0,8681**, C **1,1244**, B 0,9891, D 0,9933 (`MC34`). Esperados un lunes: A **3,5056**, C **3,9415**, CH **2,1446** (`MC34`, `tipo` municipio).
- Importancia por permutación (`MC36`, `aumento_medio`): solución, municipio **+0,2270** (+18,6 %), calendario **+0,1277** (+10,5 %); contraste, municipio **+0,1717**, calendario **+0,0955**. En los dos modelos pesa más el municipio.
- Dependencia parcial (`MC37`): XGBoost reproduce el orden del GLM con un rango más angosto entre municipios.
- GLM de los 364 días: dispersión de Pearson **1,1006**, NB2 α **0,0297** (`MC33`).

**Los datos muestran — errores (validación, solución):**
- Por municipio (`MC38`): desvianza de **1,0541** (F) a **1,4068** (E); total pred./obs. de **0,9330** (A) a **1,0222** (B); la solución acerca a 1 el total en los seis municipios que L1 subestimaba (A 0,8641 → 0,9330) y pasa a sobreestimar levemente B y CH (1,0222; 1,0218).
- Por tipo de día (`MC39`): domingo 1,4006 y martes 1,3274 (peores); jueves 1,0689 (mejor).
- **Cinco semanas de mayor desvianza** (`MC40`): cortes 43, 47, 5, 20 y 22; el 43 es 2025-01-02 → 2025-01-08, desvianza 1,8183, observado 100 contra 155,15 predicho. Están entre las 7 peores de L1. **No se atribuyen causas.**
- Calibración (`MC42`, `MC44`): observado/predicho entre **0,9449** (decil 5) y **1,1756** (decil 2); tendencia del residuo **−0,0072** por corte (IC95 −0,0195 a 0,0051); obs./pred. **1,0513** (cortes 1–23) y **1,0087** (24–47).
- Intervalos (`MC46`, validación): NB2 80 % → **0,8883** (esperada **0,8959**); 95 % → **0,9787** (**0,9840**); Poisson **0,8712** y **0,9734**. Más observaciones por encima del intervalo que por debajo.
- Pareado (`MC47`, **posterior a ver los resultados**): solución − L1 **−0,0114**, EE 0,0054, 32/15; sensibilidad − L1 −0,0017, EE 0,0005; contraste − L1 −0,0038.
- Exclusión de un municipio por vez (`MC48`, D43): el global empeora **+0,42 %**, A **+2,00 %**, CH +0,01 %, G −0,11 %.

**Los datos muestran — bloque final (solución):**
- Peor municipio CH (**1,2777**); residuo medio (observado − predicho) positivo en A, B, C, CH, D y E (de **0,0702** a **0,2049**) y casi nulo en F (**−0,0157**) y G (**0,0156**) (`EF10`). Por tipo de día (`EF11`): sábado **1,2353** y feriado **1,2256** (peores), viernes **0,9191** (mejor); pred./obs. < 1 en siete de ocho niveles (el miércoles **1,0053**).
- Cinco peores semanas: cortes 30, 18, 5, 17 y 8 (`EF12`); son también las cinco peores de L1; ninguna con feriados; el corte 18 (2025-06-05 a 06-11) tiene 216 observados contra 166,74 predichos (pred./obs. 0,7719).
- Calibración (`EF14`): solución entre **0,9426** (decil 5) y **1,1095** (decil 8), 8 de 10 deciles sobre 1; sensibilidad entre 1,0331 y 1,1985. Tendencia (`EF16`): pendiente de la solución **−0,00115**, IC95 [−0,0079; 0,0056]; obs./pred. **1,058** (cortes 1–23) y **1,025** (24–47).
- Cobertura de la solución (`EF17`, global, n = 2.632): NB2 80 % → empírica **0,9005**, esperada por el modelo **0,8871**; 95 % → **0,9791** contra **0,9810**; Poisson **0,8913** y **0,9745**; 80 %: debajo 0,0315, encima 0,0680.

**Lectura del equipo (inferencias ya rotuladas; validar):**
- La importancia mide la dependencia **del modelo** respecto de cada grupo, no una causa; sin exposición, más siniestros pueden ser más tránsito.
- La desvianza alta de las peores semanas viene de la distribución entre días y municipios, no del volumen semanal (REF §3.2).
- La asimetría de los intervalos es coherente con la subestimación del total (REF §3.4).
- La ventana de 364 días parece seguir el nivel sin deriva sostenida detectable; la pérdida de A al excluirlo es coherente con su calendario propio (RMC §3g.9). Con 8 municipios la prueba tiene poco poder.

### 2.5 Prototipo y pruebas — `PIP`, `ORI`, `HO` (fase 5)

**Los datos muestran:**
- **Qué es:** pestaña «Predicción (PAA)» agregada al dashboard del PID copiado sin cambios (commit de origen `f803bd6`, copia `d5d1726`); cambios al código heredado solo en `app/app.py`: una entrada en `NAV`, su ícono y una rama `elif` (D66, D67; `ORI`).
- **Funciones nuevas:** modo «Próxima semana» (2026-01-01 a 2026-01-07, 8 municipios × 7 días = 56 filas, intervalos del 80 % y 95 %, vía `src/modelo.py` y `models/modelo_final.json`, sin historia, D51) y modo «Histórico» (47 semanas del bloque final, leídas de `predicciones_bloque_final.csv` sin recalcular, D63); mapa pydeck por municipio, barras, líneas y tabla. No usa bases de datos ni `config` (D67).
- **Pruebas** (`PIP` §2): `pytest` en el repositorio de trabajo **76 pasadas**, 0 fallidas, 0 saltadas (antes de la fase, 46); las nuevas, **30** (`tests/test_pipeline_inferencia.py` 24 + `tests/test_app.py` 6); en clon limpio sin `data/`: **66 pasadas y 10 saltadas** (las 10 necesitan el panel; ninguna nueva se salta); `streamlit run` arranca y `/_stcore/health` responde 200. Con las versiones de D70 (streamlit 1.57.0, plotly 5.22.0, pydeck 0.9.1) las 30 pasan.
- **Qué cubren:** validación de entradas (47 orígenes válidos; 2026-01-01, 2025-02-05, 2025-02-07 y 2024-12-31 dan «fuera del bloque final»), carga del modelo (ausente, ilegible, no GLM), flujo integral (56 filas; μ igual a la del servidor con diferencia relativa ≤ 1e-6), formato y rango de salidas (sin nulos ni negativos; `inf_95 ≤ inf_80 ≤ sup_80 ≤ sup_95`), «Histórico» fila a fila con igualdad exacta en las 47 semanas.
- **Errores hallados y corregidos** (`PIP` §4): (1) el mensaje de «archivo ausente» fallaba con `ValueError` si la ruta estaba fuera del repo; (2) la capa simplificada traía el Municipio CH como `MultiPolygon` (polígono + fragmento de 5 vértices) y `datos_mapa` lo armaba mal; capa regenerada, cociente de áreas entre 0,999 y 1,004; (3) pruebas que dejaban modificado un módulo compartido (error de la prueba, no del producto).
- **Procedencia de la capa de municipios:** `ORI`; sha256 de partida `c5d9f651…` (ver §4).
- **No cubierto** (`PIP` §5): verificación visual del mapa y los gráficos; páginas heredadas (D67); los valores del modelo no se recalculan en las pruebas («Histórico» se compara con el CSV por igualdad y «Próxima semana», con el CSV del servidor con tolerancia 1e-6).
- **Dos orígenes de predicción distintos:** «Próxima semana» usa el modelo exportado único (`MOD`); «Histórico» muestra predicciones del **reentrenamiento semanal** de la evaluación final, no del modelo exportado (`PIP` §5, último punto; `REF` §1.3). El informe debe distinguirlos.
- **Capturas de pantalla:** no hay en el repositorio `<!-- PENDIENTE: el equipo toma capturas de la pestaña en el navegador (D63) -->`.

**Lectura del equipo:** sin lectura propuesta en los resúmenes para el prototipo; la valoración de usabilidad y del nivel TRL 5 la aporta el equipo tras la prueba manual (D63).

---

## 3. Tablas y figuras

Numeración **propuesta** (continúa Tabla 5 y Cuadro 5). Las ilustraciones del informe vigente están todas en anexos (L193): confirmar si las del cuerpo se admiten allí. «Anexo» = sí va al anexo.

### Tablas

| N.º | Título propuesto | Archivo | Sección | Anexo |
| --- | --- | --- | --- | --- |
| Tabla 6 | Referencias en validación (47 cortes, 8 municipios) | `experiments/modelos_candidatos/tablas/05_referencias_globales.csv`, `08_…` | 4.4 | No |
| Tabla 7 | Conjuntos de variables, GLM y XGBoost (paso A) | `…/11_paso_a_globales.csv` | 4.4 | No |
| Tabla 8 | Grilla de XGBoost y NB2 (paso B) | `…/18_paso_b_globales.csv` | 4.4 | No |
| Tabla 9 | Ventanas de entrenamiento (paso C) | `…/26_paso_c_globales.csv` | 4.4 | No |
| Tabla 10 | La regla de selección paso a paso y la decisión D42 | `…/29_paso_c_eleccion.csv`, `32_fase3_configuracion_final.csv` | 4.5 | No |
| Tabla 11 | Desempeño en el bloque final y en validación | `experiments/evaluacion_final/tablas/06_globales.csv` | 4.6 | No |
| Tabla 12 | Diferencias pareadas corte a corte (descriptivas) | `…/09_pareado.csv` | 4.6 | No |
| Tabla 13 | Desvianza por municipio en el bloque final | `…/07_por_municipio.csv` | 4.6 | Sí (Anexo G) |
| Tabla 14 | Razones del GLM respecto del lunes y de A | `experiments/modelos_candidatos/tablas/34_fase3b_coeficientes_glm.csv` | 4.7 | No |
| Tabla 15 | Importancia por permutación | `…/36_fase3b_importancia_permutacion.csv` | 4.7 | No |
| Tabla 16 | Errores por tipo de día en el bloque final | `experiments/evaluacion_final/tablas/11_errores_por_tipo_dia.csv` | 4.7 | Sí |
| Tabla 17 | Cinco semanas de mayor desvianza en el bloque final | `…/12_semanas_mayor_desvianza.csv` | 4.7 | Sí |
| Tabla 18 | Cobertura de los intervalos (bloque final y validación) | `…/17_cobertura_intervalos.csv`, `modelos_candidatos/tablas/46_…` | 4.7 | No |
| Tabla 19 | Pruebas del pipeline de inferencia | `documentacion/pruebas_pipeline.md` §2 | 4.8 | No |
| Tabla 20 | Corrida del entrenamiento en el servidor (job 136) | `documentacion/logs/servidor_modelo_final/resumen_corrida.json` | 3.4.6 / Anexo F.1 | Sí |
| Tabla 21 | Paso A por municipio | `…/12_paso_a_por_municipio.csv` | — | Sí |
| Tabla 22 | Cumplimiento de objetivos | `experiments/evaluacion_final/tablas/19_cumplimiento_objetivos.csv` | 5 | No |

Cuadros: **Cuadro 3** y **Cuadro 4** se reescriben (1.5, 1.6). Cuadro nuevo propuesto: «Decisiones del equipo y su fecha» (D17 a D20, D27 a D29, D31 a D40, D42 a D45, D48 a D58), a partir de `RMC` §1.1 y `REF` §1.1–1.2.

### Figuras

| N.º | Título propuesto | Archivo | Sección | Anexo |
| --- | --- | --- | --- | --- |
| Ilustración 1 | Desvianza por ventana de entrenamiento (paso C) | `experiments/modelos_candidatos/figuras/fig6_paso_c_ventanas.png` | 4.4 | No |
| Ilustración 2 | Razones del GLM (coeficientes con IC95) | `…/fig7_coeficientes_glm.png` | 4.7 | No |
| Ilustración 3 | Importancia por permutación | `…/fig8_importancia_permutacion.png` | 4.7 | No |
| Ilustración 4 | Desvianza por corte en el bloque final | `experiments/evaluacion_final/figuras/fig1_desvianza_por_corte.png` | 4.6 | No |
| Ilustración 5 | Cobertura de los intervalos en el bloque final | `…/fig5_cobertura_intervalos.png` | 4.7 | No |
| Ilustración G1 | Referencias por corte (validación) | `modelos_candidatos/figuras/fig1_referencias_por_corte.png` | — | Sí |
| Ilustración G2 | Referencias por municipio | `…/fig2_referencias_por_municipio.png` | — | Sí |
| Ilustración G3 | Total semanal observado y predicho (referencias) | `…/fig3_total_semanal_referencias.png` | — | Sí |
| Ilustración G4 | Paso A: desvianza por configuración | `…/fig4_paso_a_desvianza.png` | — | Sí |
| Ilustración G5 | Paso B: desvianza por configuración | `…/fig5_paso_b_desvianza.png` | — | Sí |
| Ilustración G6 | Dependencia parcial | `…/fig9_dependencia_parcial.png` | — | Sí |
| Ilustración G7 | Calibración y residuos en validación | `…/fig10_calibracion_y_residuos.png` | — | Sí |
| Ilustración G8 | Cobertura de intervalos en validación | `…/fig11_cobertura_intervalos.png` | — | Sí |
| Ilustración G9 | Desvianza por municipio en el bloque final | `evaluacion_final/figuras/fig2_desvianza_por_municipio.png` | — | Sí |
| Ilustración G10 | Total semanal en el bloque final | `…/fig3_total_semanal.png` | — | Sí |
| Ilustración G11 | Calibración y residuos en el bloque final | `…/fig4_calibracion_y_residuos.png` | — | Sí |
| Ilustración 6 | Pestaña «Predicción (PAA)» del prototipo | `<!-- PENDIENTE: captura del equipo (D63) -->` | 4.8 | No |

Toda tabla y figura necesita lectura en el texto (CLAUDE.md). Las figuras 4 a 10 de `modelos_candidatos` y 1 a 5 de `evaluacion_final` ya existen; ninguna requiere regenerarse.

---

## 4. Limitaciones a declarar

**Del §5 de `resumen_evaluacion_final.md` (12 puntos):**
1. Una sola serie de 47 semanas consecutivas; las comparaciones pareadas son descriptivas y no hay réplica independiente.
2. El bloque final **no es un conjunto virgen**: se consultó durante el E2 (INF 3.4.4); desde el 05/10/2026 ningún diagnóstico lo consulta; la solución se fijó en `1560a5b` antes del notebook de evaluación.
3. El bloque final resultó **más fácil para todos los modelos** (`EF06`, `dif_final_menos_validacion`): la mejora final − validación no se atribuye a ningún modelo.
4. Subestimación persistente: la solución predice el 96,06 % del total observado (`EF06`); los fallos de los intervalos se concentran por encima (`EF17`).
5. El modelo exportado usa **α por momentos** (0,009395), en el piso del rango del test (0,0093 a 0,0339); NB2 no convergió en la ventana final ni en los cortes 45 y 47 (`META`; `EF18`).
6. La configuración final **no es la que eligió la regla** (D42), tomada con los mismos 47 cortes de validación.
7. **Sin meteorología:** el objetivo 2 no se cumplió en esa dimensión (`EF19`).
8. La verificación del servidor **compara modelos, no evalúa** (REF §4.3).
9. Cada reejecución reescribe `commit_base` y `fecha_generacion` de `META`: único diff aceptado en `models/` (D61).
10. El log del servidor **no identifica la versión del script** que corrió (sin sha256 ni commit); la evidencia es indirecta: el log imprime la comparación de sha256, que existe desde `82c0c3a`, y no hay commits posteriores del script (REF §5, punto 10).
11. Los comentarios del script y el docstring de sus tests citan pandas 1.5.3: deuda aceptada, contradice la corrida real (REF §5, punto 11).
12. `predicciones_bloque_final.csv` versiona los conteos observados del bloque final; el equipo confirmó el 21/10/2026 que no viola las restricciones de uso de UNASEV (D65).

**Pedidas por la fase 6:**
- **Despliegue en el servidor pendiente (D69).** No hay en el repositorio ningún artefacto de despliegue del dashboard en el servidor institucional; lo verificado en el servidor es el entrenamiento (job 136). El Streamlit de referencia (D70) es 1.57.0; `app/requirements.txt` (Docker del PID) no se tocó; la prueba con las versiones del servidor usó **Python 3.13.9**, que puede no ser el del servidor (`PIP` §5). Falta además la prueba manual y el clon limpio del equipo (D63).
- **Versiones del job 136:** Python 3.10.12, numpy 1.26.4, pandas 2.3.3, scikit-learn 1.7.2, scipy 1.12.0, sin statsmodels ni `holidays` (`L136`); **no** pandas 1.5.3. El job 137 (dos versiones instaladas) no tiene log versionado (1.7).
- **Lock con Python 3.13.9:** `requirements-lock.txt` se regeneró el 2026-10-21 en un entorno limpio con Python 3.13.9, no 3.13.2 (cabecera del archivo; HO, fase 5); aceptado por el equipo, solo agrega paquetes. Las corridas de los notebooks usaron 3.13.2 (`EF00`). Un intento de `nbconvert` con el Python del sistema (3.13.9) falló en la celda 3 y no leyó el bloque final (REF §1.6).
- **Capa de municipios `c5d9f651`:** el mapa del prototipo se simplificó desde una copia local con sha256 `c5d9f651aa6d88d6ff5bb32b831664b5850b275bfe562bed9e68246492c48d4a`, **distinta** de la registrada por el ETL (`ed0ba13e…`, `experiments/etl_montevideo/tablas/03b_procedencia_capa_zonas.csv`); no se sabe en qué difieren; los 8 polígonos y sus nombres coinciden. Sirve para colorear, no para medir áreas (`ORI`).
- **α por momentos (D55):** ver punto 5 arriba; el informe debe decir que los intervalos del modelo exportado usan α por momentos y los del bloque final, NB2 en 45 de 47 cortes (`EF18`).

**Del §5 de `resumen_modelos_candidatos.md` (resumidas):**
- Los 47 cortes sirven a la vez para buscar, seleccionar y comparar: la validación del ganador es optimista (sesgo declarado).
- El EE entre cortes ignora la dependencia entre cortes vecinos; no es un EE pareado.
- L1 subestima por la tendencia creciente (0,9305).
- D43 a D45 están en el mismo commit que sus resultados (`508c46e`): git no prueba que se fijaran antes de calcular; lo respalda solo el registro de IA.
- Las coberturas de los intervalos son proporciones sin incertidumbre; las observaciones de un corte y municipio no son independientes.
- Deuda aceptada de código del notebook (lambdas, globales reutilizados) y explicaciones bajo «Evidencia» en dos lecturas (11.1, 12.1).
- Verificaciones de fuga hechas fuera del repo, sin artefacto (RMC §3b.7, §3e.4).

**Del prototipo:** AppTest no dibuja el mapa ni los gráficos; las páginas heredadas consultan bases que este repo no incluye (D67); aviso de `use_container_width` deprecado con streamlit 1.65 (aceptado por el equipo).

---

## 5. Inconsistencias en Introducción, Marco conceptual y Referencias (para el equipo; **no se corrigieron**)

| Dónde | Qué dice | Con qué choca |
| --- | --- | --- |
| **2.3.2, L469** | «solo supera la banda nula en uno de los ocho municipios (Tabla 2)» | Coherente con la Tabla 2 (L702, «1 de 8 (C)»); la versión anterior («cinco de los ocho») ya no está en el informe vigente. Sin inconsistencia, se deja constancia |
| **2.3.2, L473** | «La lista … quedará cerrada antes de comenzar esa comparación» (futuro) | La comparación ya se hizo (1.2) |
| **2.3.2, L463–465** | Una oración sin punto final (L463) y un párrafo que empieza «Por esta razón» sin antecedente | Edición; el equipo decide |
| **2.3.4, L481** | «El modelo base de este trabajo se ajusta con el criterio por omisión» (árbol) | El árbol se retiró (D4); el modelo base del E3 es GLM Poisson |
| **2.3.4, L483** | Conjuntos «como trabajo futuro» | XGBoost se evaluó en el E3 |
| **2.3.3, L477** | El vector de atributos incluye «variables meteorológicas contemporáneas y rezagadas» y estadísticos de ventanas móviles | La solución usa solo municipio y calendario (`SOL`); la lluvia se excluyó (D14) |
| **2.3.6, L493** | Árbol de profundidad acotada, «valores de atribución por observación» | No hubo árbol ni atribuciones por observación; lo hecho: coeficientes, permutación y dependencia parcial (MC34, MC36, MC37) |
| **2.1.4, L395** | «Esto justifica incorporar la lluvia mediante rezagos e indicadores derivados» | El E3 no la incorporó (D14) |
| **2.4, L497** | «El bloque de variables exógenas incorpora … meteorológicos, incluyendo el indicador de período seco previo» | Ningún modelo del E3 usa meteorología |
| **2.2.5, L445** | Validación por origen móvil «(expanding window)» | El E3 también usa ventana deslizante (D42) |
| **2.2.6, L451** | La calibración completa «queda para el Entregable 3» | Hecha (`MC42`, `EF14`) |
| **2.3.5, L489** | «excluir una zona por vez y promediar» | Hecho en D43 (`MC48`), con la salvedad de que el nivel de la zona excluida sale de su historia propia (no mide generalización a zonas sin datos) |
| **1.2.2, L335** | Obj. 2 «con y sin variables exógenas» | Las exógenas evaluadas son solo de calendario; meteorología no cumplida (`EF19`) |
| **1.2.2, L339** | Obj. 4: nueva pestaña | `EF19` lo marca «no cumplido en esta fase»; la fase 5 lo implementó (§2.5) |
| **1.3, L345** | Las variables comprenden «las condiciones meteorológicas diarias» | Ningún modelo las usa |
| **1.4, L363** | Limitación de variables meteorológicas observadas (cota optimista) | Describe una variable que la solución no usa (REF §6, punto 2) |
| **Intro, L313** | «tres insumos principales» incluye la serie meteorológica | Sigue en el conjunto preparado, sin uso en modelos |
| **Intro, L349** | «protocolo … sobre la serie de un único municipio» | Cierto para el E2; el E3 trabaja el panel de 8 |
| **Referencias** | 13 entradas, todas citadas en el texto | Falta XGBoost, binomial negativa y demás (1.9); aportan el equipo |
| **Cuadro 1** | Resume 7 fuentes | No incluye Géron ni Hyndman y Athanasopoulos, que sí se citan; decisión editorial |
| **Índice, L169** | Anexo F = «Entorno, reproducibilidad y ejecución en el servidor» | El título real (L1042) es «Resultados complementarios de la línea base» |
| **Glosario, L255** | «Bloque final … se reserva para la evaluación final» | Ya se evaluó |
| **Glosario** | No define GLM, binomial negativa, XGBoost, importancia por permutación | Entran en el E3 (1.8) |

Además: `resumen_linea_base.md` (E2, una serie, L0 de 4 semanas) **sigue sin actualizarse**: RMC §7, punto 5, lo deja pendiente; sus cifras no son comparables con las del panel.

---

## 6. Frases que no deben aparecer en el informe (todos los resúmenes)

### 6.1 `resumen_modelos_candidatos.md` §5

| Frase | Por qué no |
| --- | --- |
| «El modelo final mejora a la línea base en X %» | En validación queda a menos de 1 EE de L1 (1,2205 contra 1,2319, `MC26`) |
| «Los candidatos mejoran a L1» / «GLM (c) supera a L1» | Ninguna de (a), (b), (c) se distingue de L1 por 1 EE (`MC11`); GLM (c) N=28 tiene menor desvianza (1,2150) y gana 38 de 47 |
| «El nivel reciente corrige la subestimación» | Solo en parte: 0,9341 → 0,9523; A en 0,9001 |
| «El término de A no aporta» | Mejora A en 4,34 % (1,2950 → 1,2388); lo que no supera es 1 EE en el global |
| «Se eligió (a) porque es el mejor» | Se eligió por simplicidad entre empatados |
| «Los rezagos semanales aportan» | El conjunto (0) es peor que L1 (+0,0438 a +0,0581) |
| «El GLM Poisson está sobredispersado de forma importante» | Dispersión de Pearson 1,1035 a 1,1171 |
| «La binomial negativa mejora la predicción» (también NB2 364 d: 1,2205) | NB2 1,2301 contra 1,2302; difieren como mucho en 0,0071 |
| «Se eligió la mejor combinación de XGBoost» | Se eligió la más simple de 11 empatadas; es la décima de 12 y está sobre L1 |
| «XGBoost supera a L1» | La elegida gana en 20 de 47; la mejor de la grilla (1,2197) queda a menos de 1 EE |
| «La NB2 tuvo problemas de convergencia» / «se usó el plan B» | 47 de 47 convergieron en validación; ningún plan B |
| «La ventana expansiva es la mejor» | La eligió la regla por 0,00045; en desvianza es la peor de las cuatro del GLM |
| «El modelo final es GLM Poisson (a) con ventana expansiva» | La final es la deslizante de 364 d (D42); la expansiva es sensibilidad |
| «La configuración final la eligió la regla» (cualquier variante: «se aplicó la regla y dio…», «la regla, con un ajuste menor», «la regla recomendó…») | La regla eligió la expansiva; la de 364 d es decisión del equipo (D42) después de ver el paso C |
| «La regla de selección se cumplió» / omitir D42 | Se aplicó y se reportó, pero la final no es la que eligió |
| «La deslizante de 364 días es significativamente mejor» / «mejora significativamente» | Menos de 1 EE; los motivos de D42 son desvianza media, 30 de 47 cortes y calibración |
| «La expansiva puede reemplazar a la final si rinde mejor en el test» | D42 la fija como sensibilidad |
| «XGBoost compite con el GLM en la fase 4» | Es contraste y no compite |
| «El modelo supera a L1» / «significativamente mejor que L1» | Pareado −0,0114, EE 0,0054, 32/47: posterior, sin umbral previo, cortes dependientes |
| «La sensibilidad es mejor que L1» como hallazgo | −0,0017 (EE 0,0005): consistente pero minúscula |
| Presentar la diferencia pareada como prueba de significación (o dar media/EE como estadístico) | Análisis posterior (D35), cortes vecinos dependientes, 4 comparaciones sin corrección |
| «El municipio causa/explica los siniestros» (a partir de la importancia) | La permutación mide dependencia del modelo; sin exposición |
| «Los viernes hay más siniestros que los lunes» | 1,0529, IC95 0,9734–1,1390: no se distingue de 1 |
| «La semana del 2 de enero falló por las fiestas» (o cualquier causa) | Los datos no registran qué pasó |
| «Los intervalos del 80 % cubren el 80 %» / «están bien calibrados» | NB2 cubre 0,8883 con 0,8959 esperado; en E, 0,8602 |
| Presentar las coberturas como exactas («la cobertura es 0,8883») | Proporciones sin incertidumbre; observaciones no independientes |
| «No hay deriva» | Pendiente compatible con 0 (−0,0072, IC95 −0,0195 a 0,0051): ausencia de evidencia, no de deriva; la primera mitad sigue subestimada (1,0513) |
| «El modelo generaliza a municipios no vistos» | La exclusión usa la historia propia del municipio; poco poder con 8 |
| «Los coeficientes muestran que el feriado reduce los siniestros un 35 %» sin aclarar | Es la razón respecto del lunes en el último año del desarrollo (0,6537); asociación |
| «La línea base es L0 de 4 semanas» (con estas cifras) | Queda por detrás de la media constante (1,5210 contra 1,3967); la que pasa es la de 8 semanas |
| «La L0 de 8 semanas se fijó antes de ver los resultados» / «es mejor que la media constante» | Se eligió mirando los 47 cortes; la diferencia (0,0341) es menor que 1 EE (0,0447) |
| «L1 es el mejor modelo del proyecto» | Es la mejor **referencia** |
| «El calendario de 8 niveles explica la mayor parte de la variación» | L1 mejora sobre la media constante (1,2319 contra 1,3967) pero la desvianza sigue sobre 1 |
| «El test confirma…» / cualquier cifra del test (en `modelos_candidatos`) | Ese notebook no lo leyó |
| «La lluvia no sirve» | Se dejó fuera por no estar disponible a 7 días y por no aportar en el diagnóstico; no se probó en el E3 |
| «Estas cifras coinciden con las del Entregable 2» | Aquéllas son de una serie con bloque final; éstas, de ocho municipios y desarrollo |
| «L0 de 2 semanas es una referencia razonable» | 27 predicciones cero y desvianza 2,4384 |

### 6.2 `resumen_evaluacion_final.md` §5

| Frase | Por qué no |
| --- | --- |
| «La solución es significativamente mejor que L1 (o que la sensibilidad)» | Las razones media/EE no son pruebas (D35) |
| «Los intervalos tienen la cobertura nominal» / «sobrecubren 10 puntos» | Se compara con la esperada por el modelo (0,8871 al 80 %) |
| «El modelo mejoró en el test respecto de validación» | Todos bajaron, incluida la media constante |
| «El test confirma la elección de la ventana deslizante» | La decisión es D42, tomada en validación |
| «El modelo exportado usa el α de NB2» | Usa α por momentos |
| «XGBoost sería una alternativa mejor» / cualquier ranking que lo ponga a competir | Es contraste (D48); gana a L1 en 22 de 47 |
| «El modelo explica por qué ocurren los siniestros» / causas de las peores semanas | Trabajo predictivo; los datos no registran qué pasó |
| Cifras del chequeo en el entorno simulado presentadas como del servidor | Las del servidor son las del job 136 |
| «El servidor confirmó el desempeño» / «se validó en el servidor» | Solo verificó que el entrenamiento da el mismo modelo |
| Versiones del contenedor tomadas de `train/README.md` del 18/09 (pandas 1.5.3) | La corrida usó pandas 2.3.3 |
| «El modelo es aplicable a otros departamentos» o a datos de 2026 | No se evaluó fuera de Montevideo ni después del 2025-12-31 |

### 6.3 `resumen_diagnostico_municipios.md` §9

| Frase | Por qué no |
| --- | --- |
| «Los municipios son iguales» / «se comportan igual» | El nivel difiere 1,71× y A se comporta distinto |
| «La tendencia es creciente en todos los municipios» | En E (p = 0,61) y CH (p = 0,97) no se detecta |
| «Hace falta un modelo por municipio» | Especializar el calendario no mejora en promedio (−0,22 % y +0,32 %) |
| «El calendario de C es distinto y por eso necesita su propio modelo» | Distinto en muestra, no mejor fuera de muestra |
| «Un solo modelo resuelve todo» | Solo para nivel y calendario con un modelo mínimo |
| «A es el municipio más riesgoso» / «X es el más peligroso» | Se mide lo registrado, no el riesgo |
| «El pico de siniestros de X es en <mes>» | 3 observaciones por mes |
| «El 2021 de A y D sigue afectado por la pandemia» | Observación, no investigada |
| «G y CH tienen más atípicos» | 18 y 15 de sus 35 son días de 4–5 siniestros |
| «Los municipios se influyen entre sí» | Correlación residual media de 0,033 |
| «Hay autocorrelación en todos los municipios» | Solo C y CH de forma consistente |
| «El modelo tiene una desvianza de 1,23» | Es el modelo mínimo del diagnóstico |
| «Estas cifras coinciden con las de los diagnósticos anteriores» | Aquéllos usaban el período completo |

### 6.4 `resumen_linea_base.md` §4 (E2, una serie)

| Frase | Por qué no |
| --- | --- |
| «El árbol candidato es el modelo final del proyecto» | Era un modelo de arranque y está retirado |
| «El modelo predice cuándo o dónde ocurrirá un siniestro» | Estima el conteo esperado por día |
| «MUNICIPIO C es el más peligroso» | Es el que más siniestros registra |
| «El modelo generaliza / funciona bien en Montevideo» | Se evaluó una sola serie |
| «Se validó la ventana de L0 / se recalculó la ACF solo con desarrollo» (en el contexto de ese notebook) | No se hizo en esa tarea; la ACF se recalculó después en el diagnóstico (`INF` L543) |

### 6.5 `resumen_preparacion_montevideo.md` §10

| Frase | Por qué no |
| --- | --- |
| «El ETL prepara los datos para el modelo» | Prepara parte; escalado, particiones y variables con memoria quedan fuera a propósito |
| «Se imputaron los valores faltantes» | No se imputó nada |
| «Se balancearon las clases» / «se trató el exceso de ceros» | No corresponde (8,60 % de ceros) |
| «Se aplicó interpolación de ceros» | Se descartó |
| «El clima explica las diferencias entre municipios» | Serie única para el departamento |
| «Se eliminaron los outliers» | Se eliminaron duplicados exactos |
| «El conjunto incluye la gravedad» | Se retiró por fuga |
| «El estrato de actividad clasifica los municipios por riesgo» | Descriptivo, no entra al panel |
| «El modelo se validó comparando la zona más activa contra una de contraste» | Razón 1,15×: ya no mide generalización |

---

## 7. Pendientes del equipo

1. **Confirmar o escribir D2, D4, D14 y D69** en `HANDOFF.md` (no están definidas en ningún archivo versionado).
2. **Commitear el log del job 137** en `documentacion/logs/` si se va a citar la observación de las dos versiones instaladas; si no, no citarla (sin artefacto, regla de oro).
3. **Prueba manual del prototipo en el navegador** y **clon limpio con el README** (D63); tomar las **capturas** para el informe.
4. **Despliegue en el servidor (D69):** decidir si el informe lo declara como pendiente o se hace antes del 25/10.
5. **Fuentes para el informe:** XGBoost, binomial negativa, α por momentos (Cameron y Trivedi), Newey-West y permutación; no se inventó ninguna.
6. **Escribir a mano Introducción y Marco teórico** y resolver las inconsistencias de la §5; Claude no las toca.
7. **Decidir el destino de las Tablas 4 y 5, F1–F4 e Ilustraciones F1–F2** (E2, árboles, ajuste congelado).
8. **Validar las «Lecturas del equipo»** de la §2: son inferencias de los resúmenes, no evidencia.
9. **Confirmar la numeración de secciones** (4.4 a 4.8, 5, 6) y si las ilustraciones pueden ir en el cuerpo, contra la *Guía y modelo para la elaboración de informes* institucional (no estaba en el contexto).
10. **Actualizar `resumen_linea_base.md`** (pendiente de E2; RMC §7, punto 5).
11. **Revisar la discrepancia del informe** en el entorno (Python 3.13.15 y 17 dependencias directas, L642) contra el real (3.13.2, 18 en la fase 4, 25 hoy) y el lock con Python 3.13.9.
12. **Revisar `EF19`:** el estado del objetivo 4 quedó fijado antes de la fase 5; el informe debe usar el estado actual (§2.5), y declarar que la tabla es anterior.
13. **Registro de IA y HANDOFF:** esta sesión quedó registrada en `documentacion/registro_uso_IA.md` y `HANDOFF.md`.
