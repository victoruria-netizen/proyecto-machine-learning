# Review — Entregable 3, fases 0 y 1 (dependencias, `src/`, protocolo y referencias)

| Campo | Valor |
| --- | --- |
| Fecha | 2026-10-19 |
| Revisor | Claude Code, modelo **Opus 5.5** (`claude-opus-5-5`), según D25. No participó en las fases revisadas. |
| Rama de revisión | `e3/fase-0-1-protocolo` (creada desde `main`, sin cambios propios salvo este archivo) |
| Commit revisado | `74eafbdf4a86c2adf1d6b66965f7f3784f0c3d05` («E3») |
| Base de comparación | `34ff44d` (commit padre; el trabajo se commiteó directo en `main`, D23) |
| sha256 del panel | `82467fc87b5d2bceb24ec6f3c5072e1b7cf9e75507b1d5c5a4d20153114a1b06`: coincide con `experiments/diagnostico_municipios/tablas/00_procedencia.csv`. Solo se calculó el hash, sin abrir el archivo. |
| Entorno | `.venv` activado, `C:\Proyectos\proyecto-machine-learning\.venv\Scripts\python.exe`, Python 3.13.2 |

Nota de procedimiento: en el primer intento el panel no estaba en `data/processed/` y la revisión se detuvo en el
Paso 0.3. Se retomó cuando el equipo lo repuso, y el hash coincidió.

---

## Veredicto

**DESAPROBADA.** Falla un criterio bloqueante, **F1-B2**: la sección 1 del notebook no coincide con la lista cerrada
que fija el criterio en dos puntos, «L0 de 8 semanas» y «NB2». Además fallan dos criterios no bloqueantes, N5 y N6.
Los otros 13 criterios bloqueantes cumplen.

El fallo de F1-B2 depende de cómo se resuelva la observación 1. El notebook sigue al pie de la letra el prompt
registrado en `registro_uso_IA.md` (Prompt 1), y la elección de la L0 figura como **pendiente** en HANDOFF y en el
resumen. Hay dos lecturas posibles:

- Si el plan fijó «L0 de 8 semanas» **después** de ver la Etapa 1, la discrepancia está en el plan, no en el código.
- Si lo fijó **antes**, la implementación se apartó del plan.

En ninguno de los dos casos la corrección consiste en editar la sección 1 (ver la observación 1).

---

## Criterios

