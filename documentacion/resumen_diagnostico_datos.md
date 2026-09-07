# Resumen del diagnóstico de datos — Montevideo por municipios

**Notebook:** [`notebooks/diagnostico_datos.ipynb`](../notebooks/diagnostico_datos.ipynb)
**Artefactos:** `experiments/diagnostico_datos/` (43 tablas CSV y 3 figuras PNG)
**Fecha de ejecución:** 2026-09-07
**Alcance:** Montevideo, **2021-07-01 a 2025-12-31**, unidad de análisis **(día, municipio)**

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

> ### ⚠️ Antes que nada: este documento reemplaza a dos versiones anteriores
>
> El diagnóstico se rehízo tres veces al cambiar el alcance del proyecto. **Las cifras de las dos
> versiones anteriores están superadas y no deben citarse.**
>
> | Versión | Alcance | Estado |
> | --- | --- | --- |
> | 2026-08-30 | País entero, celdas de 1 km, 2018–2025 | **superada** |
> | 2026-09-04 | Montevideo, 62 barrios, desde 2021-01-01 | **superada** |
> | **2026-09-07** | **Montevideo, 8 municipios, desde 2021-07-01** | **vigente** |
>
> No es un cambio cosmético. Al pasar de barrios a municipios el porcentaje de ceros del panel
> cae de 71,96 % a **8,60 %**, y **dos conclusiones centrales cambian de signo**: ahora *sí* se
> detecta señal temporal a rezago 1 (antes no), y el aporte relativo de calendario y zona se
> reordena. Cualquier borrador de informe escrito contra la versión de barrios hay que revisarlo
> entero, no parchearlo.

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
a su municipio. No depende de que `data/processed/` esté construido: cuando lo está, lo usa para
*contrastar* su propia reconstrucción contra la salida del ETL (sección 7). Eso lo convierte en
una **verificación independiente** del pipeline, no en un resumen de él.

### Las dos decisiones de alcance que fija esta versión

Ambas surgieron de la reunión de seguimiento con el docente del **2026-09-07**, y ambas están
**justificadas con evidencia dentro del notebook**, no adoptadas por decreto. Esto importa para
la defensa: si el tribunal pregunta por qué ocho zonas y por qué julio, hay tabla que mostrar.

| Decisión | Justificación | Dónde |
| --- | --- | --- |
| La zona pasa de **barrio (62)** a **municipio (8)** | El municipio es la unidad con gobierno propio y competencias en tránsito: una predicción por municipio se puede accionar | §4.2, §5.4 |
| La serie empieza el **2021-07-01** | El 1.er semestre de 2021 está bajo régimen de movilidad de pandemia; se demuestra en tres pasos | §4.1 |

---

## 2. Fuentes y trazabilidad

`tablas/00_procedencia.csv`

| Fuente | Archivo | Tamaño | sha256 (prefijo) |
| --- | --- | --- | --- |
| Siniestros | `data/raw/uru_siniestros_unificado.csv` | 26,19 MB | `48a8a7e8…` |
| **Municipios** | `data/raw/municipios_montevideo.geojson` | 2,87 MB | `ed0ba13e…` |
| Clima | `data/raw/clima_montevideo.csv` | 0,08 MB | `f40e6c3c…` |

**Siniestros.** Heredado del Proyecto de Ingeniería de Datos (PID) del mismo equipo. Fuente
original: UNASEV. Cubre el país entero, 2018–2025, 224.694 registros × 11 columnas.

**Municipios.** Capa oficial de la Intendencia de Montevideo, obtenida de su GeoServer
institucional (`montevideo.gub.uy/app/geoserver`), capa
`mapstore-tematicas:zon_v_sig_municipios`, descargada por WFS `GetFeature` en GeoJSON
(`EPSG:4326`) el **2026-09-07**. **8 polígonos**: A, B, C, CH, D, E, F y G. Licencia: el servicio
declara `Fees: none` / `AccessConstraints: none` en su `GetCapabilities`.

> **Detalle no obvio, por si hay que repetir la descarga:** el servicio devuelve **403** ante el
> `User-Agent` por omisión de una librería HTTP y **200** con uno de navegador. La consulta exacta
> está transcrita en la sección 2.6 del notebook.

**Clima.** Open-Meteo, archivo histórico reanalizado, serie diaria única para el departamento
(punto −34,87 / −56,17). La caché cubre 1.826 días (2021-01-01 a 2025-12-31); el período
diagnosticado usa 1.645 de ellos.

### Recorte al alcance del proyecto

| Paso | Registros | % del archivo | Artefacto |
| --- | --- | --- | --- |
| Registros del archivo | 224.694 | 100,0 % | `02_recorte_alcance` |
| Tras filtrar `MONTEVIDEO` | 62.427 | 27,8 % | `02_recorte_alcance` |
| Tras filtrar `Fecha >= 2021-01-01` | 39.676 | 17,7 % | `02_recorte_alcance` |
| **Tras excluir el 1.er semestre de 2021** | **36.713** | 16,3 % | `02_recorte_alcance` |
| Tras eliminar 90 duplicados exactos | **36.623** | 16,3 % | `05_duplicados` |
| Tras descartar 11 que caen fuera de todo polígono | **36.612** | 16,3 % | `09_calidad_capa_municipios` |

Las dos últimas filas no están en `02_recorte_alcance.csv`: se derivan de los conteos de
`05_duplicados.csv` y `09_calidad_capa_municipios.csv`, que es donde hay que ir a verificarlas.

**Período diagnosticado:** 1.645 días (2021-07-01 a 2025-12-31).
**Base final del diagnóstico:** **36.612 siniestros** en 8 municipios.

---

## 3. Calidad

