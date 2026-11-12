# Pruebas de registro y de inicio de sesion: CP-01 a CP-04.

from datetime import datetime

import pytest

from datos.tokens_datos import buscar_token, guardar_token
from datos.usuarios_datos import buscar_usuario_por_id
from logica.errores import (
    ErrorCampoVacio,
    ErrorLongitudContrasena,
    ErrorCorreoInvalido,
    ErrorCorreoRepetido,
    ErrorCredenciales,
)
from logica.usuarios import (
    autenticar_usuario,
    hash_contrasena,
    registrar_usuario,
    verificar_contrasena,
    verificar_correo,
)

CONTRASENA = "mi-clave-larga"


def test_cp01_registrar_cuenta(conexion):
    cuenta = registrar_usuario(conexion, "Ana", "ana@x.com", CONTRASENA)
    assert cuenta["id"] > 0
    assert cuenta["correo"] == "ana@x.com"
    usuario = buscar_usuario_por_id(conexion, cuenta["id"])
    assert usuario["nombre"] == "Ana"
    assert usuario["verificado"] == 0


def test_cp01_crea_token_de_verificacion(conexion):
    cuenta = registrar_usuario(conexion, "Ana", "ana@x.com", CONTRASENA)
    token = buscar_token(conexion, cuenta["token"])
    assert token is not None
    assert token["usuario"] == cuenta["id"]
    assert token["usado"] == 0
    assert token["expiracion"] > datetime.now().isoformat()


def test_cp01_correo_guardado_en_minusculas(conexion):
    cuenta = registrar_usuario(conexion, "Ana", "  ANA@X.COM ", CONTRASENA)
    assert cuenta["correo"] == "ana@x.com"
    usuario = buscar_usuario_por_id(conexion, cuenta["id"])
    assert usuario["correo"] == "ana@x.com"


def test_cp01_contrasena_guardada_cifrada(conexion):
    cuenta = registrar_usuario(conexion, "Ana", "ana@x.com", CONTRASENA)
    usuario = buscar_usuario_por_id(conexion, cuenta["id"])
    guardada = usuario["contrasena"]
    assert guardada.startswith("pbkdf2_sha256$600000$")
    assert CONTRASENA not in guardada


def test_cp01_cada_cuenta_tiene_su_sal(conexion):
    una = registrar_usuario(conexion, "Ana", "ana@x.com", CONTRASENA)
    otra = registrar_usuario(conexion, "Beto", "beto@x.com", CONTRASENA)
    hash_ana = buscar_usuario_por_id(conexion, una["id"])["contrasena"]
    hash_beto = buscar_usuario_por_id(conexion, otra["id"])["contrasena"]
    assert hash_ana != hash_beto


def test_cp02_correo_repetido(conexion):
    registrar_usuario(conexion, "Ana", "ana@x.com", CONTRASENA)
    with pytest.raises(ErrorCorreoRepetido) as error:
        registrar_usuario(conexion, "Otra", "ana@x.com", CONTRASENA)
    assert error.value.mensaje == "Ese correo ya está registrado"


def test_cp02_correo_repetido_ignora_mayusculas(conexion):
    registrar_usuario(conexion, "Ana", "ana@x.com", CONTRASENA)
    with pytest.raises(ErrorCorreoRepetido):
        registrar_usuario(conexion, "Otra", " ANA@X.com", CONTRASENA)


@pytest.mark.parametrize("campo", ["nombre", "correo", "contrasena"])
def test_cp02_campo_vacio(conexion, campo):
    datos = {
        "nombre": "Ana",
        "correo": "ana@x.com",
        "contrasena": CONTRASENA,
    }
    datos[campo] = "" if campo == "contrasena" else "   "
    with pytest.raises(ErrorCampoVacio):
        registrar_usuario(
            conexion, datos["nombre"], datos["correo"], datos["contrasena"]
        )


@pytest.mark.parametrize(
    "correo",
    ["ana", "ana@", "@x.com", "ana@x", "ana@@x.com", "a na@x.com"],
)
def test_cp02_correo_invalido(conexion, correo):
    with pytest.raises(ErrorCorreoInvalido):
        registrar_usuario(conexion, "Ana", correo, CONTRASENA)


@pytest.mark.parametrize("largo", [11, 17, 100])
def test_cp02_contrasena_de_largo_incorrecto(conexion, largo):
    with pytest.raises(ErrorLongitudContrasena) as error:
        registrar_usuario(conexion, "Ana", "ana@x.com", "a" * largo)
    assert error.value.mensaje == (
        "La contraseña debe tener entre 12 y 16 caracteres"
    )


