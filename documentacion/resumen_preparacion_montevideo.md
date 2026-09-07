# Resumen del ETL y la preparación de datos — Montevideo por municipios

**Notebook:** [`notebooks/preparacion_montevideo.ipynb`](../notebooks/preparacion_montevideo.ipynb)
**Artefactos:** `experiments/etl_montevideo/` (15 tablas CSV, 1 mapa HTML, 1 figura PNG)
**Salida:** `data/processed/` (6 archivos, regenerables, no versionados)
**Fecha de ejecución:** 2026-09-07
**Alcance:** Montevideo, **2021-07-01 a 2025-12-31**, unidad de análisis **(día, municipio)**

---

## 0. Cómo usar este documento

Este archivo es **contexto autocontenido** para redactar la sección *Metodología — preparación*
del informe (guía PAA 6.1) sin necesidad de abrir el repositorio. Reúne qué hace el ETL, con qué
criterio, y la referencia al artefacto que respalda cada cifra.

**Reglas que quien redacte debe respetar:**

1. **Ninguna cifra sin artefacto.** Todos los números salen de una ejecución real y llevan al lado
   la tabla que los respalda (`tablas/NN_nombre.csv`). Si hace falta un número que no está acá,
   marcarlo como `<!-- PENDIENTE: ... -->` en lugar de completarlo.
2. **Distinguir evidencia de inferencia.** Separar *lo que los datos muestran* de *lo que el
   equipo concluye*.
3. **No escribir Introducción ni Marco teórico** a partir de este documento.
4. **Respetar los límites de la sección 10.** Hay afirmaciones que este ETL *no* sostiene.

**Documento hermano:** [`resumen_diagnostico_datos.md`](resumen_diagnostico_datos.md) cubre
*Metodología — datos* (calidad, cobertura, adecuación, limitaciones). Este cubre *preparación*.
Las decisiones de **alcance** —qué zonas y desde cuándo— se justifican allá con evidencia; acá se
aplican y se verifican.

> ### ⚠️ Este documento reemplaza a la versión por barrios
>
> | Versión | Alcance | Estado |
> | --- | --- | --- |
> | 2026-09-04 | Montevideo, 62 barrios, desde 2021-01-01 | **superada** |
> | **2026-09-07** | **Montevideo, 8 municipios, desde 2021-07-01** | **vigente** |
>
> **Las cifras de la versión anterior no deben citarse.** El cambio deja sin objeto tres cosas que
> ese documento discutía largamente: el **balanceo** (ya no hay exceso de ceros), la
> **interpolación de ceros** (no hay nada que interpolar) y el **estrato de actividad** como
> variable (con 8 zonas en un rango de 1,71× los terciles son arbitrarios).

---

## 1. Qué hace este notebook y qué lo distingue

Adapta al contexto de aprendizaje automático el pipeline ETL del **Proyecto de Ingeniería de Datos
(PID)** que está en `etl/`, y deja en `data/processed/` el conjunto con el que se entrenan los
modelos. Extrae del CSV crudo de UNASEV, limpia, recorta al alcance, asigna cada siniestro a su
municipio, construye las variables exógenas y arma el **panel día × municipio** con los ceros
explícitos.

**Lo que lo distingue de un script de carga:** cada decisión de preparación está justificada en el
propio notebook, y **dieciséis verificaciones detienen la ejecución** si algo no cierra
(sección 8). Ningún resultado del informe depende de que alguien se acuerde de mirar una salida.

### Trazabilidad respecto del PID

| PID (`etl/`) | Este notebook | Por qué |
| --- | --- | --- |
| Tres países (UY, BR, ES) | Sólo Uruguay → Montevideo | Alcance acordado con el docente |
| Carga a PostgreSQL y MongoDB | Carga a CSV en `data/processed/` | El PAA se entrega como repositorio ejecutable, sin infraestructura |
| Unidad = siniestro | Unidad = **(día, municipio)** | El objetivo es el conteo por zona y día |
| `encoding='latin-1'` | `encoding='utf-8'` | El CSV es UTF-8; latin-1 rompe los acentos |
| `parsear_fecha_mixta` (prueba formatos hasta que uno ande) | Formato fijo `%m/%d/%Y` **verificado contra `Dia Semana`** | El formato mixto era una suposición; el archivo es homogéneo |
| Sin tratamiento de duplicados | Duplicados exactos eliminados | Distorsionaban la cola alta del objetivo |
| Clima a PostgreSQL, por hora y por punto | Clima diario para Montevideo, cacheado en `data/raw/` | Sin base de datos, y la unidad es el día |
| Reproyección UTM→WGS84 | Reutilizada | Sirve para el mapa y para la asignación a municipios |

**`etl/` no se ejecuta en el PAA:** depende de PostgreSQL, MongoDB, Docker y rutas `/app/...`. Se
conserva en el repositorio como fuente de la adaptación.

---

## 2. Fuentes y trazabilidad

