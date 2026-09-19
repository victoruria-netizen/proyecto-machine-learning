## Guía para estudiantes: ejecución de entrenamientos con CPU/GPU

Esta guía explica cómo enviar, seguir mediante logs y cancelar scripts de entrenamiento mediante el sistema de cola configurado.

Aclaración: El estudiante no ejecuta directamente la CPU/GPU ni Slurm. Solo deja solicitudes mediante comandos controlados. Luego el sistema toma esas solicitudes automáticamente y las procesa.

## 1. Ubicación de trabajo

Los scripts de entrenamiento deben estar dentro de la carpeta de trabajo del grupo en Jupyter:

```
/train
```

Ejemplos de scripts válidos:

```
/train/train_modelo.py
/train/train_keras_test.py
/train/train_cpu_test.py
```

Desde la terminal de Jupyter, normalmente se debe trabajar dentro de la carpeta /train o indicar solamente el nombre del archivo al usar los comandos submit_gpu o submit_cpu.

## 2. Entrenamiento con GPU

Para trabajos que requieren GPU se debe usar:

```
submit_gpu nombre_script.py
```

Ejemplo:

```
submit_gpu train_keras_test.py
```

El archivo indicado debe existir dentro de /train.

## 3. Entrenamiento con CPU

Para trabajos que no requieren GPU se debe usar:

```
submit_cpu nombre_script.py
```

Ejemplo:

```
submit_cpu train_cpu_test.py
```

Cada trabajo CPU se ejecuta en la partición CPU del servidor y tiene recursos controlados por Slurm.

## Uso de n_jobs en trabajos CPU

En este tipo de entrenamientos es importante evitar configuraciones que intenten usar todos los procesadores disponibles del servidor. Por ejemplo, no se recomienda usar:

```
n_jobs=-1
```

Aunque el sistema define límites de paralelismo para las bibliotecas más comunes, el uso de n_jobs=-1 puede provocar un consumo excesivo de CPU en algunos casos, afectando el rendimiento de otros trabajos, de Jupyter, Streamlit o de los servicios del servidor.


La forma recomendada es tomar la cantidad de CPUs asignadas por Slurm desde la variable de entorno SLURM_CPUS_PER_TASK:

```
import os
N_JOBS = int(os.environ.get("SLURM_CPUS_PER_TASK", "1"))
```

Por ejemplo, en un modelo Random Forest:

```
from sklearn.ensemble import RandomForestRegressor
model = RandomForestRegressor(
n_estimators=300,
n_jobs=N_JOBS,
random_state=42
)
```

De esta manera, el entrenamiento respeta los recursos asignados al trabajo y permite un uso más ordenado del servidor compartido.

## 4. Restricciones de los comandos submit_gpu y submit_cpu

Por seguridad y para facilitar la ejecución, los comandos solo aceptan el nombre del archivo Python. No se deben indicar rutas completas ni carpetas.

## Correcto:

```
submit_gpu train_modelo.py
submit_cpu train_cpu_test.py
```

Incorrecto:

```
submit_gpu /train/train_modelo.py
submit_cpu carpetas/train_modelo.py
submit_gpu ../train_modelo.py
```

El archivo debe tener extensión .py.

## 5. Qué ocurre después de ejecutar submit_gpu o submit_cpu

Al ejecutar submit_gpu o submit_cpu, se crea una solicitud de entrenamiento en:

```
/train/requests
```

Por ejemplo:

```
/train/requests/grp10_train_keras_test_20260805_175639.submit
/train/requests/grp10_train_cpu_test_20260806_151512.cpu
```

Ese archivo indica al sistema qué script debe ejecutarse. Luego, automáticamente, el servidor revisa las solicitudes pendientes y envía el entrenamiento a la cola correspondiente.


Importante: submit_gpu y submit_cpu no ejecutan el entrenamiento inmediatamente en la terminal de Jupyter. Solo crean la solicitud. Si los recursos están ocupados, el trabajo puede quedar esperando hasta que se liberen.

## 6. Cómo cancelar un entrenamiento GPU

Si se envió un entrenamiento GPU y se quiere cancelar por algún motivo, antes o durante su ejecución, se puede solicitar la cancelación del trabajo GPU del grupo con:

```
cancel_gpu
```

Este comando crea una solicitud de cancelación en la misma carpeta de solicitudes:

```
/train/requests
```

Por ejemplo:

/train/requests/grp10_cancel_gpu_20260805_144940.cancel

Luego el sistema procesa esa solicitud automáticamente.

## Qué cancela cancel_gpu

- Cancela trabajos GPU en ejecución o en cola del propio grupo.

- No cancela trabajos CPU.

- No cancela trabajos de otros grupos.

- No genera error si el grupo no tiene ningún trabajo GPU en ejecución o en cola; simplemente no habrá nada para cancelar.

