# Registro de uso de IA generativa

Este archivo documenta, de forma incremental durante todo el proyecto, el uso de
herramientas de inteligencia artificial generativa, conforme a la sección 4.3 de la
*Guía para estudiantes PAA 2026*.

## Declaración

> _(Indicar explícitamente si se utilizaron o no herramientas de IA generativa en el
> proyecto.)_

En este proyecto **sí** se utilizaron herramientas de IA generativa como apoyo. Todo
contenido incorporado fue revisado, comprendido, adaptado y verificado por el equipo.

## Registro de interacciones

Para cada uso relevante que haya incidido en el código, el análisis, la documentación o
una decisión importante, se completa una entrada con el siguiente formato:

---

### Entrada 1

- **Fecha:** 2026-08-04
- **Herramienta:** Claude Code (Anthropic)
- **Integrante responsable:** _(completar)_
- **Prompt relevante:**
  > Inicializar la estructura de carpetas del repositorio según la guía del PAA 2026 y
  > realizar el primer push al repositorio de GitHub.
- **Respuesta relevante:**
  > Creación de la estructura recomendada (data/, notebooks/, src/, models/,
  > experiments/, app/, documentacion/, tests/), archivos base (README.md,
  > registro_uso_IA.md, requirements.txt, .gitignore) e inicialización del repositorio.
- **Cómo se utilizó / verificó:**
  > La estructura fue revisada contra la sección 4.1 de la guía. El equipo verificó el
  > contenido de cada archivo y confirmó el push al repositorio.

---

### Entrada 2

- **Fecha:**
- **Herramienta:**
- **Integrante responsable:**
- **Prompt relevante:**
- **Respuesta relevante:**
- **Cómo se utilizó / verificó:**

---

## Protección de datos

No se compartieron con estas herramientas datos personales, sensibles, confidenciales o
restringidos sin autorización.


### Desicion de coordenadas en resampling
prompt: Quiero hacer un resampling diario en mi df, que me recomendas hacer con las coordenadas que tengo en mi dataset, el sistema de coordenadas es UTM, tengo x e y, estas son las columnas de mi dataset: Calle, Tipo de Siniestro, Gravedad, Dia, Semana, Hora, Departamento, Localidad, fixed, X, Y. 
Este es el objetivo de nuestro proyecto:
Objetivo general. Desarrollar un modelo de aprendizaje automático para la predicción de siniestros de tránsito a partir de series temporales e integrar sus resultados en una interfaz que permita visualizar las zonas y períodos con mayor cantidad esperada de siniestros.

Respuesta:
Ustedes no están haciendo solamente una serie temporal de cantidad total de siniestros, sino que quieren terminar mostrando “zonas y períodos con mayor cantidad esperada”.

Por lo tanto, yo plantearía el dataset como un problema espacio-temporal.

La estructura que buscaría

En vez de:

1 fila = 1 siniestro

pasaría a:

1 fila = 1 día × 1 zona

Por ejemplo:

Día	Zona	Cantidad
2025-01-01	Z001	4
2025-01-01	Z002	0
2025-01-01	Z003	7
2025-01-02	Z001	3
2025-01-02	Z002	2
2025-01-02	Z003	5

Eso encaja muchísimo mejor con el objetivo de visualizar posteriormente las zonas de mayor riesgo.

¿Qué hago con X e Y?

Acá no recomiendo hacer un promedio diario de X e Y.

Por ejemplo, esto:

df.groupby("Dia")[["X", "Y"]].mean()

no sería una buena representación espacial. Podrías tener 30 accidentes en distintos puntos y obtener un único punto promedio que no representa realmente ninguna zona de riesgo.

En su lugar: crear una grilla espacial

Como tus coordenadas son UTM, tenés una ventaja enorme: X e Y están en metros.

Podrías dividir el territorio en celdas, por ejemplo:

500 m × 500 m

Entonces:

tam_celda = 500

