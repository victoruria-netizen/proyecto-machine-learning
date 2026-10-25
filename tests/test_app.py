"""Pruebas de interfaz de la pestaña «Predicción (PAA)» con ``streamlit.testing.v1.AppTest`` (fase 5, paso 5c).

``render()`` se prueba de forma aislada (``AppTest.from_string`` con un script mínimo) y también dentro de ``app/app.py``
eligiendo la pestaña en la barra de navegación (un ``st.radio`` nativo, que AppTest sí maneja). Ninguna prueba usa bases
de datos: la página inicial heredada («Resumen») muestra su error de conexión, que es lo esperado (D67); de esa corrida
solo se mira lo que pasa después de elegir la pestaña nueva.
"""

import tomllib

import pandas as pd
import pytest

pytest.importorskip("streamlit")
from streamlit.testing.v1 import AppTest                           # noqa: E402

from src import datos                                              # noqa: E402

APP = datos.RAIZ / "app" / "app.py"
RUTA_PRED = datos.RAIZ / "experiments" / "evaluacion_final" / "predicciones_bloque_final.csv"

SCRIPT_MINIMO = f"""
import sys
sys.path.insert(0, r"{datos.RAIZ / 'app'}")
import pagina_prediccion
pagina_prediccion.render()
"""


def _pestana():
    return AppTest.from_string(SCRIPT_MINIMO, default_timeout=90).run()


def _sin_problemas(at):
    assert not at.exception, [e.value for e in at.exception]
    assert not at.error, [e.value for e in at.error]


def test_render_proxima_semana():
    at = _pestana()
    _sin_problemas(at)
    resumen, detalle = at.dataframe[0].value, at.dataframe[1].value
    assert resumen.shape[0] == 8 and detalle.shape[0] == 56
    assert detalle["Fecha"].iloc[0] == "01/01/2026" and detalle["Fecha"].iloc[-1] == "07/01/2026"
    assert detalle["Esperado"].notna().all() and (detalle["Esperado"] >= 0).all()
    assert "cantidad esperada de siniestros viales" in at.info[0].value


def test_rotulo_del_modo_semana_posterior_al_corte():
    "D77: el modo se llama «Semana posterior al corte», aclara que es un entorno simulado y no dice «Próxima semana»."
    at = _pestana()
    _sin_problemas(at)
    assert list(at.radio(key="pred_modo").options) == ["Semana posterior al corte", "Histórico"]
    textos = [e.value for e in list(at.markdown) + list(at.info) + list(at.caption) + list(at.subheader)]
    assert any("Entorno simulado con fecha de corte 31/12/2025" in t for t in textos)
    assert not any("Próxima semana" in t for t in textos)
    assert "Próxima semana" not in at.radio(key="pred_modo").label


def test_render_historico_y_cambio_de_semana():
    at = _pestana()
    at.radio(key="pred_modo").set_value("Histórico").run()
    _sin_problemas(at)
    assert at.dataframe[1].value.shape[0] == 56 and "Observado" in at.dataframe[1].value.columns
    opciones = at.selectbox(key="pred_semana").options
    assert len(opciones) == 47
    at.selectbox(key="pred_semana").select(opciones[10]).run()
    _sin_problemas(at)
    at.selectbox(key="pred_municipio").select("MUNICIPIO CH").run()
    _sin_problemas(at)


def test_historico_mostrado_coincide_con_el_csv():
    "La tabla que ve el usuario en una semana es la del CSV (esperado redondeado a 2 decimales, observado entero)."
    at = _pestana()
    at.radio(key="pred_modo").set_value("Histórico").run()
    etiqueta = at.selectbox(key="pred_semana").options[20]
    at.selectbox(key="pred_semana").select(etiqueta).run()
    _sin_problemas(at)
    mostrada = at.dataframe[1].value
    origen = pd.to_datetime(etiqueta.split(" a ")[0], format="%d/%m/%Y")
    csv = pd.read_csv(RUTA_PRED, parse_dates=["fecha", "origen"])
    csv = csv[(csv["papel"] == "solución") & (csv["origen"] == origen)].sort_values(["fecha", "municipio"])
    assert (mostrada["Municipio"].to_numpy() == csv["municipio"].to_numpy()).all()
    assert (mostrada["Esperado"].to_numpy() == csv["predicho"].round(2).to_numpy()).all()
    assert (mostrada["Observado"].to_numpy() == csv["observado"].to_numpy()).all()


