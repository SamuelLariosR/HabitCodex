# Pruebas de la API JSON: CP-05 (API), CP-17 y cada endpoint.

import pytest

from datos.conexion import obtener_conexion
from datos.habitos_datos import guardar_habito
from datos.usuarios_datos import guardar_usuario
from logica.usuarios import hash_contrasena
from web import create_app

CONTRASENA = "mi-clave-larga"
HASH = hash_contrasena(CONTRASENA)


@pytest.fixture
def app(tmp_path, monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "clave-de-pruebas")
    monkeypatch.setenv("DATABASE_URL", str(tmp_path / "api.db"))
    aplicacion = create_app()
    aplicacion.config["TESTING"] = True
    return aplicacion


@pytest.fixture
def cliente(app):
    return app.test_client()


def _conexion(app):
    return obtener_conexion(app.config["DATABASE_PATH"])


def _crear_usuario(app, nombre, correo):
    conexion = _conexion(app)
    try:
        return guardar_usuario(
            conexion,
            nombre,
            correo,
            HASH,
            "2026-11-15T10:00:00",
        )
    finally:
        conexion.close()


def _crear_habito(app, usuario, nombre):
    conexion = _conexion(app)
    try:
        return guardar_habito(
            conexion,
            usuario,
            nombre,
            nombre.lower(),
            "2026-11-15T10:00:00",
        )
    finally:
        conexion.close()


def _valor(app, consulta, parametros=()):
    conexion = _conexion(app)
    try:
        return conexion.execute(consulta, parametros).fetchone()[0]
    finally:
        conexion.close()


def _entrar(cliente, correo="ana@x.com", contrasena=CONTRASENA):
    return cliente.post(
        "/api/login",
        json={"correo": correo, "contrasena": contrasena},
    )


def _json(respuesta):
    return respuesta.get_json()


@pytest.mark.parametrize(
    "metodo, ruta",
    [
        ("get", "/api/habits"),
        ("post", "/api/habits"),
        ("put", "/api/habits/1"),
        ("delete", "/api/habits/1"),
        ("get", "/api/habits/export"),
    ],
)
def test_cp05_api_sin_sesion_responde_401(cliente, metodo, ruta):
    respuesta = getattr(cliente, metodo)(ruta)
    assert respuesta.status_code == 401
    assert _json(respuesta) == {
        "error": "Debe iniciar sesión para ver esa página"
    }


def test_cp01_api_crea_cuenta(app, cliente):
    respuesta = cliente.post(
        "/api/register",
        json={
            "nombre": "Ana",
            "correo": "ANA@X.COM",
            "contrasena": CONTRASENA,
        },
    )
    assert respuesta.status_code == 201
    datos = _json(respuesta)
    assert datos["correo"] == "ana@x.com"
    assert "contrasena" not in datos
    assert _valor(
        app,
        "SELECT verificado FROM usuarios WHERE correo = ?",
        ("ana@x.com",),
    ) == 0
    assert _valor(app, "SELECT COUNT(*) FROM tokens") == 1


def test_cp02_api_correo_repetido(cliente):
    datos = {
        "nombre": "Ana",
        "correo": "ana@x.com",
        "contrasena": CONTRASENA,
    }
    cliente.post("/api/register", json=datos)
    respuesta = cliente.post("/api/register", json=datos)
    assert respuesta.status_code == 400
    assert _json(respuesta)["error"] == "Ese correo ya está registrado"


@pytest.mark.parametrize("campo", ["nombre", "correo", "contrasena"])
def test_cp02_api_campo_vacio(cliente, campo):
    datos = {
        "nombre": "Ana",
        "correo": "ana@x.com",
        "contrasena": CONTRASENA,
    }
    datos[campo] = ""
    respuesta = cliente.post("/api/register", json=datos)
    assert respuesta.status_code == 400
    assert _json(respuesta)["error"] == "Debe escribir algo"


