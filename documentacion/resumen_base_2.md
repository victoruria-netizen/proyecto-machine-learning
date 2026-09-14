# Resumen del modelo base simplificado — MUNICIPIO C

**Notebook:** [`notebooks/base_2.ipynb`](../notebooks/base_2.ipynb)
**Artefactos:** `experiments/base_2/` (12 tablas CSV, 10 figuras PNG)
**Salida:** ninguna a `data/processed/` (el notebook solo consume `panel_zona_top.csv` del ETL)
**Fecha de ejecución:** 2026-09-14 (`tablas/00_entorno.csv`)
**Alcance:** una única serie diaria — **MUNICIPIO C** (municipio con más siniestros
registrados), 2021-07-01 a 2025-12-31, 1.645 días

---

## 0. Cómo usar este documento

Este archivo es **contexto autocontenido** para redactar las secciones *Metodología — diseño
de evaluación*, *Línea base* y los *resultados preliminares* del informe (guía PAA 6.2) sin
abrir el repositorio. Quien lo lea no puede ejecutar el notebook: todo lo que hace falta está
escrito acá, con el artefacto que respalda cada cifra.

**Reglas que quien redacte debe respetar:**

1. **Ninguna cifra sin artefacto.** Todos los números salen de la ejecución del 2026-09-14 y
   llevan al lado la tabla que los respalda (`tablas/NN_nombre.csv`). Si hace falta un número
   que no está acá, marcarlo como `<!-- PENDIENTE: ... -->`.
2. **Distinguir evidencia de inferencia.** «Los resultados muestran X» y «el equipo concluye
   Y» son afirmaciones distintas; este documento las marca por separado.
3. **No escribir Introducción ni Marco teórico** a partir de este documento.
4. **Respetar los límites de la sección 6**, incluida la lista de frases que no deben aparecer.

**Documentos hermanos:**
[`resumen_base.md`](resumen_base.md) (versión técnica del mismo trabajo, con validación
interna y desvianza de Poisson),
[`resumen_diagnostico_datos.md`](resumen_diagnostico_datos.md) (calidad, adecuación,
justificación de la línea base) y
[`resumen_preparacion_montevideo.md`](resumen_preparacion_montevideo.md) (ETL).

> ### ⚠️ Una sola serie, a propósito
>
> `panel_zona_top.csv` es la serie de **un** municipio. El notebook fija el procedimiento de
> evaluación y la línea base sobre un caso simple. **Sus métricas no son las del proyecto** y
> no permiten afirmar que un modelo «generaliza».

> ### ⚠️ Las lecturas del notebook las redactó Claude
>
> El código base y los gráficos exploratorios son del equipo. La línea base, la evaluación
> sobre todo el test, los artefactos y **todas las celdas de interpretación** se agregaron con
> Claude Code (`registro_uso_IA.md`, sesión 2026-09-14). **El equipo tiene que leerlas y
> validarlas antes de citarlas.**

---

## 1. Qué hace el notebook y por qué

### Relación con `base.ipynb`

`base_2.ipynb` es la **versión simplificada** de `base.ipynb`, hecha por el equipo porque la
primera resultaba demasiado técnica. Comparten partición y línea base, así que **las cifras de
esas dos piezas son las mismas** (verificado dentro del notebook, §4.3 de este documento).

| Aspecto | `base.ipynb` | `base_2.ipynb` |
| --- | --- | --- |
| Partición | 80 / 20 cronológica | **Igual** (mismas fechas) |
| Línea base | Tasa × calendario (media por `tipo_dia`) | **Igual**, llamada «promedio por tipo de día» |
| Evaluación en test | 47 cortes de 7 días, ajuste congelado | **Igual** |
| Validación interna | Ventana deslizante, 47 cortes | **No hay**: no se selecciona ningún hiperparámetro |
| Métrica principal | Desvianza de Poisson | **MAE** (+ RMSE y total predicho / observado) |
| Modelo aprendido | Árbol `max_depth=4`, `min_samples_leaf=20`; rezagos 7/14/21, fin de semana, feriado y tendencia; sin recursión | Árbol `max_depth=15`; rezagos 1 a 7; **recursivo**; sin calendario |
| Implementación | Backtesting escrito a mano | `skforecast` (`ForecasterRecursive`) + bucle semanal |
| Referencias extra | Media constante, naive t−7, media móvil 56 d × calendario | Media constante, repetir semana anterior |

