"""
pagina_prediccion.py — Pestaña «Predicción (PAA)» del dashboard (Entregable 3, fase 5).

Qué muestra: la cantidad esperada de siniestros viales registrados por municipio de Montevideo y día, con la solución
final del PAA (GLM Poisson (a), ventana de 364 días). No usa bases de datos ni los módulos de conexión heredados.

Entradas (todas dentro del repositorio, nada se reentrena):
  - ``models/modelo_final.json`` vía ``src.modelo.cargar_modelo``: modo «Semana posterior al corte» (01/01/2026 al 07/01/2026,
    D51: sin historia; entorno simulado con corte al 31/12/2025, D77).
  - ``experiments/evaluacion_final/predicciones_bloque_final.csv``: modo «Histórico», leído tal cual, sin recalcular.
    Esas predicciones salen del reentrenamiento semanal de la fase 4; el modelo exportado no las reproduce (D63). De
    ahí salen también la referencia L1 y las métricas descriptivas de la semana (desvianza de Poisson, fuera del 80 %):
    se calculan sobre ese CSV y no deciden nada.
  - ``models/metadata.json``: ficha «Sobre el modelo», con el sha256 de ``modelo_final.json`` calculado en vivo.
  - ``app/assets/municipios_montevideo_simplificado.geojson``: capa de municipios para el mapa (ver ORIGEN.md).

Compatibilidad (D68, D70): sólo funciones de streamlit 1.57.0, plotly 5.22.0 y pydeck 0.9.1.
"""

import sys
from pathlib import Path

_AQUI = Path(__file__).resolve().parent
_RAIZ = _AQUI.parent
for _p in (str(_AQUI), str(_RAIZ)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import hashlib
import json

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import charts
import ui
from src import modelo as mod

RUTA_MODELO = _RAIZ / "models" / "modelo_final.json"
RUTA_PREDICCIONES = _RAIZ / "experiments" / "evaluacion_final" / "predicciones_bloque_final.csv"
RUTA_METADATA = _RAIZ / "models" / "metadata.json"
RUTA_CAPA = _AQUI / "assets" / "municipios_montevideo_simplificado.geojson"

PAPEL_SOLUCION = "solución"
COLUMNAS_HISTORICO = ["fecha", "origen", "corte", "municipio", "observado", "predicho",
                      "inf_80", "sup_80", "inf_95", "sup_95", "tipo_intervalo", "papel"]
SEMANA_COMPLETA = "Semana completa"
MODO_POSTERIOR = "Semana posterior al corte"
MODO_HISTORICO = "Histórico"
PREFIJO_REFERENCIA = "L1"

# Un color fijo por municipio (la paleta de charts tiene 7 colores y repetiría el de A en G).
COLOR_MUNICIPIO = {"MUNICIPIO A": "#0B5394", "MUNICIPIO B": "#E69F00", "MUNICIPIO C": "#009E73", "MUNICIPIO CH": "#CC79A7",
                   "MUNICIPIO D": "#56B4E9", "MUNICIPIO E": "#D55E00", "MUNICIPIO F": "#7F7F7F", "MUNICIPIO G": "#8C564B"}
COLOR_ESPERADO, COLOR_OBSERVADO, COLOR_REFERENCIA = "#0B5394", "#E69F00", "#7F7F7F"
COLOR_FUERA, COLOR_INTERVALO = "#C0392B", "#9DB7D5"
LEYENDA_ARRIBA = dict(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0))

TEXTO_QUE_SE_PREDICE = (
    "**Qué se predice.** La cantidad esperada de siniestros viales *registrados* en cada municipio de Montevideo, por día. "
    "Es un conteo esperado a partir del municipio y del calendario (día de la semana y feriados), no una probabilidad ni "
    "una predicción de un hecho puntual. Lo registrado depende de cómo se denuncia y se carga cada siniestro."
)


class ErrorEntrada(Exception):
    "Entrada inválida o archivo ausente; el mensaje está pensado para mostrarse tal cual al usuario."


