"""Pruebas del despliegue en el dashboard del servidor (fase 8a, D81 a D83).

Paso 1: ``app/pagina_prediccion.py`` agrega ``app/`` y la raíz al final de ``sys.path``, para no tapar los ``charts``,
``ui``, ``config`` y ``constants`` del dashboard del PID. Paso 2: el puente ``app/servidor/pagina_prediccion_puente.py``.
"""

import subprocess
import sys

from src import datos

APP = datos.RAIZ / "app"


def test_importar_la_pagina_no_cambia_los_primeros_elementos_de_sys_path():
    "Corre en un intérprete aparte para partir de un ``sys.path`` conocido y sin ``app/`` ni la raíz."
    codigo = f"""
import sys
base = [p for p in sys.path if p not in ({str(APP)!r}, {str(datos.RAIZ)!r})] + ["/servidor/ficticio"]
sys.path[:] = base
import importlib.util
spec = importlib.util.spec_from_file_location("pagina_prediccion_bajo_prueba", {str(APP / 'pagina_prediccion.py')!r})
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
assert sys.path[:len(base)] == base, sys.path
assert sys.path[len(base):] == [{str(APP)!r}, {str(datos.RAIZ)!r}], sys.path
print("ok")
"""
    r = subprocess.run([sys.executable, "-c", codigo], capture_output=True, text=True, cwd=str(datos.RAIZ), timeout=120)
    assert r.returncode == 0, r.stderr
    assert r.stdout.strip() == "ok"
