# Resumen del modelo base simplificado — MUNICIPIO C

**Notebook:** [`notebooks/base_2.ipynb`](../notebooks/base_2.ipynb)
**Artefactos:** `experiments/base_2/` (8 tablas CSV, 4 figuras PNG)
**Entrada:** `data/processed/panel_zona_top.csv`, del que se leen **solo** `fecha`, `zona_id` y
`n_siniestros`. El notebook no escribe nada en `data/processed/`.
**Fecha de ejecución:** 2026-09-15 (`tablas/00_entorno.csv`)
**Alcance:** una única serie diaria, **MUNICIPIO C** (el municipio con más siniestros
registrados), del 2021-07-01 al 2025-12-31 (1.645 días). **Sin variables exógenas.**
**Métrica principal:** desvianza de Poisson media.

---

## 0. Cómo usar este documento

Este archivo es **contexto autocontenido** para redactar las secciones *Metodología — diseño
de evaluación*, *Línea base* y los *resultados preliminares* del informe (guía PAA 6.2) sin
abrir el repositorio. Quien lo lea no puede ejecutar el notebook: todo lo que hace falta está
escrito acá, con el artefacto que respalda cada cifra.

**Reglas que quien redacte debe respetar:**

1. **Ninguna cifra sin artefacto.** Los números salen de la ejecución del 2026-09-15 y llevan al
   lado la tabla que los respalda (`tablas/NN_nombre.csv`). Si hace falta un número que no está
   acá, se marca como `<!-- PENDIENTE: ... -->`.
2. **Distinguir evidencia de inferencia.** «Los resultados muestran X» y «el equipo concluye Y»
   son afirmaciones distintas; este documento las marca por separado.
3. **No escribir Introducción ni Marco teórico** a partir de este documento.
4. **Respetar los límites de la sección 7**, incluida la lista de frases que no deben aparecer.

**Documentos hermanos:**
[`resumen_diagnostico_datos_municipio.md`](resumen_diagnostico_datos_municipio.md) (estructura
temporal de esta misma serie; de ahí salen los rezagos y la decisión de no transformar),
[`resumen_base.md`](resumen_base.md) (versión técnica, **con** variables de calendario),
[`resumen_diagnostico_datos.md`](resumen_diagnostico_datos.md) (calidad y adecuación de los ocho
municipios) y [`resumen_preparacion_montevideo.md`](resumen_preparacion_montevideo.md) (ETL).

> ### ⚠️ Versión del 2026-09-15: reemplaza a la del 2026-09-14
>
> Cambiaron la línea base, los rezagos del árbol, la **métrica principal** (ahora desvianza de
> Poisson, antes MAE) y la numeración de tablas y figuras. **Ninguna cifra de modelo de la versión
> anterior sigue vigente** (sección 1.4). Una tabla con nombre viejo, como `08_test_metricas.csv`,
> es de la versión anterior y no se cita.

> ### ⚠️ Una sola serie, a propósito
>
> `panel_zona_top.csv` es la serie de **un** municipio. El notebook fija el procedimiento de
> evaluación y la línea base sobre un caso simple. **Sus métricas no son las del proyecto** y
> no permiten afirmar que un modelo «generaliza».

> ### ⚠️ Las lecturas del notebook las redactó Claude
>
> El código base es del equipo. La línea base, la evaluación sobre todo el test, las métricas, los
> artefactos y **todas las celdas de lectura y conclusiones** se hicieron con Claude Code
> (`registro_uso_IA.md`, sesiones 2026-09-14 y 2026-09-15). **El equipo tiene que leerlas y
> validarlas antes de citarlas.**

---

## 1. Qué hace el notebook y por qué

### 1.1 Relación con los otros notebooks

- **`diagnostico_datos_municipio.ipynb`** analiza la estructura temporal de la misma serie:
  tendencia, patrón semanal, ACF/PACF y transformaciones. `base_2` **no repite ese análisis**. Su
  sección 2 es solo texto y cita las tablas del diagnóstico que usa el modelo (sección 3 de este
  documento).
- **`base.ipynb`** es la versión técnica. Comparte partición, procedimiento de evaluación y
  cálculo de la desvianza de Poisson, pero **usa variables de calendario**, así que sus modelos no
  son comparables con los de `base_2`. El único modelo común es la media constante, que sirve de
  control cruzado (sección 5.4).

