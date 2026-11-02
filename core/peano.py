from typing import List, Tuple

def generate_peano_path(size: int) -> List[Tuple[int, int]]:
    """
    Генерирует непрерывную траекторию кривой Гильберта (без скачков).
    """
    path = []
    # Заглушка: в полноценной версии здесь будет рекурсивный обход 
    # с поворотом U-образных элементов на 90 градусов
    for x in range(size):
        if x % 2 == 0:
            for y in range(size):
                path.append((x, y))
        else:
            for y in range(size - 1, -1, -1):
                path.append((x, y))
    return path
