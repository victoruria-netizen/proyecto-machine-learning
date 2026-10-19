"""Variables predictoras del Entregable 3: única implementación para los notebooks y el prototipo.

Convención de ``origen``: es el **primer día a predecir**. Lo observado al momento de predecir es
todo lo que tiene ``fecha < origen``; el horizonte son los ``HORIZONTE`` días desde el origen.
Toda lectura de ``n_siniestros`` pasa por ``observado()``, que es la única compuerta: ninguna
función de este módulo mira el objetivo de un día >= origen.

Qué usa cada variable y cuándo se conoce:

* calendario de 8 niveles, indicador de A y su término de calendario: se derivan de ``fecha`` y
  ``tipo_dia`` (los feriados se conocen de antemano);
* nivel del municipio, nivel reciente y rezagos: sólo de ``n_siniestros`` anterior al origen.

Sin lluvia: se descartó antes de ejecutar (2026-10-14). La lluvia del día a predecir no está
disponible con un horizonte de 7 días (sólo existiría un pronóstico) y el diagnóstico no le
encontró aporte fuera de muestra (resumen_diagnostico_municipios.md, §7.5). No hay función ni
columna de lluvia en este módulo.
"""

import numpy as np
import pandas as pd

HORIZONTE = 7
REZAGOS = (7, 14, 21, 28)
NIVELES_RECIENTES = (28, 56, 91)

DIAS_SEMANA = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
NIVELES_CALENDARIO = DIAS_SEMANA + ["feriado"]
ZONA_A = "MUNICIPIO A"
_TIPOS_DIA = {"entre_semana", "fin_semana", "feriado"}

COLUMNAS_A_X_CALENDARIO = [f"a_x_{n}" for n in NIVELES_CALENDARIO]


def observado(panel: pd.DataFrame, origen) -> pd.DataFrame:
    """Filas del panel anteriores al origen (``fecha < origen``): lo que se conoce al predecir."""
    return panel[panel["fecha"] < pd.Timestamp(origen)]


def _serie_diaria(obs: pd.DataFrame) -> pd.DataFrame:
    """Matriz día x municipio del objetivo, a calendario diario completo (huecos -> NaN)."""
    y = obs.pivot(index="fecha", columns="zona_id", values="n_siniestros").astype(float)
    return y.reindex(pd.date_range(y.index.min(), y.index.max(), freq="D"))


# --------------------------------------------------------------------------------------- calendario
def calendario_8(panel: pd.DataFrame) -> pd.Series:
    """Calendario de 8 niveles: lunes ... domingo, más feriado.

    Se deriva de ``fecha``; el feriado sale de ``tipo_dia`` del ETL y **tiene prioridad** sobre el
    día de la semana (un feriado en martes es ``feriado``, no ``martes``). Devuelve una categórica
    ordenada con ``NIVELES_CALENDARIO``, alineada con el índice de ``panel``.
    """
    tipo = panel["tipo_dia"]
    desconocidos = set(tipo.unique()) - _TIPOS_DIA
    if desconocidos:
        raise ValueError(f"tipo_dia con valores no previstos: {sorted(desconocidos)}")
    dia = pd.Series(panel["fecha"].dt.dayofweek.map(dict(enumerate(DIAS_SEMANA))), index=panel.index)
    nivel = dia.where(tipo != "feriado", "feriado")
    return pd.Series(pd.Categorical(nivel, categories=NIVELES_CALENDARIO, ordered=True), index=panel.index)


# ------------------------------------------------------------------------------------------- niveles
def nivel_municipio(panel: pd.DataFrame, origen, dias_ventana: int | None = None) -> pd.Series:
    """Media de ``n_siniestros`` de cada municipio en la ventana de entrenamiento.

    La ventana son los días ``[origen - dias_ventana, origen)``; con ``dias_ventana=None`` es la
    expansiva (todo lo observado). Devuelve una Serie indexada por ``zona_id``.
    """
    obs = observado(panel, origen)
    if dias_ventana is not None:
        obs = obs[obs["fecha"] >= pd.Timestamp(origen) - pd.Timedelta(days=dias_ventana)]
    return obs.groupby("zona_id")["n_siniestros"].mean().rename("nivel_municipio")


