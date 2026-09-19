# train_base.py
#
# Versión .py de notebooks/base.ipynb ("Modelo base y protocolo de evaluación — MUNICIPIO C"),
# adaptada para enviarse a la cola del servidor con el sistema descrito en
# documentacion/Guia_entrenamientos_CPU_GPU.md.
#
# Estructura y resultados: los mismos que el notebook, en el mismo orden (secciones 1 a 11).
# Sólo cambia la capa de ejecución/entrada-salida: sin celdas de Jupyter, sin `display`/`plt.show`,
# y los artefactos se guardan en /outputs/runs/<RUN_ID>/ (convención de la guía, sección 9-10) en
# lugar de experiments/base/ directamente.
#
# GPU: este script NO usa GPU. Entrena un único DecisionTreeRegressor (scikit-learn), que no
# tiene implementación GPU -- y con ~1.600 filas tampoco habría nada que acelerar. Se envía como
# trabajo CPU:
#
#   submit_cpu train_base.py
#
# (no submit_gpu: la guía, sección 14 punto 8, pide usar submit_gpu sólo para trabajos que
# realmente aprovechen la GPU).
#
# Tras la corrida, para que los documentos del proyecto (resumen_base.md) sigan citando las
# mismas rutas, copiar el contenido de /train/outputs/runs/<RUN_ID>/{tablas,figuras} dentro de
# experiments/base/{tablas,figuras} del repositorio (mismos nombres de archivo que el notebook).

import os
import platform
import sys
import time
from datetime import datetime
from pathlib import Path

# Los logs del servidor (.out) y algunas consolas locales no son UTF-8 por omisión; sin esto,
# imprimir "→" o "í" puede tirar UnicodeEncodeError y cortar el trabajo a mitad de camino.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import matplotlib
matplotlib.use("Agg")  # sin pantalla en el servidor: sólo se guardan figuras a disco

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sklearn
from sklearn.metrics import mean_absolute_error, mean_poisson_deviance, mean_squared_error
from sklearn.tree import DecisionTreeRegressor

T0 = time.time()

# --------------------------------------------------------------------------------------
# 0. Identificación del trabajo y carpeta de resultados (Guia_entrenamientos_CPU_GPU.md, §9-11)
# --------------------------------------------------------------------------------------
RUN_ID = datetime.now().strftime("%Y%m%d_%H%M%S")

SLURM_JOB_ID = os.environ.get("SLURM_JOB_ID", "no_slurm")
SLURM_JOB_NAME = os.environ.get("SLURM_JOB_NAME", "no_slurm")
SLURM_CPUS_PER_TASK = os.environ.get("SLURM_CPUS_PER_TASK", "no_definido")
CUDA_VISIBLE_DEVICES = os.environ.get("CUDA_VISIBLE_DEVICES", "no_definido")

# En el servidor, /outputs es la carpeta de resultados del grupo (Jupyter la ve como
# /train/outputs) y ya existe antes de que corra cualquier trabajo. Si no existe (por ejemplo,
# al probar el script en una máquina local sin el entorno Slurm) se usa una carpeta local
# equivalente, para no escribir por error fuera del repositorio (en Windows, Path("/outputs")
# resuelve contra la unidad actual -- ojo con comprobar el padre, que siempre existe).
_BASE_OUTPUTS = Path("/outputs")
if platform.system() == "Windows" or not _BASE_OUTPUTS.exists():
    _BASE_OUTPUTS = Path(__file__).resolve().parent / "outputs_local"
    print(f"AVISO: /outputs no está disponible; se usa {_BASE_OUTPUTS} (ejecución local de prueba).",
          flush=True)

OUTPUT_DIR = _BASE_OUTPUTS / "runs" / RUN_ID
DIR_TABLAS = OUTPUT_DIR / "tablas"
DIR_FIGURAS = OUTPUT_DIR / "figuras"
for _d in (DIR_TABLAS, DIR_FIGURAS):
    _d.mkdir(parents=True, exist_ok=True)

LOG_FILE = f"/outputs/logs/{SLURM_JOB_NAME}_{SLURM_JOB_ID}.out"
with open(OUTPUT_DIR / "run_info.txt", "w") as f:
    f.write(f"run_id={RUN_ID}\n")
    f.write(f"slurm_job_id={SLURM_JOB_ID}\n")
    f.write(f"slurm_job_name={SLURM_JOB_NAME}\n")
    f.write(f"slurm_log_file={LOG_FILE}\n")
    f.write(f"slurm_cpus_per_task={SLURM_CPUS_PER_TASK}\n")
    f.write(f"cuda_visible_devices={CUDA_VISIBLE_DEVICES}\n")
    f.write(f"output_dir={OUTPUT_DIR}\n")
    f.write("usa_gpu=no (DecisionTreeRegressor de scikit-learn no tiene implementacion GPU)\n")

