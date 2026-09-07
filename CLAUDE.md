# CLAUDE.md

Guía para Claude Code (y otros asistentes) al trabajar en este repositorio.

## Descripción del proyecto

Proyecto de Aprendizaje Automático (PAA) de UTEC / LIDIA 2026 sobre **predicción de
siniestros viales**. Continúa el Proyecto de Ingeniería de Datos (PID) del mismo equipo,
reutilizando sus datos y activos. La guía completa está en `Guia_estudiantes_PAA_2026.md`.

## Estructura del repositorio

```
data/
  └──processed
  └──raw            Datos o mecanismo de acceso (no versionar datos restringidos/pesados)
notebooks/       Notebooks de exploración y análisis
src/             Código fuente: preprocesamiento, modelado, inferencia
models/          Modelos entrenados y artefactos (los pesados se ignoran en git)
experiments/     Registro de experimentos, configuraciones y resultados
app/             Prototipo / dashboard integrado (objetivo TRL 5)
documentacion/   Documentación, incluye registro_uso_IA.md, Entrega1_Proyecto_Aprendizaje_Automatico_08-17-26.md, Guia_estudiantes_PAA_2026.md
tests/           Pruebas del pipeline de inferencia
```

## Propuesta de proyecto (Plantilla completada)
  documentacion\Entrega1_Proyecto_Aprendizaje_Automatico_08-17-26.md

## Entorno y comandos

- **SO:** Windows. Shell principal: PowerShell (también hay bash disponible).
- **Entorno Python:**
  ```
  python -m venv .venv
  .venv\Scripts\activate      # PowerShell/CMD
  pip install -r requirements.txt
  ```
- **Pruebas:** `pytest` (los tests viven en `tests/`).

## Reglas de trabajo (según la guía PAA)

- **Reproducibilidad:** la solución debe poder ejecutarse desde el repo sin reentrenar
  el modelo (entregables 3 y 4). Mantener README, `requirements.txt`, semillas y
  artefactos actualizados.
- **No versionar:** datos restringidos, credenciales, claves ni archivos grandes. Si no
  se versionan datos, documentar en el README cómo obtenerlos.
- **Registro de IA:** todo uso relevante de IA generativa se documenta en
  `documentacion/registro_uso_IA.md`. Ver la sección **Registro de uso de IA
  (obligatorio)** más abajo: es de cumplimiento obligatorio en cada sesión.
- **Trazabilidad:** mantener versiones identificables de cada hito (tags/ramas) y
  contribuciones identificables por integrante (cuentas personales, sin cuentas
  compartidas).
- **Evitar fugas de información** en la preparación y evaluación; el conjunto de prueba se reserva y solo se usa para evaluar la solución ya seleccionada.

## Registro de uso de IA (obligatorio)

> **Instrucción para Claude Code y cualquier otro asistente de IA:** al final de cada
> sesión de trabajo —y siempre antes de hacer commit de cambios producidos con tu
> ayuda— **debes** registrar los prompts y respuestas relevantes de esa sesión en
> `documentacion/registro_uso_IA.md`. No es opcional ni se hace “si sobra tiempo”: es un
> requisito de aprobación del PAA desde el Entregable 1 (guía PAA 2026, sección 4.3).
> Si por algún motivo no puedes escribir el archivo, avísalo explícitamente al final de
> la sesión en lugar de omitirlo en silencio.

### Qué se considera "relevante"

Se registra todo prompt/respuesta que **haya incidido** en:

- código que quedó en el repositorio (nuevo, modificado o refactorizado);
- el análisis de datos, la elección de variables, métricas o protocolo de evaluación;
- la documentación (README, informe, esta guía, plantillas);
- una decisión importante del proyecto (modelo seleccionado, arquitectura, alcance).

**No** se registra el ruido de sesión: comandos triviales, errores tipográficos,
preguntas de sintaxis puntual o intercambios descartados sin efecto alguno. Si un
intercambio se descartó pero **explica una decisión** (p. ej. se probó un enfoque y se
abandonó), sí se registra, indicando que se descartó y por qué.

### Reglas del archivo

- Nombre exacto: `registro_uso_IA.md` (así, con `IA` en mayúsculas). Ubicación:
  `documentacion/`.
- **Incremental y append-only:** las entradas nuevas se agregan al final. Nunca borres,
  reescribas ni "resumas" entradas anteriores; el archivo debe mostrar la evolución real
  del proyecto a lo largo de todo el semestre.