### 3.1 Completitud — `tablas/04_completitud.csv`

El archivo **no trae valores nulos**: los faltantes vienen codificados como texto (`SIN DATOS` y
variantes). Contarlos como categoría sería subestimar el problema.

| Columna | Centinelas en el país | **Centinelas en el recorte** |
| --- | --- | --- |
| `Localidad` | 17,91 % | **4,48 %** (1.646 registros) |
| `Calle` | 12,37 % | **2,33 %** (854 registros) |
| `Tipo de Siniestro` | 0,01 % | 0,03 % (10 registros) |
| `Gravedad`, `Dia Semana`, `Departamento` | 0,00 % | 0,00 % |

**Evidencia:** el recorte a Montevideo mejora sustancialmente la completitud.
**Inferencia del equipo:** el problema de calidad que dominaba el diagnóstico nacional era, en
buena medida, un problema del interior del país.

**Decisión: no se imputa.** Las columnas afectadas son descriptivas y **ninguna se usa como
predictora** — el municipio sale de la geometría, no del texto de `Localidad`. Se declara el
conteo en lugar de omitirlo, que es lo que la guía pide cuando la imputación no corresponde.

### 3.2 Duplicados — `tablas/05_duplicados.csv`

| Indicador | Valor |
| --- | --- |
| Duplicados exactos en el archivo completo | 347 (0,15 %) |
| **Duplicados exactos en el recorte** | **90 (0,25 %)** |
| Grupos con repetición en el recorte | 71 |
| Repeticiones en el grupo mayor | **10** |

Se cuentan como duplicados las filas idénticas en **todas** las columnas. Sin identificador de
siniestro no hay forma de distinguir con certeza un duplicado de carga de dos siniestros reales
con los mismos atributos.

**Evidencia:** el grupo mayor concentra diez copias byte a byte del mismo registro.
**Inferencia del equipo:** un siniestro no se repite diez veces en la misma esquina, a la misma
hora, con el mismo tipo y la misma gravedad; es un artefacto de carga. **Se eliminan**, y el
criterio queda declarado.

### 3.3 Consistencia interna — `tablas/06_consistencia.csv`, `06b_consistencia_otros.csv`

`Dia Semana` es redundante respecto de `Fecha`, y esa redundancia permite **verificar el formato
de fecha contra evidencia independiente del propio archivo**.

| Formato probado | Fechas no parseables | Coincidencia con `Dia Semana` |
| --- | --- | --- |
| **`%m/%d/%Y`** | **0** | **100,0000 %** |
| `%d/%m/%Y` | 133.356 | 6,7955 % |

**Un solo formato explica el 100 % de los días de la semana declarados.** Esto **refuta la
suposición del ETL del PID**, que probaba varios formatos en cascada (`parsear_fecha_mixta`)
asumiendo que el archivo los mezclaba: el archivo es homogéneo.

Otras comprobaciones (`06b_consistencia_otros`), todas en cero: horas fuera de 0–23, registros con departamento
distinto de Montevideo, fechas fuera del período declarado. `fixed` toma **un único valor**: no
aporta información y no puede usarse como indicador de calidad de la geocodificación, aunque su
nombre lo sugiera.

### 3.4 Precisión espacial — `tablas/07_precision_espacial.csv`

| Indicador | Valor |
| --- | --- |
| Coordenadas múltiplo de 5 m | 100,00 % |
| Coordenadas distintas | 7.833 |
| Siniestros por coordenada (media) | 4,7 |
| Siniestros en la coordenada más repetida | 113 (**0,31 %** del recorte) |
| Las 10 coordenadas más repetidas concentran | 2,01 % |
| Coordenadas nulas o ≤ 0 | 0 |

**Evidencia:** resolución de 5 m, miles de coordenadas distintas, concentración baja en la más
repetida.
**Inferencia del equipo:** el patrón es el de una geocodificación **a esquina o tramo de calle**,
no a un centroide genérico. Eso es lo que hace viable la asignación punto-polígono.

**Contrapartida, atenuada por el cambio de zonificación.** Un punto ajustado a la esquina puede
caer del lado equivocado de un límite cuando ese límite corre por el eje de la calle. Con
municipios hay **8 fronteras en lugar de 62**, y son en su mayoría avenidas y arroyos de gran
porte: la cantidad de casos ambiguos por borde es, por construcción, mucho menor que con barrios.

### 3.5 Validez temporal — `tablas/08_validez_temporal.csv`

| Indicador | Valor |
| --- | --- |
| Días del período | 1.645 |
| **Días sin ningún siniestro** | **0** |
| Mínimo diario | 4 (2022-01-16) |
| Mediana diaria | 22,0 |
| Máximo diario | 44 (2025-12-11) |

No hay días vacíos ni saltos en el calendario: la serie diaria del departamento está completa. Un
día sin registros habría sido sospechoso de falla del sistema de carga más que de ausencia real de
siniestros, y no ocurre.

### 3.6 Calidad de la asignación a municipios — `tablas/09_calidad_capa_municipios.csv`

| Indicador | Valor |
| --- | --- |
| Polígonos en la capa | 8 |
| Nombres distintos | 8 |
| Municipios con al menos un siniestro | **8** |
| Siniestros asignados | **36.612** |
| Siniestros fuera de todo polígono | **11 (0,03 %)** |

La fracción fuera de todo polígono es **marginal**: la capa cubre el territorio donde
efectivamente ocurren los siniestros. Los pocos casos restantes son puntos de borde —costa, límite
departamental— donde la coordenada ajustada cae milimétricamente afuera; el detalle de los
primeros treinta está en `09b_siniestros_sin_municipio.csv`.

