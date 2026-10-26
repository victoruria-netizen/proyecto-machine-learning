"""
pagina_prediccion_puente.py — Puente entre el dashboard del servidor y la pestaña «Predicción (PAA)» (Entregable 3, fase 8a).

En el servidor se copia como ``/app/streamlit/pagina_prediccion.py``, que es el módulo que el ``app.py`` del dashboard
importa. No contiene la pestaña: carga ``app/pagina_prediccion.py`` del clon del repositorio (por omisión
``/app/proyecto-machine-learning``, o la carpeta de la variable de entorno ``PAA_REPO``) y llama a su ``render()``. Así, un
``git checkout`` en el clon se ve en el dashboard sin reiniciarlo y sin volver a copiar archivos (D81 a D83).

Lee el commit del clon desde ``.git`` sin ``subprocess``. Si cambió desde la última carga, descarta el módulo cargado y el
paquete ``src`` y lo carga de nuevo. Nunca deja escapar una excepción: si el clon falta o algo falla, muestra el motivo.

Solo usa la biblioteca estándar y streamlit.
"""

import importlib.util
import os
import sys
import traceback
from pathlib import Path

import streamlit as st

NOMBRE_MODULO = "paa_pagina_prediccion"
NOMBRE_CLON = "proyecto-machine-learning"
VARIABLE_ENTORNO = "PAA_REPO"

class ClonNoDisponible(Exception):
    "El clon del repositorio no está, o no tiene la pestaña."


# Lo que quedó cargado: el módulo de la pestaña, el commit del clon con el que se cargó y los avisos de diagnóstico.
_ESTADO = {"modulo": None, "commit": None, "avisos": []}


def ubicar_clon() -> Path:
    "Carpeta del clon: ``PAA_REPO`` si está definida; si no, ``proyecto-machine-learning`` junto a la carpeta de este archivo."
    definida = os.environ.get(VARIABLE_ENTORNO)
    if definida:
        return Path(definida).expanduser()
    return Path(__file__).resolve().parent.parent / NOMBRE_CLON


def _carpeta_git(clon: Path):
    "Carpeta ``.git`` del clon; sigue el puntero ``gitdir:`` si ``.git`` es un archivo. ``None`` si no hay."
    g = clon / ".git"
    if g.is_dir():
        return g
    if g.is_file():
        texto = g.read_text(encoding="utf-8").strip()
        if texto.startswith("gitdir:"):
            destino = Path(texto[len("gitdir:"):].strip())
            return destino if destino.is_absolute() else (clon / destino).resolve()
    return None


def commit_del_clon(clon: Path):
    "Hash completo del commit en ``HEAD``, leído de ``.git/HEAD`` y de la ref o de ``packed-refs``. ``None`` si no se puede leer."
    try:
        git = _carpeta_git(Path(clon))
        if git is None:
            return None
        head = (git / "HEAD").read_text(encoding="utf-8").strip()
        if not head.startswith("ref:"):
            return head or None                        # HEAD suelto: ya es el hash
        ref = head[len("ref:"):].strip()
        carpetas = [git]
        if (git / "commondir").is_file():              # worktree: las refs están en la carpeta común
            carpetas.append((git / (git / "commondir").read_text(encoding="utf-8").strip()).resolve())
        for c in carpetas:
            if (c / ref).is_file():
                return (c / ref).read_text(encoding="utf-8").strip() or None
        for c in carpetas:
            if (c / "packed-refs").is_file():
                for linea in (c / "packed-refs").read_text(encoding="utf-8").splitlines():
                    if linea.startswith(("#", "^")):
                        continue
                    hash_, _, nombre = linea.partition(" ")
                    if nombre.strip() == ref:
                        return hash_
    except (OSError, UnicodeDecodeError):
        return None
    return None


def _descartar_modulos() -> None:
    "Quita de ``sys.modules`` la pestaña y ``src`` con todos sus submódulos, para que la próxima importación lea los archivos."
    for nombre in [n for n in sys.modules if n in (NOMBRE_MODULO, "src") or n.startswith("src.")]:
        del sys.modules[nombre]


