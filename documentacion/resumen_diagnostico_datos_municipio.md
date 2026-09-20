# Resumen del diagnóstico de series temporales — Municipio C

**Notebook:** [`notebooks/diagnostico_datos_municipio.ipynb`](../notebooks/diagnostico_datos_municipio.ipynb)
**Artefactos:** `experiments/diagnostico_datos_municipio/` (17 tablas CSV y 7 figuras PNG)
**Fecha de ejecución:** 2026-09-20 (`jupyter nbconvert --execute`, sin errores; reejecución en el
entorno estandarizado, sin cambio de cifras respecto de la del 2026-09-14)
**Alcance:** Municipio C de Montevideo, **2021-07-01 a 2025-12-31** (1.645 días), serie diaria de
conteo de siniestros

---

## 0. Cómo usar este documento

Contexto autocontenido para redactar la documentación del proyecto (informe técnico,
presentaciones, defensa) sin abrir el repositorio. Complementa
[`resumen_diagnostico_datos.md`](resumen_diagnostico_datos.md), que cubre calidad, cobertura y
adecuación de los ocho municipios; este documento cubre sólo lo que ese otro **no** hace:
estructura temporal (tendencia, estacionalidad, ACF/PACF, dispersión por rezago) de la serie de
un único municipio, y la decisión de si corresponde diferenciarla o transformarla.

**Reglas que quien redacte debe respetar:**

1. **Ninguna cifra sin artefacto.** Toda cifra sale de una ejecución real y tiene su tabla
   (`tablas/NN_nombre.csv`). No inventar ni redondear "para el ejemplo". Un número que falte se
   marca `<!-- PENDIENTE: ... -->`, no se completa.
2. **Distinguir evidencia de inferencia.** "Los datos muestran X" y "el equipo concluye Y" son
   afirmaciones distintas.
3. **No escribir Introducción ni Marco teórico** a partir de este documento.
4. **Respetar la sección 6** ("frases que no deben aparecer en el informe").
5. **Un solo municipio.** Ninguna cifra de este documento debe citarse como válida para los otros
   siete municipios ni para el panel agregado sin decirlo explícitamente. Para eso está
   `resumen_diagnostico_datos.md`.

> ### Reejecución del 2026-09-20 en el entorno estandarizado
>
> El notebook se reejecutó de punta a punta en un entorno nuevo, fijado en `requirements.txt` y
> `requirements-lock.txt`. Versiones registradas en `00b_entorno.csv`: Python 3.13.15, pandas 2.3.3,
> NumPy 2.5.2, SciPy 1.18.1, statsmodels 0.14.6, geopandas 1.1.4, matplotlib 3.11.1 y holidays
> 0.103. La corrida anterior había usado Python 3.13.9, pandas 3.0.3, NumPy 2.4.6 y SciPy 1.17.1;
> statsmodels, geopandas, matplotlib y holidays no cambiaron.
>
> **Ninguna cifra de resultados cambió.** Se comparó contra una copia de las salidas anteriores: 14
> de las 17 tablas y 5 de las 7 figuras quedaron idénticas byte a byte. Las otras 3 tablas
> cambiaron solo en `00b_entorno` (versiones y fecha), `00_procedencia` (ver más abajo) y
> `15_artefactos` (una fila más: al reejecutar, la tabla se lista a sí misma). Las 2 figuras
> restantes, `fig4_dispersion_lags_municipio_c.png` y `fig5_transformaciones_municipio_c.png`,
> difieren en 0,005 % y 0,003 % de los píxeles, con una diferencia máxima de 1 sobre 255 por canal
> de color: ruido de renderizado.
>
> **Cambio en `00_procedencia` a tener presente.** El `sha256` del geojson de municipios
> (`data/raw/municipios_montevideo.geojson`, 2,87 MB) es distinto: la corrida anterior registró
> `c5d9f651…` y la actual `ed0ba13e…`, el mismo valor que registró `diagnostico_datos` el
> 2026-09-14. El `sha256` del archivo de siniestros no cambió. La corrida anterior usó, entonces,
> **otra copia del geojson**. Como las tablas de resultados salen idénticas, la diferencia entre las
> dos copias no altera ninguna salida de este notebook. No se sabe en qué difieren, porque la copia
> anterior no se conserva. El valor vigente es `ed0ba13e…`.
>
> **Corrección en la celda 7 del notebook.** El archivo crudo tiene un registro sin `Calle`, y en
> pandas 2.x `.astype(str)` lo convierte en el texto `"nan"`. Se agregó `.where(df_pais[c].notna())`
> para conservar el nulo, igual que en `diagnostico_datos` (ver `resumen_diagnostico_datos.md`).
> Ninguna tabla ni figura de este notebook cambió por esa corrección.

