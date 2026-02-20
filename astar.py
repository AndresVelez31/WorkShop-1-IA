"""
================================================================================
NAVEGACIÓN EN CAMPUS UNIVERSITARIO USANDO A* (A-STAR)
================================================================================

Este programa implementa el algoritmo de búsqueda A* para encontrar el camino
óptimo entre edificios en un campus universitario con múltiples pisos.

Características del campus:
- Grilla 2D de 17x16 (x: 0-16, y: 0-15)
- Edificios B30-B38, Cafetería y Biblioteca
- 3 pisos por edificio
- Algunos edificios tienen ascensor (B32, B33, B35, B37, B38)
- Todos los edificios tienen escaleras
- Movimiento horizontal solo permitido en el piso 1

Costos de acciones:
- Movimiento horizontal (arriba/abajo/izquierda/derecha): 1
- Ascensor (subir/bajar): 3
- Escaleras subir: 7 + número_de_pisos
- Escaleras bajar: 5 * número_de_pisos

Heurística: Distancia euclídea entre coordenadas (ignorando diferencia de pisos)
================================================================================
"""

import heapq
import math

# ============================================================================
# CONSTANTES DEL MAPA Y CONFIGURACIÓN DEL CAMPUS
# ============================================================================

GRID_W = 17   # Ancho de la grilla: x va de 0 a 16
GRID_H = 16   # Alto de la grilla: y va de 0 a 15

# Mapa del campus: ' ' = espacio transitable, '#' = pared/obstáculo
# 'B30'-'B38' = edificios, 'C' = Cafetería, 'B' = Biblioteca
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

# ============================================================================
# CONFIGURACIÓN DE EDIFICIOS Y COORDENADAS
# ============================================================================

# Diccionario que mapea cada edificio a su coordenada (x, y) en la grilla
# Estas son las posiciones exactas donde se encuentran los edificios en el mapa
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

# Conjunto de edificios que tienen ascensor (los demás solo tienen escaleras)
BUILDINGS_WITH_ELEVATORS = {'B32', 'B33', 'B35', 'B37', 'B38'}

# Conjunto de todos los edificios del campus
BUILDINGS = set(BUILDING_COORDS.keys())

# ============================================================================
# FUNCIONES AUXILIARES PARA EL MAPA
# ============================================================================

def edificio_from_coord(coord):
    """
    Determina qué edificio se encuentra en una coordenada dada.
    
    Args:
        coord (tuple): Tupla (x, y) con la posición en la grilla
    
    Returns:
        str: Nombre del edificio si coincide con alguna coordenada,
             'Pasillo' en caso contrario
    """
    for name, c in BUILDING_COORDS.items():
        if coord == c:
            return name
    return 'Pasillo'


def is_transitable(coord):
    """
    Verifica si una coordenada es transitable (no es pared ni está fuera del mapa).
    
    Args:
        coord (tuple): Tupla (x, y) con la posición a verificar
    
    Returns:
        bool: True si la posición es transitable, False si es pared o fuera de límites
    """
    x, y = coord
    if 0 <= x < GRID_W and 0 <= y < GRID_H:
        cell = CAMPUS_MAP[y][x]
        return cell != '#'
    return False

# ============================================================================
# DEFINICIÓN DE ACCIONES Y COSTOS
# ============================================================================

# Diccionario de movimientos en el plano (solo permitidos en piso 1)
# Cada movimiento se define como un desplazamiento (dx, dy)
PLAN_MOVES = {
    'arriba':    (0, -1),
    'abajo':     (0, 1),
    'izquierda': (-1, 0),
    'derecha':    (1, 0),
}

# Diccionario de costos para cada tipo de acción
# Los costos de escaleras se calculan dinámicamente según el número de pisos
ACTION_COSTS = {
    'mover': 1,
    'subir_ascensor': 3,
    'bajar_ascensor': 3,
    'subir_escaleras': None,  # se calculará dinámicamente
    'bajar_escaleras': 5,
}

# ============================================================================
# ESTRUCTURAS DE DATOS PARA EL ALGORITMO A*
# ============================================================================