def test_cp02_api_correo_invalido(cliente):
    respuesta = cliente.post(
        "/api/register",
        json={
            "nombre": "Ana",
            "correo": "ana@",
            "contrasena": CONTRASENA,
        },
    )
    assert respuesta.status_code == 400
    assert _json(respuesta)["error"] == "Escriba un correo válido"


def test_cp02_api_contrasena_corta(cliente):
    respuesta = cliente.post(
        "/api/register",
        json={
            "nombre": "Ana",
            "correo": "ana@x.com",
            "contrasena": "a" * 11,
        },
    )
    assert respuesta.status_code == 400
    assert _json(respuesta)["error"] == (
        "La contraseña debe tener entre 12 y 16 caracteres"
    )


def test_cp03_api_login_correcto(app, cliente):
    _crear_usuario(app, "Ana", "ana@x.com")
    respuesta = _entrar(cliente)
    assert respuesta.status_code == 200
    datos = _json(respuesta)
    assert datos["nombre"] == "Ana"
    assert datos["correo"] == "ana@x.com"
    assert "contrasena" not in datos
    assert cliente.get("/api/habits").status_code == 200


def test_cp03_api_login_ignora_mayusculas(app, cliente):
    _crear_usuario(app, "Ana", "ana@x.com")
    respuesta = _entrar(cliente, " ANA@X.COM ")
    assert respuesta.status_code == 200


def test_cp03_api_login_con_campo_vacio(cliente):
    respuesta = cliente.post(
        "/api/login", json={"correo": "", "contrasena": ""}
    )
    assert respuesta.status_code == 400
    assert _json(respuesta)["error"] == "Debe escribir algo"


def test_cp04_api_credenciales_incorrectas(app, cliente):
    _crear_usuario(app, "Ana", "ana@x.com")
    casos = [
        ("ana@x.com", "otra-clave-larga"),
        ("nadie@x.com", CONTRASENA),
    ]
    for correo, contrasena in casos:
        respuesta = _entrar(cliente, correo, contrasena)
        assert respuesta.status_code == 401
        assert _json(respuesta)["error"] == (
            "Correo o contraseña incorrectos"
        )


def test_api_cerrar_sesion(app, cliente):
    _crear_usuario(app, "Ana", "ana@x.com")
    assert _entrar(cliente).status_code == 200
    respuesta = cliente.post("/api/logout")
    assert respuesta.status_code == 200
    assert _json(respuesta)["mensaje"] == "Sesión cerrada"
    assert cliente.get("/api/habits").status_code == 401


def test_api_crear_y_listar_habito(app, cliente):
    _crear_usuario(app, "Ana", "ana@x.com")
    _entrar(cliente)
    respuesta = cliente.post(
        "/api/habits", json={"nombre": "  Estudiar  "}
    )
    assert respuesta.status_code == 201
    datos = _json(respuesta)
    assert datos["nombre"] == "Estudiar"
    assert _json(cliente.get("/api/habits")) == [
        {"id": datos["id"], "nombre": "Estudiar"}
    ]


def test_api_crear_habito_vacio(app, cliente):
    _crear_usuario(app, "Ana", "ana@x.com")
    _entrar(cliente)
    respuesta = cliente.post("/api/habits", json={"nombre": "   "})
    assert respuesta.status_code == 400
    assert _json(respuesta)["error"] == "Debe escribir algo"


def test_api_crear_habito_repetido(app, cliente):
    _crear_usuario(app, "Ana", "ana@x.com")
    _entrar(cliente)
    cliente.post("/api/habits", json={"nombre": "Estudiar"})
    respuesta = cliente.post(
        "/api/habits", json={"nombre": " estudiar "}
    )
    assert respuesta.status_code == 400
    assert _json(respuesta)["error"] == "Debe escribir un hábito diferente"


