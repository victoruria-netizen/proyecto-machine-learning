# Resumen de la evaluación final — la solución en el bloque final (Entregable 3, fase 4)

**Notebook:** [`notebooks/evaluacion_final.ipynb`](../notebooks/evaluacion_final.ipynb) — **el único del repositorio que lee el bloque final**
(2025-02-06 → 2025-12-31), además de `train/train_modelo_final.py` (excepción declarada, D51).
**Artefactos:** `experiments/evaluacion_final/` (`tablas/00` a `20`, `figuras/fig1` a `fig5`, `predicciones_bloque_final.csv`,
`registro_ejecucion.csv`) y `models/` (`modelo_final.json`, `metadata.json`).
**Código que usa:** `src/modelo.py` (nuevo en la fase 4), `src/variables.py` (con `tipo_dia`, D50), `src/datos.py`; pruebas en
`tests/test_modelo.py`, `tests/test_variables.py` y `tests/test_train_modelo_final.py` (`pytest`: 46 pasados).
**Fecha de ejecución:** primera ejecución completa el **2026-10-20T19:28:50, commit `86630a3`** (`registro_ejecucion.csv`); la versión
vigente del notebook es la reejecución sobre `c235ce2`, commiteada en `6be0383`, que reproduce ese registro (§1.6).
**Alcance:** los ocho municipios de Montevideo; 47 cortes de 7 días en el bloque final (329 días, 2.632 pares día-municipio), con
reentrenamiento en cada corte; exportación del modelo final entrenado hasta el 2025-12-31.

> ### Estado: evaluación ejecutada; modelo final exportado; **verificado en el servidor** (job 136, §4.3)
>
> El notebook se escribió y commiteó antes de leer el bloque final (`86630a3`, pusheado). La primera ejecución completa fijó las métricas en
> `registro_ejecucion.csv`; las reejecuciones con la exportación (sección 13) las reprodujeron con diferencia relativa máxima 2,51e-15. El
> entrenamiento del modelo final en el servidor institucional coincidió con la exportación local (diferencias del orden de 1e-12).

---

## 0. Cómo usar este documento

Contexto autocontenido para redactar *Experimentación y resultados* (evaluación final), *Análisis crítico* y *Conclusiones* del informe sin
abrir el repositorio.

1. **Ninguna cifra sin artefacto.** Cada cifra lleva la tabla que la respalda; lo que falta se marca `<!-- PENDIENTE: ... -->`.
2. **Distinguir evidencia de inferencia.** Las lecturas van rotuladas: *Los datos muestran* (lo que dice la tabla) y *Lectura del
   equipo* (inferencia, a validar por el equipo).
3. **No escribir Introducción ni Marco teórico** a partir de este documento.
4. **Respetar §5** (frases que no deben aparecer en el informe) y **§6** (diferencias con el informe: no se resuelven acá; se alinean en la
   fase 6, D49).
5. **La solución no se eligió con el bloque final.** Quedó fijada en `experiments/modelos_candidatos/solucion_seleccionada.json`, commit
   `1560a5b`, antes de este notebook; ninguna cifra de aquí puede cambiarla (verificación con git en `tablas/01`).

---

## 1. Qué hace el notebook y por qué

### 1.1 Precisiones fijadas antes de leer el bloque final

Espejo de la celda «Precisiones de la evaluación final» del notebook.

| N.º | Contenido | Origen |
| --- | --- | --- |
| D48 | Modelos: solución GLM Poisson (a) deslizante 364 d; sensibilidad GLM Poisson (a) expansiva (**no puede reemplazar a la solución aunque gane en el test**, D42); contraste XGBoost (a) d=2 n=100 lr=0,1 deslizante 364 d (**no compite**); referencias: media constante, L0 de 8 semanas, L1. Intervalos según D44: μ de la solución y α de NB2 (a) 364 d ajustada en cada corte; también Poisson | Prompt de la fase 4 |
| D50 | Reproducción de la fase 2 en `tests/test_modelo.py` (1e-9 contra el camino de la fase 2 reconstruido; tolerancia de redondeo contra `tablas/31`, `45`, `46`); `entrenar` recibe el panel ya recortado; **fallback de NB2: plan B de D28 (α por momentos) y Poisson solo si no da α positivo** (reemplaza a D48 en ese punto); calendario de fechas fuera del panel con `var.tipo_dia` | Respuestas del equipo al paso 4a |
| D51 | Intervalos solo para la solución (NB2 principal, Poisson secundario); exportación local dentro del notebook después del registro; `train/train_modelo_final.py`, excepción declarada a la regla de lectura del bloque final; `models/historia_reciente.csv` fuera del alcance; tolerancia de los tests 6e-7 | Equipo, 20/10/2026 |
| D52 | Elecciones de análisis: cortes y ventanas; control previo en validación; métricas; comparaciones (contra L1, media constante y la propia validación; pareado descriptivo); análisis de errores; formato de `predicciones_bloque_final.csv`; registro con tolerancia relativa 1e-10; estado de los objetivos fijado antes, con los resultados del test como evidencia | Propuesta de la IA, confirmada por el equipo con dos ajustes |

### 1.2 Decisiones posteriores a la primera ejecución (D53 a D58)

Ninguna cambia una decisión de modelado ni una cifra de la evaluación: tratan del registro, de la exportación y del script del servidor.

