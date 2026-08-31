# Resumen del diagnóstico de datos

**Notebook:** [`notebooks/diagnostico_datos.ipynb`](../notebooks/diagnostico_datos.ipynb)
**Artefactos:** `experiments/diagnostico_datos/` (26 tablas CSV y 5 figuras PNG)
**Fecha de ejecución:** 2026-08-30

Documento de apoyo para presentar y defender el diagnóstico de datos ante el docente. Resume
qué se hizo, qué se encontró y qué decisiones se derivan. Todas las cifras que aparecen aquí
provienen de la ejecución del notebook y están respaldadas por un archivo de
`experiments/diagnostico_datos/`; ninguna es estimada.

---

## 1. Para qué existe este notebook

El Entregable 2 de la guía PAA (sección 5.2) exige, como primer resultado, *«un diagnóstico de
calidad, adecuación, cobertura y limitaciones de los datos»*, y la sección 6.1 pide revisar
calidad, cobertura, representatividad, sesgos y restricciones de uso, además de verificar que no
se incorpore información no disponible en el momento real de la predicción.

El notebook responde a esas cuatro preguntas con evidencia reproducible:

| Eje | Pregunta que responde |
| --- | --- |
| Calidad | ¿Los registros son completos, consistentes y precisos para lo que se les va a pedir? |
| Cobertura | ¿Qué territorio, qué período y qué fracción de la unidad de análisis observan? |
| Adecuación | ¿La variable objetivo y las variables disponibles sostienen el problema planteado? |
| Limitaciones | ¿Qué no puede afirmarse con estos datos y qué riesgo introduce cada decisión? |

**Decisión de diseño importante:** el notebook **recalcula todo desde el CSV crudo** en lugar de
apoyarse en los Parquet ya construidos. Eso lo vuelve independiente del estado de
`data/processed/` y —como se ve en el punto 2 de la sección 4— permitió detectar que esos
archivos derivados no coinciden con el código que dice generarlos.

## 2. Qué datos se diagnostican

- **Fuente:** `data/raw/uru_siniestros_unificado.csv`, heredado del PID (registros de
  siniestros de UNASEV, ya depurados y geolocalizados).
- **Volumen:** 224.694 registros × 11 columnas, del 2018-01-01 al 2025-12-31 (2.922 días).
- **Unidad de análisis del PAA:** el par **(día, zona)**, donde la zona es una celda de
  500 × 500 m sobre las coordenadas UTM 21S. La variable objetivo es el conteo de siniestros de
  esa zona ese día.

El notebook registra el `sha256` del archivo diagnosticado y las versiones de Python y de cada
biblioteca (`tablas/00_procedencia.csv`), de modo que las cifras quedan atadas a una versión
concreta del dato y no a «los datos» en abstracto.

## 3. Cómo está organizado

| Sección | Contenido |
| --- | --- |
| 0 | Configuración y trazabilidad de la fuente (hash, versiones) |
| 1 | Unidad de análisis y qué variables son utilizables como predictoras |
| 2 | **Calidad**: completitud, duplicados, consistencia, precisión espacial, validez temporal, coherencia con los artefactos derivados |
| 3 | **Cobertura**: temporal, división cronológica de particiones, territorial, del panel día × zona, estabilidad de zonas, variables exógenas |
| 4 | **Adecuación**: variable objetivo, granularidad, señal temporal disponible, ajuste al objetivo del producto |
| 5 | **Limitaciones y riesgos**: tabla de 13 limitaciones con evidencia y tratamiento |
| 6 | Artefactos generados y pendientes que el diagnóstico deja abiertos |

---

## 4. Los seis hallazgos que hay que saber explicar

Éstos son los que cambian decisiones del proyecto. El resto del notebook los sostiene.

### 4.1 Sólo tres columnas de once son utilizables como predictoras

`Gravedad`, `Tipo de Siniestro` y `Hora` describen un siniestro **que ya ocurrió**. Usarlas para
predecir si mañana habrá un siniestro equivale a conocer la respuesta. La restricción de la guía
(6.1) las deja fuera, y con ellas se va casi toda la riqueza aparente del archivo: quedan
`Fecha`, `X` e `Y` para construir la unidad de análisis y el objetivo, más `Departamento` para
agrupar y describir. `fixed` es una columna constante heredada del ETL del PID, sin información.

