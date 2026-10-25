"""Pruebas del pipeline de inferencia del prototipo (fase 5, paso 5c): validación de entradas, carga del modelo, flujo
completo de «Semana posterior al corte» (D77; los nombres internos conservan «proxima_semana») y fidelidad del modo «Histórico» al CSV de la evaluación final.

Sólo prueban la lógica de ``app/pagina_prediccion.py`` (sin interfaz; la interfaz está en ``tests/test_app.py``). No
reentrenan nada y no leen el panel: el modelo exportado y ``predicciones_bloque_final.csv`` son las únicas entradas.
"""

import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from src import datos, modelo as mod

sys.path.insert(0, str(datos.RAIZ / "app"))
import pagina_prediccion as pp                                     # noqa: E402

RUTA_MODELO = datos.RAIZ / "models" / "modelo_final.json"
RUTA_PRED = datos.RAIZ / "experiments" / "evaluacion_final" / "predicciones_bloque_final.csv"
RUTA_SERVIDOR = datos.RAIZ / "documentacion" / "logs" / "servidor_modelo_final" / "prediccion_semana_2026-01-01.csv"


@pytest.fixture(scope="module")
def historico():
    return pp.cargar_historico()


@pytest.fixture(scope="module")
def semana_nueva():
    return pp.predecir_proxima_semana(pp.cargar_modelo_final())


# ------------------------------------------------------------------------------ validación de entradas
def test_validar_semana_acepta_origenes_del_bloque_final(historico):
    disp = pp.origenes_disponibles(historico)
    assert len(disp) == 47 and disp[0] == pd.Timestamp("2025-02-06")
    assert all(pp.validar_semana(o, disp) == o for o in disp)
    assert pp.validar_semana("2025-02-13", disp) == pd.Timestamp("2025-02-13")


@pytest.mark.parametrize("entrada", ["2026-01-01", "2025-02-05", "2025-02-07", "2024-12-31"])
def test_validar_semana_fuera_de_rango_da_mensaje_claro(historico, entrada):
    with pytest.raises(pp.ErrorEntrada, match="fuera del bloque final"):
        pp.validar_semana(entrada, pp.origenes_disponibles(historico))


@pytest.mark.parametrize("entrada", ["no es una fecha", None, pd.NaT])
def test_validar_semana_rechaza_lo_que_no_es_fecha(historico, entrada):
    with pytest.raises(pp.ErrorEntrada):
        pp.validar_semana(entrada, pp.origenes_disponibles(historico))


def test_semana_historica_fuera_de_rango_falla(historico):
    with pytest.raises(pp.ErrorEntrada, match="fuera del bloque final"):
        pp.semana_historica(historico, "2026-01-01")


def test_historico_sin_columnas_falla(tmp_path):
    ruta = tmp_path / "p.csv"
    pd.read_csv(RUTA_PRED).drop(columns=["observado"]).to_csv(ruta, index=False)
    with pytest.raises(pp.ErrorEntrada, match="observado"):
        pp.cargar_historico(ruta)


# --------------------------------------------------------------------------------------- carga de archivos
def test_modelo_ausente_da_error_claro(tmp_path):
    with pytest.raises(pp.ErrorEntrada, match="No se encontró el archivo del modelo"):
        pp.cargar_modelo_final(tmp_path / "no_existe.json")


def test_predicciones_ausentes_dan_error_claro(tmp_path):
    with pytest.raises(pp.ErrorEntrada, match="No se encontró el archivo de predicciones"):
        pp.cargar_historico(tmp_path / "no_existe.csv")


def test_modelo_ilegible_da_error_claro(tmp_path):
    ruta = tmp_path / "m.json"
    ruta.write_text("{ no es json", encoding="utf-8")
    with pytest.raises(pp.ErrorEntrada, match="no se pudo leer"):
        pp.cargar_modelo_final(ruta)
    ruta.write_text('{"modelo": "XGBoost", "coeficientes": {}, "columnas": []}', encoding="utf-8")
    with pytest.raises(pp.ErrorEntrada, match="no se pudo leer"):
        pp.cargar_modelo_final(ruta)


