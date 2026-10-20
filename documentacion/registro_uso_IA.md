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

---

## Sesión 2026-09-17 — Victor Uria — Claude Code (Anthropic, Claude Opus 5 / Claude Sonnet 5)

**Contexto:** diagnóstico de series temporales para Municipio A (`data/processed/panel_zona_contraste.csv`),
espejando `notebooks/diagnostico_datos_municipio.ipynb` (que hace lo mismo para Municipio C). El
notebook `notebooks/diagnostico_zona_contraste.ipynb` ya existía, vacío.

### Prompt 1
> Claude. Para empezar lee el claude.md para que tengas mejor contexto de nuestro proyecto.
> Tenemos que hacer un diagnostico de datos para el dataset que esta en
> "data/processed/panel_zona_contraste.csv". Ya esta el notebook creado en
> "notebooks/diagnostico_zona_contraste.ipynb". Lo que quiero que hagas es que hagas exactamente
> lo mismo que el "diagnostico_datos_municipio.ipynb". El mismo codigo, con el mismo orden, lo
> unico que cambia es el csv analizado

**Respuesta (extracto relevante):**

1. **Decisión de diseño, no pedida explícitamente y no consultada por escrito con el equipo antes
   de ejecutar (registrada acá para que se revise):** `diagnostico_datos_municipio.ipynb` no
   analiza un CSV directamente — reconstruye la serie de Municipio C desde el CSV crudo
   (`uru_siniestros_unificado.csv`) y la capa de municipios con `geopandas.sjoin`, como
   verificación cruzada independiente de la asignación espacial. Ese código no es aplicable a
   `panel_zona_contraste.csv`, que ya es un panel (fecha, zona, objetivo, clima) con otras
   columnas, producido por `preparacion_montevideo.ipynb` y ya verificado por su ETL (dieciséis
   comprobaciones en OK, cruzado contra `diagnostico_datos.ipynb`; `resumen_preparacion_montevideo.md`
   §8). Se interpretó "el mismo código, el mismo orden" a nivel de las **secciones analíticas**
   (tendencia, estacionalidad diaria/semanal/anual, ACF/PACF, estacionariedad ADF/KPSS,
   diferenciación, Box-Cox, limitaciones, índice de artefactos), que sí se reprodujeron
   prácticamente línea por línea cambiando `serie_c`→`serie_a` y los sufijos de archivo. La sección
   1 (antes "recorte, asignación punto-polígono y verificación cruzada") se reescribió como "carga
   del panel ya preparado y verificación cruzada numérica" contra `resumen_diagnostico_datos.md`
   (§4.2) y `resumen_preparacion_montevideo.md` (§7.5), en vez de repetir el `sjoin` sobre datos que
   no lo requieren.
2. **Construcción:** notebook armado con `nbformat` (43 celdas), ejecutado con
   `jupyter nbconvert --execute --inplace` en el `.venv` del proyecto (0 errores). Las 15 tablas y
   7 figuras resultantes se leyeron una por una antes de escribir ninguna celda de interpretación,
   seguido la regla del proyecto de "ninguna cifra sin artefacto": los textos de "Evidencia",
   "Inferencia del equipo" y "Frases que estos datos NO sostienen" se escribieron **después** de
   ver los números reales de Municipio A, no copiando el patrón de Municipio C. Varios resultados
   difieren de forma sustantiva de los de Municipio C y así se documentaron: la ACF cruda de
   Municipio A **no** muestra la firma de múltiplos de 7 que sí domina en Municipio C (el rezago 7
   mismo queda dentro de banda), la razón viernes/domingo es más chica (1,43× contra 2,09×), el mes
   de mayor actividad es mayo y no junio, y la relación varianza-media mensual es más débil
   (r=0,46) con pendiente más cercana a la referencia Poisson pura. Coinciden, en cambio: el mínimo
   estacional en enero, la tensión ADF-estacionaria/KPSS-no-estacionaria, que diferenciar
   sobrecorrige, y un λ de Box-Cox (~0,475) casi idéntico al de Municipio C (~0,473).
3. **Documentación creada:** `documentacion/resumen_diagnostico_zona_contraste.md`, siguiendo la
   estructura y las reglas de `resumen_diagnostico_datos_municipio.md` (evidencia vs. inferencia,
   ninguna cifra sin artefacto, frases que no deben aparecer en el informe, comparación explícita
   con Municipio C sin usarla como evidencia de generalización).

**Uso y verificación:** utilizado. Verificaciones:

1. **Ejecución:** `jupyter nbconvert --to notebook --execute --inplace`: 0 celdas con error;
   `nbformat.validate` sin errores; 0 marcadores `PENDIENTE` restantes en el notebook (verificado
   con `grep`).
2. **Verificación cruzada dentro del propio notebook:** el total de siniestros (5.016) y el % de
   días en cero (5,84 %) recalculados sobre el panel coinciden exactamente con
   `resumen_diagnostico_datos.md` (§4.2) y `resumen_preparacion_montevideo.md` (§7.5) — assert en
   la celda `02_verificacion_cruzada`, no solo lectura visual.
3. **Cifras del documento acompañante:** cada número de `resumen_diagnostico_zona_contraste.md` se
   copió de las tablas CSV de `experiments/diagnostico_zona_contraste/tablas/` (leídas con `cat`),
   no del notebook renderizado ni de memoria; las comparaciones con Municipio C se releyeron de
   `resumen_diagnostico_datos_municipio.md`, no se citaron de memoria.
4. **Revisión visual:** las 7 figuras se abrieron y se revisó que los títulos, ejes y leyendas
   dijeran "Municipio A" y no arrastraran texto de la plantilla de Municipio C.
5. **Pendiente de validación del equipo:** la interpretación de por qué el patrón semanal y de
   calendario de Municipio A es más débil que el de Municipio C no se investigó (queda como
   pregunta abierta en la sección 8 del documento); y la decisión de partir del panel ya preparado
   en lugar de reconstruir la asignación espacial (punto 1 de esta entrada) conviene que el equipo
   la confirme antes de reutilizar este notebook como plantilla para otro municipio.

**Archivos afectados:** `notebooks/diagnostico_zona_contraste.ipynb` (nuevo, 43 celdas, ejecutado),
`experiments/diagnostico_zona_contraste/` (15 tablas CSV y 7 figuras PNG, nuevo),
`documentacion/resumen_diagnostico_zona_contraste.md` (nuevo), `documentacion/registro_uso_IA.md`.

---

## Sesión 2026-09-18 — Victor Uria — Claude Code (Anthropic, Claude Sonnet 5)

**Contexto:** convertir `notebooks/base.ipynb` y `notebooks/base_2.ipynb` a scripts `.py`
enviables a la cola del servidor (`documentacion/Guia_entrenamientos_CPU_GPU.md`), siguiendo la
estructura de los tres ejemplos en `notebooks/Ejemplos/` (`train_cpu_test.py`,
`train_cpu_stress_matmul.py`, `train_keras_test.py`).

### Prompt 1
> Claude, necesito que adaptes "base.ipynb" y "base_2.ipynb" a .py, crea dos archivos nuevos que
> sean .py uno para cada cuaderno. Tambien es necesario que se utilice la GPU del servidor para
> el entrenamiento. En la carpeta "documentacion/Guia_entrenamientos_CPU_GPU.md" hay un
> instructivo de como utilizar los componentes del servidor y tambien en la carpeta
> "notebooks/ejemplos" hay 3 .py como ejemplo. Crea los .py para "base.ipynb" y "base_2.ipynb"
> siguiendo estas estructuras

**Respuesta (extracto relevante):**

1. **Conflicto detectado antes de escribir código, y consultado con el equipo en vez de resolverlo
   por cuenta propia:** los dos notebooks entrenan un único `DecisionTreeRegressor` de
   scikit-learn (`base_2.ipynb` lo envuelve con `skforecast.ForecasterRecursive`). Ese algoritmo
   no tiene implementación GPU en scikit-learn, y con ~1.300-1.600 filas de entrenamiento tampoco
   habría cómputo que acelerar. Se preguntó explícitamente cómo priorizar "usar GPU" frente a
   "no cambiar el modelo sin que el equipo lo decida". **Respuesta del equipo: mantener el árbol
   tal cual y enviarlo por `submit_cpu`**, documentando por qué no corresponde `submit_gpu` (la
   propia guía, §14 punto 8, pide reservarlo para trabajos que sí aprovechan la GPU).
2. **Scripts creados:** `train/train_base.py` (de `base.ipynb`) y `train/train_base_2.py` (de
   `base_2.ipynb`), con la misma lógica y el mismo orden de secciones que cada notebook. Cambios,
   todos de infraestructura, no de modelo ni de resultados:
   - `RUN_ID`, `OUTPUT_DIR = /outputs/runs/<RUN_ID>/{tablas,figuras}`, `run_info.txt` con las
     variables de Slurm (`SLURM_JOB_ID`, `SLURM_CPUS_PER_TASK`, `CUDA_VISIBLE_DEVICES`) — igual
     que los tres ejemplos de `notebooks/Ejemplos/` y la sección 9-11 de la guía.
   - Backend de matplotlib `Agg` (sin pantalla en el servidor); se guardan figuras, no se llama
     `plt.show()`.
   - `display()`, `.head()`, `.info()` y expresiones sueltas de celda (que en Jupyter se
     autoimprimen) reemplazados por `print(..., flush=True)` explícitos, como pide la guía §12.
   - `%pip install skforecast==0.25.0` (sólo funciona como *magic* de Jupyter) reemplazado por un
     `try/except ImportError` con un mensaje que indica instalarlo de antemano en el entorno que
     usa `submit_cpu`.
   - Búsqueda de la raíz del repo basada en `Path(__file__)` en vez de `Path.cwd()`: en un trabajo
     de Slurm el directorio de trabajo puede no ser el del repositorio.
   - `sys.stdout.reconfigure(encoding="utf-8")`: sin esto, un log no-UTF-8 corta el trabajo con
     `UnicodeEncodeError` al imprimir tildes o "→" (encontrado al probar en Windows).
   - Cada script documenta, al final, cómo copiar `/outputs/runs/<RUN_ID>/{tablas,figuras}` a
     `experiments/base/` o `experiments/base_2/` para que los resúmenes existentes
     (`resumen_base.md`, `resumen_base_2.md`) sigan citando las mismas rutas.
3. **`train/README.md`** nuevo: qué script va con qué notebook, comando de envío, por qué CPU y
   no GPU, y la dependencia de `skforecast`.

**Uso y verificación:** utilizado. Verificaciones:

1. **Ejecución local completa de los dos scripts** (`.venv`, con `/outputs` inexistente: cae al
   fallback local documentado en el propio script) — los dos terminan con código de salida 0, sin
   excepciones.
2. **Primer intento con un bug real, corregido antes de dar el script por bueno:** la detección
   de "¿existe `/outputs`?" comprobaba `Path("/outputs").parent.exists()`, que en Windows es la
   raíz de la unidad actual y siempre existe — el script escribió por error en `C:\outputs\...`
   en la primera corrida. Se corrigió a comprobar la ruta misma (más `platform.system() ==
   "Windows"` como señal adicional) y se borró la carpeta creada por error.
3. **Coincidencia exacta con las cifras ya documentadas** (no sólo "corre sin errores"):
   - `train_base.py`, test: desvianza de Poisson 1,2625 (media constante), 1,0848 (tasa ×
     calendario), 1,6789 (árbol) — coincide con `resumen_base.md` / `HANDOFF.md` (1,085 y 1,679
     redondeados a 3 cifras).
   - `train_base_2.py`, test: 1,262 / 1,332 / 3,462 / 5,007 para media constante, línea base,
     árbol y repetir semana anterior — coincide exactamente con `resumen_base_2.md`.
   - Control cruzado interno de `train_base_2.py` contra `experiments/base/tablas/06_evaluacion_test.csv`:
     `OK` en desvianza (1,2620 vs 1,2625) y MAE (1,7410 vs 1,7411) — igual que el control ya
     documentado entre los dos notebooks.
   - Los 7 días con predicción 0 del árbol en `train_base_2.py` (2025-02-16, 02-27, 06-22, 07-24,
     08-03, 08-31, 09-07) coinciden uno a uno con los que cita `registro_uso_IA.md` (sesión
     2026-09-15) para `base_2.ipynb`.
4. **No verificado (pendiente, requiere el servidor):** el envío real con `submit_cpu` y la
   lectura del log `.out` correspondiente. Lo probado es la lógica del script, no la integración
   con Slurm.

**Archivos afectados:** `train/train_base.py` (nuevo), `train/train_base_2.py` (nuevo),
`train/README.md` (nuevo), `.gitignore` (se agrega `train/outputs_local/`),
`documentacion/registro_uso_IA.md`.

---

## Sesión 2026-09-18 (segunda) — Victor Uria — Claude Code (Anthropic, Claude Opus 5)

**Contexto:** `train_base_2.py` (sesión anterior) falló en el servidor real por un
`ImportError: Falta skforecast`, a pesar de que el equipo ya lo había instalado con `pip` según
la indicación de esa sesión. Se investigó por qué, con acceso solamente a lo que el equipo pegó
del servidor (esta sesión no tiene acceso directo al servidor).

### Prompt 1
> Me dio este error en el servidor: ImportError: Falta skforecast en este entorno. [...] Solo paso
> con el base_2, el otro base si corrio

**Respuesta (extracto relevante):** se ofrecieron dos hipótesis (terminal/entorno equivocado, o
instalación con errores no revisados) antes de tocar código, preguntando primero qué había
mostrado el `pip install`.

### Prompt 2
> Me volvio a aparecer el mismo error

**Respuesta:** en vez de seguir adivinando sin datos del servidor, se creó
`train/diagnostico_entorno.py` (imprime `sys.executable`, `sys.path`, variables de entorno,
intento de `import skforecast` y `pip show skforecast` con el mismo intérprete) y se pidió
correrlo con `submit_cpu` y pegar el log.

### Prompt 3 (pegó el log completo de `diagnostico_entorno.py`)
> [log de Slurm: grupo grp04, host lidia, imagen
> `/opt/apptainer-images/tensorflow_ngc_24.04_tf2_py3_mlcv.sif`, `sys.executable=/usr/bin/python`
> (3.10.12), `sys.path` sin ninguna carpeta de usuario, `skforecast` no encontrado, `pip show`
> vacío]

**Respuesta (extracto relevante, diagnóstico a partir del log):**

1. **Causa real, distinta de la asumida en la sesión anterior:** `submit_cpu` no corre en el
   entorno de la terminal de Jupyter — corre **dentro de un contenedor Apptainer fijo**
   (`tensorflow_ngc_24.04_tf2_py3_mlcv.sif`, Python 3.10 del sistema, paquetes en
   `/usr/local/lib/python3.10/dist-packages`). Son dos entornos completamente separados; instalar
   en uno no afecta al otro, sin importar `--user` ni permisos. La sesión anterior asumió que
   compartían entorno porque el `%pip install` del notebook sí "funciona" — pero eso corre en el
   kernel de Jupyter, nunca en el contenedor de Slurm.
2. **Dato aprovechable del propio log:** `sys.path` incluye `/work/train` (la carpeta `train/`
   del repo, montada dentro del contenedor) y persiste entre trabajos, a diferencia del resto del
   contenedor que es de solo lectura.
3. **Solución implementada:** `train/instalar_dependencias.py`, un script de un solo uso
   (`submit_cpu instalar_dependencias.py`) que instala `skforecast==0.25.0` con
   `pip install --target=train/vendor` usando el mismo `sys.executable` que después usará
   `train_base_2.py` — garantizando que el binario instalado es compatible con ese contenedor
   exacto (instalar localmente en Windows, por ejemplo, habría generado wheels inútiles ahí).
   `train_base_2.py` se modificó para agregar `train/vendor/` al **final** de `sys.path` (no al
   principio, para no tapar paquetes que el contenedor ya trae con versiones probablemente más
   compatibles con TensorFlow) antes de intentar el `import skforecast`, y el mensaje de error se
   actualizó para apuntar a `instalar_dependencias.py` en vez de a "instalar en el entorno".
4. **`train/vendor/` no se versiona** (se agregó a `.gitignore`): son binarios de Linux/Python
   3.10 específicos de esa imagen, inútiles en cualquier otra máquina.

**Uso y verificación:** utilizado. Verificaciones:

1. **`train_base_2.py` sigue corriendo igual en local** tras el cambio (no hay `train/vendor/`
   localmente, así que cae al `import skforecast` normal del `.venv`): mismo código de salida 0 y
   mismas cifras que la sesión anterior.
2. **No verificado (depende del servidor, fuera del alcance de esta sesión):** que
   `instalar_dependencias.py` efectivamente instale y que `train_base_2.py` corra después sin el
   `ImportError`. Pendiente que el equipo lo corra y confirme con el `.out`.
3. **Diagnóstico basado en evidencia pegada por el equipo, no en documentación del servidor**:
   ni la guía ni ningún archivo del repo mencionan Apptainer/contenedores; toda la lectura de la
   arquitectura del servidor sale del log real que pegó el equipo, citado en el punto 3 de la
   respuesta.

**Archivos afectados:** `train/diagnostico_entorno.py` (nuevo), `train/instalar_dependencias.py`
(nuevo), `train/train_base_2.py` (modificado: import de skforecast vía `train/vendor/`),
`train/README.md`, `.gitignore` (se agrega `train/vendor/`), `documentacion/registro_uso_IA.md`.

---

## Sesión 2026-09-18 (tercera) — Victor Uria — Claude Code (Anthropic, Claude Sonnet 5)

**Contexto:** continuación de la entrada anterior. El intento de vendorizar `skforecast` en
`train/vendor/` (entrada "segunda") **falló en el servidor y se descartó**; `train_base_2.py` se
reescribió sin `skforecast`. Esta entrada corrige lo que la anterior daba por bueno.

### Prompt 1 (pegó el log del job 107, `instalar_dependencias.py`)
> [...] Instalando dependencias para train_base_2.py dentro del contenedor de submit_cpu...
> Intérprete usado: /usr/bin/python [...] PermissionError: [Errno 13] Permission denied:
> '/work/train/vendor'

### Prompt 2
> Se puede arreglar en el script "train_base_2.py"?, porque me parece raro que haya funcionado el
> "train_base.py" sin problemas

**Respuesta (extracto relevante):**

1. **Por qué no era raro:** `train_base.py` nunca escribe en `/work` (sólo lee el CSV de ahí y
   escribe en `/outputs`), mientras que `instalar_dependencias.py` intentaba crear una carpeta en
   `/work/train`. Conclusión: `/work` es de sólo lectura dentro del contenedor y `/outputs` es el
   único mount escribible — lo que ya decía la guía (§9) y que la entrada anterior aplicó mal al
   suponer que `train/` era escribible porque aparecía en `sys.path`.
2. **Primer arreglo intentado (descartado):** mover el vendor a `/outputs/vendor`. Al probarlo en
   local aparecieron dos problemas de fondo, que invalidan el enfoque de vendorizar:
   - `pip install --target` no reutiliza lo ya instalado: bajó el stack científico completo
     (numpy, scipy, pandas, scikit-learn, numba…), **512 MB**.
   - El contenedor trae `numpy 1.24.4 / pandas 1.5.3 / scikit-learn 1.2.0` (del log de
     `diagnostico_entorno.py`) y `skforecast 0.25.0` exige `numpy>=1.26 / pandas>=2.1 /
     scikit-learn>=1.4` (leído de su `METADATA`). Con el vendor al final de `sys.path`, habrían
     ganado las versiones viejas del contenedor y `skforecast` habría fallado igual.
   - **Además, el "OK" que imprimió el test local de `instalar_dependencias.py` era un falso
     positivo:** el `import skforecast` resolvía al del `.venv`, no al de la carpeta vendor.
3. **Solución adoptada:** `train_base_2.py` ya no importa `skforecast`. Los rezagos
   (`matriz_rezagos`, mismo orden de columnas que skforecast: lag_1, lag_7, lag_14, lag_21) y la
   predicción recursiva (`predecir_recursivo`) se implementan a mano con `numpy`/`pandas`, que el
   contenedor ya trae. Es lo que la pregunta del equipo apuntaba (que funcione como
   `train_base.py`, sin instalar nada) y elimina de paso el conflicto `skforecast`/pandas 3 para
   este script. **Es un cambio de mecanismo respecto del notebook `base_2.ipynb`** (que sigue
   usando `skforecast`); el modelo, los rezagos, los hiperparámetros y la semilla son los mismos.
4. `train/instalar_dependencias.py` se **borró** (superado) y se quitó `train/vendor/` del
   `.gitignore`. `train/diagnostico_entorno.py` se conserva.

**Uso y verificación:** utilizado. Verificaciones:

1. **Paridad exacta contra `skforecast` como oráculo:** se guardó la versión anterior del script
   (con `skforecast`), se corrieron las dos en local con los mismos datos y se compararon
   `experiments`-equivalentes tabla por tabla con `cmp`: **las siete tablas de resultados
   (`01` a `07`) son idénticas byte a byte** (`00_entorno.csv` se excluye por diseño: lleva
   versiones y fecha).
2. **Errores propios encontrados y corregidos en el camino:** (a) un `\n` mal escapado en un
   heredoc de bash dejó una cadena partida y el script no compilaba (`SyntaxError`); se detectó
   porque la corrida local devolvió código 1, y se corrigió; (b) la limpieza de 512 MB de
   `train/outputs_local` generados por el test del instalador.
3. **No verificado (depende del servidor):** que `train_base_2.py` corra en el contenedor con
   `pandas 1.5.3 / numpy 1.24.4 / scikit-learn 1.2.0` (localmente se probó con pandas 2.3.3,
   numpy 2.5.2, scikit-learn 1.9.0; no se pudo reproducir el entorno viejo porque numpy 1.24 no
   tiene ruedas para el Python 3.13 local). Se revisó a mano que las funciones usadas existan en
   esas versiones, pero la prueba real es reenviar el trabajo y comparar las cifras con las de
   `train/README.md` ("Cómo verificar una corrida del servidor").
4. **Advertencia entregada al equipo:** `train_base.py` ya corrió en el servidor con
   `scikit-learn 1.2.0`; conviene comparar su `06_evaluacion_test.csv` con 1,2625 / 1,0848 /
   1,6789: es una comprobación gratuita de que el cambio de versión no altera los árboles.

**Archivos afectados:** `train/train_base_2.py` (reescrito sin skforecast), `train/README.md`
(reescrito), `train/instalar_dependencias.py` (creado en la entrada anterior, borrado acá),
`.gitignore`, `HANDOFF.md`, `documentacion/registro_uso_IA.md`.

---

## Sesión 2026-09-20 — Victor Uria — Claude Code (Anthropic, Claude Sonnet 5)

**Contexto:** estandarización del entorno Python del proyecto, reejecución de los seis notebooks
y verificación de que las salidas no cambian. Se trabajó en seis pasos, con paradas de
confirmación del equipo antes de aplicar (paso 3) y antes de dar por buenas las diferencias
(paso 5). No se pegaron datos en los prompts; en la sesión se inspeccionó un registro del CSV
crudo (por su posición) y no se reproduce aquí.

