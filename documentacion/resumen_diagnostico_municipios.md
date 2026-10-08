# Resumen del diagnóstico por municipio — ¿alcanza un solo modelo para los ocho?

**Notebook:** [`notebooks/diagnostico_municipios.ipynb`](../notebooks/diagnostico_municipios.ipynb)
**Artefactos:** `experiments/diagnostico_municipios/` (46 tablas CSV y 9 figuras PNG)
**Fecha de ejecución:** 2026-10-05 (`jupyter nbconvert --execute --inplace` en el `.venv`; sin errores y
sin salidas por stderr; entorno en `tablas/00b_entorno.csv`)
**Alcance:** los **ocho municipios** de Montevideo (A, B, C, CH, D, E, F, G), **sólo el bloque de
desarrollo: 2021-07-01 a 2025-02-05** (1.316 días), serie diaria de conteo de siniestros por municipio.

> ### ⚠️ El test no se consulta — y este documento reemplaza a una versión anterior que sí lo hacía
>
> El **bloque final (2025-02-06 → 2025-12-31, 329 días)** es el futuro del proyecto: se reserva para evaluar
> el modelo al final. **Este notebook no lo carga ni calcula nada con él.** Las filas posteriores a
> 2025-02-05 se descartan al leer los archivos y un `assert` verifica que no queda ninguna.
>
> La primera versión de este notebook (2026-10-05, mañana) **usó el período completo en las secciones
> descriptivas** (2 a 6), es decir, **sí calculó cifras sobre el test**. Se corrigió el mismo día; esa
> versión quedó **superada y no debe citarse**. Cambiaron cifras y, en algunos puntos, conclusiones (la
> tendencia deja de ser «creciente en los ocho»; la memoria temporal pasa de «5 de 8» a «sólo C y CH»).
> La sección 7 (decisión) ya usaba sólo desarrollo y **no cambió ninguna cifra**.

---

## 0. Cómo usar este documento

Contexto autocontenido para redactar la documentación del proyecto (informe técnico, presentaciones,
defensa) sin abrir el repositorio. Es el documento de diagnóstico del proyecto: **reemplaza** a
`resumen_diagnostico_datos.md`, `resumen_diagnostico_datos_municipio.md` (C) y
`resumen_diagnostico_zona_contraste.md` (A), retirados de `main` el 2026-10-05 junto con sus notebooks y
tablas (siguen en la rama `entregable_2`). Describe los ocho municipios y responde la **pregunta de diseño**:
¿un solo modelo puede generalizar a todos los municipios, o hay que entrenar más de uno?

**Reglas que quien redacte debe respetar:**

1. **Ninguna cifra sin artefacto.** Toda cifra sale de una ejecución real y lleva su tabla
   (`tablas/NN_nombre.csv`). Un número que falte se marca `<!-- PENDIENTE: ... -->`, no se completa.
2. **Distinguir evidencia de inferencia.** En este documento las inferencias están rotuladas.
3. **No escribir Introducción ni Marco teórico** a partir de este documento.
4. **Respetar la sección 9** («frases que no deben aparecer en el informe»).
5. **Estas cifras son del desarrollo y no son comparables** con las de los tres diagnósticos retirados
   (rama `entregable_2`), que usan el período completo, es decir, **incluyen el test** (ver §11). Por eso
   este notebook **no los cruza** con `assert`: hacerlo exigiría calcular sobre el test.
6. **El modelo de la sección 7 es mínimo a propósito** (nivel × calendario). Su desvianza **no es el
   desempeño del modelo del proyecto** y no debe compararse con la de `resumen_linea_base.md`.
7. **El test sigue sin usarse.** Nada de este documento es una evaluación del modelo final.

**Qué se hereda y qué se agrega.** Se heredan, sin discutirlos, el recorte (Montevideo, municipios, desde
2021-07-01), el panel del ETL y la partición 80 / 20 de `linea_base.ipynb`. Se agrega (i) el mismo
diagnóstico de series temporales en los ocho municipios y (ii) la comparación predictiva de la sección 7.

---

## 1. Qué hace el notebook y por qué

| Decisión | Justificación |
| --- | --- |
| **No cargar el test en ninguna sección** | Regla del proyecto: el test es el futuro y sólo se usa para evaluar el modelo final. Las filas posteriores a 2025-02-05 se descartan al leer; el límite sale del calendario (80 % de 1.645 días), no de los datos. |
| Partir del panel del ETL, sin reconstruir la asignación espacial | El panel ya está verificado de forma independiente (`resumen_preparacion_montevideo.md` §8). |
| No cruzar con las cifras de los diagnósticos retirados ni con los totales del período completo | Esas cifras incluyen el test. Se reemplaza por verificaciones de integridad que no lo requieren (`01_verificacion_integridad.csv`). |
| Decidir con una comparación **predictiva**, no con pruebas de hipótesis | Una diferencia puede ser detectable y a la vez inútil para predecir. Ejemplo medido: el calendario de C es «distinto» en muestra y no mejora fuera de muestra. |
| Modelo mínimo multiplicativo (nivel × calendario) | Mide *estructura compartida*, no desempeño. No usa clima (una sola serie para los ocho) ni rezagos. |
| Dos pliegues cronológicos de 329 días dentro del desarrollo | Una diferencia que se repite en los dos es más defendible que una sola. Ajuste de 658 y 987 días. |
| Bootstrap por **bloques semanales** (2.000 remuestreos, semilla 20260910, mismos bloques para los ocho) | Conserva la autocorrelación de corto plazo y no inventa independencia entre municipios. |
| Regla de decisión **fijada antes** de ejecutar | «M3 mejora a M2 en ≥ 1 % y el IC95 excluye 0, en los dos pliegues». |
| Prueba F de cuasi-verosimilitud; Holm en las pruebas por municipio | Dispersión > 1 en los ocho; 8 pruebas simultáneas. |
| Rehacer **sólo con desarrollo** lo que dependía del archivo crudo (faltantes, evidencia del corte de la pandemia, cobertura temporal, mapa), el calendario y los rezagos | Decisión del equipo (2026-10-05). El archivo crudo se lee y se descarta el test **en el mismo paso**; los rezagos se eligen con **sólo el entrenamiento inicial**, para no filtrar la validación. |
| No rehacer la verificación cruzada independiente con el ETL | Decisión del equipo. Queda como pérdida aceptada: el ETL se verifica a sí mismo (16 comprobaciones). |
| Estacionalidad anual con 2022–2024 solamente; tendencia sin 2025; meses incompletos excluidos | El desarrollo contiene sólo 36 días de 2025 y 5 de febrero de 2025. |

**Decisiones descartadas.** *Reconstruir la asignación a municipios desde el CSV crudo*: redundante.
*Usar el período completo en las secciones descriptivas* (lo que hizo la primera versión): **descartado por
violar la regla del test**. *Una familia de modelos (árbol, boosting)*: agregaría hiperparámetros y mezclaría
«heterogeneidad entre municipios» con «calidad del modelo».

