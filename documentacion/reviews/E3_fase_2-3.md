# Review R2 — Entregable 3, fases 2 (experimentación) y 3 (selección y análisis)

| Campo | Valor |
| --- | --- |
| Fecha | 2026-10-20 |
| Revisor | Claude Code, modelo **Opus 5.5** (`claude-opus-5-5`), según D25. No participó en las fases revisadas. Archivos creados o modificados: este informe y la entrada de la sesión en `registro_uso_IA.md`. |
| Rama | `e3/fase-3-seleccion` («Your branch is up to date with 'origin/e3/fase-3-seleccion'») |
| Base | `b59794cbae32e478408cea800faafe4e22f1e7f5` (`git merge-base main HEAD`) |
| HEAD revisado | `508c46e54fc7e748bd89f4fb33617297bbdf8d5d` |
| sha256 del panel | `82467fc87b5d2bceb24ec6f3c5072e1b7cf9e75507b1d5c5a4d20153114a1b06`: coincide con el esperado. Solo se calculó el hash. |
| Entorno | `.venv` activado en cada comando; Python 3.13.2 (`python --version` y celda de la sección 0) |

**Commits revisados** (`git log --format='%H %s' main..HEAD`, en orden cronológico; coincide con el orden pedido):

| Fase | Commit | Mensaje | Fecha |
| --- | --- | --- | --- |
| 2 | `2936c72a2053d1c9b59b5478af08e9b87b5aa606` | Precisiones de la fase 2 previas a los candidatos (D31-D34) | 2026-10-19 20:24 |
| 2 | `dec597de5625688ac3503b6cb3a335066d4fdeeb` | Fase 2, paso A: conjuntos de variables (GLM Poisson y XGBoost) | 21:02 |
| 2 | `624b7e340c43fcb9743b08cd9533e8db5a435e27` | Precisiones del paso B (D36-D38) | 21:23 |
| 2 | `80bedb7cad6f93b165f0a74415119187b8fe8416` | Fase 2, paso B: grilla de XGBoost y binomial negativa NB2 | 21:49 |
| 2 | `2cd97dca281f161f0b311ee03985c32501462acb` | Precisiones del paso C (D39-D40) | 21:58 |
| 2 | `5f207e241f43c0ad902da5f6e06da353a5ea12bf` | Fase 2, paso C: ventanas de entrenamiento | 22:38 |
| 3 | `1560a5bdddec4c433911a12e4968f19bd4a4f164` | Fase 3, paso 3a: configuración de la solución (D42) | 23:44 |
| 3 | `508c46e54fc7e748bd89f4fb33617297bbdf8d5d` | Fase 3, pasos 3b y 3c: explicabilidad, errores, intervalos y robustez (D43-D45) | 2026-10-20 00:32 |

---

## Veredicto

**APROBADA CON OBSERVACIONES.** Los 14 criterios bloqueantes cumplen (B1 a B6, F2-B1 a F2-B4, F3-B1 a F3-B3). Falla un no bloqueante, **N2**: el prompt de la fase 3 no está transcrito textualmente en el registro de IA. El recálculo independiente de la regla elige lo mismo que el notebook en A, B y C. La verificación de fuga independiente da diferencia exactamente 0. La reejecución no cambia ninguna cifra. D42 está declarada como decisión del equipo y en ningún lado se presenta como elección de la regla. Las observaciones 2 a 5 no afectan el veredicto.

---

## Criterios