### Secciones

| § | Qué hace | Por qué |
| --- | --- | --- |
| 0 | Instala `skforecast==0.25.0` y registra versiones | `skforecast` no está en `requirements.txt` |
| 1 | Carga la serie con formato de fecha explícito `%Y-%m-%d` | Leer fechas sin formato puede convertir `01/07/2021` en 7 de enero sin aviso |
| 2 | Grafica la serie completa | Primera vista, descriptiva |
| 3 | Partición cronológica 80 / 20 | En series temporales se entrena con el pasado y se evalúa sobre el futuro |
| 4 | Descomposición aditiva (período 7) y efecto de cada día de la semana | Ver cuánto pesan tendencia, patrón semanal y ruido |
| 5 | Autocorrelación (ACF) y autocorrelación parcial (PACF) | Ver si los días anteriores ayudan a predecir: es lo único que usa el árbol |
| 6 | Árbol de decisión con `skforecast`, `lags=7`, `max_depth=15` | Primer modelo aprendido, configurado por el equipo |
| 7 | Tres referencias simples; la línea base es el promedio por tipo de día | Un modelo solo vale si mejora algo simple |
| 8 | Comparación en la primera semana de prueba | Mirada inicial; se muestra por qué no alcanza |
| 9 | Comparación en las 47 semanas de prueba | Evaluación válida |
| 10 | Conclusiones separando evidencia de inferencia | — |

### Decisiones tomadas, con su motivo

| Decisión | Motivo |
| --- | --- |
| **Análisis exploratorio solo con entrenamiento** (descomposición, ACF, PACF) | La prueba se reserva para evaluar; lo que se mira del test puede influir en decisiones del modelo |
| **Línea base = promedio de entrenamiento por `tipo_dia`** | Es la forma que el diagnóstico midió como la mejor disponible fuera de muestra, y la misma de `base.ipynb` |
| **Evaluación semana a semana sobre todo el test, sin reentrenar** | 7 días no alcanzan (el MAE semanal del árbol va de 0,88 a 3,86); sin reentrenar simula un modelo puesto en uso el 2025-02-06 |
| **MAE como métrica principal**, con RMSE y total predicho / observado | Es la métrica más fácil de explicar («siniestros de diferencia por día») y existe también en `base.ipynb`, así que permite comparar. El total predicho / observado muestra si un modelo predice de menos |
| **Métricas sobre predicciones sin redondear** | Redondear esconde diferencias (3,47 pasa a 3) y alteraría las métricas |
| **Se registra el tamaño del árbol** (`04_tamano_arbol`) | `max_depth=15` se fijó a mano; la cantidad de hojas indica si el árbol memoriza |
| **Se mantiene `max_depth=15`** | Es la configuración del equipo. Cambiarla mirando el test sería una fuga; elegirla con validación es trabajo del Entregable 3 |
| **Clima no se usa** | El diagnóstico mostró que fuera de muestra no aporta |
| **Control cruzado con `base.ipynb`** | Verificar que la línea base se calcula igual en los dos notebooks |

### Decisiones descartadas o cambios respecto de la versión anterior

La versión hecha a mano por el equipo (commit `9f98004` con `max_depth=5`; versión de trabajo
posterior con `max_depth=15`) tenía estas diferencias. **Sus cifras no deben citarse como
resultado del modelo:**

| Versión anterior | Por qué se cambió |
| --- | --- |
| Evaluaba **solo los primeros 7 días** del test: MAE 2,65, RMSE 3,39 | Siete días son muy pocos. Esas cifras siguen existiendo como resultado de la primera semana (`07_primera_semana_metricas`), no como evaluación del modelo |
| **Sin línea base** | Un MAE sin referencia no se puede interpretar |
| Descomposición, ACF y PACF sobre **toda la serie**, test incluido (autocorrelación a 1 día: 0,079) | Miraba el test. Con solo entrenamiento, la autocorrelación a 1 día es **0,056** (`03_autocorrelacion`) |
| Predicciones redondeadas en el gráfico y métricas sobre las continuas | Inconsistente; ahora todo sin redondear |
| Eje del gráfico de predicción: «Cantidad diaria de bicicletas alquiladas»; comentarios con `cnt`, «demanda», «Colab» | Restos del ejemplo del curso |
| Partición definida dos veces; imports sin uso; sin celdas de texto; sin artefactos | Limpieza |