**Decisión: se descartan y se documenta el conteo**, en lugar de reasignarlos al municipio más
cercano. La reasignación introduciría una decisión arbitraria sobre casos que no cambian ninguna
conclusión.

### 3.7 Calidad de la serie climática — `tablas/10_calidad_clima.csv`, `10b_clima_resumen.csv`

| Indicador | Valor |
| --- | --- |
| Días del período cubiertos | **1.645 de 1.645** |
| Días del período sin clima | 0 |
| Fechas duplicadas | 0 |
| Celdas faltantes | **0** |
| Temperatura media fuera de −10…45 °C | 0 |
| Precipitación negativa | 0 |

**Sin faltantes y con el período completo: no corresponde imputar.** El rango de valores es el
esperable para Montevideo (temp. media 4,9–31,7 °C, precipitación 0–105,3 mm, `10b_clima_resumen`).

**Limitación de diseño, no de calidad:** se usa **una sola serie para todo el departamento**. A
resolución diaria las variables meteorológicas son prácticamente uniformes sobre unos 200 km²
urbanos, de modo que el supuesto es razonable, pero significa que el clima **no puede explicar
ninguna diferencia entre municipios**: aporta sólo variación temporal, la misma para las ocho
zonas. Tiene consecuencias directas en §5.3.

---

## 4. Cobertura

### 4.1 Cobertura temporal y la exclusión del 1.er semestre de 2021

`tablas/11_cobertura_temporal_anual.csv`, `11b_cobertura_mensual.csv`,
`12_pandemia_paso1_nivel.csv` a `12e_costo_del_corte.csv`, `figuras/fig1_cobertura_temporal.png`

| Año | Siniestros | Días observados | Media diaria | Variación |
| --- | --- | --- | --- | --- |
| 2021 | 3.936 | 184 | 21,39 | — |
| 2022 | 7.665 | 365 | 21,00 | *no comparable* |
| 2023 | 7.873 | 365 | 21,57 | +2,7 % |
| 2024 | 8.398 | 366 | 22,95 | +6,4 % |
| 2025 | 8.740 | 365 | 23,95 | +4,4 % |

> **Cuidado al citar esta tabla.** 2021 aporta sólo julio–diciembre, que es la mitad
> estacionalmente **más activa** del año: su media diaria no es comparable con la de un año
> completo, y por eso la variación 2021→2022 se marca como no comparable en lugar de informarse.
> La comparación homogénea (jul–dic contra jul–dic) es la tabla `12c_pandemia_paso3_jul_dic`.

#### Por qué la serie empieza en julio de 2021 — el argumento en tres pasos

El recorte anterior arrancaba en enero de 2021 «para que el modelo no vea la pandemia». **Esa
justificación no se sostenía con los datos**: en Uruguay la ola de COVID y las restricciones de
movilidad fueron en el **primer semestre de 2021**, dentro del período que el filtro conservaba.

**Paso 1 — cuánto falta** (`12_pandemia_paso1_nivel`)

| Período | Siniestros | Días | Media diaria |
| --- | --- | --- | --- |
| ene–jun 2021 | 2.957 | 181 | **16,34** |
| ene–jun 2022–2025 | 15.516 | 725 | **21,40** |
| **Diferencia** | | | **−23,7 %** |

**Paso 2 — que no es sólo tendencia** (`12b_pandemia_paso2_indice_estacional`). Cada mes dividido
por la media de *su propio* año, lo que elimina el nivel anual y deja sólo la forma intraanual. Si
2021 estuviera simplemente más bajo por tendencia, su forma coincidiría con la de los demás años.

| Mes | Índice 2021 | Índice 2022–2025 | Desvío |
| --- | --- | --- | --- |
| 1 | 0,774 | 0,765 | +1,1 % |
| 2 | 0,811 | 0,901 | **−10,0 %** |
| 3 | 0,875 | 0,985 | **−11,2 %** |
| 4 | 0,810 | 0,978 | **−17,2 %** |
| 5 | 0,943 | 1,059 | **−10,9 %** |
| 6 | 0,974 | 1,048 | **−7,0 %** |

**Paso 3 — que el corte alcanza** (`12c_pandemia_paso3_jul_dic`, `12d_pandemia_paso3_forma`). El tramo conservado encadena con los años
siguientes dentro de la variación interanual ordinaria:

| Año | Media diaria jul–dic | Variación interanual |
| --- | --- | --- |
| **2021** | **21,39** | — |
| 2022 | 22,05 | +3,1 % |
| 2023 | 22,68 | +2,8 % |
| 2024 | 23,96 | +5,7 % |
| 2025 | 24,62 | +2,8 % |

Y su forma intraanual vuelve a la de referencia: en **cinco de los seis meses** de julio a
diciembre de 2021 el desvío queda entre **−1,3 % y −4,6 %** (`12d_pandemia_paso3_forma`). La excepción es noviembre,
que se trata más abajo.

**Costo de la decisión** (`12e_costo_del_corte`): 2.957 registros excluidos (**7,5 %** del recorte
de Montevideo desde 2021) y 181 días de serie; quedan **1.645 días**.

**Lo que hay que decir en el informe, con sus tres matices:**

1. **Febrero a junio de 2021 están deprimidos y no por tendencia.** Es evidencia, no
   interpretación: el índice estacional lo aísla.
2. **Enero de 2021 es la excepción** — su índice coincide con el de referencia (+1,1 %), coherente
   con que la ola grande empezó en marzo. Se lo excluye igual porque cortar en febrero dejaría un
   mes suelto y un límite arbitrario. Es una decisión de conveniencia del equipo, y conviene
   declararla como tal.
