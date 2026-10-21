"""
app.py — Dashboard de Siniestros Viales
Proyecto LIDIA · Grupo 04 · UTEC ITR Norte
Uruguay · Brasil · España (2018–2025)
Modelo nuevo: gravedad {fatal | grave | leve | solo_danos} en tabla accidentes.
"""

import sys
import json
from pathlib import Path

# ── Vendoring: librerías locales ────────────────────────────────────────────
# El Python que corre el dashboard en el server (:18504) puede no traer plotly /
# SQLAlchemy / python-dotenv / streamlit-option-menu. Las bajamos físicamente a
# streamlit/librerias (pip install --target) y las cargamos desde ahí SIN tocar
# el entorno global del profe. DEBE ir antes de importar esas libs (incluido
# `from config`, que importa python-dotenv). Si la carpeta no existe (p. ej. en
# local, donde las deps están instaladas normalmente) no hace nada.
import os
_VENDOR = Path(__file__).resolve().parent / "librerias"
if _VENDOR.is_dir():
    if str(_VENDOR) not in sys.path:
        sys.path.insert(0, str(_VENDOR))
    # La carpeta vendor solo existe en el server → forzamos el perfil `server`
    # para que `config` cargue config/.env.server, sin depender de que el proceso
    # del profe exporte APP_ENV. setdefault respeta un APP_ENV ya definido.
    os.environ.setdefault("APP_ENV", "server")

from urllib.parse import quote_plus

import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, text

# Bootstrap: la raíz del repo (para `config`) y dashboard/ (para `constants`) en
# sys.path. Este archivo está en dashboard/ → un nivel bajo la raíz. Sin rutas
# absolutas. Insertar dashboard/ explícitamente hace robusto `import constants`
# tanto en `streamlit run` como en el harness AppTest.
_HERE = Path(__file__).resolve().parent          # dashboard/
_ROOT = str(_HERE.parent)                          # raíz del repo
for _p in (str(_HERE), _ROOT):
    if _p not in sys.path:
        sys.path.insert(0, _p)
from config import (
    PG_HOST, PG_PORT, PG_DB, PG_USER, PG_PASSWORD,
    MONGO_DB, get_mongo_client,
)
from constants import (  # fuente única de verdad visual (ver dashboard/constants.py)
    GRAVEDADES, POBLACION, PAISES, REGION_A_COD_INE, BR_UF_A_REGION, ESCALA_MAPA_PAIS,
    COLOR_SEVERIDAD, COLOR_PAIS, ETIQUETA_SEVERIDAD,
    NOTA_BRASIL, NOTA_ESPANA, NOTA_GEO, NOTA_RENAEST_2018, NOTA_COVID, FUENTE,
    etiqueta_sev, color_sev, colores_sev, fold_nombre,
    color_sev_rgb, fmt_int, fmt_num, fmt_pct,
)
import ui  # capa de shell visual (CSS, hero, navbar, footer)
import charts  # fábrica de figuras Plotly estilizadas (unifica el look de los charts)

# ── Constantes derivadas de la paleta central (color-blind safe, WCAG AA) ────
COLORES = colores_sev(GRAVEDADES)  # [fatal, grave, leve, solo_danos]

st.set_page_config(page_title="Siniestros Viales — Grupo 04", page_icon="🚗",
                   layout="wide", initial_sidebar_state="collapsed")
ui.inject_css()  # sistema de diseño BI corporativo (oculta chrome, tarjetas, hero)

# ── Conexión PostgreSQL ──────────────────────────────────────────────────
# Engine SQLAlchemy (con pool): elimina el UserWarning de pandas por usar una
# conexión psycopg2 cruda y mantiene max_parallel_workers_per_gather=0 por la
# restricción de /dev/shm del entorno Docker (ver §4.2.6).
@st.cache_resource
def get_engine():
    url = (f"postgresql+psycopg2://{PG_USER}:{quote_plus(PG_PASSWORD or '')}"
           f"@{PG_HOST}:{PG_PORT}/{PG_DB}")
    return create_engine(
        url, pool_pre_ping=True,
        connect_args={"options": "-c max_parallel_workers_per_gather=0"},
    )

# ── Conexión MongoDB (cliente reutilizable + agregaciones cacheadas) ───────
@st.cache_resource
def get_mongo():
    return get_mongo_client(serverSelectionTimeoutMS=8000)

@st.cache_data(ttl=3600, show_spinner="Agregando en MongoDB…")
def mongo_agg(coll, pipeline):
    return list(get_mongo()[MONGO_DB][coll].aggregate(pipeline))

# ── Helpers ────────────────────────────────────────────────────────────────
# Caché de 1 h sobre cada consulta: las Q tardan 15–42 s sin caché (§4.2.6), así
# que la primera carga las ejecuta y las siguientes son instantáneas. show_spinner
# da feedback de "cargando" en cada cache-miss sin tener que envolver cada llamada.
@st.cache_data(ttl=3600, show_spinner="Consultando base de datos…")
def query(sql, params=None):
    with get_engine().connect() as conn:
        return pd.read_sql(text(sql), conn, params=params or {})

@st.cache_data(show_spinner=False)
def _geojson(nombre):
    """Carga (una sola vez) un GeoJSON empaquetado en dashboard/assets/."""
    with open(_HERE / "assets" / nombre, encoding="utf-8") as fh:
        return json.load(fh)


def geojson_espana():
    """GeoJSON de provincias de España. Features por `properties.cod_prov` (INE)."""
    return _geojson("es_provincias.geojson")


def geojson_uruguay():
    """GeoJSON de departamentos de Uruguay (geoBoundaries ADM1, 19 features).

    Devuelve `(geojson, idx)` donde `idx` mapea el nombre normalizado (sin acentos,
    MAYÚSCULAS) → `properties.shapeName` exacto, el id que usa el choropleth. La BD
    trae la región como ' MONTEVIDEO'/'PAYSANDU' (sin tilde), por eso el match es por
    forma canónica (ver constants.fold_nombre)."""
    gj = _geojson("uy_departamentos.geojson")
    idx = {fold_nombre(f["properties"]["shapeName"]): f["properties"]["shapeName"]
           for f in gj["features"]}
    return gj, idx


def geojson_brasil():
    """GeoJSON de estados de Brasil (27 features). Id = `properties.sigla` (UF)."""
    return _geojson("br_estados.geojson")


def _ticks_125(lo, hi):
    """Valores 'lindos' (1-2-5 × 10^k) dentro de [lo, hi] para rotular la colorbar
    logarítmica con números reales (2.000 · 5.000 · 10.000 …) en vez de log10."""
    import math
    lo, hi = max(float(lo), 1.0), float(hi)
    ticks, e = [], int(math.floor(math.log10(lo)))
    while 10 ** e <= hi * 1.5:
        for m in (1, 2, 5):
            v = m * 10 ** e
            if lo * 0.7 <= v <= hi * 1.3:
                ticks.append(v)
        e += 1
    return ticks or [round(lo), round(hi)]


def coropleta(d, geojson, *, locations, featureidkey, hover_name, hover_data,
              color="total", color_scale="Reds", titulo_barra="Siniestros",
              height=540, log_color=True):
    """Choropleth (mapa de calor por área) con el look unificado del dashboard.

    Fuente única de estilo de los 3 mapas de calor (UY · BR · ES): escala secuencial
    `color_scale` (más volumen = color más intenso; ver constants.ESCALA_MAPA_PAIS),
    bordes blancos finos, colorbar compacta y separadores es-UY.

    **Escala LOGARÍTMICA por defecto** (`log_color=True`): el volumen de siniestros por
    área es muy sesgado (un outlier —Montevideo, Madrid, São Paulo— multiplica por ~20 al
    resto). En escala lineal eso aplasta a casi todas las áreas en un mismo tono pálido
    (16/19 departamentos de UY caían bajo el 17 % de la rampa). Coloreando por log10 el
    contraste se reparte; el hover y la colorbar siguen mostrando los **valores reales**.
    `d` ya debe traer la columna `locations` casada al GeoJSON."""
    import math
    import plotly.express as px
    d = d.copy()
    color_field = color
    if log_color:
        d["_logc"] = d[color].clip(lower=1).map(lambda v: math.log10(v))
        color_field = "_logc"
        hover_data = {**hover_data, "_logc": False}   # ocultar el log del tooltip
    fig = px.choropleth(
        d, geojson=geojson, locations=locations, featureidkey=featureidkey,
        color=color_field, color_continuous_scale=color_scale, hover_name=hover_name,
        hover_data=hover_data,
        labels={"total": "Siniestros", "fatales": "Fatales", "pct_fatal": "% fatal",
                "region": "Región", "estado": "Estado"})
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_traces(marker_line_color="white", marker_line_width=0.6)
    cbar = dict(title=titulo_barra, thickness=12, len=0.78, outlinewidth=0, ticks="outside")
    if log_color:
        tv = _ticks_125(d[color].min(), d[color].max())
        cbar.update(tickvals=[math.log10(t) for t in tv], ticktext=[fmt_int(t) for t in tv])
    else:
        cbar.update(tickformat=",.0f")
    fig.update_layout(
        margin=dict(l=0, r=0, t=10, b=0), height=height, separators=",.",
        dragmode=False, coloraxis_colorbar=cbar,
        font=dict(family="Inter, 'Segoe UI', sans-serif", color="#1F2937"),
        geo=dict(bgcolor="rgba(0,0,0,0)"))
    return fig

def tasa(df, col, nuevo):
    if "pais" in df.columns:
        df[nuevo] = df.apply(
            lambda r: round(r[col] / POBLACION.get(r["pais"], 1) * 100000, 2), axis=1)
    return df

def header(titulo, subtitulo=None):
    """Encabezado uniforme de sección: banner hero estilizado (ver ui.hero)."""
    ui.hero(titulo, subtitulo)

def kpi(col, label, value, delta=None, help=None, inverse=True, icon=None):
    """KPI como tarjeta (contenedor con borde) con delta semántico.

    En siniestralidad **bajar es bueno**, por eso `inverse=True`: una variación
    negativa se pinta verde y una positiva roja. El signo (+/−) y la flecha de
    st.metric aportan canales NO cromáticos (no se depende solo del color).
    `icon` (emoji opcional) precede a la etiqueta para identificar la métrica de
    un vistazo (canal redundante, no único).
    """
    lbl = f"{icon}  {label}" if icon else label
    with col.container(border=True):
        st.metric(lbl, value, delta=delta,
                  delta_color=("inverse" if inverse else "normal"), help=help)


def tabla(df, *, hide_index=True, height=None, resaltar=None, col_resaltada=None):
    """st.dataframe con formato numérico es-UY consistente (vía pandas Styler).

    Unifica la presentación de TODAS las tablas: enteros con separador de miles
    es-UY ("1.234.567") y floats con 2 decimales es-UY ("0,34"). Sin matplotlib
    (no usa background_gradient): el resaltado opcional se aplica con un color
    plano. `resaltar="max"|"min"` marca la celda extrema de `col_resaltada`.
    Degrada a st.dataframe plano si el Styler fallara.
    """
    try:
        fmt = {}
        for c in df.columns:
            s = df[c]
            if pd.api.types.is_bool_dtype(s) or not pd.api.types.is_numeric_dtype(s):
                continue
            vals = s.dropna()
            entero = pd.api.types.is_integer_dtype(s) or bool((vals % 1 == 0).all())
            if not entero:
                fmt[c] = lambda v: fmt_num(v, 2)
            elif len(vals) and bool(vals.between(1900, 2100).all()):
                fmt[c] = lambda v: str(int(v))      # columnas de año: sin separador de miles
            else:
                fmt[c] = lambda v: fmt_int(v)
        sty = df.style.format(fmt, na_rep="—") if fmt else df.style
        if resaltar in ("max", "min") and col_resaltada in df.columns:
            objetivo = df[col_resaltada].max() if resaltar == "max" else df[col_resaltada].min()

            def _mark(col):
                on = col == objetivo
                return ["background-color:#FCE8E6;color:#9F1D20;font-weight:600" if v else ""
                        for v in on]
            sty = sty.apply(_mark, subset=[col_resaltada])
        # height=None no es válido en streamlit 1.58 (espera int|'stretch'|'content');
        # solo se pasa cuando el llamador fija una altura explícita.
        extra = {"height": height} if height is not None else {}
        st.dataframe(sty, use_container_width=True, hide_index=hide_index, **extra)
    except Exception:
        extra = {"height": height} if height is not None else {}
        st.dataframe(df, use_container_width=True, hide_index=hide_index, **extra)

