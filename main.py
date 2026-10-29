import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional, Tuple

NUEVO, LISTO, EJECUCION, BLOQUEADO, FINALIZADO = (
    "Nuevo", "Listo", "Ejecución", "Bloqueado", "Finalizado")


def natural_key(pid: str):
    return tuple(int(t) if t.isdigit() else t
                 for t in re.split(r"(\d+)", pid) if t)


# Modelo de datos
@dataclass(frozen=True)
class ProcessSpec:
    pid: str
    arrival: int                                   # T_llegada
    burst: int                                     # T_rafaga
    io_events: Tuple[Tuple[int, int], ...] = ()


class Process:
    def __init__(self, spec: ProcessSpec):
        self.pid = spec.pid
        self.arrival = spec.arrival                 
        self.burst = spec.burst                     
        self.remaining = spec.burst                 
        self.state = NUEVO                          
        self.start: Optional[int] = None            
        self.finish: Optional[int] = None           
        self.pending_io = list(spec.io_events)      
        self.wake_time: Optional[int] = None        

    @property
    def executed(self) -> int:                     
        return self.burst - self.remaining

    @property
    def turnaround(self) -> int:                    # Retorno
        return self.finish - self.arrival

    @property
    def waiting(self) -> int:                       # Espera
        return self.turnaround - self.burst

    @property
    def response(self) -> int:                      # Respuesta
        return self.start - self.arrival
class Workload:

    def __init__(self):
        self.specs: Tuple[ProcessSpec, ...] = ()

    def load_default(self) -> None:
        datos = [("P1", 0, 8), ("P2", 1, 4), ("P3", 2, 9), ("P4", 3, 5),
                 ("P5", 4, 2), ("P6", 5, 6), ("P7", 6, 3), ("P8", 7, 7),
                 ("P9", 8, 1), ("P10", 9, 4)]
        io = {"P3": ((3, 4),)}                      # evento de bloqueo
        self.specs = tuple(ProcessSpec(p, a, b, io.get(p, ()))
                           for p, a, b in datos)

class Scheduler(ABC):
    name = ""
    preemptive = False
    @abstractmethod
    def select(self, ready: List[Process]) -> Process:
        """Elige el próximo proceso de la Cola de Listos."""
    def should_preempt(self, running: Process, ready: List[Process]) -> bool:
        return False                                # por defecto: no apropiativo
class FIFOScheduler(Scheduler):
    """FIFO: atiende en el orden de entrada a la cola -> el primero (ready[0])."""
    name = "FIFO"
    def select(self, ready):
        return ready[0]
class SJFScheduler(Scheduler):
    """SJF no apropiativo: menor RÁFAGA; clave (ráfaga, llegada, ID)."""
    name = "SJF"
    def select(self, ready):
        return min(ready, key=lambda p: (p.burst, p.arrival, natural_key(p.pid)))
class SRTFScheduler(Scheduler):
    name = "SRTF"
    preemptive = True

    def select(self, ready):
        return min(ready, key=lambda p: (p.remaining, p.arrival, natural_key(p.pid)))

    def should_preempt(self, running, ready):
        return self.select(ready).remaining < running.remaining


