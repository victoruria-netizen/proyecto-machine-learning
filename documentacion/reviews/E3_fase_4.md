# Review R3 — Entregable 3, fase 4 (evaluación final y exportación)

| Campo | Valor |
| --- | --- |
| Fecha | 2026-10-21 |
| Revisor | Claude Code, modelo **Opus 5.5** (`claude-opus-5-5`). No participó en la fase 4. Archivos creados o modificados: este informe y la entrada de la sesión en `registro_uso_IA.md`. |
| Rama | `e3/fase-4-evaluacion-final` (al día con `origin/e3/fase-4-evaluacion-final`) |
| Base | `4cc063a4697dad2aa9e90a8166294084f5ae42df` (`git merge-base main HEAD`) |
| HEAD revisado | `c0f8d6104e97523c35df15d79d627a98cdee3ff9` |
| sha256 del panel | `82467fc87b5d2bceb24ec6f3c5072e1b7cf9e75507b1d5c5a4d20153114a1b06`: coincide con el esperado. Solo se calculó el hash. |
| Entorno | `.venv` activado en el mismo comando que corre Python, pytest y nbconvert; `python` = `.venv\Scripts\python.exe`, Python 3.13.2 |
| Criterios | Comunes B1 a B6 y N1 a N6 (los de la review R2). Específicos F4-B1 a F4-B5 y F4-N1 a F4-N3 del plan del Entregable 3, que el equipo pasó en esta sesión con una precisión sobre F4-N3 (registro de IA, Prompt 2). Contexto del prompt de la review: D48 y D50 a D58 mandan sobre el prompt de la fase; no se evalúa si son correctas. |

**Commits revisados** (`git log main..HEAD`, orden cronológico):

| Commit | Fecha | Mensaje (abreviado) |
| --- | --- | --- |
| `24b790e` | 2026-10-20 16:21 | Informe del PAA actualizado al 12/10/2026 (subido por el equipo) |
| `86630a3` | 16:49 | Fase 4, paso 4a y precisiones del 4b, antes de leer el bloque final (D48, D50-D52) |
| `3852498` | 19:57 | Fase 4, paso 4b: ejecución oficial (D53) |
| `ba17c8d` | 20:35 | Exportación como celdas nuevas al final (D53, D54) |
| `42fe260` | 21:04 | Correcciones de D55 antes de reejecutar |
| `d93cf0c` | 2026-10-21 08:21 | Reejecución con la exportación (`models/`) |
| `7f53fe5`, `037851b`, `3dc9d78` | 08:36 a 09:09 | `train/train_modelo_final.py`, fix de raíz y rutas relativas al script |
| `c235ce2`, `6be0383` | 09:14, 09:16 | D58: JSON en LF y reejecución vigente |
| `82c0c3a` | 09:18 | Script: informa si el sha256 del modelo coincide (D58) |
| `c0f8d61` | 10:04 | Cierre: corrida del servidor (job 136), resumen, HANDOFF, registro |

---

## Veredicto

**DESAPROBADA.** Falla un criterio bloqueante, **F4-B5**: no hay ningún test en `tests/test_modelo.py` que cargue el modelo exportado
(`models/modelo_final.json`) y compruebe que reproduce las predicciones del notebook. Los tests de guardar/cargar usan un modelo
sintético. Los otros 10 bloqueantes (B1 a B6, F4-B1 a F4-B4) y los 9 no bloqueantes cumplen.

En el fondo, el modelo exportado sí carga y reproduce las predicciones. La celda 35 del notebook lo comprueba con un `assert` en cada
ejecución. El revisor también lo comprobó por su cuenta: la salida de la celda 35 coincide exactamente a 3 decimales, y la predicción del
servidor coincide a 3,42e-12. El criterio, sin embargo, pide la evidencia en un test, y ese test no existe. La corrección es chica
(observación 1). Todo lo demás se verificó. La lectura única del bloque final está probada con git. La reejecución reproduce el registro a
2,51e-15. `experiments/` no cambió desde `3852498`, y solo cambió el código de la celda 32. El servidor coincide con la corrida local.

---

## Criterios

### Comunes