**Verificaciones que detienen la ejecución (`assert`).** Ocho municipios presentes; 10.528 filas; sin pares
repetidos ni huecos; feriados iguales al `tipo_dia` del ETL; clima idéntico entre municipios; **ninguna fila
posterior a 2025-02-05**; particiones 987 / 329 / 329; los eventos suman lo mismo que el panel; ninguna
ventana de validación invade el bloque final.

---

## 2. Calidad de la serie por municipio (secciones 1 y 2 del notebook)

### 2.1 Resumen — `tablas/03_resumen_por_municipio.csv`

| Mun. | Siniestros | % total | Media/día | Var/media | % días en 0 | % ceros esperados (Poisson) | Máx. | Racha máx. de ceros |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| C | 4.508 | 15,80 | 3,4255 | 1,2914 | 5,32 | 3,25 | 13 | 2 |
| B | 4.218 | 14,78 | 3,2052 | 1,1571 | 5,47 | 4,06 | 12 | 3 |
| D | 4.141 | 14,51 | 3,1467 | 1,1530 | 4,79 | 4,30 | 12 | 2 |
| A | 3.879 | 13,59 | 2,9476 | 1,1342 | 6,61 | 5,25 | 10 | 3 |
| F | 3.472 | 12,17 | 2,6383 | 1,0685 | 7,45 | 7,15 | 9 | 2 |
| G | 2.905 | 10,18 | 2,2074 | 1,0796 | 13,37 | 11,00 | 8 | 3 |
| E | 2.780 | 9,74 | 2,1125 | 1,2667 | 15,20 | 12,09 | 11 | 4 |
| CH | 2.632 | 9,22 | 2,0000 | 1,2135 | 16,49 | 13,53 | 9 | 4 |

**Evidencia.** Los ocho paneles tienen 1.316 días, sin huecos. Media diaria de 2,00 (CH) a 3,43 (C), razón
**1,71×**. Dispersión de 1,069 a 1,291: mayor que 1 en todos, nunca extrema. Ceros de 4,79 % a 16,49 %; el
exceso sobre un Poisson con la misma media es de **+0,30 (F) a +3,11 puntos (E)**. Rachas máximas de ceros de
2 a 4 días. Mes más bajo (÷ media propia, sólo meses completos): enero en C, B, F, CH (2022-01) y E (2024-01);
**2021-07 en A** (0,71), **2021-09 en D** (0,72), 2022-02 en G.

**Inferencia del equipo.** Los ocho son la misma clase de problema (conteo de media baja con sobredispersión
leve). El mayor porcentaje de ceros de CH, E y G se explica casi todo por su media más baja: no hay evidencia
para un tratamiento *zero-inflated*. Que el mes más bajo de A y D esté al inicio de la serie es una
**observación** (¿resto de la pandemia que el corte del 2021-07-01 no eliminó del todo?), **no investigada**.

### 2.2 Concentración geográfica — `tablas/04_concentracion_geografica_eventos.csv`

| Mun. | Eventos | Coord. distintas | Eventos por coord. | % en coord. repetida | % en la coord. más frecuente |
| --- | --- | --- | --- | --- | --- |
| C | 4.508 | 943 | 4,78 | 92,61 | 1,77 |
| B | 4.218 | 871 | 4,84 | 95,31 | 0,81 |
| D | 4.141 | 907 | 4,57 | 91,69 | 1,26 |
| A | 3.879 | 1.244 | 3,12 | 83,17 | 1,73 |
| F | 3.472 | 871 | 3,99 | 89,89 | 2,04 |
| G | 2.905 | 897 | 3,24 | 84,78 | 1,34 |
| E | 2.780 | 724 | 3,84 | 90,36 | 1,29 |
| CH | 2.632 | 633 | 4,16 | 92,48 | 1,44 |

**Evidencia.** 83 % a 95 % de los eventos cae en una coordenada que se repite; ninguna coordenada concentra
más del 2,1 % de su municipio. **A es el menos repetido, B el más.** **Hipótesis no verificada:** la resolución
de la geocodificación no es idéntica entre municipios. Irrelevante para el conteo por municipio; relevante si
se subdividieran.

### 2.3 Días atípicos — `tablas/05_atipicos_por_municipio.csv`

Criterio de Tukey (1,5·IQR) dentro de cada grupo de calendario, por municipio.

| Mun. | Atípicos | % de días | De ellos, ≤ 5 siniestros | Máximo (fecha) | Desde 2024 |
| --- | --- | --- | --- | --- | --- |
| C | 16 | 1,22 | 0 | 13 (2022-11-16) | 9 |
| B | 11 | 0,84 | 0 | 12 (2022-04-29) | 1 |
| D | 33 | 2,51 | 0 | 12 (2023-02-15) | 8 |
| A | 19 | 1,44 | 0 | 10 (2021-11-22) | 10 |
| F | 16 | 1,22 | 0 | 9 (2022-07-22) | 9 |
| G | **35** | 2,66 | **18** | 8 (2024-03-06) | 12 |
| E | 9 | 0,68 | 0 | 11 (2024-04-16) | 4 |
| CH | **35** | 2,66 | **15** | 9 (2021-10-21) | 10 |

**Evidencia.** Todos por arriba. Desde 2024-01-01 (31 % de los días del desarrollo) caen 9 de 16 en C, 10 de
19 en A y 9 de 16 en F, pero 1 de 11 en B. **18 de los 35 de G y 15 de los 35 de CH tienen 5 o menos
siniestros.** **Inferencia:** no hay un patrón común; en conteos tan bajos Tukey marca de más, así que **el
número de atípicos no es comparable entre municipios de media distinta**. No se elimina ni corrige ningún día.

### 2.4 Faltantes codificados en la fuente cruda — `tablas/05b_faltantes_codificados.csv`

Se lee el archivo crudo, se **descarta al instante todo lo posterior a 2025-02-05** y se cuenta qué proporción de
cada columna es un centinela de texto (`SIN DATOS`, `SIN DATO`, `NO SE INGRESO`, `NO SE INGRESÓ`; los mismos del
diagnóstico retirado).

| Columna | Centinela en el archivo (hasta 2025-02-05; 196.431 registros) | Centinela en el recorte de Montevideo (28.629 registros, sin deduplicar) |
| --- | --- | --- |
| Localidad | 18,14 % | 4,47 % (1.281) |
| Calle | 12,50 % (más 1 nulo) | 2,32 % (663) |
| Tipo de Siniestro | 0,01 % | 0,03 % (10) |
| Gravedad, Dia Semana, Departamento | 0 % | 0 % |

**Evidencia.** Los faltantes están codificados como texto, no como nulos. **Inferencia.** El problema de
completitud es en buena medida del interior del país. Ninguna de estas columnas se usa como predictora (el
municipio sale de la geometría y el ETL las descarta): **no se imputa**, se declara el conteo.

### 2.5 Exclusión del primer semestre de 2021, sólo con desarrollo — `tablas/05c_…`, `05d_…`, `05e_…`, `05e2_…`

La evidencia original comparaba contra los mismos meses de 2022 **a 2025** (incluía febrero–junio de 2025, test).
Se rehízo con los **años completos del desarrollo, 2022–2024**, sobre la serie diaria de Montevideo sin
duplicados (mismo criterio que el ETL).