| N.º | Contenido | Motivo |
| --- | --- | --- |
| D53 | Los resultados de la ejecución oficial se commitean y pushean tal como salieron (`3852498`). `registro_ejecucion.csv` no se modifica: **`arbol_limpio = False` queda** (§1.6). La exportación (paso 4c) se agrega al final del notebook solo como celdas nuevas, se commitea el código antes de reejecutar y la reejecución tiene que reproducir el registro dentro de 1e-10 con `git diff` vacío sobre `experiments/` | Conservar la primera ejecución como evidencia y exportar sin tocar lo evaluado |
| D54 | `metadata.json` no lleva `arbol_limpio` sino **`fuentes_limpias`**: `git status --porcelain -- . ":(exclude)experiments" ":(exclude)models"` vacío, calculado en la primera celda de la sección 13, antes de escribir en `models/`; su definición va escrita en el JSON. `cargar_modelo` y la predicción con el modelo cargado no dependen de statsmodels ni de xgboost (se importan solo dentro de `entrenar`); scipy y `holidays` se mantienen (cuantiles de D44 y calendario de D50) | Que el prototipo y el servidor puedan cargar y predecir sin esas bibliotecas; un indicador de árbol limpio que no confunda las salidas de la propia ejecución con fuentes sin commitear |
| D55 | La celda 32 (índice de artefactos) se corrige para no listarse a sí misma: **excepción declarada a D53** (error de código sin efecto en métricas; §1.6). Las marcas de tiempo de nbconvert y las salidas de las celdas 7 y 26 se aceptan en el diff (el criterio de D53 se lee sobre el código). Los α ausentes van como `null` (`allow_nan=False`). El resumen declara el α por momentos del modelo exportado (§4.1) | Índice no idempotente; JSON estándar legible fuera de Python |
| D56 | `train/train_modelo_final.py`: comparación con la exportación local por **diferencia relativa máxima ≤ 1e-6** en coeficientes, μ de las 56 filas de la semana del 01/01/2026 y α; el log declara la implementación y las versiones del contenedor. Por compatibilidad con el contenedor (sin statsmodels ni `holidays`; Python 3.10.12 y pandas 2.3.3 según el log del job 136): matriz del conjunto (a) armada en el script con un test que exige igualdad con `src/`; IRLS en numpy; α por momentos (NB2 por MV no se intenta); calendario de la semana como constante verificada contra `var.tipo_dia`. Prueba previa en un entorno simulado | `src/variables.py` importa `holidays` y `src/modelo.py` entrena con statsmodels. Al decidirlo se usaron las versiones del 18/09/2026 (pandas 1.5.3, sin `stack(future_stack=True)`); el contenedor del 21/10 tenía otras (§4.3) |
| D57 | La guía del servidor (`Guia_entrenamientos_CPU_GPU`) es la fuente para todo lo que corre en él. La corrida la hace el equipo y **solo esa cuenta como evidencia**. La prueba en el entorno simulado es un chequeo previo y no va al informe | Equipo; texto de la decisión según el prompt del fix de la review R3 (21/10/2026) |
| D58 | `guardar_modelo` y la celda de metadata escriben los JSON con fin de línea LF (`newline="\n"`), con test; `.gitattributes` con `models/*.json text eol=lf`; reejecución con los chequeos de D55 y verificación de que `sha256_modelo` coincide con el archivo en git. El script del servidor compara el sha256 del modelo recibido con el de `metadata.json` **solo para informarlo** («coincide / no coincide»), sin detener la corrida | El `sha256_modelo` anterior se calculó sobre el JSON escrito con CRLF en Windows, distinto del archivo que guarda git (LF) |

Además, por indicación del equipo (21/10/2026), el script del servidor resuelve sus entradas relativas a su propia carpeta (`/train`) y
escribe `run_info.txt` según la guía del servidor (§4.2).

### 1.3 `src/modelo.py` (paso 4a y D54, D55)

- `entrenar(config, panel_hasta, ajustar_alpha=True)`: filas de `var.matriz_entrenamiento` con la ventana de la configuración, matriz de
  D31 y ajuste con los valores por defecto (GLM IRLS de statsmodels; XGBoost con los hiperparámetros del JSON). Con `ajustar_alpha`, NB2 (a)
  en las mismas filas para α (D29, D28, D50). No lee archivos. Es la única función que importa statsmodels y xgboost (D54).
- `predecir_semana(modelo, historia, origen)`: 56 filas (7 días × 8 municipios) con μ, intervalos del 80 % y 95 % (cuantiles 0,10/0,90 y
  0,025/0,975) y su tipo. Solo acepta el origen del modelo. De `historia` solo lee `tipo_dia` de los días del horizonte.
- `guardar_modelo(modelo, ruta)` / `cargar_modelo(ruta)`: el GLM en JSON (coeficientes, α y datos del ajuste), sin pickle; JSON estándar,
  con los valores no finitos como `null` (D55).
- **Verificación** (`tests/test_modelo.py`): en los 47 cortes de validación, μ y α coinciden a 1e-9 con el camino de la fase 2
  reconstruido en el test, y a 6e-7 con `tablas/31` (solución, sensibilidad y contraste), `45` y `46` de `modelos_candidatos`.
  `var.tipo_dia` coincide con el `tipo_dia` del ETL en los 1.316 días de desarrollo. Ida y vuelta exacta por JSON; carga y predicción en
  un proceso aparte con statsmodels y xgboost bloqueados en `sys.modules` (D54); un α no finito se escribe como `null` (D55).
  **Modelo exportado (D60):** `test_modelo_exportado_reproduce_la_prediccion_del_servidor` comprueba que el sha256 de
  `models/modelo_final.json` es el de `metadata.json`, carga el modelo y predice, sin historia (D51), la semana con origen 2026-01-01; compara las
  56 μ (8 municipios × 7 días) con `documentacion/logs/servidor_modelo_final/prediccion_semana_2026-01-01.csv` (job 136), con diferencia relativa
  máxima ≤ 1e-6 (criterio de D56). **Compara contra el servidor, no contra el notebook:** el notebook solo imprime esas predicciones a 3 decimales.
  No lee el panel.

### 1.4 Procedimiento de la evaluación

- **Cortes (D52, ítem 1):** 47 de 7 días, orígenes 2025-02-06 + 7k; el último horizonte termina el 2025-12-31. En cada corte, cada modelo
  se reentrena con todo lo observado antes del origen (desarrollo más las semanas ya transcurridas del bloque final) y su ventana: 364
  días para la solución y el contraste; expansiva para la sensibilidad y las tres referencias. El objetivo de los días ≥ origen no llega a
  ningún modelo (vista con NaN). Hiperparámetros fijos (JSON). *Por qué:* es el procedimiento de la validación y el del uso previsto
  (reentrenar cada semana); difiere del informe (§6, punto 1).
- **Control previo, sin el bloque final (D52, ítem 2):** el mismo procedimiento sobre los 47 cortes de validación, con
  `cargar_panel_desarrollo()`, reprodujo las **35 comprobaciones** (`tablas/02_control_validacion.csv`; diferencia máxima 5e-7, tolerancia
  6e-7). Si fallaba, la ejecución se detenía antes de leer el bloque final.
- **Panel completo (`tablas/03`, `04`):** sha256 igual al registrado por el diagnóstico; 1.645 días sin huecos, 13.160 filas; la parte de
  desarrollo es idéntica a `cargar_panel_desarrollo()`; bloque final de 329 días.
- **Métricas (D52, ítem 3):** desvianza de Poisson media (principal, EPS = 1e-6), error estándar sobre los 47 cortes, MAE, RMSE, total
  predicho/observado, días con predicción 0, desvío entre cortes y peor municipio.
- **Comparaciones (D52, ítem 4):** cada candidato contra L1 (su mismo conjunto de información), contra la media constante y contra su propia
  validación; L0 contra la media constante. Diferencia pareada corte a corte, **descriptiva** (como D35).
- **Ajustes (`tablas/05`):** 141 ajustes de candidatos (3 × 47), **0 con avisos y 0 GLM sin converger**. Origen de α en la solución: **NB2
  en 45 cortes, momentos (plan B de D28) en 2 (cortes 45 y 47, orígenes 2025-12-11 y 2025-12-25), Poisson en 0** (`tablas/18`).

### 1.5 Exportación del modelo final (sección 13; D51, D53 a D55)