## 7. Cómo cancelar un entrenamiento CPU

Si se envió un entrenamiento CPU y se quiere cancelar por algún motivo, antes o durante su ejecución, se puede solicitar la cancelación del trabajo CPU del grupo con:

```
cancel_cpu
```

Este comando crea una solicitud de cancelación en:

```
/train/requests
```

Por ejemplo:

/train/requests/grp10_cancel_cpu_20260806_152500.cancel_cpu

Luego el sistema procesa esa solicitud automáticamente.

## Qué cancela cancel_cpu

- Cancela trabajos CPU en ejecución o en cola del propio grupo.

- No cancela trabajos GPU.

- No cancela trabajos de otros grupos.

- No genera error si el grupo no tiene ningún trabajo CPU en ejecución o en cola; simplemente no habrá nada para cancelar.


## 8. Aclaraciones sobre la cancelación

La cancelación no es necesariamente inmediata. Los comandos cancel_gpu y cancel_cpu crean una solicitud que será procesada automáticamente por el servidor.

Si el trabajo está en espera, será cancelado en la cola cuando el sistema procese la solicitud. Si el trabajo comienza a ejecutarse antes de que la solicitud sea procesada, será cancelado durante la ejecución.

Si el entrenamiento ya estaba en ejecución, puede quedar un archivo .out en /train/outputs/logs indicando que el trabajo fue cancelado. Además, si el script ya había creado una carpeta dentro de /train/outputs/runs/, esa carpeta puede quedar guardada con resultados parciales. Esto es normal. La cancelación no borra automáticamente los archivos que el entrenamiento haya alcanzado a guardar.

Si el entrenamiento todavía estaba en espera en la cola y no había comenzado a ejecutarse, puede no generarse archivo .out ni carpeta de resultados, porque el script Python nunca llegó a iniciarse. En ese caso, la cancelación fue válida igualmente.

Una carpeta en /train/outputs/runs/ no significa necesariamente que el entrenamiento terminó correctamente. Para confirmarlo, se debe revisar el archivo .out correspondiente y los archivos de métricas generados por el script.

## Qué ocurre con los archivos de cancelación

Cuando el sistema procesa una solicitud de cancelación, el archivo correspondiente se mueve desde requests hacia submitted. Esto significa que la solicitud fue procesada por el sistema. No significa que el entrenamiento haya terminado correctamente.

```
requests/ -> solicitudes pendientes
submitted/ -> solicitudes procesadas por el sistema
rejected/ -> solicitudes inválidas o rechazadas
```

El archivo .out del entrenamiento puede mostrar un mensaje de cancelación generado por Slurm, por ejemplo:

```
slurmstepd: error: *** JOB 37 ON lidia CANCELLED ***
```

El mensaje exacto puede variar según el momento en que se cancele el trabajo.

## 9. Dónde quedan los resultados

Los resultados del entrenamiento deben guardarse en la carpeta de salida del grupo. Desde Jupyter, esa carpeta se ve como:

```
/train/outputs
```

Dentro del script Python ejecutado por el sistema, esa misma carpeta se accede como:

```
/outputs
```

Por eso, dentro del código Python se recomienda guardar los resultados usando /outputs. Desde Jupyter, esos mismos archivos se podrán ver navegando a /train/outputs.

Para evitar sobrescribir resultados de ejecuciones anteriores, se recomienda que cada entrenamiento guarde sus archivos dentro de una carpeta propia en:

```
/outputs/runs
```


Por ejemplo, dentro del script Python:

```
/outputs/runs/20260805_141500/
```

Desde Jupyter, esa misma ejecución se verá en:

```
/train/outputs/runs/20260805_141500/
```

## 10. Ejemplo recomendado en Python

Se recomienda crear automáticamente una carpeta por ejecución usando fecha y hora. De esta forma, cada entrenamiento conserva sus modelos, métricas y gráficos sin reemplazar archivos anteriores.

```
from pathlib import Path
from datetime import datetime
RUN_ID = datetime.now().strftime("%Y%m%d_%H%M%S")
OUTPUT_DIR = Path("/outputs") / "runs" / RUN_ID
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
modelo_path = OUTPUT_DIR / "modelo_entrenado.keras"
metricas_path = OUTPUT_DIR / "metricas.txt"
grafico_loss_path = OUTPUT_DIR / "loss.png"
print("Carpeta de resultados:", OUTPUT_DIR, flush=True)
```

## 11. Guardar información de la ejecución: run_info.txt

Para relacionar la carpeta de resultados con el log del sistema, se recomienda que cada entrenamiento guarde un archivo run_info.txt dentro de OUTPUT_DIR.