| ID | Criterio | Resultado | Evidencia |
| --- | --- | --- | --- |
| B1 | Fuera de `evaluacion_final.ipynb`, ningún código lee filas posteriores a 2025-02-05 | CUMPLE | En `src/`, `tests/` y `notebooks/modelos_candidatos.ipynb` hay una sola lectura del panel: `src/datos.py:41`, dentro de `cargar_panel_desarrollo()`, que recorta cada tramo a `fecha <= 2025-02-05` (`src/datos.py:43`) y verifica con `assert` (`:47-52`). El notebook lo lee solo en la celda 7 (`panel = datos.cargar_panel_desarrollo()`) y comprueba «ninguna fila posterior a 2025-02-05» = True (`tablas/01`). La otra lectura del notebook es `experiments/linea_base/tablas/04_desarrollo_backtesting.csv`, que es de desarrollo. `tablas/09` termina en 2025-02-05. Los tests con panel real también pasan por `cargar_panel_desarrollo()`. `evaluacion_final.ipynb` todavía no existe. Las lecturas de `preparacion_montevideo` (ETL) y `diagnostico_municipios` son de fases anteriores y no están en el diff. |
| B2 | Los notebooks de la fase ejecutan de punta a punta sin errores | CUMPLE | `jupyter nbconvert --to notebook --execute --inplace notebooks/modelos_candidatos.ipynb` en el `.venv`: exit 0, 43 s, 0 salidas de tipo `error`. La salida de la sección 0 dice «Entorno OK — Python 3.13.2, 18 dependencias directas verificadas». |
| B3 | pytest pasa entero (15 pasados, 0 saltados) | CUMPLE | `pytest -rA` desde la raíz: `15 passed in 2.41s`, sin saltados. |
| B4 | Toda cifra del resumen, del HANDOFF y del informe coincide con un artefacto | CUMPLE | Se contrastaron contra las tablas, una por una: las globales (`05`, `08`: 1,2319/0,0358, 1,3626/0,0414, 1,3967/0,0447, 1,5210/0,0443, 2,4384/0,1686, razones 0,9305/1,0067…, 27 ceros); las de los ocho municipios y las razones por municipio (`06`), incluidos 12/10/3/1/1 ceros; las de cada corte, recalculadas desde `07` (rangos, cortes 43, 46, 11 y 5, desvíos 0,2456/0,2839/0,3036/0,3061/1,1560, victorias de L1 44/47/45/38); las del control cruzado (`04`: −0,000032 y +0,000046); las particiones (`02`); las 13.160 filas de `09`; M0 1,4014 y M2 1,2385 (`diagnostico_municipios/tablas/18`, pliegue B); −0,36 % y −0,01 % (§7.5 del resumen del diagnóstico); 58,9 mm (`resumen_diagnostico_municipios.md:200`). Las fechas de publicación de xgboost 3.4.1 (2026-08-15) y pytest 9.1.1 (2026-06-19) se verificaron en PyPI. «Fallan 5» con la compuerta abierta se reprodujo (Paso 2.4, mutación M4). El informe (`documentacion/informe/`) no se tocó en esta fase. Una salvedad sin efecto en el veredicto: las versiones de la resolución del dashboard que cita el HANDOFF no tienen artefacto y hoy no se reproducen (riesgo R2). |
| B5 | Las reglas fijadas no se modificaron después de ejecutar | CUMPLE | La sección 1 (celda 3) coincide con el Prompt 1 del registro, sin (d), que se quitó en el Prompt 2 **antes** de iniciar la Etapa 1. No contiene ninguna cifra ni decisión que dependa de resultados: la elección de L0, que sí depende de ellos, quedó afuera y figura como pendiente. El historial de git no permite probar la cronología, porque hay un solo commit (riesgo R1). |
| B6 | Entorno coherente | CUMPLE | La verificación de entorno del notebook está en verde. `pip check` devuelve «No broken requirements found». Los 18 pines de `requirements.txt` son iguales a los del lock. `pip freeze` del `.venv` coincide línea a línea con `requirements-lock.txt` (127 paquetes, sin diferencias). |
| N1 | El documento acompañante sigue la estructura de CLAUDE.md, con la lista de frases prohibidas | CUMPLE | `resumen_modelos_candidatos.md` tiene encabezado, «Cómo usar» (§0), «Qué hace y por qué» con decisiones descartadas (árbol, conjunto (d)), resultados en tablas con su artefacto (§3), limitaciones y 8 «Frases que NO deben aparecer» (§5), índice de artefactos (§6) y pendientes (§7). Tiene un defecto de referencia cruzada (observación 4). |
| N2 | HANDOFF y registro de IA actualizados con la sesión | CUMPLE | `HANDOFF.md:1711-1754`, sesión 2026-10-13/14. `registro_uso_IA.md`: sesión con prompts textuales, uso y verificación. Hay un dato desactualizado (observación 5). |
| N3 | Las lecturas separan evidencia de inferencia | CUMPLE | En el resumen, §1.4, §3.1, §3.3 y §3.4 tienen bloques **Evidencia** e **Inferencia** separados, y §3.2 se rotula «no es una verificación formal». Hay una frase factual inexacta sobre la carga (observación 6). |
| N4 | Los resultados negativos quedan registrados | CUMPLE | Están registrados: L0 de 4 semanas (la del E2) por detrás de la media constante; L0 de 2 semanas con 27 predicciones cero; F, donde la media constante le gana a L1; la subestimación de L1 (0,9305); el retiro del árbol y del conjunto (d) con su motivo; el corte 43 «no se investigó». |
| N5 | Código legible: sin código muerto, `src/` documentado, nombres consistentes | **NO CUMPLE** | Código muerto: `exp_dias = lambda r: …` (celda 9 del notebook) se define y no se usa nunca. Además, `src/variables.py:12` quedó con una viñeta que termina en «;» seguida de línea vacía, resto de haber quitado la lluvia. Lo demás está bien: todas las funciones de `src/` tienen docstring y los nombres son consistentes con el ETL (`zona_id`, `n_siniestros`, `tipo_dia`). |
| N6 | El alcance coincide con lo pedido | **NO CUMPLE** | De más, declarado y justificado: `src/datos.py`, no pedido (lo declara el registro). De menos: el prompt pedía que «todo lo que aprende de los datos se estim[e] … usando las funciones de `src/variables.py`», pero `modelo_L1` y `modelo_media_constante` (celda 13) calculan el nivel del municipio con `ent.groupby("zona_id")["n_siniestros"].mean()` en lugar de `var.nivel_municipio`, y el factor de calendario no tiene función en `src/`. Lo demás está como se pidió, y la parte 0c se detuvo correctamente porque el dashboard no está en el repo. |
| F0-B1 | xgboost y pytest con versión exacta; el lock suma solo xgboost, pytest, iniconfig y pluggy | CUMPLE | `requirements.txt`: `xgboost==3.4.1`, `pytest==9.1.1`. `git diff 34ff44d -- requirements-lock.txt`: +`iniconfig==2.3.1`, +`pluggy==1.6.0`, +`pytest==9.1.1`, +`xgboost==3.4.1` y el cambio del comentario de cabecera. No cambia ningún otro pin. |
| F0-B2 | Los tests detectan fugas | CUMPLE | Se probó en una copia de `src/`, `tests/` y `pytest.ini` fuera del repo (scratchpad, ya borrada). Sin mutar: 13 pasan y 2 se saltan (en la copia no hay panel). M1, nivel reciente con `fecha <= origen`: **2 fallan**. M2, nivel del municipio con los 7 días del horizonte: **4 fallan**. M3, compuerta `observado()` con `<=`: **4 fallan**. M4, compuerta que devuelve todo el panel: **5 fallan**. |
| F0-B3 | Ninguna función de `src/variables.py` lee `n_siniestros` sin pasar por la compuerta | CUMPLE | `nivel_municipio` (`:70`), `nivel_reciente` (`:83`), `rezagos` (`:103`) y `matriz_entrenamiento` (`:187`) leen el objetivo sobre `observado(panel, origen)`. `_serie_diaria` solo recibe salidas de `observado`. `calendario_8`, `_agregar_fijas` y `variables_horizonte` solo leen `fecha`, `zona_id` y `tipo_dia`. |
| F0-N1 | La lluvia no aparece en `src/variables.py` y el motivo está escrito | CUMPLE | Las únicas menciones están en el docstring del módulo (`:14-17`): el motivo (no disponible a 7 días; sin aporte fuera de muestra, §7.5) y «No hay función ni columna de lluvia». El test lo comprueba (`tests/test_variables.py:140`). |
| F0-N2 | `pytest.ini` silencia solo el aviso de numpy 2.5 con pandas 2.3.3, con comentario | CUMPLE | Un solo filtro: `ignore:The .generic. unit for NumPy timedelta:DeprecationWarning`, con comentario. Con `-o filterwarnings=` aparecen 72 avisos, todos de ese mensaje. El comentario es impreciso (observación 7). |
| F0-N3 | README actualizado con pytest y xgboost | CUMPLE | `README.md`: lista de dependencias, «Dependencias que hoy no están» (vuelven el 2026-10-13), tabla de orden de ejecución (fila 4), registro de entorno y estado de `tests/`. |
| F0-N4 | La lectura accidental del test está asentada en HANDOFF y en el registro (D22) | CUMPLE | `HANDOFF.md:1717-1722` («Incidente: lectura del test») y `registro_uso_IA.md`, «Incidente declarado — lectura del test». En los dos consta qué se leyó, que no se tocó `n_siniestros` y la medida adoptada. |
| F1-B1 | El motor reproduce 1,5178 y 1,3782 en el Municipio C (tolerancia 0,001) | CUMPLE | `tablas/04`: 1,517768 (dif. −0,000032) y 1,378246 (dif. +0,000046), 47 cortes y 329 días. Se reprodujo dos veces, en la reejecución con nbconvert y al ejecutar las celdas del notebook en la copia temporal, con las mismas cifras. |
| F1-B2 | La sección 1 coincide con las reglas del plan, sin (d) | **NO CUMPLE** | Coinciden: conjuntos (0), (a), (b) y (c); (d) eliminado con motivo; grilla 3×2×2 = 12; ventanas expansiva y 364/546/728; media constante; L1 de 8 niveles; GLM Poisson; XGBoost `count:poisson`. No coinciden: (1) **L0**: la sección 1 la define como «promedio de lo observado 7, 14, 21 y 28 días antes; su ventana se revisa con 2, 4 y 8 semanas», no como «L0 de 8 semanas». (2) **NB2**: dice «GLM binomial negativa» sin fijar la parametrización. La familia NB de un GLM es NB2 por construcción, pero no está escrito. (3) Diferencia menor: la regla de selección tiene sus 5 criterios en 4 ítems numerados (el 4 reúne estabilidad y calibración, en ese orden), idéntica al texto del Prompt 1. |
| F1-B3 | Ningún nivel ni factor se estima con datos del horizonte | CUMPLE | Se hizo en memoria, en la copia temporal: 705 comparaciones (5 referencias más L1 de 3 niveles, por las ventanas expansiva, 364, 546 y 728 —L0 solo en la expansiva— y por los 47 cortes). La vista se pasó **sin enmascarar** el futuro, con el objetivo de los días ≥ origen real y alterado a enteros aleatorios entre 500 y 10⁶. Diferencia máxima entre predicciones: **0,0**; cortes con predicción distinta: **0**. Por el motor completo (corte 21, L1, panel alterado a 10⁶ desde el origen), las predicciones son idénticas. |
| F1-B4 | La ventana deslizante tiene exactamente N días en cada corte | CUMPLE | `tablas/03` lo comprueba para N = 364. Se extendió a los tres N en los 47 cortes: `ventana_de_entrenamiento` da {364}, {546} y {728} días; {2.912}, {4.368} y {5.824} filas; bordes [origen − N, origen − 1] en los 47. `var.matriz_entrenamiento(dias_ventana=N, solo_completas=False)` da lo mismo. |
| F1-N1 | Métricas globales, por municipio y por corte; predicciones por corte, día y municipio | CUMPLE | Métricas en `tablas/05` (global), `06` (40 filas = 5 × 8) y `07` (235 = 5 × 47). Predicciones en `09`: `modelo, corte, origen, fecha, zona_id, n_siniestros, pred`, 13.160 filas. |
| F1-N2 | M0 1,4014 y M2 1,2385 marcadas como chequeo de coherencia, no citables | CUMPLE | En el resumen, el título de §3.2 es «Coherencia con el diagnóstico (no es una verificación formal)» y el texto dice «No son comparables como cifra a citar (otro protocolo); sirven para ver que nada está roto». El HANDOFF no las cita. |

