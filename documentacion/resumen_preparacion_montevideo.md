# Resumen del ETL y la preparación de datos — Montevideo

**Notebook:** [`notebooks/preparacion_montevideo.ipynb`](../notebooks/preparacion_montevideo.ipynb)
**Artefactos:** `experiments/etl_montevideo/` (14 tablas CSV, 1 mapa HTML, 1 figura PNG)
**Salida:** `data/processed/` (5 CSV + diccionario de datos)
**Fecha de ejecución:** 2026-09-04
**Alcance:** Montevideo, 2021-01-01 a 2025-12-31, unidad de análisis **(día, barrio)**

---

## 0. Cómo usar este documento

Este archivo es **contexto autocontenido** para redactar la documentación del proyecto (informe
técnico, presentaciones, defensa ante el tribunal) sin necesidad de abrir el repositorio. Cubre la
sección *Metodología — preparación* del informe: qué transformaciones se aplicaron, **por qué**, y
qué efecto tuvieron.

Es el complemento de [`resumen_diagnostico_datos.md`](resumen_diagnostico_datos.md), que cubre
*Metodología — datos*. Los dos se leen juntos: el diagnóstico dice **cómo son** los datos; éste
dice **qué se les hizo**.

**Reglas que quien redacte debe respetar:**

1. **Ninguna cifra sin artefacto.** Todos los números salen de una ejecución real y llevan al lado
   la tabla que los respalda (`experiments/etl_montevideo/tablas/NN_nombre.csv`). Si hace falta un
   número que no está acá, marcarlo como `<!-- PENDIENTE: ... -->` en lugar de completarlo.
2. **Distinguir evidencia de inferencia.** Este documento separa *lo que se midió* de *lo que el
   equipo decidió*.
3. **Cada transformación va con su porqué y su efecto observado**, que es lo que la guía pide
   (sección 6.1). Una lista de pasos sin justificación no sirve para el informe.
4. **Respetar los límites de la sección 7.** Hay afirmaciones que este conjunto no sostiene.

---

## 1. Qué hace este notebook y qué lo distingue

Construye el **conjunto de modelado** a partir de tres fuentes crudas y lo deja en
`data/processed/` como CSV. Es la adaptación al contexto de aprendizaje automático del pipeline
ETL del **Proyecto de Ingeniería de Datos (PID)** del mismo equipo, que vive en `etl/`.

**Lo que este notebook NO hace, deliberadamente:**

- No define particiones de entrenamiento / validación / prueba.
- No escala ni normaliza.
- No balancea.
- No construye variables que aprendan de los datos (rezagos, medias móviles, tasa histórica).

Todo eso corresponde al notebook de modelado, **porque debe ajustarse dentro de cada partición
para no filtrar información**. Un escalador ajustado sobre el conjunto completo le pasa al modelo
información del tramo de prueba; una tasa histórica calculada sobre todo el período, también. Es la
distinción que la guía llama evitar fugas de información (sección 6.2), y la razón por la que el
ETL se detiene donde se detiene.

### Trazabilidad respecto del PID

Punto que el informe debe declarar con precisión, porque la guía exige distinguir **lo heredado del
PID** de **lo desarrollado en el PAA**.

| PID (`etl/`) | Este notebook | Por qué cambia |
| --- | --- | --- |
| Tres países (UY, BR, ES) | Sólo Uruguay → Montevideo | Alcance acordado con el docente |
| Carga a PostgreSQL y MongoDB | Carga a CSV en `data/processed/` | El PAA se entrega como repositorio ejecutable, sin infraestructura |
| Unidad = un siniestro | Unidad = **(día, barrio)** | El objetivo es el conteo por zona y día |
| `encoding='latin-1'` | `encoding='utf-8'` | **El archivo es UTF-8**; latin-1 rompe los acentos |
| `parsear_fecha_mixta` (prueba formatos en cascada) | Formato fijo `%m/%d/%Y` **verificado** | El «formato mixto» era una suposición del PID; el archivo es homogéneo |
| Sin tratamiento de duplicados | Duplicados exactos eliminados | Distorsionaban la cola alta del objetivo |
| Clima a PostgreSQL, por siniestro y por hora | Clima diario del departamento, cacheado en `data/raw/` | Sin base de datos, y la unidad es el día |