| Fuente | Archivo | sha256 (prefijo) | Artefacto |
| --- | --- | --- | --- |
| Siniestros | `data/raw/uru_siniestros_unificado.csv` | `48a8a7e8…` | `00_procedencia` |
| **Municipios** | `data/raw/municipios_montevideo.geojson` | `ed0ba13e…` | `03b_procedencia_capa_zonas` |
| Clima | `data/raw/clima_montevideo.csv` | — | `07_clima` |

**Siniestros.** Heredado del PID. Fuente original: UNASEV. 224.694 registros × 11 columnas, país
entero, 2018–2025. **Sin valores nulos** en ninguna columna.

**Municipios.** Capa oficial de la Intendencia de Montevideo (GeoServer institucional,
`montevideo.gub.uy/app/geoserver`), capa `mapstore-tematicas:zon_v_sig_municipios`, descargada por
WFS `GetFeature` en GeoJSON (`EPSG:4326`) el 2026-09-07. **8 polígonos**: MUNICIPIO A, B, C, CH,
D, E, F y G. Licencia: `Fees: none` / `AccessConstraints: none`.

> **Dos detalles no obvios, por si hay que reobtenerla.** El servicio devuelve **403** ante el
> `User-Agent` por omisión de una librería HTTP y **200** con uno de navegador. Y el archivo
> `data/raw/municipios.json` **no es la capa**: es la respuesta `GetCapabilities` (XML) del
> servicio WMS, útil sólo para encontrar el nombre de la capa.

**Clima.** Open-Meteo, archivo histórico reanalizado, serie diaria única para el departamento
(−34,87 / −56,17), cacheada en `data/raw/`. El notebook la acota al período: **1.645 días, sin
faltantes**.

**El repositorio no versiona `data/raw/` ni `data/processed/`.** Ambos son regenerables: el
notebook detecta las fuentes solo y registra su `sha256` en cada corrida, de modo que se puede
verificar más adelante que un resultado del informe salió de estos datos y no de otra versión.

---

## 3. Limpieza y transformación

### 3.1 Selección de columnas — el conjunto se reduce a lo que el problema necesita

El modelo predice **cuántos siniestros habrá por municipio y día**. Todo lo que no sirve para eso
se descarta en el ETL, no en el modelado:

| Columna del CSV | Destino | Motivo |
| --- | --- | --- |
| `Fecha`, `X`, `Y` | **Se conservan** | Definen la unidad de análisis: cuándo y dónde |
| `Departamento`, `fixed` | Se descartan | **Varianza cero** tras el recorte: un solo valor |
| `Localidad` | Se descarta | Faltante encubierto; la zona sale de la geometría |
| `Gravedad` | Se descarta | Agregada por día daría columnas que **suman exactamente el objetivo**: fuga perfecta |
| `Hora` | Se descarta | La unidad es el día; no sobrevive al agregado |
| `Calle`, `Tipo de Siniestro` | Se descartan | No se usan como exógenas; `Calle` tiene 854 `SIN DATOS` |
| `Dia Semana` | Se usa y se descarta | Sólo para **verificar** el formato de fecha (3.3) |

**Consecuencia declarada:** el conjunto ya no permite modelar por gravedad ni por franja horaria
sin volver a correr el ETL. Es barato —son dos líneas— pero hay que decirlo.

**Aunque `Gravedad` se descarte, se valida.** El notebook controla que sus valores sigan siendo el
vocabulario del PID (`FATAL`, `GRAVE`, `LEVE`, `SIN LESIONADOS`) y **falla** si la fuente
introduce uno nuevo: es una alarma barata sobre un cambio silencioso en el origen.

### 3.2 Duplicados — `tablas/01_duplicados.csv`

| Indicador | Valor |
| --- | --- |
| Registros antes | 224.694 |
| **Filas duplicadas eliminadas** | **347** |
| Grupos con repetición | 321 |
| **Repeticiones en el grupo mayor** | **10** |
| Registros después | 224.347 |

**Evidencia:** el archivo trae registros repetidos byte a byte; el caso extremo son diez filas
idénticas el 2021-07-30 en la misma esquina.

**Inferencia del equipo:** un siniestro no se repite diez veces en la misma esquina, a la misma
hora, con el mismo tipo y la misma gravedad. Es un artefacto de carga, no eventos distintos.

**Criterio, y por qué importa el detalle:** se eliminan las filas duplicadas en **todas** las
columnas del archivo original —**no** en las que sobreviven al paso 3.1, que serían muchas menos y
borrarían siniestros realmente distintos ocurridos el mismo día en la misma esquina—, conservando
la primera. El dataset **no tiene identificador de siniestro**, así que la decisión es
conservadora sobre la cola alta del objetivo y queda declarada.

### 3.3 Fecha — verificada, no supuesta

El PID usaba `parsear_fecha_mixta`, que probaba `%m/%d/%Y`, `%d/%m/%Y` y `%Y-%m-%d` hasta que uno
funcionara. Eso es peligroso: `05/06/2021` parsea con los dos primeros y **da días distintos, sin
avisar**.