Corre después de escribir el registro y no evalúa nada. Entrena la solución con `mod.entrenar` sobre todos los datos hasta el 2025-12-31 y
la ventana de 364 días; guarda `models/modelo_final.json` con `mod.guardar_modelo`, lo vuelve a leer con `mod.cargar_modelo` y exige que
prediga exactamente lo mismo que el modelo en memoria (56 filas). `models/metadata.json` lleva configuración, fecha de corte, versiones,
sha256 del panel y del modelo, α (D44 con el fallback de D50), `commit_base` y `fuentes_limpias` con su definición. El commit que contiene
el modelo se identifica con `git log -- models/modelo_final.json`, no con `commit_base` (D48). `models/historia_reciente.csv` quedó fuera
del alcance: el conjunto (a) no usa nivel reciente ni rezagos (D51). Resultados en §4.

### 1.6 Ejecuciones, errores y correcciones

| Ejecución | Commit base | Resultado | Qué se hizo |
| --- | --- | --- | --- |
| Intento con el Python del sistema | `86630a3` | Falló en la celda 3 (control del entorno: Python 3.13.9 y versiones distintas de `requirements.txt`) | `nbconvert` se lanzó sin activar el `.venv`. **No leyó el bloque final** ni escribió nada. Se reintentó con el `.venv` activado |
| **Primera ejecución completa** | `86630a3` | 0 errores; fija `registro_ejecucion.csv` (2026-10-20T19:28:50) | Commiteada tal como salió (`3852498`, D53) |
| Reejecución con la sección 13 | `ba17c8d` | Registro reproducido (2,51e-15), pero `tablas/20_artefactos.csv` pasó de 27 a 28 filas | **Error de código en la celda 32**; descartada (D55) |
| Reejecución con D55 | `42fe260` | Registro reproducido (2,51e-15); índice con 27 filas, igual a `3852498`; `git diff` sobre `experiments/` vacío; JSON sin NaN | Commiteada (`d93cf0c`) |
| Reejecución con D58 | `c235ce2` | Registro reproducido (2,51e-15); índice con 27 filas; `git diff` sobre `experiments/` vacío; coeficientes, α y μ e intervalos de las 56 filas idénticos a `d93cf0c`; `sha256_modelo` igual al sha256 de `git show HEAD:models/modelo_final.json` | Commiteada (`6be0383`); es la versión vigente. Durante esta reejecución, los tres documentos sin commitear (`HANDOFF.md`, `registro_uso_IA.md` y este resumen) se apartaron con `git stash`, porque no participan del cálculo, para que `fuentes_limpias` reflejara solo las fuentes; se restauraron después |

**Error de la celda 32 (índice de artefactos), antes y después (D55).** *Antes:* `DIR_TABLAS.glob("*.csv")` listaba todas las tablas,
incluida `20_artefactos.csv` si ya existía; en la primera ejecución no existía (27 filas) y en la reejecución sí (28 filas, con la línea
`tablas/20_artefactos.csv`). *Después:* la celda excluye `20_artefactos.csv` y el índice vuelve a tener las 27 filas de `3852498`. No afecta
ninguna métrica: el registro se reprodujo en ambas reejecuciones. Es la única celda existente modificada después de la primera ejecución,
como excepción declarada a D53.

**`arbol_limpio = False` en `registro_ejecucion.csv` (D53).** La celda del registro lo calcula como `git status --porcelain == ""`, y se
ejecutó **después** de que la propia ejecución creara `experiments/evaluacion_final/` (sin seguimiento todavía); `nbconvert` no reescribe el
notebook hasta el final. La evidencia de árbol limpio es el commit **`86630a3`, pusheado antes de ejecutar**: `git status` estaba vacío al
lanzar la ejecución. El archivo no se modificó. En `metadata.json` el indicador equivalente es `fuentes_limpias` (D54), que excluye esas
salidas: vale `true`.

---

## 2. Resultados en el bloque final

### 2.1 Métricas globales (`tablas/06_globales.csv`)

| Modelo | Papel | Desvianza | EE (47 cortes) | MAE | RMSE | Pred./obs. | Desvío entre cortes | Desvianza en validación |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| GLM Poisson (a) 364 d | solución | **1,1063** | 0,0335 | 1,3985 | 1,7677 | 0,9606 | 0,2299 | 1,2205 |
| XGBoost (a) 364 d | contraste | 1,1198 | 0,0341 | 1,4148 | 1,7826 | 0,9608 | 0,2341 | 1,2280 |
| GLM Poisson (a) expansiva | sensibilidad | 1,1329 | 0,0355 | 1,4019 | 1,7900 | 0,8989 | 0,2436 | 1,2302 |
| L1 (nivel × calendario de 8 niveles) | referencia | 1,1359 | 0,0357 | 1,4023 | 1,7921 | 0,8952 | 0,2448 | 1,2319 |
| L0 (8 semanas) | referencia | 1,2432 | 0,0387 | 1,4844 | 1,8776 | 0,9785 | 0,2651 | 1,3626 |
| Media constante | referencia | 1,3152 | 0,0401 | 1,5244 | 1,9376 | 0,8944 | 0,2751 | 1,3967 |

Ningún modelo tuvo días con predicción 0. Peor municipio: CH en todos (solución 1,2777), salvo la media constante (C, 1,6149).

**Los datos muestran:**
- La solución tiene la menor desvianza de los seis; le siguen el contraste, la sensibilidad y L1. El orden de los cuatro primeros es el
  mismo que en validación.
- Frente a su referencia (L1): solución −0,0295 (gana 33 de 47 cortes); contraste −0,0161 (22 de 47); sensibilidad −0,0030 (40 de 47).
  L0 frente a la media constante: −0,0720 (34 de 47). Frente a la media constante, la solución gana 46 de 47 cortes.
- **Todos** los modelos tienen menor desvianza en el bloque final que en validación, incluida la media constante: diferencia
  final − validación entre −0,0815 (media constante) y −0,1195 (L0); la solución, −0,1142.
- La solución y el contraste predicen cerca del 96 % del total observado (0,9606 y 0,9608); la sensibilidad, L1 y la media constante, cerca
  del 90 % (0,8989, 0,8952, 0,8944).

**Lectura del equipo (inferencia, a validar):** como la desvianza baja en el bloque final para todos los modelos, incluida la media
constante, la diferencia final − validación refleja en buena parte un bloque más fácil de predecir y no una mejora atribuible a un modelo;
las comparaciones informativas son las hechas dentro del mismo bloque.

### 2.2 Diferencia pareada corte a corte (`tablas/09_pareado.csv`) — descriptiva

| Comparación | Diferencia media | EE | Media/EE | Cortes que gana a / b |
| --- | --- | --- | --- | --- |
| solución − L1 | −0,0295 | 0,0071 | −4,13 | 33 / 14 |
| sensibilidad − L1 | −0,0030 | 0,0005 | −5,53 | 40 / 7 |
| contraste − L1 | −0,0161 | 0,0084 | −1,91 | 22 / 25 |
| solución − sensibilidad | −0,0265 | 0,0067 | −3,94 | 33 / 14 |
| solución − media constante | −0,2088 | 0,0200 | −10,46 | 46 / 1 |

