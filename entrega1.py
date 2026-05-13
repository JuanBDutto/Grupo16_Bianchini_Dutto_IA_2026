from simpleai.search import SearchProblem, astar

Zonas_sombras = []

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
    "recoletar": 2,
    "depositar": 1,
    "recargar": 4
}

def planear_rover(rover_inicio, bateria_inicial, zonas_sombra, muestras_igneas, muestras_sedimentarias):

        initial_state = (rover_inicio, bateria_inicial, None, frozenset(muestras_igneas), frozenset(muestras_sedimentarias), 0)
        Zonas_sombra = zonas_sombras
        # Implementa la lógica para planear el camino del rover desde el estado inicial hasta el objetivo
        pass

class Entrega1(SearchProblem):

    def actions(self, state):

        posicion_rover, bateria, taladro, muestras_igneas, muestras_sedimentarias, carga = state
        posibles_acciones = []
        if bateria - Costos_bateria["moverse"] >= 0:
            posibles_acciones.extend(self.mover_rover(posicion_rover[0], posicion_rover[1]))
        if bateria - Costos_bateria["sobremarcha"] >= 0:
            posibles_acciones.extend(self.mover_rover_sobremarcha(posicion_rover[0], posicion_rover[1]))
        if taladro == "termico" and bateria - Costos_bateria["recolectar"] >= 0 and posicion_rover in muestras_igneas and carga < 2:
            posibles_acciones.extend(self.recolectar_muestra("igneas"))
        elif taladro == "percusion" and bateria - Costos_bateria["recolectar"] >= 0 and posicion_rover in muestras_sedimentarias and carga < 2:
            posibles_acciones.extend(self.recolectar_muestra("sedimentarias"))
        if posicion_rover not in Zonas_sombra:
            posibles_acciones.extend(self.recargar_bateria())
        if bateria - Costos_bateria["depositar"] >= 0 and carga > 0 <= 2 and len(muestras_igneas) == 0 and len(muestras_sedimentarias) == 0:
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
        muestras_igneas, muestras_sedimentarias, bateria = state
        return len(muestras_igneas) == 0 and len(muestras_sedimentarias) == 0 and bateria > 0
    
    def cost(self, state1, action, state2):

        if action[0] == "moverse":
            return Costos_bateria["moverse"]
        elif action[0] == "sobremarcha":
            return Costos_bateria["sobremarcha"]
        elif action[0] == "recolectar":
            return Costos_bateria["recolectar"]
        elif action[0] == "recargar":
            return Costos_bateria["recargar"]
        elif action[0] == "depositar":
            return Costos_bateria["depositar"]
        elif action[0] == "equipar":
            return Costos_bateria["equipar"]
        
        return 0

    def heuristic(self, state):
        # Implementa la función heurística para estimar el costo restante hasta el objetivo
        pass


    def mover_rover (self, fil, col):

        acciones_posibles = []
        acciones_posibles.append(("moverse", fil-1, col))  
        acciones_posibles.append(("moverse", fil+1, col))
        acciones_posibles.append(("moverse", fil, col-1))
        acciones_posibles.append(("moverse", fil, col+1))

        return acciones_posibles
    
    def mover_rover_sobremarcha (self, fil, col):
        
        acciones_posibles = []
        acciones_posibles.append(("sobremarcha", fil-2, col))  
        acciones_posibles.append(("sobremarcha", fil+2, col))
        acciones_posibles.append(("sobremarcha", fil, col-2))
        acciones_posibles.append(("sobremarcha", fil, col+2))

        return acciones_posibles
    
    def recolectar_muestra (self, tipo_muestra):

        acciones_posibles = []
        acciones_posibles.append(("recolectar",tipo_muestra))

        return acciones_posibles
    
    def recargar_bateria (self):

        acciones_posibles = []
        acciones_posibles.append(("recargar", None))

        return acciones_posibles
    
    def depositar_muestra (self):

        acciones_posibles = []
        acciones_posibles.append(("depositar", None))

        return acciones_posibles
    
    def equipar_taladro (self, tipo_taladro):

        acciones_posibles = []
        acciones_posibles.append(("equipar", tipo_taladro))

        return acciones_posibles
    
problema = Entrega1(initial_state)
solucion = astar(problema)
    
if __name__ == "__main__":
    rover_inicio = (0, 0)
    bateria_inicial = 20
    zonas_sombra = [(1, 1), (2, 2)]
    muestras_igneas = [(3, 3), (4, 4)]
    muestras_sedimentarias = [(5, 5), (6, 6)]

    resultado = planear_rover(rover_inicio, bateria_inicial, zonas_sombra, muestras_igneas, muestras_sedimentarias)