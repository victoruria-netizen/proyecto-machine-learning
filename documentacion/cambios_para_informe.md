# Cambios para el informe — qué se hizo el 2026-10-05, qué decidió el equipo y qué hay que actualizar

**Para quién es este documento.** Para quien actualice `documentacion/informe/Entregable2_PAA_20-09-26.md` (el
informe en Markdown, versión vigente del 2026-10-05). Esa persona tendrá el repositorio pero no el contexto de por qué
se hicieron los cambios. Este documento es el puente: dice **qué se hizo**, **qué decidió el equipo**, **qué del
informe quedó desactualizado**, con qué **artefacto** se reemplaza cada cifra y qué **queda abierto**.

**Reemplaza** al `cambios_para_informe.md` anterior (puente de la unificación `base`/`base_2` → `linea_base`,
2026-09-24/25), que el equipo confirmó como **ya aplicado**. Sigue en el historial de git.

**Cómo se armó.** Se leyó el informe completo (capítulos 1 a 4, anexos A a F, listas, glosario) y se contrastó con el
estado del repositorio. Las referencias `L<n>` son **números de línea del `.md` actual**; cambian si se edita. **No se
editó el informe en esta sesión.** En lo que sigue, `dm/` = `experiments/diagnostico_municipios/tablas/` (y `dm/fig…` =
`experiments/diagnostico_municipios/figuras/`).

> ### Reglas del equipo que originan casi todo lo de abajo
>
> 1. **El test** —el bloque final, **2025-02-06 → 2025-12-31**, 329 días— es «nuestro futuro»: **no se consulta en
>    ningún momento del diagnóstico**; sólo se usa para evaluar el modelo al final del proyecto.
> 2. **La ventana de validación SÍ puede usarse en los diagnósticos** (el equipo lo confirmó con el docente,
>    2026-10-08). Sigue vigente evitar el leakage en el **ajuste y la evaluación de modelos**: lo que se ajusta usa sólo
>    datos anteriores a lo que evalúa, y las transformaciones que aprenden de los datos se ajustan sólo con
>    entrenamiento. *(Hasta el 2026-10-07 se había asumido lo contrario; ver decisión 7.)*

---

## A. Qué se hizo en la sesión

| # | Qué | Resultado |
| --- | --- | --- |
| 1 | **Notebook nuevo `notebooks/diagnostico_municipios.ipynb`**: diagnóstico de los **ocho municipios** y respuesta a «¿un solo modelo o varios?». Acompañante: `documentacion/resumen_diagnostico_municipios.md`. | 90 celdas, sin errores; **46 tablas y 9 figuras** en `experiments/diagnostico_municipios/`. |
| 2 | **Corrección por la regla del test.** La primera versión calculó las secciones descriptivas sobre el período completo. Se rehízo: se **descartan al leer las filas posteriores a 2025-02-05** (con `assert`). | Todo usa **desarrollo** (2021-07-01 → 2025-02-05, 1.316 días). La versión previa quedó descartada. |
| 3 | **Se retiraron de `main`** `diagnostico_datos`, `diagnostico_datos_municipio` y `diagnostico_zona_contraste` (notebooks, tablas y `resumen_*.md`). | Siguen en la rama `entregable_2`. Calculaban con el período completo. |
| 4 | **Medición del aporte de cada bloque de variables** (sección 7.5), sólo con desarrollo. | Reemplaza a la Tabla 3. |
| 5 | **Rehecho sólo con desarrollo** lo que dependía del archivo crudo y de cifras con el test: **faltantes codificados (2.4)**, **evidencia del corte de la pandemia (2.5)**, **cobertura temporal, objetivo y serie departamental (2.6)**, **mapa (2.7)**, **varianza explicada por el calendario (4.3)** y **rezagos con sólo entrenamiento (5.3)**. | Cada cifra del informe que dependía de eso tiene ahora artefacto (sección C y D). |
| 6 | Limpieza de referencias en `README.md`, `CLAUDE.md`, `requirements.txt`, `HANDOFF.md`, `registro_uso_IA.md`, notas en `resumen_linea_base.md` y `resumen_preparacion_montevideo.md`, comentarios de `linea_base` y `preparacion_montevideo`. | Sin cambio de resultados. `linea_base` **no se tocó**: Tablas 1, 4 y 5 vigentes. |
| 7 | `geopandas` vuelve a usarse (lo importa el mapa de 2.7). | Resuelve el pendiente de «`geopandas` sin uso». |
| 8 | **Sección 7.6 (robustez):** los diagnósticos que orientan decisiones (tendencia, calendario, memoria, transformación, homogeneidad) se repiten con **sólo el entrenamiento inicial** (987 días) y se contrastan con los del desarrollo. | `dm/25b`–`25f`. Resultado: la conclusión central **se sostiene**; **se debilitan** dos afirmaciones secundarias (ver C.5b). |

Estado del repo: **sin commit**.

### Conclusiones nuevas que el informe debe incorporar (evidencia → inferencia)

*Evidencia (todo sobre desarrollo):* el nivel difiere **1,71×** entre municipios y explica el **7,5 %** de la desvianza;
dado el nivel, un **calendario común** sirve para siete de ocho (especializarlo no mejora en promedio: −0,22 % y
+0,32 %); **A** es la excepción reproducible (sábado alto, +4,06 % y +4,24 % con calendario propio); la **tendencia no
es común** en el desarrollo (de −0,07 a 7,34 %/año; detectable sólo en C, A, F y G), **pero con sólo el entrenamiento no hay
diferencia sostenible** (p = 0,123; A deja de apartarse del agregado); la **memoria temporal** es débil (con sólo el
entrenamiento ningún rezago individual supera la banda una vez descontado el calendario; Ljung-Box conjunto sólo rechaza en CH); la lluvia no aporta; los municipios son casi
independientes dado el calendario. *Inferencia del equipo (redactada con Claude, a validar):* **un modelo único con
variable de nivel por municipio**; no se respaldan modelos por municipio, con la posible excepción de A.

---

## B. Decisiones del equipo (2026-10-05) y sus consecuencias

