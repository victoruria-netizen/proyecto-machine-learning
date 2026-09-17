# Resumen del diagnóstico de series temporales — Municipio A (zona de contraste)

**Notebook:** [`notebooks/diagnostico_zona_contraste.ipynb`](../notebooks/diagnostico_zona_contraste.ipynb)
**Artefactos:** `experiments/diagnostico_zona_contraste/` (15 tablas CSV y 7 figuras PNG)
**Fecha de ejecución:** 2026-09-17 (`jupyter nbconvert --execute`, sin errores)
**Alcance:** Municipio A de Montevideo, **2021-07-01 a 2025-12-31** (1.645 días), serie diaria de
conteo de siniestros

---

## 0. Cómo usar este documento

Contexto autocontenido para redactar la documentación del proyecto (informe técnico,
presentaciones, defensa) sin abrir el repositorio. Complementa
[`resumen_diagnostico_datos_municipio.md`](resumen_diagnostico_datos_municipio.md), que cubre el
mismo análisis para Municipio C (la zona más activa): este documento aplica el mismo método a
**Municipio A** (la zona de contraste, actividad mediana) y compara los dos resultados.

**Reglas que quien redacte debe respetar:**

1. **Ninguna cifra sin artefacto.** Toda cifra sale de una ejecución real y tiene su tabla
   (`tablas/NN_nombre.csv`). No inventar ni redondear "para el ejemplo". Un número que falte se
   marca `<!-- PENDIENTE: ... -->`, no se completa.
2. **Distinguir evidencia de inferencia.** "Los datos muestran X" y "el equipo concluye Y" son
   afirmaciones distintas.
3. **No escribir Introducción ni Marco teórico** a partir de este documento.
4. **Respetar la sección 6** ("frases que no deben aparecer en el informe").
5. **Dos municipios, no ocho.** Ninguna cifra de este documento (ni de su par sobre Municipio C)
   debe citarse como válida para los otros seis municipios ni para el panel agregado sin decirlo
   explícitamente. Para eso está `resumen_diagnostico_datos.md`.
6. **No usar la comparación C vs. A como evidencia de generalización.** El propio ETL advierte que,
   con la zonificación por municipios, el par top/contraste "ya casi no contrasta"
   (`resumen_preparacion_montevideo.md` §7.5). Sirve para tener una segunda serie con estructura
   temporal propia, no para medir cuánto varía el modelo entre zonas.

---

## 1. Por qué Municipio A y qué responde este notebook

`diagnostico_datos_municipio.ipynb` aplicó a Municipio C (la zona más activa) el análisis de
estructura temporal que `diagnostico_datos.ipynb` no hace: tendencia, estacionalidad, ACF/PACF y la
decisión de transformar el objetivo. Ese análisis quedó verificado en una sola serie. Este notebook
lo repite sobre **Municipio A**, la zona de **contraste** que reserva
`preparacion_montevideo.ipynb`: ni la más activa (Municipio C, 5.783 siniestros) ni la menos activa
(Municipio CH, 3.377), sino la de **actividad mediana** entre los ocho municipios (**5.016
siniestros, 13,70 % del total**; `resumen_diagnostico_datos.md` §4.2;
`resumen_preparacion_montevideo.md` §7.5).

**Diferencia metodológica deliberada frente a `diagnostico_datos_municipio.ipynb`:** ese notebook
reconstruye la serie desde el CSV crudo y la capa de municipios con `geopandas.sjoin`, como
verificación cruzada independiente de la asignación espacial. Este notebook **no** repite esa
reconstrucción: parte directamente de `data/processed/panel_zona_contraste.csv`, el panel de
Municipio A ya preparado y verificado por el ETL (`preparacion_montevideo.ipynb`, dieciséis
comprobaciones en OK, cruzado de forma independiente contra `diagnostico_datos.ipynb`;
`resumen_preparacion_montevideo.md` §8). Repetir la verificación espacial habría sido redundante;
en su lugar, la sección 2 hace una verificación cruzada **numérica** contra las cifras ya
publicadas para Municipio A.

**Qué responde:**