---

## 1. Por qué Municipio C y qué responde este notebook

`diagnostico_datos.ipynb` diagnostica calidad, cobertura, adecuación y limitaciones de los ocho
municipios (documentado en `resumen_diagnostico_datos.md`), pero no examina la estructura
**temporal** de ninguna serie individual: no hay tendencia, estacionalidad, ACF/PACF ni decisión
sobre transformar el objetivo. Ese hueco es lo que cubre este notebook.

**Por qué un solo municipio y por qué Municipio C.** Analizar la estructura temporal de una serie
de conteo bajo (media ≈ 0,35–3,5 siniestros/día según la zonificación) es más legible cuanto mayor
es la tasa media: con una tasa muy baja el ruido de Poisson dominaría cualquier ACF o
descomposición estacional. Municipio C es el que más siniestros concentra de los ocho — **5.783,
15,80 % del total** (`resumen_diagnostico_datos.md`, §4.2) —, así que es la serie con más soporte
para que estos análisis sean legibles.

**Qué responde:**

| Pregunta | Sección de este documento | Sección del notebook |
| --- | --- | --- |
| ¿Hay tendencia, y estacionalidad diaria/semanal/anual? | 3 | 2 |
| ¿Qué dice la ACF/PACF sobre persistencia y calendario? | 4 | 3 |
| ¿La dispersión entre un día y sus rezagos sugiere memoria? | 4.3 | 3.4 |
| ¿Corresponde diferenciar o transformar (log/Box-Cox) el objetivo? | 5 | 4 |

**El recorte territorial y temporal se hereda sin volver a discutirlo**: Montevideo, municipios
(no barrios ni grilla), desde 2021-07-01 (excluye el semestre de pandemia). Esas dos decisiones
están justificadas con evidencia en `diagnostico_datos.ipynb` (§2.6 y §3.1) y en
`resumen_diagnostico_datos.md` (§2 y §4.1); este notebook no las vuelve a justificar.

---

## 2. Datos y verificación cruzada

`tablas/00_procedencia.csv`, `01_recorte_alcance.csv`, `02_asignacion_municipios.csv`,
`03_verificacion_cruzada.csv`

El recorte es el mismo de `diagnostico_datos.ipynb`: Montevideo desde 2021-07-01, duplicados
exactos eliminados.

| Paso | Registros | % del archivo |
| --- | --- | --- |
| Registros del archivo | 224.694 | 100,0 % |
| Tras filtrar Montevideo | 62.427 | 27,78 % |
| Tras filtrar `Fecha >= 2021-07-01` | 36.713 | 16,34 % |
| Tras eliminar duplicados exactos | 36.623 | 16,30 % |

**La asignación a municipios se reimplementa con `geopandas`** (intersección punto-polígono,
`sjoin`), en lugar de reutilizar la implementación de `diagnostico_datos.ipynb` (que arma sus
propios polígonos con `matplotlib.path` para no depender de ninguna librería geoespacial). Son dos
caminos de código independientes sobre las mismas fuentes crudas.

**Verificación cruzada — las ocho cifras coinciden exactamente:**