def estilo(fig, **kw):
    """Plantilla limpia + formato es-UY. Delega en charts.estilizar (fuente única).

    Se mantiene este alias para no tocar las decenas de figuras Plotly que ya
    llamaban `estilo(fig, ...)`; toda la apariencia vive ahora en charts.estilizar.
    """
    return charts.estilizar(fig, **kw)

def leyenda_severidad(sin_dato=False):
    """Leyenda de severidad con muestras de color reales (coincide con la paleta del mapa)."""
    chips = "".join(
        f'<span style="display:inline-block;margin-right:14px;white-space:nowrap">'
        f'<span style="display:inline-block;width:11px;height:11px;background:{color_sev(g)};'
        f'border-radius:2px;margin-right:5px;vertical-align:middle"></span>{etiqueta_sev(g)}</span>'
        for g in GRAVEDADES)
    if sin_dato:
        chips += ('<span style="display:inline-block;white-space:nowrap">'
                  '<span style="display:inline-block;width:11px;height:11px;background:#2E75B6;'
                  'border-radius:2px;margin-right:5px;vertical-align:middle"></span>Sin dato</span>')
    st.markdown("**Leyenda:** " + chips, unsafe_allow_html=True)

# ── Navegación: barra superior horizontal (reemplaza la sidebar st.radio) ────
# Etiqueta corta (navbar) → etiqueta canónica que usan las 11 ramas de más abajo,
# por lo que el dispatch `if pagina == "…"` no cambia.
NAV = {
    "Resumen":     "🏠 Resumen General",
    "Evolución":   "📈 Evolución Temporal",
    "Comparativa": "🌍 Comparativa por País",
    "Gravedad":    "⚠️ Distribución de Gravedad",
    "Tipos":       "🚗 Tipos de Siniestro",
    "Geográfica":  "🗺️ Distribución Geográfica",
    "Clima":       "🌤️ Análisis Climático",
    "COVID-19":    "🦠 Impacto COVID-19",
    "WHO/Alcohol": "🍷 Indicador WHO — Alcohol",
    "MongoDB":     "🗄️ Consulta MongoDB",
    "Calidad":     "✅ Calidad & Cobertura",
}
NAV_ICONS = ["house", "graph-up", "globe-americas", "exclamation-triangle",
             "car-front", "geo-alt", "cloud-rain", "heart-pulse", "cup-straw",
             "database", "check2-circle"]
pagina = NAV[ui.render_navbar(NAV.keys(), icons=NAV_ICONS)]

# Feedback del filtro de país persistente (las páginas comparten key="pais_sel").
if st.session_state.get("pais_sel"):
    st.caption(f"🌎 País (detalle): **{st.session_state['pais_sel']}** · persiste entre secciones")

# ══════════════════════════════════════════════════════════════════════════
# PÁGINA 1 — RESUMEN GENERAL
# ══════════════════════════════════════════════════════════════════════════
if pagina == "🏠 Resumen General":
    header("🚗 Dashboard de Siniestros Viales",
           "Ecosistema de datos híbrido — Uruguay · Brasil · España (2018–2025) · tasas por 100.000 hab.")

    try:
        df = query("""
            SELECT pais, SUM(total) AS total, SUM(fatal) AS fatales,
                   SUM(grave + leve) AS con_victimas, SUM(solo_danos) AS sin_victimas
            FROM proyecto.mv_acc_anio_pais
            GROUP BY pais
        """)
        df = tasa(df, "total",   "siniestros_100k")
        df = tasa(df, "fatales", "fatales_100k")
        df["pct_fatal"]        = (df["fatales"]       / df["total"] * 100).round(2)
        df["pct_con_victimas"] = (df["con_victimas"]  / df["total"] * 100).round(2)
        df["pct_sin_victimas"] = (df["sin_victimas"]  / df["total"] * 100).round(2)

        total_g = int(df["total"].sum())
        fat_g   = int(df["fatales"].sum())
        pct_f   = round(fat_g / total_g * 100, 2)

        # Tendencia interanual sobre el último año comparable entre las 3 fuentes
        # (2024: España cierra en 2024 y 2025 es parcial → se excluye del delta).
        df_yr = query("""
            SELECT anio, SUM(total) AS total, SUM(fatal) AS fatal
            FROM proyecto.mv_acc_anio_pais
            WHERE anio BETWEEN 2018 AND 2024
            GROUP BY anio ORDER BY anio
        """)
        y_last = int(df_yr["anio"].max())
        y_prev = y_last - 1
        r_l = df_yr[df_yr["anio"] == y_last].iloc[0]
        r_p = df_yr[df_yr["anio"] == y_prev].iloc[0]
        t_l, t_p = int(r_l["total"]), int(r_p["total"])
        pf_l = round(r_l["fatal"] / r_l["total"] * 100, 2)
        pf_p = round(r_p["fatal"] / r_p["total"] * 100, 2)

        c1, c2, c3, c4 = st.columns(4, gap="medium")
        kpi(c1, "Total siniestros (2018–2025)", fmt_int(total_g), icon="🚗")
        kpi(c2, "% Fatal (global)", fmt_pct(pct_f, 2), icon="⚠️")
        kpi(c3, f"Siniestros {y_last}", fmt_int(t_l), delta=t_l - t_p, icon="🗓️",
            help=f"Variación vs {y_prev} (verde = baja siniestralidad, rojo = sube)")
        kpi(c4, f"% Fatal {y_last}", fmt_pct(pf_l, 2), delta=round(pf_l - pf_p, 2), icon="📉",
            help=f"Variación en puntos porcentuales vs {y_prev} (verde = baja, rojo = sube)")

        st.divider()
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Tasa de siniestros / 100k hab.")
            st.plotly_chart(charts.barras(
                df.set_index("pais")["siniestros_100k"], height=300,
                y_title="Siniestros / 100.000 hab."), use_container_width=True)
        with c2:
            st.subheader("Tasa de fatales / 100k hab.")
            st.plotly_chart(charts.barras(
                df.set_index("pais")["fatales_100k"], height=300,
                y_title="Fatales / 100.000 hab."), use_container_width=True)

        st.subheader("Distribución % por gravedad y país")
        # 3 columnas → 3 colores (fatal / grave+leve / solo_danos), rotuladas para
        # la leyenda. La paleta es la de severidad central (color-blind safe).
        df_g3 = df.set_index("pais")[["pct_fatal", "pct_con_victimas", "pct_sin_victimas"]].rename(
            columns={"pct_fatal": "Fatal", "pct_con_victimas": "Grave + leve",
                     "pct_sin_victimas": "Solo daños"})
        st.plotly_chart(charts.barras(
            df_g3, color=[COLOR_SEVERIDAD["fatal"], COLOR_SEVERIDAD["grave"], COLOR_SEVERIDAD["solo_danos"]],
            height=320, y_title="% del total del país"), use_container_width=True)

        st.divider()
        st.subheader("Distribución global por gravedad (%)")
        df_grav = query("""
            SELECT gravedad, total FROM (
                SELECT 'fatal'      AS gravedad, SUM(fatal)      AS total FROM proyecto.mv_acc_anio_pais
                UNION ALL SELECT 'grave',      SUM(grave)      FROM proyecto.mv_acc_anio_pais
                UNION ALL SELECT 'leve',       SUM(leve)       FROM proyecto.mv_acc_anio_pais
                UNION ALL SELECT 'solo_danos', SUM(solo_danos) FROM proyecto.mv_acc_anio_pais
            ) g WHERE total > 0 ORDER BY total DESC
        """)
        df_grav["pct"] = (df_grav["total"] / df_grav["total"].sum() * 100).round(1)
        df_grav = df_grav.set_index("gravedad").reindex(
            [g for g in GRAVEDADES if g in set(df_grav["gravedad"])]).reset_index()
        import plotly.graph_objects as go_r
        fig_r = go_r.Figure(go_r.Bar(
            x=[etiqueta_sev(g) for g in df_grav["gravedad"]], y=df_grav["pct"],
            marker_color=colores_sev(df_grav["gravedad"]),
            customdata=df_grav["total"],
            hovertemplate="%{x}<br>%{y:.1f}% · n=%{customdata:,}<extra></extra>"))
        estilo(fig_r, xaxis_title="", yaxis_title="% del total agregado", height=340)
        st.plotly_chart(fig_r, use_container_width=True)
        st.caption("Distribución global agregada — Uruguay + Brasil + España")

        st.subheader("Resumen comparativo")
        tabla(df[["pais","total","pct_fatal","pct_con_victimas","pct_sin_victimas",
                  "siniestros_100k","fatales_100k"]].rename(columns={
            "pais":"País","total":"Total","pct_fatal":"% Fatal",
            "pct_con_victimas":"% grave+leve","pct_sin_victimas":"% solo_danos",
            "siniestros_100k":"Siniestros/100k","fatales_100k":"Fatales/100k"
        }), resaltar="max", col_resaltada="% Fatal")

        st.caption("**Fuente:** UNASEV (UY) · RENAEST (BR) · DGT (ES), 2018–2025. "
                   "**Limitación:** Brasil concentra ~89 % del volumen, por eso la comparación es "
                   "siempre por **tasas/100k hab. y proporciones intra-país**, nunca por volúmenes "
                   "absolutos agregados.")

    except Exception as e:
        st.error("Error cargando datos.")
        st.exception(e)

# ══════════════════════════════════════════════════════════════════════════
# PÁGINA 2 — EVOLUCIÓN TEMPORAL  (sin persona — sin cambios de modelo)
# ══════════════════════════════════════════════════════════════════════════
elif pagina == "📈 Evolución Temporal":
    import plotly.graph_objects as go

    header("📈 Evolución Temporal",
           "Q1 · Q2 · Q5 — tasas anuales por 100.000 hab. y variación interanual")

    try:
        st.markdown("> ❓ **Q1:** ¿Cómo evolucionó la tasa de siniestros por año y país?")
        df_evol = query("""
            SELECT anio, pais, total
            FROM proyecto.mv_acc_anio_pais
            WHERE anio BETWEEN 2018 AND 2025
            ORDER BY anio, pais
        """)
        df_evol["tasa_100k"] = df_evol.apply(
            lambda r: round(r["total"] / POBLACION.get(r["pais"], 1) * 100000, 2), axis=1)

        # Marcador-resumen: tasa /100k del último año comparable (2024) por país, con
        # Δ vs 2023 (inverse: bajar la tasa = verde). Reutiliza df_evol (sin consulta extra).
        st.markdown("**Tasa de siniestros / 100k hab. — último año comparable (2024)**")
        kc = st.columns(len(PAISES), gap="medium")
        for col_ui, p in zip(kc, PAISES):
            sub = df_evol[df_evol["pais"] == p]
            a = sub.loc[sub["anio"] == 2024, "tasa_100k"]
            b = sub.loc[sub["anio"] == 2023, "tasa_100k"]
            if not a.empty:
                delta = round(float(a.iloc[0]) - float(b.iloc[0]), 1) if not b.empty else None
                kpi(col_ui, p, f"{fmt_num(float(a.iloc[0]), 1)} /100k", delta=delta, icon="📈",
                    help="Δ vs 2023 en puntos /100k (verde = baja la tasa)")
        st.divider()

        piv_evol = df_evol.pivot(index="anio", columns="pais", values="tasa_100k")
        fig_q1 = go.Figure()
        for p in [c for c in PAISES if c in piv_evol.columns]:
            fig_q1.add_trace(go.Scatter(
                x=piv_evol.index, y=piv_evol[p], mode="lines+markers", name=p,
                line=dict(color=COLOR_PAIS.get(p, "#999"), width=2.5), marker=dict(size=7)))
        fig_q1.add_vline(x=2020, line_dash="dash", line_color="#9F1D20", line_width=1.5,
                         annotation_text="COVID-19", annotation_position="top",
                         annotation_font_size=11)
        estilo(fig_q1, xaxis_title="Año", yaxis_title="Siniestros / 100.000 hab.",
               legend_title="País", height=400, xaxis=dict(tickmode="linear", dtick=1))
        st.plotly_chart(fig_q1, use_container_width=True)
        st.caption(NOTA_COVID + "  \n" + NOTA_RENAEST_2018)
        st.divider()

        st.markdown("> ❓ **Q2:** Variación interanual (%) de siniestralidad global")
        df_var = query("""
            SELECT anio, total,
                   ROUND((total - LAG(total) OVER (ORDER BY anio))*100.0
                         / NULLIF(LAG(total) OVER (ORDER BY anio), 0), 2) AS variacion_pct
            FROM (
                SELECT anio, SUM(total) AS total
                FROM proyecto.mv_acc_anio_pais
                WHERE anio BETWEEN 2018 AND 2025
                GROUP BY anio
            ) t ORDER BY anio
        """)
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Variación interanual (%)")
            st.plotly_chart(charts.barras(
                df_var.dropna().set_index("anio")["variacion_pct"], color=charts.PRIMARY,
                height=320, x_title="Año", y_title="Variación interanual (%)"),
                use_container_width=True)
        with c2:
            tabla(df_var.rename(columns={"anio":"Año","total":"Total","variacion_pct":"Variación %"}))
        st.divider()

        st.markdown("> ❓ **Q5:** Estacionalidad mensual (% del total anual por país)")
        df_mes = query("""
            SELECT mes, pais, total
            FROM proyecto.mv_acc_mes_pais
            ORDER BY mes, pais
        """)
        totales_p = df_mes.groupby("pais")["total"].sum().to_dict()
        df_mes["pct"] = df_mes.apply(
            lambda r: round(r["total"] / totales_p[r["pais"]] * 100, 2), axis=1)
        piv_mes = df_mes.pivot(index="mes", columns="pais", values="pct")
        MESES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
        fig_q5 = go.Figure()
        for p in [c for c in PAISES if c in piv_mes.columns]:
            fig_q5.add_trace(go.Scatter(
                x=piv_mes.index, y=piv_mes[p], mode="lines+markers", name=p,
                line=dict(color=COLOR_PAIS.get(p, "#999"), width=2.5), marker=dict(size=6)))
        estilo(fig_q5, xaxis_title="Mes", yaxis_title="% del total anual del país",
               legend_title="País", height=360,
               xaxis=dict(tickmode="array", tickvals=list(range(1, 13)), ticktext=MESES))
        st.plotly_chart(fig_q5, use_container_width=True)
        st.caption("Eje Y: % del total anual de siniestros por país (estacionalidad intra-país).")
        st.info("El **índice de disrupción COVID-19** (baseline 2018–2019) se analiza "
                "en detalle en la página **🦠 Impacto COVID-19**.")

    except Exception as e:
        st.error("Error cargando datos.")
        st.exception(e)

