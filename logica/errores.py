# Errores propios de la logica, con mensajes claros.


class ErrorHabito(Exception):
    """Base de los errores; `mensaje` es el texto a mostrar."""

    mensaje = "Ha ocurrido un error con el hábito"


class ErrorCampoVacio(ErrorHabito):
    mensaje = "Debe escribir algo"


class ErrorNombreLargo(ErrorHabito):
    mensaje = "El nombre no puede superar los 60 caracteres"


class ErrorNombreRepetido(ErrorHabito):
    mensaje = "Debe escribir un hábito diferente"


class ErrorNoEncontrado(ErrorHabito):
    mensaje = "No se encontró el hábito"


class ErrorCorreoRepetido(ErrorHabito):
    mensaje = "Ese correo ya está registrado"


class ErrorCorreoInvalido(ErrorHabito):
    mensaje = "Escriba un correo válido"


class ErrorLongitudContrasena(ErrorHabito):
    mensaje = "La contraseña debe tener entre 12 y 16 caracteres"


class ErrorCredenciales(ErrorHabito):
    mensaje = "Correo o contraseña incorrectos"
