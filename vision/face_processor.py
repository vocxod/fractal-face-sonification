import cv2
import numpy as np

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