| Aspecto | `base.ipynb` | `base_2.ipynb` |
| --- | --- | --- |
| Partición | 80 / 20 cronológica | **Igual** (mismas fechas) |
| Evaluación en test | 47 cortes de 7 días, ajuste congelado | **Igual** |
| Métrica principal | Desvianza de Poisson media (predicciones recortadas a 10⁻⁶) | **Igual** |
| Métricas secundarias | MAE, RMSE, razón total, sesgo medio | MAE, RMSE, total predicho / observado |
| Variables exógenas | **Sí**: calendario (fin de semana, feriado) y tendencia | **No** |
| Línea base | Tasa × calendario (usa `tipo_dia`) | **Promedio de las últimas 4 semanas** (solo la serie) |
| Modelo aprendido | Árbol `max_depth=4`, `min_samples_leaf=20`; rezagos 7/14/21 más calendario y tendencia; sin recursión | Árbol `max_depth=15`; rezagos 1/7/14/21; **recursivo**; sin exógenas |
| Validación interna | Ventana deslizante, 47 cortes | **No hay**: no se selecciona ningún hiperparámetro |
| Implementación | Backtesting escrito a mano | `skforecast` (`ForecasterRecursive`) y un bucle semanal |

### 1.2 Secciones del notebook

| § | Qué hace | Por qué |
| --- | --- | --- |
| 0 | Instala `skforecast==0.25.0` y registra versiones | `skforecast` no está en `requirements.txt` |
| 1 | Carga **solo** fecha, municipio y `n_siniestros`, con formato de fecha explícito | Así ningún modelo puede usar `tipo_dia` ni el clima por error. Sin formato explícito, `01/07/2021` puede leerse como 7 de enero |
| 2 | Tabla con los resultados del diagnóstico que usa el modelo (sin código) | No repetir el análisis exploratorio |
| 3 | Partición cronológica 80 / 20 | En series temporales se entrena con el pasado y se evalúa sobre el futuro |
| 4 | Árbol de decisión con `skforecast`, `lags=[1, 7, 14, 21]`, `max_depth=15`; imprime sus variables y el tamaño del árbol | Primer modelo aprendido, con la configuración del equipo |
| 5 | Tres referencias sin exógenas; la línea base es el promedio de las últimas 4 semanas | Un modelo solo vale si mejora algo simple |
| 6 | Define las métricas y compara en la primera semana de prueba | Mirada inicial; muestra por qué no alcanza |
| 7 | Comparación en las 47 semanas de prueba, días con predicción 0 y control cruzado con `base.ipynb` | Evaluación válida |
| 8 | Conclusiones, separando evidencia de inferencia | — |

### 1.3 Decisiones tomadas, con su motivo

| Decisión | Motivo |
| --- | --- |
| **Ningún modelo usa variables exógenas** | Decisión del equipo para esta entrega: medir primero lo que da la serie sola. El calendario y el clima quedan para una etapa posterior |
| **Se leen solo tres columnas del CSV** (`usecols`) | Garantiza que `tipo_dia` y el clima no estén disponibles. El notebook imprime las variables del árbol (`lag_1`, `lag_7`, `lag_14`, `lag_21`) y `exog_in_ = False` |
| **Sin análisis exploratorio propio**; se citan las tablas de `diagnostico_datos_municipio` | Es la misma serie: recalcularlo repetía el diagnóstico |
| **Rezagos `[1, 7, 14, 21]`** | Los fijó el equipo. Coinciden con rezagos que la ACF del diagnóstico muestra fuera de la banda de azar. Sin calendario, el patrón semanal solo puede entrar por rezagos múltiplos de 7 |
| **Se mantiene `max_depth=15`** | Es la configuración del equipo. Cambiarla mirando el test sería una fuga; elegirla con validación es trabajo del Entregable 3 |
| **Línea base = promedio de lo observado 7, 14, 21 y 28 días antes**, fijada **antes de ejecutar** | (1) usa solo la serie, igual que el árbol; (2) recoge el patrón semanal del diagnóstico: un viernes se predice con viernes; (3) promediar cuatro semanas amortigua el ruido de copiar una sola; (4) avanza con el tiempo y sigue los cambios de nivel. El 4 no se ajustó: es aproximadamente un mes |
| **Referencias adicionales: media constante y repetir semana anterior** | La primera es el piso; la segunda, la referencia estacional más habitual |
| **Evaluación semana a semana sobre todo el test, sin reentrenar** | 7 días no alcanzan; sin reentrenar se simula un modelo puesto en uso el 2025-02-06 |
| **Desvianza de Poisson media como métrica principal** (decisión del equipo) | Es la métrica para comparar y seleccionar modelos: adecuada para conteos, pondera el error según el nivel esperado. Es también la principal de `base.ipynb` |
| **Para la desvianza, las predicciones iguales a 0 se reemplazan por 10⁻⁶** (`EPS = 1e-6`) | La desvianza de Poisson no admite predicciones de 0. Se usa el mismo valor que `base.ipynb`, para que las cifras sean comparables. MAE, RMSE y total se calculan sobre las predicciones sin tocar |
| **Se registran los días con predicción 0** (columna en `05_test_metricas` y celda con los días del árbol) | Esos días explican los valores altos de desvianza: sin mostrarlos, la cifra no se puede interpretar |
| **MAE, RMSE y total predicho / observado como secundarias** | El MAE se explica fácil («siniestros de diferencia por día»); el total muestra si un modelo predice de menos |
| **La variabilidad semanal y la figura 4 usan la desvianza** | Es la métrica principal |
| **Métricas sobre predicciones sin redondear** | Redondear esconde diferencias |
| **`n_siniestros` sin diferenciar ni transformar** | El diagnóstico lo desaconseja (sección 3) |
| **Control cruzado solo con la media constante**, en desvianza y MAE | Es el único modelo igual en los dos notebooks |
| **Código simple, con la estructura original** | Pedido del equipo: se cambiaron las celdas existentes y se agregó una sola celda de una línea |

