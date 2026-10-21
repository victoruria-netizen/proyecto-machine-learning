"""Pruebas del pipeline de inferencia del prototipo (fase 5, paso 5c): validación de entradas, carga del modelo, flujo
completo de «Próxima semana» y fidelidad del modo «Histórico» al CSV de la evaluación final.

Sólo prueban la lógica de ``app/pagina_prediccion.py`` (sin interfaz; la interfaz está en ``tests/test_app.py``). No
reentrenan nada y no leen el panel: el modelo exportado y ``predicciones_bloque_final.csv`` son las únicas entradas.
"""

import json
import subprocess
import sys

import numpy as np
import pandas as pd
import pytest

from src import datos, modelo as mod

sys.path.insert(0, str(datos.RAIZ / "app"))
import pagina_prediccion as pp                                     # noqa: E402

RUTA_MODELO = datos.RAIZ / "models" / "modelo_final.json"
RUTA_PRED = datos.RAIZ / "experiments" / "evaluacion_final" / "predicciones_bloque_final.csv"
RUTA_SERVIDOR = datos.RAIZ / "documentacion" / "logs" / "servidor_modelo_final" / "prediccion_semana_2026-01-01.csv"


@pytest.fixture(scope="module")
def historico():
    return pp.cargar_historico()


@pytest.fixture(scope="module")
def semana_nueva():
    return pp.predecir_proxima_semana(pp.cargar_modelo_final())


# ------------------------------------------------------------------------------ validación de entradas
def test_validar_semana_acepta_origenes_del_bloque_final(historico):
    disp = pp.origenes_disponibles(historico)
    assert len(disp) == 47 and disp[0] == pd.Timestamp("2025-02-06")
    assert all(pp.validar_semana(o, disp) == o for o in disp)
    assert pp.validar_semana("2025-02-13", disp) == pd.Timestamp("2025-02-13")


@pytest.mark.parametrize("entrada", ["2026-01-01", "2025-02-05", "2025-02-07", "2024-12-31"])
def test_validar_semana_fuera_de_rango_da_mensaje_claro(historico, entrada):
    with pytest.raises(pp.ErrorEntrada, match="fuera del bloque final"):
        pp.validar_semana(entrada, pp.origenes_disponibles(historico))


@pytest.mark.parametrize("entrada", ["no es una fecha", None, pd.NaT])
def test_validar_semana_rechaza_lo_que_no_es_fecha(historico, entrada):
    with pytest.raises(pp.ErrorEntrada):
        pp.validar_semana(entrada, pp.origenes_disponibles(historico))


def test_semana_historica_fuera_de_rango_falla(historico):
    with pytest.raises(pp.ErrorEntrada, match="fuera del bloque final"):
        pp.semana_historica(historico, "2026-01-01")


def test_historico_sin_columnas_falla(tmp_path):
    ruta = tmp_path / "p.csv"
    pd.read_csv(RUTA_PRED).drop(columns=["observado"]).to_csv(ruta, index=False)
    with pytest.raises(pp.ErrorEntrada, match="observado"):
        pp.cargar_historico(ruta)


# --------------------------------------------------------------------------------------- carga de archivos
def test_modelo_ausente_da_error_claro(tmp_path):
    with pytest.raises(pp.ErrorEntrada, match="No se encontró el archivo del modelo"):
        pp.cargar_modelo_final(tmp_path / "no_existe.json")


def test_predicciones_ausentes_dan_error_claro(tmp_path):
    with pytest.raises(pp.ErrorEntrada, match="No se encontró el archivo de predicciones"):
        pp.cargar_historico(tmp_path / "no_existe.csv")


def test_modelo_ilegible_da_error_claro(tmp_path):
    ruta = tmp_path / "m.json"
    ruta.write_text("{ no es json", encoding="utf-8")
    with pytest.raises(pp.ErrorEntrada, match="no se pudo leer"):
        pp.cargar_modelo_final(ruta)
    ruta.write_text('{"modelo": "XGBoost", "coeficientes": {}, "columnas": []}', encoding="utf-8")
    with pytest.raises(pp.ErrorEntrada, match="no se pudo leer"):
        pp.cargar_modelo_final(ruta)


def test_modelo_real_carga():
    m = pp.cargar_modelo_final()
    assert m["modelo"] == "GLM" and m["origen"] == pd.Timestamp("2026-01-01") and len(m["columnas"]) == 15


# ---------------------------------------------------------------------------------- flujo «Próxima semana»
def test_proxima_semana_es_8_por_7_sin_nulos_ni_negativos(semana_nueva):
    s = semana_nueva
    assert s.shape[0] == 56 and s["municipio"].nunique() == 8 and s["fecha"].nunique() == 7
    assert sorted(s["municipio"].unique()) == mod.MUNICIPIOS
    assert s["fecha"].min() == pd.Timestamp("2026-01-01") and s["fecha"].max() == pd.Timestamp("2026-01-07")
    cols = ["esperado", "inf_80", "sup_80", "inf_95", "sup_95"]
    assert s[cols].notna().all().all() and (s[cols] >= 0).all().all() and (s["esperado"] > 0).all()
    assert ((s["inf_95"] <= s["inf_80"]) & (s["inf_80"] <= s["sup_80"]) & (s["sup_80"] <= s["sup_95"])).all()