**Las razones media/EE no son pruebas de significación** (D35, D52 ítem 4): los 47 cortes son semanas consecutivas de una misma serie, no
muestras independientes, y no se fijó un nivel ni una prueba antes de ejecutar. Se informan como tamaño de la diferencia relativo a su
variabilidad entre cortes.

**Los datos muestran:** la sensibilidad le gana a L1 en más cortes (40) que la solución (33), pero por una diferencia media diez veces
menor (−0,0030 contra −0,0295). El contraste le gana a L1 en menos de la mitad de los cortes (22 de 47).

### 2.3 Por municipio (`tablas/07_por_municipio.csv`, desvianza)

| Municipio | Solución | Sensibilidad | Contraste | L1 | L0 | Media constante |
| --- | --- | --- | --- | --- | --- | --- |
| A | 1,0614 | 1,1064 | 1,0767 | 1,1130 | 1,1836 | 1,2708 |
| B | 1,1401 | 1,1520 | 1,1698 | 1,1546 | 1,2800 | 1,3965 |
| C | 1,0448 | 1,0869 | 1,0883 | 1,0875 | 1,1791 | 1,6149 |
| CH | 1,2777 | 1,2883 | 1,2680 | 1,2887 | 1,4314 | 1,4165 |
| D | 1,0989 | 1,1227 | 1,1364 | 1,1257 | 1,2587 | 1,4261 |
| E | 1,1150 | 1,1606 | 1,1076 | 1,1648 | 1,2606 | 1,1847 |
| F | 1,0701 | 1,0858 | 1,0664 | 1,0892 | 1,2156 | 1,0854 |
| G | 1,0427 | 1,0604 | 1,0454 | 1,0635 | 1,1362 | 1,1266 |

**Los datos muestran:** la solución tiene menor desvianza que L1 en los ocho municipios. El contraste es el mejor en CH, E y F; la
solución, en A, B, C, D y G. CH es el peor municipio para todos los modelos salvo la media constante.

### 2.4 Por semana

`tablas/08_por_corte.csv` (282 filas: 6 modelos × 47 cortes) y `figuras/fig1_desvianza_por_corte.png`. El desvío entre cortes de la
solución es 0,2299 (`tablas/06`). Las cinco semanas de mayor desvianza están en §3.2.

---

## 3. Análisis de errores en el bloque final

Los mismos cálculos que la sección 12 de `modelos_candidatos` (D52, ítem 5). **No se atribuyen causas:** los datos no registran qué pasó en
cada semana.

### 3.1 Errores por municipio y por tipo de día (`tablas/10`, `11`)

Solución, por municipio (`tablas/10`): residuo medio (observado − predicho) positivo en seis municipios (A 0,0702; B 0,2049; C 0,1501;
CH 0,1638; D 0,1846; E 0,1947) y casi nulo en F (−0,0157) y G (0,0156); total pred./obs. entre 0,9233 (E) y 1,0054 (F). En L1 el residuo
medio es positivo en los ocho (entre 0,1812 en G y 0,4537 en A), con pred./obs. entre 0,8496 (E) y 0,9251 (G).

Por tipo de día (`tablas/11`, desvianza):

| Calendario | n | Solución | Sensibilidad | Contraste | L1 | Pred./obs. de la solución |
| --- | --- | --- | --- | --- | --- | --- |
| lunes | 352 | 1,1171 | 1,1323 | 1,1281 | 1,1367 | 0,9762 |
| martes | 360 | 1,1665 | 1,2132 | 1,1846 | 1,2176 | 0,9355 |
| miércoles | 368 | 1,0495 | 1,0614 | 1,0639 | 1,0602 | 1,0053 |
| jueves | 344 | 1,1436 | 1,2181 | 1,1585 | 1,2239 | 0,9347 |
| viernes | 360 | 0,9191 | 0,9399 | 0,9591 | 0,9391 | 0,9556 |
| sábado | 368 | 1,2353 | 1,2340 | 1,2275 | 1,2352 | 0,9496 |
| domingo | 352 | 1,0704 | 1,0874 | 1,0788 | 1,0915 | 0,9797 |
| feriado | 128 | 1,2256 | 1,2622 | 1,2264 | 1,2743 | 0,9395 |

**Los datos muestran:** la solución subestima el total en siete de los ocho niveles (pred./obs. < 1; el miércoles, 1,0053). Su mayor
desvianza está en sábado (1,2353) y feriado (1,2256); la menor, en viernes (0,9191).

### 3.2 Las cinco semanas de mayor desvianza de la solución (`tablas/12`, días en `tablas/13`)

| Rango | Corte | Semana | Solución | L1 | Rango de L1 entre 47 | Observado | Predicho | Pred./obs. | Días feriado |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 30 | 2025-08-28 a 09-03 | 1,6535 | 1,6369 | 2 | 166 | 168,86 | 1,0172 | 0 |
| 2 | 18 | 2025-06-05 a 06-11 | 1,5498 | 1,6923 | 1 | 216 | 166,74 | 0,7719 | 0 |
| 3 | 5 | 2025-03-06 a 03-12 | 1,4979 | 1,5750 | 3 | 187 | 163,46 | 0,8741 | 0 |
| 4 | 17 | 2025-05-29 a 06-04 | 1,4005 | 1,4419 | 4 | 165 | 165,97 | 1,0059 | 0 |
| 5 | 8 | 2025-03-27 a 04-02 | 1,3992 | 1,4409 | 5 | 168 | 164,19 | 0,9773 | 0 |

**Los datos muestran:** las cinco peores semanas de la solución son también las cinco peores de L1. Ninguna tiene feriados. En tres
(cortes 30, 17 y 8) el total predicho está dentro del 3 % del observado. El corte 18 es el de mayor subestimación (216 observados, 166,74
predichos).

**Lectura del equipo (inferencia, a validar):** la desvianza alta de esas semanas viene de la distribución entre días y municipios, no del
volumen semanal.

### 3.3 Calibración por deciles y residuos por corte (`tablas/14`, `15`, `16`; `figuras/fig4`)

Calibración (observada/predicha por decil de la predicción, `tablas/14`): solución entre 0,9426 (decil 5) y 1,1095 (decil 8), con 8 de 10
deciles por encima de 1; sensibilidad entre 1,0331 y 1,1985, con los 10 por encima de 1.

Tendencia de los residuos por corte (MCO, EE HAC de Newey-West con 4 rezagos; `tablas/16`):

| Modelo | Pendiente por corte | IC 95 % | Residuo medio, cortes 1–23 | Residuo medio, cortes 24–47 | Obs./pred. 1–23 | Obs./pred. 24–47 |
| --- | --- | --- | --- | --- | --- | --- |
| Solución | −0,00115 | [−0,0079; 0,0056] | 0,1685 | 0,0755 | 1,058 | 1,025 |
| Sensibilidad | 0,00024 | [−0,0065; 0,0070] | 0,3393 | 0,2825 | 1,125 | 1,101 |
| L1 | 0,00027 | [−0,0065; 0,0071] | 0,3504 | 0,2942 | 1,129 | 1,106 |

