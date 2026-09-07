# Resumen del diagnóstico de datos — Montevideo

**Notebook:** [`notebooks/diagnostico_datos.ipynb`](../notebooks/diagnostico_datos.ipynb)
**Artefactos:** `experiments/diagnostico_datos/` (36 tablas CSV y 3 figuras PNG)
**Fecha de ejecución:** 2026-09-04
**Alcance:** Montevideo, 2021-01-01 a 2025-12-31, unidad de análisis **(día, barrio)**

---

## 0. Cómo usar este documento

Este archivo es **contexto autocontenido** para redactar la documentación del proyecto (informe
técnico, presentaciones, defensa ante el tribunal) sin necesidad de abrir el repositorio. Reúne
todo lo que el diagnóstico de datos encontró, con la referencia al artefacto que respalda cada
cifra.

**Reglas que quien redacte debe respetar:**

1. **Ninguna cifra sin artefacto.** Todos los números de este documento salen de una ejecución
   real y están acompañados de la tabla que los respalda (`tablas/NN_nombre.csv`). No inventar,
   estimar ni redondear "para el ejemplo". Si hace falta un número que no está acá, marcarlo como
   `<!-- PENDIENTE: ... -->` en lugar de completarlo.
2. **Distinguir evidencia de inferencia.** Este documento separa *lo que los datos muestran* de
   *lo que el equipo concluye*. Al redactar, usar "los resultados sugieren", no "queda
   demostrado".
3. **No escribir Introducción ni Marco teórico** a partir de este documento: esas dos secciones
   las redacta el equipo a mano (regla del proyecto).
4. **Respetar los límites de la sección 6.** Hay afirmaciones que estos datos *no* sostienen;
   están listadas explícitamente y no deben aparecer en el informe.

---

## 1. Para qué existe el diagnóstico

El Entregable 2 de la guía PAA (sección 5.2) exige, como primer resultado, *«un diagnóstico de
calidad, adecuación, cobertura y limitaciones de los datos»*, y la sección 6.1 pide revisar
calidad, cobertura, representatividad, sesgos y restricciones de uso, además de verificar que no
se incorpore información no disponible en el momento real de la predicción.

| Eje | Pregunta que responde |
| --- | --- |
| Calidad | ¿Los registros son completos, consistentes y precisos para lo que se les va a pedir? |
| Cobertura | ¿Qué territorio, qué período y qué fracción de la unidad de análisis observan? |
| Adecuación | ¿La variable objetivo y las variables disponibles sostienen el problema planteado? |
| Limitaciones | ¿Qué no puede afirmarse con estos datos y qué riesgos introduce cada decisión? |

El notebook **recalcula todo desde las fuentes crudas**, incluida la asignación de cada siniestro
a su barrio. No depende de que `data/processed/` esté construido: cuando lo está, lo usa para
*contrastar* su propia reconstrucción contra la salida del ETL (sección 5). Eso lo convierte en
una **verificación independiente** del pipeline, no en un resumen de él.

> **Cambio de alcance.** Hasta 2026-09-02 el diagnóstico cubría el país entero (224.694
> siniestros, 2018–2025, celdas de 1 km) e incluía secciones sobre división cronológica,
> estabilidad del universo de zonas y elección de granularidad. Esas decisiones ya están tomadas
> —Montevideo, barrios oficiales, 2021+— y esas secciones se retiraron por ser materia del
> notebook de modelado. Los hallazgos que sobrevivieron **se recalcularon** sobre los datos
> vigentes; no se copiaron.

---

## 2. Fuentes y trazabilidad

`tablas/00_procedencia.csv`

| Fuente | Archivo | Tamaño | sha256 (prefijo) |
| --- | --- | --- | --- |
| Siniestros | `data/raw/uru_siniestros_unificado.csv` | 26,19 MB | `48a8a7e8…` |
| Barrios | `data/raw/barrios_montevideo.geojson` | 0,98 MB | `a03e8927…` |
| Clima | `data/raw/clima_montevideo.csv` | 0,08 MB | `f40e6c3c…` |

