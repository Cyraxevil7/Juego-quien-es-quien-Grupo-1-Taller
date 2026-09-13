"""Clase base abstracta para todas las pantallas del juego."""

from abc import ABC, abstractmethod


class Pantalla(ABC):
    """Define el contrato común que deben cumplir todas las pantallas:
    procesar eventos, actualizar su estado interno y dibujarse.

    El juego llama siempre a estos mismos métodos sin importar qué
    pantalla esté activa (polimorfismo), y cada subclase implementa el
    comportamiento específico de su pantalla.
    """

    def __init__(self, juego):
        self._juego = juego

    def al_entrar(self):
        """Se ejecuta cada vez que el juego cambia a esta pantalla.
        Las subclases lo sobrescriben cuando necesitan reiniciar algo
        (por ejemplo, la pantalla de pregunta debe olvidar la selección
        anterior). Por defecto no hace nada."""
        pass

    @abstractmethod
    def procesar_evento(self, evento):
        raise NotImplementedError

    @abstractmethod
    def actualizar(self):
        raise NotImplementedError

    @abstractmethod
    def dibujar(self, superficie):
        raise NotImplementedError
