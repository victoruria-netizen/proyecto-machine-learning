"""Auditoría de `notebooks/preparacion_montevideo.ipynb` (versión Colab, 2026-09-01).

Reproduce el recorte y la grilla del notebook sobre la copia local del CSV crudo y
comprueba los supuestos que el notebook da por buenos sin verificarlos. Todas las
cifras citadas en HANDOFF.md salen de la salida de este script.

Uso:  python experiments/auditoria_preparacion_montevideo/auditoria.py
"""

import hashlib
from pathlib import Path

import pandas as pd

RAW = Path("data/raw/uru_siniestros_unificado.csv")
DIAS = {0: "LUNES", 1: "MARTES", 2: "MIÉRCOLES", 3: "JUEVES",
        4: "VIERNES", 5: "SÁBADO", 6: "DOMINGO"}


def seccion(titulo):
    print("\n" + "=" * 72)
    print(titulo)
    print("=" * 72)


seccion("0. Procedencia")
print("archivo:", RAW)
print("sha256 :", hashlib.sha256(RAW.read_bytes()).hexdigest())

df = pd.read_csv(RAW)
df.columns = df.columns.str.strip()
fecha_cruda = df["Fecha"].copy()
df["Fecha"] = pd.to_datetime(df["Fecha"], format="%m/%d/%Y", errors="coerce")
for col in ["Departamento", "Localidad", "Gravedad", "Tipo de Siniestro",
            "Calle", "Dia Semana"]:
    df[col] = df[col].astype(str).str.strip()

seccion("1. ¿Es correcto el formato de fecha %m/%d/%Y? (contraste con 'Dia Semana')")
print("filas:", len(df), "| NaT tras parsear:", int(df["Fecha"].isna().sum()))
dia_csv = df["Dia Semana"].str.upper()
coincide_mdy = (dia_csv == df["Fecha"].dt.dayofweek.map(DIAS)).mean()
alt = pd.to_datetime(fecha_cruda, format="%d/%m/%Y", errors="coerce")
coincide_dmy = (dia_csv == alt.dt.dayofweek.map(DIAS)).mean()
print(f"coincidencia con %m/%d/%Y: {100 * coincide_mdy:.4f} %")
print(f"coincidencia con %d/%m/%Y: {100 * coincide_dmy:.4f} % "
      f"(NaT: {int(alt.isna().sum())})")

seccion("2. Recorte del notebook: MONTEVIDEO y Fecha.dt.year > 2020")
f = df[(df["Departamento"] == "MONTEVIDEO") & (df["Fecha"].dt.year > 2020)].copy()
print("registros:", f.shape, "| rango:", f["Fecha"].min().date(), "->",
      f["Fecha"].max().date())
print("\nsiniestros por año:")
print(f.groupby(f["Fecha"].dt.year).size().to_string())
print("\nLocalidad dentro del departamento:")
print(f["Localidad"].value_counts().to_string())

seccion("3. Régimen de movilidad residual de la pandemia dentro del recorte")
tabla = f.groupby([f["Fecha"].dt.month, f["Fecha"].dt.year]).size().unstack()
tabla.index.name = "mes"
print(tabla.to_string())
h1_21 = f[f["Fecha"].between("2021-01-01", "2021-06-30")]
h1_ref = f[(f["Fecha"].dt.month <= 6) & (f["Fecha"].dt.year.between(2022, 2025))]
dias_ref = sum(pd.Timestamp(f"{a}-06-30").dayofyear for a in range(2022, 2026))
print(f"\nmedia diaria ene-jun 2021      : {len(h1_21) / 181:.2f}")
print(f"media diaria ene-jun 2022-2025 : {len(h1_ref) / dias_ref:.2f}")
print(f"caída del primer semestre 2021 : "
      f"{100 * (1 - (len(h1_21) / 181) / (len(h1_ref) / dias_ref)):.1f} %")

seccion("4. Duplicados exactos (el notebook no los trata)")
dups = f.duplicated().sum()
print(f"filas duplicadas: {dups} ({100 * dups / len(f):.2f} % del recorte)")

seccion("5. Grilla de 1 km y panel día × zona")
f["grid_x"] = (f["X"] // 1000) * 1000
f["grid_y"] = (f["Y"] // 1000) * 1000
f["zona_id"] = f["grid_x"].astype(str) + "_" + f["grid_y"].astype(str)
z = f.groupby("zona_id").size().sort_values(ascending=False)
print("zonas:", len(z), "| mediana de siniestros por zona:", int(z.median()))
print("zonas con 1 solo siniestro en 5 años:", int((z == 1).sum()),
      "| con 5 o menos:", int((z <= 5).sum()))
print("zonas que acumulan el 90 % de los siniestros:",
      int((z.cumsum() / z.sum() <= 0.90).sum() + 1))

rango = pd.date_range(f["Fecha"].min(), f["Fecha"].max(), freq="D")
idx = pd.MultiIndex.from_product([rango, z.index], names=["Fecha", "zona_id"])
panel = (f.groupby(["Fecha", "zona_id"]).size()
         .reindex(idx, fill_value=0).reset_index(name="n"))
y = panel["n"]
print(f"\npanel: {len(rango)} días x {len(z)} zonas = {len(panel)} filas")
print(f"suma del objetivo: {int(y.sum())} (recorte: {len(f)})")
print(f"ceros en el panel : {100 * (y == 0).mean():.2f} %  "
      f"(el notebook informa 58,60 %, pero es sólo la zona más activa)")
print(f"media {y.mean():.6f} | varianza {y.var():.6f} | "
      f"índice de dispersión {y.var() / y.mean():.3f}")
print("\ndistribución del objetivo:")
print(y.value_counts().sort_index().to_string())

seccion("6. El máximo del objetivo (11) es un artefacto de duplicados")
celda = f.groupby(["Fecha", "zona_id"]).size().sort_values(ascending=False).index[0]
sub = f[(f["Fecha"] == celda[0]) & (f["zona_id"] == celda[1])]
print("celda:", celda[0].date(), celda[1], "| registros:", len(sub))
print("registros únicos tras eliminar duplicados exactos:",
      len(sub.drop_duplicates()))
print(sub[["Fecha", "Hora", "Calle", "Tipo de Siniestro", "Gravedad", "X", "Y"]]
      .to_string(index=False))

seccion("7. Zona más activa (la que grafica el notebook)")
top = z.index[0]
serie = (f[f["zona_id"] == top].groupby("Fecha").size()
         .reindex(rango, fill_value=0))
print("zona:", top, "| siniestros:", int(serie.sum()))
print(f"días con cero: {int((serie == 0).sum())} de {len(serie)} "
      f"({100 * (serie == 0).mean():.2f} %)")
