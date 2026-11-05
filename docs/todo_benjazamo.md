1. Preparar la arquitectura
- [x] Separar el código de main.py en módulos: Organizar modelos, motor, algoritmos, reportes y menú sin alterar el funcionamiento actual.
- [x] Definir las interfaces de integración: Establecer cómo los módulos de Round Robin, prioridades y menú se comunicarán con el simulador.
- [x] Comprobar los algoritmos existentes: Verificar que FIFO, SJF y SRTF sigan funcionando después de separar los archivos.

2. Modificar el motor de simulación
- [x] Agregar prioridad al modelo de procesos: Incorporar priority en ProcessSpec y Process, manteniendo los eventos de E/S.
- [x] Corregir el tiempo de espera: Contabilizar únicamente el tiempo en la cola de listos, sin incluir el tiempo bloqueado.
- [x] Adaptar el motor para gestionar el quantum: Permitir que Round Robin interrumpa un proceso y lo reincorpore a la cola cuando corresponda.
- [x] Verificar los cambios de estado: Comprobar Nuevo → Listo → Ejecución → Bloqueado → Listo → Finalizado.
- [x] Verificar las métricas y el Gantt: Comprobar inicio, finalización, espera, retorno, respuesta y línea temporal.

3. Integrar los trabajos de tus compañeros
- [x] Integrar Round Robin de José Luna: Algoritmo registrado, menú con quantum configurable y pruebas de rotación, llegadas, E/S y métricas.
- [x] Integrar prioridades de Francisco: Conectar su planificador y verificar selección y desempates.
- [x] Integrar el menú del otro Benja: Conectar los cinco algoritmos, ingreso de procesos y visualización de resultados.
- [x] Resolver errores de integración: Revisar imports, interfaces, estados compartidos y posibles regresiones.

4. Validación final
- [x] Revisar las pruebas de Thomas: Corregir los fallos del motor y de integración que detecten las pruebas.
- [x] Validar los cinco algoritmos: Comprobar FIFO, SJF, SRTF, RR y prioridades con casos conocidos.
- [ ] Revisar y aprobar los pull requests: Integrar los cambios verificados en la rama principal.
- [ ] Preparar tu explicación técnica: Dominar el motor, las estructuras, los estados, las métricas y las decisiones de diseño.