**Reutilizado del PID sin cambios:** el vocabulario controlado de gravedad
(`fatal` / `grave` / `leve` / `solo_danos`) y la reproyección UTM 21S → WGS84.

**`etl/` no se ejecuta en el PAA:** depende de PostgreSQL, MongoDB, Docker y rutas `/app/...`. Está
en el repositorio como fuente de la adaptación, no como código vivo.

---

## 2. Fuentes y trazabilidad

`tablas/00_procedencia.csv`, `tablas/03b_procedencia_capa_zonas.csv`

| Fuente | Archivo | sha256 (prefijo) | Detalle |
| --- | --- | --- | --- |
| Siniestros | `data/raw/uru_siniestros_unificado.csv` | `48a8a7e8…` | 224.694 registros × 11 columnas, heredado del PID (fuente original: UNASEV) |
| Barrios | `data/raw/barrios_montevideo.geojson` | `a03e8927…` | 62 polígonos, Intendencia de Montevideo |
| Clima | `data/raw/clima_montevideo.csv` | — | 1.826 días, Open-Meteo (caché) |

**La capa de barrios** se obtuvo del GeoServer institucional de la Intendencia de Montevideo
(`montevideo.gub.uy/app/geoserver`), capa `mapstore-tematicas:zon_v_sig_barrios`, mediante WFS
`GetFeature` en GeoJSON (`EPSG:4326`), el **2026-09-04**. Licencia: el servicio declara
`Fees: none` / `AccessConstraints: none` en su `GetCapabilities`.

*Detalle práctico para reproducir la descarga:* el servicio devuelve **403** ante un `User-Agent`
de librería (bloqueo por WAF) y **200** con uno de navegador.

**El clima** se pide una sola vez a Open-Meteo (archivo histórico reanalizado) y se cachea. Mientras
la caché exista, el notebook corre sin conexión a internet.

---

## 3. Limpieza y transformación

### 3.1 Selección de columnas — el conjunto se reduce a lo que el problema necesita

De las once columnas del archivo, **sólo tres construyen la unidad de análisis**: `Fecha`, `X`, `Y`.
El resto se descarta acá, y no en el modelado, con estos motivos:

| Columna | Destino | Motivo |
| --- | --- | --- |
| `Fecha`, `X`, `Y` | **Se conservan** | Definen cuándo y dónde: la unidad de análisis |
| `Departamento`, `fixed` | Se descartan | **Varianza cero** tras el recorte: un solo valor |
| `Localidad` | Se descarta | Dos valores, uno es `SIN DATOS`; la zona sale de la geometría |
| `Gravedad` | Se descarta | Agregada por día daría columnas que **suman exactamente el objetivo**: fuga perfecta |
| `Hora` | Se descarta | La unidad es el día; no sobrevive a la agregación |
| `Calle`, `Tipo de Siniestro` | Se descartan | No se usan como exógenas |
| `Dia Semana` | Se usa y se descarta | Sólo para **verificar** el formato de fecha (3.3) |

**La fila de `Gravedad` merece énfasis en el informe.** Desagregar el conteo por gravedad produce
`n_fatal + n_grave + n_leve + n_solo_danos`, que **suman exactamente `n_siniestros`**. Como
predictoras serían una fuga perfecta: un modelo que las use obtiene un ajuste impecable y valor
nulo. Se retiraron del panel por esa razón, no por falta de interés.

**Consecuencia declarada:** el conjunto vigente **no permite modelar por gravedad ni por franja
horaria** sin volver a ejecutar el ETL. Es barato — dos líneas — pero hay que decirlo.

### 3.2 Duplicados — `tablas/01_duplicados.csv`

| Indicador | Valor |
| --- | --- |
| Registros antes | 224.694 |
| **Filas duplicadas eliminadas** | **347** |
| Grupos con repetición | 321 |
| **Repeticiones en el grupo mayor** | **10** |
| Registros después | 224.347 |