| Paso | Resultado |
| --- | --- |
| 1. Nivel | Enero–junio de 2021: **16,34/día** contra **20,78** en los mismos meses de 2022–2024: **−21,4 %** (2022 −4,1 %; 2023 −1,5 %; 2024 +5,5 %) |
| 2. Forma (índice mensual contra el patrón de 2022–2024) | feb **−9,6 %**, mar **−11,3 %**, abr **−15,5 %**, may **−9,9 %**, jun **−7,3 %**; **enero +0,9 %** (no deprimido) |
| 3. Suficiencia del corte | Julio–diciembre: 21,39 (2021), 22,05 (**+3,1 %**), 22,68 (**+2,8 %**), 23,96 (**+5,7 %**); desvíos de forma de +3,5 % a +7,4 %, **noviembre +18,3 %** |
| Costo | 2.957 registros, 181 días, **9,39 %** del recorte 2021-01-01 → 2025-02-05 |

**Inferencia.** La decisión **se sostiene** con datos sólo de desarrollo (−21,4 % en lugar de −23,7 %). Matices:
enero de 2021 no está deprimido y se excluye por conveniencia; los índices positivos de julio–diciembre están
**inflados por construcción** (la media del propio 2021 incluye el semestre deprimido), así que el +18,3 % de
noviembre no debe leerse como efecto real; que noviembre se aparte hacia arriba **no se explica**.

### 2.6 Cobertura temporal, variable objetivo y serie departamental — `tablas/05f_…`, `03b_…`, `05g_…`, `figuras/fig8_cobertura_temporal.png`

| Año | Siniestros | Días | Media diaria | Variación |
| --- | --- | --- | --- | --- |
| 2021 (jul–dic) | 3.936 | 184 | 21,39 | no comparable |
| 2022 | 7.665 | 365 | 21,00 | no comparable |
| 2023 | 7.873 | 365 | 21,57 | +2,7 % |
| 2024 | 8.398 | 366 | 22,95 | +6,4 % |

(2025 se omite: el desarrollo sólo trae 36 días.)

| Cifra del desarrollo | Valor |
| --- | --- |
| Panel | 10.528 filas, 28.535 siniestros |
| Variable objetivo | **9,34 %** de ceros; media **2,7104**; varianza 3,4415; dispersión **1,270**; máximo 13; modo 2; 19,05 % vale 1; 71,61 % vale 2 o más |
| Serie diaria del departamento | mínimo 4 / mediana 22,0 / máximo **43**; los 1.316 días tienen ≥ 1 siniestro |
| Tukey global | Q1 17, Q3 26, IQR 9; límites 3,5 y 39,5; **7** atípicos, todos por arriba |
| Tukey por grupo de calendario | **16** atípicos (14 por arriba, 2 por debajo), ninguno feriado; 7 por ambos criterios, 9 sólo por grupo |
| Calendario | 891 entre semana / 364 fin de semana / **61** feriados; medias departamentales **23,65 / 18,01 / 14,87**; viernes **25,22**, domingo **15,72** |
| Clima | temperatura media 4,9–31,7 °C; precipitación 0–**58,9 mm** |

**Inferencia.** La lectura es la misma que con el período completo, pero **las cifras cambian** (el máximo diario
y la precipitación máxima del período completo caen fuera del desarrollo): son estas las que corresponde citar.

### 2.7 Distribución territorial — `figuras/fig9_mapa_municipios.png`, `tablas/05h_siniestros_por_municipio_mapa.csv`

Mapa coloreado por los siniestros del desarrollo: de **4.508 (C)** a **2.632 (CH)**, razón 1,71. Refleja dónde se
**registran** los siniestros, no dónde son más probables por exposición.

---

## 3. Tendencia (sección 3)

`tablas/06_media_anual_por_municipio.csv`, `tablas/07_pendiente_por_municipio.csv`, `figuras/fig1_tendencia_por_municipio.png`.

| Mun. | 2021* | 2022 | 2023 | 2024 | 1.ª → 2.ª mitad | Pendiente (%/año) [IC95] | p | ¿IC contiene al agregado? |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| C | 3,44 | 3,37 | 3,33 | 3,64 | +7,3 % | 3,17 [0,16; 6,27] | 0,039 | sí |
| B | 3,13 | 3,15 | 3,23 | 3,34 | +4,6 % | 2,33 [−0,70; 5,45] | 0,13 | sí |
| D | 3,03 | 3,09 | 3,19 | 3,23 | +5,5 % | 2,77 [−0,34; 5,98] | 0,081 | sí |
| A | 2,88 | 2,67 | 2,95 | 3,29 | +15,0 % | **7,34 [4,02; 10,77]** | 1·10⁻⁵ | **no** |
| F | 2,43 | 2,48 | 2,72 | 2,85 | +15,4 % | 7,04 [3,61; 10,58] | 4·10⁻⁵ | sí |
| G | 2,08 | 2,10 | 2,25 | 2,36 | +12,8 % | 5,50 [1,78; 9,36] | 0,0035 | sí |
| E | 2,20 | 2,13 | 2,00 | 2,19 | −0,4 % | 1,02 [−2,83; 5,03] | 0,61 | sí |
| CH | 2,22 | 2,00 | 1,91 | 2,05 | +2,0 % | −0,07 [−3,89; 3,90] | 0,97 | sí |

\* 2021 cubre sólo julio–diciembre; 2025 se omite (36 días de desarrollo). Pendiente del **agregado
departamental: 3,72 %/año**, calculada igual. Pendiente log-lineal con calendario descontado, GLM Poisson con
escala de Pearson.

**Evidencia.** La pendiente va de −0,07 a 7,34 %/año. Es significativa al 5 % sólo en **C, A, F y G**; en B, D,
**E y CH** no se detecta. **Sólo A se aparta del agregado** (su IC no contiene 3,72) **en el desarrollo; con sólo el entrenamiento ya no** (7.6). La forma tampoco es la
misma: B, D, F y G suben casi todos los años; **C, E y CH bajan hasta 2023 y después suben**.

**Inferencia del equipo.** **No puede afirmarse una tendencia común**: es creciente y detectable en cuatro, no se
distingue de cero en dos (E, CH), y A es la más empinada **en el desarrollo (no con sólo el entrenamiento: 7.6)**. La prueba formal de 7.1 sólo ve una diferencia
marginal (p = 0,033), compatible con intervalos individuales anchos: con ~3,6 años una pendiente de 2–3 %/año no
siempre se separa de 0. Que A crezca más rápido concuerda con que su nivel histórico se quede más corto (7.4):
consistencia, **no causalidad**.

---

## 4. Estacionalidad (sección 4)

### 4.1 Perfil semanal — `tablas/08_…`, `tablas/09_…`, `figuras/fig2_perfil_semanal.png`

Cada día dividido por la media del propio municipio.