3. **Noviembre de 2021 se aparta hacia arriba** (+10,7 % en el índice del segundo semestre) y el
   diagnóstico **no tiene con qué explicarlo**. Se lo deja en la serie y se lo señala como el
   único mes atípico del tramo conservado.

> **Lo que el corte NO resuelve.** La serie tiene una **tendencia creciente sostenida** en todo el
> período conservado (la media diaria pasa de 21,4 a 24,6 entre 2021 y 2025). Es un fenómeno real,
> no un artefacto de la pandemia. Tiene consecuencia directa sobre la evaluación y se cuantifica
> en §5.3.

### 4.2 Cobertura territorial — `tablas/13_cobertura_municipios.csv`, `13b_concentracion_territorial.csv`,
`figuras/fig2_cobertura_territorial.png`

| Municipio | Siniestros | % del total | Días con siniestro | Media diaria |
| --- | --- | --- | --- | --- |
| C | 5.783 | 15,80 % | 95,2 % | 3,516 |
| B | 5.377 | 14,69 % | 95,0 % | 3,269 |
| D | 5.319 | 14,53 % | 95,6 % | 3,233 |
| A | 5.016 | 13,70 % | 94,2 % | 3,049 |
| F | 4.424 | 12,08 % | 93,2 % | 2,689 |
| G | 3.701 | 10,11 % | 87,9 % | 2,250 |
| E | 3.615 | 9,87 % | 86,0 % | 2,198 |
| CH | 3.377 | 9,22 % | 84,3 % | 2,053 |

**Razón máximo/mínimo: 1,71×** (`13b_concentracion_territorial`). Con barrios superaba el orden de magnitud.

**Evidencia:** los ocho municipios están representados y el reparto es notablemente parejo; todos
registran siniestros en más del 84 % de los días del período.

**Inferencia del equipo — y tiene dos caras que no hay que confundir:**

- **A favor:** todos los municipios tienen soporte de sobra para estimar una tasa estable, y
  desaparece por completo el problema de las zonas casi vacías que arrastraba la grilla de 1 km
  (28 celdas con un único siniestro en cinco años).
- **En contra:** si las zonas se parecen tanto entre sí, **queda poco margen para que un modelo
  las ordene**. Las diferencias entre posiciones contiguas del ranking serán menores que el error
  de estimación.

**Limitación de representatividad que la agregación NO corrige:** el mapa refleja **dónde se
registran** siniestros, no dónde son más probables por unidad de exposición. Sin datos de tránsito
no se puede normalizar por volumen de vehículos.

### 4.3 El panel día × municipio — `tablas/14_panel_dia_municipio.csv`

| Indicador | Valor |
| --- | --- |
| Días del período | 1.645 |
| Municipios | 8 |
| **Filas del panel** | **13.160** |
| Filas con al menos un siniestro | 12.028 |
| **Densidad (filas no nulas)** | **91,40 %** |
| **Ceros** | **8,60 %** |
| Media de siniestros por fila | **2,7821** |
| Máximo en una fila | 13 |

**Éste es el cambio de fondo respecto de todas las versiones anteriores.** Comparación directa:

| Zonificación | Zonas | Filas del panel | % de ceros | Media | Dispersión | Máx. |
| --- | --- | --- | --- | --- | --- | --- |
| Grilla de 1 km (superada) | 403 | 735.878 | 95,08 % | 0,0538 | 1,136 | 5 |
| Barrios (superada) | 62 | 113.212 | 71,96 % | 0,3495 | 1,132 | 7 |
| **Municipios (vigente)** | **8** | **13.160** | **8,60 %** | **2,7821** | **1,259** | **13** |

> **Trazabilidad de esta tabla:** sólo la última fila sale de un artefacto vigente
> (`14_panel_dia_municipio`, `18_dispersion_objetivo`). Las dos primeras se conservan de las
> corridas anteriores, **cuyos artefactos fueron borrados** al reescribir el notebook; su respaldo
> es `HANDOFF.md` (secciones del ETL y de la reescritura del diagnóstico). Si el informe necesita
> citar la comparación, citarla como **historial del proyecto**, no como resultado de esta
> ejecución.

**Inferencia del equipo:** el problema deja de ser «un evento raro en ventanas de un día» y pasa a
ser **una regresión de conteo ordinaria**. Dos consecuencias inmediatas para el modelado:

- **No hay exceso de ceros que tratar.** Cualquier variante *zero-inflated* considerada con las
  zonificaciones anteriores queda sin objeto, y **el balanceo no corresponde**: no hay clases que
  balancear.
- **La interpolación de ceros que se había propuesto pierde sentido.** Se pensó para un panel
  dominado por ceros estructurales; con 8,60 % de ceros no hay nada que interpolar.

### 4.4 Variables exógenas — `tablas/15_cobertura_calendario.csv`, `16_feriados.csv`,
`16b_feriados_omitidos_por_defecto.csv`, `20c_perfil_semanal.csv`

| `tipo_dia` | Días | % | Media de siniestros/día |
| --- | --- | --- | --- |
| entre_semana | 1.114 | 67,7 % | **24,33** |
| fin_semana | 454 | 27,6 % | **18,31** |
| feriado | 77 | 4,7 % | **15,64** |

Perfil semanal (`20c_perfil_semanal`), media diaria del departamento: lunes 23,14 · martes 23,48 · miércoles
23,57 · jueves 23,55 · **viernes 25,74** · sábado 20,25 · **domingo 16,06**.

**Feriados** (`16_feriados`): con `categories=("public","bank")` son **77** en el período; con la
configuración por omisión de `holidays` serían **23**, omitiendo **54 días**, entre ellos
**Carnaval y Semana de Turismo** — los dos períodos de mayor alteración de la movilidad del año
(el detalle está en `16b_feriados_omitidos_por_defecto`). El ETL vigente usa las dos categorías: el hueco que reportaba el
diagnóstico nacional **está cerrado**.

