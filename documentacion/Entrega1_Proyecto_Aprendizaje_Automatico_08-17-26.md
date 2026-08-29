# **Presentación y aprobación de la propuesta de proyecto integrador**

## ***Proyecto de Aprendizaje Automático***

Licenciatura en Ingeniería de Datos e Inteligencia Artificial · Proyecto requerido en el tramo del Tecnólogo en Análisis y Gestión de Datos

**Instrucciones generales**

Esta plantilla se completa en conjunto: el/los estudiante(s) redacta(n) la propuesta y aporta(n) evidencias; el/la tutor/a revisa la integración, factibilidad y alcance, acuerda el cronograma y emite su aval. El aprendizaje automático es el eje y debe articularse, según la propuesta, con fundamentos de ciencia de datos, programación, ingeniería y gestión de datos y competencias transversales. La integración debe evidenciarse en el problema, la metodología y los entregables; no basta con enumerar tecnologías o unidades curriculares. Conservar las indicaciones azules como guía, responder en los espacios blancos, justificar lo que no aplique y evitar datos sensibles innecesarios.

# **A. Identificación**

| Carrera | Licenciatura en Ingeniería de Datos e Inteligencia Artificial |
| :---- | :---- |
| **Unidad curricular** | Proyecto de Aprendizaje Automático |
| **Período académico** | 2026 \- Sexto semestre \- Generación 2024 |
| **Modalidad** | ☐ Individual     X Grupal     Cantidad de integrantes: 2  |
| **Organización vinculada** | No aplica (se trabaja con fuentes de datos abiertos) |
| **Repositorio del proyecto** | Plataforma: X GitHub     ☐ GitLab institucional  **URL del repositorio:** https://github.com/victoruria-netizen/proyecto-machine-learning.git |

**Estudiante(s)**

| Nombre completo | Documento | Correo institucional | Firma |
| ----- | ----- | ----- | ----- |
| Victor Samuel Uría Padilla | *54965630* | *victor.uria@estudiantes.utec.edu.uy* | ![][image1] |
| Juan Lucas Pimentel Barreto | 54663222 | juan.pimentel@estudiantes.utec.edu.uy |  |

**Tutoría y referentes**

| Rol | Nombre y grado académico | Afiliación y contacto |
| ----- | ----- | ----- |
| **Tutor/a** | Mag. Matias Leonardo López Pérez | Universidad Tecnológica / Docente encargado: matias.lopez@utec.edu.uy |
| **Cotutor/a o referente (opcional)** | No aplica | No aplica |

# **B. Contenido de la propuesta**

## **1\. Título provisional**

**Cómo completar — estudiante(s):** Proponer un título breve, específico y comprensible que identifique el problema o producto principal y, cuando aporte claridad, el contexto de aplicación. Evitar títulos excesivamente generales, siglas sin desarrollar y afirmar resultados que aún no se obtuvieron.

**Revisión del/de la tutor/a:** Verificar que el título corresponda al alcance real y pueda mantenerse o ajustarse sin cambiar la esencia del proyecto.

| Modelado predictivo de siniestros de tránsito basado en series temporales en Uruguay    |
| :---- |

## **2\. Área temática y dominio de aplicación**

**Cómo completar — estudiante(s):** Indicar la línea temática de aprendizaje automático y el sector o dominio en el que se aplicará. Especificar la naturaleza de la tarea —por ejemplo, clasificación, regresión, agrupamiento, series temporales, procesamiento de texto, visión u otro enfoque— y anticipar qué componentes de ciencia e ingeniería de datos serán necesarios, sin convertir este apartado en una lista de tecnologías.

**Revisión del/de la tutor/a:** Comprobar que el aprendizaje automático constituya el eje del proyecto y que el dominio elegido permita integrar de manera significativa conocimientos del tramo del Tecnólogo.

| Línea temática: aprendizaje automático aplicado a la seguridad vial y la movilidad urbana. Naturaleza de la tarea: A partir de los registros históricos se construyen series temporales agregadas, cuya continuidad, cobertura, granularidad y posibles periodos faltantes serán evaluados durante la preparación de los datos.  Componentes de datos requeridos: integración y limpieza del dataset heterogéneo de Uruguay, agregación temporal a una granularidad común, incorporación de variables exógenas (clima y calendario) y validación mediante esquemas que respeten el orden cronológico de los datos.    |
| :---- |

