# Resumen de modelos candidatos — protocolo, referencias y experimentación (Entregable 3)

**Notebook:** [`notebooks/modelos_candidatos.ipynb`](../notebooks/modelos_candidatos.ipynb)
**Artefactos:** `experiments/modelos_candidatos/` (26 tablas CSV en `tablas/`, 5 figuras PNG en `figuras/` y
`registro_experimentos.csv`)
**Código que usa:** `src/variables.py`, `src/datos.py`; pruebas en `tests/test_variables.py`
**Fecha de ejecución:** 2026-10-14; **reejecutado el 2026-10-19** tras la review R1 (`jupyter nbconvert --execute --inplace` en el
`.venv`; 0 errores; entorno en `tablas/00_entorno.csv`). Las 11 tablas y 3 figuras quedaron **idénticas** a las del 2026-10-14
(ninguna cifra cambió; ver §8). **Fase 2, paso A: ejecutado el 2026-10-19** (mismo comando, 0 errores, 0 salidas `stderr`); las
tablas 00 a 09 y las figuras 1 a 3 no cambiaron, solo `10_artefactos.csv` (índice). Dos ejecuciones dieron tablas 11 a 16 idénticas
(el registro, idéntico salvo `fecha_hora`). **Paso B: ejecutado el 2026-10-19** (mismo comando, 0 errores, 0 salidas `stderr`);
las tablas 11 a 17 del paso A no cambiaron y sus 16 filas del registro son idénticas salvo `fecha_hora`
**Alcance:** los **ocho municipios** de Montevideo, **sólo el bloque de desarrollo (2021-07-01 → 2025-02-05,
1.316 días)**; 987 días de entrenamiento inicial y 329 de validación en 47 cortes de 7 días.

> ### ⚠️ Estado: protocolo, referencias y pasos A y B (fase 2) ejecutados; paso C pendiente
>
> **Ejecutado:** protocolo y referencias (§1 a §3), el **paso A** (§3b: conjuntos de variables con GLM Poisson y XGBoost) y el
> **paso B** (§3c: grilla de XGBoost y binomial negativa NB2), en ventana expansiva. **No ejecutado:** el paso C (ventanas). **No hay
> modelo final**: los pasos A y B eligen una configuración por familia, no una solución. Nada de este documento permite afirmar qué
> modelo se elegirá.
>
> **El test no se lee.** El bloque final (2025-02-06 → 2025-12-31) no se carga en ningún código de este
> notebook: `src.datos.cargar_panel_desarrollo()` recorta cada tramo del CSV a `fecha <= 2025-02-05` antes de
> acumularlo: ninguna fila del test se conserva ni se acumula; cada tramo se lee y se filtra antes de acumularse. Hay
> `assert` que verifican que no quedó ninguna fila posterior. El límite sale del calendario
> (80 % de 1.645 días), no de los datos.

---

## 0. Cómo usar este documento

Contexto autocontenido para redactar *Metodología — diseño de evaluación*, *Línea base* y, más adelante,
*Experimentación y resultados* del informe, sin abrir el repositorio.

**Reglas que quien redacte debe respetar:**

1. **Ninguna cifra sin artefacto.** Cada cifra lleva la tabla que la respalda (`tablas/NN_nombre.csv`). Lo que
   falta se marca `<!-- PENDIENTE: ... -->` y no se completa.
2. **Distinguir evidencia de inferencia.** Las inferencias están rotuladas.
3. **No escribir Introducción ni Marco teórico** a partir de este documento.
4. **Respetar la sección 5** («frases que no deben aparecer en el informe»).
5. **Las cifras de este documento no son comparables con las de `resumen_linea_base.md`** (una sola serie, MUNICIPIO
   C, bloque final incluido) ni con las del modelo mínimo de `resumen_diagnostico_municipios.md` §7 (ajuste fijo
   por pliegue, no reentrenado cada semana). Ver §3.2.
6. **El desempeño de las referencias en validación no es el desempeño del proyecto.** Es el piso contra el que se
   compararán los candidatos, con el mismo protocolo.

---

## 1. Qué hace el notebook y por qué

### 1.1 Reglas fijadas antes de ejecutar (sección 1 del notebook; no se modifican tras ver resultados)

| Regla | Contenido | Por qué |
| --- | --- | --- |
| Referencias | Media constante global; **L0** (promedio de lo observado 7, 14, 21 y 28 días antes; ventana revisada con 2, 4 y 8 semanas); **L1 en el panel** (nivel del municipio × factor de calendario agregado de 8 niveles, el modelo M2 del diagnóstico) | Marcan el mínimo aceptable; no se ajustan por búsqueda |
| Candidatos | GLM Poisson, GLM binomial negativa, XGBoost con `objective="count:poisson"` | Lista cerrada. **PENDIENTE: no ejecutados** |
| Árbol de decisión | **Retirado antes de ejecutar** | En el E2 no extrapoló la tendencia (`resumen_linea_base.md` §4); XGBoost con pérdida Poisson es la extensión de la misma familia |
| Conjuntos de variables (anidados) | (0) sin exógenas: municipio + nivel reciente + rezagos 7/14/21/28; (a) municipio + calendario de 8 niveles; (b) (a) + término propio de calendario para A; (c) (b) + nivel reciente (28/56/91 días) | Cada paso agrega un bloque que el diagnóstico motivó |
| **Conjunto (d) eliminado** | (d) = (c) + lluvia, **retirado de la lista antes de ejecutar** (decisión del equipo, 2026-10-14) | (i) la lluvia del día a predecir no está disponible con un horizonte de 7 días (sólo existiría un pronóstico); (ii) el diagnóstico no le encontró aporte fuera de muestra (`resumen_diagnostico_municipios.md` §7.5: B3 → B4 de −0,36 % y −0,01 %) |
| Grilla de XGBoost | `max_depth` ∈ {2, 3, 4} × `n_estimators` ∈ {100, 300} × `learning_rate` ∈ {0.05, 0.1}; resto fijo y declarado | **PENDIENTE** |
| Ventanas | Expansiva; deslizante de 364, 546 y 728 días | Comparar ambas es un objetivo declarado del proyecto |
| Orden | A: conjuntos con GLM Poisson y XGBoost por defecto (expansiva). B: grilla de XGBoost y binomial negativa sobre el conjunto elegido. C: ventanas para los dos mejores | **PENDIENTE** |
| Regla de selección | 1) desvianza de Poisson media en validación; 2) empate: a menos de 1 error estándar del mejor (error estándar sobre los 47 cortes); 3) entre empatados, el más simple y explicable (GLM antes que XGBoost; menos variables antes que más); 4) desempate por estabilidad (peor municipio, dispersión entre semanas) y luego calibración (total predicho / observado) | Criterios explícitos y no una sola métrica (guía PAA §5.3) |
| Binomial negativa | Se reporta la dispersión de Pearson del GLM Poisson y el α estimado; su papel son los intervalos de predicción y la inferencia sobre coeficientes, no mejorar la desvianza | **PENDIENTE** |
| **Sesgo declarado** | La búsqueda de hiperparámetros y la selección usan los **mismos 47 cortes**: el desempeño del ganador en validación es optimista | Se declara antes de ver resultados |

**Adenda del 19/10/2026 — precisiones fijadas después de la fase 1 y antes de ejecutar cualquier candidato**
(cada precisión con su decisión del plan: D17 a D20, D27 y D28; la sexta se agregó después, D29). Espejo de la celda «Adenda a la sección 1» del notebook, que está **debajo** de la
sección 1 y **no la modifica**. Sustituye al «pendiente de precisión» que este documento arrastraba (cómo entra N en el
conjunto (0) y cuál L0 se lleva a la comparación). Las demás reglas de la tabla anterior siguen como estaban.

