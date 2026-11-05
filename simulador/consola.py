"""Aplicación de consola (menú interactivo)."""
from typing import Optional

from .algoritmos import ALGORITMOS, Planificador
from .modelos import CargaTrabajo
from .motor import Simulador
from .reportes import Reportero


class AppConsola:
    MENU = """
 SIMULADOR DE PLANIFICACIÓN DE CPU 
 1. Cargar caso de prueba predefinido (10 procesos + bloqueo)
 2. Visualizar procesos ingresados
 3. Ejecutar simulación FIFO
 4. Ejecutar simulación SJF
 5. Ejecutar simulación SRTF
 6. Ejecutar simulación Round Robin
 7. Cargar caso Round Robin (10 procesos + bloqueo)
 8. Registrar proceso
 9. Configurar quantum de Round Robin (actual: {quantum})
 10. Ver última simulación
 11. Cargar caso de prioridades (10 procesos, mayor valor = mayor prioridad)
 12. Ayuda: lenguaje e instrucciones de uso
 13. Ejecutar simulación por Prioridades (no apropiativa)
 0. Salir
"""

    def __init__(self):
        self.carga = CargaTrabajo()
        self.quantum = 4
        self.ultima_simulacion: Optional[Simulador] = None

    def cargar_predefinida(self):
        self.carga.cargar_predefinida()
        print("Caso predefinido cargado.")
        self.mostrar_procesos()

    def cargar_caso_rr(self):
        self.carga.cargar_caso_rr()
        print("Caso Round Robin cargado.")
        self.mostrar_procesos()

    def cargar_caso_prioridades(self):
        self.carga.cargar_caso_prioridades()
        print("Caso de prioridades cargado (mayor valor = mayor prioridad).")
        self.mostrar_procesos()

    AYUDA = """
AYUDA
 Lenguaje: Python 3 (solo biblioteca estándar). Legible, listas nativas para las
 colas y POO limpia (dataclass inmutable, ABC para el patrón Strategy).
 Uso:
  1) Cargue procesos (opciones 1, 7, 11) o registre a mano (opción 8).
  2) Ejecute un algoritmo (opciones 3 a 6 y 13). Round Robin usa el quantum de la opción 9.
  3) Revise el último resultado con la opción 10.
 Prioridad: mayor valor numérico = mayor prioridad.
 E/S: 'tras N u. de CPU bloquea D u.' envía el proceso a Bloqueado y luego a Listo.
 Espera = tiempo en la cola de Listos (el bloqueo no cuenta).
"""

    def mostrar_ayuda(self):
        print(self.AYUDA)

    def ejecutar_round_robin(self):
        if not self.carga.especs:
            print("Primero cargue los procesos (opción 1 o 7).")
            return
        while True:
            entrada = input(
                f"Quantum de Round Robin (entero > 0) [{self.quantum}]: "
            ).strip()
            try:
                quantum = int(entrada) if entrada else self.quantum
                planificador = ALGORITMOS["RR"](quantum)
            except ValueError:
                print("El quantum debe ser un entero mayor que cero.")
                continue
            break
        self.ejecutar_algoritmo(planificador)

    def registrar_proceso(self):
        pid = input("Identificador del proceso: ").strip()
        llegada = self._leer_entero("Tiempo de llegada (entero >= 0): ", minimo=0)
        rafaga = self._leer_entero("Ráfaga de CPU (entero > 0): ", minimo=1)
        prioridad = self._leer_entero_opcional(
            "Prioridad (entero, mayor = más prioritario) [0]: ", defecto=0)
        eventos = []
        while input("¿Agregar evento de E/S? (s/N): ").strip().lower() == "s":
            tras = self._leer_entero("  Bloquear tras cuántas u. de CPU (entero > 0): ", minimo=1)
            dur = self._leer_entero("  Duración del bloqueo (entero > 0): ", minimo=1)
            eventos.append((tras, dur))
        try:
            self.carga.agregar(pid, llegada, rafaga, tuple(eventos), prioridad)
        except ValueError as error:
            print(f"No se pudo registrar el proceso: {error}")
            return
        print(f"Proceso {pid} registrado.")
        self.mostrar_procesos()

    def configurar_quantum(self):
        self.quantum = self._leer_entero(
            "Nuevo quantum de Round Robin (entero > 0): ", minimo=1
        )
        print(f"Quantum de Round Robin configurado en {self.quantum}.")

    @staticmethod
    def _leer_entero_opcional(mensaje: str, defecto: int) -> int:
        while True:
            entrada = input(mensaje).strip()
            if not entrada:
                return defecto
            try:
                return int(entrada)
            except ValueError:
                print("Ingrese un número entero válido.")

    @staticmethod
    def _leer_entero(mensaje: str, minimo: int) -> int:
        while True:
            entrada = input(mensaje).strip()
            try:
                valor = int(entrada)
            except ValueError:
                print("Ingrese un número entero válido.")
                continue
            if valor < minimo:
                comparacion = "mayor que cero" if minimo == 1 else "mayor o igual a cero"
                print(f"El valor debe ser {comparacion}.")
                continue
            return valor

    def mostrar_procesos(self):
        if not self.carga.especs:
            print("No hay procesos cargados. Use la opción 1 o 7.")
            return
        print(f"\n{'ID':<6}{'Llegada':>8}{'Ráfaga':>8}{'Prioridad':>11}   Evento E/S")
        print("-" * 57)
        for s in self.carga.especs:
            es = ", ".join(f"tras {a} u. de CPU bloquea {d} u." for a, d in s.eventos_es) or "-"
            print(f"{s.pid:<6}{s.llegada:>8}{s.rafaga:>8}{s.prioridad:>11}   {es}")

    def mostrar_ultima_simulacion(self):
        if self.ultima_simulacion is None:
            print("Aún no se ha ejecutado ninguna simulación.")
            return
        print("\n".join(self.ultima_simulacion.traza))
        print(Reportero.informe(self.ultima_simulacion))

    def ejecutar_algoritmo(self, planificador: Planificador):
        if not self.carga.especs:
            print("Primero cargue los procesos (opción 1, 7 u 11).")
            return
        sim = Simulador(self.carga.especs, planificador)  # copia nueva de la carga
        sim.ejecutar()
        self.ultima_simulacion = sim
        self.mostrar_ultima_simulacion()

    def ejecutar(self):
        acciones = {
            "1": self.cargar_predefinida,
            "2": self.mostrar_procesos,
            "3": lambda: self.ejecutar_algoritmo(ALGORITMOS["FIFO"]()),
            "4": lambda: self.ejecutar_algoritmo(ALGORITMOS["SJF"]()),
            "5": lambda: self.ejecutar_algoritmo(ALGORITMOS["SRTF"]()),
            "6": self.ejecutar_round_robin,
            "7": self.cargar_caso_rr,
            "8": self.registrar_proceso,
            "9": self.configurar_quantum,
            "10": self.mostrar_ultima_simulacion,
            "11": self.cargar_caso_prioridades,
            "12": self.mostrar_ayuda,
            "13": lambda: self.ejecutar_algoritmo(ALGORITMOS["PRIORIDAD"]()),
        }
        while True:
            print(self.MENU.format(quantum=self.quantum))
            op = input("Seleccione una opción: ").strip()
            if op == "0":
                print("Fin del programa.")
                break
            (acciones.get(op) or (lambda: print("Opción inválida.")))()