Acá se fija `%m/%d/%Y` y se **verifica contra la columna `Dia Semana`**, que es información
independiente del propio archivo. Resultado: **100,0000 % de coincidencia sobre 224.694 registros
y 0 fechas inválidas**. La celda falla ruidosamente si la coincidencia no es total.

Es una verificación barata que ya se pagó sola dos veces: refutó la suposición del PID, y en el
notebook de diagnóstico volvió a aparecer el mismo riesgo al leer el panel exportado (una fecha
ISO leída con `dayfirst` se interpreta como otro día, en silencio).

### 3.4 Coordenadas

Reproyección UTM 21S → WGS84, reutilizada de `etl/transform/transformer.py`, más una verificación
que el PID no hacía: que los puntos caigan dentro del rectángulo que contiene a Uruguay. Una
coordenada mal cargada crearía una zona fantasma. **Resultado: todas las coordenadas caen dentro
de Uruguay.**

---

## 4. Recorte del alcance — `tablas/02_recorte.csv`

| Paso | Registros | % del total |
| --- | --- | --- |
| Registros del país (ya deduplicados) | 224.347 | 100,0 % |
| Tras filtrar `MONTEVIDEO` | 62.288 | 27,8 % |
| **Tras filtrar `fecha >= 2021-07-01`** | **36.623** | **16,3 %** |
| Tras descartar 11 fuera de todo polígono (§5) | **36.612** | 16,3 % |

**Período:** 1.645 días, 2021-07-01 a 2025-12-31.

### El inicio de la serie: decisión tomada, no advertencia — `tablas/03_inicio_serie.csv`

La versión anterior de este ETL empezaba el 2021-01-01 y **dejaba la decisión abierta**. El filtro
se había puesto «para que el modelo no vea la pandemia», pero en Uruguay la ola de COVID y las
restricciones de movilidad fueron en el **primer semestre de 2021**, dentro del recorte.

La decisión se tomó el 2026-09-07: **`FECHA_INICIO = "2021-07-01"`**. La justificación en tres
pasos está en el notebook de diagnóstico (sección 3.1, tablas `12` a `12e`) y **no se repite acá**:
déficit de nivel de −23,7 % en ene–jun 2021, índice estacional que descarta que sea tendencia
(feb–jun entre −7,0 % y −17,2 %), y verificación de que jul–dic 2021 ya encadena normal.

Lo que el ETL sí hace es **verificar que el recorte quedó donde debe**, comparando el mismo tramo
de meses año contra año:

| Año | Media diaria (jul–dic) | Variación interanual |
| --- | --- | --- |
| **2021** | **21,39** | — |
| 2022 | 22,05 | +3,1 % |
| 2023 | 22,68 | +2,8 % |
| 2024 | 23,96 | +5,7 % |
| 2025 | 24,62 | +2,8 % |

El notebook **detiene la ejecución** si el primer año se aparta más de un 15 % de los siguientes
en el mismo tramo de meses. Corrida vigente: **−8,3 %**, dentro del margen — es la tendencia
creciente general de la serie, no un régimen distinto.

> **Nota de coherencia entre documentos.** Esta tabla coincide dígito a dígito con la `12c` del
> diagnóstico, aunque las dos se calculan sobre bases levemente distintas: el diagnóstico incluye
> los 11 siniestros que caen fuera de todo polígono y el ETL ya los descartó. La diferencia está
> por debajo del segundo decimal.

---

## 5. Zonificación: municipios de Montevideo

`tablas/03b_procedencia_capa_zonas.csv`, `03c_asignacion_zonas.csv`, `04_zonas.csv`

### Por qué municipios y no barrios

**Criterio, y no es estadístico:** el municipio es la unidad de descentralización
político-administrativa del departamento — **tiene gobierno propio con competencias en tránsito**,
de modo que una predicción por municipio se puede accionar. Un barrio no tiene a quién dirigirle
una recomendación de asignación de recursos.

**El costo está medido y hay que declararlo** (diagnóstico, §4.2 y §5.4): entre el municipio más y
el menos activo hay **1,71×** de diferencia, contra ~10× entre barrios. El margen para *ordenar*
zonas se estrechó mucho.

### Asignación: intersección punto-polígono — `tablas/03c_asignacion_zonas.csv`

No se geocodifica ninguna dirección: el CSV ya trae X/Y en UTM 21S. Se reproyecta el polígono a
UTM y se pregunta qué municipio contiene cada punto, resolviendo anillos interiores y
multipolígonos.

| Indicador | Valor |
| --- | --- |
| Polígonos en la capa | 8 |
| **Siniestros asignados** | **36.612** |
| Siniestros fuera de todo polígono | **11 (0,03 %)** |
| Municipios con al menos un siniestro | **8 de 8** |

**Decisión:** los 11 se **descartan y se documenta el conteo**, en lugar de reasignarlos al
municipio más cercano. La reasignación introduciría una decisión arbitraria sobre casos que no
cambian ninguna conclusión.

### Cambio de conducta: la capa es obligatoria

