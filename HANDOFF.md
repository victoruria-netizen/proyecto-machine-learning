# Handoff — Predicción de Siniestros Viales (PAA)

Documento de traspaso de contexto. Registra el estado del proyecto y lo pendiente para
retomar el trabajo sin perder información. Actualizar al cerrar cada sesión de trabajo.

_Última actualización: 2026-09-10_

---

## 1. Contexto del proyecto

- **Asignatura:** Proyecto de Aprendizaje Automático (PAA) — UTEC / LIDIA, 2026.
- **Tema:** Predicción de siniestros viales.
- **Continuidad:** El PAA continúa el Proyecto de Ingeniería de Datos (PID) del mismo
  equipo. Se reutilizan datos y activos del PID (declarar y distinguir en el informe).
- **Docente:** Pablo D. Cuña.
- **Guía de referencia:** `Guia_estudiantes_PAA_2026.md` (en la raíz del repo).
- **Plantilla de propuesta:** `Plantilla_presentacion_aprobacion_PAA.md`.

## 2. Repositorio

- **Remoto:** https://github.com/victoruria-netizen/proyecto-machine-learning.git
- **Rama principal:** `main` (ya con `upstream` configurado).
- **Identidad git (local):** Victor Uria / victor.uria@estudiantes.utec.edu.uy

## 3. Estado actual (hecho)

- [x] Estructura de carpetas recomendada (sección 4.1 de la guía) creada:
      `data/ notebooks/ src/ models/ experiments/ app/ documentacion/ tests/`
      (cada carpeta con `.gitkeep`).
- [x] `README.md` con propósito, estructura, requisitos y secciones a completar.
- [x] `documentacion/registro_uso_IA.md` creado con la primera entrada.
- [x] `requirements.txt` con dependencias base de ML.
- [x] `.gitignore` (ignora entornos, datos pesados/restringidos, modelos y secretos).
- [x] Commit inicial y push a `origin/main`.
- [x] Identidad de git configurada (nombre + email coinciden).
- [x] `notebooks/analisis_inicial.ipynb`: grilla espacial, panel diario día × zona relleno con
      ceros, features causales (rezagos, medias móviles, días desde el último siniestro) y
      split temporal 2019–2023 / 2024 / 2025 con submuestreo ponderado de ceros.
- [x] `notebooks/diagnostico_datos.ipynb`: diagnóstico de calidad, adecuación, cobertura y
      limitaciones exigido por el Entregable 2. **Reescrito el 2026-09-04** con alcance
      Montevideo / barrios (la versión del 2026-08-30 diagnosticaba el país con celdas de 1 km).
      Deja 36 tablas CSV y 3 figuras en `experiments/diagnostico_datos/` para citar desde el
      informe, y `documentacion/resumen_diagnostico_datos.md` como resumen autocontenido.
- [x] **División cronológica 70 / 10 / 20** fijada en el diagnóstico (sección 3.2):
      entrenamiento 2019-01-01 → 2023-11-25 (1.790 días), validación 2023-11-26 → 2024-08-07
      (256 días), test reservado 2024-08-08 → 2025-12-31 (511 días). El 20 % final se reserva
      y el 80 % restante se reparte en 70 % / 10 %.
      **Superada** por el cambio de alcance: las fechas valen para el planteo nacional.
- [x] `experiments/auditoria_preparacion_montevideo/` (2026-09-01): auditoría reproducible del
      notebook de preparación contra la copia local del CSV crudo (`auditoria.py` + `salida.txt`).
- [x] **`notebooks/preparacion_montevideo.ipynb` reescrito como notebook de ETL** (2026-09-01):
      adapta el pipeline del PID (`etl/`) al contexto de aprendizaje automático y exporta el
      conjunto de modelado a `data/processed/` en CSV. Ejecutado de punta a punta con
      `jupyter nbconvert --execute`, sin errores y con las diez verificaciones en verde.
- [x] `etl/` incorporado al repositorio (2026-09-01): el pipeline del PID, como fuente de la
      adaptación. **No se ejecuta** en el PAA — depende de PostgreSQL, MongoDB y Docker.
- [x] **Zonificación por barrios de Montevideo** (2026-09-04): capa oficial de la Intendencia (62
      polígonos) obtenida y en uso. El notebook corre completo con las 13 verificaciones en verde
      y exporta `data/processed/` con esta zonificación. Detalle en la sección siguiente.
- [x] **Convención de documentación de notebooks** (2026-09-04): cada notebook de `notebooks/`
      tiene un documento acompañante en `documentacion/`, autocontenido y trazable, pensado para
      que un asistente sin acceso al repositorio ayude a redactar el informe. La regla está en
      `CLAUDE.md`, sección **Documentación de notebooks**. Documentos vigentes:
      `resumen_diagnostico_datos.md` y `resumen_preparacion_montevideo.md`.
- [x] **Zonificación por municipios y corte de pandemia** (2026-09-07): capa oficial de los 8
      municipios obtenida vía WFS, y la serie recortada al **2021-07-01**. Aplicado a
      `diagnostico_datos.ipynb` (ejecutado sin errores, 43 tablas y 3 figuras) y a
      `resumen_diagnostico_datos.md`.
- [x] **ETL migrado al mismo alcance** (2026-09-07, segunda parte de la sesión):
      `preparacion_montevideo.ipynb` reescrito por municipios desde 2021-07-01, ejecutado con las
      **16 verificaciones en verde**, y `data/processed/` regenerado. La **verificación cruzada
      entre los dos notebooks pasa con las cinco comprobaciones en verde**: `data/processed/` ya
      es citable en el informe. `resumen_preparacion_montevideo.md` reescrito.

### Hallazgos del diagnóstico que condicionan lo que sigue

Vigentes tras la reescritura del **2026-09-07** (alcance Montevideo / **municipios**, desde
**2021-07-01**). Detalle y respaldo en `documentacion/resumen_diagnostico_datos.md`.

> ⚠️ **Los hallazgos de las versiones anteriores (país/grilla y Montevideo/barrios) están
> superados.** Dos de ellos se invirtieron al cambiar de zonificación: no alcanza con actualizar
> las cifras, cambia la conclusión.

1. **El objetivo dejó de tener exceso de ceros.** El panel es de 13.160 filas (1.645 días × 8
   municipios) con **8,60 % de ceros**, media 2,7821, dispersión **1,259**, máximo 13. Es una
   regresión de conteo ordinaria: **no corresponde balancear** ni aplicar variantes
   *zero-inflated*, y la interpolación de ceros que se había propuesto pierde su objeto.
2. **Sí hay señal temporal a rezago 1, y es genuina.** ACF mediana 0,0558 contra banda nula de
   Poisson 0,0464, con **5 de 8 municipios por encima** (0,2 esperables por azar). Sobrevive a
   descontar el calendario (mediana del residuo 0,0475, 5 de 8 sobre la banda). **A rezago 7 la
   señal es puro calendario**: descontado día de la semana y feriado, ningún municipio queda sobre
   la banda. *Antes, con barrios, no se detectaba señal a ningún rezago: el ruido de Poisson la
   tapaba.* La magnitud sigue siendo pequeña (< 1 % de la varianza), así que el rezago de un día
   es **candidato a evaluar**, no supuesto.
3. **La línea base multiplicativa está medida, no postulada.** Evaluada fuera de muestra (mitad
   temporal): constante 1,36394; sólo calendario −4,3 %; sólo tasa del municipio −7,5 %;
   **tasa × calendario −11,8 %**; con clima −11,5 %; **celdas saturadas +10,4 %** (peor que no
   usar nada). Confirma la forma multiplicativa y descarta el cruce saturado.
4. **El clima no aporta nada fuera de muestra.** Mantenerlo exige una justificación mejor que
   «estaba disponible». Ojo: el techo *en muestra* de las variables de día es −17,4 %, pero es un
   oráculo inalcanzable; el calendario construible rinde −4,3 %.