**Los datos muestran:** los tres intervalos de la pendiente incluyen el 0. La subestimación de la solución es menor en la segunda mitad
del bloque (obs./pred. 1,025) que en la primera (1,058); la de la sensibilidad y L1 es mayor en ambas mitades (entre 1,10 y 1,13).

**Lectura del equipo (inferencia, a validar):** la deslizante subestima menos el total que la expansiva, como ya ocurría en validación
(pred./obs. 0,9717 contra 0,9341, uno de los motivos de D42; `resumen_modelos_candidatos.md` §1.1). Una explicación posible, no
verificada con estos datos, es que la expansiva promedia un nivel anterior más bajo. No es una prueba.

### 3.4 Cobertura de los intervalos de la solución (`tablas/17`, `figuras/fig5`)

**La cobertura se compara contra la esperada por el propio modelo, no contra la nominal.** Con conteos (variable discreta), el intervalo
entre los cuantiles 0,10 y 0,90 cubre por construcción **al menos** el 80 % según el modelo, y en general más: la probabilidad que el
modelo asigna al intervalo es la «cobertura esperada por el modelo» (columna `cobertura_esperada_por_el_modelo`). La pregunta pertinente es
si la cobertura empírica coincide con esa, no con 80 % o 95 %.

Global (n = 2.632):

| Intervalo | Nominal | Empírica | Esperada por el modelo | Debajo | Encima | Ancho medio |
| --- | --- | --- | --- | --- | --- | --- |
| NB2 (principal) | 80 % | 0,9005 | 0,8871 | 0,0315 | 0,0680 | 4,47 |
| NB2 (principal) | 95 % | 0,9791 | 0,9810 | 0,0019 | 0,0190 | 6,71 |
| Poisson (secundario) | 80 % | 0,8913 | 0,8873 | 0,0334 | 0,0752 | 4,30 |
| Poisson (secundario) | 95 % | 0,9745 | 0,9799 | 0,0038 | 0,0217 | 6,44 |

Validación, para comparar (`modelos_candidatos/tablas/46`, reproducida en `tablas/02`), empírica (esperada por el modelo): NB2 0,8883 (0,8959)
al 80 % y 0,9787 (0,9840) al 95 %; Poisson 0,8712 (0,8937) y 0,9734 (0,9833).

Por municipio, NB2 al 80 %: empírica entre 0,8815 (B y D) y 0,9179 (G), esperada entre 0,8700 (C) y 0,9072 (CH); al 95 %, empírica entre
0,9696 (D) y 0,9909 (A), esperada entre 0,9711 (C) y 0,9862 (CH).

**Los datos muestran:** al 80 %, la cobertura empírica de NB2 supera a la esperada por el modelo en 1,3 puntos (0,9005 contra 0,8871); al
95 %, queda 0,2 puntos por debajo (0,9791 contra 0,9810). Los fallos son asimétricos: hay más observaciones por **encima** del intervalo
que por debajo (al 80 %, 6,8 % contra 3,2 %).

**Lectura del equipo (inferencia, a validar):** la asimetría es coherente con la subestimación del total (§2.1).

---

## 4. Modelo final exportado y corrida en el servidor

### 4.1 Modelo exportado (`models/modelo_final.json`, `models/metadata.json`)

| Campo | Valor | Fuente |
| --- | --- | --- |
| Configuración | GLM Poisson (a) [deslizante 364 d] | `metadata.json`, `configuracion` |
| Entrenamiento | 2025-01-02 a 2025-12-31: 364 días, 2.912 filas; GLM convergió en 4 iteraciones, sin avisos | `metadata.json`, `entrenamiento` |
| Origen de la primera predicción | 2026-01-01 | `metadata.json` |
| α de los intervalos | **0,00939508767764091, por momentos** (`origen_alpha: "momentos"`; `alpha_nb2_mv: null`) | `metadata.json`, `intervalos` |
| sha256 del panel | `82467fc8…114a1b06` (igual al del diagnóstico) | `metadata.json`, `panel` |
| `commit_base` / `fuentes_limpias` | `c235ce2…` / `true` | `metadata.json` |
| `sha256_modelo` | `94e562db…2a01939`, igual al del archivo en git (LF; D58) | `metadata.json`; `git show HEAD:models/modelo_final.json` |
| Commit que contiene el modelo | `d93cf0c` (único commit que toca `models/modelo_final.json`; el blob no cambió en `6be0383`, D58) | `git log -- models/modelo_final.json` |
| Tamaño | `modelo_final.json` 1.335 bytes; `metadata.json` 4.001 bytes (LF) | salida de la celda 36 |

**α por momentos (D55, ítem 4).** El modelo exportado usa α por momentos (0,009395) porque **NB2 no convergió en la ventana final**
(`alpha_mv` NaN, aviso «RuntimeWarning: invalid value encountered in log»; `nb2_avisos` en `modelo_final.json`), y el fallback de D50 tomó
el plan B de D28. Ese valor está en el **piso del rango de α del test** (0,0093 a 0,0339; `tablas/18`), y en el test ese origen de α se dio
en **2 de 47 cortes** (`tablas/05`, `18`). No se hizo ningún análisis adicional sobre el bloque final a partir de esto.

μ de la semana del 01/01/2026: salida de la celda 35 del notebook (tabla de 7 días × 8 municipios). Es una predicción, no una evaluación:
no hay observados con los que compararla en el repositorio.

### 4.2 `train/train_modelo_final.py` (D51, D56)

Misma exportación que la sección 13, para el servidor institucional (`submit_cpu`). Lee el panel completo: **excepción declarada a la regla
de lectura del bloque final** (D51); entrena y no evalúa. No importa `src/` (ver D56): arma la matriz del conjunto (a), ajusta el GLM con
IRLS en numpy, calcula α por momentos y usa el calendario de la semana como constante. Compara con `models/modelo_final.json` (≤ 1e-6 en
coeficientes, μ de las 56 filas y α) y termina con código 1 si no cumple. Instrucciones de envío en `train/README.md`.

**Verificación local, sin el bloque final** (`tests/test_train_modelo_final.py`, 7 tests): con el panel de desarrollo y tres orígenes de
validación, las filas y la matriz son idénticas a las de `src/`, y coeficientes, μ y α por momentos quedan dentro de 1e-6 de statsmodels;
el calendario constante coincide con `var.tipo_dia`; las rutas se resuelven junto al script; `run_info.txt` tiene las claves de la guía.