---

## 2. Datos de entrada

`data/processed/panel_zona_top.csv`, exportado por el ETL (`resumen_preparacion_montevideo.md`).
Una fila por día de MUNICIPIO C, 12 columnas. Objetivo: `n_siniestros`. Se usa además
`tipo_dia` (`entre_semana`, `fin_semana`, `feriado`) para la línea base. El clima está en el
archivo pero no se usa.

**Integridad (salidas del notebook, §1):** 1.645 días del 2021-07-01 al 2025-12-31; 1.644
diferencias entre fechas consecutivas, todas de 1 día (**sin huecos**); ninguna columna con
nulos. Mínimo 0, máximo 13, promedio 3,52 siniestros por día (salida de §2, sin tabla).

> **Procedencia del archivo en esta corrida.** El 2026-09-14 el archivo apareció sobrescrito con
> formato de Excel (separador `;`, fechas `dd/mm/aaaa`), lo que impedía leerlo. Se **restauró
> desde `panel_diario_montevideo.csv`** (salida intacta del ETL del 2026-09-07), filtrando
> MUNICIPIO C, sin reejecutar el ETL. Verificaciones: el mismo procedimiento reproduce **byte a
> byte** `panel_zona_contraste.csv`; el contenido restaurado es idéntico, valor por valor, al
> archivo que había guardado Excel (1.645 filas, 5.783 siniestros). No quedó registrado en
> ninguna tabla del repositorio: consta en `registro_uso_IA.md` (sesión 2026-09-14).

---

## 3. Procedimiento de evaluación

### 3.1 Partición — `tablas/01_particion.csv`

| Conjunto | Desde | Hasta | Días | % | Promedio de siniestros por día |
| --- | --- | --- | --- | --- | --- |
| Entrenamiento | 2021-07-01 | 2025-02-05 | 1.316 | 80,0 % | **3,426** |
| **Prueba (reservado)** | **2025-02-06** | **2025-12-31** | **329** | **20,0 %** | **3,875** |

*Evidencia:* la prueba promedia un 13,1 % más de siniestros por día que el entrenamiento
(3,875 / 3,426, calculado de `01_particion`). El promedio de prueba es **descriptivo**: no
interviene en ningún ajuste.

### 3.2 Evaluación en el test (§9)

Se parte del primer día de prueba. Cada modelo predice los 7 días siguientes con lo observado
hasta ese momento; se avanza 7 días y se repite. Resultan **47 semanas** que cubren los 329
días. **Ningún modelo se reentrena:** árbol, promedios y media quedan fijos con lo aprendido en
entrenamiento. Lo único que avanza es la información reciente: los 7 días observados que el
árbol usa como entrada y la semana anterior que copia la referencia «repetir semana anterior».

### 3.3 Métricas

| Métrica | Cómo se lee |
| --- | --- |
| **MAE** (principal) | Siniestros de diferencia por día, en promedio. Menor es mejor |
| RMSE | Como el MAE, pero castiga más los errores grandes |
| Total predicho / observado | 1 = acierta el volumen total; < 1 = predice de menos |

No se calcula la desvianza de Poisson, que es la métrica principal de `base.ipynb`: esta
versión prioriza una métrica fácil de explicar, y el árbol puede predecir exactamente 0, valor
que la desvianza de Poisson de scikit-learn no admite. **Para comparar con `base.ipynb`, usar
el MAE.**

### 3.4 Medidas contra la fuga de información

1. Promedios, media constante y árbol se calculan **solo con entrenamiento**.
2. La descomposición, la ACF y la PACF usan **solo entrenamiento**.
3. En el test, ningún modelo se reentrena. El árbol recibe como entrada solo días **ya
   observados** antes de cada semana; dentro de la semana usa sus propias predicciones
   (recursión), nunca valores reales del futuro.
4. «Repetir semana anterior» usa el valor de 7 días antes, que siempre está observado al
   predecir una semana.
5. `max_depth=15` y `lags=7` **no se eligieron mirando el test**. Sobre la primera semana,
   `max_depth=5` daba menos error que 15, así que no hay indicio de ajuste a la prueba
   (verificación de la auditoría, `registro_uso_IA.md`, sesión 2026-09-14). Aun así, la elección
   no está justificada con validación.

---