5. **Hay tendencia creciente en todo el período** y el corte de pandemia no la elimina: la media
   del objetivo sube **+11,0 %** entre la primera y la segunda mitad. El modelado tiene que
   tratarla explícitamente (recalibrar nivel, tendencia o ponderación).
6. **Sólo hay 8 zonas y se parecen mucho entre sí** (razón máx/mín **1,71×**, contra ~10× con
   barrios). Consecuencias: el margen para *ordenar* zonas es estrecho, y el hold-out de zonas del
   «megamodelo» pierde casi todo su poder — con 8 municipios lo único defendible es dejar uno
   afuera por vez y promediar.
7. **Sin datos de exposición (tránsito).** Se modela el conteo observado, no el riesgo por viaje.
8. **El subregistro no es medible con estos datos** y probablemente no es uniforme entre
   municipios. Es una amenaza a la validez que se declara, no se cuantifica.

### Cambio de alcance tras la reunión de seguimiento (2026-08-31)

El docente recomendó **acotar el proyecto a Montevideo**, trabajar por zonas de la ciudad, usar
datos a partir de 2021, tratar los ceros con una interpolación que no admita valores negativos y
probar un «megamodelo» evaluándolo en zonas que no vio al entrenar.

El diagnóstico de datos de alcance nacional queda como antecedente: sigue siendo válido como
caracterización de la fuente, pero sus decisiones de granularidad y particiones fueron
sustituidas por las del alcance montevideano.

### Reescritura del notebook de preparación en Colab (2026-09-01, primera sesión)

`notebooks/preparacion_montevideo.ipynb` **se rehizo desde cero en Google Colab**, en una versión
deliberadamente más simple. La versión anterior (34 celdas, diez secciones) nunca llegó a
commitearse, así que **no es recuperable desde git**: lo único que queda de ella son sus salidas
(ver «artefactos huérfanos» más abajo).

Estado de las recomendaciones del docente en la versión vigente (16 celdas):

| Recomendación | Estado |
| --- | --- |
| Sólo Montevideo | Hecho: 39.676 siniestros (2021–2025) |
| Datos desde 2021 | Hecho, pero **no elimina el régimen de pandemia** — hallazgo A2 |
| Trabajar por zonas | Grilla de 1 km (403 zonas). Sigue faltando la capa de barrios / municipios |
| Panel día × zona relleno con ceros | Se construye en memoria (735.878 filas) y **no se exporta** |
| Tratar los ceros con interpolación no negativa | **Ya no está**: sólo se cuenta el % de ceros de la zona más activa |
| «Megamodelo» evaluado en zonas distintas | **Ya no está**: no hay reserva de zonas ni variables transferibles |

También desaparecieron las variables predictoras (rezagos, medias móviles, calendario), las
particiones cronológicas, las verificaciones que detenían la ejecución y toda la escritura a
disco. Se agregó, en cambio, un mapa de calor `folium` de las 403 celdas y la serie diaria de la
zona más activa.

**El notebook vigente no deja ningún artefacto.** Todo queda en variables de memoria de Colab; lo
único que se escribe es `zonas_rojas_montevideo.html` en el directorio de trabajo de Colab, que
no llega al repositorio.

> ⚠️ **Artefactos huérfanos.** `data/processed/montevideo/panel_mvd.parquet` (735.878 × 21),
> `data/processed/montevideo/zonas_mvd.parquet` (403 × 11) y las 14 tablas y 3 figuras de
> `experiments/preparacion_montevideo/` los generó la versión anterior del notebook, que ya no
> existe. **Ningún código del repositorio los reproduce hoy.** Antes del Entregable 2 hay que
> decidir si se reconstruye el código que los genera o si se borran: citarlos en el informe
> mientras tanto rompe la trazabilidad código → resultado que exige la guía (secciones 4.4 y 6.3).
>
> Lo mismo, de antes, con los artefactos del planteo nacional en `data/processed/`
> (`zonas.parquet`, `panel_diario_zona.parquet`, `features/`): ya no se usan.

### Auditoría de la versión de Colab (2026-09-01)

> **Estado:** los hallazgos A1 a A15 quedaron **corregidos** en el notebook de ETL de la sección
> siguiente. Se conserva esta sección porque documenta por qué el ETL está escrito como está, y
> porque A16 (dispersión de la grilla) y A14 (fuga del catálogo de zonas) siguen abiertos.

Script reproducible en `experiments/auditoria_preparacion_montevideo/auditoria.py`, salida en
`salida.txt` del mismo directorio. Todas las cifras de esta sección salen de ahí.

**Lo que se verificó y está bien**

- El formato de fecha `%m/%d/%Y` es el correcto: coincide con la columna `Dia Semana` en el
  **100,0000 %** de los 224.694 registros (con `%d/%m/%Y` sólo el 6,80 %), y no genera ningún
  `NaT`. El `errors="coerce"` no está tapando nada.
- El recorte reproduce exactamente **39.676 siniestros** y **403 zonas**; el panel conserva la
  masa (39.676 siniestros en 735.878 filas).
- No hay coordenadas nulas ni en cero, `fixed == 1` en todos los registros y todas las celdas
  caen dentro del departamento (X 554.380–588.320, Y 6.134.505–6.157.850).
- `Localidad` dentro del recorte: 37.911 `MONTEVIDEO` y 1.765 `SIN DATOS`; ninguna localidad
  ajena al departamento.
- La proyección `EPSG:32721` ubica bien las celdas (554.500 / 6.144.500 → −56,404 / −34,840). La
  diferencia con `EPSG:5382` es submétrica frente a celdas de 1 km: el comentario dubitativo de
  la celda 12 se puede cerrar.

**Hallazgos que afectan a los datos o a las conclusiones**

- **A1 — Duplicados exactos sin tratar (96 filas, 0,24 % del recorte).** El máximo del objetivo
  (11 siniestros el 2021-07-30 en la zona `567000_6152000`) son **10 copias del mismo registro
  más uno distinto**: hay 2 siniestros reales, no 11. La cola alta del objetivo es un artefacto
  de la fuente. Afecta también al `panel_mvd.parquet` heredado, cuyo máximo declarado es 11.
- **A2 — El filtro `year > 2020` no saca la pandemia.** Enero–junio de 2021 promedia
  **16,37 siniestros/día** frente a **21,45** en los mismos meses de 2022–2025: **−23,7 %**. En
  Uruguay la ola de COVID y las restricciones de movilidad fueron justamente en el primer
  semestre de 2021. La justificación escrita en el notebook («para que el modelo no vea los datos
  de la pandemia») no se sostiene con los datos: hay que cortar en 2021-07-01 o declarar el sesgo.
- **A5 — El 58,60 % de ceros que informa el notebook es engañoso.** Es el de la zona más activa
  (`574000_6137000`, 994 siniestros). El del panel completo es **95,08 %**, con índice de
  dispersión **1,145** (media 0,0539, varianza 0,0617). La cifra que debe orientar el diseño del
  objetivo y de las métricas es la segunda, no la primera.
- **A14 — Fuga en el catálogo de zonas.** `zonas_unicas = df_filtrado["zona_id"].unique()` se
  calcula sobre todo el período, test incluido. Hay que definirlo sólo con entrenamiento o
  declarar la fuga explícitamente (pendiente que ya venía del diagnóstico).
- **A16 — La grilla es demasiado dispersa para el experimento del «megamodelo».** 28 zonas tienen
  un único siniestro en cinco años, 79 tienen cinco o menos, y 167 de las 403 concentran el 90 %.
  Un hold-out de zonas tomado al azar queda dominado por zonas casi vacías y no responde la
  pregunta del docente: hay que estratificar por actividad o exigir un soporte mínimo.

**Hallazgos de código y reproducibilidad**

- **A3 —** El comentario de la celda 6 dice «año estrictamente mayor a 2021 (a partir de 2022)»
  pero el código filtra `> 2020`, es decir a partir de 2021. El código es el correcto.
