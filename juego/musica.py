"""Música de fondo interactiva: la melodía cambia automáticamente según
la pantalla en la que está el jugador (menú, partida en curso o
resultado), en lugar de ser una única pista fija.

Igual que los efectos de sonido, la música se genera en tiempo de
ejecución para no depender de archivos de audio externos, pero con un
tratamiento distinto: cada pista combina una melodía en escala
pentatónica (para que cualquier orden de notas suene bien) con un
acompañamiento grave sostenido (tónica/quinta), y ambas usan un timbre
más cálido ("calido" en ``sintetizador.py``, con armónicos suaves y un
trémolo ligero) en vez del pitido puro de los efectos de clic/acierto/
error — para que la música se sienta como un acompañamiento sereno de
"caja de música" y no como una serie de pitidos de videojuego, algo más
acorde con un juego pensado para adultos mayores. La música es
completamente opcional y respeta en todo momento el volumen y el
interruptor de música de ``Opciones``.
"""

from .sintetizador import FRECUENCIA_MUESTREO, generar_melodia, generar_secuencia, mezclar_buffers

try:
    import pygame
except ImportError:  # pragma: no cover - pygame es una dependencia obligatoria
    pygame = None

# Traduce cada estado del juego (ver juego/juego.py) al "ánimo" musical
# que le corresponde. Varios estados comparten pista para que la música
# no se corte constantemente al pasar de pantalla en pantalla dentro de
# una misma sección.
MOOD_POR_ESTADO = {
    "menu": "menu",
    "opciones": "menu",
    "creditos": "menu",
    "personajes": "partida",
    "pregunta": "partida",
    "resultado": "resultado",
}

VOLUMEN_BASE_MUSICA = 0.55  # se multiplica luego por el volumen elegido en Opciones


class GestorMusica:
    """Reproduce, en bucle, la pista de fondo correspondiente al estado
    actual del juego, y la cambia (con su propio pequeño fundido de
    salida) cada vez que el jugador navega a una sección distinta."""

    def __init__(self, opciones):
        self._opciones = opciones
        self._disponible = False
        self._pistas = {}
        self._animo_actual = None
        self._canal = None
        self._inicializar()

    def _pista_con_bajo(self, notas_melodia, duracion_nota_ms, notas_bajo, volumen_melodia, volumen_bajo):
        """Genera una pista mezclando una melodía (escala pentatónica,
        timbre cálido) con un acompañamiento grave sostenido (tónica y
        quinta, el mismo timbre) por debajo. Ambas se componen para durar
        exactamente lo mismo, de modo que el bucle no tenga costuras."""
        melodia = generar_melodia(notas_melodia, duracion_nota_ms, volumen=volumen_melodia, timbre="calido")
        bajo = generar_secuencia(notas_bajo, duracion_nota_ms, volumen=volumen_bajo, timbre="calido")
        return mezclar_buffers([melodia, bajo])

    def _inicializar(self):
        if pygame is None:
            return
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=FRECUENCIA_MUESTREO, size=-16, channels=1)

            # Menú/opciones/créditos: una frase serena y hogareña, como de
            # caja de música, con un bajo largo de tónica/quinta debajo
            # (12.5 "tiempos" en ambas capas -> el bucle encaja sin cortes).
            self._pistas["menu"] = pygame.mixer.Sound(buffer=self._pista_con_bajo(
                notas_melodia=[
                    (0, 1.5), (4, 1.0), (2, 1.0), (0, 1.0),
                    (4, 1.5), (7, 1.0), (4, 1.5), (2, 1.0), (0, 2.0),
                ],
                duracion_nota_ms=460,
                notas_bajo=[(-12, 6.25), (-5, 6.25)],
                volumen_melodia=0.17,
                volumen_bajo=0.10,
            ))
            # Durante la partida (personajes y preguntas): un poco más
            # ligera y curiosa, sin dejar de ser tranquila, para acompañar
            # sin distraer mientras se piensa la respuesta (11 tiempos).
            self._pistas["partida"] = pygame.mixer.Sound(buffer=self._pista_con_bajo(
                notas_melodia=[
                    (0, 1.0), (2, 1.0), (4, 1.0), (7, 1.0), (4, 1.0),
                    (9, 1.0), (7, 1.0), (4, 1.0), (2, 1.0), (0, 2.0),
                ],
                duracion_nota_ms=300,
                notas_bajo=[(-12, 5.5), (-5, 5.5)],
                volumen_melodia=0.15,
                volumen_bajo=0.09,
            ))
            # Resultado: motivo ascendente y cálido que resuelve hacia la
            # tónica, con el bajo subiendo también al final (9 tiempos).
            self._pistas["resultado"] = pygame.mixer.Sound(buffer=self._pista_con_bajo(
                notas_melodia=[
                    (0, 1.0), (4, 1.0), (7, 1.0), (9, 1.0),
                    (7, 1.0), (12, 1.5), (9, 1.0), (7, 1.5),
                ],
                duracion_nota_ms=340,
                notas_bajo=[(-12, 3.0), (-5, 3.0), (0, 3.0)],
                volumen_melodia=0.21,
                volumen_bajo=0.11,
            ))
            self._disponible = True
        except pygame.error:
            # Sin dispositivo de audio disponible: el juego continúa en silencio.
            self._disponible = False

    def _volumen_efectivo(self):
        if not self._opciones.musica_activa:
            return 0.0
        return VOLUMEN_BASE_MUSICA * self._opciones.volumen_musica

    def reproducir_para_estado(self, nombre_estado):
        """Cambia la música si el nuevo estado pertenece a un "ánimo"
        distinto al que está sonando; si es el mismo, deja la pista
        actual sonando en lugar de reiniciarla en cada cambio de
        pantalla."""
        if not self._disponible:
            return
        animo = MOOD_POR_ESTADO.get(nombre_estado, "menu")
        if animo == self._animo_actual and self._canal is not None and self._canal.get_busy():
            return
        self._animo_actual = animo
        if self._canal is not None:
            self._canal.fadeout(250)
        pista = self._pistas.get(animo)
        if pista is None:
            return
        pista.set_volume(self._volumen_efectivo())
        self._canal = pista.play(loops=-1, fade_ms=250)

    def actualizar(self):
        """Aplica en vivo los cambios de volumen/activación hechos en la
        pantalla de Opciones a la música que ya está sonando."""
        if self._disponible and self._canal is not None:
            self._canal.set_volume(self._volumen_efectivo())

    def detener(self):
        if self._disponible and self._canal is not None:
            self._canal.stop()
