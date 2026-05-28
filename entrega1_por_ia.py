"""Solucion AI para el planificador del rover Ares-1."""

from simpleai.search import SearchProblem, astar


MAX_BATERIA = 20
TIEMPOS = {
	"moverse": 1,
	"sobremarcha": 1,
	"equipar": 3,
	"recolectar": 2,
	"depositar": 1,
	"recargar": 4,
}

CONSUMOS = {
	"moverse": 1,
	"sobremarcha": 4,
	"equipar": 1,
	"recolectar": 3,
	"depositar": 1,
	"recargar": -10,
}


def _normalizar_posiciones(posiciones):
	return tuple(sorted(tuple(pos) for pos in posiciones))


def _distancia_movimiento(origen, destino):
	manhattan = abs(origen[0] - destino[0]) + abs(origen[1] - destino[1])
	return (manhattan + 1) // 2


def _costo_mst(puntos):
	if len(puntos) <= 1:
		return 0

	pendientes = set(puntos[1:])
	visitados = {puntos[0]}
	costo_total = 0

	while pendientes:
		mejor_costo = None
		mejor_punto = None
		for origen in visitados:
			for destino in pendientes:
				costo = _distancia_movimiento(origen, destino)
				if mejor_costo is None or costo < mejor_costo:
					mejor_costo = costo
					mejor_punto = destino
		visitados.add(mejor_punto)
		pendientes.remove(mejor_punto)
		costo_total += mejor_costo

	return costo_total


def _limites(rover_inicio, zonas_sombra, muestras_igneas, muestras_sedimentarias):
	posiciones = [tuple(rover_inicio)]
	posiciones.extend(tuple(pos) for pos in zonas_sombra)
	posiciones.extend(tuple(pos) for pos in muestras_igneas)
	posiciones.extend(tuple(pos) for pos in muestras_sedimentarias)
	filas = [pos[0] for pos in posiciones]
	columnas = [pos[1] for pos in posiciones]
	return min(filas), max(filas), min(columnas), max(columnas)