## **3\. Integración de aprendizajes y aporte al perfil del Tecnólogo**

**Cómo completar — estudiante(s):** Identificar de manera concreta los conocimientos y capacidades desarrollados durante la carrera que se aplicarán en el proyecto. El aprendizaje automático debe constituir el eje central; los fundamentos de ciencia de datos, la programación, la ingeniería y gestión de datos y las competencias transversales deben respaldar, fundamentar o complementar la solución según su alcance. No basta con nombrar unidades curriculares: explicar qué se aplicará y cómo se evidenciará.

**Revisión del/de la tutor/a:** Comprobar que el proyecto mantenga una contribución sustantiva en aprendizaje automático y fundamentos de ciencia de datos, y que integre de manera pertinente otros aprendizajes del tramo. No exigir todas las dimensiones con igual profundidad ni aceptar menciones decorativas sin actividades o entregables verificables.

| Dimensión formativa | Posibles conocimientos y capacidades a integrar | Aplicación y evidencia prevista |
| :---- | :---- | :---- |
| **Fundamentos de Ciencia de Datos** | Matemática, probabilidad y estadística, exploración y análisis de datos, metodología de investigación, programación y pensamiento computacional. | **Aplicación:** análisis de los datos para identificar tendencia, estacionalidad y distribución de la siniestralidad; base estadística para interpretar funciones de pérdida y métricas de error. **Evidencia:** notebook en Python con gráficos y métricas descriptivas que argumenten la presencia de componentes temporales.  |
| **Ingeniería y gestión de datos** | Fuentes y adquisición; modelado, estructuración y almacenamiento; calidad, transformación, trazabilidad, seguridad y protección de datos; arquitectura o infraestructura, cuando corresponda. | **Aplicación:** reutilización y  adaptación del pipeline ETL ya construido para integrar las fuentes, tratar nulos, normalizar taxonomías y generar agregaciones temporales con variables exógenas. **Evidencia:** scripts de extracción y transformación documentados en el repositorio, más un dataset consolidado listo para el modelado.  |
| **Aprendizaje Automático** | Formulación de la tarea; línea base; selección, entrenamiento y comparación de modelos; validación, métricas, solidez, sesgos, explicabilidad y trazabilidad de resultados. | **Aplicación:** formulación como pronóstico de series temporales; definición de una línea base; entrenamiento y comparación de modelos con validación temporal estricta. **Evidencia:** módulo de código reproducible, tabla comparativa de métricas de error pertinentes definidas según las características y distribución de la serie, y análisis de errores y limitaciones del modelo.  |
| **Competencias transversales** | Ética y responsabilidad social, normativa, trabajo en equipo, pensamiento crítico y sistémico, documentación, visualización y comunicación para públicos técnicos y no técnicos. | **Aplicación:** trabajo colaborativo documentado, análisis crítico de sesgos en datos de siniestralidad y comunicación de resultados a públicos técnicos y no técnicos. **Evidencia:** repositorio con README y documentación técnica, informe final y presentación con visualizaciones adaptadas.  |
| **Síntesis:** el eje del proyecto es el Aprendizaje Automático, mientras que la Ingeniería de Datos funciona como base ya construida que deberá adaptarse a las necesidades del modelado. El mayor esfuerzo técnico está en construir un dataset temporal unificado y en entrenar y evaluar modelos predictivos. Los Fundamentos de Ciencia de Datos aportan el sustento estadístico del análisis y la validación, y las Competencias Transversales aseguran la documentación, la gestión del trabajo y la transferencia de resultados al sector de la seguridad vial.  |  |  |

## **4\. Contexto, problema y delimitación**

**Cómo completar — estudiante(s):** Describir la situación actual, las personas u organizaciones afectadas, la evidencia disponible, el proceso o sistema en el que se inserta la solución y las consecuencias del problema. Formular con precisión qué se pretende analizar, predecir, clasificar, estimar, detectar, agrupar u optimizar mediante datos. Delimitar población, período, alcance, actores, flujo de información y restricciones. Incorporar citas cuando se utilicen datos o afirmaciones externas.

**Revisión del/de la tutor/a:** Verificar que exista un problema concreto, abordable con aprendizaje automático y apoyado por una comprensión suficiente del contexto, los datos y el sistema involucrado. Diferenciar el problema real de la mera intención de aplicar un algoritmo.