### 1.4 Cambios respecto a la versión del 2026-09-14: cifras superadas

La versión anterior está en el commit `6fbb3ca` (notebook y 22 artefactos). **Sus cifras de
modelos no deben citarse.**

| Versión anterior (`6fbb3ca`) | Versión actual | Por qué cambió |
| --- | --- | --- |
| **Métrica principal MAE**; sin desvianza de Poisson | **Desvianza de Poisson media** principal; MAE, RMSE y total como secundarias | Decisión del equipo sobre las métricas de evaluación |
| Línea base «promedio por tipo de día», que **usaba `tipo_dia`**: MAE 1,592 en test | Promedio de las últimas 4 semanas: desvianza **1,332**, MAE **1,755** | No se usan variables exógenas |
| Árbol con `lags=7` (rezagos 1 a 7): MAE 2,206; 527 hojas para 1.309 filas | `lags=[1, 7, 14, 21]`: desvianza **3,462**, MAE **2,137**; 716 hojas para 1.295 filas | El equipo cambió los rezagos en su copia local antes de esta sesión (sin ejecutar); se respetó |
| §2 serie completa, §4 descomposición y patrón semanal, §5 ACF y PACF sobre entrenamiento (tablas `02`, `02b`, `03`; figuras `fig1`, `fig3`–`fig6`) | Eliminadas; la §2 cita las tablas del diagnóstico | Repetían `diagnostico_datos_municipio.ipynb` |
| Tabla `05_linea_base` y figura `fig7_linea_base` (promedios por tipo de día) | Eliminadas | La línea base nueva no calcula promedios por tipo de día |
| MAE semanal en la variabilidad y en `fig10_test_mae_semanal` | Desvianza semanal en `07_test_variabilidad_semanal` y `fig4_test_desvianza_semanal` | Métrica principal |
| Control cruzado de línea base y media constante con `base.ipynb`, solo en MAE | Solo media constante, en desvianza y MAE | La línea base de `base.ipynb` usa calendario |
| 12 tablas (`00`–`10`) y 10 figuras (`fig1`–`fig10`) | 8 tablas (`00`–`07`) y 4 figuras (`fig1`–`fig4`), renumeradas | Se borraron las anteriores antes de ejecutar |

**Sin cambios** entre versiones, como era de esperar porque su cálculo es el mismo: la partición,
el MAE de la media constante (1,741) y el de repetir semana anterior (2,228). Es un control de que
el procedimiento de evaluación no se alteró.

**Un costo de sacar la exploración.** La versión anterior calculaba la ACF **solo con
entrenamiento** (rezago 1: 0,056, tabla `03_autocorrelacion` en `6fbb3ca`). El diagnóstico la
calcula con la serie completa (rezago 1: 0,0785). Apoyar los rezagos en el diagnóstico es una
fuga de información leve, declarada en la sección 4.4.

---

## 2. Datos de entrada

`data/processed/panel_zona_top.csv`, exportado por el ETL (`resumen_preparacion_montevideo.md`).
Una fila por día de MUNICIPIO C. Objetivo: `n_siniestros`. El archivo trae además `tipo_dia` y
columnas de clima, que **no se cargan**.

**Integridad (salidas del notebook, §1):** 1.645 días del 2021-07-01 al 2025-12-31; 1.644
diferencias entre fechas consecutivas, todas de 1 día (**sin huecos**); ninguna de las columnas
cargadas tiene nulos.

**Coincidencia con el diagnóstico** (verificada en la sesión del 2026-09-15 con un script aparte,
no dentro del notebook): 1.645 días, 5.783 siniestros, 79 días en cero, máximo 13 y media 3,5155.
Son los mismos valores de `experiments/diagnostico_datos_municipio/tablas/04_resumen_serie_municipio_c.csv`,
aunque el diagnóstico arma su serie desde los datos crudos y no desde el ETL.

> **Procedencia del archivo.** El 2026-09-14 el CSV apareció sobrescrito con formato de Excel y se
> **restauró desde `panel_diario_montevideo.csv`** (salida del ETL del 2026-09-07), con contenido
> verificado idéntico. Consta en `registro_uso_IA.md`, sesión 2026-09-14 (tarde).

---

## 3. Lo que el modelo toma del diagnóstico

