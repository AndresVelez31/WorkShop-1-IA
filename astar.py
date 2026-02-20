import heapq
import math

GRID_W = 17   # x: 0..16
GRID_H = 16   # y: 0..15

CAMPUS_MAP = [
    [" ", "#", " ",  " ", "#",  " ",  " ", "#", " ",  " ", "#", " ",  " ", "#", " ",  " ", " "],  # y=0
    [" ", "#", " ",  " ", "#",  " ",  " ", "#", " ",  " ", "#", " ",  " ", "#", " ",  " ", " "],  # y=1
    [" ", " ", "B30"," ", " ", "B31"," ", " ", "B32"," ", " ", "B33"," ", " ", "B34"," ", " "],  # y=2
    [" ", "#", " ",  "#", "#", " ",  "#", " ", "#",  "#", " ", "#",  " ", "#", " ",  "#", " "],  # y=3
    [" ", "#", " ",  " ", " ", " ",  "#", " ", "#",  " ", " ", "#",  " ", "#", " ",  "#", " "],  # y=4
    [" ", " ", " ",  "#", " ", " ",  " ", " ", " ",  "#", " ", " ",  " ", " ", " ",  "#", " "],  # y=5
    [" ", "#", " ",  " ", "B35"," ",  "#", " ", "B36"," ", "#", " ",  "B37"," ", "#", " ", "B38"], # y=6
    [" ", "#", "#",  " ", "#", " ",  "#", " ", "#",  " ", "#", " ",  "#", " ", "#",  " ", " "],  # y=7
    [" ", " ", " ",  " ", "#", " ",  " ", " ", "#",  " ", " ", " ",  "#", " ", " ",  " ", " "],  # y=8
    ["#", "#", " ",  "#", "#", " ",  "#", " ", " ",  " ", "#", " ",  "#", " ", "#",  "#", " "],  # y=9
    [" ", " ", " ",  " ", "#", " ",  "C", " ", "#",  " ", "#", " ",  " ", " ", "B",  " ", " "],  # y=10
    [" ", "#", "#",  " ", "#", " ",  "#", " ", "#",  " ", "#", " ",  "#", " ", "#",  " ", " "],  # y=11
    [" ", " ", " ",  " ", " ", " ",  " ", " ", " ",  " ", " ", " ",  " ", " ", " ",  " ", " "],  # y=12
    [" ", "#", " ",  "#", " ", "#",  " ", "#", " ",  "#", " ", "#",  " ", "#", " ",  "#", " "],  # y=13
    [" ", "#", " ",  " ", " ", " ",  " ", " ", " ",  " ", " ", " ",  " ", " ", " ",  "#", " "],  # y=14
    [" ", " ", " ",  "#", "#", "#",  " ", "#", "#",  "#", " ", "#",  "#", "#", " ",  " ", " "],  # y=15
]

# Mapeo de coordenadas de edificios
BUILDING_COORDS = {
    'B30': (2, 2),
    'B31': (5, 2),
    'B32': (8, 2),
    'B33': (11, 2),
    'B34': (14, 2),
    'B35': (4, 6),
    'B36': (8, 6),
    'B37': (12, 6),
    'B38': (16, 6),
    'Cafetería': (6, 10),     # C en mapa
    'Biblioteca': (14, 10),    # B en mapa
}

BUILDINGS_WITH_ELEVATORS = {'B32', 'B33', 'B35', 'B37', 'B38'}
BUILDINGS = set(BUILDING_COORDS.keys())

# Función para determinar edificio dado una coordenada
def edificio_from_coord(coord):
    for name, c in BUILDING_COORDS.items():
        if coord == c:
            return name
    return 'Pasillo'

# Verificar si posición es transitables (según mapa textual)
def is_transitable(coord):
    x, y = coord
    if 0 <= x < GRID_W and 0 <= y < GRID_H:
        cell = CAMPUS_MAP[y][x]
        return cell != '#'
    return False

