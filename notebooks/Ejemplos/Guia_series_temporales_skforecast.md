





## GUÍA PRÁCTICA
Pronóstico de series temporales
con machine learning y skforecast
Fundamentos, decisiones metodológicas y ejemplos visuales para proyectos
Proyecto de Aprendizaje Automático
Licenciatura en Ingeniería de Datos e Inteligencia Artificial
## Docente Pablo Cuña · 2026


Índice interactivo
Cómo utilizar esta guía
Mapa de la guía
- Series temporales y pronóstico
1.1 ¿Qué es una serie temporal?
1.2 Componentes y comportamientos frecuentes
1.3 Forecasting desde machine learning
- Definir correctamente el problema
2.1 Las seis decisiones iniciales
2.2 Frecuencia original y frecuencia de trabajo
2.3 Un paso y varios pasos
- Construir una serie temporal confiable
3.1 El índice temporal
3.2 Cuatro problemas diferentes
3.3 Faltantes e imputación
3.4 Valores atípicos
- Separar antes de aprender del futuro
4.1 Qué puede revisarse antes de la partición
4.2 Qué debe aprenderse solamente con train
4.3 El preprocesamiento también forma parte de cada fold
- Análisis exploratorio orientado a predecir
5.1 Gráficos esenciales
5.2 Estacionariedad: qué significa y por qué puede ayudar
5.3 Cómo valorar si existe un problema de estacionariedad
5.4 Cuándo considerar una transformación
- Referencias iniciales: antes del modelo complejo
- Backtesting: evaluar como si estuviéramos en el pasado
7.1 Decisiones que deben declararse
7.2 Validación interna y test final
- Métricas: medir lo que importa
8.1 Error global y error por horizonte
8.2 Gráficos que acompañan las métricas
- Modelo univariante con skforecast
9.1 Elegir lags
9.2 Regresores candidatos
9.3 Ajuste de lags e hiperparámetros
- Una serie objetivo con variables exógenas
10.1 La prueba decisiva: disponibilidad futura
10.2 Preparar y y exog
10.3 Variables de calendario y categóricas
10.4 Comparación justa
- Evaluación final y despliegue
11.1 Congelar antes de abrir el test
11.2 Dos regímenes de evaluación
11.3 Reentrenamiento final
11.4 Contrato de datos para producción
11.5 Guardado, monitoreo y actualización

- Trabajar con código generado por IA
12.1 Qué debe contener una buena solicitud
12.2 Lista de revisión del código generado
- Secuencia general adaptable
- Errores frecuentes
- Qué debería documentar cada proyecto
Lista final de comprobación
## Referencias


Cómo utilizar esta guía
Esta guía ofrece un panorama general para diseñar proyectos de pronóstico con series temporales
mediante modelos de machine learning y la biblioteca skforecast. No propone una receta universal: cada
decisión debe justificarse según el fenómeno, la disponibilidad de datos y el uso real de la predicción.
IDEA CENTRAL  El objetivo no es ejecutar todos los análisis posibles. Es construir una evaluación temporal
creíble y usar únicamente información que estaría disponible al emitir el pronóstico.

Recorrido recomendado:
- Lectura esencial: secciones 1 a 10 y la lista de comprobación final.
- Según el proyecto: estacionariedad, transformaciones, escalado, variables categóricas y métricas
adicionales.
- Implementación: los fragmentos de código muestran la forma general; deben adaptarse y verificarse
con la versión instalada.
- Uso de IA: puede ayudar a programar, pero no reemplaza la definición del protocolo temporal ni la
revisión de fugas de información.
Mapa de la guía
Parte Pregunta principal
I. Comprender ¿Qué queremos pronosticar y cómo se organiza el tiempo?
II. Preparar ¿La serie está completa, ordenada y tratada sin usar el futuro?
III. Modelar ¿Qué referencia, estrategia, lags y regresor utilizaremos?
IV. Evaluar ¿Cómo simularíamos el uso real del modelo en el pasado?
V. Ampliar ¿Las variables exógenas mejoran realmente el pronóstico?
VI. Desplegar ¿Cómo generar, guardar y monitorear predicciones futuras?



Figura 1. Flujo general de un proyecto de forecasting.  Elaboración propia con datos sintéticos.
- Series temporales y pronóstico
1.1 ¿Qué es una serie temporal?
Una serie temporal es una secuencia de observaciones asociadas a momentos concretos y ordenadas
cronológicamente. El tiempo no es una columna más: determina qué información pertenece al pasado,
cuál está disponible en el presente y qué valores forman el futuro desconocido.
- Consumo eléctrico por hora.
- Ventas diarias.
- Temperatura cada diez minutos.
- Demanda turística mensual.
- Concentración de contaminantes por estación y hora.
1.2 Componentes y comportamientos frecuentes
## Componente Interpretación
Tendencia Evolución general creciente, decreciente o cambiante.
Estacionalidad Patrón que se repite con un periodo reconocible.

## Componente Interpretación
Ciclos Movimientos de duración variable, no necesariamente periódicos.
Residuo o ruido Variación no explicada por las estructuras anteriores.
Cambios de nivel Saltos persistentes por modificaciones del sistema.
Atípicos Observaciones inusuales: pueden ser errores o eventos reales.


Figura 2. Componentes frecuentes de una serie temporal.  Elaboración propia con datos sintéticos.
IMPORTANTE  Estacionalidad y estacionariedad no son sinónimos. La primera describe repetición; la segunda se
refiere a la estabilidad de propiedades estadísticas a lo largo del tiempo.


1.3 Forecasting desde machine learning
En regresión supervisada disponemos de variables predictoras X y una respuesta y. En forecasting, los
valores pasados de la propia serie se convierten en variables predictoras. Este proceso permite utilizar
Ridge, Random Forest, XGBoost, LightGBM y otros estimadores compatibles con scikit-learn. skforecast
automatiza gran parte de esa transformación y de la evaluación temporal [3–5].