- **A4 —** La cabecera markdown describe la versión anterior: promete secciones 1 a 6,
  interpolación PCHIP, reserva de zonas y exportación a `data/processed/montevideo/`, nada de lo
  cual ocurre. Sólo existen las secciones 0 y 1.
- **A6 —** Ruta de Colab fija (`/content/drive/MyDrive/...`) y `drive.mount`: el notebook no corre
  fuera de esa cuenta. El repositorio tiene el mismo archivo en
  `data/raw/uru_siniestros_unificado.csv`, con sha256 `48a8a7e8…`, idéntico al que registró
  `experiments/preparacion_montevideo/tablas/00_procedencia.csv`. Conviene una celda de
  configuración que use Drive si está montado y `data/raw/` si no.
- **A7 —** `pip install folium pyproj` dentro del notebook y sin fijar versión. `folium` no está
  en `requirements.txt`; `scipy` sí está, pero se había agregado para la PCHIP que ya no se usa.
- **A9 —** Tres `SettingWithCopyWarning` en la celda 8: `df_filtrado` es una vista y le faltan
  los `.copy()`. En pandas 3 esto puede dejar de avisar y pasar a fallar.
- **A10 — Código muerto.** `df_resampled` (celda 8, «Opción A») se calcula y no se usa nunca.
  `df_completo` (celda 9, el panel) se calcula, se muestra con `.head()` y tampoco se vuelve a
  usar: las celdas 13 y 14 trabajan de nuevo sobre `df_filtrado`.
- **A11 —** Imports sin uso en la celda 2 (`hashlib`, `importlib.metadata`, `datetime`, `Path`,
  `PchipInterpolator`, `display`, `pyproj`, restos de la versión anterior) y reimportaciones de
  `pandas` y `matplotlib` en las celdas 8, 12 y 13.
- **A12 —** El mapa nunca se muestra (falta `mapa` como última expresión de la celda 12) y
  `mapa.save()` escribe fuera del repositorio. Además la escala de color es lineal sobre el
  máximo (994) cuando la mediana por zona es 37: casi todas las celdas quedan en blanco. Conviene
  escala logarítmica o por cuantiles.
- **A13 —** La celda 15 está vacía.
- **A15 —** El rango del panel se toma de `min()`/`max()` observados en lugar de un calendario
  fijo. Hoy coincide con 2021-01-01 → 2025-12-31, pero es una casualidad del dato.
- **A8 —** No se fija semilla ni se registran versiones de bibliotecas. Hoy no hay nada
  aleatorio, pero la reserva de zonas volverá a necesitarlo.

### Notebook de ETL (2026-09-01, segunda sesión)

`notebooks/preparacion_montevideo.ipynb` pasó a ser el **notebook de ETL del proyecto**: adapta
`etl/` (el pipeline del PID) al contexto del PAA y deja el conjunto de modelado en
`data/processed/`. Corrige los hallazgos A1 a A15 de la auditoría de la mañana.

**Qué se cambió respecto del ETL del PID**

| PID (`etl/`) | Notebook del PAA | Por qué |
| --- | --- | --- |
| Tres países (UY, BR, ES) | Sólo Uruguay → Montevideo | Alcance acordado con el docente |
| Carga a PostgreSQL y MongoDB | Carga a CSV en `data/processed/` | El PAA se entrega como repositorio ejecutable, sin infraestructura |
| Unidad = siniestro | Unidad = **(día, zona)** | El objetivo es el conteo por zona y día |
| `encoding='latin-1'` | `encoding='utf-8'` | **El CSV es UTF-8**; latin-1 rompe los acentos |
| `parsear_fecha_mixta` (prueba formatos hasta que uno ande) | Formato fijo `%m/%d/%Y` verificado contra `Dia Semana` | El «formato mixto» era una suposición del PID; el archivo es homogéneo |
| Sin tratamiento de duplicados | Duplicados exactos eliminados | Distorsionaban la cola alta del objetivo |
| Reproyección UTM→WGS84, vocabulario de gravedad | Reutilizados | Continuidad con el PID |

**Resultados de la corrida** (tablas en `experiments/etl_montevideo/tablas/`)

| Indicador | Valor |
| --- | --- |
| Duplicados exactos eliminados | 347 en el país (321 grupos, el mayor con 10 repeticiones) |
| Recorte Montevideo desde 2021-01-01 | **39.580** siniestros (eran 39.676 con duplicados) |
| Zonas (grilla de 1 km) | 403 · mediana 37 siniestros · 28 con un único siniestro |
| Panel | 1.826 días × 403 zonas = **735.878** filas |
| Objetivo | 95,08 % de ceros · media 0,0538 · dispersión **1,136** · **máximo 5** |
| Verificaciones | 10 de 10 en OK |

El **máximo del objetivo bajó de 11 a 5** al eliminar los duplicados: los valores 9 y 11 eran
íntegramente artefactos de carga. Es el cambio de fondo de esta sesión.

**Qué exporta a `data/processed/`** (regenerable; no se versiona)

| Archivo | Filas | Tamaño |
| --- | --- | --- |
| `siniestros_montevideo.csv` | 39.580 | 6,5 MB |
| `panel_diario_montevideo.csv` — conjunto de modelado | 735.878 | 50,3 MB |
| `zonas_montevideo.csv` | 403 | 34 kB |
| `panel_zona_top.csv` | 1.826 | 0,1 MB |
| `panel_zona_contraste.csv` | 1.826 | 0,1 MB |
| `diccionario_datos.csv` | 79 | 6 kB |

El panel no lleva `latitud`/`longitud`: son constantes por zona, están en `zonas_montevideo.csv`
y repetirlas sumaba ~18 MB sin agregar información. Si 50 MB molestan, escribir
`panel_diario_montevideo.csv.gz` baja a ~4 MB y `pandas.read_csv` lo lee sin cambios.

**Estrategia de zonas para el primer modelo**

Se exportan dos series diarias, no una:

| Papel | Zona | Siniestros | Días en cero |
| --- | --- | --- | --- |
| Primer modelo (zona más activa) | `574000_6137000` (−34,9022 / −56,1846) | 994 | 58,6 % |
| Contraste (mediana de las zonas activas) | `575000_6143000` (−34,8480 / −56,1742) | 160 | 91,5 % |

La zona más activa sirve para poner a andar el pipeline —es la que más señal tiene—, pero **no es
representativa**: sus métricas no son las del proyecto. La zona de contraste da, sin costo, la
primera medida de cuánto se degrada un modelo al cambiar de zona. Nótese que **las dos caen en el
estrato «alta»** y aun así una tiene 58,6 % de días en cero y la otra 91,5 %: el tercil superior
va de 91 a 994 siniestros y es internamente muy heterogéneo.

**Sobre la idea de hacer tres modelos (uno por estrato)**

Los terciles quedan así:

| Estrato | Zonas | Siniestros | % del total |
| --- | --- | --- | --- |
| baja | 137 | 722 | 1,8 % |
| media | 135 | 5.931 | 15,0 % |
| alta | 131 | 32.927 | 83,2 % |

Tres modelos por estrato **no resuelven por sí solos el problema de dispersión**: el estrato
«baja» tendría 722 siniestros repartidos en 137 zonas × 1.826 días, es decir un panel con 99,7 %
de ceros sobre el que no se puede ajustar nada más complejo que una tasa constante. Lo que sí
resuelve el estrato es la **evaluación**: reportar las métricas desagregadas en vez de agregadas.

Orden recomendado, que es además el que responde la pregunta del docente:

1. **Un modelo agrupado** («megamodelo») sobre todas las zonas, sin `zona_id` como predictor y
   con variables transferibles, evaluado en zonas reservadas y **con las métricas desagregadas
   por estrato**.
2. **Recién si falla en algún estrato**, entrenar uno por estrato y comparar contra el agrupado
   bajo el mismo protocolo. Sin el modelo agrupado como referencia no se puede afirmar que
   estratificar aportó algo.