## 4. Resultados

### 4.1 Exploración (solo entrenamiento)

**Descomposición — `tablas/02b_descomposicion_resumen.csv`, `figuras/fig3_descomposicion.png`**

| Parte | % de la variación de la serie | Mínimo | Máximo |
| --- | --- | --- | --- |
| Tendencia (promedio móvil de 7 días) | 16,5 % | 0,86 | 7,00 |
| Estacionalidad semanal | 10,6 % | −1,47 | 0,75 |
| **Residuo** | **73,7 %** | −5,66 | 7,34 |

Los porcentajes no suman 100 % porque las partes no son del todo independientes.

**Patrón semanal — `tablas/02_patron_semanal.csv`, `figuras/fig4_patron_semanal.png`**

| Día | Efecto estacional | Promedio de siniestros |
| --- | --- | --- |
| lunes | +0,332 | 3,761 |
| martes | +0,153 | 3,559 |
| miércoles | +0,520 | 3,941 |
| jueves | +0,111 | 3,543 |
| **viernes** | **+0,745** | **4,191** |
| sábado | −0,393 | 3,027 |
| **domingo** | **−1,468** | **1,957** |

**Autocorrelación — `tablas/03_autocorrelacion.csv`, `figuras/fig5_acf.png`, `fig6_pacf.png`**

| Rezago (días) | Autocorrelación | Margen por azar (aprox.) |
| --- | --- | --- |
| 1 | 0,056 | 0,054 |
| 7 | 0,077 | 0,054 |
| **14** | **0,165** | 0,054 |
| 21 | 0,098 | 0,054 |
| 28 | 0,112 | 0,054 |

- *Evidencia:* el residuo concentra casi tres cuartos de la variación; la serie es
  mayormente ruido.
- *Evidencia:* hay un patrón semanal claro: el domingo promedia 1,957 siniestros y el viernes
  4,191.
- *Evidencia:* los cinco rezagos de la tabla superan el margen aproximado, pero todos son
  débiles (máximo 0,165). En la figura, las barras que sobresalen caen casi todas en múltiplos
  de 7 días, y la PACF conserva esos mismos rezagos.
- *Inferencia del equipo:* la relación con días anteriores es sobre todo el **patrón del día
  de la semana**, no una memoria de corto plazo. Coincide con el diagnóstico de datos (a 7 días,
  la señal es calendario).

### 4.2 El árbol de decisión — `tablas/04_tamano_arbol.csv`

| Indicador | Valor |
| --- | --- |
| Filas de entrenamiento | 1.309 (1.316 días menos los 7 primeros, sin rezagos completos) |
| Profundidad | 15 |
| **Hojas** | **527** |
| Filas por hoja (promedio) | **2,48** |

*Evidencia:* casi una hoja cada dos días y medio de entrenamiento. *Inferencia:* el árbol
memoriza días concretos en lugar de aprender reglas generales.

### 4.3 Línea base — `tablas/05_linea_base.csv`, `figuras/fig7_linea_base.png`

| Tipo de día | Días de entrenamiento | Promedio de siniestros |
| --- | --- | --- |
| entre_semana | 891 | **3,879** |
| fin_semana | 364 | **2,505** |
| feriado | 61 | **2,295** |
| todos (media constante) | 1.316 | 3,426 |

**Control cruzado con `base.ipynb`** (salida de la celda de coherencia, §9 del notebook): la
línea base da MAE 1,5920 en el test contra 1,5919 de «Tasa x calendario» en
`experiments/base/tablas/06_evaluacion_test.csv`, y la media constante 1,7410 contra 1,7411.
**OK** en ambos casos: los dos notebooks calculan la línea base igual.

### 4.4 Primera semana de prueba — `tablas/06_…`, `tablas/07_primera_semana_metricas.csv`

2025-02-06 a 2025-02-12. Valores reales: 6, 4, 1, 1, 2, 2, 2 (18 siniestros). Ningún feriado.

| Modelo | MAE | RMSE | Total predicho / observado |
| --- | --- | --- | --- |
| **Promedio por tipo de día (línea base)** | **1,556** | **1,675** | 1,356 |
| Repetir semana anterior | 1,714 | 2,204 | 1,111 |
| Media constante | 1,754 | 1,883 | 1,332 |
| Árbol de decisión | 2,647 | 3,387 | 1,526 |