Tablas en `experiments/diagnostico_datos_municipio/tablas/`. Detalle en
`resumen_diagnostico_datos_municipio.md`.

| Resultado del diagnóstico | Tabla | Qué implica en `base_2` |
| --- | --- | --- |
| Patrón semanal claro: viernes 4,268 siniestros de promedio, domingo 2,038 | `06_perfil_semanal` | Es la estructura principal. Sin calendario, solo se capta con días de semanas anteriores |
| ACF fuera de la banda de azar (±0,0483) en los rezagos 1 (0,0785), 7 (0,0764), 14 (0,1706), 21 (0,1099) y 28 (0,1125); apenas, también en 15 (0,0545) y 29 (0,0682) | `08_acf_pacf_crudo` | Rezagos del árbol: 1, 7, 14, 21. Línea base: 7, 14, 21, 28 |
| Descontado el calendario, el rezago 1 sigue fuera de la banda (0,0745); los rezagos 7, 21 y 28 quedan dentro (−0,0329; −0,0035; −0,0029) | `09_acf_residuo_calendario` | El rezago de 1 día trae algo propio; los de 7, 21 y 28 días traen sobre todo el patrón semanal |
| Todas las autocorrelaciones son débiles: máximo 0,1706 | `08_acf_pacf_crudo` | Se espera poca ganancia de los rezagos |
| No conviene diferenciar ni transformar: diferenciar (d=1) lleva la ACF a 1 día a −0,4621; el λ de Box-Cox es 0,4733 | `12_estacionariedad_adf_kpss`, `13_efecto_diferenciacion`, `14_diagnostico_transformacion` | Se predice `n_siniestros` tal cual, y se evalúa con una métrica de conteo |
| El nivel cambia entre años: 3,3288 siniestros por día en 2023 y 3,7562 en 2025 | `05_tendencia_anual` | Los modelos de nivel fijo van a predecir de menos en el test |

*Nota:* el rezago 28 está fuera de banda pero el árbol no lo usa; es parte de la configuración que
fijó el equipo.

---

## 4. Procedimiento de evaluación

### 4.1 Partición — `tablas/01_particion.csv`, `figuras/fig1_particion.png`

| Conjunto | Desde | Hasta | Días | % | Promedio de siniestros por día |
| --- | --- | --- | --- | --- | --- |
| Entrenamiento | 2021-07-01 | 2025-02-05 | 1.316 | 80,0 % | **3,426** |
| **Prueba (reservada)** | **2025-02-06** | **2025-12-31** | **329** | **20,0 %** | **3,875** |

*Evidencia:* la prueba promedia un 13,1 % más de siniestros por día que el entrenamiento (3,875 /
3,426, calculado de `01_particion`). El promedio de prueba es **descriptivo**: no interviene en
ningún ajuste.

### 4.2 Evaluación en el test (§7)

Se parte del primer día de prueba. Cada modelo predice los 7 días siguientes con lo observado
hasta ese momento; se avanza 7 días y se repite. Resultan **47 semanas** que cubren los 329 días.
**Ningún modelo se reentrena.** Lo único que avanza es la información reciente: los 21 días
observados que el árbol usa como entrada (su ventana, por el rezago de 21 días) y las semanas
anteriores que usan las referencias.

### 4.3 Métricas

| Métrica | Rol | Cómo se lee |
| --- | --- | --- |
| **Desvianza de Poisson media** | **Principal**: comparar y seleccionar modelos | Error pensado para conteos: pondera según el nivel esperado (equivocarse por 1 cuando se esperaba 0,5 pesa más que cuando se esperaba 5) y castiga más predecir de menos que de más. 0 = perfecto; menor es mejor |
| MAE | Secundaria, lectura operativa | Siniestros de diferencia por día, en promedio. Menor es mejor |
| RMSE | Secundaria | Como el MAE, pero castiga más los errores grandes |
| Total predicho / observado | Secundaria, volumen | 1 = acierta el volumen total; < 1 = predice de menos |

**Predicciones iguales a 0.** La desvianza de Poisson no está definida para una predicción de 0.
Para calcularla, esas predicciones se reemplazan por **10⁻⁶**, el mismo valor que usa `base.ipynb`
(`EPS = 1e-6`). Si ese día hubo siniestros, el aporte de ese día a la desvianza es muy grande, y
**su tamaño depende del valor elegido**. Las demás métricas se calculan sobre las predicciones
originales. En este notebook predicen 0 el árbol (7 días) y repetir semana anterior (10 días); la
media constante y la línea base, nunca (`05_test_metricas`).

Todas las métricas se calculan sobre predicciones **sin redondear**.

### 4.4 Medidas contra la fuga de información

1. La media constante y el árbol se ajustan **solo con entrenamiento**. La línea base y «repetir
   semana anterior» no tienen parámetros: solo usan valores ya observados.
