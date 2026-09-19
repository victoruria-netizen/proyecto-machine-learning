# train_base_2.py
#
# Versión .py de notebooks/base_2.ipynb ("Modelo base — versión simplificada"), adaptada para
# enviarse a la cola del servidor con el sistema descrito en
# documentacion/Guia_entrenamientos_CPU_GPU.md.
#
# Estructura y resultados: los mismos que el notebook, en el mismo orden (secciones 0 a 7; la
# sección 8 del notebook es sólo interpretación en texto, sin código que portar).
# Sólo cambia la capa de ejecución/entrada-salida: sin celdas de Jupyter, sin `%pip install`,
# `display()` ni salida automática de celda, y los artefactos se guardan en
# /outputs/runs/<RUN_ID>/ (convención de la guía, sección 9-10) en lugar de experiments/base_2/
# directamente.
#
# GPU: este script NO usa GPU. Entrena un único DecisionTreeRegressor (scikit-learn), que no
# tiene implementación GPU -- y con ~1.300 filas de entrenamiento tampoco habría nada que
# acelerar. Se envía como trabajo CPU:
#
#   submit_cpu train_base_2.py
#
# (no submit_gpu: la guía, sección 14 punto 8, pide usar submit_gpu sólo para trabajos que
# realmente aprovechen la GPU).
#
# Sin skforecast (diferencia deliberada con el notebook): base_2.ipynb arma los rezagos y la
# predicción recursiva con skforecast.ForecasterRecursive. Acá se hacen a mano con numpy/pandas
# (funciones `matriz_rezagos` y `predecir_recursivo`, sección 4) porque submit_cpu ejecuta el
# script dentro de un contenedor Apptainer fijo (tensorflow_ngc_24.04_tf2_py3_mlcv.sif, Python
# 3.10; confirmado con train/diagnostico_entorno.py el 2026-09-18) donde:
#   - skforecast no está instalado, y lo instalado desde la terminal de Jupyter no se ve ahí;
#   - /work (donde vive train/) es de sólo lectura, y sólo /outputs es escribible;
#   - las versiones del contenedor (numpy 1.24, pandas 1.5, scikit-learn 1.2) están por debajo de
#     lo que exige skforecast 0.25.0 (numpy>=1.26, pandas>=2.1, scikit-learn>=1.4), así que ni
#     vendorizándolo alcanzaba sin reinstalar todo el stack científico (~500 MB).
# Así el script depende sólo de lo que el contenedor ya trae, igual que train_base.py, y se
# evita también el conflicto skforecast/pandas 3 anotado en HANDOFF.md. Que el resultado sea el
# mismo que el de skforecast se comprobó localmente (mismas predicciones, mismas tablas): ver
# registro_uso_IA.md, sesión 2026-09-18 (segunda).
#
# Tras la corrida, para que los documentos del proyecto (resumen_base_2.md) sigan citando las
# mismas rutas, copiar el contenido de /train/outputs/runs/<RUN_ID>/{tablas,figuras} dentro de
# experiments/base_2/{tablas,figuras} del repositorio (mismos nombres de archivo que el notebook).

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
# 0. Entorno: identificación del trabajo y carpeta de resultados
#    (Guia_entrenamientos_CPU_GPU.md, §9-11; equivalente a la sección 0 del notebook)
# --------------------------------------------------------------------------------------
RUN_ID = datetime.now().strftime("%Y%m%d_%H%M%S")

SLURM_JOB_ID = os.environ.get("SLURM_JOB_ID", "no_slurm")
SLURM_JOB_NAME = os.environ.get("SLURM_JOB_NAME", "no_slurm")
SLURM_CPUS_PER_TASK = os.environ.get("SLURM_CPUS_PER_TASK", "no_definido")
CUDA_VISIBLE_DEVICES = os.environ.get("CUDA_VISIBLE_DEVICES", "no_definido")

# En el servidor, /outputs es la carpeta de resultados del grupo (Jupyter la ve como
# /train/outputs) y ya existe antes de que corra cualquier trabajo; es el ÚNICO mount escribible
# dentro del contenedor (/work, donde vive este script, es de sólo lectura). Si no existe (por
# ejemplo, al probar el script en una máquina local sin el entorno Slurm) se usa una carpeta local
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

