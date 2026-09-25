# Cambios para el informe — puente entre esta sesión y la corrección del informe

**Para quién es este documento.** Lo va a usar otra persona, en otra sesión, para corregir
`documentacion/informe/Entregable2_PAA_20-09-26.pdf` (el informe tal como se entregó y defendió).
Esa persona va a tener los archivos nuevos de esta sesión pero no el contexto de por qué se
hicieron los cambios. Este documento es el puente: permite auditar qué del informe quedó
desactualizado sin tener que releer código ni reconstruir el razonamiento. No se editó el
informe en esta sesión — sólo se generó este puente.

**Cómo se armó.** Se extrajo el texto completo del PDF (54 páginas) y se localizaron todas las
menciones a `base.ipynb`, `base_2.ipynb`, `experiments/base/`, `experiments/base_2/`, `skforecast`,
"Árbol A", "Árbol B" y las tablas/cuadros que dependen de esos modelos. Los números de sección y
las citas textuales de este documento salen de esa lectura, no de memoria ni de suposición.

---

## Sesión 2026-09-25 — correcciones al repositorio previas a corregir el informe

Una auditoría de solo lectura (2026-09-24/25) relevó el estado del repo después de la
unificación y encontró un error real en este documento y cuatro omisiones frente al texto del
informe. Esta sesión corrigió el repositorio (no el informe, que sigue sin tocarse) y deja
constancia acá.

### Corrección a la sección (e) — la fila del árbol en la Tabla 4 no estaba dentro de tolerancia

La sección (e) de este documento (más abajo) afirmaba que las cuatro filas de las Tablas 1, 4 y 5
estaban "reproducidas por `linea_base.ipynb` dentro de una tolerancia de 0,001, verificado por su
celda de no regresión". **Eso era incorrecto para la fila del árbol en la Tabla 4** (validación
interna): la celda de no regresión (§11) sólo verificaba la Tabla 5 (bloque final), nunca la
Tabla 4. Verificado: `experiments/linea_base/tablas/04_desarrollo_backtesting.csv` daba
1,3912/1,6789/2,1891/0,9988/−0,0045 para el árbol candidato, contra 1,4005/1,6815/2,1958/0,9981/
−0,0071 en `entregable_2:experiments/base/tablas/04_desarrollo_backtesting.csv` — una diferencia
de 0,0093 en desvianza, muy por encima de la tolerancia.

**Causa, aislada comparando ambos notebooks línea por línea y reproduciéndola en un script
aparte:** `notebooks/linea_base.ipynb` tenía `SEMILLA=20260924` (la fecha de esta unificación) en
vez de `SEMILLA=20260910` (la de `base.ipynb`) — la única diferencia de código entre ambos
notebooks para el árbol. Con datos de validación (folds tempranos, desde 987 filas) hay empates
de partición que la semilla resuelve distinto; con las 1.295 filas del desarrollo completo (ajuste
único para el bloque final) no hay empates y ambas semillas dan el mismo árbol — por eso la Tabla
5 ya coincidía exacta y sólo la Tabla 4 mostraba la diferencia.

**Corregido:** `SEMILLA=20260910` en `notebooks/linea_base.ipynb`. La Tabla 4 vigente
(`experiments/linea_base/tablas/04_desarrollo_backtesting.csv`) ahora sí reproduce exacto
1,4005/1,6815/2,1958/0,9981/−0,0071. La celda de no regresión se extendió para verificar también
la Tabla 4 (`referencia_no_regresion.csv` ahora tiene una columna `tramo`), así que una regresión
futura en esa fila sí se detectaría.

**Para quien corrija el informe:** la Tabla 4 no necesita ningún cambio adicional al ya indicado
en la sección (d), ítem 3, de este documento (los valores ahí ya eran los correctos).

### Omisiones detectadas por la auditoría frente al texto del informe

El barrido de la sesión anterior no cubrió estos cuatro pasajes. Página según el propio pie de
página del PDF:

- **§3.4.2, página 27:** *"la expresión 'sin variables exógenas' designa a los modelos que
  utilizan únicamente la historia de la serie —L0 y el árbol A—; los modelos con calendario (L1 y
  el árbol B) sí incorporan una variable exógena."* Tras la unificación, "sin variables exógenas"
  ya no incluye "el árbol A" (retirado): sólo queda L0. Reescribir junto con el resto de §3.4.2.
