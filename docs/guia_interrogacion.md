# Guía de preguntas y respuestas para la interrogación

Basada en el código real (`simulador/`). Léela con el código abierto.

## 1. Flujo general

**¿Cómo funciona la simulación?**
`Simulador.ejecutar()` (en `motor.py`) avanza el reloj de a 1 unidad (tick) hasta que todos los procesos finalizan. El simulador crea objetos `Proceso` nuevos desde las `EspecProceso` inmutables, así que la carga original no se modifica.

**¿Qué hace en cada tick, y en qué orden?**
1. **Admisión:** entran a Listos las llegadas (`t == llegada`) y los que terminan E/S (`t == t_despertar`). Si entran varios juntos se ordenan por llegada y luego ID.
2. **Fin de quantum** (si el algoritmo tiene `quantum`) y **expropiación** (si es apropiativo).
3. **Despacho:** si la CPU está libre, `planificador.seleccionar(cola_listos)` elige.
4. **Ejecución** de 1 unidad (o CPU ociosa) y contabilidad de espera y bloqueo.
5. **Fin de tick:** si `restante == 0` finaliza; si le toca un evento de E/S, pasa a Bloqueado.

**¿Por qué ese orden?** La admisión va antes del fin de quantum para que quien llega en ese instante quede en la cola *antes* del proceso interrumpido. Va antes de expropiar para que el recién llegado pueda competir por la CPU en el mismo tick.

## 2. Estructuras y estados

**¿Qué listas hay?** `cola_listos` (se agrega al final), `cola_bloqueados` y `cpu` (un solo proceso). Más `finalizados` y `linea_tiempo` (un pid o `None` por tick).

**¿Qué estados hay y qué transiciones?**
Nuevo → Listo → Ejecución → Finalizado. Desde Ejecución también a Bloqueado (E/S) y de ahí a Listo. Ejecución → Listo cuando se expropia o termina el quantum.

**¿Cómo se modela la E/S?** `eventos_es = ((n, d), ...)`: tras ejecutar `n` unidades de CPU, el proceso se bloquea `d` unidades. Se despierta en `t + 1 + d`. Cada evento se consume al usarse.

**¿Por qué `EspecProceso` es inmutable?** Es `dataclass(frozen=True)`: sirve para simular varias veces la misma carga sin contaminarla.

## 3. Métricas

- **Retorno** = fin − llegada.
- **Respuesta** = primer inicio − llegada.
- **Espera** = ticks acumulados en la cola de Listos (`t_espera`). **No** incluye el bloqueo.
- **Bloqueado** se acumula aparte (`t_bloqueado`).
- Identidad que se cumple siempre: **Retorno = Ráfaga + Espera + Bloqueado**.

**¿Por qué no cuenta el bloqueo como espera?** Porque el PDF define la espera como el tiempo en la lista de listos. Bloqueado no es esperar CPU, es esperar un dispositivo.

**¿Qué cambió respecto de la etapa 2?** Antes `espera = retorno − ráfaga`, que incluía el bloqueo. Solo cambia P3 (bloqueo de 4 u.), y por eso los promedios de espera bajaron 0,4.

## 4. Algoritmos

| Algoritmo | Criterio | Apropiativo | Clave de desempate |
|---|---|---|---|
| FIFO | Orden de entrada a la cola | No | La cola |
| SJF | Menor ráfaga total | No | llegada, ID |
| SRTF | Menor tiempo restante | Sí | llegada, ID |
| Round Robin | Cabeza de la cola, con quantum | Por tiempo | La cola |
| Prioridades | Mayor valor de prioridad | No | llegada, ID |

**SRTF vs SJF:** SJF compara la ráfaga total y nunca interrumpe. SRTF compara el restante y expropia si alguien en la cola tiene un restante *estrictamente menor*.

## 5. Round Robin y quantum

**¿Cómo se implementa?** `PlanificadorRoundRobin` solo devuelve `listos[0]` y expone `quantum`. El **motor** lleva `uso_quantum` y, al llegar al quantum, devuelve el proceso al final de la cola.

**Reglas:**
- El quantum debe ser un entero mayor que 0; si no, `ValueError`.
- Un proceso ejecuta como máximo `quantum` ticks seguidos.
- Si al vencer no hay nadie en Listos, sigue otro quantum sin interrupción.
- Si el proceso termina o se bloquea antes, libera la CPU y el siguiente parte con quantum completo (`uso_quantum = 0` al despachar).
- **Llegada simultánea con el vencimiento:** el que llega entra a la cola *antes* que el interrumpido (convención habitual).

