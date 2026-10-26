# Despliegue de la pestaña «Predicción (PAA)» en el dashboard del servidor (Entregable 3, fase 8a)

**Qué es.** El procedimiento para que la pestaña «Predicción (PAA)» corra dentro del dashboard que ya está en el servidor institucional, junto
a las páginas del PID, sin reemplazar nada de lo que ese dashboard tiene.
**Código que lo hace posible:** `app/servidor/pagina_prediccion_puente.py` (el puente; en el servidor se copia como `/app/streamlit/paa_puente.py`) y el manejo de `sys.path` de `app/pagina_prediccion.py`.
**Pruebas:** `tests/test_servidor.py` y la sección 7 de `documentacion/pruebas_pipeline.md`.
**Fecha:** 26/10/2026. **Quién lo ejecuta:** el equipo, en la terminal de Jupyter del servidor.
**Estado:** desplegado el 26/10/2026 en el commit `c1c40c3` (resultado en la sección 6).

## 1. Cómo usar este documento

- Los comandos de la sección 4 van **de a uno por línea** y se pegan **uno por vez**: la terminal de Jupyter se traba si se pegan varias líneas juntas.
- Los comandos de la sección 4 son los que el equipo ejecutó el 26/10, con una diferencia: el paso 5 está escrito como quedó **después** de corregir el problema del módulo
  cacheado (sección 3.7 y sección 6), no como se ejecutó la primera vez. Qué se verificó en el servidor, qué se verificó en otro lado y qué sigue sin verificar está en la sección 5.
- Los comandos asumen las rutas del diagnóstico del 26/10 (sección 2). Si alguna cambió, detenerse y avisar.

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

El `app.py` del servidor tenía las tres líneas que enrutan a la pestaña y, en el `elif`, importaba `pagina_prediccion` desde `/app/streamlit` (la página de diagnóstico de D1). Ahí se copia
`app/servidor/pagina_prediccion_puente.py` **con otro nombre**, `/app/streamlit/paa_puente.py`, y la línea de importación del `elif` pasa a ser `import paa_puente as pagina_prediccion`
(el nombre nuevo se explica en la sección 3.7). El puente **no contiene la pestaña**: carga `app/pagina_prediccion.py` del clon de este repositorio y llama a su `render()`.
Así la pestaña que se ve es siempre la del commit que tenga el clon.

- **Dónde está el clon.** Junto a la carpeta del puente: `/app/proyecto-machine-learning` (el puente está en `/app/streamlit/`, su carpeta padre es `/app`). Si existe la
  variable de entorno `PAA_REPO`, se usa esa carpeta.
- **Carga.** Con `importlib.util.spec_from_file_location`, bajo el nombre `paa_pagina_prediccion`. El puente usa solo la biblioteca estándar y streamlit.
- **Pie.** Cada vez que se dibuja, termina con «Versión desplegada: `<hash corto>` del repositorio del PAA». Sirve para comprobar de un vistazo qué commit se está viendo.
- **Verificación del `src`.** Después de cargar la pestaña, el puente comprueba que `sys.modules["src.modelo"].__file__` esté dentro de la carpeta del clon. Si no lo está (hay otro `src` antes en `sys.path`), muestra un `st.error` con las dos rutas, la esperada y la cargada, y deja sin cargar la pestaña; no lanza ninguna excepción.
- **Errores.** Si el clon no está o la importación falla, muestra un `st.error` con el motivo y el traceback dentro de un expander «Detalle técnico». No deja escapar la excepción: las demás páginas del PID siguen funcionando.

### 3.2 Clon fijado en un commit

El clon se deja en un commit concreto de `main` (el del merge de la rama `e3/despliegue-servidor`, `c1c40c3`), no en una rama que avance sola. Actualizar **la pestaña** es
`fetch` + `checkout` de otro commit en el clon; no hace falta reiniciar nada ni volver a copiar el puente. Eso vale para la pestaña y no para el puente mismo (sección 3.7).
La recarga al cambiar de commit se verificó en una réplica con un clon git real (sección 5); en el servidor todavía no se hizo un segundo checkout.

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
Las versiones son las mismas con las que pasaron las pruebas (`pruebas_pipeline.md`, §7).

