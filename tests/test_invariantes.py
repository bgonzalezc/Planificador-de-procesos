"""Propiedades que TODO algoritmo registrado debe cumplir, en todos los casos de prueba.

Recorre el diccionario ALGORITMOS, así que cuando se registre un algoritmo queda probado automáticamente, sin editar el codigo.

Propiedades:
  1. Todos los procesos finalizan y cada uno usa exactamente su ráfaga de CPU.
  2. Nadie ejecuta antes de llegar ni mientras está bloqueado.
  3. La CPU nunca queda ociosa si hay algún proceso listo.
  4. inicio/fin coinciden con la línea de tiempo (Gantt).
  5. Retorno = ráfaga + espera + bloqueado, y 0 <= respuesta <= espera.
  6. El tiempo bloqueado es la suma de las duraciones de E/S.
  7. No apropiativos sin quantum: un proceso solo suelta la CPU al terminar o bloquearse.
  8. Con quantum: un turno solo supera el quantum si nadie más estaba listo.
  9. Ejecutar dos veces da lo mismo y no modifica la carga original.
"""
import copy
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simulador.algoritmos import ALGORITMOS         
from simulador.modelos import CargaTrabajo, EspecProceso   
from simulador.motor import Simulador                

QUANTUMS_RR = (1, 2, 3, 4)


def planificadores():
    """(etiqueta, fábrica) por cada algoritmo registrado; RR con varios quantum."""
    for nombre, clase in ALGORITMOS.items():
        if nombre == "RR":
            for q in QUANTUMS_RR:
                yield f"RR q={q}", (lambda q=q, c=clase: c(q))
            continue
        try:
            clase()
        except NotImplementedError:
            continue                                
        yield nombre, clase


def casos():
    for metodo in ("cargar_predefinida", "cargar_caso_rr", "cargar_caso_prioridades"):
        carga = CargaTrabajo()
        getattr(carga, metodo)()
        yield metodo, carga.especs
    yield "borde", (
        EspecProceso("P10", 3, 2, prioridad=5),
        EspecProceso("P1", 2, 5, ((1, 2), (3, 1)), prioridad=2),
        EspecProceso("P3", 3, 4, ((2, 5),), prioridad=8),
        EspecProceso("P2", 1, 1, prioridad=1),
    )


def segmentos(linea_tiempo):
    """[(pid, inicio, fin)] agrupando ticks consecutivos del mismo proceso."""
    segs = []
    for t, pid in enumerate(linea_tiempo):
        if segs and segs[-1][0] == pid:
            segs[-1][2] = t + 1
        else:
            segs.append([pid, t, t + 1])
    return [tuple(s) for s in segs if s[0] is not None]


def ticks_disponible(espec, linea_tiempo, fin):
    """Ticks del proceso que está en el sistema y no bloqueado,
    reconstruidos solo a partir de la línea de tiempo y sus eventos de E/S."""
    es = dict(espec.eventos_es)
    bloqueado, ejecutado = set(), 0
    for t, pid in enumerate(linea_tiempo):
        if pid == espec.pid:
            ejecutado += 1
            if ejecutado in es:
                bloqueado.update(range(t + 1, t + 1 + es[ejecutado]))
    return set(range(espec.llegada, fin)) - bloqueado, bloqueado


