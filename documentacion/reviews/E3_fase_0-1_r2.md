# Review — Entregable 3, fases 0 y 1, ronda 2 (verificación del fix de R1)

| Campo | Valor |
| --- | --- |
| Fecha | 2026-10-19 |
| Revisor | Claude Code, modelo **Opus 5.5** (`claude-opus-5-5`), según D25. No participó en las fases revisadas ni en el fix. Solo verificó: el único archivo creado es este informe. |
| Rama | `e3/fase-0-1-protocolo`, al día con `origin` (`git pull`: «Already up to date») |
| Commit revisado | `e484dcb78fa65af135b56c7430eb369c846fbbdc` («Corrige las observaciones de la review R1 (N5, N6 y precisiones menores)») |
| Base de comparación | `34ff44d` |
| Historial `34ff44d..HEAD` | `74eafbd` (E3) → `cf76a36` (adenda, padre `74eafbd`, 2026-10-19 13:58:14) → `e484dcb` (fix, padre `cf76a36`, 2026-10-19 14:08:16). Orden correcto. |
| sha256 del panel | `82467fc87b5d2bceb24ec6f3c5072e1b7cf9e75507b1d5c5a4d20153114a1b06`: coincide con el esperado. Solo se calculó el hash, sin abrir el archivo. |
| Entorno | `.venv` activado, `C:\Proyectos\proyecto-machine-learning\.venv\Scripts\python.exe`, Python 3.13.2 |

---

## Veredicto

**APROBADA CON OBSERVACIONES.** Los 14 criterios bloqueantes cumplen, incluido **F1-B2**, que había fallado en la ronda 1:
la sección 1 sigue idéntica a la de `74eafbd` y la adenda de `cf76a36` fija todo lo que pedía el criterio. Falla un
criterio no bloqueante, **N2**: la entrada de la review R1 en el registro de IA conserva un marcador
`<!-- PENDIENTE -->` en lugar del prompt textual (observación nueva 1). Ninguna cifra cambió al reejecutar.

---

## Criterios