---

## Resultado de la reejecución (Paso 2.3)

- `git status` después de nbconvert: solo `M notebooks/modelos_candidatos.ipynb`. **Los 14 artefactos de
  `experiments/modelos_candidatos/` (11 CSV y 3 PNG) se reescribieron y quedaron idénticos byte a byte**: el
  `git hash-object` de cada archivo coincide con el blob del índice.
- **Ninguna cifra cambió.** Se comparó la salida textual del notebook antes y después, sin los avisos de deprecación,
  y es idéntica. Las 1.488 líneas del diff del notebook se reparten así:
  - 88 de metadatos de ejecución (marcas de tiempo, `execution_count`);
  - 1.130 de avisos `DeprecationWarning` con la ruta temporal del kernel (`C:\Users\victo\…\ipykernel_5896` pasa a la
    de esta máquina);
  - 270 de reordenamiento de esos mismos avisos entre bloques de `stderr`.
- Se restauró con `git restore notebooks/ experiments/` y `git status` quedó limpio.

---

## Observaciones (con lo que habría que hacer para corregirlas)

1. **F1-B2, bloqueante: la L0 y la binomial negativa no coinciden con el plan.** El equipo tiene que decidir cuál de
   las dos lecturas del veredicto es la correcta. **No hay que editar la celda de la sección 1:** hacerlo después de
   ejecutar viola B5 y su propia advertencia («Cualquier cambio posterior se registra aparte, con fecha y motivo, en el
   documento acompañante»). Lo que corresponde es:
   - **Si «L0 de 8 semanas» se decidió viendo la Etapa 1:** agregar debajo de la sección 1 una celda markdown
     *«Adenda fechada»* (y su espejo en `resumen_modelos_candidatos.md` §1.1). Tiene que decir que la L0 que pasa a la
     comparación final es la de 8 semanas, que se eligió **con los 47 cortes de validación** (1,3626 contra 1,5210 de la
     de 4 semanas, `tablas/05`) y que por eso es una elección informada por validación. También hay que cerrar el
     pendiente en HANDOFF y en el resumen §3.1 y §7.
   - **Si el plan lo fijaba desde antes:** la desviación es de la implementación. Se registra igual en la adenda, sin
     tocar la sección 1.
   - **En cualquier caso:** fijar en la misma adenda que la binomial negativa es **NB2** (varianza μ + αμ²) antes de
     ejecutar la fase 2.