**Siniestros.** Heredado del Proyecto de Ingeniería de Datos (PID) del mismo equipo. Fuente
original: UNASEV. Cubre el país entero, 2018–2025, 224.694 registros × 11 columnas.

**Barrios.** Capa oficial de la Intendencia de Montevideo, obtenida de su GeoServer institucional
(`montevideo.gub.uy/app/geoserver`), capa `mapstore-tematicas:zon_v_sig_barrios`, descargada por
WFS `GetFeature` en GeoJSON (`EPSG:4326`) el **2026-09-04**. 62 polígonos, correspondientes a la
división oficial en barrios. Licencia: el servicio declara `Fees: none` / `AccessConstraints:
none` en su `GetCapabilities`.

**Clima.** Open-Meteo, archivo histórico reanalizado, serie diaria única para el departamento
(punto −34,87 / −56,17), 2021-01-01 a 2025-12-31.

### Recorte al alcance del proyecto

| Paso | Registros | % del archivo | Artefacto |
| --- | --- | --- | --- |
| Registros del archivo | 224.694 | 100,0 % | `02_recorte_alcance` |
| Tras filtrar `MONTEVIDEO` | 62.427 | 27,8 % | `02_recorte_alcance` |
| Tras filtrar `Fecha >= 2021-01-01` | 39.676 | 17,7 % | `02_recorte_alcance` |
| Tras eliminar 96 duplicados exactos | **39.580** | 17,6 % | `05_duplicados` |
| Tras descartar 11 que caen fuera de todo polígono | **39.569** | 17,6 % | `09_calidad_capa_barrios` |

Las dos últimas filas no están en `02_recorte_alcance.csv`: se derivan de los conteos de
`05_duplicados.csv` y `09_calidad_capa_barrios.csv`, que es donde hay que ir a verificarlas.

**Período diagnosticado:** 1.826 días (2021-01-01 a 2025-12-31).

---

## 3. Calidad

### 3.1 Completitud — `tablas/04_completitud.csv`

El archivo **no trae valores nulos**: los faltantes vienen codificados como texto (`SIN DATOS` y
variantes). Contarlos como categoría sería subestimar el problema.

| Columna | Centinelas en el país | **Centinelas en Montevideo** |
| --- | --- | --- |
| `Localidad` | 17,91 % | **4,45 %** (1.765 registros) |
| `Calle` | 12,37 % | **2,33 %** (925 registros) |
| `Tipo de Siniestro` | 0,01 % | 0,03 % (10 registros) |
| `Gravedad`, `Dia Semana`, `Departamento` | 0,00 % | 0,00 % |

**Evidencia:** el recorte a Montevideo mejora sustancialmente la completitud.
**Inferencia del equipo:** el problema de calidad que dominaba el diagnóstico nacional era, en
buena medida, un problema del interior del país.

**Decisión: no se imputa.** Las columnas afectadas son descriptivas y **ninguna se usa como
predictora** — el barrio sale de la geometría, no del texto de `Localidad`. Se declara el conteo
en lugar de omitirlo, que es lo que la guía pide cuando la imputación no corresponde.

### 3.2 Duplicados — `tablas/05_duplicados.csv`

| Indicador | Valor |
| --- | --- |
| Duplicados exactos en el archivo | 347 (0,15 %) |
| Duplicados exactos en el recorte | **96 (0,24 %)** |
| Grupos con repetición | 77 |
| Repeticiones en el grupo mayor | **10** |

**Evidencia:** existen grupos de hasta diez filas idénticas byte a byte.
**Inferencia:** un siniestro no se repite diez veces en la misma esquina, a la misma hora, con el
mismo tipo y la misma gravedad — se trata de un artefacto de carga, no de eventos distintos.

**Efecto sobre la variable objetivo:** sin deduplicar, el máximo de siniestros en un día y una
zona quedaba inflado por repeticiones. Con la grilla anterior, el máximo declarado era 11 y
correspondía a **10 copias del mismo registro más uno distinto**: 2 siniestros reales.

**Limitación del criterio, a declarar:** el dataset no tiene identificador de siniestro, de modo
que dos siniestros reales con atributos idénticos serían indistinguibles de un duplicado de carga.
La eliminación es una decisión conservadora sobre la cola alta del objetivo.