| ID | Criterio | Resultado | Evidencia |
| --- | --- | --- | --- |
| B1 | Fuera de `evaluacion_final.ipynb`, ningún código lee filas posteriores a 2025-02-05 | CUMPLE | La única lectura del panel en `src/` y `tests/` sigue siendo `src/datos.py:41` (`read_csv` por tramos dentro de `cargar_panel_desarrollo()`). El fix solo cambió el docstring de esa función, no su código. El notebook carga el panel solo con `datos.cargar_panel_desarrollo()` (celda `75ecb19f`) y verifica «ninguna fila posterior a 2025-02-05» = True. `evaluacion_final.ipynb` no existe. |
| B2 | Los notebooks de la fase ejecutan de punta a punta sin errores | CUMPLE | `jupyter nbconvert --to notebook --execute --inplace notebooks/modelos_candidatos.ipynb`: exit 0, 41 s, **0 salidas `error`** y 0 salidas `stderr`. La sección 0 dice «Entorno OK — Python 3.13.2, 18 dependencias directas verificadas contra requirements.txt (ninguna diferencia)». |
| B3 | pytest pasa entero (15 pasados, 0 saltados) | CUMPLE | `pytest -rA`: `15 passed in 3.54s`, sin saltados. |
| B4 | Toda cifra del resumen, del HANDOFF y del informe coincide con un artefacto | CUMPLE | Las cifras de R1 no cambiaron (artefactos idénticos byte a byte, ver la reejecución). Las cifras nuevas de la adenda, del resumen §1.1 y §5 y del HANDOFF se contrastaron con las tablas: L0 de 8 semanas 1,362644 → 1,3626; L0 de 4 semanas 1,521011 → 1,5210; L0 de 2 semanas 2,438438 → 2,4384; media constante 1,396707 → 1,3967 (`tablas/05`); EE de la media constante 0,044654 → 0,0447 (`tablas/08`); diferencia 1,396707 − 1,362644 = 0,034063 → 0,0341, menor que 1 EE. La afirmación de statsmodels 0.14.6 se comprobó en el paquete instalado: `discrete_model.NegativeBinomial.__init__(…, loglike_method='nb2', …)` y `genmod.families.NegativeBinomial.__init__(link=None, alpha=1.0, …)`. El informe (`documentacion/informe/`) no se tocó. |
| B5 | Las reglas fijadas no se modificaron después de ejecutar | CUMPLE | Se compararon las fuentes de las celdas por `id` entre `74eafbd`, `cf76a36` y `e484dcb`: la celda de la sección 1 (`5efc0a58`) es **idéntica** en las tres. La adenda es una celda nueva (`a7d19f27`), ubicada justo debajo, y no cambió entre `cf76a36` y `e484dcb`. El fix cambió solo tres celdas de código o texto: imports (`56ef6326`, filtro del aviso), la sección 2 (`3e0e19b5`, redacción de la carga) y el motor (`b5f89a9a`, se borró `exp_dias`), más el modelo L1 (`4387c0e0`). |
| B6 | Entorno coherente | CUMPLE | `pip check`: «No broken requirements found». `pip freeze` contra `requirements-lock.txt`: 127 = 127, sin diferencias (comparación sin los fines de línea CRLF). El fix no tocó `requirements.txt` ni el lock (`git diff 74eafbd HEAD` vacío en esos archivos). |
| N1 | El documento acompañante sigue la estructura de CLAUDE.md, con la lista de frases prohibidas | CUMPLE | Se mantiene la estructura de R1. La regla 4 de §0 ahora apunta a la §5, que es la correcta. §5 suma la frase «La L0 de 8 semanas se fijó antes de ver los resultados», con su motivo. La nueva §8 registra los cambios de alcance tras R1, como pide CLAUDE.md. |
| N2 | HANDOFF y registro de IA actualizados con la sesión | **NO CUMPLE** | El HANDOFF tiene la entrada «Entregable 3, fases 0 y 1: review R1 y su fix (2026-10-19)», con el resultado de R1, D23, el fix y la verificación. El registro es append-only (0 líneas borradas desde `74eafbd`) y tiene las dos entradas: review R1 (Opus 5.5) y fix (Sonnet 5.5, Prompts 1 a 3 textuales). Pero el Prompt 1 de la entrada de la review R1 es `<!-- PENDIENTE: transcripción textual del prompt de la sesión de review … -->` (`registro_uso_IA.md:2875`): falta el prompt textual. El propio registro lo admite (Prompt 3 del fix: «el `PENDIENTE` de la entrada de la review R1 sigue abierto»). El HANDOFF no lo menciona entre los pendientes (observación nueva 1). |
| N3 | Las lecturas separan evidencia de inferencia | CUMPLE | La adenda del resumen §1.1 cierra con un bloque «Evidencia / inferencia»: las cifras salen de `tablas/05` y `08`, y la inferencia del equipo es que 8 semanas reduce el ruido de Poisson. La frase sobre la carga del test ahora es exacta: «ninguna fila del test se conserva ni se acumula; cada tramo se lee y se filtra antes de acumularse». |
| N4 | Los resultados negativos quedan registrados | CUMPLE | Siguen los de R1. La adenda agrega dos: que la elección de L0 está informada por la validación, y que L0 de 8 semanas solo supera a la media constante por menos de 1 EE. |
| N5 | Código legible: sin código muerto, `src/` documentado, nombres consistentes | CUMPLE | `exp_dias` ya no está en la celda `b5f89a9a`. La viñeta de `src/variables.py:12` termina en «.» y no queda la línea vacía de antes. No hay código nuevo sin docstring. |
| N6 | El alcance coincide con lo pedido | CUMPLE | `modelo_L1` usa `nivel = var.nivel_municipio(vista, origen, ventana)` (celda `4387c0e0`). La función calcula lo mismo que el `groupby` anterior: `observado` más el recorte `fecha >= origen − ventana`, igual que `ventana_de_entrenamiento`. La reejecución lo confirma: `tablas/05` a `09` quedan idénticas. `modelo_media_constante` es la media **global** de la ventana, como la define la sección 1, así que no corresponde que use `nivel_municipio` (precisión de esta ronda; decisión del equipo asentada en el resumen §8 y en el registro). El factor de calendario sigue en el notebook, como deuda aceptada para la fase 5. El fix no tocó nada que R1 no pidiera: `tests/`, `README.md` y los requirements no cambiaron. |
| F0-B1 | xgboost y pytest con versión exacta; el lock suma solo xgboost, pytest, iniconfig y pluggy | CUMPLE | `git diff 34ff44d HEAD` de requirements y lock: +`xgboost==3.4.1`, +`pytest==9.1.1` en `requirements.txt`; en el lock, +`iniconfig==2.3.1`, +`pluggy==1.6.0`, +`pytest==9.1.1`, +`xgboost==3.4.1` y el comentario de cabecera. Nada más. |
| F0-B2 | Los tests detectan fugas | CUMPLE | Se repitió en una copia de `src/`, `tests/` y `pytest.ini` en el scratchpad, fuera del repo. Sin mutar: 13 pasan y 2 se saltan (no hay panel en la copia). M1, nivel reciente con `fecha <= origen`: **2 fallan**. M2, nivel del municipio con los 7 días del horizonte: **4 fallan**. M3, compuerta `observado()` con `<=`: **4 fallan**. M4, compuerta que devuelve todo el panel: **5 fallan**. Son los mismos resultados que en R1. |
| F0-B3 | Ninguna función de `src/variables.py` lee `n_siniestros` sin pasar por la compuerta | CUMPLE | El fix cambió una sola línea de `src/variables.py`, en el docstring. Las lecturas del objetivo siguen pasando por `observado(panel, origen)` (`:70`, `:83`, `:103`, `:186`). |
| F0-N1 | La lluvia no aparece en `src/variables.py` y el motivo está escrito | CUMPLE | Sin cambios respecto de R1. La lluvia solo aparece en el docstring del módulo (`:14-17`), con su motivo. |
| F0-N2 | `pytest.ini` silencia solo el aviso de numpy 2.5 con pandas 2.3.3, con comentario | CUMPLE | Un solo filtro, el mismo de R1. El comentario se corrigió: «Lo disparan las llamadas a pd.Timedelta (también las de src/variables.py) por la combinación de pandas 2.3.3 con numpy 2.5.2 (pines vigentes); no indica un error del proyecto». |
| F0-N3 | README actualizado con pytest y xgboost | CUMPLE | Sin cambios desde `74eafbd`. Lo verificado en R1 sigue vigente. |
| F0-N4 | La lectura accidental del test está asentada en HANDOFF y en el registro (D22) | CUMPLE | Sin cambios. Las dos entradas siguen en su lugar: el HANDOFF no perdió el bloque «Incidente» y el registro no borró líneas. |
| F1-B1 | El motor reproduce 1,5178 y 1,3782 en el Municipio C (tolerancia 0,001) | CUMPLE | `tablas/04` regenerada e idéntica: 1,517768 (dif. −0,000032) y 1,378246 (dif. +0,000046). Se reprodujo de nuevo en memoria, ejecutando las celdas del notebook en el scratchpad, con las mismas cifras. |
| F1-B2 | La sección 1 (más la adenda) coincide con las reglas del plan, sin (d) | CUMPLE | **Sección 1:** idéntica a la de `74eafbd` (celda `5efc0a58`, comparación de fuentes). **Adenda** (`a7d19f27`, commit `cf76a36`, que es padre del fix y 10 minutos anterior): (1) **L0 de 8 semanas**, declarando que se eligió «después de fijar la lista y mirando los 47 cortes de validación», como «elección informada por la validación, no una regla previa» (D17); (2) **N ∈ {28, 56, 91}** para el conjunto (0), elegido en el paso A por familia (D18); (3) **XGBoost del paso A**: `max_depth=3`, `n_estimators=300`, `learning_rate=0.05`, resto fijo y semilla fija (D19); (4) **regla por familia**: (a), (b) o (c) por 1 EE con a < b < c, y (0) solo reemplaza si mejora por más de 1 EE (D20); (5) **NB2**, varianza μ + αμ², con **α por máxima verosimilitud** en cada corte (`NegativeBinomial`, `loglike_method="nb2"`) y **plan B por momentos en el mismo corte** (regresión auxiliar de Cameron y Trivedi, μ del GLM Poisson del mismo corte; D27 y D28). Lo que R1 ya había verificado (conjuntos, (d) eliminado, grilla, ventanas, modelos) no cambió. |
| F1-B3 | Ningún nivel ni factor se estima con datos del horizonte | CUMPLE | Se repitió en memoria con el código de `e484dcb`, que ahora incluye `var.nivel_municipio` en L1: 705 comparaciones (media constante, L1 de 8 niveles y L1 de 3 niveles en las ventanas expansiva, 364, 546 y 728; L0 de 2, 4 y 8 semanas en la expansiva; 47 cortes cada una). La vista se pasó **sin enmascarar**, con el objetivo de los días ≥ origen alterado a enteros aleatorios entre 500 y 10⁶. Diferencia máxima: **0,0**; cortes con predicción distinta: **0**. Con el motor completo (corte 21, L1 de 8 niveles, panel alterado a 10⁶ desde el origen), las predicciones son idénticas. |
| F1-B4 | La ventana deslizante tiene exactamente N días en cada corte | CUMPLE | `ventana_de_entrenamiento` en los 47 cortes da {364}, {546} y {728} días; {2.912}, {4.368} y {5.824} filas; bordes [origen − N, origen − 1] en todos. `tablas/03` está regenerada e idéntica. |
| F1-N1 | Métricas globales, por municipio y por corte; predicciones por corte, día y municipio | CUMPLE | `tablas/05`, `06`, `07` y `09` están regeneradas e idénticas a las de R1. |
| F1-N2 | M0 1,4014 y M2 1,2385 marcadas como chequeo de coherencia, no citables | CUMPLE | El resumen §3.2 no cambió y el HANDOFF no las cita. |