| ID | Criterio | Resultado | Evidencia |
| --- | --- | --- | --- |
| B1 | Fuera de `evaluacion_final.ipynb`, ningún código lee filas posteriores a 2025-02-05 | CUMPLE | Mismo criterio que la R1. Búsqueda de `panel_diario_montevideo\|cargar_panel\|read_csv(\|RUTA_PANEL` en `*.py` y `*.ipynb`. En `src/`, `tests/` y `modelos_candidatos.ipynb` la única lectura del panel es `src/datos.py:41`, dentro de `cargar_panel_desarrollo()`, que recorta cada tramo. El notebook la usa una sola vez (celda de la sección 2, que verifica «ninguna fila posterior a 2025-02-05»). La sección 11 usa `ORIGEN_FINAL = 2025-02-06` solo como origen ficticio, con `assert panel["fecha"].max() == ULTIMO`. La otra lectura es `experiments/linea_base/tablas/04_desarrollo_backtesting.csv` (desarrollo). Las lecturas de `diagnostico_municipios`, `linea_base` y `preparacion_montevideo` son de fases anteriores y no están en el diff. `evaluacion_final.ipynb` no existe en la rama (`git ls-tree -r HEAD` sin coincidencias). |
| B2 | El notebook ejecuta de punta a punta sin errores (nbconvert en el `.venv`) | CUMPLE | `jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=-1 notebooks/modelos_candidatos.ipynb` en el `.venv`: exit 0, 16 min 47 s. En el notebook resultante: 0 salidas `error` y 0 salidas `stderr` (recorrido de todas las celdas). En el log de nbconvert solo aparecen dos avisos del lanzador del kernel (zmq/Proactor y «Kernel is running over TCP»), que no son salidas de celdas. |
| B3 | pytest pasa entero (15 pasados, 0 saltados) | CUMPLE | `python -m pytest -q` en el `.venv`: `15 passed in 3.94s`, sin saltados. |
| B4 | Toda cifra nueva del resumen y del HANDOFF coincide con un artefacto | CUMPLE | Script propio (`buscar_cifras.py`, fuera del repo): extrae las cifras decimales de §3b a §3g y §5 del resumen (696 distintas) y de las líneas agregadas al HANDOFF (70), y busca cada una, con su precisión, en las 49 tablas de HEAD y en el registro. Sin coincidencia directa: 6 en el resumen y 1 en el HANDOFF. Revisadas a mano: +0,0002 (1,221890 − 1,221665, registro), 0,0036 (XGBoost (0): 1,290019 − 1,286448), 5,1 % (1,0513, `tablas/44`), 0,0341 (fase 1), 44,86 (verificación de fuga declarada sin artefacto, §3e.4) y 0,0076, que solo está en una salida impresa del notebook (`0.00762`, sección 12), no en una tabla (obs. 4). Conteos recalculados desde las tablas: 26, 33 y 38 de 47 (`tablas/13`); 30/31/29/26/25/25/20/11/9/30 (`tablas/28`, §3d.5); 8 de 10 deciles (`tablas/42`); semanas, rangos de L1, totales y feriados (`tablas/40`); días con desvianza > 2,4 y rangos del corte 43 (`tablas/41`). Todos coinciden. |
| B5 | La sección 1 y la adenda son idénticas a las de `b59794c`; solo hay bloques fechados agregados debajo | CUMPLE | Comparación del texto de las celdas entre `b59794c` y HEAD: «## 1. Reglas fijadas» y «## Adenda a la sección 1» son idénticas (sha256 `2e29652a5de54939…` y `65147a9281dd7d71…` en los dos). De las celdas de la base, solo cambiaron el encabezado (se agregaron párrafos sobre las fases 2 y 3) y «Estado y artefactos» con su índice. Debajo de la adenda hay cinco bloques nuevos (fase 2, paso B, paso C, D42, fase 3). Ninguno cambió después del commit que lo agregó (comparación commit a commit). |
| B6 | Entorno coherente: verificación del notebook en verde; pip check limpio; requirements y lock coinciden | CUMPLE | `pip check`: «No broken requirements found.» Las 18 dependencias directas de `requirements.txt` tienen la misma versión en `requirements-lock.txt` y en el `.venv` (comparación una por una). `git diff b59794c HEAD -- requirements.txt requirements-lock.txt`: vacío. Celda de la sección 0: «Entorno OK — Python 3.13.2, 18 dependencias directas verificadas contra requirements.txt (ninguna diferencia).» |
| N1 | El resumen sigue la estructura de CLAUDE.md, incluida la lista de frases | CUMPLE | Tiene encabezado (§ inicial), «Cómo usar» (§0), qué hace y por qué (§1, §3b.1, §3c.1, §3d.1, §3e.1, §3f.1, §3g.1), resultados con artefacto (§3 a §3g), limitaciones y frases (§5), índice (§6), pendiente (§7) y cambios de alcance (§8). Hay contenido desactualizado que no afecta la estructura (obs. 2). |
| N2 | HANDOFF y registro de IA actualizados con cada sesión, con prompts textuales | **NO CUMPLE** | Hay entradas de HANDOFF y del registro para A, B, C, 3a y 3b-3c. Pero el Prompt 1 de la sesión 3a (`registro_uso_IA.md`, entrada «fase 3: selección, paso 3a») no está textual: abrevia las reglas con «[...reglas de la sesión: …]» y corta los pasos 3b y 3c con «[El prompt seguía con los pasos 3b y 3c, que esperan a la confirmación de esta parada.]». La entrada siguiente («dale, segui con 3b y 3c») dice que esos pasos «son los del prompt de la fase registrado en la entrada anterior», así que el texto de 3b/3c no quedó registrado en ningún lado. Tampoco está transcrito el mensaje del equipo que autorizó el último commit («si termina y los resultados salen bien, hace el commit»); se cita, pero no como prompt (obs. 1). |
| N3 | Las lecturas separan evidencia de inferencia | CUMPLE | Las celdas 7.1, 8.1, 9.1, 11.1 y 12.1 y sus espejos (§3b.6, §3c.6, §3d.6, §3f.5, §3g.9) tienen bloques **Evidencia** e **Inferencia** separados. Hay algunos detalles menores de ubicación, por ejemplo una explicación «por ser conteos chicos» dentro de Evidencia (12.1), que no cambian el sentido (obs. 5). |
| N4 | Los resultados negativos quedan registrados (incluida la XGBoost peor que L1, D39) | CUMPLE | D39 y §3c.6: «la "mejor de XGBoost" del paso B tiene mayor desvianza media que L1 […] queda reportado como tal» (1,2375 contra 1,2319, `tablas/18`). También quedan registrados: (0) peor que L1 en las dos familias; ningún conjunto se distingue de L1 por 1 EE; NB2 no mejora la desvianza; d=2 n=100 lr=0,05 fuera de 1 EE; la expansiva, la peor ventana del GLM en desvianza; coberturas por debajo de lo esperado; G mejora al excluirlo. Las 38 configuraciones están en el registro (F2-B3). |
| N5 | Código legible: sin código muerto, nombres consistentes | CUMPLE | Análisis estático (AST) del código de las 41 celdas: ningún nombre asignado sin leer y ningún import sin uso (solo el parámetro `_` de un formateador). Nombres en español, coherentes con las secciones 0 a 6. Menores, sin efecto: lambdas asignadas a nombres (`f`, `f6`) y reutilización de nombres globales (`estab`, `filas`, `g`, `d`) entre secciones (obs. 5). |
| N6 | El alcance coincide con los prompts de las fases 2 y 3 y con D31 a D45 | CUMPLE | Lo que piden los prompts registrados está hecho: paso A (16 configuraciones), B (12 + NB2), C (8), 3a (bloque D42, JSON, `tablas/32`), 3b (coeficientes D45, permutación por grupos, dependencia parcial del contraste) y 3c (errores por municipio, tipo de día y 5 semanas, calibración y residuos, intervalos D44 NB2 y Poisson, pareado D35, exclusión D43, frases). No se encontró nada fuera de alcance. Limitación de la verificación: **D35 se usa pero no está definida en ningún archivo del repositorio, y D41 no aparece en ninguno**, así que no se pudo contrastar el alcance contra ellas (obs. 3). |
| F2-B1 | Cada bloque de precisiones está en un commit anterior a los resultados que gobierna | CUMPLE | `git log`: 2936c72 (20:24) antes de dec597d (21:02); 624b7e3 (21:23) antes de 80bedb7 (21:49); 2cd97dc (21:58) antes de 5f207e2 (22:38). `git show --stat`: cada commit de precisiones toca solo el notebook y el resumen, y la comparación de celdas muestra que agrega **una sola celda markdown**, sin código ni salidas. Cada bloque es idéntico en todos los commits posteriores. |
| F2-B2 | La regla recalculada (Paso 2.4) elige las mismas configuraciones en A, B y C | CUMPLE | Ver «Recálculo de la regla». A: GLM Poisson (a) y XGBoost (a); B: GLM Poisson (a) y XGBoost (a) d=2 n=100 lr=0.1; C: GLM Poisson (a) [expansiva]. Coinciden con las filas «ELEGIDO/ELEGIDA» de `tablas/14`, `23` y `29`. |
| F2-B3 | El registro tiene todas las combinaciones pedidas (16 A, 13 B, 8 C, NB2 364 d del 3c) | CUMPLE | `registro_experimentos.csv` de HEAD: 38 filas, `{'A': 16, 'B': 13, 'C': 8, '3c': 1}`. Incluye las que perdieron: las seis de (0), d=2 n=100 lr=0,05 fuera de 1 EE, las cuatro de XGBoost en C y NB2 (a) [deslizante 364 d] (1,220505). |
| F2-B4 | Ningún modelo usa variables fuera de su conjunto; GLM y XGBoost usan la misma matriz (D31) y la forma de D34 | CUMPLE | Código: `columnas_conjunto` y `disenio` (sección 7); los dos modelos toman `ent[cols]` de la misma `matrices()`. Comprobación independiente (`verificacion_matriz.py`): con una matriz escrita por el revisor (8 municipios sin constante, 7 de calendario, 7 `a_x_*` sin lunes, log(nivel reciente), rezagos crudos) se reproducen, en el corte 1, GLM (c) N=28 (23 columnas), GLM (0) N=91 (13), XGBoost (0) N=28 (13) y XGBoost (c) N=28 (23), con diferencia máxima ≤ 4,97e-07 contra `tablas/17` (redondeo a 6 decimales). En la verificación de fuga se reproducen igual el GLM y la XGBoost (a) de 364 d con 15 columnas, contra `tablas/31`. |
| F2-N1 | Las advertencias de convergencia están reportadas, no silenciadas | CUMPLE | `con_avisos` registra todos los avisos con `simplefilter("always")`; solo se filtra el `DeprecationWarning` de `pd.Timedelta`, declarado. `n_avisos` y `avisos` por ajuste en `tablas/16`, `24` y `30` (por ejemplo, las 376 filas de `tablas/30` con `avisos` vacío); `cortes_con_avisos` y `cortes_no_convergidos` en el registro; NB2 con D29 (`tablas/21`, `45`); exclusión, «0 no convergidos, 0 avisos» (salida impresa). Las salidas `stderr` de la reejecución: 0. |
| F2-N2 | Están reportados el α de NB2 por corte y la dispersión de Pearson del GLM Poisson | CUMPLE | α por corte: `tablas/21` (paso B, 47 filas) y `tablas/45` (364 d, 47 filas, con `alpha_usado`). Dispersión de Pearson: `tablas/15` (resumen de (a) expansiva), por ajuste en `tablas/16` y `30` (columna `dispersion_pearson`) y para el ajuste final en `tablas/33` (1,1006). |
| F2-N3 | Cada tabla de comparación muestra el error estándar y marca los empates | CUMPLE | `tablas/11`, `18` y `26` tienen `error_estandar`, `a_menos_de_1_ee_del_mejor_de_la_tabla` y `…_de_su_familia`; `12`, `19` y `27`, `error_estandar` y `a_menos_de_1_ee_del_mejor_del_municipio`; `14`, `23` y `29`, el EE y el umbral de cada paso; `47`, el EE de la diferencia. Las tablas del resumen (§3b.2, §3c.3, §3d.2) llevan columna EE y marca o umbral. |
| F3-B1 | El JSON coincide con D42, registra que la regla eligió la expansiva y que el equipo se apartó, e incluye sensibilidad y contraste | CUMPLE | `solucion_seleccionada.json`: `decision` "D42"; `origen_de_la_eleccion` «decisión del equipo D42, apartándose de la regla»; `solucion` = GLM Poisson (a) [deslizante 364 d], `ventana {"tipo": "deslizante", "dias": 364}`, 15 columnas, reentrenamiento 7, horizonte 7, desvianza 1,220513; `configuracion_de_la_regla` = GLM Poisson (a) [expansiva]; `sensibilidad` = la expansiva, «no compite y no puede reemplazar a la configuración final»; `contraste` = XGBoost (a) d=2 n=100 lr=0.1 [deslizante 364 d], «no compite»; EPS 1e-06, semilla 20260910, versiones, `bloque_final_leido: false`. En ningún archivo la de 364 d aparece como elección de la regla: las menciones de «la regla eligió» en el resumen y el HANDOFF hablan siempre de la expansiva, y §5 prohíbe la frase contraria. |
| F3-B2 | El JSON está commiteado antes del análisis (1560a5b) y no cambió después; la rama no contiene `evaluacion_final.ipynb` | CUMPLE | `git log --oneline -- …/solucion_seleccionada.json`: una sola línea, `1560a5b`. `git diff 1560a5b HEAD -- …json`: vacío. Las tablas 33 a 48 entran recién en `508c46e`. `evaluacion_final.ipynb` no está en `git ls-tree -r HEAD` ni en `notebooks/`. En la reejecución, la sección 10 imprimió «verificado, sin reescribir: …solucion_seleccionada.json | commit fijado: 5f207e2», y el archivo no aparece en `git status`. |
| F3-B3 | La importancia por permutación y la exclusión de municipios se reproducen exactas al reejecutar | CUMPLE | Después de la reejecución, `tablas/35_fase3b_permutacion_repeticiones.csv`, `36_fase3b_importancia_permutacion.csv` y `48_fase3c_exclusion_municipio.csv` no aparecen en `git status` ni en `git diff --stat`, así que son idénticas byte a byte a HEAD. Las salidas de texto de esas celdas (y de todas las demás) son idénticas a las de HEAD. |
| F3-N1 | El análisis de errores cubre municipio, tipo de día, peores semanas y calibración | CUMPLE | `tablas/38` (municipio), `39` (8 niveles de calendario), `40` y `41` (5 semanas y sus días), `42` (deciles), `43` y `44` (residuos por corte y tendencia con EE HAC); §3g.2 a §3g.5. |
| F3-N2 | La exclusión de municipios está declarada como descriptiva | CUMPLE | Celda «Precisiones de la fase 3» (D43, «no afectan la selección»), encabezado de la sección 12 y comentario de la celda («Descriptivo; no cambia la selección»), 12.1, §3g.1 y §3g.8 («**Descriptivo; no cambia la selección.**») y la frase prohibida sobre generalización (§5). |
| F3-N3 | La cobertura de los intervalos está reportada, global y por municipio, para NB2 (D44) y Poisson | CUMPLE | `tablas/46`: 36 filas = 2 tipos (NB2 con μ de la solución y α de NB2; Poisson con la misma μ) × 2 niveles (80 % y 95 %) × (global + 8 municipios), con cobertura empírica y esperada, debajo, encima y ancho. §3g.6 da las cuatro globales y los rangos por municipio de los dos tipos en los dos niveles. |
| F3-N4 | La lista de frases que no deben aparecer está actualizada con lo nuevo de la fase | CUMPLE | §5 agrega las frases de fase 2 (conjuntos, NB2, XGBoost, plan B, ventana) y de fase 3: final ≠ regla, «la eligió la regla», «la regla se cumplió», significación de 364 d, la expansiva no puede reemplazar, XGBoost no compite, solución contra L1 y pareado, causalidad por importancia, viernes, semana del 2 de enero, intervalos «bien calibrados», «no hay deriva», generalización a municipios no vistos, feriado −35 %. |

