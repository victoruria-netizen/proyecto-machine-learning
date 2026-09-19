# train_cpu_test.py

from pathlib import Path
from datetime import datetime
import os
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
import time

RUN_ID = datetime.now().strftime("%Y%m%d_%H%M%S")
OUTPUT_DIR = Path("/outputs") / "runs" / RUN_ID
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

SLURM_JOB_ID = os.environ.get("SLURM_JOB_ID", "no_slurm")
SLURM_JOB_NAME = os.environ.get("SLURM_JOB_NAME", "no_slurm")
SLURM_CPUS = int(os.environ.get("SLURM_CPUS_PER_TASK", "1"))
LOKY_MAX_CPU_COUNT = os.environ.get("LOKY_MAX_CPU_COUNT", "no_definido")

print("Inicio prueba CPU", flush=True)
print("SLURM_JOB_ID:", SLURM_JOB_ID, flush=True)
print("SLURM_JOB_NAME:", SLURM_JOB_NAME, flush=True)
print("SLURM_CPUS_PER_TASK:", SLURM_CPUS, flush=True)
print("LOKY_MAX_CPU_COUNT:", LOKY_MAX_CPU_COUNT, flush=True)

with open(OUTPUT_DIR / "run_info.txt", "w") as f:
    f.write(f"run_id={RUN_ID}\n")
    f.write(f"slurm_job_id={SLURM_JOB_ID}\n")
    f.write(f"slurm_job_name={SLURM_JOB_NAME}\n")
    f.write(f"slurm_cpus_per_task={SLURM_CPUS}\n")
    f.write(f"loky_max_cpu_count={LOKY_MAX_CPU_COUNT}\n")
    f.write(f"output_dir={OUTPUT_DIR}\n")

X = np.random.rand(10000, 30)
y = np.random.rand(10000)

model = RandomForestRegressor(
    n_estimators=200,
    random_state=42,
    n_jobs=SLURM_CPUS
)

model.fit(X, y)
pred = model.predict(X)

mae = mean_absolute_error(y, pred)

with open(OUTPUT_DIR / "metricas.txt", "w") as f:
    f.write(f"mae={mae}\n")

print("MAE:", mae, flush=True)
print("Resultados guardados en:", OUTPUT_DIR, flush=True)


#Código para prueba de concurrencia
SLEEP_MINUTES = 30
print(
    f"Prueba larga en CPU: el trabajo quedará activo durante {SLEEP_MINUTES} minutos para realizar comprobaciones.",
    flush=True
)

for i in range(SLEEP_MINUTES):
    print(f"Minuto {i + 1}/{SLEEP_MINUTES} - trabajo activo", flush=True)
    time.sleep(60)

print("Prueba larga finalizada.", flush=True)