| N.º | Precisión | Detalle y respaldo |
| --- | --- | --- |
| 1 (D17) | **L0 que pasa a la comparación: 8 semanas** | Elegida **después de fijar la lista y mirando los 47 cortes de validación**: desvianza 1,3626 (8 semanas), 1,5210 (4 semanas, la del Entregable 2) y 2,4384 (2 semanas) (`tablas/05`). Es una elección **informada por la validación**, no una regla previa. Queda por debajo de la media constante (1,3967, `tablas/05`) por 0,0341, **menos de 1 error estándar** de ella (0,0447, `tablas/08`). El bloque final no intervino |
| 2 (D18) | Nivel reciente del conjunto (0) | N ∈ {28, 56, 91} días, elegido en el paso A por desvianza media en validación, **por separado en cada familia** (GLM Poisson y XGBoost), igual que en (c) |
| 3 (D19) | XGBoost en el paso A | `max_depth=3`, `n_estimators=300`, `learning_rate=0.05`; resto de los parámetros fijos y declarados; semilla fija |
| 4 (D20) | Elección del conjunto por familia | Entre (a), (b) y (c), con la regla de 1 error estándar y el orden de simplicidad a < b < c. El conjunto (0) se reporta para el objetivo 1.2.2 y solo reemplaza al elegido si lo mejora por más de 1 error estándar |
| 5 (D27 y D28) | Binomial negativa = **NB2** | Varianza μ + αμ², con α estimado por máxima verosimilitud **en cada corte**: `statsmodels.discrete.discrete_model.NegativeBinomial` con `loglike_method="nb2"` (verificado en la firma y el docstring de statsmodels 0.14.6). La familia `NegativeBinomial` del GLM deja α fijo (1,0 si no se le pasa), por eso no es el estimador principal. **Plan B (D28):** si NB2 por máxima verosimilitud no converge en un corte, se reporta y en ese corte se usa el GLM NB con α estimado por momentos en el mismo corte: regresión auxiliar sin intercepto de ((y − μ)² − y)/μ sobre μ, con μ del GLM Poisson ajustado en el entrenamiento de ese corte (Cameron y Trivedi, 1990) |
| 6 (D29) | Criterio de convergencia de NB2 — **agregado el 19/10/2026 en el fix de la ronda 2, antes de ejecutar candidatos (D29)** | NB2 se ajusta con `method="newton"` y `maxiter=100`. Un corte cuenta como **no convergido** si `mle_retvals["converged"]` es `False`, si se emite un `ConvergenceWarning` o si α no es finito o no es positivo; en ese caso se aplica el plan B (D28) de la fila 5. Respuesta al riesgo R7 de la ronda 2 de R1 (`documentacion/reviews/E3_fase_0-1_r2.md`): `discrete_model.NegativeBinomial.fit` puede terminar con advertencias de convergencia que no son excepciones, así que el criterio se fija antes de ejecutar. Es una regla, no código: se implementa en la fase 2 |

La fila 6 es posterior a las cinco primeras: la celda de la adenda del notebook la lleva marcada con su fecha y motivo, y las filas 1 a 5 no cambiaron.

**Precisiones de la fase 2, fijadas el 19/10/2026 antes de ejecutar candidatos** (D31 a D34 y el ítem 5). Espejo de la celda del mismo
nombre del notebook, que está **debajo de la adenda** y no modifica ni la sección 1 ni la adenda. Cubren decisiones que la fase 2
necesita y que ninguna de las dos fijaba; se tomaron con las referencias de la fase 1 como único resultado visto.

| N.º | Precisión | Detalle |
| --- | --- | --- |
| D31 | **Matriz de indicadoras** | Misma matriz para GLM y XGBoost: 8 columnas de municipio **sin constante**; calendario con 7 columnas, **lunes como referencia**; término de A con 7 columnas `a_x_*`, **sin `a_x_lunes`** (con las 8 sería colineal con la indicadora de A). En el GLM la parametrización no cambia las predicciones; en XGBoost sí, y así A queda en una sola columna |
| D32 | **Error estándar del ítem 4 de la adenda** | El de (0): el conjunto (0) reemplaza al elegido entre (a), (b) y (c) solo si **desv(elegido) − desv(0) > EE(0)**. Coherente con el paso 2 de la regla de selección (el EE es el del mejor) |
| D33 | **Registro de experimentos** | `experiments/modelos_candidatos/registro_experimentos.csv` se **reescribe en cada ejecución**, con todas las configuraciones evaluadas en ella (incluidos los resultados negativos) y su fecha y hora; historial en git, con un commit en cada parada (después de A, B y C) |
| D34 | **Forma de las variables** | En (0) y en (c): **log(nivel_reciente_N)** (con coeficiente 1 la predicción escala con el nivel reciente) y **rezagos 7/14/21/28 como conteos crudos** (hay ceros: log(y) no está definido). En XGBoost el logaritmo no cambia los árboles. Una verificación detiene la ejecución si algún nivel reciente vale 0 |
| 5 | **Parámetros de XGBoost fuera de D19** | Valores por defecto de xgboost 3.4.1 (`tree_method="hist"`, `subsample=1`, `colsample_bytree=1`, `min_child_weight=1`, `reg_lambda=1`), más `random_state=SEMILLA` y `n_jobs=1` para que los resultados sean deterministas |

*Comprobación previa a fijar D34* (no es un resultado del proyecto ni se cita como tal): sobre el panel de desarrollo leído con
`cargar_panel_desarrollo()`, la media móvil por municipio de 28, 56 y 91 días nunca vale 0 (mínimos 1,0; 1,2321 y 1,3846). El
notebook repite la verificación en cada corte y se detiene si falla.

**Precisiones del paso B, fijadas el 19/10/2026 antes de ejecutarlo** (D36 a D38). Espejo de la celda del mismo nombre del
notebook, debajo de las precisiones de la fase 2; no modifica nada anterior. Precisan cómo se aplican los pasos 3 y 4 de la regla de
selección dentro de una familia con las mismas variables, caso que la sección 1 no resuelve. Se fijaron **con los resultados del paso A
ya vistos** (§3b) y **antes de ejecutar el paso B**. **Valen también para el paso C.**

| N.º | Precisión | Detalle |
| --- | --- | --- |
| D36 | **Simplicidad entre GLM Poisson y NB2** | Con la misma matriz, GLM Poisson es más simple que NB2 (un parámetro menos: NB2 con α → 0 es Poisson). Si empatan a menos de 1 EE, gana Poisson. Cómo se construyen los intervalos de predicción se decide en la fase 3 |
| D37 | **Simplicidad entre combinaciones de XGBoost** | Entre empatadas, más simple = menor `max_depth` y, a igual profundidad, menor `n_estimators`. `learning_rate` no cuenta como complejidad: si solo difieren en él, decide el paso 4 |
| D38 | **Paso 4: lexicográfico con tolerancia de 1 EE** | Pasan las empatadas cuya desvianza del peor municipio queda a menos de 1 EE de la mejor en ese criterio (el EE es el del peor municipio de esa mejor configuración, sobre los 47 cortes, como en `tablas/12`); entre ellas gana la de menor desvío entre cortes; si empatan, la de menor \|total pred./obs. − 1\| |

**Precisiones del paso C, fijadas el 19/10/2026 con los resultados de los pasos A y B ya vistos** (D39 y D40). Espejo de la celda del
mismo nombre del notebook, debajo de las precisiones del paso B; no modifica nada anterior. Se fijaron **después de ver los pasos A y B**
(§3b y §3c) y **antes de ejecutar el paso C**.

| N.º | Precisión | Detalle |
| --- | --- | --- |
| D39 | **XGBoost que pasa al paso C** | Se mantiene la elegida por la regla en el paso B (`max_depth=2`, `n_estimators=100`, `learning_rate=0.1`), **aunque su desvianza media sea peor que la de L1** (1,2375 contra 1,2319, `tablas/18`). La mejor combinación de la grilla en desvianza (`max_depth=4`, `n_estimators=300`, `learning_rate=0.05`, 1,2197) se reporta como referencia y **no se ejecuta en el paso C** |
| D40 | **La ventana no cuenta como complejidad** | En el paso 3 solo se ordena por familia (GLM antes que XGBoost); entre ventanas de la misma familia que sigan empatadas decide el paso 4 (D38) |

**Evidencia / inferencia.** *Evidencia:* las cifras de la fila 1 salen de `tablas/05` y `tablas/08`. *Inferencia del equipo:*
que 8 semanas sea la ventana razonable para L0 (promediar más días reduce el ruido de Poisson). Como la elección usó los
mismos 47 cortes con los que se compararán los candidatos, la ventaja de L0 de 8 semanas sobre la de 4 es optimista en
la misma medida que el resto de la validación (sesgo declarado en la tabla de arriba).

### 1.2 Variables (`src/variables.py`) — única implementación, compartida con el prototipo

| Variable | Definición |
| --- | --- |
| Calendario de 8 niveles | lunes a domingo + `feriado`, derivado de `fecha`; el feriado sale de `tipo_dia` del ETL y **tiene prioridad** sobre el día de la semana |
| Nivel del municipio | media de cada municipio en la ventana de entrenamiento (constante por municipio) |
| Nivel reciente | media de cada municipio en los últimos N días antes del origen (N ∈ {28, 56, 91}); fijo para los 7 días del horizonte |
| Rezagos | `y(d − k)`, k ∈ {7, 14, 21, 28}; siempre observados con horizonte de 7 días (la función falla si algún rezago cae en el origen o después: no hay recursión) |
| Indicador de A y su término de calendario | `es_a` y 8 columnas `a_x_<nivel>` |
| Lluvia | **No está**: se retiró con el conjunto (d) |

**Convención de origen:** es el primer día a predecir; lo conocido es `fecha < origen`. Toda lectura del objetivo pasa por
una única función compuerta.

