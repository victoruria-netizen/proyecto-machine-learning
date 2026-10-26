# Despliegue de la pestaña «Predicción (PAA)» en el dashboard del servidor (Entregable 3, fase 8a)

**Qué es.** El procedimiento para que la pestaña «Predicción (PAA)» corra dentro del dashboard que ya está en el servidor institucional, junto
a las páginas del PID, sin reemplazar nada de lo que ese dashboard tiene.
**Código que lo hace posible:** `app/servidor/pagina_prediccion_puente.py` (el puente) y el manejo de `sys.path` de `app/pagina_prediccion.py`.
**Pruebas:** `tests/test_servidor.py` y la sección 7 de `documentacion/pruebas_pipeline.md`.
**Fecha:** 26/10/2026. **Quién lo ejecuta:** el equipo, en la terminal de Jupyter del servidor.

## 1. Cómo usar este documento

- Los comandos de la sección 4 van **de a uno por línea** y se pegan **uno por vez**: la terminal de Jupyter se traba si se pegan varias líneas juntas.
- Nada de lo que está acá se ejecutó todavía en el servidor. Lo único verificado son las pruebas automáticas (sección 5); el resultado de la prueba
  en el servidor se registra en la sección 6.
- Los comandos de la sección 4 asumen las rutas del diagnóstico del 26/10 (sección 2). Si alguna cambió, detenerse y avisar.

## 2. Diagnóstico del servidor (26/10/2026)

Leído desde la propia pestaña de diagnóstico que estaba instalada, no desde una terminal.

| Qué | Valor |
| --- | --- |
| Programa del dashboard | `/app/streamlit/app.py`, con Python **3.11.15** y directorio de trabajo `/app` |
| `sys.path`, en orden | `/app/streamlit`, `/app`, `/app/streamlit/librerias`, `site-packages` |
| En `site-packages` | streamlit 1.56.0, pandas 3.0.2, numpy 2.4.4 |
| En `/app/streamlit/librerias/` | plotly 5.22.0, pydeck 0.9.1, SQLAlchemy 2.0.36, python-dotenv 1.0.1, streamlit-option-menu 0.3.6 |
| No están | scipy, holidays |
| Páginas del PID | `app.py`, `charts.py` y `ui.py` del servidor son una **versión anterior** del PID, distinta de la de `app/` de este repositorio. `charts.py` y `ui.py` tienen `estilizar`, `barras`, `lineas` y `hero` con la misma firma que usa la pestaña |
| `app.py` del servidor | Ya tiene las tres líneas que enrutan a la pestaña e importa `pagina_prediccion` desde `/app/streamlit` |
| Clon de este repositorio | `/app/proyecto-machine-learning`; el dashboard lo ve |
| Respaldo previo | `/app/Respaldo/streamlit_20261026` |

**Lo que el diagnóstico no dice.** No hay evidencia de que exista un paquete o módulo `src` en alguna carpeta de `sys.path` anterior al clon. Si existiera,
taparía el `src` de este repositorio; el puente lo detecta (secciones 3.1 y 3.6).

## 3. Diseño

### 3.1 Un puente en vez de copiar la pestaña

El `app.py` del servidor importa `pagina_prediccion` desde `/app/streamlit`. Ahí se copia `app/servidor/pagina_prediccion_puente.py`, que **no contiene la pestaña**:
carga `app/pagina_prediccion.py` del clon de este repositorio y llama a su `render()`. Así la pestaña que se ve es siempre la del commit que tenga el clon.

- **Dónde está el clon.** Junto a la carpeta del puente: `/app/proyecto-machine-learning` (el puente está en `/app/streamlit/`, su carpeta padre es `/app`). Si existe la
  variable de entorno `PAA_REPO`, se usa esa carpeta.
- **Carga.** Con `importlib.util.spec_from_file_location`, bajo el nombre `paa_pagina_prediccion`. El puente usa solo la biblioteca estándar y streamlit.
- **Pie.** Cada vez que se dibuja, termina con «Versión desplegada: `<hash corto>` del repositorio del PAA». Sirve para comprobar de un vistazo qué commit se está viendo.
- **Verificación del `src`.** Después de cargar la pestaña, el puente comprueba que `sys.modules["src.modelo"].__file__` esté dentro de la carpeta del clon. Si no lo está (hay otro `src` antes en `sys.path`), muestra un `st.error` con las dos rutas, la esperada y la cargada, y deja sin cargar la pestaña; no lanza ninguna excepción.
- **Errores.** Si el clon no está o la importación falla, muestra un `st.error` con el motivo y el traceback dentro de un expander «Detalle técnico». No deja escapar la excepción: las demás páginas del PID siguen funcionando.

