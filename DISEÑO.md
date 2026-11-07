
# HabitCodex – Diseño (versión 0.1)

> **Cómo leer este documento:** todo lo que está antes del título **"FUTURO"** es lo que se construye ahora. Lo que viene después (versión 0.2 en adelante) está aparte, al final, para no confundirse. Cómo instalar y ejecutar la aplicación está en [`README.md`](README).

## 1. ¿Qué es HabitCodex?

Una página web para guardar y organizar tus hábitos (por ejemplo "Estudiar", "Leer", "Practicar Python"). Cada persona crea su cuenta y ve **solo sus** hábitos. Está hecha con Python y Flask y es mi proyecto integrador de Ingeniería de Software.

**Problema que resuelve:** a veces uno se propone programar y termina en redes sociales, o no sabe por dónde empezar. Tener los hábitos importantes a la vista ayuda a no perderse.

## 2. Palabras clave 

| Palabra               | Qué significa                                                                                                                        |
| --------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| **Flask**             | La herramienta de Python que convierte mi código en una página web.                                                                  |
| **SQLite**            | Una base de datos que vive en un solo archivo; no hay que instalar nada.                                                             |
| **API**               | Una "puerta" para que otros programas hablen con mi aplicación enviando y recibiendo datos (en formato JSON, que es texto ordenado). |
| **Sesión**            | Lo que mantiene a una persona "dentro" después de iniciar sesión.                                                                    |
| **Hash**              | Cifrar la contraseña de forma que nadie pueda leerla, ni siquiera yo.                                                                |
| **CSV**               | Un archivo de texto con tablas que abre Excel o LibreOffice.                                                                         |
| **RF / RNF**          | RF = lo que la aplicación **hace**. RNF = **cómo** debe comportarse (rápida, segura, fácil...).                                      |
| **Usuarios a la vez** | Cuántas personas usan la aplicación en el mismo momento.                                                                             |
| **Percentil 95**      | "El 95 % de las veces fue igual o más rápido que este tiempo".                                                                       |
| **Gunicorn / Locust** | Gunicorn: servidor para ejecutar la app de forma más seria. Locust: programa que simula muchos usuarios para medir la rapidez.       |

## 3. ¿Qué hace la versión 0.1?

**Sí:** crear cuenta, entrar y salir, crear hábitos, verlos, buscarlos, editarlos, eliminarlos y descargarlos en un archivo CSV. También ofrece una API.

**No:** todo lo demás queda para el futuro (ver el título **FUTURO** al final).


## 4. Estructura del proyecto 

```
habitcodex/
├── app.py                 # Punto de arranque: enciende la aplicación
├── requirements.txt       # Lista de lo que hay que instalar para ejecutarla
├── requirements-dev.txt   # Herramientas extra: pruebas y calidad del código
├── .env.example           # Plantilla de la configuración (sin claves reales)
├── .gitignore             # Lo que NO se sube a GitHub (.env, venv, base de datos)
├── README.md              # Cómo instalar y ejecutar
├── DISEÑO.md              # Este documento
│
├── datos/                 # CAPA DE DATOS (la bodega)
│   ├── conexion.py        #   Abre SQLite y crea las tablas
│   ├── usuarios_datos.py  #   Guarda y busca usuarios
│   └── habitos_datos.py   #   Guarda y busca hábitos
│
├── logica/                # CAPA DE LÓGICA (la cocina)
│   ├── usuarios.py        #   Reglas de registro e inicio de sesión
│   ├── habitos.py         #   Reglas de crear, editar, eliminar, buscar, exportar
│   └── errores.py         #   Los errores propios y sus mensajes
│
├── web/                   # CAPA WEB (el mesero)
│   ├── __init__.py        #   Crea la aplicación Flask y conecta las rutas
│   ├── paginas.py         #   Rutas de las páginas que ve la persona
│   ├── api.py             #   Rutas de la API (empiezan con /api)
│   ├── templates/         #   Las páginas HTML
│   │   ├── base.html      #     Estructura común (encabezado, mensajes)
│   │   ├── registro.html
│   │   ├── login.html
│   │   ├── principal.html #     Lista, búsqueda, agregar y exportar
│   │   └── editar.html
│   └── static/
│       └── estilos.css    #   Colores y diseño
│
├── pruebas/               # Pruebas
│   ├── test_usuarios.py   #   Prueba las reglas de usuarios
│   ├── test_habitos.py    #   Prueba las reglas de hábitos
│   └── locustfile.py      #   Prueba de rendimiento (simula muchos usuarios)
│
└── docs/
    └── HabitCodex_Integrador.xlsx   # El libro de Excel de la entrega
```