# ══════════════════════════════════════════════════════════════════════════
# PÁGINA 3 — COMPARATIVA POR PAÍS
# ══════════════════════════════════════════════════════════════════════════
elif pagina == "🌍 Comparativa por País":
    header("🌍 Comparativa entre Países",
           "Q2 · Q4 — métricas normalizadas por población (tasas por 100.000 hab.)")

    try:
        st.markdown("> ❓ **Q4:** ¿Qué país tiene mayor tasa de mortalidad vial?")
        df_mort = query("""
            SELECT pais, SUM(total) AS total, SUM(fatal) AS fatales,
                   ROUND(SUM(fatal)*100.0/NULLIF(SUM(total),0),3) AS pct_fatal
            FROM proyecto.mv_acc_anio_pais
            GROUP BY pais ORDER BY pct_fatal DESC
        """)
        df_mort = tasa(df_mort, "fatales", "fatales_100k")
        df_mort = tasa(df_mort, "total",   "siniestros_100k")

        # Marcador-resumen: % fatal por país (uno por columna, paralelo a COVID/WHO).
        kc = st.columns(len(PAISES), gap="medium")
        for col_ui, p in zip(kc, PAISES):
            fila = df_mort[df_mort["pais"] == p]
            if not fila.empty:
                r = fila.iloc[0]
                kpi(col_ui, p, fmt_pct(r["pct_fatal"], 2), icon="⚠️",
                    help=f"{fmt_num(r['fatales_100k'], 2)} fatales/100k · "
                         f"{fmt_int(r['total'])} siniestros (2018–2025)")
        st.divider()

        c1, c2 = st.columns(2)
        with c1:
            st.subheader("% Fatal por país")
            st.plotly_chart(charts.barras(
                df_mort.set_index("pais")["pct_fatal"], height=300,
                y_title="% Fatal"), use_container_width=True)
        with c2:
            st.subheader("Fatales / 100k hab.")
            st.plotly_chart(charts.barras(
                df_mort.set_index("pais")["fatales_100k"], height=300,
                y_title="Fatales / 100.000 hab."), use_container_width=True)
        tabla(df_mort[["pais","total","fatales","pct_fatal","siniestros_100k","fatales_100k"]].rename(columns={
            "pais":"País","total":"Total","fatales":"Fatales",
            "pct_fatal":"% Fatal","siniestros_100k":"Siniestros/100k","fatales_100k":"Fatales/100k"
        }), resaltar="max", col_resaltada="% Fatal")
        st.divider()

        st.markdown("> ❓ **Q2:** Evolución del % de fatales por año y país")
        df_anual = query("""
            SELECT anio, pais,
                   ROUND(fatal*100.0/NULLIF(total,0),3) AS pct_fatal
            FROM proyecto.mv_acc_anio_pais
            WHERE anio BETWEEN 2018 AND 2025
            ORDER BY anio, pais
        """)
        st.plotly_chart(charts.lineas(
            df_anual.pivot(index="anio", columns="pais", values="pct_fatal").fillna(0),
            height=360, x_title="Año", y_title="% fatales / total",
            xaxis=dict(tickmode="linear", dtick=1)), use_container_width=True)
        st.caption("Eje Y: % fatales / total por año y país")
        st.divider()

        st.markdown("> ❓ **Q4:** ¿En qué día de la semana ocurre el mayor % de siniestros?")
        df_dia = query("""
            SELECT dia, num_dia, pais, total
            FROM proyecto.mv_acc_dia_pais
            ORDER BY num_dia, pais
        """)
        totales_p = df_dia.groupby("pais")["total"].sum().to_dict()
        df_dia["pct"] = df_dia.apply(
            lambda r: round(r["total"] / totales_p[r["pais"]] * 100, 2), axis=1)
        st.plotly_chart(charts.barras(
            df_dia.pivot_table(index="dia", columns="pais", values="pct", aggfunc="sum").fillna(0),
            height=360, x_title="Día de la semana", y_title="% del total del país"),
            use_container_width=True)
        st.caption("Eje Y: % del total de siniestros por país")

    except Exception as e:
        st.error("Error cargando datos.")
        st.exception(e)

# ══════════════════════════════════════════════════════════════════════════
# PÁGINA 4 — DISTRIBUCIÓN DE GRAVEDAD
# ══════════════════════════════════════════════════════════════════════════
elif pagina == "⚠️ Distribución de Gravedad":
    import plotly.graph_objects as go

    header("⚠️ Distribución de Gravedad",
           "Q2 · Q3 · Q4 — composición homologada {Fatal · Herido grave · Herido leve · Sin víctimas}")

    try:
        st.markdown("> ❓ **Q2:** Distribución de gravedad por país (100 % normalizado intra-país)")
        df_res = query("""
            WITH p AS (
                SELECT pais, SUM(fatal) AS fatal, SUM(grave) AS grave,
                       SUM(leve) AS leve, SUM(solo_danos) AS solo_danos
                FROM proyecto.mv_acc_anio_pais GROUP BY pais
            )
            SELECT pais, gravedad, total FROM (
                SELECT pais, 'fatal'      AS gravedad, fatal      AS total FROM p
                UNION ALL SELECT pais, 'grave',      grave      FROM p
                UNION ALL SELECT pais, 'leve',       leve       FROM p
                UNION ALL SELECT pais, 'solo_danos', solo_danos FROM p
            ) x WHERE total > 0 ORDER BY pais, total DESC
        """)
        totales = df_res.groupby("pais")["total"].sum().to_dict()
        df_res["pct"] = df_res.apply(
            lambda r: round(r["total"] / totales[r["pais"]] * 100, 2), axis=1)
        df_piv = df_res.pivot_table(index="pais", columns="gravedad", values="pct", aggfunc="sum").fillna(0)
        cols_ord = [c for c in GRAVEDADES if c in df_piv.columns]
        paises_ord = [p for p in PAISES if p in df_piv.index]

        # Marcador-resumen: % fatal por país (headline antes del desglose detallado).
        kc = st.columns(len(paises_ord), gap="medium")
        for col_ui, p in zip(kc, paises_ord):
            pf = float(df_piv.loc[p, "fatal"]) if "fatal" in df_piv.columns else 0.0
            kpi(col_ui, p, fmt_pct(pf, 2), icon="⚠️",
                help=f"{fmt_int(totales[p])} siniestros con gravedad informada")
        st.divider()

        # Barras 100 % normalizadas intra-país (apiladas por proporción, nunca absolutas).
        fig_grav = go.Figure()
        for g in cols_ord:
            fig_grav.add_trace(go.Bar(
                y=paises_ord, x=[df_piv.loc[p, g] for p in paises_ord], orientation="h",
                name=etiqueta_sev(g), marker_color=color_sev(g),
                hovertemplate="%{y} · " + etiqueta_sev(g) + ": %{x:.2f}%<extra></extra>"))
        estilo(fig_grav, barmode="stack", height=320,
               xaxis_title="% intra-país (suma 100 %)", yaxis_title="",
               legend_title="Gravedad")
        st.plotly_chart(fig_grav, use_container_width=True)
        tabla(df_piv[cols_ord].rename(columns=ETIQUETA_SEVERIDAD).round(2), hide_index=False)
        st.caption(NOTA_BRASIL)
        st.caption(NOTA_ESPANA)

        # Donas de composición intra-país (complementan la barra 100% apilada):
        # más legibles como parte-todo. Cada dona normaliza sobre su propio país,
        # así los ceros estructurales (BR sin 'grave', ES sin 'solo daños') quedan
        # a la vista en lugar de ocultarse en una agregación entre países.
        st.markdown("**Composición de gravedad por país (dona)**")
        cols_d = st.columns(len(paises_ord))
        cmap_sev = {etiqueta_sev(g): color_sev(g) for g in GRAVEDADES}
        for col_ui, p in zip(cols_d, paises_ord):
            dp = df_res[df_res["pais"] == p]
            serie = pd.Series({etiqueta_sev(g): t for g, t in zip(dp["gravedad"], dp["total"])})
            serie = serie.reindex([etiqueta_sev(g) for g in GRAVEDADES
                                   if etiqueta_sev(g) in serie.index])
            with col_ui:
                st.plotly_chart(charts.dona(serie, colors=cmap_sev, height=300, title=p),
                                use_container_width=True)
        st.divider()

        st.markdown("> ❓ **Q3:** % de siniestros fatales por franja horaria")
        df_hora = query("""
            SELECT pais, hora, total,
                   ROUND(fatal*100.0/NULLIF(total,0),2) AS pct_fatal
            FROM proyecto.mv_acc_hora_pais
            ORDER BY pais, hora
        """)
        pais_sel = st.selectbox("País", PAISES, key="pais_sel")
        df_h = df_hora[df_hora["pais"] == pais_sel].copy()
        df_h["pct_total"] = (df_h["total"] / df_h["total"].sum() * 100).round(2)
        # Hora como categórica ordinal 0–23: se reindexan las 24 horas (rellena
        # huecos con 0) y se rotula "00".."23" para forzar el orden en el eje X.
        df_h["hora"] = df_h["hora"].astype(int)
        df_h = df_h.set_index("hora").reindex(range(24)).fillna(0)
        df_h.index = [f"{h:02d}" for h in range(24)]
        df_h.index.name = "hora"
        c1, c2 = st.columns(2)
        with c1:
            st.subheader(f"% siniestros por hora — {pais_sel}")
            st.plotly_chart(charts.barras(
                df_h["pct_total"], color=charts.PRIMARY, height=320,
                x_title="Hora", y_title="% del total"), use_container_width=True)
        with c2:
            st.subheader(f"% fatales por hora — {pais_sel}")
            st.plotly_chart(charts.barras(
                df_h["pct_fatal"], color=COLOR_SEVERIDAD["fatal"], height=320,
                x_title="Hora", y_title="% fatales"), use_container_width=True)

        # Radar comparativo por franja horaria (los 3 países a la vez). Agrupa las
        # 24 horas en 4 franjas y normaliza intra-país (% de cada franja sobre el
        # total del país) → ejes comparables pese a los volúmenes dispares.
        FRANJAS = [("Madrugada", range(0, 6)), ("Mañana", range(6, 12)),
                   ("Tarde", range(12, 18)), ("Noche", range(18, 24))]

        def _franja(h):
            for nombre, rng in FRANJAS:
                if int(h) in rng:
                    return nombre
            return None

        dfh = df_hora.copy()
        dfh["franja"] = dfh["hora"].astype(int).apply(_franja)
        agg = dfh.groupby(["pais", "franja"])["total"].sum().reset_index()
        agg["pct"] = (agg["total"] / agg.groupby("pais")["total"].transform("sum") * 100).round(2)
        piv_fr = (agg.pivot_table(index="franja", columns="pais", values="pct", aggfunc="sum")
                  .reindex([f[0] for f in FRANJAS]).fillna(0))
        piv_fr = piv_fr[[p for p in PAISES if p in piv_fr.columns]]
        st.markdown("**Perfil por franja horaria y país (radar)**")
        st.plotly_chart(charts.radar(piv_fr, ticksuffix="%", height=400),
                        use_container_width=True)
        st.caption("% de siniestros del país en cada franja (normalizado intra-país). "
                   "Brasil: 97,5 % de los registros con hora informada; el resto se excluye.")
        st.divider()

        st.markdown("> ❓ **Q4:** % de siniestros y fatales por día de semana")
        df_dia = query("""
            SELECT pais, dia, num_dia, total,
                   ROUND(fatal*100.0/NULLIF(total,0),2) AS pct_fatal
            FROM proyecto.mv_acc_dia_pais
            ORDER BY pais, num_dia
        """)
        totales_d = df_dia.groupby("pais")["total"].sum().to_dict()
        df_dia["pct_total"] = df_dia.apply(
            lambda r: round(r["total"] / totales_d[r["pais"]] * 100, 2), axis=1)
        # Orden de días lunes→domingo (por num_dia) y orden de países para la paleta.
        dias_ord = df_dia.sort_values("num_dia")["dia"].drop_duplicates().tolist()

        def _pivot_dia(valor, aggfunc):
            piv = (df_dia.pivot_table(index="dia", columns="pais", values=valor, aggfunc=aggfunc)
                   .reindex(dias_ord).fillna(0))
            cols = [p for p in PAISES if p in piv.columns]
            return piv[cols], [COLOR_PAIS[p] for p in cols]

        c1, c2 = st.columns(2)
        with c1:
            st.subheader("% siniestros por día y país")
            piv_t, col_t = _pivot_dia("pct_total", "sum")
            st.plotly_chart(charts.barras(piv_t, color=col_t, height=340,
                x_title="Día de la semana", y_title="% del total del país"),
                use_container_width=True)
        with c2:
            st.subheader("% fatales por día y país")
            piv_f, col_f = _pivot_dia("pct_fatal", "mean")
            st.plotly_chart(charts.barras(piv_f, color=col_f, height=340,
                x_title="Día de la semana", y_title="% fatales"),
                use_container_width=True)

        # Radar del perfil semanal: cada eje un día, cada polígono un país,
        # normalizado a % intra-país (suma 100 % en los 7 días). Hace visible la
        # "forma" de la semana (p. ej. concentración en fin de semana) de forma
        # comparable entre países pese a sus volúmenes muy distintos.
        st.markdown("**Perfil semanal por país (radar) — % de siniestros del país por día**")
        st.plotly_chart(charts.radar(piv_t, ticksuffix="%", height=420),
                        use_container_width=True)

    except Exception as e:
        st.error("Error cargando datos.")
        st.exception(e)

