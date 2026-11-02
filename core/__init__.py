from typing import List, Tuple
# Импортируем будущие функции генерации траекторий
from core.morton import generate_morton_path
from core.hilbert import generate_hilbert_path
from core.peano import generate_peano_path

def get_fractal_path(curve_name: str, size: int) -> List[Tuple[int, int]]:
    """
    ДРАКОН-переключатель траектории.
    Принимает название кривой из интерфейса и размер квадратной матрицы.
    Возвращает упорядоченный список координат (x, y) для обхода.
    """
    match curve_name:
        case "Развертка Мортона (Z-кривая)":
            return generate_morton_path(size)
            
        case "Кривая Гильберта (Плавное легато)":
            return generate_hilbert_path(size)
            
        case "Кривая Пеано (Полиритмия 3x3)":
            return generate_peano_path(size)
            
        case _:
            # Безопасный фолбек на случай непредвиденного значения
            raise ValueError(f"Неизвестный тип фрактальной кривой: {curve_name}")