```
import os
SLURM_JOB_ID = os.environ.get("SLURM_JOB_ID", "no_slurm")
SLURM_JOB_NAME = os.environ.get("SLURM_JOB_NAME", "no_slurm")
SLURM_CPUS = os.environ.get("SLURM_CPUS_PER_TASK", "no_definido")
CUDA_VISIBLE_DEVICES = os.environ.get("CUDA_VISIBLE_DEVICES", "no_definido")
LOG_FILE = f"/outputs/logs/{SLURM_JOB_NAME}_{SLURM_JOB_ID}.out"
with open(OUTPUT_DIR / "run_info.txt", "w") as f:
f.write(f"run_id={RUN_ID}\n")
f.write(f"slurm_job_id={SLURM_JOB_ID}\n")
f.write(f"slurm_job_name={SLURM_JOB_NAME}\n")
f.write(f"slurm_log_file={LOG_FILE}\n")
f.write(f"slurm_cpus_per_task={SLURM_CPUS}\n")
f.write(f"cuda_visible_devices={CUDA_VISIBLE_DEVICES}\n")
f.write(f"output_dir={OUTPUT_DIR}\n")
```

Ejemplo de contenido esperado:

```
run_id=20260805_141500
slurm_job_id=37
slurm_job_name=grp10_train_keras_test
```


```
slurm_log_file=/outputs/logs/grp10_train_keras_test_37.out
slurm_cpus_per_task=4
cuda_visible_devices=0
output_dir=/outputs/runs/20260805_141500
```

## 12. Dónde quedan los logs y cómo ver el avance

Cada vez que se ejecuta un entrenamiento, el sistema genera un archivo de log dentro de:

```
/train/outputs/logs
```

Allí aparecen archivos con extensión .out, por ejemplo:

```
grp10_train_keras_test_15.out
grp10_cpu_train_cpu_test_34.out
```

El nombre del archivo de log se forma aproximadamente así:

```
grupo_nombreDelScript_numeroJob.out
```

El archivo de log se va generando durante la ejecución del entrenamiento. No es necesario esperar a que el entrenamiento termine para verlo. Desde Jupyter, se puede hacer clic sobre el archivo .out para abrirlo y revisar el avance.

El log puede incluir:

- inicio del entrenamiento

- nombre del script ejecutado

- partición utilizada, CPU o GPU

- GPU asignada, si corresponde

- CPUs asignadas

- épocas del entrenamiento

- loss, mae u otras métricas

- mensajes escritos con print()

- errores, si los hubo

- mensajes de cancelación, si el trabajo fue cancelado

- finalización del entrenamiento

Para que la información aparezca correctamente en el log, se recomienda que el script imprima mensajes importantes durante la ejecución.

```
print("Entrenamiento iniciado", flush=True)
print("Cargando datos...", flush=True)
print("Entrenamiento finalizado", flush=True)
```

En entrenamientos con Keras, se recomienda usar verbose=1 para que se muestren las épocas y métricas:

```
history = model.fit(
X_train,
y_train,
epochs=20,
batch_size=32,
verbose=1
)
```


## 13. Aclaración sobre sobrescritura de resultados

Los archivos de log generados por el sistema no se sobrescriben, ya que cada ejecución crea un archivo .out diferente con el número de job correspondiente. Por ejemplo, si se ejecuta varias veces el mismo script, se generarán logs como:

```
grp10_train_modelo_21.out
grp10_train_modelo_22.out
```

Sin embargo, los resultados que guarde el propio script Python sí pueden sobrescribirse si se usa siempre el mismo nombre de archivo, por ejemplo modelo.keras, metricas.txt o loss.png. Por eso se recomienda guardar cada ejecución dentro de una carpeta propia en /outputs/runs/<RUN_ID>/.

## 14. Recomendaciones para el script de entrenamiento

- 1. Guardar los resultados en una carpeta propia dentro de /outputs/runs/.

- 2. Crear un archivo run_info.txt con el número de job de Slurm y el archivo de log asociado.

- 3. Imprimir información relevante durante la ejecución usando flush=True.

- 4. Guardar métricas finales dentro de OUTPUT_DIR.

- 5. Guardar el modelo entrenado dentro de OUTPUT_DIR.

- 6. Evitar guardar todos los resultados directamente en /outputs con nombres fijos.

- 7. En trabajos CPU, usar SLURM_CPUS_PER_TASK para definir n_jobs en lugar de n_jobs=-1.

- 8. Usar submit_gpu solo para trabajos que realmente aprovechen GPU y submit_cpu para trabajos sin GPU.

## 15. Resumen de comandos

```
submit_gpu nombre_script.py
cancel_gpu
submit_cpu nombre_script.py
cancel_cpu
```

submit_gpu y cancel_gpu trabajan sobre la cola GPU del grupo. submit_cpu y cancel_cpu trabajan sobre la cola CPU del grupo.
