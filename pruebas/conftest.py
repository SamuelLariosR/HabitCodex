# Piezas compartidas por las pruebas: base temporal y usuarios de ejemplo.

import pytest

from datos.conexion import inicializar_bd, obtener_conexion
from datos.usuarios_datos import guardar_usuario


@pytest.fixture
def conexion(tmp_path):
    """Base limpia por prueba; tmp_path la borra al terminar."""
    ruta = str(tmp_path / "pruebas.db")
    inicializar_bd(ruta)
    con = obtener_conexion(ruta)
    yield con
    con.close()


@pytest.fixture
def usuario(conexion):
    """Id de la persona duena de los habitos."""
    return guardar_usuario(
        conexion, "Ana", "ana@x.com", "hash", "2026-11-09T10:00:00"
    )


@pytest.fixture
def otro_usuario(conexion):
    """Id de una segunda persona, para probar el aislamiento."""
    return guardar_usuario(
        conexion, "Beto", "beto@x.com", "hash", "2026-11-09T10:00:00"
    )
