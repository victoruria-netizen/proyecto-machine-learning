# Pruebas del pipeline de inferencia del prototipo (Entregable 3, fase 5, paso 5c)

**Archivos de prueba:** `tests/test_pipeline_inferencia.py` (24 pruebas recogidas por pytest, algunas parametrizadas) y
`tests/test_app.py` (6). Las dos son nuevas en esta fase.
**Código que prueban:** `app/pagina_prediccion.py` (pestaña «Predicción (PAA)»), que llama a `src/modelo.py`.
**Fecha:** 2026-10-21. **Ejecución:** `pytest` en el `.venv` (Python 3.13.2) y, aparte, en un clon limpio con entorno nuevo (Python 3.13.9).

> **Nota de rótulo (D77, 25/10/2026).** El modo que este documento llama «Próxima semana» (y que las pruebas del 21/10 ejercitaron con ese
> nombre) se llama ahora **«Semana posterior al corte»**: es un entorno simulado con corte al 31/12/2025, no la semana actual. Los
> **nombres internos se mantienen**: `predecir_proxima_semana`, `test_proxima_semana_*` y `test_render_proxima_semana`. Las constantes de la
> interfaz son `MODO_POSTERIOR` y `MODO_HISTORICO`. Donde abajo dice «Próxima semana», léase ese modo.

## 1. Cómo usar este documento

Es el registro que exige la guía para el prototipo: cada prueba, su resultado, los errores encontrados y cómo se corrigieron.
Reglas: ninguna cifra sin la corrida que la respalda (los comandos están en §2); distinguir lo que las pruebas
muestran de lo que no cubren (§5); no escribir Introducción ni Marco teórico a partir de este documento.

## 2. Resultados de las corridas

| Corrida | Comando | Resultado |
| --- | --- | --- |
| Repositorio de trabajo (con `data/processed/`) | `pytest` (en el `.venv`) | **76 pasadas**, 0 fallidas, 0 saltadas |
| Solo las pruebas nuevas | `pytest tests/test_pipeline_inferencia.py tests/test_app.py` | **30 pasadas** |
| Clon limpio (sin `data/`, entorno nuevo con `pip install -r requirements.txt -c requirements-lock.txt`) | `pytest -rs` | **66 pasadas, 10 saltadas**; las 10 saltadas son de `test_modelo.py`, `test_train_modelo_final.py` y `test_variables.py` y necesitan el panel; **ninguna prueba nueva se salta** |
| Clon limpio | `streamlit run app/app.py --server.headless true` | arranca; `/_stcore/health` responde 200 |
| Versiones del servidor (D70): entorno aparte con streamlit 1.57.0, plotly 5.22.0, pydeck 0.9.1 (Python 3.13.9, pandas 2.3.3, numpy 2.5.4) | `pytest tests/test_pipeline_inferencia.py tests/test_app.py` en el clon | **30 pasadas** |

Antes de esta fase, la suite tenía 46 pasadas (`HANDOFF.md`, fix de R3). 46 + 30 = 76.

## 3. Qué se probó

### 3.1 `tests/test_pipeline_inferencia.py` (lógica, sin interfaz)