En el recorte de Montevideo el efecto son **96 filas**.

**Criterio:** se eliminan las filas duplicadas en **todas** las columnas del archivo original,
conservando la primera. Se comparan las columnas completas y no las que sobreviven a la selección
de 3.1: con sólo fecha y coordenadas se borrarían siniestros distintos ocurridos el mismo día en la
misma esquina.

**Evidencia:** existen grupos de hasta diez filas idénticas byte a byte.
**Inferencia:** un siniestro no se repite diez veces en la misma esquina, a la misma hora, con el
mismo tipo y la misma gravedad — es un artefacto de carga.

**Efecto observado, que es el argumento fuerte:** con la zonificación anterior, el máximo del
objetivo era **11** y correspondía a **10 copias del mismo registro más uno distinto** — es decir,
2 siniestros reales. Deduplicar bajó ese máximo a 5. La cola alta del objetivo era, en su valor
extremo, un artefacto.

**Limitación del criterio, a declarar:** el dataset no tiene identificador de siniestro, así que dos
siniestros reales con atributos idénticos serían indistinguibles de un duplicado de carga. Es una
decisión conservadora sobre la cola alta.

### 3.3 Fecha — verificada, no supuesta

El ETL del PID usa `parsear_fecha_mixta`, que prueba `%m/%d/%Y`, `%d/%m/%Y` y `%Y-%m-%d` hasta que
uno funciona. **Es peligroso:** `05/06/2021` parsea con los dos primeros y da días distintos, sin
avisar.

Este notebook fija un único formato, `%m/%d/%Y`, y lo **verifica contra la columna `Dia Semana`**,
que es información independiente del propio archivo. La celda levanta `ValueError` si la
coincidencia no es total.

**Resultado:** coincidencia del **100,0000 %** en los 224.694 registros, con **0 fechas
inválidas** (con `%d/%m/%Y` la coincidencia es 6,80 %). El archivo es homogéneo y la suposición del
PID era innecesaria.

### 3.4 Coordenadas

Reproyección UTM 21S (`EPSG:32721`) → WGS84 (`EPSG:4326`), reutilizada del PID. Se agrega una
verificación que el PID no hacía: que los puntos caigan dentro del rectángulo que contiene a
Uruguay. **0 registros descartados** por este control.

---

## 4. Recorte del alcance

`tablas/02_recorte.csv`

| Paso | Registros | % del total |
| --- | --- | --- |
| Registros del país (deduplicados) | 224.347 | 100,0 % |
| Tras filtrar `MONTEVIDEO` | 62.288 | 27,8 % |
| Tras filtrar `Fecha >= 2021-01-01` | **39.580** | 17,6 % |
| Tras descartar 11 fuera de todo polígono (sección 5) | **39.569** | 17,6 % |

El conjunto queda **ordenado cronológicamente**, que es lo que necesitan después los rezagos y las
medias móviles del notebook de modelado.

### El filtro de 2021 no elimina el régimen de la pandemia — `tablas/03_pandemia_residual.csv`

| Período | Siniestros | Días | Media diaria |
| --- | --- | --- | --- |
| ene–jun **2021** | 2.957 | 181 | **16,34** |
| ene–jun 2022–2025 | 15.516 | 725 | **21,40** |
| **Diferencia** | | | **−23,7 %** |

**Evidencia:** el primer semestre de 2021 tiene una siniestralidad marcadamente inferior.
**Inferencia:** en Uruguay la ola de COVID y las restricciones de movilidad fueron justamente en ese
semestre.

*Nota para quien compare documentos:* `resumen_diagnostico_datos.md` informa **−23,6 %** para el
mismo cálculo. La diferencia son los 11 siniestros que caen fuera de todo polígono, que el ETL
descarta después de calcular esta tabla y el diagnóstico antes. Ambas cifras están respaldadas por
su propio artefacto; en el informe conviene citar una sola y decir sobre qué base se calculó. La justificación del filtro —«empezar en 2021 para que el modelo no vea la pandemia»—
**no se sostiene con los datos**.

