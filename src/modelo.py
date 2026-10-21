"""Entrenamiento y predicción semanal de la solución: única implementación para el notebook de evaluación final y el prototipo.

Reproduce el camino de la fase 2 (celda ``paso-a-motor`` de ``notebooks/modelos_candidatos.ipynb``): filas de
entrenamiento de ``var.matriz_entrenamiento``, matriz de diseño de D31 y ajuste con los valores por defecto de cada
biblioteca. La configuración sale de ``experiments/modelos_candidatos/solucion_seleccionada.json`` (D42) y no se
redefine acá.

Este módulo **no lee el panel**: quien llama le pasa los datos. Así, qué tramo del panel se usa lo decide el código que
lo carga (``src.datos.cargar_panel_desarrollo()`` o, sólo en ``notebooks/evaluacion_final.ipynb``, el bloque final).

Intervalos de predicción (D44, con el fallback de D50): μ del modelo y α de NB2 (a) ajustada con la misma ventana y las
mismas filas. Si NB2 no converge según D29, α por momentos (plan B de D28); si tampoco da un α finito y positivo, el
intervalo es Poisson con la misma μ. Sin α (``ajustar_alpha=False``), también Poisson.

Dependencias (D54): statsmodels y xgboost se importan sólo dentro de ``entrenar``. Cargar el modelo final
(``cargar_modelo``) y predecir con él usa numpy, pandas, scipy (cuantiles de D44) y ``src.variables`` (calendario, D50),
así que el prototipo y el servidor pueden predecir sin esas dos bibliotecas.
"""

import json
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

from src import variables as var

RAIZ = Path(__file__).resolve().parent.parent
RUTA_SOLUCION = RAIZ / "experiments" / "modelos_candidatos" / "solucion_seleccionada.json"

MUNICIPIOS = ["MUNICIPIO A", "MUNICIPIO B", "MUNICIPIO C", "MUNICIPIO CH",
              "MUNICIPIO D", "MUNICIPIO E", "MUNICIPIO F", "MUNICIPIO G"]
NIVELES_INTERVALO = {80: (0.10, 0.90), 95: (0.025, 0.975)}        # D44: colas iguales


def cargar_configuracion(papel: str = "solucion", ruta=RUTA_SOLUCION) -> dict:
    """Bloque ``papel`` de ``solucion_seleccionada.json``: ``solucion``, ``sensibilidad`` o ``contraste``."""
    return json.loads(Path(ruta).read_text(encoding="utf-8"))[papel]


# ----------------------------------------------------------------------------------------- matriz D31
def matriz_disenio(df: pd.DataFrame, columnas) -> pd.DataFrame:
    """Columnas del conjunto (a) (D31) a partir de la salida de ``var.matriz_entrenamiento`` o de las filas del horizonte.

    ``mun_<letra>``: indicadora de cada municipio, sin constante. ``cal_<nivel>``: indicadora del calendario de 8 niveles,
    lunes de referencia. Sólo admite esas columnas: la solución, la sensibilidad y el contraste usan el conjunto (a).
    """
    cal = df["calendario"].astype(str)
    X = pd.DataFrame(index=df.index)
    for c in columnas:
        if c.startswith("mun_"):
            X[c] = (df["zona_id"] == "MUNICIPIO " + c.removeprefix("mun_")).astype(float)
        elif c.startswith("cal_"):
            X[c] = (cal == c.removeprefix("cal_")).astype(float)
        else:
            raise ValueError(f"columna fuera del conjunto (a): {c}")
    return X


def _con_avisos(f):
    "Ejecuta f() y devuelve también los avisos emitidos (salvo el DeprecationWarning de pandas de pytest.ini)."
    with warnings.catch_warnings(record=True) as avisos:
        warnings.simplefilter("always")
        warnings.filterwarnings("ignore", message="The .generic. unit for NumPy timedelta", category=DeprecationWarning)
        out = f()
    return out, [f"{a.category.__name__}: {a.message}" for a in avisos]


# ---------------------------------------------------------------------------------------- α de NB2
def decidir_alpha(alpha_mv: float, convergio: bool, avisos, alpha_momentos=None) -> tuple:
    """α para los intervalos y su origen: ``"nb2"``, ``"momentos"`` (plan B de D28) o ``None`` (Poisson; D50).

    NB2 cuenta como no convergida si ``convergio`` es falso, si hubo un ``ConvergenceWarning`` o si α no es finito o no
    es positivo (D29). ``alpha_momentos`` es un número o una función sin argumentos que lo calcula (sólo se llama si hace
    falta).
    """
    no_convergio = (not convergio or any(a.startswith("ConvergenceWarning") for a in avisos)
                    or not np.isfinite(alpha_mv) or alpha_mv <= 0)
    if not no_convergio:
        return float(alpha_mv), "nb2"
    a_m = alpha_momentos() if callable(alpha_momentos) else alpha_momentos
    if a_m is not None and np.isfinite(a_m) and a_m > 0:
        return float(a_m), "momentos"
    return None, None