| Grupo | Pruebas | Qué verifican |
| --- | --- | --- |
| Validación de entradas | `test_validar_semana_*` (4 casos de rango + 3 de tipo), `test_semana_historica_fuera_de_rango_falla`, `test_historico_sin_columnas_falla` | Los 47 orígenes del bloque final (el primero, 2025-02-06) se aceptan; 2026-01-01, 2025-02-05, 2025-02-07 y 2024-12-31 dan un mensaje de «fuera del bloque final»; un texto, `None` o `NaT` dan error de entrada; un CSV sin la columna `observado` lo informa |
| Carga del modelo y de archivos | `test_modelo_ausente_*`, `test_predicciones_ausentes_*`, `test_modelo_ilegible_*`, `test_modelo_real_carga` | Falta el modelo o el CSV: mensaje claro (`ErrorEntrada`), no traza; un JSON roto o un modelo que no es GLM dan «no se pudo leer»; el modelo real carga (GLM, origen 2026-01-01, 15 columnas) |
| Flujo «Próxima semana» | `test_proxima_semana_es_8_por_7_*`, `test_proxima_semana_igual_a_la_del_servidor`, `test_proxima_semana_igual_a_predecir_semana_directo`, `test_modelo_no_predice_otra_semana` | 56 filas, 8 municipios, 7 fechas (2026-01-01 a 2026-01-07), sin nulos ni negativos, intervalos ordenados (`inf_95 ≤ inf_80 ≤ sup_80 ≤ sup_95`); las 56 μ coinciden con el CSV del job 136 del servidor con diferencia relativa ≤ 1e-6 (la misma comparación de F4-B5 en `tests/test_modelo.py::test_modelo_exportado_reproduce_la_prediccion_del_servidor`); igual a llamar a `mod.predecir_semana` directamente; el modelo rechaza otra semana |
| Modo «Histórico» | `test_historico_tiene_47_semanas_completas`, `test_semana_historica_coincide_fila_a_fila_con_el_csv`, `test_resumen_por_municipio_suma_los_dias` | 47 × 56 = 2.632 filas de la solución; **en cada una de las 47 semanas**, fecha, municipio, predicho, observado y los cuatro límites de los intervalos son idénticos (igualdad exacta) a las filas del CSV leído por separado con pandas |
| Mapa | `test_datos_del_mapa_*` | La capa trae los 8 municipios con polígono y color RGBA; un municipio ajeno a la predicción da error |
| Sin bases de datos (D67) | `test_la_pestana_no_importa_bases_de_datos_ni_config` | En un proceso aparte, importar la pestaña no carga `psycopg2`, `pymongo`, `sqlalchemy` ni `config` |

### 3.2 `tests/test_app.py` (interfaz, con `streamlit.testing.v1.AppTest`)

| Prueba | Qué verifica |
| --- | --- |
| `test_render_proxima_semana` | `render()` sin excepciones ni `st.error`; tabla resumen de 8 filas y detalle de 56; fechas 01/01/2026 a 07/01/2026; el texto de «qué se predice» está |
| `test_render_historico_y_cambio_de_semana` | Modo Histórico sin excepciones; 47 semanas en el selector; cambiar de semana y de municipio no falla |
| `test_historico_mostrado_coincide_con_el_csv` | La tabla que ve el usuario en una semana (la 21.ª del selector) coincide fila a fila con el CSV: municipios, esperado redondeado a 2 decimales y observado |
| `test_falta_el_archivo_de_predicciones_*` y `test_falta_el_archivo_del_modelo_*` | Con el archivo ausente, la interfaz muestra un único `st.error` con el mensaje claro y ninguna excepción |
| `test_app_completa_tiene_la_pestana_nueva_y_funciona` | En `app/app.py`, «Predicción (PAA)» está en la barra de navegación; al elegirla, y al pasar a «Histórico», no hay excepciones ni errores |

**Barra de navegación heredada y AppTest.** La barra es `st.radio` nativo (`ui.render_navbar`), no un componente personalizado,
así que AppTest la maneja (`at.radio(key="nav")`) y no hizo falta aislar `render()` para probar la integración. De todos modos
las pruebas de `render()` se hacen de forma aislada (`AppTest.from_string` con un script mínimo que solo llama a `render()`),
para que no dependan de las páginas heredadas. En `test_app_completa_*`, la página inicial heredada («Resumen») intenta conectarse
a PostgreSQL y muestra su error de conexión: es lo esperado (D67), y la prueba solo mira lo que ocurre después de elegir la pestaña nueva.

## 4. Errores encontrados y cómo se corrigieron