---

## Estado de las 8 observaciones de la ronda 1

| N.º | Observación R1 | Estado | Evidencia |
| --- | --- | --- | --- |
| 1 | F1-B2: L0 y NB no coinciden con el plan | **Corregida** | Adenda en `cf76a36`, sin tocar la sección 1. Espejo en el resumen §1.1. Pendientes de L0 y de N cerrados en el HANDOFF, en el resumen §3.1 y en §7. NB2 fijada antes de la fase 2. |
| 2 | N5: código muerto (`exp_dias`, viñeta) | **Corregida** | `exp_dias` se borró de la celda `b5f89a9a` y la viñeta de `src/variables.py:12` termina en «.». |
| 3 | N6: nivel del municipio duplicado; factor de calendario | **Corregida en lo que aplica, más deuda aceptada** | `modelo_L1` usa `var.nivel_municipio`. A `modelo_media_constante` no le aplica, porque es global por definición de la sección 1. Llevar el factor de calendario a `src/` queda **aceptado como deuda** hasta la fase 5 (HANDOFF, resumen §8). |
| 4 | Referencia cruzada §6 → §5 | **Corregida** | `resumen_modelos_candidatos.md:38`: «Respetar la sección 5». |
| 5 | HANDOFF desactualizado sobre el commit | **Corregida, con el mensaje aceptado como deuda** | El HANDOFF registra `74eafbd`, D23 y por qué no se corrige el mensaje «E3»: reescribiría `main`. Queda **aceptado como deuda**. En el registro, `74eafbd` figura en la entrada de R1, pero D23 aparece solo dentro del prompt transcripto (detalle menor, sin efecto). |
| 6 | Afirmación inexacta sobre la carga del test | **Corregida** | Nueva redacción en `src/datos.py` (docstring), en la celda `3e0e19b5` y en el resumen. Ni el HANDOFF ni el README conservan la frase anterior. |
| 7 | Comentario de `pytest.ini` | **Corregida** | El comentario reescrito nombra `src/variables.py` y la combinación de pines. |
| 8 | Notebook inflado por avisos | **Corregida** | El filtro del aviso está en la celda de imports. El notebook commiteado y el reejecutado tienen 0 salidas `stderr` y ninguna ruta local. |