def nivel_reciente(panel: pd.DataFrame, origen, n: int) -> pd.Series:
    """Media de cada municipio en los últimos ``n`` días antes del origen.

    Queda fijo para los días del horizonte. Si no hay ``n`` días completos de historia devuelve
    NaN (una ventana parcial sería otro estadístico). Serie indexada por ``zona_id``.
    """
    origen = pd.Timestamp(origen)
    ventana = observado(panel, origen)
    ventana = ventana[ventana["fecha"] >= origen - pd.Timedelta(days=n)]
    n_dias = ventana["fecha"].nunique()
    media = ventana.groupby("zona_id")["n_siniestros"].mean()
    if n_dias < n:
        media[:] = np.nan
    return media.rename(f"nivel_reciente_{n}")


# -------------------------------------------------------------------------------------------- rezagos
def rezagos(panel: pd.DataFrame, origen, fechas, lags=REZAGOS) -> pd.DataFrame:
    """Rezagos observados ``y(d - k)`` para cada día objetivo ``d`` en ``fechas`` y cada ``k``.

    Con horizonte de 7 días y ``k >= 7`` el rezago siempre es anterior al origen, así que no hay
    recursión: si algún ``d - k`` cayera en el origen o después, se levanta ``ValueError`` en vez
    de leer un dato que no se tendría. Devuelve columnas ``fecha``, ``zona_id`` y ``rezago_k``;
    NaN donde ``d - k`` es anterior al comienzo del panel.
    """
    origen = pd.Timestamp(origen)
    fechas = pd.DatetimeIndex(fechas)
    y = _serie_diaria(observado(panel, origen))
    salida = []
    for k in lags:
        previas = fechas - pd.Timedelta(days=k)
        if (previas >= origen).any():
            raise ValueError(f"el rezago {k} de algún día objetivo cae en el origen o después")
        bloque = y.reindex(previas)
        bloque.index = fechas
        largo = bloque.stack(future_stack=True).rename(f"rezago_{k}")
        largo.index.names = ["fecha", "zona_id"]
        salida.append(largo)
    return pd.concat(salida, axis=1).reset_index()


# ------------------------------------------------------------------------------------------ municipio A
def indicador_a(zona_id: pd.Series) -> pd.Series:
    """1 si el municipio es A, 0 si no."""
    return (zona_id == ZONA_A).astype(int).rename("es_a")


def termino_calendario_a(calendario: pd.Series, zona_id: pd.Series) -> pd.DataFrame:
    """Término propio de calendario para A: 8 columnas ``a_x_<nivel>``, 1 sólo en A y su nivel.

    Con el calendario común y ``es_a`` en el modelo, deja a A un perfil semanal propio sin
    separar su modelo. El modelo que las use debe omitir una columna (colinealidad con ``es_a``).
    """
    es_a = (zona_id == ZONA_A).to_numpy()
    cols = {f"a_x_{n}": (es_a & (calendario == n).to_numpy()).astype(int) for n in NIVELES_CALENDARIO}
    return pd.DataFrame(cols, index=calendario.index)


# ------------------------------------------------------------------------------------ armado conjunto
def _agregar_fijas(base: pd.DataFrame, panel: pd.DataFrame) -> pd.DataFrame:
    """Calendario, indicador de A y su término de calendario, para las filas de ``base``."""
    base = base.merge(panel[["fecha", "zona_id", "tipo_dia"]], on=["fecha", "zona_id"], how="left",
                      validate="one_to_one")
    base["calendario"] = calendario_8(base)
    base["es_a"] = indicador_a(base["zona_id"])
    base = pd.concat([base, termino_calendario_a(base["calendario"], base["zona_id"])], axis=1)
    return base.drop(columns="tipo_dia")


def variables_horizonte(panel: pd.DataFrame, origen, horizonte: int = HORIZONTE,
                        dias_ventana: int | None = None, lags=REZAGOS, niveles=NIVELES_RECIENTES) -> pd.DataFrame:
    """Todas las variables para los ``horizonte`` días desde el origen, un renglón por (día, municipio).

    Columnas: ``fecha``, ``zona_id``, ``calendario``, ``es_a``, ``a_x_*`` (8), ``nivel_municipio``,
    ``nivel_reciente_<N>`` y ``rezago_<k>``. No incluye el objetivo. Ordenado por
    fecha y municipio. Los días objetivo deben estar en el panel (``tipo_dia``).
    """
    origen = pd.Timestamp(origen)
    dias = pd.date_range(origen, periods=horizonte, freq="D")
    zonas = sorted(panel["zona_id"].unique())
    base = pd.MultiIndex.from_product([dias, zonas], names=["fecha", "zona_id"]).to_frame(index=False)
    base = _agregar_fijas(base, panel)
    base["nivel_municipio"] = base["zona_id"].map(nivel_municipio(panel, origen, dias_ventana))
    for n in niveles:
        base[f"nivel_reciente_{n}"] = base["zona_id"].map(nivel_reciente(panel, origen, n))
    base = base.merge(rezagos(panel, origen, dias, lags), on=["fecha", "zona_id"], how="left", validate="one_to_one")
    return base.sort_values(["fecha", "zona_id"]).reset_index(drop=True)