**Chequeo previo de compatibilidad (no es evidencia del servidor).** Antes de enviarlo se corrió en un entorno simulado con las versiones
que `train/README.md` registraba para el contenedor el 18/09/2026 (Python 3.10, numpy 1.24.4, pandas 1.5.3, scikit-learn 1.2.0, sin
statsmodels ni `holidays`) solo para comprobar que el script corre con ellas: terminó sin errores. El contenedor real del 21/10/2026 tenía
otras versiones (§4.3). Ese chequeo no reemplaza la corrida del servidor y **sus cifras no se citan como resultado**. Rutas: el script
resuelve el panel, `models/modelo_final.json` y `models/metadata.json` relativos a su propia carpeta (en el servidor, `/train`) e imprime
las rutas resueltas; escribe `run_info.txt` (guía del servidor, §11). Una primera versión buscaba la raíz de otra forma (`037851b`); se
reemplazó por la resolución relativa al script por indicación del equipo. Informa si el sha256 del modelo recibido coincide con el
`sha256_modelo` de `metadata.json`, sin detener la corrida (D58).

**`sha256_modelo` de `metadata.json` (corregido, D58).** Hasta `d93cf0c` se calculaba sobre `modelo_final.json` escrito con CRLF en
Windows, mientras que git guarda el archivo con LF, así que no coincidía con el archivo del repositorio. Desde `6be0383` los JSON se
escriben con LF y `.gitattributes` fija `models/*.json text eol=lf`; se verificó que `sha256_modelo` es igual al sha256 de
`git show HEAD:models/modelo_final.json`. Los coeficientes y α no cambiaron.

### 4.3 Corrida en el servidor

La corrió el equipo en el servidor institucional el 21/10/2026. **Fuentes:** `documentacion/logs/log_servidor_modelo_final.txt` (log del
job 136) y `documentacion/logs/servidor_modelo_final/` (`resumen_corrida.json`, `run_info_1.txt` —copia del `run_info.txt` de la
corrida—, `prediccion_semana_2026-01-01.csv`, `modelo_final_servidor.json` y el `.sbatch` del job). `models/modelo_final.json` **no se
reemplazó**: el modelo del repositorio sigue siendo la exportación local; el del servidor queda como evidencia de la verificación.

| Campo | Valor (job 136) | Fuente |
| --- | --- | --- |
| Job / RUN_ID | 136, `grp04_cpu_train_modelo_final`; RUN_ID `20261021_094404`; 4 CPU, 12G; 21/10/2026 09:44:02 a 09:44:04 (−03) | log, líneas 1–32; `run_info_1.txt` |
| Imagen | `tensorflow_ngc_24.04_tf2_py3_mlcv.sif`; `/train` se monta como `/work/train` | log; `.sbatch` |
| Versiones del contenedor | Python 3.10.12, numpy 1.26.4, pandas 2.3.3, scikit-learn 1.7.2, scipy 1.12.0; **sin statsmodels ni `holidays`** | log, línea 36; `resumen_corrida.json` |
| Implementación | IRLS en numpy; α por momentos; NB2 por MV no se intentó; calendario de la semana con la constante (sin `holidays`) | log, líneas 34–35 y 68 |
| Entradas | panel con sha256 `82467fc8…114a1b06` (coincide); `metadata.json` con `commit_base` `c235ce2`; sha256 del modelo recibido `94e562db…2a01939`, **coincide** con `sha256_modelo` | log, líneas 45–46 y 127 |
| Entrenamiento | 2025-01-02 a 2025-12-31 (364 días, 2.912 filas); IRLS convergió en 5 iteraciones | log, líneas 48–49 |
| α (momentos) | 0,009395087677645849 | log, línea 66 |
| **Diferencia relativa máxima contra `models/modelo_final.json`** | coeficientes **4,25e-12**; μ de las 56 filas **3,42e-12**; α **5,26e-13** | log, líneas 129–131; `resumen_corrida.json` |
| Criterio de D56 (≤ 1e-6 en todo) | **CUMPLE**; el trabajo terminó sin error | log, línea 132 |

**Los datos muestran:** el modelo entrenado en el servidor, con otra implementación (IRLS en numpy en lugar de statsmodels) y otras
versiones de las bibliotecas, coincide con la exportación local con diferencias del orden de 1e-12, cinco órdenes de magnitud por debajo
del criterio fijado antes de correrlo. Un recálculo local a partir de `modelo_final_servidor.json` y `prediccion_semana_2026-01-01.csv`
contra `models/modelo_final.json` (con `src/modelo.py`) da las mismas cifras y el mismo calendario en las 56 filas.

**Primer intento (job 135).** Se detuvo antes de entrenar: el panel figuraba como `NO EXISTE` en
`/work/train/data/processed/panel_diario_montevideo.csv` y el script terminó con código 1
(`documentacion/logs/log_servidor_modelo_final_intento1_job135.txt`). Según el equipo, la carpeta del panel se había subido como
`processed ` (con un espacio al final); se corrigió el nombre y se reenvió como job 136. No entrenó ni escribió resultados del modelo.

**Versiones.** Las del contenedor del 21/10/2026 difieren de las registradas el 18/09/2026 con la misma imagen (job 104: numpy 1.24.4,
pandas 1.5.3, scikit-learn 1.2.0; `documentacion/logs/log_servidor_base.txt`). D56 se diseñó con las del 18/09. Con pandas 2.3.3,
`stack(future_stack=True)` ya no sería un impedimento, pero `src/variables.py` importa `holidays` al cargarse y `src/modelo.py` entrena
con statsmodels, y el contenedor no tiene ninguno de los dos: el script autocontenido sigue siendo necesario.

---

## 5. Limitaciones y lo que NO puede afirmarse

**Limitaciones:**
1. **Una sola serie de 47 semanas consecutivas.** Las comparaciones pareadas son descriptivas; no hay réplica independiente del bloque.
2. **El bloque final no es un conjunto virgen:** se consultó durante el Entregable 2 (informe, §3.4.4). Desde el 05/10/2026 ningún
   diagnóstico lo consulta, y la solución se fijó en `1560a5b` antes de este notebook.
3. **El bloque final resultó más fácil para todos los modelos** (§2.1): la mejora final − validación no se atribuye a ningún modelo.
4. **Subestimación persistente:** la solución predice el 96,06 % del total observado; los fallos de los intervalos se concentran por encima.
5. **El modelo exportado usa α por momentos**, en el piso del rango del test (§4.1); NB2 no convergió en la ventana final ni en los cortes
   45 y 47.
6. **La configuración final no es la que eligió la regla de selección** (D42): se apartó de ella con los mismos 47 cortes de validación.
7. **Sin meteorología:** el objetivo 2 no se cumplió en esa dimensión (§6, punto 2; `tablas/19`).
8. **La verificación en el servidor compara modelos, no evalúa:** muestra que el entrenamiento es reproducible con otra implementación
   y otro entorno (§4.3), no dice nada nuevo sobre el desempeño.
9. **Cada reejecución reescribe `commit_base` y `fecha_generacion` de `metadata.json`** (registran el HEAD y la hora de generación). Son el
   **único diff aceptado en `models/`** (D61): la comprobación es `modelo_final.json` idéntico y `metadata.json` igual salvo esos dos campos.
10. **El log del servidor no identifica la versión del script que corrió** (no trae su sha256 ni su commit). La evidencia es indirecta: el log
    imprime la comparación del sha256 del modelo, que solo existe desde `82c0c3a`, y `git log -- train/train_modelo_final.py` no tiene commits
    posteriores.
