"""Pruebas de la integración de Round Robin con el menú de consola."""
import io
import os
import sys
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simulador.algoritmos import PlanificadorRoundRobin  # noqa: E402
from simulador.consola import AppConsola                  # noqa: E402
from simulador.modelos import CargaTrabajo                # noqa: E402


class PruebasConsolaRoundRobin(unittest.TestCase):
    def setUp(self):
        self.app = AppConsola()
        self.salida = io.StringIO()

    def test_cargar_caso_rr(self):
        with redirect_stdout(self.salida):
            self.app.cargar_caso_rr()
        esperada = CargaTrabajo()
        esperada.cargar_caso_rr()
        self.assertEqual(self.app.carga.especs, esperada.especs)
        self.assertIn("Caso Round Robin cargado.", self.salida.getvalue())
        self.assertIn("P10", self.salida.getvalue())

    def test_sin_carga_no_pide_quantum_ni_simula(self):
        with patch("builtins.input") as entrada, \
                patch.object(self.app, "ejecutar_algoritmo") as ejecutar, \
                redirect_stdout(self.salida):
            self.app.ejecutar_round_robin()
        entrada.assert_not_called()
        ejecutar.assert_not_called()
        self.assertIn("opción 1 o 7", self.salida.getvalue())

    def test_quantum_predeterminado_y_personalizado(self):
        self.app.carga.cargar_caso_rr()
        for entrada, quantum in (("", 4), ("   ", 4), ("3", 3), (" 1 ", 1)):
            with self.subTest(entrada=entrada), \
                    patch("builtins.input", return_value=entrada), \
                    patch.object(self.app, "ejecutar_algoritmo") as ejecutar:
                self.app.ejecutar_round_robin()
                ejecutar.assert_called_once()
                planificador = ejecutar.call_args[0][0]
                self.assertIsInstance(planificador, PlanificadorRoundRobin)
                self.assertEqual(planificador.quantum, quantum)

    def test_quantum_invalido_se_vuelve_a_pedir(self):
        self.app.carga.cargar_caso_rr()
        with patch("builtins.input", side_effect=["0", "-2", "abc", "2.5", "3"]) as entrada, \
                patch.object(self.app, "ejecutar_algoritmo") as ejecutar, \
                redirect_stdout(self.salida):
            self.app.ejecutar_round_robin()
        self.assertEqual(entrada.call_count, 5)
        ejecutar.assert_called_once()
        self.assertEqual(ejecutar.call_args[0][0].quantum, 3)
        self.assertEqual(self.salida.getvalue().count("entero mayor que cero"), 4)

    def test_menu_ejecuta_rr_con_reporte_y_permite_repetir(self):
        # Cargar RR, ejecutar con q=3, repetir con q=4 por defecto y salir.
        with patch("builtins.input", side_effect=["7", "6", "3", "6", "", "0"]), \
                redirect_stdout(self.salida):
            self.app.ejecutar()
        texto = self.salida.getvalue()
        self.assertEqual(texto.count("=== TRAZA DE SIMULACIÓN: RR ==="), 2)
        self.assertIn("agota su quantum de 3 u.", texto)
        self.assertIn("agota su quantum de 4 u.", texto)
        self.assertEqual(texto.count("Todos los procesos finalizaron en t=59"), 2)
        self.assertIn("GANTT", texto)
        self.assertIn("Fin del programa.", texto)
        esperada = CargaTrabajo()
        esperada.cargar_caso_rr()
        self.assertEqual(self.app.carga.especs, esperada.especs)

    def test_menu_rr_tambien_acepta_caso_base(self):
        with patch("builtins.input", side_effect=["1", "6", "2", "0"]), \
                redirect_stdout(self.salida):
            self.app.ejecutar()
        texto = self.salida.getvalue()
        self.assertIn("=== TRAZA DE SIMULACIÓN: RR ===", texto)
        self.assertIn("Todos los procesos finalizaron", texto)
        self.assertIn("Fin del programa.", texto)

    def test_menu_registra_proceso(self):
        with patch("builtins.input", side_effect=["8", "P1", "0", "5", "", "n", "0"]), \
                redirect_stdout(self.salida):
            self.app.ejecutar()
        self.assertEqual(len(self.app.carga.especs), 1)
        proceso = self.app.carga.especs[0]
        self.assertEqual((proceso.pid, proceso.llegada, proceso.rafaga), ("P1", 0, 5))
        self.assertIn("Proceso P1 registrado.", self.salida.getvalue())

    def test_menu_registra_proceso_con_prioridad_y_es(self):
        entradas = ["8", "P1", "0", "5", "7", "s", "2", "3", "n", "0"]
        with patch("builtins.input", side_effect=entradas), redirect_stdout(self.salida):
            self.app.ejecutar()
        espec = self.app.carga.especs[0]
        self.assertEqual(espec.prioridad, 7)
        self.assertEqual(espec.eventos_es, ((2, 3),))

    def test_menu_carga_prioridades_y_muestra_ayuda(self):
        with patch("builtins.input", side_effect=["11", "12", "0"]), \
                redirect_stdout(self.salida):
            self.app.ejecutar()
        texto = self.salida.getvalue()
        self.assertEqual(len(self.app.carga.especs), 10)
        self.assertIn("Prioridad", texto)
        self.assertIn("Python 3", texto)

    def test_configurar_quantum_persistente_en_el_menu(self):
        with patch("builtins.input", side_effect=["9", "3", "7", "6", "", "0"]), \
                redirect_stdout(self.salida):
            self.app.ejecutar()
        texto = self.salida.getvalue()
        self.assertEqual(self.app.quantum, 3)
        self.assertIn("Quantum de Round Robin configurado en 3.", texto)
        self.assertIn("Configurar quantum de Round Robin (actual: 3)", texto)
        self.assertIn("agota su quantum de 3 u.", texto)

    def test_configurar_quantum_rechaza_valores_invalidos(self):
        with patch("builtins.input", side_effect=["0", "2.5", "5"]), \
                redirect_stdout(self.salida):
            self.app.configurar_quantum()
        self.assertEqual(self.app.quantum, 5)
        self.assertEqual(
            self.salida.getvalue().count("El valor debe ser mayor que cero."), 1
        )
        self.assertEqual(
            self.salida.getvalue().count("Ingrese un número entero válido."), 1
        )

    def test_ver_ultima_simulacion_antes_de_ejecutar(self):
        with redirect_stdout(self.salida):
            self.app.mostrar_ultima_simulacion()
        self.assertIn("Aún no se ha ejecutado ninguna simulación.", self.salida.getvalue())

    def test_menu_muestra_la_ultima_simulacion_sin_volver_a_ejecutarla(self):
        with patch("builtins.input", side_effect=["1", "3", "10", "0"]), \
                redirect_stdout(self.salida):
            self.app.ejecutar()
        texto = self.salida.getvalue()
        self.assertEqual(texto.count("=== TRAZA DE SIMULACIÓN: FIFO ==="), 2)
        self.assertEqual(texto.count("GANTT"), 2)
        self.assertEqual(texto.count("Todos los procesos finalizaron en t="), 2)

if __name__ == "__main__":
    unittest.main()
