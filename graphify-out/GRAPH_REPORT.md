# Graph Report - .  (2026-08-05)

## Corpus Check
- Corpus is ~9,789 words - fits in a single context window. You may not need a graph.

## Summary
- 71 nodes · 115 edges · 7 communities
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 6 edges (avg confidence: 0.92)
- Token cost: 121,598 input · 0 output

## Community Hubs (Navigation)
- Bibliografía y Marco Normativo
- Configuración del Repositorio y Equipo
- Registro de Uso de IA y Estructura
- Entorno Python y Dependencias
- Entregables y Cronograma
- Propuesta de Aprobación PAA
- Reglas de Reproducibilidad y Evaluación

## God Nodes (most connected - your core abstractions)
1. `Guía para estudiantes PAA 2026` - 31 edges
2. `HANDOFF.md — Predicción de Siniestros Viales (PAA)` - 11 edges
3. `CLAUDE.md (guía para agentes)` - 8 edges
4. `Proyecto de Ingeniería de Datos (PID)` - 8 edges
5. `Plantilla de presentación y aprobación de la propuesta de PAA` - 7 edges
6. `Reglas de trabajo (según la guía PAA)` - 6 edges
7. `Entregable 1: Propuesta inicial` - 6 edges
8. `Entregable 3: Experimentación avanzada y solución seleccionada` - 6 edges
9. `Calendario general de hitos (sección 3)` - 6 edges
10. `Entregable 2: Datos, metodología y línea base` - 5 edges

## Surprising Connections (you probably didn't know these)
- `Estructura del repositorio (CLAUDE.md)` --semantically_similar_to--> `Estructura recomendada del repositorio (sección 4.1)`  [INFERRED] [semantically similar]
  CLAUDE.md → Guia_estudiantes_PAA_2026.md
- `Calendario de entregables (HANDOFF)` --semantically_similar_to--> `Calendario general de hitos (sección 3)`  [INFERRED] [semantically similar]
  HANDOFF.md → Guia_estudiantes_PAA_2026.md
- `Configuración de Git (rama main, origin, identidad)` --semantically_similar_to--> `Repositorio remoto GitHub (victoruria-netizen/proyecto-machine-learning)`  [INFERRED] [semantically similar]
  CLAUDE.md → HANDOFF.md
- `Estructura del repositorio (README)` --semantically_similar_to--> `Estructura recomendada del repositorio (sección 4.1)`  [INFERRED] [semantically similar]
  README.md → Guia_estudiantes_PAA_2026.md
- `Estado actual (hecho)` --semantically_similar_to--> `Entrada 1: Inicialización de estructura de carpetas (2026-08-04)`  [INFERRED] [semantically similar]
  HANDOFF.md → documentacion/registro_uso_IA.md

## Hyperedges (group relationships)
- **Ciclo de cuatro entregables acumulativos del PAA** — guia_estudiantes_paa_2026_entregable_1, guia_estudiantes_paa_2026_entregable_2, guia_estudiantes_paa_2026_entregable_3, guia_estudiantes_paa_2026_entregable_4 [EXTRACTED 1.00]
- **Artefactos requeridos para la reproducibilidad del PAA** — readme_readme, requirements_requirements, documentacion_registro_uso_ia_registro, guia_estudiantes_paa_2026_reproducibilidad [INFERRED 0.85]
- **Estructura de repositorio descrita de forma independiente en tres documentos** — guia_estudiantes_paa_2026_estructura_repositorio, claude_estructura_repositorio, readme_estructura_repositorio [INFERRED 0.95]

## Communities (7 total, 0 thin omitted)

### Community 0 - "Bibliografía y Marco Normativo"
Cohesion: 0.12
Nodes (16): Alpaydın (2020) — Introduction to Machine Learning, Bagnato (2020) — Aprende Machine Learning en Español, Burkov (2019) — The Hundred-Page Machine Learning Book, Circular 29/DE/2022 — Circular de trabajos finales, Circular 37/DE/2024 — Evaluaciones, calificaciones e inasistencias, Defensa final (sección 8.1), Explicabilidad e interpretación (secciones 1.3 y 6.4), Géron (2019) — Hands-On Machine Learning with Scikit-Learn, Keras, and TensorFlow (+8 more)