print("Entrenamiento iniciado: train_base.py (modelo base, MUNICIPIO C)", flush=True)
print("RUN_ID              :", RUN_ID, flush=True)
print("SLURM_JOB_ID         :", SLURM_JOB_ID, flush=True)
print("SLURM_JOB_NAME       :", SLURM_JOB_NAME, flush=True)
print("SLURM_CPUS_PER_TASK  :", SLURM_CPUS_PER_TASK, flush=True)
print("CUDA_VISIBLE_DEVICES :", CUDA_VISIBLE_DEVICES, "(no se usa GPU en este script)", flush=True)
print("Carpeta de resultados:", OUTPUT_DIR, flush=True)

# Semilla global: hoy no hay nada aleatorio salvo el árbol, pero se fija por si se agrega.
SEMILLA = 20260910
np.random.seed(SEMILLA)

plt.rcParams["figure.dpi"] = 110
plt.rcParams["axes.grid"] = True
plt.rcParams["grid.alpha"] = 0.3

print("Cargando librerías...", flush=True)
print("pandas      ", pd.__version__, flush=True)
print("numpy       ", np.__version__, flush=True)
print("matplotlib  ", matplotlib.__version__, flush=True)
print("scikit-learn", sklearn.__version__, flush=True)
print("python      ", platform.python_version(), flush=True)


def guardar_tabla(df, nombre):
    "Escribe un CSV en <OUTPUT_DIR>/tablas y lo imprime en el log."
    ruta = DIR_TABLAS / nombre
    df.to_csv(ruta, index=False)
    print(f"[tabla]  {ruta.name} ({len(df)} filas)", flush=True)
    print(df.to_string(index=False), flush=True)
    return df


def guardar_figura(fig, nombre):
    "Escribe un PNG en <OUTPUT_DIR>/figuras (sin mostrarlo: no hay pantalla en el servidor)."
    ruta = DIR_FIGURAS / nombre
    fig.savefig(ruta, bbox_inches="tight")
    plt.close(fig)
    print(f"[figura] {ruta.name}", flush=True)


# --------------------------------------------------------------------------------------
# Configuración de rutas de datos (equivalente a la celda de "Configuración de rutas" del notebook)
# --------------------------------------------------------------------------------------
# El dataset (data/processed/panel_zona_top.csv) no se versiona en git (ver .gitignore):
# tiene que existir en el checkout del servidor, generado por notebooks/preparacion_montevideo.ipynb
# o copiado manualmente. Se busca subiendo desde la ubicación del propio script (más robusto que
# usar el directorio de trabajo, que en un trabajo de Slurm puede no ser el del repositorio).
_candidatos = [Path(__file__).resolve().parent, *Path(__file__).resolve().parents, Path.cwd(), *Path.cwd().parents]
RAIZ = next((p for p in _candidatos if (p / "data" / "processed" / "panel_zona_top.csv").exists()), None)
if RAIZ is None:
    raise FileNotFoundError(
        "No se encuentra data/processed/panel_zona_top.csv a partir de la ubicación del script "
        f"({Path(__file__).resolve()}) ni del directorio de trabajo ({Path.cwd()}). "
        "Generarlo con notebooks/preparacion_montevideo.ipynb o copiarlo manualmente."
    )

RUTA_DATOS = RAIZ / "data" / "processed" / "panel_zona_top.csv"
print("Raíz del repositorio:", RAIZ, flush=True)
print("Dataset             :", RUTA_DATOS.relative_to(RAIZ), flush=True)

# --------------------------------------------------------------------------------------
# 1. Carga y estructura de la serie
# --------------------------------------------------------------------------------------
print("\n=== 1. Carga y estructura de la serie ===", flush=True)

serie_df = pd.read_csv(RUTA_DATOS, dtype={"zona_id": "string"})

# Fecha ISO, formato fijo. NO usar dayfirst / detección automática (ver registro_uso_IA.md,
# sesión 2026-09-07: con dayfirst=True, 2021-07-01 se leyó como 7 de enero, en silencio).
serie_df["fecha"] = pd.to_datetime(serie_df["fecha"], format="%Y-%m-%d")
serie_df = serie_df.sort_values("fecha").set_index("fecha")