# Movimiento plano
PLAN_MOVES = {
    'arriba':    (0, -1),
    'abajo':     (0, 1),
    'izquierda': (-1, 0),
    'derecha':    (1, 0),
}

ACTION_COSTS = {
    'mover': 1,
    'subir_ascensor': 3,
    'bajar_ascensor': 3,
    'subir_escaleras': None,  # se calculará dinámicamente
    'bajar_escaleras': 5,
}




# Definición de la clase Node para representar cada estado en el espacio de búsqueda
class Node:
    def __init__(self, state, parent=None, action=None, path_cost=0, f_value=float('inf')):
        self.state = state
        self.parent = parent
        self.action = action  # Acción que llevó a este estado
        self.path_cost = path_cost  # Costo del path g(n)
        self.f_value = f_value  # valor f(n) = g(n) + h(n)

    def __lt__(self, other):
        return self.f_value < other.f_value  # comparación para la organización de prioridad

    def __repr__(self):
        return f"Node({self.state}, g={self.path_cost:.1f}, f={self.f_value:.1f})"


# Definición de la clase Problem para representar el problema de búsqueda
class Problem:
    def __init__(self, initial, goal):
        self.initial = initial
        self.goal = goal

    def is_goal(self, state):
        return state['coordenada'] == self.goal['coordenada'] and state['piso'] == self.goal['piso']

    def h(self, state):
        """Heurística: distancia euclídea en el plano (ignorando piso)"""
        x1, y1 = state['coordenada']
        x2, y2 = self.goal['coordenada']
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

# Función f(n) = g(n) + h(n)
def f(node, problem):
    return node.path_cost + problem.h(node.state)


# Función expand: genera sucesores de un nodo aplicando todas las acciones posibles
def expand(node, problem):
    """Genera todos los sucesores válidos de un nodo"""
    successors = []
    state = node.state
    edificio = state['edificio']
    piso = state['piso']
    coord = state['coordenada']

    # 1) Movimientos en el plano (arriba, abajo, izquierda, derecha)
    for action_name, delta in PLAN_MOVES.items():
        dx, dy = delta
        new_coord = (coord[0] + dx, coord[1] + dy)
        if is_transitable(new_coord):
            new_edificio = edificio_from_coord(new_coord)
            child = Node(
                state={'edificio': new_edificio, 'piso': piso, 'coordenada': new_coord},
                parent=node,
                action=action_name,
                path_cost=node.path_cost + ACTION_COSTS['mover']
            )
            child.f_value = f(child, problem)
            successors.append(child)

    # 2) Ascensor (solo en edificios con ascensor)
    if edificio in BUILDINGS_WITH_ELEVATORS:
        # Subir ascensor
        if piso < 3:
            child = Node(
                state={'edificio': edificio, 'piso': piso + 1, 'coordenada': coord},
                parent=node,
                action='subir_ascensor',
                path_cost=node.path_cost + ACTION_COSTS['subir_ascensor']
            )
            child.f_value = f(child, problem)
            successors.append(child)
        
        # Bajar ascensor
        if piso > 1:
            child = Node(
                state={'edificio': edificio, 'piso': piso - 1, 'coordenada': coord},
                parent=node,
                action='bajar_ascensor',
                path_cost=node.path_cost + ACTION_COSTS['bajar_ascensor']
            )
            child.f_value = f(child, problem)
            successors.append(child)

    # 3) Escaleras (disponibles en cualquier edificio)
    # Solo usar escaleras si estamos EN un edificio (no en pasillo)
    if edificio != 'Pasillo':
        # Subir escaleras: costo = 7 + p (donde p = número de pisos a subir)
        for p_subir in range(1, 4 - piso + 1):  # Máximo hasta piso 3
            new_piso = piso + p_subir
            if new_piso <= 3:
                child = Node(
                    state={'edificio': edificio, 'piso': new_piso, 'coordenada': coord},
                    parent=node,
                    action=f'subir_escaleras_{p_subir}',
                    path_cost=node.path_cost + (7 + p_subir)
                )
                child.f_value = f(child, problem)
                successors.append(child)
        
        # Bajar escaleras: costo fijo = 5 (por cada piso)
        if piso > 1:
            for p_bajar in range(1, piso):
                new_piso = piso - p_bajar
                child = Node(
                    state={'edificio': edificio, 'piso': new_piso, 'coordenada': coord},
                    parent=node,
                    action=f'bajar_escaleras_{p_bajar}',
                    path_cost=node.path_cost + (5 * p_bajar)  # Costo por cada piso bajado
                )
                child.f_value = f(child, problem)
                successors.append(child)

    return successors