La columna `estrato_actividad` del panel deja las dos rutas disponibles sin volver a correr el
ETL. Es **descriptiva**: está calculada sobre todo el período, así que hay que recalcularla sólo
con entrenamiento antes de usarla para elegir las zonas reservadas.

**Lo que queda deliberadamente fuera del ETL:** particiones de entrenamiento / validación /
prueba, y toda variable que aprenda de los datos (rezagos, medias móviles, tasa histórica de la
zona, interpolación de ceros). Se calculan dentro de cada partición, en el notebook de modelado.

**Decisión pendiente del equipo — el filtro de 2021.** El notebook ahora mide el efecto y lo deja
en `experiments/etl_montevideo/tablas/03_pandemia_residual.csv`: enero–junio de 2021 promedia
**16,34 siniestros/día** frente a **21,40** en los mismos meses de 2022–2025, **−23,7 %**. El
recorte sigue empezando el 2021-01-01 como pidió el equipo; cambiar `FECHA_INICIO` a
`"2021-07-01"` es una línea en la celda de configuración. Si se deja como está, **hay que
declarar el sesgo en el informe**.

### Auditoría del ETL contra la rúbrica y rediseño del conjunto (2026-09-02)

Se auditó el ETL contra la consigna del docente («limpieza, transformación, imputación,
codificación, escalado, balanceo, selección o construcción de variables, reducción de
dimensionalidad u otras acciones cuando correspondan») y se rediseñó el conjunto de modelado.

**Hallazgo central: el conjunto de variables exógenas previsto no puede funcionar solo.** Clima,
día de semana y feriados son todas variables **de día**: ninguna distingue una zona de otra, de
modo que un modelo con sólo esas variables predice lo mismo para las 62 zonas cada día. Medido
sobre el panel con desvianza de Poisson media, usando oráculos en muestra —a cada conjunto se le
da la media exacta, así que cada fila es su **techo**—:

| Conjunto de variables | Desvianza | vs constante |
| --- | --- | --- |
| Constante global | 0,32773 | — |
| **Sólo variables de día** (clima + dow + feriados) | 0,32261 | **−1,6 %** |
| Sólo estrato de actividad (3 niveles) | 0,26234 | −20,0 % |
| **Sólo tasa histórica de la zona** (403 celdas) | 0,24436 | **−25,4 %** |
| Tasa de zona × factor de día | 0,23924 | −27,0 % |

Descomposición de varianza coherente: **entre zonas 10,0 %** de la varianza total del objetivo,
**entre días 0,44 %**. Conclusión operativa: el conjunto exógeno se disputa un 1,6 % mientras el
25 % que aporta la identidad de la zona queda sin usar. **Hace falta al menos una variable de
nivel de zona** — la tasa histórica calculada sólo con entrenamiento, o rezagos por zona. Hoy la
única que hay en el panel es `estrato_actividad`.

**Otras fugas y trampas detectadas en el panel anterior**, todas corregidas:

- `n_fatal + n_grave + n_leve + n_solo_danos` **suman exactamente el objetivo**: fuga perfecta si
  alguien las usa como predictoras.
- `anio` con corte cronológico: el año del test nunca aparece en entrenamiento y un árbol
  extrapola a una constante.
- `mes`, `dia_anio`, `semana_iso` son **cíclicas** y como enteros mienten (diciembre = 12 y
  enero = 1 quedan máximamente distantes).
- `region`, `pais`, `geocodificado`: **varianza cero**, un único valor cada una.

### Notebook de ETL v2 (2026-09-02)

Cambios aplicados a `notebooks/preparacion_montevideo.ipynb`:

| Decisión | Estado |
| --- | --- |
| Zonificación por **barrios de Montevideo** en vez de la grilla | Implementada y probada, **pero falta la capa** — ver el bloqueo |
| Codificación del calendario en una sola categórica `tipo_dia` (`entre_semana` / `fin_semana` / `feriado`) | Hecho |
| Quitar `anio`, `mes`, `dia_mes`, `dia_semana`, `dia_anio`, `semana_iso`, `es_finde` | Hecho: son recuperables desde `fecha` |
| Quitar todo lo referido a gravedad | Hecho, en el panel y en la capa de eventos |
| Quitar las columnas constantes y las que no se usan (`hora`, `calle`, `tipo_accidente`, `region`, `municipio`, `geocodificado`, `pais`) | Hecho |
| `fecha` como índice | Hecho: `DatetimeIndex` ordenado, **no único** a propósito (una fila por zona), para poder cortar por tiempo |
| Clima de Open-Meteo | Hecho: serie diaria única para Montevideo, cacheada en `data/raw/clima_montevideo.csv` |
| Escalado y balanceo | **Fuera del ETL**, como se pidió: se ajustan sólo con entrenamiento |

**Feriados: `categories=("public", "bank")`.** Con la configuración por omisión de `holidays` sólo
aparecen 25 feriados en cinco años y quedan afuera **Carnaval y Semana de Turismo**. Con las dos
categorías son 18 por año, 90 en el período (4,9 % de los días). Esto cierra el pendiente que
venía del diagnóstico nacional.

**Clima.** Una sola serie diaria para todo el departamento (−34,87 / −56,17): a resolución diaria
las variables meteorológicas son prácticamente uniformes sobre 200 km² urbanos, y pedir una serie
por barrio multiplicaría por 62 las llamadas para devolver casi los mismos números. Queda
declarado como supuesto. Variables: `temp_media`, `temp_max`, `temp_min`, `precipitacion_mm`,
`lluvia_mm`, `viento_max_kmh`, más dos construidas: `estado_clima` (código WMO agrupado en cinco
niveles, reusando la tabla del PID) y `llovio`. 1.826 días, **sin faltantes** — no corresponde
imputar.

**Panel resultante con la grilla de respaldo** (mientras no esté la capa de barrios): 735.878
filas × 13 columnas, 39.580 siniestros, 95,08 % de ceros, dispersión 1,136, máximo 5.
Las 13 verificaciones pasan.

### ✅ Resuelto: capa de barrios obtenida y en uso (2026-09-04)

El equipo consiguió la capa y la dejó en `data/raw/barrios.json`. **Ese archivo no era la capa**:
era la respuesta `GetCapabilities` (XML) del servicio WMS que la sirve, no los polígonos. La capa
real se obtuvo pidiéndole al mismo servicio los datos por **WFS** en GeoJSON:

- **Servicio:** GeoServer institucional de la Intendencia de Montevideo
  (`montevideo.gub.uy/app/geoserver`).
- **Capa:** `mapstore-tematicas:zon_v_sig_barrios` («Barrios», 62 polígonos — coincide con la
  división oficial, sin huecos ni duplicados en los nombres).
- **Consulta:** `GetFeature`, `outputFormat=application/json`, `srsName=EPSG:4326`.
- **Descargada:** 2026-09-04. **Licencia:** el propio `GetCapabilities` declara
  `Fees: none` / `AccessConstraints: none`.
- **Guardada en:** `data/raw/barrios_montevideo.geojson` (el `barrios.json` con el XML y un
  `municipios.json` con el mismo problema se retiraron/quedan sin usar).

**Detalle no obvio:** el servicio devuelve **403** ante un `User-Agent` de librería (WAF) y
**200** con uno de navegador. Si hay que repetir la descarga:

```
GET https://montevideo.gub.uy/app/geoserver/mapstore-tematicas/zon_v_sig_barrios/ows
    ?service=WFS&version=2.0.0&request=GetFeature
    &typeName=mapstore-tematicas:zon_v_sig_barrios
    &outputFormat=application/json&srsName=EPSG:4326
Header: User-Agent: Mozilla/5.0 (cualquier UA de navegador)
```

El notebook ahora registra la procedencia de la capa automáticamente en
`experiments/etl_montevideo/tablas/03b_procedencia_capa_zonas.csv` (archivo, sha256, cantidad de
polígonos, fecha de modificación), igual que ya hacía con el CSV de siniestros.