print(serie_df.head().to_string(), flush=True)
buf_info = []
serie_df.info(buf=type("_W", (), {"write": buf_info.append, "flush": lambda self: None})())
print("".join(buf_info), flush=True)

# --- Verificaciones de integridad ---
verifs = []
verifs.append(("índice temporal ordenado y único",
               serie_df.index.is_monotonic_increasing and serie_df.index.is_unique))

rango_completo = pd.date_range(serie_df.index.min(), serie_df.index.max(), freq="D")
dias_faltantes = rango_completo.difference(serie_df.index)
verifs.append(("serie diaria sin huecos", len(dias_faltantes) == 0))

verifs.append(("sin valores nulos", int(serie_df.isna().sum().sum()) == 0))

obj = serie_df["n_siniestros"]
verifs.append(("objetivo entero no negativo",
               bool((obj >= 0).all()) and obj.dtype.kind in "iu"))

verifs.append(("una sola zona (zona_id constante)", serie_df["zona_id"].nunique() == 1))

tabla_verifs = pd.DataFrame(verifs, columns=["verificación", "ok"])
print(tabla_verifs.to_string(index=False), flush=True)
assert tabla_verifs["ok"].all(), "Alguna verificación de integridad falló."
print("\nZona:", serie_df["zona_id"].iloc[0],
      "| Días:", len(serie_df),
      "|", serie_df.index.min().date(), "→", serie_df.index.max().date(), flush=True)

# --- Resumen del objetivo ---
y_todo = serie_df["n_siniestros"].astype(float)
resumen_serie = pd.DataFrame({
    "indicador": ["municipio", "dias", "fecha_min", "fecha_max", "media", "varianza",
                  "indice_dispersion", "minimo", "maximo", "pct_ceros"],
    "valor": [serie_df["zona_id"].iloc[0], len(y_todo),
              str(serie_df.index.min().date()), str(serie_df.index.max().date()),
              round(y_todo.mean(), 4), round(y_todo.var(ddof=0), 4),
              round(y_todo.var(ddof=0) / y_todo.mean(), 4),
              int(y_todo.min()), int(y_todo.max()),
              round(100 * (y_todo == 0).mean(), 2)],
})
guardar_tabla(resumen_serie, "01_serie_resumen.csv")

# --------------------------------------------------------------------------------------
# 2. Visualización de la serie
# --------------------------------------------------------------------------------------
print("\n=== 2. Visualización de la serie ===", flush=True)

y = serie_df["n_siniestros"].astype(float)
t_idx = np.arange(len(y))
pend, orig = np.polyfit(t_idx, y.values, 1)
tendencia = np.polyval((pend, orig), t_idx)
mm28 = y.rolling(28, min_periods=7).mean()

fig, ax = plt.subplots(figsize=(14, 4.5))
ax.plot(y.index, y.values, lw=0.7, alpha=0.45, label="Siniestros por día")
ax.plot(y.index, mm28.values, lw=2, label="Media móvil de 28 días")
ax.plot(y.index, tendencia, lw=2, ls="--",
        label=f"Tendencia lineal ({pend * 365:+.2f} siniestros/año)")
ax.set_title(f"Serie diaria de siniestros — {serie_df['zona_id'].iloc[0]}")
ax.set_xlabel("Fecha")
ax.set_ylabel("Siniestros por día")
ax.legend()
fig.tight_layout()
guardar_figura(fig, "fig1_serie.png")

print(f"Media 1ª mitad: {y.iloc[:len(y)//2].mean():.3f}", flush=True)
print(f"Media 2ª mitad: {y.iloc[len(y)//2:].mean():.3f}", flush=True)
print(f"Variación entre mitades: {100 * (y.iloc[len(y)//2:].mean() / y.iloc[:len(y)//2].mean() - 1):+.1f} %",
      flush=True)

# --------------------------------------------------------------------------------------
# 3. Estructura de calendario
# --------------------------------------------------------------------------------------
print("\n=== 3. Estructura de calendario ===", flush=True)

ORDEN_TIPODIA = ["entre_semana", "fin_semana", "feriado"]
perfil_cal = (serie_df.groupby("tipo_dia")["n_siniestros"]
              .agg(dias="count", media="mean", desvio="std")
              .reindex(ORDEN_TIPODIA)
              .reset_index())
perfil_cal["media"] = perfil_cal["media"].round(3)
perfil_cal["desvio"] = perfil_cal["desvio"].round(3)
perfil_cal["factor_vs_global"] = (perfil_cal["media"] / y.mean()).round(3)
guardar_tabla(perfil_cal, "02_perfil_calendario.csv")