# Motor de simulación
class Simulator:
    def __init__(self, specs: Tuple[ProcessSpec, ...], scheduler: Scheduler):
        # Objetos NUEVOS desde las specs inmutables: la carga original no se toca.
        self.processes = [Process(s) for s in specs]
        self.scheduler = scheduler
        self.ready_queue: List[Process] = []
        self.blocked_queue: List[Process] = []
        self.cpu: Optional[Process] = None
        self.finished: List[Process] = []
        self.timeline: List[Optional[str]] = []     # pid en CPU por cada tick
        self.trace: List[str] = []

    def run(self) -> None:
        t = 0
        self.trace.append(f"=== TRAZA DE SIMULACIÓN: {self.scheduler.name} ===")
        while len(self.finished) < len(self.processes):
            ini: List[str] = []                     # eventos al inicio del tick
            fin: List[str] = []                     # eventos al final del tick

            # 1) ADMISIÓN: llegadas nuevas y fin de E/S
            entrantes = [p for p in self.processes
                         if p.state == NUEVO and p.arrival == t]
            ini += [f"{p.pid} llega (Nuevo -> Listo)" for p in entrantes]
            for p in list(self.blocked_queue):
                if p.wake_time == t:
                    self.blocked_queue.remove(p)
                    entrantes.append(p)
                    ini.append(f"{p.pid} termina E/S (Bloqueado -> Listo)")
            # Si varios entran juntos: desempate por llegada y luego ID
            entrantes.sort(key=lambda p: (p.arrival, natural_key(p.pid)))
            for p in entrantes:
                p.state = LISTO
                self.ready_queue.append(p)          # entra al FINAL de la cola

            # 2) EXPROPIACIÓN (solo apropiativos)
            if (self.cpu and self.scheduler.preemptive and self.ready_queue
                    and self.scheduler.should_preempt(self.cpu, self.ready_queue)):
                ini.append(f"{self.cpu.pid} es expropiado (Ejecución -> Listo), "
                           f"restante={self.cpu.remaining}")
                self.cpu.state = LISTO
                self.ready_queue.append(self.cpu)
                self.cpu = None

            # 3) DESPACHO: CPU libre -> el planificador elige
            if self.cpu is None and self.ready_queue:
                p = self.scheduler.select(self.ready_queue)
                self.ready_queue.remove(p)
                p.state = EJECUCION
                if p.start is None:                 # primer inicio (T_inicio)
                    p.start = t
                ini.append(f"{p.pid} despachado (Listo -> Ejecución)")
                self.cpu = p

            # 4) EJECUCIÓN de 1 unidad (o CPU ociosa)
            if self.cpu:
                self.cpu.remaining -= 1
                self.timeline.append(self.cpu.pid)
                cpu_txt = f"{self.cpu.pid} (restante={self.cpu.remaining})"
            else:
                self.timeline.append(None)
                cpu_txt = "IDLE (libre)"
            listos = "[" + ", ".join(p.pid for p in self.ready_queue) + "]"
            bloq = "[" + ", ".join(f"{p.pid}(sale en t={p.wake_time})"
                                   for p in self.blocked_queue) + "]"

            # 5) FIN DE TICK: finalizar o bloquear
            p = self.cpu
            if p and p.remaining == 0:
                p.state, p.finish = FINALIZADO, t + 1
                self.finished.append(p)
                fin.append(f"{p.pid} finaliza (Ejecución -> Finalizado) en t={t + 1}")
                self.cpu = None
            elif p and p.pending_io and p.pending_io[0][0] == p.executed:
                dur = p.pending_io.pop(0)[1]        # consumir el evento de E/S
                p.state, p.wake_time = BLOQUEADO, t + 1 + dur
                self.blocked_queue.append(p)
                fin.append(f"{p.pid} solicita E/S (Ejecución -> Bloqueado) por {dur} u.; "
                           f"vuelve a Listo en t={p.wake_time}")
                self.cpu = None

            # Registro en la traza
            self.trace.append(f"t={t:>3} -> {t + 1:<3} | CPU: {cpu_txt}")
            self.trace.append(f"            | Listos: {listos}   Bloqueados: {bloq}")
            if ini:
                self.trace.append("            | Eventos al inicio: " + "; ".join(ini))
            if fin:
                self.trace.append("            | Eventos al final : " + "; ".join(fin))
            t += 1

        self.trace.append(f"=== Todos los procesos finalizaron en t={t} ===")