def _script_con_archivo_ausente(funcion, cache, ruta):
    """Script que apunta ``funcion`` a una ruta inexistente solo durante ``render()`` y deja todo como estaba (el módulo se
    comparte con las demás pruebas del proceso, así que no puede quedar modificado)."""
    return SCRIPT_MINIMO.replace("pagina_prediccion.render()", f"""
from pathlib import Path
f = pagina_prediccion.{funcion}
original = f.__defaults__
f.__defaults__ = (Path(r"{ruta}"),)
pagina_prediccion.{cache}.clear()
try:
    pagina_prediccion.render()
finally:
    f.__defaults__ = original
    pagina_prediccion.{cache}.clear()
""")


def test_falta_el_archivo_de_predicciones_muestra_mensaje_y_no_traza(tmp_path):
    "Con el CSV ausente, el modo Histórico muestra st.error (no una excepción)."
    at = AppTest.from_string(_script_con_archivo_ausente("cargar_historico", "_historico_en_cache", tmp_path / "no_esta.csv"),
                             default_timeout=90).run()
    at.radio(key="pred_modo").set_value("Histórico").run()
    assert not at.exception
    assert len(at.error) == 1 and "No se encontró el archivo de predicciones" in at.error[0].value


def test_falta_el_archivo_del_modelo_muestra_mensaje_y_no_traza(tmp_path):
    "Con el modelo ausente, «Semana posterior al corte» muestra st.error (no una excepción)."
    at = AppTest.from_string(_script_con_archivo_ausente("cargar_modelo_final", "_modelo_en_cache", tmp_path / "no_esta.json"),
                             default_timeout=90).run()
    assert not at.exception
    assert len(at.error) == 1 and "No se encontró el archivo del modelo" in at.error[0].value


def test_app_completa_tiene_la_pestana_nueva_y_funciona():
    at = AppTest.from_file(str(APP), default_timeout=90).run()           # «Resumen» heredado: su error de BD es esperado
    assert "Predicción (PAA)" in at.radio(key="nav").options
    at.radio(key="nav").set_value("Predicción (PAA)").run()
    _sin_problemas(at)
    assert at.dataframe[1].value.shape[0] == 56
    at.radio(key="pred_modo").set_value("Histórico").run()
    _sin_problemas(at)


def test_historico_muestra_4_metricas_y_los_elementos_nuevos():
    at = _pestana()
    at.radio(key="pred_modo").set_value("Histórico").run()
    _sin_problemas(at)
    assert not at.warning
    assert [m.label for m in at.metric] == ["Observado en la semana", "Esperado (solución)", "Desvianza de Poisson media",
                                            "Fuera del intervalo del 80 %"]
    assert at.metric[2].delta.endswith("frente a L1") and "56" in at.metric[3].value
    assert any("Las 47 semanas del bloque final" in s.value for s in at.subheader)
    assert any("1,1063" in c.value and "1,1359" in c.value and "33 de 47" in c.value for c in at.caption)
    assert "Fuera del 80 %" in at.dataframe[1].value.columns
    assert [e.label for e in at.expander][-1] == "Sobre el modelo"


def test_historico_sin_l1_muestra_un_warning_y_no_una_excepcion(tmp_path):
    "Con un CSV sin la referencia L1, la pestaña avisa y sigue, sin las comparaciones."
    ruta = tmp_path / "sin_l1.csv"
    crudo = pd.read_csv(RUTA_PRED)
    crudo[~crudo["modelo"].str.startswith("L1")].to_csv(ruta, index=False)
    at = AppTest.from_string(_script_con_archivo_ausente("cargar_referencia", "_referencia_en_cache", ruta),
                             default_timeout=90).run()
    at.radio(key="pred_modo").set_value("Histórico").run()
    assert not at.exception and not at.error
    assert len(at.warning) == 1 and "referencia L1" in at.warning[0].value and "sin las comparaciones" in at.warning[0].value
    assert len(at.metric) == 4 and not at.metric[2].delta                    # sin L1 no hay delta
    assert at.dataframe[1].value.shape[0] == 56


def test_semana_posterior_no_tiene_metricas_y_cierra_con_sobre_el_modelo():
    at = _pestana()
    _sin_problemas(at)
    assert len(at.metric) == 0
    assert [e.label for e in at.expander] == ["Tabla por municipio y día, con intervalos", "Sobre el modelo"]


def test_tema_claro_fijado_en_streamlit_config():
    "D80: sin este archivo, con el sistema en modo oscuro los textos casi no se leen sobre el fondo claro del CSS heredado."
    ruta = datos.RAIZ / ".streamlit" / "config.toml"
    assert ruta.is_file()
    assert tomllib.loads(ruta.read_text(encoding="utf-8"))["theme"]["base"] == "light"
