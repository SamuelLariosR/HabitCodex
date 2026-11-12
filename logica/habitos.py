# logica/habitos.py

from datetime import datetime

from datos.habitos_datos import (
    actualizar_nombre,
    buscar_habito,
    buscar_por_nombre_normalizado,
    desactivar_habito,
    guardar_habito,
    listar_habitos,
)
from logica.errores import (
    ErrorNombreLargo,
    ErrorNombreRepetido,
    ErrorCampoVacio,
    ErrorNoEncontrado,
)

LARGO_MAXIMO = 60


def normalizar_nombre(nombre):
    """Version comparable del nombre: sin extremos y en minusculas."""
    return nombre.strip().lower()


def validar_nombre(nombre):
    """Devuelve el nombre recortado o lanza el error que corresponda."""
    texto = nombre if isinstance(nombre, str) else ""
    texto = texto.strip()
    if not texto:
        raise ErrorCampoVacio()
    if len(texto) > LARGO_MAXIMO:
        raise ErrorNombreLargo()
    return texto


def listar_mis_habitos(conexion, usuario):
    """Habitos activos del usuario, del mas antiguo al mas nuevo."""
    return listar_habitos(conexion, usuario)


def obtener_habito(conexion, habito_id, usuario):
    """Devuelve el habito activo del usuario o lanza ErrorNoEncontrado."""
    habito = buscar_habito(conexion, habito_id, usuario)
    if habito is None:
        raise ErrorNoEncontrado()
    return habito


def crear_habito(conexion, usuario, nombre):
    """Valida el nombre, comprueba duplicados y guarda. Devuelve el id."""
    nombre = validar_nombre(nombre)
    normalizado = normalizar_nombre(nombre)
    if buscar_por_nombre_normalizado(conexion, usuario, normalizado):
        raise ErrorNombreRepetido()
    fecha_creacion = datetime.now().isoformat(timespec="seconds")
    return guardar_habito(
        conexion, usuario, nombre, normalizado, fecha_creacion
    )


def editar_habito(conexion, habito_id, usuario, nombre):
    """Cambia el nombre; el mismo que ya tenia es valido. True si cambio."""
    nombre = validar_nombre(nombre)
    obtener_habito(conexion, habito_id, usuario)
    normalizado = normalizar_nombre(nombre)
    otro = buscar_por_nombre_normalizado(conexion, usuario, normalizado)
    if otro is not None and otro["id"] != habito_id:
        raise ErrorNombreRepetido()
    return actualizar_nombre(
        conexion, habito_id, usuario, nombre, normalizado
    )


def eliminar_habito(conexion, habito_id, usuario):
    """Oculta el habito. Lanza ErrorNoEncontrado si no es suyo."""
    if not desactivar_habito(conexion, habito_id, usuario):
        raise ErrorNoEncontrado()
    return True
