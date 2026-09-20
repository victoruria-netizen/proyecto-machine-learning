# Resumen del modelo base y el protocolo de evaluación — MUNICIPIO C

**Notebook:** [`notebooks/base.ipynb`](../notebooks/base.ipynb)
**Artefactos:** `experiments/base/` (12 tablas CSV, 7 figuras PNG)
**Salida:** ninguna a `data/processed/` (el notebook sólo consume el panel del ETL)
**Fecha de ejecución:** 2026-09-20 (reejecución en el entorno estandarizado; las cifras no cambiaron
respecto de la corrida del 2026-09-10, ver la nota de reejecución, más abajo)
**Alcance:** una única serie diaria — **MUNICIPIO C** (municipio con más siniestros
registrados), 2021-07-01 a 2025-12-31, 1.645 días

---

## 0. Cómo usar este documento

Este archivo es **contexto autocontenido** para redactar las secciones *Metodología —
diseño de evaluación* y *Línea base* del informe (guía PAA 6.2) sin abrir el repositorio.
Reúne el protocolo que este notebook fija, la línea base que construye, y la referencia al
artefacto que respalda cada cifra.

**Reglas que quien redacte debe respetar:**

1. **Ninguna cifra sin artefacto.** Todos los números salen de la ejecución del 2026-09-20
   (idénticos a los de la corrida del 2026-09-10) y llevan al lado la tabla que los respalda (`tablas/NN_nombre.csv`). Si hace falta un
   número que no está acá, marcarlo como `<!-- PENDIENTE: ... -->`.
2. **Distinguir evidencia de inferencia.** «Los resultados muestran X» y «el equipo
   concluye Y» son afirmaciones distintas.
3. **No escribir Introducción ni Marco teórico** a partir de este documento.
4. **Respetar los límites de la sección 6.** Hay afirmaciones que este notebook *no*
   sostiene, listadas explícitamente.

**Documentos hermanos:**
[`resumen_diagnostico_datos.md`](resumen_diagnostico_datos.md) (calidad, cobertura,
adecuación) y [`resumen_preparacion_montevideo.md`](resumen_preparacion_montevideo.md)
(ETL). Las decisiones de métrica, forma de la línea base y tendencia se **justifican con
evidencia** allá; acá se **aplican** sobre una serie y se dejan los artefactos.

> ### ⚠️ Este notebook trabaja una sola serie, a propósito
>
> `panel_zona_top.csv` es la serie de **un** municipio. Sirve para **fijar el protocolo y
> la línea base** sobre un caso simple. **Sus métricas no son las del proyecto:** el
> diagnóstico mostró que los 8 municipios se parecen mucho entre sí (razón máx/mín
> 1,71×), y la evaluación seria —panel de 8 municipios con métricas desagregadas— es el
> notebook siguiente. Nada de lo que sigue permite afirmar que un modelo «generaliza».

> ### Reejecución del 2026-09-20 en el entorno estandarizado
>
> El notebook se reejecutó de punta a punta (`jupyter nbconvert --execute`) en un entorno nuevo,
> fijado en `requirements.txt` y `requirements-lock.txt`. **Ninguna cifra cambió:** las 12 tablas y
> las 7 figuras quedaron idénticas byte a byte respecto de las salidas anteriores (comparación
> contra una copia previa). Versiones que imprime el notebook (§0, salida de la celda; este
> notebook no las guarda en una tabla): Python 3.13.15, pandas 2.3.3, NumPy 2.5.2, matplotlib
> 3.11.1 y scikit-learn 1.9.0. Antes había corrido con Python 3.14.7 y pandas 3.0.5. La lógica del
> notebook no se tocó.

---

## 1. Qué hace el notebook y por qué

Cumple los tres puntos que la guía pide para el Entregable 2, en este orden:

| Punto de la guía | Sección del notebook |
| --- | --- |
| Protocolo de evaluación válido: particiones, validación, métricas, sin fugas | §5, §6, §4 |
| Conjunto de prueba reservado, no usado para ajustar ni seleccionar | §5, §9 |
| Línea base adecuada + interpretación de resultados preliminares | §7, §10 |