**Consecuencia:** el poder predictivo no puede venir de los atributos del siniestro, sino del
historial de la zona y del calendario —y, cuando se integre, del clima—.
*Evidencia:* `tablas/02_disponibilidad_variables.csv`.

### 4.2 Los datos procesados no son reproducibles con el código versionado

El notebook infiere el tamaño de celda de los propios artefactos a partir de sus centroides y lo
contrasta con el parámetro del diseño:

| Comprobación | Valor | Resultado |
| --- | --- | --- |
| Tamaño de celda del diagnóstico | 500 m | — |
| Tamaño inferido de `zonas.parquet` | 1.000 m | **discrepancia** |
| Zonas según el diagnóstico | 18.487 | — |
| Zonas en `zonas.parquet` | 11.633 | **discrepancia** |
| Filas de `panel_diario_zona.parquet` | 33.991.626 | = 11.633 × 2.922 días |

Es decir: alguien ejecutó el pipeline con celdas de 1 km sin guardar ese cambio en
`analisis_inicial.ipynb`, que sigue declarando `TAM_CELDA = 500`. No es un problema de los
datos, es un problema de **trazabilidad** —lo que la guía exige sostener entre datos, código,
configuración y resultado (4.4 y 6.3)— y habría pasado inadvertido si el diagnóstico se hubiera
apoyado en los derivados.
*Evidencia:* `tablas/08_coherencia_artefactos.csv`.

### 4.3 A nivel de zona no hay señal temporal de corto plazo

Es el hallazgo de mayor consecuencia. La pregunta es si el pasado reciente de una zona informa
sobre su futuro; para responderla no basta con mirar la autocorrelación, hay que compararla
contra lo que produciría el puro azar. El notebook simula, para cada zona, un proceso de Poisson
con su misma tasa y usa esa simulación como banda nula.

En las 520 zonas con soporte suficiente (≥ 100 siniestros en ocho años):

| Ventana | Rezago | Mediana observada | Banda nula (p5–p95) | Lectura |
| --- | --- | --- | --- | --- |
| Período completo | 1 | 0,0015 | −0,0318 a 0,0316 | dentro |
| Período completo | 7 | 0,0057 | −0,0271 a 0,0301 | dentro |
| Sólo entrenamiento | 1 | −0,0005 | −0,0379 a 0,0388 | dentro |
| Sólo entrenamiento | 7 | 0,0035 | −0,0358 a 0,0373 | dentro |

El índice de dispersión (varianza / media) por zona tiene mediana **1,015** en el período
completo y **1,009** sólo en entrenamiento: exactamente lo que caracteriza a un Poisson. La
serie diaria de una zona es **estadísticamente indistinguible del azar**.

El cálculo se repite restringido a entrenamiento precisamente porque esta conclusión orienta una
decisión de modelado, y el conjunto de prueba no debe usarse para decidir nada.

**En cambio, a nivel nacional sí hay señal, de dos tipos:**

- **Calendario:** explica el **35,3 %** de la varianza del logaritmo de la serie diaria. Viernes
  85,0 siniestros/día frente a domingo 68,9; diciembre 85,7 frente a enero 70,8; feriados en
  torno a 65 frente a 77,5 en días ordinarios.
- **Persistencia no explicada por el calendario:** tras descontarlo, el residuo conserva
  autocorrelación de **0,301** a rezago 1 y 0,180 a rezago 7 (la serie cruda daba 0,392 y
  0,384). Hay días buenos y días malos que el calendario no explica: el clima es el candidato
  inmediato, y es justamente lo que la integración pendiente de Open-Meteo debería capturar.

**Consecuencias, que conviene declarar antes de mostrar cualquier resultado:**

1. Las variables `lag_1`, `lag_7`, `lag_28` **por zona** casi no aportan. No es un error
   incluirlas, pero no hay que esperar de ellas el desempeño.
2. Lo que informa es la **tasa histórica de la zona** combinada con **factores temporales
   comunes a todo el país**.
3. Por eso la **línea base correcta es «tasa de largo plazo de la zona × factor de calendario»**.
   Una línea base más ingenua —«lo mismo que ayer en esta zona»— sería engañosamente fácil de
   superar y haría parecer valioso cualquier modelo.
