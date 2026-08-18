# Predicción de Siniestros Viales — Proyecto de Aprendizaje Automático (PAA)

**UTEC · LIDIA · Proyecto de Aprendizaje Automático 2026**

Este repositorio corresponde al Proyecto de Aprendizaje Automático (PAA), continuación
del Proyecto de Ingeniería de Datos (PID) del mismo equipo. Su objetivo es formular y
resolver un problema de aprendizaje automático relacionado con la **predicción de
siniestros viales**, reutilizando los datos y activos útiles del proyecto anterior.

El problema se aborda como un **pronóstico de series temporales**: estimar la cantidad
esperada de siniestros por zona y período a partir de la serie histórica de siniestros de
Uruguay (UNASEV) y de variables exógenas de clima y calendario. Los resultados se
integran en una nueva pestaña del dashboard existente, que representa sobre un mapa las
zonas y períodos con mayor cantidad pronosticada de siniestros.

## Proyecto de origen (PID)

- **Repositorio PID:** https://git.utec.edu.uy/juan.pimentel/siniestros-viales-grp4
- **Componentes reutilizados:** Script de extracción, transformación, carga y dataset unificado de siniestros en Uruguay (UNASEV), ya depurado, geolocalizado (coordenadas X/Y y Departamento/Localidad) y trazable; enriquecimiento climático histórico de Open-Meteo previamente cacheado; y el dashboard en Streamlit sobre el que se integrará la nueva funcionalidad.
- **Modificaciones en el PAA:**
  - Adaptación del proceso ETL para producir series temporales agregadas por zona y período, con la granularidad temporal y territorial que se defina tras el análisis de densidad y cobertura de los datos.
  - Construcción de variables predictoras: rezagos y agregados móviles de la serie, variables de calendario (día de la semana, mes, feriados) y variables climáticas (temperatura, precipitación, viento) tomadas de la caché histórica, sin llamadas recurrentes a la API externa.
  - Incorporación de un módulo de modelado, evaluación con validación temporal y artefactos de inferencia (modelo serializado y pipeline de preprocesamiento).
  - Ampliación del dashboard con una nueva pestaña de visualización georreferenciada de las predicciones.

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

Las credenciales y rutas sensibles se gestionan mediante variables de entorno. Copiar
`.env.example` a `.env` y completar los valores antes de ejecutar el pipeline.

## Datos

**Fuentes**

| Fuente | Contenido | Acceso | Formato |
| ----- | ----- | ----- | ----- |
| UNASEV (Unidad Nacional de Seguridad Vial, Uruguay) | Registros históricos de siniestros de tránsito, con fecha, hora, ubicación (coordenadas X/Y, departamento y localidad) y características del evento | Datos abiertos gubernamentales; no requiere autorizaciones adicionales a las obtenidas en el PID | CSV / TXT |
| Open-Meteo — Historical Weather API | Variables meteorológicas históricas (temperatura, precipitación, viento) por ubicación y fecha/hora | API pública con límite de uso; se emplea como carga histórica puntual ya cacheada, con clave única por latitud, longitud, fecha y hora | JSON → CSV cacheado |
| Calendario de feriados de Uruguay | Feriados y días no laborables utilizados como variable exógena | Fuente pública | CSV |

**Variable objetivo y predictoras.** La variable objetivo es la cantidad de siniestros
agregada por zona y período. Como predictoras se emplean variables temporales (día de la
semana, mes, feriados), rezagos de la propia serie y variables climáticas.

**Disponibilidad y versionado.** Los datos de siniestros ya integrados y depurados
provienen del PID. Los archivos de datos no se versionan en este repositorio: `data/`
contiene únicamente la estructura de carpetas y la caché climática se obtiene o se
restaura mediante el script de ingesta. Para reproducir el conjunto de trabajo, ubicar los
archivos fuente en `data/raw/` y ejecutar el pipeline descrito en la sección siguiente,
que deja el dataset consolidado en `data/processed/`.

**Calidad y limitaciones conocidas.** Antes de fijar la granularidad definitiva se evalúa
la densidad de observaciones por zona y período, dado el riesgo de series con exceso de
períodos en cero, y se verifica la completitud de las variables climáticas para las zonas
y fechas de interés. El pipeline se diseña para utilizar únicamente información disponible
al momento de generar el pronóstico, evitando fugas de información.

**Protección.** Los datos son públicos y agregados, sin información personal
identificable. Las credenciales de acceso se gestionan mediante variables de entorno y no
se versionan. Se evita exponer coordenadas exactas que puedan identificar domicilios
particulares en las visualizaciones públicas.

## Ejecución