# ══════════════════════════════════════════════════════════════════════════
# PÁGINA — TIPOS DE SINIESTRO  (Q7)
# ══════════════════════════════════════════════════════════════════════════
elif pagina == "🚗 Tipos de Siniestro":
    import plotly.graph_objects as go

    header("🚗 Tipos de Siniestro Predominantes",
           "Q7 — prevalencia tipológica: % sobre el total de siniestros con tipo informado, por país")

    # Catálogo DGT (España): el ETL conserva el código numérico original (sin homologar).
    DGT_TIPOS = {
        1: "Colisión frontal", 2: "Colisión fronto-lateral", 3: "Colisión lateral",
        4: "Alcance trasero", 5: "Colisión múltiple", 6: "Atropello de persona",
        7: "Salida de vía", 9: "Vuelco", 10: "Choque c/ obstáculo en calzada",
        12: "Caída moto/bici", 15: "Otro", 16: "Choque con animal",
        18: "Incendio", 19: "Atropello de peatón", 20: "Sin determinar",
    }

    def etiqueta_tipo(pais, tipo):
        if pais == "España":
            try:
                cod = int(float(tipo))
                return f"{cod} — {DGT_TIPOS.get(cod, 'Código DGT ' + str(cod))}"
            except (ValueError, TypeError):
                return str(tipo)
        return str(tipo).strip()

    try:
        with st.spinner("Agregando tipos de siniestro…"):
            df_tipo = query("""
                SELECT pais, tipo_accidente, total,
                       ROUND(fatal*100.0/NULLIF(total,0),2) AS pct_fatal
                FROM proyecto.mv_acc_tipo_pais
            """)

        c1, c2 = st.columns([1, 3])
        with c1:
            pais_t = st.selectbox("País", PAISES, key="pais_sel")
            top_n  = st.slider("Top N", 5, 15, 8, key="topn_tipo_q7")

        d = df_tipo[df_tipo["pais"] == pais_t].copy()
        if d.empty:
            st.info("Sin datos de tipo para el país seleccionado.")
        else:
            tot = d["total"].sum()
            d["pct"] = (d["total"] / tot * 100).round(2)
            d["etiqueta"] = d["tipo_accidente"].apply(lambda t: etiqueta_tipo(pais_t, t))
            d = d.sort_values("total", ascending=False).head(top_n)

            with c1:
                with st.container(border=True):
                    st.metric("Tipos distintos", fmt_int(df_tipo[df_tipo['pais'] == pais_t].shape[0]))
                with st.container(border=True):
                    st.metric("Más frecuente", d.iloc[0]["etiqueta"][:26], fmt_pct(d.iloc[0]['pct'], 2))

            with c2:
                dd = d.sort_values("total")  # asc → la barra mayor queda arriba
                fig = go.Figure(go.Bar(
                    x=dd["pct"], y=dd["etiqueta"], orientation="h",
                    marker_color=COLOR_PAIS.get(pais_t, "#2E75B6"),
                    customdata=dd[["total", "pct_fatal"]].values,
                    hovertemplate="%{y}<br>%{x:.2f}% del total<br>"
                                  "n=%{customdata[0]:,}<br>%{customdata[1]:.2f}% fatal<extra></extra>",
                ))
                estilo(fig, title=f"Top {top_n} tipos — {pais_t}",
                       xaxis_title="% del total de siniestros con tipo", yaxis_title="", height=440)
                st.plotly_chart(fig, use_container_width=True)

                # Dona de composición tipológica (top-6 + 'otros'): parte-todo
                # intra-país. La barra ordena y compara; la dona muestra qué
                # fracción del total concentra cada tipo (y cuánto queda en la cola).
                full = df_tipo[df_tipo["pais"] == pais_t].copy()
                full["etiqueta"] = full["tipo_accidente"].apply(lambda t: etiqueta_tipo(pais_t, t))
                full = full.sort_values("total", ascending=False)
                serie_t = pd.Series({r["etiqueta"]: r["total"] for _, r in full.head(6).iterrows()})
                otros = int(full["total"].iloc[6:].sum())
                if otros > 0:
                    serie_t["Otros"] = otros
                st.plotly_chart(charts.dona(serie_t, height=380, legend_bottom=False,
                    title=f"Composición tipológica — {pais_t}"), use_container_width=True)

            tabla(d[["etiqueta", "total", "pct", "pct_fatal"]].rename(columns={
                "etiqueta": "Tipo", "total": "Total", "pct": "% del total", "pct_fatal": "% fatal"
            }))

        # Fuente + limitaciones (rúbrica D5)
        st.caption("**Fuente:** UNASEV (UY) · RENAEST (BR) · DGT (ES) — total de siniestros con tipo informado.")
        if pais_t == "Brasil":
            st.warning("**Limitación BR:** 'DESCONHECIDO' + 'NAO INFORMADO' suman ≈31 % de los "
                       "registros sin clasificar — la mayor limitación de calidad en la tipología.")
        elif pais_t == "España":
            st.warning("**Limitación ES:** `tipo_accidente` conserva el **código numérico DGT** "
                       "original (decodificado arriba); no se homologó con UY/BR en el ETL.")
        else:
            st.info("**Nota UY:** 'Caída' refiere principalmente a motociclistas "
                    "(nomenclatura UNASEV). Los rótulos se cargan en UTF-8 (acentos correctos).")
        st.info("**Limitación de comparabilidad:** los vocabularios de tipo de las tres fuentes no "
                "están homologados entre sí; la comparación directa entre países requiere una tabla "
                "de mapeo, fuera del alcance de esta entrega (§4.3.7).")

    except Exception as e:
        st.error("Error cargando tipos de siniestro.")
        st.exception(e)

