# datos/conexion.py

import os
import sqlite3


def obtener_conexion(ruta=None):
    """Devuelve una conexión con WAL y claves foráneas activas."""
    # Ruta: argumento (pruebas) o DATABASE_URL; nunca escrita a mano.
    ruta = ruta or os.environ.get("DATABASE_URL", "habitcodex.db")

    # Absoluta: portable y con los -wal/-shm junto a la base.
    ruta = os.path.abspath(ruta)

    # Crea la carpeta si no existe; el archivo lo crea connect.
    carpeta = os.path.dirname(ruta)
    if carpeta:
        os.makedirs(carpeta, exist_ok=True)

    conexion = sqlite3.connect(ruta)

    # Filas accesibles por nombre de columna.
    conexion.row_factory = sqlite3.Row

    # SQLite trae las claves foráneas desactivadas.
    conexion.execute("PRAGMA foreign_keys = ON;")

    # WAL: permite leer mientras se escribe.
    conexion.execute("PRAGMA journal_mode = WAL;")

    return conexion


def inicializar_bd(ruta=None):
    """Crea las tablas si no existen; no borra datos."""
    conexion = obtener_conexion(ruta)
    cursor = conexion.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            correo TEXT UNIQUE NOT NULL,
            contrasena TEXT NOT NULL,
            verificado INTEGER NOT NULL DEFAULT 0,
            fecha_creacion TEXT NOT NULL
        )
    ''')

    # activo = 0 significa eliminado (oculto).
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS habitos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario INTEGER NOT NULL,
            nombre TEXT NOT NULL,
            nombre_normalizado TEXT NOT NULL,
            fecha_creacion TEXT NOT NULL,
            activo INTEGER NOT NULL DEFAULT 1,
            FOREIGN KEY(usuario) REFERENCES usuarios(id)
        )
    ''')

    # Token temporal para verificar el correo.
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario INTEGER NOT NULL,
            valor TEXT UNIQUE NOT NULL,
            expiracion TEXT NOT NULL,
            usado INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY(usuario) REFERENCES usuarios(id)
        )
    ''')

    conexion.commit()
    conexion.close()


if __name__ == "__main__":
    inicializar_bd()
    print("Base de datos inicializada correctamente.")