| # | Qué pasó | Cómo se detectó | Corrección |
| --- | --- | --- | --- |
| 1 | El mensaje de «archivo ausente» fallaba con `ValueError` si la ruta estaba fuera del repositorio (`Path.relative_to`), en vez de mostrar el mensaje | `test_modelo_ausente_da_error_claro` y `test_predicciones_ausentes_dan_error_claro` | `_exigir_archivo` muestra la ruta relativa al repositorio y, si no se puede, la ruta completa |
| 2 | **La capa simplificada de municipios tenía el Municipio CH como `MultiPolygon`** (un polígono más un fragmento de 5 vértices, efecto de redondear a 5 decimales al escribir) y `datos_mapa` tomaba `coordinates[0]`, que en un `MultiPolygon` no es un contorno: el mapa de ese municipio habría salido mal. El commit del paso 5b (`935de76`) trae esa capa y ese código | `test_datos_del_mapa_traen_los_8_municipios` (largo mínimo del contorno) | Capa regenerada: `simplify`, luego `shapely.set_precision(…, 1e-5)`, luego el polígono de mayor área; ahora los 8 son `Polygon`. `datos_mapa` además admite `MultiPolygon` (un registro por contorno exterior). Procedencia actualizada en `app/ORIGEN.md`. El cociente de áreas (en grados², aproximado) entre la capa nueva y la original queda entre 0,999 y 1,004 |
| 3 | Las pruebas de «archivo ausente» dejaban modificado el módulo compartido (cambiaban `__defaults__` de la función de carga) y `test_app_completa_*` fallaba después con «No se encontró el archivo del modelo» | `pytest` completo: una falla en `test_app.py` que no aparecía al correrla sola | Error de las pruebas, no del producto: el script de prueba restaura los valores y vacía las cachés en un `try/finally` |

## 5. Lo que estas pruebas no cubren

- **No hay verificación visual.** AppTest ejecuta el script y expone los elementos, pero no dibuja el mapa pydeck ni los gráficos plotly:
  las pruebas comprueban los datos que llegan a la capa (`datos_mapa`), no cómo se ve el mapa. Eso lo revisa el equipo a mano (D63).
- **Versiones.** Las 30 pruebas nuevas pasan tanto con las del lock (streamlit 1.65.0, plotly 7.1.0, pydeck 0.9.3) como con las del servidor según D70
  (streamlit 1.57.0, plotly 5.22.0, pydeck 0.9.1; fila 4 de §2). La diferencia con el servidor real: esa corrida usó Python 3.13.9 y no el que tenga el servidor.
  Con 1.65.0 aparece el aviso de que `use_container_width` está deprecado (aceptado por el equipo); con 1.57.0 se filtraron los `DeprecationWarning`.
- **Las páginas heredadas no se prueban** (D67): consultan bases de datos que este repositorio no incluye.
- **Los valores del modelo no se recalculan:** «Histórico» se compara con el CSV por igualdad; «Próxima semana», con el CSV del servidor (tolerancia 1e-6).
  Que las predicciones del CSV histórico provienen del reentrenamiento semanal, y no del modelo exportado, está declarado en `documentacion/resumen_evaluacion_final.md`.

## 6. Ampliación del 25/10/2026 (fase 5b: rótulo, mejoras de la pestaña y tema)

Las secciones 1 a 5 describen el estado del 21/10. Esta sección agrega las pruebas de la fase 5b (D77, D79, D80) sin reescribir aquello.
Cambios de la pestaña que se prueban: rótulo «Semana posterior al corte», métricas descriptivas y comparación con la referencia L1 en
«Histórico», etiquetas del mapa, ficha «Sobre el modelo» y tema claro fijado en `.streamlit/config.toml`.

### 6.1 Resultados de las corridas

| Corrida | Comando | Resultado |
| --- | --- | --- |
| Repositorio de trabajo (`.venv`, Python 3.13.2, streamlit 1.65.0, plotly 7.1.0, pydeck 0.9.3) | `pytest` | **102 pasadas**, 0 fallidas, 0 saltadas |
| Solo los dos archivos de la pestaña, mismo `.venv` | `pytest tests/test_pipeline_inferencia.py tests/test_app.py` | **56 pasadas** (44 + 12) |
| Entorno aparte con las versiones de streamlit, plotly y pydeck de D70 (no reproduce el entorno del servidor), creado con `uv`, con las dependencias de `requirements-lock.txt` salvo streamlit 1.57.0, plotly 5.22.0 y pydeck 0.9.1 (Python 3.13.2, pandas 2.3.3, numpy 2.5.2) | `pytest tests/test_pipeline_inferencia.py tests/test_app.py` | **56 pasadas** |

