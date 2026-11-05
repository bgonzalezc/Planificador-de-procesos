# Evidencias de funcionamiento

Generado con el simulador (`python3 main.py`, opciones 1, 7 y 11 para cargar casos y 3 a 6 y 13 para ejecutar). Reproducible: los casos son fijos.

## Resumen de promedios

| Algoritmo | Caso | Espera | Retorno | Respuesta |
|---|---|---|---|---|
| FIFO | `cargar_predefinida` | 19.20 | 24.50 | 16.80 |
| SJF | `cargar_predefinida` | 13.70 | 19.00 | 13.70 |
| SRTF | `cargar_predefinida` | 12.10 | 17.40 | 9.50 |
| Round Robin (quantum 3) | `cargar_caso_rr` | 31.10 | 37.40 | 10.50 |
| Round Robin (quantum 4) | `cargar_caso_rr` | 31.30 | 37.60 | 13.20 |
| Prioridades apropiativo | `cargar_caso_prioridades` | 15.10 | 20.20 | 11.50 |
| FIFO sobre el caso de prioridades (comparación) | `cargar_caso_prioridades` | 20.00 | 25.10 | 16.50 |

## FIFO

Caso: `cargar_predefinida`. Orden de finalización: P1, P2, P4, P5, P6, P7, P8, P9, P10, P3

Bloqueo y retorno a Listos:

- `| Eventos al final : P3 solicita E/S (Ejecución -> Bloqueado) por 4 u.; vuelve a Listo en t=19`
- `| Eventos al inicio: P3 termina E/S (Bloqueado -> Listo)`

```
+------------------------+------------+---------+---------------+------+------------------+
|           P1           |     P2     |    P3   |       P4      |  P5  |        P6        |
+------------------------+------------+---------+---------------+------+------------------+
0                        8            12        15              20     22                 28
+---------+---------------------+----+------------+------------------+
|    P7   |          P8         | P9 |    P10     |        P3        |
+---------+---------------------+----+------------+------------------+
28        31                    38   39           43                 49

ID    Llegada  Ráfaga  Inicio   Fin  Espera  Retorno  Respuesta
---------------------------------------------------------------
P1          0       8       0     8       0        8          0
P2          1       4       8    12       7       11          7
P3          2       9      12    49      34       47         10
P4          3       5      15    20      12       17         12
P5          4       2      20    22      16       18         16
P6          5       6      22    28      17       23         17
P7          6       3      28    31      22       25         22
P8          7       7      31    38      24       31         24
P9          8       1      38    39      30       31         30
P10         9       4      39    43      30       34         30
```

## SJF

Caso: `cargar_predefinida`. Orden de finalización: P1, P9, P5, P7, P2, P10, P4, P6, P8, P3

Bloqueo y retorno a Listos:

- `| Eventos al final : P3 solicita E/S (Ejecución -> Bloqueado) por 4 u.; vuelve a Listo en t=47`
- `| Eventos al inicio: P3 termina E/S (Bloqueado -> Listo); P3 despachado (Listo -> Ejecución)`

```
+------------------------+----+------+---------+------------+------------+---------------+
|           P1           | P9 |  P5  |    P7   |     P2     |    P10     |       P4      |
+------------------------+----+------+---------+------------+------------+---------------+
0                        8    9      11        14           18           22              27
+------------------+---------------------+---------+------------+------------------+
|        P6        |          P8         |    P3   |     --     |        P3        |
+------------------+---------------------+---------+------------+------------------+
27                 33                    40        43           47                 53

ID    Llegada  Ráfaga  Inicio   Fin  Espera  Retorno  Respuesta
---------------------------------------------------------------
P1          0       8       0     8       0        8          0
P2          1       4      14    18      13       17         13
P3          2       9      40    53      38       51         38
P4          3       5      22    27      19       24         19
P5          4       2       9    11       5        7          5
P6          5       6      27    33      22       28         22
P7          6       3      11    14       5        8          5
P8          7       7      33    40      26       33         26
P9          8       1       8     9       0        1          0
P10         9       4      18    22       9       13          9
```