| ID | Criterio | Resultado | Evidencia |
| --- | --- | --- | --- |
| B1 | Fuera de `evaluacion_final.ipynb`, ningún código lee filas posteriores a 2025-02-05 | CUMPLE | `git grep -n "panel_diario_montevideo\|cargar_panel\|read_csv(\|RUTA_PANEL\|FECHA_FIN_PERIODO\|ULTIMO_DIA_DESARROLLO" HEAD -- '*.py'`. En `src/`, la única lectura del panel es `src/datos.py:41`, dentro de `cargar_panel_desarrollo()`, con recorte por tramo y los `assert` de las l. 47-48. `src/modelo.py` no lee archivos; su l. 9 es un docstring. `tests/test_modelo.py:242` y `tests/test_train_modelo_final.py:45` leen solo con `cargar_panel_desarrollo()`. Los otros `read_csv` de `test_modelo.py` (l. 303 a 328) leen `modelos_candidatos/tablas/31`, `45` y `46`, que son de validación. La única otra lectura completa es `train/train_modelo_final.py:82` (`leer_panel`), la excepción declarada en D51, y ningún test la llama: los tests del script usan `panel_dev` y `tmp_path` (l. 55 a 116). Los notebooks de fases anteriores no cambiaron (`git diff --stat main HEAD -- notebooks/modelos_candidatos.ipynb` vacío) |
| B2 | El notebook ejecuta de punta a punta sin errores (nbconvert en el `.venv`) | CUMPLE | `jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=-1 notebooks/evaluacion_final.ipynb`: exit 0, 98 s. En el notebook resultante hay 0 salidas `error` y 0 `stderr` (recorrido de las 37 celdas). El log de nbconvert solo muestra los dos avisos del lanzador del kernel (zmq/Proactor y «Kernel is running over TCP») |
| B3 | pytest pasa entero | CUMPLE | `python -m pytest -q`: `45 passed in 63.48s`, 0 saltados. Coincide con los 45 que declaran el resumen (l. 8) y el HANDOFF |
| B4 | Toda cifra nueva del resumen y del HANDOFF coincide con un artefacto | CUMPLE | Script propio (`cifras.py`, fuera del repo). Extrae todas las cifras decimales de `resumen_evaluacion_final.md` (312) y de las líneas agregadas al HANDOFF (11), y busca cada una, con su precisión, en las tablas de `evaluacion_final`, `modelos_candidatos` y `linea_base`, en los dos registros, en `models/*.json`, en el log del job 136 y en `resumen_corrida.json`. Quedan **0 sin coincidencia**. Como la búsqueda es permisiva, se revisaron a mano las afirmaciones con su tabla. `tablas/06`: 1,1063, 1,1198, 1,1329, 1,1359, 1,2432 y 1,3152; 33, 22, 40, 34 y 46 de 47; final − validación entre −0,0815 y −0,1195. `tablas/09`: las 5 filas, con medias, EE, razón y conteos. `tablas/17`: global y rangos por municipio, con 0,8815 (B), 0,9179 (G), 0,8700 (C), 0,9072 (CH), 0,9696 (D), 0,9909 (A), 0,9711 (C) y 0,9862 (CH). `tablas/14`: deciles 0,9426 y 1,1095, 8 de 10 por encima de 1, y la sensibilidad entre 1,0331 y 1,1985. `tablas/18`: α entre 0,0093 y 0,0339, y momentos en los cortes 45 (2025-12-11) y 47 (2025-12-25). `tablas/02`: 35 de 35, con diferencia máxima 4,97e-07 («5e-7»). `tablas/05`: 141 ajustes, 0 con `n_avisos`, 0 sin converger. Log del job 136: 4,25e-12, 3,42e-12, 5,26e-13 y 5 iteraciones. `predicciones_bloque_final.csv`: 15.793 líneas en `git diff --stat`, que con el encabezado dan las 15.792 filas |
| B5 | La sección 1 y la adenda de `modelos_candidatos` no cambiaron | CUMPLE | `git diff --stat main HEAD -- notebooks/modelos_candidatos.ipynb experiments/modelos_candidatos/ src/datos.py` vacío: ni el notebook de la fase 3, ni sus artefactos, ni el cargador del panel cambiaron en la fase 4. Las precisiones de la fase 4 están en un bloque propio, la celda 1 de `evaluacion_final.ipynb` |
| B6 | Entorno coherente | CUMPLE | `pip check`: «No broken requirements found.» Las 18 dependencias directas de `requirements.txt` tienen la misma versión en `requirements-lock.txt` y en el `.venv` (comparación una por una: 0 diferencias). `git diff --stat main HEAD -- requirements.txt requirements-lock.txt` vacío. La celda 3 (control del entorno) pasó en la reejecución. `tablas/00_entorno.csv`: Python 3.13.2 y versiones iguales a las de `metadata.json` |
| N1 | El resumen sigue la estructura de CLAUDE.md, incluida la lista de frases | CUMPLE | `resumen_evaluacion_final.md` tiene encabezado (l. 1-18), «Cómo usar» (§0), qué hace y por qué, con decisiones y motivos (§1.1 a §1.6, incluidas las ejecuciones descartadas), resultados con su artefacto (§2 a §4), limitaciones y frases (§5), diferencias con el informe y objetivos (§6), índice (§7) y pendiente (§8) |
| N2 | HANDOFF y registro de IA actualizados con cada sesión, con prompts textuales | CUMPLE | El registro tiene dos entradas de la fase 4: l. 4355, con 4 prompts, y l. 4566, con 14 prompts, que cubren D48 y D50 a D56 y D58, la corrida del servidor y el cierre. **El revisor hizo su propia comparación**: cada bloque citado con `>` está textual en el `.jsonl` de su sesión (`5ca00262-…` y `cbca8349-…`), en 18 de 18. El Prompt 5 coincide si los retornos de carro se leen como saltos de línea, como declara la entrada. El HANDOFF tiene las dos entradas de la fase 4 (l. 1998 y 2019). Hay una línea desactualizada, que no afecta el resultado (observación 3) |
| N3 | Las lecturas separan evidencia de inferencia | CUMPLE | El resumen rotula **Los datos muestran** y **Lectura del equipo (inferencia, a validar)** en §2.1, §2.2, §2.3, §3.1 a §3.4 y §4.3. El notebook no tiene lecturas: la celda 31 las remite al resumen. Hay un detalle menor de ubicación en §3.2 (observación 6) |
| N4 | Los resultados negativos quedan registrados | CUMPLE | Quedan registrados: el contraste le gana a L1 en solo 22 de 47 cortes (§2.2); la solución subestima en 7 de 8 tipos de día y los fallos se concentran por encima del intervalo (§3.1, §3.4); NB2 no convergió en la ventana final y el α es por momentos, en el piso del rango (§4.1, §5.5); el objetivo 2 no se cumplió en meteorología y el 4 no se cumplió en esta fase (§6.1); el intento con el Python del sistema, la reejecución descartada de `ba17c8d` (§1.6) y el job 135 (§4.3) |
| N5 | Código legible: sin código muerto, nombres consistentes | CUMPLE | Análisis estático (AST) de `src/modelo.py`, `train/train_modelo_final.py`, `tests/test_modelo.py` y `tests/test_train_modelo_final.py`: ningún import sin uso y ninguna función definida que no se use. Nombres en español, coherentes con `src/`. Los comentarios del script y el docstring de sus tests que citan pandas 1.5.3 son deuda declarada (HANDOFF, «Pendiente menor»), como indica el prompt |
| N6 | El alcance coincide con el prompt de la fase y con D48 y D50 a D58 | CUMPLE | Todo lo que pide el prompt está hecho. 4a: `entrenar`, `predecir_semana` y los tests de reproducción. 4b: el JSON verificado, 47 cortes, los seis modelos, métricas globales, por municipio (`tablas/07`) y por semana (`tablas/08`), la comparación contra L1, L0, la media constante y la validación (`tablas/06`, columnas `desvianza_validacion` y `dif_final_menos_validacion`), errores, peores semanas, deciles, cobertura, objetivos (`tablas/19`), predicciones con las columnas pedidas (encabezado: `fecha,origen,corte,municipio,observado,predicho,inf_80,sup_80,inf_95,sup_95,tipo_intervalo,modelo,papel`) y el registro. 4c: el modelo en JSON sin pickle, `metadata.json`, el script del servidor, el log guardado y comparado, y «Diferencias con el informe». `historia_reciente.csv` no existe, por D51. **Limitaciones de la verificación:** **D57 no aparece en ningún archivo del repositorio**, así que no se pudo contrastar el alcance contra ella (observación 5). El resumen dice cómo se identifica el commit del modelo, pero no da el hash (observación 4) |

