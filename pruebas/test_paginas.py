# Pruebas de las páginas web: CP-05, CP-11 y el flujo con sesión.

import pytest

from datos.conexion import obtener_conexion
from datos.habitos_datos import guardar_habito
from datos.usuarios_datos import guardar_usuario
from logica.usuarios import hash_contrasena
from web import create_app

CONTRASENA = "mi-clave-larga"
# Un solo hash para todas las pruebas: el hash real ya se prueba aparte.
HASH = hash_contrasena(CONTRASENA)


@pytest.fixture
def app(tmp_path, monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "clave-de-pruebas")
    monkeypatch.setenv("DATABASE_URL", str(tmp_path / "paginas.db"))
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
            "2026-11-13T10:00:00",
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
            "2026-11-13T10:00:00",
        )
    finally:
        conexion.close()


def _entrar(cliente, correo, contrasena=CONTRASENA):
    return cliente.post(
        "/login",
        data={"correo": correo, "contrasena": contrasena},
        follow_redirects=True,
    )


def _valor(app, consulta, parametros):
    conexion = _conexion(app)
    try:
        return conexion.execute(consulta, parametros).fetchone()[0]
    finally:
        conexion.close()


def _texto(respuesta):
    return respuesta.get_data(as_text=True)


def test_cp05_sin_sesion_redirige_al_login(cliente):
    respuesta = cliente.get("/")
    assert respuesta.status_code == 302
    assert respuesta.headers["Location"].endswith("/login")


def test_cp05_no_deja_editar_sin_sesion(cliente):
    respuesta = cliente.get("/editar/1")
    assert respuesta.status_code == 302
    assert respuesta.headers["Location"].endswith("/login")


def test_cp11_b_no_ve_los_habitos_de_a(app, cliente):
    ana = _crear_usuario(app, "Ana", "ana@x.com")
    _crear_usuario(app, "Beto", "beto@x.com")
    _crear_habito(app, ana, "Estudiar")

    _entrar(cliente, "beto@x.com")
    html = _texto(cliente.get("/"))

    assert "Estudiar" not in html
    assert "Crea tu primer hábito" in html
    assert "Beto" in html


def test_registro_redirige_al_login_y_muestra_enlace(app, cliente):
    respuesta = cliente.post(
        "/registro",
        data={
            "nombre": "Ana",
            "correo": "ana@x.com",
            "contrasena": CONTRASENA,
        },
        follow_redirects=True,
    )
    html = _texto(respuesta)
    assert "Cuenta creada. Revisa el enlace de verificación" in html
    assert "/verificar/" in html


def test_verificar_correo_marca_la_cuenta(app, cliente):
    cliente.post(
        "/registro",
        data={
            "nombre": "Ana",
            "correo": "ana@x.com",
            "contrasena": CONTRASENA,
        },
    )
    token = _valor(
        app,
        "SELECT t.valor FROM tokens t JOIN usuarios u "
        "ON u.id = t.usuario WHERE u.correo = ?",
        ("ana@x.com",),
    )

    html = _texto(cliente.get(f"/verificar/{token}", follow_redirects=True))
    assert "Correo verificado" in html
    assert _valor(
        app,
        "SELECT verificado FROM usuarios WHERE correo = ?",
        ("ana@x.com",),
    ) == 1

    repetido = _texto(
        cliente.get(f"/verificar/{token}", follow_redirects=True)
    )
    assert "no sirve o ya caducó" in repetido


def test_login_correcto_entra_a_sus_habitos(app, cliente):
    _crear_usuario(app, "Ana", "ana@x.com")
    html = _texto(_entrar(cliente, "ANA@x.com"))
    assert "Bienvenido, Ana" in html
    assert "Mis hábitos" in html


def test_login_con_contrasena_incorrecta(app, cliente):
    _crear_usuario(app, "Ana", "ana@x.com")
    html = _texto(_entrar(cliente, "ana@x.com", "otra-clave-larga"))
    assert "Correo o contraseña incorrectos" in html
    assert "Mis hábitos" not in html


def test_login_con_campos_vacios_muestra_el_mensaje(app, cliente):
    html = _texto(
        cliente.post(
            "/login",
            data={"correo": "", "contrasena": ""},
            follow_redirects=True,
        )
    )
    assert "Debe escribir algo" in html
    assert "Correo o contraseña incorrectos" not in html