| Mun. | lun | mar | mié | jue | vie | sáb | dom | feriado | vie ÷ dom | Corr. con el agregado |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| C | 1,145 | 1,053 | 1,163 | 1,058 | 1,243 | 0,897 | 0,566 | 0,670 | 2,19 | 0,992 |
| B | 1,049 | 1,102 | 1,075 | 1,077 | 1,195 | 0,883 | 0,758 | 0,598 | 1,58 | 0,972 |
| D | 1,099 | 1,043 | 1,046 | 1,073 | 1,158 | 0,896 | 0,800 | 0,683 | 1,45 | 0,975 |
| A | 1,014 | 1,022 | 0,993 | 0,918 | 1,172 | **1,143** | 0,818 | 0,762 | 1,43 | **0,609** |
| F | 1,090 | 0,998 | 1,019 | 1,060 | 1,172 | 0,916 | 0,814 | 0,814 | 1,44 | 0,953 |
| G | 1,079 | 1,017 | 1,093 | 1,036 | 1,094 | 0,991 | 0,774 | 0,772 | 1,41 | 0,962 |
| E | 1,034 | 1,136 | 1,071 | 1,151 | 1,224 | 0,853 | 0,650 | 0,660 | 1,88 | 0,959 |
| CH | 1,188 | 1,094 | 1,168 | 1,108 | 1,128 | 0,865 | 0,632 | 0,508 | 1,79 | 0,954 |

**Evidencia.** El domingo es el día más bajo en los ocho; el más alto es el viernes en siete y **el lunes en
CH**. Observado ÷ esperado en feriados: de 0,47 (CH) a 0,79 (F), bajo 1 en los ocho. **A es el único con el
sábado sobre la media (1,14; en los otros siete, de 0,85 a 0,99)**, con miércoles y jueves bajo 1 y correlación
de 0,609 con el perfil agregado (resto ≥ 0,953).

**Inferencia del equipo.** «Fin de semana bajo, viernes alto, feriado bajo» es un rasgo común, con amplitud
distinta. **A es el único cuyo patrón semanal cambia de forma**; da una pista concreta a la pregunta que dejó
abierta el diagnóstico previo de A (¿por qué su patrón es más débil?): no es sólo más débil, es distinto en el sábado. **Causa no
investigada.**

### 4.2 Estacionalidad anual — `tablas/10_…`, `tablas/11_…`, `figuras/fig3_estacionalidad_anual.png`

**Sólo años completos 2022–2024: 3 observaciones por mes y municipio.**

| Mun. | Mes mín. | Índice mín. | Mes máx. | Índice máx. | Amplitud | Corr. con el patrón de los otros 7 |
| --- | --- | --- | --- | --- | --- | --- |
| C | 1 | 0,706 | 6 | 1,148 | 0,442 | 0,855 |
| B | **7** | 0,870 | 11 | 1,155 | 0,285 | 0,589 |
| D | 1 | 0,840 | 6 | 1,161 | 0,321 | 0,627 |
| A | 1 | 0,798 | 11 | 1,093 | 0,294 | 0,880 |
| F | 1 | 0,733 | 7 | 1,112 | 0,379 | 0,822 |
| G | **2** | 0,749 | 5 | 1,131 | 0,382 | 0,791 |
| E | 1 | 0,648 | 11 | 1,164 | 0,516 | 0,560 |
| CH | 1 | 0,691 | 10 | 1,221 | 0,530 | 0,812 |

**Evidencia.** Enero es el mes más bajo en seis de ocho (en B es julio; en G, febrero, con enero en 0,775). El
mes más alto no coincide. **Inferencia:** lo único que se comparte con claridad es el enero bajo en seis; con tres
observaciones por mes no se distingue diferencia real de ruido.

### 4.3 Varianza diaria explicada por el calendario — `tablas/11b_varianza_explicada_por_calendario.csv`

Serie diaria del departamento, en muestra, sólo desarrollo: **tipo de día de 3 niveles (ETL) 21,42 %**; día de la
semana (7 niveles) **19,94 %**; **día de la semana + feriado (8 niveles) 26,51 %**. **Inferencia.** Resumir el
calendario en tres niveles conserva más que el día de la semana solo (incorpora el feriado), pero **pierde ~5
puntos** frente a 8 niveles, que es el calendario de los modelos mínimos de la sección 7. La decisión del ETL se
justificó contra el día de la semana, no contra los 8 niveles. **No se cambió nada**; queda abierta para el E3.

---

## 5. Memoria temporal y transformación (sección 5)

### 5.1 ACF del residuo y Ljung-Box — `tablas/12_…`, `figuras/fig4_acf_residuo_por_municipio.png`

Banda analítica ±1,96/√1.316 = **±0,0540**.

| Mun. | Cruda r1 | r7 | r14 | Residuo r1 | r7 | r14 | Rezagos 1–30 fuera de banda | LB p (7) | LB p (14) | LB p (28) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| C | 0,0557 | 0,0765 | 0,1636 | **0,0554** | −0,0322 | 0,0560 | 4 | 0,0045 | 0,0066 | 0,0412 |
| B | 0,0117 | 0,0384 | 0,0158 | −0,0127 | −0,0113 | −0,0218 | 3 | 0,0189 | 0,0776 | 0,403 |
| D | 0,0459 | 0,0064 | 0,0277 | 0,0453 | −0,0249 | −0,0019 | 2 | 0,335 | 0,0258 | 0,0152 |
| A | 0,0362 | 0,0309 | 0,0441 | 0,0421 | 0,0087 | 0,0158 | 2 | 0,201 | 0,285 | 0,525 |
| F | 0,0526 | 0,0698 | 0,0415 | 0,0517 | 0,0446 | 0,0167 | 3 | 0,151 | 0,496 | 0,0623 |
| G | −0,0214 | 0,0322 | 0,0164 | −0,0175 | 0,0149 | 0,0013 | 2 | 0,0516 | 0,358 | 0,526 |
| E | 0,0531 | 0,0933 | 0,0687 | 0,0367 | 0,0413 | 0,0169 | 3 | 0,129 | 0,0606 | 0,113 |
| CH | 0,0661 | 0,0798 | 0,0532 | 0,0468 | 0,0239 | 0,0028 | 4 | 0,0015 | 0,0052 | 0,0169 |

**Evidencia.** Rezago 1 del residuo de −0,018 a 0,055 (menos del 0,3 % de la varianza). **Sólo C queda sobre la
banda** (y por poco), igual que en el rezago 14. **Ningún rezago 7 del residuo supera la banda**: los múltiplos
de 7 de la ACF cruda eran calendario. **C y CH rechazan Ljung-Box en los tres horizontes**; D en 14 y 28; B sólo
en 7; **A, F, G y E no rechazan en ninguno**.

**Inferencia del equipo.** En el desarrollo la señal temporal posterior al calendario es débil y sólo
consistentemente detectable en C y CH. El rezago de 1 día es **candidato, no supuesto**, con aporte probable pequeño.

### 5.2 Estacionariedad y transformación — `tablas/13_estacionariedad_y_transformacion.csv`

