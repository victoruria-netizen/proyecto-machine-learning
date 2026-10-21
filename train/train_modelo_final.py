# train_modelo_final.py
#
# Entrenamiento del modelo final del Entregable 3 en el servidor (submit_cpu). Es la misma exportación que la
# sección 13 de notebooks/evaluacion_final.ipynb (D51), para comparar el resultado del servidor con el local.
#
# EXCEPCIÓN DECLARADA (D51): este script lee el panel COMPLETO, incluido el bloque final (2025-02-06 -> 2025-12-31),
# porque el modelo final se entrena con todos los datos hasta el 2025-12-31. No evalúa nada: no calcula ninguna
# métrica sobre el bloque final. Fuera de este script y de evaluacion_final.ipynb, el panel se lee sólo con
# src/datos.py:cargar_panel_desarrollo().
#
# Qué hace: GLM Poisson (a), ventana deslizante de 364 días (D42), con las filas 2025-01-02 .. 2025-12-31; α de los
# intervalos por momentos (plan B de D28, con μ del GLM); μ de la semana del 2026-01-01 (8 municipios x 7 días). Si
# encuentra models/modelo_final.json (la exportación local), compara: diferencia relativa máxima <= 1e-6 en los
# coeficientes, en μ de las 56 filas y en α (criterio fijado el 21/10/2026, antes de correrlo en el servidor).
#
# Por qué no importa src/ (decisiones del 21/10/2026): el contenedor trae Python 3.10, numpy 1.24.4, pandas 1.5.3 y
# scikit-learn 1.2.0, sin statsmodels (train/README.md); src/variables.py usa stack(future_stack=True) (pandas >= 2.1)
# e importa holidays. Por eso:
#   - la matriz del conjunto (a) se arma acá, sólo con numpy y pandas; tests/test_train_modelo_final.py exige que sea
#     idéntica a var.matriz_entrenamiento + mod.matriz_disenio;
#   - el GLM se ajusta con IRLS en numpy (no statsmodels ni scikit-learn);
#   - NB2 por máxima verosimilitud no se intenta (sin statsmodels): α sale por momentos. En la exportación local NB2
#     no convergió en esta ventana y α también salió por momentos (models/metadata.json), así que son comparables;
#   - el tipo_dia de la semana a predecir es una constante calculada localmente con var.tipo_dia (D50); el test exige
#     que coincida. Si el contenedor tiene holidays, el script además lo recalcula y lo compara.
#
# Uso: submit_cpu train_modelo_final.py
#      Localmente: python train/train_modelo_final.py --salida <carpeta fuera del repositorio>
# Entrada: data/processed/panel_diario_montevideo.csv (no se versiona) y, para la comparación, models/modelo_final.json.
#      En el servidor van en /train/data/processed/ y /train/models/ (Jupyter), junto al script en /train/; el
#      contenedor los ve en /work (train/README.md).
# Salida: /outputs/runs/<RUN_ID>/ (modelo_final.json, prediccion_semana_2026-01-01.csv, resumen_corrida.json).

import argparse
import hashlib
import importlib.util
import json
import platform
import sys
from datetime import datetime
from importlib import metadata as importlib_metadata
from pathlib import Path

import numpy as np
import pandas as pd

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REL_PANEL = Path("data") / "processed" / "panel_diario_montevideo.csv"


def _raiz() -> Path:
    """Primera carpeta, subiendo desde el script o desde el directorio de trabajo, que contiene el panel.

    En el repositorio es la raíz (el script está en train/); en el servidor es /work, donde el script queda en la raíz
    del workspace, como train_base.py (log del 18/09/2026: «Raíz del repositorio: /work»).
    """
    aqui = Path(__file__).resolve()
    candidatos = [aqui.parent, *aqui.parents, Path.cwd(), *Path.cwd().parents]
    return next((p for p in candidatos if (p / REL_PANEL).exists()), aqui.parent.parent)


RAIZ = _raiz()
RUTA_PANEL = RAIZ / REL_PANEL
RUTA_MODELO_LOCAL = RAIZ / "models" / "modelo_final.json"
SHA256_PANEL = "82467fc87b5d2bceb24ec6f3c5072e1b7cf9e75507b1d5c5a4d20153114a1b06"     # models/metadata.json