**Decisión del equipo:** mantener 2021 completo y **declarar el sesgo en el informe**. La
alternativa —`FECHA_INICIO = "2021-07-01"`— cuesta seis meses de datos y es un cambio de una línea.
Consecuencia a declarar: el entrenamiento contiene un tramo con un régimen de movilidad que no
volverá a repetirse.

---

## 5. Zonificación: barrios de Montevideo

`tablas/03b_procedencia_capa_zonas.csv`, `tablas/04_zonas.csv`

**Criterio de asignación: intersección punto-polígono.** No se geocodifica ninguna dirección — el
CSV ya trae coordenadas X/Y. Se reproyecta el polígono a UTM y se pregunta qué barrio contiene cada
punto, resolviendo anillos interiores (agujeros) y multipolígonos.

| Indicador | Valor |
| --- | --- |
| Zonificación | **barrios** (62 polígonos) |
| Zonas con al menos un siniestro | **62** |
| Siniestros por zona — mínimo | **225** |
| Siniestros por zona — mediana | 570 |
| Siniestros por zona — máximo | 1.939 |
| **Zonas con 5 siniestros o menos** | **0** |
| Zonas que acumulan el 90 % | 49 |
| Siniestros fuera de todo polígono | **11 (0,03 %)** |

### Por qué barrios y no la grilla anterior

El proyecto usó primero una **grilla regular de 1 km** (403 celdas), como solución provisoria
mientras no se conseguía cartografía. La comparación explica la decisión:

| | Grilla 1 km (403 celdas) | **Barrios (62)** |
| --- | --- | --- |
| Zonas con ≤ 5 siniestros | **80** | **0** |
| Zonas con 1 solo siniestro | 28 | 0 |
| Mínimo por zona | 1 | **225** |
| Filas del panel | 735.878 | 113.212 |
| % de ceros | 95,08 % | **71,96 %** |

**Éste es el cambio que habilita el experimento que pidió el docente.** Con la grilla, un hold-out
de zonas quedaba dominado por celdas casi vacías y no podía responder si el modelo generaliza a
zonas no vistas. Con barrios, **todas las zonas tienen soporte suficiente**.

**Los 11 siniestros fuera de todo polígono se descartan y se documenta el conteo**, en lugar de
reasignarlos al barrio más cercano: la reasignación introduciría una decisión arbitraria sobre
casos que no cambian ninguna conclusión.

### Estratos de actividad — `tablas/05_estratos.csv`

| Estrato | Zonas | Siniestros | Mediana por zona | % de siniestros |
| --- | --- | --- | --- | --- |
| baja | 21 | 7.013 | 319,0 | 17,7 % |
| media | 20 | 11.334 | 570,5 | 28,6 % |
| alta | 21 | 21.222 | 997,0 | 53,6 % |

Terciles de actividad. Permiten entrenar **un** modelo y medirlo por estrato, o **uno por estrato**,
comparando ambos con el mismo protocolo, sin volver a correr el ETL.

**Advertencia metodológica, a declarar:** el estrato está calculado sobre **todo el período**, así
que es **descriptivo**. Antes de usarlo para elegir las zonas reservadas del «megamodelo» hay que
**recalcularlo sólo con el tramo de entrenamiento**: si no, la selección de zonas usaría información
del conjunto de prueba.

---

## 6. Variables exógenas

Dos bloques, ambos deterministas o externos al objetivo. Ninguno aprende de los siniestros, así que
pueden construirse en el ETL sin riesgo de fuga.

### 6.1 Codificación del calendario: `tipo_dia` — `tablas/06_calendario.csv`

En lugar de arrastrar `anio`, `mes`, `dia_mes`, `dia_semana`, `dia_anio`, `semana_iso` y `es_finde`,
el calendario se resume en **una sola variable categórica de tres niveles**:

| Nivel | Días | % del período |
| --- | --- | --- |
| `entre_semana` | 1.232 | 67,5 % |
| `fin_semana` | 504 | 27,6 % |
| `feriado` | 90 | 4,9 % |

El feriado tiene prioridad sobre el fin de semana.

**Por qué se fueron las otras** — cada motivo es distinto y el informe debería recogerlos:

