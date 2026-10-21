"""
charts.py — Fábrica de figuras Plotly estilizadas (capa de presentación).
Proyecto LIDIA · UTEC ITR Norte 2026.

Unifica el "look" de TODAS las visualizaciones del dashboard. Antes convivían
gráficos Plotly ya estilizados con st.bar_chart / st.line_chart NATIVOS
(Vega-Lite): los nativos no recibían la tarjeta, ni la paleta central, ni el
formato es-UY, y rompían la coherencia visual. Estas fábricas devuelven figuras
Plotly listas para `st.plotly_chart(...)`, reemplazando a los nativos.

Pura: depende solo de plotly + pandas + constants (sin streamlit) → testeable.
"""
import pandas as pd
import plotly.graph_objects as go

from constants import COLOR_PAIS, PLOTLY_TEMPLATE

PRIMARY = "#0B5394"   # acento institucional (coherente con ui.PRIMARY)
GRID = "#EEF1F5"      # gridline sutil (coherente con el sistema de diseño)

# Paleta cualitativa de respaldo (CB-safe, Okabe-Ito) para series sin color propio.
_QUALI = ["#0B5394", "#E69F00", "#009E73", "#CC79A7", "#56B4E9", "#D55E00", "#7F7F7F"]


def estilizar(fig, **kw):
    """Plantilla limpia (plotly_white) + separadores es-UY + tipografía Inter.

    Fuente ÚNICA de estilo de figuras: `app.estilo()` delega aquí para que cada
    figura del dashboard (las nativas migradas y las que ya eran Plotly) comparta
    exactamente la misma apariencia. `separators=",."` ⇒ decimal "," y miles "."
    en hovers y ejes (locale es-UY).
    """
    # NOTA: no fijar `title_font` acá. Si una figura no tiene `title.text`, definir
    # solo la fuente del título crea un objeto title vacío que Plotly.js renderiza
    # como el literal "undefined". Las figuras con título lo heredan de `font`.
    fig.update_layout(
        template=PLOTLY_TEMPLATE, separators=",.",
        margin=dict(l=10, r=10, t=50, b=10),
        font=dict(family="Inter, 'Segoe UI', sans-serif", size=13, color="#1F2937"),
        hoverlabel=dict(font_family="Inter, sans-serif", font_size=12),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
    )
    fig.update_xaxes(showgrid=False, zeroline=False, linecolor="#E5E9F0", ticks="outside",
                     tickcolor="#E5E9F0")
    fig.update_yaxes(showgrid=True, gridcolor=GRID, zeroline=False)
    if kw:
        fig.update_layout(**kw)
    return fig


def _df(data):
    """Normaliza una Serie a DataFrame de una columna (preserva el nombre)."""
    if isinstance(data, pd.Series):
        return data.to_frame(name=data.name if data.name is not None else "valor")
    return data


def _colores(cols, color):
    """Resuelve el color de cada columna: str | lista | dict | None (auto)."""
    cols = [str(c) for c in cols]
    if isinstance(color, str):
        return {c: color for c in cols}
    if isinstance(color, dict):
        return {c: color.get(c, PRIMARY) for c in cols}
    if isinstance(color, (list, tuple)):
        return {c: color[i % len(color)] for i, c in enumerate(cols)}
    if all(c in COLOR_PAIS for c in cols):          # columnas = países → su paleta
        return {c: COLOR_PAIS[c] for c in cols}
    return {c: _QUALI[i % len(_QUALI)] for i, c in enumerate(cols)}


def barras(data, *, color=None, horizontal=False, height=320,
           x_title="", y_title="", barmode="group", text=False, **kw):
    """Figura de barras estilizada que reemplaza a `st.bar_chart`.

    `data` puede ser una Serie (una sola serie) o un DataFrame (una barra por
    columna, agrupadas). El índice va al eje de categorías. `color` admite str
    (un color), lista (por columna), dict (por nombre) o None (por país si el
    índice/columnas son países; si no, paleta cualitativa). Con `horizontal=True`
    el índice va al eje Y (útil para etiquetas largas: regiones, estados de clima).
    """
    df = _df(data)
    cats = [str(i) for i in df.index]
    single = df.shape[1] == 1
    fig = go.Figure()

    # Caso frecuente: una sola serie cuyo índice son países → cada barra su color.
    if single and color is None and len(cats) and all(c in COLOR_PAIS for c in cats):
        col = df.columns[0]
        _barra(fig, cats, df[col].tolist(), name=str(col),
               color=[COLOR_PAIS[c] for c in cats], horizontal=horizontal,
               showlegend=False, text=text)
    else:
        cmap = _colores(df.columns, color)
        for col in df.columns:
            _barra(fig, cats, df[col].tolist(), name=str(col), color=cmap[str(col)],
                   horizontal=horizontal, showlegend=not single, text=text)

    estilizar(fig, height=height, barmode=barmode, bargap=0.22, **kw)
    fig.update_layout(
        xaxis_title=(y_title if horizontal else x_title),
        yaxis_title=(x_title if horizontal else y_title),
        showlegend=not single,
    )
    return fig


