# Cambios para el informe

**Para quién es este documento.** Para quien actualice `documentacion/informe/Entregable2_PAA_20-09-26.md` (versión
vigente del 2026-10-05). Contiene **sólo lo que hay que cambiar en el informe**, con la cifra o el texto de reemplazo y el
artefacto del repositorio que lo respalda. Todo lo que figura acá **ya está implementado** en el repositorio.

**Cómo leerlo.** `dm/` = `experiments/diagnostico_municipios/tablas/` (y `dm/fig…` = `experiments/diagnostico_municipios/figuras/`);
generadas por `notebooks/diagnostico_municipios.ipynb`, con resumen en `documentacion/resumen_diagnostico_municipios.md`.
Las referencias `L<n>` son **números de línea del `.md` actual** y cambian si se edita. «Desarrollo» = 2021-07-01 →
2025-02-05 (1.316 días: entrenamiento inicial + validación). **Todo lo del diagnóstico nuevo está calculado sólo con el
desarrollo: el test (2025-02-06 → 2025-12-31) no se consulta.** El notebook lee los archivos y descarta el test en ese mismo
paso.

## Decisiones implementadas que originan los cambios

| # | Decisión | Qué implica para el informe |
| --- | --- | --- |
| 1 | **El test es el mismo bloque final.** Como el Entregable 2 ya pasó, su uso se **declara** en el documento. | Se mantiene lo que el informe declara (3.4.4, Cuadro 3, 4.3.2, 4.3.3, glosario). Se agrega que **los diagnósticos posteriores al 2026-10-05 no lo consultan** y que se reserva para la evaluación final. |
| 2 | Cifras de **descripción del conjunto** (36.612 siniestros, 13.160 filas, 1.645 días, 224.694 registros, recorte paso a paso) **se mantienen**; las **estadísticas del diagnóstico** pasan a ser **de desarrollo**. | Ver A.4 y D. |
| 3 | **Banda nula analítica** (±1,96/√n), la del notebook. | Glosario y Tabla 2. Con n = 1.316: **±0,0540**. |
| 4 | **Se quita la verificación cruzada con el ETL.** | Se elimina la Tabla E1 y las frases que la citan. |
| 5 | **Se rehízo con el desarrollo** lo que sólo existía en los notebooks retirados (pandemia, faltantes, cobertura temporal, mapa…). | Cada cifra tiene artefacto en `dm/`. |
| 6 | **No se toca el ETL** (calendario `tipo_dia` de 3 niveles). | La preparación del informe queda como está; sólo cambian las cifras de varianza explicada (A.3, Cuadro E2). |
| 7 | **La ventana de validación puede usarse en los diagnósticos** (confirmado con el docente). | Los diagnósticos con el desarrollo completo son válidos: el informe dice **«desarrollo»** y los cita. |
| 8 | **La Tabla C2 se conserva como antecedente histórico.** | Ver A.7. |
| 9 | **La comparación de ventana expansiva y deslizante se hará más adelante, con los modelos candidatos finales** (es un objetivo del proyecto). | **El informe mantiene su objetivo (L321)**; las Tablas 4 y 5 siguen siendo de ventana expansiva. Sólo hay que dejar constancia en el plan del E3 (A.6). |

---

## A. Cambios por sección

### A.1 Listas y glosario

| Dónde | Hay que |
| --- | --- |
| Lista de tablas (L205–229) | Actualizar títulos; **quitar la Tabla E1**. |
| Lista de ilustraciones (L195–199) | B1 → `dm/fig8_cobertura_temporal.png`; C1 → `dm/fig9_mapa_municipios.png`; D1 → `dm/fig4_acf_residuo_por_municipio.png`. |
| Glosario **Banda nula** (L243) | «obtenido… por simulación» → «banda analítica ±1,96/√n». |
| Glosario **Bloque final** (L245) | Se mantiene («fue consultado durante el E2»). Agregar: «los diagnósticos posteriores al 2026-10-05 no lo consultan; se reserva para la evaluación final». |
| Glosario | Agregar **«Desarrollo»** (2021-07-01 → 2025-02-05, 1.316 días: entrenamiento inicial + validación) y, si se citan, **«Prueba F de cuasi-verosimilitud»**. |

