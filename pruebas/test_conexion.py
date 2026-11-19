# Pruebas de la base: WAL, claves foraneas y varios workers a la vez.

import threading

from datos.conexion import inicializar_bd, obtener_conexion


def test_wal_y_claves_foraneas(tmp_path):
    conexion = obtener_conexion(str(tmp_path / "uno.db"))
    try:
        assert conexion.execute("PRAGMA journal_mode").fetchone()[0] == "wal"
        assert conexion.execute("PRAGMA foreign_keys").fetchone()[0] == 1
    finally:
        conexion.close()


def test_inicializar_dos_veces_no_borra_datos(tmp_path):
    ruta = str(tmp_path / "dos.db")
    inicializar_bd(ruta)
    conexion = obtener_conexion(ruta)
    try:
        conexion.execute(
            "INSERT INTO usuarios (nombre, correo, contrasena, "
            "fecha_creacion) VALUES (?, ?, ?, ?)",
            ("Ana", "ana@x.com", "hash", "2026-11-19T10:00:00"),
        )
        conexion.commit()
    finally:
        conexion.close()

    inicializar_bd(ruta)
    conexion = obtener_conexion(ruta)
    try:
        total = conexion.execute("SELECT COUNT(*) FROM usuarios")
        assert total.fetchone()[0] == 1
    finally:
        conexion.close()


def test_varios_workers_inicializan_a_la_vez(tmp_path):
    ruta = str(tmp_path / "carrera.db")
    errores = []

    def arrancar():
        try:
            inicializar_bd(ruta)
        except Exception as error:
            errores.append(error)

    hilos = [threading.Thread(target=arrancar) for _ in range(4)]
    for hilo in hilos:
        hilo.start()
    for hilo in hilos:
        hilo.join()

    assert errores == []
    conexion = obtener_conexion(ruta)
    try:
        filas = conexion.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'"
        ).fetchall()
        nombres = {fila["name"] for fila in filas}
    finally:
        conexion.close()
    assert {"usuarios", "habitos", "tokens"} <= nombres
