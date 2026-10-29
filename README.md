        Simulador de planificación de procesos de corto plazos
Simulado por consola en python03

FIFO, SJF (no apropiativo) y SRTF (Apropiativo) incluye además un estado de bloqueo por eventos de E/S

Menú (ConsoleApp):
1) Carga de casos predefinidos (incluye el bloqueo)
2) Ver los procesos
3) FIFO
4) SJF
5) SRTF
6) Salida de consola

Se ocupan 6 clases.
ProcessSpec - copia inalterable del proceso 

Process - Procceso T_restante, Estado, T_inicio , T_finzalizacion y métricas

Workload - Guarda la carga y caso predifinido

Scheduler - Algoritmo por clase

Simulator - Reloj, cola de listos y bloqueados y cpu

Reporer - encargado de Gantt ASCII, tabla de resultados y promedios

ConsoleApp - el menú interactivo (mencionado anteriormente)

Se eligió Pyehon por la legilibilidad de este, las listas nativas modelan las colas diractemente
, la programación orientada a objetos (POO) e smás limpia porque dataclass es inmutable y ABC paara el patrón strategy
se ocupan pocaoc ticks y ademas solo se ocupan biblitecas estándar