2. En el test ningún modelo se reentrena. El árbol recibe como entrada solo días **ya observados**
   antes de cada semana; dentro de la semana usa sus propias predicciones para el rezago de 1 día
   (recursión). Los rezagos de 7, 14 y 21 días siempre caen antes de la semana.
3. La línea base usa los valores de 7, 14, 21 y 28 días antes. Para cualquier día de una semana
   de 7, los cuatro caen antes de la semana: siempre están observados.
4. `tipo_dia` y el clima **no se cargan**.
5. `max_depth=15` y los rezagos **no se eligieron mirando el test**, y la línea base se fijó antes
   de la primera ejecución.
6. ⚠️ **Fuga leve, declarada:** los rezagos se apoyan en la ACF del diagnóstico, que usa la serie
   completa, **incluido el período de prueba**. Ningún valor se ajusta con el test, pero la
   elección no se hizo solo con entrenamiento.

---

## 5. Resultados

### 5.1 El árbol de decisión — `tablas/02_tamano_arbol.csv`

Variables con que se entrenó (salida del notebook, §4): `lag_1`, `lag_7`, `lag_14`, `lag_21`.
Variables exógenas: ninguna (`exog_in_ = False`).

| Indicador | Valor |
| --- | --- |
| Filas de entrenamiento | 1.295 (1.316 días menos los 21 primeros, que no tienen el rezago de 21 días) |
| Profundidad | 15 |
| **Hojas** | **716** |
| Filas por hoja (promedio) | **1,81** |

*Evidencia:* casi una hoja cada día y medio de entrenamiento. *Inferencia:* el árbol memoriza
días concretos en lugar de aprender reglas generales.

### 5.2 Primera semana de prueba — `tablas/03_primera_semana_predicciones.csv`, `tablas/04_primera_semana_metricas.csv`, `figuras/fig2_primera_semana.png`

2025-02-06 (jueves) a 2025-02-12. Valores reales: 6, 4, 1, 1, 2, 2, 2 (18 siniestros). Ordenado
por desvianza.

| Modelo | Desvianza de Poisson | MAE | RMSE | Total predicho / observado |
| --- | --- | --- | --- | --- |
| **Árbol de decisión** | **0,957** | 1,565 | 1,802 | 1,387 |
| Promedio de las últimas 4 semanas (línea base) | 1,166 | **1,286** | 1,813 | **1,028** |
| Media constante | 1,220 | 1,754 | 1,883 | 1,332 |
| Repetir semana anterior | 8,963 | 1,714 | 2,204 | 1,111 |

- *Evidencia:* con la desvianza el árbol es el mejor de la semana; con el MAE, la línea base. Las
  dos métricas no ordenan igual a los modelos.
- *Evidencia:* el mayor error del árbol es el primer día: predijo 9 y hubo 6. Ese día la línea
  base predijo 2 (`03_…`).
- *Evidencia:* repetir semana anterior predijo 0 el martes 2025-02-11, cuando hubo 2 (`03_…`), y
  tiene una desvianza de 8,963.
- *Evidencia:* la línea base predice 18,5 siniestros en la semana, contra 18 observados (suma de su
  columna en `03_…`).
- *Inferencia:* la desvianza castiga más quedarse corto (predecir 2 cuando hubo 6) que pasarse
  (predecir 9), y castiga muchísimo predecir 0 cuando hay siniestros. Eso explica el orden distinto
  al del MAE.
- *Inferencia:* una semana es demasiado poco para evaluar. Esta además resultó baja.

### 5.3 Todo el conjunto de prueba — `tablas/05_test_metricas.csv`

47 semanas, 329 días. Ordenado por desvianza.

| Modelo | Desvianza de Poisson | vs línea base | MAE | vs línea base | RMSE | Total predicho / observado | Días con predicción 0 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Media constante | **1,262** | **−5,2 %** | **1,741** | −0,8 % | **2,120** | 0,884 | 0 |
| **Promedio de las últimas 4 semanas (línea base)** | 1,332 | — | 1,755 | — | 2,179 | **0,981** | 0 |
| Árbol de decisión | 3,462 | +159,9 % | 2,137 | +21,8 % | 2,738 | 0,967 | 7 |
| Repetir semana anterior | 5,007 | +275,8 % | 2,228 | +27,0 % | 2,866 | 0,996 | 10 |

**Variabilidad semanal (desvianza) — `tablas/07_test_variabilidad_semanal.csv`, `figuras/fig4_test_desvianza_semanal.png`**

| Modelo | Desvianza semanal mínima | Mediana | Máxima | Semanas con menor desvianza que la línea base |
| --- | --- | --- | --- | --- |
| Promedio de las últimas 4 semanas (línea base) | 0,473 | 1,209 | 2,516 | — |
| Media constante | 0,318 | 1,147 | 2,388 | **29 de 47** |
| Árbol de decisión | 0,551 | 2,158 | 19,339 | 8 de 47 |
| Repetir semana anterior | 0,322 | 2,417 | 34,962 | 6 de 47 |

