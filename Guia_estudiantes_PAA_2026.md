

<!-- Start of picture text -->
UTECHeo(<Ioo<><br>Universided Teenolégica<br><!-- End of picture text -->



**UTEC  ·  LIDIA  ·  Proyecto de Aprendizaje Automático** 



# **Índice** 

|**Introducción**.................................................................................................................................3|
|---|
|**1. Propósito y alcance del proyecto**................................................................................................4|
|**2. Organización y responsabilidades**...............................................................................................5|
|**3. Calendario general**.....................................................................................................................7|
|**4. Reglas comunes de trabajo**........................................................................................................7|
|**5. Entregables**.............................................................................................................................10|
|5.1 Entregable 1. Propuesta inicial..............................................................................................10|
|5.2 Entregable 2. Datos, metodología y línea base.........................................................................11|
|5.3 Entregable 3. Experimentación avanzada y solución seleccionada...............................................13|
|5.4 Entregable 4. Entrega definitiva al tribunal...............................................................................15|
|**6. Orientaciones técnicas del ciclo de aprendizaje automático**.........................................................16|
|**7. Informe final**............................................................................................................................17|
|**8. Sistema de evaluación**.............................................................................................................17|
|**9. Integridad académica y plagio**...................................................................................................19|
|**10. Lista de comprobación final**....................................................................................................19|
|**11. Referencias**...........................................................................................................................21|



Docente: Pablo D. Cuña | Guía para estudiantes  |  Página 2 de 21 

Bs<> 



<!-- Start of picture text -->
UTEC<br>Universidad Tecnolégico<br><!-- End of picture text -->



**UTEC  ·  LIDIA  ·  Proyecto de Aprendizaje Automático** 



# **1. Propósito y alcance del proyecto** 

El PAA integra los saberes desarrollados durante el tramo de Tecnólogo. Para abordar el proyecto, los estudiantes deberán articular conocimientos de matemática y estadística, programación, bases de datos, ingeniería y gestión de datos, calidad y preparación de datos, visualización y comunicación de resultados, gestión de proyectos, trabajo colaborativo, ética y responsabilidad profesional, además de los aprendizajes específicos de Aprendizaje Automático I y II. 

La integración de estos saberes se concretará mediante la formulación de un problema, la comprensión y preparación de los datos, el diseño de una evaluación válida, la experimentación, la selección de una solución, la interpretación crítica, la documentación, la reproducibilidad y la integración funcional del modelo en una solución demostrable. 

## **1.1 Continuidad con el proyecto anterior** 

El PAA continúa el Proyecto de Ingeniería de Datos (PID). El equipo y el tema se mantienen; no se comienza un proyecto independiente. La solución deberá reutilizar los datos y los activos útiles del trabajo anterior, reorganizándolos cuando sea necesario para esta nueva etapa. En esta continuidad, el equipo deberá: 

- Revisar la calidad y la adecuación de los datos heredados para el problema de aprendizaje automático. 

- Corregir o ampliar la obtención de datos cuando sea necesario y esté debidamente justificado. 

- Agregar observaciones, variables, etiquetas o fuentes externas solo cuando aporten valor y sean viables. 

- Integrar el modelo y las nuevas funcionalidades en la solución o _dashboard_ existente, 

   - mejorándolo de manera significativa. 

- Identificar qué componentes provienen del PID y explicar qué se modificó o desarrolló específicamente en el PAA. 

**Ajustes sustantivos:** Un cambio de tema, equipo o problema no es una alternativa ordinaria. <mark>Solo podrá realizarse cuando exista una razón de viabilidad y la autorización académica</mark> correspondiente. 

## **1.2 Nivel esperado** 

El proyecto corresponde al nivel de Tecnólogo. Se espera autonomía para investigar, seleccionar, aplicar, comparar e integrar técnicas existentes de forma correcta. No se exige desarrollar algoritmos nuevos, realizar investigación científica inédita ni construir una plataforma productiva de nivel empresarial. En particular: 

Docente: Pablo D. Cuña | Guía para estudiantes  |  Página 4 de 21 

**UTEC  ·  LIDIA  ·  Proyecto de Aprendizaje Automático** 



- La profundidad, la validez y la justificación pesan más que la cantidad de modelos o técnicas. 

- No se valorará la aplicación de procedimientos que no sean pertinentes para el problema o los datos. 

- Las técnicas avanzadas pueden fortalecer el trabajo, pero no sustituyen una metodología básica correcta. 

- La solución deberá ser comprensible para sus destinatarios y sus resultados deberán interpretarse en relación con el problema, los datos y las decisiones que podrían apoyarse en ellos. 

## **1.3 Explicabilidad e interpretación** 

El equipo deberá explicar el comportamiento del modelo a partir de evidencias obtenidas durante su desarrollo y evaluación. Según el tipo de problema y de modelo, podrá apoyarse en la importancia de las variables, coeficientes o reglas interpretables, gráficos, métricas, matrices de confusión, ejemplos de aciertos y errores, comparación del desempeño entre clases o condiciones y otros resultados disponibles. 

A partir de estas evidencias, deberá identificar qué variables o patrones parecen relevantes, en qué situaciones el modelo funciona mejor o peor y cuáles son sus principales limitaciones. Los gráficos, métricas o valores incluidos deberán interpretarse y relacionarse con el problema. 

# **2. Organización y responsabilidades** 

## **2.1 Equipo** 

El trabajo se realiza con el mismo equipo del PID. Todos los integrantes son responsables de comprender la solución completa, aunque distribuyan tareas. Las contribuciones deberán ser identificables y cada integrante deberá poder explicar las decisiones, el código, los resultados y las limitaciones del proyecto. 

## **2.2 Tutoría** 

La tutoría se organizará de acuerdo con las siguientes pautas: 

- Cada equipo seleccionará un tutor de la lista comunicada por la carrera. 

- Cada tutor podrá acompañar hasta dos equipos. 

- La modalidad y frecuencia de las reuniones se acordarán entre el equipo y el tutor. 

- La aceptación inicial se documentará en la propuesta. 

- En los entregables posteriores se incorporará una constancia breve de que el tutor realizó seguimiento y conoce el contenido presentado. 

- El tutor orienta y formula observaciones; su seguimiento no equivale a aprobar todas las decisiones ni garantiza la aprobación final. 

Docente: Pablo D. Cuña | Guía para estudiantes  |  Página 5 de 21 

**UTEC  ·  LIDIA  ·  Proyecto de Aprendizaje Automático** 



## **2.3 Evaluación** 

La evaluación considera el proceso de desarrollo, la calidad del informe y de la solución técnica, la defensa final y la demostración individual de los aprendizajes esperados. Las responsabilidades y ponderaciones generales son las siguientes: 

|**Componente**|**Incidencia**|**Responsable**|
|---|---|---|
|Proceso desarrollado en los cuatro entregables|30 %|Docente de Proyecto|
|Informe final y solución técnica|50 %|Tribunal|
|Defensa final|20 %|Tribunal|
|Competencias C3.1, C3.2 y C3.3|Acreditación<br>individual|Docente de Proyecto|



Docente: Pablo D. Cuña | Guía para estudiantes  |  Página 6 de 21 

**UTEC  ·  LIDIA  ·  Proyecto de Aprendizaje Automático** 



# **3. Calendario general** 

El curso se organizará de acuerdo con los siguientes hitos: 

|**Fecha**|**Actividad**|**Resultado esperado**|
|---|---|---|
|3 de agosto|Presentación inicial del curso|Comprensión del propósito, organización y<br>requisitos|
|10 de agosto|Sesión sobre competencias|Comprensión de C3.1, C3.2 y C3.3 y de sus<br>evidencias|
|**17 de agosto**|**Entregable 1**|**Propuesta inicial enviada al Comité Académico**|
|24 de agosto|Reformulación, si corresponde|Propuesta ajustada y aprobable|
|**20 de septiembre**|**Entregable 2**|**Datos, metodología y línea base**|
|21 de septiembre|Primera presentación intermedia|Explicación del avance y retroalimentación|
|**25 de octubre**|**Entregable 3**|**Experimentación avanzada y solución**<br>**seleccionada**|
|26 de octubre|Segunda presentación<br>intermedia|Demostración del prototipo y retroalimentación|
|**15 de noviembre**|**Entregable 4**|**Entrega definitiva y accesible al tribunal**|
|A definir|Defensa final|Presentación y respuestas ante el tribunal|



Las presentaciones intermedias son obligatorias y deberán mostrar con claridad el avance alcanzado, las decisiones tomadas, las dificultades encontradas y los pasos siguientes. Todos los integrantes deberán participar y estar preparados para responder preguntas sobre el trabajo completo. 

# **4. Reglas comunes de trabajo** 

## **4.1 Repositorio** 

Cada equipo deberá crear un repositorio nuevo y exclusivo para el PAA en GitHub (recomendado) o en el GitLab institucional. El repositorio del PID permanecerá como antecedente, pero la solución del PAA deberá poder comprenderse y reproducirse sin combinar manualmente ambos repositorios. La ruta o enlace al nuevo repositorio deberá incorporarse obligatoriamente en el Entregable 1. 

Durante todo el proyecto, el equipo deberá: 

- Usar cuentas personales, sin cuentas compartidas, y mantener contribuciones identificables. 

- Dar acceso al docente y al tutor desde el comienzo; dar acceso al tribunal en la entrega final. 

Docente: Pablo D. Cuña | Guía para estudiantes  |  Página 7 de 21 



**UTEC  ·  LIDIA  ·  Proyecto de Aprendizaje Automático** 

- Verificar los permisos y enlaces antes de cada entrega. 

- Indicar en el README el proyecto de origen y los componentes reutilizados o modificados. 

- Mantener una versión identificable de cada hito mediante etiqueta, versión, rama estable o mecanismo equivalente. 

- Incluir el código, la documentación, los archivos de entorno, los resultados y los artefactos necesarios para reproducir y demostrar la solución. 

### **Estructura recomendada** 

La organización podrá adaptarse a las particularidades del proyecto, pero se recomienda utilizar una estructura semejante a la siguiente: 

```
README.md
data/
notebooks/
src/
models/
experiments/
app/
documentacion/
    registro_uso_IA.md
tests/
requirements.txt  o  environment.yml
```

No deberán versionarse datos restringidos, credenciales, claves ni archivos de gran tamaño cuando exista un mecanismo más adecuado de almacenamiento. En esos casos, el README deberá indicar cómo obtener los datos o artefactos y cómo ubicarlos para ejecutar la solución. 

## **4.2 Servidor institucional** 

El uso del servidor institucional es obligatorio, aunque no exclusivo. En el Entregable 1, el equipo deberá confirmar que puede autenticarse y realizar una prueba básica de funcionamiento. Además, deberá indicar qué tareas prevé ejecutar allí, por ejemplo: preparación de datos, entrenamiento, ajuste de hiperparámetros, generación de artefactos o ejecución del prototipo. 

A partir del Entregable 2, cada entrega técnica deberá incluir al menos una ejecución relevante y relacionada con el avance presentado. Para documentar ese uso, los estudiantes deberán conservar evidencias que permitan: 

- Relacionar los logs con los scripts, notebooks, configuraciones, resultados o artefactos generados. 

- Identificar la fecha, el usuario responsable, la tarea ejecutada y el resultado obtenido. 

- Registrar la duración o los recursos utilizados cuando esos datos sean relevantes para interpretar la ejecución. 

Docente: Pablo D. Cuña | Guía para estudiantes  |  Página 8 de 21 

**UTEC  ·  LIDIA  ·  Proyecto de Aprendizaje Automático** 



- Verificar el uso mediante archivos y registros; las capturas de pantalla podrán complementar la evidencia, pero no sustituirla. 

**Uso responsable:** No se evalúa la cantidad de horas de cómputo. Se valorará que los recursos se utilicen de forma pertinente, verificable y responsable. 

## **4.3 Uso de inteligencia artificial generativa** 

Las herramientas de inteligencia artificial generativa pueden utilizarse como apoyo para programar, depurar, analizar, documentar u organizar el trabajo. Su uso no reemplaza la comprensión, la autoría ni la responsabilidad del equipo. Todo contenido incorporado deberá ser revisado, comprendido, adaptado y verificado, y ningún integrante podrá presentar como propio un resultado que no pueda explicar o defender. 

Desde el Entregable 1, el repositorio deberá contener un archivo denominado exactamente registro_uso_IA.md , que se actualizará de forma incremental durante todo el proyecto. Este archivo deberá incluir: 

- Una declaración explícita de si se utilizaron o no herramientas de IA generativa. 

- Los prompts relevantes que hayan incidido en el código, el análisis, la documentación o una decisión importante. 

- Las respuestas relevantes asociadas a esos prompts. 

- Una explicación breve de cómo las respuestas fueron utilizadas, modificadas, descartadas o verificadas. 

No deberán compartirse con estas herramientas datos personales, sensibles, confidenciales o restringidos sin autorización. 

## **4.4 Reproducibilidad** 

La solución deberá poder comprenderse, ejecutarse y verificarse a partir del repositorio y la documentación. En los entregables 3 y 4 deberá ser posible ejecutar la solución seleccionada y el prototipo sin volver a entrenar el modelo. Para garantizarlo, los estudiantes deberán entregar y mantener actualizados los siguientes archivos y recursos: 

- README con propósito, requisitos, datos, preparación, ejecución y resultados esperados. 

- requirements.txt , environment.yml u otro archivo equivalente de entorno y dependencias. 

- Datos, una muestra utilizable o un mecanismo reproducible de acceso cuando no puedan versionarse. 

- Semillas, configuraciones y versiones relevantes cuando afecten los resultados. 

- Modelo entrenado y demás artefactos necesarios para ejecutar la solución. 

- Registro de experimentos y trazabilidad entre datos, código, configuración, resultado y decisión. 

Docente: Pablo D. Cuña | Guía para estudiantes  |  Página 9 de 21 

**UTEC  ·  LIDIA  ·  Proyecto de Aprendizaje Automático** 



## **4.5 Pruebas del pipeline de inferencia** 

La validación estadística del modelo no sustituye la comprobación del pipeline como software. Desde el Entregable 3, el equipo deberá ejecutar y registrar un conjunto acotado de pruebas, adecuado a su solución, que permita verificar: 

- La validación del formato o esquema esperado de los datos de entrada y el tratamiento controlado de entradas inválidas o inesperadas. 

- La carga correcta del modelo y de los demás artefactos necesarios. 

- La ejecución coherente del preprocesamiento y de la inferencia mediante una prueba integral del flujo. 

- El formato, el tipo y, cuando corresponda, el rango esperado de las salidas. 

- Los resultados de las pruebas, los errores detectados y las correcciones realizadas. 

**Alcance:** No se exige una cobertura mínima, integración continua ni una batería de pruebas <mark>propia de un sistema productivo. Las pruebas deberán ser suficientes para demostrar que el flujo</mark> principal funciona de manera controlada y verificable. 

# **5. Entregables** 

El proceso se organiza en cuatro entregables acumulativos. Cada uno deberá incorporar las correcciones y decisiones surgidas del seguimiento anterior; por tanto, no se trata de productos independientes, sino de versiones progresivamente más completas de un mismo proyecto. 

## **5.1 Entregable 1. Propuesta inicial** 

**Fecha: 17 de agosto. Si el Comité Académico solicita reformulación, la nueva versión deberá presentarse el 24 de agosto.** 

La propuesta define un problema viable, pertinente y coherente con los datos disponibles. Se utilizará la Plantilla de presentación y aprobación de la propuesta de PAA. La plantilla deberá incluir la ruta o enlace al repositorio nuevo del proyecto. 

### **Resultados esperados** 

Al finalizar este hito, el equipo deberá demostrar: 

- Un problema de aprendizaje automático claramente formulado y relacionado con el proyecto anterior. 

- La relevancia del problema y la utilidad esperada de la solución. 

- Un objetivo general y objetivos específicos coherentes, alcanzables y verificables. 

- Datos identificados y efectivamente disponibles, con una revisión inicial de su viabilidad. 

- Un alcance realista y una forma prevista de integración con el _dashboard_ o producto existente. 

Docente: Pablo D. Cuña | Guía para estudiantes  |  Página 10 de 21 



**UTEC  ·  LIDIA  ·  Proyecto de Aprendizaje Automático** 

- Tutor definido, cronograma inicial, riesgos principales, repositorio creado, acceso al servidor verificado y registro de IA iniciado. 

### **Evidencias obligatorias** 

La entrega deberá incluir: 

- La plantilla completa y revisada con el tutor, incluida la aceptación inicial de la tutoría. 

- La ruta o enlace al repositorio nuevo y la verificación de acceso para docente y tutor. 

- El archivo registro_uso_IA.md creado dentro del repositorio. 

- La descripción de los datos disponibles y del uso previsto del servidor institucional. 

- El plan de trabajo o cronograma inicial del equipo. 

**En esta etapa:** El foco está en la formulación y viabilidad de la propuesta. El análisis exploratorio <mark>completo, los modelos entrenados, los hiperparámetros definitivos, las métricas finales y los</mark> resultados experimentales se desarrollarán en los entregables posteriores. 

### **Ponderación y aspectos de evaluación** 

El Entregable 1 representa el 10 % del proceso. Para alcanzar la evaluación se considerarán los siguientes aspectos, con sus respectivos pesos internos: 

|**Aspecto**|**Peso interno**|
|---|---|
|Formulación y relevancia del problema|25 %|
|Coherencia de los objetivos|20 %|
|Disponibilidad y viabilidad de los datos|25 %|
|Alcance y orientación de la solución|20 %|
|Planificación y trazabilidad inicial|10 %|



**Condición de aprobación:** La propuesta deberá presentar un problema viable, datos realmente disponibles y correspondencia razonable entre datos y solución. 

## **5.2 Entregable 2. Datos, metodología y línea base** 

#### **Fechas: Entrega: 20 de septiembre. Primera presentación intermedia: 21 de septiembre.** 

Este hito demuestra que el equipo comprende los datos, diseñó una evaluación metodológicamente válida y obtuvo una línea base reproducible. Las decisiones deberán justificarse según el tipo de datos y el problema; no existe una lista única de técnicas obligatorias. 

Docente: Pablo D. Cuña | Guía para estudiantes  |  Página 11 de 21 

**UTEC  ·  LIDIA  ·  Proyecto de Aprendizaje Automático** 



**Qué se entiende por línea base:** Es un punto de referencia inicial, sencillo y reproducible, que <mark>permite determinar si los modelos posteriores aportan una mejora real. Puede ser una regla ingenua o un modelo simple, según el problema. Debe evaluarse con el mismo protocolo y las</mark> mismas métricas que las alternativas posteriores. 

### **Resultados esperados** 

Al finalizar este hito, el equipo deberá demostrar: 

- Un diagnóstico de calidad, adecuación, cobertura y limitaciones de los datos. 

- Una preparación pertinente: limpieza, transformación, imputación, codificación, escalado, balanceo, selección o construcción de variables, reducción de dimensionalidad u otras acciones cuando correspondan. 

- Un tratamiento específico para series temporales, texto, imágenes, audio u otras modalidades cuando sea aplicable. 

- Un protocolo de evaluación válido: particiones, validación y métricas apropiadas, sin fugas de información. 

- Un conjunto de prueba reservado y no utilizado para ajustar procedimientos ni seleccionar modelos. 

- Una línea base adecuada y una interpretación de los resultados preliminares. 

**Criterio metodológico:** Las transformaciones que aprenden de los datos, por ejemplo <mark>imputación, escalado, PCA o balanceo, deberán ajustarse con los datos de entrenamiento y,</mark> cuando corresponda, dentro de cada partición de validación. 

### **Evidencias obligatorias** 

La entrega y la presentación deberán incluir: 

- Código completo desarrollado hasta el hito. 

- Datos o mecanismo reproducible para obtenerlos. 

- README actualizado con instrucciones para reproducir el procesamiento y los resultados preliminares. 

- Archivo de entorno, registro de experimentos, registro de IA y evidencia del servidor. 

- Borrador acumulativo del informe, al menos hasta los resultados preliminares. 

- Versión identificable del repositorio y constancia breve de seguimiento del tutor. 

- Presentación intermedia con participación de todos los integrantes; el formato y la duración se comunicarán en el curso. 

### **Ponderación y aspectos de evaluación** 

El Entregable 2 representa el 30 % del proceso. Se considerarán los siguientes aspectos a semejanza del entregable 1: 

Docente: Pablo D. Cuña | Guía para estudiantes  |  Página 12 de 21 



|**UTEC  ·  LIDIA  ·  Proyecto de Aprendizaje Automático**<br><br>|
|---|
|**Aspecto**<br>**Peso interno**|
|Comprensión y diagnóstico de los datos<br>20 %|
|Preparación, variables y características<br>25 %|
|Diseño de la evaluación<br>20 %|
|Línea base y resultados preliminares<br>20 %|
|Reproducibilidad y documentación<br>15 %|



**Pertinencia:** No se valorará la acumulación mecánica de técnicas. Se considerarán la necesidad, <mark>la justificación, la ejecución correcta y el efecto demostrado. Los aspectos que no correspondan</mark> al proyecto no deberán forzarse. 

## **5.3 Entregable 3. Experimentación avanzada y solución seleccionada** 

#### **Fechas: Entrega: 25 de octubre. Segunda presentación intermedia: 26 de octubre.** 

El equipo deberá realizar experimentación sistemática, seleccionar una solución con evidencia válida, analizar críticamente sus resultados e integrarla en un prototipo funcional. 

### **Resultados esperados** 

Al finalizar este hito, el equipo deberá demostrar: 

- La comparación de alternativas pertinentes de modelos, representaciones, variables o configuraciones. 

- El ajuste y la validación sin utilizar el conjunto de prueba para tomar decisiones. 

- La selección de la solución final mediante criterios explícitos y no solo por una única métrica. 

- La evaluación final sobre el conjunto de prueba una vez fijada la solución. 

- La comparación con la línea base y el análisis del cumplimiento de los objetivos. 

- La explicación de la solución y la interpretación de sus resultados mediante recursos 

   - adecuados al modelo y al caso de uso. 

- El análisis de errores, limitaciones, robustez, generalización y posibles sesgos en la medida pertinente. 

- La disponibilidad del modelo entrenado, los artefactos y la trazabilidad necesarios para reproducir los resultados. 

- La comprobación del pipeline de inferencia mediante pruebas de funcionamiento acordes con la solución. 

- Un prototipo integrado, funcional y demostrable de nivel TRL 5. 

Docente: Pablo D. Cuña | Guía para estudiantes  |  Página 13 de 21 

**UTEC  ·  LIDIA  ·  Proyecto de Aprendizaje Automático** 

**Conjunto de prueba:** Debe permanecer reservado durante el desarrollo. Se utilizará para evaluar la solución ya seleccionada, no para elegirla, ajustarla ni decidir sus hiperparámetros. 



### **Prototipo TRL 5** 

Se espera un prototipo integrado que ejecute el flujo completo con datos representativos en un entorno controlado o simulado. Debe ser funcional, reproducible y demostrable, pero no se exige despliegue productivo ni alojamiento permanente. El prototipo deberá: 

- Permitir ingresar, seleccionar o recuperar datos según el caso de uso. 

- Ejecutar el preprocesamiento y la inferencia de forma coherente con el entrenamiento. 

- Mostrar resultados comprensibles y las nuevas funcionalidades incorporadas. 

- Incluir instrucciones para ejecutar la solución sin volver a entrenar. 

- Priorizar la validez y la integración; la sofisticación visual de la interfaz no es un criterio central. 

### **Evidencias obligatorias** 

La entrega y la presentación deberán incluir: 

- Código, configuraciones, resultados y registro de experimentos. 

- Modelo entrenado y demás artefactos necesarios para la inferencia. 

- Pruebas del pipeline de inferencia y registro de sus resultados, errores detectados y correcciones. 

- README e instrucciones de ejecución actualizados. 

- Informe acumulativo con experimentación, resultados, discusión preliminar y descripción del prototipo. 

- Registro de IA, evidencia del servidor, versión identificable del repositorio y constancia del tutor. 

- Presentación de 10 minutos, incluida la demostración, seguida de 10 minutos de preguntas y retroalimentación. Todos los integrantes deberán participar. 

### **Ponderación y aspectos de evaluación** 

El Entregable 3 representa el 50 % del proceso. Se considerarán los siguientes aspectos a semejanza de los entregables 1 y 2: 

|**Aspecto**|**Peso interno**|
|---|---|
|Calidad metodológica de la experimentación|30 %|
|Selección y evaluación final de la solución|25 %|
|Análisis crítico y explicabilidad|20 %|
|Reproducibilidad y documentación|15 %|



Docente: Pablo D. Cuña | Guía para estudiantes  |  Página 14 de 21 

**UTEC  ·  LIDIA  ·  Proyecto de Aprendizaje Automático Aspecto Peso interno** Prototipo funcional 10 % 



<!-- Start of picture text -->
Peso interno<br>10 %<br><!-- End of picture text -->

## **5.4 Entregable 4. Entrega definitiva al tribunal** 

**Fecha: 15 de noviembre. La defensa se realizará en la fecha comunicada posteriormente por el tribunal o la coordinación.** 

El Entregable 4 no abre una etapa técnica nueva. Es el cierre formal y la entrega completa, ordenada, accesible y verificable de la solución final al tribunal. 

### **Contenido obligatorio** 

La entrega definitiva deberá incluir: 

- Informe final integrado y coherente, elaborado de acuerdo con la guía institucional vigente. 

- Repositorio nuevo y completo, con accesos verificados para el tribunal. 

- Datos o mecanismo de acceso reproducible, código y archivos de entorno. 

- Modelo entrenado, configuraciones, resultados y demás artefactos necesarios. 

- Prototipo TRL 5 ejecutable y demostrable sin volver a entrenar. 

- Pruebas del pipeline de inferencia y evidencia de sus resultados. 

- README e instrucciones completas de instalación, ejecución y verificación. 

- Registro incremental completo de uso de IA y evidencias del servidor institucional. 

- Constancia breve de seguimiento del tutor y comprobación de todos los enlaces. 

### **Ponderación y aspectos de evaluación** 

El Entregable 4 representa el 10 % del proceso. Se considerarán los siguientes aspectos a semejanza de los entregables 1, 2 y 3: 

|**Aspecto**|**Peso interno**|
|---|---|
|Puntualidad|30 %|
|Cumplimiento de requisitos formales|30 %|
|Completitud y accesibilidad|40 %|



**Alcance:** Estos aspectos valoran el cierre y la disponibilidad de los materiales. La calidad técnica del informe y de la solución forma parte de la evaluación integral realizada por el tribunal. 

Docente: Pablo D. Cuña | Guía para estudiantes  |  Página 15 de 21 

**UTEC  ·  LIDIA  ·  Proyecto de Aprendizaje Automático** 



# **6. Orientaciones técnicas del ciclo de aprendizaje automático** 

Estas orientaciones expresan criterios de validez y no una receta. Cada equipo deberá decidir qué procedimientos son pertinentes y explicar por qué. 

## **6.1 Problema, datos y variables** 

En relación con el problema y los datos, el equipo deberá: 

- Definir claramente la unidad de análisis, el propósito de la predicción o del análisis y, cuando corresponda, la variable objetivo. 

- Revisar calidad, cobertura, representatividad, sesgos y restricciones de uso de los datos. 

- Justificar las variables, transformaciones y características utilizadas. 

- Evitar incorporar información que no estaría disponible en el momento real de la predicción. 

- Documentar las decisiones y su relación con el problema. 

## **6.2 Diseño de evaluación** 

El protocolo de evaluación deberá: 

- Separar entrenamiento, validación y prueba de forma adecuada al problema. 

- Usar división cronológica y validación temporal cuando el orden temporal sea relevante. 

- Seleccionar métricas coherentes con el objetivo, los costos de error y el balance de clases o la distribución de la variable. 

- Incluir una línea base que permita interpretar si la mejora obtenida es relevante. 

- Prevenir fugas de información durante la preparación, la validación y la selección. 

## **6.3 Experimentación y selección** 

Durante la experimentación, el equipo deberá: 

- Investigar alternativas pertinentes y registrar las hipótesis que orientan los experimentos. 

- Comparar de forma justa, usando el mismo protocolo cuando corresponda. 

- Conservar resultados negativos o descartados cuando expliquen una decisión importante. 

- Seleccionar la solución considerando desempeño, estabilidad, explicabilidad, costo, restricciones e integración. 

- Evaluar la solución seleccionada en prueba una sola vez, salvo que exista una razón metodológica documentada para otro esquema. 

## **6.4 Explicabilidad, interpretación y análisis crítico** 

El análisis final deberá: 

Docente: Pablo D. Cuña | Guía para estudiantes  |  Página 16 de 21 

**UTEC  ·  LIDIA  ·  Proyecto de Aprendizaje Automático** 



- Relacionar los resultados con los objetivos y con la utilidad real de la solución. 

- Explicar el comportamiento del modelo como se solicita en 1.3 de esta guia. 

- Analizar errores o casos relevantes, no solo métricas agregadas. 

- Identificar limitaciones, supuestos, sesgos y amenazas a la validez. 

- Explicar resultados inesperados y proponer mejoras fundamentadas. 

- Distinguir claramente entre la evidencia obtenida y las inferencias del equipo. 

**Sesgo y equidad:** Cuando el proyecto utilice datos de personas o produzca decisiones que <mark>puedan afectarlas, el equipo deberá considerar posibles sesgos en los datos y diferencias relevantes en el desempeño entre grupos. En los demás casos, se analizará la robustez frente a</mark> distintas clases, condiciones, períodos o contextos, cuando corresponda. 

# **7. Informe final** 

El informe se desarrollará de manera acumulativa desde el Entregable 2. La versión final deberá ser un documento integrado y coherente, no una suma de fragmentos ni una repetición extensa del informe de PID. Su estructura, estilo, citas, tablas, figuras y demás requisitos formales deberán ajustarse a la Guía y modelo para la elaboración de informes de proyectos integradores y del Trabajo Final de Carrera vigente. 

## **7.1 Extensión** 

**Cuerpo principal:** Máximo 50 páginas desde la Introducción hasta Conclusiones y trabajo futuro, ambas inclusive. El límite incluye tablas y figuras y no es una meta de extensión. 

**Anexos y apéndices:** Máximo conjunto de 20 páginas, salvo autorización previa y fundada del tutor. Deben ser complementarios, estar citados en el texto y no desplazar contenido esencial. 

No se contabilizan dentro del límite principal la portada, las declaraciones, el resumen, los índices ni las referencias. El código, los notebooks completos, los logs extensos y los resultados masivos permanecerán en el repositorio. 

# **8. Sistema de evaluación** 

La asignatura utiliza el Sistema de Calificación de Proyectos 5 (SCP 5). La evaluación comprende tres componentes complementarios: 

|**Componente**|**Incidencia**|**Qué se considera**|
|---|---|---|
|Proceso|30 %|Desarrollo progresivo y cumplimiento de los cuatro<br>entregables|
|Informe final y solución<br>técnica|50 %|Calidad académica, metodológica, técnica y funcional del<br>proyecto concluido|



Docente: Pablo D. Cuña | Guía para estudiantes  |  Página 17 de 21 

**UTEC  ·  LIDIA  ·  Proyecto de Aprendizaje Automático Componente Incidencia Qué se considera** Defensa final 20 % Presentación y respuestas ante el tribunal 



A lo largo de la asignatura se considerarán, de manera articulada, la pertinencia del problema, la calidad de los datos y de la metodología, la validez de la evaluación, la experimentación, la explicabilidad y el análisis crítico, la integración funcional, la reproducibilidad, la documentación, la comunicación y el cumplimiento de los requisitos establecidos. 

Aunque los entregables se elaboran en equipo, todos los estudiantes deberán demostrar comprensión integral del proyecto y participación efectiva. El docente y el tribunal podrán realizar preguntas o comprobaciones individuales durante el seguimiento, las presentaciones y la defensa. Las competencias C3.1, C3.2 y C3.3 se acreditarán individualmente a partir de evidencias observables generadas durante el proceso. 

Las calificaciones podrán diferenciarse entre integrantes cuando las evidencias del proceso, las contribuciones identificables, las presentaciones o las respuestas individuales demuestren distintos niveles de participación, comprensión o dominio del proyecto. 

## **8.1 Defensa final** 

La defensa no deberá reproducir literalmente el informe. El equipo deberá seleccionar, explicar y fundamentar las decisiones y evidencias más importantes del proyecto. La presentación deberá incluir, al menos: 

- El problema, su relevancia, los objetivos y el alcance de la solución. 

- Los datos utilizados, la variable objetivo cuando corresponda y las principales decisiones de preparación. 

- La línea base, las alternativas evaluadas y la justificación de la solución seleccionada. 

- La estrategia de validación, las métricas empleadas y los resultados principales. 

- El análisis de errores, limitaciones, robustez y explicabilidad; cuando corresponda, los sesgos relevantes. 

- La demostración del prototipo, del pipeline de inferencia y de las pruebas realizadas sobre su funcionamiento. 

- Las conclusiones, las mejoras futuras y los principales aprendizajes del equipo. 

- La contribución de cada integrante y su capacidad para responder individualmente las preguntas del tribunal. 

**Pertinencia:** Si alguno de estos contenidos no corresponde al proyecto, el equipo deberá justificarlo brevemente. 

Docente: Pablo D. Cuña | Guía para estudiantes  |  Página 18 de 21 

**UTEC  ·  LIDIA  ·  Proyecto de Aprendizaje Automático** 



# **9. Integridad académica y plagio** 

El proyecto deberá ser de elaboración propia. Sus textos, análisis, código, decisiones y conclusiones deberán reflejar el trabajo y la comprensión del equipo, sin que ello implique desarrollar métodos inéditos ni realizar un aporte original al estado del arte. Toda idea, texto, imagen, tabla, figura, código, conjunto de datos, modelo preentrenado, notebook, recurso técnico o resultado proveniente de terceros deberá identificarse y citarse de manera adecuada. Parafrasear o traducir una fuente no elimina la obligación de reconocerla. 

Se consideran transgresiones a la integridad académica, entre otras: 

- Copiar total o parcialmente trabajos, textos, código, análisis o materiales sin atribución. 

- Presentar como propia una producción realizada por otra persona, otro equipo o un servicio externo. 

- Reutilizar trabajos previos propios o ajenos sin identificar su origen y sin autorización cuando corresponda. 

- Inventar, alterar u ocultar datos, resultados, experimentos, registros o evidencias. 

- Falsear la autoría, las contribuciones individuales, el uso del servidor, el uso de IA o el seguimiento del tutor. 

- Utilizar herramientas de IA generativa para sustituir el trabajo intelectual propio o incorporar contenido que el equipo no comprenda ni pueda defender. 

La continuidad con el PID permite reutilizar materiales producidos por el mismo equipo, pero esa reutilización deberá declararse y distinguirse claramente de los aportes desarrollados durante el PAA. El docente o el tribunal podrán solicitar explicaciones individuales, revisar el historial del repositorio, verificar fuentes y utilizar herramientas de detección de similitudes cuando corresponda. 

**Consecuencias:** Las situaciones de plagio, fraude o tergiversación de evidencias serán tratadas <mark>de acuerdo con la normativa vigente de UTEC y podrán determinar la anulación de la evaluación</mark> o la aplicación de otras medidas académicas. 

# **10. Lista de comprobación final** 

## **10.1 Antes de cada entrega** 

Antes de enviar cada hito, el equipo deberá comprobar que: 

- La versión del repositorio correspondiente al hito está identificada. 

- Docente y tutor tienen acceso; en el Entregable 4 también el tribunal. 

- Los enlaces funcionan y los archivos se abren. 

- README, dependencias, registro de IA y evidencias del servidor están actualizados. 

- El informe acumulativo refleja las decisiones y correcciones realizadas. 

Docente: Pablo D. Cuña | Guía para estudiantes  |  Página 19 de 21 

**UTEC  ·  LIDIA  ·  Proyecto de Aprendizaje Automático** 



- El tutor conoce el contenido del entregable y se incorpora la constancia de seguimiento. 

- Todos los integrantes pueden explicar el trabajo presentado. 

## **10.2 Antes de la entrega final** 

Antes de la entrega definitiva, el equipo deberá comprobar que: 

- El informe cumple la guía institucional, la extensión y los requisitos formales. 

- La solución puede ejecutarse sin volver a entrenar el modelo. 

- El prototipo TRL 5 funciona con datos representativos. 

- Las pruebas del pipeline de inferencia se ejecutan correctamente y sus resultados están registrados. 

- Los datos o el mecanismo de acceso son utilizables por los evaluadores. 

- El modelo entrenado, las configuraciones y los artefactos necesarios están disponibles. 

- Los resultados del informe coinciden con los artefactos del repositorio. 

- El registro de IA está completo y la protección de datos fue respetada. 

- Los permisos del tribunal fueron probados con anticipación. 

- Todas las fuentes fueron citadas y no existe contenido de terceros presentado como propio. 

- La defensa cubre los contenidos esperados y todos los integrantes están preparados para responder individualmente. 

Docente: Pablo D. Cuña | Guía para estudiantes  |  Página 20 de 21 

**UTEC  ·  LIDIA  ·  Proyecto de Aprendizaje Automático** 



# **11. Referencias** 

Las referencias institucionales y la bibliografía técnica de apoyo se presentan de acuerdo con APA 7. Los equipos deberán consultar además las versiones vigentes publicadas por la Universidad y las fuentes específicas que correspondan a cada proyecto. 

## **11.1 Documentos institucionales** 

- Universidad Tecnológica. (2022). _Circular de trabajos finales: Directivas complementarias del Reglamento General de Estudios (Circular 29/DE/2022)_ . 

- Universidad Tecnológica. (2023). _Plan de estudios de la Licenciatura en Ingeniería de Datos e Inteligencia Artificial, con titulación intermedia de Tecnólogo en Análisis y Gestión de Datos_ . 

- Universidad Tecnológica. (2024). _Circular de evaluaciones, calificaciones e inasistencias (Circular 37/DE/2024)_ . 

- Universidad Tecnológica. (2026a). _Guía y modelo para la elaboración de informes de proyectos integradores y del Trabajo Final de Carrera_ . 

- Universidad Tecnológica. (2026b). _Plantilla de presentación y aprobación de la propuesta del Proyecto de Aprendizaje Automático_ [Documento interno]. 

- Universidad Tecnológica. (s. f.). _Matriz institucional de estándares de competencias LIDIA/TAGD_ [Documento interno]. 

## **11.2 Bibliografía técnica de apoyo** 

Alpaydın, E. (2020). _Introduction to machine learning_ (4th ed.). The MIT Press. 

Bagnato, J. I. (2020). _Aprende machine learning en español: Teoría + práctica Python_ . Leanpub. 

Burkov, A. (2019). _The hundred-page machine learning book_ . Andriy Burkov. 

Géron, A. (2019). _Hands-on machine learning with Scikit-Learn, Keras, and TensorFlow_ (2nd ed.). O’Reilly Media. 

Géron, A. (2023). _Aprende machine learning con Scikit-Learn, Keras y TensorFlow: Conceptos, herramientas y técnicas para conseguir sistemas inteligentes_ (3.ª ed.). Anaya Multimedia. 

- Kelleher, J. D., Mac Namee, B., & D’Arcy, A. (2020). _Fundamentals of machine learning for predictive data analytics: Algorithms, worked examples, and case studies_ (2nd ed.). The MIT Press. 

Larose, C. D., & Larose, D. T. (2019). _Data science using Python and R_ . Wiley. 

Docente: Pablo D. Cuña | Guía para estudiantes  |  Página 21 de 21 

