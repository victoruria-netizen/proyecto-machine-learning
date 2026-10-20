"""Pruebas de src/modelo.py y de var.tipo_dia (D50).

Control de reproducción (D50, doble control):
1. **1e-9** contra el camino de la fase 2 reconstruido acá (celda ``paso-a-motor`` de modelos_candidatos.ipynb: vista con
   el objetivo de los días >= origen en NaN, ``var.matriz_entrenamiento``, ``var.variables_horizonte``, matriz de D31 y
   ``sm.GLM``/``NegativeBinomial``), en los 47 cortes de validación, para la solución.
2. **6e-7** (redondeo a 6 decimales, 5e-7, con margen de punto flotante; D51) contra los artefactos guardados: ``tablas/31`` (predicciones de la solución, la
   sensibilidad y el contraste), ``tablas/45`` (α de NB2 (a) 364 d) y ``tablas/46`` (cobertura de los intervalos).

Los tests con el panel real se saltan si el archivo no está y lo leen sólo por ``cargar_panel_desarrollo``.
"""

import numpy as np
import pandas as pd
import pytest
import statsmodels.api as sm
from scipy import stats
from statsmodels.discrete.discrete_model import NegativeBinomial

from src import datos, modelo as mod, variables as var

DIR_TABLAS = datos.RAIZ / "experiments" / "modelos_candidatos" / "tablas"
TOL_EXACTA = 1e-9
TOL_REDONDEO = 6e-7                     # redondeo a 6 decimales (5e-7) con margen de punto flotante (D51)
hay_panel = pytest.mark.skipif(not datos.RUTA_PANEL.exists(), reason="falta data/processed/panel_diario_montevideo.csv")


# ------------------------------------------------------------------------------------- panel sintético
def _panel_sintetico(n_dias=500, semilla=0, sobredispersion=True):
    "Media 3; con sobredispersión, gamma-Poisson con α = 0,1 (varianza μ + αμ²), como el panel real."
    rng = np.random.default_rng(semilla)
    dias = pd.date_range("2022-01-01", periods=n_dias, freq="D")
    p = pd.MultiIndex.from_product([dias, mod.MUNICIPIOS], names=["fecha", "zona_id"]).to_frame(index=False)
    mu = rng.gamma(shape=10, scale=0.3, size=len(p)) if sobredispersion else np.full(len(p), 3.0)
    p["n_siniestros"] = rng.poisson(mu)
    p["tipo_dia"] = p["fecha"].map(var.tipo_dia(dias))
    return p


@pytest.fixture(scope="module")
def sintetico():
    p = _panel_sintetico()
    origen = p["fecha"].max() - pd.Timedelta(days=13)
    return p, origen, mod.entrenar(mod.cargar_configuracion("solucion"), p[p["fecha"] < origen])


def test_predice_56_filas_con_intervalos_ordenados(sintetico):
    p, origen, m = sintetico
    s = mod.predecir_semana(m, p, origen)
    assert len(s) == 56 and s["fecha"].min() == origen and s["fecha"].nunique() == 7
    assert sorted(s["zona_id"].unique()) == mod.MUNICIPIOS
    assert (s["pred"] > 0).all() and s.notna().all().all()
    assert ((s["inf_95"] <= s["inf_80"]) & (s["inf_80"] <= s["sup_80"]) & (s["sup_80"] <= s["sup_95"])).all()
    for c in ("inf_80", "sup_80", "inf_95", "sup_95"):
        assert (s[c] >= 0).all() and (s[c] == np.floor(s[c])).all()
    assert (s["tipo_intervalo"] == "NB2").all() and m["origen_alpha"] == "nb2"


def test_prediccion_no_lee_el_objetivo_del_horizonte(sintetico):
    p, origen, m = sintetico
    basura = p.copy()
    basura.loc[basura["fecha"] >= origen, "n_siniestros"] = 10**6
    pd.testing.assert_frame_equal(mod.predecir_semana(m, p, origen), mod.predecir_semana(m, basura, origen))


def test_sin_filas_del_horizonte_usa_tipo_dia(sintetico):
    p, origen, m = sintetico
    pd.testing.assert_frame_equal(mod.predecir_semana(m, p, origen),
                                  mod.predecir_semana(m, p[p["fecha"] < origen], origen))


def test_ventana_de_364_dias(sintetico):
    _, origen, m = sintetico
    assert m["dias_entrenamiento"] == 364 and m["filas_entrenamiento"] == 364 * 8
    assert m["hasta"] == origen - pd.Timedelta(days=1) and m["desde"] == origen - pd.Timedelta(days=364)


def test_origen_distinto_del_modelo_falla(sintetico):
    p, origen, m = sintetico
    with pytest.raises(ValueError):
        mod.predecir_semana(m, p, origen + pd.Timedelta(days=7))


def test_entrenar_rechaza_objetivo_faltante():
    p = _panel_sintetico().astype({"n_siniestros": float})
    p.loc[p.index[-1], "n_siniestros"] = np.nan
    with pytest.raises(ValueError):
        mod.entrenar(mod.cargar_configuracion("solucion"), p)