| Municipio | `resumen_diagnostico_datos.md` (§4.2) | Recalculado con geopandas | Resultado |
| --- | --- | --- | --- |
| C | 5.783 | 5.783 | ✅ coincide |
| B | 5.377 | 5.377 | ✅ coincide |
| D | 5.319 | 5.319 | ✅ coincide |
| A | 5.016 | 5.016 | ✅ coincide |
| F | 4.424 | 4.424 | ✅ coincide |
| G | 3.701 | 3.701 | ✅ coincide |
| E | 3.615 | 3.615 | ✅ coincide |
| CH | 3.377 | 3.377 | ✅ coincide |

Dos implementaciones distintas (polígonos manuales vs. `geopandas`) sobre las mismas fuentes
llegan al mismo resultado en los ocho municipios: es evidencia fuerte de que la asignación
espacial de ambos notebooks está bien construida, y es citable en el informe con ese argumento.

**La capa de municipios se descargó de nuevo** el día de esta ejecución (misma consulta WFS
documentada en `resumen_diagnostico_datos.md` §2 y en `diagnostico_datos.ipynb` §2.6: GeoServer de
la Intendencia, capa `mapstore-tematicas:zon_v_sig_municipios`). El contenido no cambió (8
polígonos, mismos nombres A–G y CH), pero el `sha256` de esta descarga **no coincide** con el
documentado en la versión anterior — es una respuesta de servidor pedida en otro momento, no el
mismo archivo re-versionado; la tabla de procedencia de este notebook registra su propio hash y
fecha en lugar de asumir el del otro.

---

## 3. Tendencia y estacionalidad — `tablas/04` a `07`, `figuras/fig1`, `fig2a`, `fig2b`

### 3.1 La serie

| Indicador | Valor |
| --- | --- |
| Días del período | 1.645 |
| Siniestros totales | 5.783 |
| Días en cero | 79 (**4,80 %**) |
| Media diaria | **3,5155** |
| Varianza diaria (ddof=0) | 4,4297 |
| Índice de dispersión (var/media) | **1,260** |
| Máximo diario | 13 |
| Mediana diaria | 3,0 |

`tablas/04_resumen_serie_municipio_c.csv`. La dispersión (1,260) es casi idéntica a la del panel
completo de ocho municipios (1,259, `resumen_diagnostico_datos.md` §5.1): la sobredispersión leve
del objetivo no es un artefacto de agregar zonas, está presente ya en una sola serie.

### 3.2 Tendencia — `tablas/05_tendencia_anual.csv`, `figuras/fig1_tendencia_municipio_c.png`

| Año | Media diaria |
| --- | --- |
| 2021 (jul–dic) | 3,4402 |
| 2022 | 3,3726 |
| 2023 | 3,3288 |
| 2024 | 3,6421 |
| 2025 | 3,7562 |

**Evidencia:** a diferencia del promedio de los ocho municipios (que sube de forma sostenida de
21,4 a 24,6 siniestros/día entre 2021 y 2025, `resumen_diagnostico_datos.md` §4.1), la media anual
de Municipio C **no es monótona**: baja de 2021 a 2023 y recién sube en 2024–2025.

**Inferencia del equipo:** el crecimiento agregado del departamento no se reparte por igual entre
municipios; el de Municipio C es más débil y no lineal, coherente con que la razón máx/mín entre
municipios (1,71×) no sería estable en el tiempo si todas las zonas crecieran al mismo ritmo.

### 3.3 Estacionalidad diaria/semanal — `tablas/06_perfil_semanal.csv`, `figuras/fig2a`

| Día | Media de siniestros |
| --- | --- |
| viernes | **4,268** |
| miércoles | 3,996 |
| lunes | 3,838 |
| martes | 3,702 |
| jueves | 3,732 |
| sábado | 3,034 |
| domingo | **2,038** |

