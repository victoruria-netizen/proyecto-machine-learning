# Review R2, ronda 2 (review corta) — Entregable 3, fases 2 y 3

| Campo | Valor |
| --- | --- |
| Fecha | 2026-10-20 |
| Revisor | Claude Code, modelo **Opus 5.5** (`claude-opus-5-5`), según D25. No participó en el fix. Archivos creados o modificados: este informe y la entrada de la sesión en `registro_uso_IA.md`. |
| Alcance | Solo las observaciones de la review R2 (`documentacion/reviews/E3_fase_2-3.md`) y que el fix no haya roto nada. No se evalúa si D42 o D46 son correctas. |
| Rama | `e3/fase-3-seleccion` («Your branch is up to date with 'origin/e3/fase-3-seleccion'») |
| Base | `508c46e54fc7e748bd89f4fb33617297bbdf8d5d` (el HEAD que revisó R2), ancestro de HEAD (`git merge-base --is-ancestor 508c46e HEAD`) |
| HEAD revisado | `b0ffd062de3edccfbe39be8a5748ebc5ccdf94f1` |
| sha256 del panel | `82467fc87b5d2bceb24ec6f3c5072e1b7cf9e75507b1d5c5a4d20153114a1b06`: coincide con el esperado. Solo se calculó el hash. |
| Entorno | `.venv` activado en el mismo comando que corre Python, pytest y nbconvert. Python 3.13.2 según `python --version` y según la celda de la sección 0: «Entorno OK — Python 3.13.2, 18 dependencias directas verificadas contra requirements.txt (ninguna diferencia).» |

**Comprobaciones previas.** Una sesión anterior de esta review se cortó y el árbol se restauró a mano. Antes de empezar se verificó:

- `git status --porcelain --untracked-files=all` vacío.
- `git rev-parse HEAD` = `b0ffd062de3edccfbe39be8a5748ebc5ccdf94f1`, en `e3/fase-3-seleccion`.
- `git diff b0ffd06` vacío (0 bytes).
- `documentacion/reviews/E3_fase_2-3_r2.md` no existía.
- La última entrada de `registro_uso_IA.md` era «Sesión 2026-10-20 (fix de R2, E3 fases 2 y 3)», y el último commit que tocó el archivo es `b0ffd06`.

Se cumplieron las cuatro comprobaciones.

**Commits revisados.** `git log --oneline 508c46e..HEAD` muestra solo estos dos:

| Commit | Mensaje | Fecha | Archivos (`git diff --name-status`) |
| --- | --- | --- | --- |
| `2742039d022b7fb07ba5982b708022aa5f4bd298` | Review fase 2-3 | 2026-10-20 11:24 | `A documentacion/reviews/E3_fase_2-3.md`, `M documentacion/registro_uso_IA.md` |
| `b0ffd062de3edccfbe39be8a5748ebc5ccdf94f1` | Fix de la review R2 (D46, D47) | 2026-10-20 12:14 | `M HANDOFF.md`, `M documentacion/registro_uso_IA.md`, `M documentacion/resumen_modelos_candidatos.md`, `M experiments/modelos_candidatos/registro_experimentos.csv`, `M …/tablas/10_artefactos.csv`, `A …/tablas/49_fase3c_dif_mu_nb2_vs_solucion.csv`, `M notebooks/modelos_candidatos.ipynb` |

---

## Veredicto

**APROBADA.** Cumplen los 4 criterios bloqueantes (V1, V2, V3, B1) y los 6 no bloqueantes (O1 a O6).

- El fix tocó solo los archivos permitidos. En el notebook, el único cambio de código escribe `tablas/49`. La sección 1, la adenda y los bloques fechados no cambiaron.
- Las tablas 00 a 48, las figuras y el JSON son idénticos a `508c46e`.
- La reejecución reproduce todo sin cambios: `tablas/49` es el mismo blob de git y las salidas de texto del notebook son idénticas a HEAD.
- Los cuatro mensajes de la fase 3 coinciden con el `.jsonl` carácter por carácter. La comparación es del revisor, hecha por programa.

Hay tres observaciones menores de redacción en el HANDOFF que no afectan el veredicto, más los riesgos que siguen.

---

## Criterios

### Bloqueantes