CONFIGURACION = "GLM Poisson (a) [deslizante 364 d]"
FECHA_CORTE = pd.Timestamp("2025-12-31")
VENTANA_DIAS = 364
HORIZONTE = 7
HISTORIA_MINIMA = 91        # nivel reciente más largo de var.matriz_entrenamiento: con menos, src descarta filas
MUNICIPIOS = ["MUNICIPIO A", "MUNICIPIO B", "MUNICIPIO C", "MUNICIPIO CH",
              "MUNICIPIO D", "MUNICIPIO E", "MUNICIPIO F", "MUNICIPIO G"]
DIAS_SEMANA = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
NIVELES_CALENDARIO = DIAS_SEMANA + ["feriado"]
COLUMNAS = ["mun_" + z.replace("MUNICIPIO ", "") for z in MUNICIPIOS] + ["cal_" + n for n in NIVELES_CALENDARIO[1:]]
TIPOS_DIA = {"entre_semana", "fin_semana", "feriado"}

# tipo_dia de la semana del 2026-01-01, de var.tipo_dia (holidays 0.103, Uruguay, categorías public y bank; D50)
TIPO_DIA_SEMANA = {"2026-01-01": "feriado", "2026-01-02": "entre_semana", "2026-01-03": "fin_semana",
                   "2026-01-04": "fin_semana", "2026-01-05": "entre_semana", "2026-01-06": "feriado",
                   "2026-01-07": "entre_semana"}
TOL_COMPARACION = 1e-6
IMPLEMENTACION = ("IRLS en numpy (mínimos cuadrados ponderados con numpy.linalg.lstsq; arranque μ = (y + media(y))/2, "
                  "como statsmodels; corta cuando el cambio relativo de la desvianza es <= 1e-12)")


# ------------------------------------------------------------------------------------------- datos
def leer_panel(ruta) -> pd.DataFrame:
    panel = pd.read_csv(ruta, encoding="utf-8")
    panel["fecha"] = pd.to_datetime(panel["fecha"], format="%Y-%m-%d")
    return panel.sort_values(["fecha", "zona_id"]).reset_index(drop=True)


def calendario_8(fecha: pd.Series, tipo_dia: pd.Series) -> np.ndarray:
    "Misma regla que var.calendario_8: día de la semana, salvo feriado, que tiene prioridad."
    tipo = np.asarray(tipo_dia, dtype=object)
    desconocidos = set(tipo) - TIPOS_DIA
    if desconocidos:
        raise ValueError(f"tipo_dia con valores no previstos: {sorted(desconocidos)}")
    dia = np.array(DIAS_SEMANA, dtype=object)[np.asarray(pd.DatetimeIndex(fecha).dayofweek)]
    return np.where(tipo == "feriado", "feriado", dia)


def matriz(fecha, zona_id, tipo_dia) -> np.ndarray:
    "Matriz de D31 del conjunto (a): indicadoras de municipio sin constante y calendario de 8 niveles, lunes de referencia."
    cal = calendario_8(fecha, tipo_dia)
    zona = np.asarray(zona_id, dtype=object)
    X = np.zeros((len(zona), len(COLUMNAS)))
    for j, c in enumerate(COLUMNAS):
        if c.startswith("mun_"):
            X[:, j] = zona == "MUNICIPIO " + c[len("mun_"):]
        else:
            X[:, j] = cal == c[len("cal_"):]
    return X