- *Evidencia:* el árbol es el peor. Predijo 8 siniestros el sábado 2025-02-08 (hubo 1) y 6 el
  lunes 2025-02-10 (hubo 2) (`06_primera_semana_predicciones`, `fig8_primera_semana`).
- *Evidencia:* los cuatro modelos predicen de más: la semana tuvo 18 siniestros, por debajo del
  promedio de prueba.
- *Inferencia:* una semana es demasiado poco para evaluar. Esta además resultó baja.

### 4.5 Todo el conjunto de prueba — `tablas/08_test_metricas.csv`

47 semanas, 329 días. Ordenado por MAE.

| Modelo | MAE | RMSE | Total predicho / observado | MAE vs línea base |
| --- | --- | --- | --- | --- |
| **Promedio por tipo de día (línea base)** | **1,592** | **1,967** | 0,884 | — |
| Media constante | 1,741 | 2,120 | 0,884 | +9,4 % |
| Árbol de decisión | 2,206 | 2,784 | 0,931 | **+38,6 %** |
| Repetir semana anterior | 2,228 | 2,866 | 0,996 | +40,0 % |

**Variabilidad semanal — `tablas/10_test_variabilidad_semanal.csv`, `figuras/fig10_test_mae_semanal.png`**

| Modelo | MAE semanal mínimo | Mediana | Máximo | Semanas con menor MAE que la línea base |
| --- | --- | --- | --- | --- |
| Promedio por tipo de día (línea base) | 0,703 | 1,590 | 2,695 | — |
| Media constante | 0,875 | 1,754 | 2,632 | 14 de 47 |
| Árbol de decisión | 0,882 | 2,028 | 3,857 | **8 de 47** |
| Repetir semana anterior | 0,714 | 2,000 | 3,714 | 9 de 47 |

**Semanas destacadas — `tablas/09_test_semanal.csv`, `figuras/fig9_test_totales_semanales.png`**

| Semana (inicio) | Observado | Predicho por el árbol | Nota |
| --- | --- | --- | --- |
| 2025-03-20 | 28 | 42,0 | El árbol predice ≥ 40 |
| 2025-05-01 | 22 | 42,0 | El árbol predice ≥ 40 |
| 2025-08-28 | 26 | 40,0 | El árbol predice ≥ 40 |
| 2025-10-09 | 31 | 42,469 | El árbol predice ≥ 40 |
| 2025-09-11 | 39 | 23,493 | Segunda semana con más siniestros del test |
| 2025-12-11 | 42 | 23,395 | Semana con más siniestros del test |

**Lectura:**

- *Evidencia:* la línea base tiene el menor MAE, y el árbol es peor incluso que la media
  constante. Supera a la línea base en 8 de 47 semanas.
- *Evidencia:* el MAE semanal del árbol va de 0,882 a 3,857; el resultado de una sola semana
  depende mucho de cuál se elija.
- *Evidencia:* en 4 semanas el árbol predijo 40 o más siniestros cuando hubo entre 22 y 31.
- *Evidencia:* la línea base y la media constante predicen el 88,4 % del total observado. Ese
  valor coincide con la razón entre el promedio de entrenamiento y el de prueba (3,426 / 3,875).
- *Evidencia:* el total del árbol (0,931) está más cerca de 1 que el de la línea base, pero su
  MAE es 38,6 % mayor.
- *Inferencia del equipo:* el árbol se «engancha» en valores altos porque usa sus propias
  predicciones como entrada (recursión), y con hojas de 2–3 días propaga valores puntuales del
  pasado.
- *Inferencia del equipo:* el mejor total del árbol se debe a que sus excesos y sus faltas se
  compensan, no a que siga mejor el nivel.
- *Inferencia del equipo:* la infra-predicción de la línea base es el **crecimiento de los
  siniestros** entre entrenamiento y prueba, que ningún modelo trata. Coincide con la tendencia
  que midieron el diagnóstico y `base.ipynb`.
- *Inferencia del equipo:* **la línea base del proyecto sigue siendo el promedio por tipo de
  día.**

**Comparación con el árbol de `base.ipynb`** (`experiments/base/tablas/06_evaluacion_test.csv`):
aquel árbol (`max_depth=4`, rezagos 7/14/21, calendario y tendencia) obtuvo MAE **1,9055** en el
mismo test; el de este notebook, **2,206**. Los dos quedan por debajo de la línea base. Son
configuraciones distintas en varias cosas a la vez, así que **la diferencia entre ellos no puede
atribuirse a un único factor**.