4. El techo de desempeño es bajo por naturaleza: con λ ≈ 0,004, **ningún modelo puede predecir
   en qué celda concreta ocurrirá el siniestro**. Lo que sí puede hacerse —y es lo que el
   producto necesita— es **ordenar zonas y períodos por riesgo esperado**, bien calibrado.

*Evidencia:* `tablas/21_autocorrelacion_nacional.csv`, `tablas/22_acf_por_zona_vs_nulo.csv`,
`figuras/fig5_senal_temporal.png`.

### 4.4 La variable objetivo es casi binaria y extremadamente escasa

El panel completo tiene **54.019.014 filas** (2.922 días × 18.487 zonas) y sólo el **0,405 %**
es distinto de cero: 99,6 % de ceros. De las 218.778 celdas con al menos un siniestro, el
**97,4 % tiene exactamente uno** y sólo 206 superan los dos. El índice de dispersión global es
**1,051**, otra vez Poisson: los ceros abundan porque la tasa es bajísima, no porque exista un
mecanismo adicional que los genere.

**Consecuencias:** conviene un objetivo **Poisson** (desvianza / verosimilitud de Poisson) en
lugar de error cuadrático sobre el conteo; y *acertar el conteo* de una celda concreta no es un
objetivo alcanzable ni informativo — lo estimable es la **intensidad**, así que la evaluación
debe medir calibración y ordenamiento, no exactitud puntual.

Conviene además saber responder por qué no se cambió la granularidad. El notebook mide qué pasa
al agrandar la celda y al agregar en el tiempo (% de filas con al menos un siniestro):

| Celda | Diaria | Semanal | Mensual |
| --- | --- | --- | --- |
| 500 m | 0,405 % | 2,537 % | 8,274 % |
| 1 km | 0,616 % | 3,302 % | 8,975 % |
| 2 km | 0,951 % | 4,097 % | 10,027 % |
| 5 km | 1,767 % | 6,185 % | 14,373 % |

**La escasez no se resuelve agrandando la celda:** pasar de 500 m a 5 km multiplica el área por
100 y la densidad diaria sólo sube de 0,41 % a 1,77 %. Habría que llegar a 5 km mensuales para
alcanzar un 14,4 %, perdiendo toda la resolución que el producto necesita. La elección de
500 m × día se sostiene, pero por la razón correcta: es la granularidad que responde a la
pregunta del proyecto, y el problema es tratable con modelos de conteo y submuestreo de ceros.
*Evidencia:* `tablas/13_panel_dia_zona.csv`, `tablas/18_distribucion_objetivo.csv`,
`tablas/19_dispersion_objetivo.csv`, `tablas/20_granularidad.csv`, `figuras/fig4_granularidad.png`.

### 4.5 La variable de feriados está mal construida

`holidays.country_holidays("UY")` devuelve por defecto sólo la categoría `public`: **41 días en
ocho años**. Los feriados no laborables —Carnaval, Semana de Turismo, 6 de enero, 19 de abril,
18 de mayo, 19 de junio, 12 de octubre, 2 de noviembre— quedan en la categoría `bank` y hoy
**no** los marca la variable `es_feriado` de `analisis_inicial.ipynb`.

La omisión importa porque esos días se comportan igual que los que sí se marcan:

| Grupo | Días | Media diaria nacional |
| --- | --- | --- |
| Feriados `public` (los que usa la variable actual) | 41 | 64,8 |
| Feriados `bank` omitidos | 104 | 65,0 |
| Días ordinarios | 2.777 | 77,5 |

La variable actual identifica **41 de los 145 días con caída sistemática de siniestralidad** —el
28 %— y trata como normales a los 104 restantes, entre ellos los 40 días de Semana de Turismo,
el período de movilidad más atípico del año. **Corrección propuesta:** construirla con
`categories=("bank", "public")` y evaluar además una variable de «período especial», ya que
Semana de Turismo y Carnaval son períodos y no días sueltos.
*Evidencia:* `tablas/16_feriados.csv`, `tablas/17_feriados_omitidos.csv`.

### 4.6 Las variables climáticas están previstas pero no incorporadas

`data/` sólo contiene el CSV de siniestros y los derivados del panel; no hay ninguna caché de
Open-Meteo en el repositorio. Hasta que se integre y se verifique su cobertura por zona y fecha,
**ningún resultado puede atribuirse al clima**. Es también el hueco más prometedor: es lo que
podría explicar la autocorrelación residual de 0,30 de la sección 4.3.