| # | Decisión | Consecuencia para el informe |
| --- | --- | --- |
| **1** | **El test sigue siendo el mismo** (el bloque final). Como el Entregable 2 ya pasó, hubo que **declarar** su uso en el documento. | **No hay que reescribir** lo que el informe ya declara en 3.4.4, el Cuadro 3, 4.3.2, 4.3.3 y el glosario: el bloque final fue consultado en el E2 (modelado, Tablas 4 y 5) y **eso no se revierte**. **Sí hay que agregar** que **desde el 2026-10-05 ningún diagnóstico lo consulta** y que **para el Entregable 3 el test se reserva hasta la evaluación final**. Se **descarta** como alternativa la idea de usar otro tramo (p. ej. 2026) *salvo que el equipo la reabra*: el informe dice (L577) que la alternativa «queda pendiente de acordar»; ahora **hay que reemplazar esa frase** por la decisión (el test es el bloque final) o dejarla como opción no adoptada. |
| **2** | Cifras de **descripción del conjunto** (36.612 siniestros, 13.160 filas, 1.645 días, 224.694 registros, recorte paso a paso): **se mantienen**. Las **estadísticas descriptivas del diagnóstico** pasan a ser **de desarrollo**. | La sección C usa este criterio: lo estructural queda; ceros, media, dispersión, máximo, feriados, rango de precipitación, etc., se reemplazan (D.2, D.4). |
| **3** | **Banda nula: la misma que el notebook** (analítica, ±1,96/√n). | Reescribir el glosario (L243) y la Tabla 2; eliminar «simulación de 400 series» (L661, Anexo D). Con n = 1.316 la banda es **±0,0540**. |
| **4** | **Se quita la verificación cruzada con el ETL.** | **Eliminar** la Tabla E1 y su nota (Anexo E), la frase de 4.2 (L724) y la de 3.3.1 (L513) sobre la reconstrucción independiente, y las entradas de las listas. La corrección del conjunto se apoya **sólo en las 16 verificaciones internas del ETL**. No citar la rama `entregable_2` para esto. |
| **5** | **Se rehace con el bloque de desarrollo** lo que sólo existía en los notebooks retirados (pandemia, faltantes, cobertura temporal, mapa, etc.), **evitando el leakage en test y en validación**. | Hecho (A.5). Cada punto del informe tiene artefacto: ver C. |

### Decisiones del equipo, segunda ronda (2026-10-07)

Resuelven las tres preguntas que quedaban abiertas.

| # | Decisión | Consecuencia para el informe |
| --- | --- | --- |
| **6** | **No se toca el ETL** (calendario de 3 niveles). | El informe mantiene `tipo_dia` de tres niveles como decisión de preparación. El calendario de 8 niveles (día + feriado) **se derivará de la fecha en el modelado**, sin cambiar el ETL. **Recomendado, no confirmado por el equipo:** agregar en el informe la salvedad de que 3 niveles explican 21,42 % de la varianza diaria y 8 niveles 26,51 % (`dm/11b`), y comparar 3 contra 8 niveles sobre la **validación** en el Entregable 3. |
| **7** | **(2026-10-08, confirmada con el docente) La ventana de validación puede usarse en los diagnósticos.** *Reemplaza* la versión del 2026-10-07 («sólo lo puramente descriptivo usa todo el desarrollo»). | **Los diagnósticos que usan el desarrollo completo son válidos y citables**: tendencia, calendario, memoria, transformación y homogeneidad. **No hay que quitar ni rehacer nada.** La sección 7.6 queda como **chequeo de estabilidad entre ventanas** (informativo, no un requisito). El informe puede decir «desarrollo» y citar sus cifras. |
| **8** | **La Tabla C2 (grilla / barrios / municipios) se conserva como antecedente histórico.** | **No se recalcula.** Conservarla con la nota explícita: *«versiones previas del ETL; período completo 2021–2025 (incluye el bloque final); no reproducible en `main`; antecedente exploratorio de la decisión de partición territorial»*. La fila de municipios **queda con sus valores originales del período completo** (13.160 filas, 8,60 %, 2,7821, 1,259, 13) para que las tres filas sigan siendo comparables; **no** mezclarla con las cifras de desarrollo del resto del informe (10.528 filas, 9,34 %…). |

### Decisión sobre el tipo de ventana (2026-10-08)

| # | Decisión | Consecuencia para el informe |
| --- | --- | --- |
| **9** | **Se usará sólo ventana deslizante (rolling window)** y **no se comparará con la expansiva.** El equipo lo fundamenta en que los datos tienen una pequeña sobredispersión y no conviene tomar en cuenta días muy lejanos al presente. | Ver **C.8** (qué líneas cambian) y la **advertencia sobre la fundamentación**. **Estado en el repo: `linea_base.ipynb` sigue usando ventana expansiva**; las Tablas 4 y 5 del informe corresponden a esa versión. |

---

## C. Cambios en el informe, sección por sección

### C.1 Listas y glosario

| Dónde | Hoy dice | Hay que |
| --- | --- | --- |
| Lista de tablas (L205–229) | Tablas 2, 3, B1–B3, C1–C2, D1, **E1** | Actualizar; **quitar la Tabla E1** (decisión 4). |
| Lista de ilustraciones (L195–199) | B1, C1, D1 | Se rehacen: B1 → `dm/fig8_cobertura_temporal.png`; C1 → `dm/fig9_mapa_municipios.png`; D1 → `dm/fig4_acf_residuo_por_municipio.png`. |
| Glosario **Banda nula** (L243) | «obtenido… por simulación» | «banda analítica ±1,96/√n» (decisión 3). |
| Glosario **Bloque final** (L245) | «Fue consultado durante el desarrollo del E2» | **Se mantiene.** Agregar: «los diagnósticos posteriores al 2026-10-05 no lo consultan; se reserva para la evaluación final». |
| Glosario | — | Agregar **«Desarrollo»** (2021-07-01 → 2025-02-05, 1.316 días: entrenamiento inicial + validación) y, si se citan, **«Prueba F de cuasi-verosimilitud»**. |

### C.2 Capítulos 1 y 2

| Dónde | Hoy dice | Hay que |
| --- | --- | --- |
| **2.3.2, L455** | «la autocorrelación en el primer rezago supera la banda nula en **cinco de los ocho** municipios (Tabla 2)» | Sobre desarrollo, **sólo C** supera la banda en el rezago 1 del residuo; con **sólo el entrenamiento** ninguno la supera. Mantener «ningún municipio conserva autocorrelación en el rezago siete» (**0 de 8**, vale en ambos casos). Revisar la frase de L457 («quedaría esencialmente un término de primer orden»): ahora con evidencia **más débil**. |
| **2.3.5** | Local/global en abstracto | Se puede señalar que 4.1.3 ahora **responde** la pregunta con evidencia (C.5). No reescribir el marco (lo escribe el equipo). |
| **1.4, L347** (razón 1,71) | 1,71 | **Vigente** (1,71 también en desarrollo). |
| **1.1, L299** (1.645 días, 36.612, 224.694) | Descripción del conjunto | **Se mantiene** (decisión 2). |