def _alpha_nb2(X: pd.DataFrame, y: pd.Series, sm) -> dict:
    "NB2 (a) con las filas de entrenamiento del modelo (adenda, ítems 5 y 6; D28; D50). ``sm``: statsmodels.api, de ``entrenar``."
    res, avisos = _con_avisos(lambda: sm.NegativeBinomial(y, X, loglike_method="nb2").fit(method="newton", maxiter=100, disp=0))
    alpha_mv = float(res.params["alpha"])

    def momentos():
        # Regresión auxiliar sin intercepto de ((y − μ)² − y)/μ sobre μ, con μ del GLM Poisson (Cameron y Trivedi, 1990)
        mu = sm.GLM(y, X, family=sm.families.Poisson()).fit().fittedvalues
        return float(sm.OLS(((y - mu) ** 2 - y) / mu, mu).fit().params.iloc[0])

    alpha, origen = decidir_alpha(alpha_mv, bool(res.mle_retvals["converged"]), avisos, momentos)
    return {"alpha": alpha, "origen_alpha": origen, "alpha_mv": alpha_mv,
            "nb2_convergio": origen == "nb2", "nb2_iteraciones": int(res.mle_retvals["iterations"]),
            "nb2_avisos": sorted(set(avisos))}


# ------------------------------------------------------------------------------------------- entrenar
def entrenar(config: dict, panel_hasta: pd.DataFrame, ajustar_alpha: bool = True) -> dict:
    """Ajusta el modelo de ``config`` con lo conocido en ``panel_hasta`` y la ventana de la configuración.

    ``config``: un bloque de ``solucion_seleccionada.json`` (ver ``cargar_configuracion``). ``panel_hasta``: el panel
    (``fecha``, ``zona_id``, ``n_siniestros``, ``tipo_dia``) con los días conocidos; el origen de la predicción es el día
    siguiente al último. Las filas de entrenamiento son las de ``var.matriz_entrenamiento`` con la ventana de la
    configuración, igual que en el backtesting de la fase 2.

    Devuelve un diccionario: configuración, origen, ventana, columnas, días y filas de entrenamiento, el modelo ajustado
    (``coeficientes`` del GLM o ``xgb``, el ``XGBRegressor``) y, con ``ajustar_alpha``, el α de los intervalos (D44, D50).
    """
    import statsmodels.api as sm        # D54: sólo el entrenamiento depende de statsmodels y xgboost
    import xgboost

    if panel_hasta["n_siniestros"].isna().any():
        raise ValueError("panel_hasta tiene objetivos faltantes: debe traer sólo días conocidos")
    if sorted(panel_hasta["zona_id"].unique()) != MUNICIPIOS:
        raise ValueError("panel_hasta debe tener los 8 municipios")
    origen = panel_hasta["fecha"].max() + pd.Timedelta(days=1)
    ventana = config["ventana"]["dias"]
    cols = config["conjunto_de_variables"]["columnas"]

    ent = var.matriz_entrenamiento(panel_hasta, origen, dias_ventana=ventana)
    X, y = matriz_disenio(ent, cols), ent["n_siniestros"].astype(float)
    modelo = {"configuracion": config["configuracion"], "modelo": config["modelo"], "origen": origen,
              "ventana_dias": ventana, "columnas": list(cols), "dias_entrenamiento": int(ent["fecha"].nunique()),
              "filas_entrenamiento": len(ent), "desde": ent["fecha"].min(), "hasta": ent["fecha"].max()}

    if config["modelo"] == "GLM":
        res, avisos = _con_avisos(lambda: sm.GLM(y, X, family=sm.families.Poisson()).fit())
        modelo.update(coeficientes={c: float(res.params[c]) for c in cols}, convergio=bool(res.converged),
                      iteraciones=int(res.fit_history["iteration"]), avisos=sorted(set(avisos)))
    elif config["modelo"] == "XGBoost":
        m, avisos = _con_avisos(lambda: xgboost.XGBRegressor(**config["hiperparametros"]).fit(X, y))
        modelo.update(xgb=m, avisos=sorted(set(avisos)))
    else:
        raise ValueError(f"modelo no previsto: {config['modelo']}")

    modelo.update(_alpha_nb2(X, y, sm) if ajustar_alpha else {"alpha": None, "origen_alpha": None})
    return modelo


# ------------------------------------------------------------------------------- guardar y cargar
_CAMPOS_FECHA = ("origen", "desde", "hasta")


def _sin_no_finitos(x):
    "Reemplaza los float no finitos (NaN, ±inf) por None, para escribir JSON estándar (D55)."
    if isinstance(x, dict):
        return {k: _sin_no_finitos(v) for k, v in x.items()}
    if isinstance(x, list):
        return [_sin_no_finitos(v) for v in x]
    if isinstance(x, float) and not np.isfinite(x):
        return None
    return x


