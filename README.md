# Simulador de planificación de procesos de corto plazo

Simulador por consola en Python 3 (solo biblioteca estándar).
Algoritmos disponibles: **FIFO**, **SJF** (no apropiativo), **SRTF** (apropiativo) y
**Round Robin** y **prioridades no apropiativo**. Incluye el estado **Bloqueado** por eventos de E/S.

## Integrantes

| Integrante | Responsabilidad |
|---|---|
| Benjamin Zamora | Arquitectura, motor de simulación, integración |
| José Luna | Round Robin (`simulador/algoritmos/round_robin.py`) |
| Francisco | Algoritmo con prioridades (`simulador/algoritmos/prioridad.py`) |
| Benjamin González | Menú de consola (`simulador/consola.py`): procesos, quantum y última simulación |
| Thomas | Pruebas (`tests/`) |

## Ejecución

```
python3 main.py                              # abre el menú
python3 -m unittest discover -s tests -v     # ejecuta las pruebas
```

Requiere Python 3.8 o superior; no hay dependencias externas.

## Estructura

```
main.py                      # punto de entrada
simulador/
  constantes.py              # estados y clave_natural (orden P2 < P10)
  modelos.py                 # EspecProceso, Proceso, CargaTrabajo
  motor.py                   # Simulador: reloj, colas y CPU
  reportes.py                # Reportero: Gantt ASCII, tabla y promedios
  consola.py                 # AppConsola: menú interactivo
  algoritmos/
    base.py                  # Planificador (interfaz)
    fifo.py  sjf.py  srtf.py
    round_robin.py           # Round Robin con quantum configurable (José Luna)
    prioridad.py             # prioridades no apropiativo (Francisco)
    __init__.py              # registro ALGORITMOS
tests/                       # regresión, motor, RR, consola RR y prioridades
```

## Clases

| Clase | Rol |
|---|---|
| `EspecProceso` | Copia inmutable del proceso: id, llegada, ráfaga, eventos de E/S, prioridad |
| `Proceso` | Proceso en simulación: restante, estado, inicio, fin, espera, bloqueado y métricas |
| `CargaTrabajo` | Guarda la carga ingresada y el caso predefinido |
| `Planificador` | Interfaz (patrón Strategy); un algoritmo por clase |
| `Simulador` | Reloj, cola de listos, cola de bloqueados y CPU |
| `Reportero` | Gantt ASCII, tabla de resultados y promedios |
| `AppConsola` | Menú interactivo |

El simulador crea objetos `Proceso` nuevos a partir de las `EspecProceso`, así que la carga
original no se modifica y se puede simular varias veces.

## Listas y estados

Listas: **cola de listos** (se agrega al final), **cola de bloqueados** y **CPU** (un solo proceso a la vez).

```
Nuevo -> Listo -> Ejecución -> Finalizado
                    |   ^
                    v   |
                 Bloqueado        (E/S: vuelve a Listo al terminar)
Ejecución -> Listo                (expropiado por SRTF o por fin de quantum)
```

Cada unidad de tiempo (tick) el motor hace, en este orden:

1. **Admisión:** entran a listos las llegadas y los que terminan E/S (desempate: llegada, luego ID).
2. **Fin de quantum** (si el algoritmo define `quantum`) y **expropiación** (si es apropiativo).
3. **Despacho:** si la CPU está libre, el planificador elige de la cola de listos.
4. **Ejecución** de una unidad (o CPU ociosa) y contabilidad de espera/bloqueo.
5. **Fin de tick:** el proceso finaliza o pasa a Bloqueado si le toca un evento de E/S.

Los eventos de E/S son `(CPU ejecutada, duración)`: tras ejecutar esa cantidad de CPU el proceso se bloquea.

## Métricas

- **Retorno** = fin − llegada.
- **Respuesta** = primer inicio − llegada.
- **Espera** = tiempo acumulado en la cola de listos. **No** incluye el tiempo bloqueado.
- Se cumple `Retorno = Ráfaga + Espera + Bloqueado`.

Desempates generales: primero el que llegó antes y luego el de menor identificador.

## Quantum (Round Robin)

- `PlanificadorRoundRobin(quantum=4)` expone `self.quantum` (entero > 0). Su constructor
  lanza `ValueError` ante cero, negativos, booleanos o valores que no sean enteros.
- `seleccionar(listos)` devuelve el primero sin retirar ni reordenar elementos; el motor
  garantiza que la cola no esté vacía y se encarga del despacho y la rotación.
- El proceso ejecuta como máximo `quantum` unidades seguidas; si no termina, vuelve al **final** de la cola de listos.
- Si no hay otros procesos listos, continúa ejecutando otro quantum sin ser interrumpido.
- Si un proceso llega en el mismo instante en que vence un quantum, **entra a la cola antes** que el proceso interrumpido.
- Un proceso que se bloquea o termina antes del quantum libera la CPU y el siguiente parte con un quantum completo.

Round Robin es apropiativo **por tiempo**: el motor usa `quantum` para interrumpirlo.
La bandera interna `apropiativo` se mantiene en `False` porque habilita otra vía de
expropiación (por prioridad o tiempo restante), no el vencimiento del quantum.

### Procesos y quantum desde el menú

1. Ejecutar `python3 main.py` (o `python main.py`, según la instalación).
2. Elegir **8** para registrar un proceso indicando su identificador, tiempo de llegada
   (entero mayor o igual a cero) y ráfaga de CPU (entero mayor que cero). Los ID duplicados
   y los datos inválidos se rechazan.
3. Elegir **2** para consultar los procesos registrados, **1** para cargar el caso base, o
   **7** para cargar el caso de Round Robin de 10 procesos.
