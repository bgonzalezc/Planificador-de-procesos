# Evidencias de funcionamiento

Generado con `python3 evidencias/generar_evidencias.py`.
Cada archivo `.txt` contiene la traza tick a tick, el Gantt, la tabla de métricas y los promedios, igual que en el menú.

## Caso base (etapa 02), P3 se bloquea

| ID | Llegada | Ráfaga | Prioridad | E/S |
|---|---|---|---|---|
| P1 | 0 | 8 | 0 | - |
| P2 | 1 | 4 | 0 | - |
| P3 | 2 | 9 | 0 | tras 3 u. bloquea 4 u. |
| P4 | 3 | 5 | 0 | - |
| P5 | 4 | 2 | 0 | - |
| P6 | 5 | 6 | 0 | - |
| P7 | 6 | 3 | 0 | - |
| P8 | 7 | 7 | 0 | - |
| P9 | 8 | 1 | 0 | - |
| P10 | 9 | 4 | 0 | - |

| Algoritmo | Espera prom. | Retorno prom. | Respuesta prom. | Archivo |
|---|---|---|---|---|
| FIFO | 19.20 | 24.50 | 16.80 | `caso_base/FIFO.txt` |
| SJF | 13.70 | 19.00 | 13.70 | `caso_base/SJF.txt` |
| SRTF | 12.10 | 17.40 | 9.50 | `caso_base/SRTF.txt` |
| RR_q3 | 24.80 | 30.10 | 10.40 | `caso_base/RR_q3.txt` |
| RR_q4 | 22.80 | 28.10 | 13.20 | `caso_base/RR_q4.txt` |
| PRIORIDAD | 20.50 | 25.80 | 20.40 | `caso_base/PRIORIDAD.txt` |

## Caso Round Robin, P3 se bloquea

| ID | Llegada | Ráfaga | Prioridad | E/S |
|---|---|---|---|---|
| P1 | 0 | 10 | 0 | - |
| P2 | 1 | 5 | 0 | - |
| P3 | 2 | 8 | 0 | tras 3 u. bloquea 4 u. |
| P4 | 3 | 3 | 0 | - |
| P5 | 4 | 6 | 0 | - |
| P6 | 6 | 4 | 0 | - |
| P7 | 7 | 9 | 0 | - |
| P8 | 9 | 2 | 0 | - |
| P9 | 10 | 7 | 0 | - |
| P10 | 12 | 5 | 0 | - |

| Algoritmo | Espera prom. | Retorno prom. | Respuesta prom. | Archivo |
|---|---|---|---|---|
| FIFO | 23.10 | 29.40 | 19.90 | `caso_rr/FIFO.txt` |
| SJF | 18.20 | 24.50 | 17.70 | `caso_rr/SJF.txt` |
| SRTF | 15.70 | 22.00 | 11.70 | `caso_rr/SRTF.txt` |
| RR_q3 | 31.10 | 37.40 | 10.50 | `caso_rr/RR_q3.txt` |
| RR_q4 | 31.30 | 37.60 | 13.20 | `caso_rr/RR_q4.txt` |
| PRIORIDAD | 22.90 | 29.20 | 22.40 | `caso_rr/PRIORIDAD.txt` |

## Caso prioridades (1..10, mayor valor = mayor prioridad), P2 se bloquea

| ID | Llegada | Ráfaga | Prioridad | E/S |
|---|---|---|---|---|
| P1 | 0 | 6 | 4 | - |
| P2 | 1 | 4 | 9 | tras 2 u. bloquea 3 u. |
| P3 | 2 | 8 | 2 | - |
| P4 | 3 | 3 | 7 | - |
| P5 | 3 | 5 | 1 | - |
| P6 | 5 | 2 | 10 | - |
| P7 | 6 | 7 | 5 | - |
| P8 | 8 | 4 | 3 | - |
| P9 | 9 | 6 | 8 | - |
| P10 | 10 | 3 | 6 | - |

| Algoritmo | Espera prom. | Retorno prom. | Respuesta prom. | Archivo |
|---|---|---|---|---|
| FIFO | 20.00 | 25.10 | 16.50 | `caso_prioridades/FIFO.txt` |
| SJF | 13.10 | 18.20 | 13.00 | `caso_prioridades/SJF.txt` |
| SRTF | 12.60 | 17.70 | 11.00 | `caso_prioridades/SRTF.txt` |
| RR_q3 | 22.80 | 27.90 | 10.30 | `caso_prioridades/RR_q3.txt` |
| RR_q4 | 23.20 | 28.30 | 11.70 | `caso_prioridades/RR_q4.txt` |
| PRIORIDAD | 15.20 | 20.30 | 14.90 | `caso_prioridades/PRIORIDAD.txt` |

## Proceso bloqueado que vuelve a la lista de listos

Extracto de `caso_base/FIFO.txt`: P3 solicita E/S, pasa a la cola de bloqueados y, al terminar, vuelve a la cola de listos.

```
t= 14 -> 15  | CPU: P3 (restante=6)
            | Listos: [P4, P5, P6, P7, P8, P9, P10]   Bloqueados: []
            | Eventos al final : P3 solicita E/S (Ejecución -> Bloqueado) por 4 u.; vuelve a Listo en t=19
t= 15 -> 16  | CPU: P4 (restante=4)
            | Listos: [P5, P6, P7, P8, P9, P10]   Bloqueados: [P3(sale en t=19)]
            | Eventos al inicio: P4 despachado (Listo -> Ejecución)
t= 16 -> 17  | CPU: P4 (restante=3)
            | Listos: [P5, P6, P7, P8, P9, P10]   Bloqueados: [P3(sale en t=19)]
t= 17 -> 18  | CPU: P4 (restante=2)
            | Listos: [P5, P6, P7, P8, P9, P10]   Bloqueados: [P3(sale en t=19)]
t= 18 -> 19  | CPU: P4 (restante=1)
            | Listos: [P5, P6, P7, P8, P9, P10]   Bloqueados: [P3(sale en t=19)]
t= 19 -> 20  | CPU: P4 (restante=0)
            | Listos: [P5, P6, P7, P8, P9, P10, P3]   Bloqueados: []
            | Eventos al inicio: P3 termina E/S (Bloqueado -> Listo)
```