fig, ax = plt.subplots(figsize=(7, 4))
ax.bar(perfil_cal["tipo_dia"], perfil_cal["media"], color=["#4C72B0", "#DD8452", "#55A868"])
ax.axhline(y.mean(), color="gray", ls="--", label=f"Media global = {y.mean():.2f}")
ax.set_title("Media de siniestros por tipo de día")
ax.set_ylabel("Siniestros por día (media)")
ax.legend()
fig.tight_layout()
guardar_figura(fig, "fig2_perfil_calendario.png")

# Autocorrelación exploratoria sobre toda la serie (referencia gruesa; se recalcula sin el test
# en la sección 5).
ac_expl = pd.DataFrame({
    "rezago": [1, 7, 14],
    "autocorrelacion": [round(serie_df["n_siniestros"].autocorr(k), 4) for k in (1, 7, 14)],
})
print(ac_expl.to_string(index=False), flush=True)

# --------------------------------------------------------------------------------------
# 4. Métricas del protocolo
# --------------------------------------------------------------------------------------
print("\n=== 4. Métricas del protocolo ===", flush=True)

EPS = 1e-6  # la desvianza de Poisson exige predicciones estrictamente positivas


def evaluar(y_true, y_pred):
    "Devuelve el diccionario de métricas del protocolo para un tramo."
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.clip(np.asarray(y_pred, dtype=float), EPS, None)
    return {
        "desvianza_poisson": mean_poisson_deviance(y_true, y_pred),
        "mae": mean_absolute_error(y_true, y_pred),
        "rmse": float(np.sqrt(mean_squared_error(y_true, y_pred))),
        "razon_total": float(y_pred.sum() / y_true.sum()),
        "sesgo_medio": float(np.mean(y_pred - y_true)),
        "n_dias": int(len(y_true)),
    }


_chk = evaluar([1, 2, 3, 4], [1, 2, 3, 4])
print("desvianza de una predicción perfecta:", round(_chk["desvianza_poisson"], 8), flush=True)

# --------------------------------------------------------------------------------------
# 5. Partición temporal: desarrollo y prueba
# --------------------------------------------------------------------------------------
print("\n=== 5. Partición temporal: desarrollo y prueba ===", flush=True)

HORIZONTE = 7   # días que se predicen en cada corte (horizonte operativo semanal)
PASO = 7        # separación entre orígenes: cortes de validación no solapados
FRAC_TEST = 0.20
FRAC_ENTREN_INICIAL = 0.75

n_total = len(serie_df)
n_test = int(round(n_total * FRAC_TEST))
corte_test = n_total - n_test

serie_desarrollo = serie_df.iloc[:corte_test].copy()
serie_test = serie_df.iloc[corte_test:].copy()   # RESERVADO — no se usa hasta la sección 9

INICIAL = int(round(len(serie_desarrollo) * FRAC_ENTREN_INICIAL))
n_validacion = len(serie_desarrollo) - INICIAL
n_folds_estimado = int(np.ceil(n_validacion / PASO))

particiones = pd.DataFrame({
    "bloque": ["entrenamiento inicial", "validación (ventana deslizante)", "prueba (reservado)"],
    "desde": [serie_desarrollo.index[0].date(),
              serie_desarrollo.index[INICIAL].date(),
              serie_test.index[0].date()],
    "hasta": [serie_desarrollo.index[INICIAL - 1].date(),
              serie_desarrollo.index[-1].date(),
              serie_test.index[-1].date()],
    "dias": [INICIAL, n_validacion, len(serie_test)],
    "pct": [round(100 * INICIAL / n_total, 1),
            round(100 * n_validacion / n_total, 1),
            round(100 * len(serie_test) / n_total, 1)],
})
guardar_tabla(particiones, "03_particiones.csv")
print("Horizonte:", HORIZONTE, "días | Paso:", PASO, "días | Folds de validación estimados:",
      n_folds_estimado, flush=True)

# Autocorrelación recalculada SIN el test (compárese con la tabla exploratoria de la sección 3).
ac_dev = pd.DataFrame({
    "rezago": [1, 7, 14],
    "autocorrelacion_desarrollo": [round(serie_desarrollo["n_siniestros"].autocorr(k), 4)
                                   for k in (1, 7, 14)],
})
guardar_tabla(ac_dev, "02b_autocorrelacion.csv")

fig, ax = plt.subplots(figsize=(14, 4))
ax.plot(serie_desarrollo.index, serie_desarrollo["n_siniestros"], lw=0.8,
        color="#4C72B0", label="Desarrollo")