| Mun. | ADF p | KPSS p | ACF r1 con d=1 | λ Box-Cox | Pend. var~media mensual |
| --- | --- | --- | --- | --- | --- |
| C | 7,6·10⁻⁹ | 0,084 | −0,464 | 0,448 | 1,563 |
| B | 3,5·10⁻²⁰ | 0,10 | −0,513 | 0,497 | 0,874 |
| D | ≈ 0 | 0,10 | −0,486 | 0,409 | 1,377 |
| A | ≈ 0 | 0,01 | −0,493 | 0,461 | 0,967 |
| F | ≈ 0 | 0,01 | −0,477 | 0,420 | 1,093 |
| G | ≈ 0 | 0,01 | −0,549 | 0,419 | 1,389 |
| E | 1,0·10⁻¹⁸ | 0,10 | −0,470 | 0,251 | 0,771 |
| CH | 1,3·10⁻¹⁷ | 0,10 | −0,484 | 0,257 | 1,399 |

KPSS acota el p-valor a [0,01; 0,10]. **Evidencia.** ADF rechaza raíz unitaria en los ocho; KPSS rechaza
estacionariedad sólo en A, F y G. Diferenciar una vez sobrediferencia en los ocho (−0,46 a −0,55). λ de
Box-Cox entre 0,41 y 0,50 en seis municipios; **E y CH ≈ 0,25**. 43 puntos mensuales: la pendiente
media–varianza es demasiado ruidosa para leerla por separado. **Inferencia:** la decisión de C y A (no
diferenciar, no aplicar logaritmo) **se extiende a los ocho**; la raíz cuadrada sirve para seis pero no es la
óptima para E y CH: argumento a favor de pérdidas de la familia Poisson.

### 5.3 Rezagos candidatos: ACF sólo con el entrenamiento inicial — `tablas/12b_acf_rezagos_solo_entrenamiento.csv`

Los rezagos 7, 14 y 21 del árbol candidato se eligieron con una ACF del período completo. Para elegir rezagos
**sin usar validación ni test**, la ACF se recalcula con **sólo los 987 días de entrenamiento inicial**
(2021-07-01 → 2024-03-13; banda ±0,0624), con la media de cada grupo de calendario estimada también ahí.

**Evidencia.** En la serie **cruda** los rezagos 7, 14, 21 y 28 superan la banda en **C** (0,070; 0,161; 0,089; 0,136),
en **CH** (rezagos 7, 21 y 28) y en **E** (rezagos 7 y 14). **Sobre el residuo de calendario ningún municipio supera
la banda en los rezagos 1, 7, 14, 21 ni 28** (máximo valor absoluto 0,0611, CH en el rezago 7). **Inferencia.** Con
el entrenamiento solo, los rezagos de la serie cruda **son calendario**: no queda memoria detectable. Los rezagos
7/14/21 del árbol candidato no tienen sustento adicional al calendario en el entrenamiento. La memoria de **C** de la sección 5.1 **aparece al incluir el tramo de validación** (7.6); la de **CH** se detecta también con el
entrenamiento (Ljung-Box conjunto). Puede ser ruido o un cambio reciente, y este notebook no lo distingue. Con 987 días, una autocorrelación de 0,05 está en el límite de lo detectable.

---

## 6. Co-movimiento entre municipios (sección 6) — `tablas/14_…`, `15_…`, `figuras/fig5_…`

**Evidencia.** Correlación media entre pares: **0,080 en la serie cruda y 0,033 en el residuo de calendario**;
el residuo va de −0,035 a 0,094 (máximo C–G); **4 de 28 pares** superan ±0,054 (se esperan 1,4). **Inferencia.**
Casi toda la correlación cruda es calendario compartido; queda un componente común real pero mínimo (el mayor
par explica menos del 1 % de la varianza). Dado el calendario, **los municipios son prácticamente
independientes día a día**: entrenar con los ocho aporta observaciones no redundantes, y no hay base para usar
como predictor lo que ocurre el mismo día en otro municipio.

---

## 7. ¿Un solo modelo o varios? (sección 7)

*Esta sección ya usaba sólo el bloque de desarrollo; ninguna cifra cambió respecto de la primera versión.*

### 7.1 Pruebas de homogeneidad — `tablas/16_pruebas_de_homogeneidad.csv`

10.528 observaciones (1.316 días × 8). Prueba F de cuasi-verosimilitud entre un modelo que no distingue
municipios en el aspecto indicado y otro que sí.

| Hipótesis alternativa | gl | F | p | Reducción de desvianza |
| --- | --- | --- | --- | --- |
| Nivel propio por municipio | 7 | 134,47 | ≈ 2·10⁻¹⁹⁰ | **7,545 %** |
| Perfil de calendario distinto por municipio | 49 | 2,71 | 1,5·10⁻⁹ | 1,139 % |
| Tendencia distinta por municipio | 7 | 2,18 | 0,033 | 0,132 % |
| Estacionalidad anual distinta por municipio | 77 | 1,38 | 0,016 | 0,919 % |
| Efecto de la lluvia distinto por municipio | 7 | 1,11 | 0,35 | 0,067 % |

**Evidencia.** Con Bonferroni (0,01; 5 pruebas) sólo el nivel y el perfil de calendario lo superan. **Salvedad:**
los p-valores asumen errores independientes y hay autocorrelación residual (hasta 0,055) y correlación entre
municipios (0,033): 0,016 y 0,033 son **no concluyentes**. **Inferencia.** El nivel es la heterogeneidad
dominante (un orden de magnitud sobre cualquier otra); el calendario es distinto con efecto chico; tendencia,
estacionalidad anual y lluvia no muestran diferencias sostenibles.

### 7.1b ¿Quién se aparta del perfil agregado? — `tablas/17_perfil_calendario_vs_agregado.csv`

| Mun. | F (7 gl) | p de Holm (8 pruebas) | Reducción de desvianza | ¿Se aparta? |
| --- | --- | --- | --- | --- |
| C | 4,28 | 0,0008 | 2,074 % | **sí** |
| B | 0,90 | 1,0 | 0,434 % | no |
| D | 0,74 | 1,0 | 0,376 % | no |
| A | 6,21 | 3·10⁻⁶ | 2,920 % | **sí** |
| F | 1,58 | 0,68 | 0,768 % | no |
| G | 0,98 | 1,0 | 0,455 % | no |
| E | 1,58 | 0,68 | 0,761 % | no |
| CH | 2,63 | 0,064 | 1,251 % | no (cerca) |

**Evidencia.** Se apartan A y C; CH queda cerca. **Inferencia.** La heterogeneidad del calendario la concentran
dos municipios. C difiere sin cambiar de forma (correlación 0,992): tiene la mayor amplitud semanal.

### 7.2 Diseño de la comparación predictiva

Seis modelos multiplicativos, estimados sólo con los días de ajuste; calendario = 8 grupos (lunes … domingo,
feriado).

| Modelo | Qué es | Qué mide al compararlo |
| --- | --- | --- |
| M0 | constante global | piso |
| M1 | calendario del agregado × media global | un modelo que **no conoce el municipio** |
| M2 | calendario del agregado × **media del municipio** | un modelo único con nivel propio |
| M3 | calendario **propio** × media del municipio | un modelo por municipio |
| M4 | calendario y nivel de los **otros 7** | un municipio **sin datos propios** |
| M5 | calendario de los otros 7 × media propia | forma «prestada», nivel propio |