### Específicos de la fase 4

| ID | Criterio | Resultado | Evidencia |
| --- | --- | --- | --- |
| F4-B1 | `solucion_seleccionada.json` no cambió desde el commit de la fase 3 (`1560a5b`, por `git log`, D46) | CUMPLE | `git log -- experiments/modelos_candidatos/solucion_seleccionada.json`: una sola línea, `1560a5b 2026-10-19 23:44`. `git diff --stat 1560a5b HEAD -- …json` vacío. `git merge-base --is-ancestor 1560a5b 86630a3`: verdadero. El notebook entra en `86630a3` (`git log --diff-filter=A`). En la reejecución, la celda 7 dio `True` en sus 6 verificaciones: un único commit (`1560a5b`), el árbol igual a `1560a5b`, `1560a5b` como antecesor de HEAD, todo commit del notebook posterior, `bloque_final_leido = false` y D42 |
| F4-B2 | El bloque final se lee solo en `evaluacion_final.ipynb` | CUMPLE | Ver B1. En el notebook, la lectura completa está en la celda 13 (`pd.read_csv(datos.RUTA_PANEL)`), después del encabezado «⛔ Desde aquí se lee el bloque final» (celda 12). El control en validación (celda 11) usa `cargar_panel_desarrollo()`. La única excepción es `train/train_modelo_final.py`, declarada en D51, en el encabezado del script y en el resumen (§4.2). El revisor no leyó el bloque final fuera de su única reejecución completa. Los controles de cifras leyeron tablas de resultados, y de `predicciones_bloque_final.csv` solo el encabezado |
| F4-B3 | La reejecución reproduce las métricas del registro | CUMPLE | Celda 26 de la reejecución del revisor: «máxima diferencia relativa con el registro: 2.5125104284824626e-15. Reejecución: las métricas coinciden (tolerancia relativa 1e-10) con la primera ejecución del 2026-10-20T19:28:50 (commit 86630a3)». La comparación usa `np.isclose(rtol=1e-10, atol=0)` sobre 14 métricas por modelo. `git diff --stat -- experiments/` quedó vacío: ni el registro ni las tablas cambiaron. Las reejecuciones commiteadas `d93cf0c`, `6be0383` y `c0f8d61` muestran la misma cifra en su celda 26. Detalle en «Resultado de la reejecución» |
| F4-B4 | Las referencias y el contraste se evaluaron con el mismo procedimiento que la solución | CUMPLE | Celda 9, `backtest(panel, origenes)`. En cada corte arma **una** vista con `n_siniestros` en NaN para los días ≥ origen. Los tres candidatos (solución, sensibilidad y contraste) se entrenan con `mod.entrenar(cfg, hasta)` y se predicen con `mod.predecir_semana(m, vista, origen)`. Las tres referencias usan la misma vista y el mismo origen. Todos se comparan contra el mismo `real`, con `assert len(p) == len(real) == 56`. Los mismos 47 orígenes (`ORIGENES_FINAL`, celda 13) sirven para los seis. Los hiperparámetros salen del JSON (`CFG`). La celda 15 comprueba 364 días en la solución y el contraste, la expansiva en la sensibilidad y `hasta = origen − 1` en todos. El mismo `backtest` reprodujo la validación de los seis modelos (celda 11, 35 de 35) |
| F4-B5 | El modelo exportado carga y reproduce las predicciones del notebook (test en `tests/test_modelo.py`) | **NO CUMPLE** | Ningún test de `tests/` abre `models/modelo_final.json`. `grep -rn "models/\|modelo_final" tests/` solo encuentra un docstring de `test_modelo.py:154` y las pruebas de rutas de `test_train_modelo_final.py` (l. 92 a 100). Los tests de guardar/cargar (`test_guardar_y_cargar_ida_y_vuelta`, l. 123, y `test_cargar_y_predecir_sin_statsmodels_ni_xgboost`, l. 190) guardan y cargan un modelo **sintético** entrenado en el test (fixture `sintetico`, l. 47). Prueban el mecanismo, no el artefacto exportado. Hay otra evidencia, pero no es un test. (i) La celda 35 tiene un `assert` de que el modelo leído del JSON predice igual que el que está en memoria (salida: «predicciones idénticas (56 filas)»). (ii) Comprobación del revisor: `mod.cargar_modelo("models/modelo_final.json")` y `predecir_semana` con una historia vacía, sin leer el panel, dan 56 filas, y la diferencia máxima contra los 56 valores impresos en la celda 35 de HEAD (3 decimales) es **0,0**. La diferencia relativa máxima contra `prediccion_semana_2026-01-01.csv` del servidor es 3,42e-12 (observación 1) |
| F4-N1 | La comparación con referencias y objetivos separa evidencia de inferencia | CUMPLE | §2.1: «Los datos muestran» con las cifras de `tablas/06`, y «Lectura del equipo» con la explicación del bloque más fácil. §2.2: «Las razones media/EE no son pruebas de significación», con el motivo. §6.1 y `tablas/19`: los estados se fijaron antes de leer el bloque (D52, ítem 8), con una columna de evidencia aparte; el resumen dice que las cifras del bloque final «se agregan como evidencia, sin cambiar el estado» |
| F4-N2 | El log del servidor está incorporado y coincide con la corrida local | CUMPLE | `documentacion/logs/log_servidor_modelo_final.txt` (job 136, RUN_ID `20261021_094404`). Implementación IRLS en numpy (l. 34) y versiones del contenedor (l. 36). El sha256 del panel coincide (l. 46) y el del modelo coincide con `sha256_modelo` (l. 127). Diferencias contra el local: coeficientes 4,248798842213082e-12, μ 3,416353505867013e-12 y α 5,256744700594516e-13, que dan «CUMPLE» (l. 129-132). **Recálculo del revisor** desde los archivos del servidor contra `models/modelo_final.json`: coeficientes 4,2488e-12 (15 de 15), α 5,2567e-13 y μ de las 56 filas 3,4162e-12, calculado desde el CSV, que trae los valores redondeados a repr. Las cifras coinciden. El job 135 (`…_intento1_job135.txt`) termina con «panel … (NO EXISTE)» y `exit code 1`, como dice el resumen. §4.3 cita las cifras del job 136, y §4.2 aclara que el chequeo en el entorno simulado «no es evidencia del servidor» y que sus cifras no se citan |
| F4-N3 | `metadata.json` completo; los conteos agregados, según D51 | CUMPLE | Campos de `models/metadata.json`: `configuracion` (con conjunto, ventana, reentrenamiento y validación), `fecha_de_corte` 2025-12-31, `versiones` (9), `panel.sha256` (igual al esperado), `intervalos.alpha` 0,00939508767764091 con `origen_alpha` «momentos» (D44 y fallback de D50), `commit_base` y `commit_base_nota` (D48), y `fuentes_limpias` con su definición, en lugar de `arbol_limpio` (D54). Tiene además `sha256_modelo`, `entrenamiento` y `solucion_seleccionada.commit_fase3` (`1560a5b…`). **Conteos agregados (D51):** `git ls-files models/` da solo `.gitkeep`, `metadata.json` y `modelo_final.json`; no hay `historia_reciente.csv`. El resumen explica por qué en §1.5 («el conjunto (a) no usa nivel reciente ni rezagos (D51)») y al final de §6 |

