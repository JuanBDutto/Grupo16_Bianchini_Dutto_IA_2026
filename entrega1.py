from simpleai.search import SearchProblem, astar

Zonas_sombra = []

Costos_bateria = {
    "moverse": 1,
    "sobremarcha": 4,
    "recolectar": 3,
    "recargar": -10,
    "depositar": 1,
    "equipar": 1
}

Costos_Minutos = {
    "moverse": 1,
    "sobremarcha": 1,
    "equipar": 3,
    "recolectar": 2,
    "depositar": 1,
    "recargar": 4
}

Max_Bateria = 20


def planear_rover(rover_inicio, bateria_inicial, zonas_sombra, muestras_igneas, muestras_sedimentarias):
    
    estado_inicial = (rover_inicio, bateria_inicial, None, tuple(muestras_igneas), tuple(muestras_sedimentarias), 0)

    posiciones = [rover_inicio] + list(muestras_igneas) + list(muestras_sedimentarias) + list(zonas_sombra)
    filas = [pos[0] for pos in posiciones]
    columnas = [pos[1] for pos in posiciones]

    min_x,  max_x = min(filas), max(filas)
    min_y, max_y = min(columnas), max(columnas)
    
    global Zonas_sombra
    Zonas_sombra = zonas_sombra

    class Entrega1(SearchProblem):

        def actions(self, state):
            posicion_rover, bateria, taladro, muestras_igneas, muestras_sedimentarias, carga = state
            muestras_restantes = len(muestras_igneas) + len(muestras_sedimentarias)

            muestra_lejana = any(
                abs(posicion_rover[0] - muestra[0]) + abs(posicion_rover[1] - muestra[1]) >= 2
                for muestra in muestras_igneas + muestras_sedimentarias
            )

            posibles_acciones = []
            if bateria - Costos_bateria["moverse"] > 0:
                posibles_acciones.extend(self.mover_rover(posicion_rover[0], posicion_rover[1]))
            if bateria - Costos_bateria["sobremarcha"] > 0 and muestras_restantes > 0 and muestra_lejana:
                posibles_acciones.extend(self.mover_rover_sobremarcha(posicion_rover[0], posicion_rover[1]))
            if taladro == "termico" and bateria - Costos_bateria["recolectar"] > 0 and posicion_rover in muestras_igneas and carga < 2:
                posibles_acciones.extend(self.recolectar_muestra("ignea"))
            if taladro == "percusion" and bateria - Costos_bateria["recolectar"] > 0 and posicion_rover in muestras_sedimentarias and carga < 2:
                posibles_acciones.extend(self.recolectar_muestra("sedimentaria"))
            if posicion_rover not in Zonas_sombra and bateria <= 6:
                posibles_acciones.extend(self.recargar_bateria())
            if bateria - Costos_bateria["depositar"] > 0 and (carga == 2 or (muestras_restantes == 0 and carga > 0)):
                posibles_acciones.extend(self.depositar_muestra())
            if bateria - Costos_bateria["equipar"] > 0 and taladro != "percusion" and len(muestras_sedimentarias) > 0:
                posibles_acciones.extend(self.equipar_taladro("percusion"))
            if bateria - Costos_bateria["equipar"] > 0 and taladro != "termico" and len(muestras_igneas) > 0:
                posibles_acciones.extend(self.equipar_taladro("termico"))

            return tuple(posibles_acciones)

        def result(self, state, action):
            posicion_rover, bateria, taladro, muestras_igneas, muestras_sedimentarias, carga = state

            if action[0] == "moverse":
                return (action[1], bateria - Costos_bateria["moverse"], taladro, muestras_igneas, muestras_sedimentarias, carga)
            elif action[0] == "sobremarcha":
                return (action[1], bateria - Costos_bateria["sobremarcha"], taladro, muestras_igneas, muestras_sedimentarias, carga)
            elif action[0] == "recolectar":
                if action[1] == "ignea":
                    nuevas_muestras_igneas = tuple(m for m in muestras_igneas if m != posicion_rover)
                    return (posicion_rover, bateria - Costos_bateria["recolectar"], taladro, nuevas_muestras_igneas, muestras_sedimentarias, carga + 1)
                else:
                    nuevas_muestras_sedimentarias = tuple(m for m in muestras_sedimentarias if m != posicion_rover)
                    return (posicion_rover, bateria - Costos_bateria["recolectar"], taladro, muestras_igneas, nuevas_muestras_sedimentarias, carga + 1)
            elif action[0] == "recargar":
                if bateria - Costos_bateria["recargar"] >= Max_Bateria:
                    return (posicion_rover, Max_Bateria , taladro, muestras_igneas, muestras_sedimentarias, carga)
                else:
                    return (posicion_rover, bateria - Costos_bateria["recargar"], taladro, muestras_igneas, muestras_sedimentarias, carga)
            elif action[0] == "depositar":
                return (posicion_rover, bateria - Costos_bateria["depositar"], taladro, muestras_igneas, muestras_sedimentarias, carga - carga)
            elif action[0] == "equipar":
                return (posicion_rover, bateria - Costos_bateria["equipar"], (action[1]), muestras_igneas, muestras_sedimentarias, carga)

            return state

        def is_goal(self, state):
            posicion_rover, bateria, taladro, muestras_igneas, muestras_sedimentarias, carga = state
            return len(muestras_igneas) == 0 and len(muestras_sedimentarias) == 0 and carga == 0
    
        def cost(self, state1, action, state2):
            if action[0] == "moverse":
                return Costos_Minutos["moverse"]
            elif action[0] == "sobremarcha":
                return Costos_Minutos["sobremarcha"]
            elif action[0] == "recolectar":
                return Costos_Minutos["recolectar"]
            elif action[0] == "recargar":
                return Costos_Minutos["recargar"]
            elif action[0] == "depositar":
                carga_actual = state1[5]
                return Costos_Minutos["depositar"] * carga_actual
            elif action[0] == "equipar":
                return Costos_Minutos["equipar"]
        
            return 0

        def heuristic(self, state):
            posicion_rover, bateria, taladro, muestras_igneas, muestras_sedimentarias, carga = state
            muestras_restantes = len(muestras_igneas) + len(muestras_sedimentarias)

            if muestras_restantes == 0:
                return 0

            distancia_minima = min(
                abs(posicion_rover[0] - muestra[0]) +
                abs(posicion_rover[1] - muestra[1])
                for muestra in muestras_igneas + muestras_sedimentarias
            )

            return (muestras_restantes * Costos_Minutos["recolectar"] + ((distancia_minima + 1) // 2))
        
        def posicion_valida(self, posicion):
            return (
                min_x <= posicion[0] <= max_x and
                min_y <= posicion[1] <= max_y
            )

        def mover_rover(self, fil, col):
            acciones_posibles = []

            destinos =[
                (fil-1, col), 
                (fil+1, col), 
                (fil, col-1), 
                (fil, col+1)
            ]

            for nuevaposicion in destinos:
                if self.posicion_valida(nuevaposicion):
                    acciones_posibles.append(("moverse", nuevaposicion))
                
            
            return tuple(acciones_posibles)
    
        def mover_rover_sobremarcha(self, fil, col):
            acciones_posibles = []

            destinos =[
                (fil-2, col),
                (fil+2, col),
                (fil, col-2),
                (fil, col+2)
            ]

            for nuevaposicion in destinos:
                if self.posicion_valida(nuevaposicion):
                    acciones_posibles.append(("sobremarcha", nuevaposicion))

            return tuple(acciones_posibles)
        
        def recolectar_muestra(self, tipo_muestra):
            acciones_posibles = []
            acciones_posibles.append(("recolectar", tipo_muestra))

            return tuple(acciones_posibles)
    
        def recargar_bateria(self):
            acciones_posibles = []
            acciones_posibles.append(("recargar", None))

            return tuple(acciones_posibles)
    
        def depositar_muestra(self):
            acciones_posibles = []
            acciones_posibles.append(("depositar", None))

            return tuple(acciones_posibles)
    
        def equipar_taladro(self, tipo_taladro):
            acciones_posibles = []
            acciones_posibles.append(("equipar", tipo_taladro))

            return tuple(acciones_posibles)
    
    problema = Entrega1(estado_inicial)
    resultado = astar(problema,graph_search=True)
    return [accion for accion, estado in resultado.path()[1:]]

if __name__ == "__main__":
    rover_inicio = (0, 0)
    bateria_inicial = Max_Bateria
    zonas_sombra = [(0, 1), (0, 2)]
    muestras_igneas = [(1, 1), (1, 2)]
    muestras_sedimentarias = [(2,3)]

    resultado = planear_rover(rover_inicio, bateria_inicial, zonas_sombra, muestras_igneas, muestras_sedimentarias)

    print (resultado)