Pliegue A: ajuste 658 días, validación 2023-04-20 → 2024-03-13. Pliegue B: ajuste 987 días, validación
2024-03-14 → 2025-02-05 (`02_particiones.csv`, `19_metricas_completas_validacion.csv`). Métrica: desvianza de
Poisson media. **Regla fijada antes de ejecutar:** un municipio *necesita su propio calendario* si, en los dos
pliegues, M3 mejora a M2 en ≥ 1 % y el IC95 de la diferencia (bootstrap por bloques semanales) excluye 0.

### 7.3 Resultados — `tablas/18_…`, `20_…`, `21_…`, `figuras/fig6_calendario_propio_vs_agregado.png`

Desvianza media de los 8 en validación:

| | M0 | M1 | M2 | M3 | M4 | M5 |
| --- | --- | --- | --- | --- | --- | --- |
| Pliegue A | 1,3897 | 1,3291 | 1,2278 | 1,2305 | 1,3614 | 1,2302 |
| Pliegue B | 1,4014 | 1,3441 | 1,2385 | 1,2344 | 1,3791 | 1,2420 |

Diferencias pareadas, promedio de los 8 (positivo = mejora del segundo modelo; IC95 por bootstrap):

| Comparación | Pliegue A | Pliegue B |
| --- | --- | --- |
| M0 → M1 (calendario común) | +4,36 % [IC excluye 0] | +4,09 % [IC excluye 0] |
| **M1 → M2 (nivel propio)** | **+7,62 %** [IC excluye 0] | **+7,86 %** [IC excluye 0] |
| **M2 → M3 (calendario propio)** | −0,22 % [−0,0132; 0,0072] | +0,32 % [−0,0056; 0,0134] |
| M5 → M3 (forma prestada vs. propia) | −0,03 % [−0,0125; 0,0111] | +0,61 % [−0,0032; 0,0181] |
| M4 → M2 (municipio sin datos propios) | **+9,81 %** [IC excluye 0] | **+10,20 %** [IC excluye 0] |

Reducción relativa de desvianza M2 → M3 por municipio (`20_…`):

| Mun. | Pliegue A | Pliegue B | ¿Cumple la regla? (`21_…`) |
| --- | --- | --- | --- |
| C | −2,05 % | +1,22 % | no |
| B | −0,27 % | +0,62 % | no |
| D | −1,57 % | +0,09 % | no |
| **A** | **+4,06 %** [IC excluye 0] | **+4,24 %** [IC excluye 0] | **sí** |
| F | −0,75 % | −0,28 % | no |
| G | −0,45 % | **−2,45 %** [IC excluye 0, empeora] | no |
| E | −1,82 % | −0,60 % | no |
| CH | +1,53 % | −0,56 % | no |

**Evidencia.** Cumple la regla **1 de 8 (A)**. A pierde ~5 % (4,91 % y 5,25 %) si se le presta el calendario de
los otros siete (M5 → M3). C y CH cambian de signo entre pliegues y sus IC incluyen 0 en ambos.

**Inferencia del equipo.**

1. **Lo que más separa a los municipios es el nivel, no la forma:** conocer el nivel mejora ~7,6–7,9 %; un
   municipio sin datos propios cuesta ~10 %. Es el bloque que el diagnóstico principal ya había identificado
   (tasa histórica del municipio) y que el panel todavía no incluye.
2. **Un calendario común alcanza para siete de los ocho.** En promedio especializar no mejora y puede
   empeorar (G): con 658–987 días y 8 grupos de calendario, el perfil propio estima ruido. **Detectable no es
   explotable:** C y CH son distintos en muestra y no ganan fuera de muestra.
3. **A es la excepción reproducible**, en coherencia con su sábado alto (4.1), que se sostiene con sólo el entrenamiento (7.6). Su pendiente mayor **no** se sostiene sin la validación.
4. **Primera hipótesis a probar: un solo modelo con variable de nivel por municipio.** Modelos separados **no
   están respaldados** por estos datos, con la posible excepción de A, que se resuelve primero con un término
   propio dentro del modelo común.

### 7.4 Calibración de nivel — `tablas/22_razon_total_M2_por_municipio.csv`

Razón total predicho/observado de M2:

| Mun. | Pliegue A | Pliegue B |
| --- | --- | --- |
| C | 0,978 | 0,900 |
| B | 0,940 | 0,997 |
| D | 0,965 | 0,945 |
| A | 0,927 | **0,842** |
| F | 0,903 | 0,865 |
| G | 0,902 | 0,906 |
| E | 1,086 | 0,911 |
| CH | 0,968 | 1,007 |

**Evidencia.** Rango 0,902–1,086 (A) y 0,842–1,007 (B); siete de ocho subestiman en cada pliegue; en B, **A es el
que más se queda corto (0,842)**. **Inferencia.** La tendencia hace que el nivel histórico subestime en casi
todos, pero no por igual; coherente con la pendiente mayor de A **en el desarrollo (7.6: no se sostiene con sólo el entrenamiento)**, sin ser una medición de esa causa. El nivel
por municipio debe poder **recalibrarse** (por ejemplo con una ventana reciente).

### 7.5 Aporte de cada bloque de variables, fuera de muestra — `tablas/23_…`, `23b_…`, `24_…`, `25_…`, `figuras/fig7_aporte_bloques.png`

Mide cuánto aporta cada bloque de información y justifica la forma de la línea de referencia multiplicativa.
Mismo esquema que 7.2 (dos pliegues dentro del desarrollo, todo estimado sólo con el ajuste; **el test no
interviene**). Reemplaza la medición equivalente del diagnóstico retirado, que se hacía con el período completo.

Mejora de la desvianza media de los 8 respecto de la constante global (positivo = mejor), IC95 por bootstrap de
bloques semanales:

| Bloque | Predictor | Pliegue A | Pliegue B |
| --- | --- | --- | --- |
| B1 | sólo calendario | +4,36 % [3,07; 5,62] | +4,09 % [2,67; 5,51] |
| B2 | sólo tasa del municipio | +7,28 % [5,54; 9,07] | +7,54 % [5,56; 9,55] |
| **B3** | **tasa × calendario (= M2)** | **+11,65 %** [9,29; 13,84] | **+11,63 %** [9,45; 13,71] |
| B4 | B3 × factor de lluvia | +11,33 % [8,94; 13,49] | +11,61 % [9,41; 13,73] |
| B5 | celdas municipio × calendario (= M3) | +11,45 % [9,06; 13,77] | +11,91 % [9,48; 14,23] |
| B6 | celdas saturadas municipio × calendario × mes | **−7,64 %** [−17,29; 0,02] | **−3,31 %** [−18,08; 6,86] |