### A.2 Capítulos 1 y 2

| Dónde | Hoy dice | Hay que |
| --- | --- | --- |
| **2.3.2, L455** | «la autocorrelación en el primer rezago supera la banda nula en **cinco de los ocho** municipios (Tabla 2)» | **Sólo C** supera la banda en el rezago 1 del residuo (`dm/12`). Mantener «ningún municipio conserva autocorrelación en el rezago siete» (0 de 8). Revisar L457 («quedaría esencialmente un término de primer orden»): la evidencia es más débil. |
| **2.3.5** | Local/global en abstracto | Señalar que 4.1.3 ahora **responde** la pregunta con evidencia (A.5). No reescribir el marco (lo escribe el equipo). |

### A.3 Capítulo 3 (metodología)

| Dónde | Hoy dice | Hay que |
| --- | --- | --- |
| **3.2.3, L503** y **4.1.2, L649** (corte de pandemia) | Compara con los mismos meses de 2022 a **2025** (incluía el test) | Reemplazar por la versión de desarrollo (A.4, «Exclusión del primer semestre»). La decisión se sostiene. |
| **3.3.1, L513** | «…**reconstruye el panel de forma independiente desde las fuentes crudas**… dos series individuales: Municipio C y A» | **Reescribir:** un único diagnóstico sobre **los ocho municipios**, **sólo con el desarrollo**; el archivo crudo y los eventos se leen descartando el test. **Quitar** la reconstrucción independiente. Mantener el recorte (62.427 → 36.612) citando el ETL. |
| **3.4.1, L519** («calendario en tres niveles… 22,3 % frente al 20,8 %») | Cifras del período completo | **21,42 %** (tres niveles) frente a **19,94 %** (día de la semana) — `dm/11b_varianza_explicada_por_calendario.csv`. |
| **3.4.2** y donde se justifique la elección de rezagos con la ACF | Rezagos 7/14/21 elegidos con la ACF del período completo | Declarar que esa ACF incluía el test y agregar la ACF recalculada: en el desarrollo (`dm/12`, banda ±0,0540) el residuo de calendario sólo supera la banda en el rezago 1 de C; con sólo el entrenamiento (`dm/12b`, banda ±0,0624) **ningún municipio** supera la banda en los rezagos 1, 7, 14, 21 ni 28. Los rezagos de la serie cruda son calendario. |
| **3.4.3, Tabla 1** (L541–551) | Particiones 987 / 329 / 329 | Sin cambio. Agregar que la sección 7 del diagnóstico usa **dos pliegues** dentro del desarrollo (ajuste 658 y 987 días; validación 329). |
| **3.4.4, L575–577** y **Cuadro 3, filas 5 y 6** (L587–588) | Declaran el uso del bloque final en el E2 y que parte del diagnóstico «incluye este tramo» | **Mantener la declaración histórica.** Actualizar: (a) el diagnóstico **se recalculó sólo con desarrollo** (2026-10-05); (b) lo decidido en el E2 se decidió con el diagnóstico **anterior** y eso no se revierte; (c) desde ahora ningún diagnóstico consulta el test. Reemplazar «queda pendiente de acordar» (L577) por la decisión: el test es el bloque final. |
| **3.4.5, L596** (L1) | «el factor distinguía el día de la semana y el feriado (**14 medias**)» | En el diagnóstico nuevo el calendario es de **8 grupos** (7 días + feriado). Corregir la cuenta o aclarar que son versiones distintas. |

### A.4 Capítulo 4.1 — Diagnóstico de los datos

#### 4.1.1 Calidad

