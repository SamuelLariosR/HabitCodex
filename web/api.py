# Rutas de la API JSON.

import csv
from functools import wraps
from io import StringIO

from flask import (
    Blueprint,
    Response,
    current_app,
    jsonify,
    request,
    session,
)

from logica.bd import conexion_bd
from logica.errores import (
    ErrorCredenciales,
    ErrorHabito,
    ErrorNoEncontrado,
)
from logica.habitos import (
    buscar_mis_habitos,
    crear_habito,
    editar_habito,
    eliminar_habito,
    listar_mis_habitos,
    obtener_habito,
)
from logica.usuarios import autenticar_usuario, registrar_usuario

bp_api = Blueprint("api", __name__, url_prefix="/api")

ERROR_DATOS = "Los datos enviados no son válidos"
ERROR_SERVIDOR = "Ha ocurrido un error en el servidor"
SIN_SESION = "Debe iniciar sesión para ver esa página"


def _ruta_bd():
    """Ruta configurada en create_app; no se lee el entorno aquí."""
    return current_app.config["DATABASE_PATH"]


def _error(mensaje, codigo):
    """Respuesta de error uniforme: siempre un objeto con 'error'."""
    return jsonify({"error": mensaje}), codigo


def _cuerpo():
    """Devuelve el JSON como diccionario, o None si no sirve."""
    datos = request.get_json(silent=True)
    return datos if isinstance(datos, dict) else None


def requiere_sesion_api(vista):
    """Responde 401 en vez de redirigir, porque esto es una API."""

    @wraps(vista)
    def envuelta(*args, **kwargs):
        if "usuario_id" not in session:
            return _error(SIN_SESION, 401)
        return vista(*args, **kwargs)

    return envuelta


def errores_api(vista):
    """Traduce los errores de la lógica al código HTTP que toca."""

    @wraps(vista)
    def envuelta(*args, **kwargs):
        try:
            return vista(*args, **kwargs)
        except ErrorCredenciales as error:
            return _error(error.mensaje, 401)
        except ErrorNoEncontrado as error:
            return _error(error.mensaje, 404)
        except ErrorHabito as error:
            return _error(error.mensaje, 400)

    return envuelta


@bp_api.post("/register")
@errores_api
def registrar():
    datos = _cuerpo()
    if datos is None:
        return _error(ERROR_DATOS, 400)

    with conexion_bd(_ruta_bd()) as conexion:
        cuenta = registrar_usuario(
            conexion,
            datos.get("nombre", ""),
            datos.get("correo", ""),
            datos.get("contrasena", ""),
        )
    return jsonify(
        {"id": cuenta["id"], "correo": cuenta["correo"]}
    ), 201


@bp_api.post("/login")
@errores_api
def iniciar_sesion():
    datos = _cuerpo()
    if datos is None:
        return _error(ERROR_DATOS, 400)

    with conexion_bd(_ruta_bd()) as conexion:
        usuario = autenticar_usuario(
            conexion,
            datos.get("correo", ""),
            datos.get("contrasena", ""),
        )
    session.clear()
    session["usuario_id"] = usuario["id"]
    session["usuario_nombre"] = usuario["nombre"]
    return jsonify(
        {
            "id": usuario["id"],
            "nombre": usuario["nombre"],
            "correo": usuario["correo"],
        }
    ), 200


@bp_api.post("/logout")
def cerrar_sesion():
    session.clear()
    return jsonify({"mensaje": "Sesión cerrada"}), 200


@bp_api.get("/habits")
@requiere_sesion_api
@errores_api
def listar():
    busqueda = request.args.get("q", "").strip()
    with conexion_bd(_ruta_bd()) as conexion:
        habitos = buscar_mis_habitos(
            conexion, session["usuario_id"], busqueda
        )
    return jsonify(
        [
            {"id": habito["id"], "nombre": habito["nombre"]}
            for habito in habitos
        ]
    )


@bp_api.post("/habits")
@requiere_sesion_api
@errores_api
def crear():
    datos = _cuerpo()
    if datos is None:
        return _error(ERROR_DATOS, 400)

    with conexion_bd(_ruta_bd()) as conexion:
        habito_id = crear_habito(
            conexion,
            session["usuario_id"],
            datos.get("nombre", ""),
        )
        habito = obtener_habito(
            conexion, habito_id, session["usuario_id"]
        )
    return jsonify(
        {"id": habito["id"], "nombre": habito["nombre"]}
    ), 201


@bp_api.put("/habits/<int:habito_id>")
@requiere_sesion_api
@errores_api
def editar(habito_id):
    datos = _cuerpo()
    if datos is None:
        return _error(ERROR_DATOS, 400)

    with conexion_bd(_ruta_bd()) as conexion:
        editar_habito(
            conexion,
            habito_id,
            session["usuario_id"],
            datos.get("nombre", ""),
        )
        habito = obtener_habito(
            conexion, habito_id, session["usuario_id"]
        )
    return jsonify(
        {"id": habito["id"], "nombre": habito["nombre"]}
    ), 200


@bp_api.delete("/habits/<int:habito_id>")
@requiere_sesion_api
@errores_api
def eliminar(habito_id):
    with conexion_bd(_ruta_bd()) as conexion:
        eliminar_habito(conexion, habito_id, session["usuario_id"])
    return jsonify({"mensaje": "Hábito eliminado"}), 200


@bp_api.get("/habits/export")
@requiere_sesion_api
@errores_api
def exportar():
    with conexion_bd(_ruta_bd()) as conexion:
        habitos = listar_mis_habitos(conexion, session["usuario_id"])

    salida = StringIO()
    escritor = csv.writer(salida, lineterminator="\n")
    escritor.writerow(["id", "nombre", "fecha_creacion"])
    for habito in habitos:
        escritor.writerow(
            [
                habito["id"],
                habito["nombre"],
                habito["fecha_creacion"],
            ]
        )
    return Response(
        salida.getvalue(),
        content_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": "attachment; filename=habitos.csv"
        },
    )


@bp_api.app_errorhandler(500)
def error_servidor(error):
    """La API nunca devuelve HTML, ni siquiera en un fallo interno."""
    if request.path.startswith("/api/"):
        return _error(ERROR_SERVIDOR, 500)
    return error
