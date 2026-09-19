# diagnostico_entorno.py
#
# Script de un solo uso para averiguar por qué train_base_2.py no encuentra skforecast en el
# servidor aunque `pip install skforecast==0.25.0` haya terminado sin errores en la terminal de
# Jupyter. La hipótesis más probable es que `submit_cpu` ejecuta el script con un intérprete de
# Python (o un entorno virtual/conda) DISTINTO del que usa la terminal de Jupyter donde se hizo
# el pip install -- este script imprime toda la información necesaria para confirmarlo.
#
# Uso: submit_cpu diagnostico_entorno.py
# Después, comparar el .out contra lo que muestra `which python` / `pip show skforecast` en la
# terminal de Jupyter donde se instaló el paquete.

import os
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

print("=== Intérprete de Python que ejecuta este trabajo ===", flush=True)
print("sys.executable :", sys.executable, flush=True)
print("sys.version    :", sys.version.replace("\n", " "), flush=True)
print("sys.prefix     :", sys.prefix, flush=True)
print("sys.base_prefix:", sys.base_prefix, flush=True)
print("(si sys.prefix != sys.base_prefix, este proceso corre dentro de un venv/conda env)",
      flush=True)

print("\n=== Variables de entorno relevantes ===", flush=True)
for var in ["VIRTUAL_ENV", "CONDA_DEFAULT_ENV", "CONDA_PREFIX", "PYTHONPATH", "PATH",
            "HOME", "USER", "SLURM_JOB_ID", "SLURM_JOB_NAME", "SLURM_CPUS_PER_TASK"]:
    print(f"{var:20s}=", os.environ.get(var, "(no definida)"), flush=True)

print("\n=== sys.path (dónde busca los paquetes este proceso) ===", flush=True)
for p in sys.path:
    print(" -", p, flush=True)

print("\n=== ¿Puede importar skforecast? ===", flush=True)
try:
    import skforecast
    print("OK: skforecast", skforecast.__version__, "en", skforecast.__file__, flush=True)
except ImportError as exc:
    print("FALLA:", exc, flush=True)

print("\n=== Versiones de otras librerías, para comparar con lo que instaló pip ===", flush=True)
for modulo in ["pandas", "numpy", "sklearn", "matplotlib"]:
    try:
        m = __import__(modulo)
        print(f"{modulo:12s}", getattr(m, "__version__", "?"), "en", m.__file__, flush=True)
    except ImportError as exc:
        print(f"{modulo:12s} FALLA: {exc}", flush=True)

print("\n=== pip (el que usaría este mismo intérprete) ===", flush=True)
try:
    out = subprocess.run([sys.executable, "-m", "pip", "show", "skforecast"],
                          capture_output=True, text=True, timeout=30)
    print("--- pip show skforecast (stdout) ---", flush=True)
    print(out.stdout or "(vacío -- pip no encuentra el paquete con este intérprete)", flush=True)
    if out.stderr:
        print("--- stderr ---", flush=True)
        print(out.stderr, flush=True)
except Exception as exc:
    print("No se pudo ejecutar pip:", exc, flush=True)

print("\nDiagnóstico finalizado.", flush=True)