El archivo de la base de datos (`habitcodex.db`) se crea solo al ejecutar la aplicación y no se sube a GitHub.

**Dependencias:** `requirements.txt` solo lleva lo necesario para ejecutar (Flask, python-dotenv, y gunicorn en Linux o waitress en Windows). `requirements-dev.txt` lleva pytest, flake8 y locust.

## 5. Requerimientos 


### Funcionales

| ID    | Descripción                                                                               | Prioridad | Criterio                                                                                    |
| ----- | ----------------------------------------------------------------------------------------- | --------- | ------------------------------------------------------------------------------------------- |
| RF-01 | **Crear cuenta** con nombre, correo y contraseña.                                         | Alta      | Con datos buenos se crea; con correo repetido o algo vacío sale un error claro.             |
| RF-02 | **Entrar y salir** con correo y contraseña.                                               | Alta      | Datos correctos: entra. Incorrectos: no entra. Tras salir, no puede ver sus hábitos.        |
| RF-03 | **Crear hábito** con un nombre (reglas en la sección 8).                                  | Alta      | Nombre válido: aparece en la lista. Nombre inválido: mensaje de error.                      |
| RF-04 | **Ver y buscar** mis hábitos (del más antiguo al más nuevo).                              | Alta      | Solo veo los míos; la búsqueda filtra por nombre; sin hábitos dice "Crea tu primer hábito". |
| RF-05 | **Editar** el nombre de un hábito (mismas reglas que al crear).                           | Media     | El cambio se guarda; un nombre inválido da error.                                           |
| RF-06 | **Eliminar** un hábito pidiendo confirmación. Se oculta, no se borra de la base de datos. | Media     | Si confirmo, desaparece de la lista; si cancelo, sigue.                                     |
| RF-07 | **Exportar** mis hábitos a un archivo CSV.                                                | Baja      | Se descarga un archivo que abre en LibreOffice con mis hábitos y solo los míos.             |

### No funcionales

| ID     | Descripción                                                                                                                                                                        | Prioridad | Criterio                                                                                  |
| ------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------- | ----------------------------------------------------------------------------------------- |
| RNF-01 | **Rapidez:** 95 de cada 100 consultas responden en menos de 2 segundos con 50 usuarios a la vez.                                                                                   | Alta      | La prueba de carga con 50 usuarios lo confirma.                                           |
| RNF-02 | **Seguridad:** contraseñas cifradas, páginas privadas solo con sesión iniciada, y textos peligrosos escritos en los campos no dañan nada.                                          | Alta      | No hay contraseñas legibles en la base; sin sesión, la página privada rechaza la entrada. |
| RNF-03 | **Fácil de usar:** máximo 3 pasos por operación y todo en español.                                                                                                                 | Media     | Crear = 2 pasos, editar = 3, eliminar = 2.                                                |
| RNF-04 | **Disponible:** funcionando al menos el 95 % del tiempo durante el periodo de pruebas.                                                                                             | Media     | Un chequeo periódico registra 95 % o más.                                                 |
| RNF-05 | **Código ordenado:** estilo estándar de Python (PEP 8), separado en las tres capas, y la lógica funciona sin Flask.                                                                | Media     | flake8 no marca errores y pytest prueba la lógica sin abrir Flask.                        |
| RNF-06 | **Funciona en otros equipos:** Windows y Linux, instalando solo con `requirements.txt`. Los datos van en SQLite.                                                                   | Media     | Se instala y arranca en un equipo distinto al mío; los datos siguen al reiniciar.         |
| RNF-07 | **Errores claros:** se valida todo lo que se escribe; si algo falla se muestra un mensaje claro y la aplicación no se cae. Cada acción termina con un mensaje de éxito o de error. | Alta      | Una entrada inválida muestra su mensaje y la aplicación sigue funcionando.                |