Figura 3. Transformación mediante lags.  Elaboración propia con datos sintéticos.
LAG NO ES HORIZONTE  Los lags indican cuánta y cuál historia usa el modelo. El horizonte indica cuántos pasos
futuros debe producir. Pueden relacionarse, pero no son la misma decisión.

- Definir correctamente el problema
Antes de limpiar o modelar, conviene describir el caso de uso en una frase verificable. Por ejemplo:
«Cada día a las 00:00, pronosticar el consumo diario de los próximos siete días usando información
disponible hasta el cierre del día anterior».
2.1 Las seis decisiones iniciales
## Decisión Pregunta
Variable objetivo ¿Qué magnitud exacta queremos predecir y en qué unidad?
Frecuencia de trabajo ¿Cada fila representará una hora, un día o un mes?

## Decisión Pregunta
Horizonte ¿Cuántos pasos futuros necesita el usuario?
Momento de emisión ¿Cuándo y con qué información se genera el pronóstico?
Actualización ¿Se predice una vez o se actualiza al llegar nuevos datos?
Costo del error ¿Importa más errar en magnitud, en porcentaje o en picos?

EJEMPLO  Con datos diarios y horizonte 7, steps=7 representa siete días. Con datos horarios, steps=7
representa siete horas, no una semana.

2.2 Frecuencia original y frecuencia de trabajo
La frecuencia original indica cada cuánto se registraron los datos. La frecuencia de trabajo es una
decisión del proyecto. Cambiar de horario a diario puede ser adecuado si el producto final necesita
totales diarios, pero no debe hacerse solamente porque el horizonte se exprese en días.
Variable Agregaciones posibles
Consumo, ventas, precipitación
acumulada
Suma del periodo.
Temperatura y humedad Media, mínimo o máximo, según el objetivo.
Velocidad del viento Media; para ráfagas, puede interesar el máximo.
Precio Media, último valor o cierre.
Calendario Reconstruir desde el nuevo índice; no sumar.
Categorías Moda, última observación o una regla del dominio.

2.3 Un paso y varios pasos
Un pronóstico one-step produce únicamente el próximo valor. Un pronóstico multi-step produce una
secuencia futura. Para varios pasos, dos estrategias habituales son la recursiva y la directa [5].


Figura 4. Estrategias recursiva y directa.  Elaboración propia con datos sintéticos.
## Aspecto Recursiva Directa
## Modelos
entrenados
Uno. Uno por paso del horizonte.
Predicción Avanza usando predicciones previas. Cada modelo estima un paso específico.
Riesgo Acumulación de errores. Mayor costo y menor información por modelo.
Flexibilidad Puede cambiarse steps al predecir. El máximo de steps se fija antes del entrenamiento.
Elección Comparar mediante el mismo backtesting. Comparar mediante el mismo backtesting.

- Construir una serie temporal confiable
3.1 El índice temporal
La marca temporal debe convertirse a datetime, ordenarse y establecerse como índice. Luego se verifica
la frecuencia real. No debe asignarse una frecuencia por conveniencia sin comprobar que las
observaciones siguen ese calendario.

Mapa mínimo para comprobar el índice; adapte la frecuencia al proyecto.
df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
df = df.sort_values("fecha").set_index("fecha")

duplicados = df.index.duplicated().sum()
calendario = pd.date_range(df.index.min(), df.index.max(), freq="D")
huecos = calendario.difference(df.index)

3.2 Cuatro problemas diferentes
Problema Qué significa Decisión posible
Marca inválida La fecha no pudo interpretarse. Corregir la fuente o descartar con justificación.
Duplicado temporal
Existen varias filas para el mismo
instante.
Resolver por agregación, prioridad o revisión del origen.
Hueco temporal La fila esperada no existe. Reindexar contra el calendario y decidir cómo tratarla.
Valor faltante La fila existe, pero una variable es NaN. Imputar, modelar como faltante o excluir según el caso.

3.3 Faltantes e imputación
No existe un método universal. La elección depende de la variable, la longitud del hueco, la dinámica
local y el momento real en que se necesita completar el dato.

Figura 5. Comparación visual de métodos de imputación.  Elaboración propia con datos sintéticos.


Método Uso razonable Precaución
Interpolación lineal Huecos cortos y evolución suave.
Puede usar el punto posterior; no siempre es
causal.
## Interpolación
cuadrática
Curvatura local plausible. Puede producir oscilaciones o valores imposibles.
ffill
Variables que permanecen vigentes hasta una
actualización.
Crea tramos planos y arrastra errores.
bfill Reconstrucción histórica excepcional.
Usa información posterior; no es válida en tiempo
real.
Modelo de
imputación
Relaciones complejas entre variables. Debe ajustarse solamente con entrenamiento.

REGLA TEMPORAL  Una técnica puede ser adecuada para reconstruir una base histórica y, al mismo tiempo, ser
imposible durante la operación. Declare cuál de esos problemas está resolviendo.

3.4 Valores atípicos
Un valor extremo puede ser un error de sensor, un problema de carga, un evento excepcional o una
observación legítima. Antes de corregirlo, conviene combinar reglas físicas, visualización temporal,
contexto del dominio y métodos robustos.
- No eliminar automáticamente todo lo que quede fuera de 1,5·IQR.
- Aplicar primero reglas imposibles conocidas: humedad fuera de 0–100 %, consumos negativos si no
son admisibles, etc.
- Calcular umbrales aprendidos únicamente con train o de forma causal.
- Comparar la serie y su distribución antes y después del tratamiento.
- Conservar una máscara o registro de los valores modificados.
Después de detectar un valor sospechoso
Detectar no equivale a corregir. Si el extremo es real, se conserva; puede ser precisamente el evento
que interesa pronosticar. Si se confirma un error y existe una fuente fiable, se corrige con ese valor. Si
no puede recuperarse, se marca como faltante y se elige un tratamiento compatible con la información
disponible. Si hay dudas, se investiga y se documenta: el gráfico por sí solo no determina la causa.