**Días en que el árbol predijo 0** (salida de la celda de §7, después de `05_test_metricas`):

| Fecha | Semana | Siniestros observados |
| --- | --- | --- |
| 2025-02-16 | 2 | 0 |
| 2025-02-27 | 4 | 4 |
| 2025-06-22 | 20 | 4 |
| 2025-07-24 | 25 | 2 |
| 2025-08-03 | 26 | 3 |
| 2025-08-31 | 30 | 0 |
| 2025-09-07 | 31 | 4 |

**Semanas con desvianza alta del árbol — `tablas/06_test_semanal.csv`**

| Semana | Inicio | Desvianza del árbol | Desvianza de la línea base | ¿Contiene un día con predicción 0 y siniestros? |
| --- | --- | --- | --- | --- |
| 4 | 2025-02-27 | 17,55 | 0,67 | Sí (2025-02-27) |
| 20 | 2025-06-19 | **19,34** | 1,56 | Sí (2025-06-22) |
| 25 | 2025-07-24 | 9,64 | 1,09 | Sí (2025-07-24) |
| 26 | 2025-07-31 | 13,97 | 0,94 | Sí (2025-08-03) |
| 31 | 2025-09-04 | 16,73 | 0,69 | Sí (2025-09-07) |

**Totales semanales — `tablas/06_test_semanal.csv`, `figuras/fig3_test_totales_semanales.png`**

| Semana (inicio) | Observado | Árbol | Línea base | Nota |
| --- | --- | --- | --- | --- |
| 2025-02-20 | 29 | 24,333 | **17,25** | Predicción semanal más baja de la línea base |
| 2025-06-26 | 20 | 36,967 | 29,0 | El árbol predice mucho de más |
| 2025-07-31 | 29 | 15,0 | 27,5 | El árbol predice mucho de menos |
| 2025-10-09 | 31 | **41,607** | **32,5** | Predicción semanal más alta del árbol y de la línea base |
| 2025-12-11 | **42** | 20,011 | 27,0 | Semana con más siniestros del test |

La media constante predice 23,979 siniestros todas las semanas (`06_test_semanal`).

**Lectura:**

- *Evidencia:* con la métrica principal, la media constante tiene la menor desvianza, un 5,2 % por
  debajo de la línea base (1,262 contra 1,332), y le gana en 29 de 47 semanas. En MAE la
  diferencia es de 0,8 %.
- *Evidencia:* la línea base predice el 98,1 % del total observado; la media constante, el 88,4 %.
  Ese 88,4 % coincide con la razón entre el promedio de entrenamiento y el de prueba (3,426 /
  3,875).
- *Evidencia:* el árbol tiene una desvianza 159,9 % mayor que la de la línea base y la supera en 8
  de 47 semanas.
- *Evidencia:* el árbol predijo 0 en 7 días; en 5 hubo siniestros. Las cinco semanas que contienen
  esos días son las cinco con desvianza del árbol mayor que 9 (tabla de arriba).
- *Evidencia:* en la primera semana el árbol tenía la menor desvianza (0,957); en todo el test
  queda tercero.
- *Inferencia del equipo:* buena parte de la desvianza del árbol viene de esos pocos días con
  predicción 0. Con hojas de 1 o 2 días, el árbol puede copiar un día sin siniestros del pasado.
- *Inferencia del equipo:* la línea base sigue el crecimiento de los siniestros porque su ventana
  avanza, pero promediar solo cuatro valores arrastra ruido, y eso le quita la ventaja frente a la
  media constante.
- *Inferencia del equipo:* el total del árbol cerca de 1 (0,967) se debe a que sus excesos y sus
  faltas se compensan, no a que siga mejor el nivel.
- *Inferencia del equipo:* la línea base **se mantiene**, porque se eligió antes de mirar el test.
  Reemplazarla ahora por la media constante sería elegir con el test. Si se revisa, que sea con
  validación (Entregable 3).

### 5.4 Control cruzado con `base.ipynb`

Salida de la celda de control (§7 del notebook), contra «Media constante» en
`experiments/base/tablas/06_evaluacion_test.csv`:

| Métrica | `base_2.ipynb` | `base.ipynb` | Resultado |
| --- | --- | --- | --- |
| Desvianza de Poisson | 1,2620 | 1,2625 | **OK** |
| MAE | 1,7410 | 1,7411 | **OK** |

La partición, la evaluación semana a semana y el cálculo de las métricas son los mismos en los dos
notebooks. (Las diferencias en el cuarto decimal vienen de que `base_2` redondea a 3 decimales
antes de comparar.)

**Comparación con el árbol de `base.ipynb`** (misma tabla): aquel árbol (`max_depth=4`, rezagos
7/14/21, **con calendario** y tendencia) obtuvo desvianza **1,6789** y MAE **1,9055**; el de este
notebook, **3,462** y **2,137**. Difieren en profundidad, rezagos, recursión y variables exógenas a
la vez: **la diferencia no puede atribuirse a un único factor**, y en particular no mide cuánto
aporta el calendario.