# ------------------------------------------------------------------------------- carga y validación
def _exigir_archivo(ruta: Path, que: str) -> None:
    if not Path(ruta).is_file():
        try:
            mostrada = Path(ruta).resolve().relative_to(_RAIZ).as_posix()
        except ValueError:
            mostrada = str(ruta)
        raise ErrorEntrada(f"No se encontró {que}: {mostrada}. "
                           "Verificá que el repositorio esté completo (git pull); no hace falta reentrenar nada.")


def cargar_modelo_final(ruta=RUTA_MODELO) -> dict:
    "Carga el modelo exportado; ``ErrorEntrada`` si el archivo falta o no es un GLM guardado con ``guardar_modelo``."
    _exigir_archivo(ruta, "el archivo del modelo")
    try:
        return mod.cargar_modelo(ruta)
    except (ValueError, KeyError, json.JSONDecodeError) as e:
        raise ErrorEntrada(f"El archivo del modelo no se pudo leer ({type(e).__name__}: {e}).") from e


def _leer_predicciones(ruta) -> pd.DataFrame:
    _exigir_archivo(ruta, "el archivo de predicciones del bloque final")
    df = pd.read_csv(ruta, parse_dates=["fecha", "origen"], encoding="utf-8")
    faltan = [c for c in COLUMNAS_HISTORICO if c not in df.columns]
    if faltan:
        raise ErrorEntrada(f"Al archivo de predicciones le faltan columnas: {', '.join(faltan)}.")
    return df


def cargar_historico(ruta=RUTA_PREDICCIONES) -> pd.DataFrame:
    "Predicciones de la solución en el bloque final (47 semanas × 7 días × 8 municipios), tal como están en el CSV."
    df = _leer_predicciones(ruta)
    return df[df["papel"] == PAPEL_SOLUCION].reset_index(drop=True)


def cargar_referencia(ruta=RUTA_PREDICCIONES) -> pd.DataFrame:
    "Referencia L1 (nivel por calendario de 8 niveles) del mismo CSV; ``ErrorEntrada`` si el archivo no la trae."
    df = _leer_predicciones(ruta)
    ref = df[(df["papel"] == "referencia") & df["modelo"].astype(str).str.startswith(PREFIJO_REFERENCIA)]
    if ref.empty:
        raise ErrorEntrada("El archivo de predicciones no trae la referencia L1 (papel «referencia», modelo L1…).")
    return ref.reset_index(drop=True)


def origenes_disponibles(historico: pd.DataFrame) -> list:
    return sorted(pd.Timestamp(o) for o in historico["origen"].unique())


def validar_semana(origen, disponibles) -> pd.Timestamp:
    "Origen de semana como Timestamp; ``ErrorEntrada`` si no es una fecha o no es el inicio de una semana del bloque final."
    try:
        o = pd.Timestamp(origen)
    except (ValueError, TypeError) as e:
        raise ErrorEntrada(f"La semana indicada no es una fecha válida: {origen!r}.") from e
    if pd.isna(o):
        raise ErrorEntrada("No se indicó la semana.")
    disponibles = list(disponibles)
    if o not in disponibles:
        d, h = min(disponibles), max(disponibles) + pd.Timedelta(days=6)
        raise ErrorEntrada(f"La semana con origen {o:%d/%m/%Y} está fuera del bloque final ({d:%d/%m/%Y} a {h:%d/%m/%Y}) "
                           "o no empieza en un origen de semana de ese bloque.")
    return o


# --------------------------------------------------------------------------------------- predicción
def historia_vacia() -> pd.DataFrame:
    "El conjunto (a) no usa historia (D51): sólo se necesita el calendario de la semana, que sale de ``var.tipo_dia``."
    return pd.DataFrame({"fecha": pd.Series(dtype="datetime64[ns]"), "zona_id": pd.Series(dtype=str),
                         "tipo_dia": pd.Series(dtype=str)})


def predecir_proxima_semana(modelo: dict) -> pd.DataFrame:
    "Semana posterior al corte del modelo (el nombre interno se mantiene, D77). 56 filas (7 días × 8 municipios) desde el origen del modelo, con columnas ``municipio``, ``esperado`` e intervalos."
    s = mod.predecir_semana(modelo, historia_vacia(), modelo["origen"])
    return s.rename(columns={"zona_id": "municipio", "pred": "esperado"})