---

## Resultado de la reejecución (Paso 2.1 a 2.3)

| Paso | Comando | Resultado |
| --- | --- | --- |
| 2.1 | `python -m pytest -q` | `15 passed in 3.94s`, 0 saltados |
| 2.2 | `jupyter nbconvert --to notebook --execute --inplace … notebooks/modelos_candidatos.ipynb` | exit 0 (16 min 47 s); 0 errores; 0 salidas `stderr` |
| 2.3 | `git status --short`, `git diff --stat` | Cambian solo `experiments/modelos_candidatos/registro_experimentos.csv` (76 líneas) y el notebook. **Ningún CSV de `tablas/`, ninguna figura y `solucion_seleccionada.json` cambiaron.** |
| 2.3 | Comparación con pandas del registro contra HEAD | 38 × 21 en los dos; la única columna distinta es `fecha_hora` |
| 2.3 | Comparación de las salidas de texto del notebook, celda por celda, contra HEAD | 0 celdas distintas. El diff del `.ipynb` es solo de metadatos de ejecución (marcas de tiempo), la división de un stream de salida y las imágenes codificadas |
| 2.3 | `git restore notebooks/ experiments/` y `git status --short` | Solo queda `?? documentacion/reviews/E3_fase_2-3.md` |

**Ninguna cifra cambió.**

