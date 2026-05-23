from simpleai.search import(
    CspProblem,
    backtrack,
    min_conflicts
)

from itertools import combinations

def build_camp(camp_size, habs, generators, labs, deposits, airlocks, craters):
    filas, columnas = camp_size
    set_craters = set(craters)


    variables = []
    for i in range(habs):
        variables.append(f"hab_{i}")
    for i in range(generators):
        variables.append(f"gen_{i}")
    for i in range(labs):
        variables.append(f"lab_{i}")
    for i in range(deposits):
        variables.append(f"dep_{i}")
    for i in range(airlocks):
        variables.append(f"air_{i}")
    
    celdas_validas = [
        (fila, columna)
        for fila in range(filas)
        for columna in range(columnas)
        if (fila, columna) not in set_craters
    ]

    domains = {}
    for variable in variables:
        domains[variable] = celdas_validas
    
    constraints = []

    def sin_superposicion(variables, values):
        return values[0] != values[1]

    for var1, var2 in combinations(variables, 2):
        constraints.append(((var1, var2), sin_superposicion))

    def exclusa_en_borde(variables, values):
        fila, columna = values[0]
        return fila == 0 or fila == filas - 1 or columna == 0 or columna == columnas - 1

    for air in [f"air_{i}" for i in range(airlocks)]:
        constraints.append(((air,), exclusa_en_borde))

    def habitacion_en_interior(variables, values):
        fila, columna = values[0]
        return 0 < fila < filas - 1 and 0 < columna < columnas - 1

    for hab in [f"hab_{i}" for i in range(habs)]:
        constraints.append(((hab,), habitacion_en_interior))

    def no_es_adyacente(variables, values):
        fila1, columna1 = values[0]
        fila2, columna2 = values[1]
        return abs(fila1 - fila2) + abs(columna1 - columna2) != 1

    def es_adyacente(variables, values):
        fila1, columna1 = values[0]
        fila2, columna2 = values[1]
        return abs(fila1 - fila2) + abs(columna1 - columna2) == 1
    
    habs_total = [variable for variable in variables if variable.startswith("hab_")]
    gens_total = [variable for variable in variables if variable.startswith("gen_")]
    
    for gen in gens_total:
        for hab in habs_total:
            constraints.append(((gen, hab), no_es_adyacente))

    for gen1, gen2 in combinations(gens_total, 2):
        constraints.append(((gen1, gen2), no_es_adyacente))

    labs_total = [variable for variable in variables if variable.startswith("lab_")]
    deps_total = [variable for variable in variables if variable.startswith("dep_")]

    def lab_adyacente_deposito(variables, values):
        lab_pos = values[0]

        for dep_pos in values[1:]:
            if abs(lab_pos[0] - dep_pos[0]) + abs(lab_pos[1] - dep_pos[1]) == 1:
                return True

        return False

    for lab in labs_total:
        constraints.append(((lab, *deps_total), lab_adyacente_deposito))

    


    problem = CspProblem(variables, domains, constraints)
    solution = backtrack(problem)
    
    if solution is None:
        return None

    resultado = []
    for var, pos in solution.items():
        tipo = var.rsplit("_", 1)[0]  # "hab_0" -> "hab", "gen_0" -> "gen"
        resultado.append((tipo, pos[0], pos[1]))
    return resultado





  