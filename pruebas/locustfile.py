# Prueba de rendimiento con Locust: cada usuario se registra e inicia sesion.

import re
import uuid

from locust import HttpUser, between, tag, task

CONTRASENA = "carga-locust-123"
PATRON_EDITAR = re.compile(r"/editar/(\d+)")


class UsuarioHabitCodex(HttpUser):
    """Persona que usa la web: crea su cuenta, entra y maneja habitos."""

    wait_time = between(0.5, 1.5)

    def on_start(self):
        self.correo = f"carga-{uuid.uuid4().hex[:12]}@ejemplo.com"
        self.prefijo = uuid.uuid4().hex[:6]
        self.habitos = []
        self.contador = 0
        self._registrarse()
        self._entrar()

    def _registrarse(self):
        """Crea la cuenta y usa el enlace simulado para verificarla."""
        with self.client.post(
            "/registro",
            data={
                "nombre": "Carga",
                "correo": self.correo,
                "contrasena": CONTRASENA,
            },
            name="/registro",
            catch_response=True,
        ) as respuesta:
            if respuesta.status_code != 200:
                respuesta.failure(f"registro devolvio {respuesta.status_code}")
                return
            enlace = re.search(r"/verificar/([^\"']+)", respuesta.text)
            if enlace is None:
                respuesta.failure("no aparecio el enlace de verificacion")
                return
            self.client.get(
                f"/verificar/{enlace.group(1)}", name="/verificar/[token]"
            )

    def _entrar(self):
        with self.client.post(
            "/login",
            data={"correo": self.correo, "contrasena": CONTRASENA},
            name="/login",
            catch_response=True,
        ) as respuesta:
            if "Mis hábitos" not in respuesta.text:
                respuesta.failure("no se pudo iniciar sesion")

    def _leer_habitos(self, texto):
        """Guarda los ids que aparecen en la lista de la pagina."""
        self.habitos = [int(i) for i in PATRON_EDITAR.findall(texto)]

    @tag("normal", "media", "alta")
    @task(3)
    def ver_lista(self):
        with self.client.get("/", name="/", catch_response=True) as r:
            if r.status_code != 200 or "Mis hábitos" not in r.text:
                r.failure(f"lista devolvio {r.status_code}")
            else:
                self._leer_habitos(r.text)

    @tag("normal")
    @task(2)
    def buscar(self):
        with self.client.get(
            "/?q=e", name="/?q=...", catch_response=True
        ) as r:
            if r.status_code != 200:
                r.failure(f"busqueda devolvio {r.status_code}")

    @tag("media")
    @task(1)
    def crear(self):
        self.contador += 1
        nombre = f"{self.prefijo} {self.contador}"
        with self.client.post(
            "/habitos",
            data={"nombre": nombre},
            name="/habitos",
            catch_response=True,
        ) as r:
            if r.status_code != 200 or nombre not in r.text:
                r.failure(f"no se creo el habito ({r.status_code})")
            else:
                self._leer_habitos(r.text)

    @tag("media")
    @task(1)
    def editar(self):
        if not self.habitos:
            return
        habito = self.habitos[0]
        nombre = f"{self.prefijo} editado"
        with self.client.post(
            f"/editar/{habito}",
            data={"nombre": nombre},
            name="/editar/[id]",
            catch_response=True,
        ) as r:
            if r.status_code != 200 or nombre not in r.text:
                r.failure(f"no se edito el habito ({r.status_code})")
