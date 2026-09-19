# train_cpu_stress_matmul.py

from pathlib import Path
from datetime import datetime
import os
import time
import multiprocessing as mp
import numpy as np

RUN_ID = datetime.now().strftime("%Y%m%d_%H%M%S")
OUTPUT_DIR = Path("/outputs") / "runs" / RUN_ID
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

SLURM_JOB_ID = os.environ.get("SLURM_JOB_ID", "no_slurm")
SLURM_JOB_NAME = os.environ.get("SLURM_JOB_NAME", "no_slurm")
SLURM_CPUS = int(os.environ.get("SLURM_CPUS_PER_TASK", "1"))

MATRIX_SIZE = 2048
DURATION_SECONDS = 15 * 60

print("Inicio prueba CPU intensiva sostenida", flush=True)
print("SLURM_JOB_ID:", SLURM_JOB_ID, flush=True)
print("SLURM_JOB_NAME:", SLURM_JOB_NAME, flush=True)
print("SLURM_CPUS_PER_TASK:", SLURM_CPUS, flush=True)
print("MATRIX_SIZE:", MATRIX_SIZE, flush=True)
print("DURATION_SECONDS:", DURATION_SECONDS, flush=True)

with open(OUTPUT_DIR / "run_info.txt", "w") as f:
    f.write(f"run_id={RUN_ID}\n")
    f.write(f"slurm_job_id={SLURM_JOB_ID}\n")
    f.write(f"slurm_job_name={SLURM_JOB_NAME}\n")
    f.write(f"slurm_cpus_per_task={SLURM_CPUS}\n")
    f.write(f"output_dir={OUTPUT_DIR}\n")

def worker(worker_id: int):
    rng = np.random.default_rng(42 + worker_id)
    a = rng.random((MATRIX_SIZE, MATRIX_SIZE), dtype=np.float32)
    b = rng.random((MATRIX_SIZE, MATRIX_SIZE), dtype=np.float32)

    iterations = 0
    checksum = 0.0
    start = time.time()
    last_print = start

    while time.time() - start < DURATION_SECONDS:
        c = a @ b
        checksum += float(c[0, 0])
        iterations += 1

        now = time.time()
        if now - last_print >= 60:
            print(
                f"Worker {worker_id} activo - iteraciones={iterations} - elapsed={now - start:.1f}s",
                flush=True
            )
            last_print = now

    elapsed = time.time() - start
    return worker_id, iterations, elapsed, checksum

print(f"Lanzando {SLURM_CPUS} procesos CPU...", flush=True)

start_total = time.time()

with mp.Pool(processes=SLURM_CPUS) as pool:
    results = pool.map(worker, range(SLURM_CPUS))

elapsed_total = time.time() - start_total

print("Resultados workers:", results, flush=True)
print(f"Tiempo total: {elapsed_total:.2f} segundos", flush=True)

with open(OUTPUT_DIR / "metricas_cpu_stress_sostenido.txt", "w") as f:
    f.write(f"matrix_size={MATRIX_SIZE}\n")
    f.write(f"duration_seconds={DURATION_SECONDS}\n")
    f.write(f"processes={SLURM_CPUS}\n")
    f.write(f"elapsed_seconds={elapsed_total}\n")
    f.write(f"results={results}\n")

print("Prueba CPU sostenida finalizada.", flush=True)