- **Verificado en el servidor (26/10).** El comando del paso 3 terminó sin errores e instaló scipy 1.16.3 y holidays 0.103. Mostró dos avisos esperables: pip advierte que corre como `root`, y
  `librerias/bin` ya existía, así que el ejecutable `holidays-ics` no se copió (el código del repositorio solo importa la biblioteca `holidays`, no ese ejecutable).
- **Verificado por Claude web el 26/10, en Linux** (no en el servidor): el mismo comando `pip --target` ocupó **156 MB**, y scipy importó con Python 3.11.15 y numpy 2.4.4. Con eso la cifra de 156 MB
  deja de ser una estimación; es la que midió esa corrida, no una medición hecha en el servidor.
- **Inferencia.** `src/modelo.py` importa scipy y `src/variables.py` importa holidays; como la pestaña cargó y funcionó en el servidor, las dos bibliotecas se importan allí. El equipo no corrió un `import` suelto.

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

### 3.7 Recarga de módulos en el servidor

**Qué pasó.** El 26/10, después de copiar el puente como `/app/streamlit/pagina_prediccion.py` (el nombre que el diseño original suponía), la pestaña siguió mostrando el diagnóstico de D1. El proceso del
dashboard ya había importado ese módulo cuando el archivo era la página de diagnóstico, y el servidor **no recarga un módulo importado cuando cambia su archivo**: `app.py` sí se relee en cada ejecución,
pero `import pagina_prediccion` devuelve el módulo que ya está en `sys.modules`. Este comportamiento se observó en el servidor; no se investigó qué configuración de streamlit lo produce.

**Qué se hizo.** El puente se copió con un nombre que el proceso nunca había importado, `/app/streamlit/paa_puente.py`; en `app.py`, la línea de importación del `elif` pasó a ser
`import paa_puente as pagina_prediccion` (el resto del `elif` sigue llamando a `pagina_prediccion.render()`); se compiló sin errores y se borró `/app/streamlit/pagina_prediccion.py`.

**Consecuencia para el mantenimiento.**

- **La pestaña sí se actualiza con un checkout del clon.** El puente no es la pestaña: carga `app/pagina_prediccion.py` del clon con `spec_from_file_location` bajo el nombre `paa_pagina_prediccion` y, cuando cambia el
  commit, descarta ese módulo y `src` de `sys.modules` y los vuelve a cargar (sección 3.2). No depende de la recarga de módulos del servidor.
- **El puente no se reemplaza en caliente.** `paa_puente.py` es una copia, no está en el clon, y una vez importado el proceso lo conserva. Si cambia `app/servidor/pagina_prediccion_puente.py` en el repositorio,
  ese cambio **no llega** al servidor con un checkout: hay que volver a copiarlo **con un nombre nuevo** (y cambiar la importación de `app.py`) o reiniciar el proceso del dashboard. Reiniciar no se probó
  ni se sabe si el equipo puede hacerlo.
- **El nombre `pagina_prediccion` quedó quemado en el proceso** mientras no se reinicie: no sirve para un módulo nuevo.

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
El primer `fetch` del 26/10 (antes de preparar este despliegue) trajo `main` hasta `6f79092` y el tag `e3-entrega-25-10`. El `fetch` del despliegue trajo `main` hasta `c1c40c3`.

Comprobar que el clon no tiene cambios locales (no debe imprimir nada; si imprime algo, **detenerse** y avisar):

```
git -C /app/proyecto-machine-learning status --short
```

Comprobar que el stash sigue guardado (debe aparecer «base_2 modificado en el servidor, antes del despliegue del 26/10»):

```
git -C /app/proyecto-machine-learning stash list
```

Anotar el commit en el que está el clon **antes** de moverlo (el 26/10 imprimió `46e0c65`; sirve para saber de dónde se parte, aunque la vuelta atrás del paso 7 usa la rama `main` del clon):