### Comprobaciones del contexto de la review

| Comprobación | Resultado | Evidencia |
| --- | --- | --- |
| `86630a3` tiene las precisiones, es anterior a la ejecución oficial y no contiene salidas del bloque final | CUMPLE | `git merge-base --is-ancestor 86630a3 3852498`: verdadero (16:49 < 19:57). `git ls-tree -r 86630a3` no tiene `experiments/evaluacion_final/`, y en `models/` solo está `.gitkeep`. El notebook de `86630a3` tiene 33 celdas, **0 salidas** y ningún `execution_count`. La celda 1 es «Precisiones de la evaluación final, fijadas antes de leer el bloque final (D48, D50, D51 y D52)». La fuente de las 33 celdas es idéntica en `86630a3` y en `3852498`: la ejecución oficial corrió el código commiteado |
| Ejecución oficial = `3852498` (registro 2026-10-20T19:28:50, commit base `86630a3`) | CUMPLE | `registro_ejecucion.csv`: 6 filas con `fecha_hora` 2026-10-20T19:28:50 y `commit` `86630a3df1eb…`. La celda 26 de `3852498` imprime «guardado: … registro_ejecucion.csv (6 filas) — primera ejecución completa» |
| Las reejecuciones reproducen el registro dentro de 1e-10 | CUMPLE | Celda 26 de `d93cf0c`, `6be0383` y `c0f8d61`, y la reejecución del revisor: 2,5125104284824626e-15 |
| `experiments/evaluacion_final/` no cambió desde `3852498` | CUMPLE | `git log -- experiments/evaluacion_final/` da solo `3852498`. `git diff --stat 3852498 HEAD -- experiments/evaluacion_final/` vacío |
| Ninguna celda de `3852498` cambió de código, salvo la 32 (D55) | CUMPLE | Comparación celda por celda (`comparar_nb.py`). `ba17c8d` no tiene ninguna celda previa con fuente distinta y agrega 4 celdas (33 a 36). Desde `42fe260` hasta `c0f8d61`, la única celda previa con fuente distinta es la **32**. Las salidas de texto distintas de las previas son las de las celdas 7 («commits de este notebook antes de esta ejecución: 1» → «6»), 26 (registro reproducido en lugar de escrito), y 18 y 20, donde un stream de stdout aparece partido distinto, con el mismo texto. D55 acepta la 7 y la 26 |
| `arbol_limpio = False` explicado (D53) | CUMPLE | Resumen §1.6, l. 124 a 128: se calculó después de que la ejecución creara `experiments/evaluacion_final/`, y la evidencia de árbol limpio es `86630a3`, pusheado antes. La celda 26 del notebook confirma que `git status --porcelain` se evalúa en ese punto. No es hallazgo |
| Servidor: el resumen cita el job 136 y no el entorno simulado | CUMPLE | Ver F4-N2. §4.3 cita el log y `servidor_modelo_final/`. §5 prohíbe presentar las cifras del entorno simulado como del servidor |
| Alineación (D49): «Diferencias con el informe» con qué dice el informe, qué se hizo y por qué | CUMPLE | §6 es una tabla de 10 filas con las columnas «Qué dice el informe», «Qué se hizo» y «Por qué», todas completas. Se contrastaron citas con `Informe_PAA_Actualizado_el_12-10-26.md`: «el ajuste queda congelado» (l. 608), «Python 3.13.15» (l. 642), «últimas cuatro semanas» (l. 628), «Media móvil de 56 días» (l. 630), pandas 1.5.3 del contenedor (l. 648), calendario de «tres niveles» (l. 545) y «repetir la semana anterior» y árboles A y B (l. 591). Están en el informe. No se evalúa si las diferencias son aceptables |
| Frases: el pareado no se presenta como prueba de significación | CUMPLE | §2.2, l. 171: «Las razones media/EE no son pruebas de significación», con el motivo. §5, l. 390, prohíbe «significativamente mejor». `grep -i significa` no encuentra otro uso |
| Frases: la cobertura no se compara contra la nominal sin la esperada | CUMPLE | §3.4 compara la empírica con la esperada por el modelo (0,9005 contra 0,8871; 0,9791 contra 0,9810), y §5, l. 391, prohíbe la comparación contra la nominal. Hay dos lugares donde la cobertura aparece rotulada solo con el nivel nominal, sin la esperada (§3.4, l. 278, y §6.1, objetivo 3). No la comparan con la nominal, pero conviene completarlos (observación 7) |
| Frases: el test no se presenta como validación de D42 | CUMPLE | §5, l. 394-395: «El test confirma la elección de la ventana deslizante» está prohibida. La única mención de D42 junto a resultados del bloque (§3.3, «uno de los motivos de D42») está bajo «Lectura del equipo», que dice «No es una prueba». §6, fila 8, y §6.1 tratan D42 como salvedad |

