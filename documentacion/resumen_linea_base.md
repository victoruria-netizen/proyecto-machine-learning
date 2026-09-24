# Resumen de línea base y modelo candidato preliminar — MUNICIPIO C

**Notebook:** [`notebooks/linea_base.ipynb`](../notebooks/linea_base.ipynb)
**Artefactos:** `experiments/linea_base/` (6 tablas CSV, 4 figuras PNG, 1 CSV de referencia)
**Salida:** ninguna a `data/processed/` (el notebook sólo consume el panel del ETL)
**Fecha de ejecución:** 2026-09-24
**Alcance:** una única serie diaria — **MUNICIPIO C** (municipio con más siniestros
registrados), 2021-07-01 a 2025-12-31, 1.645 días

---

## 0. Cómo usar este documento

Contexto autocontenido para redactar las secciones *Metodología — diseño de evaluación*
y *Línea base* del informe (guía PAA §6.2) sin abrir el repositorio. Reemplaza a
[`resumen_base.md`](resumen_base.md) y [`resumen_base_2.md`](resumen_base_2.md), que
documentaban `base.ipynb` y `base_2.ipynb`: esos dos notebooks ya no están en `main`
(preservados en la rama histórica `entregable_2`) y este notebook unifica lo que
quedaba repartido entre ambos. Ver `documentacion/cambios_para_informe.md` para la
tabla completa de equivalencias de artefactos y de nombres.

**Reglas que quien redacte debe respetar:**

1. **Ninguna cifra sin artefacto.** Todos los números salen de la ejecución del
   2026-09-24 y llevan al lado la tabla que los respalda (`tablas/NN_nombre.csv`).
2. **Distinguir evidencia de inferencia.** «Los resultados muestran X» y «el equipo
   concluye Y» son afirmaciones distintas.
3. **No escribir Introducción ni Marco teórico** a partir de este documento.
4. **Respetar la distinción entre línea base y candidato** (sección 1): las tres
   primeras filas de cualquier tabla de resultados son referencias fijas; la cuarta
   (el árbol) es un modelo que se ajusta y compite, no una referencia.
5. **Respetar los límites de la sección 4.** Hay afirmaciones que este notebook *no*
   sostiene, listadas explícitamente.

**Documentos hermanos:** [`resumen_diagnostico_datos.md`](resumen_diagnostico_datos.md)
(calidad, cobertura, adecuación) y
[`resumen_preparacion_montevideo.md`](resumen_preparacion_montevideo.md) (ETL). Las
decisiones de métrica, forma de la línea base y tendencia se **justifican con
evidencia** allá; acá se **aplican** sobre una serie y se dejan los artefactos.

> ### ⚠️ Este notebook trabaja una sola serie, a propósito
>
> `panel_zona_top.csv` es la serie de **un** municipio. Sirve para fijar el protocolo,
> las líneas base y el modelo candidato sobre un caso simple. **Sus métricas no son
> las del proyecto:** el diagnóstico mostró que los 8 municipios se parecen mucho entre
> sí (razón máx/mín 1,71×), y la evaluación seria —panel de 8 municipios con métricas
> desagregadas— queda para el Entregable 3. Nada de lo que sigue permite afirmar que un
> modelo «generaliza».

---

## 1. Qué hace el notebook y por qué

Unifica en un solo lugar los cuatro modelos del Entregable 2 que se conservan,
distinguiendo explícitamente dos categorías:

- **Líneas base** (§6 del notebook): referencias fijas, no se ajustan por búsqueda,
  marcan el mínimo aceptable. Son tres: media constante, L0 y L1.
- **Modelo candidato preliminar** (§7 del notebook): un único árbol de decisión, que sí
  se ajusta con los datos y compite por ser la solución. Sus hiperparámetros se
  fijaron **a mano**, no por búsqueda; elegirlos por validación interna es trabajo del
  Entregable 3.

### Decisiones heredadas, sin cambios (vienen de `base.ipynb` / `base_2.ipynb`)