### Decisiones tomadas, con su motivo

| Decisión | Motivo | De dónde sale |
| --- | --- | --- |
| **Métrica principal: desvianza de Poisson media** | El objetivo es un conteo con sobredispersión leve (índice 1,26). La desvianza pondera el error por el nivel; el MAE no. | `resumen_diagnostico_datos.md` §5.1 |
| Acompañan **MAE, RMSE, razón total predicho/observado y sesgo medio** | Lectura operativa (MAE), sensibilidad a errores grandes (RMSE), calibración (razón, sesgo). | — |
| **Partición cronológica 80 / 20**, el 20 % final reservado | En una serie temporal no se parte al azar: entrenar con el pasado, evaluar sobre el futuro. | Ejemplo del curso; guía 6.2 |
| **Validación interna por ventana deslizante** (origen móvil, ventana expansiva) | Evaluar configuraciones sin tocar el test; simula el uso operativo. | Ejemplo del curso (`backtesting_forecaster`, `refit=True`) |
| **Horizonte de 7 días**, cortes no solapados | Horizonte operativo semanal (planificación de recursos). | — |
| **Línea base del proyecto = tasa × factor de calendario** | Forma multiplicativa que el diagnóstico midió como la mejor disponible fuera de muestra (−11,8 % en el panel). Con una sola zona se reduce a las medias por `tipo_dia`. | `resumen_diagnostico_datos.md` §5.3 |
| **Modelo base aprendido = árbol de decisión básico** (`DecisionTreeRegressor`, `max_depth=4`, `min_samples_leaf=20`) | El ejemplo del curso usa árboles (`RandomForestRegressor`); acá se usa su forma más simple, un único árbol poco profundo. Variables: rezagos `t−7/14/21`, indicadoras de `fin_semana` y `feriado`, y el tiempo en años. | Ejemplo del curso; pedido del equipo |
| **Se limita la profundidad del árbol** | Un árbol sin podar llega a profundidad 31 / 943 hojas y desvianza 12,65 (memoriza el ruido); `max_depth=4` (13 hojas) baja a 1,40 (`04c_arbol_profundidad.csv`). | corrida propia |
| **Backtesting implementado a mano** (no `skforecast`) | Que el procedimiento quede a la vista y auditable; sin dependencia nueva. | — |
| **`y(t−1)` no se usa** en el modelo aprendido | Exigiría predicción recursiva; el diagnóstico mostró que su aporte es pequeño. Queda como candidato para el panel. | `resumen_diagnostico_datos.md` §5.2 |

### Decisiones descartadas

- **Naive estacional (t−7) como línea base.** Se evaluó (§7) y se descartó: desvianza de
  Poisson 7,90, casi seis veces la de la media constante. Un único día pasado es una
  predicción puntual demasiado ruidosa para un conteo bajo. Se conserva en la tabla como
  referencia negativa.
- **Árbol de decisión sin podar.** Se evaluó en la corrida de comparación
  (`04c_arbol_profundidad.csv`): desvianza 12,65 contra 1,40 del árbol podado. Memoriza el
  ruido del entrenamiento. El modelo base usa el árbol poco profundo.
- **`skforecast`.** El ejemplo del curso lo usa; acá se prefirió un backtesting explícito
  de ~15 líneas. `skforecast` es candidato para el notebook del panel, donde la búsqueda
  de modelos justifica la dependencia.

---

## 2. Datos de entrada

`data/processed/panel_zona_top.csv` — lo exporta el ETL
(`resumen_preparacion_montevideo.md` §7.4). Serie diaria de MUNICIPIO C, una fila por día,
12 columnas. Objetivo: `n_siniestros`. Exógenas usadas: `tipo_dia` (calendario). El clima
está en el archivo pero **no se usa** (§6 del diagnóstico: fuera de muestra no aporta).

La fecha se parsea con **formato ISO explícito** (`%Y-%m-%d`), no con detección
automática: leer una fecha ISO con `dayfirst` convierte `2021-07-01` en el 7 de enero en
silencio (`registro_uso_IA.md`, sesión 2026-09-07).