Cuentas: 76 pruebas al 21/10, más 1 del rótulo (paso 1), 24 de este paso y 1 del pie de la tabla (corrección de texto del 25/10) = 102. De las 24, 20 están en `test_pipeline_inferencia.py` y 4 en `test_app.py`.
**Qué es y qué no es la corrida del entorno aparte.**
- **No es el entorno del servidor.** Es Python 3.13.2, y el del servidor es otro: Python 3.11 en el dashboard del servidor (inferido de los binarios `cpython-311` de `librerias/`, sin verificación directa) y Python 3.10.12 en el contenedor de `submit_cpu` (log del job 136). Solo coinciden las versiones de streamlit (1.57.0), plotly (5.22.0) y pydeck (0.9.1). Las demás librerías son las del lock del repositorio.
- **No es un clon limpio** como el del 21/10: usa el mismo árbol de trabajo (con `data/processed/`). No se corrió la suite completa ni se levantó `streamlit run` en ese entorno.
- **Qué muestra.** AppTest ejecuta el script de la pestaña, pero no dibuja nada en un navegador. Lo que queda verificado es que, con plotly 5.22.0, pydeck 0.9.1 y streamlit 1.57.0, las figuras y las capas se construyen sin error (incluido `add_vrect`, las barras de error y las capas `PolygonLayer` y `TextLayer` de pydeck) y que la pestaña corre sin excepciones. **No** queda verificado que streamlit 1.57.0 las muestre, ni cómo se ven.

### 6.2 Pruebas nuevas

`tests/test_pipeline_inferencia.py` (lógica, sin interfaz):

| Prueba | Qué verifica | Contra qué |
| --- | --- | --- |
| `test_desvianza_global_coincide_con_la_tabla_06` | La desvianza de Poisson global que calcula la app es 1,106342 (solución) y 1,135861 (L1), con diferencia < 6e-7; la solución tiene menor desvianza que L1 en 33 de 47 semanas | `tablas/06_globales.csv`, columnas `desvianza` y `cortes_que_gana_a_su_referencia` |
| `test_desvianza_de_cada_semana_coincide_con_la_tabla_08` (2 casos: solución y L1) | En los 47 cortes, la desvianza semanal coincide con `desvianza_poisson` con diferencia < 6e-7 (la máxima observada al diseñar la prueba fue de 4,9e-7 para la solución y 5,2e-7 para L1; el redondeo a 6 decimales de la tabla explica la diferencia) | `tablas/08_por_corte.csv`, unido por `origen` |
| `test_desvianza_reemplaza_predicciones_no_positivas_por_1e_6` | Con predicción 0 o negativa, la desvianza usa 1e-6 | Cálculo a mano |
| `test_filas_fuera_del_intervalo_coinciden_con_la_tabla_17` (80 % y 95 %) | Las filas fuera del intervalo en las 2.632 de la solución son (debajo + encima) × n de la fila «todos» del intervalo NB2; el test lo calcula de la tabla (da 262 para el 80 % y 55 para el 95 %) | `tablas/17_cobertura_intervalos.csv` |
| `test_totales_semanales_traen_47_semanas_y_l1` | 47 semanas, columnas Observado / Solución / L1 (sin L1, solo las dos primeras) | CSV de predicciones |
| `test_ficha_del_modelo_con_los_archivos_reales_coincide` | Con los archivos reales el sha256 coincide; ventana 364, reentrenamiento cada 7 días, 15 variables, entrenamiento 2025-01-02 a 2025-12-31 con 2.912 filas | `models/metadata.json`, `models/modelo_final.json` |
| `test_ficha_del_modelo_con_metadata_alterado_no_coincide` | Con un `metadata.json` alterado en `tmp_path`, «no coincide» | Copia modificada |
| `test_ficha_del_modelo_con_modelo_alterado_no_coincide` | Un byte agregado al modelo en `tmp_path` también da «no coincide» | Copia modificada |
| `test_ficha_del_modelo_con_archivo_ausente_da_error_claro` | Falta la ficha o falta el modelo: `ErrorEntrada` con mensaje claro | `tmp_path` |
| `test_ficha_del_modelo_con_metadata_ilegible_da_error_claro` | Un `metadata.json` al que le faltan campos da `ErrorEntrada` | `tmp_path` |
| `test_etiquetas_del_mapa_son_8_y_caen_dentro_de_la_capa` | 8 etiquetas; cada posición está dentro de los límites de la capa y, además, dentro de un contorno de su propio municipio (conteo de cruces) | `app/assets/municipios_montevideo_simplificado.geojson` |
| `test_etiquetas_del_mapa_son_letra_y_valor_en_dos_lineas_con_coma_decimal` | Texto `CH\n12,3` (letra, salto de línea, valor con coma decimal) | Valor sintético 12,34 |
| `test_etiquetas_del_mapa_rechazan_municipio_ajeno` | Un municipio que no está en la predicción da `ErrorEntrada` | Capa sintética |
| `test_centroide_usa_el_area_con_signo_y_el_contorno_mas_grande` | Centroide y área con signo de un cuadrado (también en sentido horario); en un `MultiPolygon` se elige el contorno de mayor área | Figuras sintéticas |
| `test_sin_l1_en_el_csv_da_error_claro` | Un CSV sin filas de L1 da `ErrorEntrada` en `cargar_referencia`, y `cargar_historico` sigue funcionando | CSV sin L1 en `tmp_path` |
| `test_referencia_real_es_l1_con_47_semanas`, `test_referencia_ausente_da_error_claro` | La referencia real son 2.632 filas de L1; con el CSV ausente, mensaje claro | CSV real / `tmp_path` |
| `test_f5_n4_el_codigo_de_la_pestana_no_habla_de_riesgo_ni_de_donde_ocurrira` | El código de `pagina_prediccion.py`, en minúsculas, no contiene «riesgo», «peligros» ni «dónde ocurrirá» | Texto del archivo |

