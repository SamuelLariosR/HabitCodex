# Rutas de las páginas HTML.

from functools import wraps

from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from logica.bd import conexion_bd
from logica.errores import ErrorHabito
from logica.habitos import (
    crear_habito,
    editar_habito,
    eliminar_habito,
    listar_mis_habitos,
    obtener_habito,
)
from logica.usuarios import (
    autenticar_usuario,
    registrar_usuario,
    verificar_correo,
)

bp_paginas = Blueprint("paginas", __name__)


def _ruta_bd():
    """Ruta configurada en create_app; no se lee el entorno aquí."""
    return current_app.config["DATABASE_PATH"]


def requiere_sesion(vista):
    """Manda al login si no hay usuario en la sesión."""

    @wraps(vista)
    def envuelta(*args, **kwargs):
        if "usuario_id" not in session:
            flash("Debe iniciar sesión para ver esa página", "aviso")
            return redirect(url_for("paginas.login"))
        return vista(*args, **kwargs)

    return envuelta


@bp_paginas.get("/")
@requiere_sesion
def principal():
    with conexion_bd(_ruta_bd()) as conexion:
        habitos = listar_mis_habitos(conexion, session["usuario_id"])
    return render_template(
        "principal.html",
        habitos=habitos,
        nombre=session.get("usuario_nombre", ""),
    )


@bp_paginas.route("/registro", methods=["GET", "POST"])
def registro():
    if "usuario_id" in session:
        return redirect(url_for("paginas.principal"))

    if request.method == "POST":
        nombre = request.form.get("nombre", "")
        correo = request.form.get("correo", "")
        contrasena = request.form.get("contrasena", "")
        try:
            with conexion_bd(_ruta_bd()) as conexion:
                cuenta = registrar_usuario(
                    conexion, nombre, correo, contrasena
                )
        except ErrorHabito as error:
            flash(error.mensaje, "error")
            return render_template(
                "registro.html", nombre=nombre, correo=correo
            )

        # El correo es simulado: el enlace se enseña una vez en el login.
        session["enlace_verificacion"] = url_for(
            "paginas.verificar", token=cuenta["token"]
        )
        flash("Cuenta creada. Revisa el enlace de verificación", "exito")
        return redirect(url_for("paginas.login"))

    return render_template("registro.html")


@bp_paginas.route("/login", methods=["GET", "POST"])
def login():
    if "usuario_id" in session:
        return redirect(url_for("paginas.principal"))

    enlace = session.pop("enlace_verificacion", None)

    if request.method == "POST":
        correo = request.form.get("correo", "")
        contrasena = request.form.get("contrasena", "")
        try:
            with conexion_bd(_ruta_bd()) as conexion:
                usuario = autenticar_usuario(conexion, correo, contrasena)
        except ErrorHabito as error:
            flash(error.mensaje, "error")
            return render_template(
                "login.html", correo=correo, enlace=enlace
            )

        session.clear()
        session["usuario_id"] = usuario["id"]
        session["usuario_nombre"] = usuario["nombre"]
        flash(f"Bienvenido, {usuario['nombre']}", "exito")
        return redirect(url_for("paginas.principal"))

    return render_template("login.html", enlace=enlace)


@bp_paginas.post("/logout")
def logout():
    session.clear()
    flash("Sesión cerrada", "exito")
    return redirect(url_for("paginas.login"))


@bp_paginas.post("/habitos")
@requiere_sesion
def crear():
    nombre = request.form.get("nombre", "")
    try:
        with conexion_bd(_ruta_bd()) as conexion:
            crear_habito(conexion, session["usuario_id"], nombre)
    except ErrorHabito as error:
        flash(error.mensaje, "error")
    else:
        flash("Hábito creado", "exito")
    return redirect(url_for("paginas.principal"))


@bp_paginas.route("/editar/<int:habito_id>", methods=["GET", "POST"])
@requiere_sesion
def editar(habito_id):
    usuario = session["usuario_id"]

    if request.method == "POST":
        nombre = request.form.get("nombre", "")
        try:
            with conexion_bd(_ruta_bd()) as conexion:
                editar_habito(conexion, habito_id, usuario, nombre)
        except ErrorHabito as error:
            flash(error.mensaje, "error")
            return redirect(
                url_for("paginas.editar", habito_id=habito_id)
            )
        flash("Hábito actualizado", "exito")
        return redirect(url_for("paginas.principal"))

    try:
        with conexion_bd(_ruta_bd()) as conexion:
            habito = obtener_habito(conexion, habito_id, usuario)
    except ErrorHabito as error:
        flash(error.mensaje, "error")
        return redirect(url_for("paginas.principal"))

    return render_template("editar.html", habito=habito)


@bp_paginas.post("/eliminar/<int:habito_id>")
@requiere_sesion
def eliminar(habito_id):
    try:
        with conexion_bd(_ruta_bd()) as conexion:
            eliminar_habito(conexion, habito_id, session["usuario_id"])
    except ErrorHabito as error:
        flash(error.mensaje, "error")
    else:
        flash("Hábito eliminado", "exito")
    return redirect(url_for("paginas.principal"))


@bp_paginas.get("/verificar/<token>")
def verificar(token):
    with conexion_bd(_ruta_bd()) as conexion:
        correcto = verificar_correo(conexion, token)
    if correcto:
        flash("Correo verificado", "exito")
    else:
        flash("El enlace de verificación no sirve o ya caducó", "error")
    return redirect(url_for("paginas.login"))
