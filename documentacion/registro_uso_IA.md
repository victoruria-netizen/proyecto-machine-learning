# Registro de uso de IA generativa

Este archivo documenta, de forma incremental durante todo el proyecto, el uso de
herramientas de inteligencia artificial generativa, conforme a la sección 4.3 de la
*Guía para estudiantes PAA 2026*.

## Declaración

> _(Indicar explícitamente si se utilizaron o no herramientas de IA generativa en el
> proyecto.)_

En este proyecto **sí** se utilizaron herramientas de IA generativa como apoyo. Todo
contenido incorporado fue revisado, comprendido, adaptado y verificado por el equipo.

## Registro de interacciones

Para cada uso relevante que haya incidido en el código, el análisis, la documentación o
una decisión importante, se completa una entrada con el siguiente formato:

---

### Entrada 1

- **Fecha:** 2026-08-04
- **Herramienta:** Claude Code (Anthropic)
- **Integrante responsable:** _(completar)_
- **Prompt relevante:**
  > Inicializar la estructura de carpetas del repositorio según la guía del PAA 2026 y
  > realizar el primer push al repositorio de GitHub.
- **Respuesta relevante:**
  > Creación de la estructura recomendada (data/, notebooks/, src/, models/,
  > experiments/, app/, documentacion/, tests/), archivos base (README.md,
  > registro_uso_IA.md, requirements.txt, .gitignore) e inicialización del repositorio.
- **Cómo se utilizó / verificó:**
  > La estructura fue revisada contra la sección 4.1 de la guía. El equipo verificó el
  > contenido de cada archivo y confirmó el push al repositorio.

---

### Entrada 2

- **Fecha:**
- **Herramienta:**
- **Integrante responsable:**
- **Prompt relevante:**
- **Respuesta relevante:**
- **Cómo se utilizó / verificó:**

---

## Protección de datos

No se compartieron con estas herramientas datos personales, sensibles, confidenciales o
restringidos sin autorización.


### Desicion de coordenadas en resampling
prompt: Quiero hacer un resampling diario en mi df, que me recomendas hacer con las coordenadas que tengo en mi dataset, el sistema de coordenadas es UTM, tengo x e y, estas son las columnas de mi dataset: Calle, Tipo de Siniestro, Gravedad, Dia, Semana, Hora, Departamento, Localidad, fixed, X, Y. 
Este es el objetivo de nuestro proyecto:
Objetivo general. Desarrollar un modelo de aprendizaje automático para la predicción de siniestros de tránsito a partir de series temporales e integrar sus resultados en una interfaz que permita visualizar las zonas y períodos con mayor cantidad esperada de siniestros.

Respuesta:
Ustedes no están haciendo solamente una serie temporal de cantidad total de siniestros, sino que quieren terminar mostrando “zonas y períodos con mayor cantidad esperada”.

Por lo tanto, yo plantearía el dataset como un problema espacio-temporal.

La estructura que buscaría

En vez de:

1 fila = 1 siniestro

pasaría a:

1 fila = 1 día × 1 zona

Por ejemplo:

Día	Zona	Cantidad
2025-01-01	Z001	4
2025-01-01	Z002	0
2025-01-01	Z003	7
2025-01-02	Z001	3
2025-01-02	Z002	2
2025-01-02	Z003	5

Eso encaja muchísimo mejor con el objetivo de visualizar posteriormente las zonas de mayor riesgo.

¿Qué hago con X e Y?

Acá no recomiendo hacer un promedio diario de X e Y.

Por ejemplo, esto:

df.groupby("Dia")[["X", "Y"]].mean()

no sería una buena representación espacial. Podrías tener 30 accidentes en distintos puntos y obtener un único punto promedio que no representa realmente ninguna zona de riesgo.

En su lugar: crear una grilla espacial

Como tus coordenadas son UTM, tenés una ventaja enorme: X e Y están en metros.

Podrías dividir el territorio en celdas, por ejemplo:

500 m × 500 m

Entonces:

tam_celda = 500

df["grid_x"] = (df["X"] // tam_celda) * tam_celda
df["grid_y"] = (df["Y"] // tam_celda) * tam_celda

Cada siniestro queda asignado a una zona.

Por ejemplo:

X       Y          grid_x   grid_y
523421  6578123    523000   6578000
523450  6578200    523000   6578000
524100  6579000    524000   6579000

Los dos primeros pertenecen a la misma celda.

Después viene el resampling diario

Una vez creada la zona:

df["Dia"] = pd.to_datetime(df["Dia"])

df_diario = (
    df.groupby(["Dia", "grid_x", "grid_y"])
      .size()
      .reset_index(name="Cantidad_siniestros")
)

Pero todavía falta algo importante.

Supongamos que una zona tuvo:

01/01 → 4
02/01 → 3
04/01 → 5

Necesitás que el dataset tenga:

01/01 → 4
02/01 → 3
03/01 → 0
04/01 → 5

Y además, si una zona existe en tu territorio pero un día no tuvo ningún accidente, también debería aparecer con 0.

Esto es fundamental para que el modelo pueda aprender correctamente.

¿Qué tendría finalmente?

Algo así:

Dia         grid_x   grid_y    Cantidad_siniestros
2025-01-01  523000   6578000  4
2025-01-01  523500   6578000  0
2025-01-01  524000   6578000  7
2025-01-02  523000   6578000  3
2025-01-02  523500   6578000  2
2025-01-02  524000   6578000  5
...

Y esa sería la variable objetivo:

Cantidad_siniestros