La versión anterior **caía a una grilla de 1 km** cuando no encontraba la capa, y lo avisaba por
pantalla. El problema es que producía igual un conjunto completo, de otro alcance (403 zonas,
95,08 % de ceros), que quedaba en `data/processed/` **indistinguible del bueno**. Ahora el
notebook **falla ruidosamente**: es preferible no correr a correr mal.

### Catálogo de municipios — `data/processed/zonas_montevideo.csv`

| Municipio | Siniestros | % del total | Días con siniestro |
| --- | --- | --- | --- |
| C | 5.783 | 15,8 % | 1.566 |
| B | 5.377 | 14,7 % | 1.562 |
| D | 5.319 | 14,5 % | 1.572 |
| A | 5.016 | 13,7 % | 1.549 |
| F | 4.424 | 12,1 % | 1.533 |
| G | 3.701 | 10,1 % | 1.446 |
| E | 3.615 | 9,9 % | 1.414 |
| CH | 3.377 | 9,2 % | 1.386 |

Mediana 4.720 · **razón máximo/mínimo 1,71×** · 7 de 8 municipios acumulan el 90 % de los
siniestros (`04_zonas`).

### Estratos de actividad: por qué dejan de usarse — `tablas/05_estratos.csv`

| Estrato | Zonas | Siniestros | Mínimo | Máximo | % |
| --- | --- | --- | --- | --- | --- |
| baja | 3 | 10.693 | 3.377 | 3.701 | 29,2 % |
| media | 2 | 9.440 | 4.424 | 5.016 | 25,8 % |
| alta | 3 | 16.479 | 5.319 | 5.783 | 45,0 % |

**`estrato_actividad` deja de incorporarse al panel y queda sólo en el catálogo.** Dos razones,
las dos declarables:

1. **Con 62 barrios era defendible** —separaba zonas cuyo volumen difería en un orden de
   magnitud—. **Con 8 municipios reparte ocho unidades en tres grupos dentro de un rango de
   1,71 ×**: los cortes son arbitrarios y no describen ninguna diferencia real. La tabla de arriba
   lo muestra: el estrato «baja» concentra el 29,2 % de los siniestros.
2. Está calculada sobre **todo el período**, así que como predictora sería una **fuga**.

`zona_activa` se retira por completo: era un umbral absoluto pensado para la grilla dispersa y con
municipios es cierto para los ocho, es decir, no informa nada.

**Consecuencia declarada: el panel exportado no lleva ninguna variable de nivel de zona.** Es
deliberado. El diagnóstico (§5.3) midió que la tasa histórica del municipio es el bloque más útil
fuera de muestra, pero **debe estimarse sólo con el tramo de entrenamiento**, y eso es trabajo del
notebook de modelado. Ponerla acá filtraría información del test.

---

## 6. Variables exógenas

Dos bloques, los dos deterministas o externos al objetivo: **calendario** y **clima**. Ninguno
aprende nada de los siniestros, así que pueden construirse en el ETL sin riesgo de fuga.

### 6.1 Codificación del calendario: `tipo_dia` — `tablas/06_calendario.csv`

| Nivel | Días | % |
| --- | --- | --- |
| `entre_semana` | 1.114 | 67,7 % |
| `fin_semana` | 454 | 27,6 % |
| `feriado` | **77** | 4,7 % |

En lugar de arrastrar `anio`, `mes`, `dia_mes`, `dia_semana`, `dia_anio`, `semana_iso` y
`es_finde`, el calendario se resume en **una sola categórica de tres niveles**. Por qué se van las
otras:

- **`anio`** es la peor de todas con un corte cronológico: el año del test nunca aparece en
  entrenamiento y un árbol extrapola a una constante.
- **`mes`, `dia_anio`, `semana_iso`** son **cíclicas** y como enteros mienten: diciembre = 12 y
  enero = 1 quedan máximamente distantes.
- Todas son **recuperables desde `fecha`**, que es el índice del panel.

**Feriados: `categories=("public", "bank")`.** Con la configuración por omisión de `holidays`
aparecen **23** feriados en el período contra **77** con las dos categorías, y quedan afuera
**Carnaval y Semana de Turismo**, los dos períodos de mayor cambio de movilidad del año en Uruguay
(diagnóstico, `16_feriados` y `16b`). Por año: 5 en 2021 (medio año) y 18 en cada uno de 2022 a
2025.

**Costo declarado, y ahora medido.** Se pierde la diferencia entre días de semana y la
estacionalidad anual. Con la unidad agregada a municipios eso ya no es inocuo: el día de la semana
explica un **20,8 %** de la varianza de la serie diaria del departamento, con el viernes en
**25,74** siniestros/día contra **16,06** el domingo (diagnóstico, `20b` y `20c`). `tipo_dia`
captura **22,3 %**, así que la simplificación sale barata **hoy**; si el análisis de errores
muestra estructura semanal sin capturar, el día de la semana se recupera desde `fecha` **sin
volver a correr el ETL**.

### 6.2 Clima — `tablas/07_clima.csv`

