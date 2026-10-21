"""
constants.py — Fuente única de verdad visual del dashboard de Siniestros Viales.
Proyecto LIDIA · UTEC ITR Norte 2026.

Centraliza la paleta de severidad (color-blind safe, contraste WCAG AA), las
etiquetas homologadas que ve el usuario, las notas de limitación de datos y los
helpers de formato numérico es-UY. Importado por dashboard/app.py para que las 11
secciones compartan exactamente la misma paleta, etiquetas y formato.

ALCANCE: este módulo toca SOLO la capa de presentación (dashboard/). NO altera el
ETL ni la homologación de origen. En producción la gravedad usa el vocabulario
controlado {fatal, grave, leve, solo_danos}; "solo_danos" unifica dos orígenes
("sin lesionados" de UNASEV-UY y "solo daños materiales" de RENAEST-BR) — la
leyenda usa SIEMPRE el término homologado, nunca el valor crudo de origen.

Sin dependencia de streamlit: solo datos y funciones puras (testeables).
"""

# ── Vocabulario controlado de gravedad (orden canónico de mayor a menor) ─────
GRAVEDADES = ["fatal", "grave", "leve", "solo_danos"]

# ── Paleta de severidad — color-blind safe (Okabe-Ito), contraste WCAG AA ────
# Reemplaza los colores hardcodeados previos (#C00000/#ED7D31/#FFD700/#70AD47).
COLOR_SEVERIDAD = {
    "fatal":      "#9F1D20",   # rojo oscuro
    "grave":      "#E69F00",   # ámbar
    "leve":       "#0072B2",   # azul
    "solo_danos": "#7F7F7F",   # gris neutro
}

# ── Etiquetas homologadas (lo que ve el usuario en leyendas/ejes/tooltips) ────
# Coherente con la Tabla 43 del informe. "solo_danos" → "Sin víctimas (solo daños)".
ETIQUETA_SEVERIDAD = {
    "fatal":      "Fatal",
    "grave":      "Herido grave",
    "leve":       "Herido leve",
    "solo_danos": "Sin víctimas (solo daños)",
}

# ── Países y paleta de país (distinta de la de severidad, también CB-safe) ───
PAISES = ["Uruguay", "Brasil", "España"]
COLOR_PAIS = {
    "Uruguay": "#56B4E9",   # celeste
    "Brasil":  "#009E73",   # verde azulado
    "España":  "#CC79A7",   # magenta
}

# ── Población de referencia (para tasas / 100k hab.) ─────────────────────────
POBLACION = {"Uruguay": 3_499_451, "Brasil": 213_500_000, "España": 49_687_120}

# ── España: región (nombre INE) → código INE de provincia (2 dígitos) ────────
# El ETL (transformer.PROVINCIAS) guarda `region` como el NOMBRE oficial INE de la
# provincia. El choropleth de la página Geográfica matchea contra el GeoJSON
# `dashboard/assets/es_provincias.geojson` por su propiedad `cod_prov` (código INE
# "01".."52"), que es estable aunque el nombre del GeoJSON sea bilingüe
# ("A Coruña", "Illes Balears", "València/Valencia"…). Por eso el match es por
# CÓDIGO, no por nombre.
REGION_A_COD_INE = {
    "Álava": "01", "Albacete": "02", "Alicante": "03", "Almería": "04", "Ávila": "05",
    "Badajoz": "06", "Balears (Illes)": "07", "Barcelona": "08", "Burgos": "09",
    "Cáceres": "10", "Cádiz": "11", "Castellón": "12", "Ciudad Real": "13",
    "Córdoba": "14", "Coruña (A)": "15", "Cuenca": "16", "Girona": "17",
    "Granada": "18", "Guadalajara": "19", "Gipuzkoa": "20", "Huelva": "21",
    "Huesca": "22", "Jaén": "23", "León": "24", "Lleida": "25", "Rioja (La)": "26",
    "Lugo": "27", "Madrid": "28", "Málaga": "29", "Murcia": "30", "Navarra": "31",
    "Ourense": "32", "Asturias": "33", "Palencia": "34", "Palmas (Las)": "35",
    "Pontevedra": "36", "Salamanca": "37", "Santa Cruz de Tenerife": "38",
    "Cantabria": "39", "Segovia": "40", "Sevilla": "41", "Soria": "42",
    "Tarragona": "43", "Teruel": "44", "Toledo": "45", "Valencia": "46",
    "Valladolid": "47", "Bizkaia": "48", "Zamora": "49", "Zaragoza": "50",
    "Ceuta": "51", "Melilla": "52",
}

# ── Brasil: UF (sigla del estado) → macro-región del DW ──────────────────────
# El ETL (transformer.UF_REGIAO) colapsa el estado/UF en una de las 5 macro-regiones
# oficiales del IBGE, así que el almacén SOLO guarda `region` a ese nivel (no los 27
# estados). El choropleth de Brasil usa un GeoJSON de estados (id = properties.sigla)
# y pinta cada estado con el total de SU macro-región: el mapa se ve a nivel estatal
# pero el dato es regional (limitación documentada en la página y el informe).
BR_UF_A_REGION = {
    "AC": "Norte", "AM": "Norte", "AP": "Norte", "PA": "Norte",
    "RO": "Norte", "RR": "Norte", "TO": "Norte",
    "AL": "Nordeste", "BA": "Nordeste", "CE": "Nordeste", "MA": "Nordeste",
    "PB": "Nordeste", "PE": "Nordeste", "PI": "Nordeste", "RN": "Nordeste", "SE": "Nordeste",
    "DF": "Centro-Oeste", "GO": "Centro-Oeste", "MS": "Centro-Oeste", "MT": "Centro-Oeste",
    "ES": "Sudeste", "MG": "Sudeste", "RJ": "Sudeste", "SP": "Sudeste",
    "PR": "Sul", "RS": "Sul", "SC": "Sul",
}