---

## 6. Conclusiones (texto de §8 del notebook, pendiente de validación del equipo)

**Evidencia:** (1) con la desvianza de Poisson media, en todo el test: media constante 1,262, línea
base 1,332, árbol 3,462 y repetir semana anterior 5,007; el árbol no mejora a las referencias
simples; (2) la media constante tiene menos desvianza que la línea base (−5,2 %), pero la línea base
predice el 98,1 % del total y la media constante el 88,4 %; (3) el árbol predijo 0 en 7 días (en 5
hubo siniestros) y tiene 716 hojas para 1.295 filas; (4) evaluar una semana es engañoso (en la
primera, el árbol tenía la menor desvianza); (5) la desvianza y el MAE no siempre ordenan igual.

**Inferencia:** los resultados sugieren que los días anteriores traen poca información para un
árbol, lo que coincide con las autocorrelaciones débiles del diagnóstico (máximo 0,1706). Un árbol
con hojas de uno o dos días puede predecir 0, y la métrica principal lo castiga fuerte; limitar la
profundidad o exigir un mínimo de días por hoja debería evitarlo (hipótesis a probar con
validación). Seguir el nivel reciente mejora el volumen total, pero no la desvianza. Para el
Entregable 3: elegir la profundidad con validación y con la desvianza como criterio, revisar con
validación la ventana de la línea base y recién después sumar variables exógenas.

---

## 7. Limitaciones y lo que NO puede afirmarse

| Limitación | Cómo se trata |
| --- | --- |
| **Una sola serie (MUNICIPIO C).** | Declarar que las cifras fijan el procedimiento, no el desempeño del sistema |
| **Un solo horizonte (7 días).** | Otros horizontes pueden cambiar las conclusiones |
| **`max_depth=15` y rezagos fijados a mano**, sin validación interna. | La selección de hiperparámetros es del Entregable 3 |
| **Rezagos apoyados en un diagnóstico que miró el test** (fuga leve, §4.4). | Declararlo. Al elegir rezagos con validación en el Entregable 3, calcular la ACF solo con entrenamiento |
| **La línea base no es la referencia de menor desvianza en test** (media constante −5,2 %). Su ventana de 4 semanas no se ajustó. | Se mantiene por haberse fijado antes; revisarla con validación, no con el test |
| **La desvianza de los modelos que predicen 0 depende del valor de reemplazo** (10⁻⁶). Con otro valor, la desvianza del árbol y de repetir semana anterior cambia; la de la media constante y la línea base, no. | Se usa el mismo valor que `base.ipynb`. Fijarlo como parte del protocolo del proyecto |
| **Sin variables exógenas.** | Decisión de esta entrega. Los resultados no dicen nada sobre cuánto aportan el calendario o el clima |
| **El crecimiento de los siniestros solo lo sigue la ventana de la línea base.** | La media constante predice el 88,4 % del total; ningún modelo lo trata explícitamente |
| **Entorno inconsistente con `requirements.txt`.** La corrida usó pandas **2.3.3** (`00_entorno`): `skforecast` 0.25 exige pandas < 3, y `requirements.txt` fija 3.0.5 y no incluye `skforecast`. | Decisión pendiente del equipo (`HANDOFF.md`) |
| **Archivo de entrada restaurado** (§2), no regenerado por el ETL. | Contenido verificado idéntico; queda documentado |
| **Sin datos de exposición** (tránsito). | Se modela el conteo registrado, no el riesgo |

### Frases que NO deben aparecer en el informe a partir de este notebook

- ❌ «La línea base es la referencia simple con menor error.» → con la métrica principal la media
  constante es un 5,2 % mejor (1,262 contra 1,332, `05_test_metricas`).
- ❌ «Se eligió como línea base la referencia con mejor desempeño.» → se eligió **antes** de
  ejecutar, con una justificación; no es la de menor desvianza.
- ❌ «El árbol de decisión es el mejor modelo» (por su desvianza de 0,957 en la primera semana). →
  es **una semana**; en todo el test queda tercero, con 3,462.
- ❌ «El árbol de decisión mejora la línea base.» → su desvianza es un **159,9 % mayor**.
- ❌ Citar la desvianza del árbol (3,462) o de repetir semana anterior (5,007) **sin aclarar** que
  depende en buena parte de pocos días con predicción 0 y del valor de reemplazo usado.
- ❌ «El árbol acierta bien el volumen total» (por su 0,967). → sus errores semanales se compensan.
- ❌ «El modelo tiene un error de 1,57 siniestros por día.» → es el MAE de **una semana**. El del
  test completo es **2,137**.
- ❌ «Los rezagos se eligieron sin mirar el conjunto de prueba» o «se eligieron con validación». →
  se apoyan en un diagnóstico que usó la serie completa, test incluido.