def test_proxima_semana_igual_a_la_del_servidor(semana_nueva):
    "Misma comparación que F4-B5 (tests/test_modelo.py): las 56 μ contra el job 136, diferencia relativa <= 1e-6 (D56)."
    servidor = pd.read_csv(RUTA_SERVIDOR, parse_dates=["fecha"]).rename(columns={"zona_id": "municipio"})
    j = semana_nueva.merge(servidor, on=["fecha", "municipio"], suffixes=("", "_servidor"), validate="one_to_one")
    assert len(j) == 56
    assert ((j["esperado"] - j["pred"]).abs() / j["pred"].abs()).max() <= 1e-6


def test_proxima_semana_igual_a_predecir_semana_directo():
    m = mod.cargar_modelo(RUTA_MODELO)
    directo = mod.predecir_semana(m, pp.historia_vacia(), pd.Timestamp("2026-01-01")).rename(
        columns={"zona_id": "municipio", "pred": "esperado"})
    pd.testing.assert_frame_equal(pp.predecir_proxima_semana(m), directo)


def test_modelo_no_predice_otra_semana():
    m = pp.cargar_modelo_final()
    with pytest.raises(ValueError, match="predice desde"):
        mod.predecir_semana(m, pp.historia_vacia(), pd.Timestamp("2026-01-08"))


# ------------------------------------------------------------------------------------------ modo «Histórico»
def test_historico_tiene_47_semanas_completas(historico):
    assert len(historico) == 47 * 56 and set(historico["papel"]) == {pp.PAPEL_SOLUCION}
    assert (historico.groupby("origen").size() == 56).all()


def test_semana_historica_coincide_fila_a_fila_con_el_csv(historico):
    "Cada una de las 47 semanas: mismas filas y valores (sin recalcular), leyendo el CSV por separado con pandas."
    crudo = pd.read_csv(RUTA_PRED, parse_dates=["fecha", "origen"])
    crudo = crudo[crudo["papel"] == "solución"]
    for o in pp.origenes_disponibles(historico):
        s = pp.semana_historica(historico, o)
        esperado = crudo[crudo["origen"] == o].sort_values(["fecha", "municipio"]).reset_index(drop=True)
        assert len(s) == len(esperado) == 56
        for c_pag, c_csv in (("fecha", "fecha"), ("municipio", "municipio"), ("esperado", "predicho"),
                             ("observado", "observado"), ("inf_80", "inf_80"), ("sup_80", "sup_80"),
                             ("inf_95", "inf_95"), ("sup_95", "sup_95")):
            assert (s[c_pag].to_numpy() == esperado[c_csv].to_numpy()).all(), (o, c_pag)


def test_resumen_por_municipio_suma_los_dias(historico):
    s = pp.semana_historica(historico, "2025-02-06")
    r = pp.resumen_por_municipio(s)
    assert list(r.index) == mod.MUNICIPIOS and np.isclose(r["observado"].sum(), s["observado"].sum())


# --------------------------------------------------------------------------------------------------- mapa
def test_datos_del_mapa_traen_los_8_municipios():
    capa = json.loads(pp.RUTA_CAPA.read_text(encoding="utf-8"))
    valores = pd.Series(np.arange(8, dtype=float), index=mod.MUNICIPIOS)
    df = pp.datos_mapa(valores, capa)
    assert sorted(df["municipio"]) == mod.MUNICIPIOS and df["polygon"].map(len).min() > 3
    assert df["color"].map(len).eq(4).all()


def test_datos_del_mapa_rechaza_municipio_ajeno():
    capa = {"features": [{"properties": {"municipio": "MUNICIPIO Z"}, "geometry": {"coordinates": [[]]}}]}
    with pytest.raises(pp.ErrorEntrada, match="MUNICIPIO Z"):
        pp.datos_mapa(pd.Series([1.0], index=["MUNICIPIO A"]), capa)


# ------------------------------------------------------------------------------- sin bases de datos (D67)
def test_la_pestana_no_importa_bases_de_datos_ni_config():
    codigo = ("import sys; sys.path.insert(0, 'app'); import pagina_prediccion; "
              "malos = [m for m in ('psycopg2', 'pymongo', 'sqlalchemy', 'config') if m in sys.modules]; "
              "print(malos); sys.exit(1 if malos else 0)")
    r = subprocess.run([sys.executable, "-c", codigo], cwd=datos.RAIZ, capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