## SRTF

Caso: `cargar_predefinida`. Orden de finalización: P2, P5, P9, P7, P10, P4, P6, P1, P8, P3

Bloqueo y retorno a Listos:

- `| Eventos al final : P3 solicita E/S (Ejecución -> Bloqueado) por 4 u.; vuelve a Listo en t=47`
- `| Eventos al inicio: P3 termina E/S (Bloqueado -> Listo); P3 despachado (Listo -> Ejecución)`

```
+----+------------+------+----+----+------+------------+---------------+------------------+
| P1 |     P2     |  P5  | P7 | P9 |  P7  |    P10     |       P4      |        P6        |
+----+------------+------+----+----+------+------------+---------------+------------------+
0    1            5      7    8    9      11           15              20                 26
+---------------------+---------------------+---------+------------+------------------+
|          P1         |          P8         |    P3   |     --     |        P3        |
+---------------------+---------------------+---------+------------+------------------+
26                    33                    40        43           47                 53

ID    Llegada  Ráfaga  Inicio   Fin  Espera  Retorno  Respuesta
---------------------------------------------------------------
P1          0       8       0    33      25       33          0
P2          1       4       1     5       0        4          0
P3          2       9      40    53      38       51         38
P4          3       5      15    20      12       17         12
P5          4       2       5     7       1        3          1
P6          5       6      20    26      15       21         15
P7          6       3       7    11       2        5          1
P8          7       7      33    40      26       33         26
P9          8       1       8     9       0        1          0
P10         9       4      11    15       2        6          2
```

## Round Robin (quantum 3)

Caso: `cargar_caso_rr`. Orden de finalización: P4, P2, P8, P5, P6, P10, P3, P1, P7, P9

Bloqueo y retorno a Listos:

- `| Eventos al final : P3 solicita E/S (Ejecución -> Bloqueado) por 4 u.; vuelve a Listo en t=13`
- `| Eventos al inicio: P3 termina E/S (Bloqueado -> Listo)`

```
+---------+---------+---------+---------+---------+---------+---------+------+---------+------+
|    P1   |    P2   |    P3   |    P4   |    P1   |    P5   |    P6   |  P2  |    P7   |  P8  |
+---------+---------+---------+---------+---------+---------+---------+------+---------+------+
0         3         6         9         12        15        18        21     23        26     28
+---------+---------+---------+---------+---------+----+---------+---------+------+------+----+
|    P9   |   P10   |    P3   |    P1   |    P5   | P6 |    P7   |    P9   | P10  |  P3  | P1 |
+---------+---------+---------+---------+---------+----+---------+---------+------+------+----+
28        31        34        37        40        43   44        47        50     52     54   55
+---------+----+
|    P7   | P9 |
+---------+----+
55        58   59

ID    Llegada  Ráfaga  Inicio   Fin  Espera  Retorno  Respuesta
---------------------------------------------------------------
P1          0      10       0    55      45       55          0
P2          1       5       3    23      17       22          2
P3          2       8       6    54      40       52          4
P4          3       3       9    12       6        9          6
P5          4       6      15    43      33       39         11
P6          6       4      18    44      34       38         12
P7          7       9      23    58      42       51         16
P8          9       2      26    28      17       19         17
P9         10       7      28    59      42       49         18
P10        12       5      31    52      35       40         19
```

## Round Robin (quantum 4)

Caso: `cargar_caso_rr`. Orden de finalización: P4, P6, P2, P8, P5, P1, P9, P10, P3, P7

Bloqueo y retorno a Listos:

- `| Eventos al final : P3 solicita E/S (Ejecución -> Bloqueado) por 4 u.; vuelve a Listo en t=15`
- `| Eventos al inicio: P3 termina E/S (Bloqueado -> Listo)`