class Node:
    """
    Representa un nodo en el árbol de búsqueda.
    
    Cada nodo contiene:
    - state: diccionario con 'edificio', 'piso' y 'coordenada'
    - parent: nodo padre en el árbol de búsqueda
    - action: acción que llevó a este estado desde el padre
    - path_cost: costo acumulado g(n) desde el nodo inicial
    - f_value: valor de evaluación f(n) = g(n) + h(n)
    
    El método __lt__ permite usar heapq para mantener una cola de prioridad
    basada en el valor f(n).
    """
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


class Problem:
    """
    Define el problema de búsqueda con estado inicial, objetivo y heurística.
    
    Atributos:
    - initial: estado inicial (dict con 'edificio', 'piso', 'coordenada')
    - goal: estado objetivo (dict con 'edificio', 'piso', 'coordenada')
    
    Métodos:
    - is_goal(state): verifica si un estado es el objetivo
    - h(state): calcula la heurística (distancia euclídea) para un estado
    """
    def __init__(self, initial, goal):
        self.initial = initial
        self.goal = goal

    def is_goal(self, state):
        """
        Verifica si un estado es el objetivo.
        
        Args:
            state (dict): Estado a verificar
        
        Returns:
            bool: True si coinciden coordenada Y piso con el objetivo
        """
        return state['coordenada'] == self.goal['coordenada'] and state['piso'] == self.goal['piso']

    def h(self, state):
        """
        Heurística: distancia euclídea en el plano (ignorando diferencia de pisos).
        
        Esta heurística es admisible porque nunca sobreestima el costo real,
        ya que la distancia en línea recta es siempre menor o igual que
        cualquier camino Manhattan en la grilla.
        
        Args:
            state (dict): Estado actual
        
        Returns:
            float: Distancia euclídea hasta las coordenadas del objetivo
        """
        x1, y1 = state['coordenada']
        x2, y2 = self.goal['coordenada']
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

# ============================================================================
# FUNCIÓN DE EVALUACIÓN Y EXPANSIÓN DE NODOS
# ============================================================================

def f(node, problem):
    """
    Calcula el valor de evaluación f(n) = g(n) + h(n) para un nodo.
    
    - g(n): costo del camino desde el inicio hasta el nodo (node.path_cost)
    - h(n): estimación heurística del costo desde el nodo hasta el objetivo
    
    Args:
        node (Node): Nodo a evaluar
        problem (Problem): Problema con la función heurística
    
    Returns:
        float: Valor f(n) = g(n) + h(n)
    """
    return node.path_cost + problem.h(node.state)


def expand(node, problem):
    """
    Genera todos los sucesores válidos de un nodo aplicando todas las acciones posibles.
    
    Las acciones disponibles dependen del estado actual:
    1. Movimiento horizontal (arriba/abajo/izquierda/derecha): Solo en piso 1
    2. Ascensor (subir/bajar): Solo en edificios con ascensor (B32, B33, B35, B37, B38)
    3. Escaleras (subir/bajar): En cualquier edificio (excepto pasillos)
    
    Restricción importante: NO se puede mover horizontalmente si no estás en piso 1.
    Primero debes bajar al piso 1, luego moverte, y después subir si es necesario.
    
    Args:
        node (Node): Nodo a expandir
        problem (Problem): Problema para calcular f(n)
    
    Returns:
        list: Lista de nodos sucesores válidos
    """
    successors = []
    state = node.state
    edificio = state['edificio']
    piso = state['piso']
    coord = state['coordenada']

    # 1) Movimientos en el plano (arriba, abajo, izquierda, derecha)
    # SOLO se puede mover en el plano si está en el piso 1
    if piso == 1:
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

# ============================================================================
# ALGORITMO RBFS (RECURSIVE BEST-FIRST SEARCH)
# ============================================================================
# NOTA: Este algoritmo no se utiliza en los ejemplos, pero está disponible.
# RBFS es una variante de A* que usa memoria limitada, útil para espacios
# de búsqueda muy grandes donde A* normal consumiría demasiada memoria.
# ============================================================================