---

## Resultado de la reejecución (Paso 2)

- `pytest -rA`: 15 pasados, 0 saltados.
- `nbconvert --execute --inplace`: exit 0, 41 s, 0 errores, 0 `stderr`. La sección 0 dice Python 3.13.2.
- `git status` después de nbconvert: solo `M notebooks/modelos_candidatos.ipynb`. `git diff --stat experiments/` vacío. Los
  **14 artefactos** de `experiments/modelos_candidatos/` (11 CSV y 3 PNG) tienen un `git hash-object` igual al blob de
  `HEAD`. **Ninguna cifra cambió.**
- El diff del notebook son 88 líneas (44 + 44), todas de metadatos de ejecución. Las fuentes de las celdas son idénticas y
  las 24 salidas textuales también. El fix eliminó las ~1.100 líneas de avisos que había visto R1.
- Se restauró con `git restore notebooks/ experiments/` y `git status` quedó limpio.
- F0-B2 y F1-B3 (más F1-B4 y F1-B1) se repitieron en una copia del código en el scratchpad y en memoria, sin escribir en el repo.
  El panel se leyó solo con `cargar_panel_desarrollo()`. Después de cada paso, `git status` quedó limpio.

---

## Observaciones nuevas

1. **N2: falta el prompt textual de la review R1 en el registro.** `registro_uso_IA.md:2875` tiene
   `<!-- PENDIENTE: transcripción textual del prompt de la sesión de review … -->`. El Prompt 3 del fix pedía reemplazarlo,
   pero llegó con el marcador de plantilla `<pegar acá el prompt del plan>` sin completar. CLAUDE.md exige que los prompts
   se transcriban textualmente. Corrección: pegar el prompt de R1 tal cual en esa entrada. Es un agregado de contenido
   faltante, no la reescritura de una entrada anterior. Agregar también, al final, la entrada de esta ronda 2.
