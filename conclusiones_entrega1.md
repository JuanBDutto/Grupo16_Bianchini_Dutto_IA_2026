IA UTILIZADA: COPILOT

Comenzamos hablando del estado. En este caso, tanto nosotros como la IA tuvimos un pensamiento muy parecido. La diferencia radica en que nuestro grupo utilizamos variables globales, mientras que la IA lo hizo, por decir de alguna manera, “mas limpio” con atributos de las clase. Además, la IA ordeno las tuplas de las muestras.

Con respecto a las acciones, nosotros decidimos separar los movimientos en varias funciones, como por ejemplo, recolectar – mover_rover, provocando a nuestro parecer, que el código pueda leerse mejor. En cambio, la IA junto toda la lógica directamente en el método de actions, evitando llar a tantas funciones extras y haciendo que el programa pueda correr más fluido.

Si hablamos de la heurística, nuestro grupo calcula la distancia Manhattan a la muestra mas cercana y le sumamos los cotos fijos. Mientras que la IA, armo un árbol para conectar todos los puntos pendientes, e incluso calcula si la batería va a alcanzar.

Finalmente, queríamos aclarar que en ambos archivos pasan todos los tests, con la diferencia de que el que hicimos nosotros lo hace en un rango de entre 14 a 16 segundos, mientras que la IA lo hace entre 4 a 6 segundos. Esto se debe a una heurística mas “completa” que tiene la IA, y como fue mencionado anteriormente, el hecho de tener funciones extra para cada acción del rover, hace que los tests se corran más lentos