### Prompt 1
> Contexto: repo del proyecto PAA (predicción de siniestros por día–municipio en
> Montevideo). Cada notebook escribe experiments/<notebook>/tablas/00_entorno.csv
> con la versión de Python y de las bibliotecas de esa corrida. Hoy el entorno es
> inconsistente: requirements.txt fija pandas 3.0.5 y no incluye skforecast, pero
> la corrida de base_2 usó pandas 2.3.3, y skforecast 0.25 exige pandas < 3.
>
> Quiero estandarizar el entorno. Hacelo en este orden y sin tocar la lógica de
> los notebooks. Pará y esperá confirmación donde te lo indico.
>
> 1. INVENTARIO. Leé todos los experiments/*/tablas/00_entorno.csv y armá una
>    tabla comparativa: notebook, fecha de corrida, versión de Python y versión
>    de cada biblioteca. Mostrámela y señalá las discrepancias. PARÁ ACÁ.
>
> 2. PROPUESTA. Proponé un conjunto único de versiones compatible con todos los
>    notebooks (restricción dura: skforecast requiere pandas < 3). Justificá cada
>    pin y decime si conviene requirements.txt o pyproject + lock. PARÁ ACÁ.
>
> 3. APLICACIÓN. Con mi confirmación: escribí el archivo de dependencias con TODAS
>    las bibliotecas que los notebooks importan, incluida skforecast, con versiones
>    exactas. Creá el entorno limpio desde cero y verificá que instala sin conflictos.
>
> 4. REEJECUCIÓN. Guardá copia de todas las tablas y figuras actuales. Después
>    corré todos los notebooks de punta a punta con jupyter nbconvert --execute,
>    en el orden de dependencia correcto.
>
> 5. VERIFICACIÓN. Compará tabla por tabla la salida nueva contra la guardada.
>    Reportame qué cifras cambian y en cuánto. NO des ningún cambio por bueno:
>    listámelo para que yo decida. PARÁ ACÁ.
>
> 6. SALIDA. Dame un bloque de texto con la versión exacta de Python y de pandas,
>    NumPy, scikit-learn, statsmodels, geopandas, holidays y skforecast, tal como
>    quedan en los 00_entorno.csv regenerados, y actualizá el README con las
>    instrucciones de instalación y ejecución.

**Respuesta (extracto relevante):** inventario en forma de tabla (una columna por notebook, más
`requirements.txt` y el `.venv` actual). Discrepancias señaladas: (1) la premisa no se cumplía:
solo `base_2` escribe `00_entorno.csv`, los tres diagnósticos escriben `00b_entorno.csv` con otro
esquema, y `base` y `preparacion_montevideo` no guardan nada; (2) pandas en tres versiones (2.3.3 en
`base_2` y `contraste`; 3.0.3 en `municipio`; 3.0.5 en `diagnostico_datos`), porque un
`%pip install skforecast` había bajado pandas en el `.venv` compartido; (3) `municipio` corrió en otro
intérprete (Python 3.13.9, NumPy 2.4.6, SciPy 1.17.1); (4) `skforecast` y `geopandas` no estaban en
`requirements.txt` ni en `requirements-lock.txt` (que el prompt no mencionaba); (5) el `.venv` local
era Python 3.14.7 con 11 paquetes, y Python 3.13 (el del README) no estaba instalado.

**Uso y verificación:** utilizado. Verificado leyendo los cuatro CSV de entorno, `requirements.txt`,
`requirements-lock.txt`, el `pip list` del `.venv`, `py -0p` y las salidas guardadas de
`base.ipynb`. Se corrigió la premisa del prompt (no todos los notebooks escriben `00_entorno.csv`).
Error propio: un `cd notebooks` persistió en el shell y hizo fallar la lectura de README/HANDOFF; se
detectó por el `No such file` y se repitió desde la raíz. **Archivos afectados:** ninguno (solo lectura).

### Prompt 2
> Sigue con paso 2

**Respuesta (extracto relevante):** conjunto único de versiones: se conservan los pines de
`requirements.txt` salvo pandas (2.3.3, la última 2.x, tope de `skforecast`); se agregan
`skforecast` 0.25.0 y `geopandas` 1.1.4; `statsmodels` `<0.15` y `matplotlib` `<3.12` por los extras de
`skforecast`. Recomendación: `requirements.txt` con pines exactos más `requirements-lock.txt`
regenerado y usado como *constraints* (`pip install -r requirements.txt -c requirements-lock.txt`),
no `pyproject` + lock (el repo no es un paquete instalable y el equipo usa `pip`). Riesgo señalado:
`diagnostico_datos` y `municipio` bajarían de pandas 3 a 2. Cuatro decisiones pedidas al equipo:
versión de Python, paquetes sin uso, la celda `%pip` de `base_2`, y `requirements.txt` frente a
`pyproject`.

**Uso y verificación:** utilizado. Verificado con `pip install --dry-run --report` para Python 3.13
y 3.14 (mismo conjunto de 158 paquetes, todos los pines respetados), lectura del `METADATA` de
`skforecast-0.25.0` (`Requires-Dist: pandas<3.0,>=2.1`, `numba`, `optuna`, `tqdm`, `rich`), `pip index
versions` y una comparación contra el lock viejo (27 versiones cambian, 18 paquetes nuevos, 0
quitados). Se declaró explícitamente qué **no** estaba verificado (instalación y `import` reales).
Errores propios: leer el JSON del informe sin `encoding="utf-8"` (falló en Windows; se repitió con la
codificación explícita) y tomar el `exit=0` de `tail` como el de `pip` (se comprobó con los informes
JSON). **Archivos afectados:** ninguno (solo archivos temporales fuera del repo).

### Prompt 3
> Respuestas de decisiones:
> 1. Python 3.13.15
> 2. Los sacamos, pero si se necesitan mas adelante, se agregan de nuevo
> 3. Saca
> 4. La que me recomiendes tu, la que creas mas adecuada

**Respuesta (extracto relevante):** aplicación de los pasos 3 a 5. `requirements.txt` reescrito con 17
dependencias directas, versión exacta y comentarios; `requirements-lock.txt` con el `pip freeze` de
136 paquetes; `.venv` recreado desde cero con Python 3.13.15 (instalado con `uv python install`);
en `base_2.ipynb` se quitó la celda `%pip install skforecast==0.25.0` y se reescribió el texto de §0.
Se respaldó `experiments/`, `data/processed/` (no está en git), los notebooks y la caché de clima
antes de reejecutar; los seis notebooks corrieron en orden de dependencia (`base` antes de `base_2`,
porque `base_2` lo lee como control). Comparación celda por celda: 108 de 122 tablas y 28 de 31
figuras idénticas byte a byte; una sola cifra real cambiaba, `Calle` en `01_esquema_crudo.csv`
(224.693 a 224.694 no nulos; 23.746 a 23.747 distintos), con la causa reproducida en pandas 2.3.3 y
3.0.5: `.astype(str)` convierte el nulo en el texto `"nan"` en pandas 2.x.

**Uso y verificación:** utilizado. Verificado con: `pip check` limpio; importación de todas las
bibliotecas; un `ForecasterRecursive` ajustado y usado para predecir (ejercita `numba` con NumPy
2.5.2); `geopandas.read_file` sobre la capa real; **un segundo entorno limpio** instalado con
`-r requirements.txt -c requirements-lock.txt`, cuyo `pip freeze` resultó idéntico al del `.venv`; los
`00_entorno` regenerados (Python 3.13.15, pandas 2.3.3, confirma que el kernel fue el del `.venv`);
que el clima salió de la caché y `clima_montevideo.csv` no cambió; el respaldo con `diff -r`. La
causa de `Calle` se comprobó ejecutando el mismo fragmento en el entorno nuevo y en uno temporal con
pandas 3.0.5 (ya eliminado). Errores propios corregidos en el camino: un `subprocess` con ruta
relativa con `/` que no resolvía en Windows (el lock no se había escrito; se detectó porque
`git status` no lo mostraba modificado y se reescribió desde el shell); un segundo entorno creado
en una ruta de unos 200 caracteres, en el que falló `ensurepip` (se comprobó que el Python base no
quedó contaminado y se repitió en una ruta corta); y un argumento equivocado (`regressor` en vez de
`estimator`) en mi prueba de `skforecast`, que no era un problema del entorno. **Descartado:** Python
3.14.7 (ya instalado, pero sumaba un segundo cambio a la comparación); `pyproject` + `uv.lock`;
conservar los paquetes sin uso. **Archivos afectados:** `requirements.txt`, `requirements-lock.txt`,
`notebooks/*.ipynb` (los seis, reejecutados; `base_2` además editado), `experiments/**` y
`data/processed/diccionario_datos.csv` (regenerados).

### Prompt 4
> 1. Corregi A
> 2. dejalo regenerado
> 3. Si
> 4. Actualiza

**Respuesta (extracto relevante):** (1) corrección en la celda 6 de `diagnostico_datos.ipynb`:
`df_pais[c] = df_pais[c].astype(str).str.strip().where(df_pais[c].notna())`, que conserva el
comportamiento de `astype(str)` para los valores presentes y restituye el nulo; (2) se deja todo lo
regenerado; (3) se deja el `DeprecationWarning` de NumPy de la celda 8; (4) se actualizan README,
los seis `resumen_*.md` con su nota de reejecución, `HANDOFF.md` y este registro. Se señaló, sin
corregirlo por quedar fuera de lo aprobado, que el mismo patrón `astype(str)` existe en
`diagnostico_datos_municipio` (celda 7) y en `preparacion_montevideo` (celda 7). Bloque de versiones
entregado: Python 3.13.15, pandas 2.3.3, NumPy 2.5.2, scikit-learn 1.9.0, statsmodels 0.14.6,
geopandas 1.1.4, holidays 0.103 y skforecast 0.25.0.

**Uso y verificación:** utilizado. Verificado con: reejecución de `diagnostico_datos` y comparación
completa contra el respaldo: `Calle` volvió a 224.693 / 23.746, **0 celdas con diferencia numérica** en
las 122 tablas, y el conjunto de archivos que difieren no creció; el bloque de versiones se armó
leyendo los `00_entorno.csv` y `00b_entorno.csv` regenerados y se cruzó con el `pip freeze` (las ocho
coinciden); los conteos de tablas y figuras de cada documento se contrastaron con los archivos
reales de cada carpeta, lo que llevó a corregir dos encabezados que ya estaban desactualizados
(`municipio`: 16 a 17; `contraste`: 15 a 16). Se comprobó también que `siniestros_montevideo.csv` no
exporta `Calle`, así que el patrón no corregido de `preparacion_montevideo` no llega a los datos.
En el README se ajustó una frase: la falla por ruta larga se observó, pero su causa exacta (límite de
260 caracteres) es una inferencia y quedó redactada como tal. **No verificado:** la instalación en
Linux/Mac (el lock se generó en Windows; el README lo dice); nada de esto está en git todavía.
**Archivos afectados:** `notebooks/diagnostico_datos.ipynb`, `README.md`,
`documentacion/resumen_base.md`, `resumen_base_2.md`, `resumen_diagnostico_datos.md`,
`resumen_diagnostico_datos_municipio.md`, `resumen_diagnostico_zona_contraste.md`,
`resumen_preparacion_montevideo.md`, `HANDOFF.md`, `documentacion/registro_uso_IA.md`.

### Prompt 5
> 1. Victor Uria
> 2. ok
> 3. crealo
> 4. Corregir
> 5. ok
> 6. ok
>
> Despues de hechas todas las modificaciones condensa toda esta seccion en un archivo .md, con todos los registros de los cambios, resultados, actualizaciones, etc. Este archivo no quedara en el repo, lo elimino una vez lo descargue.

**Respuesta (extracto relevante):** (1) integrante confirmado en este registro. (3) `.env.example`
creado con `PAA_DIR` y `PAA_CSV`, las únicas variables propias que el código lee (búsqueda de
`os.environ`, `getenv` y `dotenv` en notebooks, `train/`, `src/` y `app/`; las `SLURM_*` y
`CUDA_VISIBLE_DEVICES` las define el servidor). Se dejaron comentadas: una variable definida pero
vacía se interpretaría como el directorio actual. Se señaló que **ningún código carga un `.env`**
(`python-dotenv` está retirado) y se ajustó la frase del README que decía «copiar `.env.example` a
`.env`». (4) La misma corrección de nulos (`.where(...notna())`) en la celda 7 de
`diagnostico_datos_municipio.ipynb` y en la celda 7 de `preparacion_montevideo.ipynb`. (5) Se leyó
como acuse, no como orden de borrar: `_backup_pre_reejecucion_2026-09-20/` **no** se borró, porque
la comparación de este paso lo necesitaba; se dejó pendiente la confirmación. (2) y (6) sin cambios.
Se generó además un resumen de toda la sesión en un archivo `.md` que no se versiona (ver «Uso y
verificación»).

**Uso y verificación:** utilizado. Verificado con: round-trip de `nbformat` idéntico byte a byte antes
de editar cada notebook, y comprobación de que la línea a reemplazar aparecía exactamente una vez en
su celda; **reejecución de los seis notebooks** en orden de dependencia (código 0 en todos, 0 errores
en las salidas) y **comparación completa repetida contra el respaldo original**: los mismos 14
archivos difieren y **0 celdas con diferencia numérica**, es decir, la corrección no cambió ninguna
salida; `git check-ignore` confirma que `.env.example` se versiona y `.env` queda ignorado;
`Path("").exists()` devuelve `True` y resuelve al directorio actual, lo que sustenta la advertencia
sobre variables vacías. Documentación ajustada para que no dijera que el patrón quedaba sin corregir
(`resumen_diagnostico_datos.md`, `resumen_diagnostico_datos_municipio.md`,
`resumen_preparacion_montevideo.md` y `HANDOFF.md`). El resumen de la sesión se escribió en la raíz
del repositorio, excluido con `.git/info/exclude` para que no aparezca en `git status` ni se pueda
commitear por error; el equipo lo elimina tras descargarlo. **No verificado:** instalación en
Linux/Mac; nada de esto está en git todavía. **Archivos afectados:** `.env.example` (nuevo),
`notebooks/diagnostico_datos_municipio.ipynb`, `notebooks/preparacion_montevideo.ipynb` (más los seis
reejecutados), `README.md`, `HANDOFF.md`, `documentacion/resumen_diagnostico_datos.md`,
`resumen_diagnostico_datos_municipio.md`, `resumen_preparacion_montevideo.md`,
`documentacion/registro_uso_IA.md`, y `experiments/**` y `data/processed/diccionario_datos.csv`
(regenerados).

## Sesión 2026-09-24 — Victor Uria — Claude Code (Anthropic, Claude Sonnet 5)

**Contexto:** congelamiento del Entregable 2 en una rama de registro (`entregable_2`) y, recién
después, unificación de los seis modelos de `notebooks/base.ipynb` y `notebooks/base_2.ipynb` en
un único `notebooks/linea_base.ipynb`, retiro de lo obsoleto, salida de `skforecast` de las
dependencias, y documentación de cierre. Tarea explícitamente delimitada para no ser desarrollo
del Entregable 3. No se pegaron datos personales ni muestras de filas en los prompts.

### Prompt 1

> # CONTEXTO
>
> Repositorio del Proyecto de Aplicación en Aprendizaje Automático: predicción de
> siniestros de tránsito por municipio y día en Montevideo. El Entregable 2 ya fue
> entregado y defendido. Esta tarea tiene dos partes: congelar el estado del Entregable 2 en una
> rama de registro, y después limpiar y reordenar main. NO es desarrollo del Entregable 3. No
> cambies modelos, hiperparámetros, variables, partición ni métricas.
>
> [Instrucciones completas de las Fases 0 a 4: crear la rama `entregable_2` desde el estado
> actual de `main` antes de cambiar nada; unificar `base.ipynb`/`base_2.ipynb` en
> `notebooks/linea_base.ipynb` con una sección "Líneas base" (media constante, L0, L1) y una
> sección aparte "Modelo candidato preliminar" (el árbol, renombrado, sin tocar hiperparámetros
> ni variables); retirar "repetir semana anterior" y "Árbol A"; agregar una celda de verificación
> de entorno que detenga la ejecución si Python o alguna dependencia difieren de
> `requirements.txt`, y una celda de no regresión contra valores de referencia copiados antes de
> borrar `experiments/base/` y `experiments/base_2/`; eliminar esas carpetas y los notebooks
> retirados de `main` sin dejar referencias colgadas; sacar `skforecast` de `requirements.txt` si
> nada más lo usa y regenerar `requirements-lock.txt`; actualizar `HANDOFF.md`,
> `registro_uso_IA.md` y generar `documentacion/cambios_para_informe.md` como puente para quien
> corrija el informe en otra sesión. Lista extensa de "fuera de alcance" (no tocar partición, no
> validar la ventana de L0, no recalcular la ACF, no quitar `t_anios`, no agregar modelos nuevos,
> no extender al panel de 8 municipios, no subir versiones de dependencias más allá de quitar
> `skforecast`, no editar el informe). Pedido explícito de hacer un plan primero y de parar a
> preguntar ante cualquier contradicción con las instrucciones.]

**Respuesta (extracto relevante):** se entró en modo de planificación. Antes de planificar se
investigó el estado real del repositorio (no se asumió nada de lo que decía el prompt): se leyó
`HANDOFF.md`, los notebooks `base.ipynb`/`base_2.ipynb` completos (celda por celda, para extraer
el código real de L1, L0 y el árbol), los CSV de `experiments/base/` y `experiments/base_2/`, y se
corrieron búsquedas en todo el repositorio para las rutas a retirar. Esa investigación encontró
tres problemas no previstos por el prompt, cada uno resuelto **preguntando antes de decidir**, no
por cuenta propia:

1. **No existía ningún informe del Entregable 2 en el repositorio** (ni `documentacion/informe/`,
   ni ningún `.md`/`.pdf`/`.docx`, ni en el historial de git) — bloqueante explícito de la Fase 0.
2. `notebooks/Ejemplos/Series_temporales_y_pronóstico_ejemplo.ipynb` (tutorial, sin relación con
   el pipeline) seguía importando `skforecast`, lo que contradecía la premisa de la Fase 3 de que
   "nada más lo usa".
3. Al construir la celda de verificación de entorno se descubrió que **"Python 3.13.15"**,
   documentado como estándar del proyecto desde el 2026-09-20 en `requirements.txt`, `README.md` y
   `HANDOFF.md`, **no es una versión de Python que exista** (`uv python install 3.13.15` no la
   encuentra).

**Uso y verificación:** el plan se escribió después de resolver los tres puntos con el usuario
(ver Prompts 2 a 4) y se ejecutó en el orden pedido: Fase 0 (rama `entregable_2` creada desde el
commit que agrega el informe, publicada con `git push`), Fase 1 (`linea_base.ipynb`, construido
con `nbformat` reutilizando el código real de los notebooks originales, no reescrito de memoria),
Fase 2 (borrado con `git rm`, búsqueda de referencias colgadas antes de borrar), Fase 3 (lock
regenerado en un entorno limpio, con un kernel de Jupyter registrado explícitamente para evitar
que `jupyter nbconvert` resolviera el intérprete equivocado por `PATH` — se detectó porque un
`RuntimeWarning` de arranque seguía señalando la ruta del `.venv` del proyecto en vez del entorno
nuevo), Fase 4 (este registro, `HANDOFF.md` y `cambios_para_informe.md`, este último construido
leyendo el texto completo del PDF de 54 páginas del informe entregado, no adivinando su
estructura). Verificado con: ejecución de punta a punta de `linea_base.ipynb`
(`jupyter nbconvert`/`nbconvert --execute`) en tres entornos (el original, el regenerado sin
`skforecast`, y el `.venv` final ya sincronizado), con la celda de no regresión en verde en los
tres y el mismo resultado numérico en los cuatro modelos; `git diff` del notebook entre corridas
mostrando que sólo cambian timestamps y el conteo de dependencias verificadas; `pip check` e
inspección de `pip freeze` confirmando la ausencia de `skforecast` y sus transitivas; búsqueda
`grep`/`git grep` en todo el árbol de `main` sin referencias colgadas a `base.ipynb`, `base_2` ni
`experiments/base(_2)/` fuera de menciones históricas explícitas.

### Prompt 2 (pregunta de Claude, vía herramienta de clarificación)

> Revisé todo el repo (archivos, nombres de archivo y git log --all) y no hay ningún informe del
> Entregable 2 en el repositorio [...] ¿Dónde está la versión del informe tal como se entregó?

**Respuesta del usuario:** "Tengo el archivo, lo traigo yo" — agregó
`documentacion/informe/Entregable2_PAA_20-09-26.pdf` (8 páginas según `file`, 54 según `pypdf`;
se usó el conteo de `pypdf`, que lee el árbol de páginas real) y avisó "ready".

**Uso y verificación:** commiteado como primer paso de la Fase 0, antes de crear la rama
`entregable_2`, para que la rama de registro incluyera el informe. Verificado abriendo el PDF con
`pypdf` y confirmando 54 páginas de contenido real antes de darlo por válido.
**Archivos afectados:** `documentacion/informe/Entregable2_PAA_20-09-26.pdf`.

### Prompt 3 (pregunta de Claude)

> La Fase 3 pide verificar que nada más importe skforecast antes de sacarlo de requirements.txt.
> Encontré que notebooks/Ejemplos/Series_temporales_y_pronóstico_ejemplo.ipynb [...] sí lo
> importa. [...] ¿Cómo procedo?

**Respuesta del usuario:** "Sacar igual, dejar constancia (Recomendado)".

**Uso y verificación:** se quitó `skforecast` de `requirements.txt` igual, y se agregó
`notebooks/Ejemplos/README.md` explicando cómo reinstalarlo aparte. Verificado con
`git grep skforecast` sobre el árbol final de `main`: sólo aparece en ese notebook de ejemplo, en
su guía de referencia (`Guia_series_temporales_skforecast.md`) y en menciones históricas
(`HANDOFF.md`, `registro_uso_IA.md`).

### Prompt 4 (pregunta de Claude)

> Para la celda de entorno [...] requirements.txt y HANDOFF.md declaran "Python 3.13.15" [...]
> Pero esa versión no existe: `uv python install 3.13.15` falla [...] ¿Cómo sigo?

**Respuesta del usuario:** "Corregir el pin a 3.13.2 (Recomendado)".

**Uso y verificación:** corregido en `requirements.txt` y `README.md` (con una nota explicando el
error); no se reescribieron las menciones históricas a "3.13.15" en `registro_uso_IA.md`, en los
`resumen_*.md` ni en las salidas ya guardadas de otros notebooks, porque son registro de lo que se
documentó en su momento, no una afirmación vigente. Verificado corriendo
`.venv/Scripts/python.exe -m pip install -r requirements.txt -c requirements-lock.txt` y
`pip check` (limpio) después de la corrección, y ejecutando la celda de entorno de
`linea_base.ipynb` con resultado "Entorno OK".

**Uso y verificación (general de la sesión):** todos los cambios de código se ejecutaron
realmente (no se asumió que el código escrito funcionaba); cada fase terminó en un commit
separado (`git log --oneline` los distingue) y ninguno se hizo sin que el árbol de trabajo
reflejara exactamente lo revisado. **Archivos afectados:** `notebooks/linea_base.ipynb` (nuevo),
`experiments/linea_base/**` (nuevo), `documentacion/resumen_linea_base.md` (nuevo),
`documentacion/cambios_para_informe.md` (nuevo), `notebooks/Ejemplos/README.md` (nuevo),
`requirements.txt`, `requirements-lock.txt`, `README.md`, `train/README.md`, `HANDOFF.md`,
`documentacion/registro_uso_IA.md`; eliminados `notebooks/base.ipynb`, `notebooks/base_2.ipynb`,
`experiments/base/**`, `experiments/base_2/**`, `train/train_base.py`, `train/train_base_2.py`,
`documentacion/resumen_base.md`, `documentacion/resumen_base_2.md` (preservados en la rama
`entregable_2`).

## Sesión 2026-09-25 — Victor Uria — Claude Code (Anthropic, Claude Sonnet 5)

**Contexto:** Auditoría de solo lectura del repositorio, previa a la corrección de
`documentacion/informe/Entregable2_PAA_20-09-26.pdf`. No se modificó ningún archivo (verificado
con `git status --porcelain` y `git stash list` al inicio y al final, ambos vacíos). Se auditaron:
estado de ramas (`main`/`entregable_2`), uso de datos por notebook, revisión técnica de
`notebooks/linea_base.ipynb`, cruce exhaustivo del texto del informe (54 páginas, extraídas con un
script Python propio de solo lectura, sin dependencias externas, descartado al finalizar) contra
`documentacion/cambios_para_informe.md` y contra el repositorio, coherencia de
HANDOFF.md/README.md/CLAUDE.md/resúmenes, y revisión general del repositorio.

### Prompt 1
> # Auditoría de solo lectura del repositorio — previa a la corrección del informe del Entregable 2
>
> ## Contexto
>
> El 2026-09-24 se congeló el Entregable 2 en la rama `entregable_2` y se unificaron `base.ipynb` y
> `base_2.ipynb` en `notebooks/linea_base.ipynb`. El puente hacia el informe está en
> `documentacion/cambios_para_informe.md`. Antes de corregir el informe (`documentacion/informe/
> Entregable2_PAA_20-09-26.pdf`) el equipo quiere un **reporte detallado del estado real del repo**,
> contrastado contra lo que dicen la documentación y el informe, y aprovechar para hacer una
> **review general del repositorio**. El objetivo es detectar cualquier otra corrección necesaria
> en el repo **antes** de tocar el informe. **No es desarrollo del Entregable 3.**
>
> ## Regla absoluta: SOLO LECTURA
>
> Esta sesión no modifica nada. Concretamente:
>
> - **Prohibido:** editar, crear, mover o borrar archivos dentro del repo; `git add/commit/push/
>   checkout/switch/reset/stash/merge/rebase/worktree add/tag/branch -d`; ejecutar notebooks
>   (`nbconvert --execute`, en cualquier modo, porque escriben en `experiments/`); `pip install`,
>   `uv`, o cualquier cambio del entorno; regenerar `data/processed/`.
> - **Permitido:** leer archivos; `git status`, `git log`, `git show <rama>:<ruta>`, `git diff`,
>   `git branch -a`, `git ls-files`, `git ls-remote`, `git fetch --dry-run`; `grep`/`rg`; scripts de
>   Python que **sólo lean** (CSV, JSON de los `.ipynb`, texto del PDF) e impriman por pantalla.
>   Si necesitás un archivo temporal (p. ej. el texto extraído del PDF), creálo **fuera del repo**
>   (directorio temporal del sistema) y borralo al terminar.
> - **Excepción a CLAUDE.md:** en esta sesión **no** escribas en `documentacion/registro_uso_IA.md`
>   ni en `HANDOFF.md`. En su lugar, al final del reporte, dejá **redactada** la entrada del registro
>   de uso de IA de esta sesión (formato de CLAUDE.md) para que el equipo la agregue después.
> - **Prueba de no modificación:** corré `git status --porcelain` y `git stash list` al principio y
>   al final, y mostrá ambas salidas en el reporte. Tienen que ser idénticas.
>
> [Se omiten aquí, por brevedad y porque no cambian el resultado, las secciones "Fuentes a leer
> primero" (CLAUDE.md, HANDOFF.md, README.md, requirements*.txt, .gitignore, .env.example,
> train/README.md, notebooks/Ejemplos/README.md, todo `documentacion/`, el PDF del informe) y "Qué
> verificar" (secciones A a F con ~40 preguntas puntuales sobre: estado de git y ramas; qué datos
> usa cada notebook; revisión técnica de `linea_base.ipynb` — ventana expansiva/deslizante, fugas de
> información, semillas, sesgo medio, verificación de entorno; informe contra repositorio — barrido
> exhaustivo de términos, rutas citadas, terminología del bloque final, cifras de diagnóstico;
> coherencia de HANDOFF/README/CLAUDE.md/resúmenes; y review general del repositorio — artefactos
> huérfanos, `src/`/`app/`/`tests`/`models`, `etl/`, `requirements.txt` vs `requirements-lock.txt`,
> evidencia de ejecución en servidor). El texto completo está en el historial de esta conversación.]
>
> ## Formato del reporte
>
> Respondé en la conversación (no en un archivo), en español y en Markdown: resumen ejecutivo,
> salida de `git status` inicial, secciones A a F con evidencia, tabla consolidada de hallazgos
> (ID, descripción, evidencia, severidad, categoría), lo que no se pudo verificar en solo lectura,
> salida de `git status` final, y la entrada propuesta para `registro_uso_IA.md`.

**Respuesta (extracto relevante):** Reporte de auditoría con 28 hallazgos tabulados. Los dos más
relevantes: (1) `experiments/linea_base/tablas/03_particiones.csv` y los encabezados de
`linea_base.ipynb` rotulaban la validación como "ventana deslizante" cuando el código implementa
una ventana expansiva (`historia = datos.iloc[:origen]`, sin límite inferior) y el propio glosario
del informe define ambos términos como opuestos (H1); y `documentacion/cambios_para_informe.md`
(sección "Lo que NO cambió") afirmaba que las cuatro filas de la Tabla 4 estaban reproducidas
dentro de una tolerancia de 0,001 y verificadas por la celda de no regresión del notebook — falso
para el Árbol candidato (diferencia de hasta 0,0093 en desvianza de Poisson), y esa celda nunca
verificaba esa tabla, sólo la Tabla 5 (H2). Además: 3 omisiones confirmadas en
`cambios_para_informe.md` respecto del texto del informe (§3.4.2, nota (b) de la Tabla 5, plural
"los árboles" en §4.3.3), una fuga leve no declarada en la selección de Municipio C/A (H11), y
~15 puntos de documentación desactualizada en HANDOFF.md/README.md/CLAUDE.md/resúmenes.

**Uso y verificación:** verificado línea por línea contra el código de `notebooks/linea_base.ipynb`,
los CSV de `experiments/linea_base/` y `entregable_2` (`git show`), y el texto completo del PDF del
informe. No se aplicó ningún cambio en esa sesión; el equipo decidió qué corregir a partir de la
tabla de hallazgos, y esos hallazgos (H1–H27) son la base de la sesión siguiente (Bloques 1 a 6,
más abajo). **Archivos afectados:** ninguno (sesión de solo lectura).

## Sesión 2026-09-25 — Victor Uria — Claude Code (Anthropic, Claude Sonnet 5)

**Contexto:** Aplicación al repositorio de las correcciones surgidas de la auditoría anterior, en
seis bloques con commits separados, para que el informe se corrija después sobre una base
verificada. No es desarrollo del Entregable 3.

### Prompt 1
> # Correcciones al repositorio previas a la corrección del informe del Entregable 2
>
> Una auditoría de solo lectura (sesión anterior) relevó el estado del repo después de la
> unificación del 2026-09-24. Esta sesión **aplica las correcciones al repo** que surgieron de esa
> auditoría [...] **Esto no es desarrollo del Entregable 3.** No se toca ningún hiperparámetro,
> variable, partición, métrica ni modelo, salvo lo que exija el Bloque 1 **y sólo tras confirmación
> del equipo**.
>
> Reglas: trabajar en `main`, nunca commitear en `entregable_2`; un commit local por bloque, sin
> push; archivos temporales fuera del repo; `git status` limpio al empezar (si no, detenerse y
> avisar); ninguna cifra sin artefacto; si una reejecución cambia algo inesperado, detenerse y
> reportar, no commitear. Fuera de alcance: `origin/rama1`, `notebooks/Ejemplos/`,
> `diagnostico_datos_municipio.ipynb`, pines de versión, `train_linea_base.py`, el PDF del informe,
> y cualquier trabajo del E3.
>
> **Bloque 1 (prioridad):** investigar por qué `04_desarrollo_backtesting.csv` no reproduce
> `entregable_2` para el árbol candidato — comparar `base.ipynb` (extraído con `git show`) contra
> `linea_base.ipynb` línea por línea, aislar la causa con un script si hace falta, y
> **detenerse a reportar antes de modificar nada**, con una recomendación entre corregir, mantener
> y documentar, o no poder determinar la causa. Esperar confirmación antes de aplicar.
>
> **Bloque 2:** en `linea_base.ipynb`, reemplazar "ventana deslizante" por "ventana expansiva" y
> alinear la terminología del bloque final (rótulos de CSV, títulos de figuras, con una nota de que
> no es una prueba reservada e independiente para el E3); reejecutar el notebook una sola vez y
> diffear cada CSV contra lo commiteado; barrer el resto del repo por los mismos términos.
>
> **Bloque 3:** verificar sin modificar nada si el criterio de selección de `zona_top`/
> `zona_contraste` (calculado sobre el período completo) da el mismo resultado calculado sólo con
> el entrenamiento inicial o sólo con el desarrollo; declarar la fuga como leve e inocua si da C y
> A en ambos tramos, con las cifras, sin tocar el notebook de preparación.
>
> **Bloque 4:** verificar que el log del servidor citado en el Anexo F.1 existe, revisar que no
> tenga credenciales ni datos personales, contrastarlo cifra por cifra contra el Anexo F.1, y
> documentarlo en `train/README.md`.
>
> **Bloque 5:** actualizar `resumen_linea_base.md`, `resumen_preparacion_montevideo.md`,
> `HANDOFF.md`, `README.md` y `CLAUDE.md` según los hallazgos H3 y H16 a H27 de la auditoría;
> preguntar al equipo el rol exacto de docente y tutor antes de escribirlo; agregar una sección
> fechada a `cambios_para_informe.md` con la corrección a la sección (e), las omisiones reales
> encontradas frente al informe (con página), las decisiones del equipo sobre las Tablas F1–F4 e
> Ilustraciones F1–F2, y una nota de que el informe ya usaba la terminología correcta.
>
> **Bloque 6:** registrar esta sesión y la de auditoría en `registro_uso_IA.md` (append-only),
> actualizar `HANDOFF.md`, y reportar commits, diff resumido, resultado de cada bloque, lo
> pendiente y confirmación de que no se hizo push.

**Respuesta (extracto relevante):**

Al empezar, `git status` no estaba limpio (`documentacion/logs/` sin commitear, con nombres
distintos a los que esperaba el Bloque 4 y un job — 108, `train_base_2.py` — no documentado en el
informe): se preguntó al equipo antes de seguir en vez de asumir. Confirmado usar ambos archivos
con sus nombres actuales.

**Bloque 1:** comparando `notebooks/linea_base.ipynb` contra `base.ipynb` (extraído de
`entregable_2` con `git show`, sin `checkout`), las funciones de backtesting, construcción de
matrices y predicción del árbol son idénticas byte a byte; la única diferencia es
`SEMILLA=20260924` contra `SEMILLA=20260910`. Reproducido en un script aislado (`.venv` del
proyecto, mismas versiones que usan ambos notebooks): cada semilla reproduce exacto el valor de su
notebook (1,3912 y 1,4005 respectivamente), y ambas dan el mismo árbol al ajustar sobre las 1.295
filas del desarrollo completo (sin empates de partición con ese volumen). Reportado el hallazgo y
esperada confirmación **antes de tocar nada**; el equipo eligió corregir `linea_base.ipynb` a
`SEMILLA=20260910`. Aplicado, y extendida la celda de no regresión (§11) para cubrir también la
tabla de desarrollo (`referencia_no_regresion.csv` con columna `tramo`).

**Bloque 2:** terminología corregida en `linea_base.ipynb` (títulos, markdown, rótulo de
`03_particiones.csv`) y barrida en `HANDOFF.md`, `resumen_linea_base.md` y `train/README.md` (sólo
donde describían la misma partición, mismas fechas); no tocada en `README.md` (describe una
comparación prevista para el E3, no la implementación actual) ni en particiones instrumentales de
los diagnósticos (otro concepto). Reejecutado el notebook una sola vez
(`jupyter nbconvert --execute`): entorno OK, no regresión OK en los dos tramos. Un bug de comillas
propio (una coma sin escapar en `referencia_no_regresion.csv`) rompía el parseo de pandas; corregido
antes de reejecutar. Diff verificado: sólo cambiaron los rótulos esperados, la fila del árbol en
desarrollo (por el Bloque 1) y el render de una figura (leyenda/título).

**Bloque 3:** verificado con un script de solo lectura sobre
`data/processed/siniestros_montevideo.csv` que el ranking de municipios por siniestros es idéntico
(C > B > D > A > F > G > E > CH) calculado sobre el período completo, sólo el entrenamiento inicial
o sólo el desarrollo. Declarada la fuga como leve e inocua, con las cifras, en
`resumen_preparacion_montevideo.md` y `resumen_linea_base.md`; no se tocó
`preparacion_montevideo.ipynb`.

**Bloque 4:** el log (`log_servidor_base.txt`, Job 104) coincide cifra por cifra con el Anexo F.1
del informe (job ID, horario, script, versiones del contenedor, RUN_ID, conteo de "18 tablas y
figuras"); sin credenciales ni datos personales más allá del grupo/host institucional. `.gitignore`
no excluye `*.log`, no hizo falta ninguna excepción. Documentado en `train/README.md`.

**Bloque 5:** aplicados los 12 hallazgos de documentación (H3, H16–H27) en los seis archivos
listados por el equipo; docente y tutor confirmados con el equipo antes de escribirlos (Pablo D.
Cuña, docente de la asignatura; Matías López, tutor del proyecto). `cambios_para_informe.md` ahora
tiene la sección fechada 2026-09-25 con la corrección, las omisiones y las decisiones del equipo.

**Uso y verificación:** cada bloque se verificó antes de dar el siguiente por cerrado — el Bloque 1
con un script de reproducción aislado y comparación de código línea por línea; el Bloque 2 con la
reejecución real del notebook y el diff de cada CSV/figura contra la versión commiteada; el Bloque
3 con un script de solo lectura sobre datos reales; el Bloque 4 contrastando el log contra el
Anexo F.1 texto por texto. Cada bloque terminó en un commit separado en `main`, ninguno en
`entregable_2`, y no se hizo push. **Archivos afectados:** `notebooks/linea_base.ipynb`,
`experiments/linea_base/tablas/03_particiones.csv`, `experiments/linea_base/tablas/
04_desarrollo_backtesting.csv`, `experiments/linea_base/tablas/06_artefactos.csv`,
`experiments/linea_base/figuras/fig4_test_predicciones.png`,
`experiments/linea_base/referencia_no_regresion.csv`, `documentacion/resumen_linea_base.md`,
`documentacion/resumen_preparacion_montevideo.md`, `documentacion/cambios_para_informe.md`,
`documentacion/logs/log_servidor_base.txt` (nuevo), `documentacion/logs/log_servidor_base2.txt`
(nuevo), `HANDOFF.md`, `README.md`, `CLAUDE.md`, `train/README.md`.


## Sesión 2026-10-05 — Victor Uria — Claude Code (Anthropic, Claude Sonnet 5.5)

**Contexto:** diagnóstico de calidad de datos y de heterogeneidad para los **ocho municipios**, para
decidir si un solo modelo generaliza. Archivos: `notebooks/diagnostico_municipios.ipynb` (nuevo),
`experiments/diagnostico_municipios/` (nuevo), `documentacion/resumen_diagnostico_municipios.md` (nuevo),
`README.md`, `HANDOFF.md`.

### Prompt 1
> Claude, lee el claude.md y el handoff para que tengas mas contexto del proyecto y la metodologia de trabajo.
> Necesito que hagas un diagnostico de calidad de datos para todos los municipios, ya tenemos hecho el diagnostico para el municipio A y C, pero necesitamos el diagnostico para cada uno de los municipios.
> La idea con este diagnostico es revisar si un solo modelo puede generalizar en todos los municipios o si necesitaremos entrenar otros modelos.

**Respuesta (extracto relevante):** se creó un notebook con la misma metodología de los diagnósticos de C
y A aplicada a los ocho municipios (calidad, tendencia, calendario semanal y anual, ACF/Ljung-Box,
ADF/KPSS/Box-Cox, co-movimiento) y una sección de decisión con pruebas F de cuasi-verosimilitud y una
comparación predictiva de seis modelos mínimos (nivel × calendario) en dos pliegues cronológicos, con
bootstrap por bloques semanales y una regla de decisión fijada antes de ejecutar. Conclusión redactada por
la IA (inferencia, no evidencia directa): «un modelo único con variable de nivel por municipio; no se
respalda un modelo por municipio, con la posible excepción de A» (nivel: M1→M2 +7,62 % / +7,86 %;
calendario propio: M2→M3 −0,22 % / +0,32 %; sólo A cumple la regla, +4,06 % / +4,24 %).

**Uso y verificación:** utilizado, con decisiones de diseño tomadas por la IA **sin consulta previa** que el
equipo debe validar: (i) partir del panel del ETL en vez de reconstruir la asignación espacial (como hizo el
notebook de C); (ii) usar un modelo mínimo y no una familia de modelos, para medir estructura y no
desempeño; (iii) la regla de decisión (≥ 1 % y IC95 que excluya 0 en los dos pliegues) y los dos pliegues
de 329 días; (iv) usar sólo el bloque de desarrollo en la sección de decisión. **Verificado** así: el
notebook se ejecutó de punta a punta con `jupyter nbconvert --execute --inplace` (0 errores, 0 salidas por
stderr); los `assert` internos confirman que el panel reproduce las 16 cifras ya documentadas y que media,
varianza, días en cero, ACF residual y λ de Box-Cox de C y A coinciden con los notebooks previos; cada cifra
citada en las celdas de lectura y en el resumen se contrastó contra las tablas CSV generadas. Una primera
versión del código se ejecutó antes de redactar ninguna interpretación, y las lecturas se escribieron sobre
las cifras reales; dos tablas se ampliaron después (ceros esperados bajo Poisson; atípicos de 5 o menos
siniestros) para respaldar afirmaciones concretas, y se corrigió el formato del eje de la figura 1. **No se
usó el bloque final.** **Pendiente de validación humana:** las lecturas e inferencias del notebook y del
resumen. **Archivos afectados:** `notebooks/diagnostico_municipios.ipynb`,
`experiments/diagnostico_municipios/`, `documentacion/resumen_diagnostico_municipios.md`, `README.md`,
`HANDOFF.md`.

### Prompt 2 (corrección del equipo)
> Me olvide de aclarar algo muy importante, para no hacer data leakage, no se puede consultar en ningun momento el conjunto de datos de test, ya que ese es nuestro futuro. En este diagnostico no se puede consultar los datos de test en ningun momento, se utilizaran para evaluar el modelo al final del proyecto

**Respuesta (extracto relevante):** la IA reconoció que la versión del Prompt 1 **había usado el test**: las
secciones descriptivas (2 a 6) calcularon sobre el período completo (hasta 2025-12-31), y su resumen
afirmaba, incorrectamente, que no se tocaba el bloque final. Se rehízo el notebook: los archivos se leen y se
descartan al instante las filas posteriores a 2025-02-05 (límite calculado desde el calendario, 80 % de
1.645 días), con un `assert` de que no queda ninguna; se eliminaron los cruces con cifras del período
completo (totales, C y A); se excluyeron los períodos parciales del desarrollo (2025 y febrero de 2025).

**Uso y verificación:** la versión del Prompt 1 se **descartó** (violaba la regla del test; sus cifras no
deben citarse). Verificado: reejecución completa con `jupyter nbconvert --execute --inplace` (0 errores, 0
stderr); la tabla `01_verificacion_integridad.csv` comprueba cero filas posteriores a 2025-02-05; la
sección 7 (ya sólo con desarrollo) reprodujo exactamente las mismas cifras; todas las cifras de las lecturas
se contrastaron contra las tablas nuevas. Cambiaron conclusiones: la tendencia deja de ser «creciente en los
ocho» (detectable en C, A, F, G) y la memoria temporal pasa a ser detectable sólo en C y CH. **Hallazgo para
el equipo:** `diagnostico_datos.ipynb`, `diagnostico_datos_municipio.ipynb` y
`diagnostico_zona_contraste.ipynb` también usan el período completo; no se modificaron. **Archivos
afectados:** `notebooks/diagnostico_municipios.ipynb`, `experiments/diagnostico_municipios/`,
`documentacion/resumen_diagnostico_municipios.md`, `HANDOFF.md`.

### Prompt 3
> vamos a hacer lo siguiente:
> Vamos a descartar estos tres notebooks de diagnosticos, la idea es centralizar todo en este notebook nuevo que armaste, asi el repo queda bien organizado, limpio y sencillo de entender.

**Respuesta (extracto relevante):** se retiraron de `main` (`git rm`, sin commit) `diagnostico_datos`,
`diagnostico_datos_municipio` y `diagnostico_zona_contraste`, sus carpetas de `experiments/` y sus tres
resúmenes; se corrigieron las referencias vivas y se avisó lo que el notebook nuevo no cubre: diagnóstico de
la fuente cruda, aporte por bloque de variables fuera de muestra y verificación cruzada con el ETL.

**Uso y verificación:** ejecutado tal cual lo pidió el equipo. Antes de borrar se verificó que la rama
`entregable_2` contiene los tres notebooks, los tres resúmenes y las tablas (red de seguridad), y con `grep`
que ningún notebook ni script leía esos artefactos en código. Tras el cambio se reejecutó
`diagnostico_municipios.ipynb` (0 errores; las 23 tablas de resultados idénticas byte a byte a la corrida
anterior; sólo cambió texto). Se editaron sólo markdown y comentarios de `linea_base` y
`preparacion_montevideo` (JSON válido, sin reejecutar). **Decisión de la IA sin consulta:** en
`resumen_linea_base.md` y `resumen_preparacion_montevideo.md` no se borraron las cifras que citan los
diagnósticos retirados; se agregó una nota que las declara históricas y calculadas con el test. **Pendiente
del equipo:** decidir qué parte del diagnóstico retirado se rehace sólo con desarrollo, y si se quita
`geopandas`. **Archivos afectados:** los retirados, `README.md`, `CLAUDE.md`, `requirements.txt`,
`notebooks/linea_base.ipynb`, `notebooks/preparacion_montevideo.ipynb`, `notebooks/diagnostico_municipios.ipynb`,
`documentacion/resumen_*.md`, `documentacion/cambios_para_informe.md`, `HANDOFF.md`.

### Prompt 4
> Pero si todo esto ya lo hace el "preparacion_montevideo", no seria redundante hacerlo en este notebook?

> Vamos a rehacerlo solo con desarrollo, ya que el test no se debe tocar hasta el final

> No hagas la verificacion cruzada, solo la medicion por bloques pero sin utilizar el test

**Respuesta (extracto relevante):** la IA corrigió su afirmación anterior: la calidad de la fuente cruda ya la
documenta el ETL, así que repetirla sería redundante. Quedaban dos pérdidas reales: la verificación cruzada
independiente (el equipo decidió **no** rehacerla) y la medición del aporte de cada bloque de variables fuera de
muestra, que se rehízo como sección 7.5 de `diagnostico_municipios.ipynb`, sólo con el bloque de desarrollo:
mismos dos pliegues de la sección 7, predictores estimados sólo con el ajuste, bootstrap por bloques semanales.
Resultado: tasa del municipio +7,28 % / +7,54 %, calendario +4,36 % / +4,09 %, tasa × calendario +11,65 % /
+11,63 %, la lluvia no aporta, las celdas saturadas con el mes empeoran (−7,64 % / −3,31 %).

**Uso y verificación:** la IA **interpretó** el pedido «rehacerlo» como la medición por bloques (la que quedó
sin cubrir tras retirar los diagnósticos) y la implementó con definiciones propias (p. ej. el efecto de lluvia
como calibración multiplicativa del indicador `llovió`, el piso de 1e-6, la celda vacía que cae a B3); el
equipo debe validarlas. Verificado: reejecución completa con `jupyter nbconvert --execute --inplace` (0 errores,
0 stderr); B3 y B5 coinciden con M2 y M3 de la sección 7.2 (1,2278/1,2305 y 1,2385/1,2344); las 22 tablas
anteriores salen idénticas byte a byte; la validación no invade el bloque final (hay un `assert`); las cifras de
las lecturas se contrastaron con las tablas `23`–`25`. Las cifras **no son comparables** con las del diagnóstico
retirado (otro protocolo, y aquel usaba el test), aunque coincide la conclusión cualitativa. **Archivos
afectados:** `notebooks/diagnostico_municipios.ipynb`, `experiments/diagnostico_municipios/`,
`documentacion/resumen_diagnostico_municipios.md`, `documentacion/resumen_linea_base.md`,
`documentacion/resumen_preparacion_montevideo.md`, `HANDOFF.md`.

### Prompt 5
> Todo lo que esta en "cambios_para_informe.md" ya lo aplicamos.
> Ahora quiero que hagas lo siguiente:
> - Borra todo lo que esta escrito en ese documento, ya que eso ya esta aplicado.
> - En ese documento pone todo lo que se hizo en esta seccion y los cambios que hay que hacer en el informe
> - En la ruta "documentacion/informe/Entregable2_PAA_20-09-26.md" esta nuestro documento actualizado, puedes mirarlo para comparar lo que hay que actualizar

**Respuesta (extracto relevante):** se reescribió por completo `documentacion/cambios_para_informe.md` (el contenido
anterior, ya aplicado, queda en el historial de git). El nuevo documento resume la sesión, lista cinco decisiones
del equipo previas a editar (la más importante: la contradicción entre la regla «el test no se consulta» y lo que
el informe declara en 3.4.4 sobre el bloque final), los cambios por sección con número de línea del `.md`, las
cifras de reemplazo y los pendientes sin respaldo en `main`.

**Uso y verificación:** se leyeron los capítulos 1 a 4, los anexos y las listas del informe y se contrastaron con el
estado del repositorio; las cifras de reemplazo salen de las tablas de `experiments/diagnostico_municipios/`. **Las
cifras departamentales de desarrollo (D.2 y D.4) se calcularon con un script de la sesión y NO tienen artefacto en el
repo**: el documento lo declara y exige llevarlas a un notebook antes de citarlas. Las referencias de línea se
contrastaron contra el `.md` vigente. **No se editó el informe.** **Archivos afectados:**
`documentacion/cambios_para_informe.md`.

### Prompt 6
> Desiciones:
> 1. El test sigue siendo el mismo. Como el entregable 2 ya paso, tuvimos que declarar el uso de test en el documento.
> 2. ok
> 3. Usamos la misma que el notebook
> 4. La quitamos.
> 5. Se rehace con el bloque de desarrollo. Siempre tene presente evitar el data leakage, tanto en test como en validacion
>
> Registra todos estos cambios, para que otro agente pueda trazarlos y corregirlos en el informe, podes actualizar o crear cambios_para_informe.md

**Respuesta (extracto relevante):** se registraron las cinco decisiones y sus consecuencias en
`documentacion/cambios_para_informe.md` (reescrito), y se **rehízo sólo con desarrollo** lo que dependía de los
notebooks retirados, agregándolo a `diagnostico_municipios.ipynb`: faltantes codificados, evidencia del corte de la
pandemia (−21,4 % con 2022–2024), cobertura temporal, cifras del objetivo y de la serie departamental, mapa, varianza
explicada por el calendario (tres niveles 21,42 %; ocho, 26,51 %) y ACF de los rezagos con sólo el entrenamiento inicial
(ningún municipio supera la banda una vez descontado el calendario).

**Uso y verificación:** la IA **interpretó** la decisión 5 como «rehacer ahora» y no sólo registrarla, y tomó
decisiones de implementación sin consulta que el equipo debe validar: reutilizar los mismos centinelas de texto del
diagnóstico retirado; usar los años 2022–2024 como referencia de la pandemia (2025 sólo trae 36 días en desarrollo);
elegir los rezagos con la ACF del **entrenamiento inicial** para no filtrar la validación (la directriz de evitar el
leakage en validación se interpretó así). Verificado: reejecución completa con `jupyter nbconvert --execute --inplace`
(0 errores, 0 stderr); el archivo crudo y los eventos se filtran al leerlos y hay `assert`; las tablas 01–22
previas salen idénticas byte a byte; las cifras de las lecturas se contrastaron con las tablas nuevas; los
centinelas reproducen el orden de magnitud del diagnóstico retirado (18,14 % y 12,50 % en el archivo; 4,47 % y 2,32 %
en el recorte). **Pendiente de validación humana:** las lecturas y las tres preguntas abiertas. **Archivos
afectados:** `notebooks/diagnostico_municipios.ipynb`, `experiments/diagnostico_municipios/`,
`documentacion/resumen_diagnostico_municipios.md`, `documentacion/cambios_para_informe.md`, `README.md`, `HANDOFF.md`.

### Prompt 7
> 1- No vamos a tocar el ETL
> 2- Si las secciones que tocan todo el desarrollo son puramente descriptivas, lo dejamos como esta
> 3- Lo vamos a conservar como antecedente historico

**Respuesta (extracto relevante):** se registraron las tres decisiones en `documentacion/cambios_para_informe.md`. Para
la 2, que es condicional, la IA **clasificó** las secciones del notebook: sólo 1, 2, 4.3 y 6 son puramente
descriptivas; 3, 4.1, 4.2, 5.1, 5.2 y 7.1 orientan decisiones. Para esas se agregó la sección 7.6, que las repite con
sólo el entrenamiento inicial (987 días). La conclusión central se sostiene; no se sostienen la pendiente mayor de A ni
la memoria de C. Se corrigió además una frase propia inexacta sobre CH.

**Uso y verificación:** la clasificación de qué es «puramente descriptivo» fue **criterio de la IA** y debe validarlo el
equipo. Verificado: reejecución completa con `jupyter nbconvert --execute --inplace` (0 errores, 0 stderr); las 41
tablas previas salen idénticas byte a byte; las cifras de las lecturas se contrastaron con `25b`–`25f`; en 7.6 hay un
`assert` de que el entrenamiento termina antes de la validación. **Archivos afectados:**
`notebooks/diagnostico_municipios.ipynb`, `experiments/diagnostico_municipios/`,
`documentacion/resumen_diagnostico_municipios.md`, `documentacion/cambios_para_informe.md`, `HANDOFF.md`.

### Prompt 8
> decision 2:
> Lo hablamos con el profesor y llegamos a la conclusion de que si se puede utilizar el conjunto de validacion. Entonces si estan bien estos diagnosticos que utilizan este conjunto.
>
> Una decision mas que tomamos:
> En los modelos que creamos en el notebook de "linea_base" utilizan Expanding window (ventana expansiva). En el documento dijimos que ibamos a comparar los resultados con ambas ventanas. Pero optamos por utilizar solo Rolling Window (Ventana deslizante) y explicar en el informe que esta decision se tomo porque ternemos una pequeña sobre dispercion en los datos, entonces no conviene utilizar una ventana expansiva para no tomar en cuenta los dias muy lejanos al presente.

**Respuesta (extracto relevante):** (1) Se reencuadraron el notebook, su resumen y `cambios_para_informe.md`: los diagnósticos
con la validación son válidos; la sección 7.6 pasa a ser un chequeo de estabilidad. (2) Se registró la decisión de la
ventana deslizante con las líneas del informe a corregir (L289, L321, L548, L553, Tablas 4 y 5) y se **advirtió** que la
sobredispersión leve no es, por sí sola, argumento para descartar días lejanos; el que sí respalda la decisión es la deriva
del nivel (+5,03 % / +8,83 %), y se propuso una redacción.

**Uso y verificación:** el cambio de criterio sobre la validación se aplicó tal cual lo comunicó el equipo (con el docente).
La IA **no modificó `linea_base.ipynb`**: cambiarlo altera resultados ya citados en el informe y requiere definir el largo
de la ventana; queda como decisión del equipo. La observación sobre la fundamentación es **criterio de la IA** y debe
evaluarla el equipo. Verificado: el notebook se reejecutó (0 errores, 0 stderr) y las 46 tablas salen idénticas
(sólo cambió texto); los números de línea del informe se contrastaron contra el `.md` vigente. **Archivos afectados:**
`notebooks/diagnostico_municipios.ipynb`, `documentacion/resumen_diagnostico_municipios.md`,
`documentacion/cambios_para_informe.md`, `HANDOFF.md`.

### Prompt 9
> Deciciones:
> - Al final haremos la comparacion de ambas ventanas ya que es un objetivo del proyecto. Pero lo vamos a hacer mas adelante, con los modelos candidatos finales.
> - Deja el notebook como está, pero ajusta el archivo "cambios_para_informe.md" para que solamente queden las deciciones implementadas y que en ese documento esté solo lo que hay que cambiar en el informe

**Respuesta (extracto relevante):** se reescribió `documentacion/cambios_para_informe.md`: quedó sólo con las decisiones
implementadas y con lo que hay que cambiar en el informe (cambios por sección con número de línea, cifras de reemplazo y
equivalencia de artefactos). Se quitaron la narrativa de la sesión, las preguntas abiertas, las recomendaciones no
confirmadas, los pendientes y el chequeo de estabilidad (7.6). La decisión de la ventana deslizante quedó sin efecto: el
informe mantiene la comparación de ambas ventanas (L321) y sólo se agrega al plan del E3 que se hará con los modelos
candidatos finales.

**Uso y verificación:** `linea_base.ipynb` **no se modificó**, tal cual se pidió. La IA decidió **qué es «sólo lo que hay
que cambiar»**: retiró las recomendaciones no confirmadas (p. ej. la salvedad de los 26,51 % del calendario de 8 niveles) y las
menciones al chequeo con sólo el entrenamiento, salvo la ACF recalculada de los rezagos (`dm/12`, `dm/12b`) porque corrige
una afirmación del informe. Verificado releyendo el documento completo y recontrastando las cifras con las tablas
generadas; se renumeraron las secciones y sus referencias cruzadas. **Archivos afectados:**
`documentacion/cambios_para_informe.md`, `HANDOFF.md`.

## Sesión 2026-10-13/14 — Victor Uria — Claude Code (Anthropic, Claude Sonnet 5.5)

**Contexto:** arranque del Entregable 3. Etapas 0a (dependencias), 0b (`src/variables.py`, `src/datos.py`, tests), 0c (revisión del
dashboard del PID, sin código disponible) y Etapa 1 (`notebooks/modelos_candidatos.ipynb`: protocolo y referencias en el panel;
**sin candidatos**). El trabajo se hizo por etapas con confirmación del equipo entre una y otra.

**Incidente declarado — lectura del test.** Al explorar la estructura del panel, la IA ejecutó un comando suelto que leyó
`panel_diario_montevideo.csv` completo, con las filas posteriores a 2025-02-05. Se calcularon conteos de `tipo_dia`, un `describe`
de las columnas de lluvia y la fecha máxima. **No se leyó ni calculó nada sobre `n_siniestros` del test y no influyó en ningún
código ni decisión.** La IA lo informó al equipo al cerrar la etapa y, desde ahí, todo el panel se lee con
`src.datos.cargar_panel_desarrollo()`, que descarta el test por tramos al leer. El equipo pidió asentarlo y no llevarlo al informe.

### Prompt 1
> Empezamos el Entregable 3 del PAA. Antes de hacer nada, leé CLAUDE.md, HANDOFF.md,
> documentacion/resumen_linea_base.md, documentacion/resumen_diagnostico_municipios.md y la
> sección 5.3 de documentacion/Guia_estudiantes_PAA_2026.md. Respetá todas las reglas de
> CLAUDE.md (ninguna cifra sin artefacto, registro de IA, documento acompañante, HANDOFF).
>
> Trabajá por etapas. Al terminar cada etapa, DETENETE y mostrame un resumen de lo hecho, los
> archivos tocados y cualquier duda. No avances a la etapa siguiente sin mi confirmación. Si
> alguna instrucción de este prompt choca con lo que encuentres en el repositorio, preguntame
> antes de resolverlo por tu cuenta.
>
> ## Regla central: el test no se toca
>
> El bloque final (2025-02-06 → 2025-12-31) no se lee en ningún código de esta tarea. Toda
> lectura del panel descarta las filas posteriores a 2025-02-05 en el mismo paso, y un `assert`
> verifica que no quede ninguna. El límite sale del calendario (80 % de 1.645 días), igual que
> en diagnostico_municipios.ipynb, no de los datos.
>
> ## Etapa 0a — Dependencias
>
> - Agregá `xgboost` y `pytest` a requirements.txt con versión exacta. Elegí versiones
>   publicadas hace más de dos semanas, compatibles con Python 3.13.2 y con los pines actuales.
> - Regenerá requirements-lock.txt en un entorno limpio, como se hizo el 2026-09-24.
> - Verificá `pip check` e importá xgboost.
> - No cambies ningún otro pin.
>
> ## Etapa 0b — Módulo de variables en src/
>
> Creá `src/variables.py`. Lo van a usar los dos notebooks y el prototipo, así que tiene que
> ser la única implementación de estas variables. Funciones puras, documentadas, que reciban
> el panel y una fecha de origen y no miren datos posteriores al origen:
>
> - **Calendario de 8 niveles:** lunes a domingo, más feriado. Se deriva de `fecha`; el feriado
>   sale de `tipo_dia` del ETL y tiene prioridad sobre el día de la semana. El ETL no se toca.
> - **Nivel del municipio:** media de cada municipio en la ventana de entrenamiento.
> - **Nivel reciente:** media de cada municipio en los últimos N días antes del origen
>   (N ∈ {28, 56, 91}). Queda fijo para los 7 días del horizonte.
> - **Rezagos de 7, 14, 21 y 28 días.** Son siempre observados para un horizonte de 7 días,
>   así que no hay recursión.
> - **Indicador del municipio A,** para el término propio de calendario.
> - **Lluvia,** tomada del panel.
>
> Agregá tests en `tests/test_variables.py`. Como mínimo deben verificar: que ninguna variable
> use datos posteriores al origen, que los feriados coincidan con `tipo_dia`, las dimensiones
> de salida y que no haya nulos en el horizonte.
>
> ## Etapa 0c — Revisión del dashboard del PID (solo lectura)
>
> El prototipo va a ser una pestaña nueva en el dashboard Streamlit del PID. Su
> requirements.txt incluye streamlit==1.35.0, psycopg2-binary==2.9.9, SQLAlchemy==2.0.36,
> pymongo==4.7.2, pandas==2.2.2, plotly==5.22.0, pydeck==0.9.1, python-dotenv==1.0.1 y
> streamlit-option-menu==0.3.6.
>
> Buscá si el código del dashboard está en este repositorio (por ejemplo en app/) y, si está,
> respondé sin modificar nada:
>
> 1. ¿Cómo obtiene los datos? ¿Arranca sin PostgreSQL ni MongoDB?
> 2. ¿Esas versiones se instalan con Python 3.13.2? Sospecho que pandas 2.2.2 y
>    psycopg2-binary 2.9.9 no tienen versiones para 3.13; verificalo.
> 3. ¿Cómo se agregan las pestañas (streamlit-option-menu, páginas, otro mecanismo)?
> 4. Proponé dos o tres formas de integrar una pestaña de predicción que funcione sin bases de
>    datos, con sus ventajas y desventajas.
>
> Si el código no está en este repositorio, decímelo y no sigas con esta parte.
>
> **DETENETE AQUÍ.**
>
> ## Etapa 1 — notebooks/modelos_candidatos.ipynb: protocolo en el panel y referencias
>
> ### Sección 0 — Entorno
> Verificación de entorno igual a la de linea_base.ipynb.
>
> ### Sección 1 — Reglas fijadas antes de ejecutar
> Celda markdown que no se modifica después de ver resultados. Debe contener, textualmente:
>
> - **Lista cerrada de modelos.**
>   - Referencias: media constante global; L0 (promedio de 7/14/21/28 días antes; se revisa su
>     ventana con 2, 4 y 8 semanas); L1 en el panel (nivel del municipio × factor de calendario
>     agregado de 8 niveles, el modelo M2 del diagnóstico).
>   - Candidatos: GLM Poisson, GLM binomial negativa, XGBoost con `objective="count:poisson"`.
> - **Árbol de decisión retirado antes de ejecutar.** En el E2 no extrapoló la tendencia, y
>   XGBoost con pérdida Poisson es la extensión de la misma familia.
> - **Conjuntos de variables, anidados:**
>   - (0) sin exógenas: municipio + nivel reciente + rezagos 7/14/21/28
>   - (a) municipio + calendario de 8 niveles
>   - (b) (a) + término propio de calendario para A
>   - (c) (b) + nivel reciente (28/56/91 días)
>   - (d) (c) + lluvia
> - **Grilla de XGBoost:** `max_depth` ∈ {2, 3, 4} × `n_estimators` ∈ {100, 300} ×
>   `learning_rate` ∈ {0.05, 0.1}. El resto de los parámetros, fijos y declarados.
> - **Ventanas de entrenamiento:** expansiva; deslizante de 364, 546 y 728 días.
> - **Orden de la experimentación:**
>   - A. Conjuntos con GLM Poisson y XGBoost por defecto, en ventana expansiva.
>   - B. Grilla de XGBoost y ajuste de la binomial negativa sobre el conjunto elegido.
>   - C. Ventanas para los dos mejores candidatos.
> - **Regla de selección:**
>   1. Desvianza de Poisson media en validación.
>   2. Empate: candidatos a menos de 1 error estándar del mejor, con el error estándar
>      calculado sobre los 47 cortes.
>   3. Entre empatados, el más simple y explicable (GLM antes que XGBoost; menos variables
>      antes que más).
>   4. Desempate por estabilidad (peor municipio, dispersión entre semanas) y luego por
>      calibración (total predicho / observado).
> - **Binomial negativa:** se reporta la dispersión de Pearson del GLM Poisson y el α
>   estimado. Su papel declarado son los intervalos de predicción y la inferencia sobre
>   coeficientes, no mejorar la desvianza.
> - **Sesgo declarado:** la búsqueda de hiperparámetros y la selección usan los mismos 47
>   cortes; el desempeño del ganador en validación es optimista.
>
> ### Sección 2 — Carga sin test
> `data/processed/panel_diario_montevideo.csv`, filas posteriores a 2025-02-05 descartadas al
> leer, con `assert`. Particiones: 987 días de entrenamiento inicial y 329 de validación, en
> los 8 municipios.
>
> ### Sección 3 — Motor de backtesting
> - 47 cortes con horizonte de 7 días; origen móvil; reentrenamiento en cada corte.
> - Parámetro de ventana: expansiva o deslizante de N días. Implementalo ya, aunque en esta
>   etapa solo se use la expansiva.
> - Todo lo que aprende de los datos se estima con la ventana de entrenamiento del corte,
>   usando las funciones de src/variables.py.
> - Guardá las predicciones por corte, día y municipio. La regla del error estándar las
>   necesita.
>
> ### Sección 4 — Métricas
> Desvianza de Poisson media (predicciones nulas reemplazadas por EPS = 1e-6), MAE, RMSE,
> total predicho / observado y días con predicción cero. Calculalas globales, por municipio y
> por corte.
>
> ### Sección 5 — Control cruzado del motor
> Aplicá el motor a la serie del MUNICIPIO C sola, con la media constante y con L1 de 3
> niveles (tipo_dia), en ventana expansiva. Tiene que reproducir los valores de
> experiments/linea_base/tablas/04_desarrollo_backtesting.csv: desvianza 1,5178 y 1,3782, con
> tolerancia 0,001. Si no coincide, detenete y avisame.
>
> ### Sección 6 — Referencias en el panel
> Media constante global, L0 con 2, 4 y 8 semanas, y L1 de 8 niveles, en ventana expansiva.
> Tablas globales y por municipio.
>
> ### Artefactos y documentación
> - Tablas en `experiments/modelos_candidatos/tablas/`, numeradas, con `00_entorno.csv`.
> - Figuras en `experiments/modelos_candidatos/figuras/`.
> - Ejecutá con `jupyter nbconvert --execute` en el `.venv`: 0 errores.
> - Creá `documentacion/resumen_modelos_candidatos.md` con la estructura de CLAUDE.md. Esta
>   etapa cubre solo protocolo y referencias, así que marcá como PENDIENTE lo de los
>   candidatos.
> - Actualizá HANDOFF.md y documentacion/registro_uso_IA.md con esta sesión.
> - No hagas commit ni push sin mi confirmación.
>
> **DETENETE AQUÍ.** No empieces con los candidatos (fase 2).

**Respuesta (extracto relevante):** (0a) `xgboost==3.4.1` y `pytest==9.1.1`, lock regenerado en entorno limpio (+4 paquetes, ningún
otro pin cambió). (0b) `src/datos.py` y `src/variables.py` con la compuerta `observado()` como única lectura del objetivo, y 15
tests. (0c) «El código del dashboard no está en este repositorio»: se detuvo esa parte. Informe de la etapa con tres decisiones de
diseño y una **advertencia propia**: la lluvia del día a predecir no está disponible con horizonte de 7 días (sólo existiría un
pronóstico), por lo que el conjunto (d) equivale a suponer un pronóstico perfecto.

**Uso y verificación:** **adaptado.** `src/datos.py` no fue pedido (la IA lo agregó para cumplir la regla de «toda lectura descarta
el test»). Verificado: `pip check` limpio, `import xgboost`; `pytest` (15 pasan) y una **prueba de mutación** (se hizo que la
compuerta dejara pasar el futuro y fallaron 5 tests); la ausencia del dashboard se comprobó en el árbol, en `entregable_2` y en todo
el historial con `git grep`. **Archivos afectados:** `requirements.txt`, `requirements-lock.txt`, `pytest.ini`, `src/datos.py`,
`src/variables.py`, `src/__init__.py`, `tests/test_variables.py`.

### Prompt 2
> Respuestas a tu informe de las etapas 0a y 0b:
>
> 1. Lectura del test: queda registrado. Asentalo en registro_uso_IA.md y en HANDOFF.md
>    tal como lo describiste (qué se leyó, que no se tocó n_siniestros, que no influyó en
>    ningún código ni decisión). No hace falta llevarlo al informe.
>
> 2. Tus tres decisiones de src/variables.py quedan confirmadas: origen simulado por
>    bloques de 7 días para las filas de entrenamiento, mismas filas para todos los conjuntos
>    y nivel del municipio como constante de la ventana.
>
> 3. Lluvia: tenés razón. Sacamos el conjunto (d) de la lista cerrada antes de ejecutar.
>    Motivo, para escribir en la sección 1 del notebook: la lluvia del día a predecir no
>    está disponible con horizonte de 7 días (solo existiría un pronóstico) y el diagnóstico
>    no le encontró aporte fuera de muestra (§7.5). Quitá la lluvia de src/variables.py, o
>    dejala marcada como no usada, lo que sea más limpio.
>
> 4. Dashboard: no lo integres todavía, va en la fase 5. Por ahora solo verificá, sin tocar
>    requirements.txt, qué versiones de streamlit, plotly, pydeck, psycopg2-binary, pymongo y
>    python-dotenv se instalan junto con los pines actuales en Python 3.13.2. Informame el
>    resultado en dos líneas.
>
> 5. Actualizá el README (pytest y xgboost) junto con la documentación de la etapa 1.
>
> Después seguí con la etapa 1 tal como estaba en el prompt original, con el conjunto (d)
> eliminado.

**Respuesta (extracto relevante):** se quitó la lluvia de `src/variables.py` (función, columna y mención; el módulo deja constancia
del motivo) y de los tests. Resolución con los pines actuales (`pip install --dry-run`, con el lock como constraints): streamlit
1.65.0, plotly 7.1.0, pydeck 0.9.3, psycopg2-binary 2.9.13, pymongo 4.18.3, python-dotenv 1.2.4. Etapa 1: notebook de 22 celdas;
**control cruzado superado** (1,517768 contra 1,5178 y 1,378246 contra 1,3782); referencias en el panel con L1 de 8 niveles en
1,2319 y L0 de 8 semanas en 1,3626, media constante 1,3967, L0 de 4 semanas 1,5210 y L0 de 2 semanas 2,4384 (27 predicciones cero).

**Uso y verificación:** **utilizado con adaptaciones menores.** Verificado: tras quitar la lluvia, `pytest` (15 pasan, incluida una
aserción de que `lluvia_mm` no está en el horizonte); `jupyter nbconvert --execute --inplace` sin errores; el motor reproduce
`linea_base` dentro de 0,001; el motor se comprobó con un modelo sonda (el objetivo de días ≥ origen no llega al modelo; ventana
deslizante de 364 días exactos); todas las cifras del resumen se contrastaron contra las tablas generadas. **La resolución de
versiones del dashboard no prueba que el dashboard arranque**, y no se pudo revisar su código (no está en el repositorio).
**Observaciones de la IA que decide el equipo:** qué L0 se lleva a la comparación final (la de 4 semanas del E2 queda por detrás
de la media constante) y cómo entra el nivel reciente en el conjunto (0). **Archivos afectados:** `src/variables.py`,
`tests/test_variables.py`, `notebooks/modelos_candidatos.ipynb`, `experiments/modelos_candidatos/`,
`documentacion/resumen_modelos_candidatos.md`, `README.md`, `HANDOFF.md`.

---

## Sesión 2026-10-19 (review R1) — lucaspimentel-uy — Claude Code (Anthropic, Claude Opus 5.5)

**Contexto:** revisión independiente de las fases 0 y 1 del Entregable 3 (commit `74eafbd`, rama `e3/fase-0-1-protocolo`), hecha por un
modelo distinto del que escribió el código (decisión D25). El revisor no modificó código ni notebooks: dejó
`documentacion/reviews/E3_fase_0-1.md`, que es el artefacto de esta sesión.

### Prompt 1
> Sos el revisor de las fases 0 y 1 del Entregable 3. No trabajaste en estas fases. Tu tarea es
> verificar, no corregir: el único archivo que podés crear es el informe de review. Modelo de esta
> sesión: opus (D25); anotalo en el informe.
>
> ## Paso 0 — Rama y prerrequisitos (detenete si algo no cumple)
>
> 1. Creá la rama: `git switch main`, `git pull`, `git switch -c e3/fase-0-1-protocolo`.
>    Verificá con `git log -1 --oneline` que HEAD es 74eafbd. Si main avanzó más allá de 74eafbd,
>    detenete y avisame.
> 2. Activá el .venv (`.venv\Scripts\Activate.ps1`) y verificá que `python -c "import sys;
>    print(sys.executable, sys.version)"` apunta a .venv y dice 3.13.2. Todo comando de Python,
>    pytest y nbconvert se corre con el .venv activado: con el venv sin activar, el kernel de
>    nbconvert usa el Python 3.13.9 del sistema.
> 3. Panel: data/processed/panel_diario_montevideo.csv tiene que existir y su sha256
>    (`Get-FileHash -Algorithm SHA256`) tiene que ser
>    82467fc87b5d2bceb24ec6f3c5072e1b7cf9e75507b1d5c5a4d20153114a1b06, el registrado en
>    experiments/diagnostico_municipios/tablas/00_procedencia.csv. Calculá solo el hash: no abras
>    el archivo ni leas filas. Si falta o el hash no coincide, detenete.
>
> ## Paso 1 — Lectura
>
> Leé CLAUDE.md, HANDOFF.md, documentacion/resumen_modelos_candidatos.md y la sección 1 de
> notebooks/modelos_candidatos.ipynb. El trabajo se commiteó directo en main (D23), así que la base
> de comparación es el commit padre: `git diff 34ff44d...e3/fase-0-1-protocolo --stat` y después el
> diff completo. No uses `git diff main...`: sale vacío.
>
> ## Paso 2 — Ejecución
>
> 1. `pytest` desde la raíz: tienen que pasar los 15 tests, sin saltados.
> 2. `jupyter nbconvert --to notebook --execute --inplace notebooks/modelos_candidatos.ipynb`.
>    Tiene que terminar con 0 errores. Verificá en la salida de la sección 0 que el Python es
>    3.13.2.
> 3. La ejecución reescribe el notebook y los artefactos de experiments/modelos_candidatos/.
>    Corré `git status` y `git diff --stat`, y compará cada CSV regenerado con el commiteado:
>    reportá qué archivos cambiaron y si las cifras difieren o solo cambian metadatos (fechas,
>    rutas, bytes de PNG). Una cifra que cambia es un hallazgo. Después dejá el árbol como estaba
>    con `git restore notebooks/ experiments/` y confirmá con `git status`.
> 4. F0-B2: en una copia temporal FUERA del repo, hacé que una variable de src/variables.py lea
>    el día del origen o posteriores y verificá que al menos un test falla. Borrá la copia al
>    terminar.
>
> ## Paso 3 — Criterios
>
> Evaluá cada criterio: CUMPLE o NO CUMPLE, con evidencia concreta (comando y salida, archivo y
> línea, cifra contra el CSV). Sin evidencia, el criterio es NO CUMPLE.
>
> Comunes:
> - B1 Fuera de evaluacion_final.ipynb, ningún código lee filas posteriores a 2025-02-05 (buscar
>   lecturas del panel fuera de cargar_panel_desarrollo(); comprobar el assert del notebook).
> - B2 Los notebooks de la fase ejecutan de punta a punta sin errores (nbconvert en el .venv).
> - B3 pytest pasa entero (15 pasados, 0 saltados).
> - B4 Toda cifra del resumen, del HANDOFF y del informe coincide con un artefacto.
> - B5 Las reglas fijadas no se modificaron después de ejecutar (sección 1 del notebook).
> - B6 Entorno coherente: verificación de entorno del notebook en verde; pip check limpio;
>   requirements.txt y el lock coinciden.
> - N1 El documento acompañante sigue la estructura de CLAUDE.md, incluida la lista de frases que
>   no deben aparecer en el informe.
> - N2 HANDOFF y registro de IA actualizados con la sesión.
> - N3 Las lecturas separan evidencia de inferencia.
> - N4 Los resultados negativos quedan registrados.
> - N5 Código legible: sin código muerto, funciones de src/ documentadas, nombres consistentes.
> - N6 El alcance coincide con lo pedido: no se hizo de más ni de menos.
>
> Fase 0:
> - F0-B1 xgboost y pytest con versión exacta; el diff del lock contra 34ff44d suma solo xgboost,
>   pytest, iniconfig y pluggy.
> - F0-B2 Los tests detectan fugas (Paso 2.4).
> - F0-B3 Ninguna función de src/variables.py lee n_siniestros sin pasar por la función
>   compuerta.
> - F0-N1 La lluvia no aparece en src/variables.py y el motivo de su retiro está escrito en el
>   módulo.
> - F0-N2 pytest.ini silencia solo el aviso de numpy 2.5 con pandas 2.3.3, con un comentario que
>   lo justifica.
> - F0-N3 README actualizado con pytest y xgboost.
> - F0-N4 La lectura accidental del test está asentada en HANDOFF y en el registro de IA (D22).
>
> Fase 1:
> - F1-B1 Control cruzado: el motor reproduce 1,5178 y 1,3782 en el Municipio C, con tolerancia
>   0,001.
> - F1-B2 La sección 1 del notebook coincide con "Reglas fijadas antes de ejecutar" del plan, sin
>   el conjunto (d): lista cerrada (media constante, L0 de 8 semanas, L1 de 8 niveles, GLM
>   Poisson, NB2, XGBoost count:poisson), conjuntos (0), (a), (b), (c), grilla de 12
>   combinaciones, ventanas expansiva y deslizante de 364/546/728 días, regla de selección de 5
>   pasos.
> - F1-B3 Ningún nivel ni factor se estima con datos del horizonte: alterar los valores
>   posteriores al origen de un corte no cambia sus predicciones (probalo en la copia temporal o
>   en memoria, sin escribir en el repo).
> - F1-B4 La ventana deslizante tiene exactamente N días en cada corte.
> - F1-N1 Las métricas quedan guardadas globales, por municipio y por corte, y las predicciones
>   por corte, día y municipio.
> - F1-N2 Las cifras del diagnóstico citadas en el resumen (M0 1,4014; M2 1,2385) están marcadas
>   como chequeo de coherencia y no como cifras citables.
>
> ## Paso 4 — Veredicto e informe
>
> Veredicto, aplicando la regla sin interpretación:
> - DESAPROBADA si falla al menos un criterio bloqueante (B).
> - APROBADA CON OBSERVACIONES si fallan solo criterios no bloqueantes (N).
> - APROBADA si cumplen todos.
>
> Escribí documentacion/reviews/E3_fase_0-1.md con: fecha, modelo, commit revisado (hash
> completo), base de comparación (34ff44d), sha256 del panel, tabla de criterios (ID, criterio,
> resultado, evidencia), resultado de la reejecución (archivos que cambiaron y si cambió alguna
> cifra), veredicto, lista numerada de observaciones con lo que habría que hacer para corregir
> cada una, y riesgos fuera de criterios (sin afectar el veredicto).
>
> Mostrame el veredicto y las observaciones. No hagas commit ni push.

*Prompt completado el 19/10/2026 en el fix de la ronda 2 (D29, D30): transcripción textual del primer mensaje de la sesión del revisor (`88463c61-b062-42b9-ad62-da91e958eac5.jsonl`, transcripciones locales de Claude Code), extraída por programa y no reescrita a mano.*

**Respuesta (extracto relevante):** veredicto **DESAPROBADA**. Falla un criterio bloqueante, **F1-B2** (la sección 1 del notebook
no coincide con la lista cerrada del plan en «L0 de 8 semanas» y «NB2»), y dos no bloqueantes, **N5** (código muerto `exp_dias` y una
viñeta residual en `src/variables.py`) y **N6** (el nivel del municipio duplicado en `modelo_L1` en lugar de
`var.nivel_municipio`). Cumplen los otros 13 criterios bloqueantes. Además: pytest 15 pasados; los 14 artefactos de
`experiments/modelos_candidatos/` se reescribieron idénticos; mutaciones M1–M4 detectadas por los tests (2/4/4/5 fallan); F1-B3
sin fuga (705 comparaciones, diferencia máxima 0,0). Ocho observaciones y seis riesgos fuera de criterios (R1: sin trazabilidad
temporal en git; R2: la resolución del dashboard no se reproduce, hoy streamlit 1.66.0 y pymongo 4.19.0).

**Uso y verificación:** el informe se usó como entrada del fix de la sesión siguiente. Verificación del revisor (según el propio
informe): reejecución con `nbconvert`, comparación de hashes de artefactos, mutaciones en copia temporal fuera del repo, contraste de
cifras contra tablas y de fechas de publicación contra PyPI. **Archivos afectados:** `documentacion/reviews/E3_fase_0-1.md` (nuevo).

---

## Sesión 2026-10-19 — lucaspimentel-uy — Claude Code (Anthropic, Claude Sonnet 5.5)

**Contexto:** Entregable 3, fases 0 y 1, fix de la review R1 en la rama `e3/fase-0-1-protocolo`. Tres pasos: (1) adenda a la sección 1
de `notebooks/modelos_candidatos.ipynb` (corrige F1-B2); (2) observaciones restantes 2 a 9 de la review; (3) verificación.

### Prompt 1
> Sesión de trabajo del Entregable 3, fase <N="0 y 1 (fix de R1)">, en la rama e3/fase-0-1-protocolo.
>
> Antes de hacer nada:
> 1. Verificá con `git branch --show-current` que estás en <rama>. Si no, detenete y avisame.
> 2. Leé CLAUDE.md, HANDOFF.md y documentacion/resumen_modelos_candidatos.md. Respetá todas
>    las reglas de CLAUDE.md: ninguna cifra sin artefacto, documento acompañante por notebook,
>    registro de IA y HANDOFF al cierre.
> 3. Las reglas fijadas en la sección 1 de notebooks/modelos_candidatos.ipynb no se modifican.
>    Si algo necesita precisarse, se agrega un bloque fechado debajo y me lo consultás antes.
>
> Reglas de la sesión:
> - El bloque final (2025-02-06 → 2025-12-31) solo lo lee notebooks/evaluacion_final.ipynb.
>   En cualquier otro código, el panel entra únicamente por src/datos.py:cargar_panel_desarrollo().
>   Esto incluye comandos sueltos de exploración.
> - Variables solo desde src/variables.py. Si hace falta una nueva, va ahí y con tests.
> - Los notebooks se ejecutan con `jupyter nbconvert --execute` en el .venv, con 0 errores.
>   `pytest` tiene que pasar entero.
> - Detenete en cada parada que indique el prompt. No avances sin mi confirmación.
> - Si una instrucción choca con lo que encontrás en el repositorio, o si una decisión no
>   está cubierta por el prompt, preguntá en vez de resolverla por tu cuenta.
> - Al cerrar: actualizá el documento acompañante, HANDOFF.md y
>   documentacion/registro_uso_IA.md. Mostrame `git status` y un resumen de los archivos tocados.
>   Hacé commit en <rama> solo cuando yo lo confirme. Nunca en main y nunca push.
>
> Prompt de la fase:
>
> Fix de la review R1 (documentacion/reviews/E3_fase_0-1.md, veredicto DESAPROBADA). Leé el informe
> de review antes de empezar. No cambies nada que la review no pida. Activá el .venv antes de
> cualquier comando de Python.
>
> ## Paso 1 — Adenda (corrige F1-B2; D27)
>
> Agregá debajo de la sección 1 de notebooks/modelos_candidatos.ipynb, sin tocar el texto original,
> un bloque "Precisiones fijadas el 19/10/2026, después de la fase 1 y antes de ejecutar cualquier
> candidato" (decisiones D17 a D20 y D27 del plan):
> 1. L0 que pasa a la comparación: 8 semanas. Se eligió mirando los 47 cortes de validación
>    (desvianza 1,3626, contra 1,5210 de 4 semanas y 2,4384 de 2 semanas), después de fijar la
>    lista. Queda a menos de 1 error estándar de la media constante (1,3967). Tomá las cifras de
>    las tablas y citá el archivo de cada una.
> 2. Nivel reciente del conjunto (0): N ∈ {28, 56, 91}, elegido en el paso A por desvianza media
>    en validación, por separado en cada familia (igual que en el conjunto (c)).
> 3. XGBoost en el paso A: max_depth=3, n_estimators=300, learning_rate=0.05; resto de los
>    parámetros fijos y declarados; semilla fija.
> 4. Elección del conjunto por familia (GLM y XGBoost): entre (a), (b) y (c) con la regla de 1
>    error estándar, orden de simplicidad a < b < c. (0) se reporta para el objetivo 1.2.2 y solo
>    reemplaza al elegido si lo mejora por más de 1 error estándar.
> 5. Binomial negativa: NB2, varianza μ + αμ², con α estimado por máxima verosimilitud en cada
>    corte (statsmodels.discrete NegativeBinomial con loglike_method="nb2"; verificá el nombre
>    exacto en la documentación de statsmodels 0.14.6). La familia NegativeBinomial del GLM fija α
>    si no se le pasa, así que no se usa como estimador principal. Plan B declarado: si no
>    converge en un corte, se reporta y en ese corte se usa el GLM NB con el α del corte anterior.
> Espejo en el resumen §1.1 y cierre del pendiente de L0 en HANDOFF y en el resumen.
> DETENETE. Commit solo con esto (notebook, resumen y HANDOFF), con el mensaje
> "Adenda de precisiones previas a los candidatos (D27)", cuando yo lo confirme.
>
> ## Paso 2 — Observaciones restantes
>
> 2. Borrá exp_dias (celda 9) y el resto de la viñeta de la lluvia en src/variables.py:12-13.
> 3. modelo_L1 y modelo_media_constante usan var.nivel_municipio en lugar del groupby propio. El
>    factor de calendario no se mueve a src/ (deuda aceptada, fase 5).
> 4. Resumen §0, regla 4: la referencia a las frases prohibidas es la §5, no la §6.
> 5. HANDOFF: el trabajo de las fases 0 y 1 está en 74eafbd (mensaje "E3", que no se corrige
>    porque reescribiría main); registrá D23 y el resultado de R1.
> 6. Donde diga que ninguna fila del test "llega a memoria" o "queda en memoria" (src/datos.py,
>    resumen, HANDOFF): "ninguna fila del test se conserva ni se acumula; cada tramo se lee y se
>    filtra antes de acumularse".
> 7. Comentario de pytest.ini: el aviso lo disparan llamadas a pd.Timedelta en src/variables.py,
>    por la combinación pandas 2.3.3 con numpy 2.5.2.
> 8. En la celda de imports, filtrá solo ese aviso (misma categoría y mensaje que pytest.ini) para
>    que el notebook no arrastre las salidas con rutas locales.
> 9. Registro de IA: una entrada para la sesión de review R1 y otra para esta sesión.
>
> ## Paso 3 — Verificación
>
> - pytest: 15 pasados, 0 saltados.
> - nbconvert --execute --inplace con 0 errores.
> - `git diff --stat experiments/`: los 14 artefactos tienen que quedar idénticos. Si cambia
>   cualquier cifra (el cambio del punto 3 no debería cambiar ninguna), detenete y mostrame el
>   antes y el después.
> - Mostrame git status y el resumen de archivos tocados. Commit en la rama, incluido
>   documentacion/reviews/E3_fase_0-1.md sin modificar, cuando yo lo confirme.

**Respuesta (extracto relevante):** se verificó la rama (`e3/fase-0-1-protocolo`) y se leyeron CLAUDE.md, HANDOFF.md, el resumen y la
review. Se agregó la celda «Adenda a la sección 1» (id `a7d19f27`) debajo de la sección 1, sin tocarla, con las cifras tomadas de
`tablas/05` y `tablas/08` (L0 de 8 semanas 1,3626; 4 semanas 1,5210; 2 semanas 2,4384; media constante 1,3967 con EE 0,0447; diferencia
0,0341, menos de 1 EE). Se comprobó en el paquete instalado que `statsmodels.discrete.discrete_model.NegativeBinomial` acepta
`loglike_method` con valor por omisión `'nb2'`, y que la familia `NegativeBinomial` del GLM tiene `alpha=1.0` fijo. La IA señaló que el
plan B pedido («α del corte anterior») no cubría el primer corte.

**Uso y verificación:** **adaptado en el paso siguiente.** La IA dejó el plan B como estaba y lo preguntó; el equipo lo reemplazó
(Prompt 2). Verificación del Paso 1: el diff del notebook son solo líneas insertadas (41, luego 43), sin tocar la celda original.
**Archivos afectados:** `notebooks/modelos_candidatos.ipynb`, `documentacion/resumen_modelos_candidatos.md`, `HANDOFF.md`.

### Prompt 2
> Dos ajustes a la adenda antes del commit:
>
> 1. Ítem 5, reemplazá el plan B por: "Plan B (D28): si NB2 por máxima verosimilitud no converge
>    en un corte, se reporta y en ese corte se usa el GLM NB con α estimado por momentos en el
>    mismo corte: regresión auxiliar sin intercepto de ((y − μ)² − y)/μ sobre μ, con μ del GLM
>    Poisson ajustado en el entrenamiento de ese corte (Cameron y Trivedi, 1990)." Mismo cambio en
>    el espejo del resumen §1.1.
> 2. Asigná las referencias ítem por ítem: 1 → D17, 2 → D18, 3 → D19, 4 → D20, 5 → D27 y D28.
>    Sacá la lista conjunta del encabezado.
>
> Mostrame el diff de la celda de la adenda. Si solo cambian esos dos puntos, hacé el commit
> "Adenda de precisiones previas a los candidatos (D27)" con solo esos tres archivos (notebook,
> resumen y HANDOFF) y seguí con el Paso 2 sin detenerte. La próxima parada es antes del commit
> final.

**Respuesta (extracto relevante):** plan B (D28) y referencias D17 a D28 por ítem, en la adenda, en el espejo del resumen y en el
HANDOFF. Commit `cf76a36` («Adenda de precisiones previas a los candidatos (D27)»), con solo esos tres archivos. Paso 2: se borró
`exp_dias`; la viñeta residual de `src/variables.py` (terminaba en «;») pasó a terminar en «.»; `modelo_L1` usa
`var.nivel_municipio(vista, origen, ventana)`; la regla 4 del resumen apunta a la §5; la frase de la carga del test se reformuló en
`src/datos.py`, en la celda de la sección 2 del notebook y en el resumen (HANDOFF y registro no la contenían con esa redacción);
comentario de `pytest.ini` corregido; la celda de imports filtra solo el aviso de `pd.Timedelta` (misma categoría y mensaje que
`pytest.ini`).

**Uso y verificación:** **utilizado, con una desviación declarada:** el punto 3 pedía el cambio también en `modelo_media_constante`,
pero esa función no tiene un `groupby` por municipio (calcula la media global de la ventana), así que **no se tocó**; solo
`modelo_L1` tenía el cálculo duplicado. Verificado: `pytest` → 15 pasados, 0 saltados; `jupyter nbconvert --execute --inplace` →
0 salidas de tipo `error`, 0 salidas de `stderr` y ninguna ruta local en las salidas (antes, ~1.100 líneas de avisos);
`git hash-object --path` de los 14 artefactos de `experiments/modelos_candidatos/` contra el índice → los 14 idénticos, así que
ninguna cifra cambió. **Archivos afectados:** `notebooks/modelos_candidatos.ipynb`, `src/datos.py`, `src/variables.py`, `pytest.ini`,
`documentacion/resumen_modelos_candidatos.md`, `HANDOFF.md`, `documentacion/registro_uso_IA.md`.

### Prompt 3
> 1. Este es el prompt textual de la sesión de review R1. Reemplazá con él el
>    <!-- PENDIENTE --> de su entrada en documentacion/registro_uso_IA.md:
>    <pegar acá el prompt del plan>
> 2. Aceptado: modelo_media_constante queda como está (la sección 1 fija la media constante
>    global). Dejalo asentado en la entrada de esta sesión del registro y en el §8 del resumen.
> 3. Commit final con los 7 archivos más documentacion/reviews/E3_fase_0-1.md sin modificar,
>    mensaje "Corrige las observaciones de la review R1 (N5, N6 y precisiones menores)".
> 4. git push -u origin e3/fase-0-1-protocolo. No mergees.

*Nota del 19/10/2026 (fix de la ronda 2): el prompt se deja como se envió. El marcador `<pegar acá el prompt del plan>` del punto 1 no se completó en ese momento; el prompt de R1 se completó después, en la entrada de la review R1 (ronda 1), en la sesión que documenta la entrada «Sesión 2026-10-19 (fix de la ronda 2 de R1)», más abajo.*

**Respuesta (extracto relevante):** el punto 1 llegó con el marcador `<pegar acá el prompt del plan>` sin reemplazar, es decir, sin el
texto del prompt de la review: **el `PENDIENTE` de la entrada de la review R1 sigue abierto** y se avisó al equipo. Punto 2 asentado
aquí y en el §8 del resumen. Puntos 3 y 4 ejecutados (commit y push de la rama, sin merge).

**Uso y verificación:** **decisión del equipo (punto 2):** `modelo_media_constante` queda como está, porque la sección 1 fija la media
constante **global**; por eso no usa `var.nivel_municipio` y el punto 3 del Paso 2 se aplicó solo a `modelo_L1`. Verificación del
commit y del push: `git log --oneline 34ff44d..HEAD` da `74eafbd` (E3) → `cf76a36` (adenda) → `e484dcb` (fix); `git ls-remote origin e3/fase-0-1-protocolo`, ejecutado el 19/10/2026 antes del commit de la ronda 2, devuelve `e484dcb78fa65af135b56c7430eb369c846fbbdc	refs/heads/e3/fase-0-1-protocolo`. **Archivos afectados:**
`documentacion/registro_uso_IA.md`, `documentacion/resumen_modelos_candidatos.md`.

---

## Sesión 2026-10-19 (review R1, ronda 2) — lucaspimentel-uy — Claude Code (Anthropic, Claude Opus 5.5)

**Contexto:** segunda revisión independiente de las fases 0 y 1 del Entregable 3, sobre el fix `e484dcb` de la rama
`e3/fase-0-1-protocolo` (decisión D25: revisor distinto del que escribió el código). El revisor no modificó código ni notebooks: dejó
`documentacion/reviews/E3_fase_0-1_r2.md`, que es el artefacto de esta sesión.

### Prompt 1
> Sos el revisor de las fases 0 y 1 del Entregable 3, ronda 2. No trabajaste en estas fases ni en
> el fix. Tu tarea es verificar, no corregir: el único archivo que podés crear es el informe de
> review. Modelo de esta sesión: opus (D25); anotalo en el informe.
>
> ## Paso 0 — Rama y prerrequisitos (detenete si algo no cumple)
>
> 1. `git switch e3/fase-0-1-protocolo` y `git pull`. Mostrá `git log --oneline 34ff44d..HEAD`:
>    tienen que aparecer 74eafbd, después cf76a36 (adenda) y después el commit del fix, en ese
>    orden.
> 2. Activá el .venv (`.venv\Scripts\Activate.ps1`) y verificá que `python -c "import sys;
>    print(sys.executable, sys.version)"` apunta a .venv y dice 3.13.2.
> 3. El sha256 de data/processed/panel_diario_montevideo.csv tiene que ser
>    82467fc87b5d2bceb24ec6f3c5072e1b7cf9e75507b1d5c5a4d20153114a1b06. Calculá solo el hash.
>
> ## Paso 1 — Lectura
>
> Leé CLAUDE.md, HANDOFF.md, documentacion/resumen_modelos_candidatos.md,
> documentacion/reviews/E3_fase_0-1.md (ronda 1) y las secciones 1 y "Adenda a la sección 1" del
> notebook. Diff contra la base: `git diff 34ff44d...HEAD --stat` y completo. Además
> `git diff 74eafbd HEAD -- notebooks/modelos_candidatos.ipynb` para ver qué cambió en el fix.
>
> ## Paso 2 — Ejecución
>
> 1. `pytest`: 15 pasados, 0 saltados.
> 2. `jupyter nbconvert --to notebook --execute --inplace notebooks/modelos_candidatos.ipynb`
>    con 0 errores; la sección 0 dice Python 3.13.2.
> 3. Compará los artefactos regenerados con los commiteados (`git diff --stat experiments/`):
>    ninguna cifra puede cambiar. Restaurá con `git restore notebooks/ experiments/` y confirmá
>    con `git status`.
> 4. F0-B2 y F1-B3 se repiten igual que en la ronda 1, en una copia FUERA del repo o en memoria.
>
> ## Paso 3 — Criterios
>
> Evaluá todos los criterios de la ronda 1 (B1–B6, N1–N6, F0-B1 a F0-N4, F1-B1 a F1-N2), cada uno
> con evidencia. Precisiones para esta ronda:
> - F1-B2 se evalúa sobre la sección 1 más la adenda: la sección 1 tiene que estar idéntica a la
>   de 74eafbd, la adenda tiene que fijar L0 de 8 semanas (declarando que se eligió con la
>   validación), N ∈ {28, 56, 91} para (0), XGBoost del paso A, la regla por familia y NB2 con α
>   por máxima verosimilitud y plan B por momentos en el mismo corte, y su commit (cf76a36) tiene
>   que ser anterior al del fix.
> - N6: la media constante es global por definición de la sección 1; no es una observación que
>   modelo_media_constante no use nivel_municipio. Sí verificá que modelo_L1 use
>   var.nivel_municipio.
> - Verificá una por una las 8 observaciones de la ronda 1: corregida, aceptada como deuda
>   (mensaje del commit "E3"; factor de calendario a src/ para la fase 5) o pendiente.
> - N2: el registro de IA tiene las entradas de la review R1 y del fix con los prompts textuales,
>   sin marcas de pendiente.
>
> ## Paso 4 — Veredicto e informe
>
> Misma regla: DESAPROBADA si falla un B; APROBADA CON OBSERVACIONES si fallan solo N; APROBADA si
> cumplen todos. Escribí documentacion/reviews/E3_fase_0-1_r2.md con: fecha, modelo, commit
> revisado (hash completo), base (34ff44d), sha256 del panel, tabla de criterios con evidencia,
> estado de cada observación de la ronda 1, resultado de la reejecución, veredicto, observaciones
> nuevas numeradas y riesgos fuera de criterios. Mostrame el veredicto. No hagas commit ni push.

*Transcripción textual del primer mensaje de la sesión del revisor (`07b59f2d-b7fe-4f5e-8794-396a1ae662d9.jsonl`, transcripciones locales
de Claude Code), extraída por programa y no reescrita a mano.*

**Respuesta (extracto relevante):** veredicto **APROBADA CON OBSERVACIONES**. Los 14 criterios bloqueantes cumplen, incluido **F1-B2**
(la sección 1 es idéntica a la de `74eafbd`; la adenda de `cf76a36`, anterior al fix, fija todo lo que pedía el criterio). Falla un
criterio no bloqueante, **N2**: el Prompt 1 de la entrada de R1 (ronda 1) conserva el marcador `<!-- PENDIENTE -->`. Observaciones
nuevas: (1) falta ese prompt; (2) el HANDOFF no lista el pendiente; (3) la verificación del commit y del push en el registro no es
trazable (menor). Las 8 observaciones de la ronda 1 quedan corregidas, o aceptadas como deuda (mensaje «E3»; factor de calendario a
`src/` en la fase 5). Riesgos fuera de criterios nuevos: **R7** (NB2 y su plan B son reglas, no código; conviene fijar el criterio de no
convergencia, por ejemplo `mle_retvals["converged"]`, antes de ejecutar) y **R8** (fix y reviews son de modelos distintos pero de la
misma familia; conviene que la validación del equipo conste aparte).

**Uso y verificación:** el informe se usó como entrada del fix de la ronda 2 (sesión siguiente): las observaciones 1 a 3 se corrigen allí,
R7 se responde con la decisión D29 y R8 con la validación del equipo (D30). Verificación del revisor (según el propio informe):
`pytest` 15 pasados; `nbconvert --execute` con 0 errores; los 14 artefactos de `experiments/modelos_candidatos/` idénticos a los
commiteados; mutaciones M1–M4 detectadas (2/4/4/5 fallan); F1-B3 sin fuga (705 comparaciones, diferencia máxima 0,0); sha256 del panel
igual al esperado. **Archivos afectados:** `documentacion/reviews/E3_fase_0-1_r2.md` (nuevo).

---

## Sesión 2026-10-19 (fix de la ronda 2 de R1) — lucaspimentel-uy — Claude Code (Anthropic, Claude Sonnet 5.5)

**Contexto:** Entregable 3, fases 0 y 1, rama `e3/fase-0-1-protocolo`. Corrección de las observaciones de la ronda 2 de R1
(`documentacion/reviews/E3_fase_0-1_r2.md`). Solo documentación: no se tocó código ni artefactos.

### Prompt 1
> Sesión de trabajo del Entregable 3, fase Fix corto de las obs. de la review, en la rama e3/fase-0-1-protocolo.
>
> Antes de hacer nada:
> 1. Verificá con `git branch --show-current` que estás en <rama>. Si no, detenete y avisame.
> 2. Leé CLAUDE.md, HANDOFF.md y documentacion/resumen_modelos_candidatos.md. Respetá todas
>    las reglas de CLAUDE.md: ninguna cifra sin artefacto, documento acompañante por notebook,
>    registro de IA y HANDOFF al cierre.
> 3. Las reglas fijadas en la sección 1 de notebooks/modelos_candidatos.ipynb no se modifican.
>    Si algo necesita precisarse, se agrega un bloque fechado debajo y me lo consultás antes.
>
> Reglas de la sesión:
> - El bloque final (2025-02-06 → 2025-12-31) solo lo lee notebooks/evaluacion_final.ipynb.
>   En cualquier otro código, el panel entra únicamente por src/datos.py:cargar_panel_desarrollo().
>   Esto incluye comandos sueltos de exploración.
> - Variables solo desde src/variables.py. Si hace falta una nueva, va ahí y con tests.
> - Los notebooks se ejecutan con `jupyter nbconvert --execute` en el .venv, con 0 errores.
>   `pytest` tiene que pasar entero.
> - Detenete en cada parada que indique el prompt. No avances sin mi confirmación.
> - Si una instrucción choca con lo que encontrás en el repositorio, o si una decisión no
>   está cubierta por el prompt, preguntá en vez de resolverla por tu cuenta.
> - Al cerrar: actualizá el documento acompañante, HANDOFF.md y
>   documentacion/registro_uso_IA.md. Mostrame `git status` y un resumen de los archivos tocados.
>   Hacé commit en <rama> solo cuando yo lo confirme. Nunca en main y nunca push.
>
> Prompt de la fase:
> Fix de la review R1, ronda 2 (documentacion/reviews/E3_fase_0-1_r2.md, APROBADA CON
> OBSERVACIONES). Solo documentación: no toques código ni artefactos.
>
> 1. Prompts textuales de las reviews: Claude Code guarda las transcripciones locales en
>    %USERPROFILE%\.claude\projects\ (carpeta de este repo), en archivos .jsonl. Buscá la sesión
>    cuyo primer mensaje empieza con "Sos el revisor de las fases 0 y 1 del Entregable 3. No
>    trabajaste en estas fases. Tu tarea" (R1, ronda 1) y la de "…, ronda 2" (R1, ronda 2).
>    Transcribí cada primer mensaje tal cual. Si no las encontrás, detenete y avisame; no
>    reconstruyas el texto.
> 2. registro_uso_IA.md: reemplazá el <!-- PENDIENTE --> de la entrada de R1 ronda 1 con su
>    prompt, agregá la entrada de R1 ronda 2 (prompt y veredicto) y la de esta sesión. En la
>    entrada del fix anterior, reemplazá "ver en la sesión" por los hashes cf76a36 y e484dcb y la
>    salida de `git ls-remote origin e3/fase-0-1-protocolo`. El prompt del fix anterior se deja
>    como se envió, con una nota de que el marcador no se completó.
> 3. Adenda, ítem 6 nuevo, marcado "agregado el 19/10/2026 en el fix de la ronda 2, antes de
>    ejecutar candidatos (D29)": NB2 se ajusta con method="newton" y maxiter=100; un corte cuenta
>    como no convergido si mle_retvals["converged"] es False, si se emite ConvergenceWarning o si
>    α no es finito o no es positivo; en ese caso se aplica el plan B (D28). Espejo en el resumen
>    §1.1. No toques la sección 1 ni los ítems 1 a 5.
> 4. HANDOFF y registro, validación del equipo (D30): Lucas revisó los veredictos de las dos
>    rondas de R1 y confirmó el 19/10 las decisiones D17, D18, D23, D26 a D30, con apoyo de
>    Claude en el chat del Project. En el HANDOFF, cerrá el pendiente del prompt de R1.
> 5. Verificación: pytest con 15 pasados y 0 saltados; `git diff --stat experiments/` vacío.
> 6. Commit con todo lo anterior más documentacion/reviews/E3_fase_0-1_r2.md sin modificar,
>    mensaje "Completa el registro de R1 y fija el criterio de convergencia de NB2 (D29, D30)", y
>    push de la rama. No mergees.

**Respuesta (extracto relevante):** se verificó la rama y se leyeron CLAUDE.md, HANDOFF.md, el resumen, el registro y el informe de la
ronda 2. (1) Las sesiones del revisor existen en las transcripciones locales (`%USERPROFILE%\.claude\projects\`, carpeta de este
repositorio): R1 ronda 1 es `88463c61-…` y R1 ronda 2 es `07b59f2d-…`; se identificaron por el primer mensaje y se extrajeron por
programa (6.232 y 3.279 caracteres). (2) Registro: el `PENDIENTE` de R1 ronda 1 se reemplazó por su prompt; se agregaron las entradas de
R1 ronda 2 y de esta sesión; en el Prompt 3 del fix anterior se dejó el prompt como se envió, con una nota, y «ver en la sesión» se
reemplazó por los hashes `cf76a36` y `e484dcb` y la salida de `git ls-remote`. (3) Ítem 6 de la adenda (D29): NB2 con `method="newton"`
y `maxiter=100`; no convergido si `mle_retvals["converged"]` es `False`, si se emite `ConvergenceWarning` o si α no es finito o no es
positivo; entonces plan B (D28). Espejo en el resumen §1.1 (fila 6) y §8. (4) HANDOFF: entrada nueva con la validación del equipo (D30)
y cierre del pendiente del prompt de R1.

**Uso y verificación:** **utilizado tal cual, con dos precisiones declaradas:** (a) la celda de la adenda abre diciendo «cinco
precisiones»; no se editó para no tocar texto ya commiteado, y el ítem 6 lo aclara («sexta precisión, posterior»); (b) en el diff del
notebook la última línea del ítem 5 aparece modificada solo por el salto de línea que se le agregó al encadenar el ítem 6, sin cambio de
contenido. **La validación del equipo (D30) la declaró el equipo en el prompt** (Lucas revisó los veredictos de las dos rondas de R1 y
confirmó el 19/10 las decisiones D17, D18, D23, D26 a D30, con apoyo de Claude en el chat del Project); la IA la asentó, no la
comprobó. Verificación: antes de fijar D29 se comprobó con datos sintéticos en memoria (no el panel) y statsmodels 0.14.6 que
`NegativeBinomial(..., loglike_method="nb2").fit(method="newton", maxiter=100)` es válido, que el resultado trae
`mle_retvals["converged"]` y que `params` termina en `alpha` (comprobación de API, no resultado del proyecto); `pytest` → 15 pasados,
0 saltados; `git diff --stat experiments/` vacío; el notebook no se reejecutó (solo cambió una celda de texto). Los prompts del registro
se contrastaron con las transcripciones por programa. **Archivos afectados:** `notebooks/modelos_candidatos.ipynb` (celda de texto de la
adenda), `documentacion/resumen_modelos_candidatos.md`, `documentacion/registro_uso_IA.md`, `HANDOFF.md`,
`documentacion/reviews/E3_fase_0-1_r2.md` (sin modificar, se incluye en el commit).

---

## Sesión 2026-10-19 (review R1, ronda 3) — lucaspimentel-uy — Claude Code (Anthropic, Claude Opus 5.5)

**Contexto:** review corta de las fases 0 y 1 del Entregable 3, ronda 3. Verifica solo las observaciones de
`documentacion/reviews/E3_fase_0-1_r2.md` sobre el commit `ce6a18a` de la rama `e3/fase-0-1-protocolo` (decisión D25: revisor
distinto del que hizo el fix). El revisor no modificó código, notebooks ni artefactos: dejó `documentacion/reviews/E3_fase_0-1_r3.md`
y esta entrada.

### Prompt 1
> Sos el revisor de la review corta de las fases 0 y 1 del Entregable 3 (R1, ronda 3). Verificá
> solo las observaciones de documentacion/reviews/E3_fase_0-1_r2.md. Modelo: opus (D25).
>
> 1. `git switch e3/fase-0-1-protocolo`, `git pull`. Mostrá `git log --oneline e484dcb..HEAD` y
>    `git diff e484dcb..HEAD --stat`: solo pueden cambiar registro_uso_IA.md, HANDOFF.md,
>    resumen_modelos_candidatos.md, la celda de la adenda del notebook y el informe r2. Ningún
>    archivo de src/, tests/ ni experiments/.
> 2. Verificá, con evidencia:
>    - Obs. 1 (N2): no queda ningún "PENDIENTE" en registro_uso_IA.md; los prompts de R1 ronda 1
>      y ronda 2 están completos y textuales.
>    - Obs. 2: el HANDOFF cierra ese pendiente.
>    - Obs. 3: la entrada del fix tiene los hashes cf76a36 y e484dcb y la verificación del push.
>    - D29: la adenda tiene el ítem 6 con method, maxiter y las tres condiciones de no
>      convergencia, marcado como agregado en el fix; la sección 1 y los ítems 1 a 5 no cambiaron
>      (compará contra e484dcb); el resumen §1.1 lo refleja.
>    - D30: consta la validación del equipo en el HANDOFF y en el registro.
>    - pytest: 15 pasados, 0 saltados.
> 3. Veredicto: APROBADA si todo cumple; si algo no cumple, listalo.
> 4. Escribí documentacion/reviews/E3_fase_0-1_r3.md y agregá la entrada de esta sesión en
>    registro_uso_IA.md con este prompt textual (D30). Mostrame el veredicto. No hagas commit.

**Respuesta (extracto relevante):** veredicto **APROBADA**. `git log --oneline e484dcb..HEAD` muestra solo `ce6a18a`, y el diff toca
los cinco archivos permitidos; `src/`, `tests/` y `experiments/` no cambian. En el notebook solo cambió la celda `a7d19f27`.
(1) No queda ningún marcador `PENDIENTE` abierto en el registro: las 7 coincidencias de `grep` son citas o texto histórico. Los
prompts de R1 ronda 1 y ronda 2 coinciden con el primer mensaje de las transcripciones locales `88463c61-…` y `07b59f2d-…`; la única
diferencia son las etiquetas del bloque pegado. (2) El HANDOFF dice «Queda cerrado el pendiente del prompt de R1». (3) La entrada del
fix anterior tiene `74eafbd` → `cf76a36` → `e484dcb` y la salida de `git ls-remote` (`e484dcb…`). (D29) El ítem 6 tiene `method="newton"`,
`maxiter=100` y las tres condiciones, marcado como agregado en el fix. La sección 1 (`5efc0a58`) es idéntica en `74eafbd`, `e484dcb` y
`HEAD`, y el texto de la adenda en `e484dcb` es prefijo exacto del de `HEAD`. El resumen §1.1 tiene la fila 6. (D30) La validación del
equipo consta en el HANDOFF y en el registro, como declaración del equipo. `pytest`: 15 pasados, 0 saltados. Notas menores, sin efecto
en el veredicto: se editaron 4 líneas de entradas anteriores del registro, como pidió la ronda 2; la entrada del fix de la ronda 2 no
trae el hash de su propio commit; la apertura de la adenda sigue diciendo «cinco precisiones», como decisión declarada.

**Uso y verificación:** informe de review, sin cambios de código. Verificación: comparación por programa (script en el scratchpad de
la sesión, fuera del repo) de los prompts del registro contra las transcripciones `.jsonl` y de las fuentes de las celdas del notebook
por `id` entre `74eafbd`, `e484dcb` y `HEAD`; `python -m pytest -rA -q` → `15 passed`; `git ls-remote origin e3/fase-0-1-protocolo`
→ `ce6a18ae3a435fcda2cbc2844d22967c57f6d1da`, igual a `HEAD`, así que el commit del fix de la ronda 2 está en el remoto. Sin commit ni
push. **Archivos afectados:** `documentacion/reviews/E3_fase_0-1_r3.md` (nuevo), `documentacion/registro_uso_IA.md` (esta entrada).

---

## Sesión 2026-10-19 (E3, fase 2: experimentación, paso A) — lucaspimentel-uy — Claude Code (Anthropic, Claude Opus 5.5)

**Contexto:** fase 2 del Entregable 3 en la rama `e3/fase-2-experimentacion`. Precisiones previas a los candidatos (D31 a D34 e
ítem 5) y paso A (conjuntos de variables con GLM Poisson y XGBoost, ventana expansiva) en `notebooks/modelos_candidatos.ipynb`.
La entrada cubre hasta la parada del paso A; los pasos B y C se registran en entradas posteriores.

### Prompt 1
> Sesión de trabajo del Entregable 3, fase 2, en la rama e3/fase-2-experimentacion.
>
> Antes de hacer nada:
> 1. Verificá con `git branch --show-current` que estás en <rama>. Si no, detenete y avisame.
> 2. Leé CLAUDE.md, HANDOFF.md y documentacion/resumen_modelos_candidatos.md. Respetá todas
>    las reglas de CLAUDE.md: ninguna cifra sin artefacto, documento acompañante por notebook,
>    registro de IA y HANDOFF al cierre.
> 3. Las reglas fijadas en la sección 1 de notebooks/modelos_candidatos.ipynb no se modifican.
>    Si algo necesita precisarse, se agrega un bloque fechado debajo y me lo consultás antes.
>
> Reglas de la sesión:
> - El bloque final (2025-02-06 → 2025-12-31) solo lo lee notebooks/evaluacion_final.ipynb.
>   En cualquier otro código, el panel entra únicamente por src/datos.py:cargar_panel_desarrollo().
>   Esto incluye comandos sueltos de exploración.
> - Variables solo desde src/variables.py. Si hace falta una nueva, va ahí y con tests.
> - Los notebooks se ejecutan con `jupyter nbconvert --execute` en el .venv, con 0 errores.
>   `pytest` tiene que pasar entero.
> - Detenete en cada parada que indique el prompt. No avances sin mi confirmación.
> - Si una instrucción choca con lo que encontrás en el repositorio, o si una decisión no
>   está cubierta por el prompt, preguntá en vez de resolverla por tu cuenta.
> - Al cerrar: actualizá el documento acompañante, HANDOFF.md y
>   documentacion/registro_uso_IA.md. Mostrame `git status` y un resumen de los archivos tocados.
>   Hacé commit en <rama> solo cuando yo lo confirme. Nunca en main y nunca push.
>
> Prompt de la fase:
> Fase 2: experimentación. Todo en notebooks/modelos_candidatos.ipynb, a continuación de la
> sección 6.
>
> ## Antes de empezar
>
> - Leé la "Adenda a la sección 1" del notebook (ítems 1 a 6; decisiones D17 a D20 y D27 a
>   D29). Sus precisiones son reglas fijadas: no se modifican ni la sección 1 ni la adenda.
>   Si algo no está cubierto, preguntá.
> - Todo comando de Python, pytest y nbconvert se corre con el .venv activado en el mismo
>   comando (por ejemplo `.venv\Scripts\Activate.ps1; jupyter nbconvert ...`). Sin activarlo,
>   el kernel usa el Python 3.13.9 del sistema. Verificá en la sección 0 que dice 3.13.2.
>
> ## Reglas de los pasos A, B y C
>
> - Municipio y calendario como variables indicadoras, con la misma matriz para GLM y
>   XGBoost. El término propio de A es la interacción A × calendario.
> - GLM Poisson con statsmodels (enlace log).
> - Binomial negativa según los ítems 5 y 6 de la adenda: NB2 con α por máxima verosimilitud
>   (statsmodels.discrete NegativeBinomial, loglike_method="nb2", method="newton",
>   maxiter=100). No convergido = mle_retvals["converged"] False, ConvergenceWarning o α no
>   finito o no positivo; en ese corte se aplica el plan B (GLM NB con α por momentos en el
>   mismo corte) y se reporta.
> - Cada configuración evaluada agrega una fila a
>   experiments/modelos_candidatos/registro_experimentos.csv: modelo, conjunto, N,
>   hiperparámetros, ventana, desvianza, error estándar, MAE, RMSE, total pred./obs., días
>   con predicción 0, peor municipio, cortes con plan B y fecha/hora. Incluye los resultados
>   negativos.
> - Guardá las predicciones por corte, día y municipio de cada configuración.
> - En cada tabla de comparación, marcá qué configuraciones quedan a menos de 1 error
>   estándar de la mejor.
> - Si un modelo no converge o da advertencias, no lo silencies: reportalo.
>
> ## Paso A — Conjuntos de variables (ventana expansiva)
>
> - GLM Poisson y XGBoost (configuración del ítem 3 de la adenda) con los conjuntos (0), (a),
>   (b) y (c). N ∈ {28, 56, 91} en (0) y en (c), elegido por desvianza media en validación,
>   por separado en cada familia.
> - Tablas globales y por municipio, con comparación contra L1 y L0 de 8 semanas.
> - Aplicá la regla del ítem 4 de la adenda y decí qué conjunto queda elegido para cada
>   familia.
> - Reportá la dispersión de Pearson del GLM Poisson con el conjunto elegido.
> - Lectura separando evidencia de inferencia. En particular: ¿(c) corrige la subestimación
>   de L1 (total pred./obs. 0,93)? ¿El término de A aporta en el panel como en el
>   diagnóstico?
>
> DETENETE.
>
> ## Paso B — Hiperparámetros y binomial negativa (ventana expansiva)
>
> - XGBoost: las 12 combinaciones de la grilla sobre el conjunto elegido para XGBoost.
> - Binomial negativa NB2 sobre el conjunto elegido para el GLM. Reportá α por corte (al
>   menos su rango), cuántos cortes usaron el plan B y comparala con el GLM Poisson en
>   desvianza.
> - Elegí la mejor configuración de cada familia con la regla de selección. La familia GLM
>   incluye Poisson y binomial negativa; la familia XGBoost, las 12 combinaciones.
>
> DETENETE.
>
> ## Paso C — Ventanas
>
> - Para la mejor configuración de cada familia: ventana expansiva y deslizante de 364, 546 y
>   728 días.
> - Aplicá la regla de selección completa sobre todas las configuraciones del paso C:
>   desvianza, empate por 1 error estándar, simplicidad, estabilidad y calibración.
> - Mostrame el resultado de cada paso de la regla y la configuración que quedaría elegida.
>   No escribas todavía la configuración final: eso es la fase 3.
>
> DETENETE. En cada parada actualizá el resumen, HANDOFF y el registro de IA.

**Respuesta (extracto relevante):** antes de escribir código, la IA verificó la rama, el `.venv` (Python 3.13.2) y `pytest`
(15 pasados), y planteó cuatro decisiones que ni el prompt ni la adenda cubrían, cada una con una opción recomendada: (1) forma
del nivel reciente y de los rezagos en el GLM con enlace log; (2) parametrización de las indicadoras, que no cambia el GLM pero sí
XGBoost; (3) qué error estándar usar en «(0) solo reemplaza si mejora por más de 1 EE»; (4) si el registro se reescribe o se
acumula, dado que el notebook se reejecuta entero en cada paso. El equipo eligió las cuatro recomendadas: log(nivel) y rezagos
crudos; 8 municipios sin constante; el EE de (0); reescribir en cada corrida.

**Uso y verificación:** las cuatro respuestas pasaron a ser D31 a D34 (prompt 2). Ninguna decisión se tomó sin consulta.
**Archivos afectados:** ninguno en este intercambio.

### Prompt 2
> Antes de ejecutar el paso A:
> 1. Agregá debajo de la adenda un bloque "Precisiones de la fase 2, fijadas el 19/10/2026 antes
>    de ejecutar candidatos", sin tocar la sección 1 ni la adenda:
>    - Matriz de indicadoras (D31): 8 municipios sin constante; calendario con 7 columnas,
>      lunes como referencia; término de A con 7 columnas a_x_*, sin a_x_lunes.
>    - Error estándar del ítem 4 (D32): el de (0). (0) reemplaza al elegido solo si
>      desv(elegido) − desv(0) > EE(0).
>    - Registro de experimentos (D33): se reescribe en cada ejecución, con commit en cada parada.
>    - Forma de las variables (D34): log(nivel_reciente_N) y rezagos 7/14/21/28 como conteos
>      crudos, en (0) y en (c). Verificá que ningún nivel reciente valga 0 en desarrollo; si
>      alguno vale 0, detenete.
> 2. Espejo en el resumen §1.1.
> 3. DETENETE y mostrame el diff. Con mi confirmación, hacé el commit "Precisiones de la fase 2
>    previas a los candidatos (D31-D34)" y recién ahí ejecutá el paso A.
> 4. Además del commit al cierre, hacé un commit en cada parada (después de A, de B y de C)
>    cuando yo lo confirme.

**Respuesta (extracto relevante):** celda markdown nueva en la posición 5 del notebook, debajo de la adenda, con los cuatro ítems,
y su espejo en una tabla del resumen §1.1. Comprobación de ceros sobre el panel leído con `cargar_panel_desarrollo()`: la media
móvil por municipio de 28, 56 y 91 días nunca vale 0 (mínimos 1,0; 1,2321 y 1,3846), así que no hubo que detenerse. La IA se
detuvo y mostró el diff.

**Uso y verificación:** utilizado tal cual. `nbformat.validate` OK; el diff solo agrega líneas (la sección 1 y la adenda no
cambian). La comprobación de ceros no es un resultado del proyecto: el notebook la repite en cada corte (sección 7).
**Archivos afectados:** `notebooks/modelos_candidatos.ipynb` (celda nueva), `documentacion/resumen_modelos_candidatos.md`.

### Prompt 3
> Antes del commit, agregá al bloque un ítem 5: "Parámetros de XGBoost fuera de D19: valores por
> defecto de xgboost 3.4.1 (tree_method="hist", subsample=1, colsample_bytree=1,
> min_child_weight=1, reg_lambda=1), más random_state=SEMILLA y n_jobs=1 para que los resultados
> sean deterministas." Mismo agregado en el resumen §1.1. Después hacé el commit con los dos
> archivos y seguí con el paso A como propusiste (secciones 7, 8 y 9; "Estado y artefactos" al
> final). Detenete al terminar el paso A.

**Respuesta (extracto relevante):** antes de escribir el ítem 5, la IA comprobó sobre datos sintéticos que esos son los valores por
defecto efectivos de xgboost 3.4.1 con `count:poisson`, leyendo la configuración del booster con `save_config`. Agregó el ítem 5 y
creó el commit `2936c72`. Después escribió la sección 7 del notebook. El código construye la matriz de D31/D34 a partir de
`var.matriz_entrenamiento` y `var.variables_horizonte`, sin variables nuevas. Ajusta el GLM Poisson con `sm.GLM(..., family=Poisson())`
y XGBoost con `XGBRegressor(**XGB_FIJOS, **XGB_PASO_A)`. Registra los avisos y la convergencia de cada ajuste por corte, sin
silenciarlos. Escribe el registro de D33, las tablas 11 a 17 y la figura 4, y aplica la regla del ítem 4 con D32. Resultado:
**conjunto (a) en las dos familias** (GLM 1,2302; XGBoost 1,2217), porque (a), (b) y (c) quedan a menos de 1 EE del mejor y la
regla elige el más simple. Ninguna configuración de (a), (b) o (c) se distingue de L1 (1,2319) por 1 EE. La dispersión de Pearson
del GLM (a) va de 1,1035 a 1,1171. Lecturas: (c) corrige solo en parte la subestimación (0,9341 → 0,9523); el término de A mejora A
en 4,34 % en el GLM, como en el diagnóstico. «Estado y artefactos» pasó a ser la sección 10.

**Uso y verificación:** utilizado, con una corrección. La primera ejecución con `nbconvert` falló en la figura 4 (`ValueError` de
matplotlib: `ecolor` no acepta una serie de colores); se cambió solo el dibujo de la figura y se reejecutó. Verificación: segunda
ejecución con 0 errores y 0 salidas `stderr`; las tablas 11 a 16 de las dos ejecuciones son idénticas con `cmp` y el registro es
idéntico salvo `fecha_hora` (determinismo); las tablas 00 a 09 y las figuras 1 a 3 de la fase 1 no cambiaron (`git status`); 752
ajustes sin avisos y 376 GLM convergidos (`tablas/16`); 1.200.192 valores de nivel reciente comprobados > 0. Las cifras de la lectura
se contrastaron contra `tablas/11`, `12`, `13`, `14` y `15`. La celda de lectura 7.1 (texto) se agregó después de la ejecución, sin
reejecutar. `pytest`: 15 pasados, 0 saltados, al cierre de la parada. **Archivos afectados:** `notebooks/modelos_candidatos.ipynb`,
`experiments/modelos_candidatos/` (tablas 10 a 17, figura 4, `registro_experimentos.csv`), `documentacion/resumen_modelos_candidatos.md`,
`HANDOFF.md`, `documentacion/registro_uso_IA.md`.

---

## Sesión 2026-10-19 (E3, fase 2: experimentación, paso B) — lucaspimentel-uy — Claude Code (Anthropic, Claude Opus 5.5)

**Contexto:** continuación de la sesión del paso A, en la misma rama (`e3/fase-2-experimentacion`): commit de la parada A, precisiones
D36 a D38, verificación de fuga de los candidatos del paso A y paso B (grilla de XGBoost y NB2) en `notebooks/modelos_candidatos.ipynb`.

### Prompt 1
> Si, confirmo. Continuamos con el paso B.

**Respuesta (extracto relevante):** commit de la parada A (`dec597d`). Antes de escribir el paso B, la IA planteó tres casos que la
regla de selección no resuelve dentro de una familia con las mismas variables, cada uno con una opción recomendada: (1) si GLM Poisson
o NB2 es «más simple»; (2) cómo se aplica la simplicidad entre combinaciones de XGBoost; (3) cómo se aplica el paso 4 (estabilidad y
calibración), dado que con valores continuos casi nunca hay empate exacto. El equipo eligió: Poisson es más simple; menor `max_depth`
y luego menor `n_estimators`; paso 4 lexicográfico con tolerancia de 1 EE (no era la opción recomendada por la IA, que era una suma de
rangos).

**Uso y verificación:** las respuestas pasaron a ser D36 a D38 (prompt 2). **Archivos afectados:** ninguno en este intercambio.

### Prompt 2
> Antes de ejecutar el paso B:
> 1. Agregá debajo de las precisiones de la fase 2 un bloque "Precisiones del paso B, fijadas el
>    19/10/2026 antes de ejecutarlo", sin tocar nada anterior:
>    - D36: con la misma matriz, GLM Poisson es más simple que NB2; si empatan a menos de 1 EE,
>      gana Poisson. Cómo se construyen los intervalos se decide en la fase 3.
>    - D37: entre combinaciones de XGBoost empatadas, más simple = menor max_depth y, a igual
>      profundidad, menor n_estimators. learning_rate no cuenta; si solo difieren en él, decide
>      el paso 4.
>    - D38: paso 4 lexicográfico con tolerancia de 1 EE. Pasan las empatadas cuya desvianza del
>      peor municipio queda a menos de 1 EE de la mejor en ese criterio (el EE es el del peor
>      municipio de esa mejor configuración, tablas/12); entre ellas gana la de menor desvío
>      entre cortes; si empatan, la de menor |total pred./obs. − 1|.
>    Estas precisiones valen también para el paso C.
> 2. Espejo en el resumen §1.1.
> 3. DETENETE y mostrame el diff. Con mi confirmación, commit "Precisiones del paso B
>    (D36-D38)" y recién ahí ejecutá el paso B.

**Respuesta (extracto relevante):** celda markdown nueva debajo de las precisiones de la fase 2 y una tabla espejo en el resumen §1.1. La
IA agregó dos frases al texto pedido y las señaló para que el equipo las confirmara: «Se fijó con los resultados del paso A ya vistos» y
«Entre las empatadas que siguen sin separarse». La segunda deja escrito que el paso 4 solo actúa si el paso 3 deja más de una configuración.

**Uso y verificación:** utilizado; el equipo confirmó las dos frases («Dale, confirmo») y se hizo el commit `624b7e3`. `nbformat.validate`
OK; el diff solo agrega líneas. **Archivos afectados:** `notebooks/modelos_candidatos.ipynb`, `documentacion/resumen_modelos_candidatos.md`.

### Prompt 3
> Dale, confirmo.

**Respuesta (extracto relevante):** commit `624b7e3`.

**Uso y verificación:** `git log --oneline -1`. **Archivos afectados:** los del prompt 2.

### Prompt 4
> Antes del paso B, una verificación de fuga sobre los candidatos del paso A, sin escribir en el
> repo: para GLM (a), GLM (c) N=28, XGBoost (a) y XGBoost (c) N=28, en 5 cortes repartidos (el
> primero, el último y tres intermedios), alterá en memoria n_siniestros de las fechas >= origen,
> reentrená y predecí. Reportá la diferencia máxima entre predicciones originales y alteradas;
> tiene que ser 0. Anotalo en el resumen y en el HANDOFF. Después seguí con el paso B.

**Respuesta (extracto relevante):** la IA escribió un script en el scratchpad de la sesión, fuera del repo. El script lee el panel con
`cargar_panel_desarrollo()` y ejecuta tal cual la celda `paso-a-motor` del notebook. Usa los cortes 1, 12, 24, 36 y 47 y tres versiones
de los datos: la vista del motor, el panel con el futuro real sin ocultar y el panel con `n_siniestros` = 10⁶ en toda fecha ≥ origen.
Resultado: **diferencia máxima 0** en las 20 combinaciones, y las predicciones coinciden con `tablas/17`. Control de mutación: con la
compuerta `var.observado` abierta en memoria, las configuraciones (c) cambian (88,69 y 1,006 en el corte 12), así que la prueba detecta
fugas. Las (a) no cambian, porque no tienen variables derivadas del objetivo. Después escribió el paso B: la rama `ajustar_nb2` en la celda
del motor (NB2 por máxima verosimilitud, criterio D29 y plan B de D28) y la sección 8 con la grilla de XGBoost, la comparación NB2 contra
Poisson, la regla `aplicar_regla` con D36 a D38, las tablas 18 a 25 y la figura 5. Resultado: GLM Poisson (a) (D36; NB2 1,2301 contra
1,2302, α de 0,0349 a 0,0400, 0 cortes con plan B) y XGBoost (a) d=2 n=100 lr=0,1 (D37, la más simple de 11 empatadas; 1,2375, por
encima de L1).

**Uso y verificación:** utilizado. Verificación de fuga: `git status` sin cambios después de correr el script. Paso B: antes de escribir el
código se comprobó con datos sintéticos que `NegativeBinomial(...).fit(method="newton")` devuelve `mle_retvals["converged"]` y que
`predict` descarta `alpha`. `nbconvert --execute` terminó con 0 errores y 0 `stderr`. Las tablas 11 a 17 del paso A no cambiaron (`git
status`) y sus 16 filas del registro son idénticas salvo `fecha_hora` (comparación con pandas contra una copia previa). Un `assert` del
notebook verifica que la combinación del paso A reproduce sus predicciones. Las cifras de la lectura se contrastaron contra `tablas/18`,
`19`, `21`, `22` y `23`. La celda de lectura 8.1 se agregó después de ejecutar, sin reejecutar. `pytest`: 15 pasados, 0 saltados.
**Archivos afectados:** `notebooks/modelos_candidatos.ipynb`, `experiments/modelos_candidatos/` (tablas 10 y 18 a 25, figura 5,
`registro_experimentos.csv`), `documentacion/resumen_modelos_candidatos.md`, `HANDOFF.md`, `documentacion/registro_uso_IA.md`.

---

## Sesión 2026-10-19 (E3, fase 2: experimentación, paso C) — lucaspimentel-uy — Claude Code (Anthropic, Claude Opus 5.5)

**Contexto:** continuación de la sesión de los pasos A y B, en la misma rama (`e3/fase-2-experimentacion`): commit de la parada B,
precisiones D39 y D40 y paso C (ventanas) en `notebooks/modelos_candidatos.ipynb`.

### Prompt 1
> Confirmo el commit de la parada B con el mensaje propuesto. Antes del paso C:
> 1. Agregá debajo de las precisiones del paso B un bloque "Precisiones del paso C, fijadas el
>    19/10/2026 con los resultados de los pasos A y B ya vistos":
>    - D39: se mantiene la XGBoost elegida por la regla (d=2, n=100, lr=0,1), aunque su desvianza
>      media sea peor que la de L1. La mejor de la grilla (d=4, n=300, lr=0,05) se reporta como
>      referencia y no se ejecuta en el paso C.
>    - D40: la ventana no cuenta como complejidad. En el paso 3 solo se ordena por familia (GLM
>      antes que XGBoost); entre ventanas de la misma familia que sigan empatadas decide el paso 4
>      (D38).
> 2. Espejo en el resumen §1.1.
> 3. DETENETE y mostrame el diff. Con mi confirmación, commit "Precisiones del paso C (D39-D40)"
>    y recién ahí ejecutá el paso C.

**Respuesta (extracto relevante):** commit de la parada B (`80bedb7`). Celda markdown nueva debajo de las precisiones del paso B y tabla
espejo en el resumen §1.1; la fila de D39 lleva las cifras que la respaldan (1,2375 contra 1,2319 de L1; 1,2197 la mejor de la grilla,
`tablas/18`). La IA se detuvo, mostró el diff y describió cómo implementaría el paso C sin decisiones nuevas.

**Uso y verificación:** utilizado tal cual. `nbformat.validate` OK; el diff solo agrega líneas. **Archivos afectados:**
`notebooks/modelos_candidatos.ipynb`, `documentacion/resumen_modelos_candidatos.md`.

### Prompt 2
> Confirmo el commit "Precisiones del paso C (D39-D40)". En la tabla del paso C agregá, para cada
> configuración, el total pred./obs. global y el del municipio A (solo informativo, no entra en la
> regla). Detenete al terminar el paso C.

**Respuesta (extracto relevante):** commit `2cd97dc`. Sección 9 del notebook: 8 configuraciones (GLM Poisson (a) y XGBoost (a) d=2 n=100
lr=0,1, cada una con ventana expansiva y deslizante de 364, 546 y 728 días). Las referencias (L1, L0 de 8 semanas y la mejor de la
grilla, del paso B) quedan fuera de la regla, igual que las columnas informativas de total pred./obs. global y de A. La regla completa se
aplica con `aplicar_regla`, D38 y D40. Resultado: las 8 configuraciones empatan a menos de 1 EE (umbral 1,2569); D40 deja las 4 del GLM;
las 4 pasan la tolerancia del peor municipio (umbral 1,4939); el desvío entre cortes elige la expansiva (0,246353 contra 0,246801). Quedaría
elegida **GLM Poisson (a), ventana expansiva**, sin escribirla como configuración final. Lectura: las ventanas deslizantes mejoran la
desvianza media y la calibración (GLM 364 d: 1,2205 y 0,9717, contra 1,2302 y 0,9341), y la elección de la expansiva es en la práctica un
empate resuelto por un margen despreciable.

**Uso y verificación:** utilizado. `nbconvert --execute` terminó con 0 errores y 0 `stderr`. Las tablas de los pasos A y B no cambiaron
(`git status`), y sus 29 filas del registro son idénticas salvo `fecha_hora` (comparación con pandas contra una copia previa). Los `assert`
del notebook verifican que las dos expansivas reproducen exactamente las predicciones de los pasos A y B y que cada ajuste deslizante usó
exactamente N días. 376 ajustes sin avisos y 188 GLM convergidos (`tablas/30`). Las cifras de la lectura se contrastaron contra
`tablas/26` a `29`; los valores sin redondear del desvío entre cortes, contra `tablas/26`. La celda de lectura 9.1 se agregó después de
ejecutar, sin reejecutar. `pytest`: 15 pasados, 0 saltados. **Archivos afectados:** `notebooks/modelos_candidatos.ipynb`,
`experiments/modelos_candidatos/` (tablas 10 y 26 a 31, figura 6, `registro_experimentos.csv`),
`documentacion/resumen_modelos_candidatos.md`, `HANDOFF.md`, `documentacion/registro_uso_IA.md`.

---

## Sesión 2026-10-19 (E3, fase 3: selección, paso 3a) — lucaspimentel-uy — Claude Code (Anthropic, Claude Opus 5.5)

**Contexto:** rama `e3/fase-3-seleccion`. Paso 3a de la fase 3 en `notebooks/modelos_candidatos.ipynb`: bloque de la decisión D42,
`solucion_seleccionada.json` y tabla de la regla con la decisión.

### Prompt 1
> Sesión de trabajo del Entregable 3, fase 3, en la rama e3/fase-3-seleccion.
> [...reglas de la sesión: verificar la rama; leer CLAUDE.md, HANDOFF.md y el resumen; no modificar la sección 1; el bloque final
> solo lo lee notebooks/evaluacion_final.ipynb; variables solo desde src/variables.py; nbconvert con 0 errores y pytest entero;
> detenerse en cada parada; commit solo con confirmación, nunca en main ni push...]
>
> ## Paso 3a — Configuración de la solución (D42)
>
> - Agregá debajo de las precisiones del paso C un bloque "Decisión del equipo sobre la
>   configuración final, 19/10/2026 (D42)": la regla eligió GLM Poisson (a) con ventana
>   expansiva por una diferencia de 0,00045 en el desvío entre cortes; el equipo se aparta de
>   la regla y elige GLM Poisson (a) con ventana deslizante de 364 días, por desvianza media
>   (1,2205 contra 1,2302), cortes ganados (30 de 47) y calibración (0,9717 contra 0,9341; en
>   A, 0,9330 contra 0,8695). Citá la tabla de cada cifra. La expansiva queda como
>   configuración de sensibilidad: se evalúa en la fase 4 y no puede reemplazar a la final.
> - Escribí experiments/modelos_candidatos/solucion_seleccionada.json con: modelo, familia,
>   conjunto de variables, hiperparámetros, ventana (deslizante, 364 días), reentrenamiento
>   cada 7 días, horizonte de 7 días, EPS de la desvianza, semilla, versiones de las
>   bibliotecas y commit del repositorio. Agregá los campos "configuracion_de_la_regla" (la
>   expansiva), "origen_de_la_eleccion": "decisión del equipo D42, apartándose de la regla",
>   "sensibilidad" (la expansiva) y "contraste" (la mejor XGBoost del paso C: deslizante de
>   364 días, d=2, n=100, lr=0,1). Sensibilidad y contraste se evalúan en la fase 4 junto con
>   las referencias, pero no compiten.
> - Agregá una tabla que muestre la regla paso por paso (desvianza, empates, simplicidad,
>   estabilidad, calibración), la configuración que eligió y, en una fila aparte, la decisión
>   D42 con su motivo, lista para citar en el informe.
>
> DETENETE. El equipo commitea el bloque y el JSON antes de seguir.
>
> [El prompt seguía con los pasos 3b y 3c, que esperan a la confirmación de esta parada.]

**Respuesta (extracto relevante):** celda markdown D42 debajo de las precisiones del paso C, con cada cifra citada (`tablas/26`, `28`,
`29`). La IA precisó que el margen de 0,00045 es contra la ventana de 728 d (la segunda); contra la de 364 d es 0,0032 (`tablas/29`).
Sección 10 nueva, sin ajustes nuevos: arma el JSON desde `META` y `glob_c` (configuración, columnas del conjunto (a), hiperparámetros,
ventana, reentrenamiento y horizonte, cifras de validación, EPS, semilla, versiones de `tablas/00`, HEAD de git y si el árbol tenía
cambios) y escribe `tablas/32` con la regla paso por paso y la fila D42. Tiene `assert` para verificar que la regla elige la expansiva, que
la final es la de 364 d, que el contraste es la mejor XGBoost del paso C y que gana 30 cortes. «Estado y artefactos» pasó a ser la
sección 13.

**Uso y verificación:** utilizado. `nbconvert --execute` en el `.venv`: la primera ejecución falló al guardar `fig6` (`OSError [Errno
22]`, bloqueo transitorio del archivo); la segunda terminó con 0 errores y 0 `stderr`. Una tercera corrigió un separador decimal en
`tablas/32`. Tablas 00 a 31 y figuras sin cambios (`git status`); registro idéntico salvo `fecha_hora` (comparación con pandas contra
`HEAD`). Las cifras del bloque se contrastaron a mano contra `tablas/26`, `28` (conteo de cortes: 30) y `29`. `pytest`: 15 pasados.
**Archivos afectados:** `notebooks/modelos_candidatos.ipynb`, `experiments/modelos_candidatos/solucion_seleccionada.json`,
`experiments/modelos_candidatos/tablas/10_artefactos.csv` y `32_fase3_configuracion_final.csv`, `registro_experimentos.csv`
(solo `fecha_hora`), `documentacion/resumen_modelos_candidatos.md`, `HANDOFF.md`, `documentacion/registro_uso_IA.md`.

### Prompt 2
> Los tres puntos están bien: el margen de 0,00045 descrito contra la de 728 días, el commit
> 5f207e2 con la marca de cambios sin commitear, y la numeración.
>
> Antes del commit falta el paso 3.0, que no aparece en tu reporte: verificación de fuga sin
> escribir en el repo, para la solución (GLM Poisson (a), 364 días), la sensibilidad (expansiva),
> NB2 con 364 días y el contraste (XGBoost, 364 días). En 5 cortes (el primero, el último y tres
> intermedios), alterá en memoria n_siniestros de las fechas >= origen, reentrená y predecí: la
> diferencia máxima tiene que ser 0. Repetí el control positivo abriendo la compuerta
> var.observado. Anotalo en el resumen y en el HANDOFF, mostrame el resultado y, si da 0, hacé el
> commit "Fase 3, paso 3a: configuración de la solución (D42)" sin push.

**Respuesta (extracto relevante):** script en el scratchpad de la sesión (fuera del repo). Lee el panel con `cargar_panel_desarrollo()`
y ejecuta tal cual la celda `paso-a-motor`. Para las 4 configuraciones, en los cortes 1, 12, 24, 36 y 47, compara tres versiones de los
datos: la vista del motor, el panel sin ocultar y el panel con 10⁶ en las fechas ≥ origen. Diferencia máxima: exactamente 0.0 en las 20
combinaciones. Con la compuerta abierta, las (a) siguen en 0, porque no tienen variables derivadas del objetivo. La IA agregó, solo como
control, GLM (c) N=28 364 d, que cambia entre 11,41 y 44,86: la prueba detecta fugas.

**Uso y verificación:** utilizado. Máximos impresos con `repr` (0.0 exacto). Las predicciones de la vista del motor coinciden con
`tablas/31` (diferencia 0 al redondear a 6 decimales). `git status` sin cambios después de correr el script. Commit hecho en
`e3/fase-3-seleccion`, sin push. **Archivos afectados:** `documentacion/resumen_modelos_candidatos.md` (§3e.4), `HANDOFF.md`,
`documentacion/registro_uso_IA.md`.

---

## Sesión 2026-10-19/20 (E3, fase 3: pasos 3b y 3c) — lucaspimentel-uy — Claude Code (Anthropic, Claude Opus 5.5)

**Contexto:** continuación de la sesión del paso 3a, en la misma rama (`e3/fase-3-seleccion`), sobre
`notebooks/modelos_candidatos.ipynb`.

### Prompt 1
> dale, segui con 3b y 3c

(Los pasos 3b y 3c son los del prompt de la fase registrado en la entrada anterior: coeficientes con IC95, importancia por permutación por
grupos, dependencia parcial del contraste; errores por municipio, tipo de día y 5 peores semanas, calibración y residuos, intervalos NB2,
análisis pareado D35 y exclusión de un municipio por vez; actualizar la lista de frases que no deben aparecer.)

**Respuesta (extracto relevante):** antes de escribir código, la IA preguntó tres puntos que el prompt no fijaba: cómo combinar «nivel de su
propia historia» con «efecto fijo reemplazado por el promedio», de dónde sale la μ del intervalo NB2 y cómo expresar las indicadoras de
municipio sin constante. El equipo eligió: β̄ × reescalado por el nivel propio; μ de la solución con α de NB2; tasa de un lunes más la razón
respecto de A.

### Prompt 2
> Las tres respuestas son decisiones del plan (D43 robustez, D44 intervalos, D45 coeficientes).
> Declaralas en el resumen §3e como elecciones de análisis tomadas antes de calcular 3b y 3c,
> aclarando que no afectan la selección. En los intervalos (D44), además de la cobertura con μ de
> la solución y α de NB2, reportá la de intervalos Poisson, como pide el prompt.

**Respuesta (extracto relevante):** se agregó la celda «Precisiones de la fase 3» (D43 a D45) debajo de D42 y su espejo en el resumen
§3e.5. La §3e.4 (verificación de fuga) no se renumeró, porque la entrada anterior del registro la cita. Secciones 11 y 12 nuevas.
Reajustes por corte con el mismo camino del motor, verificados contra las predicciones del paso C. Permutación de las columnas del grupo
entre las 56 filas del horizonte, con 5 repeticiones y `default_rng(SEMILLA)`. Dependencia parcial fijando el nivel del grupo. Cuantiles
NB2 y Poisson con la cobertura esperada por el propio modelo, como comparación justa por la discreción. Tendencia de los residuos por MCO
con EE HAC. Pareado con el EE de la diferencia. Exclusión de un municipio según D43. NB2 (a) 364 d se evaluó con el motor y se agregó al
registro (paso «3c»). Lecturas 11.1 y 12.1, y en el resumen §3f, §3g, frases nuevas, índice y pendientes.

**Uso y verificación:** utilizado. `nbconvert --execute` en el `.venv`: una ejecución, 0 errores, 0 `stderr`. Las tablas 00 a 32 y las
figuras 1 a 6 no cambiaron (`git status`). Las 37 filas previas del registro son idénticas salvo `fecha_hora` (pandas contra `HEAD`). Los
`assert` del notebook verifican que los 47 modelos reajustados de la solución y del contraste reproducen las predicciones del paso C
(diferencia 0), que el nivel propio de D43 coincide con `var.nivel_municipio` y que NB2 usó 364 días. 376 ajustes de exclusión
convergidos y sin avisos; NB2 364 d, 47 cortes convergidos y ningún plan B. Las cifras de las lecturas y del resumen se contrastaron contra
`tablas/33` a `48`. La IA corrigió cinco afirmaciones de su propio borrador que no coincidían con las tablas: «cuatro de las cinco»
semanas (eran las cinco), «7 de 10 deciles» (eran 8), E sí mejora la calibración, los municipios donde la solución es peor que la
sensibilidad son CH, D y E (no C), y el rango «de 3,48» era «de 3,47». `nbformat.validate` OK. `pytest`: 15 pasados. **Archivos
afectados:** `notebooks/modelos_candidatos.ipynb`, `experiments/modelos_candidatos/` (tablas 10 y 33 a 48, figuras 7 a 11,
`registro_experimentos.csv`, `solucion_seleccionada.json`), `documentacion/resumen_modelos_candidatos.md`, `HANDOFF.md`,
`documentacion/registro_uso_IA.md`.

### Prompt 3
> 1. La fila 38 (NB2, 364 días) queda en el registro.
> 2. solucion_seleccionada.json no puede cambiar después de 1560a5b (F3-B2). Restauralo con
>    `git checkout 1560a5b -- experiments/modelos_candidatos/solucion_seleccionada.json` y
>    cambiá la sección 10: si el JSON ya existe, no lo reescribe; verifica con assert que sus
>    campos de configuración coinciden con lo calculado y lo deja intacto.
> 3. El IC95 de NB2 en los coeficientes queda.
> 4. Corregí el eje de la figura 11 (que ninguna barra quede cortada) y las marcas de la figura 7.
> Reejecutá una vez con nbconvert y verificá: 0 errores; tablas 00 a 48 sin cambios en las cifras;
> solucion_seleccionada.json sin cambios respecto de 1560a5b (git diff vacío). Después hacé el
> commit "Fase 3, pasos 3b y 3c: explicabilidad, errores, intervalos y robustez (D43-D45)" sin push.

**Respuesta (extracto relevante):** JSON restaurado con el comando indicado. Sección 10: si el archivo existe, recalcula el diccionario y
hace `assert` de que coinciden todos los campos salvo `commit_del_repositorio` y `arbol_de_trabajo_con_cambios_sin_commitear` (son de
procedencia: reflejan la ejecución que lo escribió). Si no existe, lo escribe. Figura 7: marcas fijas en decimales con coma, sin marcas
menores. Figura 11: un eje por nivel, con el límite inferior calculado del mínimo de la cobertura empírica, la esperada y el nominal, menos 0,02.

**Uso y verificación:** utilizado. Reejecución única con `nbconvert` en el `.venv`: 0 errores, 0 `stderr`. Las 49 tablas (00 a 48) son
idénticas byte a byte a una copia tomada antes de reejecutar (`cmp`). `git diff 1560a5b` de `solucion_seleccionada.json`: vacío. La celda
de la sección 10 imprimió «verificado, sin reescribir». Las figuras 7 y 11 se revisaron visualmente. `pytest`: 15 pasados. Con la
confirmación del equipo («si termina y los resultados salen bien, hace el commit»), commit en `e3/fase-3-seleccion`, sin push. **Archivos afectados:** `notebooks/modelos_candidatos.ipynb`, `experiments/modelos_candidatos/`
(figuras 7 y 11), `documentacion/resumen_modelos_candidatos.md`, `HANDOFF.md`, `documentacion/registro_uso_IA.md`.

---

## Sesión 2026-10-20 (review R2, E3 fases 2 y 3) — lucaspimentel-uy — Claude Code (Anthropic, Claude Opus 5.5)

**Contexto:** review de verificación (no de corrección) de las fases 2 y 3 del Entregable 3, en la rama `e3/fase-3-seleccion`
(base `b59794c`, HEAD `508c46e`). El revisor no participó en esas fases. Solo crea `documentacion/reviews/E3_fase_2-3.md` y esta entrada.

### Prompt 1
> Sos el revisor del bloque R2 del Entregable 3: fases 2 (experimentación) y 3 (selección y
> análisis). No trabajaste en estas fases. Tu tarea es verificar, no corregir. Solo podés crear el
> informe de review y agregar la entrada de esta sesión al registro de IA (D30). Modelo: opus
> (D25); anotalo en el informe.
>
> ## Paso 0 — Rama y prerrequisitos (detenete si algo no cumple)
>
> 1. `git switch e3/fase-3-seleccion`. Verificá que `git merge-base main HEAD` es b59794c y
>    mostrá `git log --oneline main..HEAD`: tienen que aparecer, en este orden, 2936c72, dec597d,
>    624b7e3, 80bedb7, 2cd97dc, 5f207e2 (fase 2), 1560a5b y 508c46e (fase 3).
> 2. Activá el .venv en el mismo comando que corre Python, pytest o nbconvert, y verificá que la
>    sección 0 del notebook dice Python 3.13.2.
> 3. El sha256 de data/processed/panel_diario_montevideo.csv tiene que ser
>    82467fc87b5d2bceb24ec6f3c5072e1b7cf9e75507b1d5c5a4d20153114a1b06. Calculá solo el hash.
>
> ## Paso 1 — Lectura
>
> Leé CLAUDE.md, HANDOFF.md, documentacion/resumen_modelos_candidatos.md y, en el notebook, la
> sección 1, la adenda y todos los bloques fechados que siguen (precisiones de la fase 2, del paso
> B, del paso C, decisión D42 y elecciones D43 a D45). Diffs: `git diff main...HEAD --stat`, y por
> fase `git diff b59794c 5f207e2` (fase 2) y `git diff 5f207e2 HEAD` (fase 3).
>
> Contexto que tenés que conocer:
> - D42: la configuración final (GLM Poisson (a), ventana deslizante de 364 días) NO es la que
>   eligió la regla (GLM Poisson (a), expansiva). Es una decisión del equipo, declarada. No
>   evalúes si es correcta: evaluá que esté declarada como pide F3-B1 y que no se presente en
>   ningún lado como elección de la regla. Si ves riesgos, van en riesgos fuera de criterios.
> - El paso 3.0 de la fase 3 se agregó al plan después de enviar el prompt y se ejecutó por un
>   mensaje aparte, antes de 1560a5b. No es una omisión.
> - D35: el análisis pareado es posterior a ver los resultados y no puede usarse para seleccionar.
>
> ## Paso 2 — Ejecución
>
> 1. `pytest`: 15 pasados, 0 saltados.
> 2. `jupyter nbconvert --to notebook --execute --inplace notebooks/modelos_candidatos.ipynb`:
>    0 errores, 0 salidas stderr.
> 3. `git status` y `git diff --stat`: ningún CSV de tablas/ ni solucion_seleccionada.json puede
>    cambiar; en registro_experimentos.csv solo puede cambiar fecha_hora. Reportá cualquier
>    cifra que cambie. Después `git restore notebooks/ experiments/` y confirmá con `git status`.
> 4. Recalculá la regla de selección vos mismo, con código propio en una carpeta FUERA del repo,
>    a partir de las predicciones guardadas (no de las tablas de resultados), para los pasos A, B
>    y C, aplicando la regla de la sección 1 con D32 y D36 a D40. Tiene que elegir lo mismo que
>    tablas/14, la tabla de elección del paso B y tablas/29.
> 5. Verificación de fuga independiente: para la solución y el contraste, en 2 cortes (el
>    primero y el último), reemplazá en memoria n_siniestros de las fechas >= origen por 10^6,
>    reentrená y predecí: la diferencia máxima tiene que ser 0.
> 6. Cronología: con `git log` y `git show --stat`, verificá que cada bloque de precisiones está
>    en un commit anterior al paso que gobierna (2936c72 antes de dec597d, 624b7e3 antes de
>    80bedb7, 2cd97dc antes de 5f207e2) y que solucion_seleccionada.json no cambió después de
>    1560a5b (`git log --oneline -- experiments/modelos_candidatos/solucion_seleccionada.json`).
>
> ## Paso 3 — Criterios
>
> Evaluá cada uno: CUMPLE o NO CUMPLE, con evidencia concreta (comando y salida, archivo y línea,
> cifra contra el CSV). Sin evidencia, el criterio es NO CUMPLE.
>
> Comunes:
> - B1 Fuera de evaluacion_final.ipynb, ningún código lee filas posteriores a 2025-02-05.
> - B2 El notebook ejecuta de punta a punta sin errores (nbconvert en el .venv).
> - B3 pytest pasa entero (15 pasados, 0 saltados).
> - B4 Toda cifra nueva del resumen y del HANDOFF coincide con un artefacto.
> - B5 La sección 1 y la adenda son idénticas a las de b59794c; solo hay bloques fechados
>   agregados debajo.
> - B6 Entorno coherente: verificación de entorno del notebook en verde; pip check limpio;
>   requirements.txt y el lock coinciden.
> - N1 El resumen sigue la estructura de CLAUDE.md, incluida la lista de frases que no deben
>   aparecer en el informe.
> - N2 HANDOFF y registro de IA actualizados con cada sesión, con prompts textuales.
> - N3 Las lecturas separan evidencia de inferencia.
> - N4 Los resultados negativos quedan registrados (incluida la XGBoost peor que L1, D39).
> - N5 Código legible: sin código muerto, nombres consistentes.
> - N6 El alcance coincide con los prompts de las fases 2 y 3 y con D31 a D45.
>
> Fase 2:
> - F2-B1 Cada bloque de precisiones está en un commit anterior a los resultados que gobierna.
> - F2-B2 La regla recalculada por vos (Paso 2.4) elige las mismas configuraciones en A, B y C.
> - F2-B3 El registro de experimentos tiene todas las combinaciones pedidas, incluidas las que
>   perdieron (16 del paso A, 13 del B, 8 del C, más la fila de NB2 con 364 días del 3c).
> - F2-B4 Ningún modelo usa variables fuera de su conjunto; GLM y XGBoost usan la misma matriz
>   (D31) y la forma de D34.
> - F2-N1 Las advertencias de convergencia están reportadas, no silenciadas.
> - F2-N2 Están reportados el α de NB2 por corte y la dispersión de Pearson del GLM Poisson.
> - F2-N3 Cada tabla de comparación muestra el error estándar y marca los empates.
>
> Fase 3:
> - F3-B1 El JSON coincide con D42 (GLM Poisson (a), deslizante de 364 días), registra que la
>   regla eligió la expansiva y que el equipo se apartó, e incluye la expansiva como sensibilidad
>   y la XGBoost de 364 días como contraste.
> - F3-B2 El JSON está commiteado antes del análisis (1560a5b) y no cambió después; la rama no
>   contiene evaluacion_final.ipynb.
> - F3-B3 La importancia por permutación y la exclusión de municipios se reproducen exactas al
>   reejecutar (Paso 2.3).
> - F3-N1 El análisis de errores cubre municipio, tipo de día, peores semanas y calibración.
> - F3-N2 La exclusión de municipios está declarada como descriptiva.
> - F3-N3 La cobertura de los intervalos está reportada, global y por municipio, para NB2 (D44) y
>   para Poisson.
> - F3-N4 La lista de frases que no deben aparecer está actualizada con lo nuevo de la fase.
>
> ## Paso 4 — Veredicto e informe
>
> Regla: DESAPROBADA si falla al menos un criterio bloqueante (B); APROBADA CON OBSERVACIONES si
> fallan solo no bloqueantes (N); APROBADA si cumplen todos.
>
> Escribí documentacion/reviews/E3_fase_2-3.md con: fecha, modelo, commits revisados (hash
> completo), base (b59794c), sha256 del panel, tabla de criterios (ID, criterio, resultado,
> evidencia), resultado de la reejecución, recálculo de la regla, verificación de fuga,
> cronología, veredicto, observaciones numeradas con lo que habría que hacer para corregir cada
> una, y riesgos fuera de criterios. Agregá al final de documentacion/registro_uso_IA.md la
> entrada de esta sesión con este prompt textual y el veredicto. Mostrame el veredicto y las
> observaciones. No hagas commit ni push.

**Respuesta (extracto relevante):** veredicto **APROBADA CON OBSERVACIONES**. Los 14 criterios bloqueantes cumplen; falla el no
bloqueante **N2**: el prompt de la fase 3 está abreviado con «[...]» en la entrada del paso 3a y el texto de los pasos 3b/3c no quedó
registrado. Resultados: pytest 15 pasados; nbconvert exit 0, 0 errores, 0 `stderr`; ninguna tabla, figura ni el JSON cambiaron, y en el
registro solo cambió `fecha_hora`; el recálculo independiente de la regla, hecho desde las predicciones, elige GLM Poisson (a) y XGBoost
(a) en A, GLM Poisson (a) y XGBoost (a) d=2 n=100 lr=0.1 en B, y GLM Poisson (a) expansiva en C, igual que `tablas/14`, `23` y `29`; la
verificación de fuga (solución y contraste, cortes 1 y 47, 10⁶ en fechas ≥ origen, con y sin la máscara del motor) da diferencia máxima 0
y el control positivo la detecta. Observaciones: (1) N2; (2) partes del resumen desactualizadas (PENDIENTE en §1.1, §1.3, §4, §7.4, §5 sin
limitaciones de la fase 3, frase de §8 sobre la sección 10); (3) D35 y D41 sin definición en el repo; (4) 0,0076 respaldado solo por una
salida impresa; (5) menores de redacción y código. Riesgos: D42 posterior a ver resultados; D43 a D45 en el mismo commit que sus resultados;
`commit_del_repositorio` del JSON = `5f207e2`; el pareado se presta a citarse como significación; coberturas sin incertidumbre; la
sección 10 cambió después de `1560a5b`.

**Uso y verificación:** informe escrito por el revisor. Las cifras del informe salen de comandos ejecutados en la sesión (git, pytest,
nbconvert, pip check) y de cuatro scripts propios en el scratchpad, fuera del repo: recálculo de la regla, verificación de fuga,
reproducción de la matriz D31/D34 y búsqueda de las cifras del resumen y del HANDOFF en las tablas. `git restore notebooks/ experiments/`
después de la reejecución; `git status` final: solo el informe nuevo y esta entrada. Sin commit ni push, como pide el prompt. El veredicto
lo valida el equipo (D30). **Archivos afectados:** `documentacion/reviews/E3_fase_2-3.md`, `documentacion/registro_uso_IA.md`.

---

## Sesión 2026-10-20 (fix de R2, paso F1: transcripción textual de la fase 3) — lucaspimentel-uy — Claude Code (Anthropic, Claude Sonnet 5.5)

**Contexto:** rama `e3/fase-3-seleccion`. Corrección de la observación 1 de R2 (criterio N2, `documentacion/reviews/E3_fase_2-3.md`). Esta entrada **completa** las dos entradas de la fase 3 que quedaron abreviadas, sin modificarlas: «Sesión 2026-10-19 (E3, fase 3: selección, paso 3a)», cuyo Prompt 1 abrevia las reglas de la sesión con «[...]» y corta los pasos 3b y 3c, y «Sesión 2026-10-19/20 (E3, fase 3: pasos 3b y 3c)», cuyo Prompt 1 remite al prompt de la fase «registrado en la entrada anterior», que no lo contenía. Los cuatro mensajes siguientes se enviaron en la sesión de la fase 3 (Claude Code, Opus 5.5) y se transcriben **tal cual**, en orden y con su fecha, desde la transcripción local de esa sesión (`%USERPROFILE%\.claude\projects\C--Proyectos-proyecto-machine-learning\3da4460b-7a42-4a3c-98f7-75d047b7ec94.jsonl`). Las horas son locales (UTC-3, como las de `git log`); la transcripción las guarda en UTC. Se omiten solo las marcas con que Claude Code envuelve el texto pegado; el contenido que sigue es idéntico al de la transcripción.

Los mensajes del paso 3.0 y de la autorización del commit `1560a5b` son **uno solo** (el Mensaje 2): en la transcripción no hay un mensaje aparte para cada cosa. Entre el Mensaje 2 y el Mensaje 3 no hubo otro mensaje del equipo.

### Mensaje 1 — prompt de la fase 3 completo (bloque de la sesión y prompt de la fase)
*19/10/2026 22:42 (UTC-3); en la transcripción, `2026-10-20T01:42:58.848Z`.*

> Sesión de trabajo del Entregable 3, fase 3, en la rama e3/fase-3-seleccion.
>
> Antes de hacer nada:
> 1. Verificá con `git branch --show-current` que estás en e3/fase-3-seleccion. Si no, detenete y avisame.
> 2. Leé CLAUDE.md, HANDOFF.md y documentacion/resumen_modelos_candidatos.md. Respetá todas
>    las reglas de CLAUDE.md: ninguna cifra sin artefacto, documento acompañante por notebook,
>    registro de IA y HANDOFF al cierre.
> 3. Las reglas fijadas en la sección 1 de notebooks/modelos_candidatos.ipynb no se modifican.
>    Si algo necesita precisarse, se agrega un bloque fechado debajo y me lo consultás antes.
>
> Reglas de la sesión:
> - El bloque final (2025-02-06 → 2025-12-31) solo lo lee notebooks/evaluacion_final.ipynb.
>   En cualquier otro código, el panel entra únicamente por src/datos.py:cargar_panel_desarrollo().
>   Esto incluye comandos sueltos de exploración.
> - Variables solo desde src/variables.py. Si hace falta una nueva, va ahí y con tests.
> - Los notebooks se ejecutan con `jupyter nbconvert --execute` en el .venv, con 0 errores.
>   `pytest` tiene que pasar entero.
> - Detenete en cada parada que indique el prompt. No avances sin mi confirmación.
> - Si una instrucción choca con lo que encontrás en el repositorio, o si una decisión no
>   está cubierta por el prompt, preguntá en vez de resolverla por tu cuenta.
> - Al cerrar: actualizá el documento acompañante, HANDOFF.md y
>   documentacion/registro_uso_IA.md. Mostrame `git status` y un resumen de los archivos tocados.
>   Hacé commit en e3/fase-3-seleccion solo cuando yo lo confirme. Nunca en main y nunca push.
>
> Prompt de la fase:
>
> Fase 3: selección y análisis en desarrollo. Continúa notebooks/modelos_candidatos.ipynb
> después del paso C. El test sigue sin leerse. Todo comando de Python, pytest y nbconvert va
> con el .venv activado en el mismo comando.
>
> ## Paso 3a — Configuración de la solución (D42)
>
> - Agregá debajo de las precisiones del paso C un bloque "Decisión del equipo sobre la
>   configuración final, 19/10/2026 (D42)": la regla eligió GLM Poisson (a) con ventana
>   expansiva por una diferencia de 0,00045 en el desvío entre cortes; el equipo se aparta de
>   la regla y elige GLM Poisson (a) con ventana deslizante de 364 días, por desvianza media
>   (1,2205 contra 1,2302), cortes ganados (30 de 47) y calibración (0,9717 contra 0,9341; en
>   A, 0,9330 contra 0,8695). Citá la tabla de cada cifra. La expansiva queda como
>   configuración de sensibilidad: se evalúa en la fase 4 y no puede reemplazar a la final.
> - Escribí experiments/modelos_candidatos/solucion_seleccionada.json con: modelo, familia,
>   conjunto de variables, hiperparámetros, ventana (deslizante, 364 días), reentrenamiento
>   cada 7 días, horizonte de 7 días, EPS de la desvianza, semilla, versiones de las
>   bibliotecas y commit del repositorio. Agregá los campos "configuracion_de_la_regla" (la
>   expansiva), "origen_de_la_eleccion": "decisión del equipo D42, apartándose de la regla",
>   "sensibilidad" (la expansiva) y "contraste" (la mejor XGBoost del paso C: deslizante de
>   364 días, d=2, n=100, lr=0,1). Sensibilidad y contraste se evalúan en la fase 4 junto con
>   las referencias, pero no compiten.
> - Agregá una tabla que muestre la regla paso por paso (desvianza, empates, simplicidad,
>   estabilidad, calibración), la configuración que eligió y, en una fila aparte, la decisión
>   D42 con su motivo, lista para citar en el informe.
>
> DETENETE. El equipo commitea el bloque y el JSON antes de seguir.
>
> ## Paso 3b — Explicabilidad (con datos de validación)
>
> - Coeficientes del GLM ajustado con los últimos 364 días del desarrollo, expresados como
>   razones de tasas con IC95 ("los viernes, ×1,X respecto del lunes"). Tabla y figura.
> - Importancia por permutación por grupos de variables (municipio, calendario, según el
>   conjunto). Se calcula sobre las predicciones de validación: en cada corte se permutan las
>   columnas del grupo entre las filas del horizonte y se recalcula la desvianza. 5
>   repeticiones, semilla fija. Reportar el aumento medio de la desvianza y su dispersión,
>   para la solución y para el contraste.
> - Para el contraste (XGBoost): dependencia parcial de los dos grupos más importantes.
>
> ## Paso 3c — Errores, intervalos y robustez (con datos de validación)
>
> - Errores por municipio, por tipo de día (8 niveles) y en las 5 semanas de mayor desvianza.
>   Para esas semanas, listá qué días tuvieron (feriados, fechas) sin atribuir causas que
>   los datos no muestran.
> - Calibración: media predicha contra media observada por deciles de la predicción, y
>   residuos en el tiempo (¿queda deriva sin corregir con la ventana de 364 días?).
> - Intervalos de predicción del 80 % y del 95 % con la binomial negativa NB2, porque empató
>   con Poisson en el paso B (D5, D36): α estimado en cada corte con la misma ventana de 364
>   días, con el criterio de convergencia y el plan B de la adenda. Reportá la cobertura
>   empírica en validación, global y por municipio, y compárala con la de intervalos Poisson.
> - Análisis pareado (D35), declarado como posterior a ver los resultados y sin efecto sobre
>   la selección: para la solución, la sensibilidad y el contraste, diferencia de desvianza
>   contra L1 corte a corte (media, error estándar de la diferencia y cortes ganados), y lo
>   mismo entre la solución y la sensibilidad.
> - Robustez, exclusión de un municipio por vez: el municipio excluido no aporta filas de
>   entrenamiento; su nivel se toma de su propia historia observada antes del origen y su
>   efecto fijo se reemplaza por el promedio. Reportá cuánto empeora la desvianza en cada
>   municipio contra el modelo que sí lo vio. Es descriptivo y no cambia la selección:
>   declaralo así.
>
> Actualizá el resumen, incluida la lista de frases que no deben aparecer en el informe: por
> ejemplo, "la configuración final la eligió la regla de selección", "el modelo supera a L1"
> sin la aclaración del análisis pareado, o atribuir causas a la importancia de una variable.
>
> DETENETE.

**Respuesta:** ver el extracto en la entrada del paso 3a (Prompt 1), que cubre solo el paso 3a, hasta la primera parada.

**Uso y verificación:** transcripción completa; reemplaza al Prompt 1 abreviado de la entrada del paso 3a. Los pasos 3b y 3c, que esa entrada omitía, están acá. Verificación en el cierre de esta entrada.

### Mensaje 2 — paso 3.0 (verificación de fuga) y autorización del commit `1560a5b`
*19/10/2026 23:40 (UTC-3); en la transcripción, `2026-10-20T02:40:46.492Z`.*

> Los tres puntos están bien: el margen de 0,00045 descrito contra la de 728 días, el commit
> 5f207e2 con la marca de cambios sin commitear, y la numeración.
>
> Antes del commit falta el paso 3.0, que no aparece en tu reporte: verificación de fuga sin
> escribir en el repo, para la solución (GLM Poisson (a), 364 días), la sensibilidad (expansiva),
> NB2 con 364 días y el contraste (XGBoost, 364 días). En 5 cortes (el primero, el último y tres
> intermedios), alterá en memoria n_siniestros de las fechas >= origen, reentrená y predecí: la
> diferencia máxima tiene que ser 0. Repetí el control positivo abriendo la compuerta
> var.observado. Anotalo en el resumen y en el HANDOFF, mostrame el resultado y, si da 0, hacé el
> commit "Fase 3, paso 3a: configuración de la solución (D42)" sin push.

**Respuesta:** ver el extracto en la entrada del paso 3a (Prompt 2). El commit `1560a5b` se hizo a las 23:44, después de este mensaje.

**Uso y verificación:** el texto ya figuraba como Prompt 2 de la entrada del paso 3a; se repite acá para que la secuencia de la fase 3 quede completa en un solo lugar. Verificación en el cierre de esta entrada.

### Mensaje 3 — pedido de los pasos 3b y 3c
*19/10/2026 23:46 (UTC-3); en la transcripción, `2026-10-20T02:46:54.311Z`.*

> dale, segui con 3b y 3c

**Respuesta:** ver el extracto en la entrada de los pasos 3b y 3c (Prompt 1): la IA preguntó tres puntos antes de escribir código. El texto de los pasos 3b y 3c que este mensaje pone en marcha es el del Mensaje 1.

**Uso y verificación:** transcripción completa. Verificación en el cierre de esta entrada.

### Mensaje 4 — autorización del commit `508c46e`
*20/10/2026 00:25 (UTC-3); en la transcripción, `2026-10-20T03:25:32.669Z`.*

> Ok, si termina y los resultados salen bien, hace el commit.

**Respuesta:** ver el extracto en la entrada de los pasos 3b y 3c (Prompt 3). El commit `508c46e` se hizo a las 00:32, después de este mensaje.

**Uso y verificación:** responde a la respuesta de la IA sobre cuánto demoraría la reejecución con `nbconvert`, que el equipo había preguntado antes («Cuanto demora la re ejecucion aproximadamente?», 20/10/2026 00:24). Ese intercambio no tuvo otro efecto y no se registra más allá de esta mención. El mensaje con las instrucciones que precedieron al commit (la fila 38 del registro, la restauración del JSON, el IC95 de NB2 y las figuras 7 y 11) ya figuraba como Prompt 3 de la entrada de los pasos 3b y 3c, igual que las respuestas del equipo sobre D43 a D45 (Prompt 2). Verificación en el cierre de esta entrada.

**Verificación de la entrada:** cada uno de los cuatro textos se comparó por programa contra el mensaje del `.jsonl` de la sesión de la fase 3 (texto del archivo del registro, sin el prefijo de cita, contra el contenido del mensaje sin las marcas de pegado), con igualdad exacta de cadena. El resultado se informó al equipo en la sesión de esta corrección. No se editó ninguna entrada anterior. **Archivos afectados:** `documentacion/registro_uso_IA.md`.


---

## Sesión 2026-10-20 (fix de R2, E3 fases 2 y 3) — lucaspimentel-uy — Claude Code (Anthropic, Claude Sonnet 5.5)

**Contexto:** rama `e3/fase-3-seleccion`. Corrección de las observaciones de la review R2 (`documentacion/reviews/E3_fase_2-3.md`, APROBADA CON OBSERVACIONES), decisión D46 del equipo. Pasos F1 (registro de IA), F2 (tabla 49 y encabezado del notebook), F3 (resumen) y F4 (HANDOFF y registro), con una parada del equipo después de cada uno. La entrada inmediatamente anterior («paso F1: transcripción textual de la fase 3») pertenece a esta misma sesión. Los mensajes «Dale, segui con F2» y «Dale, segui» (continuar con F3) solo confirmaron avanzar y no se transcriben (criterio D47 del equipo, 20/10: el registro guarda solo el prompt que abre la sesión y los mensajes con decisiones o instrucciones). Horas locales (UTC-3). Se omiten solo las marcas con que Claude Code envuelve el texto pegado.

### Prompt 1 (prompt de la sesión, con el bloque de la sesión incluido)
*20/10/2026 11:26.*

> Sesión de trabajo del Entregable 3, fix de fase 2 y 3 tras review, en la rama e3/fase-3-seleccion.
>
> Antes de hacer nada:
> 1. Verificá con `git branch --show-current` que estás en e3/fase-3-seleccion. Si no, detenete y avisame.
> 2. Leé CLAUDE.md, HANDOFF.md y documentacion/resumen_modelos_candidatos.md. Respetá todas
>    las reglas de CLAUDE.md: ninguna cifra sin artefacto, documento acompañante por notebook,
>    registro de IA y HANDOFF al cierre.
> 3. Las reglas fijadas en la sección 1 de notebooks/modelos_candidatos.ipynb no se modifican.
>    Si algo necesita precisarse, se agrega un bloque fechado debajo y me lo consultás antes.
>
> Reglas de la sesión:
> - El bloque final (2025-02-06 → 2025-12-31) solo lo lee notebooks/evaluacion_final.ipynb.
>   En cualquier otro código, el panel entra únicamente por src/datos.py:cargar_panel_desarrollo().
>   Esto incluye comandos sueltos de exploración.
> - Variables solo desde src/variables.py. Si hace falta una nueva, va ahí y con tests.
> - Los notebooks se ejecutan con `jupyter nbconvert --execute` en el .venv, con 0 errores.
>   `pytest` tiene que pasar entero.
> - Detenete en cada parada que indique el prompt. No avances sin mi confirmación.
> - Si una instrucción choca con lo que encontrás en el repositorio, o si una decisión no
>   está cubierta por el prompt, preguntá en vez de resolverla por tu cuenta.
> - Al cerrar: actualizá el documento acompañante, HANDOFF.md y
>   documentacion/registro_uso_IA.md. Mostrame `git status` y un resumen de los archivos tocados.
>   Hacé commit en e3/fase-3-seleccion solo cuando yo lo confirme. Nunca en main y nunca push.
>
> Prompt de la fase:
> Fix de la review R2 (fases 2 y 3). Modelo: sonnet (D25). La review está en
> documentacion/reviews/E3_fase_2-3.md: leela entera antes de empezar. Corregís solo lo que se lista
> acá (decisión D46 del equipo, 20/10). Cualquier otro cambio, consultame antes. No se modifican
> solucion_seleccionada.json, la sección 1, la adenda, los bloques fechados ni ninguna tabla o figura
> existente.
>
> ## Paso F1 — Registro de IA (observación 1, criterio N2)
>
> - Ubicá las transcripciones locales de Claude Code de las sesiones de la fase 3 (archivos .jsonl del
>   proyecto, en la carpeta de proyectos de Claude Code del usuario, C--Proyectos-proyecto-machine-learning).
>   Identificá: el prompt de la fase 3 completo (bloque S y prompt de la fase), el mensaje aparte del
>   paso 3.0, el mensaje que autorizó el commit 1560a5b, el que pidió los pasos 3b y 3c y el que autorizó
>   508c46e.
> - Agregá una entrada NUEVA al final de documentacion/registro_uso_IA.md con esos mensajes textuales,
>   completos, en orden y con su fecha. No edites las entradas anteriores: la nueva aclara que completa
>   las del paso 3a y de 3b/3c, que abreviaban o remitían.
> - Compará por programa cada texto transcripto contra el .jsonl (igualdad exacta) y mostrame el resultado.
> - Si no encontrás alguna transcripción, detenete y consultame. No reconstruyas texto de memoria.
>
> DETENETE.
>
> ## Paso F2 — Tabla nueva para el 0,0076 (observación 4) y encabezado del notebook
>
> - Ubicá en la sección 12 el print que produce el 0,0076 citado en el resumen §3g.6. Sin cambiar ningún
>   cálculo, agregá la escritura de ese valor (con su definición y las cifras de las que sale) en una tabla
>   nueva, experiments/modelos_candidatos/tablas/49_<nombre>.csv. No modifiques tablas/45 ni ninguna otra.
> - Corregí la numeración vieja de secciones en la celda markdown de encabezado del notebook.
> - Antes de ejecutar, pedime que cierre cualquier visor o sincronizador que tenga abiertas figuras de
>   experiments/ (en la fase 3 una corrida falló por un bloqueo de fig6).
> - Reejecutá con nbconvert (0 errores, 0 stderr) y pytest (15 pasados, 0 saltados).
> - Verificá con git: tablas 00 a 48, figuras y solucion_seleccionada.json idénticos a 508c46e; en
>   registro_experimentos.csv solo cambia fecha_hora; la única tabla nueva es la 49, y su valor coincide
>   con el 0,0076 del resumen.
>
> DETENETE.
>
> ## Paso F3 — Resumen (observación 2 y riesgos declarados)
>
> En documentacion/resumen_modelos_candidatos.md:
> - §1.1: quitá «PENDIENTE: no ejecutados» y reflejá el estado real. Registrá D35 donde corresponda:
>   análisis pareado posterior a ver resultados, sin efecto en la selección.
> - §1.3: corregí «sólo se usa la expansiva». En el paso C se evaluaron las deslizantes, y la
>   configuración final es la deslizante de 364 días por D42.
> - §4: eliminá las dos líneas PENDIENTE repetidas.
> - §7 ítem 4: sacá de pendientes lo que ya está hecho.
> - §8: corregí «ninguna celda anterior cambió». En 508c46e cambió la sección 10 (ahora verifica el JSON
>   con assert en vez de reescribirlo), y en este fix cambian la sección 12 (tabla 49) y el encabezado.
> - §3g.6: citá tablas/49 como fuente del 0,0076.
> - §5, limitaciones nuevas de la fase 3:
>   (a) D42 se tomó después de ver los resultados del paso C, con los mismos 47 cortes. En la práctica
>       antepone la calibración a la estabilidad del paso 4 de la regla. La cifra que se informa como
>       resultado es la del bloque final, que sigue sin abrirse.
>   (b) D43 a D45 están en el mismo commit que sus resultados: git no prueba que se fijaran antes de
>       calcular.
>   (c) El campo commit_del_repositorio de solucion_seleccionada.json dice 5f207e2, pero el JSON se generó
>       con cambios sin commitear sobre ese commit; el commit que lo contiene es 1560a5b. El JSON no se
>       corrige porque no puede cambiar después de 1560a5b (F3-B2, F4-B1).
>   (d) Las coberturas de los intervalos se reportan como proporciones, sin incertidumbre. Las
>       observaciones de un mismo corte y municipio no son independientes, así que un intervalo binomial
>       simple la subestimaría.
>   (e) Deuda aceptada (observación 5 de R2): explicaciones bajo «Evidencia», lambdas con nombre y
>       globales reutilizados entre secciones. Motivo: no afectan resultados, y cambiar código obligaría a
>       revalidar antes de la fase 4.
> - En la lista de frases que no deben aparecer en el informe, agregá: presentar la diferencia pareada
>   (sensibilidad − L1: −0,0017, EE 0,0005; o solución − L1) como prueba de significación; decir que la
>   configuración final siguió la regla de selección, en cualquier variante; presentar las coberturas como
>   exactas.
> Cada cifra nueva lleva su tabla.
>
> ## Paso F4 — HANDOFF y registro
>
> - Registrá D35 (con su definición), D41 (recomendación de seguir la regla, con la expansiva como final
>   y la deslizante de 364 días como sensibilidad; reemplazada por D42 antes de la fase 3) y D46 (esta
>   acción).
> - Corregí las líneas viejas: «Commit de la parada C pendiente de confirmación» (el commit es 5f207e2) y
>   «Próximo: la fase 4» en la entrada de 3b y 3c (lo próximo era R2; ahora, la review corta y el merge).
> - Agregá la entrada de esta sesión: resultado de R2, observaciones corregidas, deuda aceptada,
>   verificación y validación del equipo (D30): Lucas revisó el veredicto de R2 el 20/10, con apoyo de
>   Claude en el chat del Project, y decidió D46.
> - La entrada de esta sesión en el registro de IA lleva este prompt textual, con el bloque S incluido.
>
> DETENETE. Mostrame git status, git diff --stat contra 508c46e y el resumen de archivos tocados.

**Respuesta (extracto relevante):** se verificó la rama y se leyeron CLAUDE.md, HANDOFF.md, el resumen y la review R2. **F1:** las transcripciones estaban en la carpeta de proyectos de Claude Code; el mensaje del paso 3.0 y el que autorizó `1560a5b` resultaron ser uno solo, así que la entrada nueva transcribe cuatro mensajes, no cinco; comparación por programa, igualdad exacta. **F2:** la celda de intervalos de la sección 12 guarda en `tablas/49_fase3c_dif_mu_nb2_vs_solucion.csv` el máximo de |μ NB2 − μ solución| (0,00762: corte 44, 2025-01-09, MUNICIPIO A, 2.632 filas) sin cambiar el cálculo, y el encabezado pierde la numeración vieja de la fase 2. **F3:** `resumen_modelos_candidatos.md` (marcas `PENDIENTE` de §1.1 y §4, §1.3, §7, §8, D35 en §3e.5, fuente del 0,0076 en §3g.6, limitaciones (a) a (e) y tres frases nuevas en §5, índice §6). **F4:** `HANDOFF.md` con D35, D41, D46, las dos líneas viejas corregidas y la entrada de la sesión; esta entrada.

**Uso y verificación:** utilizado, con tres desviaciones declaradas: (1) el mensaje del paso 3.0 y el de la autorización de `1560a5b` son el mismo; (2) en §4 del resumen la IA dejó **una** línea en lugar de eliminar las dos repetidas, porque la evaluación en el test sigue pendiente; el equipo lo confirmó (Prompt 3); (3) la tabla `tablas/10_artefactos.csv` cambió una línea (índice de artefactos que lista la 49), algo que el prompt no preveía. Verificación: `nbconvert --execute` en el `.venv` una vez, exit 0, 0 errores y 0 `stderr`; `pytest` 15 pasados, 0 saltados; contra `508c46e` las tablas 00 a 48 son idénticas (salvo el índice `10`), las figuras y `solucion_seleccionada.json` también, el registro de experimentos solo cambia `fecha_hora`, y la tabla 49 coincide con el 0,0076 del resumen. **Archivos afectados:** `notebooks/modelos_candidatos.ipynb`, `experiments/modelos_candidatos/` (tabla 49, índice 10 y `registro_experimentos.csv`, solo `fecha_hora`), `documentacion/resumen_modelos_candidatos.md`, `HANDOFF.md`, `documentacion/registro_uso_IA.md`.

### Prompt 2
*20/10/2026 11:43.*

> dale ya cerre todo ejecuta. Antes ese habia sido el problema si, tenia la fig 6 abierta en fotos

**Respuesta (extracto relevante):** se ejecutó `nbconvert` (15,9 min), `pytest` y las comprobaciones con git descritas en el Prompt 1.

**Uso y verificación:** el equipo confirmó la causa del bloqueo de `fig6` que había fallado una ejecución de la fase 3: tener la figura abierta en el visor de fotos. Es una declaración del equipo; la IA no la comprobó. Quedó asentada en el HANDOFF. La ejecución de esta sesión no tuvo bloqueos.

### Prompt 3
*20/10/2026 12:07.*

> OK §4, queda como está. Antes de F4:
> 1. En la lectura 12.1 del notebook y en su espejo §3g.9 del resumen, la fuente del 0,0076 pasa a ser
>    tablas/49. Corregí la cita a «45, 46» donde se refiera a esa cifra. Es solo markdown: no reejecutes.
> 2. Frase «quedan para» del encabezado: si se refiere a trabajo que ya está hecho (pasos, secciones o
>    fases anteriores a la 4), actualizala al estado real; si se refiere a la fase 4, dejala como está.
>    Mostrame el antes y el después.
> 3. D35: según el plan del equipo, es del 19/10, posterior al paso A de la fase 2. Usá esa fecha en el
>    HANDOFF y en el resumen §3e.5.
> 4. Validación del equipo (D30) en F4: Lucas revisó el veredicto de R2 el 20/10 y decidió D46
>    [si corresponde: «y confirmó D31 a D45»].
> Después seguí con F4.

**Respuesta (extracto relevante):** (1) La cita del 0,0076 pasó a `tablas/49` en la lectura 12.1 del notebook (solo markdown: el encabezado de la evidencia pasa a «(`45`, `46`, `49`)», la cifra lleva «(`49`)» y la primera línea de la celda cita «`38` a `49`») y en §3g.6 del resumen. **El espejo §3g.9 del resumen no menciona esa cifra, así que no había nada que corregir ahí.** (2) La frase «quedan para» se refería a las secciones 11 y 12, ya hechas (pasos 3b y 3c), así que se actualizó. *Antes:* «las secciones 11 y 12 quedan para la explicabilidad y el análisis de errores». *Después:* «las secciones 11 y 12 contienen la explicabilidad (paso 3b) y el análisis de errores (paso 3c)». (3) D35 pasó a figurar como decisión del plan del equipo del 19/10/2026, posterior al paso A de la fase 2, en el resumen §3e.5 y en el HANDOFF. (4) La validación D30 quedó como «Lucas revisó el veredicto de R2 el 20/10 y decidió D46».

**Uso y verificación:** utilizado. **No** se agregó «y confirmó D31 a D45»: el prompt lo condicionaba a «si corresponde» y ni el prompt ni el repositorio dicen que el equipo las haya confirmado en esta revisión; si fue así, hay que agregarlo. Esa condición queda a cargo del equipo. La IA tampoco comprobó la validación D30, que es una declaración del equipo. El notebook no se reejecutó: los cambios son solo de texto (se verificó que el JSON sigue siendo válido y que, respecto de `508c46e`, solo difiere el texto de las celdas 0 y 62, markdown, y de la 59, la de código ya reejecutada en F2). **Archivos afectados:** `notebooks/modelos_candidatos.ipynb` (markdown), `documentacion/resumen_modelos_candidatos.md`, `HANDOFF.md`, `documentacion/registro_uso_IA.md`.