2. **El HANDOFF no lista ese pendiente.** La entrada del 2026-10-19 cierra con «Sigue pendiente de esta fase: el plan B de
   D28 y NB2 …» y no menciona el `PENDIENTE` abierto del registro, aunque el registro dice que «se avisó al equipo».
   Agregarlo para que no se pierda antes del commit de la fase 2.
3. **Verificación del commit y del push poco trazable en el registro (menor).** El Prompt 3 del fix cierra con «ver el
   resultado de `git log` y `git push` en la sesión», que no se puede comprobar desde el repositorio. Conviene anotar
   hashes concretos, como `cf76a36` → `e484dcb` y la rama remota.

---

## Riesgos fuera de criterios (no afectan el veredicto)

- **R1 (sigue y mejora).** La cronología de la adenda ahora tiene respaldo en git: `cf76a36` es anterior al fix y no
  contiene código de candidatos. En el notebook no hay ninguna llamada a GLM, `NegativeBinomial`, XGBoost ni `.fit(`.
  Pero «antes de ejecutar cualquier candidato» se puede verificar solo en lo commiteado, no en lo que se haya ejecutado
  fuera del repo. Para la fase 2: commitear las reglas y después el código, como se hizo acá.
- **R2, R3, R5 y R6 siguen abiertos, sin cambios.** El HANDOFF los enumera como abiertos: dashboard sin versiones fijadas,
  doble redondeo 1,5156 / 1,5155 (`resumen_modelos_candidatos.md:204`), `matriz_entrenamiento` sin uso con datos reales y
  pytest con 2 saltados si falta el panel.
- **R4 (se agrava levemente, y está declarado).** La L0 que pasa a la comparación se eligió con los mismos 47 cortes que
  decidirán entre candidatos. La adenda y la frase prohibida nueva lo dejan explícito. La ventaja de L0 de 8 semanas
  sobre la media constante es de 0,0341, menos de 1 EE (0,0447): ante el tribunal no debería presentarse como una mejora.
- **R7 (nuevo). NB2 y su plan B son reglas, no código.** La firma de statsmodels es la correcta, pero en la fase 2 habrá
  que verificar cómo se reporta la no convergencia por corte. `NegativeBinomial` de `discrete_model` puede terminar con
  advertencias de convergencia que no son excepciones. Conviene fijar el criterio, por ejemplo `mle_retvals["converged"]`,
  antes de ejecutar.
- **R8 (nuevo). Revisión con un modelo de la misma familia.** El fix se hizo con Sonnet 5.5 y las dos rondas de review
  con Opus 5.5. Se cumple D25 (son modelos distintos), pero las dos son de Anthropic. Si el tribunal pregunta por la
  independencia de la revisión, conviene que la validación del equipo conste aparte.

---

## Comandos ejecutados (resumen)

```text
git switch e3/fase-0-1-protocolo; git pull                                             -> Already up to date
git log --oneline 34ff44d..HEAD                                                        -> e484dcb, cf76a36, 74eafbd
python -c "import sys; print(sys.executable, sys.version)"                            -> .venv, 3.13.2
Get-FileHash -Algorithm SHA256 data/processed/panel_diario_montevideo.csv              -> 82467fc8…4a1b06
git diff 34ff44d...HEAD --stat; git diff 74eafbd HEAD -- notebooks/modelos_candidatos.ipynb
comparación de fuentes de celdas por id (74eafbd / cf76a36 / e484dcb)                  -> sección 1 idéntica
pytest -rA                                                                             -> 15 passed
jupyter nbconvert --to notebook --execute --inplace notebooks/modelos_candidatos.ipynb -> exit 0, 0 errores, 0 stderr
git hash-object (14 artefactos) vs HEAD; git diff --stat experiments/                  -> 14 IGUAL, sin diff
git restore notebooks/ experiments/; git status                                        -> limpio
Mutaciones M1–M4 en copia fuera del repo                                               -> 2 / 4 / 4 / 5 fallan
F1-B3 en memoria (705 comparaciones + motor completo corte 21)                         -> dif. máx. 0,0
F1-B4 en memoria (364/546/728, 47 cortes)                                              -> exactos
pip check; pip freeze vs requirements-lock.txt                                         -> OK; 127 = 127
inspect.signature de statsmodels NegativeBinomial (discrete y GLM)                     -> nb2 por omisión; alpha=1.0
```

Las copias temporales del scratchpad se borraron al terminar. Esta revisión no hizo commit ni push.