**El clima está integrado** (§3.7), lo que cierra el otro hueco que quedaba abierto.

---

## 5. Adecuación

### 5.1 La variable objetivo — `tablas/17_distribucion_objetivo.csv`, `18_dispersion_objetivo.csv`

| Indicador | Valor |
| --- | --- |
| Media | **2,7821** |
| Varianza | **3,5039** |
| **Índice de dispersión (var/media)** | **1,259** |
| Máximo | 13 |
| % de filas en cero | 8,60 % |
| % de filas con 1 | 18,47 % |
| % de filas con 2 o más | **72,93 %** |

Distribución (`17_distribucion_objetivo`): el modo está en 2 siniestros (22,56 % de las filas), con cola que llega a 13.

**Evidencia:** conteo con **sobredispersión leve** — la varianza supera a la media en algo más de
un 25 %.
**Inferencia del equipo:** un Poisson puro queda algo justo pero sigue siendo la familia de
referencia; una **binomial negativa** es la primera extensión razonable a probar.

**Métrica principal recomendada: desvianza de Poisson.** El argumento por el que se descarta el
error absoluto medio **cambió respecto de las versiones anteriores** y conviene no repetir el
viejo: antes se lo descartaba porque premiaba predecir siempre cerca de cero, y con este panel el
objetivo ya no está concentrado en cero. Se lo sigue prefiriendo por otra razón: **el MAE trata
igual un error de una unidad sobre un valor esperado de 0,5 que sobre uno de 5**, mientras que la
desvianza lo pondera por el nivel, que es lo que corresponde a un conteo.

### 5.2 Señal temporal — `tablas/19_senal_temporal_municipios.csv`, `20_senal_serie_agregada.csv`,
`20b_varianza_calendario.csv`, `figuras/fig3_senal_temporal.png`

El contraste no es contra cero sino contra el **puro azar**: se simulan series de Poisson con la
misma tasa media de cada municipio (400 simulaciones) y se compara la autocorrelación observada
contra la banda que generan. Esta versión agrega un paso que las anteriores no tenían: la misma
medición **sobre el residuo**, después de descontar día de la semana y feriado.

| Rezago | ACF cruda (mediana) | Municipios sobre la banda | ACF del residuo (mediana) | **Municipios sobre la banda (residuo)** | Banda nula |
| --- | --- | --- | --- | --- | --- |
| **1** | 0,0558 | **5 de 8** | 0,0475 | **5 de 8** | 0,0464 |
| **7** | 0,0569 | **5 de 8** | 0,0079 | **0 de 8** | 0,0450 |

*(esperables por azar al percentil 97,5: 0,2 de 8)*

Serie agregada del departamento (`20_senal_serie_agregada`):

| Serie | ACF rezago 1 | ACF rezago 7 |
| --- | --- | --- |
| Cruda | 0,1977 | **0,2964** |
| Residuo tras descontar `tipo_dia` | 0,1948 | **0,1825** |

Varianza de la serie diaria del departamento explicada por calendario (`20b_varianza_calendario`): `tipo_dia`
**22,3 %**, día de la semana 20,8 %, mes 7,4 %, `tipo_dia + mes` **30,9 %**.

#### ⚠️ Esta conclusión se invirtió respecto de las versiones anteriores

Con celdas de 1 km y con barrios, el diagnóstico concluía que **no se detecta señal temporal de
corto plazo por zona**. Con municipios **sí se detecta**.

**Evidencia:** la mediana de la ACF a rezago 1 supera la banda nula de Poisson, y lo hace en 5 de
8 municipios, muy por encima de los 0,2 esperables por azar.

**Inferencia del equipo:** el fenómeno no cambió; **antes el ruido de Poisson lo tapaba**. Una
serie con media 0,35 siniestros/día no tiene relación señal-ruido suficiente para detectar una
autocorrelación de 0,05; una con media 2,8 sí.

**El desglose por rezago es la parte útil:**

- **A rezago 7 la señal es enteramente de calendario.** Descontado día de la semana y feriado,
  *ningún* municipio queda sobre la banda nula. El pico semanal de la serie agregada es la
  repetición del calendario, **no memoria del proceso**.
- **A rezago 1 queda persistencia genuina.** El residuo conserva autocorrelación sobre la banda en
  5 de 8 municipios: hay algo real de un día para el otro que el calendario no explica.

**Consecuencia de modelado, con su matiz.** A diferencia de las versiones anteriores, un rezago de
un día **no queda descartado de entrada**. Pero la magnitud es pequeña —una ACF de 0,05 explica
menos del 1 % de la varianza de esa serie—, así que no puede ser el eje del modelo. La línea base
defendible sigue siendo **tasa histórica del municipio × factor de calendario**, y el rezago de un
día entra como **candidato a evaluar contra ella**, no como supuesto.

### 5.3 Qué aporta cada bloque de variables

`tablas/21_aporte_bloques_en_muestra.csv`, `21b_descomposicion_varianza.csv`,
`21c_aporte_bloques_fuera_de_muestra.csv`, `21d_deriva_entre_mitades.csv`

Esta sección es **el aporte metodológico de la versión vigente**. Se mide en dos pasadas, y la
distinción entre ambas es lo que hay que citar en el informe.

#### Pasada 1 — techos en muestra (`21_aporte_bloques_en_muestra`)

Oráculos: a cada predictor se le entrega la media empírica del grupo, calculada sobre los mismos
datos con los que se lo evalúa. Cada valor es una **cota superior**.

