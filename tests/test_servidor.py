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


# ------------------------------------------------------------------------------------------------ puente
import importlib.util  # noqa: E402

import pytest  # noqa: E402

pytest.importorskip("streamlit")
from streamlit.testing.v1 import AppTest  # noqa: E402

RUTA_PUENTE = APP / "servidor" / "pagina_prediccion_puente.py"
HASH_1, HASH_2 = "1" * 40, "2" * 40
PAGINA = '''
import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))   # en pytest ya está en sys.path el src del repo real
from src import VERSION

def render():
    st.write("pestaña " + VERSION)
'''


def _clon_falso(raiz, version="v1", commit=HASH_1, pagina=PAGINA):
    "Clon mínimo: HEAD apunta a una rama, la ref tiene el commit, y hay ``app/pagina_prediccion.py`` y un paquete ``src``."
    (raiz / ".git" / "refs" / "heads").mkdir(parents=True, exist_ok=True)
    (raiz / ".git" / "HEAD").write_text("ref: refs/heads/main\n", encoding="utf-8")
    (raiz / ".git" / "refs" / "heads" / "main").write_text(commit + "\n", encoding="utf-8")
    (raiz / "app").mkdir(exist_ok=True)
    (raiz / "app" / "pagina_prediccion.py").write_text(pagina, encoding="utf-8")
    (raiz / "src").mkdir(exist_ok=True)
    (raiz / "src" / "__init__.py").write_text(f"VERSION = {version!r}\n", encoding="utf-8")
    return raiz


@pytest.fixture
def puente(monkeypatch):
    "El puente cargado como módulo propio (estado limpio), registrado para que un script de AppTest pueda importarlo."
    spec = importlib.util.spec_from_file_location("puente_bajo_prueba", RUTA_PUENTE)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    monkeypatch.setitem(sys.modules, "puente_bajo_prueba", modulo)
    monkeypatch.setattr(sys, "path", list(sys.path))                    # la página falsa lo modifica; se restaura al terminar
    yield modulo
    for n in [n for n in sys.modules if n in ("paa_pagina_prediccion", "src") or n.startswith("src.")]:
        sys.modules.pop(n, None)


def _correr_render():
    return AppTest.from_string("import puente_bajo_prueba\npuente_bajo_prueba.render()", default_timeout=30).run()


def test_el_puente_carga_la_pagina_del_clon_y_expone_render(puente, tmp_path):
    clon = _clon_falso(tmp_path / "proyecto-machine-learning")
    modulo = puente.obtener_pagina(clon)
    assert modulo.__name__ == "paa_pagina_prediccion" and callable(modulo.render)
    assert puente.commit_del_clon(clon) == HASH_1


def test_el_puente_dibuja_la_pestana_y_el_commit_desplegado(puente, tmp_path, monkeypatch):
    monkeypatch.setenv("PAA_REPO", str(_clon_falso(tmp_path / "otro_nombre")))
    at = _correr_render()
    assert not at.exception and not at.error
    assert at.markdown[0].value == "pestaña v1"
    assert at.caption[-1].value == "Versión desplegada: 1111111 del repositorio del PAA"


def test_el_puente_recarga_cuando_cambia_el_commit(puente, tmp_path):
    clon = _clon_falso(tmp_path / "proyecto-machine-learning")
    primera = puente.obtener_pagina(clon)
    assert puente.obtener_pagina(clon) is primera                       # mismo commit: no recarga
    _clon_falso(clon, version="version-dos", commit=HASH_2)                      # como un git checkout; otro largo, para no reusar el .pyc
    segunda = puente.obtener_pagina(clon)
    assert segunda is not primera
    import src
    assert src.VERSION == "version-dos"                                          # src también se recargó


def test_el_puente_lee_el_commit_de_packed_refs_y_de_head_suelto(puente, tmp_path):
    clon = _clon_falso(tmp_path / "a")
    (clon / ".git" / "refs" / "heads" / "main").unlink()
    (clon / ".git" / "packed-refs").write_text(f"# pack-refs\n{HASH_2} refs/heads/main\n^{HASH_1}\n", encoding="utf-8")
    assert puente.commit_del_clon(clon) == HASH_2
    (clon / ".git" / "HEAD").write_text(HASH_1 + "\n", encoding="utf-8")
    assert puente.commit_del_clon(clon) == HASH_1
    assert puente.commit_del_clon(tmp_path / "sin_git") is None