2. **N5: código muerto.** Borrar `exp_dias` de la celda 9 del notebook y la viñeta residual de
   `src/variables.py:12-13`. Reejecutar y confirmar que los CSV quedan idénticos.
3. **N6: el nivel del municipio está duplicado.** En `modelo_L1` y `modelo_media_constante`, usar
   `var.nivel_municipio(vista, origen, ventana)` en lugar del `groupby` en línea. Si L1 va a llegar al prototipo, llevar
   también el factor de calendario agregado a `src/variables.py`, con un test de causalidad como los existentes.
   Reejecutar y comprobar que `tablas/05` a `09` no cambian.
4. **Referencia cruzada rota en el resumen.** `resumen_modelos_candidatos.md` §0, regla 4, dice «Respetar la sección 6
   (frases que no deben aparecer)», pero las frases están en §5 (§6 es el índice). Cambiar «sección 6» por «sección 5».
5. **HANDOFF desactualizado sobre el commit.** El alcance de la sesión dice «Sin commit ni push», pero el trabajo se
   commiteó en `main` como `74eafbd` con el mensaje «E3», que no es descriptivo como pide CLAUDE.md. Agregar una línea
   al HANDOFF y al registro con el hash y la decisión D23.
6. **Afirmación inexacta sobre la carga del test.** La celda 6 del notebook dice «ninguna fila del test llega a
   memoria», y el resumen y el docstring de `cargar_panel_desarrollo` dicen algo parecido. No es exacto: cada tramo de
   2.000 filas se parsea completo y recién después se filtra, así que las filas del test pasan por memoria un instante y
   no se conservan. Reformular como «ninguna fila del test se conserva ni se acumula; cada tramo se filtra al leerlo»,
   para que la frase sea defendible ante el tribunal.