def filas_entrenamiento(panel: pd.DataFrame, origen, ventana: int = VENTANA_DIAS) -> pd.DataFrame:
    """Días [origen - ventana, origen) x 8 municipios, ordenados por fecha y municipio.

    Son las filas de var.matriz_entrenamiento(..., dias_ventana=ventana) cuando hay historia completa antes de la
    ventana (rezagos y nivel reciente de 91 días); si no la hay, src descartaría filas y acá se detiene.
    """
    origen = pd.Timestamp(origen)
    desde = origen - pd.Timedelta(days=ventana)
    historia = panel[(panel["fecha"] >= desde - pd.Timedelta(days=HISTORIA_MINIMA)) & (panel["fecha"] < origen)]
    dias = pd.date_range(desde - pd.Timedelta(days=HISTORIA_MINIMA), origen - pd.Timedelta(days=1), freq="D")
    if (len(historia) != len(dias) * len(MUNICIPIOS) or historia["n_siniestros"].isna().any()
            or sorted(historia["zona_id"].unique()) != MUNICIPIOS
            or not pd.DatetimeIndex(sorted(historia["fecha"].unique())).equals(dias)):
        raise ValueError("historia incompleta antes del origen: var.matriz_entrenamiento descartaría filas")
    ent = panel[(panel["fecha"] >= desde) & (panel["fecha"] < origen)]
    return ent[["fecha", "zona_id", "tipo_dia", "n_siniestros"]].sort_values(["fecha", "zona_id"]).reset_index(drop=True)


# -------------------------------------------------------------------------------------------- ajuste
def desvianza(y, mu) -> float:
    termino = np.where(y > 0, y * np.log(np.where(y > 0, y, 1) / mu), 0.0)
    return float(2 * np.sum(termino - (y - mu)))


def irls_poisson(X: np.ndarray, y: np.ndarray, tol: float = 1e-12, max_iter: int = 100):
    "GLM Poisson con enlace log por IRLS. Devuelve (β, μ, iteraciones, convergió)."
    mu = (y + y.mean()) / 2
    eta = np.log(mu)
    dev_previa = np.inf
    for iteracion in range(1, max_iter + 1):
        z = eta + (y - mu) / mu
        raiz_w = np.sqrt(mu)
        beta = np.linalg.lstsq(X * raiz_w[:, None], z * raiz_w, rcond=None)[0]
        eta = X @ beta
        mu = np.exp(eta)
        dev = desvianza(y, mu)
        if abs(dev - dev_previa) <= tol * abs(dev):
            return beta, mu, iteracion, True
        dev_previa = dev
    return beta, mu, max_iter, False


def alpha_momentos(y: np.ndarray, mu: np.ndarray) -> float:
    "Plan B de D28: regresión sin intercepto de ((y - μ)² - y)/μ sobre μ (Cameron y Trivedi, 1990)."
    aux = ((y - mu) ** 2 - y) / mu
    return float(np.dot(mu, aux) / np.dot(mu, mu))


def entrenar(panel: pd.DataFrame, origen) -> dict:
    ent = filas_entrenamiento(panel, origen)
    X = matriz(ent["fecha"], ent["zona_id"], ent["tipo_dia"])
    y = ent["n_siniestros"].to_numpy(dtype=float)
    beta, mu, iteraciones, convergio = irls_poisson(X, y)
    alpha = alpha_momentos(y, mu)
    if not (np.isfinite(alpha) and alpha > 0):
        alpha = None                                        # D50: intervalos Poisson
    return {"configuracion": CONFIGURACION, "modelo": "GLM", "origen": pd.Timestamp(origen).strftime("%Y-%m-%d"),
            "ventana_dias": VENTANA_DIAS, "columnas": COLUMNAS, "dias_entrenamiento": int(ent["fecha"].nunique()),
            "filas_entrenamiento": int(len(ent)), "desde": ent["fecha"].min().strftime("%Y-%m-%d"),
            "hasta": ent["fecha"].max().strftime("%Y-%m-%d"),
            "coeficientes": {c: float(b) for c, b in zip(COLUMNAS, beta)}, "convergio": bool(convergio),
            "iteraciones": int(iteraciones), "avisos": [], "alpha": alpha,
            "origen_alpha": None if alpha is None else "momentos", "alpha_mv": None, "nb2_convergio": None,
            "nb2_iteraciones": None, "nb2_avisos": ["NB2 por máxima verosimilitud no se intentó: el servidor no tiene statsmodels"],
            "implementacion": IMPLEMENTACION, "desvianza_entrenamiento": desvianza(y, mu)}