def test_modelo_real_carga():
    m = pp.cargar_modelo_final()
    assert m["modelo"] == "GLM" and m["origen"] == pd.Timestamp("2026-01-01") and len(m["columnas"]) == 15


# ------------------------------------------------------------------------- flujo «Semana posterior al corte»
def test_proxima_semana_es_8_por_7_sin_nulos_ni_negativos(semana_nueva):
    s = semana_nueva
    assert s.shape[0] == 56 and s["municipio"].nunique() == 8 and s["fecha"].nunique() == 7
    assert sorted(s["municipio"].unique()) == mod.MUNICIPIOS
    assert s["fecha"].min() == pd.Timestamp("2026-01-01") and s["fecha"].max() == pd.Timestamp("2026-01-07")
    cols = ["esperado", "inf_80", "sup_80", "inf_95", "sup_95"]
    assert s[cols].notna().all().all() and (s[cols] >= 0).all().all() and (s["esperado"] > 0).all()
    assert ((s["inf_95"] <= s["inf_80"]) & (s["inf_80"] <= s["sup_80"]) & (s["sup_80"] <= s["sup_95"])).all()


def test_proxima_semana_igual_a_la_del_servidor(semana_nueva):
    "Misma comparación que F4-B5 (tests/test_modelo.py): las 56 μ contra el job 136, diferencia relativa <= 1e-6 (D56)."
    servidor = pd.read_csv(RUTA_SERVIDOR, parse_dates=["fecha"]).rename(columns={"zona_id": "municipio"})
    j = semana_nueva.merge(servidor, on=["fecha", "municipio"], suffixes=("", "_servidor"), validate="one_to_one")
    assert len(j) == 56
    assert ((j["esperado"] - j["pred"]).abs() / j["pred"].abs()).max() <= 1e-6


def test_proxima_semana_igual_a_predecir_semana_directo():
    m = mod.cargar_modelo(RUTA_MODELO)
    directo = mod.predecir_semana(m, pp.historia_vacia(), pd.Timestamp("2026-01-01")).rename(
        columns={"zona_id": "municipio", "pred": "esperado"})
    pd.testing.assert_frame_equal(pp.predecir_proxima_semana(m), directo)


def test_modelo_no_predice_otra_semana():
    m = pp.cargar_modelo_final()
    with pytest.raises(ValueError, match="predice desde"):
        mod.predecir_semana(m, pp.historia_vacia(), pd.Timestamp("2026-01-08"))


# ------------------------------------------------------------------------------------------ modo «Histórico»
def test_historico_tiene_47_semanas_completas(historico):
    assert len(historico) == 47 * 56 and set(historico["papel"]) == {pp.PAPEL_SOLUCION}
    assert (historico.groupby("origen").size() == 56).all()


def test_semana_historica_coincide_fila_a_fila_con_el_csv(historico):
    "Cada una de las 47 semanas: mismas filas y valores (sin recalcular), leyendo el CSV por separado con pandas."
    crudo = pd.read_csv(RUTA_PRED, parse_dates=["fecha", "origen"])
    crudo = crudo[crudo["papel"] == "solución"]
    for o in pp.origenes_disponibles(historico):
        s = pp.semana_historica(historico, o)
        esperado = crudo[crudo["origen"] == o].sort_values(["fecha", "municipio"]).reset_index(drop=True)
        assert len(s) == len(esperado) == 56
        for c_pag, c_csv in (("fecha", "fecha"), ("municipio", "municipio"), ("esperado", "predicho"),
                             ("observado", "observado"), ("inf_80", "inf_80"), ("sup_80", "sup_80"),
                             ("inf_95", "inf_95"), ("sup_95", "sup_95")):
            assert (s[c_pag].to_numpy() == esperado[c_csv].to_numpy()).all(), (o, c_pag)


def test_resumen_por_municipio_suma_los_dias(historico):
    s = pp.semana_historica(historico, "2025-02-06")
    r = pp.resumen_por_municipio(s)
    assert list(r.index) == mod.MUNICIPIOS and np.isclose(r["observado"].sum(), s["observado"].sum())