`tests/test_app.py` (interfaz):

| Prueba | Qué verifica |
| --- | --- |
| `test_historico_muestra_4_metricas_y_los_elementos_nuevos` | «Histórico» sin excepciones, errores ni warnings; 4 métricas con las etiquetas esperadas; delta «frente a L1»; subtítulo «Las 47 semanas del bloque final»; caption con 1,1063, 1,1359 y «33 de 47»; columna «Fuera del 80 %» en la tabla; «Sobre el modelo» al final |
| `test_historico_sin_l1_muestra_un_warning_y_no_una_excepcion` | Con un CSV sin L1, un único `st.warning` («referencia L1», «sin las comparaciones»), sin errores ni excepciones; las 4 métricas siguen, la desvianza sin delta, y la tabla por día de 56 filas |
| `test_pie_de_la_tabla_no_presenta_la_cobertura_como_exacta` | El pie de la tabla por municipio y día dice «cuantiles de colas iguales (10 % y 90 % para el 80 %; 2,5 % y 97,5 % para el 95 %)» y «cubran algo más que el nivel nominal», y ya no habla de «la misma probabilidad en ambas colas» (en `tablas/17`, NB2 al 80 %: 3,2 % debajo, 6,8 % encima, cobertura esperada por el modelo 0,887) |
| `test_semana_posterior_no_tiene_metricas_y_cierra_con_sobre_el_modelo` | El modo «Semana posterior al corte» no muestra métricas (no hay observados) y termina con «Sobre el modelo» |
| `test_tema_claro_fijado_en_streamlit_config` | `.streamlit/config.toml` existe y tiene `theme.base = "light"` (D80) |

### 6.3 Errores hallados y correcciones