4. Elegir **9** para configurar el quantum de Round Robin; el valor se conserva mientras
   la aplicación esté abierta y debe ser un entero positivo. Su valor inicial es **4**.
5. Elegir **6** para ejecutar Round Robin. Se puede aceptar el quantum configurado con
   **Enter** o ingresar otro solo para esa ejecución. Se muestran la traza, el Gantt y las
   métricas.
6. Elegir **10** para volver a ver la traza y el informe de la última simulación. La opción
   informa si aún no se ha ejecutado ninguna simulación.

También se puede usar directamente:

```python
from simulador.algoritmos import ALGORITMOS
from simulador.modelos import CargaTrabajo
from simulador.motor import Simulador
from simulador.reportes import Reportero

carga = CargaTrabajo()
carga.cargar_caso_rr()
sim = Simulador(carga.especs, ALGORITMOS["RR"](quantum=3))
sim.ejecutar()
print(Reportero.informe(sim))
```

## Algoritmo con prioridades

**Convención del equipo: el valor numérico MÁS ALTO es la MAYOR prioridad.**

- **Algoritmo:** planificación por prioridades **no apropiativa** (`PlanificadorPrioridad`, menú opción 13).
- **Criterio:** se despacha el proceso listo de mayor prioridad.
- **Apropiación:** ninguna. Un proceso en CPU nunca es expropiado, aunque llegue otro de mayor prioridad. La prioridad solo decide quién se despacha cuando la CPU queda libre (por fin de ráfaga o por bloqueo).
- **Desempates:** llegada más temprana y luego menor identificador (orden natural, P2 < P10).
- **Traza:** al despachar se muestra `[prioridad=N]` del proceso seleccionado.
- **Inanición:** existe riesgo. Un proceso de baja prioridad puede esperar indefinidamente si siguen llegando procesos más prioritarios; en el caso de 10 procesos P5 (prioridad 1) espera 40 u.t. Al ser no apropiativo, además, uno de prioridad alta puede esperar a que termine uno largo de prioridad baja.
- **Envejecimiento:** no se implementó, para mantener el criterio puro y fácil de explicar. Una mitigación posible sería subir la prioridad de los procesos cada cierto tiempo en la cola de listos.
- **Demostración vs FIFO:** con `cargar_caso_prioridades()` (menú 11 y luego 13) FIFO termina P1, P3, P4, P5... y prioridades termina P1, P6, P9, P2, P4, P10... (P2 se bloquea y, al volver a Listos, compite por su prioridad).

## Casos predefinidos

Todos tienen 10 procesos y un proceso que se bloquea y vuelve a listos (`CargaTrabajo`):

| Método | Uso |
|---|---|
| `cargar_predefinida()` | Caso base de FIFO/SJF/SRTF (P3 se bloquea) |
| `cargar_caso_rr()` | Round Robin; probar con quantum 3 o 4 (P3 se bloquea) |
| `cargar_caso_prioridades()` | Prioridades 1..10 todas distintas y fuera del orden de llegada, por lo que el orden difiere de FIFO. P4 y P5 llegan juntos en t=3; P2 se bloquea |

También se pueden ingresar procesos a mano con `CargaTrabajo.agregar(...)`.

## Cómo integrar un algoritmo nuevo

1. Crear la clase en `simulador/algoritmos/` heredando de `Planificador`:
   - `seleccionar(listos)` devuelve el próximo proceso de la cola.
   - `apropiativo = True` y `debe_expropiar(en_ejecucion, listos)` si expropia por tiempo restante (SRTF).
   - `quantum` para Round Robin.
2. Registrarla en `ALGORITMOS` (`simulador/algoritmos/__init__.py`).
3. Conectarla en el menú (`simulador/consola.py`).
4. Agregar pruebas en `tests/`.

Contrato del motor: `Simulador(especs, planificador).ejecutar()` y luego `Reportero.informe(sim)`.

## Pruebas

- `tests/test_regresion.py`: FIFO, SJF y SRTF con el caso predefinido (promedios y salida completa).
- `tests/test_motor.py`: espera sin bloqueo, ciclo de estados, métricas, Gantt y quantum.
- `tests/test_carga.py` y `tests/test_casos.py`: validación del ingreso de procesos y de los casos de 10 procesos.
- `tests/test_round_robin.py`: validación del quantum, rotación, llegadas, E/S, métricas y casos límite de RR.
- `tests/test_consola_rr.py`: carga, quantum, registro de procesos y última simulación del menú.
- `tests/test_prioridad.py`: contrato, desempates, orden distinto a FIFO, bloqueo y métricas (resultados calculados a mano, por Thomas).
- `tests/test_invariantes.py`: propiedades que cumplen todos los algoritmos registrados (por Thomas).

## Evidencias

`evidencias/` contiene, para los tres casos de 10 procesos, un archivo por algoritmo (FIFO, SJF, SRTF, RR con quantum 3 y 4, y prioridades) con la traza, el Gantt, la tabla y los promedios, más `evidencias/resumen.md` con la comparación y el bloqueo que vuelve a Listos. Se regeneran con `python3 evidencias/generar_evidencias.py`.

## Estado de la integración

- [x] FIFO, SJF, SRTF
- [x] Motor con quantum, espera corregida y prioridad en el modelo
- [x] Round Robin (algoritmo, registro, menú con quantum configurable y pruebas)
- [x] Prioridades (algoritmo no apropiativo, registro, menú y pruebas)
- [x] Menú: registrar procesos y configurar el quantum de Round Robin
- [x] Menú: ver última simulación

## Decisión de lenguaje

Se eligió Python por su legibilidad: las listas nativas modelan las colas directamente, la
programación orientada a objetos es limpia (`dataclass` inmutable para las especificaciones y
`ABC` para el patrón Strategy), la simulación necesita pocos ticks y solo se usan bibliotecas estándar.
