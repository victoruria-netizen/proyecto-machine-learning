# notebooks/Ejemplos/

Material de referencia y tutoriales del curso (no forma parte del pipeline reproducible del
proyecto): `Series_temporales_y_pronóstico_ejemplo.ipynb`, `Guia_series_temporales_skforecast.md`
y los scripts de prueba del servidor (`train_cpu_test.py`, `train_cpu_stress_matmul.py`,
`train_keras_test.py`).

**`skforecast` (2026-09-24).** `Series_temporales_y_pronóstico_ejemplo.ipynb` importa
`skforecast`, pero esa dependencia se quitó de `requirements.txt` al retirar `base_2.ipynb` del
pipeline principal (ver `HANDOFF.md`). Este notebook de ejemplo quedó fuera de
`requirements.txt`/`requirements-lock.txt` a propósito: es material de aprendizaje, no algo que
el resto del proyecto necesite poder reproducir. Para volver a ejecutarlo, instalar aparte:

```powershell
pip install skforecast==0.25.0
```

Con `pandas` en 2.3.3 (el pin vigente del proyecto) funciona sin cambios adicionales, porque esa
era justamente la versión con la que se validó `skforecast` 0.25.0 antes de retirarlo.