# Presentación de resultados
class Reporter:
    @staticmethod
    def gantt(timeline: List[Optional[str]], max_width: int = 96) -> str:
        # Comprimir ticks consecutivos iguales en segmentos (etiqueta, inicio, fin)
        segs: List[Tuple[str, int, int]] = []
        for t, pid in enumerate(timeline):
            lab = pid or "--"                       # "--" = CPU ociosa
            if segs and segs[-1][0] == lab:
                segs[-1] = (lab, segs[-1][1], t + 1)
            else:
                segs.append((lab, t, t + 1))

        # Dibujar en bloques que no excedan max_width
        out, i = [], 0
        while i < len(segs):
            chunk, width = [], 1
            while i < len(segs):
                lab, s, e = segs[i]
                w = max(len(lab) + 2, (e - s) * 3)  # ancho proporcional a duración
                if chunk and width + w + 1 > max_width:
                    break
                chunk.append((lab, s, e, w))
                width += w + 1
                i += 1
            top = "+" + "+".join("-" * w for *_, w in chunk) + "+"
            mid = "|" + "|".join(lab.center(w) for lab, _, _, w in chunk) + "|"
            ruler, pos = [" "] * (len(top) + 4), 0
            for _, s, _, w in chunk:                # instante de inicio de cada segmento
                ruler[pos:pos + len(str(s))] = str(s)
                pos += w + 1
            end = str(chunk[-1][2])                 # instante final del bloque
            ruler[pos:pos + len(end)] = end
            out += [top, mid, top, "".join(ruler).rstrip()]
        return "\n".join(out)

    @staticmethod
    def table(procs: List[Process]) -> str:
        head = (f"{'ID':<5}{'Llegada':>8}{'Ráfaga':>8}{'Inicio':>8}"
                f"{'Fin':>6}{'Espera':>8}{'Retorno':>9}{'Respuesta':>11}")
        rows = [f"{p.pid:<5}{p.arrival:>8}{p.burst:>8}{p.start:>8}{p.finish:>6}"
                f"{p.waiting:>8}{p.turnaround:>9}{p.response:>11}"
                for p in sorted(procs, key=lambda p: natural_key(p.pid))]
        return "\n".join([head, "-" * len(head)] + rows)

    @staticmethod
    def report(sim: Simulator) -> str:
        n = len(sim.finished)
        avg = lambda f: sum(f(p) for p in sim.finished) / n
        return "\n".join([
            f"\n DIAGRAMA GANTT ({sim.scheduler.name})",
            Reporter.gantt(sim.timeline),
            f"\nTABLA DE RESULTADOS({sim.scheduler.name})",
            Reporter.table(sim.finished),
            "\nPROMEDIOS GLOBALES",
            f"Tiempo de Espera    promedio: {avg(lambda p: p.waiting):.2f}",
            f"Tiempo de Retorno   promedio: {avg(lambda p: p.turnaround):.2f}",
            f"Tiempo de Respuesta promedio: {avg(lambda p: p.response):.2f}",
            "\nNota: Espera = (Fin - Llegada) - Ráfaga; el tiempo Bloqueado "
            "también cuenta como espera.",
        ])

# Aplicación de consola
class ConsoleApp:
    MENU = """
 SIMULADOR DE PLANIFICACIÓN DE CPU 
 1. Cargar caso de prueba predefinido (10 procesos + bloqueo)
 2. Visualizar procesos ingresados
 3. Ejecutar simulación FIFO
 4. Ejecutar simulación SJF
 5. Ejecutar simulación SRTF
 0. Salir
"""

    def __init__(self):
        self.workload = Workload()

    def load_default(self):
        self.workload.load_default()
        print("Caso predefinido cargado.")
        self.show_processes()

    def show_processes(self):
        if not self.workload.specs:
            print("No hay procesos cargados. Use la opción 2.")
            return
        print(f"\n{'ID':<6}{'Llegada':>8}{'Ráfaga':>8}   Evento E/S")
        print("-" * 46)
        for s in self.workload.specs:
            io = ", ".join(f"tras {a} u. de CPU bloquea {d} u." for a, d in s.io_events) or "-"
            print(f"{s.pid:<6}{s.arrival:>8}{s.burst:>8}   {io}")

    def run_algorithm(self, scheduler: Scheduler):
        if not self.workload.specs:
            print("Primero cargue los procesos (opción 2).")
            return
        sim = Simulator(self.workload.specs, scheduler)  # copia nueva de la carga
        sim.run()
        print("\n".join(sim.trace))
        print(Reporter.report(sim))

    def run(self):
        acciones = {
            "1": self.load_default,
            "2": self.show_processes,
            "3": lambda: self.run_algorithm(FIFOScheduler()),
            "4": lambda: self.run_algorithm(SJFScheduler()),
            "5": lambda: self.run_algorithm(SRTFScheduler()),
        }
        while True:
            print(self.MENU)
            op = input("Seleccione una opción: ").strip()
            if op == "0":
                print("Fin del programa.")
                break
            (acciones.get(op) or (lambda: print("Opción inválida.")))()


if __name__ == "__main__":
    try:
        ConsoleApp().run()
    except (EOFError, KeyboardInterrupt):
        print("\nPrograma interrumpido.")