Adapta `etl/enrich/enriquecer_clima.py` del PID, que consultaba la API **por siniestro y por
hora** y escribía a PostgreSQL. Acá la unidad es el día y no hay base de datos: se pide **una
serie diaria única para Montevideo** y se cachea, de modo que el notebook vuelve a correr sin red.

Variables: `temp_media`, `temp_max`, `temp_min`, `precipitacion_mm`, `lluvia_mm`,
`viento_max_kmh`, más dos construidas: `estado_clima` (código WMO agrupado en cinco niveles,
reusando la tabla del PID) y `llovio` (precipitación > 0,1 mm). **1.645 días, 0 faltantes → no
corresponde imputar.**

| `estado_clima` | Días |
| --- | --- |
| nublado | 745 |
| lluvia | 733 |
| despejado | 167 |

*(los niveles `niebla` y `tormenta` existen en la codificación pero no aparecen en el período)*

**Un solo punto para todo el departamento.** A resolución diaria las variables meteorológicas son
prácticamente uniformes sobre unos 200 km² urbanos; pedir una serie por municipio multiplicaría
por ocho las llamadas para devolver casi los mismos números. **Consecuencia que el informe debe
recoger: el clima no puede explicar ninguna diferencia entre municipios**, sólo variación temporal
común a los ocho.

> ### ⚠️ Advertencia sobre la utilidad de este bloque
>
> El diagnóstico midió **fuera de muestra** que agregar el clima a la línea base **no mejora
> nada**: −11,5 % con clima contra −11,8 % sin él (`21c`). Se conserva en el conjunto porque ya
> está construido y no cuesta nada, pero **mantenerlo en el modelo final exige una justificación
> mejor que «estaba disponible»**.

**Clima observado, no pronosticado.** Se usa el archivo histórico reanalizado, que para una fecha
pasada da la observación. Un sistema en producción tendría un **pronóstico**, con su propio error:
el desempeño medido es una **cota optimista** del operativo.

---

## 7. El conjunto de modelado

### 7.1 El panel — `tablas/08_panel.csv`

| Indicador | Valor |
| --- | --- |
| Zonificación | municipios |
| Días del período | 1.645 |
| Zonas | 8 |
| **Filas del panel** | **13.160** |
| Siniestros | **36.612** |
| **% de filas en cero** | **8,60 %** |
| Media del objetivo | **2,7821** |
| Varianza del objetivo | 3,5039 |
| **Índice de dispersión (var/media)** | **1,259** |
| Máximo del objetivo | 13 |
| Columnas | 11 (+ índice) |

Una fila por día y municipio, **con los ceros explícitos**: sin ellos el modelo sólo vería los
días en que pasó algo y no podría aprender cuándo *no* pasa nada.

**`fecha` queda como índice y no es único** —hay una fila por municipio en cada fecha—, a
propósito: permite cortar por tiempo directamente (`panel.loc["2024-03"]`), que es lo que hará el
notebook de modelado al partir cronológicamente. Si hace falta una clave única, es
`set_index(["fecha", "zona_id"])`.

**El calendario del panel es fijo** (`FECHA_INICIO` → último día observado), no el mínimo y el
máximo de los datos, para que no cambie de tamaño si se agregan o quitan registros de los extremos.

**Ninguna columna de gravedad.** `n_fatal + n_grave + n_leve + n_solo_danos` suman exactamente
`n_siniestros`: como predictoras serían una fuga perfecta.

#### Comparación con las zonificaciones anteriores

| Zonificación | Zonas | Filas | % ceros | Media | Dispersión | Máx. |
| --- | --- | --- | --- | --- | --- | --- |
| Grilla de 1 km (superada) | 403 | 735.878 | 95,08 % | 0,0538 | 1,136 | 5 |
| Barrios (superada) | 62 | 113.212 | 71,96 % | 0,3495 | 1,132 | 7 |
| **Municipios (vigente)** | **8** | **13.160** | **8,60 %** | **2,7821** | **1,259** | **13** |

> **Trazabilidad:** sólo la última fila sale de un artefacto vigente (`08_panel`). Las dos
> primeras se conservan de corridas anteriores cuyos artefactos fueron borrados; su respaldo es
> `HANDOFF.md`. Citarlas como **historial del proyecto**, no como resultado de esta ejecución.

### 7.2 Balanceo: no corresponde con esta zonificación

**El objetivo ya no tiene exceso de ceros: son el 8,60 % de las filas.** Es una regresión de
conteo ordinaria, con media cercana a tres siniestros por municipio y día.

- La familia natural sigue siendo **Poisson**, con **binomial negativa** como primera extensión
  razonable por la sobredispersión leve (índice 1,259).
- Las variantes ***zero-inflated*** y el **submuestreo de ceros** que se contemplaban con las
  zonificaciones anteriores **quedan sin objeto**.
- La **interpolación de ceros** que había pedido el docente también pierde sentido: se pensó para
  un panel dominado por ceros estructurales, y con un 8,60 % no hay nada que interpolar.