**Hallazgo de la corrida real, corregido:** con barrios (mucho más volumen por zona que la grilla)
el umbral fijo `UMBRAL_ACTIVA = 60` dejaba **las 62 zonas** por encima del corte —
`zona_activa` quedaba constante y la verificación «ninguna columna del panel es constante» lo
atrapó, tal como estaba pensada para hacer—. Se sacó `zona_activa` del panel de modelado (queda
sólo en el catálogo `zonas_montevideo.csv`, donde sigue siendo información válida) y la selección
de la zona de contraste (sección 7) pasó a usar el estrato por terciles en vez del umbral
absoluto, que se adapta solo a la granularidad.

**Estado de la corrida** (2026-09-04, con la capa real): el notebook se ejecutó completo sin
errores y con las **13 verificaciones en verde**.

| Indicador | Grilla (respaldo) | **Barrios (vigente)** |
| --- | --- | --- |
| Zonas | 403 | **62** |
| Siniestros asignados | 39.580 | **39.569** (11 fuera de todo polígono, 0,03 %) |
| Filas del panel | 735.878 | **113.212** |
| % de filas en cero | 95,08 % | **71,96 %** |
| Media / varianza del objetivo | 0,0538 / 0,0611 | **0,3495 / 0,3957** |
| Dispersión (var/media) | 1,136 | **1,132** |
| Máximo del objetivo | 5 | **7** |
| Estratos (zonas / siniestros) | — | baja 21 (17,7 %) · media 20 (28,6 %) · alta 21 (53,6 %) |

Con 62 zonas ahora sí tiene sentido el hold-out del «megamodelo» que pidió el docente: la zona más
activa (**UNIÓN**, 1.939 siniestros, 36,6 % de días en cero) y la de contraste (**TRES CRUCES**,
689 siniestros, 68,6 % de días en cero) quedan exportadas en `panel_zona_top.csv` y
`panel_zona_contraste.csv`.

**Artefactos en `data/processed/`** (regenerables, no versionados):

| Archivo | Filas | Columnas | Tamaño |
| --- | --- | --- | --- |
| `panel_diario_montevideo.csv` | 113.212 | 13 | 9,4 MB |
| `siniestros_montevideo.csv` | 39.569 | 6 | 2,5 MB |
| `zonas_montevideo.csv` | 62 | 9 | — |
| `panel_zona_top.csv` | 1.826 | 13 | 0,1 MB |
| `panel_zona_contraste.csv` | 1.826 | 13 | 0,1 MB |

Más `data/raw/clima_montevideo.csv` (1.826 días, sin faltantes) y
`data/raw/barrios_montevideo.geojson` (62 polígonos): mientras existan, el notebook corre sin red.

**El hallazgo de la auditoría del 2026-09-02 se sostiene con barrios, algo atenuado.** Repetido el
mismo cálculo de desvianza de Poisson (oráculos en muestra) sobre el panel nuevo: constante
0,94110; sólo variables de día (techo) 0,90784 (**−3,5 %**); sólo tasa de zona 0,85280
(**−9,4 %**); zona × día 0,81954 (−12,9 %). Descomposición de varianza: entre zonas **8,9 %**,
entre días **2,86 %** (antes 10,0 % y 0,44 % con la grilla). Con menos zonas y más volumen por
zona el calendario explica algo más que antes, pero la brecha se mantiene: **sigue haciendo falta
la variable de nivel de zona**, y sigue siendo la construcción prioritaria para el notebook de
modelado.

**Sigue pendiente:** recalcular `estrato_actividad` sólo con entrenamiento antes de usarlo para
elegir las zonas reservadas del «megamodelo» (sigue siendo descriptivo, calculado sobre todo el
período).

### Reescritura del diagnóstico de datos (2026-09-04)

`notebooks/diagnostico_datos.ipynb` diagnosticaba el **país entero** con celdas de 1 km: 224.694
siniestros, 2018–2025, panel de 54.019.014 filas, y secciones sobre división cronológica,
estabilidad del universo de zonas y elección de granularidad. Todo eso quedó fuera de alcance.
Ejecutaba sin errores, que era lo peor del caso: producía en silencio un diagnóstico del alcance
equivocado.

**Qué se retiró** (cuatro secciones): coherencia con artefactos derivados (leía Parquets borrados
y degradaba en silencio mientras el markdown narraba un fallo detallado sobre ellos), división
cronológica 70/10/20, estabilidad del universo de zonas entre particiones, y elección de
granularidad 500 m vs 5 km. Las tres últimas son materia del notebook de modelado, no del
diagnóstico; la primera apuntaba a archivos inexistentes.

**Qué se agregó:** diagnóstico de la **capa de barrios** (asignación punto-polígono, siniestros
fuera de todo polígono), de la **serie climática** (cobertura, huecos, plausibilidad física), el
**aporte por bloque de variables** medido con desvianza de Poisson, y una **verificación cruzada
contra el ETL**: el diagnóstico reconstruye el panel desde las fuentes crudas de forma
independiente y compara — las cinco comprobaciones coinciden.

**Cifras que cambiaron con el alcance** (nacional → Montevideo):

| Indicador | Nacional | **Montevideo 2021+** |
| --- | --- | --- |
| Registros | 224.694 | **39.569** |
| `Localidad` con centinela | 17,91 % | **4,45 %** |
| `Calle` con centinela | 12,37 % | **2,33 %** |
| Filas del panel | 54.019.014 | **113.212** |
| % de ceros | 99,6 % | **71,96 %** |
| Dispersión (var/media) | 1,05 | **1,132** |

**El hallazgo central se sostiene, y se recalculó en vez de heredarlo.** A nivel de barrio no se
detecta señal temporal de corto plazo: ACF mediana 0,0137 (rezago 1) y 0,0101 (rezago 7) contra
bandas nulas de Poisson de 0,0449 y 0,0455 (400 simulaciones por barrio). **Matiz que la versión
anterior no tenía:** 7 y 8 barrios de 62 superan la banda, más que los ≈1,6 esperables por azar al
percentil 97,5 — hay algo de estructura en una minoría, pero de magnitud despreciable (la ACF
máxima, 0,084, explica menos del 1 % de la varianza de esa serie). La línea base defendible sigue
siendo **tasa histórica del barrio × factor de calendario**.

**Hallazgo nuevo con consecuencia directa sobre el diseño de variables:** las exógenas previstas
—clima, día de la semana, feriados— son todas variables **de día** y ninguna distingue un barrio
de otro. Medido con desvianza de Poisson (oráculos en muestra, cotas superiores): constante
0,94110; sólo variables de día 0,90784 (**−3,5 %**); sólo tasa histórica del barrio 0,85280
(**−9,4 %**); barrio × día 0,81954 (−12,9 %). Descomposición de varianza: entre barrios 8,8 %,
entre días 2,85 %. Un modelo con sólo clima y calendario predeciría lo mismo para los 62 barrios
cada día.

**Dos huecos que el diagnóstico anterior reportaba como abiertos están cerrados:** el clima está
integrado (1.826 días, sin faltantes) y los feriados usan `categories=("public","bank")` — 90 en
el período contra 25 de la configuración por omisión, que omitía **65 días**, entre ellos Carnaval
y Semana de Turismo.

**Artefactos.** Se borraron las 25 tablas y 5 figuras de la versión nacional: describían un
alcance superado y convivir con las nuevas habría hecho ambigua cualquier cita desde el informe.
Quedan 36 tablas y 3 figuras, todas de esta corrida.

**Documentación.** `documentacion/resumen_diagnostico_datos.md` se reescribió como **resumen
autocontenido** pensado para que un asistente sin acceso al repositorio pueda redactar la sección
*Metodología — datos*: lleva cada cifra con la tabla que la respalda, separa evidencia de
inferencia, y tiene una lista explícita de **frases que no deben aparecer en el informe** porque
los datos no las sostienen.

### Documentación de notebooks (2026-09-04)