---

## Recálculo de la regla (Paso 2.4)

Script propio fuera del repositorio (`recalculo_regla.py`, en el scratchpad de la sesión). No importa nada del proyecto e implementa la
desvianza de Poisson a mano (2·[y·log(y/μ) − (y − μ)], μ recortada en 1e-6). Lee solo las **predicciones** guardadas en HEAD
(`tablas/17`, `25` y `31`), no las tablas de resultados. Aplica la sección 1 con D32 (A), D36 a D38 (B) y D38 y D40 (C). Como control,
verifica que el promedio de las 47 desvianzas por corte coincide con la desvianza global (< 1e-9) en las 37 configuraciones.

| Paso | Recálculo del revisor | Tabla del notebook | ¿Coincide? |
| --- | --- | --- | --- |
| A, GLM | N de (0) = 91, de (c) = 28; mejor (c) N=28 1,214976, umbral 1,251319; empatados (a), (b), (c) N=28; más simple **(a)**; D32: −0,045449 > EE(0) 0,038932 → no reemplaza | `tablas/14`: «conjunto elegido para la familia» = GLM Poisson (a) | sí |
| A, XGBoost | N de (0) = 28, de (c) = 28; mejor (b) 1,219965, umbral 1,256171; empatados (a), (b), (c) N=28; más simple **(a)**; D32: −0,064783 > 0,039482 → no | `tablas/14`: XGBoost (a) | sí |
| B, GLM | mejor NB2 (a) 1,230105 (EE 0,035935), umbral 1,266041; 2 de 2 empatan; D36 → **GLM Poisson (a)** | `tablas/23`: GLM Poisson (a) | sí |
| B, XGBoost | mejor d=4 n=300 lr=0.05 1,219692 (EE 0,035806), umbral 1,255498; 11 de 12 empatan (fuera d=2 n=100 lr=0.05); D37 → **d=2 n=100 lr=0.1** (única) | `tablas/23`: XGBoost (a) d=2 n=100 lr=0.1 | sí |
| C | mejor GLM 364 d 1,220513 (EE 0,036394), umbral 1,256907; 8 de 8 empatan; D40 → 4 GLM; 4a: mejor peor municipio la expansiva (E 1,401944 + EE 0,091946 = 1,493890), pasan 4 de 4; 4b: expansiva 0,246353, 728 d 0,246801, 546 d 0,247608, 364 d 0,249505 (margen 0,000448) → **GLM Poisson (a) [expansiva]** | `tablas/29`: GLM Poisson (a) [expansiva] | sí |