| ID | Criterio | Resultado | Evidencia |
| --- | --- | --- | --- |
| V1 | El fix solo tocó los archivos permitidos. En el notebook, el código cambia solo para escribir `tablas/49`, y la sección 1, la adenda y los bloques fechados no cambian | CUMPLE | **Archivos:** `git diff --name-status 508c46e 2742039` da solo el informe de R2 (nuevo) y `registro_uso_IA.md`, así que el informe se commiteó antes del fix. `git diff --name-status 2742039 b0ffd06` da exactamente la lista permitida (tabla de arriba). `tablas/10_artefactos.csv` suma una sola línea, `+tablas/49_fase3c_dif_mu_nb2_vs_solucion.csv`, al final (`@@ -60,3 +60,4 @@`). **Notebook:** se comparó celda por celda entre `508c46e` y `b0ffd06` (`comparar_nb.py`, `detalle.py`). Las dos versiones tienen 65 celdas. La fuente cambia solo en tres celdas: la 0 (encabezado, markdown), la 62 (lectura 12.1, markdown: cita «`38` a `49`» y «(`49`)») y la 59 (código). En la 59, `dif_mu` reemplaza a la expresión inline del `print`, se agregan `idxmax`, un `assert` de que las filas `corte`/`fecha`/`zona_id` de las dos predicciones son iguales y `guardar_tabla(…, "49_…csv")`, y no cambia ningún cálculo. Las celdas 53 y 64 cambian solo en la salida: en la 53, un stream de stdout aparece partido en dos, con el mismo texto; en la 64, el índice pasa de 61 a 62 filas. **Bloques:** sha256 del texto, igual en `508c46e` y en `b0ffd06`: celda 3, «## 1. Reglas fijadas…», `2e29652a5de54939`; celda 4, adenda, `65147a9281dd7d71`; celda 5, precisiones de la fase 2, `da2ac394d84ae134`; celda 6, paso B, `e7c2039bc4994a82`; celda 7, paso C, `aa167be0830e2941`; celda 9, fase 3 (D43 a D45), `1a1673436d7f4dce`. El texto de la celda 8 (D42) también es idéntico |
| V2 | Tablas 00 a 48, figuras y `solucion_seleccionada.json` idénticos a `508c46e`; el JSON con un único commit, `1560a5b` | CUMPLE | `git diff --name-status 508c46e b0ffd06 -- experiments/ models/ src/ tests/ data/ app/ train/ requirements.txt requirements-lock.txt` da solo `M registro_experimentos.csv`, `M tablas/10_artefactos.csv` y `A tablas/49_…`. Ninguna figura y ninguna otra tabla aparecen. Comparación con pandas del registro de `508c46e` contra el de `b0ffd06`: 38 × 21 en los dos, misma lista de columnas, y la única columna distinta es `fecha_hora`. `git log --oneline -- experiments/modelos_candidatos/solucion_seleccionada.json` da una sola línea, `1560a5b Fase 3, paso 3a: configuración de la solución (D42)`, y `git diff --stat 1560a5b b0ffd06 -- …json` está vacío |
| V3 | pytest y nbconvert como en el Paso 2, y la reejecución reproduce `tablas/49` exacta | CUMPLE | `python -m pytest -q` da `15 passed in 3.60s`, 0 saltados. `jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=-1 notebooks/modelos_candidatos.ipynb` termina con exit 0, en 16 min 18 s, con 0 salidas `error` y 0 salidas `stderr` en el notebook resultante. **`tablas/49`:** no aparece en `git status`. `git diff --exit-code` sobre ella está vacío. `git hash-object` del archivo reejecutado y `git rev-parse HEAD:…49_…csv` dan el mismo blob, `2684f9128318b6c3123f14fa9037d5849a1074d0`. Contenido: `0.00762, 2632, 44, 2025-01-09, MUNICIPIO A, 3.613476, 3.605856`. Detalle en «Resultado de la reejecución» |
| B1 | La rama no contiene `evaluacion_final.ipynb`, y ningún código lee filas posteriores a 2025-02-05 | CUMPLE | `git ls-tree -r --name-only HEAD \| grep -i evaluacion_final` no devuelve nada, y `notebooks/` tampoco lo tiene. En el código del notebook de HEAD se buscó `panel_diario_montevideo\|cargar_panel\|read_csv(\|RUTA_PANEL\|2025-02-0[6-9]\|2025-1[0-2]\|evaluacion_final`. Hay tres coincidencias. Celda 13: `panel = datos.cargar_panel_desarrollo()`. Celda 13: el texto `"2025-12-31"` en una tabla descriptiva de los bloques, que no es una lectura. Celda 19: `experiments/linea_base/tablas/04_desarrollo_backtesting.csv`, con datos de desarrollo. En `src/` y `tests/`, la única lectura del panel es `src/datos.py:41`, dentro de `cargar_panel_desarrollo()`, que recorta cada tramo a `fecha <= ULTIMO_DIA_DESARROLLO` y tiene un `assert`. `tests/test_variables.py:164` solo usa la ruta para el `skipif`. El fix no tocó `src/` ni `tests/` (`git diff --stat` vacío), y su único código nuevo (celda 59) usa `PRED_CAND`, es decir, predicciones de validación |