---

## Resultado de la reejecución

Una sola reejecución completa, con el árbol limpio, antes de escribir este informe. Así `fuentes_limpias` no ve archivos nuevos.

| Paso | Comando | Resultado |
| --- | --- | --- |
| Previo | `git status --porcelain --untracked-files=all` | vacío; HEAD `c0f8d61` |
| pytest | `python -m pytest -q` | `45 passed in 63.48s`, 0 saltados |
| nbconvert | `jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=-1 notebooks/evaluacion_final.ipynb` | exit 0, 98 s; 0 salidas `error` y 0 `stderr` |
| Registro | celda 26 | diferencia relativa máxima 2,5125104284824626e-15: «las métricas coinciden (tolerancia relativa 1e-10)… El registro no se reescribe» |
| `git status` | — | `M models/metadata.json`, `M notebooks/evaluacion_final.ipynb` |
| `git diff --stat -- experiments/` | — | **vacío** |
| `git diff -- models/` | — | **No vacío.** Solo cambian dos campos de `metadata.json`: `fecha_generacion` (2026-10-21T09:16:03 → 10:34:31) y `commit_base` (`c235ce2…` → `c0f8d61…`). `modelo_final.json` no cambió, y `fuentes_limpias` sigue en `true`. Esos dos campos registran, por diseño, el HEAD y la hora de generación, así que cambian en toda reejecución (observación 2) |
| Notebook contra HEAD | `post.py` | 0 celdas con fuente distinta. Las salidas de texto cambian solo en la celda 7 («… antes de esta ejecución: 7») y en la 34 (`commit_base`). La celda 35 imprime los mismos coeficientes, el mismo α (0.00939508767764091, momentos) y la misma tabla de μ |
| Restauración | `git restore notebooks/ models/ experiments/`, `git status --porcelain` | vacío |