### C.3 Capítulo 3 (metodología)

| Dónde | Hoy dice | Hay que |
| --- | --- | --- |
| **3.2.3, L503** y **4.1.2, L649** (corte de pandemia) | La evidencia compara con los mismos meses de 2022 a **2025** (incluía el test) | **Reemplazar** por la versión de desarrollo (C.4, fila «Exclusión del primer semestre»). La decisión **se sostiene**. |
| **3.3.1, L513** | «…**reconstruye el panel de forma independiente desde las fuentes crudas**… dos series individuales: Municipio C y Municipio A» | **Reescribir:** un único diagnóstico, `diagnostico_municipios`, sobre **los ocho municipios**, **sólo con el bloque de desarrollo**; el archivo crudo y los eventos se leen **descartando el test en el mismo paso**. **Quitar** lo de la reconstrucción independiente (decisión 4). Mantener el detalle del recorte (62.427 → 36.612) citando el ETL. |
| **3.4.3, Tabla 1** (L541–551) | Particiones 987 / 329 / 329 | **Sin cambio.** Agregar que la sección 7 del diagnóstico usa **dos pliegues** dentro del desarrollo (ajuste 658 y 987 días; validación 329). |
| **3.4.4, L575–577** y **Cuadro 3, filas 5 y 6** (L587–588) | Declaran el uso del bloque final en el E2 y que parte del diagnóstico «incluye este tramo» | **Mantener la declaración histórica.** Actualizar: (a) el diagnóstico **ya se recalculó sólo con desarrollo** (2026-10-05) y **reconfirma** la conclusión cualitativa; (b) lo decidido en el E2 se decidió con el diagnóstico **anterior** y eso **no se revierte**; (c) regla hacia adelante (test reservado, directriz sobre validación). Ver decisión 1. |
| **3.4.2** (variables) y donde se justifique la elección de rezagos con la ACF | Rezagos 7/14/21 elegidos con la ACF del período completo | Agregar: con la ACF **sólo del entrenamiento inicial** (`dm/12b_acf_rezagos_solo_entrenamiento.csv`), una vez descontado el calendario **ningún municipio** supera la banda (±0,0624) en los rezagos 1, 7, 14, 21 ni 28; los rezagos de la serie cruda son calendario. Los rezagos del árbol candidato **no tienen sustento adicional al calendario**. |
| **3.4.5, L596** (L1) | «el factor distinguía el día de la semana y el feriado (**14 medias**)» | En el diagnóstico nuevo el calendario es de **8 grupos** (7 días + feriado). Corregir la cuenta o aclarar que son versiones distintas. |
| **3.4.6, L615** | `geopandas 1.1.4` entre las bibliotecas | **Vuelve a ser correcto**: lo usa el mapa de 2.7. Sin cambio. |
| **3.4.1, L519** (calendario de tres niveles «22,3 % frente al 20,8 %») | Cifras del período completo | Reemplazar por `dm/11b_…`: **21,42 %** (tres niveles) frente a **19,94 %** (día de la semana), **y agregar** que 8 niveles explican **26,51 %** (decisión 6). |

### C.4 Capítulo 4.1 — Diagnóstico de los datos

#### 4.1.1 Calidad

| Párrafo (línea) | Reemplazo / acción |
| --- | --- |
| **Completitud** (L631), Tabla B1 | **Nuevo** `dm/05b_faltantes_codificados.csv`: en el archivo hasta 2025-02-05 (196.431 registros) el centinela afecta al **18,14 %** de `Localidad`, al **12,50 %** de `Calle` y al 0,01 % de `Tipo de Siniestro`; en el recorte de Montevideo (28.629 registros antes de deduplicar), **4,47 %** (1.281), **2,32 %** (663) y **0,03 %** (10). `Gravedad`, `Dia Semana` y `Departamento`: 0 %. Hay un nulo, en `Calle`. (Antes: 17,91 / 12,37 / 4,48 / 2,33.) |
| **Duplicados** (L633) | **Vigente**; cita: `experiments/etl_montevideo/tablas/01_duplicados.csv`. |
| **Consistencia interna** (L635) | **Vigente**; cita: `resumen_preparacion_montevideo.md` (sección «Fecha»). |
| **Precisión espacial** (L637) | **Reemplazar** por `dm/04_concentracion_geografica_eventos.csv` (por municipio, desarrollo): **83,17 % (A) a 95,31 % (B)** de los eventos en una coordenada repetida; 3,12 a 4,84 eventos por coordenada; ninguna coordenada concentra más de 2,04 % de su municipio. Los **11 hechos** fuera de polígono: ETL (`03c_asignacion_zonas.csv`). |
| **Validez temporal y atípicos** (L639), Tabla B2 | **Nuevo** `dm/05g_serie_departamental_desarrollo.csv`: mínimo 4, mediana 22,0, **máximo 43** (antes 44, que es del test); Tukey global: Q1 17, Q3 26, IQR 9, límites 3,5 y 39,5, **7** atípicos (todos por arriba); por grupo de calendario **16** (14 por arriba, 2 por debajo), **ninguno feriado**; 7 por ambos criterios, 9 sólo por grupo. Por municipio: `dm/05_atipicos_por_municipio.csv` (de 9 en E a 35 en G y CH; G y CH tienen 18 y 15 con ≤ 5 siniestros). |
| **Serie meteorológica** (L641) | `dm/05g`: temperatura media **4,9–31,7 °C**, precipitación **0–58,9 mm** (antes 105,3, que no está en el desarrollo). 1.316 días. |

#### 4.1.2 Cobertura

