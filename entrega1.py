from simpleai.search import SearchProblem, astar

Zonas_sombra = []

Costos_bateria = {
    "moverse": 1,
    "sobremarcha": 4,
    "recolectar": 3,
    "recargar": -10,
    "depositar": 2,
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

def planear_rover(rover_inicio, bateria_inicial, zonas_sombra, muestras_igneas, muestras_sedimentarias):
    
    estado_inicial = (rover_inicio, bateria_inicial, None, tuple(muestras_igneas), tuple(muestras_sedimentarias), 0)
    
    global Zonas_sombra
    Zonas_sombra = zonas_sombra

    class Entrega1(SearchProblem):

        def actions(self, state):
            posicion_rover, bateria, taladro, muestras_igneas, muestras_sedimentarias, carga = state
            posibles_acciones = []
            if bateria - Costos_bateria["moverse"] >= 0:
                posibles_acciones.extend(self.mover_rover(posicion_rover[0], posicion_rover[1]))
            if bateria - Costos_bateria["sobremarcha"] >= 0:
                posibles_acciones.extend(self.mover_rover_sobremarcha(posicion_rover[0], posicion_rover[1]))
            if taladro == "termico" and bateria - Costos_bateria["recolectar"] >= 0 and posicion_rover in muestras_igneas and carga < 2:
                posibles_acciones.extend(self.recolectar_muestra("ignea"))
            if taladro == "percusion" and bateria - Costos_bateria["recolectar"] >= 0 and posicion_rover in muestras_sedimentarias and carga < 2:
                posibles_acciones.extend(self.recolectar_muestra("sedimentaria"))
            if posicion_rover not in Zonas_sombra:
                posibles_acciones.extend(self.recargar_bateria())
            if bateria - Costos_bateria["depositar"] >= 0 and (carga == 2 or (len(muestras_igneas)+len(muestras_sedimentarias) == 0)):
                posibles_acciones.extend(self.depositar_muestra())
            if taladro is None or taladro != "percusion" and bateria - Costos_bateria["equipar"] >= 0:
                posibles_acciones.extend(self.equipar_taladro("percusion"))
            if taladro is None or taladro != "termico" and bateria - Costos_bateria["equipar"] >= 0:
                posibles_acciones.extend(self.equipar_taladro("termico"))

            return posibles_acciones

        def result(self, state, action):
            posicion_rover, bateria, taladro, muestras_igneas, muestras_sedimentarias, carga = state

            if action[0] == "moverse":
                return (action[1], bateria - Costos_bateria["moverse"], taladro, muestras_igneas, muestras_sedimentarias, carga)
            elif action[0] == "sobremarcha":
                return (action[1], bateria - Costos_bateria["sobremarcha"], taladro, muestras_igneas, muestras_sedimentarias, carga)
            elif action[0] == "recolectar":
                return (posicion_rover, bateria - Costos_bateria["recolectar"], taladro, muestras_igneas, muestras_sedimentarias, carga)
            elif action[0] == "recargar":
                return (posicion_rover, bateria - Costos_bateria["recargar"], taladro, muestras_igneas, muestras_sedimentarias, carga)
            elif action[0] == "depositar":
                return (posicion_rover, bateria - Costos_bateria["depositar"], taladro, muestras_igneas, muestras_sedimentarias, carga)
            elif action[0] == "equipar":
                return (posicion_rover, bateria - Costos_bateria["equipar"], taladro, muestras_igneas, muestras_sedimentarias, carga)

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
            return len(muestras_igneas) + len(muestras_sedimentarias)
        
        def mover_rover(self, fil, col):
            acciones_posibles = []
            acciones_posibles.append(("moverse", (fil-1, col)))
            acciones_posibles.append(("moverse", (fil+1, col)))
            acciones_posibles.append(("moverse", (fil, col-1)))
            acciones_posibles.append(("moverse", (fil, col+1)))

            return acciones_posibles
    
        def mover_rover_sobremarcha(self, fil, col):
            acciones_posibles = []
            acciones_posibles.append(("sobremarcha", (fil-2, col)))
            acciones_posibles.append(("sobremarcha", (fil+2, col)))
            acciones_posibles.append(("sobremarcha", (fil, col-2)))
            acciones_posibles.append(("sobremarcha", (fil, col+2)))

            return acciones_posibles
    
        def recolectar_muestra(self, tipo_muestra):
            acciones_posibles = []
            acciones_posibles.append(("recolectar", tipo_muestra))

            return acciones_posibles
    
        def recargar_bateria(self):
            acciones_posibles = []
            acciones_posibles.append(("recargar", None))

            return acciones_posibles
    
        def depositar_muestra(self):
            acciones_posibles = []
            acciones_posibles.append(("depositar", None))

            return acciones_posibles
    
        def equipar_taladro(self, tipo_taladro):
            acciones_posibles = []
            acciones_posibles.append(("equipar", tipo_taladro))

            return acciones_posibles
    
    problema = Entrega1(estado_inicial)
    resultado = astar(problema)
    return [accion for accion, estado in resultado.path()[1:]]

if __name__ == "__main__":
    rover_inicio = (0, 0)
    bateria_inicial = 20
    zonas_sombra = [(1, 1), (2, 2)]
    muestras_igneas = [(3, 3), (4, 4)]
    muestras_sedimentarias = [(5, 5), (6, 6)]

    resultado = planear_rover(rover_inicio, bateria_inicial, zonas_sombra, muestras_igneas, muestras_sedimentarias)

    print (resultado)