7. **Comentario de `pytest.ini` impreciso.** Dice «no viene de src/», pero el aviso se dispara en llamadas
   `pd.Timedelta(days=…)` de `src/variables.py` (líneas 72, 84, 106, 187 y 188). La causa es la combinación de pandas
   2.3.3 con numpy 2.5.2, no el código del proyecto. Reescribir: «lo emite pandas 2.3.3 con numpy 2.5.2 en cada
   `pd.Timedelta(days=…)`, también en las llamadas de src/; no indica un error del proyecto».
8. **Notebook inflado por avisos.** El notebook commiteado lleva unas 1.100 líneas del mismo `DeprecationWarning`, con
   rutas del equipo de un integrante. Agregar en la celda de imports un
   `warnings.filterwarnings("ignore", message="The .generic. unit for NumPy timedelta", category=DeprecationWarning)`
   con el mismo comentario que `pytest.ini`.

---

## Riesgos fuera de criterios (no afectan el veredicto)

- **R1. No hay trazabilidad temporal en git.** Todo entró en un único commit en `main` (D23), así que no se puede
  demostrar con el historial que la sección 1 precede a la ejecución. B5 se sostiene con evidencia indirecta (registro
  y contenido). Para las fases siguientes conviene commitear las reglas **antes** de ejecutar, en su propia rama.