---

## 5. Conclusiones (texto de §10 del notebook, pendiente de validación del equipo)

**Evidencia:** (1) la línea base tiene el menor error en todo el test (MAE 1,592) y el árbol
2,206 (+38,6 %), peor que la media constante (1,741); (2) el árbol memoriza (527 hojas / 1.309
filas); (3) los días anteriores se parecen poco al día a predecir (máximo 0,165) y lo que se
repite es el patrón semanal; (4) evaluar una semana es engañoso (MAE semanal del árbol de 0,88 a
3,86); (5) la prueba promedia un 13 % más que el entrenamiento y los modelos de nivel fijo
predicen el 88,4 % del total.

**Inferencia:** los resultados sugieren que, con solo los 7 días anteriores, el árbol no
encuentra información que mejore lo que ya da el calendario. La línea base se mantiene. Un
modelo mejor necesitaría el calendario como variable, una profundidad elegida con validación y
un tratamiento del crecimiento de los siniestros.

---

## 6. Limitaciones y lo que NO puede afirmarse

| Limitación | Cómo se trata |
| --- | --- |
| **Una sola serie (MUNICIPIO C).** | Declarar que las cifras fijan el procedimiento, no el desempeño del sistema |
| **Un solo horizonte (7 días).** | Otros horizontes pueden cambiar las conclusiones |
| **`max_depth=15` y `lags=7` fijados a mano**, sin validación interna. | La selección de hiperparámetros es el Entregable 3 (`base.ipynb` sí tiene validación interna) |
| **El árbol no recibe calendario.** | Es la configuración del equipo; el resultado no permite concluir que un árbol con calendario también perdería |
| **El crecimiento de los siniestros no se trata.** | La línea base predice 88,4 % del total del test. Pendiente del Entregable 3 |
| **Sin desvianza de Poisson.** | Comparar con `base.ipynb` solo por MAE |
| **Margen por azar de la ACF aproximado** (1,96 / √n). | El gráfico usa una banda más precisa. Que el rezago 14 (0,165) supere al 7 (0,077) **no tiene explicación con estos datos** |
| **La «tendencia» de la descomposición es un promedio de 7 días.** | No sirve para hablar de crecimiento entre años; para eso, `01_particion` o `base.ipynb` |
| **Feriados escasos** (61 días de entrenamiento). | Su promedio es el menos preciso de la línea base |
| **Entorno inconsistente con `requirements.txt`.** La corrida usó pandas **2.3.3** (`00_entorno`): `skforecast` 0.25 exige pandas < 3, y `requirements.txt` fija 3.0.5 y no incluye `skforecast`. | Decisión pendiente del equipo (`HANDOFF.md`). Hasta resolverla, la reproducción exacta requiere pandas 2.x |
| **Archivo de entrada restaurado** (§2), no regenerado por el ETL. | Contenido verificado idéntico; queda documentado |
| **Sin datos de exposición** (tránsito). | Se modela el conteo registrado, no el riesgo |

### Frases que NO deben aparecer en el informe a partir de este notebook

- ❌ «El modelo tiene un error de 2,65 siniestros por día.» → es el MAE de **una semana**. El
  del test completo es **2,206** (`08_test_metricas`).
- ❌ «El árbol de decisión mejora la línea base.» → es un **38,6 % peor** en MAE, y peor que la
  media constante.
- ❌ «El árbol calibra mejor que la línea base» (por su total de 0,931). → sus errores se
  compensan; su MAE es mucho mayor.
- ❌ «Los siniestros de un día dependen de los días anteriores» / «los rezagos son
  informativos». → autocorrelación máxima 0,165; lo que se repite es el patrón semanal.
- ❌ «La descomposición muestra la tendencia de largo plazo» / «se eliminó la tendencia». → la
  componente es un promedio de 7 días, y ningún modelo trata el crecimiento.
- ❌ «`max_depth=15` es la profundidad óptima.» → se fijó a mano, sin validación.
- ❌ «Los domingos son más seguros.» → **registran** menos siniestros; sin datos de tránsito no
  se puede hablar de riesgo.