Razón viernes/domingo: **2,09×**. El orden coincide con el perfil del departamento entero
(`resumen_diagnostico_datos.md` §4.4: viernes 25,74, domingo 16,06 sobre las ocho zonas), y la
razón es incluso algo más marcada en esta única zona que en el agregado.

### 3.4 Estacionalidad anual — `tablas/07_indice_estacional_mensual.csv`, `figuras/fig2b`

Índice estacional mensual (cada mes / media de su propio año, mismo método que
`diagnostico_datos.ipynb` §3.1):

| Mes | Índice | Mes | Índice |
| --- | --- | --- | --- |
| Enero | **0,708** (mínimo) | Julio | 1,016 |
| Febrero | 0,824 | Agosto | 1,094 |
| Marzo | 0,950 | Septiembre | 1,083 |
| Abril | 0,988 | Octubre | 1,035 |
| Mayo | 1,018 | Noviembre | 1,033 |
| Junio | **1,105** (máximo) | Diciembre | 1,058 |

**Evidencia:** el mínimo es enero y el máximo junio — **no** hay un patrón simple de
verano-alto/invierno-bajo (enero y febrero, pleno verano con vacaciones, son de los meses más
bajos del año). La tendencia de `seasonal_decompose(período=365)` coincide con la lectura de la
media móvil de 365 días: confirma que la caída 2021–2023 y la recuperación 2024–2025 de la sección
3.2 no es un artefacto del suavizado elegido.

**Frase que estos datos NO sostienen:** «el verano tiene más siniestros por las vacaciones» — es
al revés en esta serie: enero y febrero son los meses de índice más bajo.

---

## 4. ACF, PACF y dispersión por rezago — `tablas/08` a `11`, `figuras/fig3a`, `fig3b`, `fig4`

### 4.1 Metodología: por qué banda analítica y no simulada

`diagnostico_datos.ipynb` (§5.2) usa una banda nula **simulada** (siniestros de Poisson con la
tasa media de cada municipio, 400 simulaciones), porque a la escala de conteos bajos el supuesto
detrás de la banda analítica de ACF (ruido aproximadamente gaussiano) no es válido. Este notebook
usa la banda analítica estándar de `statsmodels` (±1,96/√n = **±0,0483** para n=1.645), razonable
aquí porque la media de esta serie (≈3,5) está más lejos de cero y porque la sección 5.1 confirma
con ADF que la serie es estacionaria en media — condición bajo la cual esa banda es una
aproximación aceptable. Es una diferencia metodológica deliberada frente al notebook principal, no
un descuido.

### 4.2 ACF/PACF cruda — `tablas/08_acf_pacf_crudo.csv`, `figuras/fig3a`

| Rezago | ACF | PACF | ¿Fuera de banda (±0,0483)? |
| --- | --- | --- | --- |
| 1 | 0,0785 | 0,0786 | Sí |
| 7 | 0,0764 | 0,0698 | Sí |
| 14 | **0,1706** (máximo) | — | Sí |
| 21 | 0,1099 | — | Sí |
| 28 | 0,1125 | — | Sí |

Los múltiplos de 7 dominan la ACF cruda, con el pico en el rezago 14 — la firma de un ciclo
semanal, coherente con el perfil de la sección 3.3.

### 4.3 Cuánto es calendario — `tablas/09_acf_residuo_calendario.csv`, `figuras/fig3b`

Al restar a cada día la media de su grupo de calendario (día de la semana, feriado aparte):

| Rezago | ACF residuo | ¿Fuera de banda? | Lectura |
| --- | --- | --- | --- |
| 1 | 0,0745 | Sí | **sobrevive**: persistencia genuina de un día para el otro |
| 3, 4 | 0,0593 / 0,0704 | Sí | quedan fuera de banda, magnitud similar a ruido; no se interpretan como hallazgo aislado |
| 7 | −0,0329 | No | cae dentro de banda: era calendario |
| 14 | 0,0658 | Sí (más débil que en la cruda) | señalado, no explicado (ver limitaciones) |
| 15 | 0,0412 | No | — |
| 21, 28 | −0,0035 / −0,0029 | No | caen dentro de banda: eran calendario |