| Párrafo (línea) | Reemplazo / acción |
| --- | --- |
| **Cobertura temporal** (L645–647), Tabla B3, Ilustración B1 | **Nuevo** `dm/05f_cobertura_temporal_anual.csv` y `dm/fig8_cobertura_temporal.png`: 2021 (jul–dic) 3.936 / 21,39; 2022 7.665 / 21,00; 2023 7.873 / 21,57 (**+2,7 %**); 2024 8.398 / 22,95 (**+6,4 %**). **Quitar 2025** (8.740 / 23,95 / +4,4 %: test). Segundos semestres: 21,39 / 22,05 / 22,68 / 23,96 (`dm/05e`). |
| **Exclusión del primer semestre de 2021** (L649) | **Nuevo** (`dm/05c`–`05e2`): **nivel** 16,34 contra **20,78** en los mismos meses de 2022–2024: **−21,4 %** (antes 21,40 y −23,7 %); **forma**: feb **−9,6 %**, mar **−11,3 %**, abr **−15,5 %**, may **−9,9 %**, jun **−7,3 %** (antes «−7,0 % a −17,2 %»), **enero +0,9 %**; **suficiencia**: julio–diciembre +3,1 %, +2,8 %, +5,7 % de variación interanual; **costo**: 2.957 registros, 181 días, **9,39 %** del recorte hasta 2025-02-05 (antes «7,5 %»). Mantener las dos excepciones: enero de 2021 no está deprimido (+0,9 %, se excluye por conveniencia); **noviembre de 2021 se aparta +18,3 %** y los índices de julio–diciembre **están inflados por construcción** (la media del propio 2021 incluye el semestre deprimido): no leerlo como efecto real. |
| **Cobertura territorial** (L651), Tabla C1, Ilustración C1 | **Nuevo** `dm/03_resumen_por_municipio.csv` y `dm/fig9_mapa_municipios.png` (D.1). La razón 1,71 se mantiene. «Todos superan el 84 % de días con al menos un hecho» → **«todos superan el 83 %»** (CH: 83,51 %). |
| **El panel resultante** (L653) | Desarrollo (`dm/03b_objetivo_panel_desarrollo.csv`): **10.528 filas, 9,34 % de ceros, media 2,7104** (antes 13.160, 8,60 %, 2,7821). La comparación con la grilla (95,08 %) y los barrios (71,96 %) es de otro período: ver pregunta abierta 3. |
| **Variables exógenas** (L655) | `dm/05g`: **891 / 364 / 61** días (entre semana / fin de semana / feriado); medias departamentales **23,65 / 18,01 / 14,87**; viernes **25,22**, domingo **15,72**. (Antes 1.114 / 454 / 77; 24,33 / 18,31 / 15,64; 25,74 / 16,06.) |

#### 4.1.3 Adecuación al problema

| Párrafo / elemento | Reemplazo / acción |
| --- | --- |
| **La variable objetivo** (L659) | `dm/03b`: **media 2,7104; varianza 3,4415; dispersión 1,270; modo 2; 9,34 % ceros; 19,05 % uno; 71,61 % dos o más; máximo 13**. La conclusión (Poisson de referencia, binomial negativa como primera extensión) **se mantiene**. Agregar por municipio (`dm/03`): dispersión **1,069 (F) a 1,291 (C)**; ceros de 4,79 % a 16,49 %; exceso sobre Poisson de **+0,30 a +3,11** puntos: **no hay evidencia para modelos con inflación de ceros**. |
| **Señal temporal — Tabla 2** (L661–672) | **Reemplazar** (D.3, `dm/12_…`), banda **±0,0540**: crudo r1 mediana 0,0492 (**2 de 8**); crudo r7 0,0541 (**4 de 8**); **residuo r1 0,0437 (1 de 8: sólo C)**; **residuo r7 0,0118 (0 de 8)**. |
| **Lectura de la Tabla 2** (L672) | Reescribir: a rezago 7 la señal es **calendario** (0 de 8, igual que antes). A rezago 1 la persistencia es **mínima y no general**: sólo C supera la banda; **C y CH** rechazan Ljung-Box en los tres horizontes (en el desarrollo); en A, F, G y E no se distingue del ruido (menos del 0,3 % de la varianza). **Con sólo el entrenamiento** (`dm/12b`, `dm/25f`) ningún rezago individual supera la banda y Ljung-Box sólo rechaza en **CH**: **la memoria de C aparece al incluir la validación**. Quitar la comparación con «0,2 esperables». «Candidato a evaluar, no eje del modelo» **se mantiene**. |
| **Aporte de cada bloque — Tabla 3** (L674–690) | **Reemplazar** por D.3 (`dm/23`, `23b`, `24`, `25`): una sola medición fuera de muestra, **dos pliegues dentro del desarrollo**. **Cuidado con el signo:** el informe escribe «−7,5 %» para una *mejora* y «+10,4 %» para un *empeoramiento*; el notebook usa **«mejora» positiva**. Quitar la columna «dentro de muestra», la frase «esa segunda mitad contiene el período de prueba» y la deriva **+11,0 %** (ahora **+5,03 % / +8,83 %**, `dm/24`). |
| **Estructura temporal de C y A — Tabla D1** (L692–696) | **Reemplazar** (D.5). **Dos afirmaciones cambian:** (a) «KPSS rechaza la estacionariedad **en las dos**»: en desarrollo **no la rechaza en C** (p = 0,084); en los ocho la rechaza sólo en **A, F y G**; (b) Ljung-Box de A: **sobre el residuo, A no rechaza** (p = 0,20; 0,29; 0,53). |
| **«Lo que las distingue»** (L696) | Ampliar: **A es el único** con perfil semanal distinto (sábado 1,14; correlación 0,609 con el agregado; resto ≥ 0,953), **reproducible fuera de muestra y con sólo el entrenamiento** (sábado 1,111; correlación 0,769) (C.5, C.5b). Si se dice que A tiene la tendencia más empinada, agregar la salvedad: con sólo el entrenamiento no se aparta del agregado (C.5b). Ya no hay «dos series de ocho»: hay ocho. |
| **(nuevo) ¿Un solo modelo o varios?** | Agregar un apartado (C.5). |

#### 4.1.4 Limitaciones — Cuadro 5 (L702–712)

| Fila | Hay que |
| --- | --- |
| Deriva creciente del nivel | **+5,03 % / +8,83 %** entre ajuste y validación (`dm/24`). Cautela con una tendencia específica por municipio: en el desarrollo es de −0,07 a 7,34 %/año (detectable en C, A, F, G), pero con sólo el entrenamiento la diferencia entre municipios **no es concluyente** (p = 0,123; detectable sólo en B, F y G). Recalibración del nivel **por municipio**. |
| Ocho zonas de nivel parecido | Precisar: **sólo A** difiere en la forma semanal; el calendario común sirve para 7 de 8. |
| Persistencia de corto plazo pequeña | «Residuo sobre la banda sólo en **C** (desarrollo); con sólo el entrenamiento, en ninguno. Ljung-Box conjunto: **C y CH** en el desarrollo, **sólo CH** con el entrenamiento.» |
| Diagnóstico calculado sobre el período completo | **Actualizar:** recalculado el 2026-10-05 sólo con desarrollo; el diagnóstico **original** sí lo incluía; sigue sin revertir ese uso. |
| (nuevo) | Poder bajo (8 municipios, ~3,6 años); el test no se consultó, así que el diagnóstico **no sabe** si el último tramo se comporta distinto. Las secciones que orientan decisiones usan la validación (válido, decisión 7); un chequeo con sólo el entrenamiento (C.5b) muestra que dos conclusiones secundarias son sensibles a esa ventana. |