# ══════════════════════════════════════════════════════════════════════════
# PÁGINA 5 — DISTRIBUCIÓN GEOGRÁFICA
# ══════════════════════════════════════════════════════════════════════════
elif pagina == "🗺️ Distribución Geográfica":
    header("🗺️ Distribución Geográfica",
           "Q6 — top regiones, mapa de calor por área y mapa de puntos por gravedad")

    try:
        import pydeck as pdk

        col1, col2 = st.columns([2, 1])
        with col1:
            pais_geo = st.selectbox("País", PAISES, key="pais_sel")
        with col2:
            anio_geo = st.selectbox("Año", list(range(2025, 2017, -1)),
                                    help="Solo aplica al mapa de puntos; el mapa de "
                                         "calor agrega toda la serie 2018–2025.")

        df_region = query("""
            SELECT region, total, fatal AS fatales,
                   ROUND(total*100.0 / SUM(total) OVER(), 2) AS pct_total,
                   ROUND(fatal*100.0 / NULLIF(total,0), 2)   AS pct_fatal
            FROM proyecto.mv_acc_region_pais
            WHERE pais = :pais
            ORDER BY total DESC LIMIT 20
        """, params={"pais": pais_geo})

        # KPIs de país (toda la serie): dan contexto a las barras y los mapas.
        df_pais = query("""
            SELECT COUNT(*) AS regiones, SUM(total) AS total, SUM(fatal) AS fatales
            FROM proyecto.mv_acc_region_pais WHERE pais = :pais
        """, params={"pais": pais_geo})
        if not df_pais.empty and df_pais.loc[0, "total"]:
            r = df_pais.iloc[0]
            tot_p, fat_p, n_reg = int(r["total"]), int(r["fatales"]), int(r["regiones"])
            top = df_region.iloc[0]
            etq_reg = {"Uruguay": "Departamentos", "Brasil": "Macro-regiones",
                       "España": "Provincias"}.get(pais_geo, "Regiones")
            k1, k2, k3, k4 = st.columns(4, gap="medium")
            kpi(k1, f"Siniestros · {pais_geo}", fmt_int(tot_p), icon="🚗")
            kpi(k2, "% Fatal", fmt_pct(fat_p / tot_p * 100, 2), icon="⚠️")
            kpi(k3, etq_reg, fmt_int(n_reg), icon="🗺️")
            kpi(k4, "Región líder", str(top["region"]).strip().title(), icon="📍",
                help=f"{fmt_pct(top['pct_total'], 1)} del total del país")

        st.divider()
        st.markdown("> ❓ **Q6:** Top regiones con más siniestros fatales")
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("% del total de siniestros")
            st.plotly_chart(charts.barras(
                df_region.set_index("region")["pct_total"].sort_values(),
                color=charts.PRIMARY, horizontal=True, height=460,
                x_title="Región", y_title="% del total"), use_container_width=True)
        with c2:
            st.subheader("% fatal por región")
            st.plotly_chart(charts.barras(
                df_region.set_index("region")["pct_fatal"].sort_values(),
                color=COLOR_SEVERIDAD["fatal"], horizontal=True, height=460,
                x_title="Región", y_title="% Fatal"), use_container_width=True)
        tabla(df_region.rename(columns={
            "region":"Región","total":"Total","fatales":"Fatales",
            "pct_total":"% del total","pct_fatal":"% Fatal"
        }), resaltar="max", col_resaltada="% Fatal")

        st.divider()
        st.subheader("🗺️ Mapa de distribución")

        if pais_geo == "España":
            # España deriva la ubicación de centroides de provincia (sin coordenadas a
            # nivel de evento) → solo dispone de MAPA DE CALOR por provincia (choropleth):
            # cada provincia se pinta según su volumen. Match por código INE (cod_prov).
            st.caption("España deriva la ubicación de **centroides de provincia** (sin "
                       "coordenadas a nivel de evento), por eso solo dispone de **mapa de "
                       "calor** por provincia.")
            df_es = query("""
                SELECT region, total, fatal AS fatales
                FROM proyecto.mv_acc_region_pais WHERE pais = 'España'
            """)
            if df_es.empty:
                st.info("Sin datos de provincias de España.")
            else:
                df_es["cod"] = df_es["region"].map(REGION_A_COD_INE)
                df_es["pct_fatal"] = (df_es["fatales"] / df_es["total"] * 100).round(2)
                sin_cod = df_es[df_es["cod"].isna()]["region"].tolist()
                df_es = df_es.dropna(subset=["cod"])
                st.plotly_chart(coropleta(
                    df_es, geojson_espana(), locations="cod",
                    featureidkey="properties.cod_prov", hover_name="region",
                    color_scale=ESCALA_MAPA_PAIS["España"],
                    hover_data={"cod": False, "total": ":,", "fatales": ":,",
                                "pct_fatal": ":.2f"}), use_container_width=True)
                st.caption(f"Mapa de calor por provincia — {fmt_int(int(df_es['total'].sum()))} "
                           f"siniestros de España (2018–2024). Color = volumen en "
                           f"**escala logarítmica** (más intenso = más siniestros).")
                if sin_cod:
                    st.caption("⚠️ Provincias sin mapear al GeoJSON: " + ", ".join(sin_cod))
        else:
            # Uruguay y Brasil SÍ tienen coordenadas a nivel de evento → switch entre
            # mapa de calor (choropleth por área) y mapa de puntos (coordenadas exactas
            # coloreadas por gravedad). El switch usa st.radio (estilizado como pills por
            # el CSS global) — disponible en streamlit 1.35 (a diferencia de
            # st.segmented_control). Por defecto el mapa de calor: más liviano y legible.
            modo = st.radio(
                "Tipo de mapa",
                ["🔥 Mapa de calor (por región)", "📍 Puntos (coordenadas exactas)"],
                horizontal=True, key="geo_modo_mapa", label_visibility="collapsed")

            if modo.startswith("🔥") and pais_geo == "Uruguay":
                gj, idx = geojson_uruguay()
                d = df_region.copy()
                d["match"] = d["region"].map(lambda x: idx.get(fold_nombre(x)))
                sin = d[d["match"].isna()]["region"].tolist()
                d = d.dropna(subset=["match"]).copy()
                d["region"] = d["region"].str.strip().str.title()
                st.plotly_chart(coropleta(
                    d, gj, locations="match", featureidkey="properties.shapeName",
                    hover_name="region", color_scale=ESCALA_MAPA_PAIS["Uruguay"],
                    hover_data={"match": False, "total": ":,", "fatales": ":,",
                                "pct_fatal": ":.2f"}), use_container_width=True)
                st.caption(f"Mapa de calor por **departamento** — "
                           f"{fmt_int(int(d['total'].sum()))} siniestros de Uruguay "
                           f"(2018–2025). Color = volumen en **escala logarítmica** "
                           f"(más intenso = más siniestros; Montevideo concentra el volumen).")
                if sin:
                    st.caption("⚠️ Departamentos sin mapear: " + ", ".join(sin))

            elif modo.startswith("🔥"):   # Brasil
                gj = geojson_brasil()
                reg = df_region.set_index("region")   # 5 macro-regiones del DW
                filas = [{"sigla": f["properties"]["sigla"], "estado": f["properties"]["name"],
                          "region": BR_UF_A_REGION.get(f["properties"]["sigla"]),
                          "total": int(reg.loc[BR_UF_A_REGION[f["properties"]["sigla"]], "total"]),
                          "fatales": int(reg.loc[BR_UF_A_REGION[f["properties"]["sigla"]], "fatales"]),
                          "pct_fatal": float(reg.loc[BR_UF_A_REGION[f["properties"]["sigla"]], "pct_fatal"])}
                         for f in gj["features"]
                         if BR_UF_A_REGION.get(f["properties"]["sigla"]) in reg.index]
                d = pd.DataFrame(filas)
                st.plotly_chart(coropleta(
                    d, gj, locations="sigla", featureidkey="properties.sigla",
                    hover_name="estado", color_scale=ESCALA_MAPA_PAIS["Brasil"],
                    hover_data={"sigla": False, "region": True, "total": ":,",
                                "fatales": ":,", "pct_fatal": ":.2f"},
                    titulo_barra="Siniestros (región)"), use_container_width=True)
                st.caption("Mapa de calor de Brasil **agregado a nivel macro-región**: "
                           "RENAEST guarda la UF colapsada en las 5 regiones del IBGE, así "
                           "que cada estado se pinta con el total de **su** macro-región "
                           "(Sudeste · Sul · Centro-Oeste · Nordeste · Norte). El detalle "
                           "por estado no está en el almacén (limitación del ETL).")

            else:
                # Mapa de puntos por gravedad (coordenadas exactas) — UY 100 % y BR ~34 %.
                COLOR_MAP = {g: color_sev_rgb(g, 200) for g in GRAVEDADES}
                df_mapa = query("""
                    SELECT a.latitud, a.longitud, a.gravedad, a.fecha::text AS fecha
                    FROM proyecto.accidentes a
                    JOIN proyecto.ubicacion u ON a.id_ubicacion = u.id_ubicacion
                    WHERE u.pais = :pais
                      AND EXTRACT(YEAR FROM a.fecha) = :anio
                      AND a.latitud IS NOT NULL AND a.longitud IS NOT NULL
                      AND a.latitud BETWEEN -60 AND 60
                      AND a.longitud BETWEEN -90 AND 20
                    LIMIT 50000
                """, params={"pais": pais_geo, "anio": anio_geo})

                if df_mapa.empty:
                    st.info(f"**Sin registros georreferenciados para {pais_geo} en {anio_geo}.** "
                            "Probá otro año o cambiá al mapa de calor (toda la serie).")
                else:
                    st.caption(f"Mostrando {fmt_int(len(df_mapa))} siniestros de {pais_geo} en "
                               f"{anio_geo} (muestra de hasta 50.000 puntos).")
                    df_mapa["gravedad"] = df_mapa["gravedad"].fillna("s/d")
                    df_mapa["grav_lbl"] = df_mapa["gravedad"].apply(
                        lambda v: etiqueta_sev(v) if v != "s/d" else "Sin dato")
                    df_mapa["color"] = df_mapa["gravedad"].apply(
                        lambda v: COLOR_MAP.get(v, [46, 117, 182, 180]))
                    df_mapa = df_mapa.rename(columns={"latitud": "lat", "longitud": "lon"})

                    centros = {
                        "Uruguay": {"lat": -32.5, "lon": -56.0, "zoom": 6},
                        "Brasil":  {"lat": -15.0, "lon": -50.0, "zoom": 4},
                    }
                    centro = centros.get(pais_geo, centros["Uruguay"])
                    st.pydeck_chart(pdk.Deck(
                        layers=[pdk.Layer("ScatterplotLayer", data=df_mapa,
                            get_position="[lon, lat]", get_color="color",
                            get_radius=3000, pickable=True, opacity=0.8)],
                        initial_view_state=pdk.ViewState(
                            latitude=centro["lat"], longitude=centro["lon"],
                            zoom=centro["zoom"], pitch=0),
                        tooltip={"text": "Gravedad: {grav_lbl}\nFecha: {fecha}"},
                        map_style="road",
                    ))
                    leyenda_severidad(sin_dato=True)
        st.caption(FUENTE + "  \n" + NOTA_GEO)

    except Exception as e:
        st.error("Error cargando mapa.")
        st.exception(e)

# ══════════════════════════════════════════════════════════════════════════
# PÁGINA 6 — ANÁLISIS CLIMÁTICO
# ══════════════════════════════════════════════════════════════════════════
elif pagina == "🌤️ Análisis Climático":
    import plotly.graph_objects as go

    header("🌤️ Análisis Climático y Siniestralidad",
           "Q8 — ¿la lluvia incrementa el % de siniestros fatales? (enriquecimiento Open-Meteo)")

    try:
        df_cob = query("""
            SELECT pais, SUM(total) AS total, SUM(con_clima) AS con_clima,
                   ROUND(SUM(con_clima)*100.0/NULLIF(SUM(total),0),1) AS pct
            FROM proyecto.mv_acc_anio_pais
            GROUP BY pais ORDER BY pais
        """)
        st.subheader("Cobertura de datos climáticos")
        tabla(df_cob.rename(columns={
            "pais":"País","total":"Total","con_clima":"Con clima","pct":"Cobertura %"
        }))
        st.divider()

        st.markdown("> ❓ **Q8:** ¿La lluvia incrementa el % de fatales?")
        df_lluvia = query("""
            SELECT pais, condicion, total,
                   ROUND(fatal*100.0/NULLIF(total,0),2) AS pct_fatal
            FROM proyecto.mv_acc_clima_lluvia
            ORDER BY pais, condicion
        """)
        st.subheader("% Fatal: con lluvia vs. sin lluvia (con N de cada grupo)")
        piv_pf = df_lluvia.pivot_table(index="pais", columns="condicion", values="pct_fatal").reindex(PAISES)
        piv_n  = df_lluvia.pivot_table(index="pais", columns="condicion", values="total").reindex(PAISES)
        fig_ll = go.Figure()
        for cond in list(piv_pf.columns):
            col = "#0072B2" if "lluv" in str(cond).lower() else "#7F7F7F"
            fig_ll.add_trace(go.Bar(
                name=str(cond).capitalize(), x=PAISES, y=piv_pf[cond],
                marker_color=col,
                text=[("n=" + fmt_int(piv_n.loc[p, cond])) if pd.notna(piv_n.loc[p, cond]) else ""
                      for p in PAISES],
                textposition="outside",
                hovertemplate="%{x} · " + str(cond) + "<br>%{y:.2f}% fatal<extra></extra>"))
        estilo(fig_ll, barmode="group", xaxis_title="", yaxis_title="% siniestros fatales",
               legend_title="Condición", height=380)
        st.plotly_chart(fig_ll, use_container_width=True)
        tabla(df_lluvia.assign(condicion=df_lluvia["condicion"].str.capitalize()).rename(columns={
            "pais": "País", "condicion": "Condición", "total": "N", "pct_fatal": "% fatal"}))
        st.caption("El **N** de cada grupo contextualiza el % fatal: la cobertura climática es "
                   "parcial (ver tabla superior), por lo que algunos grupos tienen muestras chicas.")
        st.divider()

        pais_clima = st.selectbox("País", PAISES, key="pais_sel")
        df_est = query("""
            SELECT estado_climatico, total,
                   ROUND(total*100.0/SUM(total) OVER(),2) AS pct_siniestros,
                   ROUND(fatal*100.0/NULLIF(total,0),2)   AS pct_fatal
            FROM proyecto.mv_acc_clima_estado
            WHERE pais = :pais
            ORDER BY total DESC LIMIT 10
        """, params={"pais": pais_clima})
        c1, c2 = st.columns(2)
        with c1:
            st.subheader(f"% siniestros por clima — {pais_clima}")
            st.plotly_chart(charts.barras(
                df_est.set_index("estado_climatico")["pct_siniestros"].sort_values(),
                color=charts.PRIMARY, horizontal=True, height=360,
                x_title="Estado climático", y_title="% siniestros"), use_container_width=True)
        with c2:
            st.subheader(f"% fatal por clima — {pais_clima}")
            st.plotly_chart(charts.barras(
                df_est.set_index("estado_climatico")["pct_fatal"].sort_values(),
                color=COLOR_SEVERIDAD["fatal"], horizontal=True, height=360,
                x_title="Estado climático", y_title="% fatal"), use_container_width=True)
        st.divider()

        df_pob = query("""
            SELECT pais, SUM(total) AS total, SUM(fatal) AS fatales
            FROM proyecto.mv_acc_anio_pais
            GROUP BY pais
        """)
        df_pob["poblacion"]       = df_pob["pais"].map(POBLACION)
        df_pob["siniestros_100k"] = (df_pob["total"]   / df_pob["poblacion"] * 100000).round(1)
        df_pob["fatales_100k"]    = (df_pob["fatales"] / df_pob["poblacion"] * 100000).round(2)
        df_pob["pct_fatal"]       = (df_pob["fatales"] / df_pob["total"]     * 100).round(2)
        c1, c2, c3 = st.columns(3)
        with c1:
            st.subheader("Siniestros / 100k hab.")
            st.plotly_chart(charts.barras(
                df_pob.set_index("pais")["siniestros_100k"], height=280,
                y_title="Siniestros / 100.000 hab."), use_container_width=True)
        with c2:
            st.subheader("Fatales / 100k hab.")
            st.plotly_chart(charts.barras(
                df_pob.set_index("pais")["fatales_100k"], height=280,
                y_title="Fatales / 100.000 hab."), use_container_width=True)
        with c3:
            st.subheader("% Fatal global")
            st.plotly_chart(charts.barras(
                df_pob.set_index("pais")["pct_fatal"], height=280,
                y_title="% Fatal"), use_container_width=True)

    except Exception as e:
        st.error("Error cargando datos climáticos.")
        st.exception(e)