class PruebasInvariantes(unittest.TestCase):
    def combinaciones(self):
        """(etiqueta, caso, simulación ya ejecutada, especs) para cada algoritmo x caso."""
        resultado = []
        for etiqueta, fabrica in planificadores():
            for caso, especs in casos():
                sim = Simulador(especs, fabrica())
                sim.ejecutar()
                resultado.append((etiqueta, caso, sim, especs))
        return resultado

    def test_todos_finalizan_y_usan_su_rafaga(self):
        for etiqueta, caso, sim, especs in self.combinaciones():
            with self.subTest(algoritmo=etiqueta, caso=caso):
                self.assertEqual(len(sim.finalizados), len(especs))
                for e in especs:
                    self.assertEqual(sim.linea_tiempo.count(e.pid), e.rafaga, e.pid)

    def test_gantt_coincide_con_inicio_y_fin(self):
        for etiqueta, caso, sim, _ in self.combinaciones():
            with self.subTest(algoritmo=etiqueta, caso=caso):
                for p in sim.finalizados:
                    ticks = [t for t, pid in enumerate(sim.linea_tiempo) if pid == p.pid]
                    self.assertEqual((p.inicio, p.fin), (ticks[0], ticks[-1] + 1), p.pid)
                self.assertEqual(len(sim.linea_tiempo), max(p.fin for p in sim.finalizados))

    def test_metricas_consistentes(self):
        for etiqueta, caso, sim, especs in self.combinaciones():
            with self.subTest(algoritmo=etiqueta, caso=caso):
                duracion_es = {e.pid: sum(d for _, d in e.eventos_es) for e in especs}
                for p in sim.finalizados:
                    self.assertEqual(p.retorno, p.rafaga + p.espera + p.t_bloqueado, p.pid)
                    self.assertEqual(p.retorno, p.fin - p.llegada, p.pid)
                    self.assertEqual(p.respuesta, p.inicio - p.llegada, p.pid)
                    self.assertTrue(0 <= p.respuesta <= p.espera, p.pid)
                    self.assertEqual(p.t_bloqueado, duracion_es[p.pid], p.pid)

    def test_no_ejecuta_antes_de_llegar_ni_bloqueado_y_cpu_no_ociosa(self):
        for etiqueta, caso, sim, especs in self.combinaciones():
            with self.subTest(algoritmo=etiqueta, caso=caso):
                fin = {p.pid: p.fin for p in sim.finalizados}
                disponible = {}
                for e in especs:
                    disponible[e.pid], bloqueado = ticks_disponible(
                        e, sim.linea_tiempo, fin[e.pid])
                    self.assertEqual(len(bloqueado), sum(d for _, d in e.eventos_es))
                for t, pid in enumerate(sim.linea_tiempo):
                    if pid is None:
                        listos = [x for x, ticks in disponible.items() if t in ticks]
                        self.assertEqual(listos, [], f"CPU ociosa en t={t} con listos")
                    else:
                        self.assertIn(t, disponible[pid],
                                      f"{pid} ejecuta en t={t} sin estar listo")

    def test_no_apropiativos_solo_sueltan_cpu_al_terminar_o_bloquearse(self):
        for etiqueta, caso, sim, especs in self.combinaciones():
            with self.subTest(algoritmo=etiqueta, caso=caso):
                if sim.planificador.apropiativo or sim.planificador.quantum:
                    continue
                for e in especs:
                    turnos = [s for s in segmentos(sim.linea_tiempo) if s[0] == e.pid]
                    self.assertEqual(len(turnos), len(e.eventos_es) + 1, e.pid)

    def test_quantum_solo_se_extiende_si_nadie_espera(self):
        for etiqueta, caso, sim, especs in self.combinaciones():
            with self.subTest(algoritmo=etiqueta, caso=caso):
                q = sim.planificador.quantum
                if not q:
                    continue
                fin = {p.pid: p.fin for p in sim.finalizados}
                disponible = {e.pid: ticks_disponible(e, sim.linea_tiempo, fin[e.pid])[0]
                              for e in especs}
                for pid, ini, fin_seg in segmentos(sim.linea_tiempo):
                    for t in range(ini + q, fin_seg, q):        
                        otros = [x for x, ticks in disponible.items() if x != pid and t in ticks]
                        self.assertEqual(otros, [],
                                         f"{pid} siguió tras vencer el quantum en t={t}")

    def test_ejecuciones_repetidas_son_identicas_y_no_alteran_la_carga(self):
        for etiqueta, fabrica in planificadores():
            for caso, especs in casos():
                with self.subTest(algoritmo=etiqueta, caso=caso):
                    original = copy.deepcopy(especs)
                    planificador = fabrica()        
                    a = Simulador(especs, planificador)
                    a.ejecutar()
                    b = Simulador(especs, planificador)
                    b.ejecutar()
                    self.assertEqual(a.traza, b.traza)
                    self.assertEqual(a.linea_tiempo, b.linea_tiempo)
                    self.assertEqual(especs, original)


if __name__ == "__main__":
    unittest.main()
