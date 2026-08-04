# Handoff — Predicción de Siniestros Viales (PAA)

Documento de traspaso de contexto. Registra el estado del proyecto y lo pendiente para
retomar el trabajo sin perder información. Actualizar al cerrar cada sesión de trabajo.

_Última actualización: 2026-08-04_

---

## 1. Contexto del proyecto

- **Asignatura:** Proyecto de Aprendizaje Automático (PAA) — UTEC / LIDIA, 2026.
- **Tema:** Predicción de siniestros viales.
- **Continuidad:** El PAA continúa el Proyecto de Ingeniería de Datos (PID) del mismo
  equipo. Se reutilizan datos y activos del PID (declarar y distinguir en el informe).
- **Docente:** Pablo D. Cuña.
- **Guía de referencia:** `Guia_estudiantes_PAA_2026.md` (en la raíz del repo).
- **Plantilla de propuesta:** `Plantilla_presentacion_aprobacion_PAA.md`.

## 2. Repositorio

- **Remoto:** https://github.com/victoruria-netizen/proyecto-machine-learning.git
- **Rama principal:** `main` (ya con `upstream` configurado).
- **Identidad git (local):** Victor Uria / victor.uria@estudiantes.utec.edu.uy

## 3. Estado actual (hecho)

- [x] Estructura de carpetas recomendada (sección 4.1 de la guía) creada:
      `data/ notebooks/ src/ models/ experiments/ app/ documentacion/ tests/`
      (cada carpeta con `.gitkeep`).
- [x] `README.md` con propósito, estructura, requisitos y secciones a completar.
- [x] `documentacion/registro_uso_IA.md` creado con la primera entrada.
- [x] `requirements.txt` con dependencias base de ML.
- [x] `.gitignore` (ignora entornos, datos pesados/restringidos, modelos y secretos).
- [x] Commit inicial y push a `origin/main`.
- [x] Identidad de git configurada (nombre + email coinciden).

## 4. Pendiente (próximos pasos)

Orientado al **Entregable 1 — Propuesta inicial (fecha límite: 17 de agosto de 2026)**:

- [ ] Completar en `README.md`: enlace al repo del PID, componentes reutilizados,
      integrantes del equipo y tutor/a.
- [ ] Dar acceso al **docente** y al **tutor** en GitHub (Settings → Collaborators).
- [ ] Verificar autenticación al **servidor institucional** y documentar el uso previsto.
- [ ] Completar la `Plantilla_presentacion_aprobacion_PAA.md` (incluye enlace al repo).
- [ ] Definir problema de ML, objetivo general y objetivos específicos.
- [ ] Revisión inicial de viabilidad y disponibilidad de los datos.
- [ ] Cronograma inicial y riesgos principales.

## 5. Calendario de entregables

| Fecha         | Hito                                              |
|---------------|---------------------------------------------------|
| 17 de agosto  | **Entregable 1** — Propuesta inicial              |
| 24 de agosto  | Reformulación (si el Comité lo solicita)          |
| 20 de septiembre | **Entregable 2** — Datos, metodología y línea base |
| 25 de octubre | **Entregable 3** — Experimentación y solución     |
| 15 de noviembre | **Entregable 4** — Entrega definitiva al tribunal |

## 6. Notas y decisiones

- Se usa `requirements.txt` (alternativa posible: `environment.yml`).
- Los datos restringidos o pesados **no** se versionan; documentar en el README cómo
  obtenerlos (sección 4.1 de la guía).
- Registrar todo uso de IA generativa en `documentacion/registro_uso_IA.md`.