def semana_historica(historico: pd.DataFrame, origen) -> pd.DataFrame:
    "Las 56 filas de la semana con ese origen, renombradas como la predicción nueva (``esperado``); sin recalcular nada."
    o = validar_semana(origen, origenes_disponibles(historico))
    s = historico[historico["origen"] == o].rename(columns={"predicho": "esperado"})
    return s.sort_values(["fecha", "municipio"]).reset_index(drop=True)


def resumen_por_municipio(semana: pd.DataFrame) -> pd.DataFrame:
    "Total de la semana por municipio: esperado y, si hay, observado."
    cols = ["esperado"] + (["observado"] if "observado" in semana.columns else [])
    return semana.groupby("municipio")[cols].sum()


# --------------------------------------------------------------------- métricas descriptivas (no deciden nada)
def desvianza_poisson(observado, predicho) -> np.ndarray:
    "Desvianza de Poisson por fila: 2·(y·ln(y/μ) − (y − μ)). Las predicciones ≤ 0 se reemplazan por 1e-6, como en todo el proyecto."
    y = np.asarray(observado, dtype=float)
    mu = np.asarray(predicho, dtype=float)
    mu = np.where(mu <= 0, 1e-6, mu)
    termino = np.where(y > 0, y * np.log(np.where(y > 0, y, 1.0) / mu), 0.0)
    return 2.0 * (termino - (y - mu))


def desvianza_media(df: pd.DataFrame, col_predicho: str = "predicho") -> float:
    return float(np.mean(desvianza_poisson(df["observado"], df[col_predicho])))


def desvianza_por_semana(df: pd.DataFrame) -> pd.Series:
    "Desvianza de Poisson media de cada semana, indexada por origen."
    d = pd.Series(desvianza_poisson(df["observado"], df["predicho"]), index=df.index)
    return d.groupby(df["origen"]).mean()


def fuera_del_intervalo(df: pd.DataFrame, nivel: int = 80) -> pd.Series:
    "Verdadero donde el observado cae por debajo del límite inferior o por encima del superior del intervalo de ese nivel."
    return (df["observado"] < df[f"inf_{nivel}"]) | (df["observado"] > df[f"sup_{nivel}"])


def comparacion_global(historico: pd.DataFrame, referencia: pd.DataFrame) -> dict:
    "Desvianza global de la solución y de L1, y en cuántas semanas la solución tiene menor desvianza que L1."
    sol, ref = desvianza_por_semana(historico), desvianza_por_semana(referencia)
    return {"solucion": desvianza_media(historico), "referencia": desvianza_media(referencia),
            "semanas_menor": int((sol < ref.reindex(sol.index)).sum()), "semanas": int(len(sol))}


def totales_semanales(historico: pd.DataFrame, referencia: pd.DataFrame | None) -> pd.DataFrame:
    "Totales por semana (índice: origen): observado, esperado de la solución y, si hay, esperado de L1."
    t = pd.DataFrame({"Observado": historico.groupby("origen")["observado"].sum(),
                      "Solución": historico.groupby("origen")["predicho"].sum()})
    if referencia is not None:
        t["L1"] = referencia.groupby("origen")["predicho"].sum()
    return t


def ficha_modelo(ruta_modelo=RUTA_MODELO, ruta_metadata=RUTA_METADATA) -> dict:
    "Datos de ``metadata.json`` y sha256 de ``modelo_final.json`` calculado ahora; ``ErrorEntrada`` si falta un archivo."
    _exigir_archivo(ruta_metadata, "la ficha del modelo")
    _exigir_archivo(ruta_modelo, "el archivo del modelo")
    try:
        meta = json.loads(Path(ruta_metadata).read_text(encoding="utf-8"))
        conf, ent, inter = meta["configuracion"], meta["entrenamiento"], meta["intervalos"]
        ficha = {"configuracion": conf["configuracion"], "variables_descripcion": conf["conjunto_de_variables"]["descripcion"],
                 "variables": list(conf["conjunto_de_variables"]["columnas"]), "ventana_dias": conf["ventana"]["dias"],
                 "reentrenamiento_cada_dias": conf["reentrenamiento_cada_dias"], "desde": ent["desde"], "hasta": ent["hasta"],
                 "filas": ent["filas"], "alpha": inter["alpha"], "origen_alpha": inter["origen_alpha"],
                 "sha256_metadata": meta["sha256_modelo"]}
    except (ValueError, KeyError, TypeError) as e:
        raise ErrorEntrada(f"La ficha del modelo no se pudo leer ({type(e).__name__}: {e}).") from e
    ficha["sha256_calculado"] = hashlib.sha256(Path(ruta_modelo).read_bytes()).hexdigest()
    ficha["coincide"] = ficha["sha256_calculado"] == ficha["sha256_metadata"]
    return ficha