- **`anio` es la peor con un corte cronológico:** el año del conjunto de prueba nunca aparece en
  entrenamiento, y un árbol que parta por esa variable extrapola a una constante.
- **`mes`, `dia_anio` y `semana_iso` son cíclicas** y como enteros mienten: diciembre (12) y enero
  (1) son adyacentes en la realidad y quedan máximamente distantes para el modelo.
- **Todas son recuperables desde `fecha`**, que es el índice del panel.

**Feriados: `categories=("public", "bank")`.** La configuración por omisión de la biblioteca
`holidays` para Uruguay reconoce sólo 25 feriados en el período y **omite Carnaval y Semana de
Turismo**, los dos períodos de mayor alteración de la movilidad del año. Con las dos categorías son
**90**.

**Costo declarado:** se pierde la diferencia entre días de semana (un viernes no es un martes) y la
estacionalidad anual. Es una simplificación deliberada; si el análisis de errores muestra estructura
semanal o estacional sin capturar, se revisa.

### 6.2 Clima — `tablas/07_clima.csv`

Serie **diaria única para todo el departamento** (punto −34,87 / −56,17), de Open-Meteo (archivo
histórico reanalizado), cacheada en `data/raw/clima_montevideo.csv`. **1.826 días, sin faltantes.**

Variables: `temp_media`, `temp_max`, `temp_min`, `precipitacion_mm`, `lluvia_mm`, `viento_max_kmh`.
Más dos construidas: `estado_clima` (código WMO agrupado en cinco niveles, reusando la tabla del
PID) y `llovio` (precipitación > 0,1 mm).

| Estado del clima | Días |
| --- | --- |
| lluvia | 825 |
| nublado | 813 |
| despejado | 188 |

Rangos observados: temperatura media 4,9–31,7 °C (media 17,0); precipitación 0–105,3 mm
(mediana 0); viento máximo 7,9–62,9 km/h.

**Supuesto declarado:** un solo punto para todo el departamento. A resolución diaria las variables
meteorológicas son prácticamente uniformes sobre unos 200 km² urbanos, y pedir una serie por barrio
multiplicaría por 62 las llamadas para devolver casi los mismos números. **Consecuencia importante:
el clima no puede explicar ninguna diferencia entre barrios** — aporta sólo variación temporal, la
misma para las 62 zonas.

---

## 7. El conjunto de modelado

### 7.1 El panel — `tablas/08_panel.csv`

| Indicador | Valor |
| --- | --- |
| Zonificación | barrios |
| Días del período | 1.826 |
| Zonas | 62 |
| **Filas del panel** | **113.212** |
| Siniestros | 39.569 |
| % de filas en cero | **71,96 %** |
| Media del objetivo | 0,3495 |
| Varianza del objetivo | 0,3957 |
| **Índice de dispersión (var/media)** | **1,132** |
| Máximo del objetivo | 7 |
| Columnas | 12 |

**`fecha` es el índice.** No es único —hay una fila por zona en cada fecha— y eso es deliberado:
permite cortar por tiempo directamente (`panel.loc["2024-03"]`), que es lo que hará el notebook de
modelado al partir cronológicamente. Si hace falta una clave única, es
`set_index(["fecha", "zona_id"])`.

### 7.2 Diccionario de datos

| Columna | Tipo | Rol |
| --- | --- | --- |
| `fecha` | datetime | **ÍNDICE** — día de la observación (no único) |
| `zona_id` | str | Barrio. **Identificador, no usar como predictor** |
| `n_siniestros` | int16 | **OBJETIVO** — siniestros en esa zona ese día |
| `estrato_actividad` | category | Tercil de actividad. **DESCRIPTIVO**: calculado sobre todo el período |
| `tipo_dia` | str | Codificación del calendario: entre_semana / fin_semana / feriado |
| `temp_media`, `temp_max`, `temp_min` | float | Temperatura diaria (°C) — Open-Meteo |
| `precipitacion_mm`, `lluvia_mm` | float | Precipitación diaria (mm) — Open-Meteo |
| `viento_max_kmh` | float | Viento máximo a 10 m (km/h) — Open-Meteo |
| `estado_clima` | str | Codificación del código WMO en 5 niveles |
| `llovio` | int8 | 1 si la precipitación superó 0,1 mm |