- El encabezado del archivo debe mantener la **declaración explícita** de que el equipo
  sí utilizó herramientas de IA generativa, con cuáles y para qué.
- Los prompts se transcriben **textualmente**. Las respuestas pueden citarse en su parte
  relevante (fragmento de código, recomendación, justificación) en lugar de copiarse
  completas, pero sin alterar su contenido.
- Cada entrada debe cerrar con cómo se **usó, modificó, descartó o verificó** la
  respuesta. "Verificado" significa decir *cómo*: se ejecutó el test X, se comparó con la
  documentación de scikit-learn, se validó contra los datos, etc.
- **Protección de datos:** no pegar en el prompt ni en el registro datos personales,
  sensibles, confidenciales o restringidos. Si un prompt incluyó una muestra de datos,
  anonimizarla o describirla en el registro (`[muestra de 5 filas anonimizada]`).
- El registro se versiona junto con los cambios que documenta, en el mismo commit o en
  uno inmediatamente posterior.

### Formato de entrada

Agregar al final del archivo un bloque por sesión, con este formato:

```markdown
## Sesión YYYY-MM-DD — <integrante> — <herramienta y modelo>

**Contexto:** <en qué se trabajó y sobre qué archivos>

### Prompt 1
> <prompt textual>

**Respuesta (extracto relevante):**
<fragmento de código o recomendación>

**Uso y verificación:** <utilizado tal cual / adaptado: qué se cambió / descartado: por
qué> — <cómo se verificó: tests, ejecución, contraste con fuentes, revisión del equipo>
**Archivos afectados:** `src/...`, `notebooks/...`

### Prompt 2
...
```

## Redacción del informe técnico

> **Instrucción para Claude Code:** puedes redactar y mantener las secciones **técnicas**
> del informe. **No** redactes la *Introducción* ni el *Marco teórico*: esas dos las
> escribe el equipo a mano. Si detectas que faltan o son inconsistentes con lo técnico,
> señálalo, pero no las escribas ni las "completes".

El informe es **acumulativo desde el Entregable 2** (guía PAA, sección 7): no se escribe
de cero al final, se amplía en cada hito. Vive en `documentacion/informe/`.

### Reparto de secciones

| Sección | Quién |
| --- | --- |
| Introducción, Marco teórico | Equipo, a mano |
| Metodología (datos, preparación, diseño de evaluación, línea base) | Claude redacta, equipo valida |
| Experimentación y resultados | Claude redacta, equipo valida |
| Análisis crítico, explicabilidad, limitaciones | Claude estructura; el juicio lo pone el equipo |
| Prototipo y pruebas del pipeline | Claude redacta, equipo valida |
| Conclusiones y trabajo futuro | Borrador de Claude, reescritura del equipo |

### Regla de oro: ninguna cifra sin artefacto

**Está prohibido inventar, estimar, redondear "para el ejemplo" o rellenar métricas,
tablas, tiempos de ejecución, tamaños de dataset o resultados.** Todo número del informe
debe poder rastrearse hasta un artefacto real del repositorio (`experiments/`, `models/`,
`notebooks/`, salidas de `src/`, logs del servidor institucional).

Si el número todavía no existe, dejar un marcador visible en lugar de completarlo:

```markdown
<!-- PENDIENTE: F1 macro del modelo final en test — falta ejecutar experiments/exp_07 -->
```

Al citar un resultado, indicar de dónde sale (nombre del experimento, notebook o archivo
de salida). Esto es lo que la guía llama **trazabilidad entre datos, código,
configuración, resultado y decisión** (secciones 4.4 y 6.3), y es lo que el tribunal
verifica cruzando informe contra repositorio.

### Qué debe contener cada sección técnica

**Metodología — datos** (guía 6.1): unidad de análisis, propósito de la predicción,
variable objetivo, fuentes y qué se hereda del PID frente a qué se agregó en el PAA;
diagnóstico de calidad, cobertura, representatividad, sesgos y restricciones de uso;
justificación de las variables y transformaciones; verificación explícita de que no se
incorpora información no disponible al momento real de la predicción.