ax.plot(serie_test.index, serie_test["n_siniestros"], lw=0.8,
        color="#C44E52", label="Prueba (reservado)")
ax.axvline(serie_desarrollo.index[INICIAL], color="gray", ls=":",
           label="Fin del entrenamiento inicial")
ax.axvline(serie_test.index[0], color="black", ls="--",
           label="Inicio de la prueba")
ax.set_title("Partición temporal de la serie")
ax.set_xlabel("Fecha")
ax.set_ylabel("Siniestros por día")
ax.legend(loc="upper left")
fig.tight_layout()
guardar_figura(fig, "fig3_particion.png")

# --------------------------------------------------------------------------------------
# 6. Backtesting de ventana deslizante
# --------------------------------------------------------------------------------------
print("\n=== 6. Backtesting de ventana deslizante ===", flush=True)


def backtesting(datos, modelo, inicio, horizonte, paso, ajuste_fijo=None):
    "Backtesting de origen móvil. `modelo(historia, futuro, ajuste) -> array de predicciones`."
    pred = pd.Series(index=datos.index, dtype=float)
    folds = []
    origen = inicio
    while origen < len(datos):
        fin = min(origen + horizonte, len(datos))
        historia = datos.iloc[:origen]
        futuro = datos.iloc[origen:fin]
        ajuste = historia if ajuste_fijo is None else ajuste_fijo
        p = np.asarray(modelo(historia, futuro, ajuste), dtype=float)
        pred.iloc[origen:fin] = p
        folds.append({
            "origen": datos.index[origen].date(),
            "fin": datos.index[fin - 1].date(),
            **evaluar(futuro["n_siniestros"].values, p),
        })
        origen += paso
    return pred, pd.DataFrame(folds)


def resumen_backtest(nombre, datos, pred):
    "Métricas sobre la unión de todos los tramos de validación (predicciones no nulas)."
    mask = pred.notna()
    m = evaluar(datos.loc[mask, "n_siniestros"].values, pred[mask].values)
    return {"modelo": nombre, **m}


# --------------------------------------------------------------------------------------
# 7. Líneas base
# --------------------------------------------------------------------------------------
print("\n=== 7. Líneas base ===", flush=True)


def base_media_constante(historia, futuro, ajuste):
    return np.full(len(futuro), ajuste["n_siniestros"].mean())


def base_naive_estacional(historia, futuro, ajuste):
    h = historia["n_siniestros"].to_numpy(dtype=float)
    n = len(h)
    return np.array([h[n - 7 + i] if n - 7 + i >= 0 else h.mean() for i in range(len(futuro))])


def base_tasa_calendario(historia, futuro, ajuste):
    glob = ajuste["n_siniestros"].mean()
    medias = ajuste.groupby("tipo_dia")["n_siniestros"].mean()
    return futuro["tipo_dia"].map(medias).fillna(glob).to_numpy(dtype=float)


def base_movil_calendario(historia, futuro, ajuste, ventana=56):
    glob = ajuste["n_siniestros"].mean()
    factor = ajuste.groupby("tipo_dia")["n_siniestros"].mean() / glob
    nivel = historia["n_siniestros"].iloc[-ventana:].mean()
    return (nivel * futuro["tipo_dia"].map(factor).fillna(1.0)).to_numpy(dtype=float)


# --- El modelo base: un árbol de decisión básico ---
# No usa GPU: DecisionTreeRegressor (scikit-learn) es CPU-only. Tampoco tiene parámetro n_jobs
# (es un único árbol, no un ensamble) -- SLURM_CPUS_PER_TASK no aplica acá; se deja documentado
# en run_info.txt para cuando el panel completo use un ensamble (RandomForest, Entregable 3).
_COLS_ARBOL = ["y_lag7", "y_lag14", "y_lag21", "t_anios", "es_fin_semana", "es_feriado"]

# Configuración del árbol base: poco profundo, hojas no minúsculas.
ARBOL_KW = dict(max_depth=4, min_samples_leaf=20, random_state=SEMILLA)


def _fila_features(valores, tipos, p, t0):
    return [valores[p - 7], valores[p - 14], valores[p - 21],
            (p - t0) / 365.25,
            1.0 if tipos[p] == "fin_semana" else 0.0,
            1.0 if tipos[p] == "feriado" else 0.0]


def _matriz_entrenamiento(ajuste):
    va = ajuste["n_siniestros"].to_numpy(dtype=float)
    ta = ajuste["tipo_dia"].to_numpy()
    X = [_fila_features(va, ta, p, 0) for p in range(21, len(va))]
    return np.asarray(X), va[21:]


