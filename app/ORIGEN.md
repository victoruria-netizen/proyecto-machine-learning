# Origen del código de `app/`

## Procedencia

- **Repositorio de origen (PID):** https://git.utec.edu.uy/juan.pimentel/siniestros-viales-grp4
- **Commit de origen:** `f803bd6` (dashboard vigente del PID, D66).
- **Copia en este repositorio:** commit `d5d1726` («Copia textual del dashboard del PID (f803bd6) y config.py»).

## Qué se copió y qué no

| Se copió (sin cambios, salvo lo indicado abajo) | No se copió |
| --- | --- |
| `app.py`, `charts.py`, `constants.py`, `ui.py`, `Dockerfile`, `requirements.txt` y `assets/` (capas de países) de `dashboard/` | `librerias/` (dependencias vendorizadas para el servidor del PID) |
| `config.py`, de la raíz del repositorio del PID | `.env` y la carpeta `config/` (credenciales y perfiles de entorno) |

`config.py` calcula `BASE_DIR` como su propia carpeta; al estar en `app/`, `config/` queda en `app/config/`, que no existe.
Sin `.env`, `config.py` usa sus valores por omisión (PostgreSQL y MongoDB en `localhost`), de modo que las páginas
heredadas que consultan bases de datos muestran su error de conexión (D67). Al importarse crea, vacías, `app/data/` y `app/logs/`.

## Cambios al código heredado

Solo en `app/app.py` (D67); ningún otro archivo heredado se modificó. Aparte, hay un archivo de configuración nuevo en la raíz del
repositorio (D80), que no es código heredado:

| Cambio | Motivo |
| --- | --- |
| Entrada `"Predicción (PAA)": "🔮 Predicción (PAA)"` al final de `NAV` | Agregar la pestaña de predicción del PAA |
| `"graph-up-arrow"` al final de `NAV_ICONS` | Ícono de esa entrada (`render_navbar` hoy no usa los íconos; se agrega por coherencia con la lista) |
| Rama `elif pagina == "🔮 Predicción (PAA)":` antes del pie, que importa `pagina_prediccion` y llama a `render()` | Enrutar a la pestaña nueva; el manejo de errores de las páginas heredadas queda igual |
| Archivo nuevo `.streamlit/config.toml` (en la raíz, fuera de `app/`) con `[theme]` `base = "light"` | Con el sistema operativo en modo oscuro, Streamlit pintaba textos, ejes, leyendas, tablas y títulos de los expanders con colores de tema oscuro sobre el fondo claro que fija el CSS heredado, y casi no se leían (reproducido en Chromium con `prefers-color-scheme: dark`). Fijar el tema claro lo evita sin tocar código heredado. Streamlit lo toma solo si se lanza desde la raíz |

## Dependencias

Las que importa `app/` se agregaron a `requirements.txt` del repositorio (fase 5, 2026-10-21): streamlit, plotly, pydeck,
psycopg2-binary, pymongo, SQLAlchemy y python-dotenv. `streamlit-option-menu` no se agregó: `ui.py` ya no lo importa.
`app/requirements.txt` es el del despliegue con Docker del PID y no se modificó (D70).

## Archivos nuevos del PAA en `app/` (no vienen del PID)

- `pagina_prediccion.py`: pestaña «Predicción (PAA)». Lee solo `models/modelo_final.json`, `models/metadata.json`,
  `experiments/evaluacion_final/predicciones_bloque_final.csv` y la capa de abajo; no usa bases de datos ni `config`.
- `assets/municipios_montevideo_simplificado.geojson` (38,8 kB): capa de los 8 municipios de Montevideo para el mapa.
- `servidor/pagina_prediccion_puente.py` (fase 8a): puente para el dashboard del servidor. Se copia allí como `/app/streamlit/pagina_prediccion.py` y carga
  `pagina_prediccion.py` del clon del repositorio; no contiene la pestaña. Procedimiento, diseño y vuelta atrás en `documentacion/despliegue_servidor.md`.
  Es código del PAA; no viene del PID y no usa `charts.py`, `ui.py`, `config.py` ni `constants.py`.

`pagina_prediccion.py` agrega `app/` y la raíz del repositorio **al final** de `sys.path` (antes, al principio), para que en el servidor los `charts.py`, `ui.py`,
`config.py` y `constants.py` del dashboard del PID no queden tapados por los de esta carpeta (fase 8a, paso 1).

### Procedencia y licencia de la capa de municipios

- **Fuente:** GeoServer de la Intendencia de Montevideo, capa `mapstore-tematicas:zon_v_sig_municipios`, consulta WFS `GetFeature` en
  GeoJSON, EPSG:4326 (la consulta completa está en `HANDOFF.md`, sección «Zonificación por municipios y corte de pandemia»).
- **Licencia:** el `GetCapabilities` del servicio declara `Fees: none` y `AccessConstraints: none`.
- **Archivo de partida:** `data/raw/municipios_montevideo.geojson` (no versionado), sha256 `c5d9f651aa6d88d6ff5bb32b831664b5850b275bfe562bed9e68246492c48d4a`
  en la copia usada para esta fase. **Ojo:** `experiments/etl_montevideo/tablas/03b_procedencia_capa_zonas.csv` registra otra huella
  para ese archivo (`ed0ba13e…`); `HANDOFF.md` ya consigna que existió una copia con la huella `c5d9f651…` y que no se sabe en qué difería.
  Los 8 polígonos y sus nombres coinciden; la simplificación no se hizo sobre la copia registrada por el ETL.
- **Transformación:** se conservaron solo el campo `municipio` (con el prefijo `MUNICIPIO `, como en el panel) y la geometría. Se simplificó con
  `geopandas` (`simplify(0.0003, preserve_topology=True)`, unos 30 m), se llevó a una grilla de 5 decimales con `shapely.set_precision(…, 1e-5)` y
  se conservó el polígono de mayor área de cada municipio. Motivo de este último paso: redondear a 5 decimales partió el contorno del
  Municipio CH en un polígono más un fragmento de 5 vértices, y esa forma rompía el armado del mapa; lo detectó `tests/test_pipeline_inferencia.py`.
  Sirve para colorear el mapa, no para medir áreas ni límites.
