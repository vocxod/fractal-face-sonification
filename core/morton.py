from typing import List
from core.quadtree import QuadtreeNode, get_nodes_at_level

def sort_nodes_by_morton(nodes: List[QuadtreeNode]) -> List[QuadtreeNode]:
    """
    Сортирует узлы квадродерева по Z-кривой (коду Мортона).
    Код Мортона получается путем перемежения битов координат X и Y.
    """
    def sfc_index(node: QuadtreeNode) -> int:
        # Перемежение битов координат X и Y
        x, y = node.x, node.y
        index = 0
        for i in range(16): # Поддержка матриц до 65536x65536
            index |= ((x & (1 << i)) << i) | ((y & (1 << i)) << (i + 1))
        return index

    return sorted(nodes, key=sfc_index)