Se fijó como convención que **cada notebook tenga un documento acompañante** en `documentacion/`,
con el mismo nombre y prefijo `resumen_`. La regla quedó en `CLAUDE.md` (sección **Documentación de
notebooks**), con la estructura mínima, las reglas de contenido y la obligación de actualizar el
documento en la misma sesión en que se toca el notebook.

**Para qué:** son contexto **autocontenido** para que un asistente sin acceso al repositorio
—típicamente Claude en la web— ayude a redactar el informe. De ahí las dos propiedades que los
definen: nada de «ver la sección 3 del notebook» (si un número importa, va escrito), y cada cifra
con el artefacto que la respalda.

La pieza que más protege al equipo es la sección **«frases que no deben aparecer en el informe»**:
lista explícita de afirmaciones que los datos no sostienen y que sería fácil escribir por inercia
(«el barrio X es el más peligroso» cuando es el que más *registra*; «se imputaron los faltantes»
cuando no se imputó nada porque no correspondía).

| Notebook | Documento | Cubre del informe |
| --- | --- | --- |
| `diagnostico_datos.ipynb` | `resumen_diagnostico_datos.md` | *Metodología — datos* |
| `preparacion_montevideo.ipynb` | `resumen_preparacion_montevideo.md` | *Metodología — preparación* |

`resumen_preparacion_montevideo.md` (545 líneas) documenta el ETL: qué se hereda del PID y qué
cambia, las decisiones de limpieza con su efecto observado, la zonificación y por qué barrios en
lugar de la grilla, las exógenas, el conjunto exportado con su diccionario, las 13 verificaciones,
y una **tabla de cobertura de la rúbrica de preparación** que declara también lo que *no*
corresponde y por qué (imputación, escalado, balanceo, reducción de dimensionalidad).

### Zonificación por municipios y corte de pandemia (2026-09-07)

Reunión de seguimiento con el docente. Tres pedidos: **zonas más grandes (municipios en lugar de
barrios)**, **sacar los meses de pandemia de 2021**, y actualizar los informes de
`documentacion/`. Esta sesión resolvió el primer notebook y su documento; **el ETL queda
pendiente**.

**Capa de municipios.** El `data/raw/municipios.json` que dejó el equipo **no era la capa**: era
la respuesta `GetCapabilities` (XML) del servicio WMS, el mismo problema que ya había pasado con
barrios. La capa real se obtuvo por WFS del GeoServer de la Intendencia:

```
GET https://montevideo.gub.uy/app/geoserver/mapstore-tematicas/zon_v_sig_municipios/ows
    ?service=WFS&version=2.0.0&request=GetFeature
    &typeName=mapstore-tematicas:zon_v_sig_municipios
    &outputFormat=application/json&srsName=EPSG:4326
Header: User-Agent: Mozilla/5.0 (cualquier UA de navegador)   # sin esto devuelve 403
```

Guardada en `data/raw/municipios_montevideo.geojson` (2,87 MB, sha256 `ed0ba13e…`). **8 polígonos:
A, B, C, CH, D, E, F y G**, campo del nombre `municipio` (trae la letra sola; el notebook le
antepone `MUNICIPIO `). Licencia: `Fees: none` / `AccessConstraints: none`.

**Corte de la pandemia: `FECHA_INICIO = "2021-07-01"`.** Cierra el pendiente A2, que venía abierto
desde el 2026-09-01 como «decisión del equipo». La decisión quedó **justificada con evidencia en
tres pasos** dentro del notebook (sección 3.1), no por decreto:

| Paso | Qué muestra | Tabla |
| --- | --- | --- |
| 1. Nivel | ene–jun 2021 promedia 16,34/día contra 21,40 en 2022–2025: **−23,7 %** | `12_pandemia_paso1_nivel` |
| 2. No es tendencia | Índice estacional (mes / media del propio año): feb–jun 2021 entre −7,0 % y **−17,2 %** | `12b_…indice_estacional` |
| 3. El corte alcanza | jul–dic 2021 encadena con 2022–2025 (+3,1 %, +2,8 %, +5,7 %, +2,8 %) | `12c`, `12d` |

Dos matices que quedaron escritos y que el informe debe recoger: **enero de 2021 no está
deprimido** (índice +1,1 %) y se excluye igual para no dejar un mes suelto — es conveniencia del
equipo, y se declara como tal; y **noviembre de 2021 se aparta hacia arriba** (+10,7 %) sin
explicación disponible. **Costo:** 2.957 registros (7,5 %) y 181 días; quedan 1.645 días.

**Estado del notebook de diagnóstico.** `notebooks/diagnostico_datos.ipynb` reescrito y **ejecutado
de punta a punta sin errores** (77 celdas). Deja **43 tablas y 3 figuras** en
`experiments/diagnostico_datos/`. Se borraron las 36 tablas y 3 figuras de la corrida por barrios:
convivir con las nuevas habría hecho ambigua cualquier cita desde el informe.

**Cifras que cambiaron** (barrios → municipios):

| Indicador | Barrios (superado) | **Municipios (vigente)** |
| --- | --- | --- |
| Zonas | 62 | **8** |
| Período | 2021-01-01 → 2025-12-31 (1.826 d) | **2021-07-01 → 2025-12-31 (1.645 d)** |
| Siniestros | 39.569 | **36.612** |
| Filas del panel | 113.212 | **13.160** |
| % de ceros | 71,96 % | **8,60 %** |
| Media / dispersión | 0,3495 / 1,132 | **2,7821 / 1,259** |
| Máximo del objetivo | 7 | **13** |
| Razón máx/mín entre zonas | ~10× | **1,71×** |

**Aporte metodológico de esta versión: la medición fuera de muestra.** Las versiones anteriores
medían el aporte de cada bloque de variables con oráculos en muestra, que son techos. Ahora el
notebook agrega una segunda pasada con partición temporal por la mitad, y **el orden se invierte**:
en muestra el oráculo de día parece dominar (−17,4 %), fuera de muestra la tasa del municipio
(−7,5 %) supera al calendario construible (−4,3 %) y la combinación multiplicativa gana (−11,8 %).
También aparece que las **celdas saturadas empeoran** el resultado (+10,4 %), lo que justifica la
forma multiplicativa de la línea base.

> **La verificación cruzada con el ETL no se pudo hacer en esta primera corrida**, porque
> `data/processed/` todavía estaba en el alcance anterior (62 zonas, desde 2021-01-01, 113.212
> filas). El notebook lo **detectó y se abstuvo de comparar** en vez de informar una discrepancia
> falsa. **Resuelto en la segunda parte de la sesión** (sección siguiente): el ETL se migró y la
> verificación pasa con las cinco comprobaciones en verde.

### Migración del ETL a municipios (2026-09-07, segunda parte)

`notebooks/preparacion_montevideo.ipynb` reescrito al mismo alcance que el diagnóstico:
**municipios (8), desde 2021-07-01**. Ejecutado de punta a punta sin errores, **16 de 16
verificaciones en OK**, y `data/processed/` regenerado.

**Resultado que cierra el bloqueante:** la verificación cruzada del diagnóstico
(`23_coherencia_etl.csv`) pasa con **las cinco comprobaciones en verde** — 13.160 filas, 36.612
siniestros, 8 zonas, 1.645 días, máximo 13. Dos implementaciones independientes del recorte, la
deduplicación, la asignación punto-polígono y el armado del panel llegan al mismo resultado.
**`data/processed/` ya es citable en el informe.**

**Cambios de fondo, más allá de la zonificación y la fecha**

