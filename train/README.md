# train/

Scripts `.py` listos para enviarse a la cola del servidor. Ver
`documentacion/Guia_entrenamientos_CPU_GPU.md` para el sistema de envío (`submit_cpu`/`submit_gpu`)
y para dónde quedan logs y resultados.

| Script | Notebook de origen | Comando de envío | GPU |
| --- | --- | --- | --- |
| `diagnostico_entorno.py` | — (utilitario) | `submit_cpu diagnostico_entorno.py`, sólo para depurar | No |

**Nota (2026-09-24):** `train_base.py` y `train_base_2.py` (versiones de `notebooks/base.ipynb` y
`notebooks/base_2.ipynb`) se retiraron junto con esos notebooks, unificados en
`notebooks/linea_base.ipynb`. Quedan preservados en la rama `entregable_2`. Si hace falta
reconstruir una versión `.py` de `linea_base.ipynb` para la cola del servidor, partir de esos dos
como referencia (mismo patrón: sólo lectura de `/work`, escritura en `/outputs/runs/<RUN_ID>/`,
dependencias limitadas a lo que trae el contenedor).

**Por qué CPU y no GPU** (aplica a cualquier script que entrene el árbol candidato).
`DecisionTreeRegressor` de scikit-learn no tiene implementación GPU, y con ~1.300-1.600 filas de
entrenamiento tampoco habría cómputo que acelerar. Enviarlo con `submit_gpu` reservaría un nodo
con GPU sin usarla, lo que la guía pide evitar (sección 14, punto 8). Cuando el proyecto pruebe
familias con soporte GPU real (una red neuronal, boosting con `device="cuda"`), ese script sí
debería enviarse con `submit_gpu`.

**Cómo es el entorno donde corren los trabajos** (medido con `diagnostico_entorno.py` el
2026-09-18, no sacado de la documentación):

- `submit_cpu` ejecuta el script dentro de un contenedor Apptainer fijo
  (`tensorflow_ngc_24.04_tf2_py3_mlcv.sif`, Python 3.10 del sistema), **separado** del entorno de la
  terminal de Jupyter: instalar algo con `pip` en Jupyter no tiene efecto sobre los trabajos.
- **`/work` (donde vive `train/`) es de sólo lectura**; el único mount escribible es `/outputs`.
  Por eso los scripts sólo leen de `/work` y escriben todo en `/outputs/runs/<RUN_ID>/`.
- Versiones que trae el contenedor: `numpy 1.24.4`, `pandas 1.5.3`, `scikit-learn 1.2.0`,
  `matplotlib 3.10.9`. **Los scripts tienen que depender sólo de eso**: agregar una librería
  significa que el equipo del servidor la instale en la imagen, no instalarla desde acá.

**Dato de entrada:** los scripts que entrenen sobre la serie de MUNICIPIO C leen
`data/processed/panel_zona_top.csv` (no se versiona en git; generarlo con
`notebooks/preparacion_montevideo.ipynb` o copiarlo manualmente antes de enviar el trabajo).

**Resultados.** Cada corrida escribe en una carpeta propia dentro de `/outputs/runs/<RUN_ID>/`
(convención de la guía), con los mismos nombres de tabla/figura que el notebook correspondiente.
Para que `documentacion/resumen_linea_base.md` siga citando las rutas vigentes
(`experiments/linea_base/...`), copiar manualmente el contenido de `tablas/` y `figuras/` de la
corrida elegida a esa carpeta del repositorio.

**Cómo verificar una corrida del servidor** (valores de referencia, desvianza de Poisson en el
conjunto de prueba): media constante 1,2625; L0 1,3324; L1 (tasa × calendario) 1,0848; árbol
candidato preliminar 1,6789 (`experiments/linea_base/tablas/05_evaluacion_test.csv`). El
contenedor trae `scikit-learn 1.2.0` (localmente se probó con 1.9.0), así que conviene comparar:
si difiere en algo, es la primera pista a revisar.