Diccionario completo, incluidos los demás archivos: `data/processed/diccionario_datos.csv`.

### 7.3 Archivos exportados — `tablas/11_exportacion.csv`

| Archivo | Filas | Columnas | Tamaño | Para qué |
| --- | --- | --- | --- | --- |
| `panel_diario_montevideo.csv` | 113.212 | 13 | 9,4 MB | **Conjunto de modelado** |
| `siniestros_montevideo.csv` | 39.569 | 6 | 2,5 MB | Capa limpia geolocalizada, para rearmar el panel con otra zonificación |
| `zonas_montevideo.csv` | 62 | 9 | 34 kB | Catálogo de barrios: actividad, estrato, centroide |
| `panel_zona_top.csv` | 1.826 | 13 | 0,1 MB | Serie de la zona más activa |
| `panel_zona_contraste.csv` | 1.826 | 13 | 0,1 MB | Serie de control |

`data/` no se versiona (política del `.gitignore`): estos archivos se regeneran ejecutando el
notebook.

### 7.4 Las dos zonas exportadas — `tablas/09_zonas_seleccionadas.csv`

| Papel | Barrio | Siniestros | % de días en cero |
| --- | --- | --- | --- |
| Zona más activa (primer modelo) | **UNIÓN** | 1.939 | 36,64 % |
| Zona de contraste (actividad mediana) | **TRES CRUCES** | 689 | 68,57 % |

**Por qué dos y no una.** La zona más activa tiene la serie con más señal del departamento, así que
sirve para poner a andar el pipeline; pero es la más densa y **no es representativa**: sus métricas
no son las del proyecto. La zona de contraste da, sin costo adicional, la primera medida de cuánto
se degrada un modelo al cambiar de zona — que es la pregunta del docente en versión reducida.

Dato ilustrativo: **ambas están en el estrato «alta»** y aun así una tiene 36,6 % de días en cero y
la otra 68,6 %. El tercil superior va de 91 a 1.939 siniestros y es internamente muy heterogéneo.

---

## 8. Verificaciones — `tablas/10_verificaciones.csv`

El notebook incorpora **13 comprobaciones que detienen la ejecución** si fallan, para que ningún
resultado del informe dependa de que alguien se acuerde de mirar una salida. **Las 13 en verde.**

| Verificación | Detalle |
| --- | --- |
| El panel conserva todos los siniestros del recorte | 39.569 vs 39.569 |
| El panel es el producto completo días × zonas | 113.212 filas |
| La clave (fecha, zona) no se repite | clave única |
| El índice es temporal y está ordenado | `DatetimeIndex` creciente |
| No quedan faltantes en el panel | 0 celdas vacías → no corresponde imputar |
| **Ninguna columna del panel es constante** | 12 columnas |
| **No hay columnas de gravedad en el panel** | sin fuga por gravedad |
| El calendario cubre todo el período sin huecos | 1.826 días |
| El clima cubre todo el período sin huecos | 1.826 días |
| `tipo_dia` tiene los tres niveles esperados | entre_semana / feriado / fin_semana |
| El objetivo es entero y no negativo | `n_siniestros` |
| Los eventos están ordenados cronológicamente | `sort_values` por fecha |
| Los centroides de zona caen dentro de Uruguay | 62 zonas |

**Dos de estas verificaciones existen porque una auditoría encontró los problemas que previenen**, y
vale la pena contarlo en el informe como parte del proceso: «ninguna columna constante» y «no hay
columnas de gravedad» se agregaron tras detectar columnas de varianza cero y la fuga por gravedad.

**Y una de ellas ya sirvió:** al cambiar de la grilla a barrios, «ninguna columna constante» falló.
El umbral fijo `zona_activa` (≥ 60 siniestros en el período) discriminaba 167 de 403 celdas en la
grilla, pero con barrios —mínimo 225 siniestros— quedaba en `True` para las 62 zonas. Se retiró del
panel (sigue en el catálogo de zonas) y la selección de la zona de contraste pasó a usar el estrato
por terciles, que se adapta solo a la granularidad.

