"""Clase principal ``Juego``: controla el estado general de la aplicación.

Es la única clase que conoce todas las pantallas y decide cuál está
activa en cada momento; también centraliza el acceso al jugador, a los
personajes, a las preguntas y a las preferencias de audio.
"""

import json
import random

import pygame

from .configuracion import (
    ALTO_VENTANA,
    ANCHO_VENTANA,
    FPS,
    NOMBRE_FUENTE,
    PUNTOS_POR_PREGUNTA,
    RUTA_PERSONAJES_JSON,
    TAMANO_FAMILIA_PARTIDA,
    TAMANOS_TEXTO,
    TITULO_VENTANA,
)
from pantallas.utilidades import dibujar_fondo
from .personaje import Personaje
from .preguntas import cargar_preguntas
from .generador_preguntas import generar_datos_preguntas
from .jugador import Jugador
from .opciones import Opciones
from .audio import GestorAudio
from .musica import GestorMusica

# Nombres de los estados/pantallas disponibles.
MENU = "menu"
PERSONAJES = "personajes"
PREGUNTA = "pregunta"
RESULTADO = "resultado"
OPCIONES_PANTALLA = "opciones"
CREDITOS = "creditos"


def _cargar_json(ruta):
    with open(ruta, "r", encoding="utf-8") as archivo:
        return json.load(archivo)