## 6. Qué información se guarda

|Usuario||
|---|---|
|id|Número único|
|nombre|Nombre de la persona|
|correo|Único; se guarda en minúsculas|
|contraseña|Cifrada (hash), nunca el texto real|
|fecha de creación|Cuándo se registró|

|Hábito||
|---|---|
|id|Número único|
|usuario|De quién es el hábito|
|nombre|Como lo escribió la persona|
|nombre normalizado|El mismo nombre sin mayúsculas ni espacios extra; sirve para detectar repetidos|
|fecha de creación|Cuándo se creó|
|activo|Sí o no (eliminar lo deja en "no")|

## 7. Reglas

**Nombre de un hábito**

1. No puede estar vacío ni tener solo espacios → _"Debe escribir algo"_.
2. Máximo 60 caracteres → mensaje de límite.
3. No puede repetir otro hábito activo **de la misma persona**. Da igual mayúsculas y espacios al inicio o al final: `" estudiar "` es lo mismo que `"Estudiar"` → _"Debe escribir un hábito diferente"_.
4. Al editar, guardar con el mismo nombre que ya tenía **sí** se permite.

**Otras reglas**

- Eliminar un hábito lo oculta; no se borra de la base de datos.
- Si un hábito eliminado tenía el nombre "Estudiar", se puede crear otro con ese nombre.
- Una persona nunca ve ni cambia los hábitos de otra (responde "no encontrado").
- Toda validación ocurre en el servidor, aunque el navegador también avise.

## 8. Pantallas

- **Registro:** nombre, correo, contraseña y botón "Crear cuenta".
- **Inicio de sesión:** correo, contraseña y botón "Entrar".
- **Principal:** mensajes de resultado, formulario "Agregar hábito", campo de búsqueda, lista con botones "Editar" y "Eliminar", botón "Exportar CSV" y botón "Cerrar sesión". Sin hábitos: "Crea tu primer hábito".
- **Editar:** el nombre actual y un botón "Guardar".

## 9. API 

Todas las rutas empiezan con `/api`, usan JSON y, si algo sale mal, responden con un mensaje: `{ "error": "El campo nombre es obligatorio" }`.

|Método|Ruta|Para qué sirve|Qué se envía|Req.|
|---|---|---|---|---|
|POST|`/api/register`|Crear cuenta|nombre, correo, contrasena|RF-01|
|POST|`/api/login`|Iniciar sesión|correo, contrasena|RF-02|
|POST|`/api/logout`|Cerrar sesión|nada|RF-02|
|POST|`/api/habits`|Crear hábito|nombre|RF-03|
|GET|`/api/habits`|Ver hábitos (con `?q=texto` para buscar)|nada|RF-04|
|PUT|`/api/habits/{id}`|Editar hábito|nombre|RF-05|
|DELETE|`/api/habits/{id}`|Eliminar (ocultar) hábito|nada|RF-06|
|GET|`/api/habits/export`|Descargar CSV|nada|RF-07|

**Códigos de respuesta**

|Código|Significa|
|---|---|
|200|Todo bien|
|201|Se creó correctamente|
|400|Los datos enviados no son válidos|
|401|No ha iniciado sesión (o datos de acceso incorrectos)|
|404|No existe lo que se pidió|
|500|Falló algo dentro del servidor|

**Ejemplo:** enviar `POST /api/habits` con `{ "nombre": "Estudiar" }` responde `201` y `{ "id": 1, "nombre": "Estudiar" }`. Si el nombre viene vacío responde `400` y `{ "error": "Debe escribir algo" }`.

## 10. Pruebas de funcionamiento