### 3.3 Consistencia interna — `tablas/06_consistencia.csv`, `06b_consistencia_otros.csv`

La columna `Dia Semana` es redundante respecto de `Fecha`, y esa redundancia permite **verificar el
formato de fecha contra evidencia independiente del propio archivo**.

| Formato probado | Fechas no parseables | Coincidencia con `Dia Semana` |
| --- | --- | --- |
| `%m/%d/%Y` | 0 | **100,0000 %** |
| `%d/%m/%Y` | 133.356 | 6,7955 % |

**Consecuencia importante:** esto **refuta la suposición del ETL del PID**, que probaba varios
formatos en cascada (`parsear_fecha_mixta`) asumiendo que el archivo los mezclaba. El archivo es
homogéneo. La suposición era peligrosa porque una fecha como `05/06/2021` parsea con los dos
formatos y da días distintos, sin avisar.

Otras comprobaciones, todas en cero: `Hora` fuera de 0–23, registros de otro departamento, fechas
fuera del período. La columna `fixed` toma **un único valor**: no aporta información y no puede
usarse como indicador de calidad de la geocodificación, aunque su nombre lo sugiera.

### 3.4 Precisión espacial — `tablas/07_precision_espacial.csv`

| Indicador | Valor |
| --- | --- |
| Coordenadas múltiplo de 5 m | 100,00 % |
| Coordenadas distintas | 8.088 |
| Siniestros por coordenada (media) | 4,9 |
| Siniestros en la coordenada más repetida | 122 (**0,31 %** del recorte) |
| Las 10 coordenadas más repetidas concentran | 1,97 % |
| Coordenadas nulas o ≤ 0 | 0 |

**Evidencia:** resolución de 5 m, miles de coordenadas distintas, concentración baja en la más
repetida.
**Inferencia:** el patrón es el de una geocodificación **a esquina o tramo de calle**, no a un
centroide genérico. Esto es lo que hace viable la asignación por intersección punto-polígono.

**Limitación a declarar:** un punto ajustado a la esquina puede caer del lado equivocado de un
límite de barrio cuando ese límite corre por el eje de la calle. El error afectaría a siniestros
individuales cerca de los bordes, no al orden de magnitud por barrio.

### 3.5 Validez temporal — `tablas/08_validez_temporal.csv`

| Indicador | Valor |
| --- | --- |
| Días del período | 1.826 |
| **Días sin ningún siniestro** | **0** |
| Mínimo / mediana / máximo diario | 4 / 22,0 / 44 |
| Fecha del mínimo / del máximo | 2022-01-16 / 2025-12-11 |

La serie diaria del departamento está completa, sin huecos. Un día sin registros habría sido
sospechoso de falla del sistema de carga más que de ausencia real de siniestros, y no ocurre.

### 3.6 Calidad de la asignación a barrios — `tablas/09_calidad_capa_barrios.csv`

La zona sale de una **intersección punto-polígono** entre las coordenadas UTM del siniestro y la
capa de barrios. **No se geocodifica ninguna dirección.**

| Indicador | Valor |
| --- | --- |
| Polígonos en la capa | 62 |
| Nombres distintos | 62 |
| Barrios con al menos un siniestro | **62** |
| Siniestros asignados | 39.569 |
| **Siniestros fuera de todo polígono** | **11 (0,03 %)** |

**Decisión:** se descartan y se documenta el conteo (detalle en `09b_siniestros_sin_barrio.csv`),
en lugar de reasignarlos al barrio más cercano. La reasignación introduciría una decisión
arbitraria sobre casos que no cambian ninguna conclusión.

### 3.7 Calidad de la serie climática — `tablas/10_calidad_clima.csv`

| Indicador | Valor |
| --- | --- |
| Días en la caché | 1.826 |
| Días del período cubiertos | **1.826 de 1.826** |
| Fechas duplicadas | 0 |
| Celdas faltantes | **0** |
| Temperatura media fuera de −10…45 °C | 0 |
| Precipitación negativa | 0 |

Sin faltantes y con el período completo: **no corresponde imputar** el clima.