### No bloqueantes

| ID | Criterio | Resultado | Evidencia |
| --- | --- | --- | --- |
| O1 | Entrada nueva en el registro de IA con los mensajes textuales de la fase 3, comparados por programa contra los `.jsonl`, y entradas anteriores sin cambios | CUMPLE | La entrada «Sesión 2026-10-20 (fix de R2, paso F1: transcripción textual de la fase 3)» (`registro_uso_IA.md:3948`) tiene cuatro mensajes. El 1 es el prompt completo de la fase 3: reglas de la sesión y pasos 3a, 3b y 3c. El 2 es el paso 3.0 y la autorización de `1560a5b`, declarados como un mismo mensaje. El 3 es «dale, segui con 3b y 3c». El 4 es la autorización de `508c46e`. **El revisor hizo su propia comparación** (`comparar_jsonl.py`) contra `3da4460b-7a42-4a3c-98f7-75d047b7ec94.jsonl`. Toma el texto citado del registro sin el prefijo `> ` y lo compara con el mensaje del usuario que tiene el timestamp indicado en la entrada, sin las marcas `<pasted_content>`. Resultado: igualdad exacta de cadena en los cuatro (5929, 782, 23 y 59 caracteres). En la ventana de la fase 3 (01:40Z a 03:40Z) hay además los mensajes de las 02:55Z (D43 a D45) y 03:17Z (instrucciones antes del commit), registrados como Prompts 2 y 3 de la entrada 3b/3c, uno sobre el tiempo de reejecución, que la entrada menciona, y notificaciones de tareas. No falta ningún mensaje con instrucciones. **Append-only:** en cada commit (`508c46e→2742039` y `2742039→b0ffd06`), `git diff -U0` muestra solo agregados (`@@ -3807,0 …` y `@@ -3944,0 …`, sin líneas `-`), y las primeras 3807 y 3944 líneas son idénticas byte a byte a las del commit anterior |
| O2 | Resumen: §1.1, §1.3, §4, §7 ítem 4 y §8 corregidos; §5 con las limitaciones (a) a (e); lista de frases ampliada | CUMPLE | En `resumen_modelos_candidatos.md` de HEAD: **§1.1**, las filas Candidatos (l. 67), Grilla (l. 71), Orden (l. 73) y Binomial negativa (l. 75) ya no dicen PENDIENTE y remiten a §3b a §3d. **§1.3** (l. 180) dice qué ventanas usó cada paso y que la final es la de 364 d. **§4** (l. 889) tiene una sola línea, «Fase 4, no hecha…», en lugar de las dos PENDIENTE repetidas, como confirmó el equipo (Prompt 3 del fix). **§7 ítem 4** (l. 1038) tacha la selección, la explicabilidad y los errores. **§8** (l. 1123) declara el cambio de la sección 10 en `508c46e`, y la l. 1136 agrega «Fix de R2». **§5**, l. 911, 914, 916, 919 y 922, tiene las limitaciones Fase 3 (a) a (e). **Frases:** tres filas nuevas, l. 946 (la final «siguió la regla» en cualquier variante), l. 952 (el pareado como significación) y l. 957 (coberturas como exactas). `grep PENDIENTE` encuentra solo la regla de uso (l. 48) y la mención en §8 (l. 1149) |
| O3 | HANDOFF: D35, D41 y D46 registradas; líneas viejas corregidas; validación del equipo asentada (D30) | CUMPLE | En `HANDOFF.md`: D35 (l. 1951), D41 (l. 1955), D46 (l. 1961) y también D47 (l. 1959). La definición de D41 viene de la instrucción del equipo en el prompt del fix (`registro_uso_IA.md:4196`). D35 coincide con el texto del paso 3c del prompt de la fase 3 (Mensaje 1, verificado en O1). **Líneas viejas:** l. 1893, «Commit de la parada C pendiente de confirmación», pasó a «Commit de la parada C: `5f207e2`»; l. 1938, el «Próximo» de la entrada 3b/3c, ahora dice cuándo se escribió y remite a R2. **D30:** l. 1992, «Lucas revisó el veredicto de R2 el 20/10 […] y decidió D46. Es una declaración del equipo; no hay otro artefacto que la respalde.» Ver la observación 1 sobre la redacción de D46 |
| O4 | El 0,0076 está en `tablas/49` y §3g.6 lo cita | CUMPLE | `tablas/49_fase3c_dif_mu_nb2_vs_solucion.csv`: `valor` = 0.00762, que coincide con 3.613476 − 3.605856 = 0.00762. El encabezado de §3g.6 (l. 815) lista `49_…csv`, y la l. 818 dice «como mucho 0,0076 (`tablas/49_…csv`: […] 0,00762, en el corte 44, 2025-01-09, MUNICIPIO A)». La lectura 12.1 del notebook (celda 62) la cita como «(`49`)» |
| O5 | El encabezado del notebook tiene la numeración actual, y la deuda aceptada está escrita con su motivo | CUMPLE | Celda 0 de HEAD: se quitó «"Estado y artefactos" pasó a ser la sección 10». Queda solo «pasó a ser la sección 13», que coincide con el notebook. «quedan para la explicabilidad…» pasó a «contienen la explicabilidad (paso 3b) y el análisis de errores (paso 3c)», y las secciones 11 y 12 existen. **Deuda:** el resumen §5, Fase 3 (e) (l. 922), y el HANDOFF (l. 1982) la escriben con su motivo: «No afectan resultados, y cambiar el código obligaría a revalidar antes de la fase 4». Los ítems coinciden con la observación 5 de R2 (explicaciones bajo «Evidencia», la lectura de los dos grupos, lambdas y globales reutilizados) |
| O6 | Toda cifra nueva del resumen y del HANDOFF coincide con un artefacto | CUMPLE | Cifras nuevas del diff del resumen. 50 tablas y 11 figuras: `git ls-tree` de `b0ffd06` da 50 y 11. 38 filas: registro, 38 × 21. 0,0076, 0,00762, 2.632, corte 44, 2025-01-09 y MUNICIPIO A: `tablas/49`. 1,2205 y 1,2302: registro, paso C (1.220513 y 1.230204). 0,8883 y 0,8959: `tablas/46`, NB2 80 % «todos» (0.888298, 0.895872). −0,0114, 0,0054, −2,09 y 32 de 47: `tablas/47`, solución − L1 (−0.011366, 0.005446, −2.087051, 32). −0,0017, 0,0005 y −3,47: `tablas/47`, sensibilidad − L1 (−0.001676, 0.000483, −3.468313). «4 comparaciones»: `tablas/47` tiene 4 filas. Las cifras nuevas del HANDOFF (14 bloqueantes, 0,00762, corte 44, 15 pasados, 11 figuras, cuatro textos) coinciden con el informe R2, `tablas/49`, pytest y `git ls-tree`. «15,9 min» no está en ninguna tabla, pero es compatible con la metadata de ejecución del notebook de `b0ffd06`: 15,62 min entre la primera y la última celda, de 14:44:14Z a 14:59:51Z, sin contar el arranque del kernel (observación 2) |