def _vaciar_cachees_del_modulo(modulo) -> None:
    """Vacía la caché de cada función cacheada de streamlit (``st.cache_data`` / ``st.cache_resource``) que defina el módulo.
    Solo las de la pestaña: las cachés de las páginas del PID no se tocan. Cada una va en su propio ``try``; si una falla,
    se anota en ``_ESTADO["avisos"]`` y se sigue con la siguiente."""
    for nombre, valor in list(vars(modulo).items()):
        if callable(getattr(valor, "clear", None)) and hasattr(valor, "__wrapped__"):
            try:
                valor.clear()
            except Exception as e:                     # noqa: BLE001
                _ESTADO["avisos"].append(f"No se pudo vaciar la caché de {nombre}: {type(e).__name__}: {e}")


def _cargar(clon: Path):
    "Importa ``app/pagina_prediccion.py`` del clon bajo el nombre ``paa_pagina_prediccion``. Propaga lo que falle."
    ruta = clon / "app" / "pagina_prediccion.py"
    if not ruta.is_file():
        raise ClonNoDisponible(f"El clon no tiene app/pagina_prediccion.py ({ruta}).")
    _descartar_modulos()
    spec = importlib.util.spec_from_file_location(NOMBRE_MODULO, ruta)
    modulo = importlib.util.module_from_spec(spec)
    sys.modules[NOMBRE_MODULO] = modulo
    try:
        spec.loader.exec_module(modulo)
    except BaseException:
        sys.modules.pop(NOMBRE_MODULO, None)
        raise
    return modulo


def obtener_pagina(clon: Path):
    """Módulo de la pestaña del clon. Si el commit del clon cambió desde la última carga, vacía las cachés de las funciones
    cacheadas del módulo viejo (conservarían el modelo y los CSV anteriores) y lo recarga junto con ``src``."""
    clon = Path(clon)
    if not clon.is_dir():
        raise ClonNoDisponible(f"No se encontró el clon del repositorio del PAA en {clon}.")
    commit = commit_del_clon(clon)
    if _ESTADO["modulo"] is not None and commit == _ESTADO["commit"]:
        return _ESTADO["modulo"]
    _ESTADO["avisos"] = []
    if _ESTADO["modulo"] is not None:
        _vaciar_cachees_del_modulo(_ESTADO["modulo"])
    _ESTADO["modulo"], _ESTADO["commit"] = None, None
    modulo = _cargar(clon)
    _ESTADO["modulo"], _ESTADO["commit"] = modulo, commit
    return modulo


def _mostrar_diagnostico(motivo: str = "") -> None:
    "Expander con el traceback del error en curso (si lo hay) y los avisos que anotó el puente."
    with st.expander("Detalle técnico"):
        if motivo:
            st.code(traceback.format_exc() if sys.exc_info()[0] else motivo, language="text")
        for aviso in _ESTADO["avisos"]:
            st.warning(aviso)


def _mostrar_error(motivo: str) -> None:
    st.error(f"No se pudo mostrar la pestaña «Predicción (PAA)»: {motivo}")
    _mostrar_diagnostico(motivo)


def render() -> None:
    "Pestaña del clon, con el commit desplegado al pie. Ante cualquier fallo muestra el motivo con ``st.error``."
    clon = ubicar_clon()
    try:
        obtener_pagina(clon).render()
    except ClonNoDisponible as e:
        _mostrar_error(f"{e} Definí la variable de entorno {VARIABLE_ENTORNO} o clonar el repositorio ahí (ver documentacion/despliegue_servidor.md).")
    except Exception as e:                             # noqa: BLE001 — el puente no deja escapar nada que no sea control de streamlit
        _mostrar_error(f"{type(e).__name__}: {e}")
    else:
        if _ESTADO["avisos"]:
            _mostrar_diagnostico()
    if clon.is_dir():
        commit = commit_del_clon(clon)
        st.caption(f"Versión desplegada: {commit[:7] if commit else 'desconocida'} del repositorio del PAA")