### 3.2 Clon fijado en un commit

El clon se deja en un commit concreto de `main` (el del merge de la rama `e3/despliegue-servidor`), no en una rama que avance sola. Actualizar el dashboard es
`fetch` + `checkout` de otro commit en el clon; no hace falta reiniciar nada ni volver a copiar el puente.

El puente lee el commit de `.git/HEAD` (y de la ref a la que apunte, o de `packed-refs`), sin lanzar procesos. Si cambió desde la última carga:

1. vacía la caché de **cada función cacheada de streamlit que defina el módulo viejo** (`_modelo_en_cache`, `_historico_en_cache`, `_referencia_en_cache` y cualquier otra):
   si no, esas funciones seguirían devolviendo el modelo y los CSV del commit anterior. Cada una va en su propio `try`; si alguna falla, se anota en el expander
   «Detalle técnico» y el puente sigue. **No** se usan `st.cache_data.clear()` ni `st.cache_resource.clear()` globales: las cachés de las páginas del PID no se tocan;
2. quita de `sys.modules` el módulo de la pestaña, `src` y todos los `src.*`;
3. vuelve a cargar la pestaña.

**Sobre el `.pyc`.** Un `git checkout` real cambia la fecha de modificación de los archivos que modifica, así que Python no reutiliza el `.pyc` viejo y la recarga ve el código nuevo.
En la prueba automática de recarga hizo falta que las dos versiones del archivo tuvieran distinto tamaño: con el mismo tamaño y escritas en el mismo segundo, Python reutilizaba el `.pyc`.
Es un artefacto de la prueba, no un riesgo del despliegue.

### 3.3 Prioridad de los módulos del dashboard

En `app/pagina_prediccion.py`, `app/` y la raíz del repositorio se agregan **al final** de `sys.path`, y solo si no están (antes se insertaban al principio). Motivo: `app/` del clon
tiene `charts.py`, `ui.py`, `config.py` y `constants.py`, y no deben tapar los del dashboard del PID. Con el orden del servidor, `import charts` y `import ui` resuelven a
`/app/streamlit/charts.py` y `/app/streamlit/ui.py`; `src` resuelve al del clon. Las rutas de datos de la pestaña siguen siendo relativas al archivo, no a `sys.path` ni al directorio de trabajo.

### 3.4 Librerías agregadas sin reemplazar nada

La pestaña necesita **scipy 1.16.3** y **holidays 0.103**, que el servidor no tiene. Se instalan con `pip --target` en `/app/streamlit/librerias/` (que ya está en `sys.path`), con `--no-deps`
y ruedas binarias para Linux x86_64 y Python 3.11. No se actualiza ni se quita ningún paquete existente. `holidays` usa `python-dateutil`, que ya viene con pandas.
Ocupan unos 156 MB (estimación del equipo; no se midió acá). Las versiones son las mismas con las que pasaron las pruebas (`pruebas_pipeline.md`, §7).

### 3.5 Tema

Se crea `/app/.streamlit/config.toml` con `[theme]` y `base = "light"`. El directorio de trabajo del dashboard es `/app`, de donde streamlit toma el archivo; streamlit 1.56 lo toma sin reiniciar,
desde la siguiente carga de la página. Es el mismo ajuste que ya tiene el repositorio en `.streamlit/config.toml` (D80): sin él, con el sistema en modo oscuro, los textos casi no se leen sobre el fondo claro.
Afecta también a las páginas del PID, que ya fijan un fondo claro por su cuenta.

### 3.6 Riesgos conocidos