**Limitación de diseño, no de calidad:** se usa **una sola serie para todo el departamento**. A
resolución diaria las variables meteorológicas son prácticamente uniformes sobre unos 200 km²
urbanos, de modo que el supuesto es razonable, pero significa que el clima **no puede explicar
ninguna diferencia entre barrios**: aporta sólo variación temporal, la misma para las 62 zonas.
Esto tiene consecuencias directas en la sección 5.3.

---

## 4. Cobertura

### 4.1 Cobertura temporal — `tablas/11_cobertura_temporal_anual.csv`, `figuras/fig1_cobertura_temporal.png`

| Año | Siniestros | Media diaria | Variación |
| --- | --- | --- | --- |
| 2021 | 6.893 | 18,88 | — |
| 2022 | 7.665 | 21,00 | +11,2 % |
| 2023 | 7.873 | 21,57 | +2,7 % |
| 2024 | 8.398 | 22,95 | +6,7 % |
| 2025 | 8.740 | 23,95 | +4,1 % |

Hay una **tendencia creciente sostenida** en todo el período. Esto importa para el diseño de
evaluación: un modelo entrenado sobre los primeros años se evalúa sobre un régimen de
siniestralidad más alto.

#### El filtro de 2021 no elimina el régimen de la pandemia — `tablas/12_pandemia_residual.csv`

| Período | Siniestros | Días | Media diaria |
| --- | --- | --- | --- |
| ene–jun **2021** | 2.957 | 181 | **16,34** |
| ene–jun 2022–2025 | 15.512 | 725 | **21,40** |
| **Diferencia** | | | **−23,6 %** |

**Evidencia:** el primer semestre de 2021 tiene una siniestralidad marcadamente inferior a la de
los mismos meses de los años siguientes.
**Inferencia:** en Uruguay la ola de COVID y las restricciones de movilidad fueron justamente en
ese semestre. La justificación del filtro —«empezar en 2021 para que el modelo no vea la
pandemia»— **no se sostiene con los datos**: el recorte excluye 2020 pero conserva el semestre más
afectado.

**Decisión del equipo:** mantener 2021 completo y **declarar el sesgo en el informe**. La
alternativa —empezar el 2021-07-01— cuesta seis meses de datos y es un cambio de una línea en el
notebook de preparación. Consecuencia a declarar: el conjunto de entrenamiento contiene un tramo
con un régimen de movilidad que no volverá a repetirse, lo que sesga a la baja cualquier tasa
histórica estimada sobre los primeros meses de la serie.

### 4.2 Cobertura territorial — `tablas/13_cobertura_barrios.csv`, `13b_concentracion_territorial.csv`, `figuras/fig2_cobertura_territorial.png`

| Indicador | Valor |
| --- | --- |
| Barrios de la capa | 62 |
| **Barrios con al menos un siniestro** | **62** |
| Siniestros — mínimo por barrio | **225** |
| Siniestros — mediana por barrio | 570 |
| Siniestros — máximo por barrio | 1.939 |
| Razón máximo/mínimo | 8,6× |
| Barrios que acumulan el 50 % | 19 |
| Barrios que acumulan el 90 % | 49 |

**Barrios más activos:** UNIÓN (1.939 · 4,90 %), CORDÓN (1.694 · 4,28 %), AGUADA (1.204 · 3,04 %),
CENTRO (1.197 · 3,03 %), MERCADO MODELO Y BOLÍVAR (1.138), CERRO (1.122), POCITOS (1.081).
**Menos activos:** LA BLANQUEADA (225), BARRIO SUR (241), JACINTO VERA (249), PALERMO (261).

**Este es el resultado que habilita el experimento del docente.** Ningún barrio queda sin
siniestros y el menos activo tiene 225 en el período, de modo que **todos tienen soporte
suficiente** para estimarles una tasa. Con la grilla de 1 km anterior había 80 celdas con 5
siniestros o menos y 28 con uno solo, lo que volvía inviable reservar zonas para evaluar
generalización.