def guardar_modelo(modelo: dict, ruta) -> None:
    """Escribe el GLM de ``entrenar`` en JSON (coeficientes, α y datos del ajuste), sin pickle.

    Sólo el GLM: μ = exp(X β) con la matriz de D31, así que los coeficientes bastan. Los float de JSON se escriben con
    su ``repr`` y se leen exactos. JSON estándar (D55): un valor no finito, como ``alpha_mv`` cuando NB2 no converge,
    se escribe como ``null``.
    """
    if modelo["modelo"] != "GLM":
        raise ValueError(f"sólo se guarda el GLM en JSON, no {modelo['modelo']}")
    out = dict(modelo)
    for c in _CAMPOS_FECHA:
        out[c] = pd.Timestamp(out[c]).strftime("%Y-%m-%d")
    Path(ruta).write_text(json.dumps(_sin_no_finitos(out), ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")


def cargar_modelo(ruta) -> dict:
    """Lee el JSON de ``guardar_modelo`` y devuelve el diccionario que espera ``predecir_semana`` (sin statsmodels, D54).

    Un ``alpha_mv`` no finito al guardar vuelve como None (D55); no interviene en la predicción.
    """
    modelo = json.loads(Path(ruta).read_text(encoding="utf-8"))
    if modelo.get("modelo") != "GLM" or sorted(modelo["coeficientes"]) != sorted(modelo["columnas"]):
        raise ValueError(f"{ruta} no es un GLM guardado con guardar_modelo")
    for c in _CAMPOS_FECHA:
        modelo[c] = pd.Timestamp(modelo[c])
    return modelo


# --------------------------------------------------------------------------------------- predecir
def filas_horizonte(historia: pd.DataFrame, origen, horizonte: int = var.HORIZONTE) -> pd.DataFrame:
    """Los ``horizonte`` días desde el origen × 8 municipios, con ``tipo_dia`` y ``calendario``.

    De ``historia`` sólo se lee ``tipo_dia`` de los días del horizonte, si están; si no, sale de ``var.tipo_dia`` (D50).
    El objetivo de esos días no se lee.
    """
    origen = pd.Timestamp(origen)
    dias = pd.date_range(origen, periods=horizonte, freq="D")
    hor = pd.MultiIndex.from_product([dias, MUNICIPIOS], names=["fecha", "zona_id"]).to_frame(index=False)
    conocido = historia.loc[historia["fecha"].isin(dias), ["fecha", "zona_id", "tipo_dia"]]
    hor = hor.merge(conocido, on=["fecha", "zona_id"], how="left", validate="one_to_one")
    faltan = hor["tipo_dia"].isna()
    hor.loc[faltan, "tipo_dia"] = hor.loc[faltan, "fecha"].map(var.tipo_dia(dias))
    hor["calendario"] = var.calendario_8(hor)
    return hor


def intervalos(mu, alpha=None) -> pd.DataFrame:
    """Cuantiles centrales de colas iguales (D44): NB2 con media μ y varianza μ + αμ²; Poisson si ``alpha`` es None."""
    mu = np.asarray(mu, dtype=float)
    if alpha is None:
        dist = stats.poisson(mu)
    else:
        r = 1 / alpha
        dist = stats.nbinom(r, r / (r + mu))                    # media r(1 − p)/p = μ
    out = {}
    for nivel, (ql, qh) in NIVELES_INTERVALO.items():
        out[f"inf_{nivel}"], out[f"sup_{nivel}"] = dist.ppf(ql), dist.ppf(qh)
    return pd.DataFrame(out)


def predecir_semana(modelo: dict, historia: pd.DataFrame, origen) -> pd.DataFrame:
    """Predicción de los 7 días desde ``origen`` para los 8 municipios (56 filas), con intervalos del 80 % y 95 %.

    ``origen`` tiene que ser el del modelo (el día siguiente a sus datos): el modelo se reentrena cada 7 días y no se
    usa para otra semana. Columnas: ``fecha``, ``zona_id``, ``calendario``, ``pred`` (μ), ``inf_80``, ``sup_80``,
    ``inf_95``, ``sup_95``, ``tipo_intervalo`` (``NB2`` o ``Poisson``), ``alpha`` y ``origen_alpha``.
    """
    origen = pd.Timestamp(origen)
    if origen != modelo["origen"]:
        raise ValueError(f"el modelo predice desde {modelo['origen'].date()}, no desde {origen.date()}")
    hor = filas_horizonte(historia, origen)
    Xh = matriz_disenio(hor, modelo["columnas"])
    if modelo["modelo"] == "GLM":
        beta = np.array([modelo["coeficientes"][c] for c in modelo["columnas"]])
        pred = np.exp(Xh.to_numpy() @ beta)
    else:
        pred = np.asarray(modelo["xgb"].predict(Xh), dtype=float)
    out = hor[["fecha", "zona_id", "calendario"]].assign(pred=pred)
    out = pd.concat([out, intervalos(pred, modelo["alpha"])], axis=1)
    out["tipo_intervalo"] = "Poisson" if modelo["alpha"] is None else "NB2"
    out["alpha"] = modelo["alpha"]
    out["origen_alpha"] = modelo["origen_alpha"]
    return out
