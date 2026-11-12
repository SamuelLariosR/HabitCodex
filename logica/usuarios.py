# logica/usuarios.py

import sqlite3
from datetime import datetime, timedelta
from hashlib import pbkdf2_hmac
from hmac import compare_digest
from secrets import token_bytes, token_urlsafe

from datos.tokens_datos import (
    buscar_token,
    guardar_token,
    marcar_token_usado,
)
from datos.usuarios_datos import (
    buscar_usuario_por_correo,
    guardar_usuario,
    marcar_usuario_verificado,
)
from logica.errores import (
    ErrorCampoVacio,
    ErrorLongitudContrasena,
    ErrorCorreoInvalido,
    ErrorCorreoRepetido,
    ErrorCredenciales,
)

ALGORITMO = "pbkdf2_sha256"
ITERACIONES = 600_000
LARGO_MINIMO = 12
LARGO_MAXIMO = 16
BYTES_SAL = 16
HORAS_TOKEN = 24


def _ahora():
    """Fecha en texto y sin microsegundos, como se guarda en la base."""
    return datetime.now().isoformat(timespec="seconds")


def normalizar_correo(correo):
    """Correo comparable: sin espacios extremos y en minusculas."""
    return correo.strip().lower() if isinstance(correo, str) else ""


def validar_correo(correo):
    """Devuelve el correo normalizado o lanza el error que corresponda."""
    correo = normalizar_correo(correo)
    if not correo:
        raise ErrorCampoVacio()
    partes = correo.split("@")
    if len(partes) != 2:
        raise ErrorCorreoInvalido()
    usuario, dominio = partes
    if not usuario or "." not in dominio:
        raise ErrorCorreoInvalido()
    if dominio.startswith(".") or dominio.endswith("."):
        raise ErrorCorreoInvalido()
    if any(caracter.isspace() for caracter in correo):
        raise ErrorCorreoInvalido()
    return correo


def validar_nombre_usuario(nombre):
    """Devuelve el nombre recortado; vacio o sin texto es un error."""
    texto = nombre if isinstance(nombre, str) else ""
    texto = texto.strip()
    if not texto:
        raise ErrorCampoVacio()
    return texto


def validar_contrasena(contrasena):
    """Devuelve la contrasena sin recortar; los espacios cuentan."""
    if not isinstance(contrasena, str) or not contrasena:
        raise ErrorCampoVacio()
    if not LARGO_MINIMO <= len(contrasena) <= LARGO_MAXIMO:
        raise ErrorLongitudContrasena()
    return contrasena


def hash_contrasena(contrasena, sal=None, iteraciones=ITERACIONES):
    """Devuelve pbkdf2_sha256$iteraciones$sal$hash."""
    sal = sal or token_bytes(BYTES_SAL).hex()
    calculado = pbkdf2_hmac(
        "sha256",
        contrasena.encode("utf-8"),
        bytes.fromhex(sal),
        iteraciones,
    ).hex()
    return f"{ALGORITMO}${iteraciones}${sal}${calculado}"


def verificar_contrasena(contrasena, guardado):
    """True si la contrasena produce el mismo hash que el guardado."""
    if not isinstance(contrasena, str) or not isinstance(guardado, str):
        return False
    partes = guardado.split("$")
    if len(partes) != 4 or partes[0] != ALGORITMO:
        return False
    _, iteraciones, sal, esperado = partes
    try:
        calculado = pbkdf2_hmac(
            "sha256",
            contrasena.encode("utf-8"),
            bytes.fromhex(sal),
            int(iteraciones),
        ).hex()
    except ValueError:
        return False
    return compare_digest(calculado, esperado)


def registrar_usuario(conexion, nombre, correo, contrasena):
    """Crea la cuenta y su token. Devuelve id, correo y token."""
    nombre = validar_nombre_usuario(nombre)
    correo = validar_correo(correo)
    contrasena = validar_contrasena(contrasena)

    if buscar_usuario_por_correo(conexion, correo) is not None:
        raise ErrorCorreoRepetido()

    try:
        usuario_id = guardar_usuario(
            conexion, nombre, correo, hash_contrasena(contrasena), _ahora()
        )
    except sqlite3.IntegrityError:
        # Otra peticion gano la carrera del UNIQUE del correo.
        raise ErrorCorreoRepetido() from None

    valor = token_urlsafe(32)
    expiracion = (datetime.now() + timedelta(hours=HORAS_TOKEN)).isoformat(
        timespec="seconds"
    )
    guardar_token(conexion, usuario_id, valor, expiracion)
    return {"id": usuario_id, "correo": correo, "token": valor}


def autenticar_usuario(conexion, correo, contrasena):
    """Devuelve el usuario si todo coincide, o lanza ErrorCredenciales."""
    usuario = buscar_usuario_por_correo(conexion, normalizar_correo(correo))
    if usuario is None:
        raise ErrorCredenciales()
    if not verificar_contrasena(contrasena, usuario["contrasena"]):
        raise ErrorCredenciales()
    return usuario


def verificar_correo(conexion, valor):
    """Marca el correo como verificado. False si el token no sirve."""
    token = buscar_token(conexion, valor) if isinstance(valor, str) else None
    if token is None or token["usado"]:
        return False
    if token["expiracion"] < _ahora():
        return False
    marcar_token_usado(conexion, token["id"])
    marcar_usuario_verificado(conexion, token["usuario"])
    return True
