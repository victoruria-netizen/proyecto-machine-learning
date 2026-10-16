"""Pruebas de src/variables.py y src/datos.py.

Los tests de causalidad usan un panel sintético (no dependen de data/processed/). Los que usan el
panel real se saltan si el archivo no está y lo leen siempre por ``cargar_panel_desarrollo``, que
descarta el bloque final al leer.
"""

import numpy as np
import pandas as pd
import pytest

from src import datos, variables as v

ZONAS = ["MUNICIPIO A", "MUNICIPIO B", "MUNICIPIO C", "MUNICIPIO CH",
         "MUNICIPIO D", "MUNICIPIO E", "MUNICIPIO F", "MUNICIPIO G"]
INICIO = pd.Timestamp("2021-07-01")
N_DIAS = 260
ORIGEN = INICIO + pd.Timedelta(days=200)          # 60 días por delante del origen; el horizonte cabe
# Un feriado en martes y otro en sábado: el feriado debe ganarle al día de la semana.
FERIADOS = {pd.Timestamp("2021-08-24"), pd.Timestamp("2021-09-04"), pd.Timestamp("2022-01-18")}  # mar, sáb, mar


def _panel_sintetico(semilla=0) -> pd.DataFrame:
    rng = np.random.default_rng(semilla)
    dias = pd.date_range(INICIO, periods=N_DIAS, freq="D")
    p = pd.MultiIndex.from_product([dias, ZONAS], names=["fecha", "zona_id"]).to_frame(index=False)
    p["n_siniestros"] = rng.poisson(3, len(p))
    fin = p["fecha"].dt.dayofweek >= 5
    p["tipo_dia"] = np.where(p["fecha"].isin(FERIADOS), "feriado", np.where(fin, "fin_semana", "entre_semana"))
    return p


@pytest.fixture(scope="module")
def panel():
    return _panel_sintetico()


def _con_futuro_basura(panel, origen):
    "Misma tabla pero con el objetivo de todo día >= origen reemplazado por un valor imposible."
    otro = panel.copy()
    otro.loc[otro["fecha"] >= origen, "n_siniestros"] = 10**6
    return otro


# ---------------------------------------------------------------------------------------- causalidad
def test_horizonte_no_usa_datos_posteriores_al_origen(panel):
    ref = v.variables_horizonte(panel, ORIGEN)
    alt = v.variables_horizonte(_con_futuro_basura(panel, ORIGEN), ORIGEN)
    pd.testing.assert_frame_equal(ref, alt)


def test_entrenamiento_no_usa_datos_posteriores_al_origen(panel):
    ref = v.matriz_entrenamiento(panel, ORIGEN)
    alt = v.matriz_entrenamiento(_con_futuro_basura(panel, ORIGEN), ORIGEN)
    pd.testing.assert_frame_equal(ref, alt)
    assert ref["fecha"].max() < ORIGEN
    assert (ref["n_siniestros"] < 10**6).all()


def test_cada_variable_coincide_con_su_definicion_a_mano(panel):
    h = v.variables_horizonte(panel, ORIGEN)
    y = panel.pivot(index="fecha", columns="zona_id", values="n_siniestros")
    previo = y[y.index < ORIGEN]
    d, z = ORIGEN + pd.Timedelta(days=3), "MUNICIPIO C"
    fila = h[(h["fecha"] == d) & (h["zona_id"] == z)].iloc[0]
    for k in v.REZAGOS:
        assert fila[f"rezago_{k}"] == y.loc[d - pd.Timedelta(days=k), z]
    for n in v.NIVELES_RECIENTES:
        assert fila[f"nivel_reciente_{n}"] == pytest.approx(previo[z].iloc[-n:].mean())
    assert fila["nivel_municipio"] == pytest.approx(previo[z].mean())
    # el nivel reciente queda fijo para los 7 días del horizonte
    assert h.groupby("zona_id")["nivel_reciente_28"].nunique().eq(1).all()


def test_nivel_municipio_con_ventana_deslizante(panel):
    previo = panel[(panel["fecha"] < ORIGEN) & (panel["fecha"] >= ORIGEN - pd.Timedelta(days=90))]
    esperado = previo.groupby("zona_id")["n_siniestros"].mean()
    pd.testing.assert_series_equal(v.nivel_municipio(panel, ORIGEN, dias_ventana=90),
                                   esperado.rename("nivel_municipio"))


def test_origen_simulado_del_entrenamiento(panel):
    "Cada día de entrenamiento usa el nivel reciente medido al comienzo de su bloque de 7 días."
    ent = v.matriz_entrenamiento(panel, ORIGEN)
    y = panel.pivot(index="fecha", columns="zona_id", values="n_siniestros")
    for d in (ORIGEN - pd.Timedelta(days=1), ORIGEN - pd.Timedelta(days=7), ORIGEN - pd.Timedelta(days=30)):
        o_sim = ORIGEN - pd.Timedelta(days=7 * int(np.ceil((ORIGEN - d).days / 7)))
        assert o_sim <= d < o_sim + pd.Timedelta(days=7) and o_sim < ORIGEN
        fila = ent[(ent["fecha"] == d) & (ent["zona_id"] == "MUNICIPIO B")].iloc[0]
        previo = y[y.index < o_sim]["MUNICIPIO B"]
        assert fila["nivel_reciente_91"] == pytest.approx(previo.iloc[-91:].mean())
        assert fila["rezago_7"] == y.loc[d - pd.Timedelta(days=7), "MUNICIPIO B"]


