"""Punto de entrada del juego "¿Quién es quién?".

Este archivo se mantiene deliberadamente pequeño (ver documento de
diseño, sección 14): solo inicializa Pygame, crea la ventana y la
instancia principal de ``Juego``, y arranca el ciclo principal. Toda la
lógica del juego vive en los paquetes ``juego`` y ``pantallas``.

El juego está preparado para ejecutarse tanto de forma independiente
(``python main.py``) como lanzado por el launcher "enfocate" como un
subproceso: las rutas de datos/recursos se resuelven siempre respecto a
la ubicación de este archivo (ver ``juego/configuracion.py``), sin
depender del directorio de trabajo desde el que se invoque.
"""

import os
import sys

# Asegura que los paquetes "juego" y "pantallas" (ubicados junto a este
# archivo) sean importables sin importar desde qué directorio se lance
# el proceso.
RUTA_PROYECTO = os.path.dirname(os.path.abspath(__file__))
if RUTA_PROYECTO not in sys.path:
    sys.path.insert(0, RUTA_PROYECTO)

import pygame  # noqa: E402  (import después de ajustar sys.path)

from juego.configuracion import ALTO_VENTANA, ANCHO_VENTANA, TITULO_VENTANA  # noqa: E402
from juego.juego import Juego  # noqa: E402


def main():
    # pre_init debe llamarse antes de pygame.init() para fijar el formato
    # de audio (44100 Hz, 16 bits, mono) que usa juego/audio.py.
    pygame.mixer.pre_init(frequency=44100, size=-16, channels=1)
    pygame.init()

    pantalla = pygame.display.set_mode((ANCHO_VENTANA, ALTO_VENTANA))
    pygame.display.set_caption(TITULO_VENTANA)

    juego = Juego(pantalla)
    juego.ejecutar()

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