# ---------------------------
# Funciones RBFS (no utilizadas en este ejercicio, pero disponibles)
# ---------------------------

# La función recursive_best_first_search implementa el algoritmo RBFS, que es una variante de A* que utiliza una cantidad limitada de memoria.
def recursive_best_first_search(problem):
    initial_node = Node(problem.initial, path_cost=0, f_value=problem.h(problem.initial))
    return rbfs(problem, initial_node, float('inf'))

# La función rbfs toma un nodo y un límite f(n) como argumentos. 
def rbfs(problem, node, f_limit):
    if problem.is_goal(node.state):
        return node, node.f_value

    successors = expand(node, problem)
    if not successors:
        return None, float('inf')

    heapq.heapify(successors)

    while True:
        best = heapq.heappop(successors)
        if best.f_value > f_limit:
            return None, best.f_value
        alternative = successors[0].f_value if successors else float('inf')
        result, best.f_value = rbfs(problem, best, min(f_limit, alternative))
        if result is not None:
            return result, best.f_value
        heapq.heappush(successors, best)


# ---------------------------
# Algoritmo A* (principal)
# ---------------------------

def astar_search(problem, max_iters=100000):
    """Implementación de A* para encontrar el camino óptimo"""
    initial_node = Node(problem.initial, path_cost=0, f_value=problem.h(problem.initial))
    frontier = []
    heapq.heappush(frontier, initial_node)
    explored = set()

    it = 0
    while frontier and it < max_iters:
        it += 1
        node = heapq.heappop(frontier)
        state = node.state
        key = (state['edificio'], state['piso'], state['coordenada'])
        
        if key in explored:
            continue
        explored.add(key)

        if problem.is_goal(state):
            # Reconstruir ruta de estados y acciones
            ruta_estados = []
            ruta_acciones = []
            current = node
            while current is not None:
                ruta_estados.append(current.state)
                if current.action is not None:
                    ruta_acciones.append(current.action)
                current = current.parent
            ruta_estados.reverse()
            ruta_acciones.reverse()
            return ruta_estados, ruta_acciones, node.path_cost

        for succ in expand(node, problem):
            succ_key = (succ.state['edificio'], succ.state['piso'], succ.state['coordenada'])
            if succ_key not in explored:
                heapq.heappush(frontier, succ)

    return None, None, float('inf')

# ---------------------------
# Ejemplos de uso
# ---------------------------

def print_resultado(nombre_caso, ruta_estados, ruta_acciones, costo):
    """Imprime el resultado de una búsqueda de manera formateada"""
    print(f"\n{'='*70}")
    print(f"CASO: {nombre_caso}")
    print(f"{'='*70}")
    
    if ruta_estados is None:
        print("❌ No se encontró ruta.")
        return
    
    print(f"✓ Ruta encontrada con costo total: {costo}")
    print(f"\n📋 Acciones ({len(ruta_acciones)}):")
    print(ruta_acciones)
    
    print(f"\n🗺️  Secuencia de estados ({len(ruta_estados)}):")
    for i, estado in enumerate(ruta_estados):
        coord = estado['coordenada']
        print(f"  {i+1}. {estado['edificio']:12} | Piso {estado['piso']} | ({coord[0]:2}, {coord[1]:2})")
    print()


