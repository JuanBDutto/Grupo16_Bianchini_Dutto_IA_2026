IA UTILIZADA: COPILOT

Comenzamos hablando del estado. En este caso, tanto nosotros como la IA modelamos el estado de una forma bastante similar, incluyendo la posicion del rover, la bateria disponible, el taladro equipado, las muestras restantes y la carga actual. La diferencia radica en que nosotros utilizamos variables globales para almacenar información del entorno, mientras que la IA lo hizo, por decir de alguna manera, “mas limpio” con atributos de las clase. Además, la IA ordeno las tuplas de las muestras.

Con respecto a las acciones, nosotros decidimos separar los movimientos en varias funciones, como por ejemplo, recolectar_muestra o mover_rover, provocando a nuestro parecer, que el código pueda leerse mejor. En cambio, la IA junto toda la lógica directamente en el método de actions, evitando llamar a tantas funciones extras y haciendo que el programa pueda correr más fluido.

Si hablamos de la heurística, nuestro grupo calcula la distancia Manhattan a la muestra mas cercana y le sumamos los costos fijos. Mientras que la IA, armo un árbol de expansión mínima (MST) que tiene en cuenta todas las muestras pendientes, los cambios de taladro e incluso calcula si la batería va a alcanzar.

Finalmente, queríamos aclarar que en ambos archivos pasan todos los tests, con la diferencia de que el que hicimos nosotros lo hace en un rango de entre 14 a 16 segundos, mientras que la IA lo hace entre 4 a 6 segundos. Suponemos que esto es así debido a que su heurística reduce mucho mas la cantidad de estados que explora el algoritmo A* y como fue mencionado anteriormente, el hecho de tener funciones extra para cada acción del rover, hace que los tests se corran más lentos