El flujo completo se ejecuta en cuatro etapas. Los scripts leen su configuración
(granularidad temporal y territorial, período, rutas) desde `src/config.py`.

```bash
# 1. Ingesta y consolidación: construye el dataset unificado a partir de las fuentes
python -m src.data.ingesta

# 2. Construcción del dataset temporal: agregación por zona y período,
#    incorporación de variables exógenas (clima cacheado, calendario, feriados) y rezagos
python -m src.features.construir_dataset

# 3. Entrenamiento y evaluación: línea base y modelos candidatos con validación temporal.
#    Guarda métricas y configuraciones en experiments/ y los artefactos en models/
python -m src.models.entrenar

# 4. Inferencia con el modelo ya entrenado (no requiere reentrenar)
python -m src.models.predecir --horizonte 4
```

Prototipo / dashboard:

```bash
streamlit run app/app.py
```

El dashboard carga el modelo serializado y el pipeline de preprocesamiento desde
`models/`, por lo que puede ejecutarse sin repetir el entrenamiento. Los notebooks de
exploración y análisis descriptivo se encuentran en `notebooks/`.

Pruebas del pipeline de inferencia:

```bash
pytest tests/
```

## Resultados esperados

Los resultados se completan de forma acumulativa según avancen los entregables. El
protocolo de evaluación previsto es el siguiente:

- **Línea base.** Modelo ingenuo de referencia (valor del período anterior o promedio
  móvil), contra el cual se contrasta todo modelo posterior.
- **Modelos candidatos.** Dos familias de enfoques: modelos estadísticos clásicos de
  series temporales (por ejemplo SARIMA) y modelos de aprendizaje automático supervisado
  con variables de rezago (por ejemplo modelos de boosting).
- **Estrategias comparadas.** Con y sin variables exógenas, y esquemas de ventana
  expansiva frente a ventana deslizante.
- **Validación.** Particiones que respetan el orden cronológico de los datos, con un tramo
  temporal final reservado como conjunto de prueba, no utilizado para seleccionar modelos,
  ajustar hiperparámetros ni tomar decisiones metodológicas.
- **Métricas.** Métricas de error estandarizadas para pronóstico, definidas según las
  características y la distribución de la serie una vez completado el análisis
  exploratorio.

Todavía no se anticipan métricas ni desempeños: se documentarán aquí una vez obtenidos,
junto con el análisis de errores, la solidez del modelo y sus limitaciones y sesgos
previsibles. El registro detallado de configuraciones y resultados se mantiene en
`experiments/`.

## Equipo y tutoría

- **Integrantes:**
  - Victor Samuel Uría Padilla — victor.uria@estudiantes.utec.edu.uy
  - Juan Lucas Pimentel Barreto — juan.pimentel@estudiantes.utec.edu.uy
- **Tutor:** Mag. Matias Leonardo López Pérez — Universidad Tecnológica (UTEC), docente encargado — matias.lopez@utec.edu.uy

## Uso de inteligencia artificial

El uso de herramientas de IA generativa se registra en
[`documentacion/registro_uso_IA.md`](documentacion/registro_uso_IA.md).

## Referencias

- Deretić, N., Stanimirović, D., Awadh, M. A., Vujanović, N., & Djukić, A. (2022). *SARIMA modelling approach for forecasting of traffic accidents*. Sustainability, 14(8), 4403. https://doi.org/10.3390/su14084403
- Géron, A. (2023). *Aprende Machine Learning con Scikit-Learn, Keras y TensorFlow* (3.ª ed.). Marcombo.
- Hyndman, R. J., & Athanasopoulos, G. (2021). *Forecasting: Principles and practice* (3rd ed.). OTexts. https://otexts.com/fpp3/
- Hyndman, R. J., & Koehler, A. B. (2006). *Another look at measures of forecast accuracy*. International Journal of Forecasting, 22(4), 679–688. https://doi.org/10.1016/j.ijforecast.2006.03.001
- Open-Meteo. *Historical Weather API*. https://open-meteo.com
- UNASEV. (2025). *Informe Anual de Siniestralidad Vial 2025*. https://www.gub.uy/unidad-nacional-seguridad-vial/datos-y-estadisticas/estadisticas/2025-informe-anual-siniestralidad-vial
- UNASEV. (2025). *Modelos SARIMA para la predicción de lesionados en siniestros de tránsito en Uruguay*. https://www.gub.uy/unidad-nacional-seguridad-vial/datos-y-estadisticas/estadisticas/modelos-sarima-para-prediccion-lesionados-siniestros-transito
- World Health Organization. (2023). *Global status report on road safety 2023*. https://www.who.int/publications/i/item/9789240086517