# --------------------------------------------------------------------------------------------------- mapa
def test_datos_del_mapa_traen_los_8_municipios():
    capa = json.loads(pp.RUTA_CAPA.read_text(encoding="utf-8"))
    valores = pd.Series(np.arange(8, dtype=float), index=mod.MUNICIPIOS)
    df = pp.datos_mapa(valores, capa)
    assert sorted(df["municipio"]) == mod.MUNICIPIOS and df["polygon"].map(len).min() > 3
    assert df["color"].map(len).eq(4).all()


def test_datos_del_mapa_rechaza_municipio_ajeno():
    capa = {"features": [{"properties": {"municipio": "MUNICIPIO Z"}, "geometry": {"coordinates": [[]]}}]}
    with pytest.raises(pp.ErrorEntrada, match="MUNICIPIO Z"):
        pp.datos_mapa(pd.Series([1.0], index=["MUNICIPIO A"]), capa)


# ------------------------------------------------------------------------------- sin bases de datos (D67)
def test_la_pestana_no_importa_bases_de_datos_ni_config():
    codigo = ("import sys; sys.path.insert(0, 'app'); import pagina_prediccion; "
              "malos = [m for m in ('psycopg2', 'pymongo', 'sqlalchemy', 'config') if m in sys.modules]; "
              "print(malos); sys.exit(1 if malos else 0)")
    r = subprocess.run([sys.executable, "-c", codigo], cwd=datos.RAIZ, capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr


# ------------------------------------------------- métricas descriptivas del paso 5b (D79): contra las tablas de la evaluación final
TABLAS = datos.RAIZ / "experiments" / "evaluacion_final" / "tablas"
RUTA_METADATA = datos.RAIZ / "models" / "metadata.json"
SOLUCION = "GLM Poisson (a) [deslizante 364 d]"


@pytest.fixture(scope="module")
def referencia():
    return pp.cargar_referencia()


def test_desvianza_global_coincide_con_la_tabla_06(historico, referencia):
    "La desvianza global que calcula la app coincide con tablas/06 (6 decimales; tolerancia 6e-7 por el redondeo) y gana 33 semanas."
    t = pd.read_csv(TABLAS / "06_globales.csv").set_index("modelo")
    ref = t.index[t.index.str.startswith("L1")][0]
    c = pp.comparacion_global(historico, referencia)
    assert t.loc[SOLUCION, "desvianza"] == pytest.approx(1.106342) and t.loc[ref, "desvianza"] == pytest.approx(1.135861)
    assert abs(c["solucion"] - t.loc[SOLUCION, "desvianza"]) < 6e-7
    assert abs(c["referencia"] - t.loc[ref, "desvianza"]) < 6e-7
    assert c["semanas_menor"] == int(t.loc[SOLUCION, "cortes_que_gana_a_su_referencia"]) == 33
    assert c["semanas"] == 47


@pytest.mark.parametrize("quien", ["solucion", "referencia"])
def test_desvianza_de_cada_semana_coincide_con_la_tabla_08(historico, referencia, quien):
    "En los 47 cortes, la desvianza de la semana coincide con desvianza_poisson de tablas/08 (diferencia máxima esperada ~5,2e-7)."
    t = pd.read_csv(TABLAS / "08_por_corte.csv", parse_dates=["origen"])
    df, nombre = (historico, SOLUCION) if quien == "solucion" else (referencia, referencia["modelo"].iloc[0])
    esperado = t[t["modelo"] == nombre].set_index("origen")["desvianza_poisson"]
    calculada = pp.desvianza_por_semana(df)
    assert len(esperado) == len(calculada) == 47
    assert (calculada.index.sort_values() == esperado.index.sort_values()).all()
    assert (calculada - esperado.reindex(calculada.index)).abs().max() < 6e-7


def test_desvianza_reemplaza_predicciones_no_positivas_por_1e_6():
    d = pp.desvianza_poisson([0, 2, 3], [0.0, -1.0, 3.0])
    assert d[0] == pytest.approx(2e-6)                               # y=0: 2·μ con μ=1e-6
    assert d[1] == pytest.approx(2 * (2 * np.log(2 / 1e-6) - (2 - 1e-6)))
    assert d[2] == pytest.approx(0.0)


@pytest.mark.parametrize("nivel", [80, 95])
def test_filas_fuera_del_intervalo_coinciden_con_la_tabla_17(historico, nivel):
    "Filas fuera del intervalo = (debajo + encima) × n de la fila «todos» de tablas/17 (intervalo NB2, el de la solución)."
    assert len(historico) == 2632
    t = pd.read_csv(TABLAS / "17_cobertura_intervalos.csv")
    tipo = historico["tipo_intervalo"].iloc[0]                       # NB2: la tabla trae también el Poisson
    fila = t[(t["municipio"] == "todos") & (t["nivel_nominal"] == nivel) & t["intervalo"].str.startswith(tipo)]
    assert len(fila) == 1
    esperado = (fila["debajo"].iloc[0] + fila["encima"].iloc[0]) * fila["n"].iloc[0]
    assert fila["n"].iloc[0] == len(historico)
    assert pp.fuera_del_intervalo(historico, nivel).sum() == pytest.approx(esperado, abs=0.5)


def test_totales_semanales_traen_47_semanas_y_l1(historico, referencia):
    t = pp.totales_semanales(historico, referencia)
    assert t.shape == (47, 3) and list(t.columns) == ["Observado", "Solución", "L1"]
    assert t["Observado"].sum() == historico["observado"].sum()
    assert list(pp.totales_semanales(historico, None).columns) == ["Observado", "Solución"]


# ------------------------------------------------------------------------------------- ficha del modelo (sha256 en vivo)
def test_ficha_del_modelo_con_los_archivos_reales_coincide():
    f = pp.ficha_modelo()
    assert f["coincide"] and f["sha256_calculado"] == f["sha256_metadata"]
    assert f["ventana_dias"] == 364 and f["reentrenamiento_cada_dias"] == 7 and len(f["variables"]) == 15
    assert f["desde"] == "2025-01-02" and f["hasta"] == "2025-12-31" and f["filas"] == 2912


def test_ficha_del_modelo_con_metadata_alterado_no_coincide(tmp_path):
    meta = json.loads(RUTA_METADATA.read_text(encoding="utf-8"))
    meta["sha256_modelo"] = "0" * 64
    ruta = tmp_path / "metadata.json"
    ruta.write_text(json.dumps(meta), encoding="utf-8")
    f = pp.ficha_modelo(RUTA_MODELO, ruta)
    assert not f["coincide"] and f["sha256_calculado"] != f["sha256_metadata"]


def test_ficha_del_modelo_con_modelo_alterado_no_coincide(tmp_path):
    ruta = tmp_path / "modelo_final.json"
    ruta.write_bytes(RUTA_MODELO.read_bytes() + b" ")
    assert not pp.ficha_modelo(ruta, RUTA_METADATA)["coincide"]


def test_ficha_del_modelo_con_archivo_ausente_da_error_claro(tmp_path):
    with pytest.raises(pp.ErrorEntrada, match="No se encontró la ficha del modelo"):
        pp.ficha_modelo(RUTA_MODELO, tmp_path / "no_esta.json")
    with pytest.raises(pp.ErrorEntrada, match="No se encontró el archivo del modelo"):
        pp.ficha_modelo(tmp_path / "no_esta.json", RUTA_METADATA)


def test_ficha_del_modelo_con_metadata_ilegible_da_error_claro(tmp_path):
    ruta = tmp_path / "metadata.json"
    ruta.write_text('{"configuracion": {}}', encoding="utf-8")
    with pytest.raises(pp.ErrorEntrada, match="no se pudo leer"):
        pp.ficha_modelo(RUTA_MODELO, ruta)


# --------------------------------------------------------------------------------------- etiquetas del mapa
def _dentro(punto, anillo):
    "Punto en polígono por conteo de cruces."
    x, y = punto
    dentro = False
    for (x0, y0), (x1, y1) in zip(anillo, anillo[1:] + anillo[:1]):
        if (y0 > y) != (y1 > y) and x < (x1 - x0) * (y - y0) / (y1 - y0) + x0:
            dentro = not dentro
    return dentro


def test_etiquetas_del_mapa_son_8_y_caen_dentro_de_la_capa():
    capa = json.loads(pp.RUTA_CAPA.read_text(encoding="utf-8"))
    valores = pd.Series(np.arange(8, dtype=float) + 0.25, index=mod.MUNICIPIOS)
    et = pp.etiquetas_mapa(valores, capa)
    assert len(et) == 8 and sorted(et["municipio"]) == mod.MUNICIPIOS
    puntos = [p for f in capa["features"] for a in pp._contornos(f) for p in a]
    lon_min, lon_max = min(p[0] for p in puntos), max(p[0] for p in puntos)
    lat_min, lat_max = min(p[1] for p in puntos), max(p[1] for p in puntos)
    contornos = {f["properties"]["municipio"]: pp._contornos(f) for f in capa["features"]}
    for _, e in et.iterrows():
        lon, lat = e["posicion"]
        assert lon_min <= lon <= lon_max and lat_min <= lat <= lat_max
        assert any(_dentro((lon, lat), a) for a in contornos[e["municipio"]]), e["municipio"]   # y en su propio municipio


def test_etiquetas_del_mapa_son_letra_y_valor_en_dos_lineas_con_coma_decimal():
    capa = json.loads(pp.RUTA_CAPA.read_text(encoding="utf-8"))
    et = pp.etiquetas_mapa(pd.Series(12.34, index=mod.MUNICIPIOS), capa).set_index("municipio")
    assert et.loc["MUNICIPIO CH", "texto"] == "CH\n12,3" and et.loc["MUNICIPIO A", "texto"] == "A\n12,3"


def test_etiquetas_del_mapa_rechazan_municipio_ajeno():
    capa = {"features": [{"properties": {"municipio": "MUNICIPIO Z"}, "geometry": {"type": "Polygon", "coordinates": [[]]}}]}
    with pytest.raises(pp.ErrorEntrada, match="MUNICIPIO Z"):
        pp.etiquetas_mapa(pd.Series([1.0], index=["MUNICIPIO A"]), capa)


def test_centroide_usa_el_area_con_signo_y_el_contorno_mas_grande():
    cuadrado = [[0, 0], [2, 0], [2, 2], [0, 2]]
    area, centro = pp._area_y_centroide(cuadrado)
    assert area == pytest.approx(4.0) and centro == pytest.approx([1.0, 1.0])
    area_h, centro_h = pp._area_y_centroide(cuadrado[::-1])           # sentido horario: área negativa, mismo centroide
    assert area_h == pytest.approx(-4.0) and centro_h == pytest.approx([1.0, 1.0])
    capa = {"features": [{"properties": {"municipio": "MUNICIPIO A"}, "geometry": {"type": "MultiPolygon", "coordinates": [
        [[[10, 10], [10.1, 10], [10.1, 10.1]]], [cuadrado]]}}]}
    et = pp.etiquetas_mapa(pd.Series([1.0], index=["MUNICIPIO A"]), capa)
    assert et["posicion"].iloc[0] == pytest.approx([1.0, 1.0])


# ------------------------------------------------------------------------------------------------ referencia L1
def test_sin_l1_en_el_csv_da_error_claro(tmp_path):
    ruta = tmp_path / "sin_l1.csv"
    crudo = pd.read_csv(RUTA_PRED)
    crudo[~crudo["modelo"].str.startswith("L1")].to_csv(ruta, index=False)
    with pytest.raises(pp.ErrorEntrada, match="referencia L1"):
        pp.cargar_referencia(ruta)
    assert len(pp.cargar_historico(ruta)) == 2632                       # lo demás sigue funcionando


def test_referencia_real_es_l1_con_47_semanas(referencia):
    assert len(referencia) == 2632 and referencia["modelo"].str.startswith("L1").all() and set(referencia["papel"]) == {"referencia"}


def test_referencia_ausente_da_error_claro(tmp_path):
    with pytest.raises(pp.ErrorEntrada, match="No se encontró el archivo de predicciones"):
        pp.cargar_referencia(tmp_path / "no_existe.csv")


# ------------------------------------------------------------------------------------------------------- F5-N4
def test_f5_n4_el_codigo_de_la_pestana_no_habla_de_riesgo_ni_de_donde_ocurrira():
    fuente = Path(pp.__file__).read_text(encoding="utf-8").lower()
    for prohibida in ("riesgo", "peligros", "dónde ocurrirá"):
        assert prohibida not in fuente, prohibida
