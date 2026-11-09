# datos/usuarios_datos.py

# Esta función guarda un usuario en la base de datos.
def guardar_usuario(conexion, nombre, correo, contrasena, fecha_creacion):
    """Guarda un usuario y devuelve su id."""
    cursor = conexion.execute(
        "INSERT INTO usuarios (nombre, correo, contrasena, fecha_creacion) "
        "VALUES (?, ?, ?, ?)",
        (nombre, correo, contrasena, fecha_creacion),
    )
    conexion.commit()
    return cursor.lastrowid

# Esta función devuelve el usuario con ese correo, o None.
def buscar_usuario_por_correo(conexion, correo):
    """Devuelve el usuario con ese correo, o None."""
    fila = conexion.execute(
        "SELECT * FROM usuarios WHERE correo = ?", (correo,)
    ).fetchone()
    return dict(fila) if fila else None

# Esta función devuelve el usuario con ese id, o None.
def buscar_usuario_por_id(conexion, usuario_id):
    """Devuelve el usuario con ese id, o None."""
    fila = conexion.execute(
        "SELECT * FROM usuarios WHERE id = ?", (usuario_id,)
    ).fetchone()
    return dict(fila) if fila else None