print("Entrenamiento iniciado: train_base_2.py (modelo base simplificado, MUNICIPIO C)", flush=True)
print("RUN_ID              :", RUN_ID, flush=True)
print("SLURM_JOB_ID         :", SLURM_JOB_ID, flush=True)
print("SLURM_JOB_NAME       :", SLURM_JOB_NAME, flush=True)
print("SLURM_CPUS_PER_TASK  :", SLURM_CPUS_PER_TASK, flush=True)
print("CUDA_VISIBLE_DEVICES :", CUDA_VISIBLE_DEVICES, "(no se usa GPU en este script)", flush=True)
print("Carpeta de resultados:", OUTPUT_DIR, flush=True)

# Semilla global: el árbol de decisión la usa como random_state.
SEMILLA = 42
np.random.seed(SEMILLA)

plt.rcParams["figure.dpi"] = 110
plt.rcParams["axes.grid"] = True
plt.rcParams["grid.alpha"] = 0.3

versiones = {
    "python": platform.python_version(),
    "pandas": pd.__version__,
    "numpy": np.__version__,
    "matplotlib": matplotlib.__version__,
    "scikit-learn": sklearn.__version__,
}
for nombre, version in versiones.items():
    print(f"{nombre:13s}", version, flush=True)


def guardar_tabla(tabla, nombre):
    """Guarda una tabla en <OUTPUT_DIR>/tablas y la imprime en el log."""
    ruta = DIR_TABLAS / nombre
    tabla.to_csv(ruta, index=False, encoding="utf-8")
    print(f"[tabla]  {ruta.name} ({len(tabla)} filas)", flush=True)
    print(tabla.to_string(index=False), flush=True)
    return tabla


def guardar_figura(fig, nombre):
    """Guarda una figura en <OUTPUT_DIR>/figuras (sin mostrarla: no hay pantalla en el servidor)."""
    ruta = DIR_FIGURAS / nombre
    fig.savefig(ruta, bbox_inches="tight")
    plt.close(fig)
    print(f"[figura] {ruta.name}", flush=True)


entorno = pd.DataFrame({"componente": list(versiones), "version": list(versiones.values())})
entorno.loc[len(entorno)] = ["fecha_ejecucion", datetime.now().strftime("%Y-%m-%d %H:%M")]
guardar_tabla(entorno, "00_entorno.csv")

# --------------------------------------------------------------------------------------
# Configuración de rutas de datos
# --------------------------------------------------------------------------------------
# El dataset (data/processed/panel_zona_top.csv) no se versiona en git (ver .gitignore): tiene
# que existir en el checkout del servidor, generado por notebooks/preparacion_montevideo.ipynb o
# copiado manualmente. Se busca subiendo desde la ubicación del propio script (más robusto que
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
# 1. Carga de datos
# --------------------------------------------------------------------------------------
print("\n=== 1. Carga de datos ===", flush=True)

# Solo leemos la fecha, el municipio y la variable a predecir: nada de calendario ni clima.
# La fecha es el índice. Se lee con formato explícito: si pandas lo adivina, una fecha escrita
# como 01/07/2021 puede leerse como 7 de enero sin avisar.
df = pd.read_csv(RUTA_DATOS, index_col="fecha", usecols=["fecha", "zona_id", "n_siniestros"])
df.index = pd.to_datetime(df.index, format="%Y-%m-%d")

MUNICIPIO = df["zona_id"].iloc[0]
print("Municipio:", MUNICIPIO, flush=True)
print(df.head().to_string(), flush=True)

buf_info = []
df.info(buf=type("_W", (), {"write": buf_info.append, "flush": lambda self: None})())
print("".join(buf_info), flush=True)

print("Rango de la serie:", df.index.min(), "->", df.index.max(), flush=True)
print(df.index.to_series().diff().value_counts().head().to_string(), flush=True)

# --------------------------------------------------------------------------------------
# 2. Lo que se toma del diagnóstico (sin código propio: ver notebooks/diagnostico_datos_municipio.ipynb
#    y la tabla en la sección 2 del notebook base_2.ipynb para el detalle de cada cifra usada)
# --------------------------------------------------------------------------------------
print("\n=== 2. Lo que se toma del diagnóstico (ver diagnostico_datos_municipio.ipynb) ===", flush=True)

# --------------------------------------------------------------------------------------
# 3. Entrenamiento y prueba
# --------------------------------------------------------------------------------------
print("\n=== 3. Entrenamiento y prueba ===", flush=True)