# ------------------------------------------------------------------------------------------- mapa
def _rampa(valor: float, minimo: float, maximo: float) -> list:
    "Color RGBA de una rampa secuencial de azul claro a azul institucional."
    t = 0.5 if maximo <= minimo else (valor - minimo) / (maximo - minimo)
    claro, oscuro = (222, 235, 247), (11, 83, 148)
    return [round(c + (o - c) * t) for c, o in zip(claro, oscuro)] + [200]


def _contornos(f: dict) -> list:
    "Contornos exteriores (listas de [lon, lat]) de una entidad de la capa."
    g = f["geometry"]
    return [g["coordinates"][0]] if g["type"] == "Polygon" else [p[0] for p in g["coordinates"]]   # contorno exterior


def _area_y_centroide(anillo: list) -> tuple:
    "Área con signo (fórmula del lazo) y centroide [lon, lat] de un contorno."
    a = cx = cy = 0.0
    for (x0, y0), (x1, y1) in zip(anillo, anillo[1:] + anillo[:1]):
        c = x0 * y1 - x1 * y0
        a += c
        cx += (x0 + x1) * c
        cy += (y0 + y1) * c
    a /= 2.0
    if a == 0:
        raise ErrorEntrada("La capa de municipios trae un contorno sin área.")
    return a, [cx / (6.0 * a), cy / (6.0 * a)]


def datos_mapa(valores: pd.Series, capa: dict) -> pd.DataFrame:
    "Un registro por municipio con su polígono, color y texto, para ``pydeck.PolygonLayer``."
    minimo, maximo = float(valores.min()), float(valores.max())
    filas = []
    for f in capa["features"]:
        nombre = f["properties"]["municipio"]
        if nombre not in valores.index:
            raise ErrorEntrada(f"La capa de municipios trae {nombre}, que no está en la predicción.")
        v = float(valores[nombre])
        for anillo in _contornos(f):
            filas.append({"municipio": nombre, "polygon": anillo, "esperado": v,
                          "texto": f"{v:.1f}".replace(".", ","), "color": _rampa(v, minimo, maximo)})
    return pd.DataFrame(filas)


def etiquetas_mapa(valores: pd.Series, capa: dict) -> pd.DataFrame:
    """Un registro por municipio para ``pydeck.TextLayer``: su letra y su valor (coma decimal), en dos líneas, en el
    centroide del contorno exterior más grande."""
    filas = []
    for f in capa["features"]:
        nombre = f["properties"]["municipio"]
        if nombre not in valores.index:
            raise ErrorEntrada(f"La capa de municipios trae {nombre}, que no está en la predicción.")
        v = float(valores[nombre])
        _, centro = max((_area_y_centroide(a) for a in _contornos(f)), key=lambda ac: abs(ac[0]))
        filas.append({"municipio": nombre, "posicion": centro,
                      "texto": f"{nombre.replace('MUNICIPIO ', '')}\n{v:.1f}".replace(".", ",")})
    return pd.DataFrame(filas)


