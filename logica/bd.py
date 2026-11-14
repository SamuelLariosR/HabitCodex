# logica/bd.py

from contextlib import contextmanager

from datos.conexion import inicializar_bd, obtener_conexion


def preparar_bd(ruta):
    """Crea las tablas si no existen; no borra datos."""
    inicializar_bd(ruta)


@contextmanager
def conexion_bd(ruta):
    """Entrega una conexión y la cierra aunque la ruta falle."""
    conexion = obtener_conexion(ruta)
    try:
        yield conexion
    finally:
        conexion.close()
