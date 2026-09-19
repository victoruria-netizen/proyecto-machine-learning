from pathlib import Path
from datetime import datetime
import tensorflow as tf
from tensorflow import keras
import numpy as np
import pandas as pd
import sklearn
import matplotlib.pyplot as plt
import cv2
import os
import time

print("TensorFlow:", tf.__version__)
print("GPUs disponibles:", tf.config.list_physical_devices("GPU"))
print("NumPy:", np.__version__)
print("Pandas:", pd.__version__)
print("Scikit-learn:", sklearn.__version__)
print("OpenCV:", cv2.__version__)

RUN_ID = datetime.now().strftime("%Y%m%d_%H%M%S")
OUTPUT_DIR = Path("/outputs") / "runs" / RUN_ID
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

SLURM_JOB_ID = os.environ.get("SLURM_JOB_ID", "no_slurm")
SLURM_JOB_NAME = os.environ.get("SLURM_JOB_NAME", "no_slurm")
LOG_FILE = f"/outputs/logs/{SLURM_JOB_NAME}_{SLURM_JOB_ID}.out"

with open(OUTPUT_DIR / "run_info.txt", "w") as f:
    f.write(f"run_id={RUN_ID}\n")
    f.write(f"output_dir={OUTPUT_DIR}\n")
    f.write(f"slurm_job_id={SLURM_JOB_ID}\n")
    f.write(f"slurm_job_name={SLURM_JOB_NAME}\n")
    f.write(f"slurm_log_file={LOG_FILE}\n")

X = np.random.rand(1000, 10)
y = np.random.rand(1000, 1)

model = keras.Sequential([
    keras.layers.Input(shape=(10,)),
    keras.layers.Dense(32, activation="relu"),
    keras.layers.Dense(16, activation="relu"),
    keras.layers.Dense(1)
])

model.compile(optimizer="adam", loss="mse", metrics=["mae"])

history = model.fit(
    X,
    y,
    epochs=3,
    batch_size=32,
    verbose=1
)

model.save(OUTPUT_DIR / "modelo_keras_prueba_mlcv.keras")

plt.figure()
plt.plot(history.history["loss"])
plt.title("Loss de entrenamiento")
plt.xlabel("Epoch")
plt.ylabel("Loss")
plt.savefig(OUTPUT_DIR / "loss_keras_prueba_mlcv.png")

with open(OUTPUT_DIR / "metricas_keras_prueba_mlcv.txt", "w") as f:
    f.write(f"tensorflow={tf.__version__}\n")
    f.write(f"gpus={tf.config.list_physical_devices('GPU')}\n")
    f.write(f"numpy={np.__version__}\n")
    f.write(f"pandas={pd.__version__}\n")
    f.write(f"sklearn={sklearn.__version__}\n")
    f.write(f"opencv={cv2.__version__}\n")
    f.write(f"loss_final={history.history['loss'][-1]}\n")
    f.write(f"mae_final={history.history['mae'][-1]}\n")

print("Modelo, gráfico y métricas guardados en:", OUTPUT_DIR)

#Código para prueba de concurrencia
SLEEP_MINUTES = 30
print(
    f"Prueba larga en GPU: el trabajo quedará activo durante {SLEEP_MINUTES} minutos para realizar comprobaciones.",
    flush=True
)

for i in range(SLEEP_MINUTES):
    print(f"Minuto {i + 1}/{SLEEP_MINUTES} - trabajo activo", flush=True)
    time.sleep(60)

print("Prueba larga finalizada.", flush=True)
