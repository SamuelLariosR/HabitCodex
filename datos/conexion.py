# datos/conexion.py

import os
import sqlite3
import time

INTENTOS = 6


def _activar_wal(conexion):
    """Activa WAL esperando si otro proceso tiene la base ocupada.

    Al arrancar Gunicorn, varios workers abren la base a la vez y el
    PRAGMA falla con 'database is locked'. Reintentar lo resuelve.
    """
    for intento in range(INTENTOS):
        try:
            conexion.execute("PRAGMA journal_mode = WAL;")
            return
        except sqlite3.OperationalError:
            if intento == INTENTOS - 1:
                raise
            time.sleep(0.1 * (intento + 1))


def _empezar_transaccion(cursor):
    """BEGIN IMMEDIATE toma el turno de escritura desde el principio."""
    for intento in range(INTENTOS):
        try:
            cursor.execute("BEGIN IMMEDIATE")
            return
        except sqlite3.OperationalError:
            if intento == INTENTOS - 1:
                raise
            time.sleep(0.1 * (intento + 1))


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

    # timeout: si otro worker está escribiendo, espera en vez de fallar.
    conexion = sqlite3.connect(ruta, timeout=15)

    # Filas accesibles por nombre de columna.
    conexion.row_factory = sqlite3.Row

    # SQLite trae las claves foráneas desactivadas.
    conexion.execute("PRAGMA foreign_keys = ON;")

    # WAL: permite leer mientras se escribe. Solo se cambia si hace falta.
    modo = conexion.execute("PRAGMA journal_mode;").fetchone()[0]
    if modo.lower() != "wal":
        _activar_wal(conexion)

    return conexion


def inicializar_bd(ruta=None):
    """Crea las tablas si no existen; no borra datos."""
    conexion = obtener_conexion(ruta)
    cursor = conexion.cursor()

    # Un solo BEGIN: sin el, cada CREATE se confirma aparte y el disco
    # se sincroniza tres veces. IMMEDIATE evita choques entre workers.
    _empezar_transaccion(cursor)

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