| Pregunta | Sección de este documento | Sección del notebook |
| --- | --- | --- |
| ¿Hay tendencia, y estacionalidad diaria/semanal/anual? | 3 | 2 |
| ¿Qué dice la ACF/PACF sobre persistencia y calendario? | 4 | 3 |
| ¿La dispersión entre un día y sus rezagos sugiere memoria? | 4.4 | 3.4 |
| ¿Corresponde diferenciar o transformar (log/Box-Cox) el objetivo? | 5 | 4 |

**El recorte territorial y temporal se hereda sin volver a discutirlo**: Montevideo, municipios
(no barrios ni grilla), desde 2021-07-01. Esa decisión está justificada con evidencia en
`diagnostico_datos.ipynb` (§2.6 y §3.1) y en `resumen_diagnostico_datos.md` (§2 y §4.1); este
notebook no la vuelve a justificar — `panel_zona_contraste.csv` ya viene recortado así.

---

## 2. Datos y verificación cruzada

`tablas/00_procedencia.csv`, `01_carga_panel.csv`, `02_verificacion_cruzada.csv`

`panel_zona_contraste.csv` ya trae una fila por (fecha, zona) para Municipio A. La carga confirma
que tiene la forma esperada:

| Indicador | Valor |
| --- | --- |
| Filas del panel | 1.645 |
| Zona presente | MUNICIPIO A (única) |
| Fecha mínima | 2021-07-01 |
| Fecha máxima | 2025-12-31 |
| Huecos de calendario | 0 |
| Fechas duplicadas | 0 |

**Verificación cruzada — coincide en los dos indicadores comprobados:**

| Indicador | Referencia (`resumen_diagnostico_datos.md` / `resumen_preparacion_montevideo.md`) | Recalculado sobre el panel | Resultado |
| --- | --- | --- | --- |
| Siniestros totales | 5.016 | 5.016 | ✅ coincide |
| % de días en cero | 5,84 | 5,84 | ✅ coincide |

El total y el porcentaje de días en cero de Municipio A ya estaban citados en dos fuentes con
implementaciones distintas (polígonos manuales del diagnóstico principal, y el ETL). Que el panel
ya preparado los reproduzca es una **tercera** confirmación independiente — misma lógica de
verificación cruzada que usan `diagnostico_datos.ipynb` y `diagnostico_datos_municipio.ipynb`.

---

## 3. Tendencia y estacionalidad — `tablas/03` a `06`, `figuras/fig1`, `fig2a`, `fig2b`

### 3.1 La serie — `tablas/03_resumen_serie_municipio_a.csv`

| Indicador | Valor |
| --- | --- |
| Días del período | 1.645 |
| Siniestros totales | 5.016 |
| Días en cero | 96 (**5,84 %**) |
| Media diaria | **3,0492** |
| Varianza diaria (ddof=0) | 3,4231 |
| Índice de dispersión (var/media) | **1,1226** |
| Máximo diario | 11 |
| Mediana diaria | 3,0 |

Municipio A tiene una dispersión (1,1226) más leve que Municipio C (1,260,
`resumen_diagnostico_datos_municipio.md` §3.1): más cerca de un proceso Poisson puro (var = media).

### 3.2 Tendencia — `tablas/04_tendencia_anual.csv`, `figuras/fig1_tendencia_municipio_a.png`

| Año | Media diaria |
| --- | --- |
| 2021 (jul–dic) | 2,875 |
| 2022 | 2,6685 |
| 2023 | 2,9452 |
| 2024 | 3,2869 |
| 2025 | 3,3836 |

**Evidencia:** a diferencia de Municipio C (que baja de 2021 a 2023 y recién sube en 2024-2025), la
media anual de Municipio A **cae sólo el primer año** (2021→2022) y luego **sube cada año** hasta
2025, un crecimiento de **+17,7 %** entre el mínimo (2022) y el máximo (2025). Es un patrón más
parecido al crecimiento sostenido del agregado departamental (`resumen_diagnostico_datos.md` §4.1:
21,4 → 24,6 siniestros/día entre 2021 y 2025, +14,95 %) que al de Municipio C, que no es monótono.

**Inferencia del equipo:** el crecimiento agregado no se reparte igual entre municipios, pero
tampoco es exclusivo de uno solo. Con sólo dos series no alcanza para generalizar el patrón a los
seis municipios restantes.

