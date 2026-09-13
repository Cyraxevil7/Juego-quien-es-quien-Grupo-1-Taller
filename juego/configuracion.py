"""Constantes de configuración compartidas por todo el juego.

Centralizar aquí la resolución, colores y rutas evita "números mágicos"
repartidos por el código y facilita mantener la interfaz consistente y
accesible (texto grande, alto contraste).
"""

import os

# --- Ventana -----------------------------------------------------------
# Misma resolución base que el launcher "enfocate" (1280x720 / 60 FPS),
# para que la transición entre el launcher y el juego se sienta natural.
ANCHO_VENTANA = 1280
ALTO_VENTANA = 720
FPS = 60
TITULO_VENTANA = "¿Quién es quién?"

# --- Rutas ---------------------------------------------------------------
# Todas las rutas se calculan relativas a la ubicación de este archivo y
# NO al directorio de trabajo actual, para que el juego funcione igual
# sin importar cómo lo invoque el launcher (por ejemplo, como subproceso).
RUTA_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUTA_DATOS = os.path.join(RUTA_BASE, "datos")
RUTA_RECURSOS = os.path.join(RUTA_BASE, "recursos")
RUTA_IMAGENES = os.path.join(RUTA_RECURSOS, "imagenes")
RUTA_SONIDOS = os.path.join(RUTA_RECURSOS, "sonidos")
RUTA_FUENTES = os.path.join(RUTA_RECURSOS, "fuentes")
RUTA_PERSONAJES_JSON = os.path.join(RUTA_DATOS, "personajes.json")

# --- Paleta de colores ---------------------------------------------------
# Colores cálidos y de alto contraste, evitando tonos muy saturados para
# no resultar agresivos a la vista del público objetivo.
COLOR_FONDO = (250, 246, 237)
COLOR_FONDO_PANEL = (255, 255, 255)
COLOR_TEXTO = (43, 43, 43)
COLOR_TEXTO_SUAVE = (95, 95, 95)
COLOR_TITULO = (58, 74, 96)
COLOR_BORDE = (210, 200, 185)

# Fondo degradado (ver pantallas/utilidades.py: dibujar_fondo) usado en
# todas las pantallas, en lugar de un color plano.
COLOR_FONDO_DEGRADADO_ARRIBA = (255, 249, 240)
COLOR_FONDO_DEGRADADO_ABAJO = (234, 219, 196)

COLOR_BOTON = (58, 121, 145)
COLOR_BOTON_HOVER = (78, 148, 175)
COLOR_BOTON_TEXTO = (255, 255, 255)

COLOR_BOTON_SECUNDARIO = (225, 221, 212)
COLOR_BOTON_SECUNDARIO_HOVER = (211, 205, 192)
COLOR_BOTON_SECUNDARIO_TEXTO = (58, 58, 58)

COLOR_CORRECTO = (86, 155, 94)
COLOR_INCORRECTO = (196, 90, 78)

COLOR_SOMBRA = (40, 30, 20)

# --- Tipografía ------------------------------------------------------
# Se usa la fuente por defecto de Pygame (siempre disponible sin
# depender de fuentes instaladas en el sistema del usuario).
NOMBRE_FUENTE = None  # None -> fuente por defecto de pygame.font

TAMANOS_TEXTO = {
    "normal": {
        "titulo": 54,
        "subtitulo": 30,
        "texto": 26,
        "boton": 26,
        "pequeno": 20,
    },
    "grande": {
        "titulo": 62,
        "subtitulo": 36,
        "texto": 32,
        "boton": 30,
        "pequeno": 24,
    },
}

PUNTOS_POR_PREGUNTA = 10

# --- Variedad entre partidas --------------------------------------------
# El archivo personajes.json guarda un "banco" con al menos 8 integrantes
# posibles; cada partida sortea al azar TAMANO_FAMILIA_PARTIDA de ellos
# (ver Juego.iniciar_partida) para que ni las caras ni las preguntas sean
# siempre las mismas, aunque la mecánica (opciones por pregunta, cantidad
# de preguntas) no cambie de una partida a otra.
TAMANO_FAMILIA_PARTIDA = 3
TOTAL_PREGUNTAS_PARTIDA = 8