```
git -C /app/proyecto-machine-learning rev-parse --short=7 HEAD
```

Traer los commits nuevos:

```
git -C /app/proyecto-machine-learning fetch origin
```

Pasar al commit de `main` que resultó del merge de `e3/despliegue-servidor`: `c1c40c3`. Queda con `HEAD` suelto: es lo esperado, el puente lo lee igual (en el servidor se comprobó, sección 6). Para desplegar otro commit
más adelante, el mismo comando con el hash nuevo, después de un `fetch`.

```
git -C /app/proyecto-machine-learning checkout c1c40c3
```

Confirmar el commit (anotar los 7 caracteres: el pie de la pestaña muestra los primeros 7 del hash; el 26/10 imprimió `c1c40c3`):

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

El puente se copia con el nombre **`paa_puente.py`**, no como `pagina_prediccion.py`: el proceso del dashboard ya tiene importado un módulo con ese nombre (la página de diagnóstico de D1) y no lo recarga
si el archivo cambia (sección 3.7). El 26/10 se copió primero como `pagina_prediccion.py` y la pestaña siguió mostrando el diagnóstico.

```
cp /app/proyecto-machine-learning/app/servidor/pagina_prediccion_puente.py /app/streamlit/paa_puente.py
```

Editar `/app/streamlit/app.py`: en el `elif` de la pestaña «Predicción (PAA)», la línea de importación pasa a ser (el resto del `elif` no cambia):

```
import paa_puente as pagina_prediccion
```

### Paso 6. Verificación

Compilar el puente y `app.py` (no deben imprimir nada):

```
python3 -m py_compile /app/streamlit/paa_puente.py
```

```
python3 -m py_compile /app/streamlit/app.py
```

Con los dos compilados, borrar la página de diagnóstico de D1, `/app/streamlit/pagina_prediccion.py`, que ya no importa nadie (el 26/10 se borró; queda en el respaldo del paso 1):

```
rm /app/streamlit/pagina_prediccion.py
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

Comprobar que el respaldo tiene los dos archivos que se restauran (deben aparecer `app.py` y `pagina_prediccion.py`; si falta alguno, **detenerse** y avisar):

```
ls /app/Respaldo/streamlit_20261026
```

Restaurar el `app.py` del dashboard desde el respaldo. Con esto, la línea del `elif` vuelve a importar `pagina_prediccion` y deja de importar `paa_puente`:

```
cp /app/Respaldo/streamlit_20261026/app.py /app/streamlit/app.py
```

Restaurar la página de diagnóstico de D1, que se borró en el paso 6 y que el `app.py` del respaldo vuelve a importar:

```
cp /app/Respaldo/streamlit_20261026/pagina_prediccion.py /app/streamlit/pagina_prediccion.py
```

Borrar el puente:

```
rm /app/streamlit/paa_puente.py
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

El clon queda en el commit nuevo; no hace falta moverlo, porque sin el puente nadie lo importa. Para devolverlo al estado anterior, volver a la rama `main` del clon, que quedó en `46e0c65` (el `fetch` trae commits nuevos pero no mueve la rama `main` local):

```
git -C /app/proyecto-machine-learning checkout main
```

Y recuperar el cambio local de `notebooks/base_2.ipynb` (el stash sigue guardado):

```
git -C /app/proyecto-machine-learning stash pop
```

## 5. Qué está verificado y qué no

**Verificado por pruebas automáticas (`pruebas_pipeline.md` §7, en Windows):** el puente carga la pestaña de un clon, la recarga cuando cambia el commit (incluido `src`), vacía solo las cachés de la pestaña, y ante un clon ausente, una importación rota o un `src` ajeno
muestra el error sin lanzar excepciones; importar la pestaña no cambia el principio de `sys.path`; y las pruebas del pipeline, de la interfaz y de las variables pasan con Python 3.11.15, streamlit 1.56.0, pandas 3.0.2,
numpy 2.4.4, plotly 5.22.0, pydeck 0.9.1, scipy 1.16.3 y holidays 0.103.