### C.5 Apartado nuevo: «¿Un solo modelo o varios?» (insertar en 4.1.3)

Todo con artefacto (`resumen_diagnostico_municipios.md` §7 y `dm/16`–`22`):

1. **Qué se mide.** Pruebas F de cuasi-verosimilitud (10.528 observaciones) y una comparación predictiva de **seis
   modelos mínimos** (nivel × calendario) en **dos pliegues cronológicos** dentro del desarrollo (ajuste 658 y 987
   días; validación 329), bootstrap por bloques semanales (2.000 remuestreos, semilla 20260910) y una **regla fijada
   antes de ejecutar**: «M3 mejora a M2 en ≥ 1 % y el IC95 excluye 0, en los dos pliegues».
2. **Resultados:**

| Pregunta | Resultado |
| --- | --- |
| ¿El nivel difiere entre municipios? | **Sí**: F = 134,47; reduce 7,545 % la desvianza. |
| ¿Cuánto vale conocer el nivel? | **+7,62 % y +7,86 %**. |
| ¿Un municipio sin datos propios cuesta algo? | **+9,81 % y +10,20 %** de desvianza. |
| ¿El perfil de calendario difiere? | Estadísticamente sí (F = 2,71; 1,139 %), **pero** especializarlo **no mejora en promedio**: **−0,22 % y +0,32 %** (ICs con 0). |
| ¿Quién se aparta del perfil agregado? | **A** (p de Holm 3·10⁻⁶; 2,92 %) y **C** (0,0008; 2,07 %); CH cerca (0,064). |
| ¿Quién necesita calendario propio (regla)? | **Sólo A** (+4,06 % y +4,24 %). C (−2,05 % / +1,22 %) y CH (+1,53 % / −0,56 %) **cambian de signo**; G **empeora** (−2,45 %). |
| ¿Tendencia, estacionalidad anual o lluvia distintas? | **No sostenible** (p = 0,033; 0,016; 0,35; reducciones ≤ 0,92 %). |
| ¿El nivel histórico alcanza? | Subestima en 7 de 8; **A el que más (0,842)**: recalibrar. |

3. **Inferencia del equipo** (rotularla así): **un solo modelo con variable de nivel por municipio** es la primera
   hipótesis a probar; los modelos separados **no están respaldados**, salvo quizá A (se resuelve primero con un
   término propio dentro del modelo común).
4. **Orden para el Entregable 3:** (1) modelo común con nivel por municipio, calculado **sólo con entrenamiento** y
   con recalibración; (2) término propio para A; (3) modelo separado para A sólo si lo anterior no alcanza.
5. **Límites:** modelo mínimo; 8 municipios y 2 pliegues; p-valores con supuesto de independencia; «municipio sin datos»
   hipotético; **causa de la diferencia de A no investigada**.

Esto **responde** el párrafo del informe que dice que el factor de calendario común «debe contrastarse en el panel»
(L696) y la verificación prevista en 4.3.3 (L782). Los rezagos por municipio se evaluaron sólo vía ACF/Ljung-Box.

### C.5b Estabilidad entre ventanas (sección 7.6): qué cambia si se excluye la validación — informativo

Fuente: `dm/25b`–`25f`. Las cifras de 4.1.3 y de C.5 son del **desarrollo** (entrenamiento + validación) y **son
válidas** (decisión 7). Para saber qué tan sensibles son a la ventana, las que orientan decisiones se repitieron con
los **987 días de entrenamiento** (2021-07-01 → 2024-03-13). **No es un reparo de leakage: es información de
estabilidad.** «No se sostiene» significa «aparece al incluir la validación»:

| Conclusión | Con sólo el entrenamiento | Estabilidad | Cómo citarla |
| --- | --- | --- | --- |
| El **nivel** difiere entre municipios | F = 98,31; 7,36 % (desarrollo: 134,47; 7,545 %) | **Estable** | Sin salvedad |
| El **perfil de calendario** difiere | F = 2,08; p = 1,6·10⁻⁵; 1,165 % | **Estable** | Sin salvedad |
| **A** tiene el sábado alto | sábado 1,111 (desarrollo 1,143); correlación 0,769 (0,609); siguiente: G 1,003 | **Estable**, algo atenuada | «único con el sábado sobre la media» vale **sólo en el desarrollo**; con el entrenamiento, G queda en ≈ 1 |
| Calendario propio de A mejora la predicción | pliegue A (validación **dentro** del entrenamiento): **+4,06 %**, IC excluye 0 | **Estable** | Sin salvedad |
| **No diferenciar ni transformar** | λ de Box-Cox 0,25–0,50 (igual); r1 con d = 1 de −0,46 a −0,54; ADF rechaza en 8; KPSS rechaza sólo en F | **Estable** | Sin salvedad |
| La **lluvia** no cambia por municipio | p = 0,33 | **Estable** | Sin salvedad |
| **Tendencia distinta por municipio** | p = 0,123; 0,131 % (desarrollo: 0,033; 0,132 %) | **No concluyente** | No afirmarla |
| **A tiene la pendiente mayor** | A 3,89 %/año [−1,12; 9,16], p = 0,13; agregado 2,61 %/año (desarrollo: 7,34 contra 3,72) | **Sensible a la ventana** | Citable con la mención «aparece al incluir la validación» |
| Tendencia **detectable** en C, A, F, G | con el entrenamiento: sólo **B (5,23), F (6,07), G (6,20)** | **Cambia** | Citar ambas versiones o ninguna |
| **C** tiene memoria de corto plazo | Ljung-Box con el entrenamiento: C no rechaza (0,069; 0,147; 0,364) | **Sensible a la ventana** | Citable con la mención «en el desarrollo» |
| **CH** tiene memoria de corto plazo | rechaza también con el entrenamiento (0,0006; 0,0008; 0,009) | **Estable** | Sin salvedad (por Ljung-Box; ningún rezago individual supera la banda) |
| Estacionalidad anual distinta | p = 0,033; 1,17 % | **No concluyente** (igual que antes) | No afirmarla |