def recursive_best_first_search(problem):
    """
    Implementa el algoritmo RBFS (Recursive Best-First Search).
    
    RBFS es similar a A* pero usa menos memoria al expandir solo el camino
    más prometedor y mantener un límite f. Si el mejor camino excede el límite,
    retrocede y prueba alternativas.
    
    Args:
        problem (Problem): Problema a resolver
    
    Returns:
        tuple: (nodo_objetivo, valor_f) si encuentra solución, (None, inf) si no
    """
    initial_node = Node(problem.initial, path_cost=0, f_value=problem.h(problem.initial))
    return rbfs(problem, initial_node, float('inf'))


def rbfs(problem, node, f_limit):
    """
    Función recursiva auxiliar para RBFS.
    
    Explora el árbol de búsqueda manteniendo un límite f. Si el mejor
    sucesor excede el límite, retrocede y actualiza el valor f del nodo.
    
    Args:
        problem (Problem): Problema a resolver
        node (Node): Nodo actual
        f_limit (float): Límite superior para el valor f
    
    Returns:
        tuple: (nodo_objetivo, nuevo_f_limit)
    """
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


# ============================================================================
# ALGORITMO A* (PRINCIPAL)
# ============================================================================
# Este es el algoritmo principal usado para encontrar caminos óptimos.
# A* combina el costo del camino g(n) con la heurística h(n) para explorar
# eficientemente el espacio de búsqueda, garantizando encontrar el camino
# de menor costo cuando la heurística es admisible.
# ============================================================================

def astar_search(problem, max_iters=100000):
    """
    Implementa el algoritmo A* para encontrar el camino óptimo.
    
    A* mantiene dos conjuntos:
    - frontier (frontera): nodos por explorar, ordenados por f(n)
    - explored (explorados): nodos ya visitados
    
    El algoritmo expande el nodo con menor f(n) en cada iteración,
    garantizando encontrar el camino óptimo si la heurística es admisible.
    
    Args:
        problem (Problem): Problema a resolver
        max_iters (int): Número máximo de iteraciones para evitar bucles infinitos
    
    Returns:
        tuple: (ruta_estados, ruta_acciones, costo_total) si encuentra solución
               (None, None, inf) si no encuentra solución
    """
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

# ============================================================================
# FUNCIONES DE VISUALIZACIÓN Y EJEMPLOS
# ============================================================================

def print_resultado(nombre_caso, ruta_estados, ruta_acciones, costo):
    """
    Imprime el resultado de una búsqueda de manera formateada y legible.
    
    Muestra:
    - Nombre del caso de prueba
    - Costo total del camino
    - Lista de acciones tomadas
    - Secuencia completa de estados visitados
    
    Args:
        nombre_caso (str): Descripción del caso de prueba
        ruta_estados (list): Lista de estados visitados
        ruta_acciones (list): Lista de acciones tomadas
        costo (float): Costo total del camino
    """
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


# ============================================================================
# EJEMPLOS DE PRUEBA
# ============================================================================
# Los siguientes ejemplos demuestran diferentes escenarios:
# 1. Movimiento horizontal simple
# 2. Cambio de piso con ascensor
# 3. Ruta compleja con múltiples edificios y cambio de piso
# 4. Uso de escaleras en edificio sin ascensor
# 5. Navegación entre edificios
# ============================================================================

def ejemplo_1():
    """
    Ejemplo 1: Movimiento horizontal simple en el mismo piso.
    
    Demuestra el caso más básico: moverse de un punto a otro
    en el piso 1 sin cambiar de piso.
    """
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
    """
    Ejemplo 2: Cambio de piso usando ascensor.
    
    Demuestra el uso del ascensor para subir múltiples pisos
    en un edificio que tiene ascensor (B32).
    """
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
    """
    Ejemplo 3: Ruta compleja con cambio de edificio y piso.
    
    Demuestra una navegación más compleja que requiere:
    - Moverse horizontalmente entre edificios
    - Cambiar de piso al llegar al destino
    - Optimizar la elección entre ascensor y escaleras
    """
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
    """
    Ejemplo 4: Uso de escaleras en edificio sin ascensor.
    
    Demuestra el caso donde el edificio (B30) no tiene ascensor,
    por lo que solo puede usar escaleras para cambiar de piso.
    Compara el costo de escaleras vs ascensor.
    """
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
    """
    Ejemplo 5: Navegación entre edificios en el mismo piso.
    
    Demuestra una ruta horizontal sin cambios de piso,
    desde B35 (que tiene ascensor) hasta la Cafetería.
    """
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