**Evidencia:** el calendario explica la mayor parte de los picos a múltiplos de 7 de la ACF cruda
(7, 21 y 28 caen dentro de la banda tras descontarlo). El rezago 1 sobrevive — coherente con el
hallazgo de `resumen_diagnostico_datos.md` (§5.2) de que 5 de 8 municipios muestran persistencia
residual a rezago 1. El rezago 14 sobrevive más débil que en la serie cruda; con una sola serie y
sin corrección por comparaciones múltiples (se probaron 30 rezagos) **no alcanza para afirmar un
ciclo quincenal genuino**.

**Ljung-Box** (`tablas/10_ljung_box.csv`): rechaza "no autocorrelación conjunta" con `p < 0,001`
en los tres horizontes probados (7, 14 y 30 rezagos) — hay estructura temporal estadísticamente
detectable, aunque cada rezago individual es de magnitud pequeña.

### 4.4 Dispersión por rezago — `tablas/11_dispersion_por_rezago.csv`, `figuras/fig4`

| Rezago | Correlación de Pearson |
| --- | --- |
| 1 | 0,0785 |
| 7 | 0,0768 |
| 14 | 0,1724 |
| 30 | 0,0021 |

Coeficientes chicos en los cuatro paneles (todos < 0,2); ninguna nube de dispersión se ve
claramente alineada sobre la diagonal — coherente con la lectura de la ACF: hay señal, es pequeña.

---

## 5. ¿Corresponde diferenciar o transformar el objetivo? — `tablas/12` a `14`, `figuras/fig5`

### 5.1 Estacionariedad: ADF y KPSS — `tablas/12_estacionariedad_adf_kpss.csv`

| Prueba | H0 | Estadístico | p-valor | Resultado (α=0,05) |
| --- | --- | --- | --- | --- |
| ADF | hay raíz unitaria | −7,0716 | 4,92 × 10⁻¹⁰ | **rechaza H0** (estacionaria) |
| KPSS | la serie es estacionaria | 1,2915 | ≤ 0,01 | **rechaza H0** (no estacionaria) |

**Evidencia — tensión que se declara, no se esconde:** el ADF rechaza la raíz unitaria con margen
amplio; el KPSS rechaza la estacionariedad. Las dos pruebas no son contradictorias en sentido
estricto: prueban hipótesis nulas opuestas y reaccionan a cosas distintas. El KPSS es sensible
también a un **nivel que deriva lentamente** sin llegar a una raíz unitaria — exactamente lo que
muestra la media anual no monótona de la sección 3.2.

**Lectura del equipo:** la serie es compatible con un proceso estacionario alrededor de un nivel
que deriva despacio entre años, no con una tendencia determinística fuerte ni con una caminata
aleatoria. No corresponde afirmar sin matices que "la serie es estacionaria".

### 5.2 Diferenciar empeora, no mejora — `tablas/13_efecto_diferenciacion.csv`

| Serie | ACF rezago 1 | ACF rezago 7 | Varianza |
| --- | --- | --- | --- |
| Cruda | 0,0785 | 0,0764 | 4,4297 |
| Diferenciada (d=1) | **−0,4621** | 0,0708 | 8,1661 |
| Diferenciada estacional (D=1, s=7) | 0,0722 | −0,5481 | 8,1740 |

**Evidencia:** diferenciar en nivel (d=1) no reduce la autocorrelación — la vuelve fuertemente
**negativa** en el rezago 1 (−0,46): es la firma clásica de sobrediferenciación. La diferenciación
estacional (s=7) genera el mismo problema en su propio rezago 7 (−0,55). Las dos aumentan la
varianza en vez de reducirla. **Ninguna ayuda; ambas perjudican.**