class AresRoverProblem(SearchProblem):
	def __init__(self, rover_inicio, bateria_inicial, zonas_sombra, muestras_igneas, muestras_sedimentarias):
		self.zonas_sombra = {tuple(pos) for pos in zonas_sombra}
		self.limites = _limites(rover_inicio, self.zonas_sombra, muestras_igneas, muestras_sedimentarias)
		estado_inicial = (tuple(rover_inicio), bateria_inicial, None, _normalizar_posiciones(muestras_igneas), _normalizar_posiciones(muestras_sedimentarias), 0)
		super().__init__(estado_inicial)

	def actions(self, state):
		posicion, bateria, taladro, muestras_igneas, muestras_sedimentarias, carga = state
		min_fila, max_fila, min_columna, max_columna = self.limites
		restantes = len(muestras_igneas) + len(muestras_sedimentarias)
		acciones = []

		if carga > 0 and bateria > 1 and (carga == 2 or restantes == 0):
			acciones.append(("depositar", None))

		if bateria < MAX_BATERIA and posicion not in self.zonas_sombra and (restantes > 0 or carga > 0):
			acciones.append(("recargar", None))

		if restantes > 0 and bateria > 1:
			if muestras_igneas and taladro != "termico":
				acciones.append(("equipar", "termico"))
			if muestras_sedimentarias and taladro != "percusion":
				acciones.append(("equipar", "percusion"))

		if bateria > 3 and carga < 2:
			if posicion in muestras_igneas and taladro == "termico":
				acciones.append(("recolectar", "ignea"))
			if posicion in muestras_sedimentarias and taladro == "percusion":
				acciones.append(("recolectar", "sedimentaria"))

		if bateria > 1:
			fila, columna = posicion
			movimientos = (
				("moverse", (fila + 1, columna)),
				("moverse", (fila - 1, columna)),
				("moverse", (fila, columna + 1)),
				("moverse", (fila, columna - 1)),
			)
			for accion, destino in movimientos:
				if min_fila <= destino[0] <= max_fila and min_columna <= destino[1] <= max_columna:
					acciones.append((accion, destino))

		if bateria > 4:
			fila, columna = posicion
			movimientos = (
				("sobremarcha", (fila + 2, columna)),
				("sobremarcha", (fila - 2, columna)),
				("sobremarcha", (fila, columna + 2)),
				("sobremarcha", (fila, columna - 2)),
			)
			for accion, destino in movimientos:
				if min_fila <= destino[0] <= max_fila and min_columna <= destino[1] <= max_columna:
					acciones.append((accion, destino))

		return tuple(acciones)

	def result(self, state, action):
		posicion, bateria, taladro, muestras_igneas, muestras_sedimentarias, carga = state
		tipo, parametro = action

		if tipo == "moverse":
			return (parametro, bateria - CONSUMOS[tipo], taladro, muestras_igneas, muestras_sedimentarias, carga)

		if tipo == "sobremarcha":
			return (parametro, bateria - CONSUMOS[tipo], taladro, muestras_igneas, muestras_sedimentarias, carga)

		if tipo == "equipar":
			return (posicion, bateria - CONSUMOS[tipo], parametro, muestras_igneas, muestras_sedimentarias, carga)

		if tipo == "recolectar":
			if parametro == "ignea":
				nuevas_igneas = tuple(muestra for muestra in muestras_igneas if muestra != posicion)
				return (posicion, bateria - CONSUMOS[tipo], taladro, nuevas_igneas, muestras_sedimentarias, carga + 1)

			nuevas_sedimentarias = tuple(muestra for muestra in muestras_sedimentarias if muestra != posicion)
			return (posicion, bateria - CONSUMOS[tipo], taladro, muestras_igneas, nuevas_sedimentarias, carga + 1)

		if tipo == "depositar":
			return (posicion, bateria - CONSUMOS[tipo], taladro, muestras_igneas, muestras_sedimentarias, 0)

		if tipo == "recargar":
			return (posicion, min(MAX_BATERIA, bateria - CONSUMOS[tipo]), taladro, muestras_igneas, muestras_sedimentarias, carga)

		raise ValueError(f"Accion desconocida: {action}")

	def is_goal(self, state):
		_, _, _, muestras_igneas, muestras_sedimentarias, carga = state
		return not muestras_igneas and not muestras_sedimentarias and carga == 0

	def cost(self, state1, action, state2):
		tipo, _ = action
		if tipo == "depositar":
			return TIEMPOS[tipo] * state1[5]
		return TIEMPOS[tipo]

	def heuristic(self, state):
		posicion, _, taladro, muestras_igneas, muestras_sedimentarias, carga = state
		restantes = list(muestras_igneas) + list(muestras_sedimentarias)
		if not restantes and carga == 0:
			return 0

		estimacion = 0
		nodos_movimiento = [posicion] + restantes
		estimacion += _costo_mst(nodos_movimiento)
		estimacion += 2 * len(restantes)
		estimacion += carga + len(restantes)

		tipos_restantes = 0
		if muestras_igneas:
			tipos_restantes += 1
		if muestras_sedimentarias:
			tipos_restantes += 1

		if tipos_restantes == 1:
			if muestras_igneas and taladro != "termico":
				estimacion += 3
			elif muestras_sedimentarias and taladro != "percusion":
				estimacion += 3
		elif tipos_restantes == 2:
			if taladro is None:
				estimacion += 6
			else:
				estimacion += 3

		bateria_necesaria = _costo_mst(nodos_movimiento) + 3 * len(restantes) + carga + len(restantes)
		if muestras_igneas and muestras_sedimentarias:
			bateria_necesaria += 2 if taladro is None else 1
		elif restantes:
			if (muestras_igneas and taladro != "termico") or (muestras_sedimentarias and taladro != "percusion"):
				bateria_necesaria += 1

		if bateria_necesaria > state[1]:
			estimacion += 4 * ((bateria_necesaria - state[1] + 9) // 10)

		return estimacion


def planear_rover(rover_inicio, bateria_inicial, zonas_sombra, muestras_igneas, muestras_sedimentarias):
	problema = AresRoverProblem(
		rover_inicio=rover_inicio,
		bateria_inicial=bateria_inicial,
		zonas_sombra=zonas_sombra,
		muestras_igneas=muestras_igneas,
		muestras_sedimentarias=muestras_sedimentarias,
	)
	resultado = astar(problema, graph_search=True)
	if resultado is None:
		return []
	return [accion for accion, _ in resultado.path()[1:]]


if __name__ == "__main__":
	acciones = planear_rover(
		rover_inicio=(0, 0),
		bateria_inicial=20,
		zonas_sombra=[(0, 1), (0, 2)],
		muestras_igneas=[(1, 1), (1, 2)],
		muestras_sedimentarias=[(2, 3)],
	)
	print(acciones)