### Verificación cruzada independiente

`notebooks/diagnostico_datos.ipynb` reconstruye el panel **desde las fuentes crudas**, con su propia
implementación de la asignación punto-polígono, y compara. **Las cinco comprobaciones coinciden**
(113.212 filas, 39.569 siniestros, 62 zonas, 1.826 días, máximo 7). Dos implementaciones
independientes llegando al mismo resultado es evidencia real de que el pipeline es correcto, y es
un argumento fuerte para la defensa.

---

## 9. Cobertura de la rúbrica de preparación

La consigna pide *«limpieza, transformación, imputación, codificación, escalado, balanceo, selección
o construcción de variables, reducción de dimensionalidad u otras acciones cuando correspondan»*.
Ésta es la trazabilidad completa, incluido **lo que no corresponde y por qué** — que también hay que
declarar, no omitir:

| Acción | Estado | Dónde / por qué |
| --- | --- | --- |
| **Limpieza** | ✅ Hecha | Duplicados exactos, fecha verificada, coordenadas validadas (3) |
| **Transformación** | ✅ Hecha | UTM → WGS84, agregación a (día, barrio) (3.4, 7.1) |
| **Imputación** | ⬜ **No corresponde** | 0 faltantes en las columnas que sobreviven. Se documenta con el conteo, no se omite |
| **Codificación** | ✅ Hecha | `tipo_dia` (3 niveles) y `estado_clima` (5 niveles) (6) |
| **Escalado** | ⬜ **Fuera del ETL a propósito** | Debe ajustarse sólo con entrenamiento → notebook de modelado |
| **Balanceo** | ⬜ **Fuera del ETL a propósito** | Depende del modelo. Se documenta la tasa de ceros para decidirlo |
| **Construcción de variables** | ✅ Parcial | Zona, `tipo_dia`, clima, estrato. **Falta la tasa histórica del barrio** |
| **Selección de variables** | ✅ Hecha | Se descartan constantes, no usadas y las de gravedad por fuga (3.1) |
| **Reducción de dimensionalidad** | ⬜ **No corresponde** | El conjunto final tiene 12 columnas |

**Sobre el balanceo**, que es la decisión abierta más importante: con **71,96 % de ceros** y
dispersión 1,132, la primera opción a probar es una **pérdida de Poisson o Tweedie** (GLM,
`HistGradientBoostingRegressor(loss="poisson")`, LightGBM `objective="poisson"`), que maneja el
exceso de ceros nativamente y **no necesita balanceo**. Si se pasa a una formulación binaria
(«¿hubo al menos un siniestro?») entran en juego los pesos por clase o el submuestreo, y hay que
declarar cuál se usó. Balancear en el ETL obligaría a todos los modelos posteriores a heredar una
decisión que sólo tiene sentido para algunos, y rompería la comparación con la línea base.

---

## 10. Limitaciones y lo que NO puede afirmarse

| Limitación | Sección | Cómo se trata |
| --- | --- | --- |
| Régimen de pandemia dentro del período | 4 | Se declara; alternativa: iniciar 2021-07-01 |
| El clima no varía entre barrios | 6.2 | Declararlo: sólo aporta variación temporal |
| Clima observado, no pronosticado | 6.2 | El desempeño medido es una **cota optimista** del operativo |
| Estrato calculado sobre todo el período | 5 | Recalcular sólo con entrenamiento antes de reservar zonas |
| Sin gravedad ni franja horaria en el conjunto | 3.1 | Declarar que exige volver a ejecutar el ETL |
| 11 siniestros fuera de todo polígono | 5 | Se descartan; se documenta el conteo |
| Duplicados: criterio sin identificador de siniestro | 3.2 | Decisión conservadora, declarada |
| Falta la variable de nivel de zona | 6 | **Pendiente prioritario** del notebook de modelado |
| Código geográfico duplicado entre notebooks | — | Candidato a migrar a `src/` |

### Frases que NO deben aparecer en el informe