# ── Escala secuencial del mapa de calor, teñida por identidad de país ────────
# Cada coropleta usa una rampa ColorBrewer que evoca el color de país de COLOR_PAIS
# (UY celeste → Blues · BR verde → Greens · ES magenta → Purples). Refuerza la
# identidad cromática del tablero sin perder la lectura "más intenso = más volumen".
ESCALA_MAPA_PAIS = {"Uruguay": "Blues", "Brasil": "Greens", "España": "Purples"}

# ── Plantilla Plotly limpia (sin gridlines pesadas) ──────────────────────────
PLOTLY_TEMPLATE = "plotly_white"

# ── Notas de limitación que el UI DEBE comunicar (trazabilidad / rúbrica D5) ──
NOTA_BRASIL = (
    "**Brasil (RENAEST):** la categoría `grave` no se registra (siempre NULL); "
    "todo herido cae en `leve`, que por tanto sobreestima `{grave ∪ leve}`. "
    "La comparación es por **proporciones intra-país**, nunca por volúmenes absolutos."
)
NOTA_ESPANA = (
    "**España (DGT):** no informa `solo_danos` (los siniestros sin víctimas se "
    "homologan como `leve`) y no tiene coordenadas a nivel de evento "
    "(ubicación derivada de centroides de provincia → 0 % de coordenadas)."
)
NOTA_GEO = (
    "**Cobertura geoespacial = 33,0 % del total** (Uruguay 100 % · Brasil 33,8 % "
    "de coordenadas válidas · España 0 %). El mapa muestra una **muestra**, no el "
    "universo de siniestros."
)
NOTA_RENAEST_2018 = (
    "**Subconteo RENAEST 2018:** los ficheros de Brasil 2018 tienen cobertura "
    "parcial en los primeros meses (749.134 vs 1.031.973 en 2019); cualquier "
    "baseline que incluya 2018 queda artificialmente bajo (§4.3.1)."
)
NOTA_COVID = "Línea vertical en 2020: inicio de la pandemia COVID-19."

# Fuente común al pie de cada visualización.
FUENTE = "**Fuente:** UNASEV (UY) · RENAEST (BR) · DGT (ES), 2018–2025."


# ── Helpers de presentación (puros) ──────────────────────────────────────────
def etiqueta_sev(g):
    """Etiqueta homologada para una clave de gravedad ('fatal' → 'Fatal')."""
    return ETIQUETA_SEVERIDAD.get(g, str(g))


def color_sev(g, fallback="#2E75B6"):
    """Color de severidad para una clave de gravedad."""
    return COLOR_SEVERIDAD.get(g, fallback)


def colores_sev(claves):
    """Lista de colores en el orden de las claves dadas (para color= de charts)."""
    return [color_sev(g) for g in claves]


def etiquetas_sev(claves):
    """Lista de etiquetas homologadas en el orden de las claves dadas."""
    return [etiqueta_sev(g) for g in claves]


def fold_nombre(s):
    """Normaliza un nombre para hacer match laxo: sin acentos, MAYÚSCULAS y sin
    espacios en los extremos. Usado para casar `region` de la BD (p. ej. la BD trae
    ' MONTEVIDEO', 'PAYSANDU' sin tilde) contra el nombre del GeoJSON ('Montevideo',
    'Paysandú') por su forma canónica. Puro: no depende de streamlit."""
    import unicodedata
    s = unicodedata.normalize("NFKD", str(s))
    s = "".join(c for c in s if not unicodedata.combining(c))
    return s.strip().upper()


def hex_to_rgb(h, alpha=None):
    """'#9F1D20' → [159, 29, 32] (o [r,g,b,alpha] si se pasa alpha). Para pydeck."""
    h = h.lstrip("#")
    rgb = [int(h[i:i + 2], 16) for i in (0, 2, 4)]
    return rgb + [alpha] if alpha is not None else rgb


def color_sev_rgb(g, alpha=200, fallback="#2E75B6"):
    """Color de severidad como [r,g,b,alpha] (capa pydeck/ScatterplotLayer)."""
    return hex_to_rgb(COLOR_SEVERIDAD.get(g, fallback), alpha)


# ── Formato numérico es-UY (separador de miles "." y decimal ",") ────────────
def _es(s):
    """Intercambia separadores: formato Python (1,234.5) → es-UY (1.234,5)."""
    return s.replace(",", "§").replace(".", ",").replace("§", ".")


def fmt_int(n):
    """123456 → '123.456' (separador de miles es-UY, sin decimales)."""
    try:
        return _es(f"{int(round(float(n))):,}")
    except (TypeError, ValueError):
        return str(n)


def fmt_num(x, dec=2):
    """1234.5 → '1.234,50' (miles "." y decimal "," con `dec` decimales)."""
    try:
        return _es(f"{float(x):,.{dec}f}")
    except (TypeError, ValueError):
        return str(x)


def fmt_pct(x, dec=1):
    """33.0 → '33,0 %' (número en formato es-UY + símbolo de porcentaje)."""
    return f"{fmt_num(x, dec)} %"