| Decisión | Motivo | De dónde sale |
| --- | --- | --- |
| **Métrica principal: desvianza de Poisson media** | El objetivo es un conteo con sobredispersión leve (índice 1,26, `01_serie_resumen.csv`). Pondera el error por el nivel; el MAE no. | `resumen_diagnostico_datos.md` §5.1 |
| Acompañan **MAE, RMSE, razón total predicho/observado, sesgo medio y días con predicción cero** | Lectura operativa, sensibilidad a errores grandes, calibración, y detección de predicciones degeneradas. | — |
| **Partición cronológica en tres bloques (987 / 329 / 329 días)** | Entrenamiento inicial (60 %), validación por ventana deslizante (20 %), prueba reservada (20 %). En una serie temporal no se parte al azar. | `03_particiones.csv` |
| **Validación interna: 47 cortes de 7 días, origen móvil, ventana expansiva** | Evaluar configuraciones sin tocar el test; en el test el ajuste queda congelado en el desarrollo. | Protocolo de `base.ipynb` |
| **L1 = tasa × factor de calendario** | Forma multiplicativa que el diagnóstico midió como la mejor disponible fuera de muestra (−11,8 % en el panel). Con una sola zona se reduce a las medias por `tipo_dia`. | `resumen_diagnostico_datos.md` §5.3 |
| **L0 = promedio de lo observado 7/14/21/28 días antes** | Recoge el patrón semanal sin exógenas; promedia cuatro semanas para que el ruido de una sola pese menos. Sin parámetros que ajustar. | `base_2.ipynb` (2026-09-15) |
| **Árbol candidato: `DecisionTreeRegressor`, `max_depth=4`, `min_samples_leaf=20`, rezagos `t−7/14/21`, `es_fin_semana`, `es_feriado`, `t_anios`** | Un árbol sin podar memoriza el ruido (profundidad 31, 943 hojas, desvianza 12,65 en desarrollo, `04c_arbol_profundidad.csv` de `base.ipynb`, rama `entregable_2`). Esta config es la mínima para que sea una referencia sensata. | `base.ipynb` §7-§8 |
| **Backtesting implementado a mano** (no `skforecast`) | Auditable, sin dependencia nueva. | — |

### Lo único nuevo de esta unificación

- Reorganización en dos secciones (líneas base / candidato) que antes no existía.
- `dias_prediccion_cero` se agrega a las métricas (ya se usaba en `base_2.ipynb`, no en
  `base.ipynb`); no cambia el cálculo de las demás métricas.
- Celda de verificación de entorno (§0) y celda de no regresión (§11), ninguna de las
  cuales existía en los notebooks originales.

---

## 2. Resultados, en tablas

### Validación interna — líneas base (`04_desarrollo_backtesting.csv`)

| Modelo | Desvianza de Poisson | MAE |
| --- | --- | --- |
| L1 (tasa × calendario) | 1,3782 | 1,6114 |
| Media constante | 1,5178 | 1,7591 |
| L0 (promedio 4 semanas) | 1,6908 | 1,8792 |

### Validación interna — modelo candidato (`04_desarrollo_backtesting.csv`)

| Modelo | Desvianza de Poisson | MAE |
| --- | --- | --- |
| Árbol candidato (preliminar) | 1,3912 | 1,6789 |

En desarrollo el árbol queda entre L1 y la media constante — parece competitivo.

### Evaluación final en el test reservado (`05_evaluacion_test.csv`) — una sola vez

| Modelo | Desvianza de Poisson | MAE | Razón total pred./obs. | Días con predicción 0 |
| --- | --- | --- | --- | --- |
| **L1 (tasa × calendario)** | **1,0848** | 1,5919 | 0,8841 | 0 |
| Media constante | 1,2625 | 1,7411 | 0,8839 | 0 |
| L0 (promedio 4 semanas) | 1,3324 | 1,7546 | 0,9810 | 0 |
| Árbol candidato (preliminar) | 1,6789 | 1,9055 | 0,7229 | 0 |

**Lectura (evidencia):** en el test, L1 tiene la menor desvianza de los cuatro modelos.
El árbol candidato, que en desarrollo parecía competitivo, **es el peor de los
cuatro** en el test — infra-predice un 27,7 % del volumen (razón 0,7229, contra 0,88 de
las dos primeras líneas base). L0 no es la referencia de menor desvianza: la media
constante le gana (1,2625 contra 1,3324).

**Inferencia del equipo:** el protocolo funcionó — un modelo que en validación interna
parecía razonable se cae en la prueba reservada. Sigue siendo razonable recomendar L1
como línea base del proyecto y tratar al árbol como un modelo de arranque a mejorar en
el Entregable 3, no como candidato final.

### Verificación de no regresión (`referencia_no_regresion.csv`, celda §11)

Los cuatro modelos coinciden (tolerancia 0,001) con los valores que ya se habían
obtenido por separado en `base.ipynb` y `base_2.ipynb` antes de retirarse de `main`.
Única diferencia observable: L0 difiere en el cuarto decimal (1,3324 aquí contra 1,332
en `base_2.ipynb`, que sólo guardaba 3 decimales) — redondeo, no discrepancia.

---

## 3. Qué se retiró y por qué