**Ninguna cifra de la evaluación cambió.**

---

## Observaciones

1. **F4-B5 (bloqueante): falta el test del modelo exportado.** `tests/test_modelo.py` prueba guardar y cargar con un modelo sintético,
   pero ningún test carga `models/modelo_final.json` ni compara sus predicciones con las del notebook. *Corrección:* agregar a
   `tests/test_modelo.py` un test que haga lo siguiente. (a) Verificar que el sha256 de `models/modelo_final.json` es igual a
   `sha256_modelo` de `metadata.json`. (b) Cargarlo con `mod.cargar_modelo`. (c) Predecir la semana del 2026-01-01 con una historia vacía,
   como en `_SIN_STATSMODELS_NI_XGBOOST`. (d) Comparar contra un artefacto con las predicciones del notebook. Hoy ese artefacto no existe,
   porque la celda 35 solo imprime la tabla a 3 decimales. Hay dos opciones, y decide el equipo. (i) Una celda nueva al final de la
   sección 13 que guarde las 56 predicciones, por ejemplo `models/prediccion_semana_2026-01-01.csv`, con igualdad exacta en el test; por
   D53, el código se commitea antes de reejecutar, y después se verifica de nuevo el registro y `experiments/`. (ii) Comparar contra
   `documentacion/logs/servidor_modelo_final/prediccion_semana_2026-01-01.csv` con la tolerancia de D56, pero eso compara contra el
   servidor y no contra el notebook. Ninguna de las dos necesita leer el panel.