def _mapa(valores: pd.Series, etiqueta: str) -> None:
    import pydeck as pdk
    _exigir_archivo(RUTA_CAPA, "la capa de municipios")
    capa = json.loads(RUTA_CAPA.read_text(encoding="utf-8"))
    df, textos = datos_mapa(valores, capa), etiquetas_mapa(valores, capa)
    st.pydeck_chart(pdk.Deck(
        layers=[pdk.Layer("PolygonLayer", data=df, get_polygon="polygon", get_fill_color="color",
                          get_line_color=[255, 255, 255], line_width_min_pixels=1, stroked=True, filled=True,
                          pickable=True, auto_highlight=True),
                pdk.Layer("TextLayer", data=textos, get_position="posicion", get_text="texto", get_size=13,
                          get_color=[31, 41, 55, 255], background=True, get_background_color=[255, 255, 255, 190],
                          get_text_anchor='"middle"', get_alignment_baseline='"center"', pickable=False)],
        initial_view_state=pdk.ViewState(latitude=-34.82, longitude=-56.17, zoom=9.3, pitch=0),
        tooltip={"text": "{municipio}\n" + etiqueta + ": {texto}"},
        map_style="road",
    ))
    st.caption(f"Color: {etiqueta.lower()} por municipio, de {str(round(valores.min(), 1)).replace('.', ',')} (claro) "
               f"a {str(round(valores.max(), 1)).replace('.', ',')} (oscuro); cada municipio lleva su letra y su valor. "
               "El mapa base necesita conexión; sin red se ven igual los municipios y sus valores.")


# ---------------------------------------------------------------------------------------- pantalla
@st.cache_resource(show_spinner=False)
def _modelo_en_cache():
    return cargar_modelo_final()


@st.cache_data(show_spinner=False)
def _historico_en_cache():
    return cargar_historico()


@st.cache_data(show_spinner=False)
def _referencia_en_cache():
    return cargar_referencia()


def _fmt(d) -> str:
    return pd.Timestamp(d).strftime("%d/%m/%Y")


def _num(x, decimales: int = 1) -> str:
    "Número con coma decimal y punto de miles (es-UY)."
    return f"{x:,.{decimales}f}".replace(",", "\0").replace(".", ",").replace("\0", ".")


def texto_modo_posterior(modelo: dict, semana: pd.DataFrame) -> str:
    "Texto del modo «Semana posterior al corte»; las fechas y la ventana salen del modelo, no se escriben fijas (D77)."
    return (f"Entorno simulado con fecha de corte {_fmt(modelo['hasta'])}, el último día con datos. Predicción de la "
            f"semana posterior al corte, del {_fmt(semana['fecha'].min())} al {_fmt(semana['fecha'].max())}, para los "
            "8 municipios, con el modelo final exportado (`models/modelo_final.json`), entrenado con los "
            f"{modelo['ventana_dias']} días anteriores al corte. No es la semana actual y no hay observados con los que "
            "compararla.")


def _intervalo(inf, sup) -> str:
    return f"{int(inf)} a {int(sup)}"


def _config_dos_decimales(tabla: pd.DataFrame) -> dict:
    "Formato de 2 decimales para las columnas decimales; no cambia los valores."
    return {c: st.column_config.NumberColumn(format="%.2f") for c in tabla.columns if pd.api.types.is_float_dtype(tabla[c])}


def _metricas_semana(semana: pd.DataFrame, referencia_semana: pd.DataFrame | None) -> None:
    "Cuatro métricas descriptivas de la semana elegida, calculadas sobre el CSV de la evaluación final."
    n, observado, esperado = len(semana), int(semana["observado"].sum()), float(semana["esperado"].sum())
    desvianza = desvianza_media(semana, "esperado")
    fuera = int(fuera_del_intervalo(semana).sum())
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Observado en la semana", _num(observado, 0), help="Siniestros registrados en los 8 municipios durante los 7 días.")
    if referencia_semana is not None:
        c2.metric("Esperado (solución)", _num(esperado, 1),
                  help=f"Suma de los esperados de la solución. El esperado de L1 (referencia) en la misma semana es "
                       f"{_num(float(referencia_semana['predicho'].sum()), 1)}.")
        d_ref = desvianza_media(referencia_semana)
        c3.metric("Desvianza de Poisson media", _num(desvianza, 3), delta=f"{desvianza - d_ref:+.3f} frente a L1".replace(".", ","),
                  delta_color="inverse",
                  help=f"Promedio de la desvianza de Poisson de los {n} pares municipio-día. Menor valor, menor desvianza. "
                       f"La de L1 en la misma semana es {_num(d_ref, 3)}.")
    else:
        c2.metric("Esperado (solución)", _num(esperado, 1), help="Suma de los esperados de la solución.")
        c3.metric("Desvianza de Poisson media", _num(desvianza, 3),
                  help=f"Promedio de la desvianza de Poisson de los {n} pares municipio-día. Menor valor, menor desvianza.")
    c4.metric("Fuera del intervalo del 80 %", f"{fuera} de {n}",
              help="Pares municipio-día cuyo observado cae por debajo del límite inferior o por encima del superior del "
                   "intervalo del 80 %.")
    st.caption("Métricas descriptivas de esta semana, calculadas en la app sobre el CSV de la evaluación final; no deciden nada.")