| Decisión | Antes | Ahora | Por qué |
| --- | --- | --- | --- |
| Capa de zonas ausente | Caía a **grilla de 1 km** y lo avisaba por pantalla | **Falla ruidosamente** | Producía igual un conjunto completo de otro alcance (403 zonas, 95 % de ceros) que quedaba en `data/processed/` indistinguible del bueno |
| `estrato_actividad` | En el panel | **Sólo en el catálogo** | Con 8 zonas en un rango de 1,71× los terciles son arbitrarios, y está calculado sobre todo el período (fuga) |
| `zona_activa` / `UMBRAL_ACTIVA` | En el catálogo | **Eliminados** | Con municipios es cierto para los ocho: no informa nada |
| Balanceo | «Decisión del modelado, ver tasa de ceros» | **No corresponde** | 8,60 % de ceros: no hay clases que balancear |
| Interpolación de ceros | Pendiente a revisar | **Sin objeto** | Se pensó para un panel dominado por ceros estructurales |
| Sección 3.1 | «Advertencia» sobre el filtro de 2021 | **Verificación que detiene la ejecución** | La decisión ya está tomada; lo que hay que impedir es que la fecha se mueva sin releer el diagnóstico |

**Consecuencia declarada: el panel exportado no lleva ninguna variable de nivel de zona.** Es
deliberado — la tasa histórica del municipio, que el diagnóstico identificó como el bloque más
útil fuera de muestra, debe estimarse **sólo con entrenamiento** y es trabajo del modelado.
Ponerla en el ETL filtraría información del test. Hay una verificación nueva que lo custodia.

**Tres verificaciones nuevas** (5, 6 y 10 de las 16), cada una contra un error concreto: que
`FECHA_INICIO` se mueva sin releer el diagnóstico, que un polígono de la capa quede sin datos, y
que vuelva a colarse al panel una variable de zona calculada sobre todo el período.

**Salida en `data/processed/`** (regenerable, no versionada):

| Archivo | Filas | Columnas | Tamaño |
| --- | --- | --- | --- |
| `panel_diario_montevideo.csv` | 13.160 | 12 | 1,0 MB |
| `siniestros_montevideo.csv` | 36.612 | 6 | 2,2 MB |
| `zonas_montevideo.csv` | 8 | 8 | — |
| `panel_zona_top.csv` / `panel_zona_contraste.csv` | 1.645 c/u | 12 | 0,1 MB c/u |
| `diccionario_datos.csv` | 50 | 4 | — |

El panel bajó de 9,4 MB a **1,0 MB**: con 8 zonas ya no hay razón para comprimirlo.

**Dos errores propios detectados y corregidos durante la migración**

1. **Fecha ISO leída con `dayfirst`.** La celda del diagnóstico que lee el panel del ETL usaba
   `pd.to_datetime(..., format="mixed", dayfirst=True)`, que sobre `2021-07-01` devuelve **el 7 de
   enero**, en silencio. Por eso la verificación cruzada seguía diciendo «otro alcance» aun con el
   ETL ya migrado. Es exactamente el riesgo que el propio notebook verifica en la fuente cruda
   (sección 2.3). Corregido: el formato se decide mirando el texto, no por bandera.
2. **Cifras que parecían discrepancias y eran redondeo.** La varianza del objetivo difería en el
   cuarto decimal (`ddof=1` en el ETL contra `ddof=0` en el diagnóstico) y la variación interanual
   en el segundo (el ETL la calculaba sobre medias ya redondeadas). Ambas alineadas: el panel es
   la población completa, así que `ddof=0`, y la variación se calcula sin redondear antes.

**Par top/contraste: perdió sentido y queda declarado.** Con barrios eran UNIÓN (1.939) contra
TRES CRUCES (689), razón 2,8×. Con municipios son C (5.783) contra A (5.016), razón **1,15×**, y
las dos series son casi indistinguibles (`figuras/series_zonas.png`). Se conservan por continuidad
del pipeline, pero **no sirven como evidencia de generalización**: la evaluación seria es la del
panel completo con métricas desagregadas por municipio.

### Notebook base: protocolo de evaluación + línea base (2026-09-10)

`notebooks/base.ipynb` creado y **ejecutado de punta a punta sin errores** (44 celdas).
Trabaja **una sola serie** —`data/processed/panel_zona_top.csv`, MUNICIPIO C, 1.645 días—
para fijar el protocolo sobre un caso simple antes del panel. Deja **12 tablas y 7
figuras** en `experiments/base/` y el documento acompañante
`documentacion/resumen_base.md`.

**Qué fija (los tres puntos del Entregable 2):**

| Punto | Decisión |
| --- | --- |
| Protocolo de evaluación | Partición cronológica **80 / 20**; validación interna por **ventana deslizante** (origen móvil, ventana expansiva, horizonte 7 días, 47 cortes); métrica principal **desvianza de Poisson** + MAE, RMSE, razón total predicho/observado y sesgo medio |
| Conjunto de prueba reservado | Últimos **329 días (20 %)**, 2025-02-06 → 2025-12-31. Congelado entre §5 y §9; usado una sola vez |
| Línea base del proyecto | **Tasa × factor de calendario** (media del entrenamiento por `tipo_dia`) — la forma multiplicativa que el diagnóstico recomienda |
| Modelo base aprendido | **Árbol de decisión básico** (`DecisionTreeRegressor`, `max_depth=4`, `min_samples_leaf=20`) con rezagos t−7/14/21, calendario y tendencia. Contrastado con media constante, naive estacional (t−7) y media móvil 56 d × calendario |

**Sin fugas:** medias y árbol se ajustan con la ventana de entrenamiento de cada corte; en
el test el ajuste queda fijo en el desarrollo; el árbol usa sólo rezagos observados
(t−7/14/21), sin recursión; backtesting implementado a mano (~15 líneas, sin `skforecast`)
para que sea auditable.

**Resultados (artefactos en `experiments/base/tablas/`):**

- **Poda obligatoria** (`04c_arbol_profundidad`): árbol sin podar → profundidad 31, 943
  hojas, desvianza **12,65**; árbol `max_depth=4` (13 hojas) → **1,40**.
- **Desarrollo** (`04_desarrollo_backtesting`): el árbol base (1,401) **supera a la media
  constante** (1,518, −7,7 %) pero **queda por debajo de la línea base** `Tasa × calendario`
  (1,378). Calibración en muestra del árbol casi perfecta (razón 0,998). `Naive estacional
  (t−7)` **descartada** (desvianza 7,90).
- Importancias del árbol (`05_importancias_arbol`): `es_fin_semana` 53 %, `t_anios` 23 %,
  `es_feriado` 17 %; rezagos < 8 % (`y_lag14` = 0).
- **Test** (`06_evaluacion_test`, una sola vez): **el árbol es el peor de los tres** —
  desvianza **1,679**, contra 1,085 de la línea base y 1,263 de la media constante. Razón
  total 0,723 (infra-predice 28 %, sesgo −1,07/día). **Causa: el árbol no extrapola la
  tendencia** (el diagnóstico lo anticipó para `anio`). La línea base también infra-predice
  (0,884) pero mucho menos.
- **Conclusión:** la línea base del proyecto sigue siendo `Tasa × calendario`; un árbol
  básico no es un modelo final adecuado para una serie con tendencia. **El protocolo hizo
  su trabajo:** un modelo competitivo en desarrollo se cayó en el test reservado.

**Entorno:** no había `.venv` en la máquina. Se creó uno (`python -m venv .venv`,
gitignored) con `pandas 3.0.5 / numpy 2.5.2 / scikit-learn 1.9.0 / scipy 1.18.1 /
matplotlib 3.11.1 / statsmodels 0.14.6 / jupyter 1.1.1` sobre **Python 3.14.7** (el
sistema; `requirements.txt` dice 3.13). El notebook usa sólo pandas/numpy/matplotlib/
scikit-learn: **no se agregó ninguna dependencia a `requirements.txt`**.

**Lo que este notebook NO hace y queda para el del panel:** métricas desagregadas por
municipio, tasa histórica por municipio (sólo con entrenamiento), rezago de 1 día como
candidato, tratamiento explícito de la tendencia, destino del clima, hold-out de zonas, y
comparar el árbol base contra familias apropiadas para conteo (Poisson, boosting con
pérdida Poisson, RandomForest) con ajuste de hiperparámetros. El par top/contraste sigue
sin servir como evidencia de generalización.