### 3.3 Estacionalidad diaria/semanal — `tablas/05_perfil_semanal.csv`, `figuras/fig2a`

| Día | Media de siniestros |
| --- | --- |
| viernes | **3,5234** (máximo) |
| sábado | 3,3106 |
| martes | 3,1064 |
| lunes | 3,0298 |
| miércoles | 3,0170 |
| jueves | 2,8894 |
| domingo | **2,4681** (mínimo) |

Razón viernes/domingo: **1,43×**. El orden (viernes máximo, domingo mínimo) coincide con el
agregado departamental (`resumen_diagnostico_datos.md` §4.4: viernes 25,74, domingo 16,06, razón
≈1,60×) y con Municipio C, pero la razón de Municipio A es **menos marcada** que la del agregado y
que la de Municipio C (donde, según `resumen_diagnostico_datos_municipio.md` §3.3, la razón es
2,09× — más marcada que el agregado). El patrón semanal está presente en las dos zonas, pero no con
la misma intensidad.

### 3.4 Estacionalidad anual — `tablas/06_indice_estacional_mensual.csv`, `figuras/fig2b`

| Mes | Índice | Mes | Índice |
| --- | --- | --- | --- |
| Enero | **0,797** (mínimo) | Julio | 0,978 |
| Febrero | 0,876 | Agosto | 1,058 |
| Marzo | 1,022 | Septiembre | 0,986 |
| Abril | 0,963 | Octubre | 1,016 |
| Mayo | **1,083** (máximo) | Noviembre | 1,068 |
| Junio | 1,061 | Diciembre | 1,046 |

**Evidencia:** el mínimo es enero, igual que en Municipio C (donde el mínimo también es enero,
0,708), pero el máximo está en **mayo** y no en junio (que en Municipio C es el máximo, 1,105; en
Municipio A junio es el segundo más alto, 1,061). El mes de mayor actividad no coincide exactamente
entre las dos zonas, aunque ambas comparten el mínimo de enero y evitan el patrón
verano-alto/invierno-bajo.

**Frase que estos datos NO sostienen:** «el verano tiene más siniestros por las vacaciones» —
enero (0,797) y febrero (0,876) son, de los doce meses, los dos de índice más bajo, igual que en
Municipio C.

---

## 4. ACF, PACF y dispersión por rezago — `tablas/07` a `10`, `figuras/fig3a`, `fig3b`, `fig4`

### 4.1 Metodología

Igual que en `diagnostico_datos_municipio.ipynb`, se usa la banda analítica estándar de
`statsmodels` (±1,96/√n = **±0,0483** para n=1.645) en vez de la banda simulada de
`diagnostico_datos.ipynb`: razonable porque la media de esta serie (≈3,05) está lejos de cero y
porque la sección 5.1 confirma con ADF que la serie es estacionaria en media.

### 4.2 ACF/PACF cruda — `tablas/07_acf_pacf_crudo.csv`, `figuras/fig3a`

| Rezago | ACF | ¿Fuera de banda (±0,0483)? |
| --- | --- | --- |
| 1 | 0,0396 | No |
| 2, 3, 4 | 0,0487 / 0,0526 / 0,0550 | Sí |
| 7 | 0,0266 | No |
| 13, 14 | 0,0540 / 0,0511 | Sí |
| 21 | 0,0475 | No |
| 28, 29 | 0,0529 / 0,0683 | Sí |

**A diferencia de Municipio C**, donde los múltiplos de 7 (7, 14, 21, 28) dominan la ACF cruda con
el pico en el rezago 14 (0,1706), en Municipio A el rezago 7 (0,0266) y el 21 (0,0475) quedan
**dentro** de la banda, y el 1 también (0,0396): no es la firma clásica de un ciclo semanal.

### 4.3 Cuánto es calendario — `tablas/08_acf_residuo_calendario.csv`, `09_ljung_box.csv`, `figuras/fig3b`