def _grafico_semanas(historico: pd.DataFrame, referencia: pd.DataFrame | None, origen: pd.Timestamp) -> None:
    "Totales semanales del bloque final (observado, solución y L1) con la semana elegida marcada."
    totales = totales_semanales(historico, referencia)
    colores = {"Observado": COLOR_OBSERVADO, "Solución": COLOR_ESPERADO, "L1": COLOR_REFERENCIA}
    fig = charts.lineas(totales, color=colores, height=340, markers=False, x_title="Inicio de la semana",
                        y_title="Siniestros por semana", margin=dict(t=60), **LEYENDA_ARRIBA)
    for traza in fig.data:
        if traza.name == "L1":
            traza.update(line=dict(color=COLOR_REFERENCIA, dash="dot", width=2.2))
    fig.update_xaxes(tickformat="%d/%m/%y", hoverformat="%d/%m/%Y")
    fig.add_vrect(x0=origen - pd.Timedelta(hours=84), x1=origen + pd.Timedelta(hours=84), fillcolor=COLOR_INTERVALO,
                  opacity=0.35, line_width=0, layer="below")
    st.plotly_chart(fig, use_container_width=True)
    if referencia is not None:
        c = comparacion_global(historico, referencia)
        st.caption(f"Desvianza de Poisson media en las {c['semanas']} semanas: solución {_num(c['solucion'], 4)}; "
                   f"L1 {_num(c['referencia'], 4)}. La solución tiene menor desvianza que L1 en {c['semanas_menor']} de "
                   f"{c['semanas']} semanas. Es una descripción de este bloque final, calculada en la app sobre el CSV; "
                   "no decide nada. La franja marca la semana elegida.")
    else:
        st.caption("Sin la referencia L1 no se muestran las comparaciones. La franja marca la semana elegida.")


def _grafico_dia_municipio(semana: pd.DataFrame, municipio: str) -> None:
    "Esperado como línea, intervalo del 80 % como barras de error y observado como puntos (en rojo, los fuera del intervalo)."
    d = semana[semana["municipio"] == municipio].sort_values("fecha")
    x = [_fmt(f) for f in d["fecha"]]
    esperado = d["esperado"].to_numpy(dtype=float)
    inf, sup = d["inf_80"].to_numpy(dtype=float), d["sup_80"].to_numpy(dtype=float)
    fuera = fuera_del_intervalo(d).to_numpy()
    observado = d["observado"].to_numpy(dtype=float)
    fig = charts.lineas(pd.DataFrame({"Esperado": esperado}, index=x), color=[COLOR_ESPERADO], height=340,
                        y_title="Siniestros registrados", margin=dict(t=60), **LEYENDA_ARRIBA)
    fig.update_layout(showlegend=True)
    fig.update_xaxes(type="category")
    # Las barras de error van centradas en el punto medio del intervalo para que cubran exactamente de inf a sup.
    fig.add_trace(go.Scatter(
        x=x, y=(inf + sup) / 2, mode="markers", name="Intervalo del 80 %", customdata=np.column_stack([inf, sup]),
        marker=dict(symbol="line-ew", size=12, color=COLOR_INTERVALO, line=dict(width=2, color=COLOR_INTERVALO)),
        error_y=dict(type="data", symmetric=True, array=(sup - inf) / 2, color=COLOR_INTERVALO, thickness=3, width=7),
        hovertemplate="%{x}<br>Intervalo del 80 %: %{customdata[0]:.0f} a %{customdata[1]:.0f}<extra></extra>"))
    for etiqueta, mascara, color in (("Observado", ~fuera, COLOR_OBSERVADO), ("Observado fuera del 80 %", fuera, COLOR_FUERA)):
        fig.add_trace(go.Scatter(
            x=[xi for xi, m in zip(x, mascara) if m], y=observado[mascara], mode="markers", name=etiqueta,
            marker=dict(size=10, color=color, line=dict(width=1, color="white")),
            hovertemplate=f"%{{x}}<br>{etiqueta}: %{{y:.0f}}<extra></extra>"))
    st.plotly_chart(fig, use_container_width=True)