df["grid_x"] = (df["X"] // tam_celda) * tam_celda
df["grid_y"] = (df["Y"] // tam_celda) * tam_celda

Cada siniestro queda asignado a una zona.

Por ejemplo:

X       Y          grid_x   grid_y
523421  6578123    523000   6578000
523450  6578200    523000   6578000
524100  6579000    524000   6579000

Los dos primeros pertenecen a la misma celda.

Después viene el resampling diario

Una vez creada la zona:

df["Dia"] = pd.to_datetime(df["Dia"])

df_diario = (
    df.groupby(["Dia", "grid_x", "grid_y"])
      .size()
      .reset_index(name="Cantidad_siniestros")
)

Pero todavía falta algo importante.

Supongamos que una zona tuvo:

01/01 → 4
02/01 → 3
04/01 → 5

Necesitás que el dataset tenga:

01/01 → 4
02/01 → 3
03/01 → 0
04/01 → 5

Y además, si una zona existe en tu territorio pero un día no tuvo ningún accidente, también debería aparecer con 0.

Esto es fundamental para que el modelo pueda aprender correctamente.

¿Qué tendría finalmente?

Algo así:

Dia         grid_x   grid_y    Cantidad_siniestros
2025-01-01  523000   6578000  4
2025-01-01  523500   6578000  0
2025-01-01  524000   6578000  7
2025-01-02  523000   6578000  3
2025-01-02  523500   6578000  2
2025-01-02  524000   6578000  5
...

Y esa sería la variable objetivo:

Cantidad_siniestros
---

## Sesión 2026-08-30 — Victor Uria — Claude Code (Anthropic, Claude Opus 5)

**Contexto:** creación de `notebooks/diagnostico_datos.ipynb`, el notebook que respalda con
evidencia reproducible el diagnóstico de calidad, adecuación, cobertura y limitaciones de los
datos exigido por el Entregable 2 (guía PAA, sección 5.2) y por la sección *Metodología —
datos* del informe (guía 6.1). Se trabajó sobre `data/raw/uru_siniestros_unificado.csv`, se
leyeron sin modificar los derivados de `data/processed/` y se generaron artefactos citables en
`experiments/diagnostico_datos/`.

### Prompt 1

> Cambie el claude.md, empeza leyendo eso. quiero que crees un notebook nuevo en la carpeta de
> notebooks nuevo que respalde Un diagnóstico de calidad, adecuación, cobertura y limitaciones
> de los datos.

**Respuesta (extracto relevante):** se creó un notebook de 72 celdas estructurado en seis
secciones (trazabilidad de la fuente; fuente y disponibilidad de variables; calidad; cobertura;
adecuación; limitaciones), que exporta 24 tablas en CSV y 4 figuras PNG a
`experiments/diagnostico_datos/`. Los hallazgos con incidencia en decisiones del proyecto
fueron:

1. **Sólo `Fecha`, `X` e `Y` son utilizables como predictoras.** `Gravedad`, `Tipo de Siniestro`
   y `Hora` describen el siniestro ya ocurrido y su uso violaría la restricción de la guía 6.1
   sobre información no disponible en el momento de la predicción.

2. **Ausencia de señal temporal de corto plazo dentro de cada zona.** En las 520 zonas con
   ≥ 100 siniestros, la autocorrelación diaria mediana es 0,0015 (rezago 1) y 0,0057 (rezago 7),
   dentro de la banda nula de un Poisson simulado de la misma tasa ([−0,032, +0,032]); el índice
   de dispersión por zona tiene mediana 1,015. La señal aprovechable es la tasa histórica de la
   zona más el calendario nacional (que explica el 35,3 % de la varianza de log de la serie
   diaria), con una autocorrelación residual de 0,301 a rezago 1 aún sin explicar.

3. **La variable objetivo es casi binaria:** 99,6 % de ceros y 97,4 % de las celdas positivas
   con exactamente un siniestro; índice de dispersión global 1,05.

4. **`es_feriado` está mal construida** en `analisis_inicial.ipynb`: `holidays.country_holidays("UY")`
   devuelve por defecto sólo la categoría `public` (41 días en ocho años). Los 104 días de la
   categoría `bank` omitidos —Semana de Turismo, Carnaval y otros— presentan una media de 65,0
   siniestros diarios frente a 64,8 de los `public` y 77,5 de los días ordinarios.

5. **Los artefactos de `data/processed/` no son reproducibles con el código versionado:**
   `zonas.parquet` tiene 11.633 zonas y centroides de celdas de 1.000 m, mientras
   `analisis_inicial.ipynb` declara `TAM_CELDA = 500` y sus salidas guardadas muestran 18.487
   zonas.

6. **1.308 zonas activas en 2025 (19,1 %) no registran siniestros en 2019–2023**, y concentran
   el 4,6 % de los siniestros del año de prueba. Además, el catálogo de zonas se construye con
   los ocho años, test incluido: fuga leve pero real que debe declararse o corregirse.

**Uso y verificación:** adaptado. El notebook fue reescrito varias veces sobre las salidas
reales: se corrigieron tres cifras que no coincidían con la ejecución (participación anual de
`Hora = 0`, varianza explicada por el calendario y las bandas nulas por rezago) y se rehicieron
tres figuras defectuosas (ejes compartidos que colapsaban el panel de días de la semana, marcas
menores espurias en el eje logarítmico y etiquetas superpuestas). Verificación realizada:
(a) el notebook se ejecutó completo de arriba a abajo con `jupyter nbconvert --execute` sin
errores ni advertencias, y sus salidas quedan guardadas en el archivo; (b) el conteo total de
siniestros se comprueba por aserción en cada transformación (`M.sum() == N`); (c) los conteos
de zonas y de concentración espacial a 500 m se contrastaron contra las salidas guardadas de
`analisis_inicial.ipynb` (18.487 zonas; 687 y 2.589 zonas para el 50 % y el 80 % de los
siniestros); (d) la afirmación de ausencia de señal se validó contra una simulación nula de
Poisson con semilla fija en lugar de interpretar la magnitud de la autocorrelación en abstracto;
(e) la discrepancia de granularidad se verificó leyendo directamente los metadatos de los
Parquet e infiriendo el tamaño de celda desde los centroides.

**Archivos afectados:** `notebooks/diagnostico_datos.ipynb`,
`experiments/diagnostico_datos/tablas/*.csv`, `experiments/diagnostico_datos/figuras/*.png`,
`HANDOFF.md`, `documentacion/registro_uso_IA.md`.

### Prompt 2

> Tengo una observacion para hacerte. La validacion tiene que ser parte del 80% de el conjunto
> de entrenamiento, cuando estudie lo que haciamos era 70% para entrenamiento 10% validacion y
> 20% test. arreglalo en el .ipynb que creaste

**Respuesta (extracto relevante):** se reemplazó la división por años completos
(2019–2023 / 2024 / 2025 ≈ 71/14/14) por una división cronológica en la proporción
**70 / 10 / 20** calculada sobre el eje de días del período de modelado (2019-01-01 a
2025-12-31, 2.557 días), y se añadió al notebook la sección **3.2 «División cronológica del
período de modelado»** con la tabla de particiones y una figura. Cortes resultantes:

| Partición | Desde | Hasta | Días | % días | Siniestros | % siniestros | Media diaria |
| --- | --- | --- | --- | --- | --- | --- | --- |
| entrenamiento | 2019-01-01 | 2023-11-25 | 1.790 | 70,0 | 131.760 | 67,3 | 73,6 |
| validación | 2023-11-26 | 2024-08-07 | 256 | 10,0 | 20.666 | 10,6 | 80,7 |
| test (reservado) | 2024-08-08 | 2025-12-31 | 511 | 20,0 | 43.416 | 22,2 | 85,0 |

Junto con el cambio se señaló una consecuencia que la propuesta no contemplaba: **cumplir
70/10/20 con exactitud obliga a cortar a mitad de año**, y eso deja a las particiones con
distinta composición estacional. La validación no contiene ningún día de setiembre ni de
octubre y el test incluye dos diciembres, el mes de mayor siniestralidad (85,7 siniestros
diarios de media). Esto se documentó como limitación explícita: el *nivel* del error de
validación y el de test no es directamente comparable, aunque sí lo es la comparación entre
modelos dentro de una misma partición. Se dejó registrada la alternativa —cortar por años
completos, a costa de no alcanzar las proporciones pedidas— para que la decisión quede a la
vista.

El nuevo corte también modificó el análisis de estabilidad de zonas (sección 3.5): con las
particiones anteriores eran 1.308 zonas de test sin historial (19,1 %); con las nuevas son
**1.787 de 8.061 (22,2 %), con el 4,6 % de los siniestros del tramo de test**, y 922 de 5.773
(16,0 %) en validación, con el 4,7 %.

Además, al quedar el conjunto de prueba explícitamente delimitado, se revisó la disciplina de
particiones del propio diagnóstico: el análisis de señal temporal de la sección 4.3, que es el
que fija la línea base, se recalculó **restringido al tramo de entrenamiento** para no apoyar
una decisión de modelado en datos reservados. La conclusión se mantiene: la autocorrelación
mediana por zona es −0,0005 (rezago 1) y 0,0035 (rezago 7), dentro de las bandas nulas de
Poisson [−0,038, +0,039] y [−0,036, +0,037], con dispersión mediana de 1,009.

**Uso y verificación:** utilizado, con una salvedad declarada al equipo (la asimetría estacional
que introduce el corte a mitad de año, señalada antes de implementar y documentada en el
notebook y en `HANDOFF.md`). Verificación realizada: (a) el notebook se ejecutó completo con
`jupyter nbconvert --execute` sin errores; (b) una aserción comprueba que las tres particiones
cubren exactamente los 2.557 días del período de modelado, sin solapamiento ni huecos;
(c) las proporciones por días se verificaron contra la tabla `10_particiones.csv` (70,0 / 10,0 /
20,0); (d) la composición mensual de cada partición se representó en `fig2_particiones.png`,
que muestra los ceros de setiembre y octubre en validación; (e) dos bandas nulas citadas en el
texto no coincidían con la ejecución y se corrigieron contra la salida real.

**Archivos afectados:** `notebooks/diagnostico_datos.ipynb`,
`experiments/diagnostico_datos/tablas/*.csv`, `experiments/diagnostico_datos/figuras/*.png`,
`HANDOFF.md`, `documentacion/registro_uso_IA.md`.

### Prompt 3

> Podes hacerme un resumen de todo lo que hicimos en el notebook para que pueda explicarlo al
> profesor. crealo en la carpeta "documentacion"

**Respuesta (extracto relevante):** se creó `documentacion/resumen_diagnostico_datos.md`, un
documento de apoyo para presentar y defender el diagnóstico ante el docente. Estructura: para
qué existe el notebook y a qué requisito de la guía responde; qué datos diagnostica; cómo está
organizado; los seis hallazgos que cambian decisiones del proyecto; cobertura territorial y
temporal; diseño de las particiones; qué se verificó y salió bien; limitaciones declaradas;
pendientes; cómo reproducirlo; y un anexo de preguntas previsibles con su respuesta apoyada en
evidencia.

Al redactarlo se detectaron dos cifras del notebook que **no eran trazables a ningún artefacto**,
lo que contradecía la regla de trazabilidad del proyecto:

1. La afirmación «el 28 % de los registros son SIN LESIONADOS», usada para discutir el
   subregistro, no se calculaba en ninguna celda. Se agregó la tabla
   `01b_composicion_descriptiva.csv` con la distribución de `Gravedad` y `Tipo de Siniestro`:
   LEVE 59,95 %, SIN LESIONADOS 28,12 %, GRAVE 10,49 %, FATAL 1,45 %. La tabla dejó además a la
   vista dos categorías con un único registro (`VUELCO` y `COLISIÓN CON OBSTACULO EN CALZADA`,
   variante sin tilde de una categoría existente con 6.792 registros), anotadas como ruido de
   codificación sin efecto sobre el PAA.
2. Las cifras «abril de 2020: 1.331 siniestros frente a 2.298 de media en los demás abriles» se
   afirmaban sin calcularse. Se agregó el cálculo a la celda de cobertura anual.

Se corrigió también un desajuste de una unidad: el texto de la sección 2.1 decía que `Calle`
tenía 27.792 faltantes cuando la tabla `03_completitud.csv` da 27.793 (un nulo explícito más
27.792 centinelas de texto).

**Uso y verificación:** utilizado. Verificación realizada: (a) cada cifra del resumen se
contrastó una por una contra el CSV o la figura que la respalda en
`experiments/diagnostico_datos/`, y las tres que no tenían respaldo se corrigieron en el
notebook —no en el resumen— para que el artefacto exista; (b) el notebook se reconstruyó y
ejecutó completo con `jupyter nbconvert --execute` sin errores tras cada corrección; (c) se
verificaron los conteos de artefactos citados en el resumen y en `HANDOFF.md` (26 tablas y
5 figuras, 31 archivos) listando el directorio.

**Archivos afectados:** `documentacion/resumen_diagnostico_datos.md` (nuevo),
`notebooks/diagnostico_datos.ipynb`, `experiments/diagnostico_datos/tablas/*.csv`, `HANDOFF.md`,
`documentacion/registro_uso_IA.md`.

---

## Sesión 2026-08-31 — Victor Uria — Claude Code (Anthropic, Claude Opus 5)

**Contexto:** tras la reunión de seguimiento con el docente, se acotó el alcance del proyecto a
Montevideo y se creó `notebooks/preparacion_montevideo.ipynb`, que construye el conjunto de
modelado y lo exporta a `data/processed/montevideo/`.

### Prompt 1

> Tuvimos una reunion y el profesor nos dio estas recomendaciones:
> "Achicar el alcance a Montevideo
> Entrenen un modelo solo para montevideo, que prediga cuantos accidentes van a haber por zona.
> Haganlo por zonas de Mdeo/Barrios/alcaldias.
> Tomamos una zona, y entrenamos un "megamodelo". Lo evaluamos en dos o tres zonas diferentes, Si
> generaliza bien, joya. Si generaliza mal, hay que hacer un modelo para cada zona. Es decir, si no
> conseguimos un modelo que generalice, se tendra que hacer un modelo por zona.
> Tecnica recomendada para tratar los ceros: Interpolacion (que prohiba valores negativos
> obviamente).
> Utilizar los datos a partir del 2021 (asi el modelo no ve los datos de la pandemia)."
>
> La idea ahora es hacer un notebook para el tratamiento del dataset, quiero que crees un notebook
> que agarre los datos de montevideo, los trate segun las recomendaciones del profesor y los
> exporte a data\processed

**Respuesta (extracto relevante):** antes de construir se señaló un bloqueo: el repositorio no
contiene ninguna capa de límites administrativos y el entorno no tiene `geopandas`, de modo que
no era posible asignar barrios ni alcaldías. Se consultó al equipo, que optó por una **grilla de
1 km (403 zonas) con paso diario**. El notebook resultante tiene 34 celdas y diez secciones.

Decisiones técnicas y su justificación:

- **Filtro 2021+ aplicado también al cálculo de variables.** No se usa 2020 ni siquiera como
  período de calentamiento de las medias móviles, para que el régimen de la pandemia no entre por
  la puerta de atrás. A cambio, las medias del arranque de 2021 se calculan con ventana expansiva
  (dividiendo por los días realmente disponibles, no por el ancho de la ventana) y se agrega la
  columna `dias_historia` para poder descartar ese tramo si se quiere.
- **Interpolación de los ceros.** Se implementó como interpolación PCHIP del *conteo acumulado*,
  usando como nodos únicamente los días con siniestro. La derivada de esa curva es la intensidad
  diaria y, como el acumulado nunca decrece y PCHIP preserva la monotonía, **no puede ser
  negativa por construcción**, que es la restricción que puso el docente. El resultado se reescala
  para conservar el total observado por zona y partición.
- **Primera implementación descartada.** Se probó antes tomando como nodos todos los días del
  calendario: PCHIP aplana los tramos sin eventos y devolvía prácticamente el conteo original
  (95,1 % de ceros, desviación 0,2763 frente a 0,2740 del conteo crudo). Es decir, no trataba los
  ceros en absoluto. Con los nodos en los días con evento, los ceros bajan al 17,8 % y la
  desviación a 0,1505.
- **Advertencia declarada en el notebook:** la intensidad interpolada usa información de días
  posteriores dentro de su tramo, así que **no puede usarse como variable predictora**. Se entrega
  como objetivo alternativo de entrenamiento y se calcula por separado dentro de cada partición
  para que no cruce los cortes temporales. La evaluación se hace siempre contra `n_siniestros`.
- **Soporte del experimento del docente.** Se reservó el 20 % de las zonas (80 de 403),
  estratificadas por cuartil de actividad medido sólo en entrenamiento, y ninguna variable
  predictora identifica la zona, de modo que un modelo entrenado en unas zonas pueda aplicarse a
  otras.
- **Particiones cronológicas 70/10/20:** entrenamiento 2021-01-01 → 2024-07-01, validación
  2024-07-02 → 2024-12-31, test 2025-01-01 → 2025-12-31. El corte deja el test coincidiendo con
  un año calendario completo, lo que evita el desbalance estacional que tenía el planteo nacional.

**Uso y verificación:** adaptado. El notebook incorpora seis verificaciones que detienen la
ejecución si fallan, todas en verde: conservación de los 39.676 siniestros, coincidencia de
rezagos y medias móviles con `shift`/`rolling` de pandas en una zona de control, no negatividad
de la intensidad, conservación de la masa por zona y partición (error máximo 0,0000), ausencia de
faltantes y particiones sin solapamiento. Además: (a) el notebook se ejecutó completo con
`jupyter nbconvert --execute` sin errores; (b) el Parquet exportado se releyó y se comprobó que
conserva filas y siniestros; (c) tres cifras del texto no coincidían con la ejecución —el índice
de dispersión, y el efecto de la interpolación sobre los ceros y la desviación— y se corrigieron
contra la salida real; (d) se midió el origen de los ceros que la interpolación no elimina
(6,8 % zonas sin siniestros en su tramo, 11,0 % días posteriores al último siniestro) en lugar de
atribuirlo sin comprobar.

**Archivos afectados:** `notebooks/preparacion_montevideo.ipynb` (nuevo),
`data/processed/montevideo/panel_mvd.parquet`, `data/processed/montevideo/zonas_mvd.parquet`,
`experiments/preparacion_montevideo/`, `requirements.txt` (se agregó `scipy`), `HANDOFF.md`,
`documentacion/registro_uso_IA.md`.

---

## Sesión 2026-09-01 — Victor Uria — Claude Code (Anthropic, Claude Opus 5)

**Contexto:** el equipo rehízo `notebooks/preparacion_montevideo.ipynb` desde cero en Google
Colab, en una versión más simple que la anterior. Se pidió una auditoría del notebook nuevo y la
actualización de `HANDOFF.md`.

### Prompt 1

> Lee el Claude.md primero para tener contexto. Rehice el notebook "preparacion_montevideo.ipynb".
> lo hice en el colab, asi que las rutas estan mal. debido a que lo hice mas snecillo/adaptado a lo
> que queria, no lo hice tan robusto. Entonces el HANDOFF.md quedo desactualizado. Lo que quiero
> que hagas es lo siguiente:
> - Una auditoria del nuevo codigo
> - Actualizar el handoff

**Respuesta (extracto relevante):** en lugar de auditar leyendo el notebook, se reprodujo su
recorte y su grilla sobre la copia local del CSV crudo y se comprobaron los supuestos que el
notebook da por buenos. Hallazgos con consecuencias sobre los datos:

- **Duplicados exactos sin tratar:** 96 filas (0,24 % del recorte). El máximo del objetivo
  —11 siniestros el 2021-07-30 en la zona `567000_6152000`— son 10 copias del mismo registro más
  uno distinto: hay 2 siniestros reales, no 11. El artefacto también está en el
  `panel_mvd.parquet` heredado de la versión anterior.
- **El filtro `year > 2020` no elimina la pandemia:** enero–junio de 2021 promedia 16,37
  siniestros/día frente a 21,45 en los mismos meses de 2022–2025 (−23,7 %). En Uruguay las
  restricciones de movilidad fueron en el primer semestre de 2021, de modo que la justificación
  escrita en el notebook no se sostiene con los datos.
- **El 58,60 % de ceros que informa el notebook es el de la zona más activa**, no el del panel:
  el del panel completo es 95,08 %, con índice de dispersión 1,145. Es esta última la cifra que
  debe orientar el diseño del objetivo y de las métricas.
- **La grilla es demasiado dispersa para el experimento del «megamodelo»:** 28 zonas tienen un
  único siniestro en cinco años, 79 tienen cinco o menos y 167 de 403 concentran el 90 %.
- **El notebook vigente no deja ningún artefacto,** y las salidas que están en disco
  (`data/processed/montevideo/*.parquet`, `experiments/preparacion_montevideo/`) las generó la
  versión anterior, que no llegó a commitearse y no es recuperable. Quedan sin código que las
  reproduzca, lo que rompe la trazabilidad exigida por la guía.

También se verificó lo que **sí** está bien: el formato de fecha `%m/%d/%Y` es el correcto —
coincide con la columna `Dia Semana` en el 100,0000 % de los 224.694 registros, frente al 6,80 %
de `%d/%m/%Y`—, el recorte reproduce exactamente 39.676 siniestros y 403 zonas, el panel conserva
la masa, no hay coordenadas nulas ni fuera del departamento, y la proyección `EPSG:32721` ubica
las celdas correctamente.

**Uso y verificación:** utilizado. La auditoría no se aceptó como texto: se dejó como script
ejecutable (`experiments/auditoria_preparacion_montevideo/auditoria.py`) que corre sobre
`data/raw/uru_siniestros_unificado.csv` y cuya salida (`salida.txt`) respalda cada cifra citada en
`HANDOFF.md`. Verificaciones realizadas: (a) el script reproduce las 39.676 filas, las 403 zonas y
las 735.878 filas del panel que informa el notebook, lo que confirma que se está auditando el
mismo recorte; (b) el sha256 del CSV local (`48a8a7e8…`) coincide con el que registró
`experiments/preparacion_montevideo/tablas/00_procedencia.csv` en la corrida anterior, de modo que
la copia local y la de Drive son el mismo archivo; (c) la hipótesis del formato de fecha se
contrastó contra una columna independiente del propio dataset (`Dia Semana`) en lugar de darla por
buena; (d) el duplicado del máximo se inspeccionó registro a registro antes de afirmarlo. No se
modificó el notebook: la auditoría es diagnóstica y las correcciones quedan como pendientes
priorizados en `HANDOFF.md`.

**Archivos afectados:** `experiments/auditoria_preparacion_montevideo/auditoria.py` (nuevo),
`experiments/auditoria_preparacion_montevideo/salida.txt` (nuevo), `HANDOFF.md`,
`documentacion/registro_uso_IA.md`.

---

## Sesión 2026-09-01 (segunda) — Victor Uria — Claude Code (Anthropic, Claude Opus 5)

**Contexto:** a partir de la auditoría de la sesión anterior, se reescribió
`notebooks/preparacion_montevideo.ipynb` como notebook de **ETL**, adaptando el pipeline del
Proyecto de Ingeniería de Datos (carpeta `etl/`, incorporada al repositorio en esta sesión) al
contexto de aprendizaje automático, con salida a `data/processed/` en CSV.

### Prompt 1

> Bien, ahora vamos a arreglar el notebook, quiero que hagas lo siguiente:
> - Trata los duplicados
> - arregla bien el tema de la fecha, que no incluya 2020 y que los datos esten ordenados a partir
> del 2021
> - Separe la zona mas activa para poder entrenar el primer modelo. ¿Dices que utilice otra zona
> que sea mas representativa?, otra estrategia que podemos tomar en cuenta es hacer 3 modelos
> diferentes, con la finalidad de poder generalizar en el departamento, esto solucionaria el punto
> 4.
> -En el notebook no defini datos para entrenar ni validar. Por ahora solo queria definir que se
> va a hacer en el proceso ETL. Con respecto a eso. uno de nuestros objetivos del proyecto es
> adaptar el ETL de nuestro proyecto anterior "Proyecto de ingenieria de datos", acabo de subir
> esa carpeta "prediccion-siniestros-viales\etl", la idea es adaptarlo al contexto de machine
> learning. Quiero que el dataset tratado se guarde en "/data/processed" como csv

**Respuesta (extracto relevante):**

*Sobre los duplicados.* Se eliminan los duplicados exactos en todas las columnas conservando la
primera aparición: 347 en el archivo del país (321 grupos, el mayor con diez repeticiones), 96
dentro del recorte de Montevideo. **El máximo del objetivo bajó de 11 a 5** y desaparecieron los
valores 9 y 11, que eran íntegramente artefactos de carga. El criterio quedó justificado en el
notebook: el dataset no tiene identificador de siniestro, de modo que dos siniestros reales con
idéntica fecha, hora, calle, coordenada, tipo y gravedad serían indistinguibles de un artefacto;
la evidencia de diez copias exactas indica lo segundo. Es una decisión conservadora sobre la cola
alta del objetivo y se declara como tal.

*Sobre la fecha.* El PID usa `parsear_fecha_mixta`, que prueba `%m/%d/%Y`, `%d/%m/%Y` y
`%Y-%m-%d` hasta que uno funciona; es peligroso porque `05/06/2021` parsea con los dos primeros y
da días distintos sin avisar. Se fijó `%m/%d/%Y` y se **verifica contra la columna `Dia Semana`**
del propio archivo, que es información independiente: la celda levanta `ValueError` si la
coincidencia no es del 100 %. El recorte queda en `fecha >= 2021-01-01` y ordenado
cronológicamente.

*Sobre la zona más activa y la pregunta de las tres estrategias.* Se exportan **dos** series, no
una: la zona más activa (`574000_6137000`, 994 siniestros, 58,6 % de días en cero) para poner a
andar el pipeline, y una zona de contraste de actividad mediana entre las activas
(`575000_6143000`, 160 siniestros, 91,5 % de días en cero). La zona más activa es la celda más
densa de Montevideo y no es representativa: sus métricas no pueden presentarse como resultado del
proyecto. Sobre la propuesta de tres modelos por estrato, se respondió que **no resuelve por sí
sola el problema de dispersión**: el estrato «baja» reúne 722 siniestros en 137 zonas × 1.826
días, un panel con 99,7 % de ceros sobre el que no se puede ajustar más que una tasa constante.
Lo que el estrato sí resuelve es la evaluación. Se recomendó el orden inverso: primero un modelo
agrupado con métricas desagregadas por estrato, y sólo si falla en alguno, pasar a un modelo por
estrato comparándolo contra el agrupado bajo el mismo protocolo — sin la referencia agrupada no
se puede afirmar que estratificar aportó algo. El ETL exporta `estrato_actividad` para dejar las
dos rutas disponibles sin volver a correr nada.

*Sobre la adaptación del ETL del PID.* El notebook conserva del PID el vocabulario controlado de
gravedad (`fatal/grave/leve/solo_danos`) y la reproyección UTM 21S → WGS84, y se aparta en cinco
puntos, cada uno justificado en el propio notebook: alcance de tres países a Montevideo; carga a
CSV en lugar de PostgreSQL y MongoDB; unidad de análisis del siniestro al par (día, zona);
`encoding='utf-8'` en lugar de `latin-1` (**el archivo es UTF-8; latin-1 rompe los acentos**); y
formato de fecha fijo y verificado en lugar de la cascada de formatos. Se dejó explícito que el
notebook **no** define particiones ni variables que aprendan de los datos (rezagos, medias
móviles, interpolación de ceros), porque deben calcularse dentro de cada partición.

**Uso y verificación:** adaptado. Verificaciones realizadas: (a) el notebook se ejecutó completo
con `jupyter nbconvert --to notebook --execute`, sin errores en ninguna de sus 39 celdas; (b)
incorpora diez verificaciones que levantan `AssertionError` si fallan —conservación de los 39.580
siniestros, panel igual al producto días × zonas, clave (fecha, zona) única, suma por gravedad
igual al conteo total, ausencia de faltantes, ausencia de duplicados residuales, pertenencia al
departamento y al período, orden cronológico, objetivo entero no negativo y centroides dentro de
Uruguay—, las diez en verde; (c) los cinco CSV exportados se releyeron con `pandas` y se comprobó
que conservan filas, suma del objetivo (39.580) y tipos; (d) la verificación del formato de fecha
se apoya en la columna `Dia Semana`, que es evidencia independiente del propio archivo, y no en
una suposición. Se advirtió además que el filtro de 2021 **no elimina el régimen de pandemia**
(ene–jun 2021 promedia 16,34 siniestros/día frente a 21,40 en 2022–2025, −23,7 %); el equipo pidió
mantener 2021 completo, de modo que el notebook lo deja medido y documentado en
`experiments/etl_montevideo/tablas/03_pandemia_residual.csv`, y queda pendiente declarar el sesgo
en el informe.

**Archivos afectados:** `notebooks/preparacion_montevideo.ipynb` (reescrito),
`data/processed/*.csv` (nuevos, no versionados), `experiments/etl_montevideo/` (nuevo),
`requirements.txt`, `HANDOFF.md`, `documentacion/registro_uso_IA.md`.

---

## Sesión 2026-09-02 — Victor Uria — Claude Code (Anthropic, Claude Opus 5)

**Contexto:** auditoría del ETL contra la rúbrica de preparación de la consigna y rediseño del
conjunto de modelado en `notebooks/preparacion_montevideo.ipynb`: zonificación por barrios,
codificación del calendario, clima de Open-Meteo y descarte de columnas.

### Prompt 1

> Hagamos una auditoria del ETL que hiciste en "preparacion_montevideo.ipynb", en la consigna del
> trabajo el profesor puso esto:
> Una preparación pertinente: limpieza, transformación, imputación, codificación, escalado,
> balanceo, selección o construcción de variables, reducción de dimensionalidad u otras
> acciones cuando correspondan.
>
> mirando el csv resultante del codigo, se mantuvieron las variables "gravedad", "region",
> "minicipio", "geocodificado", "pais", "hora"(que por el resampling diario no deberia de quedar),
> "calle", "tipo_accidente". Todas estas columnas no las vamos a utilizar, ya que como variables
> exogenas vamos a utilizar "clima", obtenidas mediante la API de openmeteo, "Dia de semana" y
> "feriados"

**Respuesta (extracto relevante):** se señaló primero que las columnas listadas estaban en
`siniestros_montevideo.csv` (capa de eventos) y no en `panel_diario_montevideo.csv` (tabla de
modelado), pero que la crítica era correcta y que el panel tenía problemas peores.

*Hallazgo central, con evidencia.* Clima, día de semana y feriados son **todas variables de día**:
ninguna distingue una zona de otra, de modo que un modelo con sólo esas variables predice lo mismo
para todas las zonas cada día. Se midió con desvianza de Poisson media usando oráculos en muestra
—a cada conjunto se le entrega la media exacta, así que cada valor es su techo—: constante global
0,32773; sólo variables de día 0,32261 (**−1,6 %**); sólo estrato de actividad 0,26234 (−20,0 %);
sólo tasa histórica de la zona 0,24436 (**−25,4 %**); tasa de zona × factor de día 0,23924
(−27,0 %). La descomposición de varianza coincide: entre zonas 10,0 % de la varianza total, entre
días 0,44 %. Conclusión: el conjunto exógeno previsto se disputa un 1,6 % mientras el 25 % de la
identidad de la zona queda sin usar; hace falta al menos una variable de nivel de zona.

*Otras fugas.* `n_fatal + n_grave + n_leve + n_solo_danos` suman exactamente el objetivo (fuga
perfecta); `anio` con corte cronológico deja el año del test fuera del entrenamiento; `mes`,
`dia_anio` y `semana_iso` son cíclicas y como enteros mienten; `region`, `pais` y `geocodificado`
tienen varianza cero.

### Prompt 2

> Perfecto. vamos a aplicar estas decisiones al notebook:
> Vamos a cambiar la grilla de 1km por los barrios de montevideo (que son 62), dado a esta
> desicion, vemos despues lo de la interpolacion de ceros.
> Con respecto a la codificacion, en la codificacion de las siclicas haremos lo siguiente: Crear
> una columna que sea "entre_semana", "fin_semana", "feriado", esta va a ser la codificacion.
> quitamos las columnas que sean respectivas al mes, año y semana, que eso ya esta contenido en la
> fecha, tambien quitar todo lo que haga referencia a la gravedad del siniestro. Poner la fecha
> como indice. Agregar lo del clima. lo de el escalado lo dejamos fuera del ETL (lo voy a hacer en
> otro notebook, cuando vaya a hacer el modelo base).

**Respuesta (extracto relevante):** se aplicaron las seis decisiones. La zonificación quedó como
un cargador que lee la capa de `data/raw/` (GeoJSON o shapefile en `.zip`), la reproyecta a UTM 21S
y asigna cada siniestro por **intersección punto-polígono** resolviendo agujeros y multipolígonos,
con la grilla de 1 km como respaldo que avisa por pantalla. Se eligió `pyshp` +
`matplotlib.path.Path` en lugar de `geopandas` porque este último arrastra GDAL y es la causa más
frecuente de que un notebook deje de correr en Colab.

Los feriados se toman de `holidays` con **`categories=("public", "bank")`**: con la configuración
por omisión aparecen 25 feriados en cinco años y quedan afuera Carnaval y Semana de Turismo; con
las dos categorías son 90 en el período. El clima se pide a Open-Meteo como **una serie diaria
única para el departamento** —a resolución diaria las variables meteorológicas son prácticamente
uniformes sobre 200 km² urbanos— y se cachea en `data/raw/clima_montevideo.csv`.

**Uso y verificación:** adaptado. Verificaciones: (a) el notebook se ejecutó completo con
`jupyter nbconvert --execute` en los **dos caminos de zonificación**, sin errores; (b) como la
capa oficial de barrios no se pudo descargar, el camino de barrios se probó contra una **capa
sintética de 62 polígonos** construida con un polígono con agujero, un multipolígono y una zona
deliberadamente sin cubrir, en los dos formatos (GeoJSON y `.zip` con shapefile), que dieron
resultados idénticos: 38.968 siniestros asignados y 612 (1,55 %) correctamente detectados como
fuera de todo polígono; (c) las trece verificaciones internas del notebook pasan en ambos caminos,
incluidas dos nuevas —«ninguna columna del panel es constante» y «no hay columnas de gravedad»—
que existen precisamente para que los hallazgos de la auditoría no vuelvan a colarse; (d) el
cálculo de desvianza se validó comprobando que la estimación Poisson del porcentaje de ceros
(94,8 %) coincide con el observado (95,08 %); (e) el CSV exportado se releyó y se comprobó que el
índice es un `DatetimeIndex` ordenado y no único, como se buscaba.

**Limitación declarada:** la capa oficial de barrios **no se pudo obtener** —
`intgis.montevideo.gub.uy` y `ckan-data.montevideo.gub.uy` no responden desde el entorno de
desarrollo, y OpenStreetMap no tiene los 62 barrios oficiales como límites administrativos—, así
que el encuentro del código con la capa real queda sin verificar (nombre del campo del barrio y
CRS). El equipo tiene que bajarla y registrar organismo, capa, fecha, versión y licencia.

**Archivos afectados:** `notebooks/preparacion_montevideo.ipynb` (reescrito), `requirements.txt`
(se agregó `pyshp`), `HANDOFF.md`, `documentacion/registro_uso_IA.md`.

---

## Sesión 2026-09-04 — Victor Uria — Claude Code (Anthropic, Claude Sonnet 5)

**Contexto:** el equipo consiguió la capa geográfica de barrios y la dejó en `data/raw/`;
se pidió actualizar `notebooks/preparacion_montevideo.ipynb` para usarla.

### Prompt 1

> Ya puse los los barrios en data/raw, actualiza el notebook

**Respuesta (extracto relevante):** antes de correr nada se inspeccionó el archivo que el equipo
dejó (`data/raw/barrios.json`) y resultó ser la respuesta `GetCapabilities` (XML) de un servicio
WMS, no los polígonos: 10.262 bytes de metadatos del servicio, sin ninguna geometría. El XML sí
identificaba el servicio y la capa: GeoServer de la Intendencia de Montevideo
(`montevideo.gub.uy/app/geoserver`), capa `mapstore-tematicas:zon_v_sig_barrios`. Se pidió esa
misma capa por **WFS `GetFeature`** en GeoJSON (`outputFormat=application/json`,
`srsName=EPSG:4326`); la primera petición devolvió **403** con la librería `requests` por defecto
(bloqueo de WAF por `User-Agent`) y **200** al agregar un `User-Agent` de navegador. El resultado
son 62 polígonos, nombres únicos, coincidentes con la nomenclatura oficial de barrios (Cordón,
Pocitos, Ciudad Vieja, Casavallé…), guardado en `data/raw/barrios_montevideo.geojson`. El archivo
original (`barrios.json`) y otro similar que había quedado (`municipios.json`, con el mismo
problema) se retiraron.

Se corrió el notebook completo contra la capa real y la verificación **«ninguna columna del panel
es constante»** encontró un problema genuino: `zona_activa` (siniestros ≥ 60 en el período) había
quedado en `True` para las 62 zonas, porque el umbral se había fijado pensando en la grilla de
1 km, donde discriminaba 167 de 403 zonas. Con barrios —mucho más volumen por zona, mínimo 225
siniestros— el umbral absoluto dejó de discriminar. Se sacó `zona_activa` del panel de modelado
(sigue en el catálogo `zonas_montevideo.csv`, donde continúa siendo información válida) y la
selección de la zona de contraste pasó a usar el estrato por terciles, que se adapta solo a la
granularidad en vez de depender de un número fijo.

Se repitió el cálculo de desvianza de Poisson de la auditoría del 2026-09-02 sobre el panel nuevo,
para no dar por sentado que el hallazgo seguía valiendo con otra zonificación: con barrios, sólo
variables de día explica −3,5 % (antes −1,6 %), sólo tasa de zona −9,4 % (antes −25,4 %). La
brecha se achica pero no cierra — con menos zonas y más volumen el calendario explica algo más,
pero sigue haciendo falta una variable de nivel de zona.

**Uso y verificación:** adaptado, con un paso de verificación previo que evitó procesar un archivo
que no era la capa. Verificaciones: (a) el JSON no parseaba como GeoJSON — error inmediato de
`json.loads`, que llevó a inspeccionar los bytes crudos en lugar de asumir el formato; (b) los 62
nombres de barrio se listaron y se comprobó que son únicos y reconocibles como barrios reales de
Montevideo, no solo que "el conteo da 62"; (c) el notebook se ejecutó completo con
`jupyter nbconvert --execute`, primero falló por la columna constante (se dejó fallar, no se
ignoró), se corrigió y se volvió a ejecutar hasta las 13 verificaciones en verde; (d) se comprobó
que el número de polígonos dibujados en el mapa folium (62) coincide con el catálogo de zonas;
(e) el cálculo de desvianza se recalculó de cero sobre el panel exportado en lugar de reutilizar
las cifras de la sesión anterior, que correspondían a la grilla.

**Archivos afectados:** `notebooks/preparacion_montevideo.ipynb` (actualizado), `data/raw/`
(`barrios_montevideo.geojson` nuevo; `barrios.json` y `municipios.json` retirados),
`data/processed/*.csv` (regenerados con la nueva zonificación),
`experiments/etl_montevideo/tablas/` (regeneradas, incluida `03b_procedencia_capa_zonas.csv`
nueva), `HANDOFF.md`, `documentacion/registro_uso_IA.md`.

---

## Sesión 2026-09-04 (segunda) — Victor Uria — Claude Code (Anthropic, Claude Opus 5)

**Contexto:** auditoría y reescritura de `notebooks/diagnostico_datos.ipynb`, que había quedado
con el alcance nacional anterior, y reescritura de `documentacion/resumen_diagnostico_datos.md`.

### Prompt 1

> Perfecto, quiero que hagas una auditoria del notebook de "diagnostico_datos", porque creo que
> esta desactualizado. la idea en este notebook no es ya separar las zonas, sino hacer un
> diagnostico completo de calidad, adecuacion, cobertura y limitaciones de los datos de montevideo.

**Respuesta (extracto relevante):** se auditó verificando empíricamente, no sólo leyendo. Hallazgo
de forma: **el notebook ejecutaba sin un solo error**, lo que era lo peor del caso — producía en
silencio un diagnóstico del alcance equivocado. Se comprobó ejecutándolo en una copia aislada para
no tocar los artefactos del repositorio.

Hallazgos: (a) diagnosticaba 224.694 registros de todo el país, 2018–2025, con un panel de
54.019.014 filas sobre celdas de 1 km; (b) las cifras de calidad cambian de forma material con el
recorte —`Localidad` con centinela pasa de 17,91 % a 4,45 %, `Calle` de 12,37 % a 2,33 %, y
`SIN LESIONADOS` de 28,1 % a 15,5 %, lo que debilita el argumento sobre subregistro que la sección
de limitaciones apoyaba en ese 28 %—; (c) cuatro secciones habían quedado fuera de tema
(coherencia con Parquets borrados, división cronológica, estabilidad del universo de zonas,
elección de granularidad); (d) contradicciones internas: la tabla `02_disponibilidad_variables`,
pensada para citarse desde el informe, decía «celda de 500 m» mientras la constante valía 1000, y
ocho celdas referenciaban `analisis_inicial.ipynb`, borrado; (e) dos hallazgos ya resueltos se
seguían reportando como abiertos (clima ausente, feriados incompletos).

**Verificación clave:** antes de recomendar conservar el hallazgo central del diagnóstico —«no hay
señal temporal de corto plazo por zona»— se **recalculó sobre los 62 barrios**, porque una
conclusión obtenida con celdas de 1 km no se hereda al cambiar de granularidad. Se sostiene.

### Prompt 2

> Perfecto, reescribe el notebook

### Prompt 3

> Luego de reescribirlo y tener el diagnostico nuevo, actualiza la documentacion en
> "documentacion/resumen_diagnostico.md", el objetivo de este documento es que claude web me ayude
> a completar la documentacion del proyecto

**Respuesta (extracto relevante):** el notebook se reescribió con 75 celdas, alcance Montevideo
2021–2025 y unidad (día, barrio). Se conservaron los cuatro ejes que pide la guía y se retiraron
las cuatro secciones de zonificación y particiones. Se agregaron tres diagnósticos que antes no
existían: calidad de la asignación punto-polígono a barrios, calidad de la serie climática, y
aporte de cada bloque de variables medido con desvianza de Poisson.

Decisión de diseño: el notebook **recalcula todo desde las fuentes crudas**, incluida la asignación
a barrios, en lugar de leer `data/processed/`. Eso lo convierte en una verificación independiente
del ETL en vez de un resumen de él; la sección 5 compara ambas reconstrucciones y las cinco
comprobaciones coinciden. El código de lectura de la capa y de intersección punto-polígono queda
deliberadamente duplicado respecto del ETL, y se declara en el notebook como candidato a migrar a
`src/`.

Hallazgo nuevo, con consecuencia directa sobre el diseño de variables: las exógenas previstas
—clima, día de la semana, feriados— son **todas variables de día** y ninguna distingue un barrio de
otro. Con oráculos en muestra (cotas superiores): sólo variables de día −3,5 % de desvianza contra
−9,4 % de la sola tasa histórica del barrio. Un modelo con sólo clima y calendario predeciría el
mismo número para los 62 barrios cada día.

`documentacion/resumen_diagnostico_datos.md` se reescribió como resumen **autocontenido**, pensado
para que un asistente sin acceso al repositorio pueda redactar la sección *Metodología — datos*:
cada cifra va con la tabla que la respalda, separa evidencia de inferencia, y agrega una lista
explícita de **frases que no deben aparecer en el informe** porque los datos no las sostienen.

**Uso y verificación:** adaptado. Verificaciones: (a) el notebook se ejecutó completo con
`jupyter nbconvert --execute`, sin errores; (b) la verificación cruzada contra el ETL —dos
implementaciones independientes de la asignación punto-polígono y del armado del panel— coincide en
las cinco comprobaciones (113.212 filas, 39.569 siniestros, 62 zonas, 1.826 días, máximo 7); (c)
**se corrigió una afirmación propia antes de publicarla**: la primera redacción decía que los
barrios con ACF sobre la banda nula eran «del orden de lo esperable por azar», y al contrastarlo
resultó que son 7 y 8 de 62 contra ≈1,6 esperables — se reescribió el pasaje para declarar el
exceso y acotarlo por magnitud (ACF máxima 0,084, menos del 1 % de la varianza), y se subió de 60 a
400 el número de simulaciones para estabilizar la banda; (d) se comprobó por script que las 34
tablas y 3 figuras citadas en el resumen existen en `experiments/diagnostico_datos/`.

**Limpieza:** se borraron las 25 tablas y 5 figuras de la versión nacional. Describían un alcance
superado y convivir con las nuevas habría vuelto ambigua cualquier cita desde el informe (el riesgo
es concreto: la numeración cambió, y `08_verificaciones` de una versión no es lo mismo que de la
otra).

**Archivos afectados:** `notebooks/diagnostico_datos.ipynb` (reescrito),
`documentacion/resumen_diagnostico_datos.md` (reescrito),
`experiments/diagnostico_datos/` (36 tablas y 3 figuras nuevas; 25 tablas y 5 figuras retiradas),
`HANDOFF.md`, `documentacion/registro_uso_IA.md`.

---

## Sesión 2026-09-04 (tercera) — Victor Uria — Claude Code (Anthropic, Claude Opus 5)

**Contexto:** se fijó la convención de documentar cada notebook con un `.md` acompañante en
`documentacion/`, y se escribió el documento del notebook de ETL.

### Prompt 1

> Muy bien. Ahora quiero que hagas lo siguiente:
> - Quiero que agregues al claude.md una seccion de documentacion. Para que en cada seccion se cree
> un nuevo archivo para cada notebook. El objetivo para cada documento es el mismo que el de
> diagnostico de datos. mandarle el .md a claude web para que me ayude con la documentacion del
> proyecto.
> - Quiero que crees un nuevo .md en documentos para el notebook de "preparacion_montevideo". asi
> ya abarco estos puntos en el documento

**Respuesta (extracto relevante):** se agregó a `CLAUDE.md` la sección **Documentación de notebooks
(obligatorio)**, con: el propósito (contexto autocontenido para un asistente **sin acceso al
repositorio**), la convención de nombres (`documentacion/<nombre_del_notebook>.md`, prefijo
`resumen_` por continuidad), una estructura mínima de siete piezas, y cuatro reglas de contenido.
Se añadió también la obligación de actualizar el documento **en la misma sesión** en que se toca el
notebook, con el argumento de que un documento desactualizado es peor que ninguno: induce a citar
cifras que ya no existen.

Las dos propiedades que definen estos documentos, y que la sección enuncia explícitamente: son
**autocontenidos** (nada de «ver la sección 3 del notebook»: si un número importa, va escrito) y
**trazables** (cada cifra con el artefacto que la respalda). La segunda es la regla de oro del
informe aplicada un nivel antes: si el documento no puede rastrear una cifra, el informe tampoco
podrá.

Se escribió `documentacion/resumen_preparacion_montevideo.md` (545 líneas), que cubre
*Metodología — preparación*: trazabilidad respecto del PID (qué se hereda y qué cambia, con el
porqué de cada cambio), las decisiones de limpieza con su **efecto observado** —no sólo el paso—,
la zonificación por barrios frente a la grilla anterior con la comparación que justifica el cambio,
las exógenas, el conjunto exportado con su diccionario, las 13 verificaciones, y una **tabla de
cobertura de la rúbrica de preparación** que declara también lo que *no* corresponde y por qué
(imputación, escalado, balanceo, reducción de dimensionalidad). Incluye la sección de **frases que
no deben aparecer en el informe**, con casos concretos como «se imputaron los valores faltantes»
—no se imputó nada porque no correspondía— y «se eliminaron los outliers» —se eliminaron
duplicados exactos, que es otra cosa—.

**Uso y verificación:** adaptado. Verificaciones: (a) se comprobó por script que las 14 tablas y 2
figuras citadas en el documento nuevo existen en `experiments/etl_montevideo/`, y además que
**ninguna tabla existente quedó sin citar**; (b) se verificó que las cuatro rutas citadas en la
sección nueva de `CLAUDE.md` resuelven; (c) se detectó y corrigió un conteo propio equivocado —el
documento decía «13 tablas» y son 14—; (d) se detectó una diferencia entre documentos (−23,7 % en
el ETL contra −23,6 % en el diagnóstico, por los 11 siniestros que caen fuera de polígono, que cada
notebook descarta en un momento distinto) y se agregó una nota que la explica, en lugar de
uniformar las cifras por comodidad.

**Archivos afectados:** `CLAUDE.md` (sección nueva **Documentación de notebooks** y un bullet en
**Convenciones**), `documentacion/resumen_preparacion_montevideo.md` (nuevo), `HANDOFF.md`,
`documentacion/registro_uso_IA.md`.


---

## Sesión 2026-09-07 — Victor Uria — Claude Code (Anthropic, Claude Opus 5)

**Contexto:** ajustes pedidos por el docente en la reunión de seguimiento: cambiar la zonificación
de barrios a **municipios**, excluir del período los meses de pandemia de 2021, y actualizar los
informes de `documentacion/`. La sesión cubrió el primer notebook y su documento acompañante:
`notebooks/diagnostico_datos.ipynb` y `documentacion/resumen_diagnostico_datos.md`. El ETL
(`preparacion_montevideo.ipynb`) quedó explícitamente pendiente.

### Prompt 1

> Claude, para que tengas mas contexto de nuestro proyecto lee el claude.md y el handoff.md.
> Acabamos de reunirnos con nuestro profesor y tenemos que hacer unos ajustes:
> - cambiar el tamaño de las zonas de Montevideo. vamos a hacer por municipios. En data/raw hay un
> .json que tiene el link de donde conseguir el .geojson con los limites de dichos municipios (Si
> no me equivoco son 8)
> - Arreglar el indice temporal en los notebooks. Empieza con 2021 pero en ese año hubieron algunos
> meses de pandemia, hay que sacarlos.
> - Arreglar los informes que estan en documentacion, especificamente "resumen_diagnostico_datos.md"
> y "resumen_preparacion_montevideo.md"
>
> Vamos a empezar arreglando el primer notebook "diagnostico_datos.ipynb" con el nuevo enfoque y su
> respectivo informe

**Respuesta (extracto relevante):**

*Capa de municipios.* Se identificó que `data/raw/municipios.json` **no era la capa** sino la
respuesta `GetCapabilities` (XML) del servicio WMS —el mismo problema que ya había ocurrido con
barrios—. De ese XML se extrajo el nombre de la capa (`zon_v_sig_municipios`) y se la descargó por
WFS, con `User-Agent` de navegador porque el servicio devuelve 403 ante el de una librería:

```
GET https://montevideo.gub.uy/app/geoserver/mapstore-tematicas/zon_v_sig_municipios/ows
    ?service=WFS&version=2.0.0&request=GetFeature
    &typeName=mapstore-tematicas:zon_v_sig_municipios
    &outputFormat=application/json&srsName=EPSG:4326
```

Resultado: 8 polígonos (A, B, C, CH, D, E, F, G), guardados en
`data/raw/municipios_montevideo.geojson`. Confirma la cifra que anticipaba el equipo.

*Corte temporal.* En lugar de aplicar el corte por decreto, se midió primero. El análisis
exploratorio mostró que el déficit de 2021 se concentra en **febrero–junio** y que julio–diciembre
ya se comporta como un año normal, de modo que `FECHA_INICIO = "2021-07-01"` quedó respaldado con
evidencia en tres pasos, que se incorporaron al notebook como sección 3.1:

| Paso | Qué mide | Resultado |
| --- | --- | --- |
| 1. Nivel | ene–jun 2021 contra los mismos meses de 2022–2025 | −23,7 % |
| 2. Índice estacional | cada mes / media de su propio año (elimina la tendencia) | feb–jun 2021 entre −7,0 % y −17,2 % |
| 3. Verificación del corte | jul–dic 2021 contra jul–dic siguientes | +3,1 %, +2,8 %, +5,7 %, +2,8 % (variación ordinaria) |

El paso 2 es el que separa «pandemia» de «tendencia creciente», y sin él el argumento no cerraba.

*Advertencia sobre el impacto del cambio de zonificación.* Al recalcular el panel con 8 municipios
en lugar de 62 barrios, **dos conclusiones centrales del diagnóstico se invierten**, y se señaló
como el hallazgo más importante de la sesión:

| Indicador | Barrios | Municipios |
| --- | --- | --- |
| Filas del panel | 113.212 | 13.160 |
| % de ceros | 71,96 % | **8,60 %** |
| Señal temporal a rezago 1 | no se detecta | **5 de 8 zonas sobre la banda nula** |
| Razón máx/mín entre zonas | ~10× | **1,71×** |

Consecuencias que se dejaron escritas: ya no corresponde balancear ni tratar exceso de ceros; el
rezago de un día pasa a ser candidato en vez de estar descartado; y el hold-out de zonas del
«megamodelo» pierde casi todo su poder estadístico.

*Aporte metodológico añadido.* Las versiones anteriores medían el aporte de cada bloque de
variables con **oráculos en muestra**, que son techos inalcanzables. Se agregó una segunda pasada
con partición temporal, y el orden se invierte:

| Predictor (estimado en la 1.ª mitad, evaluado en la 2.ª) | Desvianza | Mejora |
| --- | --- | --- |
| Sólo calendario (día de semana + feriado) | 1,30530 | −4,3 % |
| Sólo tasa histórica del municipio | 1,26172 | −7,5 % |
| **Tasa × calendario (multiplicativa)** | **1,20308** | **−11,8 %** |
| Tasa × (calendario + llovió) | 1,20716 | −11,5 % |
| Celdas saturadas municipio × calendario × mes | 1,50546 | **+10,4 %** |

Esto confirmó con medición la línea base que hasta ahora estaba postulada, mostró que **el clima no
aporta nada fuera de muestra**, y mostró que **la forma saturada empeora el resultado**, lo que
justifica la forma multiplicativa.

**Uso y verificación:** utilizado con adaptaciones. Verificaciones realizadas:

1. **Ejecución completa del notebook** con `jupyter nbconvert --to notebook --execute`: 77 celdas,
   **sin errores**, 43 tablas y 3 figuras escritas en `experiments/diagnostico_datos/`.
2. **Contraste de cada cifra del documento contra su artefacto CSV**, no contra la memoria de la
   conversación.
3. Se detectaron y corrigieron **tres defectos propios** antes de cerrar: (a) la tabla del costo
   del corte contaba registros sin deduplicar (2.963) mientras la del paso 1 contaba deduplicados
   (2.957) — se unificó al criterio deduplicado; (b) la tabla de cobertura anual informaba una
   variación 2021→2022 de +94,7 % que era un artefacto de comparar medio año contra uno entero —
   se pasó a comparar medias diarias, se agregó la columna de días observados y se marcó esa
   celda como «no comparable»; (c) la etiqueta del municipio C quedaba ilegible sobre el relleno
   oscuro del mapa — se le agregó halo blanco.
4. Se verificó que el bloque climático más fino (`dow + feriado + mes + llovió + temp`) daba
   −9,3 % **en muestra** pero +0,4 % fuera de muestra: era sobreajuste (1.344 grupos para 1.645
   días). Se descartó esa cifra en lugar de informarla.
5. **La verificación cruzada contra el ETL no se pudo ejecutar** porque `data/processed/` sigue en
   el alcance anterior. Se modificó la celda para que **detecte el desfasaje y se abstenga de
   comparar**, en vez de informar una discrepancia falsa, y quedó registrado como bloqueante en
   `HANDOFF.md` y en el documento.
6. Se borraron las 36 tablas y 3 figuras de la corrida por barrios: convivir con las nuevas habría
   hecho ambigua cualquier cita desde el informe.

**Lo que quedó pendiente y se declaró explícitamente:** `preparacion_montevideo.ipynb` y
`documentacion/resumen_preparacion_montevideo.md` **siguen en el alcance anterior**. Mientras
tanto, ninguna cifra de `data/processed/` puede citarse en el informe.

**Archivos afectados:** `notebooks/diagnostico_datos.ipynb`,
`documentacion/resumen_diagnostico_datos.md`, `experiments/diagnostico_datos/` (43 tablas y 3
figuras), `data/raw/municipios_montevideo.geojson` (nuevo), `HANDOFF.md`,
`documentacion/registro_uso_IA.md`.


---

## Sesión 2026-09-07 (segunda) — Victor Uria — Claude Code (Anthropic, Claude Opus 5)

**Contexto:** continuación de la sesión anterior. Migración del ETL
(`notebooks/preparacion_montevideo.ipynb`) al mismo alcance que el diagnóstico —municipios (8)
desde 2021-07-01— y reescritura de su documento acompañante
`documentacion/resumen_preparacion_montevideo.md`.

### Prompt 1

> Perfecto. Sigue con el ETL

**Respuesta (extracto relevante):**

*Migración aplicada.* El notebook se reescribió con la zonificación por municipios y
`FECHA_INICIO = "2021-07-01"`, y se ejecutó de punta a punta con **16 de 16 verificaciones en
verde**. Resultado del panel, idéntico al que el diagnóstico reconstruye por su cuenta: 13.160
filas, 36.612 siniestros, 8 zonas, 1.645 días, 8,60 % de ceros, máximo 13.

*Cambios de criterio que fueron más allá de cambiar dos parámetros*, cada uno con su razón:

| Decisión | Antes | Ahora | Por qué |
| --- | --- | --- | --- |
| Capa ausente | Caía a grilla de 1 km | **Falla ruidosamente** | Producía igual un conjunto de otro alcance (403 zonas, 95 % de ceros) indistinguible del bueno en `data/processed/` |
| `estrato_actividad` | En el panel | **Sólo en el catálogo** | Con 8 zonas en un rango de 1,71× los terciles son arbitrarios, y está calculado sobre todo el período (fuga) |
| `zona_activa` | En el catálogo | **Eliminado** | Con municipios es cierto para los ocho: no informa |
| Balanceo / interpolación de ceros | Pendientes a decidir | **No corresponden** | 8,60 % de ceros: no hay exceso que tratar |
| Sección 3.1 | «Advertencia» sobre el filtro de 2021 | **Verificación que detiene la ejecución** | La decisión ya está tomada; hay que impedir que la fecha se mueva sin releer el diagnóstico |

Consecuencia declarada y deliberada: **el panel exportado no lleva ninguna variable de nivel de
zona**. La tasa histórica del municipio —el bloque más útil según el diagnóstico— debe estimarse
sólo con entrenamiento, así que corresponde al notebook de modelado. Se agregó una verificación
que lo custodia.

*Tres verificaciones nuevas* (5, 6 y 10 de las 16), cada una contra un error concreto: que
`FECHA_INICIO` se mueva sin releer el diagnóstico, que un polígono de la capa quede sin datos, y
que vuelva a colarse al panel una variable de zona calculada sobre todo el período.

**Uso y verificación:** utilizado con adaptaciones. Verificaciones realizadas:

1. **Ejecución completa** del notebook con `jupyter nbconvert --to notebook --execute`: 42 celdas,
   sin errores, 16/16 verificaciones en OK, 15 tablas y 2 figuras en
   `experiments/etl_montevideo/`.
2. **Verificación cruzada entre los dos notebooks**, que es la evidencia más fuerte de esta
   sesión: `diagnostico_datos.ipynb` reconstruye el panel desde las fuentes crudas con su propia
   implementación de la asignación punto-polígono, y **las cinco comprobaciones coinciden**
   (13.160 filas, 36.612 siniestros, 8 zonas, 1.645 días, máximo 13). Con esto `data/processed/`
   pasa a ser citable en el informe.
3. Se detectaron y corrigieron **dos errores propios**, ambos del tipo que produce cifras
   equivocadas en silencio:
   - **Fecha ISO leída con `dayfirst=True`.** La celda del diagnóstico que lee el panel del ETL
     usaba `pd.to_datetime(..., format="mixed", dayfirst=True)`, que sobre `2021-07-01` devuelve
     **el 7 de enero**. Por eso la verificación cruzada seguía diciendo «otro alcance» aun con el
     ETL ya migrado. Es exactamente el riesgo que el propio notebook verifica en la fuente cruda
     (sección 2.3). Corregido: el formato se decide mirando el texto, no por bandera.
   - **Dos diferencias de redondeo que parecían discrepancias entre notebooks:** la varianza del
     objetivo (`ddof=1` en el ETL contra `ddof=0` en el diagnóstico) y la variación interanual
     (el ETL la calculaba sobre medias ya redondeadas). Ambas alineadas en vez de explicadas al
     pie: el panel es la población completa, así que `ddof=0`.
4. **Contraste de cada cifra del documento contra su artefacto CSV**, y comprobación por script de
   que las 15 tablas están citadas y de que no se cita ninguna que no exista.
5. Se verificó que el par `panel_zona_top` / `panel_zona_contraste` **perdió su utilidad**: la
   razón entre ambos bajó de 2,8× (barrios) a **1,15×** (municipios) y las series son casi
   indistinguibles. Se conservan por continuidad, pero quedó declarado en el documento que **no
   sirven como evidencia de generalización**.

**Archivos afectados:** `notebooks/preparacion_montevideo.ipynb`,
`documentacion/resumen_preparacion_montevideo.md`, `notebooks/diagnostico_datos.ipynb` (celda de
lectura del panel del ETL), `documentacion/resumen_diagnostico_datos.md` (sección 7 y pendientes),
`experiments/etl_montevideo/` (15 tablas, 2 figuras), `experiments/diagnostico_datos/`
(reejecutado), `data/processed/` (6 archivos regenerados), `HANDOFF.md`,
`documentacion/registro_uso_IA.md`.

---

## Sesión 2026-09-10 — Victor Uria — Claude Code (Anthropic, Claude Sonnet 5)

**Contexto:** creación de `notebooks/base.ipynb` —el modelo base del proyecto— sobre la serie
diaria de un municipio (`data/processed/panel_zona_top.csv`). Cubre los tres puntos del
Entregable 2: protocolo de evaluación (particiones, validación, métricas, sin fugas), conjunto
de prueba reservado, y línea base con interpretación preliminar. Se dejó como referencia de
estilo el notebook del curso `notebooks/Ejemplos/Series_temporales_y_pronóstico_ejemplo.ipynb`.
Documento acompañante nuevo: `documentacion/resumen_base.md`.

### Prompt 1

> Claude, lee el claude.md y handoff para que tengas mejor contexto del proyecto. Luego vamos a
> proceder a hacer lo siguiente:
> En esta carpeta cree un notebook que esta vacio que se llama "base.ipynb". La idea de este
> notebook es ya crear el modelo base para nuestro proyecto. El dataset que vamos a utilizar esta
> en "data/processed/panel_zona_top.csv".
> Los puntos que debe cubrir este notebook son:
> - Un protocolo de evaluación válido: particiones, validación y métricas apropiadas, sin fugas
> de información.
> - Un conjunto de prueba reservado y no utilizado para ajustar procedimientos ni seleccionar
> modelos.
> - Una línea base adecuada y una interpretación de los resultados preliminares.
> deje un ejemplo de notebook de series temporales que nuestro profesor hizo el año pasado. el
> ejemplo esta en notebooks/ejemplos. Lo subi para que veas masomenos la estructura de lenguaje
> que quiero que utilices

**Respuesta (extracto relevante):**

Notebook de 44 celdas, en el registro y la estructura del ejemplo del curso (español, primera
persona del plural, markdown explicativo antes de cada bloque de código). Decisiones tomadas y su
origen:

| Decisión | Origen |
| --- | --- |
| Métrica principal **desvianza de Poisson media** + MAE, RMSE, razón total predicho/observado, sesgo medio | `resumen_diagnostico_datos.md` §5.1 |
| Partición cronológica **80 % desarrollo / 20 % prueba reservada** (últimos 329 días); dentro de desarrollo, **backtesting de ventana deslizante** (origen móvil, expansiva, horizonte 7 días, 47 cortes) | Ejemplo del curso (`backtesting_forecaster`, `TimeSeriesFold`); guía 6.2 |
| Línea base = **tasa × factor de calendario** (media del entrenamiento por `tipo_dia`); contrastada con media constante, naive estacional (t−7), media móvil 56 d × calendario, y una regresión de Poisson de referencia (rezagos t−7/14/21 + calendario + tendencia) | `resumen_diagnostico_datos.md` §5.3 |
| Backtesting **implementado a mano** (no `skforecast`), para que sea auditable y sin dependencia nueva | criterio del equipo |
| **`y(t−1)` no se usa** (exigiría recursión; aporte pequeño según el diagnóstico) | `resumen_diagnostico_datos.md` §5.2 |

Resultados (artefactos en `experiments/base/`): en desarrollo la regresión de Poisson tiene la
menor desvianza (1,364; −10,1 % vs media constante), con la línea base muy cerca (1,378, −9,2 %);
el naive estacional (t−7) queda descartado (desvianza 7,90). En el **test** (una sola vez): la
regresión de Poisson 1,030, mejor que la línea base (1,085, −5,0 %) y la media constante (1,263,
−18,4 %). Los tres finalistas **infra-predicen** el test (razón total 0,88–0,95), lo que confirma
que la tendencia creciente hay que tratarla explícitamente en el notebook del panel.

**Uso y verificación:** utilizado con adaptaciones (el borrador se reescribió para reemplazar los
marcadores de interpretación por los números reales de la corrida). Verificaciones realizadas:

1. **Ejecución completa** con `jupyter nbconvert --to notebook --execute --inplace`: 44 celdas,
   **0 celdas con error**, 11 tablas y 6 figuras escritas en `experiments/base/`. Entorno: se
   creó un `.venv` (gitignored) sobre Python 3.14.7 con las versiones de `requirements.txt`
   (`pandas 3.0.5`, `numpy 2.5.2`, `scikit-learn 1.9.0`, `scipy 1.18.1`, `matplotlib 3.11.1`,
   `statsmodels 0.14.6`, `jupyter 1.1.1`). El notebook usa sólo pandas/numpy/matplotlib/
   scikit-learn: **no se agregó ninguna dependencia a `requirements.txt`**.
2. **Verificación de ausencia de fugas**, revisada por lectura del código: medias y coeficientes
   se estiman con la ventana de entrenamiento de cada corte (`ajuste = historia`); en el test el
   ajuste queda congelado en el desarrollo (`ajuste_fijo = serie_desarrollo`) y sólo la historia
   para los rezagos avanza; el modelo de referencia usa rezagos `t−7/14/21` (todos observados
   para horizonte 7), **sin recursión**; `serie_test` no aparece en el código entre §5 y §9.
3. **Contraste de cada cifra del documento acompañante contra su artefacto CSV** — todas las
   tablas de `resumen_base.md` salen de `experiments/base/tablas/`.
4. **Verificación de la métrica:** `evaluar()` devuelve desvianza 0 para una predicción perfecta;
   la desvianza de Poisson exige predicciones > 0, resuelto con un recorte a 1e-6.
5. **Revisión del formato de fecha:** se parsea con `format="%Y-%m-%d"` explícito, no con
   `dayfirst` ni detección automática, por el error registrado en la sesión 2026-09-07.

**Archivos afectados:** `notebooks/base.ipynb` (nuevo), `documentacion/resumen_base.md` (nuevo),
`experiments/base/` (11 tablas, 6 figuras, nuevo), `HANDOFF.md`,
`documentacion/registro_uso_IA.md`, `.venv/` (entorno local, no versionado).

### Prompt 2

> Quisiera que el modelo base sea un desicion tree basico

**Respuesta (extracto relevante):**

Se reemplazó el modelo aprendido del notebook: la regresión de Poisson pasó a ser un
**árbol de decisión básico** (`DecisionTreeRegressor`, `max_depth=4`, `min_samples_leaf=20`),
con las mismas variables (rezagos `t−7/14/21`, indicadoras de fin de semana y feriado,
tiempo en años). Se mantiene `Tasa × calendario` como **línea base del proyecto** porque es
la que el diagnóstico exige metodológicamente y la que mejor rinde fuera de muestra;
reemplazarla contradiría `resumen_diagnostico_datos.md`.

Se agregó una **corrida de comparación de profundidad** (§7, `04c_arbol_profundidad.csv`):
árbol sin podar → profundidad 31, 943 hojas, desvianza de Poisson **12,65**; árbol
`max_depth=4` (13 hojas) → **1,40**. Justifica el límite de profundidad con evidencia.

Resultado, y es un hallazgo útil para el informe:

- **Desarrollo** (`04_desarrollo_backtesting`): el árbol base (desvianza 1,401) supera a la
  media constante (1,518, −7,7 %) pero queda por debajo de la línea base `Tasa × calendario`
  (1,378). Calibración en muestra casi perfecta (razón total 0,998).
- Importancias (`05_importancias_arbol`): `es_fin_semana` 53 %, `t_anios` 23 %,
  `es_feriado` 17 %; los tres rezagos juntos < 8 %, `y_lag14` exactamente 0.
- **Test** (`06_evaluacion_test`, una sola vez): **el árbol es el peor de los tres** —
  desvianza **1,679**, contra 1,085 de la línea base y 1,263 de la media constante. Razón
  total 0,723 (infra-predice 28 %, sesgo −1,07/día); el detalle mensual baja a 0,64 en
  agosto–septiembre.
- **Causa:** un árbol **no extrapola** — fuera del rango de entrenamiento devuelve el valor
  de la última hoja. El diagnóstico lo había anticipado para `anio`
  (`resumen_diagnostico_datos.md`, §5.3). El conjunto de prueba reservado hizo su trabajo:
  un modelo competitivo en desarrollo se cae en el test.

**Uso y verificación:** utilizado con adaptaciones (el borrador se reescribió para
reemplazar los números de la regresión de Poisson por los del árbol tras ejecutar).
Verificaciones:

1. **Reejecución completa** con `nbconvert --execute --inplace`: 46 celdas, 0 errores,
   12 tablas y 7 figuras en `experiments/base/`. Sin dependencias nuevas
   (`DecisionTreeRegressor` es de `scikit-learn`, ya en `requirements.txt`).
2. **Ausencia de fugas revisada de nuevo:** el árbol se entrena con `ajuste` (la ventana de
   cada corte en desarrollo; el desarrollo completo y congelado en el test); las variables
   de rezago se construyen sólo con `historia` observada; los rezagos `t−7/14/21` caen
   todos dentro de la ventana observada para un horizonte de 7 días, sin recursión.
3. **Contraste de cada cifra del notebook y de `resumen_base.md` contra los CSV de
   `experiments/base/tablas/`.**
4. **Lectura de las figuras ejecutadas:** `fig5` muestra el árbol sistemáticamente por
   debajo del nivel observado del test; `fig4b` la jerarquía de importancias.

**Archivos afectados:** `notebooks/base.ipynb` (regenerado, ahora 46 celdas),
`documentacion/resumen_base.md` (§1, §4, §5.1–5.4, §6, §7, §8 reescritas),
`experiments/base/` (12 tablas —nueva `04c`, `05` renombrada de `05_coeficientes_poisson`—, 7 figuras —nueva `fig4b`—),
`HANDOFF.md`, `documentacion/registro_uso_IA.md`.

## Sesión 2026-09-14 — Victor Uria — Claude Code (Anthropic, Claude Opus 5)

**Contexto:** el equipo agregó a mano la sección 2.8 *Análisis de outliers* en
`notebooks/diagnostico_datos.ipynb` y lo reejecutó. Se pidió documentarla en `HANDOFF.md` y en el
documento acompañante del notebook. Claude **no modificó el notebook ni lo ejecutó**: documentó la
corrida que ya estaba guardada.

### Prompt 1

> claude, hice una nueva seccion en diagnostico de datos, 2.8 outliers. Documentalo en handoff y resumen diagnostico de datos con su respectiva fecha

**Respuesta (extracto relevante):**

Se agregó la **§3.8** a `resumen_diagnostico_datos.md` (la numeración del resumen va una sección
por delante de la del notebook) y una sección fechada en `HANDOFF.md`. Contenido central, tomado
de `10c_outliers_diarios.csv` y `10d_dias_atipicos.csv`:

- Criterio de Tukey sobre la serie diaria del departamento: Q1 18, Q3 27, IQR 9, límites **4,5** y
  **40,5**; **8 días atípicos (0,49 %)**, 1 inferior (2022-01-16, 4) y 7 superiores (41–44).
- De los 7 superiores, **5 son viernes** y 6 son de 2023 en adelante.
- El notebook **no elimina ningún día**; la sección es descriptiva.

Observaciones señaladas al equipo, no resueltas:

1. La sección 2.8 **no tiene celda de interpretación**: termina en la figura.
2. El criterio global **no descuenta el calendario**, lo que explica la concentración en viernes.
3. En `fig0_outliers_diarios.png` **los puntos no son los atípicos de `10d`**: `matplotlib`
   calcula los atípicos por caja (por día de la semana), mientras que las líneas horizontales son
   los límites globales. Se recomendó una tabla por día de la semana antes de citar esa diferencia.

La lectura «el patrón es compatible con actividad real (calendario + tendencia), no con fallas de
carga» se dejó marcada explícitamente como **inferencia de Claude a validar por el equipo**, porque
el notebook no la escribe ni la verifica.

**Uso y verificación:** utilizado tal cual en la documentación; la interpretación queda sujeta a
revisión del equipo. Verificaciones:

1. **Cada cifra de §3.8 y del HANDOFF contrastada contra `10c_outliers_diarios.csv` y
   `10d_dias_atipicos.csv`**; los días de la semana y la cuenta por año se contaron sobre `10d`. Las
   medias por `tipo_dia` y la del viernes se tomaron de §4.4 del resumen (`15_cobertura_calendario`,
   `20c_perfil_semanal`), que no cambiaron.
2. **Que no cambió ninguna cifra previa:** `git status` / `git diff` sobre
   `experiments/diagnostico_datos/` muestran sólo 3 archivos nuevos y 2 modificados (`00b_entorno`:
   fecha de ejecución; `25_artefactos`: listado). Conteo en disco: 45 tablas y 4 figuras.
3. **Que la corrida no tiene errores:** recorrido con Python de las salidas del `.ipynb`
   (0 salidas de tipo error, 80 celdas).
4. **Que no hay eliminación de atípicos ni fuga:** búsqueda de `atipicos`, `LIM_INF` y `LIM_SUP` en
   todas las celdas; sólo aparecen en las dos celdas de la sección 2.8.
5. **Qué serie se analiza:** `por_dia = df_dedup.groupby("Fecha").size()`, es decir el recorte ya
   deduplicado, antes de asignar municipios.
6. **Referencias internas del markdown de la 2.8** (a 2.2, 2.5 y 4.1) contrastadas contra los
   encabezados del notebook: son correctas.
7. **Lectura de la figura** para describir qué representan puntos y líneas; la diferencia entre
   figura y tabla se describe sólo cualitativamente, por no tener artefacto tabular.

**Archivos afectados:** `documentacion/resumen_diagnostico_datos.md` (encabezado, tabla de
versiones, §3.5, §3.8 nueva, §6, §8, §9), `HANDOFF.md` (fecha, §3, sección nueva, pendientes),
`documentacion/registro_uso_IA.md`.

### Prompt 2

*(Los tres puntos refieren a las tres observaciones de la respuesta anterior: falta de celda de
interpretación, figura y tabla que no marcaban los mismos días, y criterio global que mezcla
calendario.)*

> 1. Agrega la celda
> 2. Soluciona esto, si no podes, le hacemos caso a los valores calculados en la tabla y dejamos la grafica para visualizar. 
> 3. Resolve.

**Respuesta (extracto relevante):**

Se editó la sección 2.8 del notebook (con `nbformat`, desde un script; el notebook excede el
tamaño que admite la herramienta de edición de celdas) y se reejecutó completo:

1. **Criterio por grupo de calendario** (resuelve el punto 3). Celda nueva que aplica Tukey dentro
   de cada día de la semana, con los feriados como grupo propio (construidos igual que en la
   sección 3.4, `categories=("public","bank")`). Genera `10e_outliers_por_calendario`,
   `10f_dias_atipicos_por_calendario` (incluye el feriado más cercano y la distancia en días) y
   `10g_comparacion_criterios`.
2. **Figura rehecha** (resuelve el punto 2 sin tener que recurrir a la alternativa del equipo): una
   caja por grupo; puntos rellenos = atípicos en su grupo, anillos = atípicos globales. Verificación
   dentro de la celda:

   ```python
   for g, puntos in zip(GRUPOS_CAL, caja["fliers"]):
       esperado = sorted(por_dia[(grupo_cal == g) & atipico_grupo].tolist())
       assert sorted(puntos.get_ydata().tolist()) == esperado, f"figura y 10f difieren en «{g}»"
   assert glob.index.equals(atipicos.sort_index().index), "anillos de la figura y 10d difieren"
   ```
3. **Celda de interpretación** (punto 1), escrita después de ejecutar y con las cifras de las
   tablas: 8 atípicos globales, 9 dentro de su grupo, 3 en común; 5 de los 8 globales son normales
   para su grupo; los 8 atípicos altos por grupo son de 2023 en adelante; 3 días a +3 de un feriado;
   decisión de no eliminar ningún día. La coincidencia de dos domingos con jornadas electorales
   (2024-11-24 y 2025-05-11) se escribió como **hipótesis externa no verificada**, que requiere
   fuente para usarse en el informe.

**Uso y verificación:** utilizado; la interpretación del notebook queda pendiente de validación del
equipo, y así quedó señalado en `HANDOFF.md` y en el resumen. Verificaciones:

1. **Respaldo** del notebook antes de editar (copia en el scratchpad de la sesión, no versionada).
2. **Round-trip de `nbformat`** comprobado idéntico al archivo original antes de escribir, para no
   reformatear el resto del notebook.
3. **Ejecución completa** con `jupyter nbconvert --execute --inplace` en el `.venv` (Python 3.13.2,
   el mismo entorno de la corrida del equipo): 0 salidas de error, ninguna celda de código sin
   ejecutar. Los `assert` de la figura pasaron (la celda imprime la confirmación).
4. **Ninguna cifra previa cambió:** `git status`/`git diff --stat` sobre
   `experiments/diagnostico_datos/` sólo muestran `00b_entorno` y `25_artefactos` modificados,
   además de los archivos nuevos.
5. **Coherencia con otras tablas:** el grupo «feriado» tiene 77 días, igual que
   `15_cobertura_calendario.csv`; los días por grupo suman 1.645.
6. **Lectura de la figura generada** y contraste de cada cifra de la celda de interpretación, del
   resumen y del HANDOFF contra `10c`, `10e`, `10f` y `10g`.
7. Las fechas electorales son **conocimiento del modelo, no del repositorio**; por eso se marcaron
   como hipótesis a verificar y no como hallazgo.

**Archivos afectados:** `notebooks/diagnostico_datos.ipynb` (import `Line2D`, markdown de la 2.8
ampliado, 1 celda de código nueva, celda de figura reemplazada, 1 celda markdown nueva),
`experiments/diagnostico_datos/` (`10e`, `10f`, `10g` nuevas; `fig0` regenerada; `00b`, `25`
actualizadas), `documentacion/resumen_diagnostico_datos.md` (§3.8 reescrita, encabezado, §6, §8,
§9), `HANDOFF.md`, `documentacion/registro_uso_IA.md`.

---

## Sesión 2026-09-14 (tarde) — Victor Uria — Claude Code (Claude Opus 5)

**Contexto:** auditoría de `notebooks/base_2.ipynb`, notebook de modelo base hecho a mano por el
equipo como alternativa a `base.ipynb` (que resultó demasiado técnico). Sólo lectura: **no se
modificó el notebook** ni ningún dato.

### Prompt 1
> Claude. para empezar esta sesion quiero que leas el claude.md y el handoff.md para tener un mejor contexto de todo.
> Hice un nuevo notebook a mano llamado "base_2.ipynb". ya que el notebook "base.ipynb" no me convencio, tiene demasiado tecnisismo y se graficaron cosas las cuales no entendi muy bien. Por eso ahora te pido una auditoria de el nuevo notebook. "base_2.ipynb"

**Respuesta (extracto relevante):**

Hallazgos, en orden de gravedad:

1. **El notebook no corre hoy.** `data/processed/panel_zona_top.csv` fue sobrescrito a las 13:00 del
   2026-09-14, después de la corrida (12:45), con separador `;` y fechas `dd/mm/aaaa` (formato de
   Excel en español). `pd.read_csv(..., index_col=0)` ya no lo lee; `base.ipynb` tampoco. Los otros
   CSV de `data/processed/` siguen con el formato del ETL (2026-09-07).
2. **El `.venv` quedó con pandas 2.3.3**: `skforecast 0.25` exige `pandas<3` y el `!pip install`
   lo bajó. La celda de versiones imprime 3.0.5 porque el kernel lo había importado antes.
   `requirements.txt` fija 3.0.5 y `skforecast` no figura.
3. **No hay línea base.** El MAE de 2,65 no tiene contra qué compararse. Sobre los mismos 7 días:
   media constante 1,754; tasa × calendario 1,556; naive t−7 1,714. El árbol es el peor.
4. **Se evalúa sobre 7 días de 329.** Repetido sobre todo el test (47 semanas, sin reentrenar): árbol
   `max_depth=15` MAE 2,206; `max_depth=4` 1,772; `max_depth=2` 1,738; media constante 1,741;
   **tasa × calendario 1,592**. El MAE semanal del árbol va de 0,88 a 3,86; le gana a la línea base
   en 8 de 47 semanas.
5. **El árbol memoriza:** profundidad 15, 527 hojas para 1.309 filas; el 46,8 % de sus predicciones
   del test son enteros exactos (hojas de una sola observación). Predice 8 un sábado cuya media de
   entrenamiento es 2,5.
6. **El modelo sólo ve rezagos (`lags=7`)**, sin calendario, que es la señal principal según el
   diagnóstico.
7. **El análisis exploratorio mira el test**: descomposición, ACF y PACF sobre la serie completa (ACF
   a rezago 1: 0,079 con todo, 0,056 sólo con entrenamiento).
8. Restos del ejemplo del curso: «bicicletas alquiladas» en el eje Y de la figura, `cnt`, «demanda»,
   «Colab»; partición repetida (celdas 4 y 11); imports sin uso; cero celdas markdown; sin artefactos
   en `experiments/`; sin documento acompañante; métricas distintas de las fijadas en `base.ipynb`
   (falta la desvianza de Poisson).

**Uso y verificación:** informe entregado al equipo; ningún archivo del proyecto modificado salvo
este registro y `HANDOFF.md`. Verificado así:

1. Se reprodujeron las predicciones y métricas del notebook en un script aparte con el mismo `.venv`:
   predicciones `[3, 3,469, 8, 3, 6, 1, 3]`, MAE 2,647 y RMSE 3,387, idénticas a las salidas guardadas.
2. Para leer el CSV actual se usó `sep=";"` y `format="%d/%m/%Y"`, con un control: todos los días
   no feriados marcados `fin_semana` caen en sábado o domingo (resultado `True`). Los valores
   coinciden con las primeras filas que muestra el notebook.
3. Las líneas base sobre todo el test coinciden con `experiments/base/tablas/06_evaluacion_test.csv`
   (desvianza 1,085 y 1,262; MAE 1,592 y 1,741): la comparación es consistente entre notebooks.
4. Fechas de modificación con `stat`; versiones con `import` en el `.venv`; restricción de pandas en
   la salida de `pip` guardada en el propio notebook.
5. `git show HEAD`: la versión commiteada tenía `max_depth=5`. Sobre los 7 días, `max_depth` 3, 5, 10,
   15 y sin límite dan MAE 1,657, 1,653, 1,571, 2,647 y 2,000: el 15 no minimiza el error del test,
   así que no hay indicio de ajuste mirando el test, pero la elección queda sin justificar.
6. Figuras extraídas de las salidas del notebook y revisadas una por una.

**Archivos afectados:** `documentacion/registro_uso_IA.md`, `HANDOFF.md`.

### Prompt 2
> Perfecto, apliquemos esos tres cambios en el notebook y hay que generar el resumen del notebook

*(Los «tres cambios» son los recomendados al final de la respuesta anterior: agregar la línea base
del promedio por tipo de día, evaluar sobre todo el conjunto de prueba con una tabla comparativa, y
agregar celdas de texto que expliquen cada resultado.)*

**Respuesta (extracto relevante):**

1. **Restauración del CSV.** `panel_zona_top.csv` se reconstruyó desde `panel_diario_montevideo.csv`
   (salida del ETL del 2026-09-07), filtrando MUNICIPIO C y exportando con `to_csv(index=False,
   lineterminator="\r\n")`, sin reejecutar el ETL.
2. **Notebook reconstruido** con un script `nbformat` (no versionado). Se conservaron el código, los
   gráficos y la configuración del equipo (`max_depth=15`, `lags=7`), con estos cambios:
   - Línea base «promedio por tipo de día» y dos referencias, todas calculadas solo con entrenamiento.
   - Evaluación semana a semana sobre las 47 semanas de prueba, sin reentrenar:
     ```python
     posicion = serie_completa.index.get_loc(fechas[0])
     ultimos_dias = serie_completa.iloc[posicion - forecaster.window_size:posicion]
     pred = forecaster.predict(steps=len(fechas), last_window=ultimos_dias)
     ```
   - Análisis exploratorio (descomposición, ACF, PACF) solo con entrenamiento.
   - Tamaño del árbol, efecto de cada día de la semana y control cruzado contra
     `experiments/base/tablas/06_evaluacion_test.csv`.
   - 12 tablas y 10 figuras en `experiments/base_2/`.
   - 23 celdas markdown: explicaciones, lecturas con cifras y conclusiones que separan evidencia de
     inferencia.
   - Limpieza de los restos del ejemplo del curso («bicicletas alquiladas», `cnt`, «Colab»).
3. **Resultado en el test completo** (`08_test_metricas`): línea base MAE 1,592; media constante
   1,741; árbol 2,206 (+38,6 %); repetir semana anterior 2,228. El árbol supera a la línea base en 8
   de 47 semanas (`10_test_variabilidad_semanal`).
4. **`documentacion/resumen_base_2.md`** con la estructura de la convención de notebooks, incluida
   la lista de frases que no deben aparecer en el informe.

**Uso y verificación:** utilizado; **las lecturas y conclusiones están pendientes de validación del
equipo** (señalado en el resumen y en `HANDOFF.md`). Verificaciones:

1. **CSV:** el mismo procedimiento aplicado a MUNICIPIO A reproduce **byte a byte**
   `panel_zona_contraste.csv`. El archivo restaurado, leído con formato ISO, es igual (`DataFrame.equals`)
   al que había guardado Excel leído con `sep=";"` y `%d/%m/%Y`: 1.645 filas y 5.783 siniestros.
   Respaldos de ambos archivos en el scratchpad de la sesión.
2. **Ejecución:** dos corridas completas con `jupyter nbconvert --execute --inplace` en el `.venv`,
   con 0 errores. En la segunda, 0 salidas por stderr (en la primera había 47 `DeprecationWarning` de
   aritmética con `Timedelta`, corregidas). Todas las celdas de código ejecutadas en orden (1 a 26).
3. **Estabilidad entre corridas:** `cmp` de las tablas de la primera y la segunda corrida. Solo
   cambiaron `00_entorno` (fecha), `01_particion` (columna agregada) y `04_tamano_arbol` (formato).
4. **Control cruzado dentro del notebook:** línea base MAE 1,5920 contra 1,5919 en `base.ipynb`;
   media constante 1,7410 contra 1,7411.
5. **Coherencia con la auditoría:** las métricas coinciden con las del script independiente de la
   consulta anterior (MAE del árbol 2,206; media constante 1,741; línea base 1,592).
6. **Lecturas:** cada cifra de las celdas markdown y del resumen se tomó de las salidas y tablas de
   la segunda corrida. Las figuras 3 a 10 se revisaron visualmente antes de describirlas. El
   script verificó que no quedara ninguna celda con el marcador de lectura pendiente.

**Archivos afectados:** `notebooks/base_2.ipynb`, `experiments/base_2/` (nuevo: 12 tablas, 10
figuras), `documentacion/resumen_base_2.md` (nuevo), `data/processed/panel_zona_top.csv` (restaurado,
no versionado), `HANDOFF.md`, `documentacion/registro_uso_IA.md`.

---

## Sesión 2026-09-14 (segunda) — Juan Lucas Pimentel Barreto — Claude Code (Anthropic, Claude Sonnet 5)

**Contexto:** el equipo pidió un nuevo diagnóstico, limitado al municipio con más siniestros
(Municipio C), tomando `diagnostico_datos.ipynb` como referencia pero con adiciones que ese
notebook no tiene: gráficos de tendencia, estacionalidad (diaria/semanal/anual), ACF/PACF y
dispersión por rezago; y, a partir de esos gráficos, la decisión de si corresponde diferenciar o
transformar (logaritmo/Box-Cox) el objetivo. Claude creó el notebook, lo ejecutó de punta a punta
y escribió su documento acompañante.

### Prompt 1

> Claude, necesito hacer otro diagnostico de los datos, pero limitado solo al Municipio con mas
> siniestros (Municipio C). Toma como referencia el notebook "diagnostico_datos.ipynb" pero
> necesito que hagas algunas adiciones.
>
> Adiciones:
> [ ]Gráficos exploratorios: ¿Se analizaron patrones de tendencia, estacionalidad
> (diaria/semanal/anual), autocorrelación (ACF/PACF) y dispersión por lags?
>
> A partir de los graficos de ACF y PACF
> [ ] Transformaciones del objetivo: Se deberian aplicar diferencias o transformaciones
> logarítmicas/Box-Cox para estabilizar la varianza/tendencia?
>
> Lee el claude.md y comencemos.

**Respuesta (extracto relevante):** antes de escribir una sola cifra, Claude verificó que
`data/raw/` estaba vacío en esta máquina (sin CSV de siniestros ni capa de municipios) y, en vez de
simular datos, ubicó el CSV original en `C:\Users\Lucas\Downloads\uru_siniestros_unificado.csv` y
confirmó por `sha256` que es el mismo archivo que documenta `resumen_diagnostico_datos.md`
(`48a8a7e8…`); volvió a descargar la capa de municipios con la misma consulta WFS documentada. Con
eso, construyó `notebooks/diagnostico_datos_municipio.ipynb` (47 celdas, vía `nbformat`) con:

- Recorte heredado (Montevideo, desde 2021-07-01) y asignación a municipios reimplementada con
  `geopandas` (independiente de la implementación manual del notebook principal), verificada contra
  las ocho cifras de `resumen_diagnostico_datos.md` §4.2 (coincidencia exacta, con `assert`).
- Serie diaria de Municipio C: media 3,5155, dispersión 1,260, 4,80 % de días en cero.
- Tendencia (media móvil 30/90 d y media anual), estacionalidad semanal (perfil por día) y anual
  (índice mensual + `seasonal_decompose`), ACF/PACF crudas y del residuo tras descontar calendario,
  dispersión por rezago (scatter k=1,7,14,30).
- Diagnóstico de transformación: ADF (rechaza raíz unitaria, `p≈5×10⁻¹⁰`) vs. KPSS (rechaza
  estacionariedad, `p≤0,01`); diferenciar d=1 vuelve la ACF fuertemente negativa en rezago 1
  (sobrediferenciación); relación media-varianza mensual lineal, no cuadrática; λ de Box-Cox
  estimado por MLE ≈ 0,47 (cerca de raíz cuadrada, lejos de logaritmo). **Conclusión: no
  corresponde diferenciar ni transformar con log/Box-Cox el objetivo**, consistente con tratarlo
  como conteo (Poisson/binomial negativa), la familia que el diagnóstico principal ya recomienda.

**Uso y verificación:**

1. **Integridad del dato de entrada:** el CSV encontrado se verificó por `sha256` completo (no
   sólo tamaño) contra el valor documentado antes de usarlo.
2. **Verificación cruzada de la asignación espacial:** implementación independiente (`geopandas`
   vs. `matplotlib.path` del notebook principal) con `assert` en el propio notebook que detiene la
   ejecución si alguna de las ocho cifras no coincide.
3. **Ejecución completa** con `jupyter nbconvert --execute --inplace`: 0 errores, 47 celdas, 16
   tablas y 7 figuras generadas y verificadas contra sus valores en el notebook resultante (no se
   citó ninguna cifra sin confirmarla en el CSV correspondiente).
4. **Corrección de un desliz de redacción** («meaningfully» en una celda markdown) detectado al
   revisar el notebook exportado y corregido antes de darlo por cerrado.
5. La interpretación de la sección de transformaciones (adaptada al pie de las cuatro pruebas
   estadísticas) **queda pendiente de validación del equipo**, como toda inferencia redactada por
   Claude en este proyecto.

**Archivos afectados:** `notebooks/diagnostico_datos_municipio.ipynb` (nuevo),
`experiments/diagnostico_datos_municipio/` (nuevo, 16 tablas + 7 figuras),
`documentacion/resumen_diagnostico_datos_municipio.md` (nuevo), `HANDOFF.md`,
`documentacion/registro_uso_IA.md`. `data/raw/uru_siniestros_unificado.csv` y
`data/raw/municipios_montevideo.geojson` se restauraron localmente para poder ejecutar el
notebook; ambos quedan fuera de git por `.gitignore` (`data/raw/`).

---

## Sesión 2026-09-15 — Victor Uria — Claude Code (Anthropic, Claude Opus 5)

**Contexto:** ajuste de `notebooks/base_2.ipynb` para que no repita lo que ya hace
`notebooks/diagnostico_datos_municipio.ipynb` y para que ningún modelo use variables exógenas en esta
entrega. Se reejecutó el notebook y se reescribió su documento acompañante.

### Prompt 1
> Lee el claude.md para que tengas un mejor contexto.
> Claude, en el notebook "base_2.ipynb" entrenamos los primeros modelos. Pero hay coss las cuales ajustar. Se repiten informaciones del "diagnostico_datos_municipio.ipynb" y se estan utilizando la variable exogena "tipo_dia".
> Lo que quiero que hagas es lo siguiente:
> - Arregla el notebook para que no se repita lo mismo que en el diagnostico de datos
> - Que los modelos no utilicen ningun tipo de variables exogenas. Las vamos a utilizar mas adelante pero no para esta entrega

### Prompt 2 (enviado mientras se trabajaba en el anterior)
> Necesito que el codigo sea sencillo. que se pueda entender. Sigue la misma estructura de codigo que ya esta en el notebook

**Respuesta (extracto relevante, ambos prompts):**

1. **Diagnóstico.** Repetían el diagnóstico la §2 (serie completa), la §4 (descomposición y patrón
   semanal) y la §5 (ACF y PACF). El árbol ya usaba solo rezagos: `tipo_dia` lo usaba la **línea
   base** («promedio por tipo de día»). En la copia local había un cambio del equipo sin commitear ni
   ejecutar, `lags=[1, 7, 14, 21]`, que se respetó.
2. **Cambios**, con un script `nbformat` que conserva las celdas del equipo por id (no versionado):
   - Se eliminaron las tres secciones repetidas. En su lugar, una §2 **solo de texto**: una tabla con
     los resultados del diagnóstico que usa el modelo, cada uno con su tabla de
     `experiments/diagnostico_datos_municipio/`.
   - El CSV se lee con `usecols=["fecha", "zona_id", "n_siniestros"]`.
   - Línea base nueva, sin exógenas, **fijada antes de la primera ejecución**:
     ```python
     promedio_4_semanas = (serie_completa.shift(7) + serie_completa.shift(14)
                           + serie_completa.shift(21) + serie_completa.shift(28)) / 4
     ```
     Justificación: usa solo la serie; recoge el patrón semanal; promedia el ruido de una sola
     semana; sigue los cambios de nivel. Referencias: media constante y repetir semana anterior.
   - El control cruzado con `base.ipynb` quedó solo para la media constante, porque la línea base de
     ese notebook usa calendario.
   - Artefactos renumerados (8 tablas y 4 figuras); los 22 anteriores se borraron antes de ejecutar.
   - Por el Prompt 2 no se agregaron mecanismos nuevos: se descartó meter en el notebook una
     comprobación automática contra el diagnóstico y una tabla de variables por modelo. La
     coincidencia con el diagnóstico se verificó fuera del notebook.
3. **Resultados en todo el test** (`05_test_metricas`): media constante MAE 1,741; **línea base
   1,755**; árbol 2,137 (+21,8 %); repetir semana anterior 2,228. Totales predicho / observado: 0,884,
   0,981, 0,967 y 0,996. El árbol tiene 716 hojas para 1.295 filas.
4. **Advertencias entregadas:**
   - La línea base no es la referencia de menor MAE (la media constante le gana por 0,8 %). No se
     cambia, porque sería elegir con el test.
   - Los rezagos se apoyan en una ACF calculada con la serie completa: es una fuga leve.
   - `base.ipynb` usa calendario.

**Uso y verificación:** utilizado. **Lecturas, conclusiones y elección de la línea base pendientes
de validación del equipo.** Verificaciones:

1. **Ejecución:** `jupyter nbconvert --execute --inplace` en el `.venv`: 0 errores y 0 salidas por
   stderr; las 21 celdas de código se ejecutaron en orden. `nbformat.validate` sin errores.
2. **Sin exógenas:** la salida del notebook muestra que las variables del árbol son `lag_1`,
   `lag_7`, `lag_14` y `lag_21`, con `exog_in_ = False`. Una búsqueda en el notebook no encuentra
   `tipo_dia` en ninguna celda de código (solo en dos celdas de texto que lo explican).
3. **Misma serie que el diagnóstico:** script aparte sobre `panel_zona_top.csv`: 1.645 días, 5.783
   siniestros, 79 ceros, máximo 13 y media 3,5155. Coincide con
   `diagnostico_datos_municipio/tablas/04_resumen_serie_municipio_c.csv`.
4. **Control cruzado:** media constante MAE 1,7410 contra 1,7411 en `base.ipynb`, **OK**.
5. **Protocolo sin cambios:** con `git show 6fbb3ca` se comprobó que la media constante (1,741) y
   repetir semana anterior (2,228) dan lo mismo que en la versión anterior. Las cifras superadas que
   cita el resumen (1,592; 2,206; 527 hojas; ACF 0,056) se leyeron del mismo commit.
6. **Cifras del diagnóstico:** leídas de sus CSV (`05`, `06`, `08`, `09`, `12`, `13`, `14`), no del
   resumen.
7. **Lecturas:** cada cifra se tomó de las tablas de esta corrida; las cuatro figuras se revisaron
   visualmente antes de describirlas. El script de lecturas verifica que no quede ningún marcador
   pendiente.

**Archivos afectados:** `notebooks/base_2.ipynb`, `experiments/base_2/` (8 tablas y 4 figuras
nuevas; 22 artefactos anteriores borrados), `documentacion/resumen_base_2.md` (reescrito),
`HANDOFF.md`, `documentacion/registro_uso_IA.md`.

### Prompt 3
> Bien. Necesito que hagas lo siguiente.
> Vamos a utilizar estas metricas para evaluar nuestros modelos:
> 1. Métrica Principal
> Desvianza de Poisson media (Mean Poisson Deviance): Es la función de pérdida y métrica principal adoptada para la selección y comparación de modelos
> . Es la medida idónea para variables de conteo, ya que pondera el error en función del nivel esperado del conteo.
> Se utiliza la metrica principal que menciona el informe?, Si no se esta utilizando, agregala.

*(El prompt se envió dos veces por una interrupción; el texto es el mismo.)*

### Prompt 4 (enviado mientras se trabajaba en el anterior)
> Hablamos de el informe del proyecto, actualmente no esta en el repo

**Respuesta (extracto relevante, prompts 3 y 4):**

1. **No se usaba.** `base_2.ipynb` tenía el MAE como métrica principal, y el notebook y su resumen
   decían explícitamente que no calculaban la desvianza de Poisson. `base.ipynb` sí la usa. Como el
   informe no está en el repositorio, se tomó como referencia la definición del prompt.
2. **Se agregó** con el mismo cálculo que `base.ipynb`, para que las cifras sean comparables:
   ```python
   EPS = 1e-6

   def calcular_metricas(real, prediccion):
       return {
           "desvianza_poisson": mean_poisson_deviance(real, prediccion.clip(lower=EPS)),
           "MAE": mean_absolute_error(real, prediccion),
           ...
   ```
   Se hizo con scripts `nbformat` que reemplazan texto exacto en las celdas existentes (no
   versionados):
   - Las tablas quedaron ordenadas por desvianza, con la diferencia porcentual contra la línea base.
   - La variabilidad semanal y la figura 4 pasaron a desvianza.
   - El control cruzado con `base.ipynb` compara la desvianza y el MAE.
   - Se agregaron la columna `dias_con_prediccion_cero` y una celda de una línea que lista los días
     en que el árbol predijo 0.
3. **Resultados** (`05_test_metricas`): desvianza de la media constante 1,262; de la línea base
   1,332; del árbol 3,462 (+159,9 %); de repetir semana anterior 5,007. El árbol predijo 0 en 7 días,
   5 de ellos con siniestros, y esas semanas son sus picos de desvianza. En la primera semana el árbol
   tenía la menor desvianza (0,957).
4. **Advertencias entregadas:**
   - La media constante supera a la línea base por 5,2 % con la métrica principal. No se cambia la
     línea base, porque sería elegir con el test.
   - La desvianza de los modelos que predicen 0 depende de `EPS`.

**Uso y verificación:** utilizado; lecturas pendientes de validación del equipo. Verificaciones:

1. **Ejecución:** tres corridas con `jupyter nbconvert --execute --inplace` (métrica, columna de
   ceros y celda nueva): 0 errores, 0 salidas por stderr, celdas ejecutadas en orden;
   `nbformat.validate` sin errores.
2. **Control cruzado:** media constante, desvianza 1,2620 contra 1,2625 y MAE 1,7410 contra 1,7411
   en `experiments/base/tablas/06_evaluacion_test.csv`, **OK**. También se contrastó el cálculo con
   la función `evaluar` de `base.ipynb` (`np.clip(..., EPS, None)` con `EPS = 1e-6`).
3. **El recorte no altera las demás métricas:** MAE, RMSE y totales de `05_test_metricas` son iguales
   a los de la corrida anterior de la misma sesión.
4. **Réplica independiente** (script aparte con el mismo `.venv`): el árbol vuelve a dar desvianza
   3,4625 y 7 días con predicción 0 (2025-02-16, 02-27, 06-22, 07-24, 08-03, 08-31 y 09-07; 5 con
   siniestros), en las semanas 4, 20, 25, 26 y 31, que son sus cinco semanas con desvianza > 9 en
   `06_test_semanal`. La misma réplica da desvianza 2,0521 sin esos 7 días (322 días): es solo una
   comprobación de que «buena parte» es correcto, no se cita en ningún documento. La celda nueva del
   notebook muestra los mismos 7 días.
5. **Lecturas:** cifras tomadas de `04`, `05`, `06` y `07`; la figura 4 nueva se revisó visualmente.

**Archivos afectados:** `notebooks/base_2.ipynb`, `experiments/base_2/tablas/` (`04` a `07`
regeneradas), `experiments/base_2/figuras/fig4_test_desvianza_semanal.png` (reemplaza a
`fig4_test_mae_semanal.png`), `documentacion/resumen_base_2.md`, `HANDOFF.md`,
`documentacion/registro_uso_IA.md`.
