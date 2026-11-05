"""Genera las evidencias de funcionamiento de todos los algoritmos registrados.

Uso (desde la raíz del proyecto):
    python3 evidencias/generar_evidencias.py

Crea, para cada caso de 10 procesos, un archivo por algoritmo con la traza completa,
el Gantt, la tabla de métricas y los promedios (exactamente lo que muestra el menú),
y un `resumen.md` con la comparación de promedios y la evidencia del bloqueo.
"""
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from simulador.algoritmos import ALGORITMOS          
from simulador.modelos import CargaTrabajo           
from simulador.motor import Simulador                
from simulador.reportes import Reportero             

SALIDA = os.path.join(RAIZ, "evidencias")
QUANTUMS_RR = (3, 4)
CASOS = {
    "caso_base": ("cargar_predefinida", "Caso base (etapa 02), P3 se bloquea"),
    "caso_rr": ("cargar_caso_rr", "Caso Round Robin, P3 se bloquea"),
    "caso_prioridades": ("cargar_caso_prioridades",
                         "Caso prioridades (1..10, mayor valor = mayor prioridad), P2 se bloquea"),
}


def planificadores():
    """(etiqueta de archivo, planificador) por cada algoritmo disponible."""
    for nombre, clase in ALGORITMOS.items():
        if nombre == "RR":
            for q in QUANTUMS_RR:
                yield f"RR_q{q}", clase(q)
            continue
        try:
            yield nombre, clase()
        except NotImplementedError:
            print(f"  (omitido {nombre}: aún no implementado)")


def promedios(sim):
    n = len(sim.finalizados)
    return tuple(sum(getattr(p, a) for p in sim.finalizados) / n
                 for a in ("espera", "retorno", "respuesta"))


def tabla_procesos(especs):
    filas = ["| ID | Llegada | Ráfaga | Prioridad | E/S |", "|---|---|---|---|---|"]
    for e in especs:
        es = ", ".join(f"tras {a} u. bloquea {d} u." for a, d in e.eventos_es) or "-"
        filas.append(f"| {e.pid} | {e.llegada} | {e.rafaga} | {e.prioridad} | {es} |")
    return filas


def extracto_bloqueo(sim):
    """Traza desde que el primer proceso pasa a Bloqueado hasta que vuelve a Listo
    (incluye los ticks intermedios, donde se ve en la cola de bloqueados)."""
    traza = sim.traza
    i_bloq = next(i for i, l in enumerate(traza) if "(Ejecución -> Bloqueado)" in l)
    i_vuelve = next(i for i, l in enumerate(traza)
                    if i > i_bloq and "(Bloqueado -> Listo)" in l)
    inicio_tick = max(i for i in range(i_bloq + 1) if traza[i].startswith("t="))
    return traza[inicio_tick:i_vuelve + 1]


def main():
    resumen = ["# Evidencias de funcionamiento", "",
               "Generado con `python3 evidencias/generar_evidencias.py`.",
               "Cada archivo `.txt` contiene la traza tick a tick, el Gantt, la tabla de "
               "métricas y los promedios, igual que en el menú.", ""]
    bloqueo = None
    for carpeta, (metodo, titulo) in CASOS.items():
        print(f"{titulo}:")
        carga = CargaTrabajo()
        getattr(carga, metodo)()
        os.makedirs(os.path.join(SALIDA, carpeta), exist_ok=True)
        resumen += [f"## {titulo}", ""] + tabla_procesos(carga.especs) + [
            "", "| Algoritmo | Espera prom. | Retorno prom. | Respuesta prom. | Archivo |",
            "|---|---|---|---|---|"]
        for etiqueta, planificador in planificadores():
            sim = Simulador(carga.especs, planificador)
            sim.ejecutar()
            archivo = os.path.join(carpeta, f"{etiqueta}.txt")
            with open(os.path.join(SALIDA, archivo), "w", encoding="utf-8") as f:
                f.write(f"{titulo} - {etiqueta}\n\n")
                f.write("\n".join(sim.traza) + "\n")
                f.write(Reportero.informe(sim) + "\n")
            e, r, s = promedios(sim)
            resumen.append(f"| {etiqueta} | {e:.2f} | {r:.2f} | {s:.2f} | `{archivo}` |")
            print(f"  {archivo}")
            if bloqueo is None and carpeta == "caso_base" and etiqueta == "FIFO":
                bloqueo = extracto_bloqueo(sim)
        resumen.append("")
    resumen += ["## Proceso bloqueado que vuelve a la lista de listos", "",
                "Extracto de `caso_base/FIFO.txt`: P3 solicita E/S, pasa a la cola de "
                "bloqueados y, al terminar, vuelve a la cola de listos.", "", "```"]
    resumen += (bloqueo or []) + ["```", ""]
    with open(os.path.join(SALIDA, "resumen.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(resumen))
    print("Resumen: evidencias/resumen.md")


if __name__ == "__main__":
    main()