def _mostrar_semana(semana: pd.DataFrame, con_observado: bool, historico: pd.DataFrame | None = None,
                    referencia: pd.DataFrame | None = None) -> None:
    """Mapa, resumen, gráficos y tabla de una semana (56 filas con ``esperado``, y ``observado`` en el histórico).
    En el histórico, ``historico`` y ``referencia`` (L1, opcional) aportan las métricas y las comparaciones."""
    if con_observado:
        origen = pd.Timestamp(semana["origen"].iloc[0])
        ref_semana = None
        if referencia is not None:
            ref_semana = referencia[referencia["origen"] == origen]
            ref_semana = ref_semana if len(ref_semana) else None
        _metricas_semana(semana, ref_semana)

    dias = sorted(semana["fecha"].unique())
    periodo = st.selectbox("Período del mapa", [SEMANA_COMPLETA] + [_fmt(d) for d in dias],
                           key=f"pred_periodo_{_fmt(dias[0])}")
    if periodo == SEMANA_COMPLETA:
        valores, etiqueta = semana.groupby("municipio")["esperado"].sum(), "Esperado en la semana"
    else:
        valores = semana[semana["fecha"] == pd.to_datetime(periodo, format="%d/%m/%Y")].set_index("municipio")["esperado"]
        etiqueta = "Esperado en el día"
    _mapa(valores, etiqueta)

    st.subheader("Total de la semana por municipio")
    resumen = resumen_por_municipio(semana)
    if con_observado:
        resumen = resumen.rename(columns={"esperado": "Esperado", "observado": "Observado"})
        st.plotly_chart(charts.barras(resumen[["Esperado", "Observado"]], height=340, y_title="Siniestros registrados",
                                      color=[COLOR_ESPERADO, COLOR_OBSERVADO], margin=dict(t=60), **LEYENDA_ARRIBA),
                        use_container_width=True)
        resumen["Diferencia (esperado − observado)"] = resumen["Esperado"] - resumen["Observado"]
    else:
        resumen = resumen.rename(columns={"esperado": "Esperado"})
        st.plotly_chart(charts.barras(resumen[["Esperado"]], height=320, y_title="Siniestros esperados"),
                        use_container_width=True)
    resumen = resumen.round(2)
    st.dataframe(resumen, use_container_width=True, column_config=_config_dos_decimales(resumen))

    if con_observado:
        n_semanas = historico["origen"].nunique()
        st.subheader(f"Las {n_semanas} semanas del bloque final")
        _grafico_semanas(historico, referencia, origen)

    st.subheader("Por día")
    if con_observado:
        mun = st.selectbox("Municipio", list(mod.MUNICIPIOS), key="pred_municipio")
        _grafico_dia_municipio(semana, mun)
    else:
        graf = semana.pivot(index="fecha", columns="municipio", values="esperado")
        graf.index = [_fmt(i) for i in graf.index]
        st.plotly_chart(charts.lineas(graf, color=COLOR_MUNICIPIO, height=380, y_title="Siniestros esperados",
                                      margin=dict(t=80), **LEYENDA_ARRIBA), use_container_width=True)

    t = pd.DataFrame({"Fecha": [_fmt(f) for f in semana["fecha"]], "Municipio": semana["municipio"],
                      "Esperado": semana["esperado"].round(2),
                      "Intervalo 80 %": [_intervalo(a, b) for a, b in zip(semana["inf_80"], semana["sup_80"])],
                      "Intervalo 95 %": [_intervalo(a, b) for a, b in zip(semana["inf_95"], semana["sup_95"])]})
    if con_observado:
        t["Observado"] = semana["observado"].astype(int)
        t["Fuera del 80 %"] = ["Sí" if f else "No" for f in fuera_del_intervalo(semana)]
    with st.expander("Tabla por municipio y día, con intervalos"):
        st.dataframe(t, use_container_width=True, hide_index=True, column_config=_config_dos_decimales(t))
        st.caption(f"Intervalos de predicción de conteos ({semana['tipo_intervalo'].iloc[0]}), con cuantiles de colas iguales "
                   "(10 % y 90 % para el 80 %; 2,5 % y 97,5 % para el 95 %). Por ser conteos enteros, el modelo espera que "
                   "cubran algo más que el nivel nominal.")
    st.download_button("Descargar la tabla de la semana (CSV)", t.to_csv(index=False).encode("utf-8"),
                       file_name=f"prediccion_semana_{pd.Timestamp(semana['fecha'].min()):%Y-%m-%d}.csv", mime="text/csv",
                       key="pred_descarga_" + ("historico" if con_observado else "posterior"))


