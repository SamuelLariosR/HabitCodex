# Comprueba cada cierto tiempo que la aplicacion responde y anota el resultado.

import argparse
import csv
import os
import time
from datetime import datetime
from urllib.error import HTTPError, URLError
from urllib.request import urlopen


def comprobar(url, segundos_espera=5):
    """Devuelve (codigo, milisegundos). Codigo 0 si no hubo respuesta."""
    inicio = time.perf_counter()
    try:
        with urlopen(url, timeout=segundos_espera) as respuesta:
            codigo = respuesta.status
    except HTTPError as error:
        codigo = error.code
    except (URLError, OSError):
        codigo = 0
    milisegundos = (time.perf_counter() - inicio) * 1000
    return codigo, round(milisegundos, 1)


def main():
    parser = argparse.ArgumentParser(
        description="Comprueba que la app responde y lo anota en un CSV."
    )
    parser.add_argument(
        "--url", default="http://127.0.0.1:8000/", help="direccion a probar"
    )
    parser.add_argument(
        "--duracion",
        type=int,
        default=5,
        help="minutos que dura la comprobacion",
    )
    parser.add_argument(
        "--intervalo",
        type=float,
        default=60.0,
        help="segundos entre comprobaciones",
    )
    parser.add_argument(
        "--salida",
        default="resultados/disponibilidad.csv",
        help="archivo CSV",
    )
    args = parser.parse_args()

    carpeta = os.path.dirname(args.salida)
    if carpeta:
        os.makedirs(carpeta, exist_ok=True)

    fin = time.monotonic() + args.duracion * 60
    total = 0
    fallos = 0
    with open(args.salida, "w", newline="", encoding="utf-8") as archivo:
        escritor = csv.writer(archivo)
        escritor.writerow(
            [
                "fecha",
                "hora",
                "url",
                "codigo",
                "milisegundos",
                "ok",
            ]
        )
        while time.monotonic() < fin:
            codigo, milisegundos = comprobar(args.url)
            ahora = datetime.now()
            correcto = "si" if codigo == 200 else "no"
            escritor.writerow(
                [
                    ahora.strftime("%Y-%m-%d"),
                    ahora.strftime("%H:%M:%S"),
                    args.url,
                    codigo,
                    milisegundos,
                    correcto,
                ]
            )
            archivo.flush()
            total += 1
            if codigo != 200:
                fallos += 1
            print(
                f"{ahora.strftime('%H:%M:%S')}  codigo {codigo}  "
                f"{milisegundos} ms"
            )
            restante = fin - time.monotonic()
            if restante <= 0:
                break
            time.sleep(min(args.intervalo, restante))

    print(
        f"Listo: {total} comprobaciones, {fallos} fallos. "
        f"Archivo: {args.salida}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
