import cv2
import numpy as np

def process_and_center_face(image_bgr, target_size=256):
    """
    Находит лицо на фото, вырезает его строгим квадратом,
    центрирует и возвращает ч/б матрицу заданного размера.
    
    image_bgr: исходное изображение, считанное через cv2.imdecode/cv2.imread
    target_size: размер стороны итогового квадрата (256, 512 и т.д.)
    """
    # 1. Переводим в градации серого для работы детектора
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    
    # 2. Загружаем предобученный каскад Хаара для поиска лиц
    # OpenCV содержит эти файлы внутри своего пакета
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    # 3. Ищем лица на фотографии
    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(60, 60) # Игнорируем слишком мелкие шумы
    )
    
    # Если лицо не найдено, берем центральный квадрат всего изображения в качестве фолбека
    if len(faces) == 0:
        h, w = gray.shape[:2]
        crop_size = min(h, w)
        start_x = (w - crop_size) // 2
        start_y = (h - crop_size) // 2
        face_square = gray[start_y:start_y+crop_size, start_x:start_x+crop_size]
        resized = cv2.resize(face_square, (target_size, target_size), interpolation=cv2.INTER_AREA)
        return resized, False # Возвращаем матрицу и флаг, что лицо найдено не было
        
    # 4. Берем первое найденное лицо (обычно оно самое крупное)
    # x, y — координаты верхнего левого угла; w, h — ширина и высота окна лица
    x, y, w, h = faces[0]
    
    # Нам нужен строгий квадрат. Вычисляем центр найденной зоны лица
    center_x = x + w // 2
    center_y = y + h // 2
    
    # Чтобы портрет был красивым, возьмем рамку чуть шире, чем просто лицо (с запасом на прическу/уши)
    # Коэффициент 1.4 расширяет рамку
    crop_size = int(max(w, h) * 1.4)
    
    # Исходные размеры картинки для контроля границ
    img_h, img_w = gray.shape[:2]
    crop_size = min(crop_size, img_h, img_w) # Рамка не может быть больше самого фото
    
    # Вычисляем новые координаты начала обрезки
    start_x = max(0, center_x - crop_size // 2)
    start_y = max(0, center_y - crop_size // 2)
    
    # Корректируем, если рамка вылетела за правый или нижний край
    if start_x + crop_size > img_w:
        start_x = img_w - crop_size
    if start_y + crop_size > img_h:
        start_y = img_h - crop_size
        
    # 5. Вырезаем квадратную зону лица
    face_square = gray[start_y:start_y+crop_size, start_x:start_x+crop_size]
    
    # 6. Масштабируем к нашему целевому фрактальному размеру (например, 256x256)
    resized_face = cv2.resize(face_square, (target_size, target_size), interpolation=cv2.INTER_AREA)
    
    return resized_face, True
