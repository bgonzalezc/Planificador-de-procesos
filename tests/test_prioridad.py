"""Pruebas del algoritmo con prioridades (código: Francisco · pruebas: Thomas).

Se escribieron ANTES de la implementación, siguiendo lo acordado:
  - Variante NO apropiativa (recomendada en el plan de trabajo, sección 2.3).
  - Convención del equipo (modelos.py y README): MAYOR valor numérico = MAYOR prioridad.
  - Desempates: primero llegada y luego identificador (orden natural: P2 < P10).
  - La traza debe mostrar la prioridad del proceso despachado (requisito del enunciado).

Mientras `PlanificadorPrioridad` lance NotImplementedError, todas estas pruebas se
omiten (skip). En cuanto se suba la implementación, se activan solas.

Todos los resultados esperados están calculados A MANO (ver comentarios); no se usa
el programa para generarlos.
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simulador.algoritmos import ALGORITMOS, Planificador, PlanificadorFIFO  # noqa: E402
from simulador.algoritmos.prioridad import PlanificadorPrioridad            # noqa: E402
from simulador.constantes import FINALIZADO                                 # noqa: E402
from simulador.modelos import CargaTrabajo, EspecProceso, Proceso           # noqa: E402
from simulador.motor import Simulador                                       # noqa: E402

try:
    PlanificadorPrioridad()
    PENDIENTE = None
except NotImplementedError as error:
    PENDIENTE = str(error)

omitir_si_pendiente = unittest.skipIf(
    PENDIENTE is not None, f"Prioridades aún no implementadas: {PENDIENTE}")


def espec(pid, llegada, rafaga, prioridad, eventos_es=()):
    # Argumentos con nombre: evita confundir eventos_es con prioridad (ver plan, sección 4).
    return EspecProceso(pid=pid, llegada=llegada, rafaga=rafaga,
                        eventos_es=eventos_es, prioridad=prioridad)


def correr(especs, planificador=None):
    sim = Simulador(tuple(especs), planificador or PlanificadorPrioridad())
    sim.ejecutar()
    return sim, {p.pid: p for p in sim.finalizados}


def expandir(turnos):
    """[("P1", 2), ("P2", 1)] -> ["P1", "P1", "P2"]"""
    return [pid for pid, duracion in turnos for _ in range(duracion)]


def orden_de_despacho(sim):
    """Orden en que cada proceso usa la CPU por primera vez."""
    vistos = []
    for pid in sim.linea_tiempo:
        if pid and pid not in vistos:
            vistos.append(pid)
    return vistos


def metricas(procesos):
    """(inicio, fin, espera, retorno, respuesta, bloqueado) por proceso."""
    return {p.pid: (p.inicio, p.fin, p.espera, p.retorno, p.respuesta, p.t_bloqueado)
            for p in procesos}


@omitir_si_pendiente
class PruebasContratoPrioridad(unittest.TestCase):
    def test_es_un_planificador_no_apropiativo_sin_quantum(self):
        pr = PlanificadorPrioridad()
        self.assertIsInstance(pr, Planificador)
        self.assertFalse(pr.apropiativo)
        self.assertIsNone(pr.quantum)

    def test_esta_registrado_en_algoritmos(self):
        self.assertIn(PlanificadorPrioridad, ALGORITMOS.values())

    def test_selecciona_mayor_valor_de_prioridad(self):
        listos = [Proceso(espec("P1", 0, 5, 2)),
                  Proceso(espec("P2", 1, 1, 9)),     # mayor prioridad
                  Proceso(espec("P3", 0, 3, 5))]
        self.assertEqual(PlanificadorPrioridad().seleccionar(listos).pid, "P2")

    def test_desempate_por_llegada(self):
        # Misma prioridad: gana P5 porque llegó antes, aunque su ID sea mayor.
        listos = [Proceso(espec("P3", 4, 1, 6)), Proceso(espec("P5", 1, 9, 6))]
        self.assertEqual(PlanificadorPrioridad().seleccionar(listos).pid, "P5")

    def test_desempate_por_identificador_en_orden_natural(self):
        # Misma prioridad y llegada: P2 < P10 (orden natural, no alfabético).
        listos = [Proceso(espec("P10", 0, 1, 3)), Proceso(espec("P2", 0, 1, 3))]
        self.assertEqual(PlanificadorPrioridad().seleccionar(listos).pid, "P2")

    def test_seleccionar_no_modifica_la_cola(self):
        listos = [Proceso(espec("P1", 0, 2, 1)), Proceso(espec("P2", 0, 2, 7))]
        copia = list(listos)
        PlanificadorPrioridad().seleccionar(listos)
        self.assertEqual(listos, copia)


@omitir_si_pendiente
class PruebasSimulacionPrioridad(unittest.TestCase):
    def test_llegada_mas_prioritaria_no_interrumpe(self):
        # No apropiativo: P2 (prioridad 10) llega en t=1 pero espera a que P1 termine.
        sim, p = correr([espec("P1", 0, 4, 1), espec("P2", 1, 2, 10)])
        self.assertEqual(sim.linea_tiempo, ["P1"] * 4 + ["P2"] * 2)
        self.assertNotIn("expropiado", "\n".join(sim.traza))
        self.assertEqual(p["P2"].espera, 3)

    def test_ordena_por_prioridad_no_por_llegada_ni_por_rafaga(self):
        # t=2 hay en listos: P2(pr 1), P3(pr 3), P4(pr 2) -> P3, luego P4, luego P2.
        # FIFO daría P1,P2,P3,P4 y SJF daría P1,P4,P2,P3.
        sim, _ = correr([espec("P1", 0, 2, 5), espec("P2", 1, 3, 1),
                         espec("P3", 1, 4, 3), espec("P4", 2, 1, 2)])
        self.assertEqual(sim.linea_tiempo,
                         expandir([("P1", 2), ("P3", 4), ("P4", 1), ("P2", 3)]))

    def test_bloqueado_vuelve_a_listos_y_compite_por_prioridad(self):
        # P1 (pr 9) corre 1 u. y se bloquea 2 u. (vuelve en t=3).
        # P3 (pr 5) toma la CPU en t=1; en t=3 vuelve P1 pero NO interrumpe a P3.
        # En t=4 hay listos P1 (pr 9) y P2 (pr 1) -> P1; P2 queda al final.
        sim, p = correr([espec("P1", 0, 4, 9, eventos_es=((1, 2),)),
                         espec("P2", 0, 5, 1),
                         espec("P3", 1, 3, 5)])
        self.assertEqual(sim.linea_tiempo,
                         expandir([("P1", 1), ("P3", 3), ("P1", 3), ("P2", 5)]))
        self.assertEqual(metricas(sim.finalizados), {
            "P1": (0, 7, 1, 7, 0, 2),     # espera: solo t=3 en listos
            "P2": (7, 12, 7, 12, 7, 0),
            "P3": (1, 4, 0, 3, 0, 0),
        })
        traza = "\n".join(sim.traza)
        self.assertIn("P1 solicita E/S (Ejecución -> Bloqueado)", traza)
        self.assertIn("P1 termina E/S (Bloqueado -> Listo)", traza)

    def test_traza_muestra_la_prioridad_del_despachado(self):
        # Requisito del enunciado: "mostrar la prioridad de los procesos seleccionados".
        sim, _ = correr([espec("P1", 0, 1, 4), espec("P2", 0, 1, 8)])
        linea = next(l for l in sim.traza if "P2 despachado" in l)
        self.assertIn("prioridad", linea.lower())
        self.assertIn("8", linea.split("P2 despachado", 1)[1])


@omitir_si_pendiente
class PruebasCasoDiezProcesos(unittest.TestCase):
    """Caso `cargar_caso_prioridades()` resuelto a mano (no apropiativo).

    Proc  Lleg  Ráf  Prio  E/S
    P1     0     6    4
    P2     1     4    9    tras 2 u. de CPU bloquea 3 u.
    P3     2     8    2
    P4     3     3    7
    P5     3     5    1
    P6     5     2   10
    P7     6     7    5
    P8     8     4    3
    P9     9     6    8
    P10   10     3    6

    t=0  solo P1                                  -> P1 (0-6)
    t=6  listos P2,P3,P4,P5,P6,P7                 -> P6 pr10 (6-8)
    t=8  + P8                                     -> P2 pr9 (8-10), se bloquea hasta t=13
    t=10 + P9, P10                                -> P9 pr8 (10-16); P2 vuelve en t=13
    t=16                                          -> P2 pr9 (16-18)
    luego P4 pr7 (18-21), P10 pr6 (21-24), P7 pr5 (24-31),
          P8 pr3 (31-35), P3 pr2 (35-43), P5 pr1 (43-48)
    """

    TURNOS = [("P1", 6), ("P6", 2), ("P2", 2), ("P9", 6), ("P2", 2), ("P4", 3),
              ("P10", 3), ("P7", 7), ("P8", 4), ("P3", 8), ("P5", 5)]

    # (inicio, fin, espera, retorno, respuesta, bloqueado)
    METRICAS = {
        "P1": (0, 6, 0, 6, 0, 0),
        "P2": (8, 18, 10, 17, 7, 3),
        "P3": (35, 43, 33, 41, 33, 0),
        "P4": (18, 21, 15, 18, 15, 0),
        "P5": (43, 48, 40, 45, 40, 0),
        "P6": (6, 8, 1, 3, 1, 0),
        "P7": (24, 31, 18, 25, 18, 0),
        "P8": (31, 35, 23, 27, 23, 0),
        "P9": (10, 16, 1, 7, 1, 0),
        "P10": (21, 24, 11, 14, 11, 0),
    }

    def setUp(self):
        self.carga = CargaTrabajo()
        self.carga.cargar_caso_prioridades()
        self.sim, self.p = correr(self.carga.especs)

    def test_linea_de_tiempo(self):
        self.assertEqual(self.sim.linea_tiempo, expandir(self.TURNOS))

    def test_metricas_por_proceso(self):
        self.assertEqual(metricas(self.sim.finalizados), self.METRICAS)
        for p in self.sim.finalizados:
            self.assertEqual(p.estado, FINALIZADO)
            self.assertEqual(p.retorno, p.rafaga + p.espera + p.t_bloqueado)

    def test_promedios(self):
        n = len(self.sim.finalizados)
        promedio = lambda a: round(sum(getattr(p, a) for p in self.sim.finalizados) / n, 2)
        self.assertEqual((promedio("espera"), promedio("retorno"), promedio("respuesta")),
                         (15.2, 20.3, 14.9))   # 152/10, 203/10, 149/10

    def test_orden_distinto_a_fifo(self):
        fifo = Simulador(self.carga.especs, PlanificadorFIFO())
        fifo.ejecutar()
        self.assertEqual(orden_de_despacho(fifo),
                         ["P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8", "P9", "P10"])
        self.assertEqual(orden_de_despacho(self.sim),
                         ["P1", "P6", "P2", "P9", "P4", "P10", "P7", "P8", "P3", "P5"])

    def test_menor_prioridad_queda_al_final(self):
        # Ilustra el riesgo de inanición: P5 (prioridad 1) llega en t=3 y espera 40 u.
        self.assertEqual(self.sim.finalizados[-1].pid, "P5")
        self.assertEqual(self.p["P5"].espera, max(p.espera for p in self.sim.finalizados))


if __name__ == "__main__":
    unittest.main()
