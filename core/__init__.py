import numpy as np
from typing import Dict, List
from core.quadtree import build_quadtree, get_nodes_at_level, QuadtreeNode
from core.morton import sort_nodes_by_morton
from core.hilbert import sort_nodes_by_hilbert

def process_face_to_layers(matrix: np.ndarray, curve_name: str) -> Dict[str, List[QuadtreeNode]]:
    """
    Строит квадродерево по матрице лица и сортирует узлы уровней 
    согласно выбранной фрактальной траектории.
    """
    size = matrix.shape[0]
    # Наш оркестр работает на уровнях 2, 3 и 4
    root = build_quadtree(matrix, x=0, y=0, size=size, level=0, max_level=4)
    
    # Извлекаем сырые слои
    layers = {
        'large':  get_nodes_at_level(root, target_level=2), # БАС (Сетка 4x4 = 16 нот)
        'medium': get_nodes_at_level(root, target_level=3), # МИД (Сетка 8x8 = 64 ноты)
        'small':  get_nodes_at_level(root, target_level=4)  # ТОП (Сетка 16x16 = 256 нот)
    }
    
    # Сортируем каждый слой согласно выбранной ДРАКОН-стратегии
    match curve_name:
        case "Развертка Мортона (Z-кривая)":
            for key in layers:
                layers[key] = sort_nodes_by_morton(layers[key])
        case "Кривая Гильберта (Плавное легато)":
            for key in layers:
                layers[key] = sort_nodes_by_hilbert(layers[key], size)
        case _:
            # Временный фолбек для Пеано
            pass
            
    return layers