```
+------------+------------+---------+---------+------------+------------+------------+
|     P1     |     P2     |    P3   |    P4   |     P5     |     P1     |     P6     |
+------------+------------+---------+---------+------------+------------+------------+
0            4            8         11        14           18           22           26
+------------+----+------+------------+------------+------------+------+------+------------+
|     P7     | P2 |  P8  |     P9     |    P10     |     P3     |  P5  |  P1  |     P7     |
+------------+----+------+------------+------------+------------+------+------+------------+
26           30   31     33           37           41           45     47     49           53
+---------+-----+----+----+
|    P9   | P10 | P3 | P7 |
+---------+-----+----+----+
53        56    57   58   59

ID    Llegada  Ráfaga  Inicio   Fin  Espera  Retorno  Respuesta
---------------------------------------------------------------
P1          0      10       0    49      39       49          0
P2          1       5       4    31      25       30          3
P3          2       8       8    58      44       56          6
P4          3       3      11    14       8       11          8
P5          4       6      14    47      37       43         10
P6          6       4      22    26      16       20         16
P7          7       9      26    59      43       52         19
P8          9       2      31    33      22       24         22
P9         10       7      33    56      39       46         23
P10        12       5      37    57      40       45         25
```

## Prioridades apropiativo

Caso: `cargar_caso_prioridades`. Orden de finalización: P6, P2, P9, P4, P10, P7, P1, P8, P3, P5

Bloqueo y retorno a Listos:

- `| Eventos al final : P2 solicita E/S (Ejecución -> Bloqueado) por 3 u.; vuelve a Listo en t=6`
- `| Eventos al inicio: P7 llega (Nuevo -> Listo); P2 termina E/S (Bloqueado -> Listo)`

```
+----+------+------+------+------+------------------+----+---------+---------------------+
| P1 |  P2  |  P4  |  P6  |  P2  |        P9        | P4 |   P10   |          P7         |
+----+------+------+------+------+------------------+----+---------+---------------------+
0    1      3      5      7      9                  15   16        19                    26
+---------------+------------+------------------------+---------------+
|       P1      |     P8     |           P3           |       P5      |
+---------------+------------+------------------------+---------------+
26              31           35                       43              48

ID    Llegada  Ráfaga  Inicio   Fin  Espera  Retorno  Respuesta
---------------------------------------------------------------
P1          0       6       0    31      25       31          0
P2          1       4       1     9       1        8          0
P3          2       8      35    43      33       41         33
P4          3       3       3    16      10       13          0
P5          3       5      43    48      40       45         40
P6          5       2       5     7       0        2          0
P7          6       7      19    26      13       20         13
P8          8       4      31    35      23       27         23
P9          9       6       9    15       0        6          0
P10        10       3      16    19       6        9          6
```

## FIFO sobre el caso de prioridades (comparación)

Caso: `cargar_caso_prioridades`. Orden de finalización: P1, P3, P4, P5, P6, P7, P8, P9, P10, P2

Bloqueo y retorno a Listos:

- `| Eventos al final : P2 solicita E/S (Ejecución -> Bloqueado) por 3 u.; vuelve a Listo en t=11`
- `| Eventos al inicio: P2 termina E/S (Bloqueado -> Listo)`

```
+------------------+------+------------------------+---------+---------------+------+
|        P1        |  P2  |           P3           |    P4   |       P5      |  P6  |
+------------------+------+------------------------+---------+---------------+------+
0                  6      8                        16        19              24     26
+---------------------+------------+------------------+---------+------+
|          P7         |     P8     |        P9        |   P10   |  P2  |
+---------------------+------------+------------------+---------+------+
26                    33           37                 43        46     48

ID    Llegada  Ráfaga  Inicio   Fin  Espera  Retorno  Respuesta
---------------------------------------------------------------
P1          0       6       0     6       0        6          0
P2          1       4       6    48      40       47          5
P3          2       8       8    16       6       14          6
P4          3       3      16    19      13       16         13
P5          3       5      19    24      16       21         16
P6          5       2      24    26      19       21         19
P7          6       7      26    33      20       27         20
P8          8       4      33    37      25       29         25
P9          9       6      37    43      28       34         28
P10        10       3      43    46      33       36         33
```