def _matriz_prediccion(historia, futuro):
    vh = historia["n_siniestros"].to_numpy(dtype=float)
    th = historia["tipo_dia"].to_numpy()
    tf = futuro["tipo_dia"].to_numpy()
    n = len(vh)
    # Los rezagos t-7/14/21 caen todos dentro de `historia` para un horizonte de 7 días.
    tt = np.concatenate([th, tf])
    Xf = []
    for i in range(len(futuro)):
        p = n + i
        Xf.append([vh[p - 7], vh[p - 14], vh[p - 21],
                   p / 365.25,
                   1.0 if tt[p] == "fin_semana" else 0.0,
                   1.0 if tt[p] == "feriado" else 0.0])
    return np.asarray(Xf)


def hacer_modelo_arbol(**kw):
    "Devuelve un `ajustar_predecir` que entrena un DecisionTreeRegressor con la config dada."
    params = {**ARBOL_KW, **kw}

    def ajustar_predecir(historia, futuro, ajuste):
        X, obj = _matriz_entrenamiento(ajuste)
        modelo = DecisionTreeRegressor(**params).fit(X, obj)
        return np.clip(modelo.predict(_matriz_prediccion(historia, futuro)), 0.0, None)

    return ajustar_predecir


modelo_arbol = hacer_modelo_arbol()

# --- Por qué se limita la profundidad: corrida de comparación ---
print("Comparando árbol sin podar vs árbol base (max_depth=4)...", flush=True)
_variantes_arbol = [
    ("Arbol sin podar (por omision)", dict(max_depth=None, min_samples_leaf=1)),
    ("Arbol base (max_depth=4)", {}),
]
_Xd, _yd = _matriz_entrenamiento(serie_desarrollo)
_filas_prof = []
for _nom, _kw in _variantes_arbol:
    _p, _ = backtesting(serie_desarrollo, hacer_modelo_arbol(**_kw), INICIAL, HORIZONTE, PASO)
    _arb = DecisionTreeRegressor(**{**ARBOL_KW, **_kw}).fit(_Xd, _yd)  # ajustado sobre todo el desarrollo
    _filas_prof.append({**resumen_backtest(_nom, serie_desarrollo, _p),
                        "profundidad": _arb.get_depth(), "hojas": _arb.get_n_leaves()})
tabla_prof = pd.DataFrame(_filas_prof)
for c in ["desvianza_poisson", "mae", "rmse", "razon_total", "sesgo_medio"]:
    tabla_prof[c] = tabla_prof[c].round(4)
guardar_tabla(tabla_prof, "04c_arbol_profundidad.csv")

# --- Ejecución del backtesting en desarrollo ---
print("Ejecutando backtesting de los 5 modelos en desarrollo (47 cortes aprox.)...", flush=True)
MODELOS = {
    "Media constante": base_media_constante,
    "Naive estacional (t-7)": base_naive_estacional,
    "Tasa x calendario": base_tasa_calendario,
    "Media movil 56d x calendario": base_movil_calendario,
    "Arbol de decision": modelo_arbol,
}

pred_dev = {}
folds_dev = {}
filas_resumen = []
for nombre, fn in MODELOS.items():
    p, f = backtesting(serie_desarrollo, fn, INICIAL, HORIZONTE, PASO)
    pred_dev[nombre] = p
    folds_dev[nombre] = f
    filas_resumen.append({**resumen_backtest(nombre, serie_desarrollo, p),
                          "n_folds": len(f)})
    print(f"  {nombre}: listo ({len(f)} folds)", flush=True)

tabla_dev = pd.DataFrame(filas_resumen).sort_values("desvianza_poisson").reset_index(drop=True)
for c in ["desvianza_poisson", "mae", "rmse", "razon_total", "sesgo_medio"]:
    tabla_dev[c] = tabla_dev[c].round(4)
guardar_tabla(tabla_dev, "04_desarrollo_backtesting.csv")
guardar_tabla(folds_dev["Tasa x calendario"].round(4), "04b_folds_linea_base.csv")

# Predicciones de los últimos ~140 días de desarrollo, para ver el comportamiento.
ventana_fig = serie_desarrollo.index[-140:]
fig, ax = plt.subplots(figsize=(14, 5))
ax.plot(ventana_fig, serie_desarrollo.loc[ventana_fig, "n_siniestros"],
        color="black", lw=1.4, marker="o", ms=3, label="Observado")
