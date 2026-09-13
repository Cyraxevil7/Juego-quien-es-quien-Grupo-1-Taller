"""Pantalla de menú principal: punto central de navegación del juego."""

import pygame

from juego.configuracion import (
    ANCHO_VENTANA,
    COLOR_BORDE,
    COLOR_FONDO_PANEL,
    COLOR_TEXTO_SUAVE,
    COLOR_TITULO,
)
from juego.juego import CREDITOS, OPCIONES_PANTALLA
from . import iconos
from .pantalla import Pantalla
from .boton import Boton
from .avatar import dibujar_avatar
from .utilidades import dibujar_panel, dibujar_texto_centrado, dibujar_texto_con_sombra


class MenuPrincipal(Pantalla):
    def __init__(self, juego):
        super().__init__(juego)

        ancho_boton, alto_boton = 380, 66
        x = (ANCHO_VENTANA - ancho_boton) // 2
        y_inicial = 360
        separacion = 78

        def con_clic(accion):
            def envoltura():
                self._juego.audio.reproducir_clic()
                accion()
            return envoltura

        padding_panel = 30
        y_superior_botones = y_inicial
        y_inferior_botones = y_inicial + separacion * 3 + alto_boton
        self._panel = pygame.Rect(
            0, 0, ancho_boton + 120, (y_inferior_botones - y_superior_botones) + padding_panel * 2
        )
        self._panel.center = (ANCHO_VENTANA // 2, (y_superior_botones + y_inferior_botones) // 2)

        self._botones = [
            Boton(
                juego,
                (x, y_inicial, ancho_boton, alto_boton),
                "JUGAR",
                icono=iconos.jugar,
                enfatizado=True,
                al_hacer_clic=con_clic(self._juego.iniciar_partida),
            ),
            Boton(
                juego,
                (x, y_inicial + separacion, ancho_boton, alto_boton),
                "OPCIONES",
                icono=iconos.opciones,
                al_hacer_clic=con_clic(lambda: self._juego.cambiar_pantalla(OPCIONES_PANTALLA)),
            ),
            Boton(
                juego,
                (x, y_inicial + separacion * 2, ancho_boton, alto_boton),
                "CRÉDITOS",
                icono=iconos.creditos,
                al_hacer_clic=con_clic(lambda: self._juego.cambiar_pantalla(CREDITOS)),
            ),
            Boton(
                juego,
                (x, y_inicial + separacion * 3, ancho_boton, alto_boton),
                "SALIR",
                icono=iconos.salir,
                color_normal=COLOR_BORDE,
                color_hover=(198, 184, 164),
                color_texto=(70, 60, 50),
                al_hacer_clic=con_clic(self._juego.salir),
            ),
        ]

    def procesar_evento(self, evento):
        for boton in self._botones:
            boton.procesar_evento(evento)

    def actualizar(self):
        pos_mouse = pygame.mouse.get_pos()
        for boton in self._botones:
            boton.actualizar(pos_mouse)

    def dibujar(self, superficie):
        fuente_titulo = self._juego.fuente("titulo")
        fuente_subtitulo = self._juego.fuente("subtitulo")

        dibujar_texto_con_sombra(
            superficie, "¿Quién es quién?", fuente_titulo, COLOR_TITULO, (ANCHO_VENTANA // 2, 108)
        )
        dibujar_texto_centrado(
            superficie,
            "Conoce a la familia y pon a prueba tu memoria",
            fuente_subtitulo,
            COLOR_TEXTO_SUAVE,
            (ANCHO_VENTANA // 2, 160),
        )

        # Pequeña "carátula" con todo el banco de personajes disponible,
        # a modo de presentación (la familia real de cada partida se
        # sortea al pulsar JUGAR, ver Juego.iniciar_partida).
        personajes = self._juego.personajes
        n = len(personajes)
        radio_avatar = 44 if n <= 5 else 36
        separacion_avatares = 118 if n <= 5 else 92
        x_inicial = ANCHO_VENTANA // 2 - separacion_avatares * (n - 1) // 2
        for indice, personaje in enumerate(personajes):
            offset_y = -8 if indice % 2 == 0 else 8
            centro = (x_inicial + indice * separacion_avatares, 232 + offset_y)
            dibujar_avatar(superficie, personaje, centro, radio_avatar, flotante=True)

        dibujar_panel(superficie, self._panel, COLOR_FONDO_PANEL, COLOR_BORDE, radio_borde=26)

        for boton in self._botones:
            boton.dibujar(superficie)