| Párrafo (línea) | Reemplazo |
| --- | --- |
| **Completitud** (L631), Tabla B1 | `dm/05b_faltantes_codificados.csv`: en el archivo hasta 2025-02-05 (196.431 registros) el centinela afecta al **18,14 %** de `Localidad`, al **12,50 %** de `Calle` y al 0,01 % de `Tipo de Siniestro`; en el recorte de Montevideo (28.629 registros antes de deduplicar), **4,47 %** (1.281), **2,32 %** (663) y **0,03 %** (10). `Gravedad`, `Dia Semana` y `Departamento`: 0 %. Un nulo, en `Calle`. (Antes: 17,91 / 12,37 / 4,48 / 2,33.) |
| **Duplicados** (L633) | Cifras vigentes; citar `experiments/etl_montevideo/tablas/01_duplicados.csv`. |
| **Consistencia interna** (L635) | Cifras vigentes; citar `resumen_preparacion_montevideo.md` (sección «Fecha»). |
| **Precisión espacial** (L637) | `dm/04_concentracion_geografica_eventos.csv` (por municipio): **83,17 % (A) a 95,31 % (B)** de los eventos en una coordenada repetida; 3,12 a 4,84 eventos por coordenada; ninguna coordenada concentra más de 2,04 % de su municipio. Los **11 hechos** fuera de polígono: ETL (`03c_asignacion_zonas.csv`). |
| **Validez temporal y atípicos** (L639), Tabla B2 | `dm/05g_serie_departamental_desarrollo.csv`: mínimo 4, mediana 22,0, **máximo 43** (antes 44, que es del test); Tukey global: Q1 17, Q3 26, IQR 9, límites 3,5 y 39,5, **7** atípicos (todos por arriba); por grupo de calendario **16** (14 por arriba, 2 por debajo), **ninguno feriado**; 7 por ambos criterios, 9 sólo por grupo. Por municipio: `dm/05_atipicos_por_municipio.csv` (de 9 en E a 35 en G y CH; G y CH tienen 18 y 15 con ≤ 5 siniestros). |
| **Serie meteorológica** (L641) | `dm/05g`: temperatura media **4,9–31,7 °C**, precipitación **0–58,9 mm** (antes 105,3, que no está en el desarrollo); 1.316 días. |

#### 4.1.2 Cobertura

| Párrafo (línea) | Reemplazo |
| --- | --- |
| **Cobertura temporal** (L645–647), Tabla B3, Ilustración B1 | `dm/05f_cobertura_temporal_anual.csv` y `dm/fig8_cobertura_temporal.png`: 2021 (jul–dic) 3.936 / 21,39; 2022 7.665 / 21,00; 2023 7.873 / 21,57 (**+2,7 %**); 2024 8.398 / 22,95 (**+6,4 %**). **Quitar 2025** (8.740 / 23,95 / +4,4 %: test). Segundos semestres: 21,39 / 22,05 / 22,68 / 23,96 (`dm/05e`). |
| **Exclusión del primer semestre de 2021** (L649) | `dm/05c`–`05e2`: **nivel** 16,34 contra **20,78** en los mismos meses de 2022–2024: **−21,4 %** (antes 21,40 y −23,7 %); **forma**: feb **−9,6 %**, mar **−11,3 %**, abr **−15,5 %**, may **−9,9 %**, jun **−7,3 %** (antes «−7,0 % a −17,2 %»), **enero +0,9 %**; **suficiencia**: julio–diciembre +3,1 %, +2,8 %, +5,7 % de variación interanual; **costo**: 2.957 registros, 181 días, **9,39 %** del recorte hasta 2025-02-05 (antes «7,5 %»). Mantener las dos excepciones: enero de 2021 no está deprimido (+0,9 %; se excluye por conveniencia) y **noviembre de 2021 se aparta +18,3 %**; los índices de julio–diciembre **están inflados por construcción** (la media del propio 2021 incluye el semestre deprimido): no leerlo como efecto real. |
| **Cobertura territorial** (L651), Tabla C1, Ilustración C1 | `dm/03_resumen_por_municipio.csv` y `dm/fig9_mapa_municipios.png` (B.1). La razón 1,71 se mantiene. «Todos superan el 84 % de días con al menos un hecho» → **«todos superan el 83 %»** (CH: 83,51 %). |
| **El panel resultante** (L653) | Desarrollo (`dm/03b_objetivo_panel_desarrollo.csv`): **10.528 filas, 9,34 % de ceros, media 2,7104** (antes 13.160, 8,60 %, 2,7821). La comparación con la grilla (95,08 %) y los barrios (71,96 %) es de otro período: ver Tabla C2 (A.7). |
| **Variables exógenas** (L655) | `dm/05g`: **891 / 364 / 61** días (entre semana / fin de semana / feriado); medias departamentales **23,65 / 18,01 / 14,87**; viernes **25,22**, domingo **15,72**. (Antes 1.114 / 454 / 77; 24,33 / 18,31 / 15,64; 25,74 / 16,06.) |