## 4. Pendiente (próximos pasos)

Orientado al **Entregable 2 — Datos, metodología y línea base (fecha límite: 20 de septiembre
de 2026)**. En orden de prioridad.

**✅ Resuelto — el ETL ya está en el alcance nuevo** (2026-09-07)

- [x] ~~Reescribir `preparacion_montevideo.ipynb` con municipios y `FECHA_INICIO = "2021-07-01"`~~
      — hecho, 16/16 verificaciones en verde.
- [x] ~~Volver a correr la sección 5 del diagnóstico~~ — hecho: `23_coherencia_etl.csv` con las
      cinco comprobaciones en verde. **`data/processed/` ya es citable en el informe.**
- [x] ~~Actualizar `resumen_preparacion_montevideo.md`~~ — hecho.
- [x] ~~Revisar `estrato_actividad`~~ — resuelto: sale del panel, queda en el catálogo como
      descriptivo. Con 8 zonas en un rango de 1,71× los terciles son arbitrarios.
- [x] ~~Revisar `panel_zona_top` / `panel_zona_contraste`~~ — se conservan, pero **declarados como
      no informativos**: la razón entre ambos bajó de 2,8× a 1,15×.

**Bloqueantes del Entregable 2**

- [x] ~~Reconstruir la preparación~~ — hecho: `preparacion_montevideo.ipynb` es el notebook de
      ETL y exporta a `data/processed/`. **Pendiente de migrar al alcance nuevo (arriba).**
- [x] ~~Deduplicar el recorte~~ — hecho. Con el recorte vigente son 90 duplicados exactos.
- [x] ~~Sacar la ruta de Colab~~ — hecho: las rutas se resuelven solas en Colab y en local.
- [x] ~~Decidir el filtro de pandemia~~ (hallazgo A2) — **resuelto el 2026-09-07**:
      `FECHA_INICIO = "2021-07-01"`, con la justificación en tres pasos dentro del diagnóstico.
- [ ] **Borrar los artefactos huérfanos**: `experiments/preparacion_montevideo/`,
      `data/processed/montevideo/` y los Parquet nacionales de `data/processed/`. Ninguno lo
      genera código vigente. Ya no hay razón para esperar: el ETL vigente está validado.
- [x] ~~**Fijar las métricas** del protocolo de evaluación~~ — hecho en `notebooks/base.ipynb`
      (§4): **desvianza de Poisson** como principal, más MAE, RMSE, razón total predicho/observado
      y sesgo medio. *Ojo:* la redacción anterior hablaba de «objetivo Poisson con exceso de
      ceros» y **ya no aplica** — con municipios los ceros son el 8,60 %.
- [x] ~~Decidir el balanceo~~ — **no corresponde**: con 8,60 % de ceros no hay clases que
      balancear. Las notas anteriores sobre exceso de ceros y Tweedie están superadas.
- [~] **Implementar la línea base multiplicativa** (tasa del municipio × factor de calendario) y
      evaluarla con el protocolo definitivo. **Hecho sobre una sola serie** en
      `notebooks/base.ipynb` (§7): `Tasa × calendario` mejora la desvianza un −9,2 % vs la media
      constante en desarrollo y un −14,1 % en el test. **Falta llevarlo al panel de 8 municipios**
      con la tasa histórica por municipio ajustada sólo con entrenamiento. El diagnóstico ya midió
      que es la mejor forma disponible (−11,8 % fuera de muestra) y que **la forma saturada
      empeora** el resultado.

**Metodología abierta**

- [x] ~~Bajar la capa de zonas~~ — hecho: barrios (2026-09-04, 62 polígonos) y **municipios
      (2026-09-07, 8 polígonos, vigente)**, ambos vía WFS del GeoServer de la Intendencia.
- [x] ~~Verificar el campo del nombre~~ — en municipios el campo es `municipio` y trae la letra
      sola (A, B, C, CH, D, E, F, G); el notebook le antepone `MUNICIPIO `.
- [x] ~~Corregir `es_feriado`~~ — hecho: `categories=("public","bank")`. En el período vigente son
      77 feriados contra 23 de la configuración por omisión.
- [x] ~~Integrar el clima~~ — hecho, pero **hay que reconsiderarlo**: fuera de muestra no aporta
      nada (−11,5 % con clima contra −11,8 % sin él).
- [x] ~~Decidir el destino de `analisis_inicial.ipynb`~~ — borrado del repositorio.
- [ ] **Agregar la variable de nivel de zona** (tasa histórica del municipio, ajustada sólo con
      entrenamiento). Sigue siendo el bloque más útil fuera de muestra (−7,5 %) y hoy no está en
      el panel.
- [ ] **Tratar la tendencia creciente** (+11,0 % entre mitades): recalibrar nivel, incluir
      tendencia o ponderar los datos recientes. Decisión abierta. **`base.ipynb` lo confirmó como
      problema real:** en el test los tres finalistas infra-predicen (razón total 0,72–0,88);
      el árbol de decisión, que **no extrapola**, es el que peor rinde (razón 0,72, desvianza
      1,68 contra 1,08 de la línea base). La ventana móvil de 56 d corrige la calibración en
      desarrollo sin bajar la desvianza.
- [ ] **Evaluar el rezago de un día** como variable candidata, contra la línea base y bajo el
      mismo protocolo. Ya no se lo descarta de entrada: hay señal en 5 de 8 municipios.
- [ ] **Rediseñar el hold-out de zonas del «megamodelo».** Con 8 municipios, dejar uno afuera por
      vez y promediar las ocho corridas es lo único defendible; declarar que su poder estadístico
      es bajo y que no puede ser la evidencia principal de la generalización.
- [~] **Definir las particiones cronológicas** con el conjunto de prueba reservado. **Definidas
      en `base.ipynb` (§5):** 80 % desarrollo / 20 % prueba reservada; dentro de desarrollo,
      ventana deslizante con origen móvil (75 % entrenamiento inicial, 47 cortes de 7 días). La
      partición por la mitad del diagnóstico era sólo instrumental. **Falta aplicarlo al panel.**
- [ ] **Decidir el tratamiento del catálogo de zonas** (hallazgo A14). Con 8 municipios fijos y
      todos con siniestros, la fuga es mucho menor que con barrios, pero sigue existiendo.

**Entrega**

- [ ] Migrar de notebooks a `src/` lo que deba ser reproducible por línea de comandos.
- [ ] Borrador acumulativo del informe en `documentacion/informe/`, al menos hasta resultados
      preliminares (la sección *Metodología — datos* puede apoyarse ya en el diagnóstico).
- [ ] Evidencia de uso del **servidor institucional** y constancia de seguimiento del tutor.

## 5. Calendario de entregables

| Fecha         | Hito                                              |
|---------------|---------------------------------------------------|
| 17 de agosto  | **Entregable 1** — Propuesta inicial              |
| 24 de agosto  | Reformulación (si el Comité lo solicita)          |
| 20 de septiembre | **Entregable 2** — Datos, metodología y línea base |
| 25 de octubre | **Entregable 3** — Experimentación y solución     |
| 15 de noviembre | **Entregable 4** — Entrega definitiva al tribunal |

## 6. Notas y decisiones

- `etl/` es el pipeline del **PID**, incorporado como fuente de la adaptación. **No se ejecuta
  en el PAA:** depende de PostgreSQL, MongoDB, Docker y rutas `/app/...`. Lo que el PAA usa está
  reimplementado en `notebooks/preparacion_montevideo.ipynb`, con las diferencias documentadas
  en la sección del ETL.
- Se usa `requirements.txt` (alternativa posible: `environment.yml`).
- Los datos restringidos o pesados **no** se versionan; documentar en el README cómo
  obtenerlos (sección 4.1 de la guía).
- Registrar todo uso de IA generativa en `documentacion/registro_uso_IA.md`.
