# train/

Versiones `.py` de los notebooks base, listas para enviarse a la cola del servidor. Ver
`documentacion/Guia_entrenamientos_CPU_GPU.md` para el sistema de envío (`submit_cpu`/`submit_gpu`)
y para dónde quedan logs y resultados.

| Script | Notebook de origen | Comando de envío | GPU |
| --- | --- | --- | --- |
| `train_base.py` | `notebooks/base.ipynb` | `submit_cpu train_base.py` | No |
| `train_base_2.py` | `notebooks/base_2.ipynb` | `submit_cpu train_base_2.py` | No |
| `diagnostico_entorno.py` | — (utilitario) | `submit_cpu diagnostico_entorno.py`, sólo para depurar | No |

**Por qué CPU y no GPU.** Los dos notebooks entrenan un único `DecisionTreeRegressor` de
scikit-learn. Ese algoritmo no tiene implementación GPU, y con ~1.300-1.600 filas de entrenamiento
tampoco habría cómputo que acelerar. Enviarlos con `submit_gpu` reservaría un nodo con GPU sin
usarla, lo que la guía pide evitar (sección 14, punto 8). Cuando el proyecto pruebe familias con
soporte GPU real (una red neuronal, boosting con `device="cuda"`), ese script sí debería enviarse
con `submit_gpu`.

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

**Sin `skforecast` en `train_base_2.py`.** El notebook `base_2.ipynb` arma los rezagos y la
predicción recursiva con `skforecast.ForecasterRecursive`. En el servidor eso no era viable
(no está instalado, `/work` no es escribible para vendorizarlo, y `skforecast 0.25.0` exige
`numpy>=1.26 / pandas>=2.1 / scikit-learn>=1.4`, por encima de lo que trae el contenedor). Por eso
`train_base_2.py` hace lo mismo a mano con `numpy`/`pandas` (`matriz_rezagos` y
`predecir_recursivo`). **Se comprobó que da lo mismo:** corrido en local junto a la versión con
`skforecast`, las siete tablas de resultados salen idénticas byte a byte. Como efecto lateral,
desaparece el conflicto `skforecast` vs. `pandas 3` anotado en `HANDOFF.md` para este script.

**Dato de entrada:** ambos scripts leen `data/processed/panel_zona_top.csv` (no se versiona en
git; generarlo con `notebooks/preparacion_montevideo.ipynb` o copiarlo manualmente antes de
enviar el trabajo).

**Resultados.** Cada corrida escribe en una carpeta propia dentro de `/outputs/runs/<RUN_ID>/`
(convención de la guía), con los mismos nombres de tabla/figura que el notebook correspondiente.
Para que `documentacion/resumen_base.md` y `documentacion/resumen_base_2.md` sigan citando las
rutas vigentes (`experiments/base/...`, `experiments/base_2/...`), copiar manualmente el contenido
de `tablas/` y `figuras/` de la corrida elegida a esas carpetas del repositorio.

**Cómo verificar una corrida del servidor.** Los valores esperados en el conjunto de prueba
(desvianza de Poisson) son: `train_base.py` → 1,2625 (media constante), 1,0848 (tasa × calendario),
1,6789 (árbol); `train_base_2.py` → 1,262 (media constante), 1,332 (línea base), 3,462 (árbol),
5,007 (repetir semana anterior). El contenedor trae `scikit-learn 1.2.0` (localmente se probó con
1.9.0), así que conviene comparar: si difiere en algo, es la primera pista a revisar.