### 5.3 Relación media-varianza y Box-Cox — `tablas/14_diagnostico_transformacion.csv`

| Indicador | Valor |
| --- | --- |
| Ajuste lineal var ~ media (pendiente, intercepto) | 1,334 , −0,378 |
| Ajuste cuadrático var ~ media² (pendiente, intercepto) | 0,188 , 1,935 |
| Correlación media-varianza mensual | 0,468 |
| λ de Box-Cox (MLE, sobre serie + 1) | **0,4733** |

**Evidencia:**

- La relación media-varianza mensual se ajusta mejor con una recta cercana al origen
  (var ≈ 1,33·media − 0,38) que con una parábola: patrón de conteo con sobredispersión moderada y
  constante (cuasi-Poisson, razón ≈ 1,3, coherente con el índice de dispersión 1,26 de la sección
  3.1) — **no** el patrón de varianza proporcional al cuadrado de la media que el logaritmo está
  diseñado para corregir.
- El λ de Box-Cox estimado por máxima verosimilitud da **≈ 0,47**, cerca de **0,5** (raíz
  cuadrada, la transformación de Anscombe para datos de Poisson), lejos de **0** (logaritmo).
- Con 4,80 % de días en cero, ni el logaritmo ni Box-Cox están definidos sobre la serie original;
  los dos exigen desplazarla (+1).
- En la ACF a 14 rezagos, ni `log1p` ni Box-Cox cambian la estructura de forma apreciable frente a
  la serie cruda (`figuras/fig5`, panel derecho).

### 5.4 La decisión

**No corresponde aplicar diferenciación ni una transformación logarítmica o Box-Cox clásica al
objetivo.** Tres argumentos independientes se sostienen entre sí:

1. El ADF no encuentra raíz unitaria, y diferenciar sobrecorrige (§5.2).
2. La relación varianza-media es lineal, no cuadrática — el supuesto detrás del logaritmo no se
   cumple (§5.3).
3. El propio λ de Box-Cox estimado cae cerca de la raíz cuadrada (transformación nativa de un
   proceso de conteo), no cambia la estructura de autocorrelación, y exige un desplazamiento
   arbitrario por los ceros.

Es consistente con la decisión que ya toma `resumen_diagnostico_datos.md` (§5.1): tratar el
objetivo como una variable de **conteo** (familia Poisson/binomial negativa, desvianza de Poisson
como métrica) en vez de forzarlo a un esquema Box-Jenkins pensado para series continuas. Si algún
método del notebook de modelado exigiera igualmente estabilizar varianza, la evidencia acá respalda
la **raíz cuadrada**, no el logaritmo.

---

## 6. Limitaciones y frases que NO deben aparecer en el informe

| Limitación | Consecuencia |
| --- | --- |
| **Un solo municipio.** La conclusión de la sección 5 no está verificada en los otros siete. | Antes de fijar la transformación del objetivo para el modelo final, repetir al menos el diagnóstico de estacionariedad en 2-3 municipios de actividad distinta. |
| **Banda de ACF/PACF analítica**, no simulada. | Aproximación razonable a esta escala (§4.1), pero no citar el valor de la banda como exacto. |
| **Rezago 14 en el residuo de calendario** queda señalado, no explicado. | Declarar como observación, no como hallazgo confirmado; no se corrigió por comparaciones múltiples. |
| **No se evaluó el clima** en este notebook. | Ver `resumen_diagnostico_datos.md` §5.3 para el aporte del clima al panel completo. |
| **La recomendación de no transformar es sobre el objetivo definido hoy** (conteo diario por municipio). | Releer la sección 5 si cambia la definición del objetivo. |

**Frases que NO deben aparecer en el informe:**

- ❌ «La serie no es estacionaria y hay que diferenciarla.» → El ADF rechaza la raíz unitaria con
  amplio margen, y diferenciar empeora la ACF.