Tres decisiones de construcción (confirmadas por el equipo, 2026-10-14):

1. **Filas de entrenamiento con origen simulado.** Para que el entrenamiento se parezca a la predicción, los bloques de
   7 días se alinean hacia atrás desde el origen real y cada día toma el nivel reciente medido al comienzo de su bloque.
2. **Mismas filas para todos los conjuntos.** Se descartan las filas sin historia para la variable más exigente (nivel
   reciente de 91 días: los primeros ~91 días del panel), así que la comparación entre conjuntos es sobre las mismas filas.
   Costo: el conjunto (0) pierde filas que podría usar.
3. **Nivel del municipio como constante de la ventana.** Incluye el propio objetivo de entrenamiento en su media (sesgo
   menor, el de cualquier efecto fijo por municipio).

**Pruebas** (`tests/test_variables.py`, 15 pasan): ninguna variable usa datos posteriores al origen (con el objetivo
futuro reemplazado por un valor imposible, las variables son idénticas); los feriados coinciden con `tipo_dia`, también
en el panel real; dimensiones (56 filas en el horizonte); sin nulos en el horizonte. Se comprobó que las pruebas
detectan una fuga: haciendo que la compuerta deje pasar el futuro, fallan 5.

### 1.3 Motor de backtesting y métricas

- **47 cortes** de horizonte 7; **origen móvil**; reentrenamiento en cada corte. Primer origen: 2024-03-14 (día 988);
  último horizonte: termina el 2025-02-05.
- **Parámetro de ventana** (`None` = expansiva; `N` = deslizante de N días), implementado ya; en esta etapa sólo se usa la
  expansiva.
- **El modelo no puede mirar el futuro ni por descuido:** recibe una *vista* del panel hasta el último día del horizonte con
  el objetivo de los días ≥ origen reemplazado por NaN. Comprobado con un «modelo sonda» (`tablas/03`).
- **Predicciones guardadas** por corte, día y municipio (`tablas/09`), porque la regla del error estándar las necesita.
- **Métricas:** desvianza de Poisson media (principal; predicciones nulas reemplazadas por EPS = 1e-6), MAE, RMSE, total
  predicho / observado y días con predicción cero; globales, por municipio y por corte. **Error estándar** de la desvianza
  = desvío (ddof = 1) de las 47 desvianzas por corte ÷ √47. Como cada corte pesa lo mismo (56 filas), el promedio de las 47
  coincide con la desvianza global.

### 1.4 Control cruzado del motor — `tablas/04_control_cruzado_municipio_c.csv`

Se aplicó el motor a la serie del MUNICIPIO C sola, ventana expansiva, y se comparó con
`experiments/linea_base/tablas/04_desarrollo_backtesting.csv` (sólo esa tabla de desarrollo):

| Modelo | Desvianza (motor) | Desvianza (`linea_base`) | Diferencia | MAE (motor) | MAE (`linea_base`) |
| --- | --- | --- | --- | --- | --- |
| Media constante | 1,517768 | 1,5178 | −0,000032 | 1,759104 | 1,7591 |
| L1 (3 niveles, `tipo_dia`) | 1,378246 | 1,3782 | +0,000046 | 1,611371 | 1,6114 |

**Evidencia.** Las diferencias son de redondeo (< 0,0001, contra una tolerancia de 0,001); 47 cortes y 329 días en ambos.
**Inferencia.** El motor reproduce el protocolo de `linea_base.ipynb`; es lo que habilita comparar lo que sigue con el
Entregable 2 sin cambiar de protocolo.

---

## 2. Datos del protocolo (`tablas/01_verificacion_integridad.csv`, `02_particiones.csv`)

| Bloque | Desde | Hasta | Días |
| --- | --- | --- | --- |
| Entrenamiento inicial | 2021-07-01 | 2024-03-13 | 987 |
| Validación (47 cortes de 7 días) | 2024-03-14 | 2025-02-05 | 329 |
| Bloque final (test) | 2025-02-06 | 2025-12-31 | **no cargado** |

Verificaciones que detienen la ejecución, todas en OK: límite 2025-02-05 calculado del calendario; ninguna fila
posterior; 8 municipios; 10.528 filas (1.316 × 8); sin pares repetidos; calendario sin huecos; objetivo entero no
negativo y sin nulos; 987 / 329; 47 cortes; el último termina en el último día de desarrollo.

---

## 3. Resultados: referencias en el panel (ventana expansiva, 47 cortes, 8 municipios)

### 3.1 Globales — `tablas/05_referencias_globales.csv`, `08_referencias_error_estandar_y_estabilidad.csv`

| Modelo | Desvianza | Error estándar (47 cortes) | MAE | RMSE | Total pred./obs. | Días con predicción 0 |
| --- | --- | --- | --- | --- | --- | --- |
| **L1 (nivel × calendario de 8 niveles)** | **1,2319** | 0,0358 | 1,4006 | 1,7960 | 0,9305 | 0 |
| L0 (8 semanas) | 1,3626 | 0,0414 | 1,4957 | 1,8958 | 1,0067 | 0 |
| Media constante | 1,3967 | 0,0447 | 1,5209 | 1,9212 | 0,9305 | 0 |
| L0 (4 semanas) | 1,5210 | 0,0443 | 1,5723 | 1,9988 | 1,0054 | 0 |
| L0 (2 semanas) | 2,4384 | 0,1686 | 1,7179 | 2,1741 | 1,0044 | **27** |

(2.632 predicciones por modelo = 47 cortes × 56 filas.)

**Evidencia.**
- L1 tiene la menor desvianza. Es el único dentro de 1 error estándar de sí mismo (1,2319 + 0,0358 = 1,2677): los otros
  cuatro quedan por encima (`a_menos_de_1_ee_del_mejor` en `tablas/08`).
- **Revisión de la ventana de L0:** la desvianza **baja al alargar la ventana** (2 semanas 2,4384; 4 semanas 1,5210;
  8 semanas 1,3626). **L0 de 4 semanas —la del Entregable 2— queda por detrás de la media constante** (1,5210 contra
  1,3967); la de 8 semanas le gana (1,3626). La de 2 semanas es la peor y produce **27 predicciones exactamente cero**,
  que la desvianza reemplaza por 1e-6 (12 en CH, 10 en E, 3 en G, 1 en C, 1 en F; `tablas/06`), lo que explica en parte su
  desvianza de 2,4384.
- La razón total predicho / observado de L1 y de la media constante es la misma (0,9305): subestiman ~7 % del volumen.
  L0 queda en ≈ 1,00–1,01 porque usa lo observado reciente y sigue el nivel.
- L1 gana a la media constante en 44 de los 47 cortes, a L0 de 2 semanas en 47, de 4 semanas en 45 y de 8 semanas en 38
  (conteo sobre `tablas/07`).

**Inferencia del equipo.** El calendario de 8 niveles con nivel propio es la referencia que hay que superar. Que L0 mejore
con la ventana sugiere que promediar pocos días mete ruido de Poisson, no que la memoria semanal sirva: coincide con el
diagnóstico (el calendario explica la señal semanal y el residuo no tiene memoria detectable, `resumen_diagnostico_municipios.md`
§5.3). **Decisión (adenda del 19/10/2026, §1.1):** la L0 que se lleva a la comparación final es la de **8 semanas**, elegida
mirando estos mismos 47 cortes. En el Entregable 2 la referencia era la de 4 semanas; con estos números la de 8 semanas es
la mejor de las tres.

### 3.2 Coherencia con el diagnóstico (no es una verificación formal)

En el diagnóstico, el pliegue B de `resumen_diagnostico_municipios.md` §7.3 usa la **misma ventana de validación** (2024-03-14
→ 2025-02-05) con el ajuste fijo en los 987 días: M0 1,4014 y M2 1,2385 (`dm/18`). Acá, reentrenando cada semana: media
constante 1,3967 y L1 1,2319. La diferencia (−0,005 y −0,007) tiene el signo esperado de reentrenar con el nivel que sube, y
es chica. **No son comparables como cifra a citar** (otro protocolo); sirven para ver que nada está roto.

### 3.3 Por municipio — `tablas/06_referencias_por_municipio.csv` (desvianza)

| Municipio | Media constante | L0 2 sem. | L0 4 sem. | L0 8 sem. | **L1** |
| --- | --- | --- | --- | --- | --- |
| A | 1,3456 | 1,9148 | 1,4994 | 1,3434 | **1,3017** |
| B | 1,2708 | 1,6593 | 1,3291 | 1,2221 | **1,0862** |
| C | 1,8299 | 2,2070 | 1,6908 | 1,5142 | **1,3530** |
| CH | 1,6020 | 3,7218 | 1,6811 | 1,5156 | **1,3350** |
| D | 1,2711 | 1,7309 | 1,3251 | 1,1995 | **1,1036** |
| E | 1,5418 | 3,9930 | 1,8655 | 1,6267 | **1,4026** |
| F | 1,0755 | 1,6817 | 1,2886 | 1,2070 | **1,0856** |
| G | 1,2369 | 2,5988 | 1,4885 | 1,2727 | **1,1874** |

