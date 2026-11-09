# datos/habitos_datos.py

# Esta función guarda un hábito en la base de datos.
def guardar_habito(conexion, usuario, nombre, nombre_normalizado,
                   fecha_creacion):
    """Guarda un hábito activo y devuelve su id."""
    cursor = conexion.execute(
        "INSERT INTO habitos (usuario, nombre, nombre_normalizado, "
        "fecha_creacion, activo) VALUES (?, ?, ?, ?, 1)",
        (usuario, nombre, nombre_normalizado, fecha_creacion),
    )
    conexion.commit()
    return cursor.lastrowid

# Esta Función devuelve una lista de hábitos activos de un usuario, ordenados por fecha de creación y id.
def listar_habitos(conexion, usuario):
    """Devuelve los activos, del más antiguo al más nuevo."""
    filas = conexion.execute(
        "SELECT * FROM habitos WHERE usuario = ? AND activo = 1 "
        "ORDER BY fecha_creacion, id",
        (usuario,),
    ).fetchall()
    return [dict(fila) for fila in filas]

# Esta función devuelve un hábito activo del usuario, o None si no existe.
def buscar_habito(conexion, habito_id, usuario):
    """Devuelve un hábito activo del usuario, o None."""
    fila = conexion.execute(
        "SELECT * FROM habitos WHERE id = ? AND usuario = ? AND activo = 1",
        (habito_id, usuario),
    ).fetchone()
    return dict(fila) if fila else None

# Esta función cambia el nombre de un hábito activo. Devuelve True si cambió.
def actualizar_nombre(conexion, habito_id, usuario, nombre,
                      nombre_normalizado):
    """Cambia el nombre de un hábito activo. Devuelve True si cambió."""
    cursor = conexion.execute(
        "UPDATE habitos SET nombre = ?, nombre_normalizado = ? "
        "WHERE id = ? AND usuario = ? AND activo = 1",
        (nombre, nombre_normalizado, habito_id, usuario),
    )
    conexion.commit()
    return cursor.rowcount > 0

# Esta función oculta un hábito (activo = 0). Devuelve True si lo encontró.
def desactivar_habito(conexion, habito_id, usuario):
    """Oculta un hábito (activo = 0). Devuelve True si lo encontró."""
    cursor = conexion.execute(
        "UPDATE habitos SET activo = 0 "
        "WHERE id = ? AND usuario = ? AND activo = 1",
        (habito_id, usuario),
    )
    conexion.commit()
    return cursor.rowcount > 0