---

## 5. Cobertura: qué observan realmente los datos

**Temporal.** Los 2.922 días están completos y **no hay un solo día vacío**. El mínimo nacional
son 26 siniestros (22 de marzo de 2020, primer fin de semana de la emergencia sanitaria) y el
máximo 129 (23 de diciembre de 2024). Que el piso sea 26 y no 0 es lo que hace correcto el
relleno con ceros del panel: **el cero de una zona es ausencia de siniestro, no ausencia de
dato**, porque el país nunca deja de registrar.

El volumen anual es estable salvo **2020, con 24.031 siniestros (−13,0 % respecto de 2019)** y
una caída concentrada en abril (1.331 frente a 2.298 de media en los demás abriles). Desde 2021
la serie se recupera y crece hasta 2025 (31.005, máximo del período). El período de
entrenamiento contiene, por tanto, una anomalía estructural que no reaparece en validación ni en
test: hay que declararla y no interpretar una caída de desempeño entre particiones como
sobreajuste sin antes descartar el cambio de régimen.

**Territorial.** Los 19 departamentos están representados, pero la cobertura es muy concentrada:

- Las 18.487 celdas observadas suman **4.622 km², el 2,6 % del territorio continental**. El
  modelo sólo puede pronunciarse sobre esa fracción; el resto del país no es «riesgo bajo», es
  **territorio no observado**.
- **Montevideo concentra el 27,8 % de los siniestros en 1.167 zonas** (53,5 por zona), mientras
  Rocha o Florida reparten menos de 6 por zona.
- La mitad de los siniestros ocurre en **687 zonas** y el 80 % en **2.589**, sobre 18.487.

El problema es entonces **muy heterogéneo en soporte**: unas pocas zonas urbanas con serie densa
y una larga cola de zonas con dos o tres eventos en ocho años. Es el argumento para evaluar el
desempeño **por estrato de soporte** y no sólo de forma agregada.

| Umbral de soporte | Zonas | % de zonas | % de siniestros | % de días con evento |
| --- | --- | --- | --- | --- |
| ≥ 1 siniestro | 18.487 | 100,0 | 100,0 | 0,41 |
| ≥ 5 | 5.458 | 29,5 | 90,5 | 1,24 |
| ≥ 50 | 1.113 | 6,0 | 61,7 | 4,10 |
| ≥ 100 | 520 | 2,8 | 43,4 | 6,12 |

## 6. Diseño de las particiones (70 / 10 / 20)

La división es **cronológica, nunca aleatoria**: con variables de rezago, un corte al azar le
filtra el futuro al modelo. El período de modelado empieza en 2019 porque 2018 se consume como
calentamiento de las medias móviles de 365 días. Se reserva el 20 % final como test y el 80 %
restante se reparte en 70 % de entrenamiento y 10 % de validación, calculando los cortes sobre
el eje de días para que las proporciones se cumplan exactamente.

| Partición | Desde | Hasta | Días | % días | Siniestros | % siniestros | Media diaria |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Entrenamiento | 2019-01-01 | 2023-11-25 | 1.790 | 70,0 | 131.760 | 67,3 | 73,6 |
| Validación | 2023-11-26 | 2024-08-07 | 256 | 10,0 | 20.666 | 10,6 | 80,7 |
| Test (reservado) | 2024-08-08 | 2025-12-31 | 511 | 20,0 | 43.416 | 22,2 | 85,0 |

**Dos asimetrías que hay que declarar.**

1. **Composición estacional.** Cumplir 70/10/20 con exactitud obliga a cortar a mitad de año: la
   validación **no contiene ningún día de setiembre ni de octubre**, mientras el test cubre los
   doce meses e incluye dos diciembres, el mes de mayor siniestralidad. Por eso **el nivel del
   error de validación y el de test no son directamente comparables**; la comparación *entre
   modelos dentro de la validación* sí lo es, que es para lo que la validación se usa. La
   alternativa —cortar por años completos— daría particiones estacionalmente homogéneas a costa
   de no alcanzar las proporciones pedidas.
2. **Régimen de siniestralidad.** La media diaria sube de 73,6 en entrenamiento a 85,0 en test:
   el modelo se entrena sobre un régimen algo más bajo que aquel sobre el que se lo evalúa.