| # | Qué pasó | Cómo se detectó | Corrección |
| --- | --- | --- | --- |
| 4 | Al agregar las etiquetas de dos líneas (D80, punto 2) quedó un salto de línea real dentro de un f-string de `etiquetas_mapa`: `SyntaxError` al importar la pestaña | La colección de pytest falló al correr los tests de `test_pipeline_inferencia.py` | Error de edición mío, no de diseño: se escribió el `\n` como secuencia de escape; `test_etiquetas_del_mapa_son_letra_y_valor_en_dos_lineas_con_coma_decimal` fija el texto exacto |
| 5 | **La tabla 17 trae dos filas «todos» por nivel**, una del intervalo NB2 y otra del Poisson; tomar la primera que coincide con el nivel habría comparado contra el intervalo equivocado (el Poisson da otras proporciones) | Al leer la tabla antes de escribir la prueba | La prueba filtra por el tipo de intervalo que trae el propio CSV de predicciones (`tipo_intervalo`, NB2) y exige exactamente una fila |
| — | Las pruebas nuevas no encontraron defectos en el código de la pestaña: pasaron en la primera corrida completa | — | — |

Además, el intérprete global del equipo (streamlit 1.58.0) no importa por un conflicto con `starlette`; no se usó. Las corridas de §6.1 salen del `.venv` y del entorno aparte.

### 6.4 Lo que esta ampliación no cubre

- **Siguen sin verificarse visualmente** el dibujo del mapa (etiquetas con fondo y salto de línea en `TextLayer`), las leyendas, las barras de error del intervalo y la franja de la semana elegida: AppTest comprueba qué elementos se generan, no cómo se ven. Lo revisa el equipo con capturas.
- **El parámetro `background` de `TextLayer`** (y `get_background_color`) no lo interpreta pydeck sino deck.gl, en el navegador: pydeck 0.9.1 lo acepta al construir la capa, pero no se verificó que la versión de deck.gl que trae lo dibuje. Tampoco se verificó el salto de línea dentro del texto de la etiqueta.
- **El tema claro se prueba como archivo, no como render:** la prueba verifica que `.streamlit/config.toml` existe con `base = "light"`; el problema de legibilidad lo reprodujo el equipo en Chromium con `prefers-color-scheme: dark`, y que el tema claro lo resuelva no lo comprueba ninguna prueba automática. Además Streamlit solo lo toma si se lanza desde la raíz del repositorio.
- **Las métricas son descriptivas:** que la solución tenga menor desvianza que L1 en 33 de 47 semanas es una descripción del bloque final, que no es una prueba independiente (D63); no decide nada.

## 7. Ampliación del 26/10/2026 (fase 8a: despliegue en el dashboard del servidor, D81 a D83)

Las secciones 1 a 6 describen el estado del 21/10 y del 25/10. Esta sección agrega las pruebas del despliegue (`sys.path` de la pestaña y puente
para el servidor) y dos corridas: una con las versiones del servidor y otra con la suite completa del repositorio. El procedimiento de despliegue
está en `documentacion/despliegue_servidor.md`.

### 7.1 Pruebas nuevas: `tests/test_servidor.py` (13 pruebas)