class Juego:
    """Controla el ciclo de vida completo de la partida y de la ventana."""

    def __init__(self, superficie):
        self._superficie = superficie
        self._reloj = pygame.time.Clock()
        self._ejecutando = True

        # "Banco" completo de personajes disponibles (al menos 8); cada
        # partida sortea unos pocos de ellos, ver iniciar_partida().
        self._personajes = Personaje.cargar_familia(_cargar_json(RUTA_PERSONAJES_JSON))

        self._jugador = Jugador()
        self._opciones = Opciones()
        self._audio = GestorAudio(self._opciones)
        self._musica = GestorMusica(self._opciones)

        self._familia_partida = []
        self._preguntas_partida = []
        self._indice_pregunta_actual = 0

        self._cache_fuentes = {}

        # Importación diferida para evitar un ciclo de importación entre
        # "juego" y "pantallas" (las pantallas reciben esta instancia de
        # Juego, no la importan directamente).
        from pantallas.menu import MenuPrincipal
        from pantallas.personajes_screen import PantallaPersonajes
        from pantallas.pregunta_screen import PantallaPregunta
        from pantallas.resultado_screen import PantallaResultado
        from pantallas.opciones_screen import PantallaOpciones
        from pantallas.creditos_screen import PantallaCreditos

        self._pantallas = {
            MENU: MenuPrincipal(self),
            PERSONAJES: PantallaPersonajes(self),
            PREGUNTA: PantallaPregunta(self),
            RESULTADO: PantallaResultado(self),
            OPCIONES_PANTALLA: PantallaOpciones(self),
            CREDITOS: PantallaCreditos(self),
        }
        self._estado_actual = MENU
        self.cambiar_pantalla(MENU)

    # --- Propiedades de acceso a los subsistemas ------------------------
    @property
    def jugador(self):
        return self._jugador

    @property
    def opciones(self):
        return self._opciones

    @property
    def audio(self):
        return self._audio

    @property
    def musica(self):
        return self._musica

    @property
    def personajes(self):
        """Lista de TODOS los personajes del banco (dict de Python
        conserva el orden de inserción). Se usa solo como "carátula"
        decorativa en el menú; la familia de la partida en curso es
        ``familia_actual``."""
        return list(self._personajes.values())

    @property
    def familia_actual(self):
        """Los pocos personajes sorteados para la partida en curso (ver
        iniciar_partida). Antes de jugar por primera vez está vacía."""
        return list(self._familia_partida)

    def obtener_personaje(self, nombre):
        return self._personajes.get(nombre)

    # --- Manejo de pantallas ---------------------------------------------
    def cambiar_pantalla(self, nombre_estado):
        self._estado_actual = nombre_estado
        self._pantallas[nombre_estado].al_entrar()
        self._musica.reproducir_para_estado(nombre_estado)

    @property
    def estado_actual(self):
        return self._estado_actual

    # --- Flujo de la partida ----------------------------------------------
    def iniciar_partida(self):
        """Prepara una partida nueva: reinicia puntuación, sortea qué
        integrantes del banco de personajes forman la familia de esta
        partida y genera un cuestionario nuevo a partir de ellos, para
        que ni las caras ni las preguntas se repitan siempre igual."""
        self._jugador.reiniciar()
        cantidad = min(TAMANO_FAMILIA_PARTIDA, len(self._personajes))
        self._familia_partida = random.sample(self.personajes, cantidad)
        datos_preguntas = generar_datos_preguntas(self._familia_partida)
        self._preguntas_partida = cargar_preguntas(datos_preguntas)
        self._indice_pregunta_actual = 0
        self.cambiar_pantalla(PERSONAJES)

    def comenzar_preguntas(self):
        self.cambiar_pantalla(PREGUNTA)

    def pregunta_actual(self):
        if not self._preguntas_partida:
            return None
        return self._preguntas_partida[self._indice_pregunta_actual]

    def numero_pregunta_actual(self):
        """Número de pregunta a mostrar al jugador (base 1)."""
        return self._indice_pregunta_actual + 1

    def total_preguntas(self):
        return len(self._preguntas_partida)

    def responder_pregunta(self, opcion_elegida):
        """Evalúa la respuesta escogida, actualiza la puntuación y
        reproduce el sonido correspondiente. Devuelve True/False según si
        fue correcta."""
        pregunta = self.pregunta_actual()
        es_correcta = pregunta.comprobar_respuesta(opcion_elegida)
        if es_correcta:
            self._jugador.sumar_puntos(PUNTOS_POR_PREGUNTA)
            self._audio.reproducir_correcto()
        else:
            self._jugador.registrar_fallo()
            self._audio.reproducir_incorrecto()
        return es_correcta

    def avanzar_pregunta(self):
        """Pasa a la siguiente pregunta, o a la pantalla de resultado si
        ya se respondieron todas."""
        self._indice_pregunta_actual += 1
        if self._indice_pregunta_actual >= len(self._preguntas_partida):
            self.cambiar_pantalla(RESULTADO)
        else:
            self.cambiar_pantalla(PREGUNTA)

    def salir(self):
        self._ejecutando = False

    # --- Tipografía accesible ------------------------------------------------
    def fuente(self, clave):
        """Devuelve (con caché) una fuente pygame para la clave indicada
        ("titulo", "subtitulo", "texto", "boton" o "pequeno"), respetando
        el tamaño de texto elegido en Opciones."""
        tamano_actual = self._opciones.tamano_texto
        llave_cache = (clave, tamano_actual)
        if llave_cache not in self._cache_fuentes:
            tamano_px = TAMANOS_TEXTO[tamano_actual][clave]
            self._cache_fuentes[llave_cache] = pygame.font.Font(NOMBRE_FUENTE, tamano_px)
        return self._cache_fuentes[llave_cache]

    # --- Ciclo principal ---------------------------------------------------
    def procesar_eventos(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                self._ejecutando = False
            else:
                self._pantallas[self._estado_actual].procesar_evento(evento)

    def actualizar(self):
        self._pantallas[self._estado_actual].actualizar()
        self._musica.actualizar()

    def dibujar(self):
        dibujar_fondo(self._superficie)
        self._pantallas[self._estado_actual].dibujar(self._superficie)
        pygame.display.flip()

    def ejecutar(self):
        pygame.display.set_caption(TITULO_VENTANA)
        while self._ejecutando:
            self.procesar_eventos()
            self.actualizar()
            self.dibujar()
            self._reloj.tick(FPS)
        pygame.quit()


__all__ = [
    "Juego",
    "MENU",
    "PERSONAJES",
    "PREGUNTA",
    "RESULTADO",
    "OPCIONES_PANTALLA",
    "CREDITOS",
    "ANCHO_VENTANA",
    "ALTO_VENTANA",
    "FPS",
]