**Zonas sin historial.** De las 8.061 zonas con siniestros en el tramo de test, **1.787
(22,2 %) no registraron ninguno durante el entrenamiento**; en validación son 922 de 5.773
(16,0 %). Sobre ellas el modelo predice con historial vacío. Concentran el **4,6 % de los
siniestros del test** y el 4,7 % de los de validación: es una cota inferior del error inevitable
para cualquier modelo basado en historial de zona, y debe tratarse como estrato propio en el
análisis de errores.

**Fuga leve declarada.** El catálogo de zonas se construye con los ocho años, test incluido: la
existencia de una zona en el panel usa información posterior al corte de entrenamiento. Afecta
al universo de filas, no a ninguna variable predictora, y su efecto es conservador —agrega zonas
casi siempre vacías—, pero es real y se declara en lugar de dejarla implícita. La alternativa
limpia es definir el catálogo sólo con entrenamiento y tratar las zonas nuevas como fuera de
dominio.

## 7. Calidad: lo que se verificó y salió bien

Conviene poder decir también qué se comprobó y **no** dio problemas, porque es parte del
diagnóstico:

- **Completitud.** Las columnas que sostienen la unidad de análisis (`Fecha`, `X`, `Y`) están
  completas. Los faltantes están en `Localidad` (40.238, 17,91 %) y `Calle` (27.793, 12,37 %) y
  vienen **encubiertos como texto** (`SIN DATOS`, `NO SE INGRESO`), no como nulos: contar sólo
  nulos habría dado una completitud aparente del 100 %. Ninguna de las dos se usa como
  predictora, así que no compromete al modelo; sí impide usar la localidad como unidad
  territorial alternativa a la grilla.
- **Consistencia.** `Dia Semana` coincide con el día de `Fecha` en los 224.694 registros, `Hora`
  siempre está en [0, 23] y no hay coordenadas fuera de Uruguay.
- **Duplicados.** Hay 347 registros idénticos (0,15 %), repartidos de forma pareja entre 2018 y
  2025 (24 a 58 por año). La regularidad interanual descarta un error de carga —un archivo
  cargado dos veces se concentraría en un año— y es compatible con siniestros múltiples
  registrados por separado. **Se conservan**, porque el archivo no tiene identificador de
  siniestro que permita distinguir un duplicado de dos eventos reales en el mismo punto, día y
  hora.
- **Precisión espacial.** Todas las coordenadas son múltiplos de 5 m y los 224.694 siniestros se
  reparten entre sólo **68.152 puntos distintos** (3,3 por punto de media, 186 en el más
  repetido): la geocodificación ajusta al eje de calle o a la intersección. Eso **respalda la
  celda de 500 m** —cien veces la resolución de la fuente— y **descalifica** cualquier análisis
  de puntos negros a escala de decenas de metros.
- **Hora = 0** concentra el 2,08 % de los registros, con participación estable año a año
  (1,98 %–2,17 %). Un centinela encubierto daría un pico muy superior al de las horas vecinas;
  aquí es compatible con tránsito real de medianoche. No afecta al PAA porque la hora no se usa.

## 8. Limitaciones declaradas

La sección 5 del notebook las reúne en `tablas/24_limitaciones.csv`, cada una con su evidencia y
su tratamiento. Las que no se derivan de los puntos anteriores:

- **Sin medida de exposición.** Los datos registran siniestros, no tránsito ni población. Una
  zona con muchos siniestros puede ser peligrosa o simplemente muy transitada, y sin denominador
  ambas explicaciones son indistinguibles. Por eso el producto **no señala «zonas peligrosas»
  sino zonas donde se espera mayor cantidad de siniestros**, que es una afirmación más débil y
  más honesta. Para fiscalización sigue siendo útil; para inferir causas o rediseñar
  infraestructura, no alcanza.
- **Subregistro no cuantificable.** El archivo contiene los siniestros que fueron registrados;
  la fracción no registrada es desconocida y probablemente distinta entre Montevideo y el
  interior. El registro no se limita a los casos graves —**28,1 % «SIN LESIONADOS»**, casi 60 %
  «LEVE», 10,5 % «GRAVE» y 1,4 % «FATAL»—, lo que sugiere una cobertura amplia pero no la
  prueba: cuantificar el subregistro exigiría una fuente externa de contraste que el proyecto no
  tiene. Es la única limitación que **no** surge de un cálculo del notebook, y así está marcada
  en la tabla. *Evidencia del indicio interno:* `tablas/01b_composicion_descriptiva.csv`.