for nombre in ["Tasa x calendario", "Media movil 56d x calendario", "Arbol de decision"]:
    ax.plot(ventana_fig, pred_dev[nombre].loc[ventana_fig], lw=1.6, ls="--", label=nombre)
ax.set_title("Validación interna — predicciones sobre el tramo final de desarrollo")
ax.set_xlabel("Fecha")
ax.set_ylabel("Siniestros por día")
ax.legend()
fig.tight_layout()
guardar_figura(fig, "fig4_desarrollo_predicciones.png")

# --------------------------------------------------------------------------------------
# 8. Selección para la evaluación final
# --------------------------------------------------------------------------------------
print("\n=== 8. Selección para la evaluación final ===", flush=True)

FINALISTAS = ["Media constante", "Tasa x calendario", "Arbol de decision"]

# Árbol base reajustado sobre todo el desarrollo, para inspeccionar su estructura.
_Xd, _yd = _matriz_entrenamiento(serie_desarrollo)
_arbol_dev = DecisionTreeRegressor(**ARBOL_KW).fit(_Xd, _yd)
importancias_arbol = (pd.DataFrame({"variable": _COLS_ARBOL,
                                    "importancia": np.round(_arbol_dev.feature_importances_, 4)})
                      .sort_values("importancia", ascending=False).reset_index(drop=True))
guardar_tabla(importancias_arbol, "05_importancias_arbol.csv")
print("profundidad:", _arbol_dev.get_depth(), "| hojas:", _arbol_dev.get_n_leaves(), flush=True)

fig, ax = plt.subplots(figsize=(8, 3.5))
ax.barh(importancias_arbol["variable"], importancias_arbol["importancia"], color="#4C72B0")
ax.invert_yaxis()
ax.set_title("Importancia de variables — árbol base (desarrollo)")
ax.set_xlabel("Importancia (reducción de impureza)")
fig.tight_layout()
guardar_figura(fig, "fig4b_importancias_arbol.png")

# --------------------------------------------------------------------------------------
# 9. Evaluación final sobre el conjunto de prueba
# --------------------------------------------------------------------------------------
print("\n=== 9. Evaluación final sobre el conjunto de prueba ===", flush=True)

serie_total = pd.concat([serie_desarrollo, serie_test])
inicio_test = len(serie_desarrollo)

pred_test = {}
filas_test = []
for nombre in FINALISTAS:
    p, f = backtesting(serie_total, MODELOS[nombre], inicio_test, HORIZONTE, PASO,
                       ajuste_fijo=serie_desarrollo)
    pred_test[nombre] = p.iloc[inicio_test:]
    filas_test.append({**resumen_backtest(nombre, serie_total, p), "n_folds": len(f)})
    print(f"  {nombre}: evaluado en prueba ({len(f)} folds)", flush=True)

tabla_test = pd.DataFrame(filas_test)
for c in ["desvianza_poisson", "mae", "rmse", "razon_total", "sesgo_medio"]:
    tabla_test[c] = tabla_test[c].round(4)
guardar_tabla(tabla_test, "06_evaluacion_test.csv")

# Comparación desarrollo vs test para los finalistas.
comp = (tabla_dev[tabla_dev["modelo"].isin(FINALISTAS)][["modelo", "desvianza_poisson", "mae", "razon_total"]]
        .rename(columns={"desvianza_poisson": "desv_poisson_dev", "mae": "mae_dev", "razon_total": "razon_dev"}))
comp = comp.merge(
    tabla_test[["modelo", "desvianza_poisson", "mae", "razon_total"]].rename(
        columns={"desvianza_poisson": "desv_poisson_test", "mae": "mae_test", "razon_total": "razon_test"}),
    on="modelo")
guardar_tabla(comp.round(4), "06b_desarrollo_vs_test.csv")

# Figura: observado vs finalistas en el test, con 30 días de contexto.
ctx = serie_desarrollo.index[-30:]
fig, ax = plt.subplots(figsize=(14, 5))
ax.plot(ctx, serie_desarrollo.loc[ctx, "n_siniestros"], color="gray", lw=1, label="Desarrollo (contexto)")
ax.plot(serie_test.index, serie_test["n_siniestros"], color="black", lw=1.2, label="Prueba — observado")
for nombre in ["Tasa x calendario", "Arbol de decision"]:
    ax.plot(serie_test.index, pred_test[nombre], lw=1.4, ls="--", label=nombre)
ax.axvline(serie_test.index[0], color="black", ls=":")
ax.set_title("Evaluación final sobre el conjunto de prueba")
ax.set_xlabel("Fecha")
ax.set_ylabel("Siniestros por día")
ax.legend()
fig.tight_layout()
guardar_figura(fig, "fig5_test_predicciones.png")

