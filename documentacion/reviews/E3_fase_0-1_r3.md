# Review — Entregable 3, fases 0 y 1, ronda 3 (verificación corta del fix de la ronda 2)

| Campo | Valor |
| --- | --- |
| Fecha | 2026-10-19 |
| Revisor | Claude Code, modelo **Opus 5.5** (`claude-opus-5-5`), según D25. No participó en el fix. Archivos creados o modificados: este informe y la entrada de la sesión en `registro_uso_IA.md`. |
| Alcance | Solo las observaciones de `documentacion/reviews/E3_fase_0-1_r2.md` (obs. nuevas 1 a 3), D29, D30 y pytest. No se repitieron los criterios de la ronda 2. |
| Rama | `e3/fase-0-1-protocolo`, al día con `origin` (`git pull`: «Already up to date») |
| Commit revisado | `ce6a18ae3a435fcda2cbc2844d22967c57f6d1da` («Completa el registro de R1 y fija el criterio de convergencia de NB2 (D29, D30)»), padre `e484dcb`, 2026-10-19 19:18:36 −0300 |
| Base de comparación | `e484dcb` |

---

## Veredicto

**APROBADA.** Las tres observaciones de la ronda 2 están corregidas, D29 y D30 constan como se pidió, y pytest pasa entero
(15 pasados, 0 saltados). El fix no tocó código ni artefactos.

---

## Paso 1 — Alcance del cambio

`git log --oneline e484dcb..HEAD`:

```text
ce6a18a Completa el registro de R1 y fija el criterio de convergencia de NB2 (D29, D30)
```

`git diff e484dcb..HEAD --stat`:

```text
 HANDOFF.md                                  |  27 +++
 documentacion/registro_uso_IA.md            | 282 +++++++++++++++++++++++++++-
 documentacion/resumen_modelos_candidatos.md |  19 +-
 documentacion/reviews/E3_fase_0-1_r2.md     | 145 ++++++++++++++
 notebooks/modelos_candidatos.ipynb          |   7 +-
 5 files changed, 474 insertions(+), 6 deletions(-)
```

Son exactamente los cinco archivos permitidos. `git diff e484dcb..HEAD --stat -- src tests experiments` sale vacío. En el
notebook, la comparación de fuentes por `id` entre `e484dcb` y `HEAD` da la misma lista de celdas, en el mismo orden, y **una sola
celda cambiada: `a7d19f27`** (la adenda). `E3_fase_0-1_r2.md` entra como archivo nuevo (145 líneas, 0 borradas).

---

## Paso 2 — Verificación

| Punto | Resultado | Evidencia |
| --- | --- | --- |
| **Obs. 1 (N2): sin `PENDIENTE` y prompts textuales** | CUMPLE | `grep -n PENDIENTE registro_uso_IA.md` da 7 coincidencias, y **ninguna es un marcador abierto**: la línea 1678 es texto histórico sobre el notebook del E2, la 2804 está dentro de un prompt transcripto de otra sesión, y las 3132, 3143, 3221, 3276 y 3297 citan o narran el marcador ya resuelto. El `<!-- PENDIENTE: … -->` de la entrada de R1 ronda 1 se reemplazó por el prompt (diff: −3 líneas del marcador, +101 del prompt y una nota de procedencia). **Textualidad:** se extrajo por programa el primer mensaje de las transcripciones locales `88463c61-b062-42b9-ad62-da91e958eac5.jsonl` (R1 ronda 1) y `07b59f2d-b7fe-4f5e-8794-396a1ae662d9.jsonl` (R1 ronda 2) y se comparó línea a línea con el bloque citado del registro (quitando el prefijo `> ` y los espacios finales). La única diferencia, en los dos, son las etiquetas de apertura y cierre del bloque pegado, que envuelven el texto y no son parte del prompt. Contenido: 6.232 y 3.279 caracteres, idénticos. |
| **Obs. 2: el HANDOFF cierra ese pendiente** | CUMPLE | Entrada nueva «Entregable 3, fases 0 y 1: ronda 2 de R1 y su fix (2026-10-19, sesión de Claude)», viñeta «Prompts de las reviews»: «**Queda cerrado el pendiente del prompt de R1**». |
| **Obs. 3: hashes y verificación del push** | CUMPLE | En la entrada del fix anterior, «ver el resultado de `git log` y `git push` en la sesión» pasó a: «`git log --oneline 34ff44d..HEAD` da `74eafbd` (E3) → `cf76a36` (adenda) → `e484dcb` (fix); `git ls-remote origin e3/fase-0-1-protocolo`, ejecutado el 19/10/2026 antes del commit de la ronda 2, devuelve `e484dcb78fa65af135b56c7430eb369c846fbbdc refs/heads/e3/fase-0-1-protocolo`». Es lo que pedía la observación. Además, en esta ronda: `git ls-remote origin e3/fase-0-1-protocolo` → `ce6a18ae3a435fcda2cbc2844d22967c57f6d1da`, igual a `HEAD`: el commit del fix de la ronda 2 también está en el remoto. |
| **D29: ítem 6 de la adenda** | CUMPLE | Celda `a7d19f27`: ítem 6 «**Criterio de convergencia de NB2** (D29) — *agregado el 19/10/2026 en el fix de la ronda 2, antes de ejecutar candidatos (D29).*», con `method="newton"`, `maxiter=100` y las tres condiciones de no convergencia: `mle_retvals["converged"]` es `False`, se emite `ConvergenceWarning`, α no finito o no positivo; entonces plan B (D28). **Sin cambios en lo anterior:** la celda de la sección 1 (`5efc0a58`) es idéntica en `74eafbd`, `e484dcb` y `HEAD`; el texto de `a7d19f27` en `e484dcb` es **prefijo exacto** del de `HEAD` (`new.startswith(old)` = True), así que la apertura y los ítems 1 a 5 no cambiaron. En el diff JSON, la última línea del ítem 5 aparece modificada solo porque se le agregó `\n` para encadenar el ítem 6. **Resumen §1.1:** fila 6 (D29) con las mismas reglas y la misma marca, más la nota «La fila 6 es posterior a las cinco primeras […] las filas 1 a 5 no cambiaron»; el encabezado de la adenda suma «la sexta se agregó después, D29». §8 registra el cambio de alcance. |
| **D30: validación del equipo** | CUMPLE | **HANDOFF**, viñeta «D30 — validación del equipo»: Lucas revisó los veredictos de las dos rondas y confirmó el 19/10 D17, D18, D23 y D26 a D30, «Es una declaración del equipo; no hay otro artefacto que la respalde». **Registro**, entrada del fix de la ronda 2: «La validación del equipo (D30) la declaró el equipo en el prompt […]; la IA la asentó, no la comprobó». Las dos fuentes coinciden y separan declaración de verificación. |
| **pytest** | CUMPLE | `.venv\Scripts\python.exe -m pytest -rA -q`: `15 passed in 2.98s`, sin saltados. |