#### 4.1.3 Adecuación al problema

| Párrafo / elemento | Reemplazo |
| --- | --- |
| **La variable objetivo** (L659) | `dm/03b`: **media 2,7104; varianza 3,4415; dispersión 1,270; modo 2; 9,34 % ceros; 19,05 % uno; 71,61 % dos o más; máximo 13**. La conclusión (Poisson de referencia, binomial negativa como primera extensión) se mantiene. Agregar por municipio (`dm/03`): dispersión **1,069 (F) a 1,291 (C)**; ceros de 4,79 % a 16,49 %; exceso sobre Poisson de **+0,30 a +3,11** puntos: **no hay evidencia para modelos con inflación de ceros**. |
| **Señal temporal — Tabla 2** (L661–672) | Reemplazar por B.3 (`dm/12`), banda **±0,0540**: crudo r1 mediana 0,0492 (**2 de 8**); crudo r7 0,0541 (**4 de 8**); **residuo r1 0,0437 (1 de 8: sólo C)**; **residuo r7 0,0118 (0 de 8)**. |
| **Lectura de la Tabla 2** (L672) | Reescribir: a rezago 7 la señal es **calendario** (0 de 8, igual que antes). A rezago 1 la persistencia es **mínima y no general**: sólo C supera la banda; **C y CH** rechazan Ljung-Box en los tres horizontes; en A, F, G y E no se distingue del ruido (menos del 0,3 % de la varianza). Quitar la comparación con «0,2 esperables» (era de la banda simulada). «Candidato a evaluar, no eje del modelo» se mantiene. |
| **Aporte de cada bloque — Tabla 3** (L674–690) | Reemplazar por B.3 (`dm/23`, `23b`, `24`, `25`): una sola medición fuera de muestra, **dos pliegues dentro del desarrollo**. **Cuidado con el signo:** el informe escribe «−7,5 %» para una *mejora* y «+10,4 %» para un *empeoramiento*; el notebook usa **«mejora» positiva**. Quitar la columna «dentro de muestra», la frase «esa segunda mitad contiene el período de prueba» y la deriva **+11,0 %** (ahora **+5,03 % / +8,83 %**, `dm/24`). |
| **Estructura temporal de C y A — Tabla D1** (L692–696) | Reemplazar por B.5. **Dos afirmaciones cambian:** (a) «KPSS rechaza la estacionariedad **en las dos**»: en el desarrollo **no la rechaza en C** (p = 0,084); en los ocho la rechaza sólo en **A, F y G**; (b) Ljung-Box de A: **sobre el residuo, A no rechaza** (p = 0,20; 0,29; 0,53). |
| **«Lo que las distingue»** (L696) | Ampliar: **A es el único** con perfil semanal distinto (sábado 1,14; correlación 0,609 con el agregado; resto ≥ 0,953), reproducible fuera de muestra (A.5). Ya no hay «dos series de ocho»: hay ocho. |
| **(nuevo) ¿Un solo modelo o varios?** | Agregar el apartado de A.5. |

