import numpy as np
from typing import List, Dict, Any, Tuple

class QuadtreeNode:
    def __init__(self, x: int, y: int, size: int, level: int):
        self.x = x            # Координата X верхнего левого угла на матрице
        self.y = y            # Координата Y верхнего левого угла на матрице
        self.size = size      # Размер стороны квадрата (в пикселях)
        self.level = level    # Уровень вложенности (0 - корень, 1 - 2x2, 2 - 4x4 и т.д.)
        self.brightness = 0.0 # Средняя яркость этого квадранта (0-255)
        self.children: List['QuadtreeNode'] = [] # 4 потомка

    def is_leaf(self) -> bool:
        return len(self.children) == 0

def build_quadtree(matrix: np.ndarray, x: int, y: int, size: int, level: int, max_level: int) -> QuadtreeNode:
    """
    Рекурсивно строит полное квадродерево до уровня max_level.
    Рассчитывает среднюю яркость для каждого узла.
    """
    node = QuadtreeNode(x, y, size, level)
    
    # Считаем среднюю яркость в этой зоне
    roi = matrix[y:y+size, x:x+size]
    node.brightness = float(np.mean(roi)) if roi.size > 0 else 0.0
    
    # Базовый случай: достигли максимальной глубины сканирования
    if level >= max_level or size <= 1:
        return node
        
    half = size // 2
    
    # Создаем 4 потомков (пока в стандартном порядке координат)
    # 0: Верхний левый, 1: Верхний правый, 2: Нижний левый, 3: Нижний правый
    node.children.append(build_quadtree(matrix, x, y, half, level + 1, max_level))
    node.children.append(build_quadtree(matrix, x + half, y, half, level + 1, max_level))
    node.children.append(build_quadtree(matrix, x, y + half, half, level + 1, max_level))
    node.children.append(build_quadtree(matrix, x + half, y + half, half, level + 1, max_level))
    
    return node

def get_nodes_at_level(node: QuadtreeNode, target_level: int) -> List[QuadtreeNode]:
    """ Возвращает все узлы дерева, находящиеся на строго заданном уровне """
    if node.level == target_level:
        return [node]
    
    nodes = []
    for child in node.children:
        nodes.extend(get_nodes_at_level(child, target_level))
    return nodes