Cifras de D42 recalculadas con el mismo script: desvianza 1,220513 contra 1,230204; la de 364 d gana en **30 de 47** cortes; total
pred./obs. 0,971655 contra 0,934095; en A, 0,932967 contra 0,869534; la mejor XGBoost del paso C es la de 364 d. Coinciden con el
bloque D42, `tablas/32` y el JSON.

---

## Verificación de fuga independiente (Paso 2.5)

Script propio fuera del repositorio (`verificacion_fuga.py`). Lee el panel con `cargar_panel_desarrollo()` y arma las variables con
`src/variables.py`, pero la matriz de diseño y los ajustes son del revisor; no ejecuta celdas del notebook. Solución (GLM Poisson (a),
364 d) y contraste (XGBoost (a) d=2 n=100 lr=0.1, 364 d), cortes 1 (2024-03-14) y 47 (2025-01-30). Tres versiones: (i) panel real con
la máscara del motor; (ii) `n_siniestros` = 10⁶ en todas las fechas ≥ origen, con la máscara; (iii) el mismo panel alterado
**pasado sin máscara** a `matriz_entrenamiento` y `variables_horizonte`, es decir, probando la compuerta de `src/`.

| Modelo | Corte | Filas alteradas | máx \|i − ii\| | máx \|i − iii\| | máx \|i − `tablas/31`\| |
| --- | --- | --- | --- | --- | --- |
| GLM Poisson (a) [deslizante 364 d] | 1 | 2.632 | 0.0 | 0.0 | 4,94e-07 |
| GLM Poisson (a) [deslizante 364 d] | 47 | 56 | 0.0 | 0.0 | 4,95e-07 |
| XGBoost (a) d=2 n=100 lr=0.1 [deslizante 364 d] | 1 | 2.632 | 0.0 | 0.0 | 4,97e-07 |
| XGBoost (a) d=2 n=100 lr=0.1 [deslizante 364 d] | 47 | 56 | 0.0 | 0.0 | 4,91e-07 |