### Verificaciones de integridad — todas en verde (§1 del notebook)

Índice temporal ordenado y único · serie diaria **sin huecos** (1.645 días) · sin nulos ·
objetivo entero no negativo · `zona_id` constante (por eso no es predictor).

### Resumen de la serie — `tablas/01_serie_resumen.csv`

| Indicador | Valor |
| --- | --- |
| Municipio | MUNICIPIO C |
| Días | 1.645 (2021-07-01 → 2025-12-31) |
| Media | **3,5155** |
| Varianza | 4,4297 |
| **Índice de dispersión (var/media)** | **1,26** |
| Mínimo / Máximo | 0 / 13 |
| % de días en cero | **4,8 %** |

Es una regresión de conteo ordinaria: sin exceso de ceros, sobredispersión leve. La
familia natural es **Poisson**, con **binomial negativa** como primera extensión.

### Tendencia (§2 del notebook, `figuras/fig1_serie.png`)

La media diaria pasa de **3,363** (primera mitad) a **3,668** (segunda mitad): **+9,1 %**.
Coherente con el +11,0 % que el diagnóstico midió sobre la serie del departamento
(`resumen_diagnostico_datos.md` §4.1). *Evidencia:* la recta de tendencia sube
~0,15 siniestros/año.

### Perfil de calendario (§3, `tablas/02_perfil_calendario.csv`, `figuras/fig2_...png`)

| `tipo_dia` | Días | Media | Factor vs media global |
| --- | --- | --- | --- |
| `entre_semana` | 1.114 | 3,988 | **1,134** |
| `fin_semana` | 454 | 2,564 | **0,729** |
| `feriado` | 77 | 2,286 | **0,650** |

*Cálculo descriptivo sobre toda la serie.* La línea base vuelve a estimar estas medias
**sólo con entrenamiento**.

### Autocorrelación cruda (§3, §5, `tablas/02b_autocorrelacion.csv`)

Sobre el tramo de **desarrollo** (sin el test): rezago 1 = **0,056**, rezago 7 = **0,077**,
rezago 14 = **0,165**. Son autocorrelaciones de Pearson **crudas** —la tendencia las infla
y no se descuenta el calendario—, así que sirven de referencia gruesa, no de prueba. La
prueba correcta (banda nula de Poisson, sobre el residuo) es la del diagnóstico §5.2:
persistencia genuina a rezago 1, de magnitud despreciable.

---

## 3. El protocolo de evaluación

### 3.1 Particiones — `tablas/03_particiones.csv`

| Bloque | Desde | Hasta | Días | % del total |
| --- | --- | --- | --- | --- |
| Entrenamiento inicial | 2021-07-01 | 2024-03-13 | 987 | 60,0 % |
| Validación (ventana deslizante) | 2024-03-14 | 2025-02-05 | 329 | 20,0 % |
| **Prueba (reservado)** | **2025-02-06** | **2025-12-31** | **329** | **20,0 %** |

**Desarrollo** = entrenamiento inicial + validación = 1.316 días (80 %). **Prueba** = 329
días (20 %), el tramo cronológicamente final.

### 3.2 Validación interna: ventana deslizante (§6)

La función `backtesting` parte de un origen (el 75 % de desarrollo), entrena con **todo lo
anterior al origen**, predice los siguientes **7 días**, guarda esas predicciones y avanza
el origen **7 días**. La ventana de entrenamiento **crece** en cada corte. Resultan
**47 cortes** de validación.

Cada modelo recibe dos DataFrames: `historia` (lo observado antes del origen, para
rezagos) y `ajuste` (el tramo con el que se estiman medias y se entrena el árbol). En
validación interna `ajuste = historia` (se reajusta en cada corte); en el test `ajuste`
queda **fijo en todo el desarrollo** (equivale a `refit=False`).

### 3.3 Métricas — `evaluar()` en §4

