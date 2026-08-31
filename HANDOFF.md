# Handoff — Predicción de Siniestros Viales (PAA)

Documento de traspaso de contexto. Registra el estado del proyecto y lo pendiente para
retomar el trabajo sin perder información. Actualizar al cerrar cada sesión de trabajo.

_Última actualización: 2026-08-30_

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
- [x] `notebooks/analisis_inicial.ipynb`: grilla espacial, panel diario día × zona relleno con
      ceros, features causales (rezagos, medias móviles, días desde el último siniestro) y
      split temporal 2019–2023 / 2024 / 2025 con submuestreo ponderado de ceros.
- [x] `notebooks/diagnostico_datos.ipynb` (2026-08-30): diagnóstico de calidad, adecuación,
      cobertura y limitaciones exigido por el Entregable 2. Deja 26 tablas CSV y 5 figuras en
      `experiments/diagnostico_datos/` para citar desde el informe.
- [x] **División cronológica 70 / 10 / 20** fijada en el diagnóstico (sección 3.2):
      entrenamiento 2019-01-01 → 2023-11-25 (1.790 días), validación 2023-11-26 → 2024-08-07
      (256 días), test reservado 2024-08-08 → 2025-12-31 (511 días). El 20 % final se reserva
      y el 80 % restante se reparte en 70 % / 10 %.

### Hallazgos del diagnóstico que condicionan lo que sigue

1. **No hay señal temporal de corto plazo por zona.** La autocorrelación diaria de las series
   por zona cae dentro de la banda nula de un Poisson de la misma tasa. La señal aprovechable
   es la tasa histórica de la zona más el calendario nacional. Consecuencia: la línea base debe
   ser *tasa de la zona × factor de calendario*, no una regla de persistencia.
2. **El objetivo es casi binario** (99,6 % de ceros; 97,4 % de los positivos valen 1) y de
   dispersión Poisson (1,05). Las métricas deben medir calibración y ordenamiento, no exactitud
   puntual del conteo.
3. **`data/processed/` no es reproducible con el código versionado:** los Parquet están
   construidos con celdas de 1 km (11.633 zonas) y `analisis_inicial.ipynb` declara 500 m
   (18.487 zonas).
4. **`es_feriado` está incompleta:** marca 41 de los 145 días con caída sistemática de
   siniestralidad; omite Semana de Turismo y Carnaval.
5. **El clima no está integrado:** no hay caché de Open-Meteo en `data/`, y queda una
   autocorrelación residual de 0,30 en la serie nacional sin explicar por el calendario.
6. **Las particiones 70/10/20 no son estacionalmente homogéneas.** El corte cae a mitad de año:
   la validación no contiene ningún día de setiembre ni de octubre y el test incluye dos
   diciembres. El *nivel* del error de validación y el de test no son comparables entre sí; sí
   lo es la comparación entre modelos dentro de una misma partición.

## 4. Pendiente (próximos pasos)

Orientado al **Entregable 2 — Datos, metodología y línea base (fecha límite: 20 de septiembre
de 2026)**. En orden de prioridad, según lo que dejó abierto el diagnóstico:

- [ ] **Fijar la granularidad y regenerar `data/processed/`.** La evidencia para elegirla está
      en la sección 4.2 del diagnóstico; hoy el código y los artefactos no coinciden.
- [ ] **Alinear `analisis_inicial.ipynb` con la división 70/10/20.** Hoy parte por años
      completos (≈71/14/14) y escribe las *features* particionadas por año; al cortar dentro
      del año, el filtro de partición pasa a ser por fecha y no por directorio.
- [ ] **Integrar la caché climática de Open-Meteo** heredada del PID y volver a medir la señal
      residual de la serie nacional.
- [ ] **Corregir `es_feriado`** con `categories=("bank", "public")` y evaluar una variable de
      «período especial» para Semana de Turismo y Carnaval.
- [ ] **Decidir el tratamiento del catálogo de zonas** (definirlo sólo con entrenamiento o
      declarar la fuga) y tratar las zonas sin historial como estrato propio.
- [ ] **Fijar las métricas** del protocolo de evaluación en coherencia con un objetivo Poisson
      casi binario: desvianza de Poisson, calibración por estrato de soporte y ordenamiento.
- [ ] **Implementar la línea base** (tasa histórica de la zona × factor de calendario) y
      evaluarla con el protocolo definitivo.
- [ ] Migrar de notebooks a `src/` lo que deba ser reproducible por línea de comandos.
- [ ] Borrador acumulativo del informe en `documentacion/informe/`, al menos hasta resultados
      preliminares (la sección *Metodología — datos* puede apoyarse ya en el diagnóstico).
- [ ] Evidencia de uso del **servidor institucional** y constancia de seguimiento del tutor.

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
