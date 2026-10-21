# Pruebas del pipeline de inferencia del prototipo (Entregable 3, fase 5, paso 5c)

**Archivos de prueba:** `tests/test_pipeline_inferencia.py` (24 pruebas recogidas por pytest, algunas parametrizadas) y
`tests/test_app.py` (6). Las dos son nuevas en esta fase.
**Código que prueban:** `app/pagina_prediccion.py` (pestaña «Predicción (PAA)»), que llama a `src/modelo.py`.
**Fecha:** 2026-10-21. **Ejecución:** `pytest` en el `.venv` (Python 3.13.2) y, aparte, en un clon limpio con entorno nuevo (Python 3.13.9).

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