# ============================================================================
# FUNCIÓN PARA PRUEBAS PERSONALIZADAS
# ============================================================================

def prueba_personalizada(start_edificio, start_piso, goal_edificio, goal_piso):
    """
    Ejecuta una prueba personalizada con parámetros definidos por el usuario.
    
    Permite probar cualquier combinación de edificio inicial/final y piso.
    
    Args:
        start_edificio (str): Nombre del edificio de inicio
        start_piso (int): Piso de inicio (1-3)
        goal_edificio (str): Nombre del edificio objetivo
        goal_piso (int): Piso objetivo (1-3)
    """
    start = {
        'edificio': start_edificio,
        'piso': start_piso,
        'coordenada': BUILDING_COORDS.get(start_edificio, (0, 0))  # Si no se encuentra, usar (0,0)
    }
    
    goal = {
        'edificio': goal_edificio,
        'piso': goal_piso,
        'coordenada': BUILDING_COORDS.get(goal_edificio, (0, 0))  # Si no se encuentra, usar (0,0)
    }
    
    problem = Problem(initial=start, goal=goal)
    ruta_estados, ruta_acciones, costo = astar_search(problem)
    print_resultado(f"Prueba Personalizada: {start_edificio} Piso {start_piso} → {goal_edificio} Piso {goal_piso}", ruta_estados, ruta_acciones, costo)


# ============================================================================
# MENÚ INTERACTIVO
# ============================================================================

def menu():
    """
    Menú interactivo para ejecutar ejemplos o pruebas personalizadas.
    
    Opciones:
    [1] Ejecutar los 5 ejemplos predeterminados
    [2] Crear una prueba personalizada con edificios y pisos a elección
    [0] Salir del programa
    """
    print("\n" + "="*70)
    print(" "*20 + "NAVEGACIÓN EN CAMPUS CON A*")
    print("="*70)
    print("Seleccione un ejemplo para ejecutar:")
    print("[1] Ejemplos Predeterminados")
    print("[2] Prueba Personalizada")
    print("[0] Salir")
    
    opcion = input("Ingrese su opción: ")

    if opcion == '1':
        print("\nEjecutando ejemplos predeterminados...")
        ejemplo_1()
        ejemplo_2()
        ejemplo_3()
        ejemplo_4()
        ejemplo_5()
        print("\n" + "="*70)
        print(" "*20 + "✓ PRUEBAS COMPLETADAS")
        print("="*70 + "\n")
    elif opcion == '2':
        print("\nVamos a crear tu propia prueba personalizada.")
        print("Ingresa el punto de inicio:")
        start_edificio = input("Edificio de inicio (B30, B31, B32, B33, B34, B35, B36, B37, B38, Cafetería, Biblioteca): ")
        start_piso = int(input("Piso de inicio (1, 2, o 3): "))
        print("\nIngresa el punto objetivo:")
        goal_edificio = input("Edificio objetivo (B30, B31, B32, B33, B34, B35, B36, B37, B38, Cafetería, Biblioteca): ")
        goal_piso = int(input("Piso objetivo (1, 2, o 3): "))
        
        prueba_personalizada(start_edificio, start_piso, goal_edificio, goal_piso)
        
        print("\n" + "="*70)
        print(" "*20 + "PRUEBA COMPLETADA")
        print("="*70 + "\n")

    elif opcion == '0':
        print("\n¡Hasta luego!")
    else:
        print("\nOpción inválida. Por favor intente de nuevo.")


# ============================================================================
# PUNTO DE ENTRADA DEL PROGRAMA
# ============================================================================

if __name__ == "__main__":
    """
    Ejecuta el menú interactivo cuando el script se ejecuta directamente.
    
    Para usar este código como módulo en otro programa, puedes importar
    las funciones directamente sin ejecutar el menú:
    
        from astar import astar_search, Problem, BUILDING_COORDS
    """
    menu()