| Situación. La siniestralidad vial es un problema de salud pública vigente: la OMS estima 1,19 millones de muertes anuales en el mundo, siendo la principal causa de muerte entre los 5 y 29 años (OMS, 2023). En Uruguay, UNASEV reportó 471 fallecidos y 28.342 lesionados en 2025, con tendencia creciente desde 2021\. Problema. Los organismos de gestión de tránsito disponen de pocas herramientas predictivas que permitan anticipar la distribucion temporal y territorial de la siniestralidad. El proyecto busca responder: ¿es posible estimar, a partir de la serie histórica de siniestros y de variables exógenas (clima y calendario), la cantidad esperada de siniestros por zona y período? Punto de partida. Fuentes históricas ya integradas y depuradas en el Proyecto de Ingeniería de Datos: UNASEV (Uruguay), enriquecidas con datos climáticos (Open-Meteo).  Delimitación. El foco de aplicación es Uruguay: es una de las fuentes que el equipo ya tiene integrada, depurada y geolocalizada (coordenadas X/Y y Departamento/Localidad) desde el Proyecto de Ingeniería de Datos, lo que permite construir la visualización georreferenciada sin trabajo adicional de estandarización entre fuentes con taxonomías distintas. Esta elección es además coherente con la misión de UTEC de promover el desarrollo tecnológico, económico y social del país. El período se acotará a los años con datos comparables. Queda fuera de alcance la integración operativa con aplicaciones de terceros (Uber, Waze, Google Maps), que se plantea solo como línea futura.   |
| :---- |

## **5\. Objetivos**

**Cómo completar — estudiante(s):** Redactar un objetivo general que exprese el resultado integrador principal del proyecto y entre tres y cinco objetivos específicos que describan logros verificables. Los objetivos deben cubrir el núcleo de aprendizaje automático y, cuando corresponda, la preparación y gestión de datos, la implementación, la evaluación, la documentación o la comunicación de resultados. Emplear verbos en infinitivo y no confundir objetivos con tareas como “leer”, “investigar” o “hacer reuniones”.

**Revisión del/de la tutor/a:** Revisar que los objetivos sean coherentes con el problema, representen la integración propuesta, puedan verificarse mediante resultados o entregables y sean realizables dentro del cronograma.

| Objetivo general. Desarrollar un modelo de aprendizaje automático para la predicción de siniestros de tránsito a partir de series temporales e integrar sus resultados en una interfaz que permita visualizar las zonas y períodos con mayor cantidad esperada de siniestros.  Objetivos específicos: Adaptar el proceso ETL del Proyecto de Ingeniería de Datos para obtener la granularidad temporal requerida y reutilizar las variables exógenas ya disponibles, evitando nuevas llamadas recurrentes a APIs externas con límite de uso. Evaluar y comparar estrategias de entrenamiento y validación (con y sin variables exógenas, ventana expansiva y ventana deslizante) mediante métricas de error estandarizadas. Seleccionar el modelo con mejor desempeño y solidez, documentando sus limitaciones y sesgos previsibles. Implementar en el dashboard una nueva pestaña con interfaz gráfica intuitiva que permita visualizar las predicciones y la distribución territorial de la cantidad esperada de siniestros sobre un mapa.  |
| :---- |

## **6\. Datos e integración con la ingeniería y gestión de datos**

**Cómo completar — estudiante(s):** Identificar fuentes, responsables o propietarios, modalidad de acceso, tamaño estimado, variables o etiquetas relevantes, período, calidad conocida y formato. Describir, según corresponda, cómo se adquirirán, validarán, limpiarán, integrarán, transformarán, estructurarán, almacenarán y versionarán los datos, y qué elementos podrán reutilizarse del Proyecto de Ingeniería de Datos. Indicar permisos, licencias, confidencialidad, datos personales o sensibles, sesgos previsibles, trazabilidad y medidas de seguridad y protección.

**Revisión del/de la tutor/a:** Confirmar que el acceso sea viable y oportuno, que el volumen y la calidad permitan el proyecto y que exista una estrategia de gestión coherente con el alcance. Verificar la articulación con conocimientos de bases de datos e ingeniería de datos sin imponer una infraestructura innecesaria. No avalar una propuesta que dependa de datos inciertos sin un plan alternativo.