Comparaciones entre bloques (`23b`): B2 → B3 **+4,71 % / +4,42 %** (IC excluye 0); B3 → B4 **−0,36 %** (IC −0,65 a
−0,07) y **−0,01 %** (IC con 0); B3 → B6 **−21,83 % / −16,90 %** (IC excluye 0). B6 ocupa 760 de 768 celdas
posibles (celda vacía: cae a B3; piso de 1e-6). **Deriva del nivel** (`24`): la media diaria por municipio sube
**5,03 %** (A) y **8,83 %** (B) de ajuste a validación. **Varianza del desarrollo** (`25`): 7,71 % entre
municipios y 18,04 % entre días, de lo cual ≈ 11,54 % es el azar de Poisson al promediar 8 municipios por día;
exceso atribuible al día, a lo sumo **6,50 %**.

**Inferencia del equipo.** (1) La tasa del municipio aporta más que el calendario y la combinación
multiplicativa es la mejor, con IC que excluye 0 frente a cada bloque solo. (2) La lluvia (indicador binario
`llovió`) no aporta. (3) Saturar con celdas independientes memoriza ruido y queda peor que la constante.
(4) La variación entre días no contradice lo anterior: casi dos tercios es ruido de Poisson compartido.
(5) El nivel sube entre ajuste y validación, así que las mejoras son conservadoras (coherente con 7.4).
**Las cifras no son comparables con las del diagnóstico retirado** (otro protocolo y período, test incluido); la
conclusión cualitativa coincide. No se recalculan los «techos en muestra»: no informan ninguna decisión.

### 7.6 Robustez con sólo el entrenamiento inicial — `tablas/25b_…`–`25f_…`

**Criterio del equipo (confirmado con el docente, 2026-10-08): la ventana de validación SÍ puede usarse en los diagnósticos**; sólo el test queda vedado. Por eso las cifras del desarrollo son válidas. Esta sección es un **chequeo de estabilidad**, no un requisito: las que **orientan decisiones** (3, 4.1, 4.2, 5.1, 5.2, 7.1) se repitieron con **sólo los 987 días de entrenamiento** (2021-07-01 → 2024-03-13) para ver cuánto dependen de incluir la validación.


| Conclusión | Con sólo el entrenamiento | Estabilidad |
| --- | --- | --- |
| Nivel distinto entre municipios | F = 98,31; 7,36 % | **Estable** |
| Perfil de calendario distinto | F = 2,08; p = 1,6·10⁻⁵; 1,165 % | **Estable** |
| A tiene el sábado alto | 1,111 (desarrollo 1,143); correlación 0,769 (0,609); siguiente G 1,003 | **Estable** (G ≈ 1) |
| Calendario propio de A mejora | pliegue A (validación dentro del entrenamiento): +4,06 %, IC excluye 0 | **Estable** |
| No diferenciar ni transformar | λ 0,25–0,50; r1 con d = 1 de −0,46 a −0,54; KPSS rechaza sólo en F | **Estable** |
| Lluvia no cambia por municipio | p = 0,33 | **Estable** |
| Tendencia distinta por municipio | p = 0,123; 0,131 % | **No concluyente** |
| A con la pendiente mayor | A 3,89 %/año [−1,12; 9,16], p = 0,13; agregado 2,61 %/año | **Sensible a la ventana** |
| Tendencia detectable en C, A, F, G | con el entrenamiento: sólo B (5,23), F (6,07), G (6,20) | **Cambia** |
| C con memoria de corto plazo | Ljung-Box: C no rechaza (0,069; 0,147; 0,364) | **Sensible a la ventana** |
| CH con memoria de corto plazo | rechaza (0,0006; 0,0008; 0,009) | **Estable** |

**Inferencia.** La conclusión central se sostiene sin mirar la validación. Se **debilitan dos afirmaciones secundarias**:
la pendiente mayor de A y la memoria de C: conviene citarlas **con la mención de que aparecen al incluir la validación**. No hay evidencia
concluyente de una tendencia específica por municipio.

---

## 8. Síntesis para el informe

| Aspecto | ¿Homogéneo entre los 8? | Evidencia principal | Consecuencia para el modelado |
| --- | --- | --- | --- |
| Calidad de la serie | **Sí** | cobertura completa; ceros y dispersión explicados por la media (2.1) | un mismo tratamiento del objetivo |
| **Nivel** | **No** (1,71×) | F = 134; 7,5 % de la desvianza; M1 → M2 ≈ 7,7 % | **variable de nivel por municipio, obligatoria** |
| Aporte de cada bloque (7.5) | **Tasa > calendario**; combinación multiplicativa la mejor | tasa +7,3/+7,5 %; calendario +4,4/+4,1 %; ambos +11,6 %; lluvia sin aporte; celdas saturadas peor que la constante | línea de referencia tasa × calendario; no incorporar la lluvia como binaria; no saturar |
| Calendario semanal | **Casi** (excepción A; débil C, CH) | 5 de 8 indistinguibles; M2 → M3 no mejora en promedio | calendario común; probar un término propio para A |
| Tendencia | **No** | −0,07 a 7,34 %/año; sólo C, A, F, G detectables; A más empinada **sólo en el desarrollo** (7.6) | no suponer pendiente común; permitir recalibrar el nivel |
| Estacionalidad anual | **Sólo enero, con 3 años** | enero mínimo en 6 de 8 | no modelar un patrón anual por municipio |
| Memoria temporal | **Débil**; detectable sólo en C y CH | r1 residual −0,018 a 0,055 | rezagos como candidatos, no como supuesto |
| Transformación del objetivo | **Sí** | no diferenciar; λ de 0,25 a 0,50 | pérdida de la familia Poisson, sin transformar |
| Clima | **Sí** (una sola serie) | lluvia homogénea, p = 0,35 | no distingue municipios |
| Co-movimiento | **Independientes** dado el calendario | correlación residual media 0,033 | observaciones no redundantes |

**Respuesta a la pregunta del equipo (inferencia).** Los datos respaldan **un modelo único para los ocho
municipios que incorpore el nivel de cada uno**; no respaldan entrenar un modelo por municipio.

**Qué probar en el Entregable 3, en este orden:** (1) modelo común con variable de nivel por municipio,
calculada sólo con entrenamiento y con recalibración; (2) un término propio para A (municipio × día de la
semana), midiendo si cierra la brecha sin perjudicar a los otros siete; (3) sólo si no alcanza, un modelo
separado para A como desafiante.

---

## 9. Limitaciones y lo que NO puede afirmarse

**Limitaciones y amenazas a la validez**

- **Modelo mínimo.** La sección 7 mide estructura compartida de nivel y calendario, **no** el desempeño del
  modelo final; un árbol o boosting con rezagos podría hacer aparecer o desaparecer heterogeneidades.
- **Poder bajo.** Ocho municipios, ~3,6 años y dos pliegues de 329 días: que C y CH no ganen con calendario
  propio puede ser falta de datos más que ausencia de diferencia.
- **Supuestos de las pruebas.** Los p-valores de 7.1 asumen errores independientes; el bootstrap por bloques
  semanales conserva la dependencia de corto plazo, no la anual.
- **El test no se consultó, y eso limita lo que se puede decir:** si el último tramo se comporta distinto (por
  ejemplo, en tendencia), este diagnóstico no lo sabe. Es lo que el test medirá.