**Verificado por Claude web el 26/10, en Linux (no en el servidor):**

- el mismo comando `pip --target` del paso 3 ocupó **156 MB**, y scipy importó con Python 3.11.15 y numpy 2.4.4;
- en una réplica con un **clon git real** y `HEAD` suelto, el pie mostró el commit, y la pestaña **recargó sin reiniciar** al pasar de `0117bff` a `6f79092` y volver.

La réplica no es el servidor: no tiene su `app.py`, su `sys.path` ni sus páginas del PID.

**Verificado en el servidor (26/10, sección 6):**

- que el comando de `pip --target` del paso 3 instala scipy 1.16.3 y holidays 0.103 (antes solo se había probado con `uv pip install` en Windows y con el mismo `pip --target` en Linux);
- que el puente lee bien el `.git` del clon real, con `HEAD` suelto: el pie mostró «Versión desplegada: `c1c40c3`»;
- que la pestaña funciona en los dos modos, con el tema claro, con las tablas en pantalla verificadas por el equipo y el panel «Sobre el modelo» con la integridad en «Coincide»;
- que los números del modo «Histórico» coinciden con los de `experiments/evaluacion_final/tablas/06_globales.csv` en el pie de las 47 semanas (1,1063, 1,1359 y 33 de 47);
- que las páginas del PID revisadas por el equipo siguen funcionando (el equipo anotó «Revisadas»; no detalló cuáles ni anotó diferencias). **Inferencia:** esto sugiere que `charts` y `ui` siguen resolviendo a los del dashboard,
  como se describe en 3.3; el equipo no comprobó la ruta de importación de cada uno.

No consta en el registro del equipo el punto 5 del paso 6 (ningún `st.error`): ver la sección 6 y la sección 7.

**Sigue sin verificar:**

- la **recarga al cambiar de commit en el servidor real**: se probó en la réplica de Linux y en las pruebas automáticas, pero el registro del equipo informa un solo checkout en el clon del servidor (de `46e0c65` a `c1c40c3`, antes de cargar la pestaña);
- el comportamiento con **varias sesiones a la vez**;
- el **mapa, las etiquetas y los gráficos** en el servidor: el equipo informó que la pestaña funciona en los dos modos y que verificó las tablas, pero no detalló el mapa ni las etiquetas, y no hay capturas archivadas en el repositorio;
- la **vuelta atrás completa** del paso 7: no consta que se haya ejecutado (el despliegue no falló). Los pasos que usan nombres nuevos (`paa_puente.py`, la restauración de `pagina_prediccion.py`) se escribieron a partir de lo ejecutado el 26/10, sin probarlos;
- que el **docstring del puente** (`app/servidor/pagina_prediccion_puente.py`) siga diciendo que se copia como `/app/streamlit/pagina_prediccion.py`: es código y esta fase no lo toca; ver la sección 7.

## 6. Resultado de la prueba en el servidor

**Fecha:** 26/10/2026. **Commit desplegado:** `c1c40c3` (merge de `e3/despliegue-servidor` en `main`). **Quién ejecutó:** el equipo, en la terminal de Jupyter del servidor. El registro de lo que pasó lo escribió el equipo; esta sección lo transcribe.

### Pasos 1 a 4

Sin errores.

| Paso | Resultado |
| --- | --- |
| 1. Respaldo | `/app/Respaldo/streamlit_20261026` (ya estaba hecho) |
| 2. Clon | pasó de `46e0c65` a `c1c40c3`, con `HEAD` suelto. El stash con `base_2` se conservó |
| 3. `librerias/` | pip instaló scipy 1.16.3 y holidays 0.103. Dos avisos esperables: pip corre como `root`, y `librerias/bin` ya existe, así que el ejecutable `holidays-ics` no se copió |
| 4. Tema | se creó `/app/.streamlit/config.toml` |