**Limitación de representatividad, a declarar:** el mapa refleja **dónde se registran** siniestros,
no dónde son más probables por unidad de exposición. Sin datos de tránsito no se puede normalizar
por volumen de vehículos, de modo que un barrio muy transitado aparecerá arriba aunque su riesgo
por viaje sea bajo.

### 4.3 El panel día × barrio — `tablas/14_panel_dia_barrio.csv`

| Indicador | Valor |
| --- | --- |
| Filas del panel (días × barrios) | **113.212** |
| Filas con al menos un siniestro | 31.747 |
| **Densidad (filas no nulas)** | **28,04 %** |
| Ceros | 71,96 % |
| Media de siniestros por fila | 0,3495 |
| Máximo en una fila | 7 |

Comparación con la zonificación anterior (grilla de 1 km, 403 celdas): el panel tenía 735.878
filas y **95,08 % de ceros**. La agregación por barrios **reduce drásticamente la escasez**.

**Consecuencia de modelado:** con esta densidad, una pérdida de conteo (Poisson o Tweedie) tiene
material suficiente y **no hace falta balancear**. Con el panel anterior el objetivo era casi
binario y eso obligaba a un tratamiento distinto.

### 4.4 Variables exógenas — `tablas/15_cobertura_calendario.csv`, `16_feriados.csv`

| `tipo_dia` | Días | % | Media de siniestros/día |
| --- | --- | --- | --- |
| `entre_semana` | 1.232 | 67,5 % | **23,75** |
| `fin_semana` | 504 | 27,6 % | **17,73** |
| `feriado` | 90 | 4,9 % | **15,41** |

La variable **discrimina**: feriados y fines de semana no se comportan como los días hábiles.

**Un problema detectado y ya resuelto** (`tablas/16_feriados.csv`): la configuración por omisión de
la biblioteca `holidays` para Uruguay reconoce **25 feriados** en el período, mientras que
`categories=("public", "bank")` reconoce **90**. Los **65 días omitidos** incluyen **Carnaval y
Semana de Turismo**, los dos períodos de mayor alteración de la movilidad del año. El ETL vigente
usa la configuración correcta. Detalle en `16b_feriados_omitidos_por_defecto.csv`.

El **clima está integrado** (sección 3.7), lo que cierra el otro hueco que el diagnóstico
reportaba como abierto en su versión nacional.

---

## 5. Adecuación

### 5.1 La variable objetivo — `tablas/17_distribucion_objetivo.csv`, `18_dispersion_objetivo.csv`

| `n_siniestros` | Filas | % |
| --- | --- | --- |
| 0 | 81.465 | 71,958 % |
| 1 | 25.332 | 22,376 % |
| 2 | 5.248 | 4,636 % |
| 3 | 974 | 0,860 % |
| 4 | 158 | 0,140 % |
| 5 | 26 | 0,023 % |
| 6 | 6 | 0,005 % |
| 7 | 3 | 0,003 % |

| Indicador | Valor |
| --- | --- |
| Media | 0,3495 |
| Varianza | 0,3957 |
| **Índice de dispersión (var/media)** | **1,132** |

**Evidencia:** la varianza casi iguala a la media.
**Inferencia:** es la firma de un proceso de **Poisson**, con una sobredispersión leve.

**Consecuencia para el protocolo de evaluación:** las métricas deben medir **calibración y
ordenamiento** de una intensidad esperada, no exactitud puntual del conteo. Un error absoluto medio
sobre un objetivo así premia predecir siempre cerca de cero y no informa nada útil. La
recomendación derivada es **desvianza de Poisson** como métrica principal, acompañada de
calibración por estrato de actividad.

### 5.2 Señal temporal — `tablas/19_senal_temporal_barrios.csv`, `20_senal_serie_agregada.csv`, `20b_varianza_calendario.csv`, `figuras/fig3_senal_temporal.png`

Éste es **el hallazgo de mayor consecuencia del diagnóstico**. Se recalculó íntegramente sobre los
barrios, porque una conclusión obtenida con celdas de 1 km no se hereda al cambiar de granularidad.

El contraste no es contra cero, sino contra lo que produciría el **puro azar**: se simulan 400
series de Poisson con la tasa media de cada barrio y se compara la autocorrelación observada contra
la banda que generan esas simulaciones.

