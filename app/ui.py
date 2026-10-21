"""
ui.py — Capa de shell visual del dashboard (sistema de diseño BI corporativo).
Proyecto LIDIA · UTEC ITR Norte 2026.

Centraliza el "marco" de la interfaz (NO los datos): CSS inyectado, hero header,
navbar superior y footer. Importa la paleta desde dashboard/constants.py para no
duplicar colores. Diseñado para funcionar tanto en streamlit 1.35.0 (imagen Docker)
como en 1.58 (host de dev): se ocultan los elementos de chrome por `data-testid`
estables y se evita cualquier API nueva de Streamlit.
"""
import streamlit as st

from constants import COLOR_SEVERIDAD  # paleta única (color-blind safe)

PRIMARY = "#0B5394"   # acento institucional (coherente con .streamlit/config.toml)

# ── Variables de color (única fuente: constants.COLOR_SEVERIDAD) ─────────────
_VARS = f""":root {{
  --primary:{PRIMARY}; --primary-d:#083a68;
  --bg:#F6F8FB; --card:#FFFFFF; --text:#1F2937; --muted:#5B6677;
  --border:#E5E9F0; --grid:#EEF1F5;
  --radius:14px;
  --shadow:0 1px 3px rgba(16,24,40,.06);
  --shadow-h:0 8px 24px rgba(16,24,40,.12);
  --fatal:{COLOR_SEVERIDAD['fatal']}; --grave:{COLOR_SEVERIDAD['grave']};
  --leve:{COLOR_SEVERIDAD['leve']}; --solo:{COLOR_SEVERIDAD['solo_danos']};
}}"""

# ── Reglas (string plano: las llaves CSS son literales, sin f-string) ────────
_RULES = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [data-testid="stAppViewContainer"], [class*="css"] {
  font-family: 'Inter', -apple-system, 'Segoe UI', sans-serif;
}

/* Fondo de la app (gris muy claro para que las tarjetas blancas resalten) */
[data-testid="stAppViewContainer"] { background: var(--bg); }