- ❌ «MUNICIPIO C es el más peligroso.» → es el que más siniestros **registra**.
- ❌ «El modelo generaliza / funciona en Montevideo.» → se evaluó **una sola serie**.
- ❌ «El clima no influye en los siniestros.» → no se usó en este notebook; el diagnóstico solo
  mostró que no mejora las predicciones fuera de muestra.
- ❌ «El árbol de `base.ipynb` es mejor porque tiene menos profundidad.» → difiere en
  profundidad, variables y recursión a la vez; no se puede atribuir a un factor.

---

## 7. Índice de artefactos

`experiments/base_2/` — **12 tablas, 10 figuras**.

| Artefacto | Qué respalda | § notebook |
| --- | --- | --- |
| `tablas/00_entorno.csv` | Versiones de Python y bibliotecas, fecha de ejecución | 0 |
| `tablas/01_particion.csv` | Fechas, días, % y promedio diario de entrenamiento y prueba | 3 |
| `tablas/02_patron_semanal.csv` | Efecto estacional y promedio por día de la semana (entrenamiento) | 4 |
| `tablas/02b_descomposicion_resumen.csv` | % de variación, mínimo y máximo de tendencia, estacionalidad y residuo | 4 |
| `tablas/03_autocorrelacion.csv` | Autocorrelación a 1, 7, 14, 21 y 28 días, con margen aproximado | 5 |
| `tablas/04_tamano_arbol.csv` | Filas, profundidad, hojas y filas por hoja del árbol | 6 |
| `tablas/05_linea_base.csv` | Promedios de entrenamiento por tipo de día y media constante | 7 |
| `tablas/06_primera_semana_predicciones.csv` | Valor real y predicción de cada modelo, primera semana | 8 |
| `tablas/07_primera_semana_metricas.csv` | MAE, RMSE y total predicho / observado, primera semana | 8 |
| `tablas/08_test_metricas.csv` | Métricas en las 47 semanas y diferencia de MAE contra la línea base | 9 |
| `tablas/09_test_semanal.csv` | Observado, MAE y total predicho por semana y modelo | 9 |
| `tablas/10_test_variabilidad_semanal.csv` | MAE semanal mínimo, mediano y máximo; semanas mejores que la línea base | 9 |
| `figuras/fig1_serie.png` | Serie diaria completa | 2 |
| `figuras/fig2_particion.png` | Entrenamiento y prueba en el tiempo | 3 |
| `figuras/fig3_descomposicion.png` | Descomposición aditiva (entrenamiento) | 4 |
| `figuras/fig4_patron_semanal.png` | Efecto de cada día de la semana | 4 |
| `figuras/fig5_acf.png` | Autocorrelación hasta 60 días (entrenamiento) | 5 |
| `figuras/fig6_pacf.png` | Autocorrelación parcial hasta 60 días (entrenamiento) | 5 |
| `figuras/fig7_linea_base.png` | Promedio por tipo de día y media constante | 7 |
| `figuras/fig8_primera_semana.png` | Últimos 30 días de entrenamiento, real, árbol y línea base en la primera semana | 8 |
| `figuras/fig9_test_totales_semanales.png` | Siniestros por semana en el test: observado, línea base y árbol | 9 |
| `figuras/fig10_test_mae_semanal.png` | MAE de cada semana del test: línea base y árbol | 9 |

**Antes de citar cualquier cifra:** verificar que `data/processed/panel_zona_top.csv` sea la
salida vigente del ETL, y que no se haya vuelto a guardar desde Excel. Si el ETL se reejecuta
con otro alcance, este notebook hay que volver a correrlo.

---

## 8. Qué queda pendiente

1. **Validar las lecturas y conclusiones** del notebook (redactadas con Claude).
2. **Decidir qué notebook base se presenta** en el Entregable 2: `base.ipynb`, `base_2.ipynb` o
   ambos (por ejemplo, `base_2` en el cuerpo y `base` como respaldo técnico). Las cifras
   compartidas coinciden.
3. **Resolver pandas 3 vs `skforecast`** y dejar `requirements.txt` coherente con la corrida.
4. **Entregable 3**, para el panel de 8 municipios:
   - calendario como variable del modelo (en `skforecast`, como `exog`);
   - profundidad y rezagos elegidos con validación temporal, sin tocar el test;
   - tratamiento del crecimiento de los siniestros;
   - métricas desagregadas por municipio y hold-out dejando un municipio afuera por vez.
