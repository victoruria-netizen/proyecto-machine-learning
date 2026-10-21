"""
pagina_prediccion.py — Pestaña «Predicción (PAA)» del dashboard (Entregable 3, fase 5).

Qué muestra: la cantidad esperada de siniestros viales registrados por municipio de Montevideo y día, con la solución
final del PAA (GLM Poisson (a), ventana de 364 días). No usa bases de datos ni los módulos de conexión heredados.

Entradas (todas dentro del repositorio, nada se reentrena):
  - ``models/modelo_final.json`` vía ``src.modelo.cargar_modelo``: modo «Próxima semana» (01/01/2026 al 07/01/2026, D51:
    sin historia).
  - ``experiments/evaluacion_final/predicciones_bloque_final.csv``: modo «Histórico», leído tal cual, sin recalcular.
    Esas predicciones salen del reentrenamiento semanal de la fase 4; el modelo exportado no las reproduce (D63).
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

import json

import pandas as pd
import streamlit as st

import charts
import ui
from src import modelo as mod

RUTA_MODELO = _RAIZ / "models" / "modelo_final.json"
RUTA_PREDICCIONES = _RAIZ / "experiments" / "evaluacion_final" / "predicciones_bloque_final.csv"
RUTA_CAPA = _AQUI / "assets" / "municipios_montevideo_simplificado.geojson"

PAPEL_SOLUCION = "solución"
COLUMNAS_HISTORICO = ["fecha", "origen", "corte", "municipio", "observado", "predicho",
                      "inf_80", "sup_80", "inf_95", "sup_95", "tipo_intervalo", "papel"]
SEMANA_COMPLETA = "Semana completa"

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


def cargar_historico(ruta=RUTA_PREDICCIONES) -> pd.DataFrame:
    "Predicciones de la solución en el bloque final (47 semanas × 7 días × 8 municipios), tal como están en el CSV."
    _exigir_archivo(ruta, "el archivo de predicciones del bloque final")
    df = pd.read_csv(ruta, parse_dates=["fecha", "origen"], encoding="utf-8")
    faltan = [c for c in COLUMNAS_HISTORICO if c not in df.columns]
    if faltan:
        raise ErrorEntrada(f"Al archivo de predicciones le faltan columnas: {', '.join(faltan)}.")
    return df[df["papel"] == PAPEL_SOLUCION].reset_index(drop=True)


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
    "56 filas (7 días × 8 municipios) desde el origen del modelo, con columnas ``municipio``, ``esperado`` e intervalos."
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


# ------------------------------------------------------------------------------------------- mapa
def _rampa(valor: float, minimo: float, maximo: float) -> list:
    "Color RGBA de una rampa secuencial de azul claro a azul institucional."
    t = 0.5 if maximo <= minimo else (valor - minimo) / (maximo - minimo)
    claro, oscuro = (222, 235, 247), (11, 83, 148)
    return [round(c + (o - c) * t) for c, o in zip(claro, oscuro)] + [200]


def datos_mapa(valores: pd.Series, capa: dict) -> pd.DataFrame:
    "Un registro por municipio con su polígono, color y texto, para ``pydeck.PolygonLayer``."
    minimo, maximo = float(valores.min()), float(valores.max())
    filas = []
    for f in capa["features"]:
        nombre = f["properties"]["municipio"]
        if nombre not in valores.index:
            raise ErrorEntrada(f"La capa de municipios trae {nombre}, que no está en la predicción.")
        v = float(valores[nombre])
        g = f["geometry"]
        anillos = [g["coordinates"][0]] if g["type"] == "Polygon" else [p[0] for p in g["coordinates"]]   # contorno exterior
        for anillo in anillos:
            filas.append({"municipio": nombre, "polygon": anillo, "esperado": v,
                          "texto": f"{v:.1f}".replace(".", ","), "color": _rampa(v, minimo, maximo)})
    return pd.DataFrame(filas)


def _mapa(valores: pd.Series, etiqueta: str) -> None:
    import pydeck as pdk
    _exigir_archivo(RUTA_CAPA, "la capa de municipios")
    capa = json.loads(RUTA_CAPA.read_text(encoding="utf-8"))
    df = datos_mapa(valores, capa)
    st.pydeck_chart(pdk.Deck(
        layers=[pdk.Layer("PolygonLayer", data=df, get_polygon="polygon", get_fill_color="color",
                          get_line_color=[255, 255, 255], line_width_min_pixels=1, stroked=True, filled=True,
                          pickable=True, auto_highlight=True)],
        initial_view_state=pdk.ViewState(latitude=-34.82, longitude=-56.17, zoom=9.3, pitch=0),
        tooltip={"text": "{municipio}\n" + etiqueta + ": {texto}"},
        map_style="road",
    ))
    st.caption(f"Color: {etiqueta.lower()} por municipio, de {str(round(valores.min(), 1)).replace('.', ',')} (claro) "
               f"a {str(round(valores.max(), 1)).replace('.', ',')} (oscuro).")


# ---------------------------------------------------------------------------------------- pantalla
@st.cache_resource(show_spinner=False)
def _modelo_en_cache():
    return cargar_modelo_final()


@st.cache_data(show_spinner=False)
def _historico_en_cache():
    return cargar_historico()


def _fmt(d) -> str:
    return pd.Timestamp(d).strftime("%d/%m/%Y")


def _intervalo(inf, sup) -> str:
    return f"{int(inf)} a {int(sup)}"


def _mostrar_semana(semana: pd.DataFrame, con_observado: bool) -> None:
    "Mapa, resumen, gráfico y tabla de una semana (56 filas con ``esperado``, y ``observado`` en el histórico)."
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
        st.plotly_chart(charts.barras(resumen[["Esperado", "Observado"]], height=320, y_title="Siniestros registrados",
                                      color=["#0B5394", "#E69F00"]), use_container_width=True)
        resumen["Diferencia (esperado − observado)"] = resumen["Esperado"] - resumen["Observado"]
    else:
        resumen = resumen.rename(columns={"esperado": "Esperado"})
        st.plotly_chart(charts.barras(resumen[["Esperado"]], height=320, y_title="Siniestros esperados"),
                        use_container_width=True)
    st.dataframe(resumen.round(2), use_container_width=True)

    st.subheader("Por día")
    if con_observado:
        mun = st.selectbox("Municipio", list(mod.MUNICIPIOS), key="pred_municipio")
        d = semana[semana["municipio"] == mun].set_index("fecha")
        graf = pd.DataFrame({"Esperado": d["esperado"], "Observado": d["observado"]})
        graf.index = [_fmt(i) for i in graf.index]
        st.plotly_chart(charts.lineas(graf, color=["#0B5394", "#E69F00"], height=320, y_title="Siniestros registrados"),
                        use_container_width=True)
    else:
        graf = semana.pivot(index="fecha", columns="municipio", values="esperado")
        graf.index = [_fmt(i) for i in graf.index]
        st.plotly_chart(charts.lineas(graf, height=360, y_title="Siniestros esperados"), use_container_width=True)

    with st.expander("Tabla por municipio y día, con intervalos"):
        t = pd.DataFrame({"Fecha": [_fmt(f) for f in semana["fecha"]], "Municipio": semana["municipio"],
                          "Esperado": semana["esperado"].round(2),
                          "Intervalo 80 %": [_intervalo(a, b) for a, b in zip(semana["inf_80"], semana["sup_80"])],
                          "Intervalo 95 %": [_intervalo(a, b) for a, b in zip(semana["inf_95"], semana["sup_95"])]})
        if con_observado:
            t["Observado"] = semana["observado"].astype(int)
        st.dataframe(t, use_container_width=True, hide_index=True)
        st.caption(f"Intervalos de predicción de conteos ({semana['tipo_intervalo'].iloc[0]}): cada uno deja afuera la "
                   "misma probabilidad en ambas colas.")


def render() -> None:
    ui.hero("🔮 Predicción (PAA)", "Cantidad esperada de siniestros registrados por municipio de Montevideo · solución final del PAA")
    st.info(TEXTO_QUE_SE_PREDICE)
    modo = st.radio("Modo", ["Próxima semana", "Histórico"], horizontal=True, key="pred_modo")

    try:
        if modo == "Próxima semana":
            modelo = _modelo_en_cache()
            semana = predecir_proxima_semana(modelo)
            st.markdown(f"**Predicción del {_fmt(semana['fecha'].min())} al {_fmt(semana['fecha'].max())}** para los "
                        "8 municipios, con el modelo final exportado (`models/modelo_final.json`), entrenado con datos "
                        f"hasta el {_fmt(modelo['hasta'])}. Todavía no hay observados con los que compararla.")
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
            _mostrar_semana(semana, con_observado=True)
    except ErrorEntrada as e:
        st.error(str(e))
