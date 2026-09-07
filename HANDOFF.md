# Handoff — Predicción de Siniestros Viales (PAA)

Documento de traspaso de contexto. Registra el estado del proyecto y lo pendiente para
retomar el trabajo sin perder información. Actualizar al cerrar cada sesión de trabajo.

_Última actualización: 2026-09-04_

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

### Hallazgos del diagnóstico que condicionan lo que sigue

Vigentes tras la reescritura del 2026-09-04 (alcance Montevideo / barrios). Detalle y respaldo en
`documentacion/resumen_diagnostico_datos.md`.

1. **No se detecta señal temporal de corto plazo por barrio.** ACF mediana 0,0137 (rezago 1) y
   0,0101 (rezago 7) contra bandas nulas de Poisson de 0,0449 y 0,0455. Consecuencia: la línea
   base debe ser *tasa histórica del barrio × factor de calendario*, no una regla de persistencia.
   *Matiz:* 7 y 8 barrios de 62 superan la banda, más que los ≈1,6 esperables por azar — hay algo
   de estructura en una minoría, pero de magnitud despreciable (ACF máxima 0,084).
2. **El objetivo es de tipo Poisson** (71,96 % de ceros, dispersión 1,132, máximo 7). Las métricas
   deben medir calibración y ordenamiento, no exactitud puntual del conteo: desvianza de Poisson
   como principal. Con esta densidad **no hace falta balancear**.
3. **Las variables exógenas previstas no alcanzan solas.** Clima, día de la semana y feriados son
   todas variables *de día*: ninguna distingue un barrio de otro. Techo conjunto −3,5 % de
   desvianza, contra −9,4 % de la sola tasa histórica del barrio. **Falta construir la variable de
   nivel de zona**, ajustada sólo con entrenamiento.
4. **El filtro de 2021 no elimina el régimen de pandemia.** Ene–jun 2021 promedia 16,34
   siniestros/día contra 21,40 en los mismos meses de 2022–2025 (**−23,6 %**). Decisión del equipo:
   mantener 2021 completo y declarar el sesgo en el informe.
5. **Sin datos de exposición (tránsito).** Se modela el conteo observado, no el riesgo por viaje:
   el sistema puede ordenar y calibrar riesgo esperado por barrio, **no** anticipar siniestros
   individuales ni hablar de «peligrosidad».
6. **El subregistro no es medible con estos datos** y probablemente no es uniforme entre barrios.
   Es una amenaza a la validez que se declara, no se cuantifica.

*Resueltos desde la versión nacional del diagnóstico:* clima integrado (1.826 días sin faltantes),
feriados corregidos con `categories=("public","bank")` (90 en el período contra 25), y
`data/processed/` reproducible con el código versionado (verificado por contraste cruzado).

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

## 4. Pendiente (próximos pasos)

Orientado al **Entregable 2 — Datos, metodología y línea base (fecha límite: 20 de septiembre
de 2026)**. En orden de prioridad.

**Bloqueantes del Entregable 2**

- [x] ~~Reconstruir la preparación~~ — hecho: `preparacion_montevideo.ipynb` es ahora el
      notebook de ETL y exporta a `data/processed/`.
- [x] ~~Deduplicar el recorte~~ — hecho (347 filas en el país, 96 en el recorte). El máximo del
      objetivo bajó de 11 a 5.
- [x] ~~Sacar la ruta de Colab~~ — hecho: las rutas se resuelven solas en Colab y en local.
- [ ] **Decidir el filtro de pandemia** (hallazgo A2). El notebook ya mide el efecto (−23,7 % en
      ene–jun 2021); falta que el equipo decida: cortar en `FECHA_INICIO = "2021-07-01"` o dejar
      2021 completo y declarar el sesgo en el informe. **Es decisión del equipo, no técnica.**
- [ ] **Borrar los artefactos huérfanos** una vez validado el ETL nuevo:
      `experiments/preparacion_montevideo/`, `data/processed/montevideo/` y los Parquet
      nacionales de `data/processed/`. Ninguno lo genera código vigente.
- [ ] **Fijar las métricas** del protocolo de evaluación en coherencia con un objetivo Poisson
      con exceso de ceros: desvianza de Poisson, calibración por estrato de soporte y
      ordenamiento. Recalcular la tasa de ceros con la zonificación por barrios antes de decidir.
- [ ] **Decidir el balanceo.** Primera opción a probar: pérdida de Poisson o Tweedie, que maneja
      el exceso de ceros nativamente y no necesita balanceo. Si se pasa a una formulación binaria,
      hay que declarar los pesos por clase o el submuestreo usados.
- [ ] **Implementar la línea base** (tasa histórica de la zona × factor de calendario) y
      evaluarla con el protocolo definitivo.

**Metodología abierta**

- [x] ~~Bajar la capa de barrios de Montevideo~~ — hecho (2026-09-04): 62 polígonos vía WFS del
      GeoServer de la Intendencia, en `data/raw/barrios_montevideo.geojson`. Detalle y consulta
      exacta en la sección 3 de arriba.
- [x] ~~Verificar el campo del nombre del barrio~~ — el campo es `barrio` (ya cubierto por
      `CAMPOS_NOMBRE`); los 62 nombres son únicos y coinciden con la nomenclatura oficial.
- [ ] **Primer modelo sobre `panel_zona_top.csv`**, y el mismo modelo sobre
      `panel_zona_contraste.csv` para medir la caída al cambiar de zona.
- [ ] **Entrenar el «megamodelo»** con todas las zonas menos las reservadas, sin `zona_id` como
      predictor, y evaluarlo **con métricas desagregadas por estrato**. Sólo si falla en algún
      estrato, pasar a un modelo por estrato y compararlo contra el agrupado bajo el mismo
      protocolo (ver la sección del ETL para el detalle del razonamiento).
- [ ] **Recalcular `estrato_actividad` sólo con entrenamiento** antes de usarlo para elegir las
      zonas reservadas: hoy está calculado sobre todo el período y es descriptivo.
- [ ] **Decidir el tratamiento del catálogo de zonas** (definirlo sólo con entrenamiento o
      declarar la fuga, hallazgo A14) y tratar las zonas sin historial como estrato propio.
- [x] ~~Corregir `es_feriado`~~ — hecho: `categories=("public", "bank")`, 90 feriados en el
      período, con Carnaval y Semana de Turismo incluidos.
- [x] ~~Integrar el clima~~ — hecho: serie diaria de Open-Meteo cacheada en `data/raw/`.
- [x] ~~Decidir el destino de `analisis_inicial.ipynb`~~ — borrado del repositorio.
- [ ] **Agregar la variable de nivel de zona** (tasa histórica ajustada sólo con entrenamiento).
      Sin ella el modelo no puede distinguir una zona de otra: es el 25 % de desvianza que hoy
      queda sobre la mesa.

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
