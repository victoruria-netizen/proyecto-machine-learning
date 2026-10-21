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

Solo en `app/app.py` (D67); ningún otro archivo heredado se modificó.

| Cambio | Motivo |
| --- | --- |
| Entrada `"Predicción (PAA)": "🔮 Predicción (PAA)"` al final de `NAV` | Agregar la pestaña de predicción del PAA |
| `"graph-up-arrow"` al final de `NAV_ICONS` | Ícono de esa entrada (`render_navbar` hoy no usa los íconos; se agrega por coherencia con la lista) |
| Rama `elif pagina == "🔮 Predicción (PAA)":` antes del pie, que importa `pagina_prediccion` y llama a `render()` | Enrutar a la pestaña nueva; el manejo de errores de las páginas heredadas queda igual |

## Dependencias

Las que importa `app/` se agregaron a `requirements.txt` del repositorio (fase 5, 2026-10-21): streamlit, plotly, pydeck,
psycopg2-binary, pymongo, SQLAlchemy y python-dotenv. `streamlit-option-menu` no se agregó: `ui.py` ya no lo importa.
`app/requirements.txt` es el del despliegue con Docker del PID y no se modificó (D70).
