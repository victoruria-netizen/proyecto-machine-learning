# train/

Scripts `.py` listos para enviarse a la cola del servidor. Ver
`documentacion/Guia_entrenamientos_CPU_GPU.md` para el sistema de envío (`submit_cpu`/`submit_gpu`)
y para dónde quedan logs y resultados.

| Script | Notebook de origen | Comando de envío | GPU |
| --- | --- | --- | --- |
| `diagnostico_entorno.py` | — (utilitario) | `submit_cpu diagnostico_entorno.py`, sólo para depurar | No |
| `train_modelo_final.py` | `notebooks/evaluacion_final.ipynb`, sección 13 (exportación del modelo final, D51) | `submit_cpu train_modelo_final.py` | No |

## `train_modelo_final.py` — modelo final del Entregable 3 (D51, D56)

Entrena la solución (GLM Poisson (a), ventana deslizante de 364 días) con todos los datos hasta el 2025-12-31 y
compara el resultado con la exportación local (`models/modelo_final.json`): diferencia relativa máxima ≤ 1e-6 en los
coeficientes, en μ de las 56 filas de la semana del 01/01/2026 y en α. **Es una excepción declarada a la regla de
lectura del bloque final (D51):** lee el panel completo para entrenar y no calcula ninguna métrica.

No importa `src/`: el contenedor tiene pandas 1.5.3 (sin `stack(future_stack=True)`) y no tiene statsmodels ni
`holidays`. Arma la matriz del conjunto (a) con numpy y pandas, ajusta el GLM con IRLS en numpy y calcula α por
momentos (plan B de D28; NB2 por máxima verosimilitud no se intenta). `tests/test_train_modelo_final.py` exige, con el
panel de desarrollo, que la matriz sea idéntica a la de `src/` y que coeficientes, μ y α queden dentro de 1e-6 de
statsmodels.

**Estructura dentro de `/train`** (Jupyter; `Guia_entrenamientos_CPU_GPU.md`, §1). El script resuelve todas sus
entradas relativas a su propia carpeta (`Path(__file__).parent`) e imprime las rutas resueltas al arrancar:

```
/train/
├── train_modelo_final.py
├── data/
│   └── processed/
│       └── panel_diario_montevideo.csv      (no se versiona: copiarlo desde la copia local)
└── models/
    ├── modelo_final.json                    (exportación local, para la comparación)
    └── metadata.json                        (sha256 esperado del panel)
```

**Antes de enviarlo:**

1. Copiar `train/train_modelo_final.py` del repositorio a `/train/train_modelo_final.py`.
2. Crear `/train/data/processed/` y subir ahí el panel (*Upload* del explorador de archivos de Jupyter). El script
   verifica su sha256 contra `models/metadata.json` y se detiene si no coincide.
3. Crear `/train/models/` y subir `models/modelo_final.json` y `models/metadata.json`. Sin `modelo_final.json`, el
   script entrena igual pero avisa que no compara; sin `metadata.json`, usa el sha256 del panel fijado en el script.
4. Desde la terminal de Jupyter, en `/train`: `submit_cpu train_modelo_final.py` (sólo el nombre del archivo; guía, §4).

**Después:** el log queda en `/train/outputs/logs/<SLURM_JOB_NAME>_<SLURM_JOB_ID>.out` y los resultados en
`/train/outputs/runs/<RUN_ID>/`: `run_info.txt` (guía, §11: `run_id`, `slurm_job_id`, `slurm_job_name`,
`slurm_log_file`, `slurm_cpus_per_task`, `output_dir`), `modelo_final.json`, `prediccion_semana_2026-01-01.csv` y
`resumen_corrida.json`. Guardar el log en `documentacion/logs/log_servidor_modelo_final.txt`. La corrida está bien si
el log dice `Criterio (<= 1e-06 en todo): CUMPLE` y el trabajo termina con código 0 (si no cumple, sale con código 1).

**Nota (2026-09-24):** `train_base.py` y `train_base_2.py` (versiones de `notebooks/base.ipynb` y
`notebooks/base_2.ipynb`) se retiraron junto con esos notebooks, unificados en
`notebooks/linea_base.ipynb`. Quedan preservados en la rama `entregable_2`. Si hace falta
reconstruir una versión `.py` de `linea_base.ipynb` para la cola del servidor, partir de esos dos
como referencia (mismo patrón: sólo lectura de `/work`, escritura en `/outputs/runs/<RUN_ID>/`,
dependencias limitadas a lo que trae el contenedor).

**Logs de esas corridas:** `documentacion/logs/log_servidor_base.txt` (Job 104, `train_base.py`,
18/09/2026, RUN_ID `20260918_124207`) es la fuente del Anexo F.1 del informe — coincide cifra por
cifra con esa tabla. `documentacion/logs/log_servidor_base2.txt` (Job 108, `train_base_2.py`,
18/09/2026, RUN_ID `20260918_132608`) es una corrida adicional que el informe no cita.

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
bloque final): media constante 1,2625; L0 1,3324; L1 (tasa × calendario) 1,0848; árbol
candidato preliminar 1,6789 (`experiments/linea_base/tablas/05_evaluacion_test.csv`). El
contenedor trae `scikit-learn 1.2.0` (localmente se probó con 1.9.0), así que conviene comparar:
si difiere en algo, es la primera pista a revisar.
