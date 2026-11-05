"""Pruebas del algoritmo con prioridades apropiativo (mayor valor = mayor prioridad)."""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simulador.algoritmos import ALGORITMOS, PlanificadorPrioridad   # noqa: E402
from simulador.modelos import CargaTrabajo, EspecProceso, Proceso     # noqa: E402
from simulador.motor import Simulador                                  # noqa: E402


def proceso(pid, llegada, prioridad, rafaga=5):
    return Proceso(EspecProceso(pid, llegada, rafaga, (), prioridad))


def correr(especs, nombre="PRIORIDAD"):
    sim = Simulador(tuple(especs), ALGORITMOS[nombre]())
    sim.ejecutar()
    return sim


class PruebasPrioridad(unittest.TestCase):
    def test_registrado(self):
        self.assertIs(ALGORITMOS["PRIORIDAD"], PlanificadorPrioridad)
        self.assertTrue(PlanificadorPrioridad.apropiativo)

    def test_selecciona_mayor_prioridad(self):
        listos = [proceso("P1", 0, 2), proceso("P2", 1, 9), proceso("P3", 2, 5)]
        self.assertEqual(PlanificadorPrioridad().seleccionar(listos).pid, "P2")

    def test_desempates(self):
        plan = PlanificadorPrioridad()
        # misma prioridad: llegada más temprana
        self.assertEqual(plan.seleccionar([proceso("P1", 3, 5), proceso("P2", 1, 5)]).pid, "P2")
        # misma prioridad y llegada: menor ID natural (P2 < P10)
        self.assertEqual(plan.seleccionar([proceso("P10", 0, 5), proceso("P2", 0, 5)]).pid, "P2")

    def test_expropia_solo_con_prioridad_estrictamente_mayor(self):
        plan = PlanificadorPrioridad()
        corriendo = proceso("P1", 0, 5)
        self.assertFalse(plan.debe_expropiar(corriendo, [proceso("P2", 1, 5)]))
        self.assertFalse(plan.debe_expropiar(corriendo, [proceso("P2", 1, 4)]))
        self.assertTrue(plan.debe_expropiar(corriendo, [proceso("P2", 1, 6)]))

    def test_llegada_prioritaria_expropia(self):
        sim = correr([EspecProceso("P1", 0, 4, (), 1), EspecProceso("P2", 1, 2, (), 9)])
        self.assertEqual(sim.linea_tiempo, ["P1", "P2", "P2", "P1", "P1", "P1"])
        self.assertIn("P1 es expropiado", "\n".join(sim.traza))

    def test_traza_muestra_prioridad_del_seleccionado(self):
        sim = correr([EspecProceso("P1", 0, 1, (), 3)])
        self.assertIn("P1 despachado (Listo -> Ejecución) [prioridad=3]", "\n".join(sim.traza))

    def test_otros_algoritmos_no_muestran_prioridad(self):
        sim = correr([EspecProceso("P1", 0, 1, (), 3)], "FIFO")
        self.assertNotIn("prioridad=", "\n".join(sim.traza))

    def test_orden_distinto_a_fifo_con_10_procesos(self):
        carga = CargaTrabajo()
        carga.cargar_caso_prioridades()
        orden = {n: [p.pid for p in correr(carga.especs, n).finalizados]
                 for n in ("FIFO", "PRIORIDAD")}
        self.assertEqual(len(orden["PRIORIDAD"]), 10)
        self.assertNotEqual(orden["FIFO"], orden["PRIORIDAD"])
        # P6 (prioridad 10) termina primero; P5 (prioridad 1) termina último
        self.assertEqual((orden["PRIORIDAD"][0], orden["PRIORIDAD"][-1]), ("P6", "P5"))

    def test_bloqueado_vuelve_a_listos_y_expropia(self):
        carga = CargaTrabajo()
        carga.cargar_caso_prioridades()
        sim = correr(carga.especs)
        traza = "\n".join(sim.traza)
        self.assertIn("P2 solicita E/S (Ejecución -> Bloqueado)", traza)
        self.assertIn("P2 termina E/S (Bloqueado -> Listo)", traza)
        p2 = next(p for p in sim.finalizados if p.pid == "P2")
        self.assertEqual(p2.t_bloqueado, 3)
        self.assertEqual(p2.retorno, p2.rafaga + p2.espera + p2.t_bloqueado)

    def test_inanicion_visible_en_proceso_de_menor_prioridad(self):
        carga = CargaTrabajo()
        carga.cargar_caso_prioridades()
        sim = correr(carga.especs)
        p5 = next(p for p in sim.finalizados if p.pid == "P5")
        self.assertEqual(max(sim.finalizados, key=lambda p: p.espera).pid, "P5")
        self.assertGreater(p5.espera, 30)


if __name__ == "__main__":
    unittest.main()