**Efecto sobre el texto del informe:** la conclusión central («un modelo único con nivel por municipio; A la excepción de
calendario») **no cambia**. Como el desarrollo es válido, **no es obligatorio suavizar nada**; **se recomienda** mencionar
la sensibilidad en cuatro frases: A con la tendencia más empinada, tendencia detectable en C y A, memoria de C, y el
«5 de 8 → 1 de 8» de la Tabla 2 cuando se lo presente como evidencia de memoria. Lo que antes decía «no afirmar» pasa a
«citar con la salvedad».

### C.6 Capítulos 4.2 y 4.3

| Dónde | Hay que |
| --- | --- |
| **4.2, L720–722** | **Sin cambio** (descripción del conjunto y 16 verificaciones). |
| **4.2, L724** | **Eliminar** (decisión 4): «La evidencia más sólida… reconstrucción independiente… (Tabla E1) y… geopandas». Reescribir apoyando la corrección del conjunto en las **16 verificaciones internas** y su reejecución (L722). |
| **4.3 (Tablas 4 y 5, L726–772)** | **Sin cambio**: `linea_base` no se tocó. |
| **4.3.3, L780** | «+11,0 % entre mitades» → **+5,03 % / +8,83 %**; y por municipio **no es igual**. |
| **4.3.3, L782** (plan del E3) | Reemplazar la verificación prevista por el orden de C.5 (punto 4). Pendiente real: los **rezagos** (con sólo entrenamiento no tienen sustento adicional al calendario). |

### C.7 Anexos

| Anexo | Dónde | Hay que |
| --- | --- | --- |
| **A** | Tabla A2 | **Cifras vigentes** (construcción del conjunto); cambiar la **fuente** a `experiments/etl_montevideo/tablas/` (`01_duplicados`, `02_recorte`, `03c_asignacion_zonas`). |
| **A** | Nota (L841) | **Eliminar** (ese procedimiento ya no existe en `main`). |
| **B** | Tabla B1 | **Reemplazar** por `dm/05b` (C.4, 4.1.1). Columnas: «archivo hasta 2025-02-05» y «recorte de Montevideo». |
| **B** | Tabla B2 | **Reemplazar** por `dm/05g` (serie departamental, desarrollo) y/o `dm/05_…` (por municipio). |
| **B** | Tabla B3 + Ilustración B1 | **Reemplazar** por `dm/05f` y `dm/fig8_cobertura_temporal.png`. |
| **B** | Párrafo final (L888) | «calcularlos sobre el período completo no introduce fuga» → **ya no es el criterio**: «el criterio se aplica sólo sobre el desarrollo». |
| **C** | Tabla C1 + Ilustración C1 | **Reemplazar** por D.1 y `dm/fig9_mapa_municipios.png`. |
| **C** | Tabla C2 + nota | **Conservar como antecedente histórico** con la nota de la decisión 8; fila de municipios con los valores originales del período completo. |
| **D** | Tabla D1 + Ilustración D1 | **Reemplazar** por D.5 (ocho municipios) y `dm/fig4_…`. Banda analítica (decisión 3): cambiar la frase final. |
| **E** | Cuadro E1, «Transformación del objetivo» | **Vigente** y ahora cubre los ocho (λ de Box-Cox de 0,25 a 0,50). |
| **E** | Cuadro E2, «calendario en tres niveles» | 22,3 % / 20,8 % → **21,42 % / 19,94 %** (`dm/11b`), **más la salvedad de los 26,51 %** (decisión 6). |
| **E** | Cuadro E2, «Conservar el nulo…» (L979) | «en los **tres** procedimientos» → hoy sólo queda el **ETL**. |
| **E** | **Tabla E1** y su nota | **Eliminar** (decisión 4). |
| **F** | L999 («los seis notebooks vigentes») | **Histórica y correcta**; agregar «tres se retiraron después y se reemplazaron por `diagnostico_municipios`». |
| **F** | F.1 | **Sin cambio.** |

### C.8 Ventana deslizante en lugar de expansiva (decisión 9)

**Dónde dice hoy otra cosa** (líneas del `.md` actual):

| Dónde | Hoy dice | Hay que |
| --- | --- | --- |
| **L321** (objetivo específico) | «…(con y sin variables exógenas, **ventana expansiva y ventana deslizante**)» | Quitar la comparación: «…con y sin variables exógenas, con **ventana deslizante**». |
| **L289** (glosario «Ventana expansiva») | Define la expansiva por oposición a la deslizante | Agregar **«Ventana deslizante»** (longitud fija que se desplaza) como definición propia; la expansiva puede quedar como antecedente. |
| **L548** (Tabla 1) | «Validación por origen móvil (**ventana expansiva**)» | Cambiar a «(ventana deslizante)» **cuando se reejecute** (ver estado). |
| **L553** (3.4.3, «Validación interna») | «origen móvil con ventana expansiva… el primer entrenamiento abarca los 987 días iniciales… se repite con todo lo observado antes de él» | Reescribir: ventana de **longitud fija** que se desplaza siete días por corte; **declarar el largo** y que se fijó **con la validación, no con el test**; y la fundamentación. |
| **L736** (Tabla 4) y **L755** (Tabla 5) | Resultados de la versión expansiva | **Se mantienen sólo si `linea_base` no se reejecuta.** Si se reejecuta con ventana deslizante, **cambian las cifras** de ambas tablas y de sus lecturas (4.3.1, 4.3.2, 4.3.3) y del `referencia_no_regresion.csv`. |
| **L431** (2.2.5) y el marco | Describe la validación temporal | Revisar que no suponga expansiva. |

**Estado en el repo:** `notebooks/linea_base.ipynb` y `documentacion/resumen_linea_base.md` siguen con **ventana expansiva**
(el notebook la llama así en sus secciones 3, 5 y 6; `experiments/linea_base/tablas/03_particiones.csv`). **No se
cambiaron en esta sesión**: es un cambio de protocolo que modifica resultados ya citados. **Falta decidir** si se
implementa ahora o en el Entregable 3, y con **qué largo de ventana** (ver advertencia).

**Advertencia sobre la fundamentación (para el equipo, antes de escribirla):** la sobredispersión leve (índice de
dispersión 1,07–1,29) describe **cuánto varía el conteo respecto de su media en un día**; no implica que los días lejanos
sean menos representativos. El argumento que **sí respalda** la ventana deslizante es la **deriva del nivel**: la media
por municipio sube +5,03 % y +8,83 % entre ajuste y validación (`dm/24`), el nivel histórico subestima en 7 de 8
municipios (`dm/22`: razones de 0,84 a 1,09) y el árbol, que no extrapola, fue el peor modelo en el bloque final. Una
ventana corta sigue el nivel; una expansiva lo promedia con el pasado lejano. **Sugerencia de redacción (a validar por
el equipo):** «Se adopta una ventana deslizante porque el nivel de la serie deriva (Sección 4.1.3, Cuadro 5): promediar
todo el pasado arrastra información de un nivel que ya no rige. Contra: una ventana corta tiene menos observaciones y
más varianza de estimación, en conteos de media baja.» **No** dar a la sobredispersión como causa. Además, el largo de
la ventana es un **hiperparámetro**: debe fijarse con la validación (no con el bloque final) y declararse; una opción sin
elección arbitraria es usar el tamaño del entrenamiento inicial (**987 días**), de modo que el primer corte coincide con
el actual.

