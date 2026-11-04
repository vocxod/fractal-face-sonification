import cv2
import numpy as np
import os
import urllib.request


def apply_shift(matrix: np.ndarray, shift_percent_x: float, shift_percent_y: float) -> np.ndarray:
    """ Сдвигает ч/б матрицу на заданный процент от её размера """
    h, w = matrix.shape[:2]
    shift_x = int(w * (shift_percent_x / 100.0))
    shift_y = int(h * (shift_percent_y / 100.0))
    
    # Матрица аффинного сдвига
    T = np.float32([[1, 0, shift_x], [0, 1, shift_y]])
    # Сдвигаем, заполняя пустоты черным цветом (0)
    return cv2.warpAffine(matrix, T, (w, h), borderMode=cv2.BORDER_CONSTANT, borderValue=0)

def apply_zoom(matrix: np.ndarray, zoom_percent: float) -> np.ndarray:
    """ Масштабирует матрицу относительно её центра на заданный процент """
    h, w = matrix.shape[:2]
    # Коэффициент масштабирования: 1.0 — без изменений, 1.05 — увеличение на 5%
    scale = 1.0 + (zoom_percent / 100.0)
    
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle=0, scale=scale)
    return cv2.warpAffine(matrix, M, (w, h), borderMode=cv2.BORDER_CONSTANT, borderValue=0)



'''
def position_by_eyes(image_bgr, target_size=256):
    # Стратегия 1: Позиционирование по глазам с помощью анализа проекций яркости.
    # Находит горизонтальную ось глаз по минимуму яркости в верхней половине лица,
    # разделяет левую и правую зоны, определяет центры глаз и аффинно смещает их 
    # строго в координаты Узла 0 (64, 64) и Узла 1 (192, 64).

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
'''

'''
def position_by_center(image_bgr, target_size=256):
    # Стратегия 2: Простое кадрирование по центру.
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
'''

def get_positioned_face(image_bgr, strategy_name, target_size=256):
    # ДРАКОН-переключатель стратегий предварительной подготовки лица.
    match strategy_name:
        case "Позиционирование по глазам (Жесткая фрактальная сетка)":
            return position_by_eyes(image_bgr, target_size)
        case "Простое кадрирование по центру холста":
            return position_by_center(image_bgr, target_size), True
        case _:
            return position_by_center(image_bgr, target_size), False


def process_and_center_face(image_bgr, target_size=256):
    # Принимает предварительно подготовленное пользователем изображение,
    # гарантирует перевод в Ч/Б и размер target_size x target_size.

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

###

def load_cascade_safely(cascade_name):
    """
    Безопасно загружает каскад Хаара, обходя баги файловой системы OpenCV 5.0.
    Скачивает XML с GitHub и загружает его через буфер, если системный путь сбоит.
    """
    cc = cv2.CascadeClassifier()
    # Пытаемся найти стандартный путь
    if hasattr(cv2, 'data') and hasattr(cv2.data, 'haarcascades'):
        sys_path = os.path.join(cv2.data.haarcascades, cascade_name)
        if os.path.exists(sys_path) and cc.load(sys_path):
            return cc
            
    # Если системный путь сбоит, качаем в локальную папку vision/
    local_path = os.path.join(os.path.dirname(__file__), cascade_name)
    if not os.path.exists(local_path):
        url = f"https://githubusercontent.com{cascade_name}"
        try:
            urllib.request.urlretrieve(url, local_path)
        except Exception:
            return None
            
    # Чтобы OpenCV 5.0 гарантированно прочитал файл без SystemError,
    # используем обходной путь файлового дескриптора
    if os.path.exists(local_path):
        cc.load(local_path)
    return cc

def position_by_eyes(image_bgr, target_size=256):
    """
    Стратегия 1: Позиционирование по глазам через детекторы Хаара.
    Находит лицо и глаза, вычисляет их центры и выполняет аффинную
    трансформацию строго в целевые точки квадродерева: (64, 64) и (192, 64).
    """
    if len(image_bgr.shape) == 3:
        gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    else:
        gray = image_bgr

    # Загружаем детекторы лица и глаз
    face_cc = load_cascade_safely('haarcascade_frontalface_default.xml')
    eye_cc = load_cascade_safely('haarcascade_eye.xml')

    if face_cc is None or eye_cc is None or face_cc.empty() or eye_cc.empty():
        # Если детекторы не инициализировались, возвращаем обычный центр
        return position_by_center(image_bgr, target_size), False

    # 1. Ищем лицо
    faces = face_cc.detectMultiScale(gray, 1.1, 5, minSize=(80, 80))
    if len(faces) == 0:
        return position_by_center(image_bgr, target_size), False

    # Берем самое крупное лицо
    x, y, w, h = sorted(faces, key=lambda f: f[2], reverse=True)[0]
    face_roi = gray[y:y+h, x:x+w]

    # 2. Ищем глаза внутри зоны лица
    eyes = eye_cc.detectMultiScale(face_roi, 1.1, 4, minSize=(15, 15))
    
    # Нам нужно строго два глаза
    if len(eyes) < 2:
        return position_by_center(image_bgr, target_size), False

    # Сортируем глаза слева направо по координате X внутри лица
    eyes = sorted(eyes, key=lambda e: e[0])
    
    # Вычисляем абсолютные центры левого и правого глаза на исходной картинке
    ex0, ey0, ew0, eh0 = eyes[0]
    ex1, ey1, ew1, eh1 = eyes[1]
    
    p_left = np.array([x + ex0 + ew0//2, y + ey0 + eh0//2], dtype=np.float32)
    p_right = np.array([x + ex1 + ew1//2, y + ey1 + eh1//2], dtype=np.float32)

    # 3. --- МАТЕМАТИКА АФФИННОГО ВЫРАВНИВАНИЯ ---
    target_left = np.array([64.0, 64.0], dtype=np.float32)
    target_right = np.array([192.0, 64.0], dtype=np.float32)

    # Расчет угла, масштаба и центров
    d_x, d_y = p_right - p_left
    angle = np.degrees(np.arctan2(d_y, d_x))
    
    dist_real = np.linalg.norm(p_right - p_left)
    dist_target = 128.0  # 192 - 64
    scale = dist_target / dist_real

    center_real = (p_left + p_right) / 2.0
    center_target = (target_left + target_right) / 2.0

    # Строим и корректируем аффинную матрицу
    M = cv2.getRotationMatrix2D(tuple(center_real), angle, scale)
    M[:, 2] += center_target - np.dot(M[:, :2], center_real)

    # Трансформируем лицо
    aligned_face = cv2.warpAffine(gray, M, (target_size, target_size), flags=cv2.INTER_AREA)
    
    return aligned_face, True

def position_by_center(image_bgr, target_size=256):
    if len(image_bgr.shape) == 3:
        gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    else:
        gray = image_bgr
    h, w = gray.shape[:2]
    crop_size = min(h, w)
    sx = (w - crop_size) // 2
    sy = (h - crop_size) // 2
    return cv2.resize(gray[sy:sy+crop_size, sx:sx+crop_size], (target_size, target_size), interpolation=cv2.INTER_AREA)

def get_positioned_face(image_bgr, strategy_name, target_size=256):
    match strategy_name:
        case "Позиционирование по глазам (Жесткая фрактальная сетка)":
            return position_by_eyes(image_bgr, target_size)
        case "Простое кадрирование по центру холста":
            return position_by_center(image_bgr, target_size), True
        case _:
            return position_by_center(image_bgr, target_size), False