#### 4.1.4 Limitaciones — Cuadro 5 (L702–712)

| Fila | Hay que |
| --- | --- |
| Deriva creciente del nivel | **+5,03 % / +8,83 %** entre ajuste y validación (`dm/24`); la tendencia por municipio va de **−0,07 a 7,34 %/año** (agregado 3,72), detectable en C, A, F y G (`dm/07`). Recalibración del nivel **por municipio**. |
| Ocho zonas de nivel parecido | Precisar: **sólo A** difiere en la forma semanal; el calendario común sirve para 7 de 8. |
| Persistencia de corto plazo pequeña | «Residuo sobre la banda sólo en **C**; Ljung-Box rechaza en **C y CH**.» |
| Diagnóstico calculado sobre el período completo | **Actualizar:** recalculado el 2026-10-05 sólo con desarrollo; el diagnóstico **original** sí lo incluía; sigue sin revertir ese uso. |
| (nueva) | Poder bajo (8 municipios, ~3,6 años); el test no se consultó, así que el diagnóstico **no sabe** si el último tramo se comporta distinto. |

### A.5 Apartado nuevo «¿Un solo modelo o varios?» (insertar en 4.1.3)

Todo con artefacto (`resumen_diagnostico_municipios.md` §7 y `dm/16`–`22`):

1. **Qué se mide.** Pruebas F de cuasi-verosimilitud (10.528 observaciones) y una comparación predictiva de **seis modelos
   mínimos** (nivel × calendario) en **dos pliegues cronológicos** dentro del desarrollo (ajuste 658 y 987 días; validación
   329), bootstrap por bloques semanales (2.000 remuestreos, semilla 20260910) y una **regla fijada antes de ejecutar**:
   «M3 mejora a M2 en ≥ 1 % y el IC95 excluye 0, en los dos pliegues».
2. **Resultados:**

| Pregunta | Resultado |
| --- | --- |
| ¿El nivel difiere entre municipios? | **Sí**: F = 134,47; reduce 7,545 % la desvianza. |
| ¿Cuánto vale conocer el nivel? | **+7,62 % y +7,86 %**. |
| ¿Un municipio sin datos propios cuesta algo? | **+9,81 % y +10,20 %** de desvianza. |
| ¿El perfil de calendario difiere? | Estadísticamente sí (F = 2,71; 1,139 %), **pero** especializarlo **no mejora en promedio**: **−0,22 % y +0,32 %** (ICs con 0). |
| ¿Quién se aparta del perfil agregado? | **A** (p de Holm 3·10⁻⁶; 2,92 %) y **C** (0,0008; 2,07 %); CH cerca (0,064). |
| ¿Quién necesita calendario propio (regla)? | **Sólo A** (+4,06 % y +4,24 %). C (−2,05 % / +1,22 %) y CH (+1,53 % / −0,56 %) **cambian de signo**; G **empeora** (−2,45 %). |
| ¿Tendencia, estacionalidad anual o lluvia distintas? | **No concluyente** (p = 0,033; 0,016; 0,35; reducciones ≤ 0,92 %). |
| ¿El nivel histórico alcanza? | Subestima en 7 de 8; **A el que más (0,842)**: recalibrar. |

3. **Inferencia del equipo** (rotularla así): **un solo modelo con variable de nivel por municipio** es la primera hipótesis a
   probar; los modelos separados **no están respaldados**, salvo quizá A (se resuelve primero con un término propio dentro
   del modelo común).
4. **Orden para el Entregable 3:** (1) modelo común con nivel por municipio, calculado **sólo con entrenamiento** y con
   recalibración; (2) término propio para A; (3) modelo separado para A sólo si lo anterior no alcanza.
5. **Límites:** modelo mínimo; 8 municipios y 2 pliegues; p-valores con supuesto de independencia; «municipio sin datos»
   hipotético; **la causa de la diferencia de A no se investigó** (decir «no se investigó»).

