"""Planificación por prioridades APROPIATIVA.

Criterio: MAYOR valor numérico de `prioridad` = MAYOR prioridad.
Desempate: llegada más temprana y luego menor identificador (natural: P2 < P10).
Expropia solo si en la cola hay un proceso de prioridad ESTRICTAMENTE mayor.
Sin envejecimiento: ver README (riesgo de inanición).
"""
from typing import List

from ..constantes import clave_natural
from ..modelos import Proceso
from .base import Planificador


class PlanificadorPrioridad(Planificador):
    nombre = "PRIORIDAD"
    apropiativo = True
    muestra_prioridad = True

    @staticmethod
    def _clave(p: Proceso):
        return (-p.prioridad, p.llegada, clave_natural(p.pid))

    def seleccionar(self, listos: List[Proceso]) -> Proceso:
        return min(listos, key=self._clave)

    def debe_expropiar(self, en_ejecucion: Proceso, listos: List[Proceso]) -> bool:
        return self.seleccionar(listos).prioridad > en_ejecucion.prioridad