- ❌ «El ETL prepara los datos para el modelo.» → Prepara **parte**: escalado, balanceo,
  particiones y variables con memoria quedan fuera **a propósito**, y hay que explicar por qué.
- ❌ «Se imputaron los valores faltantes.» → **No se imputó nada**: no hay faltantes en las columnas
  que sobreviven. Decir que no correspondió es la respuesta correcta.
- ❌ «Los datos están balanceados.» → No se balanceó. La decisión es del notebook de modelado.
- ❌ «El clima explica las diferencias entre barrios.» → Es una serie única para el departamento:
  **no puede** explicar ninguna diferencia entre zonas.
- ❌ «Se eliminaron los outliers.» → No se eliminaron outliers. Se eliminaron **duplicados exactos**,
  que es otra cosa, y el efecto sobre la cola alta se explica en 3.2.
- ❌ «El conjunto incluye la gravedad de los siniestros.» → Se retiró deliberadamente por fuga.

---

## 11. Índice de artefactos

`experiments/etl_montevideo/` — 14 tablas, 1 mapa HTML, 1 figura PNG.

| Artefacto | Qué respalda |
| --- | --- |
| `tablas/00_procedencia.csv` | sha256 y tamaño del CSV de siniestros |
| `tablas/01_duplicados.csv` | Conteo de duplicados y grupo mayor (3.2) |
| `tablas/02_recorte.csv` | Cascada del recorte al alcance (4) |
| `tablas/03_pandemia_residual.csv` | Efecto del filtro de 2021 (4) |
| `tablas/03b_procedencia_capa_zonas.csv` | sha256 y polígonos de la capa de barrios (2) |
| `tablas/04_zonas.csv` | Resumen de la zonificación (5) |
| `tablas/05_estratos.csv` | Terciles de actividad (5) |
| `tablas/06_calendario.csv` | Distribución de `tipo_dia` (6.1) |
| `tablas/07_clima.csv` | Distribución de `estado_clima` (6.2) |
| `tablas/08_panel.csv` | Dimensiones y estadísticos del panel (7.1) |
| `tablas/09_zonas_seleccionadas.csv` | Zona top y de contraste (7.4) |
| `tablas/10_verificaciones.csv` | Las 13 comprobaciones (8) |
| `tablas/11_exportacion.csv` | Archivos exportados (7.3) |
| `tablas/12_diccionario_datos.csv` | Diccionario completo (7.2) |
| `figuras/mapa_zonas.html` | Mapa interactivo de barrios por actividad |
| `figuras/series_zonas.png` | Series diarias de la zona top y la de contraste |

**Antes de citar cualquier cifra:** verificar que los `sha256` de `00_procedencia.csv` y
`03b_procedencia_capa_zonas.csv` sigan siendo los de las fuentes vigentes. Si alguna cambió, hay que
volver a ejecutar el notebook.

---

## 12. Qué queda pendiente

Lo que este ETL deja planteado para el notebook de modelado:

1. **Construir la tasa histórica del barrio**, ajustada sólo con el tramo de entrenamiento. Es el
   pendiente prioritario: sin una variable de nivel de zona, el modelo predice lo mismo para los 62
   barrios cada día. El diagnóstico lo cuantifica
   ([`resumen_diagnostico_datos.md`](resumen_diagnostico_datos.md), sección 5.3).
2. **Definir las particiones cronológicas** con el conjunto de prueba reservado.
3. **Recalcular `estrato_actividad` sólo con entrenamiento** antes de reservar zonas.
4. **Decidir el escalado y el balanceo**, y declarar ambas decisiones.
5. **Decidir el filtro de 2021**: mantener y declarar el sesgo, o mover el inicio a 2021-07-01.
6. **Interpolación de ceros** — la técnica que pidió el docente. Se implementó y se descartó de esta
   versión porque **mira días posteriores**: sólo puede usarse como objetivo alternativo de
   entrenamiento y hay que calcularla dentro de cada partición. Se revisa ahora que la zonificación
   por barrios está fijada.
7. **Migrar a `src/`** el código geográfico duplicado entre este notebook y el de diagnóstico.