Esto responde el párrafo del informe que dice que el factor de calendario común «debe contrastarse en el panel» (L696) y la
verificación prevista en 4.3.3 (L782).

### A.6 Capítulos 4.2 y 4.3

| Dónde | Hay que |
| --- | --- |
| **4.2, L724** | **Eliminar** («La evidencia más sólida… reconstrucción independiente… (Tabla E1) y… geopandas»). Reescribir apoyando la corrección del conjunto en las **16 verificaciones internas** y su reejecución (L722). |
| **4.3.3, L780** | «+11,0 % entre mitades» → **+5,03 % / +8,83 %** (`dm/24`); y por municipio no es igual. |
| **4.3.3, L782** (plan del E3) | Reemplazar la verificación prevista por el orden de A.5, punto 4. **Agregar a la lista del E3** la **comparación de ventana expansiva y ventana deslizante con los modelos candidatos finales** (objetivo de L321): las Tablas 4 y 5 son de ventana expansiva y siguen siéndolo. |

Sin cambio: 4.2 L720–722; Tablas 4 y 5 y sus lecturas (4.3.1, 4.3.2); L321, L289, L548 y L553 (ventana expansiva).

### A.7 Anexos

| Anexo | Dónde | Hay que |
| --- | --- | --- |
| **A** | Tabla A2 | Cifras vigentes (construcción del conjunto); cambiar la **fuente** a `experiments/etl_montevideo/tablas/` (`01_duplicados`, `02_recorte`, `03c_asignacion_zonas`). |
| **A** | Nota (L841) | **Eliminar** (ese procedimiento ya no existe en `main`). |
| **B** | Tabla B1 | Reemplazar por `dm/05b` (columnas «archivo hasta 2025-02-05» y «recorte de Montevideo»). |
| **B** | Tabla B2 | Reemplazar por `dm/05g` (serie departamental) y/o `dm/05_atipicos_por_municipio.csv`. |
| **B** | Tabla B3 + Ilustración B1 | Reemplazar por `dm/05f` y `dm/fig8_cobertura_temporal.png`. |
| **B** | Párrafo final (L888) | «calcularlos sobre el período completo no introduce fuga» → «el criterio se aplica sólo sobre el desarrollo». |
| **C** | Tabla C1 + Ilustración C1 | Reemplazar por B.1 y `dm/fig9_mapa_municipios.png`. |
| **C** | Tabla C2 + nota (L913–923) | **Conservar como antecedente histórico, sin recalcular.** Nota explícita: *«versiones previas del ETL; período completo 2021–2025 (incluye el bloque final); no reproducible en `main`; antecedente exploratorio de la decisión de partición territorial»*. La fila de municipios **queda con sus valores originales del período completo** (13.160 filas, 8,60 %, 2,7821, 1,259, 13) para que las tres filas sigan comparables; no mezclarla con las cifras de desarrollo del resto del informe (10.528 filas, 9,34 %…). |
| **D** | Tabla D1 + Ilustración D1 | Reemplazar por B.5 (ocho municipios) y `dm/fig4_acf_residuo_por_municipio.png`. Cambiar la frase final («banda nula… simulación de 400 series») por la banda analítica. |
| **E** | Cuadro E1, «Transformación del objetivo» | Vigente y ahora cubre los ocho (λ de Box-Cox de 0,25 a 0,50). |
| **E** | Cuadro E2, «calendario en tres niveles» | 22,3 % / 20,8 % → **21,42 % / 19,94 %** (`dm/11b`). |
| **E** | Cuadro E2, «Conservar el nulo…» (L979) | «en los **tres** procedimientos» → hoy sólo queda el **ETL**. |
| **E** | **Tabla E1** y su nota (L983+) | **Eliminar.** |
| **F** | L999 («los seis notebooks vigentes») | Es histórica y correcta; agregar «tres se retiraron después y se reemplazaron por `diagnostico_municipios`». |