---

## Notas menores (no afectan el veredicto)

1. **Edición de entradas anteriores del registro.** Se borraron 4 líneas: el marcador `PENDIENTE` (3) y la frase «ver el resultado
   de `git log` …» (1). Las dos sustituciones las pidió la ronda 2. Completan contenido faltante, no reescriben lo que pasó, y cada una
   lleva una nota fechada. Es compatible con la regla append-only en su intención. Si el tribunal pregunta, las notas lo explican.
2. **La entrada del fix de la ronda 2 no trae el hash de su propio commit.** Se escribió antes de commitear. Lo verificado en esta
   ronda lo cubre: `ce6a18a`, en el remoto. Queda asentado en la entrada de esta sesión.
3. **La apertura de la adenda sigue diciendo «cinco precisiones».** Está declarado en el resumen §8 y en el registro como decisión
   deliberada, para no editar texto commiteado. El ítem 6 lo aclara.

## Riesgos que siguen abiertos (sin cambios en esta ronda)

R1 (commitear las reglas antes del código en la fase 2), R2, R3, R5 y R6 de la ronda 1, y R4 (L0 de 8 semanas: 0,0341 sobre la media
constante, menos de 1 EE de 0,0447, cifras de la ronda 2). R7 queda respondido como **regla** por D29, pero falta implementarlo en la
fase 2. Allí habrá que comprobar que la bandera de convergencia por corte aparece en la salida.

---

## Comandos ejecutados (resumen)

```text
git switch e3/fase-0-1-protocolo; git pull                       -> Already up to date
git log --oneline e484dcb..HEAD                                  -> ce6a18a
git diff e484dcb..HEAD --stat / --numstat                        -> 5 archivos permitidos
git diff e484dcb..HEAD --stat -- src tests experiments           -> vacío
git diff e484dcb..HEAD -- registro, HANDOFF, resumen, notebook   -> revisado
grep -n PENDIENTE documentacion/registro_uso_IA.md               -> 7 coincidencias, ninguna abierta
comparación de prompts contra transcripciones .jsonl (programa)  -> idénticos salvo las etiquetas del pegado
comparación de celdas por id (74eafbd / e484dcb / HEAD)          -> solo cambia a7d19f27; 5efc0a58 idéntica; prefijo intacto
python -m pytest -rA -q                                          -> 15 passed
git ls-remote origin e3/fase-0-1-protocolo                       -> ce6a18a… = HEAD
```

No se reejecutó el notebook: el único cambio es una celda de texto. El script de comparación se escribió en el scratchpad de la
sesión, fuera del repo. Esta revisión no hizo commit ni push.
