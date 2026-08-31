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
