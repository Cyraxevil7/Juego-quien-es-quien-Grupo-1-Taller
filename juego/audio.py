"""Gestor de efectos de sonido del juego (clic, acierto, error).

Se generan matemáticamente en tiempo de ejecución (ver
``sintetizador.py``) en lugar de depender de archivos de audio externos
cuya licencia habría que revisar. Todo el sonido es opcional: si el
dispositivo del jugador no tiene salida de audio disponible, el juego
sigue funcionando en silencio sin errores.
"""

try:
    import pygame
except ImportError:  # pragma: no cover - pygame es una dependencia obligatoria
    pygame = None

from .sintetizador import FRECUENCIA_MUESTREO, generar_tono


class GestorAudio:
    """Crea y reproduce los efectos de sonido del juego, respetando las
    ``Opciones`` de volumen y activación."""

    def __init__(self, opciones):
        self._opciones = opciones
        self._disponible = False
        self._sonidos = {}
        self._inicializar()

    def _inicializar(self):
        if pygame is None:
            return
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=FRECUENCIA_MUESTREO, size=-16, channels=1)
            self._sonidos["clic"] = pygame.mixer.Sound(buffer=generar_tono(440, 60, 0.35))
            self._sonidos["correcto"] = pygame.mixer.Sound(
                buffer=generar_tono(660, 90, 0.4) + generar_tono(880, 120, 0.4)
            )
            self._sonidos["incorrecto"] = pygame.mixer.Sound(buffer=generar_tono(180, 220, 0.35))
            self._disponible = True
        except pygame.error:
            # Sin dispositivo de audio disponible: el juego continúa en silencio.
            self._disponible = False

    def _reproducir(self, nombre):
        if not self._disponible or not self._opciones.efectos_activos:
            return
        sonido = self._sonidos.get(nombre)
        if sonido is not None:
            sonido.set_volume(self._opciones.volumen_efectos)
            sonido.play()

    def reproducir_clic(self):
        self._reproducir("clic")

    def reproducir_correcto(self):
        self._reproducir("correcto")

    def reproducir_incorrecto(self):
        self._reproducir("incorrecto")