def _sobre_el_modelo() -> None:
    "Ficha del modelo final con los datos de ``models/metadata.json`` y la comprobación del sha256 en vivo."
    with st.expander("Sobre el modelo"):
        try:
            f = ficha_modelo()
        except ErrorEntrada as e:
            st.warning(str(e))
            return
        st.markdown(f"**Configuración:** {f['configuracion']}.  \n"
                    f"**Variables ({len(f['variables'])}):** {f['variables_descripcion']}: "
                    f"{', '.join('`' + v + '`' for v in f['variables'])}.")
        st.markdown(f"**Ventana:** deslizante de {f['ventana_dias']} días. En la evaluación del bloque final el modelo se "
                    f"reentrenó cada {f['reentrenamiento_cada_dias']} días; el modelo exportado es un único ajuste.")
        st.markdown(f"**Entrenamiento:** del {_fmt(f['desde'])} al {_fmt(f['hasta'])}, {_num(f['filas'], 0)} filas.")
        origen_alpha = ("método de momentos (la estimación por máxima verosimilitud de NB2 no convergió)"
                        if f["origen_alpha"] == "momentos" else str(f["origen_alpha"]))
        st.markdown(f"**α de los intervalos:** {_num(f['alpha'], 5)}, estimado por {origen_alpha}.")
        veredicto = "coincide" if f["coincide"] else "no coincide"
        st.markdown(f"**Integridad:** sha256 de `models/modelo_final.json` calculado ahora: `{f['sha256_calculado']}`; "
                    f"el de `models/metadata.json`: `{f['sha256_metadata']}`. **{veredicto.capitalize()}.**")
        if not f["coincide"]:
            st.warning("El archivo del modelo no coincide con el registrado en la ficha: no es el modelo que se exportó.")


def render() -> None:
    ui.hero("🔮 Predicción (PAA)", "Cantidad esperada de siniestros registrados por municipio de Montevideo · solución final del PAA")
    st.info(TEXTO_QUE_SE_PREDICE)
    modo = st.radio("Modo", [MODO_POSTERIOR, MODO_HISTORICO], horizontal=True, key="pred_modo")

    try:
        if modo == MODO_POSTERIOR:
            modelo = _modelo_en_cache()
            semana = predecir_proxima_semana(modelo)
            st.markdown(texto_modo_posterior(modelo, semana))
            _mostrar_semana(semana, con_observado=False)
        else:
            historico = _historico_en_cache()
            origenes = origenes_disponibles(historico)
            st.markdown("**Predicho contra observado en el bloque final** (06/02/2025 al 31/12/2025). Las predicciones salen "
                        "del reentrenamiento semanal de la evaluación final y se muestran tal como están en "
                        "`experiments/evaluacion_final/predicciones_bloque_final.csv`; no se recalculan acá y el modelo "
                        "exportado no las reproduce.")
            etiquetas = {f"{_fmt(o)} a {_fmt(o + pd.Timedelta(days=6))}": o for o in origenes}
            elegida = st.selectbox("Semana", list(etiquetas), key="pred_semana")
            semana = semana_historica(historico, validar_semana(etiquetas[elegida], origenes))
            try:
                referencia = _referencia_en_cache()
            except ErrorEntrada as e:
                referencia = None
                st.warning(f"{e} La pestaña sigue sin las comparaciones.")
            _mostrar_semana(semana, con_observado=True, historico=historico, referencia=referencia)
    except ErrorEntrada as e:
        st.error(str(e))
    _sobre_el_modelo()
