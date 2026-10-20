# Resumen de la evaluación final — la solución en el bloque final (Entregable 3, fase 4)

**Notebook:** [`notebooks/evaluacion_final.ipynb`](../notebooks/evaluacion_final.ipynb) — **el único del repositorio que lee el bloque final**
(2025-02-06 → 2025-12-31).
**Artefactos:** `experiments/evaluacion_final/` (`tablas/`, `figuras/`, `predicciones_bloque_final.csv`, `registro_ejecucion.csv`).
**Código que usa:** `src/modelo.py` (nuevo en la fase 4), `src/variables.py` (con `tipo_dia`, D50), `src/datos.py`; pruebas en
`tests/test_modelo.py` y `tests/test_variables.py`.
**Fecha de ejecución:** <!-- PENDIENTE: primera ejecución completa con nbconvert; fecha y commit salen de registro_ejecucion.csv -->
**Alcance:** los ocho municipios de Montevideo; 47 cortes de 7 días en el bloque final (329 días), con reentrenamiento en cada corte.

> ### ⚠️ Estado: notebook escrito y commiteado antes de leer el bloque final; **todavía no ejecutado**
>
> Las precisiones D48, D50, D51 y D52 están en la primera celda del notebook y en §1 de este documento. Las secciones 0 a 3 (sin el bloque
> final) se probaron el 20/10/2026 en un proceso aparte: el procedimiento reproduce las 35 cifras de validación comprobadas
> (`modelos_candidatos/tablas/05`, `08`, `26`, `45` y `46`, tolerancia 6e-7). Esa prueba no dejó artefactos (se borraron); la cifra la
> vuelve a producir la ejecución oficial en `tablas/02_control_validacion.csv`.

---

## 0. Cómo usar este documento

Contexto autocontenido para redactar *Experimentación y resultados* (evaluación final), *Análisis crítico* y *Conclusiones* del informe sin
abrir el repositorio.

1. **Ninguna cifra sin artefacto.** Cada cifra lleva la tabla que la respalda; lo que falta se marca `<!-- PENDIENTE: ... -->`.
2. **Distinguir evidencia de inferencia**, rotuladas como tales.
3. **No escribir Introducción ni Marco teórico** a partir de este documento.
4. **Respetar §5** (frases que no deben aparecer en el informe) y **§6** (diferencias con el informe: no se resuelven acá; se alinean en la
   fase 6, D49).
5. **La solución no se eligió con el bloque final.** Quedó fijada en `experiments/modelos_candidatos/solucion_seleccionada.json`, commit
   `1560a5b`, antes de este notebook; ninguna cifra de aquí puede cambiarla.

---

## 1. Qué hace el notebook y por qué

### 1.1 Precisiones fijadas antes de leer el bloque final

Espejo de la celda «Precisiones de la evaluación final» del notebook.

| N.º | Contenido | Origen |
| --- | --- | --- |
| D48 | Modelos: solución GLM Poisson (a) deslizante 364 d; sensibilidad GLM Poisson (a) expansiva (**no puede reemplazar a la solución aunque gane en el test**, D42); contraste XGBoost (a) d=2 n=100 lr=0,1 deslizante 364 d (**no compite**); referencias: media constante, L0 de 8 semanas, L1. Intervalos según D44: μ de la solución y α de NB2 (a) 364 d ajustada en cada corte; también Poisson | Prompt de la fase 4 |
| D50 | Reproducción de la fase 2 en `tests/test_modelo.py` (1e-9 contra el camino de la fase 2 reconstruido; tolerancia de redondeo contra `tablas/31`, `45`, `46`); `entrenar` recibe el panel ya recortado; **fallback de NB2: plan B de D28 (α por momentos) y Poisson solo si no da α positivo** (reemplaza a D48 en ese punto); calendario de fechas fuera del panel con `var.tipo_dia` | Respuestas del equipo al paso 4a |
| D51 | Intervalos solo para la solución (NB2 principal, Poisson secundario); exportación local dentro del notebook después del registro; `train/train_modelo_final.py`, excepción declarada a la regla de lectura del bloque final; `models/historia_reciente.csv` fuera del alcance; tolerancia de los tests 6e-7 | Equipo, 20/10/2026 |
| D52 | Elecciones de análisis: cortes y ventanas; control previo en validación; métricas; comparaciones (contra L1, media constante y la propia validación; pareado descriptivo); análisis de errores; formato de `predicciones_bloque_final.csv`; registro con tolerancia relativa 1e-10; estado de los objetivos fijado antes, con los resultados del test como evidencia | Propuesta de la IA, confirmada por el equipo con dos ajustes |

### 1.2 `src/modelo.py` (paso 4a)

- `entrenar(config, panel_hasta, ajustar_alpha=True)`: filas de `var.matriz_entrenamiento` con la ventana de la configuración, matriz de
  D31 y ajuste con los valores por defecto (GLM IRLS de statsmodels; XGBoost con los hiperparámetros del JSON). Con `ajustar_alpha`, NB2 (a)
  en las mismas filas para α (D29, D28, D50). No lee archivos.