def test_sin_alpha_los_intervalos_son_poisson(sintetico):
    p, origen, _ = sintetico
    m = mod.entrenar(mod.cargar_configuracion("solucion"), p[p["fecha"] < origen], ajustar_alpha=False)
    s = mod.predecir_semana(m, p, origen)
    assert (s["tipo_intervalo"] == "Poisson").all()
    assert (s["sup_95"] == stats.poisson(s["pred"]).ppf(0.975)).all()


def test_sin_sobredispersion_cae_a_poisson():
    "Datos Poisson puros: NB2 no da un α positivo, el plan B (D28) tampoco y los intervalos son Poisson (D50)."
    p = _panel_sintetico(sobredispersion=False)
    origen = p["fecha"].max() - pd.Timedelta(days=13)
    m = mod.entrenar(mod.cargar_configuracion("solucion"), p[p["fecha"] < origen])
    assert m["alpha"] is None and m["origen_alpha"] is None and not m["nb2_convergio"]
    assert (mod.predecir_semana(m, p, origen)["tipo_intervalo"] == "Poisson").all()


def test_contraste_xgboost_predice(sintetico):
    p, origen, _ = sintetico
    m = mod.entrenar(mod.cargar_configuracion("contraste"), p[p["fecha"] < origen], ajustar_alpha=False)
    s = mod.predecir_semana(m, p, origen)
    assert len(s) == 56 and (s["pred"] > 0).all()


# ----------------------------------------------------------------------------------- α (D29, D28, D50)
def test_decidir_alpha():
    llamado = []
    momentos = lambda: llamado.append(1) or 0.05
    assert mod.decidir_alpha(0.03, True, [], momentos) == (0.03, "nb2") and not llamado
    assert mod.decidir_alpha(0.03, False, [], 0.05) == (0.05, "momentos")
    assert mod.decidir_alpha(0.03, True, ["ConvergenceWarning: x"], 0.05) == (0.05, "momentos")
    assert mod.decidir_alpha(np.nan, True, [], 0.05) == (0.05, "momentos")
    assert mod.decidir_alpha(-1.0, True, [], 0.05) == (0.05, "momentos")
    assert mod.decidir_alpha(-1.0, True, [], -0.01) == (None, None)        # D50: Poisson
    assert mod.decidir_alpha(np.inf, False, [], np.nan) == (None, None)


def test_nb2_con_alpha_chico_tiende_a_poisson():
    mu = np.array([0.5, 2.0, 3.7, 8.0])
    pd.testing.assert_frame_equal(mod.intervalos(mu, 1e-9), mod.intervalos(mu, None))


# -------------------------------------------------------------------------------------------- tipo_dia
def test_tipo_dia_semana_de_2026():
    t = var.tipo_dia(pd.date_range("2026-01-01", periods=7))
    assert t.loc["2026-01-01"] == "feriado"                             # Año Nuevo, jueves
    assert t.loc["2026-01-03"] == "fin_semana" and t.loc["2026-01-02"] == "entre_semana"


@hay_panel
def test_tipo_dia_coincide_con_el_etl(panel_real):
    fechas = pd.DatetimeIndex(panel_real["fecha"].unique())
    etl = panel_real.drop_duplicates("fecha").set_index("fecha")["tipo_dia"]
    assert (var.tipo_dia(fechas) == etl.reindex(fechas)).all()


# ------------------------------------------------------------------------------- reproducción de la fase 2
@pytest.fixture(scope="module")
def panel_real():
    return datos.cargar_panel_desarrollo()


@pytest.fixture(scope="module")
def origenes(panel_real):
    fechas = pd.DatetimeIndex(sorted(panel_real["fecha"].unique()))
    o = list(fechas[987::7])
    assert len(o) == 47 and o[-1] + pd.Timedelta(days=6) == datos.ULTIMO_DIA_DESARROLLO
    return o


def _referencia_fase2(panel, origen, cols, ventana):
    "Camino de la celda paso-a-motor (fase 2) para el conjunto (a): μ del GLM Poisson y α de NB2 por máxima verosimilitud."
    vista = panel[panel["fecha"] < origen + pd.Timedelta(days=7)].copy()
    vista.loc[vista["fecha"] >= origen, "n_siniestros"] = np.nan
    ent = var.matriz_entrenamiento(vista, origen, dias_ventana=ventana)
    hor = var.variables_horizonte(vista, origen, dias_ventana=ventana)

    def disenio(df):
        X = pd.DataFrame(index=df.index)
        for z in sorted(panel["zona_id"].unique()):
            X["mun_" + z.replace("MUNICIPIO ", "")] = (df["zona_id"] == z).astype(float)
        cal = df["calendario"].astype(str)
        for n in var.NIVELES_CALENDARIO[1:]:
            X["cal_" + n] = (cal == n).astype(float)
        return X[cols]

    X, y, Xh = disenio(ent), ent["n_siniestros"], disenio(hor)
    pred = sm.GLM(y, X, family=sm.families.Poisson()).fit().predict(Xh)
    alpha = float(NegativeBinomial(y, X, loglike_method="nb2").fit(method="newton", maxiter=100, disp=0).params["alpha"])
    return hor[["fecha", "zona_id"]].assign(pred=np.asarray(pred, dtype=float)), alpha


