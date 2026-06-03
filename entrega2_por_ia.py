from itertools import combinations

"""Solucion del campamento como CSP con SimpleAI.

Ejercicio 1
- Variables: una variable por modulo a ubicar.
- Dominios: celdas validas de la grilla, filtradas por el tipo de modulo.
- Restricciones:
  1. Sin superposicion.
  2. Sin ubicacion sobre crateres.
  3. Esclusas sobre el borde.
  4. Habitacionales al interior.
  5. Generadores no adyacentes a habitacionales.
  6. Generadores no adyacentes entre si.
  7. Laboratorios adyacentes a al menos un deposito.
  8. Habitacionales con al menos una celda adyacente libre para evacuacion.

Ejercicio 2
- build_camp construye y resuelve el CSP y retorna la lista pedida o None.
"""

from simpleai.search import CspProblem, backtrack


TYPE_ORDER = {"air": 0, "hab": 1, "gen": 2, "lab": 3, "dep": 4}


def _is_border(cell, rows, cols):
	row, col = cell
	return row == 0 or row == rows - 1 or col == 0 or col == cols - 1


def _adjacent(cell_a, cell_b):
	return abs(cell_a[0] - cell_b[0]) + abs(cell_a[1] - cell_b[1]) == 1


def _neighbors(cell, rows, cols):
	row, col = cell
	for delta_row, delta_col in ((-1, 0), (1, 0), (0, -1), (0, 1)):
		new_row = row + delta_row
		new_col = col + delta_col
		if 0 <= new_row < rows and 0 <= new_col < cols:
			yield new_row, new_col

def _not_on_crater(cell, crater_set):
	return cell not in crater_set


def _on_border(cell, rows, cols):
	return _is_border(cell, rows, cols)


def _in_interior(cell, rows, cols):
	return not _is_border(cell, rows, cols)


def _not_adjacent(first, second):
	return not _adjacent(first, second)


def _all_different(_, values):
	return values[0] != values[1]


def _border_constraint(_, values, rows, cols):
	return _on_border(values[0], rows, cols)


def _interior_constraint(_, values, rows, cols):
	return _in_interior(values[0], rows, cols)


def _not_in_crater_constraint(_, values, crater_set):
	return _not_on_crater(values[0], crater_set)


def _not_adjacent_constraint(_, values):
	return _not_adjacent(values[0], values[1])


def _lab_has_deposit_constraint(_, values):
	lab_cell = values[0]
	return any(_adjacent(lab_cell, deposit_cell) for deposit_cell in values[1:])


def _hab_has_free_neighbor_constraint(_, values, rows, cols, crater_set):
	hab_cell = values[0]
	occupied = set(values[1:])
	for neighbor in _neighbors(hab_cell, rows, cols):
		if neighbor not in occupied and neighbor not in crater_set:
			return True
	return False


def build_camp(camp_size, habs, generators, labs, deposits, airlocks, craters):
	rows, cols = camp_size
	crater_set = set(craters)

	if rows <= 0 or cols <= 0:
		return None

	all_cells = [(row, col) for row in range(rows) for col in range(cols)]
	valid_cells = [cell for cell in all_cells if cell not in crater_set]
	border_cells = [cell for cell in valid_cells if _is_border(cell, rows, cols)]
	interior_cells = [cell for cell in valid_cells if not _is_border(cell, rows, cols)]
	hab_cells = [
		cell
		for cell in interior_cells
		if any(neighbor not in crater_set for neighbor in _neighbors(cell, rows, cols))
	]

	if airlocks > len(border_cells):
		return None
	if habs > len(hab_cells):
		return None
	if habs + generators + labs + deposits + airlocks > len(valid_cells):
		return None
	if labs > 0 and deposits == 0:
		return None

	variables = []
	domains = {}
	constraints = []
	metadata = {}

	def add_variable(tipo, index, domain):
		name = f"{tipo}_{index}"
		variables.append(name)
		domains[name] = list(domain)
		metadata[name] = tipo
		return name

	air_vars = [add_variable("air", index, border_cells) for index in range(airlocks)]
	hab_vars = [add_variable("hab", index, hab_cells) for index in range(habs)]
	gen_vars = [add_variable("gen", index, valid_cells) for index in range(generators)]
	dep_vars = [add_variable("dep", index, valid_cells) for index in range(deposits)]
	lab_vars = [add_variable("lab", index, valid_cells) for index in range(labs)]

	if any(not domains[name] for name in variables):
		return None

	def add_pairwise_distinct(names):
		for first, second in combinations(names, 2):
			constraints.append(([first, second], _all_different))

	add_pairwise_distinct(variables)

	for air_var in air_vars:
		constraints.append(([air_var], lambda variables, values, rows=rows, cols=cols: _border_constraint(variables, values, rows, cols)))

	for hab_var in hab_vars:
		constraints.append(([hab_var], lambda variables, values, rows=rows, cols=cols: _interior_constraint(variables, values, rows, cols)))

	for name in variables:
		constraints.append(([name], lambda variables, values, crater_set=crater_set: _not_in_crater_constraint(variables, values, crater_set)))

	for gen_var in gen_vars:
		for hab_var in hab_vars:
			constraints.append(([gen_var, hab_var], _not_adjacent_constraint))

	for first_gen, second_gen in combinations(gen_vars, 2):
		constraints.append(([first_gen, second_gen], _not_adjacent_constraint))

	for lab_var in lab_vars:
		if dep_vars:
			constraints.append(([lab_var, *dep_vars], _lab_has_deposit_constraint))

	all_vars_for_escape = air_vars + hab_vars + gen_vars + dep_vars + lab_vars
	if hab_vars:
		for hab_var in hab_vars:
			constraints.append((
				[hab_var, *all_vars_for_escape],
				lambda variables, values, rows=rows, cols=cols, crater_set=crater_set: _hab_has_free_neighbor_constraint(
					variables, values, rows, cols, crater_set
				),
			))

	problem = CspProblem(variables, domains, constraints)
	solution = backtrack(problem)

	if solution is None:
		return None

	result = []
	for variable in variables:
		tipo = metadata[variable]
		row, col = solution[variable]
		result.append((tipo, row, col))

	result.sort(key=lambda item: (TYPE_ORDER[item[0]], item[1], item[2]))
	return result