| Fuentes y acceso. UNASEV (Uruguay), datos abiertos gubernamentales en formato CSV/TXT; no se requieren autorizaciones adicionales a las ya obtenidas en el proyecto anterior. Variable objetivo y predictoras. La variable objetivo es la cantidad de siniestros agregada por zona y período. Como predictoras se emplearán variables temporales (día de la semana, mes, feriados) y climáticas (temperatura, precipitación, viento). Calidad y limitaciones relevantes para el modelado. Antes de fijar la granularidad definitiva deberá evaluarse la densidad de observaciones por zona y período, dado el riesgo de series con exceso de períodos en cero (ver punto 10). También deberá verificarse la completitud de las variables climáticas para las zonas y fechas de interés. Uso de la API de clima. Open-Meteo tiene límite de uso, por lo que el enriquecimiento climático se trata como carga histórica puntual ya cacheada (clave única por latitud, longitud, fecha y hora) y no se incorpora como llamada recurrente dentro del flujo de trabajo. Datos ya disponibles. El Proyecto de Ingeniería de Datos dejó un dataset consolidado, depurado y trazable, lo que permite que este proyecto se concentre en la construcción de variables y en el modelado en lugar de en la ingesta y limpieza. Protección. Los datos son públicos y agregados, sin información personal identificable. Las credenciales de acceso se gestionan mediante variables de entorno. Se evitará exponer coordenadas exactas que puedan identificar domicilios particulares en las visualizaciones públicas.   |
| :---- |

## **7\. Orientación metodológica inicial**

**Cómo completar — estudiante(s):** Presentar una idea preliminar de cómo podría abordarse el proyecto. Indicar, en términos generales, cómo se prevé obtener y preparar los datos, qué tipo de análisis o técnicas de aprendizaje automático podrían explorarse y cómo se imagina integrar otros conocimientos de la carrera. Se pueden mencionar herramientas o alternativas posibles, pero no se espera definir todavía algoritmos, arquitecturas, hiperparámetros, métricas detalladas ni un procedimiento definitivo.

**Revisión del/de la tutor/a:** Verificar que la orientación propuesta sea coherente con el problema y realizable, y que mantenga al aprendizaje automático como eje. Ayudar a identificar decisiones que deberán estudiarse durante el proyecto, sin exigir una metodología cerrada antes de comenzar el trabajo.

|  Preparación. Partir de los datos ya integrados y depurados, agregándolos temporalmente (conteos diarios, semanales o mensuales por zona) e incorporando variables exógenas ya disponibles: clima cacheado, calendario y feriados.  Modelado. Explorar dos familias de enfoques y compararlas siempre contra una línea base simple (valor del período anterior o promedio móvil): modelos estadísticos clásicos de series temporales, como SARIMA, y modelos de aprendizaje automático supervisado con variables de rezago, como los de boosting.   Validación. Respetar siempre el orden cronológico de los datos utilizando particiones temporales coherentes con el problema, contrastando esquemas de ventana expansiva y ventana deslizante. Reservar un tramo temporal final como conjunto de prueba, que no sea utilizado para seleccionar modelos, ajustar hiperparámetros ni tomar decisiones metodológicas.  A definir durante el proyecto. El formato de trabajo (base relacional o CSV), el nivel de agregación temporal definitivo y si se entrenará un modelo por zona o un modelo conjunto incorporando la zona, departamento/localidad u otra unidad territorial como variable.   |
| :---- |

## **8\. Justificación, relevancia y aplicación de conocimientos**

**Cómo completar — estudiante(s):** Explicar por qué el problema o la situación elegida resulta pertinente, quiénes podrían beneficiarse y por qué el aprendizaje automático es adecuado para abordarlo. Describir de qué manera el proyecto permitirá aplicar e integrar conocimientos adquiridos durante el tramo del Tecnólogo en Análisis y Gestión de Datos. No se espera demostrar originalidad ni realizar un aporte diferencial respecto del estado del arte.

**Revisión del/de la tutor/a:** Valorar la pertinencia para el perfil del Tecnólogo, la adecuación del componente de aprendizaje automático y la posibilidad real de aplicar e integrar los conocimientos declarados.