| Prueba | Qué verifica |
| --- | --- |
| `test_importar_la_pagina_no_cambia_los_primeros_elementos_de_sys_path` | En un intérprete aparte, con un `sys.path` conocido que no tiene `app/` ni la raíz del repositorio, importar `app/pagina_prediccion.py` no cambia ningún elemento previo y agrega esas dos carpetas **al final**, en ese orden (paso 1). Se comprobó que la prueba falla si el código vuelve a `sys.path.insert(0, …)` |
| `test_el_puente_carga_la_pagina_del_clon_y_expone_render` | Con un clon falso en `tmp_path`, el puente carga `app/pagina_prediccion.py` bajo el nombre `paa_pagina_prediccion`, expone `render` y lee el commit de la ref a la que apunta `.git/HEAD` |
| `test_el_puente_dibuja_la_pestana_y_el_commit_desplegado` | Con `PAA_REPO` apuntando al clon falso, `render()` dibuja la pestaña y cierra con «Versión desplegada: 1111111 del repositorio del PAA» |
| `test_el_puente_recarga_cuando_cambia_el_commit` | Con el mismo commit devuelve el mismo módulo; al cambiar el commit y los archivos (como un `git checkout`), carga uno nuevo y `src` también se recarga |
| `test_el_puente_lee_el_commit_de_packed_refs_y_de_head_suelto` | El commit se lee de `packed-refs` si la ref suelta no existe, de un `HEAD` suelto, y es `None` si no hay `.git` |
| `test_sin_clon_muestra_error_y_no_lanza` | Con `PAA_REPO` apuntando a una carpeta inexistente: un único `st.error` («No se encontró el clon…») y ninguna excepción |
| `test_con_una_importacion_que_falla_muestra_error_y_no_lanza` | Con una página que importa un módulo inexistente: un único `st.error` con `ModuleNotFoundError`, el traceback en el expander y ninguna excepción; no queda `paa_pagina_prediccion` a medio cargar en `sys.modules` |
| `test_tras_cambiar_el_commit_la_funcion_cacheada_de_la_pagina_devuelve_el_valor_nuevo` | Una función de la página con `st.cache_data` que lee un archivo devuelve el valor nuevo tras cambiar el commit y el archivo. Sin vaciar su caché, devolvería el anterior (se comprobó quitando la llamada: la prueba falla) |
| `test_vaciar_la_cache_de_la_pagina_no_vacia_la_de_una_funcion_ajena` | Una función cacheada que no es del módulo conserva su caché después de la recarga (D82: no se usan `st.cache_*.clear()` globales) |
| `test_si_falla_el_vaciado_de_una_cache_se_anota_en_el_diagnostico_y_el_puente_sigue` | Si el `.clear()` de un atributo del módulo lanza una excepción, el puente la anota como `st.warning` en el expander de diagnóstico, vacía igual las demás cachés y la página sigue mostrando el valor nuevo |
| `test_un_src_ajeno_antes_en_sys_path_dispara_un_error_con_las_dos_rutas` | Con un paquete `src` ajeno puesto antes en `sys.path`, el puente detecta que `sys.modules["src.modelo"].__file__` no está dentro del clon: un único `st.error` con la ruta esperada y la cargada, ninguna excepción, y no queda cargada la pestaña. Se comprobó que la prueba falla si se quita la verificación |
| `test_con_el_src_del_clon_la_verificacion_pasa` | Con el `src` del clon primero en `sys.path`, la verificación no da error y la pestaña se dibuja |
| `test_el_puente_con_este_repositorio_como_clon_muestra_la_pestana_real` | Integración: con este mismo repositorio como clon (`PAA_REPO`), el puente dibuja la pestaña real (texto «qué se predice») y el pie con un hash, sin errores |

**Un detalle de la prueba de recarga.** Las versiones del clon falso tienen distinto largo («version-dos»). Con textos del mismo largo escritos en el mismo
segundo (`v1` y `v2`), Python reutilizaba el `.pyc` de la versión anterior y `src` parecía no recargarse. Es un artefacto de la prueba: un `git checkout`
real cambia la fecha de modificación de los archivos que modifica, de modo que Python no reutiliza el `.pyc` viejo.

### 7.2 Corridas

| Corrida | Comando | Resultado |
| --- | --- | --- |
| **Entorno con las versiones del servidor** (ver abajo) | `pytest tests/test_pipeline_inferencia.py tests/test_app.py tests/test_servidor.py tests/test_variables.py` | **84 pasadas** (44 + 12 + 13 + 15), 0 fallidas, 0 saltadas |
| **Repositorio de trabajo** (`.venv`: Python 3.13.2, streamlit 1.65.0, pandas 2.3.3, numpy 2.5.2, plotly 7.1.0, pydeck 0.9.3, scipy 1.18.1, holidays 0.103, statsmodels 0.14.6) | `pytest` | **115 pasadas**, 0 fallidas, 0 saltadas |
| `tests/test_servidor.py` solo, en los dos entornos anteriores | `pytest tests/test_servidor.py` | **13 pasadas** en cada uno |

Cuentas: 102 pruebas al 25/10 (§6.1) + 13 de `tests/test_servidor.py` = 115. En el entorno del servidor: 44 + 12 + 13 + 15 = 84.