def _barra(fig, cats, vals, *, name, color, horizontal, showlegend, text):
    """Agrega una traza Bar (orientación V/H) con hover es-UY."""
    txt = [f"{v:,.1f}" if v is not None else "" for v in vals] if text else None
    common = dict(name=name, marker_color=color, showlegend=showlegend,
                  marker_line_width=0, text=txt,
                  textposition="outside" if text else "none",
                  textfont=dict(size=11))
    if horizontal:
        fig.add_trace(go.Bar(
            y=cats, x=vals, orientation="h",
            hovertemplate=f"<b>%{{y}}</b><br>{name}: %{{x:,.2f}}<extra></extra>", **common))
    else:
        fig.add_trace(go.Bar(
            x=cats, y=vals,
            hovertemplate=f"<b>%{{x}}</b><br>{name}: %{{y:,.2f}}<extra></extra>", **common))


def _rgba(hex_color, alpha):
    """#RRGGBB → 'rgba(r,g,b,a)' (para rellenos translúcidos del radar)."""
    h = str(hex_color).lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


def dona(data, *, colors=None, height=320, hole=0.55, legend_bottom=True, **kw):
    """Dona (pie con agujero) para composición PARTE-TODO de UNA variable
    categórica con pocas tajadas. `data` = Serie (índice = categorías, valor =
    conteo o %) o dict. `colors` se resuelve como en `barras` (str | lista |
    dict por nombre | None). Plotly calcula el % sobre los valores; el hover
    muestra valor absoluto + %. `legend_bottom=False` pone la leyenda a la
    derecha (útil con etiquetas largas, p. ej. tipos de siniestro).
    """
    s = data if isinstance(data, pd.Series) else pd.Series(data)
    labels = [str(i) for i in s.index]
    vals = [float(v) for v in s.values]
    cmap = _colores(labels, colors)
    fig = go.Figure(go.Pie(
        labels=labels, values=vals, hole=hole, sort=False, direction="clockwise",
        marker=dict(colors=[cmap[ll] for ll in labels],
                    line=dict(color="#FFFFFF", width=1.5)),
        textinfo="percent", textfont=dict(size=12),
        hovertemplate="<b>%{label}</b><br>%{value:,.0f} (%{percent})<extra></extra>"))
    leg = (dict(orientation="h", yanchor="top", y=-0.04, xanchor="center", x=0.5)
           if legend_bottom else
           dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.0))
    estilizar(fig, height=height, showlegend=True, legend=leg, **kw)
    return fig


def radar(data, *, color=None, height=380, range_max=None, ticksuffix="",
          fill=True, **kw):
    """Radar / 'tela de araña' (Scatterpolar) para comparar varias SERIES sobre
    los mismos ejes cuantitativos comparables. `data` = DataFrame: índice = ejes
    (categorías, p. ej. días), columnas = series (p. ej. países). Cierra el
    polígono repitiendo el primer eje. `color` se resuelve como en `barras` (por
    país si las columnas son países). Solo tiene sentido con ejes en la MISMA
    unidad/escala (p. ej. % intra-país).
    """
    df = _df(data)
    cmap = _colores(df.columns, color)
    ejes = [str(i) for i in df.index]
    theta = ejes + ejes[:1]                      # cerrar el anillo
    fig = go.Figure()
    for col in df.columns:
        r = [float(v) for v in df[col].tolist()]
        c = cmap[str(col)]
        fig.add_trace(go.Scatterpolar(
            r=r + r[:1], theta=theta, name=str(col),
            fill="toself" if fill else None,
            fillcolor=_rgba(c, 0.12) if fill else None,
            line=dict(color=c, width=2.4), marker=dict(size=5),
            hovertemplate="%{theta}<br>" + str(col) + ": %{r:,.2f}"
                          + ticksuffix + "<extra></extra>"))
    estilizar(fig, height=height, showlegend=df.shape[1] > 1, **kw)
    fig.update_layout(polar=dict(
        bgcolor="rgba(0,0,0,0)",
        radialaxis=dict(visible=True, gridcolor=GRID, linecolor="#E5E9F0",
                        ticksuffix=ticksuffix,
                        range=[0, range_max] if range_max else None),
        angularaxis=dict(gridcolor=GRID, linecolor="#E5E9F0")))
    return fig


def lineas(data, *, color=None, height=360, x_title="", y_title="", markers=True, **kw):
    """Figura de líneas estilizada que reemplaza a `st.line_chart`.

    `data` es un DataFrame (una línea por columna; el índice va al eje X) o una
    Serie. `color` se resuelve igual que en `barras` (por país si las columnas
    son países).
    """
    df = _df(data)
    cmap = _colores(df.columns, color)
    mode = "lines+markers" if markers else "lines"
    fig = go.Figure()
    for col in df.columns:
        fig.add_trace(go.Scatter(
            x=list(df.index), y=df[col].tolist(), mode=mode, name=str(col),
            line=dict(color=cmap[str(col)], width=2.6), marker=dict(size=6),
            hovertemplate=f"%{{x}}<br>{col}: %{{y:,.2f}}<extra></extra>"))
    estilizar(fig, height=height, xaxis_title=x_title, yaxis_title=y_title,
              showlegend=df.shape[1] > 1, **kw)
    return fig