**Metodología — preparación:** limpieza, imputación, codificación, escalado, balanceo,
selección o construcción de variables, reducción de dimensionalidad, tratamiento
específico de la modalidad (temporal, texto, etc.). Cada paso va con su *porqué* y su
efecto observado. Dejar constancia de que las transformaciones que aprenden de los datos
se ajustaron solo con entrenamiento (y dentro de cada partición de validación cuando
corresponda).

**Metodología — diseño de evaluación** (guía 6.2): particiones, esquema de validación,
métricas elegidas y por qué son coherentes con el objetivo, los costos de error y el
balance de clases; división cronológica si el orden temporal importa; medidas concretas
contra fugas de información; conjunto de prueba reservado y no usado para decidir nada.

**Línea base:** qué es, por qué esa, y evaluada con **el mismo protocolo y las mismas
métricas** que las alternativas posteriores. Sin esto los resultados no son interpretables.

**Experimentación y resultados** (guía 6.3): hipótesis que orientaron cada experimento,
comparación justa bajo el mismo protocolo, resultados negativos o descartados cuando
expliquen una decisión, criterios explícitos de selección final (no una sola métrica:
desempeño, estabilidad, explicabilidad, costo, restricciones, integración), y la
evaluación en test **una sola vez**, ya fijada la solución. Comparar contra la línea base
y contra los objetivos declarados.

**Análisis crítico y explicabilidad** (guía 1.3 y 6.4): qué variables o patrones resultan
relevantes según la evidencia disponible (importancias, coeficientes, reglas, matrices de
confusión, ejemplos de acierto y error, desempeño por clase o condición); en qué
situaciones el modelo funciona mejor y peor; análisis de errores y no solo métricas
agregadas; limitaciones, supuestos y amenazas a la validez; explicación de resultados
inesperados. Si el proyecto usa datos de personas o afecta decisiones sobre ellas,
analizar sesgos y diferencias de desempeño entre grupos; si no, analizar robustez entre
clases, períodos o condiciones.

**Prototipo TRL 5 y pruebas:** qué hace el prototipo, cómo se integra con el dashboard
heredado del PID, qué funcionalidades nuevas aporta, y el resultado de las pruebas del
pipeline de inferencia (validación de entradas, carga del modelo, flujo integral,
formato/rango de salidas), incluidos los errores detectados y sus correcciones.

### Estilo y forma

- Español, registro académico, impersonal o primera persona del plural, **consistente**.
  Pasado para lo realizado, presente para lo que el sistema hace.
- **Interpretar, no describir.** Toda tabla, figura o métrica debe estar leída en el
  texto y relacionada con el problema. Una figura sin lectura no suma y ocupa página.
- **Distinguir evidencia de inferencia** (guía 6.4): separar lo que los datos muestran de
  lo que el equipo concluye. Usar "los resultados sugieren", no "queda demostrado".
- Sin relleno retórico, sin "cabe destacar", sin vender la solución. Sin repetir
  extensamente el informe del PID: se lo referencia.
- **Extensión** (guía 7.1): máximo 50 páginas de Introducción a Conclusiones inclusive,
  tablas y figuras incluidas; anexos, 20 páginas en conjunto. **Es un techo, no una
  meta.** Código, notebooks completos, logs extensos y salidas masivas quedan en el
  repositorio, nunca en el informe.
- El formato (estructura, numeración, tablas, figuras, citas) sigue la *Guía y modelo
  para la elaboración de informes de proyectos integradores* institucional vigente. Si
  esa guía no está en contexto, **preguntar antes de asumir un formato**.
- **Citas APA 7.** No inventar referencias, DOI, años ni autores bajo ningún concepto.
  Citar solo fuentes efectivamente consultadas por el equipo. Todo recurso de terceros
  (código, dataset, modelo preentrenado, notebook, figura) se identifica y cita.

### Antes de dar por cerrada una tanda de redacción

- No quedaron marcadores `PENDIENTE` sin avisar al equipo.
- Cada cifra del texto coincide con el artefacto del repositorio que la respalda.
- Cada tabla y figura está numerada, referida desde el texto e interpretada.
- Lo heredado del PID está distinguido de lo desarrollado en el PAA.
- El texto es defendible: si hay algo que el equipo no podría explicar ante el tribunal,
  señalarlo explícitamente en vez de dejarlo pasar.
- La sesión quedó registrada en `documentacion/registro_uso_IA.md`.

## Documentación de notebooks (obligatorio)