def test_rezago_menor_al_horizonte_se_rechaza(panel):
    dias = pd.date_range(ORIGEN, periods=7, freq="D")
    with pytest.raises(ValueError):
        v.rezagos(panel, ORIGEN, dias, lags=(3,))


# -------------------------------------------------------------------------------- feriados y calendario
def test_feriados_coinciden_con_tipo_dia_y_tienen_prioridad(panel):
    cal = v.calendario_8(panel)
    assert list(cal.cat.categories) == v.NIVELES_CALENDARIO and len(v.NIVELES_CALENDARIO) == 8
    assert ((cal == "feriado") == (panel["tipo_dia"] == "feriado")).all()
    # el martes y el sábado feriados quedan como feriado, no como su día de la semana
    for f in (pd.Timestamp("2021-08-24"), pd.Timestamp("2021-09-04")):
        assert (cal[panel["fecha"] == f] == "feriado").all()
    # fuera de feriados, el nivel es el día de la semana
    resto = panel["tipo_dia"] != "feriado"
    esperado = panel.loc[resto, "fecha"].dt.dayofweek.map(dict(enumerate(v.DIAS_SEMANA)))
    assert (cal[resto].astype(str) == esperado).all()


def test_tipo_dia_desconocido_falla(panel):
    malo = panel.head(5).copy()
    malo["tipo_dia"] = "otro"
    with pytest.raises(ValueError):
        v.calendario_8(malo)


def test_termino_calendario_de_a(panel):
    cal = v.calendario_8(panel)
    t = v.termino_calendario_a(cal, panel["zona_id"])
    assert list(t.columns) == v.COLUMNAS_A_X_CALENDARIO
    assert (t.sum(axis=1) == (panel["zona_id"] == "MUNICIPIO A").astype(int)).all()
    assert t.loc[panel["zona_id"] != "MUNICIPIO A"].to_numpy().sum() == 0


# ------------------------------------------------------------------------------- dimensiones y nulos
def test_dimensiones_y_sin_nulos_en_el_horizonte(panel):
    h = v.variables_horizonte(panel, ORIGEN)
    esperadas = (["fecha", "zona_id", "calendario", "es_a"] + v.COLUMNAS_A_X_CALENDARIO + ["nivel_municipio"]
                 + [f"nivel_reciente_{n}" for n in v.NIVELES_RECIENTES] + [f"rezago_{k}" for k in v.REZAGOS])
    assert sorted(h.columns) == sorted(esperadas)
    assert h.shape == (7 * 8, len(esperadas))
    assert not h.isna().any().any()
    assert h["fecha"].min() == ORIGEN and h["fecha"].max() == ORIGEN + pd.Timedelta(days=6)
    assert h.groupby("fecha").size().eq(8).all()
    assert "lluvia_mm" not in h.columns and not hasattr(v, "lluvia")   # conjunto (d) retirado
    assert "n_siniestros" not in h.columns                       # el horizonte no trae el objetivo


def test_entrenamiento_dimensiones_y_filas_comunes(panel):
    ent = v.matriz_entrenamiento(panel, ORIGEN)
    # se pierden los primeros días sin historia suficiente para el nivel reciente de 91 días
    # (+ el origen simulado puede estar hasta 6 días antes que el día)
    assert not ent.isna().any().any()
    assert ent["fecha"].max() == ORIGEN - pd.Timedelta(days=1)
    assert ent.groupby("fecha").size().eq(8).all()
    completa = v.matriz_entrenamiento(panel, ORIGEN, solo_completas=False)
    assert len(completa) == 200 * 8 and len(ent) < len(completa)
    corta = v.matriz_entrenamiento(panel, ORIGEN, dias_ventana=100)
    assert corta["fecha"].min() == ORIGEN - pd.Timedelta(days=100)
    assert len(corta) == 100 * 8


def test_nivel_reciente_con_historia_insuficiente_es_nan(panel):
    cerca = INICIO + pd.Timedelta(days=10)
    assert v.nivel_reciente(panel, cerca, 28).isna().all()


# ----------------------------------------------------------------------------------------- panel real
RUTA_REAL = datos.RUTA_PANEL
sin_panel = pytest.mark.skipif(not RUTA_REAL.exists(), reason="data/processed/ no está generado")


def test_limite_del_desarrollo_sale_del_calendario():
    assert datos.N_TOTAL == 1645 and datos.N_DESARROLLO == 1316
    assert datos.ULTIMO_DIA_DESARROLLO == pd.Timestamp("2025-02-05")
    assert datos.PRIMER_DIA_TEST == pd.Timestamp("2025-02-06")


@sin_panel
def test_panel_real_sin_test_y_variables_sin_nulos():
    real = datos.cargar_panel_desarrollo()
    assert real["fecha"].max() == pd.Timestamp("2025-02-05")
    assert not (real["fecha"] > pd.Timestamp("2025-02-05")).any()
    assert real.shape[0] == 1316 * 8
    # origen = primer día de la validación (987 días de entrenamiento inicial)
    origen = datos.FECHA_INICIO + pd.Timedelta(days=987)
    h = v.variables_horizonte(real, origen)
    assert h.shape[0] == 56 and not h.isna().any().any()


@sin_panel
def test_panel_real_feriados_y_fin_de_semana_coinciden_con_tipo_dia():
    real = datos.cargar_panel_desarrollo()
    cal = v.calendario_8(real)
    assert ((cal == "feriado") == (real["tipo_dia"] == "feriado")).all()
    no_fer = real["tipo_dia"] != "feriado"
    es_finde = cal[no_fer].isin(["sábado", "domingo"])
    assert (es_finde == (real.loc[no_fer, "tipo_dia"] == "fin_semana")).all()
