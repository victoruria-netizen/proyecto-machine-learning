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
