"""Crea la aplicación Flask y conecta sus partes."""
import os

from dotenv import load_dotenv
from flask import Flask


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
    # Las rutas pedirán la conexión con esta ruta (Fase 4).
    app.config["DATABASE_PATH"] = os.environ.get(
        "DATABASE_URL", "habitcodex.db"
    )

    # Ruta temporal de la Fase 1; se reemplaza por las páginas en la Fase 5.
    @app.route("/")
    def inicio():
        return "Hola"

    return app