11. **Los comentarios del script y el docstring de sus tests que citan pandas 1.5.3 son deuda aceptada:** no afectan el cálculo, pero
    contradicen §4.3 y `train/README.md`.
12. **`predicciones_bloque_final.csv` versiona los conteos observados del bloque final** (2025-02-06 a 2025-12-31, por municipio y día). El
    equipo confirmó el 21/10/2026 que versionarlos no viola las restricciones de uso de los datos de UNASEV (D65).

**Frases que NO deben aparecer en el informe:**
- «La solución es significativamente mejor que L1 (o que la sensibilidad)». Las razones media/EE no son pruebas de significación (§2.2).
- «Los intervalos tienen la cobertura nominal» o «los intervalos del 80 % sobrecubren 10 puntos». La comparación pertinente es contra la
  cobertura esperada por el modelo (0,8871 al 80 %), no contra 0,80 (§3.4).
- «El modelo mejoró en el test respecto de validación». Todos los modelos bajaron su desvianza, incluida la media constante (§2.1).
- «El test confirma la elección de la ventana deslizante» o «la deslizante fue elegida por su desempeño en el test». La decisión es D42,
  tomada en validación; el test no la valida retroactivamente ni podía cambiarla (D48).
- «El modelo exportado usa el α de NB2». Usa α por momentos (§4.1).
- «XGBoost sería una alternativa mejor» o cualquier ranking que lo ponga a competir: es contraste y no compite (D48); además gana a L1 en
  22 de 47 cortes.
- «El modelo explica por qué ocurren los siniestros» o causas de las peores semanas: el trabajo es predictivo y los datos no registran qué
  pasó en cada semana (§3).
- Cifras del chequeo en el entorno simulado presentadas como del servidor (§4.2): las del servidor son las del job 136 (§4.3).
- «El servidor confirmó el desempeño del modelo» o «se validó en el servidor»: la corrida del servidor solo verificó que el entrenamiento
  da el mismo modelo (§4.3); no evaluó nada.
- Versiones del contenedor tomadas de `train/README.md` del 18/09 (pandas 1.5.3) para la corrida del 21/10: la corrida usó pandas 2.3.3.
- «El modelo es aplicable a otros departamentos» o a datos de 2026: no se evaluó fuera de Montevideo ni después del 2025-12-31.

---

## 6. Diferencias con el informe

Puntos donde lo ejecutado difiere de la metodología o de los objetivos del informe vigente
(`documentacion/informe/Informe_PAA_Actualizado_el_12-10-26.md`, capítulos 1 y 3). **No se resuelven en el código ni en el informe:** se
alinean en la fase 6 (D49).

| N.º | Sección del informe | Qué dice el informe | Qué se hizo | Por qué |
| --- | --- | --- | --- | --- |
| 1 | §3.4.3 (Validación interna) y Cuadro 3, fila «Estimar parámetros con información futura» | «Sobre el bloque final, el ajuste queda congelado en el bloque de desarrollo»: solo avanza la historia que cada modelo usa como entrada | En cada uno de los 47 cortes del bloque final, cada modelo se **reentrena** con todo lo observado antes del origen y su ventana (D48, D52 ítem 1) | Es el procedimiento de la validación del E3 (reentrenamiento cada 7 días, `solucion_seleccionada.json`: `reentrenamiento_cada_dias` 7) y el del uso previsto. La frase del informe describe el protocolo del E2 |
| 2 | §1.2.2, objetivo 2; §1.3 (Alcance); §1.4, limitación «Variables meteorológicas observadas» | El objetivo 2 compara estrategias «con y sin variables exógenas»; el alcance dice que las variables explicativas comprenden el calendario, **las condiciones meteorológicas diarias** y la historia de cada municipio; §1.4 declara la cota optimista de usar meteorología observada | El E3 **no evaluó variables meteorológicas**: el conjunto (d) (lluvia) se retiró antes de ejecutar (14/10/2026). Las exógenas evaluadas son solo de calendario; la limitación de §1.4 describe una variable que la solución no usa | La lluvia del día a predecir no está disponible con horizonte de 7 días (solo un pronóstico) y el diagnóstico no le encontró aporte fuera de muestra (`resumen_diagnostico_municipios.md` §7.5) |
| 3 | §3.4.5 y Cuadro 4 | L0 = promedio de las últimas **cuatro** semanas; «la cantidad de semanas se fijó antes de ejecutar y no se ajustó» | L0 de **8 semanas** | D17: elegida mirando los 47 cortes de validación (`resumen_modelos_candidatos.md` §1.1) |
| 4 | §3.4.2 (Calendario) y §3.4.5 (L1) | Calendario de **tres niveles**; L1 usa los tres niveles | Calendario de **8 niveles** (lunes a domingo + feriado) en L1 y en los candidatos | Sección 1 de `modelos_candidatos` (la forma del diagnóstico, M2) |
| 5 | Tabla 1 y §3.4.3 | Validación por origen móvil con **ventana expansiva** | La solución usa **ventana deslizante de 364 días**; la expansiva queda como sensibilidad | D42, decisión del equipo apartándose de la regla de selección |
| 6 | §3.4.5 y Cuadro 4 (modelos evaluados); Cuadro 3, fila «Realimentar predicciones» | Modelos aprendidos: árbol A (recursivo) y árbol B | Candidatos del E3: GLM Poisson, NB2 y XGBoost; el árbol se retiró antes de ejecutar; ningún modelo de la fase 4 es recursivo | Sección 1 de `modelos_candidatos`: el árbol no extrapoló la tendencia en el E2 |
| 7 | §3.4.5, Cuadro 4 (referencias) | Referencias evaluadas en validación y bloque final: media constante, **repetir la semana anterior**, L0, L1 y **media móvil de 56 días por calendario** (esta, solo en validación) | En el bloque final del E3 las referencias son **media constante, L0 (8 semanas) y L1** | D48 fijó el conjunto de referencias de la evaluación final antes de leer el bloque |
| 8 | §1.2.2, objetivo 3 | «Seleccionar el modelo con mejor desempeño y solidez» | La configuración final no es la que eligió la regla de selección (D42); el estado del objetivo se fijó antes de leer el bloque final como «cumplido en el procedimiento, con la salvedad de D42» (`tablas/19`) | D42: el equipo se apartó de la regla con los mismos 47 cortes de validación; ninguna diferencia de validación superaba 1 EE |
| 9 | §3.4.6 (Entorno de ejecución) | Entorno único: Python 3.13.15, con skforecast 0.25.0 y diecisiete dependencias directas | La fase 4 corrió con **Python 3.13.2** y **18 dependencias directas** de `requirements.txt` (entre ellas xgboost 3.4.1), verificadas por la celda 3 (`tablas/00_entorno.csv`) | `requirements.txt` vigente del E3; el informe describe el entorno al 20/09/2026 |
| 10 | §3.4.6, último párrafo; Anexo F.1 | El entrenamiento verificado en el servidor corre en un contenedor propio (Python 3.10.12, pandas 1.5.3, scikit-learn 1.2.0) y «las cifras de este informe provienen de las corridas locales»; el Anexo F.1 documenta solo `train_base.py` (modelo base, Municipio C) | La corrida del servidor del E3 es `train/train_modelo_final.py` (job 136, 21/10/2026), con **otra implementación** que la local: IRLS en numpy en lugar de statsmodels, α por momentos (sin NB2 por MV) y calendario constante. Coincidió con la exportación local con diferencia relativa máxima de 4,25e-12 en coeficientes, 3,42e-12 en μ de las 56 filas y 5,26e-13 en α (criterio ≤ 1e-6: CUMPLE). El contenedor tenía Python 3.10.12, numpy 1.26.4, pandas 2.3.3 y scikit-learn 1.7.2, no las versiones que cita el informe. Las cifras siguen saliendo de las corridas locales | D56: el contenedor no tiene statsmodels ni `holidays`. Fuente: `documentacion/logs/log_servidor_modelo_final.txt` y `documentacion/logs/servidor_modelo_final/resumen_corrida.json` (§4.3) |