---

## Resultado de la reejecución (Paso 2)

| Paso | Comando | Resultado |
| --- | --- | --- |
| 2.1 | `python -m pytest -q` (en el `.venv`) | `15 passed in 3.60s`, 0 saltados |
| 2.2 | `jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=-1 notebooks/modelos_candidatos.ipynb` | exit 0, 16 min 18 s. En el notebook resultante hay 0 salidas `error` y 0 salidas `stderr`. En el log de nbconvert solo aparecen los dos avisos del lanzador del kernel (zmq/Proactor y «Kernel is running over TCP»), que no son salidas de celdas |
| 2.3 | `git status --short` | `M experiments/modelos_candidatos/registro_experimentos.csv`, `M notebooks/modelos_candidatos.ipynb` y el informe sin seguimiento. **Ninguna tabla, figura ni el JSON cambiaron** (`git ls-files -m -o --exclude-standard experiments/` muestra solo el registro) |
| 2.3 | `git diff --stat` | `registro_experimentos.csv` con 76 líneas y el notebook con 304 |
| 2.3 | Registro contra HEAD (pandas) | 38 × 21 en los dos; la única columna distinta es `fecha_hora` |
| 2.3 | Notebook contra HEAD (`post_reejecucion.py`) | 0 celdas con fuente distinta y 0 celdas con salida de texto distinta. El diff del `.ipynb` es de las marcas de tiempo de 37 celdas (`iopub.*`, `shell.execute_reply`) y de un stream de stdout de la celda 53 partido distinto, con el mismo texto. Las imágenes no cambiaron |
| 2.3 | `tablas/49` | Idéntica: mismo blob `2684f912…` (`git hash-object` contra `HEAD:`) |
| 2.3 | `git restore notebooks/ experiments/` y `git status --short` | Solo queda `?? documentacion/reviews/E3_fase_2-3_r2.md` |