- **M2 incluye al propio municipio** en el calendario agregado (1/8 del peso): favorece levemente a M2 frente a
  M5; no altera M2 contra M3. **M4 es un escenario hipotético:** los ocho municipios están fijos.
- **Criterio sobre la validación (confirmado con el docente, 2026-10-08):** la validación **puede usarse en los diagnósticos**; el test, no. Todas las secciones usan el desarrollo. En 7.6, un chequeo con sólo el entrenamiento muestra que la conclusión central es estable y que dos afirmaciones secundarias (pendiente mayor de A, memoria de C) **aparecen al incluir la validación**: citables, con esa mención.
- **Subregistro** (heredado): no medible con estos datos y probablemente desigual entre municipios.
- **Causas no investigadas:** el sábado alto de A; los mínimos de A y D en 2021; la menor
  repetición de coordenadas de A.

**Frases que NO deben aparecer en el informe**

| Frase | Por qué los datos no la sostienen |
| --- | --- |
| «Los municipios son iguales» / «se comportan igual» | El nivel difiere 1,71× y A se comporta distinto en calendario y pendiente. |
| «La tendencia es creciente en todos los municipios» | En E (1,02 %/año, p = 0,61) y CH (−0,07 %/año, p = 0,97) no se detecta. |
| «Hace falta un modelo por municipio» | Especializar el calendario no mejora en promedio (−0,22 % y +0,32 %, ICs con 0). |
| «El calendario de C es distinto y por eso necesita su propio modelo» | Distinto en muestra, no mejor fuera de muestra (−2,05 % y +1,22 %). |
| «Un solo modelo resuelve todo» | Se afirma sólo para estructura de nivel y calendario con un modelo mínimo. |
| «A es el municipio más riesgoso» / «X es el más peligroso» | Los datos miden lo que se **registra**, no el riesgo; no hay exposición. |
| «El pico de siniestros de X es en <mes>» | 3 observaciones por mes: el máximo cambia con poco. |
| «El 2021 de A y D sigue afectado por la pandemia» | Observación (mes más bajo al inicio), no investigada. |
| «G y CH tienen más atípicos» | 18 y 15 de sus 35 son días de 4–5 siniestros; Tukey no es comparable entre medias distintas. |
| «Los municipios se influyen entre sí» | Correlación residual media de 0,033. |
| «Hay autocorrelación en todos los municipios» | Sólo C y CH la muestran de forma consistente. |
| «El modelo tiene una desvianza de 1,23» | Es el modelo mínimo de este diagnóstico, no el del proyecto. |
| «Estas cifras coinciden con las de los diagnósticos anteriores (C, A, datos)» | Aquellos usaban el período completo; éste, sólo desarrollo. |

---

## 10. Índice de artefactos

| Afirmación | Respaldo |
| --- | --- |
| Integridad del panel de desarrollo; ninguna fila de test | `01_verificacion_integridad.csv` |
| Particiones 987 / 329 / 329 (test marcado «no cargado») | `02_particiones.csv` |
| Nivel, dispersión, ceros, racha de ceros, mes extremo | `03_resumen_por_municipio.csv` |
| Concentración geográfica de los eventos | `04_concentracion_geografica_eventos.csv` |
| Atípicos por municipio | `05_atipicos_por_municipio.csv` |
| Medias anuales y pendientes | `06_…`, `07_…`; `fig1_tendencia_por_municipio.png` |
| Perfil semanal, feriado | `08_…`, `09_…`; `fig2_perfil_semanal.png` |
| Estacionalidad anual | `10_…`, `11_…`; `fig3_estacionalidad_anual.png` |
| ACF, Ljung-Box | `12_…`; `fig4_acf_residuo_por_municipio.png` |
| ADF, KPSS, diferenciación, Box-Cox | `13_estacionariedad_y_transformacion.csv` |
| Co-movimiento | `14_…`, `15_…`; `fig5_correlacion_entre_municipios.png` |
| Pruebas de homogeneidad | `16_pruebas_de_homogeneidad.csv`, `17_perfil_calendario_vs_agregado.csv` |
| Desvianza por modelo y municipio | `18_…`, `19_metricas_completas_validacion.csv` |
| Comparaciones pareadas y regla | `20_…`, `20b_…`, `21_regla_de_decision.csv`; `fig6_calendario_propio_vs_agregado.png` |
| Calibración de nivel | `22_razon_total_M2_por_municipio.csv` |
| Aporte de cada bloque, deriva del nivel, descomposición de varianza | `23_…`, `23b_…`, `24_…`, `25_…`; `fig7_aporte_bloques.png` |
| Faltantes, corte de la pandemia, cobertura temporal, objetivo y serie departamental, mapa | `05b_…`, `05c_…`–`05e2_…`, `05f_…`, `03b_…`, `05g_…`, `05h_…`; `fig8`, `fig9` |
| Varianza explicada por el calendario; rezagos con sólo entrenamiento | `11b_…`; `12b_…` |
| Robustez de los diagnósticos que orientan decisiones, con sólo el entrenamiento | `25b_…`–`25f_…` |
| Procedencia y entorno | `00_procedencia.csv`, `00b_entorno.csv`; listado en `26_artefactos.csv` |

---

## 11. Qué queda pendiente

- **Qué se recuperó y qué no del diagnóstico retirado (2026-10-05).** *Recuperado, sólo con desarrollo:* el
  **aporte de cada bloque de variables** (7.5), los **faltantes codificados** (2.4), la **evidencia del corte de la
  pandemia** (2.5), la **cobertura temporal** y las cifras del objetivo y de la serie departamental (2.6), el **mapa**
  (2.7), la **varianza explicada por el calendario** (4.3) y los **rezagos con sólo entrenamiento** (5.3). *No se
  rehízo, por decisión del equipo:* la **verificación cruzada independiente con el ETL**: el ETL sólo se verifica a
  sí mismo. *No hace falta rehacer:* duplicados, formato de fecha, coordenadas, asignación a municipios y clima, que
  documenta el ETL (`preparacion_montevideo`, `experiments/etl_montevideo/`; ojo: el ETL procesa el período completo,
  por construcción del conjunto). Todo lo del diagnóstico retirado sigue en `entregable_2`, pero **se calculó con el
  test**. `resumen_linea_base.md` y `resumen_preparacion_montevideo.md` aún citan cifras antiguas con una nota que
  lo advierte; **las equivalentes sólo con desarrollo están en este documento**.
- **Decidido (2026-10-07): no se toca el ETL** (calendario de 3 niveles, 21,42 %). El calendario de 8 niveles (26,51 %)
  se derivará de la fecha en el modelado. Recomendado, no confirmado: compararlos sobre la validación en el
  Entregable 3 y declarar la salvedad en el informe.
- **Decidido (2026-10-08, con el docente): la validación puede usarse en los diagnósticos.** 7.6 queda como chequeo de
  estabilidad.
- Verificar el patrón de A (sábado alto) con la fuente. **No se investigó.**
- Ejecutar en el Entregable 3 el orden de la sección 8 con el **modelo final** y el protocolo de
  `linea_base.ipynb`; el test sigue reservado para la evaluación final.