| Modelo retirado | Por qué | Evidencia | Dónde queda |
| --- | --- | --- | --- |
| Repetir semana anterior (naive estacional) | Peor desempeño de los seis modelos del Entregable 2: desvianza 5,007 en el test completo. Ya cumplió su función de referencia negativa. | `experiments/base_2/tablas/05_test_metricas.csv` | Rama `entregable_2` |
| Árbol A (`max_depth=15`, `skforecast.ForecasterRecursive`, rezagos `[1,7,14,21]`) | 716 hojas para 1.295 filas de entrenamiento (1,81 días/hoja): memorización, no aprendizaje de reglas. Sin validación interna — se evaluó directo contra el test. Reajustar hiperparámetros no corrige la falta de validación. | `experiments/base_2/tablas/02_tamano_arbol.csv` | Rama `entregable_2` |

---

## 4. Limitaciones y lo que NO puede afirmarse

- **Es una sola serie.** MUNICIPIO C no representa al proyecto. La evaluación
  desagregada por municipio es trabajo del notebook del panel (Entregable 3).
- **El árbol candidato es un modelo de arranque, no ajustado.** `max_depth=4` se fijó a
  mano; la selección de modelo e hiperparámetros con validación es el Entregable 3.
- **L0 no se revisó con datos de validación.** Que la media constante le gane en el
  test no es motivo para cambiarla ahora: revisarla con el test sería elegir el modelo
  mirando la prueba reservada.
- **El clima y el rezago de 1 día no se usan** en ningún modelo de este notebook.
  Quedan como candidatos para el panel.
- **`t_anios` en el árbol candidato no extrapola.** Es la causa identificada de por qué
  el árbol rinde peor en el test: la tendencia creciente de la serie deja esa variable
  fuera del rango visto en entrenamiento.

**Frases que no deben aparecer en el informe a partir de este notebook:**

- ❌ «El árbol candidato es el modelo final del proyecto.» → es un modelo de arranque
  preliminar; la selección de modelo es el Entregable 3.
- ❌ «El modelo predice cuándo o dónde ocurrirá un siniestro.» → estima el **conteo
  esperado** por día.
- ❌ «MUNICIPIO C es el más peligroso.» → es el que más siniestros **registra**.
- ❌ «El modelo generaliza / funciona bien en Montevideo.» → se evaluó una sola serie.
- ❌ «Se validó la ventana de L0 / se recalculó la ACF sólo con desarrollo.» → ninguna
  de las dos cosas se hizo en esta tarea; quedan pendientes (sección 6).

---

## 5. Índice de artefactos

| Artefacto | Qué respalda |
| --- | --- |
| `tablas/00_entorno.csv` | Versiones efectivas de la corrida |
| `tablas/01_serie_resumen.csv` | Estadísticos de la serie (media, dispersión, % de ceros) |
| `tablas/02_perfil_calendario.csv` | Media de siniestros por `tipo_dia`, insumo de L1 |
| `tablas/03_particiones.csv` | Los tres bloques cronológicos (987/329/329 días) |
| `tablas/04_desarrollo_backtesting.csv` | Métricas de los 4 modelos en validación interna |
| `tablas/05_evaluacion_test.csv` | Métricas de los 4 modelos en el test reservado — **la tabla a citar en el informe** |
| `referencia_no_regresion.csv` | Valores de referencia de `base.ipynb` / `base_2.ipynb` (rama `entregable_2`) |
| `figuras/fig1_serie.png` | Serie diaria, media móvil de 28 días y tendencia lineal |
| `figuras/fig2_perfil_calendario.png` | Media de siniestros por tipo de día |
| `figuras/fig3_desarrollo_predicciones.png` | Predicciones de los 4 modelos, últimos ~140 días de desarrollo |
| `figuras/fig4_test_predicciones.png` | Observado vs los 4 modelos en el test, con contexto |

---

## 6. Qué queda pendiente (Entregable 3)

1. Repetir el protocolo sobre el panel día × municipio (8 zonas), con métricas
   desagregadas.
2. Construir la tasa histórica por municipio ajustada sólo con entrenamiento.
3. Evaluar el rezago de 1 día como variable candidata.
4. Tratar la tendencia creciente de forma explícita (el árbol candidato no la
   extrapola).
5. Decidir el destino del clima (fuera de muestra no aportó nada en el diagnóstico).
6. Diseñar el hold-out de zonas dejando un municipio afuera por vez.
7. Revisar con datos de validación (no con el test) si L0 sigue siendo la línea base
   preferida frente a la media constante.
8. Recalcular la ACF que orientó los rezagos del árbol usando sólo desarrollo (hoy usa
   la serie completa — fuga leve heredada, declarada desde `base_2.ipynb`).
9. Decidir si `t_anios` se mantiene en el árbol candidato, dado que es la causa
   identificada de su mal desempeño en el test.
10. Elegir los hiperparámetros del árbol (o de la familia que se use) por validación
    interna, no a mano.
11. Actualizar los pines de versión de `requirements.txt` que quedaron liberados al
    quitar `skforecast` (pandas, matplotlib, statsmodels) — es una decisión aparte, no
    tomada en esta tarea.
