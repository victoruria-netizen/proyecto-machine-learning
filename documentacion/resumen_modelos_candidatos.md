# Resumen de modelos candidatos — protocolo en el panel y referencias (Etapa 1 del Entregable 3)

**Notebook:** [`notebooks/modelos_candidatos.ipynb`](../notebooks/modelos_candidatos.ipynb)
**Artefactos:** `experiments/modelos_candidatos/` (11 tablas CSV en `tablas/` y 3 figuras PNG en `figuras/`)
**Código que usa:** `src/variables.py`, `src/datos.py`; pruebas en `tests/test_variables.py`
**Fecha de ejecución:** 2026-10-14 (`jupyter nbconvert --execute --inplace` en el `.venv`; 0 errores; entorno en
`tablas/00_entorno.csv`)
**Alcance:** los **ocho municipios** de Montevideo, **sólo el bloque de desarrollo (2021-07-01 → 2025-02-05,
1.316 días)**; 987 días de entrenamiento inicial y 329 de validación en 47 cortes de 7 días.

> ### ⚠️ Estado: este documento cubre sólo protocolo y referencias
>
> **Los modelos candidatos (GLM Poisson, GLM binomial negativa, XGBoost) y las etapas A, B y C de la
> experimentación NO se ejecutaron.** Todo lo que dependa de ellos está marcado
> `<!-- PENDIENTE -->`. Nada de este documento permite afirmar qué modelo se elegirá ni cuánto mejora sobre la
> línea base.
>
> **El test no se lee.** El bloque final (2025-02-06 → 2025-12-31) no se carga en ningún código de este
> notebook: `src.datos.cargar_panel_desarrollo()` recorta cada tramo del CSV a `fecha <= 2025-02-05` antes de
> acumularlo y hay `assert` que verifican que no quedó ninguna fila posterior. El límite sale del calendario
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
4. **Respetar la sección 6** («frases que no deben aparecer en el informe»).
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

**Pendiente de precisión para la etapa de candidatos.** Los conjuntos (0) y (c) dicen «nivel reciente» sin fijar N en (0);
(c) lo fija en 28/56/91. Cómo entra N en (0) se resuelve antes de ejecutar los candidatos.

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
§5.3). **Decisión pendiente (del equipo):** cuál L0 se lleva a la comparación final. En el Entregable 2 la referencia era
la de 4 semanas; con estos números la de 8 semanas es la mejor de las tres.

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

## 4. Qué NO se hizo en esta etapa

- **PENDIENTE:** GLM Poisson, GLM binomial negativa y XGBoost; conjuntos (0), (a), (b), (c); etapas A, B y C; dispersión de
  Pearson y α; selección del modelo final; comparación de ventanas (364, 546, 728 días contra la expansiva).
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

**Frases que NO deben aparecer en el informe**

| Frase | Por qué los datos no la sostienen |
| --- | --- |
| «El modelo final mejora a la línea base en X %» | No hay modelo final: los candidatos no se ejecutaron |
| «La línea base es L0 de 4 semanas» (con estas cifras) | Con 2.632 predicciones, L0 de 4 semanas (1,5210) queda por detrás de la media constante (1,3967); la elección de L0 está **pendiente** |
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

---

## 7. Qué queda pendiente

1. **Candidatos** (etapa siguiente): conjuntos (0), (a), (b), (c) con GLM Poisson y XGBoost por defecto; grilla de XGBoost y
   binomial negativa; ventanas para los dos mejores. Sobre el motor y las referencias de este notebook, sin tocarlos.
2. **Decidir qué L0 se lleva a la comparación final** (§3.1).
3. Precisar cómo entra el nivel reciente en el conjunto (0) (§1.1).
4. Selección con la regla fijada, evaluación en el test **una sola vez**, explicabilidad, análisis de errores y prototipo.
5. Actualizar `resumen_linea_base.md`: su L0 de 4 semanas y sus cifras son de una sola serie; en el panel la referencia
   cambia (esta etapa).