| Métrica | Rol | Interpretación |
| --- | --- | --- |
| **Desvianza de Poisson media** | Principal — selecciona | Error ponderado por el nivel del conteo. 0 = predicción perfecta. |
| **MAE** | Operativa | «Siniestros de diferencia, en promedio». |
| **RMSE** | Errores grandes | Penaliza más las desviaciones grandes. |
| **Razón total predicho / observado** | Calibración global | ≈ 1 = no infra/sobre-predice el volumen. |
| **Sesgo medio** (predicho − observado) | Dirección | < 0 = infra-predice. |

Se calculan sobre las **predicciones continuas** (no redondeadas), como en el ejemplo del
curso.

### 3.4 Medidas concretas contra la fuga de información

1. Toda media, factor o coeficiente se estima con la **ventana de entrenamiento de cada
   corte**, nunca con datos posteriores al origen.
2. En el test, el ajuste queda **congelado en el desarrollo**; sólo la historia para los
   rezagos avanza a medida que pasan los días, como en operación.
3. La ventana de predicción **nunca** entra al ajuste.
4. El árbol de decisión usa sólo rezagos **observados** (`t−7`, `t−14`, `t−21`) para un
   horizonte de 7 días: **sin recursión**, sin realimentar predicciones.
5. `zona_id` es constante → no es predictor. No hay columnas derivadas del objetivo
   (gravedad) en el conjunto (las quitó el ETL).
6. El objeto `serie_test` **no aparece en el código entre la §5 y la §9**.

---

## 4. Líneas base y modelo base aprendido

Cinco modelos, **todos evaluados con la misma llamada a `backtesting`**, los mismos
cortes y las mismas métricas.

| Modelo | Qué predice |
| --- | --- |
| **Media constante** | La media del entrenamiento, todos los días. Es el piso. |
| **Naive estacional (t−7)** | El valor de 7 días atrás. Referencia habitual de *forecasting*. |
| **Tasa × calendario** ← *línea base del proyecto* | La media del entrenamiento **para ese `tipo_dia`**. Nivel global × factor de calendario. |
| **Media móvil 56 d × calendario** | Igual, pero el nivel sale de los últimos 56 días observados. Sirve para ver si seguir la tendencia ayuda. |
| **Árbol de decisión** ← *modelo base aprendido* | `DecisionTreeRegressor` poco profundo (`max_depth=4`, `min_samples_leaf=20`) con rezagos `t−7/14/21`, indicadoras de fin de semana y feriado, y el tiempo en años. |

El árbol de decisión es el **modelo aprendido de arranque**, no el modelo final del
proyecto: la selección de modelo e hiperparámetros es el Entregable 3. La configuración
`max_depth=4` se fijó a mano; la corrida de comparación (`04c_arbol_profundidad.csv`)
muestra por qué un árbol sin podar no sirve.

---

## 5. Resultados

### 5.1 Validación interna (desarrollo) — `tablas/04_desarrollo_backtesting.csv`

47 cortes de 7 días. Ordenado por desvianza de Poisson (menor es mejor).

| Modelo | Desv. Poisson | MAE | RMSE | Razón total | Sesgo medio |
| --- | --- | --- | --- | --- | --- |
| Media móvil 56 d × calendario | 1,3766 | 1,6501 | 2,1663 | **1,0102** | +0,0377 |
| **Tasa × calendario** (línea base) | 1,3782 | **1,6114** | 2,1641 | 0,9146 | −0,3163 |
| **Árbol de decisión** (`max_depth=4`) | 1,4005 | 1,6815 | 2,1958 | **0,9981** | −0,0071 |
| Media constante | 1,5178 | 1,7591 | 2,2735 | 0,9133 | −0,3208 |
| Naive estacional (t−7) | **7,8956** | 2,3769 | 3,0647 | 1,0066 | +0,0243 |

Mejora en desvianza respecto de la media constante: Media móvil 56 d **−9,3 %**,
Tasa × calendario **−9,2 %**, Árbol de decisión **−7,7 %**.

**Corrida de comparación de profundidad — `tablas/04c_arbol_profundidad.csv`**