# Definimos el tamaño del conjunto de prueba: el 20% final de la serie.
n_test = int(len(df) * 0.2)

# Partición temporal: el pasado entrena, el futuro evalúa.
train = df.iloc[:-n_test].copy()
test = df.iloc[-n_test:].copy()

particion = pd.DataFrame({
    "conjunto": ["entrenamiento", "prueba"],
    "desde": [train.index.min().date(), test.index.min().date()],
    "hasta": [train.index.max().date(), test.index.max().date()],
    "dias": [len(train), len(test)],
    "porcentaje": [round(100 * len(train) / len(df), 1), round(100 * len(test) / len(df), 1)],
    # Descriptivo: no se usa para ajustar nada.
    "promedio_siniestros_por_dia": [round(train["n_siniestros"].mean(), 3), round(test["n_siniestros"].mean(), 3)],
})
guardar_tabla(particion, "01_particion.csv")

fig, ax = plt.subplots(figsize=(14, 5))
ax.plot(train.index, train["n_siniestros"], color="tab:blue", label="Entrenamiento")
ax.plot(test.index, test["n_siniestros"], color="tab:orange", label="Prueba")
ax.axvline(test.index.min(), color="black", linestyle="--", linewidth=1,
           label="Inicio del conjunto de prueba")
ax.set_title("Partición temporal de los siniestros")
ax.set_xlabel("Fecha")
ax.set_ylabel("Cantidad de siniestros")
ax.legend()
guardar_figura(fig, "fig1_particion.png")

# --------------------------------------------------------------------------------------
# 4. Modelo: árbol de decisión sobre rezagos de la propia serie
#    (el notebook usa skforecast.ForecasterRecursive; acá se arma a mano -- ver el encabezado)
# --------------------------------------------------------------------------------------
print("\n=== 4. Modelo: árbol de decisión sobre rezagos ===", flush=True)

LAGS = [1, 7, 14, 21]            # Siniestros de 1, 7, 14 y 21 días antes
VENTANA = max(LAGS)              # días de historia que necesita cada predicción (21)
NOMBRES_LAGS = [f"lag_{k}" for k in LAGS]


def matriz_rezagos(valores):
    """Tabla de entrenamiento: una fila por día (desde el día 22), con los rezagos como columnas.

    Mismo orden de columnas que skforecast (lag_1, lag_7, lag_14, lag_21). Los primeros 21 días no
    tienen el rezago de 21 días, así que no entran a la tabla.
    """
    valores = np.asarray(valores, dtype=float)
    X = np.column_stack([valores[VENTANA - k:len(valores) - k] for k in LAGS])
    return X, valores[VENTANA:]


def predecir_recursivo(modelo, ultimos_dias, steps):
    """Predice `steps` días seguidos a partir de los últimos VENTANA días observados.

    Recursivo: la predicción de un día se usa como si fuera un dato observado para el rezago de
    1 día del siguiente. Con estos rezagos eso solo afecta al lag_1: en una semana, los rezagos de
    7, 14 y 21 días siempre caen en días ya observados.
    """
    historial = list(np.asarray(ultimos_dias, dtype=float))
    assert len(historial) == VENTANA, "hacen falta exactamente 21 días de historia"
    predicciones = []
    for _ in range(steps):
        fila = np.array([[historial[-k] for k in LAGS]])
        p = float(modelo.predict(fila)[0])
        predicciones.append(p)
        historial.append(p)
    return np.array(predicciones)


# El índice tiene que tener una frecuencia explícita para poder afirmar que no faltan días.
frecuencia = pd.infer_freq(train.index)
if frecuencia is None:
    raise ValueError("No se pudo inferir la frecuencia temporal del índice de train.")

y_train = train["n_siniestros"].asfreq(frecuencia)
y_test = test["n_siniestros"].asfreq(frecuencia)

# Verificamos que fijar la frecuencia no haya creado días faltantes.
if y_train.isna().any() or y_test.isna().any():
    raise ValueError("El índice contiene fechas faltantes después de establecer la frecuencia.")

print("Entrenando DecisionTreeRegressor (max_depth=15, lags=[1,7,14,21])...", flush=True)
# Solo la serie objetivo: sin variables exógenas.
X_train, obj_train = matriz_rezagos(y_train.to_numpy())
arbol = DecisionTreeRegressor(max_depth=15, random_state=SEMILLA).fit(X_train, obj_train)
print("Entrenamiento del árbol finalizado.", flush=True)