def test_cp11_api_solo_muestra_los_propios(app, cliente):
    ana = _crear_usuario(app, "Ana", "ana@x.com")
    _crear_habito(app, ana, "Estudiar")
    _crear_usuario(app, "Beto", "beto@x.com")
    _entrar(cliente, "beto@x.com")
    assert _json(cliente.get("/api/habits")) == []


def test_cp12_api_edita_habito(app, cliente):
    ana = _crear_usuario(app, "Ana", "ana@x.com")
    habito = _crear_habito(app, ana, "Estudiar")
    _entrar(cliente)
    respuesta = cliente.put(
        f"/api/habits/{habito}", json={"nombre": "Leer"}
    )
    assert respuesta.status_code == 200
    assert _json(respuesta) == {"id": habito, "nombre": "Leer"}
    assert _json(cliente.get("/api/habits")) == [
        {"id": habito, "nombre": "Leer"}
    ]


def test_cp12_api_permite_el_mismo_nombre(app, cliente):
    ana = _crear_usuario(app, "Ana", "ana@x.com")
    habito = _crear_habito(app, ana, "Estudiar")
    _entrar(cliente)
    respuesta = cliente.put(
        f"/api/habits/{habito}", json={"nombre": "Estudiar"}
    )
    assert respuesta.status_code == 200


def test_cp13_api_editar_a_repetido(app, cliente):
    ana = _crear_usuario(app, "Ana", "ana@x.com")
    _crear_habito(app, ana, "Estudiar")
    habito = _crear_habito(app, ana, "Leer")
    _entrar(cliente)
    respuesta = cliente.put(
        f"/api/habits/{habito}", json={"nombre": "estudiar"}
    )
    assert respuesta.status_code == 400
    assert _json(respuesta)["error"] == (
        "Debe escribir un hábito diferente"
    )


def test_cp11_api_no_toca_habito_ajeno(app, cliente):
    ana = _crear_usuario(app, "Ana", "ana@x.com")
    habito = _crear_habito(app, ana, "Estudiar")
    _crear_usuario(app, "Beto", "beto@x.com")
    _entrar(cliente, "beto@x.com")
    respuesta = cliente.put(
        f"/api/habits/{habito}", json={"nombre": "Leer"}
    )
    assert respuesta.status_code == 404
    assert _json(respuesta)["error"] == "No se encontró el hábito"
    respuesta = cliente.delete(f"/api/habits/{habito}")
    assert respuesta.status_code == 404
    assert _json(respuesta)["error"] == "No se encontró el hábito"


def test_cp14_api_elimina_habito(app, cliente):
    ana = _crear_usuario(app, "Ana", "ana@x.com")
    habito = _crear_habito(app, ana, "Estudiar")
    _entrar(cliente)
    respuesta = cliente.delete(f"/api/habits/{habito}")
    assert respuesta.status_code == 200
    assert _json(respuesta)["mensaje"] == "Hábito eliminado"
    assert _json(cliente.get("/api/habits")) == []
    respuesta = cliente.delete(f"/api/habits/{habito}")
    assert respuesta.status_code == 404
    assert _json(respuesta)["error"] == "No se encontró el hábito"


def test_cp17_json_mal_escrito_no_tumba_la_api(app, cliente):
    _crear_usuario(app, "Ana", "ana@x.com")
    _entrar(cliente)
    respuesta = cliente.post(
        "/api/habits",
        data="{esto no es json",
        content_type="application/json",
    )
    assert respuesta.status_code == 400
    assert _json(respuesta) == {
        "error": "Los datos enviados no son válidos"
    }
    assert cliente.get("/api/habits").status_code == 200


def test_api_rechaza_json_que_no_es_objeto(app, cliente):
    _crear_usuario(app, "Ana", "ana@x.com")
    _entrar(cliente)
    for cuerpo in (["Estudiar"], "Estudiar"):
        respuesta = cliente.post("/api/habits", json=cuerpo)
        assert respuesta.status_code == 400
        assert _json(respuesta)["error"] == (
            "Los datos enviados no son válidos"
        )