2. **La comprobación «`git diff` vacío en `models/`» no se puede cumplir al pie de la letra.** Cada reejecución reescribe
   `commit_base` y `fecha_generacion` de `metadata.json`. Pasó en esta review y también entre `d93cf0c` y `6be0383`. No es un problema de
   reproducción, porque el modelo y el resto de la metadata no cambian. Sí deja el árbol sucio después de cualquier reejecución, y el
   resumen (§1.6) solo declara «`git diff` sobre `experiments/` vacío». *Corrección:* declarar, en el resumen o en una decisión del
   equipo, que la comprobación de `models/` es `modelo_final.json` idéntico más `metadata.json` igual salvo esos dos campos, o bien que la
   reejecución de verificación no reescriba `metadata.json`.
3. **La línea de estado del HANDOFF está desactualizada.** `HANDOFF.md:6` dice «corrida del servidor pendiente», pero la corrida se hizo
   (job 136) y está documentada en el mismo archivo (l. 2057). *Corrección:* actualizar la línea a «verificado en el servidor (job 136)».
4. **El resumen no da el commit que contiene el modelo.** §1.5 dice que se identifica con `git log -- models/modelo_final.json`, y §4.1 da
   solo `commit_base` (`c235ce2`). `git log -- models/modelo_final.json` devuelve un solo commit, **`d93cf0c`**: el blob no cambió en
   `6be0383` (D58). Como el documento existe para leerse sin el repositorio, la cifra tiene que estar escrita. *Corrección:* agregar a la
   tabla de §4.1 la fila «Commit que contiene el modelo (`git log`): `d93cf0c`».