**La diferencia máxima es exactamente 0** en los cuatro casos. Las predicciones coinciden con las guardadas, salvo el redondeo a 6
decimales. **Control positivo:** si el entrenamiento incluye a propósito los 7 días del horizonte alterado (GLM, corte 1), la
diferencia máxima es 2,326e+04: la prueba detecta una fuga. `git status` no cambió por correr los scripts.

---

## Cronología (Paso 2.6)

| Comprobación | Resultado |
| --- | --- |
| 2936c72 antes de dec597d | 20:24:00 < 21:02:45; padre directo |
| 624b7e3 antes de 80bedb7 | 21:23:19 < 21:49:37; padre directo |
| 2cd97dc antes de 5f207e2 | 21:58:38 < 22:38:36; padre directo |
| Commits de precisiones | Solo `notebooks/modelos_candidatos.ipynb` y `documentacion/resumen_modelos_candidatos.md`; cada uno agrega una sola celda markdown (sin código, sin artefactos) |
| `solucion_seleccionada.json` | `git log --oneline -- …json` → solo `1560a5b`; `git diff 1560a5b HEAD` vacío |
| D42 | En `1560a5b`, el mismo commit que el JSON, después de `5f207e2` (resultados del paso C), como declara el bloque |
| D43 a D45 | En `508c46e`, **el mismo commit que los resultados de 3b y 3c** (riesgo R2) |