**Esto invalida el argumento que la versión anterior de este documento daba sobre el balanceo.**
El informe no puede repetirlo: describiría un conjunto que ya no existe.

### 7.3 Diccionario de datos

`data/processed/diccionario_datos.csv` (50 filas, copia en `tablas/12_diccionario_datos.csv`).
Columnas del panel:

| Columna | Qué es |
| --- | --- |
| `fecha` | ÍNDICE — día de la observación (no único: una fila por municipio) |
| `zona_id` | Municipio. **Identificador, no usar como predictor** |
| `n_siniestros` | **OBJETIVO** — siniestros en ese municipio ese día |
| `tipo_dia` | CODIFICACIÓN del calendario: entre_semana / fin_semana / feriado |
| `temp_media`, `temp_max`, `temp_min` | Temperaturas diarias (°C) — Open-Meteo |
| `precipitacion_mm`, `lluvia_mm` | Precipitación y lluvia diarias (mm) — Open-Meteo |
| `viento_max_kmh` | Velocidad máxima del viento a 10 m (km/h) — Open-Meteo |
| `estado_clima` | CODIFICACIÓN del código WMO en 5 niveles |
| `llovio` | 1 si la precipitación superó 0,1 mm |

### 7.4 Archivos exportados — `tablas/11_exportacion.csv`

| Archivo | Filas | Columnas | Tamaño |
| --- | --- | --- | --- |
| `panel_diario_montevideo.csv` — **conjunto de modelado** | 13.160 | 12 | 1,0 MB |
| `siniestros_montevideo.csv` — capa limpia geolocalizada | 36.612 | 6 | 2,2 MB |
| `zonas_montevideo.csv` — catálogo | 8 | 8 | — |
| `panel_zona_top.csv` | 1.645 | 12 | 0,1 MB |
| `panel_zona_contraste.csv` | 1.645 | 12 | 0,1 MB |
| `diccionario_datos.csv` | 50 | 4 | — |

Se exporta en CSV con separador `,` y fechas ISO (`%Y-%m-%d`). `siniestros_montevideo.csv` existe
para poder **rearmar el panel con otra zonificación** sin volver a limpiar desde el CSV crudo.

### 7.5 Las dos series por municipio — `tablas/09_zonas_seleccionadas.csv`

| Papel | Municipio | Siniestros | % de días en cero |
| --- | --- | --- | --- |
| Más activo | **C** | 5.783 | 4,80 % |
| Contraste (actividad mediana) | **A** | 5.016 | 5,84 % |

> ### ⚠️ Su utilidad cambió con la zonificación
>
> Con 62 barrios este par medía algo real: la zona más densa y una mediana diferían en un orden de
> magnitud (UNIÓN 1.939 contra TRES CRUCES 689, razón 2,8×), así que comparar el mismo modelo en
> ambas daba una primera medida de cuánto se degradaba al cambiar de zona. Con municipios la razón
> es **1,15×** y las dos series son casi indistinguibles (`figuras/series_zonas.png`).
>
> **El contraste ya casi no informa.** Se conservan por continuidad del pipeline y porque no
> cuestan nada, pero **la evaluación seria es la del panel completo con métricas desagregadas por
> municipio**. No presentar esta comparación en el informe como evidencia de generalización.

---

## 8. Verificaciones — `tablas/10_verificaciones.csv`

**Dieciséis comprobaciones que detienen la ejecución si fallan.** En la corrida del 2026-09-07,
**las dieciséis en OK**.

| # | Verificación | Detalle |
| --- | --- | --- |
| 1 | El panel conserva todos los siniestros del recorte | 36.612 vs 36.612 |
| 2 | El panel es el producto completo días × zonas | 13.160 filas |
| 3 | La clave (fecha, zona) no se repite | clave única |
| 4 | El índice es temporal y está ordenado | DatetimeIndex creciente |
| 5 | **La serie empieza en la fecha declarada** | 2021-07-01 == 2021-07-01 |
| 6 | **Todos los polígonos de la capa tienen siniestros** | 8 de 8 municipios |
| 7 | No quedan faltantes en el panel | 0 celdas vacías → no corresponde imputar |
| 8 | Ninguna columna del panel es constante | 11 columnas |
| 9 | No hay columnas de gravedad en el panel | sin fuga por gravedad |
| 10 | **El panel no lleva variables de nivel de zona** | sólo `zona_id` como identificador |
| 11 | El calendario cubre todo el período sin huecos | 1.645 días |
| 12 | El clima cubre todo el período sin huecos | 1.645 días |
| 13 | `tipo_dia` tiene los tres niveles esperados | entre_semana, feriado, fin_semana |
| 14 | El objetivo es entero y no negativo | `n_siniestros` |
| 15 | Los eventos están ordenados cronológicamente | sort_values por fecha |
| 16 | Los centroides de zona caen dentro de Uruguay | 8 zonas |

Las verificaciones **5, 6 y 10 son nuevas** de esta versión y las tres nacen de errores concretos
que se quieren impedir: que `FECHA_INICIO` se mueva sin releer el diagnóstico, que un polígono
quede sin datos, y que vuelva a colarse al panel una variable de zona calculada sobre todo el
período.