def test_api_exporta_solo_mis_habitos(app, cliente):
    ana = _crear_usuario(app, "Ana", "ana@x.com")
    _crear_habito(app, ana, "Estudiar")
    beto = _crear_usuario(app, "Beto", "beto@x.com")
    _crear_habito(app, beto, "Correr")
    _entrar(cliente)
    respuesta = cliente.get("/api/habits/export")
    assert respuesta.status_code == 200
    assert respuesta.mimetype == "text/csv"
    texto = respuesta.get_data(as_text=True)
    assert "Estudiar" in texto
    assert "Correr" not in texto
    assert "attachment" in respuesta.headers["Content-Disposition"]


def test_la_sesion_de_la_web_sirve_para_la_api(app, cliente):
    _crear_usuario(app, "Ana", "ana@x.com")
    html = cliente.post(
        "/login",
        data={"correo": "ana@x.com", "contrasena": CONTRASENA},
        follow_redirects=True,
    ).get_data(as_text=True)
    assert "Mis hábitos" in html
    assert cliente.get("/api/habits").status_code == 200


def test_el_login_de_la_api_sirve_para_la_web(app, cliente):
    _crear_usuario(app, "Ana", "ana@x.com")
    assert _entrar(cliente).status_code == 200
    html = cliente.get("/").get_data(as_text=True)
    assert "Mis hábitos" in html


def test_cp10_api_buscar_filtra(app, cliente):
    ana = _crear_usuario(app, "Ana", "ana@x.com")
    estudiar = _crear_habito(app, ana, "Estudiar")
    _crear_habito(app, ana, "Leer")
    _entrar(cliente)

    respuesta = cliente.get("/api/habits?q=est")
    assert respuesta.status_code == 200
    assert _json(respuesta) == [
        {"id": estudiar, "nombre": "Estudiar"}
    ]


def test_cp10_api_buscar_ignora_mayusculas_y_espacios(app, cliente):
    ana = _crear_usuario(app, "Ana", "ana@x.com")
    estudiar = _crear_habito(app, ana, "Estudiar")
    _entrar(cliente)

    assert _json(cliente.get("/api/habits?q=+EST+")) == [
        {"id": estudiar, "nombre": "Estudiar"}
    ]


def test_cp10_api_buscar_sin_resultados(app, cliente):
    ana = _crear_usuario(app, "Ana", "ana@x.com")
    _crear_habito(app, ana, "Estudiar")
    _entrar(cliente)

    respuesta = cliente.get("/api/habits?q=correr")
    assert respuesta.status_code == 200
    assert _json(respuesta) == []


def test_cp10_api_busqueda_vacia_devuelve_todos(app, cliente):
    ana = _crear_usuario(app, "Ana", "ana@x.com")
    estudiar = _crear_habito(app, ana, "Estudiar")
    leer = _crear_habito(app, ana, "Leer")
    _entrar(cliente)

    respuesta = cliente.get("/api/habits?q=")
    assert _json(respuesta) == [
        {"id": estudiar, "nombre": "Estudiar"},
        {"id": leer, "nombre": "Leer"},
    ]


def test_cp10_api_buscar_no_mezcla_habitos_ajenos(app, cliente):
    ana = _crear_usuario(app, "Ana", "ana@x.com")
    _crear_habito(app, ana, "Estudiar")
    _crear_usuario(app, "Beto", "beto@x.com")
    _entrar(cliente, "beto@x.com")

    assert _json(cliente.get("/api/habits?q=est")) == []


def test_cp10_api_buscar_toma_los_comodines_como_texto(app, cliente):
    ana = _crear_usuario(app, "Ana", "ana@x.com")
    agua = _crear_habito(app, ana, "Beber 100% agua")
    _crear_habito(app, ana, "Leer")
    _entrar(cliente)

    assert _json(cliente.get("/api/habits?q=%25")) == [
        {"id": agua, "nombre": "Beber 100% agua"}
    ]