**A nivel de barrio:**

| Rezago | ACF mediana | ACF máxima | Banda nula Poisson (p97,5) | Barrios sobre la banda | Esperables por azar |
| --- | --- | --- | --- | --- | --- |
| 1 | 0,0137 | 0,0724 | 0,0449 | **7 de 62** | 1,6 |
| 7 | 0,0101 | 0,0838 | 0,0455 | **8 de 62** | 1,6 |

**Evidencia:** la autocorrelación mediana cae muy por debajo de la banda nula. Pero los barrios que
la superan (7 y 8) son **más de los que produciría el azar** (≈1,6 al percentil 97,5).

**Inferencia, enunciada con cuidado:** en la enorme mayoría de los barrios no se detecta señal
temporal de corto plazo; en una minoría parece haber algo de estructura real, pero **su magnitud es
despreciable para el modelado** — incluso la autocorrelación más alta observada (0,084) explica
menos del 1 % de la varianza de esa serie. La distinción importa: una cosa es «no se detecta señal»
y otra «no existe». Lo que estos datos sostienen es lo primero.

**A nivel del departamento sí hay señal, y es de calendario:**

| Serie | ACF rezago 1 | ACF rezago 7 |
| --- | --- | --- |
| Serie cruda del departamento | 0,2379 | **0,3459** |
| Residuo tras descontar `tipo_dia` | 0,2438 | **0,2427** |

El pico en el rezago 7 es estacionalidad semanal, y `tipo_dia` la captura **en parte** (0,346 →
0,243). Queda autocorrelación en el residuo: días buenos y días malos que ninguna de las variables
disponibles anticipa.

**Varianza de la serie diaria del departamento explicada por el calendario:**

| Bloque | % de varianza explicada |
| --- | --- |
| `tipo_dia` | 21,0 % |
| Día de la semana | 19,5 % |
| Mes | 9,0 % |
| `tipo_dia` + mes | 30,2 % |
| Día de la semana + mes | 30,8 % |

**Consecuencia de modelado, sin adornos:** una regla de persistencia por zona («ayer hubo, hoy
habrá») **no tiene fundamento en estos datos**. La línea base defendible es **tasa histórica del
barrio × factor de calendario**, y cualquier modelo más complejo debe justificarse contra ella con
el mismo protocolo.

### 5.3 Qué puede aportar cada bloque de variables — `tablas/21_aporte_bloques_variables.csv`, `21b_descomposicion_varianza.csv`

Se compara la **desvianza de Poisson** de cuatro predictores, todos **oráculos calculados en
muestra**: a cada uno se le entrega directamente la media empírica del grupo correspondiente. Cada
valor es por tanto una **cota superior** — ningún modelo real que use sólo esas variables la va a
superar.

| Información disponible | Desvianza de Poisson | Mejora sobre la constante |
| --- | --- | --- |
| Constante global (sin información) | 0,94110 | — |
| **Sólo variables de día (clima + calendario) — techo** | 0,90784 | **−3,5 %** |
| **Sólo tasa histórica del barrio** | 0,85280 | **−9,4 %** |
| Barrio × día | 0,81954 | −12,9 % |

Descomposición de varianza (`21b`):

| Componente | Varianza | % de la total |
| --- | --- | --- |
| Total del objetivo | 0,39573 | 100,0 % |
| **Entre barrios** | 0,03476 | **8,8 %** |
| **Entre días** | 0,01130 | **2,85 %** |

**Éste es el resultado con mayor consecuencia práctica para el diseño de variables.**

**Evidencia:** las variables exógenas previstas —clima, día de la semana, feriados— son **todas
variables de día**. Ninguna distingue un barrio de otro: para una fecha dada, los 62 barrios reciben
exactamente los mismos valores. Su techo conjunto es −3,5 %. La identidad del barrio aporta −9,4 %,
casi el triple.

**Inferencia:** un modelo construido sólo con clima y calendario **predeciría el mismo número para
todos los barrios cada día**, que es precisamente lo que el producto no puede hacer. Hace falta al
menos una variable de nivel de zona —la tasa histórica del barrio, ajustada sólo con datos de
entrenamiento— y ésa es la construcción que el notebook de modelado debe abordar primero.

