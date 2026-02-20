import heapq

# Definición de la clase Node para representar cada estado en el espacio de búsqueda

class Node:
    def __init__(self, state, parent=None, path_cost=0, f_value=float('inf')):
        self.state = {
            "edificio": str, # 'B30'...'B38', 'Cafetería', 'Biblioteca' o 'Pasillo'
            "piso": int, # 1..8
            "coordenada": (x, y) # tupla con la posición en la grilla
        }
        self.parent = parent
        self.path_cost = path_cost #Costo del path g(n)
        self.f_value = f_value #valor del costo para el camino alternativo

    def __lt__(self, other):
        return self.f_value < other.f_value #comparación para la organización de prioridad

    def __repr__(self):
        return f"Node({self.state})" #Impresión del estado ante la invocación del método print
    


# Definición de la clase Problem para representar el problema de búsqueda, incluyendo el estado inicial, el estado objetivo, las acciones posibles, la función de resultado y la función heurística
class Problem:
    def __init__(self, initial, goal, actions, result, h):
        self.initial = initial
        self.goal = goal
        self.actions = actions #conjunto de actions posible para un estado [s]
        self.result = result
        self.h = h #Aplicación de la función heuristica

    def is_goal(self, state):
        return state == self.goal
    

# Definición de la función A* para encontrar el camino óptimo desde el estado inicial hasta el estado objetivo
def f(node, problem):
    return node.path_cost + problem.h(node.state) #retorna f(n)=g(n)+h(n)


# 
def expand(node, problem):
    successors = [] #lista de sucesores, recuerden qye tambien podrian usar yield si lo requieren
    for action, cost in problem.actions[node.state].items():
        child_state = problem.result(node.state, action)
        child = Node(state=child_state, parent=node, path_cost=node.path_cost + cost)#definición de costo del camino g(n)
        child.f_value = f(child, problem)#aplicación f(n)=g(n)+h(n) para hacer un set del atributo
        successors.append(child)
    return successors