Ejemplo visual de 3.4. Datos sintéticos. Las causas se conocen por verificación externa, no por la altura del pico. La corrección
supone que el respaldo ya está disponible; en backtesting debe respetarse también ese momento de disponibilidad.
Aplicar a test lo aprendido en train
Sí: cuando el preprocesamiento aprende parámetros, se estiman en train y se reutilizan en test sin
recalcularlos con test. Por ejemplo, si la media de train es 1.000 kWh y el desvío 100 kWh, un dato
nuevo de 1.200 kWh se escala como (1.200 − 1.000)/100 = 2. Se conserva la misma regla, aunque la
distribución del test sea diferente.
Si se transforma la variable objetivo para entrenar, se devuelve el pronóstico a la escala original antes de
calcular MAE o RMSE. Esto no equivale a reemplazar la verdad observada: un escalado cambia la
representación; recortar o sustituir un pico real cambia el dato contra el que se evalúa.
Para los atípicos, un umbral de 1.500 kWh aprendido en train puede señalar un dato nuevo de 2.000
kWh como sospechoso. Si los 2.000 kWh son reales y el modelo predijo 1.200, el error absoluto sigue
siendo 800 kWh. No se recorta el objetivo de test a 1.500 para obtener un error menor.
Si ese dato pasa después a formar parte de los lags, se aplica únicamente el tratamiento de entradas
previsto en producción, fijado con train y con la información disponible entonces. Se conserva por
separado la observación original para evaluar. En cada fold se aprende con su entrenamiento; si la
política es no reentrenar, se conservan los parámetros del último ajuste. Véanse 4.1–4.3 para la
secuencia temporal completa.

- Separar antes de aprender del futuro
La decisión que protege todo el experimento es reservar el tramo final como conjunto de prueba antes
de ejecutar cualquier procedimiento que estime parámetros a partir de los valores.

Figura 6. Partición temporal entre entrenamiento y prueba.  Elaboración propia con datos sintéticos.
Partición por una fecha con significado para el proyecto.
inicio_test = "2025-01-01"
train = serie.loc[serie.index < inicio_test]
test  = serie.loc[serie.index >= inicio_test]

4.1 Qué puede revisarse antes de la partición
- Nombres, tipos y unidades de las columnas.
- Orden cronológico, rango y zona horaria.
- Duplicados y huecos del índice esperado.
- Reglas físicas fijas que no se estiman con los valores.

## ATÍPICOS Y PARTICIÓN: EL ORDEN IMPORTA
Primero, revisar reglas físicas o de dominio fijadas de antemano, sobre toda la serie: por ejemplo, una
humedad del 130 % es imposible. Estas reglas no se calculan mirando la distribución de los datos.
Después, reservar el test. Estimar los umbrales estadísticos solo con train; durante el backtesting, volver a
estimarlos con el entrenamiento disponible en cada fold.
Sobre test, aplicar únicamente el tratamiento que el sistema realizará en producción, con información
disponible en ese momento. No borrar un pico real de demanda porque sea difícil de predecir ni sustituirlo
por un valor más cómodo para evaluar.
Ejemplo: si el consumo real fue 2.000 kWh y el pronóstico 1.200 kWh, el error absoluto es 800 kWh.
Reemplazar el dato real por 1.250 kWh reduciría artificialmente el error a 50 kWh. Si el objetivo observado es
inválido o falta, declarar los casos no evaluables; no inventar una verdad mediante imputación. Conservar el
registro original y documentar toda exclusión.
4.2 Qué debe aprenderse solamente con train
En esta guía, ajustar un procedimiento significa estimar sus parámetros con datos. Transformar significa
aplicar una operación. La pregunta clave no es si corrige la no estacionariedad, sino si aprende algún
número o decisión de los valores de la serie: una media, un desvío, un cuantil o una configuración. Si lo
hace, solo puede utilizar el entrenamiento disponible.
- Medias, medianas, cuantiles y límites estadísticos para imputar o detectar atípicos.
- Escaladores y transformadores.
- Categorías y codificadores aprendidos.
- Selección de variables, lags, modelos e hiperparámetros.
- Toda decisión influida por métricas de desempeño.
FUGA DE INFORMACIÓN  Existe cuando una decisión o predictor contiene información que no habría estado
disponible al emitir la predicción. Puede ocurrir en la limpieza, el feature engineering, la validación o las
variables exógenas.

Por ejemplo, un escalador aprendido con toda la serie introduce información futura aunque no busque
corregir la estacionariedad. En cambio, la diferencia y(t) − y(t−1), con orden fijado, solo usa el presente y
el pasado: no aprende un umbral global. Elegir el orden mirando test, o usar operaciones con valores
posteriores, sí puede introducir fuga.