---

## D. Cifras de reemplazo (todas sobre desarrollo, con artefacto)

### D.1 Cobertura territorial (Tabla C1) — `dm/03_resumen_por_municipio.csv`

| Municipio | Siniestros | % del total | % días con ≥ 1 siniestro | Media diaria |
| --- | --- | --- | --- | --- |
| C | 4.508 | 15,80 | 94,68 | 3,4255 |
| B | 4.218 | 14,78 | 94,53 | 3,2052 |
| D | 4.141 | 14,51 | 95,21 | 3,1467 |
| A | 3.879 | 13,59 | 93,39 | 2,9476 |
| F | 3.472 | 12,17 | 92,55 | 2,6383 |
| G | 2.905 | 10,18 | 86,63 | 2,2074 |
| E | 2.780 | 9,74 | 84,80 | 2,1125 |
| CH | 2.632 | 9,22 | 83,51 | 2,0000 |
| **Total** | **28.535** | 100 | — | 2,7104 |

(«% días con ≥ 1» = 100 − «% días en cero».) Razón máx/mín: **1,71**.

### D.2 Variable objetivo del panel de desarrollo — `dm/03b_objetivo_panel_desarrollo.csv`

10.528 filas, 28.535 siniestros, **9,34 %** de ceros, media **2,7104**, varianza 3,4415, dispersión **1,270**, máximo 13,
modo 2, 19,05 % de filas con 1 siniestro, 71,61 % con 2 o más.

### D.3 Tablas 2 y 3 nuevas

**Tabla 2** — `dm/12_acf_y_ljung_box_por_municipio.csv`, banda analítica ±0,0540:

| Rezago | Cruda (mediana) | Sobre la banda | Residuo (mediana) | Sobre la banda | Banda |
| --- | --- | --- | --- | --- | --- |
| 1 | 0,0492 | 2 de 8 | 0,0437 | **1 de 8 (C)** | 0,0540 |
| 7 | 0,0541 | 4 de 8 | 0,0118 | **0 de 8** | 0,0540 |

Con **sólo el entrenamiento** (`dm/12b`, banda ±0,0624): residuo r1, r7, r14, r21 y r28 **no superan la banda en
ningún municipio** (máximo |r| = 0,0611, CH en el rezago 7).

**Tabla 3** — `dm/23_aporte_bloques_fuera_de_muestra.csv`, `23b_…`, `24_…`, `25_…`. Mejora = reducción de la desvianza
media de los 8 frente a la constante.

| Predictor (estimado sólo con el ajuste) | Pliegue A (ajuste 658) | Pliegue B (ajuste 987) |
| --- | --- | --- |
| Constante global | 1,3897 | 1,4014 |
| Sólo calendario | 1,3291 (**+4,36 %**) | 1,3441 (**+4,09 %**) |
| Sólo tasa del municipio | 1,2885 (**+7,28 %**) | 1,2958 (**+7,54 %**) |
| **Tasa × calendario** | **1,2278 (+11,65 %)** | **1,2385 (+11,63 %)** |
| Tasa × calendario × lluvia | 1,2323 (+11,33 %) | 1,2386 (+11,61 %) |
| Celdas municipio × calendario | 1,2305 (+11,45 %) | 1,2344 (+11,91 %) |
| Celdas saturadas con el mes | 1,4958 (**−7,64 %**, peor que la constante) | 1,4477 (**−3,31 %**, peor) |

B2 → B3 **+4,71 % / +4,42 %**; B3 → B4 (lluvia) **−0,36 % / −0,01 %** (no aporta); B3 → B6 **−21,83 % / −16,90 %**. Deriva:
**+5,03 % / +8,83 %**. Varianza: 7,71 % entre municipios, 18,04 % entre días (≈ 11,54 % es azar de Poisson). La lluvia se
midió sólo como indicador binario `llovió`. **No son comparables con la Tabla 3 anterior.**

### D.4 Serie departamental, calendario y clima — `dm/05g_serie_departamental_desarrollo.csv`

| Cifra | Desarrollo | Hoy en el informe |
| --- | --- | --- |
| Mínimo / mediana / máximo diario | 4 / 22,0 / **43** | 4 / 22,0 / **44** |
| Tukey global: Q1, Q3, IQR; límites; atípicos | 17, 26, 9; 3,5 y 39,5; **7** | 18, 27, 9; 4,5 y 40,5; 8 |
| Tukey por grupo | **16** (14 arriba, 2 abajo), 0 feriados | 9 |
| Días entre semana / fin de semana / feriado | **891 / 364 / 61** | 1.114 / 454 / 77 |
| Media departamental por tipo de día | **23,65 / 18,01 / 14,87** | 24,33 / 18,31 / 15,64 |
| Viernes / domingo | **25,22 / 15,72** | 25,74 / 16,06 |
| Precipitación máxima | **58,9 mm** | 105,3 mm |

### D.5 Tabla D1 nueva (ocho municipios) — `dm/12_…`, `13_…`, `09_…`, `03_…`