def test_las_paginas_no_se_guardan_en_cache(cliente):
    respuesta = cliente.get("/login")
    assert respuesta.headers["Cache-Control"] == "no-store"


def test_crear_habito_aparece_en_la_lista(app, cliente):
    _crear_usuario(app, "Ana", "ana@x.com")
    _entrar(cliente, "ana@x.com")
    html = _texto(
        cliente.post(
            "/habitos",
            data={"nombre": "Estudiar"},
            follow_redirects=True,
        )
    )
    assert "Hábito creado" in html
    assert "Estudiar" in html


def test_crear_habito_vacio_muestra_el_mensaje(app, cliente):
    _crear_usuario(app, "Ana", "ana@x.com")
    _entrar(cliente, "ana@x.com")
    html = _texto(
        cliente.post(
            "/habitos",
            data={"nombre": "   "},
            follow_redirects=True,
        )
    )
    assert "Debe escribir algo" in html


def test_crear_habito_con_html_se_muestra_escapado(app, cliente):
    _crear_usuario(app, "Ana", "ana@x.com")
    _entrar(cliente, "ana@x.com")
    html = _texto(
        cliente.post(
            "/habitos",
            data={"nombre": "<script>alert(1)</script>"},
            follow_redirects=True,
        )
    )
    assert "<script>alert(1)</script>" not in html
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in html


def test_crear_habito_repetido_muestra_el_mensaje(app, cliente):
    _crear_usuario(app, "Ana", "ana@x.com")
    _entrar(cliente, "ana@x.com")
    cliente.post("/habitos", data={"nombre": "Estudiar"})
    html = _texto(
        cliente.post(
            "/habitos",
            data={"nombre": " estudiar "},
            follow_redirects=True,
        )
    )
    assert "Debe escribir un hábito diferente" in html


def test_editar_cambia_el_nombre(app, cliente):
    ana = _crear_usuario(app, "Ana", "ana@x.com")
    habito = _crear_habito(app, ana, "Estudiar")
    _entrar(cliente, "ana@x.com")

    assert "Estudiar" in _texto(cliente.get(f"/editar/{habito}"))

    html = _texto(
        cliente.post(
            f"/editar/{habito}",
            data={"nombre": "Leer"},
            follow_redirects=True,
        )
    )
    assert "Hábito actualizado" in html
    assert "Leer" in html
    assert "Estudiar" not in html


def test_editar_con_el_mismo_nombre_es_valido(app, cliente):
    ana = _crear_usuario(app, "Ana", "ana@x.com")
    habito = _crear_habito(app, ana, "Estudiar")
    _entrar(cliente, "ana@x.com")

    html = _texto(
        cliente.post(
            f"/editar/{habito}",
            data={"nombre": "Estudiar"},
            follow_redirects=True,
        )
    )
    assert "Hábito actualizado" in html


def test_editar_habito_ajeno_dice_no_encontrado(app, cliente):
    ana = _crear_usuario(app, "Ana", "ana@x.com")
    habito = _crear_habito(app, ana, "Estudiar")
    _crear_usuario(app, "Beto", "beto@x.com")
    _entrar(cliente, "beto@x.com")

    html = _texto(
        cliente.get(f"/editar/{habito}", follow_redirects=True)
    )
    assert "No se encontró el hábito" in html
    assert "Estudiar" not in html


def test_eliminar_oculta_el_habito(app, cliente):
    ana = _crear_usuario(app, "Ana", "ana@x.com")
    habito = _crear_habito(app, ana, "Estudiar")
    _entrar(cliente, "ana@x.com")

    html = _texto(
        cliente.post(f"/eliminar/{habito}", follow_redirects=True)
    )
    assert "Hábito eliminado" in html
    assert "Estudiar" not in html
    assert _valor(
        app,
        "SELECT activo FROM habitos WHERE id = ?",
        (habito,),
    ) == 0


def test_cerrar_sesion_vuelve_al_login(app, cliente):
    _crear_usuario(app, "Ana", "ana@x.com")
    _entrar(cliente, "ana@x.com")

    html = _texto(cliente.post("/logout", follow_redirects=True))
    assert "Sesión cerrada" in html

    respuesta = cliente.get("/")
    assert respuesta.status_code == 302
    assert respuesta.headers["Location"].endswith("/login")