# ══════════════════════════════════════════════════════════════════════════
# PÁGINA 7 — IMPACTO COVID-19  (Q10)
# ══════════════════════════════════════════════════════════════════════════
elif pagina == "🦠 Impacto COVID-19":
    import plotly.graph_objects as go

    header("🦠 Impacto COVID-19 en la Siniestralidad Vial",
           "Q10 — ¿cómo afectó la pandemia el volumen y la gravedad? (baseline 2018–2019)")

    try:
        # ── 1. Volumen anual por país ──────────────────────────────────────
        df_anual = query("""
            SELECT anio, pais, total
            FROM proyecto.mv_acc_anio_pais
            WHERE anio BETWEEN 2018 AND 2024
            ORDER BY anio, pais
        """)
        df_anual["tasa_100k"] = df_anual.apply(
            lambda r: round(r["total"] / POBLACION.get(r["pais"], 1) * 100000, 2), axis=1)
        df_pivot = df_anual.pivot(index="anio", columns="pais", values="tasa_100k").fillna(0)

        COLORES_PAIS = COLOR_PAIS

        st.subheader("Tasa de siniestros / 100k hab. por año")
        st.caption("Zona sombreada: período COVID-19 (2020–2022)")
        fig1 = go.Figure()
        for pais in [c for c in PAISES if c in df_pivot.columns]:
            fig1.add_trace(go.Scatter(
                x=df_pivot.index, y=df_pivot[pais],
                mode="lines+markers", name=pais,
                line=dict(color=COLORES_PAIS.get(pais, "#999"), width=2.5),
                marker=dict(size=7)
            ))
        fig1.add_vrect(x0=2019.5, x1=2022.5,
                       fillcolor="lightgrey", opacity=0.3, layer="below", line_width=0,
                       annotation_text="COVID-19", annotation_position="top left",
                       annotation_font_size=12)
        estilo(fig1, xaxis_title="Año", yaxis_title="Siniestros / 100.000 hab.",
               legend_title="País", height=400, xaxis=dict(tickmode="linear", dtick=1))
        st.plotly_chart(fig1, use_container_width=True)
        st.caption(NOTA_RENAEST_2018)
        st.divider()

        # ── 2. Índice de disrupción anual vs baseline 2018–2019 ───────────
        st.subheader("Índice de disrupción anual vs. baseline 2018–2019 (%)")
        st.caption("Negativo = menos siniestros que el promedio 2018–2019 · Positivo = más")
        br_solo_2019 = st.toggle(
            "Brasil: usar baseline **solo-2019** (corrige la cobertura parcial de RENAEST 2018)",
            value=False, key="br_baseline_2019")
        if br_solo_2019:
            st.info("**Artefacto Brasil (§4.3.1):** los ficheros RENAEST de 2018 tienen cobertura "
                    "parcial en los primeros meses (749.134 vs 1.031.973 en 2019), por lo que un "
                    "baseline promedio 2018–2019 queda artificialmente bajo e **infla** el índice de "
                    "disrupción de Brasil (lo vuelve muy positivo). Con baseline **solo-2019** el "
                    "salto de Brasil se atenúa. Uruguay y España conservan el promedio 2018–2019, "
                    "cuyas fuentes no presentan este sesgo de cobertura.")
        df_dis = query("""
            WITH base AS (
                SELECT pais,
                       CASE
                         WHEN pais = 'Brasil' AND :br_solo_2019 THEN
                              SUM(total) FILTER (WHERE anio = 2019)::numeric
                         ELSE SUM(total)::numeric / 2
                       END AS promedio_base
                FROM proyecto.mv_acc_anio_pais
                WHERE anio IN (2018, 2019)
                GROUP BY pais
            ),
            anual AS (
                SELECT pais, anio, total::numeric AS total
                FROM proyecto.mv_acc_anio_pais
                WHERE anio BETWEEN 2020 AND 2024
            )
            SELECT a.pais, a.anio,
                   ROUND((a.total / b.promedio_base - 1) * 100, 2) AS indice_pct
            FROM anual a JOIN base b ON a.pais = b.pais
            ORDER BY a.pais, a.anio
        """, params={"br_solo_2019": br_solo_2019})
        df_dis_piv = df_dis.pivot(index="anio", columns="pais", values="indice_pct").fillna(0)

        # KPIs: el choque inicial de 2020 vs. baseline, por país (delta semántico:
        # negativo = menos siniestros que el baseline = verde).
        if 2020 in df_dis_piv.index and 2020 in df_pivot.index:
            st.markdown("**Choque inicial 2020: tasa/100k y disrupción vs. baseline 2018–2019**")
            dis_2020 = df_dis_piv.loc[2020]
            paises_k = [p for p in PAISES if p in dis_2020.index]
            kcols = st.columns(len(paises_k), gap="medium")
            for kc, p in zip(kcols, paises_k):
                tasa_2020 = round(float(df_pivot.loc[2020, p]), 1)
                disrupcion = round(float(dis_2020[p]), 1)
                kpi(kc, f"{p} · 2020", f"{fmt_num(tasa_2020, 1)} /100k", delta=disrupcion,
                    help="Δ = disrupción 2020 vs. promedio 2018–2019, en % "
                         "(verde = menos siniestros, rojo = más)")

        fig2 = go.Figure()
        for pais in df_dis_piv.columns:
            fig2.add_trace(go.Bar(
                x=df_dis_piv.index.astype(str), y=df_dis_piv[pais],
                name=pais, marker_color=COLORES_PAIS.get(pais, "#999")
            ))
        fig2.add_hline(y=0, line_dash="dash", line_color="black", line_width=1)
        estilo(fig2, barmode="group", xaxis_title="Año",
               yaxis_title="Variación vs. baseline (%)", legend_title="País", height=380)
        st.plotly_chart(fig2, use_container_width=True)
        tabla(df_dis.rename(columns={"pais": "País", "anio": "Año", "indice_pct": "Índice disrupción (%)"}))
        st.divider()

        # ── 3. Composición de gravedad por período ────────────────────────
        st.subheader("Distribución de gravedad por período")
        st.caption("Pre-COVID (2018–2019) · Durante COVID (2020–2022) · Post-COVID (2023–2024)")
        df_grav = query("""
            WITH per AS (
                SELECT pais,
                       CASE WHEN anio BETWEEN 2018 AND 2019 THEN 'Pre-COVID'
                            WHEN anio BETWEEN 2020 AND 2022 THEN 'Durante COVID'
                            WHEN anio BETWEEN 2023 AND 2024 THEN 'Post-COVID' END AS periodo,
                       SUM(fatal) AS fatal, SUM(grave) AS grave,
                       SUM(leve)  AS leve,  SUM(solo_danos) AS solo_danos
                FROM proyecto.mv_acc_anio_pais
                WHERE anio BETWEEN 2018 AND 2024
                GROUP BY pais, periodo
            )
            SELECT pais, periodo, gravedad, total FROM (
                SELECT pais, periodo, 'fatal'      AS gravedad, fatal      AS total FROM per
                UNION ALL SELECT pais, periodo, 'grave',      grave      FROM per
                UNION ALL SELECT pais, periodo, 'leve',       leve       FROM per
                UNION ALL SELECT pais, periodo, 'solo_danos', solo_danos FROM per
            ) x WHERE total > 0
        """)
        totales_pp = df_grav.groupby(["pais", "periodo"])["total"].sum().reset_index()
        totales_pp.columns = ["pais", "periodo", "tot_periodo"]
        df_grav = df_grav.merge(totales_pp, on=["pais", "periodo"])
        df_grav["pct"] = (df_grav["total"] / df_grav["tot_periodo"] * 100).round(2)

        PERIODO_ORDER = ["Pre-COVID", "Durante COVID", "Post-COVID"]
        COLOR_GRAV = COLOR_SEVERIDAD

        pais_q10 = st.selectbox("País", PAISES, key="pais_sel")
        df_gp = df_grav[df_grav["pais"] == pais_q10].copy()

        fig3 = go.Figure()
        for grav in GRAVEDADES:
            df_g = df_gp[df_gp["gravedad"] == grav].set_index("periodo").reindex(PERIODO_ORDER)
            fig3.add_trace(go.Bar(
                x=PERIODO_ORDER, y=df_g["pct"].values,
                name=etiqueta_sev(grav), marker_color=COLOR_GRAV.get(grav, "#999")
            ))
        estilo(fig3, barmode="stack", xaxis_title="Período", yaxis_title="% siniestros del período",
               legend_title="Gravedad", height=380)
        st.plotly_chart(fig3, use_container_width=True)
        tabla(df_gp.assign(gravedad=df_gp["gravedad"].map(ETIQUETA_SEVERIDAD))[
            ["periodo", "gravedad", "pct"]].rename(
            columns={"periodo": "Período", "gravedad": "Gravedad", "pct": "%"}
        ).sort_values(["Período", "Gravedad"]))
        if pais_q10 == "Brasil":
            st.caption(NOTA_BRASIL)

    except Exception as e:
        st.error("Error cargando datos Q10.")
        st.exception(e)

# ══════════════════════════════════════════════════════════════════════════
# PÁGINA — INDICADOR MACRO WHO · ALCOHOL PER CÁPITA
# ══════════════════════════════════════════════════════════════════════════
elif pagina == "🍷 Indicador WHO — Alcohol":
    import plotly.graph_objects as go

    header("🍷 Indicador macro — Consumo de alcohol per cápita (WHO)",
           "Indicador WHO/GHO SA_0000001688 vs. tasa de fatalidad vial · JOIN semántico país+año · 2018–2022")

    COLORES_PAIS = COLOR_PAIS

    try:
        with st.spinner("Cruzando siniestralidad con el indicador WHO…"):
            df_who = query("""
                SELECT m.pais, m.anio, m.total,
                       m.fatal AS fatales,
                       ROUND(100.0 * m.fatal / NULLIF(m.total, 0), 2) AS pct_fatal,
                       iw.valor AS alcohol
                FROM proyecto.mv_acc_anio_pais m
                LEFT JOIN proyecto.indicador_who iw
                    ON  iw.pais          = m.pais
                    AND iw.anio          = m.anio
                    AND iw.indicador_cod = 'SA_0000001688'
                    AND iw.sexo          = 'TOTAL'
                WHERE m.pais IN ('Uruguay', 'Brasil', 'España')
                  AND m.anio BETWEEN 2018 AND 2022
                ORDER BY m.pais, m.anio
            """)
        df_who = df_who.dropna(subset=["alcohol"]).copy()
        df_who["alcohol"] = df_who["alcohol"].astype(float)

        # Estado vacío robusto: si no hay cruce con el indicador WHO (tabla sin
        # cargar o sin filas país+año), degradar con aviso en vez de romper
        # st.columns(0) más abajo. Presentación: no altera la consulta.
        if df_who.empty:
            st.info("Sin datos del indicador WHO de alcohol (SA_0000001688) para "
                    "2018–2022: `proyecto.indicador_who` no devolvió filas que crucen "
                    "por país+año. Verificá la carga de ese indicador.")
            st.stop()

        # ── KPIs: consumo medio 2018–2022 por país ─────────────────────────
        st.subheader("Consumo medio de alcohol per cápita 2018–2022")
        kpis = df_who.groupby("pais")["alcohol"].mean().round(2)
        cols = st.columns(len(kpis))
        for col_, (p, v) in zip(cols, kpis.items()):
            with col_.container(border=True):
                st.metric(p, f"{fmt_num(v, 2)} L",
                          help="Litros de alcohol puro per cápita/año (media 2018–2022)")
        st.divider()

        c1, c2 = st.columns(2)

        # ── Serie temporal: alcohol per cápita por país ────────────────────
        with c1:
            st.subheader("Alcohol per cápita por país (2018–2022)")
            fig_ts = go.Figure()
            for p in ["Brasil", "España", "Uruguay"]:
                d = df_who[df_who["pais"] == p]
                fig_ts.add_trace(go.Scatter(
                    x=d["anio"], y=d["alcohol"], mode="lines+markers", name=p,
                    line=dict(color=COLORES_PAIS[p], width=2.5), marker=dict(size=8)))
            estilo(fig_ts, xaxis_title="Año", yaxis_title="Litros per cápita/año",
                   legend_title="País", height=380, xaxis=dict(tickmode="linear", dtick=1))
            st.plotly_chart(fig_ts, use_container_width=True)

        # ── Scatter: alcohol (X) vs % fatal (Y), punto por país-año ────────
        with c2:
            st.subheader("Alcohol per cápita vs. % de siniestros fatales")
            fig_sc = go.Figure()
            for p in ["Brasil", "España", "Uruguay"]:
                d = df_who[df_who["pais"] == p]
                fig_sc.add_trace(go.Scatter(
                    x=d["alcohol"], y=d["pct_fatal"], mode="markers+text",
                    name=p, text=d["anio"].astype(str), textposition="top center",
                    textfont=dict(size=9),
                    marker=dict(size=13, color=COLORES_PAIS[p], line=dict(width=1, color="white")),
                    hovertemplate=(p + "<br>Año %{text}<br>Alcohol %{x:.2f} L"
                                   "<br>%{y:.2f}% fatal<extra></extra>")))
            estilo(fig_sc, xaxis_title="Alcohol per cápita (L/año)", yaxis_title="% siniestros fatales",
                   legend_title="País", height=380)
            st.plotly_chart(fig_sc, use_container_width=True)

        # ── Tabla de los 15 pares país-año ─────────────────────────────────
        tabla(df_who[["pais", "anio", "total", "fatales", "pct_fatal", "alcohol"]].rename(columns={
            "pais": "País", "anio": "Año", "total": "Siniestros", "fatales": "Fatales",
            "pct_fatal": "% fatal", "alcohol": "Alcohol L/cápita"}))

        # ── Caveat obligatorio (rúbrica) ───────────────────────────────────
        st.caption("**Fuente:** WHO Global Health Observatory — indicador SA_0000001688 "
                   "(alcohol total per cápita, ≥15 años). Cobertura 2018–2022 (sin 2023–2024).")
        st.warning("**Correlación ecológica país-año, no inferencia causal individual.** "
                   "Subconjunto reducido (15 pares país-año, 2018–2022).")

    except Exception as e:
        st.error("Error cargando el indicador WHO.")
        st.exception(e)

