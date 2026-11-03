import cv2
import numpy as np
import mediapipe as mp


def position_by_eyes(image_bgr, target_size=256):
    """
    Стратегия 1: Позиционирование по глазам с помощью анализа проекций яркости.
    Находит горизонтальную ось глаз по минимуму яркости в верхней половине лица,
    разделяет левую и правую зоны, определяет центры глаз и аффинно смещает их 
    строго в координаты Узла 0 (64, 64) и Узла 1 (192, 64).
    """
    # 1. Гарантируем перевод в Ч/Б и приведение к базовому размеру для анализа
    if len(image_bgr.shape) == 3:
        gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    else:
        gray = image_bgr
        
    gray_res = cv2.resize(gray, (target_size, target_size), interpolation=cv2.INTER_AREA)
    
    # 2. Ищем область глаз с помощью интегрального профиля яркости (горизонтальный срез)
    # Глаза гарантированно лежат в диапазоне от 20% до 55% высоты лица
    search_top = int(target_size * 0.20)
    search_bottom = int(target_size * 0.55)
    roi_eyes_zone = gray_res[search_top:search_bottom, :]
    
    # Считаем среднюю яркость каждой строки. Строка с глазами — самая темная (минимум яркости)
    row_means = np.mean(roi_eyes_zone, axis=1)
    eye_y_relative = np.argmin(row_means)
    eye_y = search_top + eye_y_relative  # Абсолютная координата Y оси глаз
    
    # 3. Разделяем левую и правую половины для поиска точного центра каждого глаза по оси X
    # Берем узкую горизонтальную полосу шириной 16 пикселей вокруг найденной оси Y
    strip_top = max(0, eye_y - 8)
    strip_bottom = min(target_size, eye_y + 8)
    eye_strip = gray_res[strip_top:strip_bottom, :]
    
    # Левая половина (для левого глаза) и правая половина (для правого глаза)
    left_half = eye_strip[:, :target_size // 2]
    right_half = eye_strip[:, target_size // 2:]
    
    # Ищем самые темные вертикальные столбцы (центры зрачков по X)
    left_x = np.argmin(np.mean(left_half, axis=0))
    right_x = (target_size // 2) + np.argmin(np.mean(right_half, axis=0))
    
    # Координаты реальных центров глаз
    p_left = np.array([left_x, eye_y], dtype=np.float32)
    p_right = np.array([right_x, eye_y], dtype=np.float32)
    
    # 4. --- МАТЕМАТИКА АФФИННОГО ВЫРАВНИВАНИЯ ---
    # Наши жесткие целевые точки квадродерева первого уровня
    target_left = np.array([64.0, 64.0], dtype=np.float32)
    target_right = np.array([192.0, 64.0], dtype=np.float32)
    
    # Вычисляем угол наклона (если лицо наклонено на фото)
    d_x, d_y = p_right - p_left
    angle = np.degrees(np.arctan2(d_y, d_x))
    
    # Расстояние между глазами
    dist_real = np.linalg.norm(p_right - p_left)
    dist_target = 128.0  # 192 - 64
    
    # Если точки определились некорректно (слишком близко), уходим на безопасный центр
    if dist_real < 20:
        return gray_res, False
        
    scale = dist_target / dist_real
    
    # Центроиды
    center_real = (p_left + p_right) / 2.0
    center_target = (target_left + target_right) / 2.0
    
    # Строим матрицу трансформации OpenCV (Поворот + Масштаб)
    M = cv2.getRotationMatrix2D(tuple(center_real), angle, scale)
    
    # Корректируем сдвиг, чтобы центры идеально совпали с (64,64) и (192,64)
    M[0, 2] += center_target[0] - center_real[0]
    M[1, 2] += center_target[1] - center_real[1]
    
    # Применяем трансформацию ко всей матрице лица
    aligned_face = cv2.warpAffine(gray, M, (target_size, target_size), flags=cv2.INTER_AREA)
    
    return aligned_face, True


def position_by_center(image_bgr, target_size=256):
    """
    Стратегия 2: Простое кадрирование по центру.
    """
    if len(image_bgr.shape) == 2:
        gray = image_bgr
    else:
        gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
        
    h, w = gray.shape[:2]
    crop_size = min(h, w)
    start_x = (w - crop_size) // 2
    start_y = (h - crop_size) // 2
    face_square = gray[start_y:start_y+crop_size, start_x:start_x+crop_size]
    return cv2.resize(face_square, (target_size, target_size), interpolation=cv2.INTER_AREA)


def get_positioned_face(image_bgr, strategy_name, target_size=256):
    """
    ДРАКОН-переключатель стратегий предварительной подготовки лица.
    """
    match strategy_name:
        case "Позиционирование по глазам (Жесткая фрактальная сетка)":
            return position_by_eyes(image_bgr, target_size)
        case "Простое кадрирование по центру холста":
            return position_by_center(image_bgr, target_size), True
        case _:
            return position_by_center(image_bgr, target_size), False


def process_and_center_face(image_bgr, target_size=256):
    """
    Принимает предварительно подготовленное пользователем изображение,
    гарантирует перевод в Ч/Б и размер target_size x target_size.
    """
    # Если изображение уже одноканальное (серое)
    if len(image_bgr.shape) == 2:
        gray = image_bgr
    else:
        # Если загружено как цветное, переводим в градации серого
        gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    
    # Изменяем размер до целевого (256x256), если он отличается
    if gray.shape[0] != target_size or gray.shape[1] != target_size:
        gray = cv2.resize(gray, (target_size, target_size), interpolation=cv2.INTER_AREA)
        
    return gray, True