Total predicho / observado por municipio (misma tabla): **L1** de 0,8641 (A), 0,8862 (F), 0,9133 (C), 0,9221 (G), 0,9279 (E),
0,9557 (D), 0,9961 (B) y 1,0048 (CH); **media constante** de 0,7254 (C) a 1,3510 (CH).

**Evidencia.** L1 es la mejor en siete de los ocho municipios; **en F la media constante gana por poco (1,0755 contra
1,0856)**. El peor municipio de L1 es E (1,4026); el de la media constante, C (1,8299). L1 subestima más en A (0,8641) y F
(0,8862). **Inferencia:** la subestimación de L1 no es pareja (cf. `resumen_diagnostico_municipios.md` §7.4, misma dirección);
una recalibración del nivel (el nivel reciente del conjunto (c)) es lo que los candidatos tienen que ganar.

### 3.4 Por corte — `tablas/07_referencias_por_corte.csv`, `figuras/fig1_referencias_por_corte.png`

Rango de la desvianza por corte: L1 de 0,7786 (corte 46) a 1,7534 (corte 43); media constante de 0,7096 (46) a 2,0320 (43);
L0 de 4 semanas de 0,9219 (11) a 2,3420 (43); L0 de 8 semanas de 0,8416 (46) a 2,2221 (43); **L0 de 2 semanas de 1,2066 (11) a
5,5600 (5)**. Desvío entre cortes: L1 0,2456; L0 8 s. 0,2839; L0 4 s. 0,3036; media constante 0,3061; **L0 2 s. 1,1560**.

**Evidencia.** El corte 43 es el peor para cuatro de las cinco referencias y el 46 el mejor para tres. **Inferencia:** hay
semanas intrínsecamente difíciles que ningún modelo simple arregla; es ruido de Poisson sumado a eventos que el calendario no
explica. Qué pasó en el corte 43 **no se investigó**.

`figuras/fig2_referencias_por_municipio.png` muestra la tabla de §3.3; `figuras/fig3_total_semanal_referencias.png`, el total
semanal observado contra tres referencias.

---

## 3b. Fase 2, paso A: conjuntos de variables (ventana expansiva) — sección 7 del notebook

### 3b.1 Qué se hizo y por qué

| Elemento | Decisión | Origen |
| --- | --- | --- |
| Familias | GLM Poisson (`statsmodels` GLM, enlace log, IRLS por defecto) y XGBoost (`count:poisson`, `max_depth=3`, `n_estimators=300`, `learning_rate=0.05`; resto por defecto de 3.4.1, `random_state=SEMILLA`, `n_jobs=1`) | Sección 1; adenda ítem 3 (D19); precisiones de la fase 2, ítem 5 |
| Conjuntos | (0) municipio + log(nivel reciente) + rezagos 7/14/21/28; (a) municipio + calendario; (b) (a) + término de A; (c) (b) + log(nivel reciente) | Sección 1; D34 |
| Matriz | 8 indicadoras de municipio sin constante; calendario 7 columnas (lunes de referencia); término de A 7 columnas (sin `a_x_lunes`); la misma para las dos familias | D31 |
| N del nivel reciente | {28, 56, 91} en (0) y (c), por desvianza media, por familia | Adenda ítem 2 (D18) |
| Variables | Sólo `src/variables.py`: `matriz_entrenamiento` (origen simulado; mismas filas para todos los conjuntos) y `variables_horizonte` | Etapa 1 |
| Elección del conjunto | Entre (a), (b), (c): 1 EE del mejor y simplicidad a < b < c; (0) reemplaza sólo si desv(elegido) − desv(0) > EE(0) | Adenda ítem 4 (D20); D32 |
| Registro | Una fila por configuración en `registro_experimentos.csv`, reescrito en cada ejecución | D33 |

16 configuraciones (2 familias × [3 de (0) + (a) + (b) + 3 de (c)]) × 47 cortes = 752 ajustes. Filas de entrenamiento por corte:
de 7.168 (896 días, primer corte) a 9.744 (1.218 días, último) (`tablas/16`). La verificación de D34 comprobó 1.200.192 valores de
nivel reciente, todos > 0 (salida de la sección 7).

### 3b.2 Resultados globales — `tablas/11_paso_a_globales.csv`, `figuras/fig4_paso_a_desvianza.png`

Ordenados por desvianza. «≤ 1 EE» = a menos de 1 error estándar de la mejor de la tabla (GLM (c) N=28: 1,2150 + 0,0363 = 1,2513).

| Configuración | Desvianza | EE | MAE | RMSE | Total pred./obs. | Peor mun. | Dif. vs L1 | Cortes que gana a L1 | ≤ 1 EE |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| GLM Poisson (c) N=28 | 1,2150 | 0,0363 | 1,3981 | 1,7826 | 0,9523 | E (1,4121) | −0,0169 | 38 | sí |
| GLM Poisson (c) N=56 | 1,2167 | 0,0363 | 1,3992 | 1,7840 | 0,9479 | E (1,4018) | −0,0152 | 37 | sí |
| GLM Poisson (c) N=91 | 1,2168 | 0,0364 | 1,3996 | 1,7841 | 0,9480 | E (1,4011) | −0,0151 | 35 | sí |
| XGBoost (b) | 1,2200 | 0,0362 | 1,3997 | 1,7888 | 0,9338 | E (1,3997) | −0,0119 | 32 | sí |
| GLM Poisson (b) | 1,2207 | 0,0362 | 1,3990 | 1,7876 | 0,9341 | E (1,3995) | −0,0111 | 35 | sí |
| **XGBoost (a)** — elegido | 1,2217 | 0,0361 | 1,3999 | 1,7900 | 0,9338 | E (1,4004) | −0,0102 | 31 | sí |
| XGBoost (c) N=28 | 1,2219 | 0,0370 | 1,4051 | 1,7894 | 0,9586 | E (1,4454) | −0,0100 | 29 | sí |
| XGBoost (c) N=56 | 1,2224 | 0,0382 | 1,4082 | 1,7893 | 0,9667 | E (1,4165) | −0,0095 | 29 | sí |
| XGBoost (c) N=91 | 1,2243 | 0,0373 | 1,4074 | 1,7919 | 0,9730 | E (1,4219) | −0,0075 | 27 | sí |
| **GLM Poisson (a)** — elegido | 1,2302 | 0,0359 | 1,4013 | 1,7951 | 0,9341 | E (1,4019) | −0,0017 | 36 | sí |
| *L1 (referencia)* | 1,2319 | 0,0358 | 1,4006 | 1,7960 | 0,9305 | E (1,4026) | 0 | — | **sí** |
| GLM Poisson (0) N=91 | 1,2757 | 0,0389 | 1,4264 | 1,8300 | 0,9529 | E (1,4803) | +0,0438 | 15 | no |
| GLM Poisson (0) N=28 | 1,2760 | 0,0389 | 1,4266 | 1,8303 | 0,9524 | E (1,4855) | +0,0441 | 15 | no |
| GLM Poisson (0) N=56 | 1,2769 | 0,0388 | 1,4255 | 1,8309 | 0,9485 | E (1,4814) | +0,0450 | 14 | no |
| XGBoost (0) N=28 | 1,2864 | 0,0395 | 1,4389 | 1,8396 | 0,9590 | C (1,5063) | +0,0546 | 14 | no |
| XGBoost (0) N=56 | 1,2866 | 0,0412 | 1,4392 | 1,8396 | 0,9675 | C (1,5311) | +0,0548 | 13 | no |
| XGBoost (0) N=91 | 1,2900 | 0,0402 | 1,4467 | 1,8445 | 0,9775 | C (1,5380) | +0,0581 | 14 | no |
| *L0 de 8 semanas (referencia)* | 1,3626 | 0,0414 | 1,4957 | 1,8958 | 1,0067 | E (1,6267) | +0,1308 | 9 | no |

Ninguna configuración produjo predicciones iguales a 0. Ningún ajuste emitió avisos; los 376 ajustes del GLM convergieron, con 5
iteraciones de IRLS cada uno (`tablas/16`; `registro_experimentos.csv`: `cortes_no_convergidos` 0 y `cortes_con_avisos` 0 en las 16 filas).

### 3b.3 Aplicación de la regla del ítem 4 — `tablas/14_paso_a_eleccion.csv`