# ══════════════════════════════════════════════════════════════════════════
# PÁGINA 8 — CONSULTA MONGODB
# ══════════════════════════════════════════════════════════════════════════
elif pagina == "🗄️ Consulta MongoDB":
    import pydeck as pdk

    header("🗄️ Consulta NoSQL — MongoDB",
           "Análisis sobre la colección documental `accidentes` (Q1 · Q3–Q7 · Q9)")

    try:
        db  = get_mongo()[MONGO_DB]
        col = db["accidentes"]
        total_mongo = col.estimated_document_count()

        k1, k2 = st.columns([1, 3], gap="medium")
        kpi(k1, "Documentos (NoSQL)", fmt_int(total_mongo), icon="🗄️")
        with k2:
            st.info("Cada pestaña responde una pregunta analítica sobre la colección "
                    "documental de MongoDB. Resultados cacheados (TTL 1 h).")

        tabs = st.tabs([
            "P1 · Volumen", "P2 · Tipos (Q7)", "P3 · Evolución (Q1+Q5)",
            "P4 · Horarios (Q3+Q4)", "P5 · Regiones (Q6)", "P6 · Severidad (Q2+Q7)",
            "P7 · Geoespacial (Q9)",
        ])

        # ── P1 — Volumen por país ($group + $sort) ─────────────────────────
        with tabs[0]:
            st.subheader("Distribución de documentos por país")
            p1 = [{"$group": {"_id": "$pais", "total": {"$sum": 1}}}, {"$sort": {"total": -1}}]
            res = mongo_agg("accidentes", p1)
            d = pd.DataFrame([{"pais": r["_id"], "total": r["total"]} for r in res])
            if not d.empty:
                d["pct"] = (d["total"] / d["total"].sum() * 100).round(2)
                st.plotly_chart(charts.barras(d.set_index("pais")["pct"], height=320,
                                x_title="País", y_title="% de documentos"), use_container_width=True)
                tabla(d.rename(columns={"pais": "País", "total": "Documentos", "pct": "%"}))

        # ── P2 — Tipos (Q7): $match + $group + $sort + $limit ──────────────
        with tabs[1]:
            st.subheader("% por tipo de siniestro y país (Q7)")
            p2 = [
                {"$match": {"tipo_accidente": {"$nin": [None, "Sin datos"]}}},
                {"$group": {"_id": {"pais": "$pais", "tipo": "$tipo_accidente"}, "total": {"$sum": 1}}},
                {"$sort": {"total": -1}}, {"$limit": 100},
            ]
            res = mongo_agg("accidentes", p2)
            d = pd.DataFrame([{"pais": r["_id"]["pais"], "tipo": r["_id"]["tipo"],
                              "total": r["total"]} for r in res])
            if not d.empty:
                pais_p2 = st.selectbox("País", sorted(d["pais"].dropna().unique()), key="mp2_pais")
                dd = d[d["pais"] == pais_p2].head(10).copy()
                dd["pct"] = (dd["total"] / dd["total"].sum() * 100).round(2)
                st.plotly_chart(charts.barras(
                    dd.set_index("tipo")["pct"].sort_values(), color=charts.PRIMARY,
                    horizontal=True, height=400, x_title="Tipo", y_title="% del país"),
                    use_container_width=True)
                tabla(dd[["tipo", "total", "pct"]].rename(columns={
                    "tipo": "Tipo", "total": "Total", "pct": "% del país"}))

        # ── P3 — Evolución (Q1+Q5): $setWindowFields + $shift (LAG) ────────
        with tabs[2]:
            st.subheader("Evolución anual y variación interanual (Q1 + Q5)")
            p3 = [
                {"$match": {"fecha": {"$ne": None}}},
                {"$project": {"anio": {"$year": "$fecha"}, "pais": 1}},
                {"$match": {"anio": {"$gte": 2018, "$lte": 2025}}},
                {"$group": {"_id": {"anio": "$anio", "pais": "$pais"}, "total": {"$sum": 1}}},
                {"$setWindowFields": {"partitionBy": "$_id.pais", "sortBy": {"_id.anio": 1},
                    "output": {"prev": {"$shift": {"output": "$total", "by": -1}}}}},
                {"$project": {"_id": 0, "anio": "$_id.anio", "pais": "$_id.pais", "total": 1,
                    "variacion_pct": {"$cond": [
                        {"$or": [{"$eq": ["$prev", None]}, {"$eq": ["$prev", 0]}]}, None,
                        {"$round": [{"$multiply": [{"$divide": [
                            {"$subtract": ["$total", "$prev"]}, "$prev"]}, 100]}, 2]}]}}},
                {"$sort": {"pais": 1, "anio": 1}},
            ]
            res = mongo_agg("accidentes", p3)
            d = pd.DataFrame(res)
            if not d.empty:
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("**Total anual por país**")
                    st.plotly_chart(charts.lineas(
                        d.pivot(index="anio", columns="pais", values="total").fillna(0),
                        height=340, x_title="Año", y_title="Documentos",
                        xaxis=dict(tickmode="linear", dtick=1)), use_container_width=True)
                with c2:
                    st.markdown("**Variación interanual (%)**")
                    st.plotly_chart(charts.barras(
                        d.pivot(index="anio", columns="pais", values="variacion_pct").fillna(0),
                        height=340, x_title="Año", y_title="Variación %"), use_container_width=True)
                tabla(d.rename(columns={"anio": "Año", "pais": "País", "total": "Total",
                                        "variacion_pct": "Variación %"}))

        # ── P4 — Horarios (Q3+Q4): $switch + $dayOfWeek ────────────────────
        with tabs[3]:
            st.subheader("Franja horaria por tipo de día (Q3 + Q4)")
            pais_p4 = st.selectbox("País", PAISES, key="mp4_pais")
            p4 = [
                {"$match": {"pais": pais_p4, "hora": {"$ne": None, "$regex": r"^\d{1,2}"},
                            "fecha": {"$ne": None}}},
                {"$addFields": {"hora_int": {"$toInt": {"$substr": ["$hora", 0, 2]}},
                                "dow": {"$dayOfWeek": "$fecha"}}},
                {"$addFields": {
                    "franja": {"$switch": {"branches": [
                        {"case": {"$lt": ["$hora_int", 6]},  "then": "Madrugada (00-06)"},
                        {"case": {"$lt": ["$hora_int", 12]}, "then": "Mañana (06-12)"},
                        {"case": {"$lt": ["$hora_int", 18]}, "then": "Tarde (12-18)"},
                        {"case": {"$lte": ["$hora_int", 23]}, "then": "Noche (18-24)"}],
                        "default": "Desconocido"}},
                    "tipo_dia": {"$cond": [{"$in": ["$dow", [1, 7]]}, "Fin de semana", "Laborable"]}}},
                {"$group": {"_id": {"franja": "$franja", "tipo_dia": "$tipo_dia"}, "total": {"$sum": 1}}},
                {"$sort": {"_id.franja": 1}},
            ]
            res = mongo_agg("accidentes", p4)
            d = pd.DataFrame([{"franja": r["_id"]["franja"], "tipo_dia": r["_id"]["tipo_dia"],
                              "total": r["total"]} for r in res])
            if not d.empty:
                piv = d.pivot(index="franja", columns="tipo_dia", values="total").fillna(0)
                st.plotly_chart(charts.barras(piv, height=360, x_title="Franja horaria",
                                y_title="Siniestros"), use_container_width=True)
                tabla(d.rename(columns={"franja": "Franja", "tipo_dia": "Tipo de día",
                                        "total": "Total"}))

        # ── P5 — Regiones (Q6): $facet con sub-pipelines paralelos ─────────
        with tabs[4]:
            st.subheader("TOP 10 regiones por volumen y % fatal (Q6)")
            pais_p5 = st.selectbox("País", PAISES, key="mp5_pais")
            p5 = [
                {"$match": {"pais": pais_p5, "ubicacion.region": {"$ne": None}}},
                {"$facet": {
                    "regiones": [
                        {"$group": {"_id": "$ubicacion.region", "total": {"$sum": 1},
                            "fatales": {"$sum": {"$cond": [{"$eq": ["$gravedad", "fatal"]}, 1, 0]}}}},
                        {"$sort": {"total": -1}}, {"$limit": 10}],
                    "total_pais": [{"$count": "n"}]}},
                {"$project": {"resultado": {"$map": {"input": "$regiones", "as": "r", "in": {
                    "region": "$$r._id", "total": "$$r.total", "fatales": "$$r.fatales",
                    "pct_nacional": {"$round": [{"$multiply": [{"$divide": ["$$r.total",
                        {"$arrayElemAt": ["$total_pais.n", 0]}]}, 100]}, 2]},
                    "pct_fatal": {"$round": [{"$multiply": [{"$divide": ["$$r.fatales",
                        "$$r.total"]}, 100]}, 2]}}}}}},
            ]
            res = mongo_agg("accidentes", p5)
            if res and res[0].get("resultado"):
                d = pd.DataFrame(res[0]["resultado"])
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("**% sobre total nacional**")
                    st.plotly_chart(charts.barras(
                        d.set_index("region")["pct_nacional"].sort_values(), color=charts.PRIMARY,
                        horizontal=True, height=400, x_title="Región", y_title="% nacional"),
                        use_container_width=True)
                with c2:
                    st.markdown("**% fatal por región**")
                    st.plotly_chart(charts.barras(
                        d.set_index("region")["pct_fatal"].sort_values(),
                        color=COLOR_SEVERIDAD["fatal"], horizontal=True, height=400,
                        x_title="Región", y_title="% fatal"), use_container_width=True)
                tabla(d.rename(columns={"region": "Región", "total": "Total", "fatales": "Fatales",
                    "pct_nacional": "% nacional", "pct_fatal": "% Fatal"}),
                    resaltar="max", col_resaltada="% Fatal")

        # ── P6 — Severidad por tipo (Q2+Q7): $cond ─────────────────────────
        with tabs[5]:
            st.subheader("Severidad por tipo de siniestro (Q2 + Q7)")
            p6 = [
                {"$match": {"tipo_accidente": {"$nin": [None, "Sin datos"]}, "gravedad": {"$ne": None}}},
                {"$group": {"_id": {"pais": "$pais", "tipo": "$tipo_accidente"}, "total": {"$sum": 1},
                    "fatales": {"$sum": {"$cond": [{"$eq": ["$gravedad", "fatal"]}, 1, 0]}},
                    "graves": {"$sum": {"$cond": [{"$eq": ["$gravedad", "grave"]}, 1, 0]}}}},
                {"$match": {"total": {"$gte": 100}}},
                {"$project": {"_id": 0, "pais": "$_id.pais", "tipo": "$_id.tipo", "total": 1,
                    "pct_fatal": {"$round": [{"$multiply": [{"$divide": ["$fatales", "$total"]}, 100]}, 2]},
                    "pct_grave": {"$round": [{"$multiply": [{"$divide": ["$graves", "$total"]}, 100]}, 2]}}},
                {"$sort": {"pais": 1, "pct_fatal": -1}}, {"$limit": 50},
            ]
            res = mongo_agg("accidentes", p6)
            d = pd.DataFrame(res)
            if not d.empty:
                pais_p6 = st.selectbox("País", sorted(d["pais"].unique()), key="mp6_pais")
                dd = d[d["pais"] == pais_p6].head(10)
                piv = dd.set_index("tipo")[["pct_fatal", "pct_grave"]].rename(
                    columns={"pct_fatal": "% Fatal", "pct_grave": "% Grave"})
                st.plotly_chart(charts.barras(
                    piv, color=[COLOR_SEVERIDAD["fatal"], COLOR_SEVERIDAD["grave"]],
                    horizontal=True, height=420, x_title="Tipo", y_title="%"),
                    use_container_width=True)
                tabla(dd.rename(columns={"pais": "País", "tipo": "Tipo", "total": "Total",
                    "pct_fatal": "% Fatal", "pct_grave": "% Grave"}))

        # ── P7 — Geoespacial (Q9): $geoNear + anillos + mapa ───────────────
        with tabs[6]:
            st.subheader("Distribución geoespacial cerca de capital (Q9)")
            st.caption("Siniestros por anillos de distancia alrededor de la capital "
                       "(índice geoespacial 2dsphere).")
            CIUDADES = {
                "Montevideo (UY)": (-56.1645, -34.9011),
                "São Paulo (BR)":  (-46.6333, -23.5505),
                "Madrid (ES)":     ( -3.7038,  40.4168),
            }
            cc1, cc2 = st.columns(2)
            with cc1:
                ciudad = st.selectbox("Ciudad de referencia", list(CIUDADES.keys()), key="mp7_city")
            with cc2:
                radio_km = st.slider("Radio máximo (km)", 5, 50, 20, 5, key="mp7_radio")
            lon0, lat0 = CIUDADES[ciudad]
            # Anillos DINÁMICOS: el radio se divide en 5 bandas iguales, así mover el
            # slider re-reparte TODOS los puntos. Antes los cortes 0-5/5-10/10-20 eran
            # FIJOS → subir el radio solo agrandaba el bucket "20+" y las 3 primeras
            # barras no cambiaban (parecía que el slider no hacía nada). Como el slider
            # avanza de a 5 km, cada banda mide km enteros. `$bucket` agrupa por el
            # límite inferior numérico, evitando el orden alfabético erróneo del $sort
            # anterior (que ponía "10-20 km" antes que "5-10 km").
            n_anillos = 5
            paso_km = radio_km / n_anillos
            km_bordes = [round(i * paso_km) for i in range(n_anillos + 1)]
            bordes_m = [k * 1000 for k in km_bordes]
            bordes_m[-1] += 1  # incluir el punto exactamente en el radio máximo
            etiquetas = [f"{km_bordes[i]}–{km_bordes[i + 1]} km" for i in range(n_anillos)]
            p7 = [
                {"$geoNear": {"near": {"type": "Point", "coordinates": [lon0, lat0]},
                    "distanceField": "dist_m", "maxDistance": radio_km * 1000, "spherical": True}},
                {"$bucket": {
                    "groupBy": "$dist_m", "boundaries": bordes_m, "default": "resto",
                    "output": {"total": {"$sum": 1},
                        "fatales": {"$sum": {"$cond": [{"$eq": ["$gravedad", "fatal"]}, 1, 0]}}}}},
            ]
            try:
                with st.spinner(f"Ejecutando $geoNear + $bucket a ≤{radio_km} km de {ciudad}…"):
                    res = list(col.aggregate(p7))
                # Reindexar a los 5 anillos en orden (los vacíos quedan en 0).
                por_lo = {r["_id"]: r for r in res if isinstance(r["_id"], (int, float))}
                filas_anillos = [{"rango": etiquetas[i],
                                  "total":   por_lo.get(bordes_m[i], {}).get("total", 0),
                                  "fatales": por_lo.get(bordes_m[i], {}).get("fatales", 0)}
                                 for i in range(n_anillos)]
                if any(f["total"] for f in filas_anillos):
                    d = pd.DataFrame(filas_anillos)
                    d["pct_fatal"] = (d["fatales"] / d["total"].replace(0, pd.NA) * 100).round(2)
                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown(f"**Siniestros por anillo · {ciudad}**")
                        st.plotly_chart(charts.barras(d.set_index("rango")["total"],
                            color=charts.PRIMARY, height=320, x_title="Anillo", y_title="Siniestros"),
                            use_container_width=True)
                    with c2:
                        st.markdown("**% fatal por anillo**")
                        st.plotly_chart(charts.barras(d.set_index("rango")["pct_fatal"],
                            color=COLOR_SEVERIDAD["fatal"], height=320, x_title="Anillo",
                            y_title="% fatal"), use_container_width=True)
                    tabla(d.rename(columns={"rango": "Anillo", "total": "Total",
                        "fatales": "Fatales", "pct_fatal": "% Fatal"}))

                    # Mapa de puntos en el radio. Usamos $sample (NO $limit sobre el orden
                    # de $geoNear): $geoNear entrega los puntos de cerca a lejos, así que un
                    # $limit fijo devolvía siempre los 4000 MÁS CERCANOS (el núcleo denso) y
                    # el mapa no cambiaba al mover el slider (en Montevideo/São Paulo hay
                    # decenas de miles de puntos hasta en 5 km → ampliar el radio solo agregaba
                    # puntos lejanos que el $limit recortaba). Con $sample la muestra se
                    # reparte por TODO el radio y se expande visiblemente al subirlo.
                    pts = list(col.aggregate([
                        {"$geoNear": {"near": {"type": "Point", "coordinates": [lon0, lat0]},
                            "distanceField": "dist_m", "maxDistance": radio_km * 1000,
                            "spherical": True}},
                        {"$project": {"_id": 0, "gravedad": 1, "fecha": 1,
                            "coords": "$ubicacion.coordenadas.coordinates"}},
                        {"$sample": {"size": 4000}}]))
                    filas = [{"lon": p["coords"][0], "lat": p["coords"][1],
                              "gravedad": p.get("gravedad") or "s/d",
                              "grav_lbl": etiqueta_sev(p["gravedad"]) if p.get("gravedad") else "Sin dato",
                              "fecha": str(p.get("fecha"))[:10]}
                             for p in pts if p.get("coords") and len(p["coords"]) == 2]
                    if filas:
                        dfm = pd.DataFrame(filas)
                        cmap = {g: color_sev_rgb(g, 200) for g in GRAVEDADES}
                        dfm["color"] = dfm["gravedad"].apply(lambda g: cmap.get(g, [46, 117, 182]))
                        st.pydeck_chart(pdk.Deck(
                            layers=[pdk.Layer("ScatterplotLayer", data=dfm,
                                get_position="[lon, lat]", get_color="color",
                                get_radius=80, pickable=True, opacity=0.7)],
                            initial_view_state=pdk.ViewState(latitude=lat0, longitude=lon0,
                                zoom=10, pitch=0),
                            tooltip={"text": "Gravedad: {grav_lbl}\nFecha: {fecha}"},
                            map_style="road"))
                        leyenda_severidad(sin_dato=True)
                elif "(ES)" in ciudad:
                    # España deriva la ubicación de centroides de provincia → sus
                    # documentos NO llevan coordenadas a nivel de evento (campo NULL),
                    # por lo que el índice 2dsphere (sparse) no los incluye y $geoNear
                    # devuelve 0. No es un fallo del índice, es la cobertura de la fuente.
                    st.info("**Sin coordenadas a nivel de evento para España (DGT).** La "
                            "ubicación se deriva de **centroides de provincia**, así que los "
                            "documentos no tienen punto GeoJSON propio y `$geoNear` no los "
                            "alcanza (0 % de cobertura geoespacial). Probá **Montevideo** o "
                            "**São Paulo**, que sí tienen coordenadas. El índice 2dsphere está activo.")
                else:
                    st.warning("Sin resultados en el radio para esta ciudad. Probá ampliar el "
                               "radio o verificá que el índice 2dsphere esté activo.")
            except Exception as ge:
                st.warning("Consulta geoespacial no disponible: falta el índice **2dsphere** "
                           "sobre `ubicacion.coordenadas`. El resto de las secciones (P1–P6) "
                           "funcionan igual.")
                st.caption(f"Detalle: {type(ge).__name__}")

        st.divider()
        st.warning(NOTA_GEO)

    except Exception as e:
        st.error("No se pudo consultar MongoDB.")
        st.exception(e)