- ❌ «Los siniestros de un día dependen de los días anteriores.» → autocorrelación máxima 0,1706;
  lo que más se repite es el patrón semanal.
- ❌ «El calendario (o el clima) no aporta.» → no se usó en este notebook.
- ❌ «Agregar calendario mejora el árbol», a partir de comparar con `base.ipynb` (desvianza 1,6789).
  → los dos árboles difieren en varias cosas a la vez.
- ❌ Cualquier cifra de la versión anterior: línea base 1,592, árbol 2,206, 527 hojas, «+38,6 %».
  → superadas (sección 1.4).
- ❌ «`max_depth=15` es la profundidad óptima.» → se fijó a mano, sin validación.
- ❌ «MUNICIPIO C es el más peligroso.» → es el que más siniestros **registra**.
- ❌ «El modelo generaliza / funciona en Montevideo.» → se evaluó **una sola serie**.

---

## 8. Índice de artefactos

`experiments/base_2/`: **8 tablas y 4 figuras**.

| Artefacto | Qué respalda | § notebook |
| --- | --- | --- |
| `tablas/00_entorno.csv` | Versiones de Python y bibliotecas, fecha de ejecución | 0 |
| `tablas/01_particion.csv` | Fechas, días, % y promedio diario de entrenamiento y prueba | 3 |
| `tablas/02_tamano_arbol.csv` | Filas, profundidad, hojas y filas por hoja del árbol | 4 |
| `tablas/03_primera_semana_predicciones.csv` | Valor real y predicción de cada modelo, primera semana | 6 |
| `tablas/04_primera_semana_metricas.csv` | Desvianza de Poisson, MAE, RMSE y total predicho / observado, primera semana | 6 |
| `tablas/05_test_metricas.csv` | Desvianza, MAE, RMSE y total en las 47 semanas; diferencias contra la línea base; días con predicción 0 | 7 |
| `tablas/06_test_semanal.csv` | Observado, desvianza, MAE y total predicho por semana y modelo | 7 |
| `tablas/07_test_variabilidad_semanal.csv` | Desvianza semanal mínima, mediana y máxima; semanas mejores que la línea base | 7 |
| `figuras/fig1_particion.png` | Entrenamiento y prueba en el tiempo | 3 |
| `figuras/fig2_primera_semana.png` | Últimos 30 días de entrenamiento; real, árbol y línea base en la primera semana | 6 |
| `figuras/fig3_test_totales_semanales.png` | Siniestros por semana en el test: observado, línea base y árbol | 7 |
| `figuras/fig4_test_desvianza_semanal.png` | Desvianza de Poisson de cada semana del test: línea base y árbol | 7 |

Los días en que el árbol predijo 0 no tienen tabla propia: son la salida de la celda
`c-test-ceros` del notebook (§7).

Del diagnóstico se citan, sin regenerarlas: `05_tendencia_anual`, `06_perfil_semanal`,
`08_acf_pacf_crudo`, `09_acf_residuo_calendario`, `12_estacionariedad_adf_kpss`,
`13_efecto_diferenciacion`, `14_diagnostico_transformacion` y `04_resumen_serie_municipio_c`.

**Antes de citar cualquier cifra:** verificar que `data/processed/panel_zona_top.csv` sea la
salida vigente del ETL y que no se haya vuelto a guardar desde Excel. Si el ETL o el diagnóstico se
reejecutan con otro alcance, este notebook y este documento hay que actualizarlos.

---

## 9. Qué queda pendiente

1. **Validar las lecturas y conclusiones** del notebook (redactadas con Claude).
2. **Decidir si se mantiene la línea base** «promedio de las últimas 4 semanas» o se usa la media
   constante. Hacerlo **con validación dentro de entrenamiento** y con la desvianza como criterio,
   no con el test.
3. **Fijar en el protocolo del proyecto el tratamiento de las predicciones 0** para la desvianza
   (hoy 10⁻⁶, igual que `base.ipynb`), y declararlo en el informe.
4. **Decidir qué notebook base se presenta.** Ojo: `base.ipynb` usa variables de calendario; si la
   regla «sin exógenas» vale para toda la entrega, ese notebook no la cumple.
5. **Resolver pandas 3 vs `skforecast`** y dejar `requirements.txt` coherente con la corrida.
6. **Entregable 3**, para el panel de 8 municipios:
   - profundidad (y mínimo de días por hoja) y rezagos elegidos con validación temporal y con la
     desvianza de Poisson como criterio, con la ACF calculada solo con entrenamiento;
   - revisión de la ventana de la línea base con el mismo protocolo;
   - recién después, variables exógenas (calendario, clima; en `skforecast`, como `exog`) para
     medir cuánto agregan sobre la base sin exógenas;
   - métricas desagregadas por municipio y hold-out dejando un municipio afuera por vez.