| Paso | GLM Poisson | XGBoost |
| --- | --- | --- |
| N de (0) por desvianza media | **N=91** (1,2757; N=28 1,2760; N=56 1,2769) | **N=28** (1,2864; N=56 1,2866; N=91 1,2900) |
| N de (c) por desvianza media | **N=28** (1,2150; N=56 1,2167; N=91 1,2168) | **N=28** (1,2219; N=56 1,2224; N=91 1,2243) |
| Mejor entre (a), (b), (c) y umbral | (c) N=28, 1,2150 + 0,0363 = **1,2513** | (b), 1,2200 + 0,0362 = **1,2562** |
| Empatados (≤ umbral) | (a) 1,2302, (b) 1,2207, (c) 1,2150 | (a) 1,2217, (b) 1,2200, (c) 1,2219 |
| El más simple de los empatados | **(a)** | **(a)** |
| ¿(0) reemplaza? desv(a) − desv(0) > EE(0) | −0,0454 ≤ 0,0389: **no** | −0,0648 ≤ 0,0395: **no** |
| **Conjunto elegido** | **(a)** | **(a)** |

### 3b.4 Por municipio — `tablas/12_paso_a_por_municipio.csv`

Desvianza (el EE por municipio se calcula sobre los 47 cortes de 7 filas; `*` = a menos de 1 EE del mejor del municipio):

| Configuración | A | B | C | CH | D | E | F | G |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| GLM Poisson (a) | 1,2950* | 1,0879* | 1,3549* | 1,3344* | 1,1010* | 1,4019* | 1,0820* | 1,1844* |
| GLM Poisson (b) | 1,2388* | 1,0836* | 1,3484* | 1,3307* | 1,0991* | 1,3995* | 1,0818* | 1,1840* |
| GLM Poisson (c) N=28 | 1,2165* | 1,0870* | 1,3363* | 1,3277* | 1,0958* | 1,4121* | 1,0647* | 1,1796* |
| XGBoost (a) | 1,2511* | 1,0826* | 1,3449* | 1,3410* | 1,1068* | 1,4004* | 1,0658* | 1,1806* |
| XGBoost (b) | 1,2478* | 1,0833* | 1,3459* | 1,3408* | 1,1044* | 1,3997* | 1,0594* | 1,1785* |
| XGBoost (c) N=28 | 1,2285* | 1,0903* | 1,3573* | 1,3318* | 1,1021* | 1,4454* | 1,0511* | 1,1685* |
| L1 | 1,3017 | 1,0862* | 1,3530* | 1,3350* | 1,1036* | 1,4026* | 1,0856* | 1,1874* |
| L0 de 8 semanas | 1,3434 | 1,2221 | 1,5142 | 1,5155 | 1,1995 | 1,6267 | 1,2070 | 1,2727* |

(Las 18 filas, con MAE, EE y total pred./obs., en `tablas/12`.) Total predicho / observado de GLM (c) N=28: A 0,9001, B 1,0058,
C 0,9378, CH 1,0117, D 0,9685, E 0,9483, F 0,9160, G 0,9529; de L1: A 0,8641, F 0,8862 (§3.3).

### 3b.5 Dispersión de Pearson del GLM Poisson con el conjunto elegido — `tablas/15_paso_a_dispersion_pearson.csv`

χ² de Pearson / gl residuales del GLM Poisson (a), en el entrenamiento de cada uno de los 47 cortes: **mínimo 1,1035, mediana 1,1109,
máximo 1,1171** (primer corte 1,1100; último 1,1124).

### 3b.6 Lectura (espejo de la celda 7.1 del notebook)

**Evidencia.**
- En las dos familias, (a), (b) y (c) quedan a menos de 1 EE del mejor de los tres, y la regla elige **(a)** por simplicidad. (0) es
  peor que (a) en las dos familias y no reemplaza.
- **Por el criterio de 1 EE, ninguna configuración de (a), (b) o (c) se distingue de L1**: L1 queda dentro del umbral de la mejor
  configuración. GLM (a) queda a −0,0017 de L1 (*inferencia:* con nivel por municipio × calendario común, es la misma estructura
  que L1 ajustada por máxima verosimilitud); la mejor, GLM (c) N=28, a −0,0169, y le
  gana en 38 de 47 cortes.
- La elección de N cambia la desvianza a lo sumo en 0,0036, muy por debajo de 1 EE.

**¿(c) corrige la subestimación de L1 (0,9305)?** *Evidencia:* en parte. El total predicho / observado pasa de 0,9341 en GLM (a) a
0,9523 en GLM (c) N=28, y de 0,9338 en XGBoost (a) a entre 0,9586 y 0,9730 en XGBoost (c). Ninguna llega a 1. A sigue siendo el
municipio más subestimado (0,9001 en GLM (c) N=28, contra 0,8641 en L1). En desvianza, GLM (c) N=28 mejora a GLM (a) en 0,0152 y le gana
en 38 de 47 cortes, pero queda dentro de 1 EE; en XGBoost, (c) N=28 no mejora a (a) (+0,0002; gana en 26 de 47, conteo sobre `tablas/13`).
*Inferencia:* el nivel reciente absorbe parte de la tendencia, no toda; qué explica el resto no se investigó.

**¿El término de A aporta en el panel como en el diagnóstico?** *Evidencia:* en el GLM, sí en A y casi nada en el global. La desvianza
de A baja de 1,2950 con (a) a 1,2388 con (b), un **−4,34 %**. En el diagnóstico, el calendario propio mejoraba a A en 4,06 % y 4,24 %
(`resumen_diagnostico_municipios.md` §7.3). Son protocolos distintos, así que se compara la dirección y el orden de magnitud, no la
cifra. Globalmente, (b) mejora a (a) en 0,0095 (EE 0,0362) y le gana en 33 de 47 cortes. En XGBoost el término casi no cambia: A pasa de
1,2511 a 1,2478 y el global, de 1,2217 a 1,2200. *Inferencia:* XGBoost (a) ya modela A mejor que GLM (a) (1,2511 contra 1,2950), lo que
sugiere que los árboles encuentran la interacción municipio × calendario sin el término explícito.

**Inferencia general.** Con este protocolo y esta regla, ninguno de los bloques que motivó el diagnóstico (término de A, nivel reciente)
supera el umbral de 1 EE. El EE se calcula entre cortes y recoge las semanas difíciles que afectan a todos los modelos por igual; las
comparaciones corte a corte (38 de 47, 33 de 47) muestran diferencias más consistentes de lo que el umbral deja ver. La regla está fijada
y se aplicó como está.

### 3b.7 Verificación de fuga de los candidatos del paso A (19/10/2026, después de la parada A y antes del paso B)

Verificación hecha **fuera del repositorio**: un script en el directorio temporal de la sesión, que lee el panel con
`cargar_panel_desarrollo()` y ejecuta tal cual el código de la celda `paso-a-motor` del notebook. **No dejó ningún artefacto en el
repositorio**, así que sus cifras no tienen respaldo en `experiments/`: se citan como verificación del código, no como resultado del proyecto.

- **Diseño.** Para GLM Poisson (a), GLM Poisson (c) N=28, XGBoost (a) y XGBoost (c) N=28, en los cortes 1, 12, 24, 36 y 47 (orígenes
  2024-03-14, 2024-05-30, 2024-08-22, 2024-11-14 y 2025-01-30), se reentrenó y se predijo con tres versiones de los datos:
  (i) la vista del motor, con el objetivo de las fechas ≥ origen en NaN; (ii) el panel de desarrollo completo con el objetivo real sin
  ocultar; (iii) el panel completo con `n_siniestros` = 10⁶ en todas las fechas ≥ origen (entre 56 y 2.632 filas alteradas según el
  corte). La caché de matrices se vació antes de cada predicción.
- **Resultado.** Diferencia máxima entre predicciones: **0** entre (i) y (iii) y **0** entre (ii) y (iii), en las 20 combinaciones
  (4 configuraciones × 5 cortes). Las predicciones de (i) coinciden con las guardadas en `tablas/17` (diferencia 0 al redondear a 6 decimales).
- **Control de que la prueba detecta una fuga.** Con la compuerta `var.observado` abierta en memoria (devuelve todo el panel), en el
  corte 12 la diferencia (i)–(iii) es **88,69 en GLM (c) N=28 y 1,006 en XGBoost (c) N=28**: la prueba detecta la fuga. En las dos
  configuraciones (a) la diferencia sigue en 0, como se espera: (a) no tiene ninguna variable derivada del objetivo, y las filas de
  entrenamiento se acotan a fechas < origen por construcción (`matriz_entrenamiento`), no por la compuerta.

---

## 3c. Fase 2, paso B: hiperparámetros de XGBoost y binomial negativa (ventana expansiva) — sección 8 del notebook

### 3c.1 Qué se hizo y por qué