def test_sin_clon_muestra_error_y_no_lanza(puente, tmp_path, monkeypatch):
    monkeypatch.setenv("PAA_REPO", str(tmp_path / "no_existe"))
    at = _correr_render()
    assert not at.exception
    assert len(at.error) == 1 and "No se encontró el clon" in at.error[0].value


def test_con_una_importacion_que_falla_muestra_error_y_no_lanza(puente, tmp_path, monkeypatch):
    pagina_rota = "import modulo_que_no_existe_xyz\n\ndef render():\n    pass\n"
    monkeypatch.setenv("PAA_REPO", str(_clon_falso(tmp_path / "roto", pagina=pagina_rota)))
    at = _correr_render()
    assert not at.exception
    assert len(at.error) == 1 and "ModuleNotFoundError" in at.error[0].value
    assert any("Traceback" in c.value and "modulo_que_no_existe_xyz" in c.value for c in at.code)
    assert "paa_pagina_prediccion" not in sys.modules                   # no queda a medio cargar
    assert at.caption[-1].value.startswith("Versión desplegada: 1111111")


PAGINA_CON_CACHE = '''
from pathlib import Path

import streamlit as st

DATO = Path(__file__).resolve().parent.parent / "dato.txt"

@st.cache_data(show_spinner=False)
def leer_dato():
    return DATO.read_text(encoding="utf-8")

def render():
    st.write("dato: " + leer_dato())
'''

PAGINA_CON_CACHE_ROTA = PAGINA_CON_CACHE + '''
class _Rota:
    __wrapped__ = None
    def clear(self):
        raise RuntimeError("no se pudo")

rota = _Rota()
'''


def _clon_con_dato(raiz, dato, commit, pagina=PAGINA_CON_CACHE):
    _clon_falso(raiz, version=dato, commit=commit, pagina=pagina)
    (raiz / "dato.txt").write_text(dato, encoding="utf-8")
    return raiz


def test_tras_cambiar_el_commit_la_funcion_cacheada_de_la_pagina_devuelve_el_valor_nuevo(puente, tmp_path):
    clon = _clon_con_dato(tmp_path / "proyecto-machine-learning", "uno", HASH_1)
    assert puente.obtener_pagina(clon).leer_dato() == "uno"
    _clon_con_dato(clon, "dos", HASH_2)
    assert puente.obtener_pagina(clon).leer_dato() == "dos"
    assert puente._ESTADO["avisos"] == []


def test_vaciar_la_cache_de_la_pagina_no_vacia_la_de_una_funcion_ajena(puente, tmp_path):
    import streamlit as st
    llamadas = []

    @st.cache_data(show_spinner=False)
    def ajena():                                      # hace de función cacheada de otra página del dashboard
        llamadas.append(1)
        return len(llamadas)

    assert ajena() == 1
    clon = _clon_con_dato(tmp_path / "proyecto-machine-learning", "uno", HASH_1)
    puente.obtener_pagina(clon).leer_dato()
    _clon_con_dato(clon, "dos", HASH_2)
    puente.obtener_pagina(clon)
    assert ajena() == 1 and len(llamadas) == 1        # sigue en caché: el puente no la vació


def test_si_falla_el_vaciado_de_una_cache_se_anota_en_el_diagnostico_y_el_puente_sigue(puente, tmp_path, monkeypatch):
    clon = _clon_con_dato(tmp_path / "proyecto-machine-learning", "uno", HASH_1, pagina=PAGINA_CON_CACHE_ROTA)
    monkeypatch.setenv("PAA_REPO", str(clon))
    at = _correr_render()
    assert not at.exception and not at.error and at.markdown[0].value == "dato: uno"
    _clon_con_dato(clon, "dos", HASH_2, pagina=PAGINA_CON_CACHE_ROTA)
    at = _correr_render()
    assert not at.exception and not at.error
    assert at.markdown[0].value == "dato: dos"                         # la caché sana sí se vació y la página sigue
    assert any("rota" in w.value and "RuntimeError" in w.value for w in at.warning)
    assert at.caption[-1].value == "Versión desplegada: 2222222 del repositorio del PAA"