5. **D57 no figura en ningún archivo.** El prompt de la review habla de «D50 a D58», pero el HANDOFF y el resumen §1.2 saltan de D56 a
   D58, y `grep D57` no encuentra nada en el repositorio. *Corrección:* si D57 es una decisión del equipo, asentarla en el HANDOFF y en el
   resumen; si el número no se usó, decirlo, para que no parezca una decisión perdida.
6. **En §3.2 hay una inferencia bajo «Los datos muestran».** «La desvianza alta viene de la distribución entre días y municipios, no del
   volumen semanal» es una lectura, aunque sea razonable. *Corrección:* pasarla a «Lectura del equipo». Lo mismo vale para «coherente con
   la subestimación del total» en §3.4.
7. **Hay coberturas sin la esperada por el modelo.** §6.1, objetivo 3, dice «cobertura NB2 0,9005 (80 %) y 0,9791 (95 %)», y §3.4, l. 278,
   da las coberturas de validación de la misma forma. No hay una comparación explícita con la nominal, pero si esas frases pasan al informe
   pueden leerse así. *Corrección:* agregar la esperada en el texto del resumen (0,8871 y 0,9810 en el test; las de validación, según
   `modelos_candidatos/tablas/46`). `tablas/19` es un artefacto de la ejecución oficial y no se toca.

---

## Riesgos fuera de criterios (no afectan el veredicto)

- **R1. Versionado de conteos observados del bloque final.** `predicciones_bloque_final.csv` versiona la columna `observado`, es decir,
  los conteos diarios por municipio de 2025-02-06 a 2025-12-31. Es el mismo tipo de dato agregado por el que el prompt del 4c pedía
  confirmación antes de versionar `historia_reciente.csv`. Ya hay precedente (`modelos_candidatos/tablas/31` versiona los del desarrollo)
  y el prompt pidió guardar el archivo, pero no encontré una confirmación explícita sobre las restricciones de uso de estos conteos.
  Conviene que el equipo la asiente.
- **R2. El log no identifica la versión del script que corrió.** El log del job 136 no tiene el sha256 ni el commit de
  `train_modelo_final.py`. Lo que hay es indirecto: el log imprime la comparación del sha256 del modelo («coincide con sha256_modelo»),
  que solo existe desde `82c0c3a` (09:18), y el trabajo corrió a las 09:44. `git log -- train/train_modelo_final.py` no tiene commits
  posteriores. En una corrida futura convendría que el script imprima su propio sha256.
- **R3. El α del modelo exportado sale del plan B.** NB2 no convergió en la ventana final (`nb2_avisos`: «invalid value encountered in
  log»), y el α por momentos (0,009395) está en el piso del rango del test. Está declarado (§4.1, §5.5). En la fase 5, los intervalos del
  prototipo dependen de este valor.
- **R4. La evidencia del modelo exportado vive en el notebook y no en `pytest`.** Hasta que se corrija la observación 1, un cambio en
  `cargar_modelo` o en `predecir_semana` que rompa la lectura de `models/modelo_final.json` pasaría los 45 tests: solo lo detectaría una
  reejecución del notebook, que lee el bloque final, o del script del servidor.
- **R5. La deuda declarada sigue abierta.** Los comentarios del script y el docstring de sus tests citan pandas 1.5.3. No afecta el
  cálculo, pero contradice §4.3 y `train/README.md`. Conviene corregirlo en el próximo cambio del script y volver a correrlo.

---

## Scripts del revisor

Están fuera del repositorio, en el scratchpad de la sesión (`…/scratchpad/rev4/`), y no dejaron artefactos en el repo. Leen copias del
notebook en `86630a3`, `3852498`, `ba17c8d`, `42fe260`, `d93cf0c`, `c235ce2`, `6be0383` y `c0f8d61`, extraídas con `git show`, y una copia
de la reejecución:

- `comparar_nb.py`: celdas, fuente y salidas de texto de cada versión contra `3852498`, más salidas en `86630a3`.
- `detalle_salidas.py`: diff de las salidas de las celdas 7, 18, 20 y 26.
- `post.py`: después de la reejecución, `error`/`stderr`, fuente y texto contra HEAD.
- `cifras.py`: B4, cifras decimales del resumen y del HANDOFF contra los artefactos.
- Comprobaciones en línea (sin archivo): carga de `models/modelo_final.json` y predicción de la semana del 2026-01-01 contra la celda 35 y
  el CSV del servidor; coeficientes y α del servidor contra el local; citas del registro contra los `.jsonl`.