| Pertinencia. Quienes gestionan la seguridad vial —UNASEV, intendencias y equipos de planificación de tránsito— necesitan anticipar dónde y cuándo concentrar controles, campañas y señalización. Hoy ese ejercicio se apoya principalmente en estadística descriptiva retrospectiva, por lo que una herramienta predictiva aporta valor directo a la asignación de recursos.  Adecuación del enfoque. La propia UNASEV ya aplicó modelos SARIMA para predecir lesionados mensuales en Uruguay (UNASEV, 2025), lo que confirma que un enfoque de series temporales es apropiado para este dominio y ofrece una referencia metodológica concreta contra la cual contrastar los resultados del equipo.  Aporte formativo. El proyecto capitaliza el trabajo de integración y limpieza del Proyecto de Ingeniería de Datos, profundiza en fundamentos estadísticos y de aprendizaje automático aplicados al pronóstico, y ejercita la comunicación técnica al traducir resultados en una visualización comprensible para actores no técnicos.  |
| :---- |

## **9\. Idea del producto o solución que se pretende desarrollar**

**Cómo completar — estudiante(s):** Describir con claridad qué se pretende alcanzar al finalizar el proyecto: por ejemplo, un análisis, modelo, sistema, herramienta, prototipo o apoyo para la toma de decisiones. Explicar cómo el proyecto continuará y mejorará lo desarrollado en el Proyecto de Ingeniería de Datos y qué nuevas funcionalidades de aprendizaje automático se integrarán en el dashboard o solución existente. Explicar quién lo utilizaría, qué datos recibiría, qué función cumpliría y qué resultado general produciría. Delimitar qué quedaría incluido y qué quedaría fuera. No anticipar métricas, desempeños ni resultados técnicos que todavía no se conocen. Los entregables deben ajustarse a la definición del docente para el curso.

**Revisión del/de la tutor/a:** Comprobar que la idea permita comprender cabalmente qué se quiere construir o lograr, que sea coherente con el problema y que tenga un alcance inicial razonable. No exigir especificaciones técnicas ni resultados propios de una etapa avanzada.

| Qué se construye. Un módulo de modelado predictivo que estime la cantidad esperada de siniestros por zona y período, junto con los artefactos necesarios para ponerlo en inferencia: el modelo entrenado serializado, el pipeline de preprocesamiento y generación de variables, y el mecanismo para obtener las variables exógenas (clima, calendario) al momento de predecir; y una nueva pestaña dentro del dashboard existente que represente esas predicciones sobre un mapa, señalando las zonas y períodos con mayor cantidad pronosticada de siniestros.  Para quién. Un organismo de gestión de tránsito o movilidad, que recibiría como entrada los datos históricos ya integrados y obtendría como salida una visualización de las predicciones con su incertidumbre asociada. Dentro del alcance. El modelo predictivo, sus artefactos de inferencia, su evaluación y su incorporación visual como una nueva pestaña del dashboard existente en Streamlit, usando una librería de mapas compatible (por ejemplo folium o pydeck).  Fuera del alcance. La integración operativa con aplicaciones de terceros (Uber, Waze, Google Maps). No es viable en el plazo disponible: esas plataformas no ofrecen mecanismos públicos para que una aplicación externa modifique lo que ven sus propios usuarios, y sus programas de colaboración están reservados a organismos públicos reconocidos. Se mantiene como posible línea de trabajo futura. No se anticipan métricas de desempeño; se documentarán una vez obtenidas durante el desarrollo.      |
| :---- |

## **10\. Factibilidad, recursos, restricciones y riesgos**

**Cómo completar — estudiante(s):** Identificar recursos humanos, datos, infraestructura, almacenamiento, hardware, software, servicios, presupuesto y autorizaciones necesarios. Señalar restricciones y riesgos técnicos, metodológicos, de integración, acceso o calidad de datos, seguridad, privacidad, tiempo o dependencia externa, indicando probabilidad, impacto y acciones de mitigación. Incluir un plan alternativo para los riesgos críticos. Para el servidor institucional, indicar si el acceso fue verificado y describir brevemente el uso previsto.

**Revisión del/de la tutor/a:** Evaluar si los recursos están disponibles, si el alcance integrado es razonable y si las mitigaciones son suficientes. Evitar que la incorporación de componentes complementarios vuelva inviable el proyecto y proponer ajustes antes de emitir el aval.

|  Servidor institucional Acceso verificado: X Sí     ☐ No Uso previsto: Preparación de datos, entrenamiento y evaluación de modelos, generación de artefactos y conservación de logs de ejecuciones relevantes. |
| :---- |