### Verificación cruzada independiente — diagnóstico `tablas/23_coherencia_etl.csv`

`diagnostico_datos.ipynb` **reconstruye el panel desde las fuentes crudas** con su propia
implementación de la asignación punto-polígono, y compara:

| Comprobación | Diagnóstico (recalculado) | ETL (`data/processed`) | Resultado |
| --- | --- | --- | --- |
| Filas del panel | 13.160 | 13.160 | ✅ coincide |
| Siniestros totales | 36.612 | 36.612 | ✅ coincide |
| Zonas | 8 | 8 | ✅ coincide |
| Días | 1.645 | 1.645 | ✅ coincide |
| Máximo del objetivo | 13 | 13 | ✅ coincide |

**Las cinco comprobaciones coinciden.** Dos implementaciones independientes del recorte, la
deduplicación, la asignación punto-polígono y el armado del panel llegan al mismo resultado. Es la
evidencia más fuerte de que el conjunto está bien construido, y es citable en el informe.

---

## 9. Cobertura de la rúbrica de preparación

La consigna pide *«limpieza, transformación, imputación, codificación, escalado, balanceo,
selección o construcción de variables, reducción de dimensionalidad u otras acciones cuando
correspondan»*. Ésta es la trazabilidad completa, incluido **lo que no corresponde y por qué** —
que también hay que declarar, no omitir:

| Acción | Estado | Dónde / por qué |
| --- | --- | --- |
| **Limpieza** | ✅ Hecha | Duplicados exactos, fecha verificada, coordenadas validadas (3) |
| **Transformación** | ✅ Hecha | UTM → WGS84, agregación a (día, municipio) (3.4, 7.1) |
| **Imputación** | ⬜ **No corresponde** | 0 faltantes en las columnas que sobreviven y 0 en el clima. Se documenta con el conteo, no se omite |
| **Codificación** | ✅ Hecha | `tipo_dia` (3 niveles) y `estado_clima` (5 niveles) (6) |
| **Escalado** | ⬜ **Fuera del ETL a propósito** | Debe ajustarse sólo con entrenamiento → notebook de modelado |
| **Balanceo** | ⬜ **No corresponde** | 8,60 % de ceros: no hay clases que balancear (7.2) |
| **Construcción de variables** | ✅ Parcial | Municipio, `tipo_dia`, clima. **La tasa histórica del municipio va en el modelado**, sólo con entrenamiento |
| **Selección de variables** | ✅ Hecha | Se descartan constantes, no usadas y las de gravedad por fuga (3.1) |
| **Reducción de dimensionalidad** | ⬜ **No corresponde** | El conjunto final tiene 12 columnas |

---

## 10. Limitaciones y lo que NO puede afirmarse

| Limitación | Sección | Cómo se trata |
| --- | --- | --- |
| **Sólo 8 zonas, muy parecidas entre sí (1,71×)** | 5 | Declarar el margen estrecho para ordenar zonas |
| **El panel no lleva variable de nivel de zona** | 5 | **Deliberado**: se construye en el modelado, con entrenamiento |
| **El clima no aporta fuera de muestra** | 6.2 | Reevaluarlo o quitarlo; no venderlo como explicativo |
| El clima no varía entre municipios | 6.2 | Declararlo: sólo aporta variación temporal |
| Clima observado, no pronosticado | 6.2 | El desempeño medido es una **cota optimista** del operativo |
| **Tendencia creciente no corregida** | 4 | +11,0 % entre mitades del período; la trata el modelado |
| Sin gravedad ni franja horaria en el conjunto | 3.1 | Declarar que exige volver a ejecutar el ETL |
| 11 siniestros fuera de todo polígono | 5 | Se descartan; se documenta el conteo |
| Duplicados: criterio sin identificador de siniestro | 3.2 | Decisión conservadora, declarada |
| El par top/contraste ya casi no contrasta | 7.5 | No usarlo como evidencia de generalización |
| Código geográfico duplicado entre notebooks | — | Candidato a migrar a `src/`; hoy es la base de la verificación cruzada |

### Frases que NO deben aparecer en el informe

- ❌ «El ETL prepara los datos para el modelo.» → Prepara **parte**: escalado, particiones y
  variables con memoria quedan fuera **a propósito**, y hay que explicar por qué.
- ❌ «Se imputaron los valores faltantes.» → **No se imputó nada**: no hay faltantes. Decir que no
  correspondió es la respuesta correcta.
- ❌ «Se balancearon las clases» / «se trató el exceso de ceros». → **No corresponde**: con 8,60 %
  de ceros no hay exceso que tratar. *(Esta frase sí aparecía justificada en la versión por
  barrios: no reciclarla.)*
- ❌ «Se aplicó interpolación de ceros.» → Se descartó, y con esta zonificación **ya no tiene
  objeto**.
- ❌ «El clima explica las diferencias entre municipios.» → Es una serie única para el
  departamento: **no puede** explicar ninguna diferencia entre zonas. Y fuera de muestra no mejora
  nada.
