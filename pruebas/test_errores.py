# Pruebas del contrato de los errores de la logica.

from logica.errores import ErrorHabito


def test_todos_los_errores_declaran_su_mensaje():
    errores = ErrorHabito.__subclasses__()
    assert errores
    for error in errores:
        assert "mensaje" in vars(error), error.__name__


def test_ningun_mensaje_esta_vacio():
    for error in ErrorHabito.__subclasses__():
        assert error.mensaje.strip(), error.__name__


def test_los_mensajes_no_se_repiten():
    mensajes = [error.mensaje for error in ErrorHabito.__subclasses__()]
    assert len(mensajes) == len(set(mensajes))
