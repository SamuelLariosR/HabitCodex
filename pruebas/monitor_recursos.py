# Anota el uso de CPU y memoria de Gunicorn durante una prueba de carga.

import argparse
import csv
import os
import time
from datetime import datetime

import psutil


def buscar_procesos(patron):
    """Procesos de Gunicorn cuyo comando contiene el patron."""
    encontrados = []
    for proceso in psutil.process_iter(["name", "cmdline"]):
        try:
            comando = " ".join(proceso.info["cmdline"] or [])
            nombre = proceso.info["name"] or ""
            if "gunicorn" in nombre or "gunicorn" in comando:
                if patron in comando:
                    encontrados.append(proceso)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return encontrados


def medir(procesos):
    """Devuelve los procesos vivos, la CPU sumada y la memoria en MB."""
    vivos = []
    cpu = 0.0
    memoria = 0.0
    for proceso in procesos:
        try:
            cpu += proceso.cpu_percent(interval=None)
            memoria += proceso.memory_info().rss
            vivos.append(proceso)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return vivos, cpu, memoria / (1024 * 1024)


def main():
    parser = argparse.ArgumentParser(
        description="Anota CPU y memoria de Gunicorn en un CSV."
    )
    parser.add_argument(
        "--salida", default="resultados/recursos.csv", help="archivo CSV"
    )
    parser.add_argument(
        "--duracion",
        type=int,
        default=120,
        help="segundos que dura la medicion",
    )
    parser.add_argument(
        "--intervalo",
        type=float,
        default=2.0,
        help="segundos entre cada medicion",
    )
    parser.add_argument(
        "--patron",
        default="app:app",
        help="texto que debe llevar el comando de Gunicorn",
    )
    args = parser.parse_args()

    carpeta = os.path.dirname(args.salida)
    if carpeta:
        os.makedirs(carpeta, exist_ok=True)

    procesos = buscar_procesos(args.patron)
    if not procesos:
        print(
            "Aviso: no se encontro Gunicorn con "
            f"'{args.patron}'. Arranca la app antes de medir."
        )
        return 1

    # La primera lectura de cpu_percent siempre da 0: se descarta.
    for proceso in procesos:
        try:
            proceso.cpu_percent(interval=None)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    inicio = time.monotonic()
    filas = 0
    with open(args.salida, "w", newline="", encoding="utf-8") as archivo:
        escritor = csv.writer(archivo)
        escritor.writerow(
            [
                "fecha",
                "segundo",
                "procesos",
                "cpu_porcentaje",
                "memoria_mb",
            ]
        )
        while time.monotonic() - inicio < args.duracion:
            procesos, cpu, memoria = medir(procesos)
            segundo = round(time.monotonic() - inicio, 1)
            escritor.writerow(
                [
                    datetime.now().isoformat(timespec="seconds"),
                    segundo,
                    len(procesos),
                    round(cpu, 1),
                    round(memoria, 1),
                ]
            )
            archivo.flush()
            filas += 1
            time.sleep(args.intervalo)

    print(f"Listo: {filas} mediciones en {args.salida}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