# Calibración en el test: total mensual observado vs predicho (modelo base aprendido).
mens = pd.DataFrame({"observado": serie_test["n_siniestros"]})
mens["predicho"] = pred_test["Arbol de decision"]
mens_m = mens.resample("MS").sum()
calib_mens = mens_m.assign(razon=(mens_m["predicho"] / mens_m["observado"]).round(3)).reset_index()
calib_mens["fecha"] = calib_mens["fecha"].dt.strftime("%Y-%m")
guardar_tabla(calib_mens, "07_calibracion_mensual_test.csv")

fig, axes = plt.subplots(1, 2, figsize=(14, 4.5))
axes[0].plot(mens_m.index, mens_m["observado"], marker="o", label="Observado")
axes[0].plot(mens_m.index, mens_m["predicho"], marker="o", ls="--", label="Predicho (árbol)")
axes[0].set_title("Total mensual en el test")
axes[0].set_ylabel("Siniestros por mes")
axes[0].legend()

for nombre in ["Tasa x calendario", "Arbol de decision"]:
    axes[1].scatter(serie_test["n_siniestros"], pred_test[nombre], s=12, alpha=0.5, label=nombre)
lim = [0, serie_test["n_siniestros"].max() + 1]
axes[1].plot(lim, lim, color="black", lw=1)
axes[1].set_xlabel("Observado")
axes[1].set_ylabel("Predicho")
axes[1].set_title("Predicho vs observado (test, por día)")
axes[1].legend()
fig.tight_layout()
guardar_figura(fig, "fig6_calibracion_test.png")

# --------------------------------------------------------------------------------------
# 11. Índice de artefactos (la sección 10 del notebook es sólo interpretación en texto)
# --------------------------------------------------------------------------------------
print("\n=== 11. Índice de artefactos ===", flush=True)

indice = pd.DataFrame([
    ("tablas/01_serie_resumen.csv", "Estadísticos de la serie de MUNICIPIO C (§1)"),
    ("tablas/02_perfil_calendario.csv", "Media por tipo de día y factor vs global (§3)"),
    ("tablas/02b_autocorrelacion.csv", "Autocorrelación a rezagos 1/7/14 sin el test (§5)"),
    ("tablas/03_particiones.csv", "Bloques de entrenamiento, validación y prueba (§5)"),
    ("tablas/04_desarrollo_backtesting.csv", "Métricas de los 5 modelos en validación interna (§7)"),
    ("tablas/04b_folds_linea_base.csv", "Métricas por corte de la línea base (§7)"),
    ("tablas/04c_arbol_profundidad.csv", "Árbol sin podar vs árbol base: desvianza, profundidad, hojas (§7)"),
    ("tablas/05_importancias_arbol.csv", "Importancia de variables del árbol base (§8)"),
    ("tablas/06_evaluacion_test.csv", "Métricas de los finalistas en el test (§9)"),
    ("tablas/06b_desarrollo_vs_test.csv", "Comparación desarrollo vs test (§9)"),
    ("tablas/07_calibracion_mensual_test.csv", "Total mensual observado vs predicho en test (§9)"),
    ("figuras/fig1_serie.png", "Serie diaria, media móvil y tendencia (§2)"),
    ("figuras/fig2_perfil_calendario.png", "Media por tipo de día (§3)"),
    ("figuras/fig3_particion.png", "Partición temporal (§5)"),
    ("figuras/fig4_desarrollo_predicciones.png", "Predicciones en el tramo final de desarrollo (§7)"),
    ("figuras/fig4b_importancias_arbol.png", "Importancia de variables del árbol base (§8)"),
    ("figuras/fig5_test_predicciones.png", "Observado vs finalistas en el test (§9)"),
    ("figuras/fig6_calibracion_test.png", "Calibración en el test (§9)"),
], columns=["artefacto", "qué respalda"])
guardar_tabla(indice, "08_artefactos.csv")

elapsed = time.time() - T0
print(f"\nEntrenamiento finalizado en {elapsed:.1f} s.", flush=True)
print("Resultados guardados en:", OUTPUT_DIR, flush=True)
print("Para citarlos desde el informe con las mismas rutas que el notebook, copiar", flush=True)
print(f"  {OUTPUT_DIR}/tablas/*  ->  experiments/base/tablas/", flush=True)
print(f"  {OUTPUT_DIR}/figuras/* ->  experiments/base/figuras/", flush=True)
