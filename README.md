# HabitCodex

Aplicación web para guardar y organizar tus hábitos. Cada persona crea su cuenta y ve solo sus hábitos. Hecha con Python y Flask.

> **Estado:** en desarrollo. La estructura, el arranque y la lógica de hábitos ya funcionan; las pantallas, la API y las pruebas de rendimiento se completan en las fases siguientes. El diseño completo está en [`DISEÑO.md`](DISEÑO.md).

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

## Si algo falla

|Problema|Qué hacer|
|---|---|
|`ModuleNotFoundError`|Falta activar el entorno virtual (paso 3) o instalar con `pip install -r requirements.txt`.|
|`SECRET_KEY` o `DATABASE_URL` no encontrados|Falta crear el archivo `.env` (sección Configuración).|
|El puerto ya está en uso|Cambia el número de puerto en el comando (por ejemplo `--port=5001` en Flask).|
|Gunicorn no funciona en Windows|Es normal; en Windows usa `waitress-serve`.|

## Despliegue en la nube (opcional)

Se puede publicar en Render, Railway o PythonAnywhere. Cuando se haga, aquí se anotará la dirección pública, el comando de inicio y las variables de entorno configuradas.

## Estructura del proyecto

Está explicada, archivo por archivo, en [`DISEÑO.md`](DISEÑO.md), sección 4.