Al restar a cada día la media de su grupo de calendario (día de la semana, feriado aparte), el
conjunto de rezagos fuera de banda **cambia** en vez de reducirse de forma sistemática: 3, 14 y 28
pasan a estar dentro de banda, pero 9 y 20 pasan a estar fuera (no estaban fuera en la serie
cruda). El calendario no explica un patrón tan claro como en Municipio C (donde los múltiplos de 7
caían dentro de banda casi en bloque tras descontarlo) — la autocorrelación de Municipio A parece
más difusa que estructurada por semana.

**Ljung-Box:** rechaza "no autocorrelación conjunta" con `p < 0,05` en los tres horizontes probados
(7, 14 y 30 rezagos: p = 0,0074; 0,0013; 0,00026), aunque con menos margen que en Municipio C
(`p < 0,001` en los tres). Hay estructura temporal estadísticamente detectable, pero más débil y
menos concentrada en el calendario semanal que en la zona más activa.

**Inferencia del equipo:** en Municipio A el calendario semanal pesa menos como explicación de la
autocorrelación que en Municipio C — coherente con la razón viernes/domingo más chica (§3.3). Los
rezagos 9 y 20 del residuo no tienen una interpretación de calendario obvia y se dejan señalados,
no explicados.

### 4.4 Dispersión por rezago — `tablas/10_dispersion_por_rezago.csv`, `figuras/fig4`

| Rezago | Correlación de Pearson |
| --- | --- |
| 1 | 0,0396 |
| 7 | 0,0267 |
| 14 | 0,0517 |
| 30 | 0,0338 |

Coeficientes chicos en los cuatro paneles (todos ≤ 0,052) y, a diferencia de lo esperable si
hubiera memoria de corto plazo, **no decaen con el rezago**: el más alto es el del rezago 14, no el
del rezago 1.

---

## 5. ¿Corresponde diferenciar o transformar el objetivo? — `tablas/11` a `13`, `figuras/fig5`

### 5.1 Estacionariedad: ADF y KPSS — `tablas/11_estacionariedad_adf_kpss.csv`

| Prueba | H0 | Estadístico | p-valor | Resultado (α=0,05) |
| --- | --- | --- | --- | --- |
| ADF | hay raíz unitaria | −17,8908 | 2,98 × 10⁻³⁰ | **rechaza H0** (estacionaria) |
| KPSS | la serie es estacionaria | 2,8405 | ≤ 0,01 (el p-valor real es menor aún, según aviso de `statsmodels`) | **rechaza H0** (no estacionaria) |

**Evidencia — la misma tensión que en Municipio C, con margen aún mayor:** el ADF rechaza la raíz
unitaria con margen incluso mayor que en Municipio C (10⁻³⁰ contra 10⁻¹⁰). El KPSS también rechaza
la estacionariedad.

**Lectura del equipo:** igual que en Municipio C, la combinación es compatible con una serie
estacionaria alrededor de un nivel que deriva despacio (cae en 2022, sube sostenidamente
2022-2025, §3.2), no con una tendencia determinística fuerte ni con una caminata aleatoria. Que el
mismo patrón — ADF estacionario, KPSS no — aparezca en dos municipios distintos apoya que es una
propiedad genuina del proceso y no un artefacto de una sola serie.

### 5.2 Diferenciar empeora, no mejora — `tablas/12_efecto_diferenciacion.csv`

| Serie | ACF rezago 1 | ACF rezago 7 | Varianza |
| --- | --- | --- | --- |
| Cruda | 0,0396 | 0,0266 | 3,4231 |
| Diferenciada (d=1) | **−0,5044** | 0,0006 | 6,5785 |
| Diferenciada estacional (D=1, s=7) | 0,0131 | **−0,5104** | 6,6679 |

**Evidencia:** igual que en Municipio C, diferenciar en nivel (d=1) no reduce la autocorrelación —
la vuelve fuertemente negativa en el rezago 1 (−0,5044, incluso más marcada que en Municipio C,
−0,4621) y casi duplica la varianza. La diferenciación estacional tiene el mismo problema en su
propio rezago 7 y también casi duplica la varianza. **Ninguna de las dos ayuda.**

### 5.3 Relación media-varianza y Box-Cox — `tablas/13_diagnostico_transformacion.csv`

| Indicador | Valor |
| --- | --- |
| Ajuste lineal var ~ media (pendiente, intercepto) | 0,900 , 0,568 |
| Ajuste cuadrático var ~ media² (pendiente, intercepto) | 0,143 , 1,955 |
| Correlación media-varianza mensual | **0,4597** |
| λ de Box-Cox (MLE, sobre serie + 1) | **0,475** |