# ¿Con qué variables se entrenó? Deben ser solo rezagos de la serie.
print("Variables del árbol:", NOMBRES_LAGS, flush=True)
print("¿Usa variables exógenas?:", False, flush=True)

# ¿Aprende patrones o memoriza días? Comparamos la cantidad de hojas con las filas de entrenamiento.
filas_ajuste = len(X_train)
assert filas_ajuste == len(y_train) - VENTANA

tamano_arbol = pd.DataFrame({
    "indicador": ["filas de entrenamiento", "profundidad", "hojas", "filas por hoja (promedio)"],
    "valor": pd.Series([filas_ajuste, arbol.get_depth(), arbol.get_n_leaves(),
                        round(filas_ajuste / arbol.get_n_leaves(), 2)], dtype="object"),
})
guardar_tabla(tamano_arbol, "02_tamano_arbol.csv")

# --------------------------------------------------------------------------------------
# 5. Línea base
# --------------------------------------------------------------------------------------
print("\n=== 5. Línea base ===", flush=True)

ARBOL = "Árbol de decisión"
LINEA_BASE = "Promedio de las últimas 4 semanas (línea base)"
MODELOS = [ARBOL, "Media constante", LINEA_BASE, "Repetir semana anterior"]

# La media constante se calcula solo con entrenamiento.
media_train = y_train.mean()
print("Media de entrenamiento:", round(media_train, 3), flush=True)

# Serie completa con frecuencia diaria: las referencias y el árbol necesitan los días ya
# observados antes de cada fecha a predecir.
serie_completa = df["n_siniestros"].asfreq(frecuencia)

# Promedio de lo observado 7, 14, 21 y 28 días antes de cada fecha.
# Al predecir una semana, esos cuatro días siempre son anteriores a la semana: ya están observados.
promedio_4_semanas = (serie_completa.shift(7) + serie_completa.shift(14)
                      + serie_completa.shift(21) + serie_completa.shift(28)) / 4


def predecir_referencias(fechas):
    """Predicciones de las tres referencias simples para las fechas indicadas."""
    return {
        "Media constante": pd.Series(media_train, index=fechas),
        LINEA_BASE: promedio_4_semanas.loc[fechas],
        "Repetir semana anterior": serie_completa.shift(7).loc[fechas],
    }


# --------------------------------------------------------------------------------------
# 6. Primera mirada: la primera semana de prueba
# --------------------------------------------------------------------------------------
print("\n=== 6. Primera mirada: la primera semana de prueba ===", flush=True)

# La desvianza de Poisson exige predicciones mayores que 0.
# Solo para esa métrica, los ceros se reemplazan por un valor mínimo (igual que en train_base.py).
EPS = 1e-6


def calcular_metricas(real, prediccion):
    """Desvianza de Poisson (principal), MAE, RMSE y total predicho sobre total observado."""
    return {
        "desvianza_poisson": mean_poisson_deviance(real, prediccion.clip(lower=EPS)),
        "MAE": mean_absolute_error(real, prediccion),
        "RMSE": np.sqrt(mean_squared_error(real, prediccion)),
        "total_predicho_sobre_observado": prediccion.sum() / real.sum(),
    }


# Horizonte de predicción: los primeros 7 días del conjunto de prueba.
steps = 7
fechas_semana = y_test.index[:steps]

# El árbol predice de forma recursiva a partir de los últimos días de entrenamiento.
pred_arbol = pd.Series(predecir_recursivo(arbol, y_train.iloc[-VENTANA:], steps), index=fechas_semana)
assert y_train.index[-1] + pd.Timedelta(days=1) == fechas_semana[0], "la semana no sigue al entrenamiento"

predicciones_semana = pd.DataFrame({
    "valor_real": y_test.loc[fechas_semana],
    ARBOL: pred_arbol,
})
for nombre, prediccion in predecir_referencias(fechas_semana).items():
    predicciones_semana[nombre] = prediccion

guardar_tabla(predicciones_semana.round(3).rename_axis("fecha").reset_index(),
              "03_primera_semana_predicciones.csv")

# Contexto: los últimos 30 días de entrenamiento antes de la semana predicha.
dias_contexto = 30
contexto = y_train.iloc[-dias_contexto:]

fig, ax = plt.subplots(figsize=(14, 5))
ax.plot(contexto.index, contexto, marker="o", color="tab:blue", label="Entrenamiento: últimos 30 días")
ax.plot(fechas_semana, predicciones_semana["valor_real"], marker="o", color="tab:orange",
        label="Prueba: valor real")