| Árbol | Desv. Poisson | MAE | Razón total | Profundidad | Hojas |
| --- | --- | --- | --- | --- | --- |
| **Sin podar** (por omisión) | **12,6468** | 2,4863 | 1,0476 | 31 | **943** |
| **Base** (`max_depth=4`) | **1,4005** | 1,6815 | 0,9981 | 4 | 13 |

**Lectura (§7 del notebook):**

- *Evidencia:* un árbol sin podar tiene una desvianza **nueve veces peor** que el podado:
  con 943 hojas sobre ~1.290 días de entrenamiento, memoriza el ruido. La poda es
  imprescindible.
- *Evidencia:* el árbol base **supera a la media constante** (−7,7 % de desvianza) pero
  **queda por debajo de las dos formas con calendario** (su desvianza es 1,6 % peor que la
  de la línea base; su MAE 1,68 contra 1,61).
- *Evidencia:* el árbol calibra casi perfecto **en muestra** (razón total 0,998), mejor
  que la línea base (0,915). Es calibración de desarrollo, no de test.
- *Evidencia:* la ventana móvil de 56 días tiene la **misma desvianza** que la tasa ×
  calendario pero **mejor calibración** (razón 1,010 vs 0,915).
- *Inferencia del equipo:* la tendencia creciente introduce un sesgo de infra-predicción
  que una ventana de nivel corta corrige; **hay que tratarla explícitamente** en el panel.
- *Inferencia del equipo:* `Naive estacional (t−7)` no es una línea base admisible.

### 5.2 Importancia de variables del árbol base — `tablas/05_importancias_arbol.csv`

Árbol reajustado sobre **todo el desarrollo** (`figuras/fig4b_importancias_arbol.png`).
Importancia = reducción total de impureza atribuida a cada variable.

| Variable | Importancia |
| --- | --- |
| `es_fin_semana` | **0,525** |
| `t_anios` (tendencia) | **0,226** |
| `es_feriado` | **0,171** |
| `y_lag21` | 0,064 |
| `y_lag7` | 0,013 |
| `y_lag14` | 0,000 |

*Evidencia:* el árbol se apoya sobre todo en el **calendario** (fin de semana + feriado ≈
70 %) y algo en la **tendencia** (23 %). **Los tres rezagos juntos pesan menos del 8 %**,
y `y_lag14` exactamente 0. Coherente con el diagnóstico §5.2: la persistencia de corto
plazo es despreciable.

### 5.3 Evaluación final sobre el conjunto de prueba — `tablas/06_evaluacion_test.csv`

47 cortes de 7 días. Ajuste **congelado en el desarrollo**. Se usó una sola vez.

| Modelo | Desv. Poisson | MAE | RMSE | Razón total | Sesgo medio |
| --- | --- | --- | --- | --- | --- |
| **Tasa × calendario** (línea base) | **1,0848** | **1,5919** | **1,9667** | 0,8841 | −0,4493 |
| Media constante | 1,2625 | 1,7411 | 2,1199 | 0,8839 | −0,4498 |
| **Árbol de decisión** | **1,6789** | 1,9055 | 2,4087 | **0,7229** | **−1,0737** |

Comparación desarrollo vs test en `tablas/06b_desarrollo_vs_test.csv`.

- *Evidencia:* **en el test el árbol es el peor de los tres**, incluso peor que predecir
  la media constante. Su desvianza (1,679) es un 55 % más alta que la de la línea base
  (1,085) y un 33 % más alta que la de la media constante (1,263).
- *Evidencia:* el árbol infra-predice fuerte: razón total **0,723** (−28 % de volumen),
  sesgo **−1,07 siniestros/día**. La línea base y la media constante también infra-predicen
  (razón 0,884) pero mucho menos.
- *Evidencia:* la línea base `Tasa × calendario` mejora la media constante en el test un
  **−14,1 %** de desvianza (1,263 → 1,085).
- *Inferencia del equipo:* **el árbol no extrapola.** En el test `t_anios` cae siempre
  fuera del rango de entrenamiento, así que todas las filas terminan en la misma hoja,
  entrenada con el tramo final del desarrollo —que por la tendencia creciente ya está por
  debajo del nivel del test—. El diagnóstico lo había anticipado para `anio` (§5.3).