| Elemento | Decisión | Origen |
| --- | --- | --- |
| Conjunto | (a) en las dos familias, tomado de la elección del paso A | §3b.3 |
| XGBoost | Las 12 combinaciones de la grilla (`max_depth` {2, 3, 4} × `n_estimators` {100, 300} × `learning_rate` {0,05; 0,1}); resto fijo | Sección 1; ítem 5 de las precisiones |
| NB2 | `NegativeBinomial(loglike_method="nb2").fit(method="newton", maxiter=100)`, α por máxima verosimilitud en cada corte; no convergido según D29 → plan B (D28) en ese corte; si el α por momentos no fuera positivo, la ejecución se detiene (caso no cubierto) | Adenda, ítems 5 y 6 |
| Selección | Familia GLM = GLM Poisson (a) + NB2 (a); familia XGBoost = 12 combinaciones. Regla de la sección 1 con D36 (Poisson antes que NB2), D37 (menor `max_depth`, luego menor `n_estimators`) y D38 (paso 4 lexicográfico con tolerancia de 1 EE) | Sección 1; precisiones del paso B |
| Control | La combinación (3, 300, 0,05) es la del paso A: se reevaluó y reprodujo exactamente sus predicciones (`assert` en la sección 8) | — |

Código: la rama NB2 (`ajustar_nb2`) se agregó a la celda del motor de la sección 7, para tener una sola fábrica de modelos; las ramas de GLM
Poisson y XGBoost no cambiaron y las tablas del paso A quedaron idénticas.

### 3c.2 NB2 contra GLM Poisson — `tablas/21_paso_b_nb2_por_corte.csv`, `22_paso_b_nb2_vs_poisson.csv`

| Medida | Valor |
| --- | --- |
| Desvianza GLM Poisson (a) / NB2 (a) | 1,2302 / 1,2301 (diferencia −0,000098; EE 0,0359 en los dos) |
| Cortes en que NB2 gana a Poisson | 27 de 47 |
| Diferencia máxima entre predicciones | 0,0071 siniestros (0,18 % relativo) |
| **α por máxima verosimilitud** (47 cortes) | **mínimo 0,0349, mediana 0,0377, máximo 0,0400** (primer corte 0,0383; último 0,0379) |
| Convergencia | 47 de 47 según D29, 4 iteraciones de Newton cada uno, sin avisos |
| **Cortes con plan B** | **0** |

### 3c.3 Resultados globales — `tablas/18_paso_b_globales.csv`, `figuras/fig5_paso_b_desvianza.png`

Ordenados por desvianza. «≤ 1 EE fam.» = a menos de 1 EE del mejor de su familia (GLM: 1,2301 + 0,0359 = 1,2660; XGBoost:
1,2197 + 0,0358 = 1,2555). Todas las filas, salvo XGBoost d=2 n=100 lr=0,05 y L0, quedan además a menos de 1 EE del mejor de la tabla.

| Configuración | Desvianza | EE | Total pred./obs. | Peor mun. | Desvío entre cortes | Dif. vs L1 | Cortes que gana a L1 | ≤ 1 EE fam. |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| XGBoost d=4 n=300 lr=0,05 | 1,2197 | 0,0358 | 0,9339 | E (1,4002) | 0,2455 | −0,0122 | 31 | sí |
| XGBoost d=2 n=300 lr=0,1 | 1,2202 | 0,0360 | 0,9339 | E (1,4035) | 0,2468 | −0,0117 | 33 | sí |
| XGBoost d=4 n=100 lr=0,1 | 1,2204 | 0,0362 | 0,9338 | E (1,3975) | 0,2483 | −0,0115 | 31 | sí |
| XGBoost d=3 n=300 lr=0,1 | 1,2211 | 0,0358 | 0,9339 | E (1,4036) | 0,2453 | −0,0108 | 29 | sí |
| XGBoost d=3 n=300 lr=0,05 (= paso A) | 1,2217 | 0,0361 | 0,9338 | E (1,4004) | 0,2476 | −0,0102 | 31 | sí |
| XGBoost d=4 n=300 lr=0,1 | 1,2223 | 0,0356 | 0,9340 | E (1,4036) | 0,2441 | −0,0096 | 29 | sí |
| XGBoost d=3 n=100 lr=0,1 | 1,2264 | 0,0366 | 0,9337 | E (1,3975) | 0,2510 | −0,0054 | 29 | sí |
| XGBoost d=2 n=300 lr=0,05 | 1,2276 | 0,0368 | 0,9337 | E (1,4016) | 0,2521 | −0,0042 | 27 | sí |
| XGBoost d=4 n=100 lr=0,05 | 1,2290 | 0,0374 | 0,9336 | E (1,3935) | 0,2562 | −0,0029 | 26 | sí |
| NB2 (a) | 1,2301 | 0,0359 | 0,9341 | E (1,4020) | 0,2464 | −0,0018 | 33 | sí |
| **GLM Poisson (a)** — elegido | 1,2302 | 0,0359 | 0,9341 | E (1,4019) | 0,2464 | −0,0017 | 36 | sí |
| *L1 (referencia)* | 1,2319 | 0,0358 | 0,9305 | E (1,4026) | 0,2456 | 0 | — | — |
| **XGBoost d=2 n=100 lr=0,1** — elegido | 1,2375 | 0,0375 | 0,9336 | E (1,4024) | 0,2573 | **+0,0056** | **20** | sí |
| XGBoost d=3 n=100 lr=0,05 | 1,2443 | 0,0380 | 0,9335 | C (1,4096) | 0,2607 | +0,0124 | 17 | sí |
| XGBoost d=2 n=100 lr=0,05 | 1,2671 | 0,0396 | 0,9332 | C (1,4781) | 0,2711 | +0,0353 | 10 | **no** |
| *L0 de 8 semanas (referencia)* | 1,3626 | 0,0414 | 1,0067 | E (1,6267) | 0,2839 | +0,1308 | 9 | — |

611 ajustes nuevos (13 configuraciones × 47 cortes), ninguno con avisos (`tablas/24`); ninguna predicción igual a 0.

### 3c.4 Aplicación de la regla — `tablas/23_paso_b_eleccion.csv`

| Paso | Familia GLM | Familia XGBoost |
| --- | --- | --- |
| 1. Mejor desvianza | NB2 (a), 1,2301 | d=4 n=300 lr=0,05, 1,2197 |
| 2. Empatadas (≤ 1 EE) | NB2 (a) y GLM Poisson (a) (umbral 1,2660) | 11 de 12 (umbral 1,2555; afuera solo d=2 n=100 lr=0,05) |
| 3. Simplicidad | D36: **GLM Poisson (a)** | D37: profundidad 2 → {n=100 lr=0,1; n=300 lr=0,05; n=300 lr=0,1}; 100 árboles → **d=2 n=100 lr=0,1** |
| 4. Estabilidad y calibración (D38) | no se aplica (el paso 3 deja una) | no se aplica (el paso 3 deja una) |
| **Elegida** | **GLM Poisson (a)** (1,2302) | **XGBoost (a) d=2 n=100 lr=0,1** (1,2375) |

### 3c.5 Por municipio — `tablas/19_paso_b_por_municipio.csv`

Desvianza y total predicho / observado de las dos elegidas, de la mejor combinación de XGBoost en desvianza y de L1:

| Configuración | A | B | C | CH | D | E | F | G |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| GLM Poisson (a) — desvianza | 1,2950 | 1,0879 | 1,3549 | 1,3344 | 1,1010 | 1,4019 | 1,0820 | 1,1844 |
| XGBoost d=2 n=100 lr=0,1 — desvianza | 1,2894 | 1,1036 | 1,4024 | 1,3553 | 1,1332 | 1,4024 | 1,0469 | 1,1670 |
| XGBoost d=4 n=300 lr=0,05 — desvianza | 1,2360 | 1,0799 | 1,3405 | 1,3416 | 1,1028 | 1,4002 | 1,0697 | 1,1867 |
| L1 — desvianza | 1,3017 | 1,0862 | 1,3530 | 1,3350 | 1,1036 | 1,4026 | 1,0856 | 1,1874 |
| GLM Poisson (a) — total pred./obs. | 0,8695 | 1,0018 | 0,9138 | 1,0049 | 0,9589 | 0,9328 | 0,8897 | 0,9277 |
| XGBoost d=2 n=100 lr=0,1 — total pred./obs. | 0,8378 | 0,9520 | 0,8720 | 1,0727 | 0,9121 | 0,9943 | 0,9404 | 0,9863 |
| XGBoost d=4 n=300 lr=0,05 — total pred./obs. | 0,8679 | 0,9989 | 0,9103 | 1,0104 | 0,9545 | 0,9386 | 0,8909 | 0,9315 |

### 3c.6 Lectura (espejo de la celda 8.1 del notebook)