ax.plot(fechas_semana, predicciones_semana[ARBOL], marker="o", linestyle="--", color="tab:green",
        label=ARBOL)
ax.plot(fechas_semana, predicciones_semana[LINEA_BASE], marker="s", linestyle="--", color="tab:red",
        label=LINEA_BASE)
ax.set_title("Predicción de la primera semana de prueba, con contexto previo")
ax.set_xlabel("Fecha")
ax.set_ylabel("Cantidad de siniestros por día")
ax.legend()
plt.tight_layout()
guardar_figura(fig, "fig2_primera_semana.png")

metricas_semana = pd.DataFrame([
    {"modelo": m, **calcular_metricas(predicciones_semana["valor_real"], predicciones_semana[m])}
    for m in MODELOS
]).sort_values("desvianza_poisson").round(3)
guardar_tabla(metricas_semana, "04_primera_semana_metricas.csv")

# --------------------------------------------------------------------------------------
# 7. Evaluación en todo el conjunto de prueba
# --------------------------------------------------------------------------------------
print("\n=== 7. Evaluación en todo el conjunto de prueba ===", flush=True)

bloques = []
for inicio in range(0, len(y_test), steps):
    fechas = y_test.index[inicio:inicio + steps]

    # Últimos 21 días observados antes de la semana (de entrenamiento o de semanas de prueba ya pasadas).
    posicion = serie_completa.index.get_loc(fechas[0])
    ultimos_dias = serie_completa.iloc[posicion - VENTANA:posicion]
    pred = pd.Series(predecir_recursivo(arbol, ultimos_dias, len(fechas)), index=fechas)

    bloque = pd.DataFrame({"semana": inicio // steps + 1, "valor_real": y_test.loc[fechas], ARBOL: pred})
    for nombre, prediccion in predecir_referencias(fechas).items():
        bloque[nombre] = prediccion
    bloques.append(bloque)

predicciones_test = pd.concat(bloques)
assert len(predicciones_test) == len(y_test) and predicciones_test.notna().all().all()
print("Semanas evaluadas:", predicciones_test["semana"].nunique(), "| días:", len(predicciones_test),
      flush=True)

metricas_test = pd.DataFrame([
    {"modelo": m, **calcular_metricas(predicciones_test["valor_real"], predicciones_test[m])}
    for m in MODELOS
]).sort_values("desvianza_poisson")

# Diferencia contra la línea base, en porcentaje (positivo = peor que la línea base).
desvianza_linea_base = metricas_test.loc[metricas_test["modelo"] == LINEA_BASE, "desvianza_poisson"].iloc[0]
mae_linea_base = metricas_test.loc[metricas_test["modelo"] == LINEA_BASE, "MAE"].iloc[0]
metricas_test["desvianza_vs_linea_base_pct"] = 100 * (metricas_test["desvianza_poisson"] / desvianza_linea_base - 1)
metricas_test["MAE_vs_linea_base_pct"] = 100 * (metricas_test["MAE"] / mae_linea_base - 1)
metricas_test = metricas_test.round({"desvianza_poisson": 3, "MAE": 3, "RMSE": 3,
                                     "total_predicho_sobre_observado": 3,
                                     "desvianza_vs_linea_base_pct": 1, "MAE_vs_linea_base_pct": 1})

# Días en que cada modelo predijo exactamente 0: ahí la desvianza de Poisson castiga mucho.
metricas_test["dias_con_prediccion_cero"] = [int((predicciones_test[m] == 0).sum()) for m in metricas_test["modelo"]]
guardar_tabla(metricas_test, "05_test_metricas.csv")

# Días en que el árbol predijo 0. Si ese día hubo siniestros, la desvianza de Poisson es muy grande.
dias_pred_cero = predicciones_test.loc[predicciones_test[ARBOL] == 0, ["semana", "valor_real", ARBOL]]
print("Días con predicción 0 del árbol:", flush=True)
print(dias_pred_cero.to_string(), flush=True)

# Control cruzado: la media constante debe dar lo mismo que en train_base.py / base.ipynb,
# que usa la misma partición, la misma evaluación semana a semana y el mismo cálculo de métricas.
ruta_base = RAIZ / "experiments" / "base" / "tablas" / "06_evaluacion_test.csv"
if ruta_base.exists():
    base = pd.read_csv(ruta_base).set_index("modelo")
    media_propia = metricas_test.set_index("modelo").loc["Media constante"]
    media_base = base.loc["Media constante"]
    for metrica, metrica_base in [("desvianza_poisson", "desvianza_poisson"), ("MAE", "mae")]:
        estado = "OK" if abs(media_propia[metrica] - media_base[metrica_base]) < 0.001 else "DIFIERE"
        print(f"{estado}: Media constante {metrica} {media_propia[metrica]:.4f} | "
              f"base.ipynb/train_base.py {media_base[metrica_base]:.4f}", flush=True)
else:
    print("No está experiments/base/tablas/06_evaluacion_test.csv: control cruzado omitido.", flush=True)

# Error y total por semana, para ver cuánto cambia el resultado según la semana.
filas = []
for semana, grupo in predicciones_test.groupby("semana"):
    fila = {"semana": semana, "desde": grupo.index.min().date(), "observado_total": grupo["valor_real"].sum()}
    for m in MODELOS:
        fila[f"desvianza | {m}"] = mean_poisson_deviance(grupo["valor_real"], grupo[m].clip(lower=EPS))
    for m in MODELOS:
        fila[f"MAE | {m}"] = mean_absolute_error(grupo["valor_real"], grupo[m])
    for m in MODELOS:
        fila[f"total | {m}"] = grupo[m].sum()
    filas.append(fila)
semanal = pd.DataFrame(filas).round(3)
guardar_tabla(semanal, "06_test_semanal.csv")

# La variabilidad se mide con la métrica principal.
variabilidad = pd.DataFrame([{
    "modelo": m,
    "desvianza_semanal_minima": semanal[f"desvianza | {m}"].min(),
    "desvianza_semanal_mediana": semanal[f"desvianza | {m}"].median(),
    "desvianza_semanal_maxima": semanal[f"desvianza | {m}"].max(),
    "semanas_con_menor_desvianza_que_linea_base": (
        pd.NA if m == LINEA_BASE
        else int((semanal[f"desvianza | {m}"] < semanal[f"desvianza | {LINEA_BASE}"]).sum())
    ),
    "semanas": len(semanal),
} for m in MODELOS])
guardar_tabla(variabilidad, "07_test_variabilidad_semanal.csv")

fechas_semanas = pd.to_datetime(semanal["desde"])

fig, ax = plt.subplots(figsize=(14, 5))
ax.plot(fechas_semanas, semanal["observado_total"], marker="o", color="tab:orange", label="Observado")
ax.plot(fechas_semanas, semanal[f"total | {LINEA_BASE}"], marker="s", linestyle="--", color="tab:red",
        label=LINEA_BASE)
ax.plot(fechas_semanas, semanal[f"total | {ARBOL}"], marker="o", linestyle="--", color="tab:green",
        label=ARBOL)
ax.set_title("Siniestros por semana en el conjunto de prueba: observado y predicho")
ax.set_xlabel("Semana (fecha de inicio)")
ax.set_ylabel("Siniestros en la semana")
ax.legend()
plt.tight_layout()
guardar_figura(fig, "fig3_test_totales_semanales.png")

fig, ax = plt.subplots(figsize=(14, 5))
ax.plot(fechas_semanas, semanal[f"desvianza | {LINEA_BASE}"], marker="s", color="tab:red", label=LINEA_BASE)
ax.plot(fechas_semanas, semanal[f"desvianza | {ARBOL}"], marker="o", color="tab:green", label=ARBOL)
ax.set_title("Desvianza de Poisson de cada semana del conjunto de prueba")
ax.set_xlabel("Semana (fecha de inicio)")
ax.set_ylabel("Desvianza de Poisson media de la semana")
ax.legend()
plt.tight_layout()
guardar_figura(fig, "fig4_test_desvianza_semanal.png")

elapsed = time.time() - T0
print(f"\nEntrenamiento finalizado en {elapsed:.1f} s.", flush=True)
print("Resultados guardados en:", OUTPUT_DIR, flush=True)
print("Para citarlos desde el informe con las mismas rutas que el notebook, copiar", flush=True)
print(f"  {OUTPUT_DIR}/tablas/*  ->  experiments/base_2/tablas/", flush=True)
print(f"  {OUTPUT_DIR}/figuras/* ->  experiments/base_2/figuras/", flush=True)