@pytest.mark.parametrize("largo", [12, 16])
def test_cp02_limites_de_contrasena(conexion, largo):
    cuenta = registrar_usuario(conexion, "Ana", "ana@x.com", "a" * largo)
    assert cuenta["id"] > 0


def test_cp03_entrar_con_datos_correctos(conexion):
    cuenta = registrar_usuario(conexion, "Ana", "ana@x.com", CONTRASENA)
    usuario = autenticar_usuario(conexion, "ana@x.com", CONTRASENA)
    assert usuario["id"] == cuenta["id"]
    assert usuario["nombre"] == "Ana"


def test_cp03_correo_con_mayusculas_al_entrar(conexion):
    registrar_usuario(conexion, "Ana", "ana@x.com", CONTRASENA)
    usuario = autenticar_usuario(conexion, " ANA@X.com ", CONTRASENA)
    assert usuario["correo"] == "ana@x.com"


def test_cp03_entrar_sin_verificar_correo(conexion):
    registrar_usuario(conexion, "Ana", "ana@x.com", CONTRASENA)
    usuario = autenticar_usuario(conexion, "ana@x.com", CONTRASENA)
    assert usuario["verificado"] == 0


def test_cp04_contrasena_incorrecta(conexion):
    registrar_usuario(conexion, "Ana", "ana@x.com", CONTRASENA)
    with pytest.raises(ErrorCredenciales):
        autenticar_usuario(conexion, "ana@x.com", "otra-contrasena")


def test_cp04_correo_inexistente(conexion):
    with pytest.raises(ErrorCredenciales):
        autenticar_usuario(conexion, "nadie@x.com", CONTRASENA)


def test_cp04_mismo_mensaje_en_los_dos_casos(conexion):
    registrar_usuario(conexion, "Ana", "ana@x.com", CONTRASENA)
    with pytest.raises(ErrorCredenciales) as mala_clave:
        autenticar_usuario(conexion, "ana@x.com", "otra-contrasena")
    with pytest.raises(ErrorCredenciales) as no_existe:
        autenticar_usuario(conexion, "nadie@x.com", CONTRASENA)
    assert mala_clave.value.mensaje == no_existe.value.mensaje
    assert mala_clave.value.mensaje == "Correo o contraseña incorrectos"


def test_hash_y_verificacion():
    guardado = hash_contrasena(CONTRASENA)
    assert verificar_contrasena(CONTRASENA, guardado) is True
    assert verificar_contrasena("otra-cosa-larga", guardado) is False


def test_verificar_contrasena_con_texto_raro():
    assert verificar_contrasena(CONTRASENA, "basura") is False
    assert verificar_contrasena(CONTRASENA, None) is False
    assert verificar_contrasena(CONTRASENA, "pbkdf2_sha256$x$x$x") is False


def test_verificar_correo_con_token_valido(conexion):
    cuenta = registrar_usuario(conexion, "Ana", "ana@x.com", CONTRASENA)
    assert verificar_correo(conexion, cuenta["token"]) is True
    usuario = buscar_usuario_por_id(conexion, cuenta["id"])
    assert usuario["verificado"] == 1
    assert buscar_token(conexion, cuenta["token"])["usado"] == 1


def test_verificar_correo_no_sirve_dos_veces(conexion):
    cuenta = registrar_usuario(conexion, "Ana", "ana@x.com", CONTRASENA)
    verificar_correo(conexion, cuenta["token"])
    assert verificar_correo(conexion, cuenta["token"]) is False


def test_verificar_correo_con_token_inventado(conexion):
    registrar_usuario(conexion, "Ana", "ana@x.com", CONTRASENA)
    assert verificar_correo(conexion, "inventado") is False
    assert verificar_correo(conexion, None) is False


def test_verificar_correo_con_token_caducado(conexion):
    cuenta = registrar_usuario(conexion, "Ana", "ana@x.com", CONTRASENA)
    guardar_token(conexion, cuenta["id"], "viejo", "2020-01-01T00:00:00")
    assert verificar_correo(conexion, "viejo") is False
    assert buscar_usuario_por_id(conexion, cuenta["id"])["verificado"] == 0


def test_mensajes_canonicos_de_usuarios():
    assert ErrorCampoVacio.mensaje == "Debe escribir algo"
    assert ErrorCorreoRepetido.mensaje == "Ese correo ya está registrado"
    assert ErrorCorreoInvalido.mensaje == "Escriba un correo válido"
    assert ErrorCredenciales.mensaje == "Correo o contraseña incorrectos"
    assert ErrorLongitudContrasena.mensaje == (
        "La contraseña debe tener entre 12 y 16 caracteres"
    )