| Información disponible | Desvianza | Mejora |
| --- | --- | --- |
| Constante global | 1,36899 | — |
| Oráculo de día — techo de TODA variable de día | 1,13018 | **−17,4 %** |
| Oráculo de municipio — tasa histórica | 1,26796 | −7,4 % |
| Municipio × día | 1,02914 | −24,8 % |

Descomposición de varianza (`21b_descomposicion_varianza`): entre municipios **7,9 %**, entre días **18,47 %**.

#### Pasada 2 — desempeño fuera de muestra (`21c_aporte_bloques_fuera_de_muestra`)

El panel se parte por la mitad **en el tiempo**: las medias de grupo se estiman con la primera
mitad y la desvianza se evalúa sobre la segunda. Es una versión mínima del protocolo, hecha sólo
para dimensionar cada bloque; **la partición definitiva se fija en el notebook de modelado y el
conjunto de prueba real no se toca aquí.**

| Predictor (estimado sólo con la 1.ª mitad) | Medias estimadas | Desvianza | Mejora |
| --- | --- | --- | --- |
| Constante global | 1 | 1,36394 | — |
| Sólo factor de calendario (día de semana + feriado) | 14 | 1,30530 | −4,3 % |
| Sólo tasa histórica del municipio | 8 | 1,26172 | **−7,5 %** |
| **Tasa del municipio × factor de calendario** ← línea base | 22 | **1,20308** | **−11,8 %** |
| Tasa del municipio × (calendario + llovió) | 34 | 1,20716 | −11,5 % |
| Celdas saturadas municipio × calendario × mes | 888 | 1,50546 | **+10,4 %** |

#### Qué hay que concluir de las dos tablas

**En muestra el oráculo de día parece dominar (−17,4 % contra −7,4 %). Es un espejismo, por
partida doble:** ese oráculo recibe la media exacta de cada día, que incluye toda la fluctuación
diaria irrepetible —es el techo de *cualquier* variable de día, incluidas las que nadie tiene—, y
además no paga ningún costo por la cantidad de grupos que usa.

**Fuera de muestra el orden se invierte y aparece el resultado útil:**

- La **tasa histórica del municipio**, con ocho parámetros, mejora **más** que el calendario
  realizable con catorce (−7,5 % contra −4,3 %).
- El **calendario efectivamente construible** rinde mucho menos que lo que prometía el oráculo de
  día. La diferencia entre −17,4 % y −4,3 % es la parte de la variación diaria que **ninguna
  variable disponible captura**.
- La combinación **multiplicativa** es la mejor de la tabla (−11,8 %) y supera a los dos bloques
  por separado. **Es exactamente la línea base que el diagnóstico recomienda, ahora medida en vez
  de postulada.**
- **Agregar el clima no mejora nada** (−11,5 % contra −11,8 %). A resolución diaria y con esta
  agregación espacial, el clima no aporta señal utilizable.
- Las **celdas saturadas rinden peor que no usar nada** (+10,4 %). Es el resultado que justifica la
  forma multiplicativa: con este volumen de datos, cruzar municipio y calendario en celdas
  independientes memoriza ruido.

**Dos advertencias sobre cómo leer estos números:**

1. La descomposición de varianza (`21b_descomposicion_varianza`) atribuye más peso a la variación *entre días* (18,47 %)
   que *entre municipios* (7,9 %). **No contradice lo anterior:** buena parte de esa variación
   diaria es ruido de Poisson compartido, no señal predecible, y por eso el calendario realizable
   recupera sólo una fracción pequeña.
2. **Deriva entre mitades** (`21d_deriva_entre_mitades`): la media del objetivo pasa de **2,6369** a **2,9271**
   (**+11,0 %**). Todos los predictores están estimados sobre el tramo bajo y evaluados sobre el
   alto, así que **todos subestiman el nivel y todas las mejoras informadas son conservadoras**.
   El modelado tendrá que tratar esa tendencia explícitamente —recalibrar nivel, incluir
   tendencia, o ponderar los datos recientes—; el diagnóstico no decide cuál.

### 5.4 Adecuación al objetivo del producto — `tablas/22_adecuacion_objetivo.csv`

| Pregunta | Respuesta | Fundamento |
| --- | --- | --- |
| ¿Predecir el conteo diario por municipio? | **Sí** | Panel denso (< 9 % de ceros), objetivo de tipo Poisson |
| ¿Predecir dónde ocurrirá el próximo siniestro? | **No** | La unidad es municipio-día; la persistencia detectada es despreciable |
| ¿Ordenar municipios por riesgo esperado? | **Sí, con margen estrecho** | La tasa es el bloque más útil, pero entre mayor y menor hay < 2× |
| ¿Estimar riesgo por unidad de exposición? | **No** | No hay datos de tránsito |
| ¿Modelar por gravedad o franja horaria? | **No con el conjunto vigente** | El ETL descarta esas columnas |
| ¿Evaluar en municipios no vistos al entrenar? | **Muy limitado** | Con 8 zonas, reservar 2 deja 6 para entrenar |
| ¿La resolución sirve para asignar recursos? | **Parcialmente** | Un municipio abarca 1.148–14.380 ha |

**Las dos consecuencias del cambio de zonificación que el equipo tiene que asumir explícitamente:**

**1. El experimento del «megamodelo» evaluado en zonas no vistas queda muy debilitado.** Con 62
barrios era una prueba razonable; con 8 municipios, reservar dos deja seis para entrenar y el
resultado dependería casi por completo de *cuáles* dos se reserven. Se puede hacer —dejando *uno*
afuera por vez y promediando las ocho corridas, que es lo único defendible a esta escala—, pero
**su poder estadístico es bajo y no puede ser la evidencia principal de la generalización**.