**Evidencia.**
- NB2 y GLM Poisson dan prácticamente la misma predicción (diferencia máxima 0,0071; desvianza 1,2301 contra 1,2302); α va de 0,0349 a
  0,0400 y ningún corte usó el plan B. D36 elige GLM Poisson (a).
- En XGBoost, 11 de las 12 combinaciones quedan a menos de 1 EE de la mejor, y D37 elige la más simple, **d=2 n=100 lr=0,1**. Su
  desvianza (1,2375) es la décima de las doce y **está por encima de L1 (+0,0056)**; le gana a L1 en 20 de 47 cortes.
- Su total predicho / observado por municipio va de 0,8378 (A) a 1,0727 (CH), un rango más amplio que el de GLM Poisson (a) (0,8695 a 1,0049)
  y el de d=4 n=300 lr=0,05 (0,8679 a 1,0104) (`tablas/19`).

**Inferencia.**
- Con α ≈ 0,04 la media de NB2 es casi la de Poisson: su aporte posible está en los intervalos y en la inferencia (sección 1, D36), no en la
  desvianza. La sobredispersión es moderada, coherente con la dispersión de Pearson del paso A.
- La grilla de XGBoost tiene una meseta (seis combinaciones entre 1,2197 y 1,2223). Las combinaciones de 100 árboles con lr = 0,05 son las
  peores de cada profundidad, y la elegida reparte el nivel entre municipios de forma menos pareja. Eso **sugiere** que con 100 árboles y
  profundidad 2 el modelo todavía no terminó de ajustar los niveles por municipio. No se verificó.
- La elección es consecuencia directa de la regla fijada: un 1 EE amplio más la simplicidad de D37. No es un error de cálculo. Que la «mejor
  de XGBoost» del paso B tenga mayor desvianza media que L1 es un resultado incómodo, y queda reportado como tal.

---

## 4. Qué NO se hizo todavía

- ~~Pasos A y B~~ — **hechos** (§3b y §3c).
- **PENDIENTE:** paso C (ventanas expansiva y deslizantes de 364, 546 y 728 días para GLM Poisson (a) y XGBoost (a) d=2 n=100 lr=0,1);
  selección del modelo final (fase 3).
- **PENDIENTE:** evaluación en el test (una sola vez, con la solución ya fijada).
- La ventana deslizante está **implementada y comprobada estructuralmente** (364 días exactos en cada corte; `tablas/03`), pero
  **ninguna referencia se evaluó con ella**.

---

## 5. Limitaciones

- **Las referencias se evalúan con los mismos 47 cortes con los que se elegirá el candidato** (sesgo declarado en §1.1): la
  validación del ganador será optimista; la comparación contra referencias, no tanto, porque todas pasan por lo mismo.
- **La revisión de la ventana de L0 usa validación.** Es la revisión que el protocolo pidió; elegir entre las tres usa los
  mismos cortes. El test no interviene.
- **El error estándar sobre 47 cortes ignora la dependencia entre cortes** vecinos (nivel que deriva, semanas difíciles
  consecutivas); es el que fijó la regla de selección, no uno pareado entre modelos.
- **L1 subestima el volumen (0,9305)** por la tendencia creciente; no es un defecto del código sino de un nivel histórico fijo.
- **Mismas limitaciones de datos** que `resumen_diagnostico_municipios.md` §9: subregistro, sin exposición, causas no
  investigadas.
- **Paso A: el umbral de 1 EE es amplio frente a las diferencias entre conjuntos.** Los EE rondan 0,036 y las diferencias entre
  (a), (b) y (c), 0,002 a 0,015; con esta regla los conjuntos anidados no se distinguen entre sí ni de L1. Es una propiedad de la
  regla fijada (EE entre cortes, no pareado), no un hallazgo sobre los datos.
- **Paso A: la elección de N, del conjunto y de la L0 usan los mismos 47 cortes** (sesgo declarado en §1.1).

**Frases que NO deben aparecer en el informe**

| Frase | Por qué los datos no la sostienen |
| --- | --- |
| «El modelo final mejora a la línea base en X %» | No hay modelo final: el paso A elige un conjunto por familia; faltan los pasos B y C y la fase 3 |
| «Los candidatos mejoran a L1» / «GLM (c) supera a L1» | Por el criterio de 1 EE, ninguna configuración de (a), (b) o (c) se distingue de L1 (`tablas/11`). Lo que sí puede decirse: GLM (c) N=28 tiene menor desvianza media (1,2150 contra 1,2319) y le gana en 38 de 47 cortes |
| «El nivel reciente corrige la subestimación» | La corrige en parte: el total pred./obs. pasa de 0,9341 (GLM (a)) a 0,9523 (GLM (c) N=28); ninguna configuración llega a 1 y A queda en 0,9001 |
| «El término de A no aporta» | En el GLM mejora la desvianza de A en 4,34 % (1,2950 → 1,2388); lo que no supera es el umbral de 1 EE en el global |
| «Se eligió (a) porque es el mejor» | Se eligió por **simplicidad** entre empatados a menos de 1 EE; en desvianza media, (a) es el peor de los tres en el GLM y el segundo en XGBoost |
| «Los rezagos semanales aportan» | El conjunto (0) (rezagos + nivel reciente, sin calendario) es peor que L1 en las dos familias (+0,0438 a +0,0581) |
| «El GLM Poisson está sobredispersado de forma importante» | La dispersión de Pearson del GLM (a) va de 1,1035 a 1,1171 (`tablas/15`): sobredispersión moderada |
| «La binomial negativa mejora la predicción» | NB2 (a) 1,2301 contra GLM Poisson (a) 1,2302; las predicciones difieren como mucho en 0,0071 (`tablas/22`) |
| «Se eligió la mejor combinación de XGBoost» | Se eligió la **más simple** de las 11 empatadas (D37). En desvianza es la décima de 12 y queda por encima de L1 (1,2375 contra 1,2319, `tablas/18`) |
| «XGBoost supera a L1» | La XGBoost elegida en el paso B tiene mayor desvianza media que L1 y le gana en 20 de 47 cortes; la mejor de la grilla (1,2197) queda a menos de 1 EE de L1 |
| «La NB2 tuvo problemas de convergencia» / «se usó el plan B» | Los 47 cortes convergieron según D29; ningún corte usó el plan B (`tablas/21`) |
| «La línea base es L0 de 4 semanas» (con estas cifras) | Con 2.632 predicciones, L0 de 4 semanas (1,5210) queda por detrás de la media constante (1,3967); la L0 que pasa a la comparación es la de 8 semanas (adenda del 19/10/2026) |
| «La L0 de 8 semanas se fijó antes de ver los resultados» | Se eligió mirando los 47 cortes de validación (`tablas/05`), después de fijar la lista; la adenda lo declara. «Es mejor que la media constante» tampoco: la diferencia (0,0341) es menor que 1 error estándar (0,0447, `tablas/08`) |
| «L1 es el mejor modelo del proyecto» | Es la mejor **referencia**; no compitió con ningún candidato |
| «El calendario de 8 niveles explica la mayor parte de la variación» | L1 mejora sobre la media constante (1,2319 contra 1,3967), pero la desvianza sigue por encima de 1 |
| «El test confirma…» / cualquier cifra del test | El test no se leyó |
| «La lluvia no sirve» | Se dejó fuera por **no estar disponible** a 7 días y por no aportar fuera de muestra (§7.5 del diagnóstico); no se probó en este notebook |
| «Estas cifras coinciden con las del Entregable 2» | Aquéllas son de una serie (MUNICIPIO C) con bloque final; éstas, de ocho municipios y sólo desarrollo. Lo que coincide es el **motor**, en el control del §1.4 |
| «L0 de 2 semanas es una referencia razonable» | Produce 27 predicciones cero y una desvianza de 2,4384 |

---

## 6. Índice de artefactos