**Evidencia:**

- La relación media-varianza mensual en Municipio A es bastante más débil que en Municipio C
  (r = 0,46 contra 0,468 — similar en magnitud, pero la pendiente ajustada cambia): la recta
  (var ≈ 0,900·media + 0,568) tiene pendiente cercana a **1**, más próxima a la referencia Poisson
  pura (var = media) que la de Municipio C (pendiente 1,334). Coherente con el índice de
  dispersión más chico de la sección 3.1 (1,12 en A contra 1,26 en C).
- El ajuste cuadrático (var ∝ media²) tiene pendiente chica (0,143): tampoco acá el patrón es el
  que el logaritmo está pensado para corregir.
- El λ de Box-Cox estimado da **0,475** — prácticamente el mismo valor que en Municipio C (0,4733),
  cerca de 0,5 (raíz cuadrada) y lejos de 0 (logaritmo).
- Con 5,84 % de días en cero, log y Box-Cox exigen desplazar la serie (+1), igual que en
  Municipio C.
- En la ACF a 14 rezagos, `log1p` y Box-Cox no cambian la estructura de forma apreciable frente a
  la serie cruda.

### 5.4 La decisión

**Tampoco corresponde en Municipio A aplicar diferenciación ni una transformación logarítmica o
Box-Cox clásica al objetivo.** El argumento es, si acaso, más fuerte que en Municipio C: la
relación varianza-media es más débil todavía y la pendiente está más cerca de la referencia
Poisson pura. El λ de Box-Cox coincide con el de Municipio C (~0,47-0,48): si hiciera falta
estabilizar varianza en el modelado, la **raíz cuadrada** es la transformación que reaparece en las
dos zonas — no el logaritmo. Es una segunda confirmación, con una serie distinta, de la decisión
que ya toma `resumen_diagnostico_datos.md` (§5.1) de tratar el objetivo como variable de conteo.

---

## 6. Limitaciones y frases que NO deben aparecer en el informe

| Limitación | Consecuencia |
| --- | --- |
| **Dos municipios, no ocho.** C y A dan dos series, pero no hay garantía de que la conclusión de la sección 5 valga para los otros seis; ninguna zona se eligió por representatividad. | Antes de fijar la transformación del objetivo para el modelo final, repetir el diagnóstico de estacionariedad en algún municipio adicional de actividad distinta (p. ej. G o CH). |
| **El par top/contraste "ya casi no contrasta"** con la zonificación por municipios (razón 1,15×, `resumen_preparacion_montevideo.md` §7.5). | No usar la comparación C vs. A como evidencia de generalización — sólo da una segunda serie con estructura temporal propia. |
| **Este notebook no reconstruye la asignación punto-polígono**, a diferencia de `diagnostico_datos_municipio.ipynb`; se apoya en las dieciséis comprobaciones del ETL en lugar de una verificación geoespacial propia. | Si hiciera falta una verificación espacial independiente también para Municipio A, hay que repetirla desde el CSV crudo. |
| **Banda de ACF/PACF analítica**, no simulada. | Aproximación razonable con media ≈3,05/día, lejos de cero, pero sigue siendo asintótica. |
| **El residuo de calendario (§4.3) no tiene una lectura simple** (rezagos 9 y 20 fuera de banda, sin interpretación obvia). | Declarar como observación, no como hallazgo confirmado. |
| **No se evaluó el clima** en este notebook. | Ver `resumen_diagnostico_datos.md` §5.3 y `resumen_preparacion_montevideo.md` §6.2. |
| **La recomendación de no transformar es sobre el objetivo definido hoy** (conteo diario por municipio). | Releer la sección 5 si cambia la definición del objetivo. |

**Frases que NO deben aparecer en el informe:**

- ❌ «La serie de Municipio A no es estacionaria y hay que diferenciarla.» → El ADF rechaza la raíz
  unitaria con margen aún mayor que en Municipio C, y diferenciar empeora la ACF.
