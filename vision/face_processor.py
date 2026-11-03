import cv2
import numpy as np
import mediapipe as mp


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

def position_by_eyes(image_bgr, target_size=256):
    """
    Стратегия 1: Позиционирование по глазам.
    Находит центры глаз и трансформирует картинку так, чтобы глаза 
    легли ровно в центры верхних квадрантов квадродерева: (64, 64) и (192, 64).
    """
    img_h, img_w = image_bgr.shape[:2]
    
    # Инициализируем легкий детектор ключевых точек лица MediaPipe
    mp_face_mesh = mp.solutions.face_mesh
    with mp_face_mesh.FaceMesh(
        static_image_mode=True,
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5
    ) as face_mesh:
        
        # Переводим в RGB для MediaPipe
        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(image_rgb)
        
        # Если лицо или точки не найдены — уходим на фолбек (обычный центр)
        if not results.multi_face_landmarks:
            return position_by_center(image_bgr, target_size), False

        landmarks = results.multi_face_landmarks[0].landmark
        
        # Индексы MediaPipe для точных центров зрачков:
        # Левый глаз: 468, Правый глаз: 473
        left_eye_pts = landmarks[468]
        right_eye_pts = landmarks[473]
        
        # Переводим относительные координаты (0.0 - 1.0) в реальные пиксели
        p_left = np.array([left_eye_pts.x * img_w, left_eye_pts.y * img_h], dtype=np.float32)
        p_right = np.array([right_eye_pts.x * img_w, right_eye_pts.y * img_h], dtype=np.float32)
        
        # --- МАТЕМАТИКА АФФИННОГО ВЫРАВНИВАНИЯ ---
        # Целевые координаты на фрактальной матрице 256x256
        target_left = np.array([64.0, 64.0], dtype=np.float32)
        target_right = np.array([192.0, 64.0], dtype=np.float32)
        
        # Вычисляем угол наклона лица, чтобы выровнять его строго по горизонту
        d_x, d_y = p_right - p_left
        angle = np.degrees(np.arctan2(d_y, d_x))
        
        # Расстояние между глазами (реальное и целевое)
        dist_real = np.linalg.norm(p_right - p_left)
        dist_target = 128.0 # 192 - 64
        scale = dist_target / dist_real
        
        # Центр между глазами на исходном фото
        center_real = (p_left + p_right) / 2.0
        # Центр между глазами на целевой матрице
        center_target = (target_left + target_right) / 2.0
        
        # Строим матрицу поворота и масштабирования вокруг реального центра глаз
        M = cv2.getRotationMatrix2D(tuple(center_real), angle, scale)
        
        # Корректируем сдвиг (трансляцию), чтобы центры совпали
        M[0, 2] += center_target[0] - center_real[0]
        M[1, 2] += center_target[1] - center_real[1]
        
        # Применяем трансформацию: получаем идеально выровненный квадрат лица
        aligned_face = cv2.warpAffine(image_bgr, M, (target_size, target_size), flags=cv2.INTER_AREA)
        
        # Переводим в Ч/Б
        gray_face = cv2.cvtColor(aligned_face, cv2.COLOR_BGR2GRAY)
        return gray_face, True

def position_by_center(image_bgr, target_size=256):
    """
    Стратегия 2: Простое кадрирование по центру.
    Используется как фолбек или если выбран ручной режим без геометрии лица.
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