### 5.4 Adecuación al objetivo del producto — `tablas/22_adecuacion_objetivo.csv`

| Pregunta | Respuesta | Fundamento |
| --- | --- | --- |
| ¿Se puede predecir el conteo diario por barrio? | **Sí** | densidad suficiente; objetivo de tipo Poisson (5.1) |
| ¿Se puede predecir dónde ocurrirá el próximo siniestro? | **No** | sin persistencia sobre el azar a nivel barrio-día (5.2) |
| ¿Se puede ordenar barrios por riesgo esperado? | **Sí** | la tasa histórica es estable y aporta la mayor parte de la señal (5.3) |
| ¿Se puede estimar riesgo por unidad de exposición? | **No** | no hay datos de tránsito |
| ¿Se puede modelar por gravedad o franja horaria? | **No con el conjunto vigente** | el ETL descarta esas columnas |
| ¿Se puede evaluar en barrios no vistos al entrenar? | **Sí** | los 62 tienen soporte; ninguna variable identifica al barrio |

**Las filas 2 y 4 acotan honestamente el alcance del producto.** El sistema puede **ordenar y
calibrar riesgo esperado por barrio**, que es lo que sirve para asignar recursos de fiscalización;
**no puede anticipar siniestros individuales**, y no hay dato disponible que lo permita.
Presentarlo de otro modo ante el tribunal sería insostenible.

---

## 6. Limitaciones y lo que NO puede afirmarse

`tablas/24_limitaciones.csv` — diez limitaciones, cada una con la sección que la sustenta y el
tratamiento que recibe.

| Limitación | Sección | Cómo se trata |
| --- | --- | --- |
| Régimen de pandemia dentro del período | 4.1 | Se declara; alternativa: iniciar 2021-07-01 |
| Sin señal temporal de corto plazo por barrio | 5.2 | Línea base = tasa × calendario |
| Variables exógenas sin variación espacial | 3.7, 5.3 | Construir tasa histórica del barrio |
| Clima observado, no pronosticado | 2 | Declararlo: el desempeño medido es cota optimista |
| Sin datos de exposición (tránsito) | 4.2, 5.4 | Limitar afirmaciones a conteo esperado |
| Duplicados exactos en la fuente | 3.2 | Eliminados; criterio declarado |
| Faltantes encubiertos como texto | 3.1 | No se imputa; se declara el conteo |
| Siniestros fuera de todo polígono | 3.6 | Se descartan (11); se documenta |
| Catálogo y estratos sobre todo el período | 4.2 | Recalcular estrato sólo con entrenamiento |
| **Subregistro de siniestros** | **—** | **No es medible con estos datos** |

### Frases que NO deben aparecer en el informe

- ❌ «El modelo predice dónde ocurrirá el próximo siniestro.» → Sólo ordena y calibra riesgo
  esperado por barrio y día.
- ❌ «El barrio X es el más peligroso.» → Es el que **registra** más siniestros. Sin exposición no
  se puede hablar de peligrosidad por viaje.
- ❌ «Los datos cubren todos los siniestros de Montevideo.» → Cubren los **registrados**. El
  subregistro es desconocido.
- ❌ «El clima explica la siniestralidad.» → Aporta, junto con el calendario, un techo de −3,5 % de
  desvianza, y no explica diferencias entre barrios.
- ❌ «Queda demostrado que no hay señal temporal.» → **No se detecta** señal aprovechable; en 7–8
  barrios de 62 hay algo por encima de la banda nula, de magnitud despreciable.

### Sobre el subregistro

**No es medible con los propios datos.** El archivo contiene los siniestros que fueron registrados;
la fracción no registrada —típicamente los leves o sin lesionados que no generan intervención— es
desconocida y probablemente no uniforme entre barrios. Si la propensión a registrar variara entre
barrios, el ordenamiento estaría sesgado de una forma que este diagnóstico **no puede detectar**.
Cuantificarlo exigiría una fuente externa de contraste que el proyecto no tiene. Declararlo es
parte del diagnóstico.