| Riesgo | Probabilidad | Impacto | Mitigación | Plan alternativo |
| ----- | :---: | :---: | ----- | ----- |
| Definición inadecuada de variable objetivo o granularidad | **Media** | **Alta** | Realizar análisis preliminar de densidad y cobertura antes de cerrar la unidad temporal y territorial. | Usar una agregación temporal o territorial mayor. |
| Escasez de observaciones o exceso de períodos con cero siniestros | **Media** | **Alta** | Comparar granularidades y seleccionar una que produzca una serie suficientemente informativa. | Reducir resolución espacial o aumentar ventana temporal. |
| Variables meteorológicas incompletas para el nuevo esquema temporal | **Media** | **Media/Alta** | Definir una serie meteorológica reproducible por zona y período y documentar disponibilidad al momento de predicción. | Comparar un modelo sin clima como alternativa válida. |
| Carga computacional o esperas en el servidor institucional | **Media** | **Media** | Planificar ejecuciones, conservar logs, usar recursos de forma controlada y evitar entrenamientos innecesarios. | Reducir búsqueda de hiperparámetros o complejidad de modelos. |
| Desviación del cronograma y acumulación de documentación al final | **Media** | **Alta** | Actualizar informe, README, registro de experimentos y registro de IA en cada hito. | Reducir alcance del prototipo sin reducir la validez metodológica del modelo. |
| Disponibilidad de variables meteorológicas al momento de realizar la predicción | **Media** | **Alta** | Verificar que variables meteorológicas estarán efectivamente disponibles para el horizonte de predicción seleccionado y diseñar el pipeline para utilizar únicamente información disponible al momento de generar pronóstico, evitando fugas de información. | Entrenar y evaluar una variante del modelo sin variables meteorológicas, utilizando únicamente información histórica de siniestros y variables de calendario como día de semana, feriados y días festivos. |

## **11\. Posible difusión o transferencia (opcional)**

**Cómo completar — estudiante(s):** Indicar, solo si corresponde, si el proyecto podría presentarse en un evento o instancia académica, profesional o institucional sugerida por la carrera o la unidad curricular. En esta etapa el nombre o formato puede ser provisional. Explicar brevemente qué aspecto del proyecto podría compartirse. La participación no se considera obligatoria.

**Revisión del/de la tutor/a:** Orientar al equipo sobre la posible instancia de presentación y comprobar que la idea sea compatible con el alcance y los tiempos del proyecto. La definición final podrá realizarse más adelante.

| No aplica |
| :---- |

## **12\. Cronograma de trabajo**

**Cómo completar — estudiante(s):** Ajustar el cronograma con el/la tutor/a. Modificar, agregar o eliminar las filas según la propuesta y sombrear las celdas correspondientes al período previsto para cada tema o actividad. El cronograma abarca agosto, septiembre, octubre y noviembre; las fases y su distribución son orientativas y deberán adecuarse al proyecto.

**Revisión del/de la tutor/a:** Comprobar que la secuencia general sea razonable para la carga académica disponible y que reserve tiempo para la documentación, las correcciones y la presentación o defensa. En esta etapa se espera una planificación inicial, que podrá ajustarse durante el desarrollo.

## 

| Tema o actividad | Agosto | Septiembre | Octubre | Noviembre |
| ----- | :---: | :---: | :---: | :---: |
| **E1: Presentación y aprobación de la propuesta; repositorio, servidor y registro de IA** | **17/08-24/08** |   |   |   |
| Revisión de datos y definición de granularidad temporal y territorial | 17/08-31/08 | 01/09-06/09 |   |   |
| Construcción del dataset temporal y preparación de variables exógenas | 24/08-31/08 | 01/09-13/09 |   |   |
| Línea base y diseño del protocolo de evaluación con conjunto de prueba reservado |   | 01/09-20/09 |   |   |
| **E2: Datos, metodología y línea base \+ primera presentación intermedia** |   | **20/09-21/09** |   |   |
| Experimentación y comparación de modelos |   | 21/09-30/09 | 01/10-18/10 |   |
| Selección del modelo y evaluación final: errores, robustez, limitaciones y sesgos |   |   | 12/10-25/10 |   |
| **E3: Experimentación avanzada y solución seleccionada \+ demostración** |   |   | **25/10-26/10** |   |
| Integración del modelo al dashboard, artefactos de inferencia y pruebas del pipeline |   |   | 15/10-31/10 | 01/11-08/11 |
| Documentación, reproducibilidad y correcciones: informe, README, experimentos, IA y evidencias del servidor | 17/08-31/08 | Durante el mes | Durante el mes | 01/11-15/11 |
| **E4: Entrega definitiva al tribunal** |   |   |   | **15/11** |
| Preparación de defensa final |   |   |   | Fecha a definir |

