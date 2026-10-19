"""Carga del panel diario del ETL, con el bloque final (test) descartado al leer.

El bloque final (2025-02-06 -> 2025-12-31) es el futuro del proyecto: se reserva para evaluar
la solución ya seleccionada y no se lee en ningún código de desarrollo. El límite sale del
calendario (80 % de los días del período), no de los datos, igual que en
notebooks/diagnostico_municipios.ipynb.
"""

from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
RUTA_PANEL = RAIZ / "data" / "processed" / "panel_diario_montevideo.csv"

FECHA_INICIO = pd.Timestamp("2021-07-01")
FECHA_FIN_PERIODO = pd.Timestamp("2025-12-31")
FRAC_DESARROLLO = 0.80

_DIAS_TOTAL = pd.date_range(FECHA_INICIO, FECHA_FIN_PERIODO, freq="D")
N_TOTAL = len(_DIAS_TOTAL)                                  # 1.645
N_DESARROLLO = int(round(FRAC_DESARROLLO * N_TOTAL))        # 1.316
ULTIMO_DIA_DESARROLLO = _DIAS_TOTAL[N_DESARROLLO - 1]       # 2025-02-05
PRIMER_DIA_TEST = _DIAS_TOTAL[N_DESARROLLO]                 # 2025-02-06 (no se lee)

N_MUNICIPIOS = 8


def cargar_panel_desarrollo(ruta=RUTA_PANEL) -> pd.DataFrame:
    """Lee el panel (fecha x municipio) y devuelve sólo el bloque de desarrollo.

    El archivo se lee por tramos y cada tramo se recorta a ``fecha <= ULTIMO_DIA_DESARROLLO``
    antes de acumularse: ninguna fila del test se conserva ni se acumula; cada tramo se lee y se
    filtra antes de acumularse. Un ``assert`` verifica que no sobrevivió ninguna y que el panel
    está completo (1.316 días x 8 municipios, sin pares repetidos).

    Devuelve un DataFrame con ``fecha`` (datetime64) y ``zona_id`` como columnas, ordenado por
    ambas.
    """
    tramos = []
    for tramo in pd.read_csv(ruta, encoding="utf-8", chunksize=2_000):
        tramo["fecha"] = pd.to_datetime(tramo["fecha"], format="%Y-%m-%d")  # ISO: formato fijo
        tramos.append(tramo[tramo["fecha"] <= ULTIMO_DIA_DESARROLLO])
    panel = pd.concat(tramos, ignore_index=True)
    panel = panel.sort_values(["fecha", "zona_id"]).reset_index(drop=True)

    assert not (panel["fecha"] > ULTIMO_DIA_DESARROLLO).any(), "quedaron filas del bloque final"
    assert panel["fecha"].max() == ULTIMO_DIA_DESARROLLO, "el panel no llega al último día de desarrollo"
    assert panel["fecha"].min() == FECHA_INICIO, "el panel no empieza en FECHA_INICIO"
    assert panel["zona_id"].nunique() == N_MUNICIPIOS, panel["zona_id"].unique()
    assert not panel.duplicated(["fecha", "zona_id"]).any(), "hay pares (fecha, municipio) repetidos"
    assert len(panel) == N_DESARROLLO * N_MUNICIPIOS, len(panel)
    return panel
