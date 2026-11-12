# Errores propios de la logica, con mensajes claros.


class ErrorHabito(Exception):
    """Base de errores de habitos; `mensaje` es el texto a mostrar."""

    mensaje = "Ha ocurrido un error con el hábito"


class ErrorNombreVacio(ErrorHabito):
    mensaje = "Debe escribir algo"


class ErrorNombreLargo(ErrorHabito):
    mensaje = "El nombre no puede superar los 60 caracteres"


class ErrorNombreRepetido(ErrorHabito):
    mensaje = "Debe escribir un hábito diferente"


class ErrorNoEncontrado(ErrorHabito):
    mensaje = "No se encontró el hábito"
