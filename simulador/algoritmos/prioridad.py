"""Planificación por prioridades NO APROPIATIVA.

Criterio: MAYOR valor numérico de `prioridad` = MAYOR prioridad.
Desempate: llegada más temprana y luego menor identificador (natural: P2 < P10).
Un proceso en CPU nunca es expropiado: la prioridad solo decide quién es el próximo
despachado cuando la CPU queda libre (por fin de ráfaga o bloqueo).
Sin envejecimiento: ver README (riesgo de inanición).
"""
from typing import List

from ..constantes import clave_natural
from ..modelos import Proceso
from .base import Planificador


class PlanificadorPrioridad(Planificador):
    nombre = "PRIORIDAD"
    muestra_prioridad = True

    @staticmethod
    def _clave(p: Proceso):
        return (-p.prioridad, p.llegada, clave_natural(p.pid))

    def seleccionar(self, listos: List[Proceso]) -> Proceso:
        return min(listos, key=self._clave)