**Entorno con las versiones del servidor.** Armado con `uv` fuera del repositorio: Python **3.11.15**, streamlit 1.56.0, pandas 3.0.2, numpy 2.4.4,
plotly 5.22.0, pydeck 0.9.1, SQLAlchemy 2.0.36, python-dotenv 1.0.1, streamlit-option-menu 0.3.6, scipy 1.16.3, holidays 0.103 y pytest 9.1.1 (las
versiones se leyeron del propio entorno después de instalarlo). Comandos:

```
uv venv --python 3.11.15 entorno_servidor
uv pip install --python entorno_servidor/Scripts/python.exe streamlit==1.56.0 pandas==3.0.2 numpy==2.4.4 plotly==5.22.0 pydeck==0.9.1 SQLAlchemy==2.0.36 python-dotenv==1.0.1 streamlit-option-menu==0.3.6 scipy==1.16.3 holidays==0.103 pytest
```

Se corrieron cuatro archivos. (La primera versión de esta sección, del commit del paso 3, daba 81 pasadas, con 10 pruebas en `test_servidor.py`; el puente ganó después la verificación del `src` y tres pruebas.) **`tests/test_modelo.py` y `tests/test_train_modelo_final.py` quedaron excluidos** porque necesitan `statsmodels`,
que el servidor no usa para la pestaña y que este entorno no tiene instalado. `tests/test_variables.py` (15 pruebas) sí se incluyó: no necesita `statsmodels`.
La pestaña (`src/modelo.py` incluido) no importa `statsmodels`: las 84 pruebas pasaron sin él.

`tests/test_variables.py` usa un panel sintético, salvo dos pruebas (`test_panel_real_*`) que leen el panel real por `src/datos.py:cargar_panel_desarrollo()`
y se saltan solas si `data/processed/` no existe. **En esta corrida no se saltaron**, porque el árbol de trabajo tiene `data/processed/` (no se versiona).
En un clon sin esos datos, como el del servidor, esas dos se saltarían: el total sería 82 pasadas y 2 saltadas.

### 7.3 Lo que estas corridas no cubren

- **No reemplazan la prueba en el servidor.** El entorno de la primera corrida reproduce las **versiones** de Python y de las bibliotecas del diagnóstico del
  26/10, pero es **Windows**, con un Python de uv, y el servidor es Linux. No reproduce el `sys.path` del servidor (`/app/streamlit`, `/app`,
  `/app/streamlit/librerias`, `site-packages`), el `cwd` `/app`, el `app.py` del dashboard del PID (con sus `charts.py` y `ui.py` propios), ni el clon real
  en `/app/proyecto-machine-learning`.
- **No prueban la instalación de scipy y holidays en `librerias/`.** Esa corrida los instala con `uv pip install`, no con el `pip install --target` del
  procedimiento de despliegue, que baja ruedas `manylinux` para Linux; en Windows no se pueden ejecutar.
- **El puente se prueba con un clon falso, no con el real:** no se probó un `git checkout` verdadero sobre `/app/proyecto-machine-learning` ni la lectura de
  su `.git` (por ejemplo con `packed-refs` generado por `git gc`; sólo se prueba con archivos escritos a mano).
- **La concurrencia no se probó.** Si dos sesiones cargan la página a la vez justo cuando cambia el commit, el estado del puente (un diccionario del módulo) es compartido; no se analizó ese caso.
- **No se verificó con el tema del servidor ni visualmente** (igual que §6.4).
- **Pandas 3.0.2 contra 2.3.3.** Las pruebas de la pestaña pasan con las dos versiones: en las dos se comparan las 56 μ de la semana posterior al corte con el CSV del job 136
  (tolerancia 1e-6) y la desvianza global con `tablas/06_globales.csv`, de modo que los resultados numéricos no cambian entre versiones.
  Esta es la corrida de las pruebas, no una comparación aparte de valores.
- **Corrección a §6.1.** Allí el Python del dashboard del servidor figura como «inferido… sin verificación directa»: el diagnóstico del 26/10, leído desde la propia pestaña, da 3.11.15.