**¿Por qué `apropiativo` es False en RR?** Esa bandera habilita la expropiación por comparación (`debe_expropiar`). RR se expropia por tiempo, y eso lo hace el motor mirando `quantum`.

**Capacidad de respuesta:** con RR la respuesta es baja (los procesos empiezan pronto), pero espera y retorno suben por la rotación. En los datos: RR q=3 da respuesta 10,50 contra 16,80 de FIFO, pero espera 31,10 contra 19,20.

**Efecto del quantum:** uno grande tiende a FIFO; uno chico mejora la respuesta pero multiplica las rotaciones (aquí no hay costo de cambio de contexto, pero en un sistema real sí).

## 6. Prioridades

- **Variante:** **no apropiativa**. **Mayor valor = mayor prioridad.**
- **Desempate:** llegada más temprana y luego ID menor.
- **No expropia nunca:** aunque llegue un proceso más prioritario, espera a que la CPU quede libre (fin de ráfaga o bloqueo). Es más simple y sin cambios de contexto por prioridad; el costo es que uno urgente puede esperar a uno largo de baja prioridad.
- **Muestra la prioridad:** la traza agrega `[prioridad=N]` al despachar (bandera `muestra_prioridad`).
- **Distinto de FIFO:** en el caso de 10 procesos FIFO termina P1, P3, P4… y prioridades termina P1, P6, P9, P2…

**Inanición:** un proceso de baja prioridad puede no ejecutarse nunca si siguen llegando procesos más prioritarios. En el caso de ejemplo P5 (prioridad 1) espera 40 u.t.

**Envejecimiento:** no se implementó para mantener el criterio puro y explicable. La mitigación sería subir la prioridad de los procesos según el tiempo que llevan en Listos.

## 7. Casos de prueba

- **Caso base (`cargar_predefinida`):** 10 procesos, P3 se bloquea.
- **Caso RR (`cargar_caso_rr`):** 10 procesos, P3 se bloquea; probar con quantum 3 y 4.
- **Caso prioridades (`cargar_caso_prioridades`):** prioridades 1 a 10 todas distintas; P4 y P5 llegan juntos en t=3 (prueba el desempate por prioridad); P2 se bloquea.
- Evidencias completas en `evidencias/` (generadas con `python3 evidencias/generar_evidencias.py`).

## 8. Decisión de lenguaje y diseño

- **Python:** legible, listas nativas modelan las colas, POO limpia y solo biblioteca estándar.
- **Patrón Strategy:** `Planificador` es la interfaz; cada algoritmo es una clase. Para agregar uno se crea la clase y se registra en `ALGORITMOS`. El motor y el menú no cambian.
- **Separación:** modelos, motor, algoritmos, reportes y consola en módulos distintos.

## 9. Preguntas trampa

**¿Qué pasa si llega un proceso justo cuando termina otro?** No hay hueco en la CPU. Un proceso que ejecuta su última unidad en el tick `t` finaliza al final de ese tick (fin = t+1). Si otro llega en `t+1`, la admisión lo mete a Listos al inicio de ese tick y el despacho lo pone en CPU en el mismo tick. Verificado: P1 (ll=0, ráfaga 2) y P2 (ll=2) dan Gantt `P1 P1 P2`, sin `--`.

**¿Qué pasa con la CPU si nadie está listo?** Queda ociosa (`IDLE`) y el Gantt marca `--`.

**¿Dónde se ve que un bloqueado vuelve a Listos?** En la traza: `P3 solicita E/S (Ejecución -> Bloqueado)` y más adelante `P3 termina E/S (Bloqueado -> Listo)`.

**¿Cómo sé que las métricas están bien?** Los tests verifican `Retorno = Ráfaga + Espera + Bloqueado`, y que los ticks de CPU del Gantt suman las ráfagas. Comprobamos 18 combinaciones de algoritmo y caso.

**¿Qué algoritmo es el más eficiente?** Depende de la métrica. En el caso base SRTF tiene los mejores promedios (espera 12,10; retorno 17,40; respuesta 9,50), pero puede postergar procesos largos. RR es más equitativo y responde mejor, pero tiene mayor espera. Prioridades favorece a los importantes a costa de la inanición. No existe un único mejor.

## 10. Para repasar antes

1. Los 5 pasos del tick y por qué van en ese orden.
2. Dónde se cuenta el quantum (motor) y dónde se elige (planificador).
3. Cómo se calcula la espera y por qué excluye el bloqueo.
4. Cuándo expropia SRTF (restante estrictamente menor) y por qué prioridades no expropia.
5. Ejecutar a mano el menú: opciones 7, 9, 6 y luego 11 y 13.