- `predecir_semana(modelo, historia, origen)`: 56 filas (7 días × 8 municipios) con μ, intervalos del 80 % y 95 % (cuantiles 0,10/0,90 y
  0,025/0,975) y su tipo. Solo acepta el origen del modelo. De `historia` solo lee `tipo_dia` de los días del horizonte.
- **Verificación** (`tests/test_modelo.py`, 18 tests; `pytest` completo: 33 pasados): en los 47 cortes de validación, μ y α coinciden a
  1e-9 con el camino de la fase 2 reconstruido en el test, y a 6e-7 con `tablas/31` (solución, sensibilidad y contraste), `45` y `46`.
  `var.tipo_dia` coincide con el `tipo_dia` del ETL en los 1.316 días de desarrollo. Con datos sintéticos Poisson puros, NB2 y el plan B no
  dan α positivo y los intervalos pasan a Poisson (D50).

<!-- PENDIENTE: secciones 1.3 (procedimiento) a 4 (resultados) se completan después de la primera ejecución completa -->

---

## 2. Resultados

<!-- PENDIENTE: globales, por municipio, por semana, comparaciones, errores, calibración, intervalos, cumplimiento de objetivos — tablas/06 a 19 -->

## 5. Limitaciones y lo que NO puede afirmarse

<!-- PENDIENTE: después de la ejecución -->

## 6. Diferencias con el informe

Puntos donde lo ejecutado difiere de la metodología o de los objetivos del informe vigente
(`documentacion/informe/Informe_PAA_Actualizado_el_12-10-26.md`, capítulos 1 y 3). **No se resuelven en el código ni en el informe:** se
alinean en la fase 6 (D49). Lista abierta: se completa al cerrar la fase 4.

| N.º | Sección del informe | Qué dice el informe | Qué se hizo | Por qué |
| --- | --- | --- | --- | --- |
| 1 | §3.4.3 (Validación interna) y Cuadro 3, fila «Estimar parámetros con información futura» | «Sobre el bloque final, el ajuste queda congelado en el bloque de desarrollo»: solo avanza la historia que cada modelo usa como entrada | En cada uno de los 47 cortes del bloque final, cada modelo se **reentrena** con todo lo observado antes del origen y su ventana (D48, D52 ítem 1) | Es el procedimiento de la validación del E3 (reentrenamiento cada 7 días, `solucion_seleccionada.json`: `reentrenamiento_cada_dias` 7) y el del uso previsto. La frase del informe describe el protocolo del E2 |
| 2 | §1.2.2, objetivo 2, y §1.3 (Alcance) | El objetivo 2 compara estrategias «con y sin variables exógenas»; el alcance dice que las variables explicativas comprenden el calendario, **las condiciones meteorológicas diarias** y la historia de cada municipio | El E3 **no evaluó variables meteorológicas**: el conjunto (d) (lluvia) se retiró antes de ejecutar (14/10/2026). Las exógenas evaluadas son solo de calendario | La lluvia del día a predecir no está disponible con horizonte de 7 días (solo un pronóstico) y el diagnóstico no le encontró aporte fuera de muestra (`resumen_diagnostico_municipios.md` §7.5) |
| 3 | §3.4.5 y Cuadro 4 | L0 = promedio de las últimas **cuatro** semanas; «la cantidad de semanas se fijó antes de ejecutar y no se ajustó» | L0 de **8 semanas** | D17: elegida mirando los 47 cortes de validación (`resumen_modelos_candidatos.md` §1.1) |
| 4 | §3.4.2 (Calendario) y §3.4.5 (L1) | Calendario de **tres niveles**; L1 usa los tres niveles | Calendario de **8 niveles** (lunes a domingo + feriado) en L1 y en los candidatos | Sección 1 de `modelos_candidatos` (la forma del diagnóstico, M2) |
| 5 | Tabla 1 y §3.4.3 | Validación por origen móvil con **ventana expansiva** | La solución usa **ventana deslizante de 364 días**; la expansiva queda como sensibilidad | D42, decisión del equipo apartándose de la regla de selección |
| 6 | §3.4.5 y Cuadro 4 (modelos evaluados) | Modelos aprendidos: árbol A y árbol B | Candidatos del E3: GLM Poisson, NB2 y XGBoost; el árbol se retiró antes de ejecutar | Sección 1 de `modelos_candidatos`: el árbol no extrapoló la tendencia en el E2 |

<!-- PENDIENTE: revisar la lista completa contra los capítulos 1 y 3 al cerrar la fase 4 (incluido el paso 4c) -->

`models/historia_reciente.csv` quedó fuera del alcance (D51); el informe no lo menciona, así que no figura en esta tabla.

## 7. Índice de artefactos

<!-- PENDIENTE: después de la ejecución (tablas/00 a 20, figuras 1 a 5, predicciones_bloque_final.csv, registro_ejecucion.csv) -->

## 8. Qué queda pendiente

- Ejecutar el notebook completo con `jupyter nbconvert --execute --inplace` (paso 4b) y completar §2, §5 y §7.
- Paso 4c: exportación del modelo final (`models/`), `train/train_modelo_final.py` en el servidor (excepción declarada, D51) y su log.
