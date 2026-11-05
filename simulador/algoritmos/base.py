"""Interfaz que debe cumplir todo algoritmo de planificación (patrón Strategy)."""
from abc import ABC, abstractmethod
from typing import List, Optional

from ..modelos import Proceso


class Planificador(ABC):
    nombre = ""
    apropiativo = False
    muestra_prioridad = False           # True: la traza indica la prioridad al despachar
    quantum: Optional[int] = None       # None = sin límite de quantum (Round Robin lo define)

    @abstractmethod
    def seleccionar(self, listos: List[Proceso]) -> Proceso:
        """Elige el próximo proceso de la Cola de Listos."""

    def debe_expropiar(self, en_ejecucion: Proceso, listos: List[Proceso]) -> bool:
        return False                                # por defecto: no apropiativo