- *Inferencia del equipo:* **el protocolo funcionó.** Un modelo que en desarrollo parecía
  competitivo (−7,7 % vs constante, calibración 0,998) se cae en el test. Para eso sirve el
  conjunto reservado.

### 5.4 Calibración mensual en el test — `tablas/07_calibracion_mensual_test.csv`

Total mensual predicho / observado (**árbol de decisión**). Test: **1.275 siniestros
observados** en 329 días evaluados.

| Mes 2025 | Observado | Predicho | Razón |
| --- | --- | --- | --- |
| 02 (parcial) | 72 | 63,12 | 0,877 |
| 03 | 112 | 82,19 | 0,734 |
| 04 | 116 | 82,04 | 0,707 |
| 05 | 111 | 85,52 | 0,770 |
| 06 | 110 | 84,86 | 0,771 |
| 07 | 121 | 85,66 | 0,708 |
| **08** | **134** | 86,45 | **0,645** |
| **09** | **134** | 85,04 | **0,635** |
| 10 | 128 | 91,58 | 0,715 |
| 11 | 109 | 86,12 | 0,790 |
| 12 | 128 | 89,16 | 0,697 |

*Evidencia:* el árbol infra-predice **todos los meses del test** (razón entre 0,64 y 0,88),
con el hueco mayor en agosto–septiembre. No es un desajuste puntual: es la tendencia que el
árbol no puede seguir.

---

## 6. Limitaciones y lo que NO puede afirmarse

| Limitación | Cómo se trata |
| --- | --- |
| **Es una sola serie (MUNICIPIO C).** No representa al proyecto. | Declarar que las cifras son de puesta a punto del protocolo, no del sistema. |
| **No se puede hablar de generalización.** Con una serie no hay hold-out de zonas. | El panel de 8 municipios, con hold-out dejando uno afuera por vez, es el notebook siguiente. |
| **El clima no se usó.** | Coherente con el diagnóstico (fuera de muestra no aporta). Cuando entre, el desempeño será una cota optimista (clima observado, no pronosticado). |
| **La tendencia no se trató.** El árbol recibe `t_anios` pero **no la extrapola**; la línea base no la modela. | En el test los tres modelos infra-predicen. El tratamiento explícito (recalibración de nivel, ponderación de datos recientes) es un pendiente del panel. |
| **El árbol es un modelo de arranque**, no ajustado (`max_depth=4` a mano). | La búsqueda de modelo e hiperparámetros es el Entregable 3. |
| **Horizonte fijo en 7 días.** | Otros horizontes pueden dar otras conclusiones. |
| **`y(t−1)` no se evaluó.** | Se evaluará como candidato en el panel. |
| **Autocorrelaciones crudas** (§2). | Referencia gruesa; la prueba formal es la del diagnóstico §5.2. |

### Frases que NO deben aparecer en el informe a partir de este notebook

- ❌ «El modelo predice cuándo o dónde ocurrirá un siniestro.» → estima el **conteo
  esperado** por día.
- ❌ «MUNICIPIO C es el más peligroso.» → es el que más siniestros **registra**
  (`resumen_diagnostico_datos.md` §6).
- ❌ «El modelo generaliza / funciona bien en Montevideo.» → se evaluó **una sola serie**.
- ❌ «El árbol de decisión es el modelo final del proyecto.» → es el **modelo base de
  arranque**; en el test rinde peor que la media constante. La selección de modelo es el
  Entregable 3.
- ❌ «El árbol de decisión mejora la línea base.» → en el test es **peor** (desvianza
  1,679 vs 1,085): no extrapola la tendencia.
- ❌ «El árbol sin podar da mejores resultados.» → `04c_arbol_profundidad.csv` muestra lo
  contrario (desvianza 12,65 vs 1,40).
- ❌ «Se eliminó la tendencia / la estacionalidad.» → el árbol ni siquiera la extrapola;
  en el test los modelos infra-predicen.