- **Etiqueta departamental aproximada en zonas limítrofes.** 57 celdas de 18.487 reciben
  siniestros de más de un departamento; el catálogo resuelve por moda. Sirve para agrupar y
  describir, no como predictor fino.

## 9. Qué queda pendiente

En el orden de prioridad que el propio notebook propone:

1. Resolver la discrepancia de granularidad entre `analisis_inicial.ipynb` (500 m) y los
   artefactos de `data/processed/` (1 km), y regenerar los derivados.
2. Alinear el corte de particiones de `analisis_inicial.ipynb` —hoy por años completos— con la
   división 70/10/20.
3. Integrar la caché climática de Open-Meteo y repetir el análisis de señal residual.
4. Corregir la construcción de `es_feriado`.
5. Decidir si el catálogo de zonas se redefine usando sólo entrenamiento.
6. Fijar las métricas del Entregable 2 en coherencia con un objetivo Poisson casi binario.
7. Implementar la línea base como tasa histórica de la zona × factor de calendario.

## 10. Cómo reproducirlo

Con el entorno del `README.md` activado, ejecutar el notebook de arriba a abajo. No requiere
descargas ni credenciales, y es de sólo lectura sobre `data/`: no reescribe el panel ni las
*features*. Es determinista salvo la simulación nula de la sección 4.3, fijada con
`SEMILLA = 42`.

```powershell
.venv\Scripts\Activate.ps1
jupyter lab notebooks/diagnostico_datos.ipynb
```

Al ejecutarlo se regeneran los 31 archivos de `experiments/diagnostico_datos/`. Cada cifra
citada en la sección *Metodología — datos* del informe debe remitir a uno de esos archivos o a
una celda del notebook.

---

## Anexo. Preguntas previsibles y cómo responderlas

**«¿Por qué celdas de 500 m y no otra cosa?»**
Porque es cien veces la resolución real de la fuente (5 m), de modo que el redondeo no puede
mover un siniestro de celda salvo en el borde, y porque agrandar la celda no resuelve la escasez
(tabla de la sección 4.4): a 5 km diarios la densidad sigue en 1,77 %. La granularidad se eligió
por la pregunta del proyecto, no por comodidad del panel.

**«¿No es un problema tener 99,6 % de ceros?»**
Es la naturaleza del fenómeno, no un defecto del dato: ningún umbral ni granularidad razonable
lo convierte en un problema denso. Se trata con objetivo Poisson, submuestreo de ceros con pesos
(que preserva el valor esperado) y métricas de calibración y ordenamiento en lugar de exactitud
puntual.

**«¿Cómo saben que los ceros son ceros reales y no falta de datos?»**
Porque no hay un solo día vacío en 2.922 días y el mínimo nacional es 26 siniestros. El país
nunca deja de registrar, así que el cero de una zona significa que no hubo siniestro.

**«¿Por qué dicen que los rezagos no sirven?»**
Porque la autocorrelación observada por zona cae dentro de la banda que produciría un proceso
puramente aleatorio de la misma tasa, y la comparación se hizo contra una simulación explícita,
no contra la intuición. Se verificó además restringiendo el cálculo a entrenamiento, para no
apoyar la decisión en datos reservados.

**«¿Cómo evitan las fugas de información?»**
Tres medidas: las columnas posteriores al evento quedan fuera del conjunto de predictoras
(sección 4.1); la división es cronológica y el test está reservado; y las dos fugas residuales
detectadas —el catálogo de zonas definido con los ocho años y el uso del histórico completo en
los análisis descriptivos— se declaran explícitamente, con la comprobación de que la conclusión
que orienta el modelado se mantiene usando sólo entrenamiento.

**«¿Qué esperan que logre el modelo?»**
Estimar la intensidad esperada por zona y día y ordenar zonas por riesgo, que es lo que el mapa
necesita. No predecir en qué celda concreta ocurrirá un siniestro: con λ ≈ 0,004 eso no es
alcanzable por ningún método, y decirlo por adelantado es parte del diagnóstico.
