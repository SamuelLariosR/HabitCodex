# datos/usuarios_datos.py


def guardar_usuario(conexion, nombre, correo, contrasena, fecha_creacion):
    """Guarda un usuario y devuelve su id."""
    cursor = conexion.execute(
        "INSERT INTO usuarios (nombre, correo, contrasena, fecha_creacion) "
        "VALUES (?, ?, ?, ?)",
        (nombre, correo, contrasena, fecha_creacion),
    )
    conexion.commit()
    return cursor.lastrowid


def buscar_usuario_por_correo(conexion, correo):
    """Devuelve el usuario con ese correo, o None."""
    fila = conexion.execute(
        "SELECT * FROM usuarios WHERE correo = ?", (correo,)
    ).fetchone()
    return dict(fila) if fila else None


def buscar_usuario_por_id(conexion, usuario_id):
    """Devuelve el usuario con ese id, o None."""
    fila = conexion.execute(
        "SELECT * FROM usuarios WHERE id = ?", (usuario_id,)
    ).fetchone()
    return dict(fila) if fila else None


def marcar_usuario_verificado(conexion, usuario_id):
    """Pone verificado = 1. Devuelve True si cambio."""
    cursor = conexion.execute(
        "UPDATE usuarios SET verificado = 1 "
        "WHERE id = ? AND verificado = 0",
        (usuario_id,),
    )
    conexion.commit()
    return cursor.rowcount > 0