---

## Observaciones

1. **N2 (no bloqueante): el prompt de la fase 3 no está transcrito textualmente.** La entrada del paso 3a abrevia las reglas de la sesión
   con «[...]» y omite el texto de los pasos 3b y 3c. La entrada de 3b/3c remite a «el prompt de la fase registrado en la entrada
   anterior», que no los contiene. *Corrección:* agregar al final del registro (es append-only) una entrada que transcriba completo el
   prompt de la fase 3, sacado del transcript de la sesión (`.jsonl`) como se hizo en el fix de la ronda 2 de R1, y transcribir también el
   mensaje que autorizó el commit `508c46e`. No reescribir las entradas existentes: la nueva las referencia.
2. **Resumen desactualizado en partes que no tocaron las fases 2 y 3** (sin efecto en el veredicto; se registra porque CLAUDE.md
   considera un documento desactualizado «peor que uno sin documento»):
   - §1.1, tabla de reglas: las filas «Candidatos», «Grilla de XGBoost», «Orden» y «Binomial negativa» dicen todavía «**PENDIENTE: no
     ejecutados**» o «**PENDIENTE**».
   - §1.3: «en esta etapa sólo se usa la expansiva».
   - §4: dos líneas «PENDIENTE» con el mismo contenido (evaluación en el test).
   - §7, ítem 4: lista como pendientes la selección, la explicabilidad y el análisis de errores, que ya están hechos.
   - §5, «Limitaciones»: no tiene ninguna limitación nueva de la fase 3 (decisión D42 tomada después de ver la validación,
     explicabilidad solo en validación, cobertura sin incertidumbre). Hoy esas limitaciones están solo en la tabla de frases.
   - §8, «Fase 3, pasos 3b y 3c»: dice «Ninguna celda anterior cambió, salvo el texto de la sección 13», pero en `508c46e` cambiaron
     también la celda markdown y la de código de la sección 10 (la protección del JSON, que el punto siguiente sí explica).
   *Corrección:* actualizar esas líneas sin tocar las cifras.
