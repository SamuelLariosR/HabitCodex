"""Crea la aplicación Flask y conecta sus partes."""
import os

from dotenv import load_dotenv
from flask import Flask

from logica.bd import preparar_bd
from web.paginas import bp_paginas


def create_app():
    """Construye la aplicación con la configuración del archivo .env."""
    load_dotenv()

    secret_key = os.environ.get("SECRET_KEY")
    if not secret_key:
        raise RuntimeError(
            "Falta SECRET_KEY. Copia .env.example a .env y escribe ahí un "
            "texto largo y secreto."
        )

    app = Flask(__name__)
    app.config["SECRET_KEY"] = secret_key
    # Las rutas piden la conexión con esta ruta; nunca leen el entorno.
    app.config["DATABASE_PATH"] = os.environ.get(
        "DATABASE_URL", "habitcodex.db"
    )
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

    # Crea las tablas al arrancar; si ya existen, no toca los datos.
    preparar_bd(app.config["DATABASE_PATH"])

    app.register_blueprint(bp_paginas)
    return app
