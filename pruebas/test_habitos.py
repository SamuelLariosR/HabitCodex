# Pruebas de las reglas de habitos: CP-06 a CP-09 y CP-12 a CP-14.

import pytest

from logica.errores import (
    ErrorNombreLargo,
    ErrorNombreRepetido,
    ErrorNombreVacio,
    ErrorNoEncontrado,
)
from logica.habitos import (
    crear_habito,
    editar_habito,
    eliminar_habito,
    listar_mis_habitos,
    normalizar_nombre,
    validar_nombre,
)


def test_cp06_crear_habito_lista_vacia(conexion, usuario):
    habito_id = crear_habito(conexion, usuario, "Estudiar")
    habitos = listar_mis_habitos(conexion, usuario)
    assert len(habitos) == 1
    assert habitos[0]["id"] == habito_id
    assert habitos[0]["nombre"] == "Estudiar"


def test_cp07_nombre_repetido(conexion, usuario):
    crear_habito(conexion, usuario, "Estudiar")
    with pytest.raises(ErrorNombreRepetido) as error:
        crear_habito(conexion, usuario, " estudiar ")
    assert error.value.mensaje == "Debe escribir un habito diferente"


def test_cp07_repetido_ignora_mayusculas(conexion, usuario):
    crear_habito(conexion, usuario, "Estudiar")
    with pytest.raises(ErrorNombreRepetido):
        crear_habito(conexion, usuario, "ESTUDIAR")


def test_cp07_otro_usuario_si_puede(conexion, usuario, otro_usuario):
    crear_habito(conexion, usuario, "Estudiar")
    crear_habito(conexion, otro_usuario, "Estudiar")
    assert len(listar_mis_habitos(conexion, usuario)) == 1
    assert len(listar_mis_habitos(conexion, otro_usuario)) == 1


def test_cp07_nombre_liberado_al_eliminar(conexion, usuario):
    habito_id = crear_habito(conexion, usuario, "Estudiar")
    eliminar_habito(conexion, habito_id, usuario)
    crear_habito(conexion, usuario, "estudiar")
    assert len(listar_mis_habitos(conexion, usuario)) == 1


@pytest.mark.parametrize("nombre", ["", " ", "   ", "\t", "\n"])
def test_cp08_nombre_vacio(conexion, usuario, nombre):
    with pytest.raises(ErrorNombreVacio):
        crear_habito(conexion, usuario, nombre)


def test_cp08_nombre_nulo(conexion, usuario):
    with pytest.raises(ErrorNombreVacio):
        crear_habito(conexion, usuario, None)


def test_cp09_nombre_largo(conexion, usuario):
    with pytest.raises(ErrorNombreLargo):
        crear_habito(conexion, usuario, "a" * 61)


def test_cp09_limite_exacto(conexion, usuario):
    nombre = "a" * 60
    crear_habito(conexion, usuario, nombre)
    assert listar_mis_habitos(conexion, usuario)[0]["nombre"] == nombre


def test_cp09_espacios_extremos_no_cuentan(conexion, usuario):
    nombre = "a" * 60
    crear_habito(conexion, usuario, "  " + nombre + "  ")
    assert listar_mis_habitos(conexion, usuario)[0]["nombre"] == nombre


def test_cp12_editar_nombre(conexion, usuario):
    habito_id = crear_habito(conexion, usuario, "Estudiar")
    editar_habito(conexion, habito_id, usuario, "Leer")
    assert listar_mis_habitos(conexion, usuario)[0]["nombre"] == "Leer"


def test_cp12_guardar_sin_cambios(conexion, usuario):
    habito_id = crear_habito(conexion, usuario, "Leer")
    assert editar_habito(conexion, habito_id, usuario, "Leer") is True
    assert editar_habito(conexion, habito_id, usuario, " leer ") is True


def test_cp13_editar_a_repetido(conexion, usuario):
    crear_habito(conexion, usuario, "Estudiar")
    leer = crear_habito(conexion, usuario, "Leer")
    with pytest.raises(ErrorNombreRepetido):
        editar_habito(conexion, leer, usuario, "estudiar")


def test_cp14_eliminar_oculta(conexion, usuario):
    habito_id = crear_habito(conexion, usuario, "Estudiar")
    eliminar_habito(conexion, habito_id, usuario)
    assert listar_mis_habitos(conexion, usuario) == []
    fila = conexion.execute(
        "SELECT activo FROM habitos WHERE id = ?", (habito_id,)
    ).fetchone()
    assert fila["activo"] == 0


def test_editar_habito_ajeno(conexion, usuario, otro_usuario):
    habito_id = crear_habito(conexion, usuario, "Estudiar")
    with pytest.raises(ErrorNoEncontrado):
        editar_habito(conexion, habito_id, otro_usuario, "Leer")


def test_eliminar_habito_ajeno(conexion, usuario, otro_usuario):
    habito_id = crear_habito(conexion, usuario, "Estudiar")
    with pytest.raises(ErrorNoEncontrado):
        eliminar_habito(conexion, habito_id, otro_usuario)


def test_eliminar_inexistente(conexion, usuario):
    with pytest.raises(ErrorNoEncontrado):
        eliminar_habito(conexion, 999, usuario)


def test_normalizar_nombre():
    assert normalizar_nombre("  Estudiar  ") == "estudiar"
    assert normalizar_nombre("Leer  Un  Libro") == "leer  un  libro"


def test_validar_nombre_recorta():
    assert validar_nombre("  Estudiar  ") == "Estudiar"


def test_mensajes_canonicos():
    assert ErrorNombreVacio.mensaje == "Debe escribir algo"
    assert ErrorNombreLargo.mensaje == (
        "El nombre no puede superar los 60 caracteres"
    )
    assert ErrorNombreRepetido.mensaje == "Debe escribir un habito diferente"
    assert ErrorNoEncontrado.mensaje == "No se encontro el habito"