| Afirmación | Respaldo |
| --- | --- |
| Entorno (versiones) | `tablas/00_entorno.csv` |
| Integridad del panel; ninguna fila de test | `tablas/01_verificacion_integridad.csv` |
| Particiones 987 / 329; test «no cargado» | `tablas/02_particiones.csv` |
| El motor oculta el futuro; ventanas expansiva y deslizante | `tablas/03_comprobacion_motor.csv` |
| El motor reproduce `linea_base` (MUNICIPIO C) | `tablas/04_control_cruzado_municipio_c.csv` |
| Métricas globales de las 5 referencias | `tablas/05_referencias_globales.csv` |
| Métricas por municipio | `tablas/06_referencias_por_municipio.csv`; `figuras/fig2_referencias_por_municipio.png` |
| Métricas por corte | `tablas/07_referencias_por_corte.csv`; `figuras/fig1_referencias_por_corte.png` |
| Error estándar sobre 47 cortes, estabilidad, ≤ 1 EE del mejor | `tablas/08_referencias_error_estandar_y_estabilidad.csv` |
| Predicciones por corte, día y municipio (13.160 filas = 5 × 2.632) | `tablas/09_predicciones_referencias.csv` |
| Total semanal observado y predicho | `figuras/fig3_total_semanal_referencias.png` |
| Listado | `tablas/10_artefactos.csv` |
| Paso A: métricas globales, EE, comparación con L1 y L0 de 8 semanas, marca de 1 EE | `tablas/11_paso_a_globales.csv`; `figuras/fig4_paso_a_desvianza.png` |
| Paso A: por municipio, con EE y marca de 1 EE por municipio | `tablas/12_paso_a_por_municipio.csv` |
| Paso A: métricas por corte (conteos de cortes ganados) | `tablas/13_paso_a_por_corte.csv` |
| Paso A: elección de N y del conjunto por familia, paso por paso | `tablas/14_paso_a_eleccion.csv` |
| Paso A: dispersión de Pearson del GLM Poisson (a) | `tablas/15_paso_a_dispersion_pearson.csv` |
| Paso A: convergencia, avisos, filas de entrenamiento y dispersión por ajuste (752) | `tablas/16_paso_a_ajustes_por_corte.csv` |
| Paso A: predicciones por corte, día y municipio (42.112 filas = 16 × 2.632) | `tablas/17_paso_a_predicciones.csv` |
| Paso B: métricas globales, EE, comparación con L1 y L0, marca de 1 EE (tabla y familia GLM / XGBoost) | `tablas/18_paso_b_globales.csv`; `figuras/fig5_paso_b_desvianza.png` |
| Paso B: por municipio, con EE y marca de 1 EE por municipio | `tablas/19_paso_b_por_municipio.csv` |
| Paso B: métricas por corte | `tablas/20_paso_b_por_corte.csv` |
| Paso B: NB2 por corte (convergencia, iteraciones, α, plan B, avisos) | `tablas/21_paso_b_nb2_por_corte.csv` |
| Paso B: NB2 contra GLM Poisson (desvianza, cortes ganados, diferencia de predicciones, rango de α) | `tablas/22_paso_b_nb2_vs_poisson.csv` |
| Paso B: regla de selección por familia, paso por paso | `tablas/23_paso_b_eleccion.csv` |
| Paso B: convergencia y avisos por ajuste (611) | `tablas/24_paso_b_ajustes_por_corte.csv` |
| Paso B: predicciones de NB2 y de las 12 combinaciones (34.216 filas = 13 × 2.632) | `tablas/25_paso_b_predicciones.csv` |
| Una fila por configuración evaluada (fase 2; 29 filas tras el paso B) | `registro_experimentos.csv` |

---

## 7. Qué queda pendiente

1. **Candidatos.** ~~Paso A~~ — **hecho** el 19/10/2026 (§3b): conjunto elegido **(a)** en las dos familias. ~~Paso B~~ — **hecho** el
   19/10/2026 (§3c): GLM Poisson (a) y XGBoost (a) d=2 n=100 lr=0,1. **Pendiente:** paso C (ventanas para esas dos configuraciones).
2. ~~Decidir qué L0 se lleva a la comparación final~~ — **cerrado** el 19/10/2026: 8 semanas (adenda de §1.1, precisión 1).
3. ~~Precisar cómo entra el nivel reciente en el conjunto (0)~~ — **cerrado** el 19/10/2026: N ∈ {28, 56, 91} por familia
   (adenda de §1.1, precisión 2).
4. Selección con la regla fijada, evaluación en el test **una sola vez**, explicabilidad, análisis de errores y prototipo.
5. Actualizar `resumen_linea_base.md`: su L0 de 4 semanas y sus cifras son de una sola serie; en el panel la referencia
   cambia (esta etapa).

---

## 8. Cambios posteriores a la primera versión de este documento (19/10/2026, review R1)

La review R1 (`documentacion/reviews/E3_fase_0-1.md`, veredicto DESAPROBADA por un criterio bloqueante) motivó estos cambios. Quien
cite este documento debe saber qué cubría antes:

- **Adenda a la sección 1** (§1.1): precisiones D17 a D20, D27 y D28, fijadas antes de ejecutar candidatos. Antes, este documento
  dejaba pendiente cuál L0 pasa a la comparación y cómo entra N en (0); ya no.
- **Código:** se borró código muerto del notebook (`exp_dias`), `modelo_L1` usa `var.nivel_municipio` en lugar de un cálculo propio y
  la celda de imports filtra el aviso `DeprecationWarning` de `pd.Timedelta` (pandas 2.3.3 con numpy 2.5.2). `modelo_media_constante`
  no cambió, y así queda por decisión del equipo (19/10/2026): la sección 1 fija la media constante **global**, no un nivel por
  municipio, así que no corresponde que use `var.nivel_municipio`. El factor de calendario de L1 sigue en el notebook y no en `src/` (deuda aceptada
  hasta la fase 5).
- **Redacción:** la carga del test se describe ahora como «ninguna fila del test se conserva ni se acumula; cada tramo se lee y se
  filtra antes de acumularse» (antes decía que no llegaba a memoria, lo cual no es exacto: cada tramo se lee completo y recién
  después se filtra).
- **Verificación de que nada numérico cambió:** reejecutado el notebook, los 14 artefactos de `experiments/modelos_candidatos/` son
  idénticos a los anteriores (`git hash-object --path` contra el índice); `pytest` 15 pasados, 0 saltados. Las cifras de §3 siguen
  respaldadas por las mismas tablas.

### Fix de la ronda 2 de R1 (19/10/2026)

La ronda 2 de la review (`documentacion/reviews/E3_fase_0-1_r2.md`, veredicto APROBADA CON OBSERVACIONES; falló solo el criterio no
bloqueante N2) motivó este cambio, que es **solo de documentación**:

- **Adenda, ítem 6 nuevo (D29):** criterio de convergencia de NB2, agregado antes de ejecutar candidatos y marcado como tal en la celda
  del notebook y en la fila 6 de §1.1. La sección 1 y los ítems 1 a 5 de la adenda no se tocaron. El texto de apertura de la celda de la
  adenda sigue diciendo «cinco precisiones»: se dejó así a propósito, para no editar lo ya commiteado; el ítem 6 aclara que es posterior.
- **Notebook no reejecutado:** el cambio es una celda de texto, no cambia ninguna salida. Los 14 artefactos de
  `experiments/modelos_candidatos/` no se tocaron (`git diff --stat experiments/` vacío).
- **Antes de fijar el criterio** se comprobó, con datos sintéticos generados en memoria (no el panel) y statsmodels 0.14.6, que
  `NegativeBinomial(..., loglike_method="nb2").fit(method="newton", maxiter=100)` es una llamada válida, que el resultado trae
  `mle_retvals["converged"]` y que `params` termina en el parámetro `alpha`. Esa comprobación no es un resultado del proyecto y no se cita como tal.

### Fase 2, paso A (19/10/2026)

- **Antes de ejecutar** se fijaron las precisiones D31 a D34 y el ítem 5 (§1.1), en el commit `2936c72`, separado del código del paso A.
- **Notebook:** sección 7 nueva (paso A), a continuación de la sección 6. «Estado y artefactos» pasó de sección 7 a **sección 10**
  (las 8 y 9 quedan para los pasos B y C), con el texto actualizado; su celda de índice ahora lista también `registro_experimentos.csv`.
  Al encabezado se le agregó un párrafo sobre la fase 2. Las secciones 0 a 6, la sección 1, la adenda y las precisiones no cambiaron.
- **Primera ejecución fallida** por un error de la figura 4 (`ecolor` no acepta una serie de colores); se corrigió el código de la
  figura (sin tocar el cálculo) y se reejecutó. Las tablas 11 a 16 de las dos ejecuciones son idénticas byte a byte, y el registro
  también lo es salvo `fecha_hora`: el paso A es determinista.
- **La celda de lectura 7.1** (texto) se agregó después de la ejecución, sin reejecutar: no cambia ninguna salida.

### Fase 2, paso B (19/10/2026)

- **Antes de ejecutar** se fijaron D36 a D38 (§1.1), en el commit `624b7e3`, y se hizo la verificación de fuga del §3b.7.
- **Código:** la rama NB2 (`ajustar_nb2`) se agregó a la celda del motor de la sección 7, junto con `hiper` en `META` y el conteo de
  `cortes_plan_b` del registro. Las ramas de GLM Poisson y XGBoost no cambiaron: al reejecutar, las tablas 11 a 17 quedaron idénticas y
  las 16 filas del paso A en el registro son iguales salvo `fecha_hora`. Sección 8 nueva; «Estado y artefactos» (sección 10) actualizada.
- **La celda de lectura 8.1** (texto) se agregó después de la ejecución, sin reejecutar: no cambia ninguna salida.