- ❌ «Los rezagos de la serie son informativos.» → pesan < 8 % en el árbol; `y_lag14` = 0.
- ❌ «El clima explica la siniestralidad.» → no se usó, y el diagnóstico mostró que fuera
  de muestra no aporta.
- ❌ «El naive estacional es una línea base razonable.» → desvianza de Poisson 7,90;
  se descartó.

---

## 7. Índice de artefactos

`experiments/base/` — **12 tablas, 7 figuras** (`tablas/08_artefactos.csv` las lista).

| Artefacto | Qué respalda | § notebook |
| --- | --- | --- |
| `tablas/01_serie_resumen.csv` | Estadísticos de la serie de MUNICIPIO C | 1 |
| `tablas/02_perfil_calendario.csv` | Media por `tipo_dia` y factor vs global | 3 |
| `tablas/02b_autocorrelacion.csv` | Autocorrelación cruda a rezagos 1/7/14 sin el test | 3, 5 |
| `tablas/03_particiones.csv` | Bloques de entrenamiento, validación y prueba | 5 |
| `tablas/04_desarrollo_backtesting.csv` | Métricas de los 5 modelos en validación interna | 7 |
| `tablas/04b_folds_linea_base.csv` | Métricas por corte (47) de la línea base | 7 |
| `tablas/04c_arbol_profundidad.csv` | Árbol sin podar vs árbol base: desvianza, profundidad, hojas | 7 |
| `tablas/05_importancias_arbol.csv` | Importancia de variables del árbol base | 8 |
| `tablas/06_evaluacion_test.csv` | Métricas de los finalistas en el test | 9 |
| `tablas/06b_desarrollo_vs_test.csv` | Comparación desarrollo vs test | 9 |
| `tablas/07_calibracion_mensual_test.csv` | Total mensual observado vs predicho en test | 9 |
| `tablas/08_artefactos.csv` | Este índice | 11 |
| `figuras/fig1_serie.png` | Serie diaria, media móvil de 28 días y tendencia lineal | 2 |
| `figuras/fig2_perfil_calendario.png` | Media de siniestros por tipo de día | 3 |
| `figuras/fig3_particion.png` | Partición temporal (desarrollo / validación / prueba) | 5 |
| `figuras/fig4_desarrollo_predicciones.png` | Predicciones sobre el tramo final de desarrollo | 7 |
| `figuras/fig4b_importancias_arbol.png` | Importancia de variables del árbol base | 8 |
| `figuras/fig5_test_predicciones.png` | Observado vs finalistas en el test, con contexto | 9 |
| `figuras/fig6_calibracion_test.png` | Total mensual y dispersión predicho-vs-observado en test | 9 |

**Antes de citar cualquier cifra:** verificar que `data/processed/panel_zona_top.csv` sea
la salida del ETL vigente (`resumen_preparacion_montevideo.md`, tabla `08_panel`). Si el
ETL se reejecuta con otro alcance, este notebook hay que volver a correrlo.

---

## 8. Qué queda pendiente

Para el notebook del panel (día × municipio, 8 zonas):

1. **Repetir el protocolo sobre el panel completo**, con métricas **desagregadas por
   municipio**.
2. **Construir la tasa histórica por municipio**, ajustada sólo con entrenamiento — el
   bloque más útil fuera de muestra según el diagnóstico (§5.3).
3. **Evaluar el rezago de 1 día** como variable candidata, contra la línea base.
4. **Tratar la tendencia creciente** de forma explícita (recalibración de nivel,
   ponderación de datos recientes, término de tendencia). En el test de este notebook los
   tres modelos infra-predicen, y el árbol —que no extrapola— es el que peor rinde.
5. **Decidir el destino del clima** (fuera de muestra no aportó en el diagnóstico).
6. **Diseñar el hold-out de zonas** dejando un municipio afuera por vez y promediando.
7. **Comparar el árbol base contra familias apropiadas para conteo** (regresión de Poisson,
   boosting con pérdida Poisson, `RandomForest` como en el ejemplo del curso) y ajustar
   hiperparámetros con validación temporal — Entregable 3. Considerar `skforecast`.