**2. El margen para ordenar zonas se estrechó.** Con razón 1,71× entre el municipio más y el menos
activo, un modelo que ordene municipios acierta poco más que el orden de la tasa histórica. Es una
limitación **del alcance elegido, no del método**, y el informe debe declararla en lugar de
presentar el ordenamiento como un resultado sólido.

---

## 6. Limitaciones y lo que NO puede afirmarse

`tablas/24_limitaciones.csv` — doce limitaciones, cada una con la sección que la sustenta y el
tratamiento que recibe.

| Limitación | Sección | Cómo se trata |
| --- | --- | --- |
| **Tendencia creciente en todo el período** | 4.1, 5.3 | Tratarla en el modelado: recalibrar nivel, tendencia o ponderación |
| **Sólo 8 zonas, y muy parecidas entre sí** | 4.2, 5.4 | Declarar el margen; hold-out dejando una afuera por vez |
| **Resolución espacial gruesa** | 3.6, 5.4 | Acotar las afirmaciones a esa granularidad |
| Persistencia de corto plazo detectable pero mínima | 5.2 | El rezago de un día se evalúa; ni se asume ni se descarta |
| Variables exógenas sin variación espacial | 3.7, 5.3 | La tasa del municipio es el bloque principal; el clima se reevalúa |
| Clima observado, no pronosticado | 2 | Declararlo: el desempeño medido es cota optimista |
| Sin datos de exposición (tránsito) | 4.2, 5.4 | Limitar afirmaciones a conteo esperado |
| Primer semestre de 2021 excluido | 4.1 | Justificado con evidencia; costo explícito en `12e_costo_del_corte` |
| Duplicados exactos en la fuente | 3.2 | Eliminados (90); criterio declarado |
| Faltantes encubiertos como texto | 3.1 | No se imputa; se declara el conteo |
| Siniestros fuera de todo polígono | 3.6 | Se descartan (11); se documenta |
| **Subregistro de siniestros** | **—** | **No es medible con estos datos** |

Las **tres primeras son nuevas de esta versión** y las tres nacen del cambio de alcance: la
tendencia quedó a la vista al medir fuera de muestra, y el número y el tamaño de las zonas son
consecuencia directa de pasar de barrios a municipios. Ninguna invalida el proyecto, pero **las
tres tienen que estar en el informe**.

### Frases que NO deben aparecer en el informe

- ❌ «El modelo predice dónde ocurrirá el próximo siniestro.» → Sólo estima y calibra el **conteo
  esperado** por municipio y día.
- ❌ «El municipio X es el más peligroso.» → Es el que **registra** más siniestros. Sin exposición
  no se puede hablar de peligrosidad por viaje.
- ❌ «Los datos cubren todos los siniestros de Montevideo.» → Cubren los **registrados**. El
  subregistro es desconocido.
- ❌ «El clima explica la siniestralidad.» → **Fuera de muestra no aporta nada** (−11,5 % contra
  −11,8 % sin él), y no explica diferencias entre municipios.
- ❌ «Queda demostrado que no hay señal temporal.» → **Esta frase era de la versión de barrios y ya
  no aplica.** Ahora *sí* se detecta señal a rezago 1 en 5 de 8 municipios; lo que corresponde
  decir es que **su magnitud es pequeña**.
- ❌ «Las variables de día son las más informativas» citando el −17,4 %. → Ese número es un
  **oráculo en muestra**, techo inalcanzable. El calendario construible rinde −4,3 %.
- ❌ «El objetivo tiene exceso de ceros» / «se aplicó balanceo». → Con municipios los ceros son el
  **8,60 %**. No hay exceso de ceros ni corresponde balancear.
- ❌ «El modelo generaliza a zonas no vistas.» → Con 8 zonas esa prueba tiene poder estadístico
  bajo; se puede reportar, no se puede usar como evidencia principal.
- ❌ «Se eliminó el efecto de la pandemia.» → Se excluyó el semestre afectado. **Queda una
  tendencia creciente** que el corte no elimina, y noviembre de 2021 sigue siendo atípico.

### Sobre el subregistro

**No es medible con los propios datos.** El archivo contiene los siniestros que fueron
registrados; la fracción no registrada —típicamente los leves o sin lesionados que no generan
intervención— es desconocida y probablemente no uniforme entre municipios. Si la propensión a
registrar variara entre municipios, el ordenamiento estaría sesgado de una forma que este
diagnóstico **no puede detectar**. Cuantificarlo exigiría una fuente externa de contraste que el
proyecto no tiene. Declararlo es parte del diagnóstico.

---

## 7. Verificación cruzada con el ETL — `tablas/23_coherencia_etl.csv`

El diagnóstico reconstruye el panel desde las fuentes crudas de forma **independiente** del ETL,
con su propia implementación del recorte, la deduplicación y la asignación punto-polígono. La
comparación es una verificación real: una discrepancia significaría que uno de los dos notebooks
tiene un error.

| Comprobación | Diagnóstico (recalculado) | ETL (`data/processed`) | Resultado |
| --- | --- | --- | --- |
| Filas del panel | 13.160 | 13.160 | ✅ coincide |
| Siniestros totales | 36.612 | 36.612 | ✅ coincide |
| Zonas | 8 | 8 | ✅ coincide |
| Días | 1.645 | 1.645 | ✅ coincide |
| Máximo del objetivo | 13 | 13 | ✅ coincide |

**Las cinco comprobaciones coinciden.** Dos implementaciones independientes llegan al mismo
resultado: es la evidencia más fuerte de que el conjunto está bien construido, y es citable en el
informe.