4.3 El preprocesamiento también forma parte de cada fold
Durante el backtesting, un transformador aprendido debería ajustarse con el entrenamiento disponible
en cada corte. Una alternativa práctica es encapsular las transformaciones dentro del forecaster o de un
Pipeline compatible, siempre que se respete la dirección temporal.
## EJEMPLO: UN UMBRAL QUE APRENDE DEL FUTURO
Supongamos una regla ilustrativa: marcar valores superiores a media + 3 × desvío. En un corte temprano de
train, la media es 100 kWh y el desvío 10 kWh: el umbral es 130 kWh y un pico de 150 kWh se marca para
revisión.
Más adelante la serie crece. Al calcular sobre toda la historia, la media resulta 150 kWh y el desvío 40 kWh: el
umbral sube a 270 kWh. El mismo pico de 150 kWh ya no se marca. Son cifras ilustrativas: la tendencia futura
infló el criterio usado para limpiar el pasado.
Por eso, en cada fold se calcula el umbral con su propio entrenamiento. Marcar un atípico tampoco significa
eliminarlo: todavía debe decidirse si es un error o un evento real.
- Análisis exploratorio orientado a predecir
El análisis exploratorio no busca producir todos los gráficos posibles. Su función es descubrir estructuras
que cambien decisiones del modelo o de la evaluación.
5.1 Gráficos esenciales
Gráfico Qué ayuda a responder
Serie completa ¿Existen tendencia, cambios de nivel, huecos o periodos anómalos?
Serie por año/mes/semana ¿Los patrones se repiten o cambian con el tiempo?
Media o mediana móvil ¿Cuál es la evolución general del nivel?
Histograma/densidad ¿Cómo se distribuyen los valores y cómo cambian tras transformar?
Caja o violín por calendario ¿Cambian el nivel y la dispersión según mes o día?
ACF/PACF ¿Qué memoria temporal y periodicidades podrían ser útiles?
Dispersión con lags ¿La relación con un rezago es visible y aproximadamente lineal?
Objetivo vs exógenas ¿Hay relaciones plausibles, retardadas o no lineales?



Figura 7. Autocorrelación y relación con un lag estacional.  Elaboración propia con datos sintéticos.
INTERPRETACIÓN  La ACF y la PACF orientan candidatos de lags, pero no seleccionan por sí solas la mejor
ventana. La decisión final se comprueba mediante validación temporal.

5.2 Estacionariedad: qué significa y por qué puede ayudar
Una serie es aproximadamente estacionaria cuando sus propiedades estadísticas principales se
mantienen estables a lo largo del tiempo. En una formulación práctica, si dividimos la historia en varios
tramos, esperamos encontrar una media y una varianza semejantes, y relaciones temporales que
dependan del rezago y no de la fecha exacta. Esto no significa que todos los valores sean parecidos ni
que la serie deba ser horizontal: puede fluctuar intensamente alrededor de un nivel relativamente
estable.
¿Por qué interesa esta estabilidad? Un modelo aprende en el pasado una relación entre los lags y el
valor futuro. Si el nivel, la dispersión o esa relación cambian continuamente, el patrón aprendido deja de
representar al periodo que se quiere pronosticar. Una serie más estable facilita que lo aprendido en
distintos tramos sea comparable y que el modelo pueda reutilizarlo en observaciones futuras.


Figura 8. Serie aproximadamente estacionaria y serie no estacionaria.  Elaboración propia con datos sintéticos.
NO ES UNA EXIGENCIA UNIVERSAL  La estacionariedad estricta es un supuesto importante de varios modelos
estadísticos, pero no es un requisito automático para utilizar Random Forest, XGBoost, LightGBM o skforecast.
Aun así, una tendencia o un cambio de régimen puede dificultar la generalización, especialmente en modelos
de árboles, que no suelen extrapolar fuera del rango aprendido.

5.3 Cómo valorar si existe un problema de estacionariedad
- Inspección temporal: compare el nivel y la amplitud de las oscilaciones al principio, en el centro y al
final de train.
- Estadísticos móviles: represente media o mediana móvil y desviación estándar móvil con una
ventana coherente con la frecuencia.
- Comparación por tramos: revise distribuciones, cuantiles y patrones estacionales en periodos
distintos.
- Cambios estructurales: identifique saltos por tarifas, sensores, políticas, hábitos o cambios
operativos; una transformación matemática no siempre los resuelve.
- Pruebas ADF y KPSS: pueden aportar evidencia complementaria sobre raíces unitarias o
estacionariedad, pero no sustituyen los gráficos ni el conocimiento del proceso.
CON ESTACIONALIDAD  Una serie con patrones semanales o anuales puede cambiar de media según el
momento del ciclo. En esos casos puede modelarse la estacionalidad con lags, variables de calendario o
diferenciación estacional. Estacionalidad y estacionariedad no son sinónimos.


5.4 Cuándo considerar una transformación
No se transforma una serie solo porque una prueba estadística resulte significativa. La transformación
debe responder a un comportamiento observado, poder aplicarse sin mirar el test y demostrar una
mejora mediante el mismo backtesting utilizado para comparar modelos.
Transformación Puede ayudar cuando... Debe comprobarse...
Log o raíz La variabilidad aumenta claramente junto con el nivel.
Dominio válido, sesgo al invertir y métricas en
la escala original.
Box-Cox/Yeo-
## Johnson
Se necesita estabilizar la varianza o reducir una asimetría
marcada.
Parámetros aprendidos solo con train e
inversión correcta.
## Diferenciación
regular
Existe una tendencia persistente y interesa modelar los
cambios entre periodos.
Pérdida de la primera observación y
reconstrucción acumulada de la escala
original.
## Diferenciación
estacional
Se repite un patrón fuerte cada s periodos y su nivel
cambia lentamente.
Periodo s justificado y reconstrucción con los
valores históricos necesarios.
Tendencia o
calendario como
variables
La evolución es predecible y estará disponible en el
horizonte futuro.
Que mejore fuera de muestra y no introduzca
información futura.
Ventana móvil o
variables de régimen
El proceso cambió y la historia antigua dejó de ser
representativa.
Longitud de ventana o definición del régimen
mediante backtesting.
## Escalado
El regresor depende de distancias, gradientes o
penalizaciones.
El escalado no vuelve estacionaria a una serie
y no suele ser necesario para árboles.

RECOMENDACIÓN PRÁCTICA  Compare, dentro de train, el modelo sin transformar y una alternativa justificada.
Si transforma el objetivo, conserve lo necesario para invertir cada predicción y calcule las métricas finales en la
unidad original. Una distribución normal no es un requisito para los modelos de árboles.