`models/historia_reciente.csv` quedó fuera del alcance (D51); el informe no lo menciona, así que no figura en esta tabla.

### 6.1 Cumplimiento de los objetivos específicos (`tablas/19_cumplimiento_objetivos.csv`)

Estados fijados antes de leer el bloque final (D52, ítem 8); las cifras del bloque final se agregan como evidencia, sin cambiar el estado.

| Objetivo (1.2.2) | Estado | Evidencia | Lo que no se cumplió |
| --- | --- | --- | --- |
| 1. Adaptar el ETL del PID | Cumplido (Entregable 2) | `preparacion_montevideo.ipynb`, 16 verificaciones automáticas; clima cacheado en `data/raw/clima_montevideo.csv` | — |
| 2. Evaluar y comparar estrategias (con y sin exógenas; expansiva y deslizante) | Cumplido en calendario y ventanas; **no cumplido en meteorología** | Validación: conjuntos (0) sin exógenas y (a)–(c) con calendario (`modelos_candidatos/tablas/11`); ventanas expansiva, 364, 546 y 728 d (`modelos_candidatos/tablas/26`). Bloque final: solución (364 d) 1,1063; sensibilidad (expansiva) 1,1329; solución − sensibilidad −0,0265 (EE 0,0067; 33 de 47); L0 1,2432; L1 1,1359 | La meteorología no se evaluó: conjunto (d) retirado antes de ejecutar |
| 3. Seleccionar el modelo con mejor desempeño y solidez | Cumplido en el procedimiento, **con la salvedad de D42** | Selección fijada antes del bloque final (`1560a5b`). Bloque final: solución 1,1063 (EE 0,0335); L1 1,1359; media constante 1,3152; solución − L1 −0,0295 (33 de 47); validación 1,2205; pred./obs. 0,9606; cobertura NB2 0,9005 (esperada por el modelo 0,8871) al 80 % y 0,9791 (esperada 0,9810) al 95 % (`tablas/17`) | La configuración final no es la que eligió la regla (D42) |
| 4. Nueva pestaña del dashboard | **No cumplido en esta fase** (fase 5) | Preparado: `src/modelo.py` (`entrenar`, `predecir_semana`, `cargar_modelo`) y `predicciones_bloque_final.csv` para el modo «Histórico» | El código del dashboard del PID no está en este repositorio |

---

## 7. Índice de artefactos

| Artefacto | Respalda |
| --- | --- |
| `tablas/00_entorno.csv` | Versiones del entorno (§6, punto 9) |
| `tablas/01_verificacion_solucion_fijada.csv` | La solución es la de `1560a5b` (§0, ítem 5) |
| `tablas/02_control_validacion.csv` | 35 comprobaciones del procedimiento en validación (§1.4); cobertura de validación (§3.4) |
| `tablas/03_verificacion_panel_completo.csv`, `04_procedencia_panel.csv` | Integridad y sha256 del panel completo (§1.4) |
| `tablas/05_ajustes_por_corte.csv`, `18_alpha_por_corte.csv` | Convergencia; origen y valor de α por corte (§1.4, §4.1) |
| `tablas/06_globales.csv` | Métricas globales y comparaciones (§2.1) |
| `tablas/07_por_municipio.csv`, `10_errores_por_municipio.csv` | Por municipio (§2.3, §3.1) |
| `tablas/08_por_corte.csv`, `figuras/fig1_desvianza_por_corte.png` | Por semana (§2.4) |
| `tablas/09_pareado.csv` | Diferencias pareadas, descriptivas (§2.2) |
| `tablas/11_errores_por_tipo_dia.csv` | Por tipo de día (§3.1) |
| `tablas/12_semanas_mayor_desvianza.csv`, `13_semanas_mayor_desvianza_dias.csv` | Cinco peores semanas (§3.2) |
| `tablas/14_calibracion_deciles.csv`, `15_residuos_por_corte.csv`, `16_tendencia_residuos.csv`, `figuras/fig4_calibracion_y_residuos.png` | Calibración y tendencia (§3.3) |
| `tablas/17_cobertura_intervalos.csv`, `figuras/fig5_cobertura_intervalos.png` | Cobertura de los intervalos (§3.4) |
| `tablas/19_cumplimiento_objetivos.csv` | Objetivos (§6.1) |
| `tablas/20_artefactos.csv` | Índice (27 filas; §1.6) |
| `figuras/fig2_desvianza_por_municipio.png`, `fig3_total_semanal.png` | Figuras de §2.3 y del total semanal |
| `predicciones_bloque_final.csv` | 15.792 filas (6 modelos × 2.632); modo «Histórico» del prototipo |
| `registro_ejecucion.csv` | Métricas de la primera ejecución (2026-10-20T19:28:50, `86630a3`) y `arbol_limpio = False` (§1.6) |
| `models/modelo_final.json`, `models/metadata.json` | Modelo final y su metadata (§4.1) |
| `documentacion/logs/log_servidor_modelo_final.txt` | Corrida del servidor, job 136 (§4.3; §6, punto 10) |
| `documentacion/logs/log_servidor_modelo_final_intento1_job135.txt` | Primer intento, job 135 (§4.3) |
| `documentacion/logs/servidor_modelo_final/` | Salidas del job 136: `resumen_corrida.json`, `run_info_1.txt`, `prediccion_semana_2026-01-01.csv`, `modelo_final_servidor.json`, `.sbatch` (§4.3) |

Rutas relativas a `experiments/evaluacion_final/`, salvo `models/` y `documentacion/logs/`.

## 8. Qué queda pendiente

- Review de la fase 4.
- Fase 5: prototipo (pestaña del dashboard; modo «Histórico» con `predicciones_bloque_final.csv`; predicción con `cargar_modelo`).
- Fase 6: alinear el informe con §6 (D49).