> **Cómo se llegó acá.** En la primera corrida de esta versión del diagnóstico (2026-09-07) la
> comparación **no se pudo hacer**: el ETL seguía en el alcance anterior (62 zonas desde enero de
> 2021) y el notebook se abstuvo de comparar en lugar de informar una discrepancia falsa. El ETL
> se migró en la misma sesión ([`resumen_preparacion_montevideo.md`](resumen_preparacion_montevideo.md))
> y la verificación se volvió a ejecutar.
>
> **Un error real que esta verificación destapó:** la celda que lee el panel del ETL parseaba la
> fecha con `dayfirst=True`, y sobre una fecha ISO como `2021-07-01` eso da **el 7 de enero**, en
> silencio. Es exactamente el riesgo que la sección 3.3 verifica en la fuente cruda. Corregido:
> el formato se decide mirando el texto, no por bandera.

---

## 8. Índice de artefactos

`experiments/diagnostico_datos/` — **43 tablas y 3 figuras**. `tablas/25_artefactos.csv` lista
todas con su tamaño.

**Figuras:**

| Figura | Qué muestra | Sección |
| --- | --- | --- |
| `fig1_cobertura_temporal.png` | Serie mensual, con el 1.er semestre de 2021 sombreado como excluido | 4.1 |
| `fig2_cobertura_territorial.png` | Mapa coroplético de los 8 municipios, etiquetados, por siniestros acumulados | 4.2 |
| `fig3_senal_temporal.png` | ACF por municipio — observada, residuo y banda nula (izq.); ACF de la serie agregada, cruda y sin calendario (der.) | 5.2 |

**Qué tabla respalda qué afirmación:**

| Eje | Tablas |
| --- | --- |
| Trazabilidad | `00_procedencia`, `00b_entorno`, `01_esquema_crudo`, `02_recorte_alcance` |
| Disponibilidad | `03_disponibilidad_variables`, `03b_disponibilidad_exogenas` |
| Calidad | `04_completitud`, `05_duplicados`, `06_consistencia`, `06b_consistencia_otros`, `07_precision_espacial`, `08_validez_temporal`, `09_calidad_capa_municipios`, `09b_siniestros_sin_municipio`, `10_calidad_clima`, `10b_clima_resumen` |
| **Corte de pandemia** | `12_pandemia_paso1_nivel`, `12b_pandemia_paso2_indice_estacional`, `12c_pandemia_paso3_jul_dic`, `12d_pandemia_paso3_forma`, `12e_costo_del_corte` |
| Cobertura | `11_cobertura_temporal_anual`, `11b_cobertura_mensual`, `13_cobertura_municipios`, `13b_concentracion_territorial`, `14_panel_dia_municipio`, `15_cobertura_calendario`, `16_feriados`, `16b_feriados_omitidos_por_defecto` |
| Adecuación | `17_distribucion_objetivo`, `18_dispersion_objetivo`, `19_senal_temporal_municipios`, `20_senal_serie_agregada`, `20b_varianza_calendario`, `20c_perfil_semanal`, `22_adecuacion_objetivo` |
| **Aporte de variables** | `21_aporte_bloques_en_muestra`, `21b_descomposicion_varianza`, `21c_aporte_bloques_fuera_de_muestra`, `21d_deriva_entre_mitades` |
| Verificación | `23_coherencia_etl` |
| Limitaciones | `24_limitaciones` |

**Antes de citar cualquier cifra:** verificar que los `sha256` de `00_procedencia.csv` sigan siendo
los de las fuentes vigentes. Si alguna fuente cambió, hay que volver a ejecutar el notebook.

---

## 9. Qué queda pendiente

Lo que este diagnóstico **deja planteado** y corresponde a los notebooks siguientes:

1. ~~Reejecutar el ETL con el alcance nuevo~~ — **hecho** (2026-09-07): el ETL trabaja por
   municipios desde 2021-07-01 y la verificación cruzada del §7 pasa con las cinco comprobaciones
   en verde. `data/processed/` **ya es citable**.
2. ~~Actualizar `resumen_preparacion_montevideo.md`~~ — **hecho**: documenta el ETL vigente,
   incluida la decisión de dejar `estrato_actividad` fuera del panel.
3. **Construir la variable de nivel de zona** (tasa histórica del municipio), ajustada sólo con el
   tramo de entrenamiento. Es el bloque más útil fuera de muestra (§5.3) y hoy no existe en el
   panel.
4. **Implementar la línea base multiplicativa** (tasa del municipio × factor de calendario) y
   evaluarla con el protocolo definitivo. El diagnóstico ya midió que es la mejor forma disponible
   (−11,8 % fuera de muestra) y que **la forma saturada no sirve**.
5. **Definir las particiones cronológicas** con el conjunto de prueba reservado. El diagnóstico
   *no* las define: la partición por la mitad de §5.3 es sólo instrumental.
6. **Tratar la tendencia creciente** (§4.1, §5.3): recalibrar nivel, incluir tendencia o ponderar
   los datos recientes. Es una decisión abierta.
7. **Evaluar el rezago de un día** como variable candidata, contra la línea base y bajo el mismo
   protocolo (§5.2). Ya no se lo descarta de entrada.
8. **Reconsiderar el clima.** Fuera de muestra no aporta nada (§5.3); mantenerlo exige una
   justificación mejor que «estaba disponible».
9. **Fijar las métricas**: desvianza de Poisson como principal. **Revisar la decisión de
   balanceo**: con 8,60 % de ceros no corresponde balancear, y las notas anteriores que hablaban
   de exceso de ceros están superadas.
10. **Decidir el diseño del hold-out de zonas** (§5.4): con 8 municipios, dejar uno afuera por vez
    y promediar es lo único defendible.
