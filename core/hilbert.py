from typing import List
from core.quadtree import QuadtreeNode

def sort_nodes_by_hilbert(nodes: List[QuadtreeNode], size: int) -> List[QuadtreeNode]:
    """
    Сортирует узлы по непрерывной кривой Гильберта.
    """
    def xy2d(n: int, x: int, y: int) -> int:
        """ Перевод координат X, Y в расстояние d вдоль кривой Гильберта """
        d = 0
        s = n // 2
        while s > 0:
            rx = (x & s) > 0
            ry = (y & s) > 0
            d += s * s * ((3 * rx) ^ ry)
            # Вращаем квадранты
            if ry == 0:
                if rx == 1:
                    x = s - 1 - x
                    y = s - 1 - y
                x, y = y, x
            s //= 2
        return d

    return sorted(nodes, key=lambda node: xy2d(size, node.x, node.y))