- Referencias iniciales: antes del modelo complejo
Un modelo solo resulta útil si supera alternativas simples. Las referencias ingenuas permiten detectar
errores en el flujo y dimensionar el valor real del machine learning [1,4].

Referencia Pronóstico Adecuada cuando...
Media histórica Promedia el entrenamiento. La serie oscila alrededor de un nivel estable.
Persistencia simple Repite el último valor observado. Existe fuerte inercia de corto plazo.
Persistencia estacional Repite el valor del mismo periodo anterior. Hay patrón semanal, mensual o anual marcado.
Modelo base de ML Regresor sencillo con lags razonables. Se desea validar el flujo antes del ajuste.


Figura 9. Comparación contra referencias simples.  Elaboración propia con datos sintéticos.
DOS SIGNIFICADOS  En esta guía, baseline ingenuo significa persistencia u otra regla elemental. Modelo base
significa un regresor de machine learning con configuración inicial. Conviene reportar ambos.

- Backtesting: evaluar como si estuviéramos en el pasado
El backtesting repite el pronóstico en distintos cortes históricos. En cada corte, el modelo utiliza
solamente información anterior al origen del pronóstico y se evalúa en el bloque siguiente [2,6,7].


Figura 10. Ventanas expansiva y deslizante.  Elaboración propia con datos sintéticos.
7.1 Decisiones que deben declararse
- steps: número de pasos predichos en cada corte; debe coincidir con el uso previsto.
- initial_train_size: historia disponible antes de la primera evaluación.
- ventana: expansiva si toda la historia sigue siendo representativa; deslizante si conviene priorizar lo
reciente.
- refit: si el estimador se vuelve a entrenar en cada corte, periódicamente o nunca.
- stride: cuánto avanza el origen entre cortes.
- gap: separación necesaria cuando existe demora operativa o riesgo de contaminación temporal.
- métrica principal: criterio definido antes de observar los resultados.
NO CONFUNDIR  Actualizar la ventana con observaciones recientes permite crear nuevos lags, pero no equivale
a reentrenar el regresor. Refit significa volver a ajustar sus parámetros.

7.2 Validación interna y test final
Zona Para qué se utiliza Qué no debe hacerse
Train + validación
temporal
Comparar estrategias, lags, variables, algoritmos e
hiperparámetros.
No usar información posterior a cada corte.

Zona Para qué se utiliza Qué no debe hacerse
Test final
Estimar una vez el desempeño del modelo ya
congelado.
No cambiar la métrica ni volver a seleccionar
el modelo.
Train + test Reentrenamiento posterior para producción.
No afirmar que este modelo reentrenado fue
evaluado en test.

- Métricas: medir lo que importa
No existe una métrica universal. Debe elegirse una principal de acuerdo con el costo del error y
reportarse una o dos complementarias [8].
Métrica Qué expresa Precaución
MAE Magnitud media del error en la unidad original. No permite comparar escalas muy distintas.
RMSE Penaliza con mayor fuerza los errores grandes. Puede quedar dominado por pocos extremos.
MAPE Error absoluto relativo medio, expresado en porcentaje.
Indefinido con valores reales cero e inestable
cerca de cero. Penalización asimétrica en
términos relativos.
sMAPE Error relativo aproximadamente simétrico.
Es inestable cerca de cero y tiene variantes de
fórmula.
## MASE
MAE dividido por el error absoluto medio de una referencia
ingenua calculado en train.
Fijar el periodo estacional y calcular el
denominador solo con train. No está definido si
ese denominador es cero.
## RMSSE
Raíz del error cuadrático medio escalado por el de una
referencia ingenua en train.
Definir el periodo estacional. Denominador
calculado solo con train y distinto de cero.
Sesgo medio Indica sobrepredicción o subpredicción sistemática.
Errores positivos y negativos pueden
compensarse.

RECOMENDACIÓN  Para una serie de consumo: MAE como métrica principal interpretable, RMSE para vigilar
errores grandes y una métrica escalada o relativa para contextualizar. Declare la elección antes de abrir el test.

Ejemplo de MAPE: un error de 10 kWh representa 1 % si el valor real es 1.000 kWh, pero 1.000 % si es 1
kWh. Su asimetría es relativa: pronosticar 200 cuando se observan 100 penaliza 100 %; pronosticar 100

cuando se observan 200 penaliza 50 %. Para un mismo valor real y errores absolutos iguales, la
penalización sí es igual.
Ejemplo de MASE: si el MAE del modelo es 60 kWh y el error medio de la persistencia calculado en train
es 100 kWh, MASE = 60/100 = 0,60. Esto contextualiza la escala; no reemplaza comparar ambos
pronósticos en el mismo test [8]. MASE y RMSSE son alternativas de consulta, no métricas adicionales
obligatorias para este curso [1].
8.1 Error global y error por horizonte
En multi-step conviene calcular una métrica global reuniendo todas las predicciones y, adicionalmente,
observar el error para t+1, t+2, ..., t+h. El promedio puede ocultar que el modelo funciona bien a corto
plazo y se degrada al final del horizonte.
8.2 Gráficos que acompañan las métricas
- Serie real y pronosticada en el tiempo.
- Residuos a lo largo del periodo.
- Distribución de errores.
- Error por paso del horizonte.
- Comparación visual contra persistencia.
## EXTENSIÓN OPCIONAL: INTERVALOS DE PREDICCIÓN
Fuera del alcance exigido. Para este curso basta con obtener el pronóstico puntual del modelo de regresión y
evaluarlo, por ejemplo, con MAE y RMSE. No se exige construir intervalos, calcular cobertura ni reproducir
este gráfico.
Un número y un rango. El pronóstico puntual puede decir «mañana, 1.200 kWh». Podemos acompañarlo con
«mañana, entre 1.050 y 1.350 kWh, con un 80 % de probabilidad». Ese 80 % es el nivel que buscamos:
debemos comprobar cómo funciona en datos no utilizados para construir los intervalos [1].
¿De dónde sale el rango? Una forma es aprovechar los errores de pronósticos históricos del backtesting
dentro de train: cuánto y hacia qué lado se equivocó el modelo. Son los errores con los que también
calculamos MAE, pero ahora interesa su distribución, no solo su promedio. Para varios pasos conviene
distinguir horizontes. No basta con sumar y restar el MAE ni con usar solo los residuos del entrenamiento.
¿Qué se agrega? El intervalo acompaña al mismo pronóstico puntual; no lo reemplaza. MAE y RMSE se
calculan igual. La nueva pregunta es la cobertura: ¿qué proporción de valores observados quedó dentro? Si de
100 intervalos del 80 % entran 55 valores, la cobertura observada es 55 % y está por debajo de lo buscado. Si
entran 98, está por encima: conviene revisar si son innecesariamente anchos. Una cobertura alta no implica
por sí sola que no informen; también importa su amplitud y la cantidad de casos evaluados.