- **§3.4.3, página 28:** *"No se informa el sesgo medio que registra base.ipynb: sobre la misma
  serie observada es una transformación de la razón total."* La sustancia sigue siendo válida
  (`linea_base.ipynb` también calcula y guarda `sesgo_medio`, sigue siendo redundante con la razón
  total para la misma serie), pero la cita a "`base.ipynb`" queda obsoleta: actualizar a
  `linea_base.ipynb` o quitar el nombre del notebook.
- **Nota (b) de la Tabla 5, página 42:** *"Valor obtenido de las predicciones guardadas de
  base.ipynb (experiments/base/…), no inferido de otras métricas."* Al reescribir la Tabla 5 con
  `experiments/linea_base/tablas/05_evaluacion_test.csv` (sección (d), ítem 4), esta nota también
  necesita actualizar la ruta y el notebook citados.
- **§4.3.3, página 43:** *"se prevé fijar la profundidad y el tamaño mínimo de hoja de **los
  árboles** con la desvianza como criterio"* — plural. Sólo sobrevive un árbol (el candidato);
  ajustar a singular o aclarar que la referencia a "los árboles" es al panorama del Entregable 2.

**Descartada:** la leyenda de la Ilustración F1 (página 6 y página 53, "tres series" contra las
cuatro de la figura nueva) **ya está cubierta** en la sección (b) de este documento ("la nueva
figura incluye también L0 (4 series en vez de 3)"). No es una omisión.

### Decisiones del equipo (2026-09-25)

- Se quitan del informe las Tablas F1 a F4 y las Ilustraciones F1 y F2.
- El Anexo F.1 (ejecución en el servidor) se conserva como anexo propio, ahora respaldado por
  `documentacion/logs/log_servidor_base.txt` (coincide cifra por cifra con la tabla actual del
  Anexo F.1). `documentacion/logs/log_servidor_base2.txt` (Job 108, `train_base_2.py`) es
  evidencia adicional que el informe no cita; queda disponible si el equipo decide agregar un
  segundo anexo.
- Se quitan del informe todas las menciones al árbol A, sin nota histórica.
- **Pasajes del cuerpo que quedan sin respaldo por estas decisiones** (al quitar F1–F4 e
  Ilustraciones F1–F2): §3.4.5 (la poda del árbol, hoy respaldada por la Tabla F1: "sin límite
  alcanza 31 niveles y 943 hojas, y su desvianza sube a 12,6468"); §4.3.2 (`t_anios` y la
  calibración mensual, hoy respaldados por la Tabla F3); §4.3.3 (la lección de la "primera semana"
  con el árbol A, y la referencia a la Tabla F4 para "29 de 47 semanas"). Quien corrija el informe
  tiene que decidir si esos pasajes se recortan, se reescriben sin la cifra que perdían el
  respaldo, o si alguna tabla se reconstruye igual a partir de `linea_base.ipynb` en una sesión
  aparte (Entregable 3).

### Cambios de terminología (Bloque 2 de esta sesión)

El informe **ya usaba la terminología correcta** ("ventana expansiva" en la Tabla 1 y en el
glosario, que define "expansiva" y "deslizante" como opuestas; "bloque final", con la aclaración
explícita de que no es una prueba reservada e independiente). Fue **el repositorio el que se
alineó** al informe, no al revés: `notebooks/linea_base.ipynb` decía "ventana deslizante" en
varios lugares (incluido el rótulo que genera `03_particiones.csv`) para un procedimiento que su
propio código implementa como expansivo (`historia = datos.iloc[:origen]`, sin límite inferior), y
llamaba al bloque final "prueba (reservado)"/"conjunto de prueba" sin la aclaración del informe.
Corregido en `notebooks/linea_base.ipynb`, `documentacion/resumen_linea_base.md`, `HANDOFF.md` y
`train/README.md`. Quien corrija el informe no tiene que cambiar esta terminología ahí: ya estaba
bien.

---

## a) Nota inicial sobre la estrategia de ramas

El informe vigente (`documentacion/informe/Entregable2_PAA_20-09-26.pdf`) describe y cita
artefactos de `notebooks/base.ipynb`, `notebooks/base_2.ipynb`, `experiments/base/` y
`experiments/base_2/`. Esos cuatro elementos **ya no existen en `main`**: se retiraron el
2026-09-24 al unificarse en `notebooks/linea_base.ipynb` / `experiments/linea_base/`.

Quedan preservados, intactos, en la rama histórica **`entregable_2`**, creada desde el commit de
`main` inmediatamente posterior a agregar el informe entregado. Para consultarlos:

```
git checkout entregable_2 -- notebooks/base.ipynb notebooks/base_2.ipynb
git show entregable_2:experiments/base/tablas/06_evaluacion_test.csv
# o, para explorar libremente sin tocar main:
git worktree add ../revision-entregable-2 entregable_2
```

`data/raw/` y `data/processed/` **no** se preservan en esa rama (son regenerables y nunca se
versionaron); todo lo demás — código, notebooks, `experiments/`, documentación — sí.

**Regla para quien corrija el informe:** ninguna cita nueva debe apuntar a `experiments/base/` ni
a `experiments/base_2/` como si estuvieran en `main`. Si una cifra sigue sin equivalente
reproducible en `experiments/linea_base/` (sección b), citarla como "rama `entregable_2`,
`experiments/base.../...`", nunca como si fuera parte del estado actual del repositorio.

---

## b) Tabla de equivalencia de artefactos

### Con equivalente directo en `experiments/linea_base/`

| Artefacto citado en el informe | Ruta anterior | Ruta nueva |
| --- | --- | --- |
| Tabla 1 — Particiones cronológicas (987/329/329 días) | `experiments/base/tablas/03_particiones.csv` | `experiments/linea_base/tablas/03_particiones.csv` (mismas cifras exactas) |
| Partición de `base_2.ipynb` (nota al pie de §4.3, "El promedio diario del bloque final...") | `experiments/base_2/tablas/01_particion.csv` | Ya no aplica como partición separada: `experiments/linea_base/tablas/03_particiones.csv` la incluye en el bloque único de tres partes |
| Tabla 4 — Desempeño en validación interna (§4.3.1) | `experiments/base/tablas/04_desarrollo_backtesting.csv` | `experiments/linea_base/tablas/04_desarrollo_backtesting.csv` — **con 4 filas, no 5** (ver sección d) |
| Tabla 5 — Desempeño en el bloque final (§4.3.2) | `experiments/base/tablas/06_evaluacion_test.csv` + `experiments/base_2/tablas/05_test_metricas.csv` combinadas a mano | `experiments/linea_base/tablas/05_evaluacion_test.csv` — **con 4 filas, no 6** (ver sección d); cifras de los cuatro modelos que sobreviven, idénticas dentro del redondeo |
| Cuadro 4 — Modelos evaluados bajo el protocolo común (§3.4.5) | Descriptivo, sin artefacto único | Sigue siendo descriptivo; la lista de modelos se reduce a 4 (ver sección c) |
| Ilustración F1 — Observado y predicho en el bloque final | `experiments/base/figuras/fig5_test_predicciones.png` | `experiments/linea_base/figuras/fig4_test_predicciones.png` — **no es idéntica**: la nueva figura incluye también L0 (4 series en vez de 3) |

### Retirados, disponibles solo en la rama `entregable_2` (sin equivalente en `experiments/linea_base/`)

`notebooks/linea_base.ipynb` no reprodujo todas las tablas auxiliares de `base.ipynb` —sólo las
que la Fase 1 de esta tarea pedía explícitamente (protocolo, líneas base, candidato, métricas de
desarrollo y de prueba)—. Estas quedan **retiradas de `main`, disponibles en `entregable_2`**:

| Artefacto citado en el informe | Ruta (rama `entregable_2`) | Por qué no tiene equivalente |
| --- | --- | --- |
| Tabla F1 — Efecto de limitar la profundidad del árbol B | `experiments/base/tablas/04c_arbol_profundidad.csv` | La comparación "sin podar vs. `max_depth=4`" no se reprodujo; `linea_base.ipynb` usa directamente la configuración podada |
| Tabla F2 — Importancia de variables del árbol B | `experiments/base/tablas/05_importancias_arbol.csv` | No se recalculó `feature_importances_` en el notebook unificado |
| Tabla F3 — Volumen mensual predicho y observado del árbol B | `experiments/base/tablas/07_calibracion_mensual_test.csv` | No se agregó el desglose mensual |
| Tabla F4 — Variabilidad semanal (modelos sin exógenas) | `experiments/base_2/tablas/07_test_variabilidad_semanal.csv` | Además de no reproducirse, mezclaba L0/media constante con Árbol A y "repetir semana anterior", ambos retirados (sección c) |
| Ilustración F2 — Volumen mensual, dispersión predicho/observado | `experiments/base/figuras/fig6_calibracion_test.png` | No se generó una figura equivalente |
| Tabla "primera semana" citada en §4.3.3 ("el árbol A, con la menor desvianza de la primera semana, 0,957") | `experiments/base_2/tablas/04_primera_semana_metricas.csv` | `linea_base.ipynb` no evalúa una sola semana suelta, sólo el protocolo de 47 cortes completo |
| `train_base.py` (Anexo F.1, "Script: train_base.py") | `train/train_base.py` | Se retiró junto con `base.ipynb`. Si se necesita una versión `.py` de `linea_base.ipynb` para el servidor, hay que construirla nueva (ver `train/README.md`) |
| `train_base_2.py` (mencionado en HANDOFF, no en el informe directamente) | `train/train_base_2.py` | Ídem |

**Nota aparte, no causada por esta tarea:** el Anexo F.1 cita
`documentacion/logs/slurm_104_20260918.log` como fuente. Ese archivo **no existe en el
repositorio ni en su historial** (verificado). Es un problema preexistente del informe, no algo
que esta sesión haya movido o roto — se deja constancia para que quien corrija no lo confunda con
las rutas de esta tabla.

---

## c) Tabla de equivalencia de nombres

| Nombre en el informe | Nombre nuevo | Estado |
| --- | --- | --- |
| "Árbol B" | **"Árbol candidato (preliminar)"** | Se mantiene — mismos hiperparámetros (`max_depth=4`, `min_samples_leaf=20`), mismas variables (rezagos 7/14/21, calendario, tiempo en años). Sólo cambia el rótulo y pasa a su propia sección ("Modelo candidato preliminar"), separada de las líneas base |
| "Árbol A" | — | **Retirado.** 716 hojas para 1.295 filas de entrenamiento (memorización), sin validación interna. Preservado en `entregable_2` |
| "Repetir semana anterior" (naive estacional) | — | **Retirado.** Peor desempeño de los seis modelos (desvianza 5,007 en el bloque final). Preservado en `entregable_2` |
| "Media móvil de 56 días por calendario" | — | **Retirado.** Este modelo aparecía en `base.ipynb` como contraste sobre el tratamiento de la tendencia (sólo evaluado en validación interna, nunca en el bloque final); no estaba en el alcance de los "seis modelos" que esta tarea pedía unificar ni retirar explícitamente, pero al no ser ninguno de los cuatro que sobreviven, tampoco pasó a `linea_base.ipynb`. Preservado en `entregable_2` |
| "L0" / "L0 — Promedio de las últimas cuatro semanas" | Sin cambio | Se mantiene con el mismo nombre |
| "L1" / "L1 — Tasa por factor de calendario" | Sin cambio | Se mantiene con el mismo nombre |
| "Media constante" | Sin cambio | Se mantiene con el mismo nombre |

---

## d) Secciones del informe afectadas

### REESCRITURA (el esquema de modelos cambió)

1. **§3.4.5 "Referencias, línea base y modelos evaluados", Cuadro 4** ("Modelos evaluados bajo el
   protocolo común"). Hoy lista 7 filas: Media constante, Repetir semana anterior, L0, L1, Media
   móvil de 56 días por calendario, Árbol A, Árbol B. Reescribir a 4 filas: Media constante, L0,
   L1, Árbol candidato (preliminar) — con una nota aclarando que los otros tres se evaluaron en el
   Entregable 2 y se retiraron después (motivo en la tabla de la sección c de este documento).

2. **Párrafo inmediatamente posterior al Cuadro 4** (§3.4.5, página 33): *"Los dos árboles son
   modelos aprendidos de arranque, configurados a mano y sin selección de hiperparámetros. El
   árbol A, implementado con skforecast, reproduce la configuración inicial del equipo: profundidad
   máxima de 15 niveles, predicción recursiva y rezagos que la autocorrelación del Municipio C
   muestra fuera de la banda de azar (Sección 4.1.3). El árbol B limita la profundidad a cuatro
   niveles..."* — Reescribir para describir sólo el árbol candidato (segunda oración en adelante);
   la mención a `skforecast` queda obsoleta (se quitó de `requirements.txt` el 2026-09-24).

3. **Tabla 4 — "Desempeño en validación interna por origen móvil" (§4.3.1)**. Hoy tiene 5 filas
   (Media móvil 56 días, L1, Árbol B, Media constante, Repetir semana anterior). Reescribir a 4
   filas con los valores de `experiments/linea_base/tablas/04_desarrollo_backtesting.csv`: L1
   (1,3782), Árbol candidato (1,3912), Media constante (1,5178), L0 (1,6908) — **el orden cambia**:
   L0 pasa a ser el peor de los cuatro en validación interna (no estaba en esta tabla en la
   versión anterior con ese conjunto de comparación). El párrafo que sigue ("Las dos formas con
   calendario mejoran la desvianza... el árbol B la mejora en un 7,7 %...") debe revisarse cifra
   por cifra contra la tabla nueva.

4. **Tabla 5 — "Desempeño en el bloque final" (§4.3.2)**. Hoy tiene 6 filas. Reescribir a 4 con
   `experiments/linea_base/tablas/05_evaluacion_test.csv`: L1 (1,085), Media constante (1,262), L0
   (1,332), Árbol candidato (1,679) — estas cuatro cifras **no cambian** respecto de la tabla
   actual, sólo se quitan las filas de Árbol A y Repetir semana anterior.

5. **Párrafo sobre los dos árboles en §4.3.2** (página 42, *"Ninguno de los dos árboles supera a
   las referencias, y por mecanismos distintos. El árbol B subestima el volumen total... El árbol
   A, en cambio, acierta el volumen total (0,967)... con 716 hojas..."*). La parte sobre el árbol
   candidato (antes "árbol B") se mantiene con evidencia vigente. La parte sobre Árbol A cita un
   artefacto retirado (sección b) — decidir si se conserva como nota histórica ("en el Entregable
   2 se evaluó además un segundo árbol, con estas cifras, retirado después; ver rama
   `entregable_2`") o se quita.

6. **§3.4.6 "Entorno de ejecución y reproducibilidad"**. Contiene tres afirmaciones que ya no son
   exactas: *"Los seis notebooks se ejecutan sobre un mismo entorno: Python 3.13.15... y
   skforecast 0.25.0"*; *"requirements.txt (diecisiete dependencias directas...)"*; *"...y el árbol
   completo en requirements-lock.txt (ciento treinta y seis paquetes)"*. Ver correcciones puntuales
   más abajo — son cifras concretas, no un cambio de esquema, pero conviene revisar el párrafo
   completo porque también depende de "seis notebooks" para el conteo de tablas/figuras
   comparadas en la auditoría de reproducibilidad del 2026-09-20 (108/122 tablas, 28/31 figuras):
   esos totales corresponden a los seis notebooks de esa fecha y son un registro histórico válido,
   no hace falta recalcularlos, pero sí aclarar que ya no reflejan la estructura vigente de
   `notebooks/`.

7. **§3.4.3, último párrafo antes de "3.4.4"** (página 30): *"Los dos notebooks de modelado
   comparten partición, esquema y cálculo de métricas: la media constante, único modelo común,
   obtiene sobre el bloque final la misma desvianza (1,2625 y 1,2620) y el mismo MAE (1,7411 y
   1,7410)... lo que funciona como control cruzado del procedimiento."* Describe el control cruzado
   **entre dos notebooks separados**, que ya no existen como tales. Reescribir para describir el
   mecanismo vigente: una celda de no regresión dentro de `linea_base.ipynb` que compara contra
   `experiments/linea_base/referencia_no_regresion.csv` (los valores que en su momento salieron de
   esos dos notebooks). Puede conservarse como antecedente histórico si se aclara que el mecanismo
   cambió.

8. **Anexo F completo** ("Resultados complementarios de la línea base"): Tablas F1, F2, F3, F4 e
   Ilustración F2 citan artefactos retirados sin equivalente (sección b). Decisión abierta para el
   equipo: (i) dejar el anexo tal cual, como registro histórico del Entregable 2, con una nota que
   diga que esos artefactos están en la rama `entregable_2` y ya no se recalculan automáticamente;
   o (ii) reconstruir las tablas que todavía tienen sentido con el árbol candidato (F1, F2, F3) a
   partir del notebook unificado, en una sesión aparte. Esta tarea no tomó esa decisión.

### CORRECCIÓN PUNTUAL (cifra o frase puntual, sin cambio de esquema)

| Dónde | Texto actual | Cambiar por |
| --- | --- | --- |
| §3.4.6 | "Python 3.13.15" | "Python 3.13.2" — el número anterior no correspondía a ninguna versión real de Python (`uv python install 3.13.15` no la encuentra); corregido el 2026-09-24 en `requirements.txt` y `README.md`, ver `HANDOFF.md` |
| §3.4.6 | "requirements.txt (diecisiete dependencias directas..." | "dieciséis dependencias directas" (se quitó `skforecast`) |
| §3.4.6 | "...y el árbol completo en requirements-lock.txt (ciento treinta y seis paquetes)" | "ciento veintitrés paquetes" (se regeneró el 2026-09-24 sin `skforecast` ni sus transitivas: numba, optuna, tqdm, rich, llvmlite, alembic, SQLAlchemy, Mako, greenlet, colorlog, markdown-it-py, mdurl) |
| §3.4.6 | "...matplotlib 3.11.1, geopandas 1.1.4, holidays 0.103 y skforecast 0.25.0." | Quitar "y skforecast 0.25.0" del final de la lista |
| §3.4.6 | "La versión de pandas responde a una restricción dura: skforecast 0.25.0 exige pandas >= 2.1, < 3.0." | La restricción ya no aplica (se quitó `skforecast`); los pines de `pandas`/`matplotlib`/`statsmodels` se mantuvieron igual de todos modos — actualizarlos es una decisión aparte, pendiente (sección f) |
| §3.4.4 | "Se evaluaron sobre él la media constante, repetir la semana anterior, L0, L1, el árbol A y el árbol B..." | Frase histórica correcta en sí misma, pero cita "Tabla 5", que va a quedar con 4 filas. Ajustar para que quede consistente con la Tabla 5 reescrita (ver ítem 5 de REESCRITURA) |
| Índice de tablas (p. 5–6) | "Tabla F1 – Efecto de limitar la profundidad del árbol B", "Tabla F2 – ... del árbol B", "Tabla F3 – ... del árbol B", "Ilustración F1 – ... el árbol B" | Cambiar "árbol B" por "árbol candidato (preliminar)" en los cuatro títulos, si el Anexo F se conserva |
| Anexo F.1 | "Script: train_base.py (modelo base, Municipio C)" | Aclarar que es el script histórico del Entregable 2, retirado de `main` el 2026-09-24 (preservado en `entregable_2`); si se reenvía al servidor una versión de `linea_base.ipynb`, documentar el script nuevo aparte |

---

## e) Lo que NO cambió (para no reescribir de más)

> **Corrección (2026-09-25):** el primer punto de esta sección era incorrecto para la fila del
> árbol candidato en la Tabla 4 (validación interna) — no estaba dentro de tolerancia, y la celda
> de no regresión nunca la verificaba. Causa, corrección y verificación en "Sesión 2026-09-25" al
> principio de este documento. El texto original queda abajo, sin reescribir, para que se vea qué
> decía antes de la corrección.

- **Ninguna cifra de las cuatro filas que sobreviven en las Tablas 1 y 5** (media constante, L0,
  L1, árbol candidato): reproducidas por `linea_base.ipynb` dentro de una tolerancia de 0,001,
  verificado por su celda de no regresión. **En la Tabla 4, la fila del árbol candidato sí
  cambió** (ver la corrección arriba): la causa era una semilla distinta a la de `base.ipynb`, ya
  corregida; L1 y media constante en la Tabla 4 nunca cambiaron.
- **Partición cronológica:** 987 / 329 / 329 días, mismas fechas (2021-07-01 → 2024-03-13 →
  2025-02-05 → 2025-12-31). No se tocó.
- **Protocolo de validación:** 47 cortes de 7 días, origen móvil, ventana expansiva, ajuste
  congelado en el bloque final. No se tocó.
- **Métricas:** desvianza de Poisson media como principal, MAE/RMSE/razón total/días con
  predicción cero como secundarias, `EPS = 1e-6` para las predicciones nulas. No se tocó.
- **Hiperparámetros y variables del árbol candidato:** `max_depth=4`, `min_samples_leaf=20`,
  rezagos de 7/14/21 días, indicadoras de fin de semana y feriado, tiempo transcurrido en años.
  No se tocó (esta tarea tenía prohibido tocarlo).
- **Tratamiento del clima:** no se modificó nada al respecto; sigue fuera del alcance de
  `linea_base.ipynb`, igual que estaba fuera del alcance de `base.ipynb` y `base_2.ipynb`.
- **Medidas contra la fuga de información (Cuadro 3, §3.4.4):** todas siguen aplicando igual.
- **Uso del bloque final durante el Entregable 2** (§3.4.4): la narrativa de que el bloque final
  fue "evaluado preliminarmente" y no debe tratarse como prueba reservada e independiente para el
  Entregable 3 sigue vigente sin cambios.
- **Aspectos éticos (§3.5):** sin relación con esta tarea, no se tocó nada.
- **Secciones de diagnóstico de datos (§4.1) y conjunto de datos preparado (§4.2):** no se tocó
  ningún notebook ni artefacto de `diagnostico_datos`, `diagnostico_datos_municipio`,
  `diagnostico_zona_contraste` ni `preparacion_montevideo`.

---

## f) Decisiones pendientes que esta tarea dejó abiertas

Ninguna se resolvió en esta sesión; todas están fuera de alcance según las instrucciones
originales ("Fuera de alcance — no hacer").

1. **Actualización de los pines de versión liberados.** Al quitar `skforecast`, las restricciones
   que fijaban `pandas < 3.0`, `matplotlib < 3.12` y `statsmodels < 0.15` dejaron de tener motivo,
   pero los pines se mantuvieron igual (`requirements.txt`, con el comentario actualizado
   explicando por qué). Subir esas versiones exige reejecutar y comparar todos los notebooks
   vigentes, incluidos los de diagnóstico.
2. **Ventana de L0** (promedio de 4 semanas): no se validó con datos de validación interna; se
   fijó a mano antes de ejecutar, igual que en `base_2.ipynb`. El propio informe (§4.3.3) ya
   declaraba esto como pendiente para el Entregable 3.
3. **Recálculo de la ACF que orienta los rezagos del árbol candidato**, usando sólo el bloque de
   desarrollo en vez del período completo (fuga leve, declarada desde `base_2.ipynb`, ver §3.4.4
   del informe, "parte del diagnóstico... se calculó sobre el período completo").
4. **Eliminación de `t_anios` (tiempo en años) del árbol candidato**, dado que el propio análisis
   (informe §4.3.2, Anexo F Tabla F3) atribuye a esa variable el mal desempeño del árbol en el
   bloque final — el árbol no extrapola la tendencia.
5. **Partición y tratamiento del clima**, a definir con el tutor — el informe mismo (§3.4.4) deja
   pendiente el diseño de la evaluación final del Entregable 3, incluyendo si se usa el semestre
   2026 recién publicado por la UNASEV.
6. **Destino del Anexo F** (ver sección d, ítem 8): si se reconstruyen las tablas F1–F3 con el
   árbol candidato a partir de `linea_base.ipynb`, o si el anexo queda como registro histórico
   apuntando a la rama `entregable_2`.
7. **Reconstrucción de una versión `.py` de `linea_base.ipynb`** para el sistema de cola del
   servidor, si el equipo quiere repetir el entrenamiento verificado que documenta el Anexo F.1
   (hoy sólo existe para los notebooks retirados).