# ══════════════════════════════════════════════════════════════════════════
# PÁGINA — CALIDAD & COBERTURA  (transparencia · rúbrica D5)
# ══════════════════════════════════════════════════════════════════════════
elif pagina == "✅ Calidad & Cobertura":
    header("✅ Calidad & Cobertura de Datos",
           "Transparencia DAMA (completitud/cobertura) por fuente sobre 9.266.912 registros")

    try:
        dfq = query("""
            SELECT pais,
                   SUM(total)        AS n,
                   SUM(con_coords)   AS con_coords,
                   SUM(con_clima)    AS con_clima,
                   SUM(con_gravedad) AS con_gravedad,
                   SUM(fatal) AS fatal, SUM(grave) AS grave,
                   SUM(leve)  AS leve,  SUM(solo_danos) AS solo_danos
            FROM proyecto.mv_acc_anio_pais
            GROUP BY pais ORDER BY n DESC
        """)
        n_tot  = int(dfq["n"].sum())
        cc_tot = int(dfq["con_coords"].sum())
        cl_tot = int(dfq["con_clima"].sum())
        cg_tot = int(dfq["con_gravedad"].sum())

        k1, k2, k3, k4 = st.columns(4)
        with k1.container(border=True):
            st.metric("Registros totales", fmt_int(n_tot))
        with k2.container(border=True):
            st.metric("Cobertura coordenadas", fmt_pct(cc_tot / n_tot * 100, 1), f"{fmt_int(cc_tot)} regs")
        with k3.container(border=True):
            st.metric("Cobertura clima", fmt_pct(cl_tot / n_tot * 100, 1), f"{fmt_int(cl_tot)} regs")
        with k4.container(border=True):
            st.metric("Con gravedad", fmt_pct(cg_tot / n_tot * 100, 1), f"{fmt_int(cg_tot)} regs")
        st.divider()

        dfq["% coords"]   = (dfq["con_coords"]   / dfq["n"] * 100).round(1)
        dfq["% clima"]    = (dfq["con_clima"]    / dfq["n"] * 100).round(1)
        dfq["% gravedad"] = (dfq["con_gravedad"] / dfq["n"] * 100).round(1)

        st.subheader("Cobertura por país")
        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(charts.barras(
                dfq.set_index("pais")[["% coords", "% clima"]], height=320,
                x_title="País", y_title="% de registros"), use_container_width=True)
            st.caption("% de registros con coordenadas válidas y con enriquecimiento climático")
        with c2:
            tabla(dfq[["pais", "n", "% coords", "% clima", "% gravedad"]].rename(columns={"pais": "País"}))
        st.divider()

        st.subheader("Distribución de gravedad por país (%)")
        grav_pct = dfq.copy()
        for g in GRAVEDADES:
            grav_pct[g] = (grav_pct[g] / grav_pct["n"] * 100).round(2)
        grav_piv = (grav_pct.set_index("pais")[GRAVEDADES]
                    .reindex([p for p in PAISES if p in set(grav_pct["pais"])])
                    .rename(columns=ETIQUETA_SEVERIDAD))
        st.plotly_chart(charts.barras(
            grav_piv, color=colores_sev(GRAVEDADES), height=340,
            x_title="País", y_title="% del total del país"), use_container_width=True)
        tabla(grav_piv.round(2), hide_index=False)
        leyenda_severidad()
        st.caption("% sobre el total de cada país.")

        st.warning("**Limitaciones de calidad documentadas:** "
                   "(a) **Brasil**: `grave`=NULL (RENAEST no lo registra) y ≈31 % de tipos sin "
                   "clasificar; ≈33,8 % con coordenadas. "
                   "(b) **España**: 0 % de coordenadas a nivel de evento (centroides de provincia) "
                   "y 0 % de `solo_danos` (DGT no reporta esa categoría). "
                   "(c) **Clima**: enriquecimiento parcial limitado a las combinaciones más "
                   "frecuentes (UY 7,0 % · BR 0,5 % · ES 0 %).")
        st.caption("**Fuente:** vistas materializadas sobre proyecto.accidentes (9.266.912 regs).")

    except Exception as e:
        st.error("Error cargando datos de calidad.")
        st.exception(e)

# ── Footer (marca, población de referencia y fuentes; antes en la sidebar) ───
ui.footer()