- ❌ «Se eliminaron los outliers.» → Se eliminaron **duplicados exactos**, que es otra cosa; el
  efecto sobre la cola alta se explica en 3.2.
- ❌ «El conjunto incluye la gravedad de los siniestros.» → Se retiró deliberadamente por fuga.
- ❌ «El estrato de actividad clasifica los municipios por riesgo.» → Es descriptivo, calculado
  sobre todo el período y sobre un rango de 1,71×: los cortes son arbitrarios y **no entra al
  panel**.
- ❌ «El modelo se validó comparando la zona más activa contra una de contraste.» → Con municipios
  las dos series son casi iguales (razón 1,15×); esa comparación ya no mide generalización.

---

## 11. Índice de artefactos

`experiments/etl_montevideo/` — **15 tablas, 1 mapa HTML, 1 figura PNG**.

| Artefacto | Qué respalda |
| --- | --- |
| `tablas/00_procedencia.csv` | sha256 y tamaño del CSV de siniestros (2) |
| `tablas/01_duplicados.csv` | Conteo de duplicados y grupo mayor (3.2) |
| `tablas/02_recorte.csv` | Cascada del recorte al alcance (4) |
| `tablas/03_inicio_serie.csv` | Verificación del corte en 2021-07-01 (4) |
| `tablas/03b_procedencia_capa_zonas.csv` | sha256, polígonos y nombres de la capa de municipios (2) |
| `tablas/03c_asignacion_zonas.csv` | Asignación punto-polígono y siniestros fuera de capa (5) |
| `tablas/04_zonas.csv` | Resumen de la zonificación y razón máx/mín (5) |
| `tablas/05_estratos.csv` | Terciles de actividad — evidencia de por qué se descartan (5) |
| `tablas/06_calendario.csv` | Distribución de `tipo_dia` (6.1) |
| `tablas/07_clima.csv` | Distribución de `estado_clima` (6.2) |
| `tablas/08_panel.csv` | Dimensiones y estadísticos del panel (7.1) |
| `tablas/09_zonas_seleccionadas.csv` | Municipio más activo y de contraste (7.5) |
| `tablas/10_verificaciones.csv` | Las 16 comprobaciones (8) |
| `tablas/11_exportacion.csv` | Archivos exportados (7.4) |
| `tablas/12_diccionario_datos.csv` | Diccionario completo (7.3) |
| `figuras/mapa_zonas.html` | Mapa interactivo de los 8 municipios por actividad |
| `figuras/series_zonas.png` | Series diarias del municipio top y el de contraste |

**Antes de citar cualquier cifra:** verificar que los `sha256` de `00_procedencia.csv` y
`03b_procedencia_capa_zonas.csv` sigan siendo los de las fuentes vigentes. Si alguna cambió, hay
que volver a ejecutar el notebook.

---

## 12. Qué queda pendiente

Lo que este ETL deja planteado para el notebook de modelado:

1. **Construir la tasa histórica del municipio**, ajustada sólo con el tramo de entrenamiento. Es
   el pendiente prioritario: el panel **no lleva ninguna variable de nivel de zona**, a propósito.
   El diagnóstico midió que es el bloque más útil fuera de muestra —−7,5 % contra −4,3 % del
   calendario— ([`resumen_diagnostico_datos.md`](resumen_diagnostico_datos.md), §5.3).
2. **Implementar la línea base multiplicativa** (tasa del municipio × factor de calendario), que
   el diagnóstico midió en −11,8 % fuera de muestra, y verificar que **la forma saturada no se
   usa**: cruzar municipio y calendario en celdas independientes empeora el resultado (+10,4 %).
3. **Definir las particiones cronológicas** con el conjunto de prueba reservado.
4. **Tratar la tendencia creciente** (+11,0 % entre mitades): recalibrar nivel, incluir tendencia
   o ponderar los datos recientes. Decisión abierta.
5. **Decidir el escalado** y declararlo.
6. **Evaluar el rezago de un día** como variable candidata: el diagnóstico detecta persistencia
   genuina en 5 de 8 municipios, de magnitud pequeña (§5.2).
7. **Reconsiderar el clima**: fuera de muestra no aporta nada.
8. **Rediseñar el hold-out de zonas**: con 8 municipios, dejar uno afuera por vez y promediar las
   ocho corridas es lo único defendible, y su poder estadístico es bajo.
9. **Migrar a `src/`** el código geográfico duplicado entre este notebook y el de diagnóstico.
   Hoy la duplicación es deliberada —es lo que hace independiente a la verificación cruzada—, así
   que al unificarlos hay que reemplazarla por otra forma de contraste.

**Dos pendientes que salieron de la lista porque ya no aplican:**

- **Decidir el filtro de 2021** — resuelto: `FECHA_INICIO = "2021-07-01"`, justificado en el
  diagnóstico (§4).
- **Balanceo e interpolación de ceros** — no corresponden con esta zonificación (§7.2).