3. **Trazabilidad de D35 y D41.** D35 se cita como «análisis pareado posterior», pero no está definida en ningún archivo del repo. D41 no
   aparece en ninguno. *Corrección:* registrar en el HANDOFF (o en el resumen §1.1) el texto de las dos decisiones del plan, o declarar que
   D41 no existe o se descartó.
4. **Una cifra respaldada solo por una salida impresa.** «Su μ difiere de la de la solución en como mucho 0,0076» (§3g.6, 12.1) sale de un
   `print` de la sección 12 (`0.00762`), no de una tabla. *Corrección:* agregar la columna a `tablas/45` o citar la salida de la sección 12
   como fuente.
5. Menores de redacción y código, sin efecto: en 12.1, «Por ser conteos chicos, los intervalos cubren más que el nominal» está bajo
   Evidencia y es una explicación; en §3f.5, «los municipios se separan en dos grupos» es una lectura. En el notebook hay lambdas asignadas
   a nombres (`f`, `f6`) y nombres globales reutilizados entre secciones (`estab`, `filas`, `g`, `d`). El encabezado del notebook conserva
   «"Estado y artefactos" pasó a ser la sección 10» (de la fase 2) junto al de la fase 3 (sección 13).

---

## Riesgos fuera de criterios

- **R1. D42 es una elección posterior a ver los resultados, con los mismos 47 cortes.** Está declarada como pide F3-B1. En los hechos,
  reordena el paso 4 de D38: pone la calibración y la desvianza media por delante de la estabilidad, después de ver qué ganaba. Ninguna de
  las diferencias supera 1 EE. El desempeño en validación de la de 364 d es optimista por dos vías: la búsqueda (sesgo declarado en la
  sección 1) y el apartamiento de la regla. Si el tribunal pregunta por qué no se cambió la regla antes del paso C, la respuesta tiene que
  estar en el informe. La salvaguarda que existe, que la expansiva no pueda reemplazar a la final en la fase 4, es correcta y hay que
  respetarla.
- **R2. D43 a D45 no son verificables por git como previas al cálculo.** El bloque dice «antes de calcular 3b y 3c», pero está en el mismo
  commit que los resultados (`508c46e`). Solo lo respalda el registro de IA (la IA preguntó y el equipo respondió antes de que se escribiera
  el código). Como son elecciones de análisis que no afectan la selección, el impacto es bajo; en la fase 4, conviene commitear cualquier
  precisión antes de su ejecución, como en la fase 2.
- **R3. `commit_del_repositorio` del JSON apunta a `5f207e2`, con el árbol sucio.** Está declarado (§8), pero el JSON no identifica por sí
  solo el commit que lo fija (`1560a5b`). La fase 4 debería leerlo verificando `git log` de ese archivo, no confiando en ese campo.
- **R4. El análisis pareado (D35) muestra «sensibilidad − L1: −0,0017, EE 0,0005, media/EE −3,47».** Es el número más fácil de citar mal
  como significación. §5 lo cubre, pero conviene que el informe lo presente siempre junto con la advertencia de que es posterior y de que
  los cortes son dependientes.
- **R5. Las coberturas de los intervalos se reportan sin incertidumbre.** Con 2.632 observaciones dependientes (por día y por corte), la
  diferencia entre 0,8883 y 0,8959 puede no ser distinguible. No hay que interpretarla como subcobertura demostrada.
- **R6. La celda de la sección 10 cambió después de `1560a5b`.** Al reejecutar el notebook de `1560a5b`, el JSON se reescribiría con otro
  `commit_del_repositorio`. HEAD lo protege con un `assert`. Es un detalle de reproducibilidad de versiones viejas, no de la actual.

---

## Scripts del revisor

Están fuera del repositorio, en el scratchpad de la sesión (`…/scratchpad/rev/`), y no dejaron artefactos en el repo:
`recalculo_regla.py` (Paso 2.4), `verificacion_fuga.py` (Paso 2.5), `verificacion_matriz.py` (F2-B4) y `buscar_cifras.py` (B4), con
sus salidas `.out`. Leen copias de las tablas de HEAD extraídas con `git show`, no el árbol de trabajo mientras se reejecutaba el
notebook.
