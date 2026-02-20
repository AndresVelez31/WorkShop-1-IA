<div align="center">
 
  <h1>🤖 Workshop 1 - Inteligencia Artificial </h1>
  

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Jupyter](https://img.shields.io/badge/Jupyter-Notebook-orange.svg)
</div>

---

## 👥 Información del Equipo

| Nombre | Código |
|--------|--------|
| **Andres Felipe Velez Alvarez** | 1021923619 |
| **Nathalia Valentina Cardoza Azuaje** | 4992531 |
| **Sebastian Salazar Henao** | 1022003377 |

**Universidad:** Universidad EAFIT  
**Curso:** Inteligencia Artificial  
**Semestre:** 5to Semestre  
**Fecha:** Febrero 20, 2026

---

## 📋 Descripción del Proyecto

Este repositorio contiene la implementación de dos ejercicios prácticos fundamentales en inteligencia artificial:

1. **🗺️ Búsqueda A\*** - Navegación en campus universitario
2. **🧬 Algoritmo Genético** - Planificación de horarios de cursos

Ambos ejercicios demuestran la aplicación de técnicas clásicas de IA para resolver problemas de búsqueda y optimización.

---

## 🎯 Objetivos del Workshop

- ✅ Comprender el modelado de problemas en términos de estados, acciones, costos y objetivos
- ✅ Implementar y analizar algoritmos clásicos de IA (A\* y AG)
- ✅ Trabajar con descripciones formales y código base
- ✅ Desarrollar habilidades de programación en Python
- ✅ Analizar y comparar diferentes estrategias de búsqueda y optimización

---

## 📂 Estructura del Proyecto

```
Workshop 1/
│
├── 📓 Lab_ASTAR_AndresVelezNathaliaCardozaSebastianSalazar.ipynb    # Notebook A* completo con documentación
├── 🐍 astar.py    # Implementación A* en Python puro
├── 📓 Lab_AG_AndresVelezNathaliaCardozaSebastianSalazar.ipynb    #Notebook Algoritmo Genético completo
└── 📖 README.md    # Este archivo
```

---

## 🗺️ Ejercicio 1: Algoritmo A\* - Navegación en Campus

### 🎯 Objetivo
Implementar el algoritmo A\* para encontrar el camino óptimo entre diferentes ubicaciones en un campus universitario, considerando múltiples pisos y diferentes tipos de movimientos.

### 🔑 Características Principales

- **Mapa 2D tipo grilla** (17×16) con obstáculos
- **Sistema de 3 pisos** por edificio
- **Ascensores y escaleras** con costos diferenciados
- **Heurística admisible** (distancia euclídea)
- **5 ejemplos predefinidos** + pruebas personalizadas

### 🏢 Edificios del Campus

| Edificio | Coordenada | Ascensor |
|----------|------------|----------|
| B30-B34 | Fila superior | ❌ |
| B35-B38 | Fila media | ✅ |
| Cafetería | Central | ❌ |
| Biblioteca | Derecha | ❌ |

### 💰 Costos de Acciones

| Acción | Costo |
|--------|-------|
| Movimiento horizontal (1 casilla) | 1 |
| Ascensor (por piso) | 3 |
| Subir escaleras (por piso) | 7 + p |
| Bajar escaleras (por piso) | 5 × p |

### 🚀 Cómo Ejecutar

El libro de notas `Lab_ASTAR_AndresVelezNathaliaCardozaSebastianSalazar.ipynb` contiene la implementación completa con explicaciones detalladas. Para ejecutar el script Python independiente:
#### Script Python
```bash
python astar.py
```

### 📊 Ejemplos de Resultados

```
Ejemplo 1: (0,0) → B30 Piso 1
✓ Ruta encontrada con costo total: 12.0
Acciones: ['derecha', 'derecha', 'abajo', 'abajo']

Ejemplo 2: B32 Piso 1 → B32 Piso 3 (con ascensor)
✓ Ruta encontrada con costo total: 6.0
Acciones: ['subir_ascensor', 'subir_ascensor']
```

---

## 🧬 Ejercicio 2: Algoritmo Genético - Planificación de Horarios

### 🎯 Objetivo
Resolver el problema de planificación de horarios de cursos utilizando un algoritmo genético, optimizando restricciones duras y blandas.

### 📚 Problema

Asignar **8 cursos** en **5 bloques de tiempo** usando **3 salones**, respetando:

#### 🔴 Restricciones Duras (OBLIGATORIAS)
- No solapamiento de cursos en mismo salón/horario
- Capacidad suficiente del salón
- Profesores no pueden estar en dos lugares a la vez

#### 🟡 Restricciones Blandas (PREFERIBLES)
- Preferir horarios tempranos
- Uso eficiente de salones

### 🧬 Representación del Cromosoma

```python
individuo = [
    (bloque, salon),  # MAT
    (bloque, salon),  # FIS
    (bloque, salon),  # QUI
    # ... 8 cursos
]

# Ejemplo
[(1, 'A'), (2, 'B'), (3, 'C'), ...]
```

**Espacio de búsqueda:** 15^8 = 2,562,890,625 soluciones posibles

### ⚙️ Parámetros del Algoritmo

| Parámetro | Valor | Justificación |
|-----------|-------|---------------|
| Población | 30 | Balance diversidad/velocidad |
| Generaciones | 100 | Convergencia completa |
| Mutación | 20% | Exploración sin destruir soluciones |
| Elitismo | 2 mejores | Preservar calidad |
| Selección | Torneo-3 | Simple y efectivo |

### 🎁 Características Bonus Implementadas

1. ✅ **Cruce de dos puntos** - Mejor mezcla genética
2. ✅ **Mutación inteligente** - Corrige violaciones específicas
3. ✅ **Visualización con matplotlib** - Gráfico de evolución del fitness
4. ✅ **Restricción de proximidad** - Penaliza cursos relacionados muy cerca

### 🚀 Cómo Ejecutar

```bash
# Abrir el notebook
jupyter notebook Lab_AG_AndresVelezNathaliaCardozaSebastianSalazar.ipynb

# Ejecutar todas las celdas
# Runtime → Run all
```

### 📊 Resultados Esperados

```
MEJOR SOLUCIÓN
==============
✓ Fitness final: 185.0
✓ Generación de convergencia: 15-20
✓ Conflictos de salón: 0
✓ Violaciones de capacidad: 0
✓ Conflictos de profesor: 0
```

### 📈 Evolución del Fitness

El algoritmo converge rápidamente hacia soluciones válidas, con mejoras incrementales en restricciones blandas:

- Generaciones 1-10: Satisface restricciones duras
- Generaciones 11-30: Optimiza restricciones blandas
- Generaciones 31-100: Refinamiento fino

---

## 🛠️ Tecnologías Utilizadas

<div align="center">

| Tecnología | Uso |
|------------|-----|
| ![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white) | Lenguaje principal |
| ![Jupyter](https://img.shields.io/badge/Jupyter-F37626?style=for-the-badge&logo=jupyter&logoColor=white) | Notebooks interactivos |
| ![NumPy](https://img.shields.io/badge/NumPy-013243?style=for-the-badge&logo=numpy&logoColor=white) | Cálculos numéricos |
| ![Matplotlib](https://img.shields.io/badge/Matplotlib-11557c?style=for-the-badge&logo=python&logoColor=white) | Visualización |

</div>

### 📦 Dependencias

```python
# Librerías estándar
import random
import heapq
import math
import time
from typing import List, Tuple

# Librerías externas
import matplotlib.pyplot as plt  # Para visualización AG
```

---


## 🎓 Aprendizajes Clave

### A\* - Búsqueda Informada

```
✅ La heurística admisible garantiza optimalidad
✅ La cola de prioridad (heap) es crucial para eficiencia
✅ El manejo de estados explorados evita ciclos
✅ f(n) = g(n) + h(n) balancea costo real vs estimación
```

### Algoritmo Genético - Optimización

```
✅ La codificación del cromosoma debe ser simple y directa
✅ Las restricciones duras requieren penalizaciones mayores
✅ El balance exploración-explotación es fundamental
✅ El elitismo acelera convergencia sin perder diversidad
```

---

## 🔬 Análisis Comparativo

### A\* vs RBFS

| Aspecto | A\* | RBFS |
|---------|-----|------|
| Memoria | O(b^d) | O(bd) |
| Tiempo | Más rápido | Más lento (re-expansiones) |
| Optimalidad | ✅ | ✅ |
| Uso recomendado | Memoria disponible | Memoria limitada |

### Mutación Aleatoria vs Inteligente

| Aspecto | Aleatoria | Inteligente |
|---------|-----------|-------------|
| Convergencia | Más lenta | Más rápida |
| Diversidad | Alta | Media |
| Complejidad | Baja | Alta |
| Uso recomendado | Exploración | Explotación |

---

## 🚀 Instalación y Ejecución

### Requisitos Previos

```bash
# Python 3.8 o superior
python --version

# Jupyter Notebook
pip install jupyter

# Matplotlib (para AG)
pip install matplotlib
```

### Pasos de Instalación

```bash
# 1. Clonar o descargar el repositorio
cd "Workshop 1"

# 2. Instalar dependencias
pip install matplotlib

# 3. Ejecutar notebooks
jupyter notebook
```

---

## 🎯 Conclusiones

Este workshop demuestra la aplicación práctica de dos técnicas fundamentales en IA:

### A\* - Búsqueda Óptima
- ✅ Encuentra el camino de menor costo garantizado
- ✅ Eficiente con heurística admisible
- ✅ Aplicable a problemas de navegación y planificación

### Algoritmo Genético - Optimización Evolutiva
- ✅ Maneja espacios de búsqueda enormes (>2 mil millones)
- ✅ Flexible para restricciones múltiples
- ✅ No requiere conocimiento del dominio

**Ambos algoritmos son herramientas poderosas** que, usadas apropiadamente, pueden resolver problemas complejos del mundo real.

---

**Última actualización:** Febrero 20, 2026