**Ninguna cifra cambió.**

---

## Observaciones

Ningún criterio falla. Las tres observaciones son menores, de redacción del HANDOFF, y no afectan el veredicto.

1. **La redacción de D46 en el HANDOFF dice más que la decisión.** `HANDOFF.md:1961` dice «Se corrige solo lo que el equipo listó (observaciones 1 a 5 de R2 y los riesgos declarados…)». La decisión D46, tal como la enuncia el prompt de esta review, es otra: se corrigen las observaciones 1 a 4 y la numeración del encabezado; el resto de la 5 queda como deuda aceptada. El mismo HANDOFF lo precisa más abajo («Obs. 5 (parte)», l. 1976; «Deuda aceptada», l. 1982), así que no hay contradicción de fondo. *Corrección:* reescribir la línea de D46 como «observaciones 1 a 4 y la numeración del encabezado (parte de la 5); el resto de la 5 queda como deuda aceptada; los riesgos se declaran en el resumen».
2. **«15,9 min» sin artefacto exacto.** `HANDOFF.md:1985` da la duración de la reejecución del fix como «15,9 min». La metadata del notebook de `b0ffd06` registra 15,62 min de ejecución de celdas. La diferencia es compatible con el arranque del kernel, pero la cifra exacta no se puede rastrear. Es un dato operativo del HANDOFF y no va al informe. *Corrección:* escribir «unos 16 min (metadata de ejecución del notebook)» o citar la fuente.
3. **D41 y la validación D30 se apoyan solo en declaraciones del equipo.** La definición de D41 sale del prompt del fix (`registro_uso_IA.md:4196`), no de un documento previo. La validación D30 está declarada como tal (`HANDOFF.md:1992`). Así se cumple lo que pidió R2, pero si el tribunal pregunta por D41 la única fuente es ese prompt. Además, el fix dejó abierto agregar «y confirmó D31 a D45» (registro, Prompt 3 del fix), y eso sigue sin asentarse. *Corrección:* si el equipo confirmó D31 a D45, agregarlo a la línea de D30. Si D41 tiene un origen anterior (plan del equipo, chat del Project), citarlo.

---

## Riesgos fuera de criterios (no afectan el veredicto)

- **R1. HANDOFF §4.2 desactualizado.** `HANDOFF.md:2093` («4.2 Pendientes que pasan al Entregable 3») sigue diciendo «Sólo una lista — nada de esto se empezó». Varios ítems ya están resueltos en el E3: el nivel de zona, la partición en el panel, la exclusión de un municipio por vez y los hiperparámetros por validación. Es anterior al fix y R2 no lo señaló, pero contradice el estado de la §3 del mismo archivo. Conviene actualizarlo antes del merge o de la fase 4.
- **R2. Los riesgos R1 a R6 de R2 siguen vigentes.** Ahora están declarados (resumen §5, Fase 3 (a) a (d), y la frase nueva sobre el pareado). En la fase 4 hay que respetar tres cosas. La expansiva no puede reemplazar a la final. El commit del JSON se identifica con `git log` del archivo (`1560a5b`), no con `commit_del_repositorio` (`5f207e2`). Cualquier precisión de la fase 4 se commitea antes de ejecutarla, para que git pruebe el orden, cosa que D43 a D45 no logran.
- **R3. Cambios de markdown después de reejecutar.** En el fix, las celdas 0 y 62 se editaron después de la ejecución, sin reejecutar (lo declara el registro, Prompt 3 del fix). Esta review reejecutó HEAD, y las fuentes y salidas de texto coinciden, así que hoy el notebook es coherente. El patrón, de todos modos, vuelve a abrir la posibilidad de que el texto y las salidas diverjan. En la fase 4 conviene que la última operación antes del commit sea la ejecución.

---

## Scripts del revisor

Están fuera del repositorio, en el scratchpad de la sesión (`…/scratchpad/rev/`), y no dejaron artefactos en el repo. Leen copias de `508c46e`, `2742039` y `b0ffd06` extraídas con `git show`, no el árbol de trabajo:

- `comparar_nb.py` y `detalle.py`: fuente y salidas de cada celda del notebook, y sha256 de los bloques fechados.
- `comparar_jsonl.py`: O1, mensajes del registro contra el `.jsonl` de la fase 3.
- `post_reejecucion.py`: Paso 2, salidas `error`/`stderr`, celdas, `tablas/49` y registro contra HEAD.