---

## 7. Verificación cruzada con el ETL — `tablas/23_coherencia_etl.csv`

El diagnóstico reconstruye el panel desde las fuentes crudas de forma **independiente** del ETL. La
comparación es una verificación real: una discrepancia significaría que uno de los dos notebooks
tiene un error.

| Comprobación | Diagnóstico (recalculado) | ETL (`data/processed`) | Resultado |
| --- | --- | --- | --- |
| Filas del panel | 113.212 | 113.212 | ✅ coincide |
| Siniestros totales | 39.569 | 39.569 | ✅ coincide |
| Zonas | 62 | 62 | ✅ coincide |
| Días | 1.826 | 1.826 | ✅ coincide |
| Máximo del objetivo | 7 | 7 | ✅ coincide |

**Las cinco comprobaciones coinciden.** Dos implementaciones independientes de la asignación
punto-polígono y del armado del panel llegan al mismo resultado.

---

## 8. Índice de artefactos

`experiments/diagnostico_datos/` — 36 tablas y 3 figuras. `tablas/25_artefactos.csv` lista todas.

**Figuras:**

| Figura | Qué muestra | Sección |
| --- | --- | --- |
| `fig1_cobertura_temporal.png` | Serie mensual de siniestros, con el 1.º semestre de 2021 sombreado | 4.1 |
| `fig2_cobertura_territorial.png` | Mapa coroplético de los 62 barrios por siniestros acumulados | 4.2 |
| `fig3_senal_temporal.png` | ACF por barrio vs banda nula (izq.) y ACF de la serie agregada (der.) | 5.2 |

**Tablas principales por eje:**

| Eje | Tablas |
| --- | --- |
| Trazabilidad | `00_procedencia`, `00b_entorno`, `01_esquema_crudo`, `02_recorte_alcance` |
| Disponibilidad | `03_disponibilidad_variables`, `03b_disponibilidad_exogenas` |
| Calidad | `04_completitud`, `05_duplicados`, `06_consistencia`, `06b`, `07_precision_espacial`, `08_validez_temporal`, `09_calidad_capa_barrios`, `09b`, `10_calidad_clima`, `10b` |
| Cobertura | `11_cobertura_temporal_anual`, `11b`, `12_pandemia_residual`, `13_cobertura_barrios`, `13b`, `14_panel_dia_barrio`, `15_cobertura_calendario`, `16_feriados`, `16b` |
| Adecuación | `17_distribucion_objetivo`, `18_dispersion_objetivo`, `19_senal_temporal_barrios`, `20_senal_serie_agregada`, `20b`, `21_aporte_bloques_variables`, `21b`, `22_adecuacion_objetivo` |
| Verificación | `23_coherencia_etl` |
| Limitaciones | `24_limitaciones` |

**Antes de citar cualquier cifra:** verificar que los `sha256` de `00_procedencia.csv` sigan siendo
los de las fuentes vigentes. Si alguna fuente cambió, hay que volver a ejecutar el notebook.

---

## 9. Qué queda pendiente

Lo que este diagnóstico **deja planteado** y corresponde al notebook de modelado:

1. **Construir la variable de nivel de zona** (tasa histórica del barrio), ajustada sólo con el
   tramo de entrenamiento. Es el aporte más grande disponible (5.3) y hoy no existe.
2. **Definir las particiones cronológicas** con el conjunto de prueba reservado. El diagnóstico
   *no* las define: es decisión del protocolo de evaluación.
3. **Recalcular el estrato de actividad sólo con entrenamiento** antes de usarlo para reservar
   barrios del «megamodelo». Hoy es descriptivo, calculado sobre todo el período.
4. **Fijar las métricas**: desvianza de Poisson como principal, más calibración por estrato.
5. **Decidir el balanceo**: primera opción a probar, pérdida de Poisson o Tweedie, que maneja el
   exceso de ceros nativamente.
6. **Implementar la línea base** (tasa del barrio × factor de calendario) y evaluarla con el
   protocolo definitivo.
7. **Decidir el filtro de 2021** (4.1): mantener y declarar el sesgo, o mover el inicio.