def predecir_semana(coeficientes: dict, origen, tipo_dia_semana: dict) -> pd.DataFrame:
    "μ de los 7 días desde el origen x 8 municipios (56 filas, ordenadas por fecha y municipio)."
    dias = pd.date_range(pd.Timestamp(origen), periods=HORIZONTE, freq="D")
    hor = pd.MultiIndex.from_product([dias, MUNICIPIOS], names=["fecha", "zona_id"]).to_frame(index=False)
    hor["tipo_dia"] = hor["fecha"].dt.strftime("%Y-%m-%d").map(tipo_dia_semana)
    if hor["tipo_dia"].isna().any():
        raise ValueError("falta el tipo_dia de algún día del horizonte")
    hor["calendario"] = calendario_8(hor["fecha"], hor["tipo_dia"])
    beta = np.array([coeficientes[c] for c in COLUMNAS])
    hor["pred"] = np.exp(matriz(hor["fecha"], hor["zona_id"], hor["tipo_dia"]) @ beta)
    return hor


def tipo_dia_con_holidays(fechas):
    "Misma regla que var.tipo_dia, si el contenedor tiene holidays; si no, None."
    if importlib.util.find_spec("holidays") is None:
        return None
    import holidays
    fechas = pd.DatetimeIndex(fechas)
    fer = holidays.country_holidays("UY", years=range(fechas.min().year, fechas.max().year + 1),
                                    categories=("public", "bank"))
    return {d.strftime("%Y-%m-%d"): ("feriado" if d.date() in fer else "fin_semana" if d.dayofweek >= 5 else "entre_semana")
            for d in fechas}


# ------------------------------------------------------------------------------------------ registro
def version(paquete):
    try:
        return importlib_metadata.version(paquete)
    except importlib_metadata.PackageNotFoundError:
        return "no instalado"


def diferencia_relativa(a, b) -> float:
    a, b = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    return float(np.max(np.abs(a - b) / np.abs(b)))