## 

## 

## **13\. Referencias iniciales**

**Cómo completar — estudiante(s):** Incluir las fuentes principales utilizadas para formular el problema, fundamentar las decisiones y diseñar la metodología integrada: artículos, libros, documentación técnica, normativa, estándares y descripciones de datos o sistemas. Usar un único estilo de citación de manera consistente y verificar enlaces, autores, año y título.

**Revisión del/de la tutor/a:** Comprobar que las referencias sean pertinentes y suficientes para fundamentar los componentes de ciencia de datos, ingeniería o gestión de datos y aprendizaje automático que efectivamente formen parte de la propuesta. Preferir fuentes académicas, institucionales o documentación técnica oficial.

| Deretić, N., Stanimirović, D., Awadh, M. A., Vujanović, N., & Djukić, A. (2022). SARIMA modelling approach for forecasting of traffic accidents. *Sustainability*, 14(8), 4403\. [https://doi.org/10.3390/su14084403](https://doi.org/10.3390/su14084403) Géron, A. (2023). *Aprende Machine Learning con Scikit-Learn, Keras y TensorFlow* (3.ª ed.). Marcombo. Hyndman, R. J., & Athanasopoulos, G. (2021). *Forecasting: Principles and practice* (3rd ed.). OTexts. [https://otexts.com/fpp3/](https://otexts.com/fpp3/) Hyndman, R. J., & Koehler, A. B. (2006). Another look at measures of forecast accuracy. *International Journal of Forecasting*, 22(4), 679–688. [https://doi.org/10.1016/j.ijforecast.2006.03.001](https://doi.org/10.1016/j.ijforecast.2006.03.001) Open-Meteo. Historical Weather API. [https://open-meteo.com](https://open-meteo.com) Unidad Nacional de Seguridad Vial (UNASEV). (2025a). *Informe Anual de Siniestralidad Vial 2025*. [https://www.gub.uy/unidad-nacional-seguridad-vial/datos-y-estadisticas/estadisticas/2025-informe-anual-siniestralidad-vial](https://www.gub.uy/unidad-nacional-seguridad-vial/datos-y-estadisticas/estadisticas/2025-informe-anual-siniestralidad-vial) Unidad Nacional de Seguridad Vial (UNASEV). (2025b). *Modelos SARIMA para la predicción de lesionados en siniestros de tránsito en Uruguay*. [https://www.gub.uy/unidad-nacional-seguridad-vial/datos-y-estadisticas/estadisticas/modelos-sarima-para-prediccion-lesionados-siniestros-transito](https://www.gub.uy/unidad-nacional-seguridad-vial/datos-y-estadisticas/estadisticas/modelos-sarima-para-prediccion-lesionados-siniestros-transito) World Health Organization. (2023). *Global status report on road safety 2023*. [https://www.who.int/publications/i/item/9789240086517](https://www.who.int/publications/i/item/9789240086517)      |
| :---- |

# **C. Carta aval y aceptación de tutoría**

**Finalidad de esta sección**

Debe ser completada después de que el/la tutor/a haya revisado la propuesta y acordado con el equipo el alcance, la integración de aprendizajes, la metodología inicial y el cronograma. El aval confirma la aceptación de la tutoría y la viabilidad preliminar; no sustituye las evaluaciones posteriores del proceso, del documento escrito ni de la defensa.

**El/La docente tutor/a declara que:**

* ha revisado la propuesta y acepta orientar el proyecto identificado en este formulario;  
* considera que el aprendizaje automático constituye el eje técnico y que el proyecto aporta al perfil del Tecnólogo en Análisis y Gestión de Datos;  
* ha verificado que la integración de fundamentos de ciencia de datos, programación, ingeniería o gestión de datos y competencias transversales es pertinente al problema y no meramente declarativa;  
* ha verificado preliminarmente la disponibilidad de datos, recursos, autorizaciones y tiempo necesarios;  
* ha acordado con el equipo un cronograma y una modalidad de seguimiento;  
* orientará el cumplimiento de los aspectos metodológicos, éticos, formales y de autoría aplicables; y  
* comunicará oportunamente cualquier situación que comprometa la viabilidad o continuidad del proyecto.

## **Recomendación del/de la tutor/a**

X Recomienda aprobar la propuesta     ☐ Recomienda aprobar con observaciones     ☐ Solicita reformulación

| Se recomienda aprobar la propuesta. El proyecto presenta un alcance viable y coherente con los objetivos del Proyecto de Aprendizaje Automático, manteniendo al aprendizaje automático como eje central y dando continuidad al Proyecto de Ingeniería de Datos desarrollado previamente. Durante el desarrollo deberán definirse y justificarse, a partir del análisis de los datos, la granularidad temporal y territorial definitiva, las métricas de evaluación y la estrategia final de modelado. Asimismo, deberá mantenerse la trazabilidad, reproducibilidad y documentación de las decisiones metodológicas y técnicas adoptadas.      |
| :---- |

## **Compromiso del/de los estudiante(s)**

El/Los estudiante(s) declara(n) que la propuesta es de elaboración propia; que aplicará(n) de manera fundada los conocimientos y capacidades indicados en la matriz de integración; que utilizará(n) datos, fuentes, software y herramientas respetando las normas institucionales, legales y éticas; que cumplirá(n) el plan de trabajo acordado; y que informará(n) al/a la tutor/a cualquier cambio relevante de alcance, datos, metodología, integración o cronograma.

Lugar y fecha: Rivera, 17 de agosto de 2026

| \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ Tutor/a | \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ Estudiante / representante del equipo |
| :---: | :---: |
| \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ **Cotutor/a (si corresponde)** | \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ **Estudiante adicional (si corresponde)** |

# **D. Decisión sobre la propuesta y la tutoría**

**Uso institucional**

Esta sección debe ser completada por el órgano o responsable que la carrera determine para aprobar el tema y la tutoría. La decisión debe considerar la centralidad del aprendizaje automático, la contribución al perfil del Tecnólogo, la integración pertinente de aprendizajes, el alcance y la viabilidad. Registrar de forma clara las observaciones y condiciones que el equipo deberá atender.

| Fecha de recepción | *\[Completar\]* |
| :---- | :---- |
| **Órgano / responsable** | *\[Comité Académico u órgano definido por la carrera\]* |
| **Decisión** | ☐ Aprobada     ☐ Aprobada con observaciones     ☐ Reformulación requerida     ☐ No aprobada |
| **Tutoría** | ☐ Aprobada     ☐ Requiere modificación |
| **Integración formativa** | ☐ Adecuada     ☐ Requiere ajuste |
| **Plazo para subsanar** | *\[Completar, si corresponde\]* |
| **Fecha de notificación** | *\[Completar\]* |

## **Fundamentación u observaciones**

|               |
| :---- |

## **Registro de firmas**

| \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ Nombre, cargo y firma | \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ Nombre, cargo y firma |
| :---: | :---: |
|  \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ **Nombre, cargo y firma** |  \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ **Sello / constancia institucional** |

## 

| \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ Nombre, cargo y firma |
| ----- |

Recepción por Secretaría: \_\_\_\_/\_\_\_\_/\_\_\_\_\_\_\_\_    Responsable: \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_    Registro/expediente: \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

[image1]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEsAAABACAYAAABSiYopAAAA6klEQVR4Xu3YMQ6CMBTGcQZj4shjZZHH5ClcXDyGq6uOJo5ew90beAhXz2C8gwaDUl4KCImJSf+/hLT96MKXdiGKAAAAAAAAAAD/QPRhI/j0KarP3qBR1Bdi3X7mFIZ2ku9t1CnYU2U/3K7Rwi1LspXzpswoE/iFb65WrEcbAR0ku9ioRvKTjcIlei/H7uuIFjJd2AgYSHT3GpP8wNX0SdNJtZiNq7lDdGOjMBUnKMnXNq7hlDmaynjnTe+D1FbKkF85CJHv9BSKXPRqY4iey3KqJ9Gb3Qav+cgm8ImzpY0AAAAAAAAAAEB4nlDeLVLlBUmLAAAAAElFTkSuQmCC>