### Paso 5: el problema del módulo cacheado y su solución

Después de copiar el puente como `/app/streamlit/pagina_prediccion.py`, la pestaña **siguió mostrando el diagnóstico de D1**. El proceso del dashboard ya tenía importado ese módulo y el servidor no recarga módulos
importados cuando cambia el archivo (`app.py` sí se relee). Explicación y consecuencias en la sección 3.7.

Solución:

1. el puente se copió como `/app/streamlit/paa_puente.py`;
2. en `app.py`, la línea de importación del `elif` pasó a ser `import paa_puente as pagina_prediccion`;
3. `py_compile` sin errores;
4. se borró `/app/streamlit/pagina_prediccion.py`.

El paso 5 de la sección 4 está escrito con esta solución, no con la primera copia.

### Paso 6: verificación

| Punto | Resultado |
| --- | --- |
| 1. Pie de la pestaña | «Versión desplegada: `c1c40c3`», el mismo hash que imprimió `rev-parse` después del checkout. Tema claro |
| 2. Modo «Semana posterior al corte» | funciona. «Sobre el modelo», integridad: **Coincide** |
| 3. Modo «Histórico», semana del 06/02/2025 | observado **143**, esperado **163,0**, desvianza de Poisson media **1,033** (**+0,053** frente a L1) y **5 de 56** pares fuera del intervalo del 80 % |
| 3. Modo «Histórico», pie de las 47 semanas | desvianza **1,1063** (solución) y **1,1359** (L1); **33 de 47** semanas con menor desvianza para la solución. Igual que `experiments/evaluacion_final/tablas/06_globales.csv` (README, «Resultados») |
| Tablas en pantalla | verificadas por el equipo |
| 4. Dos páginas del PID | «Revisadas» |
| 5. Sin `st.error` ni «Detalle técnico» | **el registro del equipo no lo menciona** |

**Cómo leerlo.** Los números de la semana del 06/02/2025 los leyó el equipo en la pantalla del servidor; la pestaña los calcula desde `experiments/evaluacion_final/predicciones_bloque_final.csv`. No se contrastaron
contra ese archivo al escribir este documento. Lo que sí coincide con un artefacto del repositorio es el pie de las 47 semanas (`tablas/06_globales.csv`). La desvianza de la semana, +0,053 frente a L1, es **peor** que la de L1
en esa semana; es una semana, no el desempeño del modelo (los 33 de 47 son la comparación sobre todo el bloque).

**Sobre el punto 5.** Confirmado: la pestaña se mostró en los dos modos sin errores ni el expander «Detalle técnico», con el pie «Versión desplegada: c1c40c3» (impresiones del 26/10 en `documentacion/logs/servidor_despliegue_20261026/`).

## 7. Qué queda pendiente

- **Actualizar el informe** con el resultado de la sección 6 (el prototipo está desplegado en el servidor, en `c1c40c3`). `README.md` ya lo dice; `documentacion/cambios_informe.md` todavía lo lista como pendiente (D69) y esta fase no lo toca.
- **Docstring del puente** (`app/servidor/pagina_prediccion_puente.py`, líneas 1 a 5): dice que se copia como `/app/streamlit/pagina_prediccion.py`. Es el nombre que no funcionó; en el servidor el archivo es `paa_puente.py`. Corregirlo exige tocar código y
  correr las pruebas, por eso queda para otra fase.
- **Si cambia el puente** (el archivo del repositorio), el cambio no llega al servidor con un checkout: hay que copiarlo con un nombre nuevo y cambiar la importación de `app.py`, o reiniciar el proceso del dashboard (sección 3.7).
- **Probar una actualización de la pestaña en el servidor real** (`fetch` + `checkout` de otro commit) la próxima vez que haya que desplegar uno: hoy solo se probó en una réplica.
- **Archivar capturas** del mapa y los gráficos en el servidor, si el equipo las quiere citar. No hay ninguna en el repositorio.
- El `<commit de main>` del paso 2 ya está completo (`c1c40c3`).