def comparar_con_local(modelo: dict, semana: pd.DataFrame, ruta_local: Path) -> dict:
    local = json.loads(ruta_local.read_text(encoding="utf-8"))
    mu_local = predecir_semana(local["coeficientes"], local["origen"], TIPO_DIA_SEMANA)["pred"]
    filas = {
        "coeficientes": diferencia_relativa([modelo["coeficientes"][c] for c in COLUMNAS],
                                            [local["coeficientes"][c] for c in COLUMNAS]),
        "mu_56_filas": diferencia_relativa(semana["pred"], mu_local),
        "alpha": (diferencia_relativa([modelo["alpha"]], [local["alpha"]])
                  if modelo["alpha"] is not None and local["alpha"] is not None else None),
    }
    return {"origen_alpha_local": local["origen_alpha"], "diferencia_relativa_maxima": filas,
            "cumple": all(v is not None and v <= TOL_COMPARACION for v in filas.values()), "tolerancia": TOL_COMPARACION}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--panel", default=str(RUTA_PANEL))
    parser.add_argument("--salida", default=None, help="carpeta de salida (por omisión /outputs/runs/<RUN_ID>)")
    args = parser.parse_args(argv)

    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    if args.salida:
        salida = Path(args.salida)
    elif Path("/outputs").is_dir():
        salida = Path("/outputs") / "runs" / run_id
    else:
        raise SystemExit("No existe /outputs: indicar --salida (fuera del repositorio).")
    salida.mkdir(parents=True, exist_ok=True)

    print("=== train_modelo_final.py ===", flush=True)
    print("RUN_ID:", run_id)
    print("Excepción declarada (D51): lee el panel completo, incluido el bloque final; entrena y no evalúa.")
    print("Implementación:", IMPLEMENTACION)
    print("α: por momentos (plan B de D28); NB2 por máxima verosimilitud no se intenta (sin statsmodels).")
    versiones = {"python": platform.python_version(), "numpy": np.__version__, "pandas": pd.__version__,
                 **{p: version(p) for p in ("scikit-learn", "scipy", "statsmodels", "holidays")}}
    print("Versiones del entorno:", json.dumps(versiones, ensure_ascii=False))
    print("Plataforma:", platform.platform())

    print("Raíz:", RAIZ)
    ruta_panel = Path(args.panel)
    if not ruta_panel.exists():
        raise SystemExit(f"No está el panel {ruta_panel}: copiarlo a data/processed/ junto al script (train/README.md).")
    sha = hashlib.sha256(ruta_panel.read_bytes()).hexdigest()
    print(f"\nPanel: {ruta_panel}\n  sha256 {sha}")
    if sha != SHA256_PANEL:
        raise SystemExit(f"El sha256 del panel no es el de models/metadata.json ({SHA256_PANEL}): DETENERSE.")
    panel = leer_panel(ruta_panel)
    assert panel["fecha"].max() == FECHA_CORTE and sorted(panel["zona_id"].unique()) == MUNICIPIOS
    origen = FECHA_CORTE + pd.Timedelta(days=1)

    modelo = entrenar(panel, origen)
    print(f"\nEntrenamiento: {modelo['desde']} a {modelo['hasta']} ({modelo['dias_entrenamiento']} días, "
          f"{modelo['filas_entrenamiento']} filas); origen {modelo['origen']}")
    print(f"IRLS: convergió = {modelo['convergio']}, iteraciones = {modelo['iteraciones']}, "
          f"desvianza = {modelo['desvianza_entrenamiento']!r}")
    print("Coeficientes:")
    for c in COLUMNAS:
        print(f"  {c:<15} {modelo['coeficientes'][c]!r}")
    print(f"α (momentos): {modelo['alpha']!r}")

    con_holidays = tipo_dia_con_holidays(pd.date_range(origen, periods=HORIZONTE, freq="D"))
    if con_holidays is None:
        print("\nCalendario de la semana: holidays no está instalado; se usa la constante TIPO_DIA_SEMANA (D50).")
    else:
        print("\nCalendario de la semana: holidays", version("holidays"), "- coincide con la constante:",
              con_holidays == TIPO_DIA_SEMANA)
        if con_holidays != TIPO_DIA_SEMANA:
            raise SystemExit("holidays da otro calendario que TIPO_DIA_SEMANA: DETENERSE.")

    semana = predecir_semana(modelo["coeficientes"], origen, TIPO_DIA_SEMANA)
    print("μ de la semana del 2026-01-01 (56 filas):")
    for r in semana.itertuples(index=False):
        print(f"  {r.fecha:%Y-%m-%d} {r.zona_id:<13} {r.calendario:<10} {r.pred!r}")

    resumen = {"run_id": run_id, "script": "train/train_modelo_final.py", "versiones": versiones, "sha256_panel": sha,
               "implementacion": IMPLEMENTACION}
    if RUTA_MODELO_LOCAL.exists():
        comp = comparar_con_local(modelo, semana, RUTA_MODELO_LOCAL)
        resumen["comparacion_con_local"] = comp
        print(f"\nComparación con {RUTA_MODELO_LOCAL.relative_to(RAIZ).as_posix()} (origen de α local: "
              f"{comp['origen_alpha_local']}); diferencia relativa máxima:")
        for k, v in comp["diferencia_relativa_maxima"].items():
            print(f"  {k:<13} {v!r}")
        print(f"Criterio (<= {TOL_COMPARACION:g} en todo): {'CUMPLE' if comp['cumple'] else 'NO CUMPLE'}")
    else:
        print(f"\nNo está {RUTA_MODELO_LOCAL}: sin comparación con la exportación local.")

    (salida / "modelo_final.json").write_text(json.dumps(modelo, ensure_ascii=False, indent=2, allow_nan=False),
                                              encoding="utf-8")
    semana.assign(fecha=semana["fecha"].dt.strftime("%Y-%m-%d")).to_csv(
        salida / "prediccion_semana_2026-01-01.csv", index=False, encoding="utf-8", float_format="%.17g")
    (salida / "resumen_corrida.json").write_text(json.dumps(resumen, ensure_ascii=False, indent=2, allow_nan=False),
                                                 encoding="utf-8")
    print("\nSalidas en", salida)
    print("Corrida finalizada.", flush=True)
    if "comparacion_con_local" in resumen and not resumen["comparacion_con_local"]["cumple"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
