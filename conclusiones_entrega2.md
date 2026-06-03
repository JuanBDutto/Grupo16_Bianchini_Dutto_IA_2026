IA UTILIZADA: COPILOT

Comenzamos hablando de los dominios. En este caso, se nota una clara diferencia en como pensamos los dominios. Por nuestra parte, todos los módulos comparten el mismo dominio de celdas válidas y después, las restricciones determinan las posiciones permitidas para cada tipo de módulo. Mientras que la IA, realiza un filtrado previo de los dominios, donde le asigna a cada módulo aquellas celdas que pueden cumplir con las restricciones, lo que reduce mucho el espacio de búsqueda.

Con respecto a las restricciones y validaciones, se pueden ver diferentes enfoques: nuestro grupo define las restricciones de una forma más directa. Mientras que la IA divide una gran parte de la lógica en funciones auxiliares e incluso utiliza expresiones lambda para construir las restricciones. Además, agrega validaciones previas que le permiten detectar casos sin solución antes de que se ejecute el algoritmo de búsqueda.

A la hora de analizar la estructura general del código, una vez que encontramos la solución, nosotros solamente transformamos los datos al formato que se solicita y los devolvemos. En cambio, la IA usa algunas estructuras adicionales, como diccionarios para almacenar información de los módulos y una tabla de prioridades para ordenar el resultado final.

Finalmente, queríamos aclarar que ambos archivos pasan todos los tests. Si bien, la IA incluye algunas optimizaciones y verificaciones adicionales, los tiempos de ejecución de los tests fueron bastante parecidos en ambos casos, por lo que no existen tantas diferencias de rendimiento en ellos.