> **Instrucción para Claude Code:** **cada notebook de `notebooks/` tiene un documento
> acompañante en `documentacion/`**. Al crear un notebook nuevo, crear su documento. Al
> modificarlo de forma que cambie cualquier cifra o decisión, **actualizar el documento en la
> misma sesión**. Un notebook cuyo documento quedó desactualizado es peor que uno sin documento:
> induce a citar cifras que ya no existen.

### Para qué existen estos documentos

Son **contexto autocontenido** para que un asistente **sin acceso al repositorio** —típicamente
Claude en la web— pueda ayudar a redactar la documentación del proyecto (informe técnico,
presentaciones, defensa). Quien los lea no puede abrir el notebook, ni ejecutar código, ni ver
`experiments/`: **todo lo que necesite tiene que estar en el documento**.

De ahí las dos propiedades que los definen:

1. **Autocontenidos.** Nada de «ver la sección 3 del notebook». Si un número importa, va escrito.
2. **Trazables.** Cada cifra lleva al lado el artefacto que la respalda
   (`tablas/NN_nombre.csv`, `figuras/figN_nombre.png`). Es la regla de oro del informe aplicada
   un nivel antes: si el documento no puede rastrear una cifra, el informe tampoco podrá.

### Convención de nombres

`documentacion/<nombre_del_notebook>.md`, con el mismo nombre que el notebook. Ejemplos:

| Notebook | Documento |
| --- | --- |
| `notebooks/diagnostico_datos.ipynb` | `documentacion/resumen_diagnostico_datos.md` |
| `notebooks/preparacion_montevideo.ipynb` | `documentacion/resumen_preparacion_montevideo.md` |

El prefijo `resumen_` se mantiene por continuidad con el primero. **Referencia de estructura y
tono:** `documentacion/resumen_diagnostico_datos.md`.

### Estructura mínima

Adaptar al contenido del notebook, pero no omitir estas piezas:

1. **Encabezado** — notebook de origen, artefactos que produce, fecha de ejecución, alcance.
2. **Cómo usar este documento** — para qué sirve y las reglas que quien redacte debe respetar
   (ninguna cifra sin artefacto; distinguir evidencia de inferencia; no redactar Introducción ni
   Marco teórico).
3. **Qué hace el notebook y por qué** — decisiones tomadas **con su justificación**, no sólo el
   qué. Las decisiones descartadas se registran igual, con el motivo.
4. **Resultados, en tablas** — con la referencia al artefacto en cada bloque.
5. **Limitaciones y lo que NO puede afirmarse** — incluida una lista explícita de **frases que no
   deben aparecer en el informe** porque los datos no las sostienen. Esta sección es la que más
   protege al equipo ante el tribunal.
6. **Índice de artefactos** — qué tabla o figura respalda qué afirmación.
7. **Qué queda pendiente** — lo que el notebook deja planteado para el siguiente.

### Reglas de contenido

- **Distinguir evidencia de inferencia**, explícitamente. «Los datos muestran X» y «el equipo
  concluye Y» son afirmaciones distintas y se marcan como tales.
- **Registrar los cambios de alcance.** Si el notebook fue reescrito, decir qué cubría antes y por
  qué cambió: evita que alguien cite cifras de una versión superada.
- **Comparar contra la versión anterior** cuando ayude a entender una decisión (p. ej. «con la
  grilla de 1 km eran 95,08 % de ceros; con barrios, 71,96 %»).
- **No adornar.** Si un resultado es débil o incómodo, se dice. El documento existe para que el
  equipo pueda defender el trabajo, y una cifra maquillada se cae en la primera pregunta.

## Convenciones

- Idioma del proyecto y de la documentación: **español**.
- Nombres de archivos y variables en español o inglés de forma consistente con el código
  existente.
- Al terminar una sesión relevante, actualizar `HANDOFF.md` con el estado y lo pendiente,
  y `documentacion/registro_uso_IA.md` con los prompts de la sesión.
- Si la sesión tocó un notebook, actualizar también su documento acompañante en
  `documentacion/` (ver **Documentación de notebooks**).

## Git

- Rama principal: `main`. Remoto: `origin`
  (https://github.com/victoruria-netizen/proyecto-machine-learning.git).
- Identidad configurada localmente: Victor Uria / victor.uria@estudiantes.utec.edu.uy.
- Hacer commits descriptivos en español. Confirmar con el equipo antes de push cuando
  haya cambios sensibles.
