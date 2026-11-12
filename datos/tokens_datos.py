# datos/tokens_datos.py


def guardar_token(conexion, usuario, valor, expiracion):
    """Guarda un token de verificacion y devuelve su id."""
    cursor = conexion.execute(
        "INSERT INTO tokens (usuario, valor, expiracion) VALUES (?, ?, ?)",
        (usuario, valor, expiracion),
    )
    conexion.commit()
    return cursor.lastrowid


def buscar_token(conexion, valor):
    """Devuelve el token con ese valor, o None."""
    fila = conexion.execute(
        "SELECT * FROM tokens WHERE valor = ?", (valor,)
    ).fetchone()
    return dict(fila) if fila else None


def marcar_token_usado(conexion, token_id):
    """Marca el token como usado. Devuelve True si estaba libre."""
    cursor = conexion.execute(
        "UPDATE tokens SET usado = 1 WHERE id = ? AND usado = 0",
        (token_id,),
    )
    conexion.commit()
    return cursor.rowcount > 0