| Mun. | Media / dispersión | Vie ÷ dom | ACF cruda r1 / r7 / r14 | ACF residuo r1 | Ljung-Box residuo p (7 / 14 / 28) | ADF p | KPSS p | r1 con d = 1 | λ Box-Cox |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| C | 3,4255 / 1,291 | 2,19 | 0,0557 / 0,0765 / 0,1636 | 0,0554 | 0,0045 / 0,0066 / 0,0412 | 7,6·10⁻⁹ | 0,084 | −0,464 | 0,448 |
| B | 3,2052 / 1,157 | 1,58 | 0,0117 / 0,0384 / 0,0158 | −0,0127 | 0,0189 / 0,0776 / 0,403 | 3,5·10⁻²⁰ | 0,10 | −0,513 | 0,497 |
| D | 3,1467 / 1,153 | 1,45 | 0,0459 / 0,0064 / 0,0277 | 0,0453 | 0,335 / 0,0258 / 0,0152 | ≈ 0 | 0,10 | −0,486 | 0,409 |
| A | 2,9476 / 1,134 | 1,43 | 0,0362 / 0,0309 / 0,0441 | 0,0421 | 0,201 / 0,285 / 0,525 | ≈ 0 | 0,01 | −0,493 | 0,461 |
| F | 2,6383 / 1,069 | 1,44 | 0,0526 / 0,0698 / 0,0415 | 0,0517 | 0,151 / 0,496 / 0,0623 | ≈ 0 | 0,01 | −0,477 | 0,420 |
| G | 2,2074 / 1,080 | 1,41 | −0,0214 / 0,0322 / 0,0164 | −0,0175 | 0,0516 / 0,358 / 0,526 | ≈ 0 | 0,01 | −0,549 | 0,419 |
| E | 2,1125 / 1,267 | 1,88 | 0,0531 / 0,0933 / 0,0687 | 0,0367 | 0,129 / 0,0606 / 0,113 | 1,0·10⁻¹⁸ | 0,10 | −0,470 | 0,251 |
| CH | 2,0000 / 1,214 | 1,79 | 0,0661 / 0,0798 / 0,0532 | 0,0468 | 0,0015 / 0,0052 / 0,0169 | 1,3·10⁻¹⁷ | 0,10 | −0,484 | 0,257 |

**Diferencias de método con la Tabla D1 actual** (no mezclar): (a) Ljung-Box sobre el **residuo de calendario** y a 7,
14 y 28 rezagos (antes sobre la serie cruda y a 7, 14 y 30); (b) sólo p-valores de ADF y KPSS (KPSS acotado a
[0,01; 0,10]); (c) razón viernes ÷ domingo en lugar de las medias absolutas (el perfil normalizado está en `dm/08`);
(d) banda analítica.

---

## E. Lo que NO cambia (para no reescribir de más)

- **Tablas 1, 4 y 5, Cuadros 2 y 4, 4.3.1 y 4.3.2** y las lecturas de 4.3: `linea_base` no se tocó.
- Lo que el informe **declara sobre el uso del bloque final en el E2** (3.4.4, Cuadro 3): se mantiene (decisión 1).
- **Anexo F** y la **Tabla F1**; **Anexo A, Tabla A1** y las cifras de la **Tabla A2** (construcción del conjunto).
- **Capítulo 2** (marco), **1.2, 1.3** y las limitaciones de 1.4 salvo lo indicado; **3.5**.
- La razón **1,71**, la **tendencia creciente** del agregado (21,39 → 22,95 siniestros/día de 2021 a 2024), la conclusión de
  **no diferenciar ni transformar el objetivo** y de usar la familia Poisson (se **refuerza**).
- `geopandas` en la lista de bibliotecas (L615): vuelve a ser correcto.

---

## F. Pendientes que siguen abiertos

0. **Ventana deslizante (decisión 9):** decidir si se reejecuta `linea_base` ahora (cambian las Tablas 4 y 5 y sus lecturas) o en el
   Entregable 3, y el largo de la ventana. Mientras tanto el informe describe la versión expansiva que produjo sus tablas.
1. **Recomendaciones no confirmadas** (decisión 6): agregar al informe la salvedad de los 26,51 % y comparar calendario de 3 contra 8 niveles sobre la **validación** en el Entregable 3.
2. **Rezagos del árbol candidato:** con sólo el entrenamiento no tienen sustento más allá del calendario (`dm/12b`). El
   modelado del E3 debe decidir si los mantiene; la justificación del informe debe reflejarlo.
3. **Causa de la diferencia de A** (sábado alto) y de sus mínimos de 2021 (A y D): **no investigadas**; el
   informe debe decir «no se investigó».
4. **Commit** de todo lo de esta sesión (hoy sin confirmar) y **revisión por el equipo** de las lecturas del notebook y del
   resumen, **que redactó Claude**.
5. **Entregable 3:** ejecutar el orden de C.5 con el **modelo final**; el test queda reservado hasta la evaluación final.

*Resuelto en esta ronda (ya no es pendiente):* evidencia del corte de la pandemia, faltantes codificados (Tabla B1),
cobertura temporal (Tabla B3, Ilustración B1), mapa (Ilustración C1), cifras departamentales (D.2, D.4) y calendario
22,3 %/20,8 %: todos tienen artefacto sólo-desarrollo. Verificación cruzada con el ETL: **eliminada** por decisión del equipo.

---

## G. Equivalencia de artefactos (retirado → vigente)

| En el informe / notebook retirado | Reemplazo en `main` |
| --- | --- |
| Diagnóstico de datos §3.1 completitud (`04_completitud`) | `dm/05b_faltantes_codificados.csv` |
| §3.2 duplicados (`05_duplicados`) | `experiments/etl_montevideo/tablas/01_duplicados.csv` |
| §3.3 fecha, §3.4 coordenadas | `resumen_preparacion_montevideo.md` §3.3–3.4 |
| §3.4 precisión espacial (`07_precision_espacial`) | `dm/04_concentracion_geografica_eventos.csv` |
| §3.6 asignación (`09_calidad_capa_municipios`) | `experiments/etl_montevideo/tablas/03c_asignacion_zonas.csv` |
| §3.7 clima (`10_calidad_clima`) | `experiments/etl_montevideo/tablas/07_clima.csv`; rango en `dm/05g` |
| §3.8 atípicos (`10c`–`10g`) | `dm/05_atipicos_por_municipio.csv`, `dm/05g_…` |
| §4.1 cobertura temporal y corte de la pandemia (`12`–`12e`, `13`) | `dm/05c`–`05e2`, `05f`, `fig8` |
| §4.2 cobertura territorial (`13_cobertura_municipios`) y mapa | `dm/03`, `05h`, `fig9` |
| §5.1 objetivo (`17`, `18`) | `dm/03b`, `dm/03` |
| §5.2 señal temporal (`19`, `20`) | `dm/12`, `dm/12b` |
| §5.3 aporte por bloque (`21`–`21d`) | `dm/23`, `23b`, `24`, `25` |
| Notebooks de C y A | `dm/05`–`13` (los ocho municipios) |
| Calendario 22,3 % / 20,8 % (ETL `06_calendario`) | `dm/11b_varianza_explicada_por_calendario.csv` |
| §7 verificación cruzada (`23_coherencia_etl`) | **Eliminada** (decisión 4) |
| (no existía) | `dm/16`–`22`: homogeneidad y comparación predictiva (C.5) |