Ejemplo opcional. Ocho de diez valores reales están dentro: cobertura observada = 8/10 = 80 %. Datos y límites sintéticos,
elegidos para ilustrar; diez casos no demuestran que el intervalo esté bien calibrado en general.
Para entregar el proyecto, el resultado central sigue siendo el valor pronosticado por la regresión y su
evaluación. Este recuadro solo muestra una posible ampliación futura.
- Modelo univariante con skforecast
En el enfoque univariante se predice una serie utilizando únicamente sus valores pasados. skforecast
construye los lags, entrena un estimador compatible y genera el pronóstico. El ejemplo siguiente
muestra la forma general de la API 0.24.0; debe revisarse si se utiliza otra versión [3].
Estructura mínima de un forecaster recursivo.
from sklearn.ensemble import RandomForestRegressor
from skforecast.recursive import ForecasterRecursive

forecaster = ForecasterRecursive(
estimator=RandomForestRegressor(random_state=123),
lags=14
## )
forecaster.fit(y=y_train)
prediccion = forecaster.predict(steps=7)

9.1 Elegir lags
Elegir lags significa decidir qué valores pasados estarán disponibles como predictores. Pueden ser
consecutivos —por ejemplo, 1 a 14— o específicos —1, 2, 7, 14 y 28—.
- Partir de la frecuencia y de ciclos conocidos del dominio.
- Usar ACF, PACF y dispersión como orientación exploratoria.
- Incluir candidatos que representen memoria corta y estacionalidad relevante.
- Comparar ventanas pequeñas y justificadas mediante el mismo backtesting.

- Evitar interpretar «más lags» como «mejor modelo». Pueden agregar ruido y costo.
9.2 Regresores candidatos
## Regresor Ventaja Atención
Ridge Rápido, estable e interpretable. Captura principalmente relaciones lineales.
Random Forest Robusto y fácil de usar. Puede ser costoso y no extrapola tendencias.
XGBoost Gran capacidad no lineal y regularización.
Requiere ajustar cuidadosamente complejidad y tasa
de aprendizaje.
LightGBM Eficiente en datos grandes y muchas variables. Puede sobreajustar conjuntos pequeños.

ÁRBOLES Y TENDENCIA  Los modelos basados en árboles predicen combinando valores aprendidos dentro del
rango observado; no suelen extrapolar una tendencia creciente de manera natural. Las variables temporales,
transformaciones o estrategias de modelado deben evaluarse con cuidado.

9.3 Ajuste de lags e hiperparámetros
La búsqueda debe realizarse únicamente dentro de train. Todas las combinaciones deben compartir
folds, horizonte, política de refit y métrica principal. Una grilla pequeña y razonada suele ser más
educativa, reproducible y eficiente que una búsqueda masiva.
Esquema conceptual de búsqueda temporal; compruebe las importaciones y la versión.
cv = TimeSeriesFold(steps=7, initial_train_size=730, refit=False)
lags_grid = [7, 14, 21, 30]
param_grid = {"n_estimators": [100, 300], "max_depth": [5, 10]}

resultados = grid_search_forecaster(
forecaster=forecaster, y=y_train, cv=cv,
lags_grid=lags_grid, param_grid=param_grid,
metric="mean_absolute_error", return_best=True
## )

- Una serie objetivo con variables exógenas
En esta guía llamaremos enfoque con variables exógenas al problema en el que la variable objetivo sigue
siendo una sola, pero el modelo utiliza además calendario, clima, promociones u otra información
externa. No se aborda la predicción simultánea de múltiples series.


Figura 11. Una variable exógena puede aportar una relación no lineal.  Elaboración propia con datos sintéticos.
10.1 La prueba decisiva: disponibilidad futura
Tipo de variable Ejemplos Uso
Conocida a futuro Día, hora, feriado, promoción planificada.
Puede proporcionarse directamente para el
horizonte.
Pronosticada Temperatura, humedad, viento.
Debe usarse el pronóstico que habría estado
disponible, no el valor observado posterior.
Desconocida Venta, demanda o consumo real futuro. No puede utilizarse; generaría fuga.
Derivada del objetivo Emisiones calculadas desde el consumo futuro. No puede usarse para predecir ese mismo consumo.

ESCENARIO ORÁCULO  Evaluar con el clima realmente observado puede servir como límite ideal del aporte
meteorológico, pero no representa el desempeño operativo si en producción se usarán pronósticos con error.

10.2 Preparar y y exog
- y contiene la variable objetivo y conserva un índice temporal regular.
- exog contiene las variables adicionales alineadas exactamente con y.
- Las filas futuras de exog deben cubrir todos los steps solicitados.
- La codificación y el escalado deben aprenderse dentro de train.
- La correlación lineal orienta, pero no demuestra utilidad predictiva ni causalidad.

La misma clase puede combinar lags de y con variables exógenas.
forecaster.fit(y=y_train, exog=exog_train)

prediccion = forecaster.predict(
steps=7,
exog=exog_futuro
## )

10.3 Variables de calendario y categóricas
Mes, día de la semana y hora son variables cíclicas: diciembre está cerca de enero y domingo está cerca
de lunes. Los árboles pueden trabajar con enteros, pero una codificación categórica, one-hot o
senoidal/cosenoidal puede representar mejor esa estructura. La opción se valida, no se presupone.
10.4 Comparación justa
El modelo con exógenas debe compararse contra el mejor univariante congelado usando el mismo
periodo, horizonte, folds, refit y métricas. Una relación visual fuerte no basta: la pregunta es si mejora el
pronóstico fuera del entrenamiento.
- Evaluación final y despliegue
11.1 Congelar antes de abrir el test
Antes de evaluar, deben quedar fijados la estrategia, el algoritmo, los lags, las variables, las
transformaciones, los hiperparámetros y la métrica principal. Si se cambia cualquiera de ellos después
de mirar el test, ese conjunto deja de ser una evaluación final independiente.
11.2 Dos regímenes de evaluación
Régimen Simulación Adecuado cuando...
## Estricto
Entrenar con train y pronosticar todo test sin
incorporar sus valores reales.
El sistema emitirá una predicción larga sin
actualizaciones.
Walk-forward sin refit
Actualizar los lags con observaciones recientes sin
reajustar el regresor.
Llegan datos nuevos, pero el modelo se
reentrena con menor frecuencia.
Walk-forward con refit
Actualizar historia y volver a ajustar según una
frecuencia declarada.
La operación realmente reentrena al
avanzar.


11.3 Reentrenamiento final
Después de cerrar la evaluación, es legítimo ajustar la configuración elegida con train + test para
producción. Ese nuevo modelo aprovecha toda la historia, pero ya no es exactamente el modelo
evaluado. Debe conservarse el resultado de test como estimación histórica y registrar la fecha de
reentrenamiento.
11.4 Contrato de datos para producción
- Frecuencia, zona horaria, nombres, tipos y unidades esperadas.
- Máximo retraso admitido y tratamiento de observaciones ausentes.
- Historia mínima requerida por el mayor lag o ventana.
- Variables exógenas exigidas para todo el horizonte futuro.
- Versión de Python, skforecast y estimador.
- Semilla, fecha de entrenamiento y configuración elegida.
11.5 Guardado, monitoreo y actualización
Guardar el forecaster preserva el regresor y la configuración, pero no reemplaza la documentación. En
operación deben monitorearse el error, el sesgo, la disponibilidad de variables, los cambios de
distribución y la degradación por horizonte. El reentrenamiento puede programarse por calendario o
activarse cuando el desempeño empeora.
- Trabajar con código generado por IA
La IA puede acelerar la implementación, pero también produce código aparentemente correcto con
particiones aleatorias, fugas, versiones incompatibles o supuestos que no corresponden al caso. El
estudiante sigue siendo responsable del diseño experimental y de justificar cada decisión.
12.1 Qué debe contener una buena solicitud
- Variable objetivo, frecuencia, horizonte y momento de emisión.
- Rangos exactos de train, validación y test.
- Información disponible en cada instante y variables prohibidas por fuga.
- Estrategia recursiva o directa y política de refit.
- Baseline, métrica principal y métricas complementarias.
- Versión instalada de skforecast y del estimador.

- Solicitud explícita de explicar y comprobar el código, no solo generarlo.
12.2 Lista de revisión del código generado
## Comprobación Pregunta
Orden temporal ¿Algún split, shuffle o validación mezcla pasado y futuro?
Preprocesamiento ¿Los parámetros se estiman solo con el entrenamiento disponible?
Exógenas ¿Sus valores futuros existen realmente cuando se predice?
Horizonte ¿steps representa la unidad temporal correcta?
Backtesting ¿Los folds reproducen la operación prevista?
Test ¿Se utilizó una sola vez después de congelar decisiones?
Versión ¿Los nombres de clases y argumentos corresponden a la instalación?
Ejecución ¿El notebook funciona con «Ejecutar todo» en un entorno limpio?

RESPONSABILIDAD  Que una celda se ejecute sin error no demuestra que el experimento sea válido. La prueba
principal es si reproduce honestamente la información y las decisiones disponibles en el momento real de
pronosticar.

- Secuencia general adaptable
La siguiente secuencia funciona como mapa de trabajo. Algunos proyectos requerirán volver a etapas
anteriores; otros no necesitarán todas las transformaciones mencionadas.
## Paso Finalidad
Definir el caso de uso. Objetivo, frecuencia, horizonte, emisión y actualización.
Validar la estructura temporal. Orden, rango, duplicados, huecos, zona horaria y unidades.
Reservar el test. Tramo final independiente, antes de aprender de los valores.
Preparar train. Faltantes, atípicos, agregación y transformaciones justificadas.

## Paso Finalidad
Comprender la serie. Evolución, estacionalidad, distribuciones, autocorrelación y contexto.
Fijar el protocolo interno. Folds, steps, ventana, refit, gap y métrica principal.
Construir baselines. Persistencia simple, estacional y modelo base.
Comparar estrategias y
configuraciones.
Lags, regresores e hiperparámetros dentro de train.
Congelar el modelo. No seguir eligiendo después de abrir test.
Evaluar una vez. Mismo horizonte y régimen que el uso real.
Incorporar exógenas, si corresponde. Disponibilidad futura, alineación y comparación justa.
Reentrenar y desplegar. Toda la historia, contrato de datos, guardado y monitoreo.

- Errores frecuentes
Error Por qué es problemático
Usar train_test_split aleatorio Permite que el futuro influya en el entrenamiento.
Imputar toda la serie antes del split Los valores o parámetros de test contaminan el pasado.
Elegir el modelo mirando test El test se convierte en validación y pierde independencia.
Confundir lag con horizonte Se define una memoria que no responde al problema.
Usar toda columna disponible Puede introducir fuga, redundancia o información inexistente a futuro.
Descartar por baja correlación Pearson Ignora relaciones no lineales o retardadas.
Usar clima observado como si fuera
pronosticado
Produce una evaluación idealizada y optimista.
Aplicar una grilla enorme Aumenta costo, dificulta justificar y puede sobreajustar la validación.
Informar solo una métrica global Oculta sesgo, picos o degradación al final del horizonte.

Error Por qué es problemático
No fijar versiones El notebook puede dejar de ejecutar cuando cambia la API.

- Qué debería documentar cada proyecto
- Problema, variable objetivo, unidad, frecuencia y horizonte.
- Origen, cobertura y limitaciones de los datos.
- Integridad del índice y decisiones de limpieza.
- Partición temporal y justificación del test.
- Gráficos y hallazgos que influyeron en el modelo.
- Baselines ingenuos y modelo base.
- Protocolo de backtesting y métrica principal.
- Lags, variables, modelos e hiperparámetros comparados.
- Resultados internos y resultado final en test.
- Error global, error por horizonte y gráficos de predicción.
- Disponibilidad futura de cada variable exógena.
- Configuración final, versiones, semilla y procedimiento de despliegue.
- Limitaciones y mejoras futuras.
Lista final de comprobación
✓ Antes de entregar
□ El índice es temporal, está ordenado y tiene frecuencia comprobada.
□ El test se reservó antes del preprocesamiento aprendido.
□ Toda imputación o transformación está justificada y no mira el futuro.
□ Existen persistencia simple y/o estacional como referencia.
□ La selección se realizó mediante backtesting dentro de train.
□ La métrica principal se definió antes de evaluar test.

✓ Antes de entregar
□ Las exógenas estarán disponibles para todo el horizonte.
□ El modelo fue comparado con el mismo periodo, folds y métricas.
□ Se reporta error global y se inspecciona el error por horizonte.
□ El notebook ejecuta de principio a fin y registra versiones.
□ El reentrenamiento de producción está separado de la evaluación.

## Referencias
[1] Hyndman, R. J., y Athanasopoulos, G. (2021). Forecasting: Principles and Practice (3.ª ed.). OTexts. https://otexts.com/fpp3/
Apartados 5.5 (intervalos) y 5.8 (métricas): https://otexts.com/fpp3/prediction-intervals.html y
https://otexts.com/fpp3/accuracy.html
[2] Cerqueira, V., Torgo, L., y Mozetič, I. (2020). Evaluating time series forecasting models: an empirical study on performance
estimation methods. Machine Learning, 109, 1997–2028. https://doi.org/10.1007/s10994-020-05910-7
[3] skforecast Developers (2026). skforecast documentation, versión 0.24.0. https://skforecast.org/  (consulta: 6 de septiembre
de 2026).
[4] skforecast Developers (2026). Baseline forecaster. https://skforecast.org/latest/user_guides/forecasting-baseline.html
[5] skforecast Developers (2026). Direct multi-step forecasting. https://skforecast.org/latest/user_guides/direct-multi-step-
forecasting.html
[6] skforecast Developers (2026). Backtesting forecaster. https://skforecast.org/latest/user_guides/backtesting.html
[7] Bergmeir, C., Hyndman, R. J., y Koo, B. (2018). A note on the validity of cross-validation for evaluating autoregressive time
series prediction. Computational Statistics & Data Analysis, 120, 70–83. https://doi.org/10.1016/j.csda.2017.11.003
[8] Hyndman, R. J., y Koehler, A. B. (2006). Another look at measures of forecast accuracy. International Journal of Forecasting,
22(4), 679–688. https://doi.org/10.1016/j.ijforecast.2006.03.001
Lecturas recomendadas y materiales de apoyo
Bontempi, G., Ben Taieb, S., y Le Borgne, Y.-A. (2013). Machine Learning Strategies for Time Series Forecasting. En Business
Intelligence (pp. 62–77). Springer. https://doi.org/10.1007/978-3-642-36318-4_3
Géron, A. (2023). Aprende machine learning con Scikit-Learn, Keras y TensorFlow (3.ª ed.). Anaya Multimedia.
Amat Rodrigo, J., y Escobar Ortiz, J. (2024). Skforecast: forecasting series temporales con Python, Machine Learning y Scikit-
learn. Ciencia de Datos. https://cienciadedatos.net/documentos/py27-forecasting-series-temporales-python-scikitlearn

scikit-learn Developers (2026). Lagged features for time series forecasting. https://scikit-
learn.org/stable/auto_examples/applications/plot_time_series_lagged_features.html
Palma Méndez, J. T., y Martínez España, R. (2024/2025). Predicción de Series Temporales. Material del Máster Universitario en
Inteligencia Artificial, Universidad de Murcia.
Cuña, P. (2026). Series temporales y pronóstico. Material docente de Aprendizaje Automático II, Licenciatura en Ingeniería de
Datos e Inteligencia Artificial, Universidad Tecnológica.
NOTA DE VERSIÓN  skforecast evoluciona con rapidez. Antes de ejecutar ejemplos, consulte la documentación
de la versión instalada. En la versión 0.24.0 la API principal utiliza el argumento estimator en clases como
ForecasterRecursive y ForecasterDirect.
