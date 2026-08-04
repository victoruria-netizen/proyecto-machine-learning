# Predicción de Siniestros Viales — Proyecto de Aprendizaje Automático (PAA)

**UTEC · LIDIA · Proyecto de Aprendizaje Automático 2026**

Este repositorio corresponde al Proyecto de Aprendizaje Automático (PAA), continuación
del Proyecto de Ingeniería de Datos (PID) del mismo equipo. Su objetivo es formular y
resolver un problema de aprendizaje automático relacionado con la **predicción de
siniestros viales**, reutilizando los datos y activos útiles del proyecto anterior.

## Proyecto de origen (PID)

- **Repositorio PID:** _(completar con el enlace al repositorio del PID)_
- **Componentes reutilizados:** _(describir qué datos, código o artefactos provienen del PID)_
- **Modificaciones en el PAA:** _(describir qué se modificó o desarrolló específicamente en el PAA)_

## Estructura del repositorio

```
README.md              Este archivo: propósito, requisitos, datos, ejecución y resultados
data/                  Datos (o mecanismo de acceso; no se versionan datos restringidos)
notebooks/             Notebooks de exploración y análisis
src/                   Código fuente de la solución (preprocesamiento, modelado, inferencia)
models/                Modelos entrenados y artefactos necesarios para la inferencia
experiments/           Registro de experimentos, configuraciones y resultados
app/                   Prototipo / dashboard integrado (TRL 5)
documentacion/         Documentación del proyecto
    registro_uso_IA.md Registro incremental del uso de IA generativa
tests/                 Pruebas del pipeline de inferencia
requirements.txt       Dependencias del entorno
```

## Requisitos e instalación

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate

pip install -r requirements.txt
```

## Datos

_(Describir las fuentes de datos, su disponibilidad y, cuando no puedan versionarse, el
mecanismo reproducible para obtenerlos y dónde ubicarlos.)_

## Ejecución

_(Instrucciones para reproducir el procesamiento, entrenar/cargar el modelo y ejecutar el
prototipo sin necesidad de reentrenar.)_

## Resultados esperados

_(Resumen de métricas, línea base y resultados principales; se completará de forma
acumulativa según avancen los entregables.)_

## Equipo y tutoría

- **Integrantes:** _(completar)_
- **Tutor/a:** _(completar)_

## Uso de inteligencia artificial

El uso de herramientas de IA generativa se registra en
[`documentacion/registro_uso_IA.md`](documentacion/registro_uso_IA.md).