/* Ocultar el chrome de Streamlit (selectores estables en 1.35 y 1.58) */
[data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stDecoration"] { display: none !important; }
#MainMenu { visibility: hidden; }
footer { visibility: hidden; height: 0; }
section[data-testid="stSidebar"], [data-testid="collapsedControl"],
[data-testid="stSidebarCollapsedControl"] { display: none !important; }

/* Contenedor principal: ancho cómodo y menos padding superior */
.block-container, [data-testid="stMainBlockContainer"] {
  padding-top: 1.1rem; padding-bottom: 2.4rem; max-width: 1320px;
}

/* Barra de scroll discreta acorde a la paleta */
::-webkit-scrollbar { width: 10px; height: 10px; }
::-webkit-scrollbar-thumb { background: #C7D0DC; border-radius: 6px; }
::-webkit-scrollbar-thumb:hover { background: #AEB9C8; }

/* Navbar superior: st.radio(horizontal) estilizado como barra de pestañas.
   Selectores sobre data-testid="stRadio" → estables en 1.35 y 1.57. Si el
   navegador no soporta :has(), igual navega (degrada a radios planos). */
div[data-testid="stRadio"] > div[role="radiogroup"] {
  flex-direction: row; flex-wrap: wrap; gap: 4px; align-items: center;
  background: #FFFFFF; border: 1px solid var(--border); border-radius: 14px;
  padding: 0.45rem 0.55rem; box-shadow: var(--shadow); margin-bottom: 0.8rem;
}
div[data-testid="stRadio"] > div[role="radiogroup"] > label {
  background: transparent; border-radius: 9px; margin: 2px 3px;
  padding: 0.4rem 0.85rem; cursor: pointer; transition: all .15s ease;
}
div[data-testid="stRadio"] > div[role="radiogroup"] > label:hover { background: #EEF3F9; }
/* Ocultar el círculo del radio: dejar solo el texto como "pestaña" */
div[data-testid="stRadio"] > div[role="radiogroup"] > label > div:first-child { display: none; }
div[data-testid="stRadio"] > div[role="radiogroup"] label p {
  font-size: 0.82rem; font-weight: 500; color: #1F2937;
}
/* Pestaña activa (el label que contiene el input marcado) */
div[data-testid="stRadio"] > div[role="radiogroup"] > label:has(input:checked) {
  background: var(--primary); box-shadow: 0 2px 8px rgba(11,83,148,.30);
}
div[data-testid="stRadio"] > div[role="radiogroup"] > label:has(input:checked) p {
  color: #FFFFFF !important; font-weight: 600;
}

/* Hero header por sección (banner con gradiente + brillo decorativo) */
.lidia-hero {
  position: relative; overflow: hidden;
  background: linear-gradient(110deg, var(--primary-d) 0%, var(--primary) 48%, #1565C0 100%);
  color: #fff; padding: 22px 28px; border-radius: 16px; margin: 0 0 18px 0;
  box-shadow: 0 6px 22px rgba(11,83,148,.22);
}
.lidia-hero::after {
  content: ""; position: absolute; right: -50px; top: -70px;
  width: 240px; height: 240px; border-radius: 50%;
  background: radial-gradient(circle, rgba(255,255,255,.16), transparent 70%);
}
.lidia-hero-title { position: relative; font-size: 1.7rem; font-weight: 800; letter-spacing: .2px; line-height: 1.2; }
.lidia-hero-sub   { position: relative; font-size: .95rem; font-weight: 400; opacity: .93; margin-top: 6px; max-width: 86ch; }

/* Tarjetas KPI: se estiliza el contenedor con borde que envuelve cada st.metric.
   Hover con leve elevación para reforzar la jerarquía de "tarjeta". */
/* Tarjeta KPI: borde uniforme 1px + franja azul de acento con box-shadow INSET.
   CLAVE — `:not(:has(stVerticalBlockBorderWrapper))`: Streamlit envuelve TODO el
   bloque principal en un stVerticalBlockBorderWrapper que también contiene métricas;
   sin el :not, el selector `:has(stMetric)` pintaba el borde/acento azul en ese
   wrapper GRANDE además de en cada tarjeta → se veía un "doble borde" a la izquierda
   del contenido. El :not(:has(...)) limita la regla a los wrappers HOJA (los que no
   contienen otro wrapper), es decir, solo las tarjetas reales. El inset-shadow pinta
   el acento dentro del borde, sin alterar su geometría (un único borde limpio). */
div[data-testid="stVerticalBlockBorderWrapper"]:has([data-testid="stMetric"]):not(:has(div[data-testid="stVerticalBlockBorderWrapper"])) {
  background: var(--card); border: 1px solid var(--border) !important;
  border-radius: 12px;
  padding: 6px 16px 12px;
  box-shadow: inset 4px 0 0 0 var(--primary), var(--shadow);
  transition: box-shadow .18s ease, transform .18s ease;
}
div[data-testid="stVerticalBlockBorderWrapper"]:has([data-testid="stMetric"]):not(:has(div[data-testid="stVerticalBlockBorderWrapper"])):hover {
  box-shadow: inset 4px 0 0 0 var(--primary), var(--shadow-h); transform: translateY(-2px);
}
[data-testid="stMetricValue"] {
  font-size: 1.85rem; font-weight: 700; color: var(--text);
  font-variant-numeric: tabular-nums; line-height: 1.15;
}
[data-testid="stMetricLabel"] p {
  font-size: .72rem; text-transform: uppercase; letter-spacing: .6px;
  color: var(--muted); font-weight: 700;
}
[data-testid="stMetricDelta"] { font-weight: 600; font-size: .82rem; }

/* Charts como tarjetas */
[data-testid="stPlotlyChart"] {
  background: var(--card); border: 1px solid #E9EDF2; border-radius: var(--radius);
  padding: 6px 10px; box-shadow: var(--shadow);
}

/* Tablas como tarjetas (la grilla canvas no admite zebra por CSS; el formato
   es-UY y el resaltado se aplican vía pandas Styler en app.tabla). */
[data-testid="stDataFrame"], [data-testid="stTable"] {
  background: var(--card); border: 1px solid #E9EDF2; border-radius: var(--radius);
  padding: 4px; box-shadow: var(--shadow);
}

/* Mapas (pydeck) también como tarjeta para no romper el ritmo visual */
[data-testid="stDeckGlJsonChart"] {
  border-radius: var(--radius); overflow: hidden; box-shadow: var(--shadow);
}

/* Pestañas (st.tabs): tipografía Inter + acento institucional en la activa.
   Selectores baseweb: si una versión de Streamlit no los expone, la regla
   simplemente no aplica (CSS no-match = sin efecto), nunca rompe la página. */
div[data-testid="stTabs"] button[data-baseweb="tab"] {
  font-family: 'Inter', sans-serif; font-weight: 600; font-size: .84rem;
  color: var(--muted); letter-spacing: .1px;
}
div[data-testid="stTabs"] button[data-baseweb="tab"]:hover { color: var(--text); }
div[data-testid="stTabs"] button[data-baseweb="tab"][aria-selected="true"] { color: var(--primary); }
div[data-testid="stTabs"] div[data-baseweb="tab-highlight"] { background: var(--primary); }
div[data-testid="stTabs"] div[data-baseweb="tab-border"] { background: var(--grid); }

/* Jerarquía tipográfica de subtítulos de sección */
.block-container h2 { color: var(--text); font-weight: 700; letter-spacing: -.01em; }
.block-container h3 {
  color: var(--primary); font-weight: 600;
  border-bottom: 1px solid var(--grid); padding-bottom: 4px; margin-top: .5rem;
}

/* Separadores y etiquetas de widgets */
.block-container hr { margin: 1rem 0; border: none; border-top: 1px solid var(--border); }
[data-testid="stWidgetLabel"] p { font-weight: 600; color: var(--muted); font-size: .8rem; }
[data-testid="stCaptionContainer"] p, [data-testid="stCaptionContainer"] { color: var(--muted); }

/* Alertas (info/warning/success/error) con esquinas suaves */
[data-testid="stAlert"], [data-testid="stNotification"] { border-radius: 10px; }

/* Blockquotes (las preguntas «> ❓ Qx») */
.block-container blockquote {
  border-left: 3px solid var(--primary); background: #F4F8FC;
  padding: 10px 16px; border-radius: 8px; color: #33414F;
}
.block-container blockquote p { margin: 0; }

/* Footer informativo */
.lidia-footer {
  color: var(--muted); font-size: .8rem; text-align: center; line-height: 1.75;
  padding: 14px 0 4px 0; border-top: 1px solid var(--border); margin-top: 18px;
}
.lidia-footer b { color: var(--text); }
"""

CSS = _VARS + _RULES


def inject_css():
    """Inyecta el sistema de diseño una vez por render (idempotente)."""
    st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)


def hero(titulo, subtitulo=None):
    """Encabezado de sección como banner (reemplaza el antiguo st.title + caption)."""
    sub = f'<div class="lidia-hero-sub">{subtitulo}</div>' if subtitulo else ""
    st.markdown(
        f'<div class="lidia-hero"><div class="lidia-hero-title">{titulo}</div>{sub}</div>',
        unsafe_allow_html=True,
    )


def render_navbar(items, icons=None, key="nav"):
    """Navbar horizontal superior. Devuelve la etiqueta elegida.

    Implementado con `st.radio(horizontal=True)` — widget NATIVO disponible desde
    Streamlit 1.18, por lo que funciona igual en 1.35.0 (Docker local) y 1.57.0
    (server). Se estiliza como barra de pestañas (pills) vía CSS en `inject_css`
    (selector `[data-testid="stRadio"]`). Antes usaba `streamlit-option-menu`, un
    componente custom cuyo frontend rompía con el Streamlit nuevo del server
    (página en blanco al navegar). `icons` se acepta por compatibilidad de firma
    pero no se usa (st.radio no soporta iconos por opción).
    """
    return st.radio(
        "Navegación", list(items), index=0, horizontal=True,
        key=key, label_visibility="collapsed",
    )


def footer():
    """Footer con marca, población de referencia y fuentes (lo que estaba en la sidebar)."""
    from constants import POBLACION, PAISES, fmt_int
    pob = " · ".join(f"{p} {fmt_int(POBLACION[p])}" for p in PAISES)
    st.markdown(
        '<div class="lidia-footer">'
        '🚗 <b>Grupo 04 · LIDIA · UTEC ITR Norte</b> — Uruguay · Brasil · España (2018–2025)'
        f'<br>Población de referencia: {pob}'
        ' &nbsp;·&nbsp; Fuentes: 🇺🇾 UNASEV · 🇧🇷 RENAEST · 🇪🇸 DGT'
        '</div>',
        unsafe_allow_html=True,
    )