---

## B. Cifras de reemplazo (sobre el desarrollo, con artefacto)

### B.1 Cobertura territorial (Tabla C1) — `dm/03_resumen_por_municipio.csv`

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

### B.2 Variable objetivo del panel de desarrollo — `dm/03b_objetivo_panel_desarrollo.csv`

10.528 filas, 28.535 siniestros, **9,34 %** de ceros, media **2,7104**, varianza 3,4415, dispersión **1,270**, máximo 13, modo 2,
19,05 % de filas con 1 siniestro, 71,61 % con 2 o más.

### B.3 Tablas 2 y 3 nuevas

**Tabla 2** — `dm/12_acf_y_ljung_box_por_municipio.csv`, banda analítica ±0,0540:

| Rezago | Cruda (mediana) | Sobre la banda | Residuo (mediana) | Sobre la banda | Banda |
| --- | --- | --- | --- | --- | --- |
| 1 | 0,0492 | 2 de 8 | 0,0437 | **1 de 8 (C)** | 0,0540 |
| 7 | 0,0541 | 4 de 8 | 0,0118 | **0 de 8** | 0,0540 |

**Tabla 3** — `dm/23_aporte_bloques_fuera_de_muestra.csv`, `23b_…`, `24_…`, `25_…`. Mejora = reducción de la desvianza media de
los 8 frente a la constante.

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
**+5,03 % / +8,83 %**. Varianza: 7,71 % entre municipios, 18,04 % entre días (≈ 11,54 % es azar de Poisson). La lluvia se midió
sólo como indicador binario `llovió`. **No son comparables con la Tabla 3 anterior.**

### B.4 Serie departamental, calendario y clima — `dm/05g_serie_departamental_desarrollo.csv`

| Cifra | Desarrollo | Hoy en el informe |
| --- | --- | --- |
| Mínimo / mediana / máximo diario | 4 / 22,0 / **43** | 4 / 22,0 / **44** |
| Tukey global: Q1, Q3, IQR; límites; atípicos | 17, 26, 9; 3,5 y 39,5; **7** | 18, 27, 9; 4,5 y 40,5; 8 |
| Tukey por grupo | **16** (14 arriba, 2 abajo), 0 feriados | 9 |
| Días entre semana / fin de semana / feriado | **891 / 364 / 61** | 1.114 / 454 / 77 |
| Media departamental por tipo de día | **23,65 / 18,01 / 14,87** | 24,33 / 18,31 / 15,64 |
| Viernes / domingo | **25,22 / 15,72** | 25,74 / 16,06 |
| Precipitación máxima | **58,9 mm** | 105,3 mm |

### B.5 Tabla D1 nueva (ocho municipios) — `dm/12_…`, `13_…`, `09_…`, `03_…`

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

**Diferencias de método con la Tabla D1 actual** (no mezclar): (a) Ljung-Box sobre el **residuo de calendario** y a 7, 14 y 28
rezagos (antes sobre la serie cruda y a 7, 14 y 30); (b) sólo p-valores de ADF y KPSS (KPSS acotado a [0,01; 0,10]); (c) razón
viernes ÷ domingo en lugar de las medias absolutas (el perfil normalizado está en `dm/08`); (d) banda analítica.

---

## C. Equivalencia de artefactos (para cambiar las citas)

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
| §5.2 señal temporal (`19`, `20`) | `dm/12` |
| §5.3 aporte por bloque (`21`–`21d`) | `dm/23`, `23b`, `24`, `25` |
| Notebooks de C y A | `dm/05`–`13` (los ocho municipios) |
| Calendario 22,3 % / 20,8 % (ETL `06_calendario`) | `dm/11b_varianza_explicada_por_calendario.csv` |
| §7 verificación cruzada (`23_coherencia_etl`) | **Eliminada** (decisión 4) |
| (no existía) | `dm/16`–`22`: homogeneidad y comparación predictiva (A.5) |