@pytest.fixture(scope="module")
def backtest_solucion(panel_real, origenes):
    "Solución reentrenada en cada corte con src/modelo.py, y la referencia de la fase 2 del mismo corte."
    cfg = mod.cargar_configuracion("solucion")
    filas, alphas = [], []
    for corte, o in enumerate(origenes, start=1):
        m = mod.entrenar(cfg, panel_real[panel_real["fecha"] < o])
        s = mod.predecir_semana(m, panel_real[panel_real["fecha"] < o + pd.Timedelta(days=7)], o)
        ref, a_ref = _referencia_fase2(panel_real, o, cfg["conjunto_de_variables"]["columnas"], cfg["ventana"]["dias"])
        filas.append(s.merge(ref.rename(columns={"pred": "pred_ref"}), on=["fecha", "zona_id"], validate="one_to_one")
                     .assign(corte=corte, origen=o))
        alphas.append({"corte": corte, "alpha": m["alpha"], "alpha_ref": a_ref, "origen_alpha": m["origen_alpha"]})
    return pd.concat(filas, ignore_index=True), pd.DataFrame(alphas)


@hay_panel
def test_solucion_reproduce_el_camino_de_la_fase_2(backtest_solucion):
    pred, alphas = backtest_solucion
    assert len(pred) == 47 * 56
    assert (pred["pred"] - pred["pred_ref"]).abs().max() <= TOL_EXACTA
    assert (alphas["alpha"] - alphas["alpha_ref"]).abs().max() <= TOL_EXACTA
    assert (alphas["origen_alpha"] == "nb2").all()


@hay_panel
def test_solucion_reproduce_tablas_31_y_45(backtest_solucion):
    pred, alphas = backtest_solucion
    cfg = mod.cargar_configuracion("solucion")
    t31 = pd.read_csv(DIR_TABLAS / "31_paso_c_predicciones.csv", parse_dates=["fecha"], encoding="utf-8")
    t31 = t31[t31["configuracion"] == cfg["configuracion"]]
    m = pred.merge(t31, on=["corte", "fecha", "zona_id"], validate="one_to_one", suffixes=("", "_t31"))
    assert len(m) == 47 * 56 and (m["pred"] - m["pred_t31"]).abs().max() <= TOL_REDONDEO
    t45 = pd.read_csv(DIR_TABLAS / "45_fase3c_nb2_364_alpha_por_corte.csv", encoding="utf-8")
    assert len(t45) == 47 and np.abs(alphas["alpha"].to_numpy() - t45["alpha_usado"].to_numpy()).max() <= TOL_REDONDEO


@hay_panel
def test_intervalos_reproducen_tablas_46(backtest_solucion):
    pred, _ = backtest_solucion
    t31 = pd.read_csv(DIR_TABLAS / "31_paso_c_predicciones.csv", parse_dates=["fecha"], encoding="utf-8")
    m = pred.merge(t31[["fecha", "zona_id", "n_siniestros"]].drop_duplicates(), on=["fecha", "zona_id"], validate="one_to_one")
    assert len(m) == 47 * 56
    t46 = pd.read_csv(DIR_TABLAS / "46_fase3c_cobertura_intervalos.csv", encoding="utf-8")
    t46 = t46[(t46["municipio"] == "todos") & t46["intervalo"].str.startswith("NB2")].set_index("nivel_nominal")
    for nivel in (80, 95):
        dentro = ((m["n_siniestros"] >= m[f"inf_{nivel}"]) & (m["n_siniestros"] <= m[f"sup_{nivel}"])).mean()
        assert abs(dentro - t46.loc[nivel, "cobertura_empirica"]) <= TOL_REDONDEO


@hay_panel
@pytest.mark.parametrize("papel", ["sensibilidad", "contraste"])
def test_sensibilidad_y_contraste_reproducen_tablas_31(panel_real, origenes, papel):
    cfg = mod.cargar_configuracion(papel)
    t31 = pd.read_csv(DIR_TABLAS / "31_paso_c_predicciones.csv", parse_dates=["fecha"], encoding="utf-8")
    t31 = t31[t31["configuracion"] == cfg["configuracion"]]
    assert len(t31) == 47 * 56
    dif = 0.0
    for o in origenes:
        m = mod.entrenar(cfg, panel_real[panel_real["fecha"] < o], ajustar_alpha=False)
        s = mod.predecir_semana(m, panel_real[panel_real["fecha"] < o], o)
        r = s.merge(t31, on=["fecha", "zona_id"], validate="one_to_one", suffixes=("", "_t31"))
        dif = max(dif, float((r["pred"] - r["pred_t31"]).abs().max()))
    assert dif <= TOL_REDONDEO
