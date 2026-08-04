# CLAUDE.md

Guía para Claude Code (y otros asistentes) al trabajar en este repositorio.

## Descripción del proyecto

Proyecto de Aprendizaje Automático (PAA) de UTEC / LIDIA 2026 sobre **predicción de
siniestros viales**. Continúa el Proyecto de Ingeniería de Datos (PID) del mismo equipo,
reutilizando sus datos y activos. La guía completa está en `Guia_estudiantes_PAA_2026.md`.

## Estructura del repositorio

```
data/            Datos o mecanismo de acceso (no versionar datos restringidos/pesados)
notebooks/       Notebooks de exploración y análisis
src/             Código fuente: preprocesamiento, modelado, inferencia
models/          Modelos entrenados y artefactos (los pesados se ignoran en git)
experiments/     Registro de experimentos, configuraciones y resultados
app/             Prototipo / dashboard integrado (objetivo TRL 5)
documentacion/   Documentación, incluye registro_uso_IA.md
tests/           Pruebas del pipeline de inferencia
```

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
  `documentacion/registro_uso_IA.md` (prompt, respuesta, cómo se usó/verificó).
- **Trazabilidad:** mantener versiones identificables de cada hito (tags/ramas) y
  contribuciones identificables por integrante (cuentas personales, sin cuentas
  compartidas).
- **Evitar fugas de información** en la preparación y evaluación; el conjunto de prueba
  se reserva y solo se usa para evaluar la solución ya seleccionada.

## Convenciones

- Idioma del proyecto y de la documentación: **español**.
- Nombres de archivos y variables en español o inglés de forma consistente con el código
  existente.
- Al terminar una sesión relevante, actualizar `HANDOFF.md` con el estado y lo pendiente.

## Git

- Rama principal: `main`. Remoto: `origin`
  (https://github.com/victoruria-netizen/proyecto-machine-learning.git).
- Identidad configurada localmente: Victor Uria / victor.uria@estudiantes.utec.edu.uy.
- Hacer commits descriptivos en español. Confirmar con el equipo antes de push cuando
  haya cambios sensibles.
