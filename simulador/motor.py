"""Motor de simulación: reloj, cola de listos, bloqueados y CPU."""
from typing import List, Optional, Tuple

from .algoritmos.base import Planificador
from .constantes import (BLOQUEADO, EJECUCION, FINALIZADO, LISTO, NUEVO,
                         clave_natural)
from .modelos import EspecProceso, Proceso


class Simulador:
    def __init__(self, especs: Tuple[EspecProceso, ...], planificador: Planificador):
        # Objetos NUEVOS desde las specs inmutables: la carga original no se toca.
        self.procesos = [Proceso(e) for e in especs]
        self.planificador = planificador
        self.cola_listos: List[Proceso] = []
        self.cola_bloqueados: List[Proceso] = []
        self.cpu: Optional[Proceso] = None
        self.uso_quantum = 0                            # ticks seguidos del proceso en CPU
        q = planificador.quantum
        if q is not None and q <= 0:
            raise ValueError("El quantum debe ser mayor que cero.")
        self.finalizados: List[Proceso] = []
        self.linea_tiempo: List[Optional[str]] = []     # pid en CPU por cada tick
        self.traza: List[str] = []

    def ejecutar(self) -> None:
        t = 0
        self.traza.append(f"=== TRAZA DE SIMULACIÓN: {self.planificador.nombre} ===")
        while len(self.finalizados) < len(self.procesos):
            ini: List[str] = []                     # eventos al inicio del tick
            fin: List[str] = []                     # eventos al final del tick

            # 1) ADMISIÓN: llegadas nuevas y fin de E/S
            entrantes = [p for p in self.procesos
                         if p.estado == NUEVO and p.llegada == t]
            ini += [f"{p.pid} llega (Nuevo -> Listo)" for p in entrantes]
            for p in list(self.cola_bloqueados):
                if p.t_despertar == t:
                    self.cola_bloqueados.remove(p)
                    entrantes.append(p)
                    ini.append(f"{p.pid} termina E/S (Bloqueado -> Listo)")
            # Si varios entran juntos: desempate por llegada y luego ID
            entrantes.sort(key=lambda p: (p.llegada, clave_natural(p.pid)))
            for p in entrantes:
                p.estado = LISTO
                self.cola_listos.append(p)          # entra al FINAL de la cola

            # 2a) FIN DE QUANTUM (Round Robin): se evalúa DESPUÉS de la admisión, así
            #     los que llegan en este instante quedan antes del proceso interrumpido.
            q = self.planificador.quantum
            if self.cpu and q and self.uso_quantum >= q:
                if self.cola_listos:
                    ini.append(f"{self.cpu.pid} agota su quantum de {q} u. "
                               f"(Ejecución -> Listo), restante={self.cpu.restante}")
                    self.cpu.estado = LISTO
                    self.cola_listos.append(self.cpu)
                    self.cpu = None
                else:
                    self.uso_quantum = 0            # nadie espera: sigue otro quantum

            # 2b) EXPROPIACIÓN (solo apropiativos)
            if (self.cpu and self.planificador.apropiativo and self.cola_listos
                    and self.planificador.debe_expropiar(self.cpu, self.cola_listos)):
                ini.append(f"{self.cpu.pid} es expropiado (Ejecución -> Listo), "
                           f"restante={self.cpu.restante}")
                self.cpu.estado = LISTO
                self.cola_listos.append(self.cpu)
                self.cpu = None

            # 3) DESPACHO: CPU libre -> el planificador elige
            if self.cpu is None and self.cola_listos:
                p = self.planificador.seleccionar(self.cola_listos)
                self.cola_listos.remove(p)
                p.estado = EJECUCION
                if p.inicio is None:                # primer inicio (T_inicio)
                    p.inicio = t
                prio = (f" [prioridad={p.prioridad}]"
                        if self.planificador.muestra_prioridad else "")
                ini.append(f"{p.pid} despachado (Listo -> Ejecución){prio}")
                self.cpu = p
                self.uso_quantum = 0

            # 4) EJECUCIÓN de 1 unidad (o CPU ociosa)
            # Contabilidad de espera: solo cola de listos; el bloqueo se cuenta aparte
            for p in self.cola_listos:
                p.t_espera += 1
            for p in self.cola_bloqueados:
                p.t_bloqueado += 1
            if self.cpu:
                self.cpu.restante -= 1
                self.uso_quantum += 1
                self.linea_tiempo.append(self.cpu.pid)
                cpu_txt = f"{self.cpu.pid} (restante={self.cpu.restante})"
            else:
                self.linea_tiempo.append(None)
                cpu_txt = "IDLE (libre)"
            listos = "[" + ", ".join(p.pid for p in self.cola_listos) + "]"
            bloq = "[" + ", ".join(f"{p.pid}(sale en t={p.t_despertar})"
                                   for p in self.cola_bloqueados) + "]"

            # 5) FIN DE TICK: finalizar o bloquear
            p = self.cpu
            if p and p.restante == 0:
                p.estado, p.fin = FINALIZADO, t + 1
                self.finalizados.append(p)
                fin.append(f"{p.pid} finaliza (Ejecución -> Finalizado) en t={t + 1}")
                self.cpu = None
            elif p and p.es_pendientes and p.es_pendientes[0][0] == p.ejecutado:
                dur = p.es_pendientes.pop(0)[1]     # consumir el evento de E/S
                p.estado, p.t_despertar = BLOQUEADO, t + 1 + dur
                self.cola_bloqueados.append(p)
                fin.append(f"{p.pid} solicita E/S (Ejecución -> Bloqueado) por {dur} u.; "
                           f"vuelve a Listo en t={p.t_despertar}")
                self.cpu = None

            # Registro en la traza
            self.traza.append(f"t={t:>3} -> {t + 1:<3} | CPU: {cpu_txt}")
            self.traza.append(f"            | Listos: {listos}   Bloqueados: {bloq}")
            if ini:
                self.traza.append("            | Eventos al inicio: " + "; ".join(ini))
            if fin:
                self.traza.append("            | Eventos al final : " + "; ".join(fin))
            t += 1

        self.traza.append(f"=== Todos los procesos finalizaron en t={t} ===")