- **Un `src` ajeno en `sys.path` (detectado por el puente).** Si hubiera uno en `/app/streamlit`, `/app` o `librerias/`, se importaría en lugar del del clon. El puente lo detecta (3.1): la pestaña no se muestra y el `st.error` dice qué ruta se esperaba y cuál se cargó. La solución sería quitar o renombrar ese `src` ajeno; el procedimiento no lo prevé porque el diagnóstico no encontró ninguno.
- **Estado compartido entre sesiones.** El puente guarda el módulo cargado y el commit en un diccionario del módulo, compartido por todas las sesiones del dashboard. Si dos sesiones se dibujan a la vez justo cuando cambia el commit, una podría ver un error transitorio; se resuelve recargando la página. No se probó.
- **Cachés de otras funciones del módulo.** Solo se vacían las funciones cacheadas de streamlit que sean atributos del módulo de la pestaña. Una caché que viviera en otro módulo (por ejemplo dentro de `src`) no se vacía.
- **`git checkout` a mitad de una lectura.** El puente lee `.git/HEAD` en cada dibujado. Si lo lee justo mientras git actualiza la ref, puede tomar el commit anterior o no poder leerlo (el pie dice «desconocida»); la próxima carga lo corrige.
- **Versiones.** Streamlit 1.56.0 en el servidor; el `.venv` del repositorio usa 1.65.0. Las pruebas pasaron con 1.56.0 (`pruebas_pipeline.md`, §7), pero en Windows.

## 4. Comandos para el servidor

Pegar **un comando por vez**. Entre paréntesis, qué debería verse.

### Paso 1. Respaldo

Ya está hecho: `/app/Respaldo/streamlit_20261026`. No hay que ejecutar nada. Para confirmar que sigue ahí:

```
ls /app/Respaldo/streamlit_20261026
```

### Paso 2. Clon en el commit de `main` del merge de esta rama

El 26/10 el clon tenía un cambio local en `notebooks/base_2.ipynb` (2 líneas). Ese notebook se retiró del repositorio el 24/09 y vive en la rama `entregable_2`. Antes del checkout se guardó
una copia en `/app/Respaldo/clon_paa_20261026/base_2_modificado_en_servidor.ipynb` y se hizo `git stash` con el mensaje «base_2 modificado en el servidor, antes del despliegue del 26/10». **No se descartó.**
El `fetch` del 26/10 trajo `main` hasta `6f79092` y el tag `e3-entrega-25-10`.

Comprobar que el clon no tiene cambios locales (no debe imprimir nada; si imprime algo, **detenerse** y avisar):

```
git -C /app/proyecto-machine-learning status --short
```

Comprobar que el stash sigue guardado (debe aparecer «base_2 modificado en el servidor, antes del despliegue del 26/10»):

```
git -C /app/proyecto-machine-learning stash list
```

Anotar el commit en el que está el clon **antes** de moverlo (sirve para la vuelta atrás del paso 7):

```
git -C /app/proyecto-machine-learning rev-parse --short=7 HEAD
```

Traer los commits nuevos:

```
git -C /app/proyecto-machine-learning fetch origin
```

Pasar al commit de `main` que resulte del merge de esta rama. **`<commit de main>` lo completa el equipo** con el hash del commit de merge, una vez hecho el merge en `main` y el push (el commit tiene que existir en `origin` para que el `fetch` lo traiga). Queda con `HEAD` suelto: es lo esperado, el puente lo lee igual.

```
git -C /app/proyecto-machine-learning checkout <commit de main>
```

Confirmar el commit (anotar los 7 caracteres: el pie de la pestaña muestra los primeros 7 del hash):

```
git -C /app/proyecto-machine-learning rev-parse --short=7 HEAD
```

### Paso 3. scipy y holidays en `librerias/`

Ocupa unos 156 MB. Es un solo comando; en la terminal se puede ver en dos líneas por el ancho, pero se pega entero:

```
python3 -m pip install --no-deps --only-binary=:all: --python-version 3.11 --implementation cp --platform manylinux2014_x86_64 --platform manylinux_2_17_x86_64 --platform manylinux_2_28_x86_64 --target /app/streamlit/librerias scipy==1.16.3 holidays==0.103
```

### Paso 4. Tema

Comprobar que `/app/.streamlit` **no existe** (debe responder «No such file or directory»; si existe, **detenerse**: la vuelta atrás lo borra y se perdería algo previo):

```
ls -a /app/.streamlit
```

Crear la carpeta:

```
mkdir /app/.streamlit
```

Crear el archivo:

```
printf '[theme]\nbase = "light"\n' > /app/.streamlit/config.toml
```

### Paso 5. Instalar el puente

Reemplaza la página de diagnóstico que estaba en `/app/streamlit/pagina_prediccion.py` (queda en el respaldo del paso 1).

```
cp /app/proyecto-machine-learning/app/servidor/pagina_prediccion_puente.py /app/streamlit/pagina_prediccion.py
```

### Paso 6. Verificación

Compilar el puente (no debe imprimir nada):

```
python3 -m py_compile /app/streamlit/pagina_prediccion.py
```