- **R2. La resolución de dependencias del dashboard no se reproduce.** El HANDOFF cita streamlit 1.65.0 y pymongo
  4.18.3. El mismo `pip install --dry-run -c requirements-lock.txt` da hoy **streamlit 1.66.0** y **pymongo 4.19.0**
  (plotly 7.1.0, pydeck 0.9.3, psycopg2-binary 2.9.13 y python-dotenv 1.2.4 no cambian). No hay artefacto que la
  respalde. En la fase 5, fijar versiones exactas antes de integrar.
- **R3. Doble redondeo.** El resumen §3.3 da 1,5156 para L0 de 8 semanas en CH, coherente con el CSV redondeado
  (1,51555). La salida del notebook muestra 1,5155. Si alguien cita desde el notebook, la cifra no coincide con la del
  resumen.
- **R4. Validación optimista.** Las referencias, la revisión de la ventana de L0 y la futura selección usan los mismos
  47 cortes. Está declarado; sumado a la observación 1, la L0 de 8 semanas queda elegida con validación.
- **R5. Parte de `src/` todavía no se usó con datos reales.** `matriz_entrenamiento`, `variables_horizonte` y los
  niveles recientes solo los ejercitan los tests (sintético más un horizonte real). La fase 2 será su primer uso real;
  conviene repetir ahí la prueba de F1-B3 con los candidatos.
- **R6. B3 depende de tener el panel.** En un clon sin `data/processed/`, pytest da 13 pasados y 2 saltados. Por eso
  la condición «15 pasados, 0 saltados» depende de regenerar antes el ETL.

---

## Comandos ejecutados (resumen)

```text
git switch main; git pull; git switch -c e3/fase-0-1-protocolo; git log -1 --oneline   -> 74eafbd E3
python -c "import sys; print(sys.executable, sys.version)"                            -> .venv, 3.13.2
Get-FileHash -Algorithm SHA256 data/processed/panel_diario_montevideo.csv              -> 82467fc8…4a1b06
pytest -rA                                                                             -> 15 passed
pip check                                                                              -> No broken requirements found
pip freeze vs requirements-lock.txt                                                    -> 127 = 127, sin diferencias
jupyter nbconvert --to notebook --execute --inplace notebooks/modelos_candidatos.ipynb -> exit 0, 0 errores
git hash-object (14 artefactos) vs índice                                              -> 14 IGUAL
git restore notebooks/ experiments/; git status                                        -> limpio
Mutaciones M1–M4 en copia temporal fuera del repo                                      -> 2 / 4 / 4 / 5 tests fallan
F1-B3 y F1-B4 en copia temporal (celdas del notebook, panel vía cargar_panel_desarrollo) -> 0 diferencias; 364/546/728 exactos
pip install --dry-run -c requirements-lock.txt streamlit plotly pydeck psycopg2-binary pymongo python-dotenv
```

La copia temporal se borró al terminar. Esta revisión no hizo commit ni push.
