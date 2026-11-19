# HabitCodex

Aplicación web para guardar y organizar tus hábitos. Cada persona crea su cuenta y ve solo sus hábitos. Hecha con Python y Flask.

> **Estado:** versión 0.1 terminada. Funcionan el registro, el inicio de sesión, la lista de hábitos, la búsqueda, la exportación CSV y la API, y las pruebas de rendimiento y disponibilidad ya están hechas (resultados en [`resultados/`](resultados/)). El diseño completo está en [`DISEÑO.md`](DISEÑO.md).

## Qué se necesita

- Python 3.10 o superior (se desarrolla con 3.13).
- Git y pip.

Para comprobar: `python --version` y `git --version`.

## Instalación

Abre una terminal y ejecuta uno por uno:

```bash
# 1. Descargar el proyecto
git clone https://github.com/SamuelLariosR/HabitCodex.git
cd HabitCodex

# 2. Crear un entorno virtual
python -m venv venv

# 3. Activarlo
source venv/bin/activate        # Linux
venv\Scripts\activate           # Windows

# 4. Instalar lo necesario
pip install -r requirements.txt
```

## Configuración

Copia la plantilla de configuración y ábrela para ponerle tus valores:

```bash
cp .env.example .env            # Linux
copy .env.example .env          # Windows
```

El archivo `.env` lleva dos datos:

```
SECRET_KEY=escribe-aqui-un-texto-largo-y-secreto
DATABASE_URL=habitcodex.db
```

- `SECRET_KEY`: un texto largo y secreto que la aplicación usa para proteger la sesión de cada persona.
- `DATABASE_URL`: dónde se guarda la base de datos (SQLite, un solo archivo). Se crea sola la primera vez.

**Recomendación: No subir el archivo `.env` a GitHub** (ya está en `.gitignore`).

## Ejecutar la aplicación

**Para probar y desarrollar:**

```bash
flask --app app run --debug
```

Abre `http://127.0.0.1:5000` en el navegador.

**Para uso más profesional:**

```bash
gunicorn -w 4 -b 0.0.0.0:8000 app:app          # Linux
waitress-serve --port=8000 app:app             # Windows
```

Abre `http://localhost:8000`.

## Cómo usarla

1. Entra a la página y pulsa **Crear cuenta**.
2. Inicia sesión con tu correo y contraseña.
3. Escribe un hábito y pulsa **Agregar**.
4. Usa **Editar** o **Eliminar** en cada hábito, el buscador para filtrar, y **Exportar CSV** para descargar tu lista.

## Pruebas

Primero instala las herramientas extra:

```bash
pip install -r requirements-dev.txt
```

|Qué|Comando|
|---|---|
|Pruebas de funcionamiento|`pytest`|
|Revisar el estilo del código|`flake8`|
|Prueba de rendimiento|`locust -f pruebas/locustfile.py --host http://localhost:8000`|

Para la prueba de rendimiento, deja la aplicación corriendo con Gunicorn en otra terminal y abre `http://localhost:8089` para elegir cuántos usuarios simular.

### Resultados de las pruebas

Los archivos quedan en `resultados/`:

|Archivo|Qué contiene|
|---|---|
|`normal_stats.csv`|resumen de la carga normal (10 usuarios)|
|`media_stats.csv`|resumen de la carga media (50 usuarios)|
|`alta_stats.csv`|resumen de la carga alta (100 usuarios)|
|`recursos_*.csv`|CPU y memoria de Gunicorn durante cada carga|
|`*_stats_history.csv`|la misma información segundo a segundo, para ver la evolución|
|`disponibilidad.csv`|una fila por minuto: código y tiempo de respuesta|

Cada carga usa un escenario distinto:

|Escenario|Usuarios|Tareas|Etiqueta|
|---|---|---|---|
|Carga normal|10|Ver la lista y buscar|`normal`|
|Carga media|50|Ver la lista, crear y editar|`media`|
|Carga alta|100|Ver la lista|`alta`|

Ejemplo de una tanda completa, con la base de pruebas aparte:

```bash
# 1. servidor (en otra terminal)
DATABASE_URL=pruebas.db gunicorn -w 4 -b 127.0.0.1:8000 app:app

# 2. carga normal, con la CPU y la memoria apuntándose
python pruebas/monitor_recursos.py \
  --salida resultados/recursos_normal.csv --duracion 120 &
locust -f pruebas/locustfile.py --headless -u 10 -r 2 --run-time 2m \
  --tags normal --host http://127.0.0.1:8000 --csv resultados/normal

# 3. disponibilidad: una comprobación por minuto
python pruebas/chequeo_disponibilidad.py --duracion 10

# 4. borrar la base de pruebas al terminar
rm -f pruebas.db pruebas.db-wal pruebas.db-shm
```

Cambia `--tags`, `-u`, `-r` y el nombre del CSV para la carga media (`media`, 50 usuarios) y la alta (`alta`, 100 usuarios). No uses `habitcodex.db` para las pruebas de carga.

### Qué salió

Tanda del 19 de noviembre de 2026: Gunicorn con 4 workers, modo WAL activo y una base de pruebas aparte, borrada al terminar.

|Escenario|Usuarios|Solicitudes|Fallos|Promedio|Percentil 95|Solicitudes/s|
|---|---|---|---|---|---|---|
|Carga normal|10|1188|0|19 ms|16 ms|10|
|Carga media|50|4295|0|363 ms|1400 ms|36|
|Carga alta|100|9291|0|277 ms|78 ms|78|

Recursos de Gunicorn, sumando los 4 workers (400 % sería el 100 % de los 4 núcleos):

|Escenario|CPU promedio|CPU máximo|Memoria|
|---|---|---|---|
|Carga normal|9.9 %|135.9 %|168 MB|
|Carga media|48.4 %|234.4 %|169 MB|
|Carga alta|84.1 %|386.1 %|169 MB|

Disponibilidad: 10 comprobaciones, una por minuto, todas con código 200 (0 fallos) y entre 5.2 y 30.9 ms de respuesta.

**Contraste con el RNF-01:** con 50 usuarios a la vez, 95 de cada 100 solicitudes respondieron en 1400 ms o menos, por debajo de los 2000 ms que pide el requisito. **Se cumple**, y ningún escenario tuvo un solo fallo.

El punto débil son el registro y el inicio de sesión: con 50 usuarios tardan 3900 ms y 3300 ms en el percentil 95. La causa es el hash de la contraseña (600 000 iteraciones), que se calcula una sola vez por usuario y de golpe al empezar la prueba. La lista, la búsqueda, la creación y la edición se mantienen muy por debajo de 2 s. Con 100 usuarios el uso de CPU llega al 386 % de 400 %, así que el límite es el procesador, no SQLite: no apareció ningún `database is locked` con WAL activo.

Mejoras posibles, sin cambiar el diseño: más workers o `--worker-class gthread`, repartir el registro en una cola para no bloquear la petición, y servir los archivos estáticos con Nginx. Bajar las iteraciones del hash no se recomienda porque debilita las contraseñas.

## Si algo falla

|Problema|Qué hacer|
|---|---|
|`ModuleNotFoundError`|Falta activar el entorno virtual (paso 3) o instalar con `pip install -r requirements.txt`.|
|`SECRET_KEY` o `DATABASE_URL` no encontrados|Falta crear el archivo `.env` (sección Configuración).|
|El puerto ya está en uso|Cambia el número de puerto en el comando (por ejemplo `--port=5001` en Flask).|
|`database is locked` al arrancar Gunicorn|Varios workers intentan activar WAL a la vez. La app ya reintenta y espera hasta 15 s; si sigue apareciendo, comprueba que ningún otro proceso esté usando esa misma base.|
|Locust avisa `open file limit ... below 10000`|Sube el límite en esa terminal con `ulimit -n 10000` antes de lanzar la prueba.|
|Gunicorn no funciona en Windows|Es normal; en Windows usa `waitress-serve`.|

## Despliegue en la nube (opcional)

Se puede publicar en Render, Railway o PythonAnywhere. Cuando se haga, aquí se anotará la dirección pública, el comando de inicio y las variables de entorno configuradas.

## Estructura del proyecto

Está explicada, archivo por archivo, en [`DISEÑO.md`](DISEÑO.md), sección 4.