Después, en el navegador (recargar el dashboard):

1. Abrir la pestaña «Predicción (PAA)». Al pie debe decir «Versión desplegada: `<hash>` del repositorio del PAA», con los mismos 7 caracteres que imprimió `rev-parse` después del checkout en el paso 2.
2. Modo «Semana posterior al corte»: mapa, gráfico y tabla del 01/01/2026 al 07/01/2026, y «Sobre el modelo» con la integridad en «Coincide».
3. Modo «Histórico»: elegir una semana y un municipio; deben verse las métricas y el gráfico de las 47 semanas.
4. Abrir **dos páginas del PID** y comprobar que se ven y se comportan como antes del despliegue (incluido el fondo claro).
5. No debe aparecer ningún `st.error` ni el expander «Detalle técnico» en la pestaña. Si aparece, copiar el traceback y avisar.

Registrar el resultado en la sección 6 de este documento.

### Paso 7. Vuelta atrás completa

Si algo falla y no se resuelve rápido, deshacer en este orden. Un comando por vez.

Restaurar el `app.py` del dashboard desde el respaldo (comprobar antes con `ls /app/Respaldo/streamlit_20261026` que el archivo está ahí):

```
cp /app/Respaldo/streamlit_20261026/app.py /app/streamlit/app.py
```

Borrar el puente:

```
rm /app/streamlit/pagina_prediccion.py
```

Ver qué se agregó a `librerias/` (deben aparecer solo scipy, `scipy.libs`, `scipy-1.16.3.dist-info`, holidays y `holidays-0.103.dist-info`; si aparece otra cosa, **no borrar** y avisar):

```
ls -d /app/streamlit/librerias/scipy* /app/streamlit/librerias/holidays*
```

Borrar solo eso:

```
rm -rf /app/streamlit/librerias/scipy /app/streamlit/librerias/scipy.libs /app/streamlit/librerias/scipy-1.16.3.dist-info /app/streamlit/librerias/holidays /app/streamlit/librerias/holidays-0.103.dist-info
```

Borrar el tema:

```
rm -rf /app/.streamlit
```

El clon queda en el commit nuevo; no hace falta moverlo, porque sin el puente nadie lo importa. Para devolverlo al estado anterior: `git -C /app/proyecto-machine-learning checkout` del commit previo (el que imprimió `rev-parse` antes del `fetch`, en el paso 2) y `git stash pop` para recuperar el cambio de `base_2.ipynb` (el stash sigue guardado).

## 5. Qué está verificado y qué no

**Verificado (pruebas automáticas, `pruebas_pipeline.md` §7):** el puente carga la pestaña de un clon, la recarga cuando cambia el commit (incluido `src`), vacía solo las cachés de la pestaña, y ante un clon ausente, una importación rota o un `src` ajeno
muestra el error sin lanzar excepciones; importar la pestaña no cambia el principio de `sys.path`; y las pruebas del pipeline, de la interfaz y de las variables pasan con Python 3.11.15, streamlit 1.56.0, pandas 3.0.2,
numpy 2.4.4, plotly 5.22.0, pydeck 0.9.1, scipy 1.16.3 y holidays 0.103.

**No verificado, y solo se puede verificar en el servidor:**

- que el comando de `pip --target` del paso 3 instala las ruedas esperadas (las pruebas instalaron las mismas versiones con `uv pip install` en Windows);
- que el orden real de `sys.path` resuelve `charts`, `ui` y `src` como se describe en 3.3 (para `src`, lo comprueba el puente al cargar; para `charts` y `ui`, el equipo en el paso 6);
- que el puente lee bien el `.git` del clon real (las pruebas usan clones falsos con archivos escritos a mano);
- la apariencia: mapa, etiquetas, tema y las páginas del PID (AppTest no dibuja nada);
- el comportamiento con varias sesiones a la vez.

## 6. Resultado de la prueba en el servidor

<!-- PENDIENTE: fecha, commit desplegado (hash corto), resultado de cada punto del paso 6 y problemas encontrados — lo completa el equipo después de ejecutar la sección 4 -->

## 7. Qué queda pendiente

- Completar `<commit de main>` en el paso 2 con el hash del merge, y la sección 6 con el resultado de la prueba.
- La sección de resultados del `README.md` dice que el despliegue en el servidor está pendiente; actualizarla cuando la sección 6 tenga el resultado (esa sección del README no se toca en esta fase).