- ❌ «Hace falta un logaritmo para estabilizar la varianza.» → La relación media-varianza es débil
  y con pendiente cercana a 1 (Poisson); el λ de Box-Cox (≈0,48) apunta a raíz cuadrada.
- ❌ «La serie es estacionaria», sin matices. → El KPSS rechaza esa hipótesis; hay una deriva de
  nivel lenta (caída en 2022, alza sostenida 2022-2025) que el ADF no capta.
- ❌ «Municipio A tiene el mismo patrón semanal que Municipio C.» → La razón viernes/domingo es más
  chica (1,43× contra 2,09× en C) y la ACF cruda no muestra la firma de múltiplos de 7 que sí
  aparece en C.
- ❌ «El modelo se validó comparando la zona más activa contra una de contraste.» → Con
  municipios las dos series son casi iguales en escala (razón 1,15×,
  `resumen_preparacion_montevideo.md` §7.5); esa comparación no mide generalización.
- ❌ Citar cualquier cifra de este documento como válida para «Montevideo» o «el panel completo»
  sin aclarar que es de **Municipio A únicamente**.

---

## 7. Índice de artefactos

`experiments/diagnostico_zona_contraste/` — **15 tablas y 7 figuras**
(`tablas/14_artefactos.csv` lista todas con su tamaño).

| Eje | Tablas |
| --- | --- |
| Trazabilidad | `00_procedencia`, `00b_entorno` |
| Datos | `01_carga_panel`, `02_verificacion_cruzada`, `03_resumen_serie_municipio_a` |
| Tendencia y estacionalidad | `04_tendencia_anual`, `05_perfil_semanal`, `06_indice_estacional_mensual` |
| ACF/PACF y dispersión | `07_acf_pacf_crudo`, `08_acf_residuo_calendario`, `09_ljung_box`, `10_dispersion_por_rezago` |
| Transformaciones | `11_estacionariedad_adf_kpss`, `12_efecto_diferenciacion`, `13_diagnostico_transformacion` |

**Figuras:**

| Figura | Qué muestra | Sección de este documento |
| --- | --- | --- |
| `fig1_tendencia_municipio_a.png` | Serie diaria, medias móviles de 30/90 días y media anual | 3.2 |
| `fig2a_perfil_semanal_municipio_a.png` | Media de siniestros por día de la semana | 3.3 |
| `fig2b_estacionalidad_anual_municipio_a.png` | Índice estacional mensual y tendencia de `seasonal_decompose` | 3.4 |
| `fig3a_acf_pacf_crudo_municipio_a.png` | ACF y PACF de la serie cruda (`statsmodels`) | 4.2 |
| `fig3b_acf_residuo_calendario_municipio_a.png` | ACF cruda vs. ACF del residuo tras descontar calendario | 4.3 |
| `fig4_dispersion_lags_municipio_a.png` | Dispersión de yₜ contra yₜ₋ₖ para k=1,7,14,30 | 4.4 |
| `fig5_transformaciones_municipio_a.png` | Relación media-varianza mensual y ACF cruda vs. log1p vs. Box-Cox | 5.3 |

---

## 8. Qué queda pendiente

1. **Repetir el diagnóstico de estacionariedad (§5) en 2-3 municipios adicionales** de actividad
   distinta de C y A (por ejemplo G o CH), para verificar si la decisión de no transformar el
   objetivo generaliza a todo el panel o es propia de estas dos zonas.
2. **Si se decide un método que exija varianza estabilizada** en el notebook de modelado, evaluar
   la raíz cuadrada (respaldada por λ de Box-Cox ≈0,47-0,48 en las dos zonas ya analizadas) en vez
   de logaritmo.
3. **Los rezagos 9 y 20 del residuo de calendario (§4.3)** quedan como observación abierta: no se
   investigó su origen. Si se quiere usar en el modelado, evaluarlos como variable candidata bajo
   el mismo protocolo que `resumen_diagnostico_datos.md` (§5.2) usa para el rezago 1, no asumirlos.
4. **Por qué Municipio A tiene un patrón semanal y de calendario más débil que Municipio C** no se
   investigó (¿composición de la red vial, tipo de siniestro, volumen de tránsito?); queda como
   pregunta abierta para el análisis crítico del informe, no como hallazgo de este notebook.
