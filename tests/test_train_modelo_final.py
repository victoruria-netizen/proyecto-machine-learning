"""Pruebas de train/train_modelo_final.py (decisiones del 21/10/2026).

El script no importa src/ (el contenedor tiene pandas 1.5.3, sin statsmodels ni holidays): arma la matriz del conjunto
(a) y ajusta el GLM por su cuenta. Estas pruebas exigen que lo haga igual que src/:
1. constantes (municipios, columnas, ventana, configuración) y calendario de la semana del 2026-01-01 iguales a src/;
2. con el panel de desarrollo (``cargar_panel_desarrollo``; el script sólo lee el bloque final en el servidor, D51):
   filas y matriz idénticas a ``var.matriz_entrenamiento`` + ``mod.matriz_disenio``, y coeficientes, μ y α por momentos
   dentro del criterio de comparación (1e-6) contra statsmodels.
"""

import importlib.util

import numpy as np
import pandas as pd
import pytest
import statsmodels.api as sm

from src import datos, modelo as mod, variables as var

_spec = importlib.util.spec_from_file_location("train_modelo_final", datos.RAIZ / "train" / "train_modelo_final.py")
tmf = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(tmf)

hay_panel = pytest.mark.skipif(not datos.RUTA_PANEL.exists(), reason="falta data/processed/panel_diario_montevideo.csv")


def test_constantes_iguales_a_src():
    cfg = mod.cargar_configuracion("solucion")
    assert tmf.MUNICIPIOS == mod.MUNICIPIOS
    assert tmf.COLUMNAS == cfg["conjunto_de_variables"]["columnas"]
    assert tmf.NIVELES_CALENDARIO == var.NIVELES_CALENDARIO and tmf.HORIZONTE == var.HORIZONTE
    assert tmf.VENTANA_DIAS == cfg["ventana"]["dias"] and tmf.CONFIGURACION == cfg["configuracion"]
    assert tmf.FECHA_CORTE == datos.FECHA_FIN_PERIODO
    assert max(var.NIVELES_RECIENTES + var.REZAGOS) == tmf.HISTORIA_MINIMA


def test_calendario_de_la_semana_igual_a_tipo_dia():
    t = var.tipo_dia(pd.date_range("2026-01-01", periods=7))
    assert {d.strftime("%Y-%m-%d"): v for d, v in t.items()} == tmf.TIPO_DIA_SEMANA
    assert tmf.tipo_dia_con_holidays(t.index) == tmf.TIPO_DIA_SEMANA       # la rama del script con holidays


@pytest.fixture(scope="module")
def panel_dev():
    return datos.cargar_panel_desarrollo()


@pytest.fixture(scope="module")
def origenes(panel_dev):
    "Tres orígenes de validación (el primero, uno intermedio y el día siguiente al desarrollo)."
    return [pd.Timestamp("2024-03-14"), pd.Timestamp("2024-09-19"), datos.ULTIMO_DIA_DESARROLLO + pd.Timedelta(days=1)]


@hay_panel
def test_matriz_identica_a_src(panel_dev, origenes):
    cols = mod.cargar_configuracion("solucion")["conjunto_de_variables"]["columnas"]
    for origen in origenes:
        ent_src = var.matriz_entrenamiento(panel_dev, origen, dias_ventana=tmf.VENTANA_DIAS)
        ent = tmf.filas_entrenamiento(panel_dev, origen)
        assert ent["fecha"].tolist() == ent_src["fecha"].tolist() and ent["zona_id"].tolist() == ent_src["zona_id"].tolist()
        assert (ent["n_siniestros"].to_numpy(dtype=float) == ent_src["n_siniestros"].to_numpy(dtype=float)).all()
        X = tmf.matriz(ent["fecha"], ent["zona_id"], ent["tipo_dia"])
        assert (X == mod.matriz_disenio(ent_src, cols).to_numpy()).all()


@hay_panel
def test_glm_mu_y_alpha_dentro_del_criterio(panel_dev, origenes):
    cfg = mod.cargar_configuracion("solucion")
    for origen in origenes:
        hasta = panel_dev[panel_dev["fecha"] < origen]
        m_src = mod.entrenar(cfg, hasta, ajustar_alpha=False)
        m = tmf.entrenar(panel_dev, origen)
        assert m["convergio"] and m["filas_entrenamiento"] == m_src["filas_entrenamiento"]
        assert tmf.diferencia_relativa([m["coeficientes"][c] for c in tmf.COLUMNAS],
                                       [m_src["coeficientes"][c] for c in tmf.COLUMNAS]) <= tmf.TOL_COMPARACION

        dias = pd.date_range(origen, periods=7)
        cal = {d.strftime("%Y-%m-%d"): v for d, v in var.tipo_dia(dias).items()}
        s_src = mod.predecir_semana(m_src, hasta, origen)
        s = tmf.predecir_semana(m["coeficientes"], origen, cal)
        assert s["calendario"].tolist() == s_src["calendario"].astype(str).tolist()
        assert tmf.diferencia_relativa(s["pred"], s_src["pred"]) <= tmf.TOL_COMPARACION

        # α por momentos de src (el mismo cálculo que mod._alpha_nb2, con μ de statsmodels)
        ent = var.matriz_entrenamiento(hasta, origen, dias_ventana=tmf.VENTANA_DIAS)
        X, y = mod.matriz_disenio(ent, cfg["conjunto_de_variables"]["columnas"]), ent["n_siniestros"].astype(float)
        mu = sm.GLM(y, X, family=sm.families.Poisson()).fit().fittedvalues
        a_src = float(sm.OLS(((y - mu) ** 2 - y) / mu, mu).fit().params.iloc[0])
        assert tmf.diferencia_relativa([m["alpha"]], [a_src]) <= tmf.TOL_COMPARACION


def test_raiz_en_el_layout_del_servidor(tmp_path):
    "En el servidor el script está en la raíz del workspace (/work), con data/ al lado; en el repositorio, en train/."
    (tmp_path / "data" / "processed").mkdir(parents=True)
    (tmp_path / tmf.REL_PANEL).write_text("", encoding="utf-8")
    script = tmp_path / "train_modelo_final.py"
    script.write_bytes((datos.RAIZ / "train" / "train_modelo_final.py").read_bytes())
    spec = importlib.util.spec_from_file_location("tmf_servidor", script)
    copia = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(copia)
    assert copia.RAIZ == tmp_path and copia.RUTA_MODELO_LOCAL == tmp_path / "models" / "modelo_final.json"
    assert tmf.RAIZ == datos.RAIZ or not datos.RUTA_PANEL.exists()


def test_irls_recupera_coeficientes_conocidos():
    rng = np.random.default_rng(0)
    X = np.eye(3)[rng.integers(0, 3, 30_000)]
    beta = np.array([0.5, 1.0, 1.5])
    y = rng.poisson(np.exp(X @ beta)).astype(float)
    b, _, _, convergio = tmf.irls_poisson(X, y)
    medias = np.array([y[X[:, j] == 1].mean() for j in range(3)])
    assert convergio and np.allclose(b, np.log(medias), rtol=0, atol=1e-12)     # MLE con indicadoras: log de la media