- ❌ «Hace falta un logaritmo para estabilizar la varianza.» → La relación media-varianza es
  lineal, no cuadrática; el λ de Box-Cox estimado (≈0,47) apunta a raíz cuadrada, no a logaritmo.
- ❌ «La serie es estacionaria», sin matices. → El KPSS rechaza esa hipótesis; hay una deriva de
  nivel lenta que el ADF no capta por no ser una raíz unitaria.
- ❌ «El verano tiene más siniestros por las vacaciones.» → Enero y febrero son los meses de
  índice estacional más bajo en esta serie (§3.4).
- ❌ «Hay un ciclo quincenal (14 días) confirmado.» → El rezago 14 queda fuera de banda tanto en
  la serie cruda como en el residuo de calendario, pero con una sola serie y sin corrección por
  comparaciones múltiples es una observación, no un hallazgo confirmado (§4.3).
- ❌ Citar cualquier cifra de este documento como válida para «Montevideo» o «el panel completo»
  sin aclarar que es de **Municipio C únicamente**.

---

## 7. Índice de artefactos

`experiments/diagnostico_datos_municipio/` — **16 tablas y 7 figuras**
(`tablas/15_artefactos.csv` lista todas con su tamaño).

| Eje | Tablas |
| --- | --- |
| Trazabilidad | `00_procedencia`, `00b_entorno` |
| Datos | `01_recorte_alcance`, `02_asignacion_municipios`, `03_verificacion_cruzada`, `04_resumen_serie_municipio_c` |
| Tendencia y estacionalidad | `05_tendencia_anual`, `06_perfil_semanal`, `07_indice_estacional_mensual` |
| ACF/PACF y dispersión | `08_acf_pacf_crudo`, `09_acf_residuo_calendario`, `10_ljung_box`, `11_dispersion_por_rezago` |
| Transformaciones | `12_estacionariedad_adf_kpss`, `13_efecto_diferenciacion`, `14_diagnostico_transformacion` |

**Figuras:**

| Figura | Qué muestra | Sección de este documento |
| --- | --- | --- |
| `fig1_tendencia_municipio_c.png` | Serie diaria, medias móviles de 30/90 días y media anual | 3.2 |
| `fig2a_perfil_semanal_municipio_c.png` | Media de siniestros por día de la semana | 3.3 |
| `fig2b_estacionalidad_anual_municipio_c.png` | Índice estacional mensual y tendencia de `seasonal_decompose` | 3.4 |
| `fig3a_acf_pacf_crudo_municipio_c.png` | ACF y PACF de la serie cruda (`statsmodels`) | 4.2 |
| `fig3b_acf_residuo_calendario_municipio_c.png` | ACF cruda vs. ACF del residuo tras descontar calendario | 4.3 |
| `fig4_dispersion_lags_municipio_c.png` | Dispersión de yₜ contra yₜ₋ₖ para k=1,7,14,30 | 4.4 |
| `fig5_transformaciones_municipio_c.png` | Relación media-varianza mensual y ACF cruda vs. log1p vs. Box-Cox | 5.3 |

---

## 8. Qué queda pendiente

1. **Repetir el diagnóstico de estacionariedad (§5) en 2-3 municipios adicionales** de actividad
   distinta (por ejemplo el de mayor y el de menor actividad), para verificar si la decisión de no
   transformar el objetivo generaliza a todo el panel o es propia de Municipio C.
2. **Si se decide un método que exija varianza estabilizada** en el notebook de modelado, evaluar
   la raíz cuadrada (respaldada por el λ de Box-Cox ≈0,47 estimado acá) en vez de logaritmo.
3. **El rezago 14** (§4.3) queda como observación abierta: no se investigó su origen (¿quincena de
   pago, patrón de recolección de datos, azar?). Si se quiere usar en el modelado, evaluarlo como
   variable candidata bajo el mismo protocolo que `resumen_diagnostico_datos.md` (§5.2) usa para
   el rezago 1, no asumirlo.