|ID|Req.|Qué pruebo|Qué debe pasar|
|---|---|---|---|
|CP-01|RF-01|Crear cuenta con datos válidos|Se crea (201)|
|CP-02|RF-01|Crear cuenta con correo repetido o campo vacío|Error 400 con mensaje|
|CP-03|RF-02|Entrar con datos correctos|Entra (200)|
|CP-04|RF-02|Entrar con contraseña incorrecta|Rechaza (401)|
|CP-05|RNF-02|Pedir la lista de hábitos sin haber iniciado sesión|Rechaza (401)|
|CP-06|RF-03|Con lista vacía, crear "Estudiar"|Aparece en la lista|
|CP-07|RF-03|Existe "Estudiar"; crear " estudiar "|Error: "Debe escribir un hábito diferente"|
|CP-08|RF-03|Crear un nombre vacío o solo espacios|Error: "Debe escribir algo"|
|CP-09|RF-03|Crear un nombre de más de 60 caracteres|Error de límite|
|CP-10|RF-04|Existen "Estudiar" y "Leer"; buscar "est"|Solo sale "Estudiar"|
|CP-11|RF-04|La persona B mira su lista; la persona A tiene hábitos|B no ve los de A|
|CP-12|RF-05|Editar "Estudiar" a "Leer"; luego guardar sin cambiar nada|Ambas se guardan sin error|
|CP-13|RF-05|Existen "Estudiar" y "Leer"; editar "Leer" a "estudiar"|Error de repetido|
|CP-14|RF-06|Eliminar y confirmar; en otro intento, cancelar|Al confirmar desaparece; al cancelar sigue|
|CP-15|RF-07|Exportar con hábitos existentes|Se descarga un CSV con mis hábitos|
|CP-16|RNF-06|Cerrar y volver a abrir la aplicación|Los hábitos siguen ahí|
|CP-17|RNF-07|Enviar a la API un texto JSON mal escrito|Error 400 con mensaje; la aplicación sigue viva|

## 11. Pruebas de rendimiento 

Con **Locust** se simulan personas usando la aplicación (cada una inicia sesión primero). Se ejecuta con Gunicorn, no con el servidor de desarrollo de Flask, porque ese no representa el uso real.

|Escenario|Usuarios a la vez|Qué hacen|
|---|---|---|
|Carga normal|10|Ver la lista y buscar|
|Carga media|50|Ver la lista, crear y editar|
|Carga alta|100|Ver la lista durante 2 minutos seguidos|

**Qué se mide:** tiempo promedio y percentil 95 (en milisegundos), solicitudes por segundo, porcentaje de errores, y uso de procesador y memoria. Todo se compara con el RNF-01 (menos de 2 segundos) y se escribe una conclusión con posibles mejoras.

**Riesgo conocido:** SQLite guarda de a una escritura a la vez. Con 50 personas creando y editando puede haber esperas. Se reduce activando el modo WAL (permite leer mientras se escribe) y se anota en los resultados.



# FUTURO: versión 0.2 y posteriores

> **Nada de esta sección se construye en la versión 0.1.** Se deja escrita para no olvidar el rumbo del proyecto.

## Versión 0.2: marcar hábitos, racha y notas

- Un hábito se repite **todos los días** desde que se crea.
- Cada día se puede marcar un hábito como cumplido con una casilla (una vez por día, y se puede desmarcar).
- **Racha:** cuántos días seguidos cumpliste al menos un hábito. No se guarda como número: se calcula mirando los registros. El día de hoy sin cumplir **no** rompe la racha; se pierde cuando termina un día sin cumplir ninguno.
- **Nota diaria:** una por día, sobre cómo me siento, con botón de guardar. Solo se puede editar la de hoy.
- Todo funciona por usuario.
- Para esto se agregarán tablas nuevas (registros diarios y notas) ligadas al hábito, sin cambiar las que ya existen.

**Pruebas de la racha** (hoy es jueves en todos los casos)

1. Cumplí lunes, martes y miércoles; hoy no he marcado → racha 3.
2. Cumplí lunes y martes, miércoles no; hoy no he marcado → racha 0.
3. Igual que el 2, pero hoy marco un hábito → racha 1.
4. Primer día, nada marcado → racha 0; al marcar un hábito → racha 1.
5. Tengo dos hábitos y cumplo solo uno cada día, de lunes a miércoles; hoy no he marcado → racha 3.
6. Cumplí de lunes a miércoles; hoy marco el único hábito (racha 4) y lo desmarco (vuelve a 3).

## Ideas para más adelante

- Consejo al azar al pie de la página (de una lista fija de 5).
- Calendario para moverse entre días y marcar días pasados.
- Cambiar el aspecto con React (la API ya existe desde la v0.1, así que la parte visual se podría reemplazar sin tocar las reglas).
- Estadísticas y recordatorios.
- Recuperación de contraseña.