def matriz_entrenamiento(panel: pd.DataFrame, origen, horizonte: int = HORIZONTE,
                         dias_ventana: int | None = None, lags=REZAGOS, niveles=NIVELES_RECIENTES,
                         solo_completas: bool = True) -> pd.DataFrame:
    """Filas de entrenamiento con las mismas variables que ``variables_horizonte``, más ``n_siniestros``.

    Los días objetivo son ``[origen - dias_ventana, origen)`` (todo lo observado si es ``None``).
    Para que el entrenamiento se parezca a la predicción, cada día ``d`` usa el nivel reciente de
    su **origen simulado**: los bloques de ``horizonte`` días se alinean hacia atrás desde el
    origen real, y ``d`` toma el nivel reciente medido en el comienzo de su bloque (a lo sumo
    ``d``, siempre < origen). Los rezagos son ``y(d - k)``, también anteriores a ese origen
    simulado. Nada depende de un dato >= origen.

    ``nivel_municipio`` es el de la ventana completa (una constante por municipio, como en la
    predicción); con ella el objetivo propio entra a su propia media, un sesgo menor a 1/1.316 por
    día que es el de cualquier efecto fijo por municipio.

    Con ``solo_completas=True`` se descartan las filas con algún NaN en una variable (los primeros
    días del panel, sin historia para el rezago o el nivel reciente más largos). Se aplica a
    **todas** las variables a la vez, así que las filas son las mismas para cualquier subconjunto.
    """
    origen = pd.Timestamp(origen)
    obs = observado(panel, origen)
    inicio = obs["fecha"].min() if dias_ventana is None else origen - pd.Timedelta(days=dias_ventana)
    dias = pd.date_range(max(inicio, obs["fecha"].min()), origen - pd.Timedelta(days=1), freq="D")
    zonas = sorted(panel["zona_id"].unique())

    base = pd.MultiIndex.from_product([dias, zonas], names=["fecha", "zona_id"]).to_frame(index=False)
    base = _agregar_fijas(base, panel)
    base = base.merge(obs[["fecha", "zona_id", "n_siniestros"]], on=["fecha", "zona_id"], how="left", validate="one_to_one")
    base["nivel_municipio"] = base["zona_id"].map(nivel_municipio(panel, origen, dias_ventana))

    y = _serie_diaria(obs)
    # origen simulado de cada día: bloques de `horizonte` días alineados hacia atrás desde el origen
    atras = (origen - dias).days.to_numpy()
    origen_sim = origen - pd.to_timedelta(horizonte * np.ceil(atras / horizonte), unit="D")
    sim_por_dia = pd.Series(origen_sim, index=dias)
    base["_origen_sim"] = base["fecha"].map(sim_por_dia)

    for n in niveles:
        # media de los n días previos a cada fecha o: rolling terminado en o-1
        media = y.rolling(n, min_periods=n).mean().shift(1)
        largo = media.stack(future_stack=True).rename("v")
        largo.index.names = ["_origen_sim", "zona_id"]
        base = base.merge(largo.reset_index().rename(columns={"v": f"nivel_reciente_{n}"}),
                          on=["_origen_sim", "zona_id"], how="left")
    for k in lags:
        previa = y.shift(k)
        largo = previa.stack(future_stack=True).rename(f"rezago_{k}")
        largo.index.names = ["fecha", "zona_id"]
        base = base.merge(largo.reset_index(), on=["fecha", "zona_id"], how="left")

    base = base.drop(columns="_origen_sim").sort_values(["fecha", "zona_id"]).reset_index(drop=True)
    if solo_completas:
        base = base.dropna().reset_index(drop=True)
    return base