def ejemplo_1():
    """Ejemplo 1: Mismo piso, solo movimiento horizontal"""
    start = {
        'edificio': edificio_from_coord((0, 0)),
        'piso': 1,
        'coordenada': (0, 0)
    }
    
    goal = {
        'edificio': 'B30',
        'piso': 1,
        'coordenada': BUILDING_COORDS['B30']
    }
    
    problem = Problem(initial=start, goal=goal)
    ruta_estados, ruta_acciones, costo = astar_search(problem)
    print_resultado("Ejemplo 1: (0,0) → B30 Piso 1", ruta_estados, ruta_acciones, costo)


def ejemplo_2():
    """Ejemplo 2: Cambiando de piso con ascensor"""
    start = {
        'edificio': 'B32',
        'piso': 1,
        'coordenada': BUILDING_COORDS['B32']
    }
    
    goal = {
        'edificio': 'B32',
        'piso': 3,
        'coordenada': BUILDING_COORDS['B32']
    }
    
    problem = Problem(initial=start, goal=goal)
    ruta_estados, ruta_acciones, costo = astar_search(problem)
    print_resultado("Ejemplo 2: B32 Piso 1 → B32 Piso 3 (con ascensor)", ruta_estados, ruta_acciones, costo)


def ejemplo_3():
    """Ejemplo 3: Ruta compleja con cambio de edificio y piso"""
    start = {
        'edificio': 'B30',
        'piso': 1,
        'coordenada': BUILDING_COORDS['B30']
    }
    
    goal = {
        'edificio': 'Biblioteca',
        'piso': 2,
        'coordenada': BUILDING_COORDS['Biblioteca']
    }
    
    problem = Problem(initial=start, goal=goal)
    ruta_estados, ruta_acciones, costo = astar_search(problem)
    print_resultado("Ejemplo 3: B30 Piso 1 → Biblioteca Piso 2", ruta_estados, ruta_acciones, costo)


def ejemplo_4():
    """Ejemplo 4: Usando escaleras en edificio sin ascensor"""
    start = {
        'edificio': 'B30',
        'piso': 1,
        'coordenada': BUILDING_COORDS['B30']
    }
    
    goal = {
        'edificio': 'B30',
        'piso': 2,
        'coordenada': BUILDING_COORDS['B30']
    }
    
    problem = Problem(initial=start, goal=goal)
    ruta_estados, ruta_acciones, costo = astar_search(problem)
    print_resultado("Ejemplo 4: B30 Piso 1 → B30 Piso 2 (solo escaleras)", ruta_estados, ruta_acciones, costo)


def ejemplo_5():
    """Ejemplo 5: De B35 con ascensor a Cafetería"""
    start = {
        'edificio': 'B35',
        'piso': 1,
        'coordenada': BUILDING_COORDS['B35']
    }
    
    goal = {
        'edificio': 'Cafetería',
        'piso': 1,
        'coordenada': BUILDING_COORDS['Cafetería']
    }
    
    problem = Problem(initial=start, goal=goal)
    ruta_estados, ruta_acciones, costo = astar_search(problem)
    print_resultado("Ejemplo 5: B35 Piso 1 → Cafetería Piso 1", ruta_estados, ruta_acciones, costo)


if __name__ == "__main__":
    print("\n" + "="*70)
    print(" "*15 + "🎓 NAVEGACIÓN EN CAMPUS CON A* 🎓")
    print("="*70)
    
    # Ejecutar todos los ejemplos
    ejemplo_1()
    ejemplo_2()
    ejemplo_3()
    ejemplo_4()
    ejemplo_5()
    
    print("\n" + "="*70)
    print(" "*20 + "✓ PRUEBAS COMPLETADAS")
    print("="*70 + "\n")