### Community 1 - "Configuración del Repositorio y Equipo"
Cohesion: 0.24
Nodes (10): CLAUDE.md (guía para agentes), Convenciones del repositorio, Estructura del repositorio (CLAUDE.md), Configuración de Git (rama main, origin, identidad), Pablo D. Cuña (Docente de Proyecto), Proyecto de Aprendizaje Automático (PAA), Calendario de entregables (HANDOFF), HANDOFF.md — Predicción de Siniestros Viales (PAA) (+2 more)

### Community 2 - "Registro de Uso de IA y Estructura"
Cohesion: 0.31
Nodes (9): Claude Code (Anthropic), Entrada 1: Inicialización de estructura de carpetas (2026-08-04), Estructura recomendada del repositorio (sección 4.1), registro_uso_IA.md (requisito obligatorio desde Entregable 1), Estado actual (hecho), Estructura del repositorio (README), Proyecto de origen (PID) — sección README, README.md — Predicción de Siniestros Viales (+1 more)

### Community 3 - "Entorno Python y Dependencias"
Cohesion: 0.25
Nodes (8): Entorno Python (venv + requirements.txt), jupyter, matplotlib, numpy, pandas, pytest, scikit-learn, seaborn

### Community 4 - "Entregables y Cronograma"
Cohesion: 0.33
Nodes (9): Calendario general de hitos (sección 3), Entregable 1: Propuesta inicial, Entregable 2: Datos, metodología y línea base, Entregable 3: Experimentación avanzada y solución seleccionada, Entregable 4: Entrega definitiva al tribunal, Servidor institucional (sección 4.2), Prototipo TRL 5, Pendiente (próximos pasos) para Entregable 1 (+1 more)

### Community 5 - "Propuesta de Aprobación PAA"
Cohesion: 0.28
Nodes (9): Integridad académica y plagio (sección 9), Proyecto de Ingeniería de Datos (PID), Sección C: Carta aval y aceptación de tutoría, Sección B: Contenido de la propuesta (13 puntos), Punto 6: Datos e integración con ingeniería y gestión de datos, Sección D: Decisión sobre la propuesta y la tutoría, Punto 9: Idea del producto/solución (continuidad con el PID), Sección A: Identificación (+1 more)

### Community 6 - "Reglas de Reproducibilidad y Evaluación"
Cohesion: 0.25
Nodes (8): Reglas de trabajo (según la guía PAA), Declaración de uso de IA generativa, Diseño de evaluación (sección 6.2), Prevención de fugas de información / conjunto de prueba reservado, Línea base (baseline reproducible), Pruebas del pipeline de inferencia (sección 4.5), Reproducibilidad (sección 4.4), Uso de inteligencia artificial generativa (sección 4.3)

## Knowledge Gaps
- **25 isolated node(s):** `Prototipo TRL 5`, `Explicabilidad e interpretación (secciones 1.3 y 6.4)`, `Defensa final (sección 8.1)`, `Alpaydın (2020) — Introduction to Machine Learning`, `Bagnato (2020) — Aprende Machine Learning en Español` (+20 more)
  These have ≤1 connection - possible missing edges or undocumented components.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Guía para estudiantes PAA 2026` connect `Bibliografía y Marco Normativo` to `Configuración del Repositorio y Equipo`, `Registro de Uso de IA y Estructura`, `Entregables y Cronograma`, `Propuesta de Aprobación PAA`, `Reglas de Reproducibilidad y Evaluación`?**
  _High betweenness centrality (0.633) - this node is a cross-community bridge._
- **Why does `HANDOFF.md — Predicción de Siniestros Viales (PAA)` connect `Configuración del Repositorio y Equipo` to `Bibliografía y Marco Normativo`, `Registro de Uso de IA y Estructura`, `Entregables y Cronograma`, `Propuesta de Aprobación PAA`?**
  _High betweenness centrality (0.197) - this node is a cross-community bridge._
- **Why does `Estado actual (hecho)` connect `Registro de Uso de IA y Estructura` to `Configuración del Repositorio y Equipo`, `Entorno Python y Dependencias`?**
  _High betweenness centrality (0.158) - this node is a cross-community bridge._
- **What connects `Prototipo TRL 5`, `Explicabilidad e interpretación (secciones 1.3 y 6.4)`, `Defensa final (sección 8.1)` to the rest of the system?**
  _25 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Bibliografía y Marco Normativo` be split into smaller, more focused modules?**
  _Cohesion score 0.125 - nodes in this community are weakly interconnected._