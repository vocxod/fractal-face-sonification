import argparse
import os
import sys
from collections import deque
import numpy as np
from PIL import Image

# ==========================================
# Порядки обхода (Стратегии кривых)
# ==========================================
def get_z_order(x, y, half):
    """Классический Z-порядок (Morton)"""
    return [
        (x, y),          # Top-Left
        (x + half, y),   # Top-Right
        (x, y + half),   # Bottom-Left
        (x + half, y + half) # Bottom-Right
    ]

def get_hilbert_order(x, y, half, rotation=0):
    """
    Вычисляет координаты детей и их дальнейшую ориентацию для кривой Гильберта.
    rotation: 0, 1, 2, 3 (повороты на 90 градусов)
    Возвращает список кортежей: (x, y, next_rotation)
    """
    # Базовые смещения для 4 квадрантов
    quads = [
        (x, y),                  # TL
        (x + half, y),           # TR
        (x + half, y + half),    # BR
        (x, y + half)            # BL
    ]
    
    # Изменение ориентации (поворотов) для дочерних подотрезков кривой
    # Индексы переходов зависят от текущего поворота родителя
    if rotation == 0:
        # Стандартный обход: ➔ вниз ➔ вправо ➔ вверх
        order = [0, 3, 2, 1]
        rotations = [1, 0, 0, 3]
    elif rotation == 1:
        order = [0, 1, 2, 3]
        rotations = [0, 1, 1, 2]
    elif rotation == 2:
        order = [2, 1, 0, 3]
        rotations = [3, 2, 2, 1]
    else: # rotation == 3
        order = [2, 3, 0, 1]
        rotations = [2, 3, 3, 0]
        
    return [(quads[i][0], quads[i][1], rotations[idx]) for idx, i in enumerate(order)]

# ==========================================
# Структура данных: Узел Квадродерева
# ==========================================
class QuadNode:
    def __init__(self, x=0, y=0, size=0):
        self.x = x
        self.y = y
        self.size = size
        self.color = None
        self.is_compressed = False
        self.children = []

    def get_brightness(self):
        if self.color is None: return 0.0
        return 0.299 * self.color[0] + 0.587 * self.color[1] + 0.114 * self.color[2]

    def get_grayscale_color(self):
        y = int(round(self.get_brightness()))
        return [y, y, y]

# ==========================================
# Построение дерева с поддержкой типа кривой
# ==========================================
def build_tree(img_array, x, y, size, curve_type="z", rotation=0):
    node = QuadNode(x, y, size)
    
    if size == 1:
        node.color = img_array[y, x].tolist()
        return node
    
    half = size // 2
    
    if curve_type == "hilbert":
        # Получаем координаты с учетом вращения кривой Гильберта
        for cx, cy, next_rot in get_hilbert_order(x, y, half, rotation):
            node.children.append(build_tree(img_array, cx, cy, half, curve_type, next_rot))
    else:
        # По умолчанию Z-кривая
        for cx, cy in get_z_order(x, y, half):
            node.children.append(build_tree(img_array, cx, cy, half, curve_type))
            
    # Усредняем цвет родителя
    node.color = np.mean([child.color for child in node.children], axis=0).round().astype(int).tolist()
    return node

def compress_tree(node, threshold_percentage):
    if not node.children:
        return

    for child in node.children:
        compress_tree(child, threshold_percentage)
        
    if all(not child.children or child.is_compressed for child in node.children):
        brightnesses = [child.get_brightness() for child in node.children]
        max_diff = max(brightnesses) - min(brightnesses)
        
        if max_diff <= 255.0 * (threshold_percentage / 100.0):
            node.is_compressed = True
            node.children = [] # Освобождаем память

# ==========================================
# Исправленная послойная отрисовка (БЕЗ зависаний)
# ==========================================
def render_layers_progressive(root_node, img_size, output_dir="render_steps"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    current_img = np.zeros((img_size, img_size, 3), dtype=np.uint8)
    queue = deque([root_node])
    layer_idx = 0
    
    while queue:
        layer_size = len(queue)
        next_queue = deque()
        
        # Проверяем, последний ли это слой (если в очереди не осталось узлов с детьми)
        is_final_layer = all(not n.children or n.is_compressed for n in queue)
        
        for _ in range(layer_size):
            node = queue.popleft()
            
            # Применяем новое правило: финал в цвете, промежуточные — в Ч/Б
            render_color = node.color if is_final_layer else node.get_grayscale_color()
            current_img[node.y:node.y+node.size, node.x:node.x+node.size] = render_color
            
            # ИСПРАВЛЕНИЕ: Передаем дальше только те узлы, которые РАЗДЕЛЯЮТСЯ.
            # Сжатые узлы и пиксели 1x1 больше не плодятся в очереди!
            if node.children and not node.is_compressed:
                next_queue.extend(node.children)
                
        img_to_save = Image.fromarray(current_img)
        img_to_save.save(f"{output_dir}/layer_{layer_idx:02d}.png")
        
        print(f"Слой {layer_idx:02d} готов. Узлов на обработку дальше: {len(next_queue)}")
        
        if is_final_layer or not next_queue:
            break
            
        queue = next_queue
        layer_idx += 1

# ==========================================
# CLI Интерфейс
# ==========================================
def main():
    parser = argparse.ArgumentParser(description="Послойное сжатие квадродерева (Z / Hilbert).")
    parser.add_argument("image_path", type=str, help="Путь к файлу")
    parser.add_argument("-s", "--size", type=int, default=512, help="Размер картинки")
    parser.add_argument("-t", "--threshold", type=float, default=5.0, help="Порог сжатия %")
    parser.add_argument("-c", "--curve", type=str, choices=["z", "hilbert"], default="z", help="Тип кривой: z или hilbert")
    
    args = parser.parse_args()
    
    # Валидация размера
    if (args.size & (args.size - 1)) != 0 or args.size <= 0:
        print("[Ошибка]: Размер должен быть степенью 2", file=sys.stderr)
        sys.exit(1)
        
    print(f" Загрузка {args.image_path} и ресайз до {args.size}...")
    img = Image.open(args.image_path).convert('RGB')
    img_array = np.array(img.resize((args.size, args.size), Image.Resampling.LANCZOS))
    
    print(f" Построение дерева (Кривая: {args.curve.upper()})...")
    root = build_tree(img_array, 0, 0, args.size, curve_type=args.curve)
    
    print(f" Сжатие по порогу {args.threshold}%...")
    compress_tree(root, args.threshold)
    
    print(" Послойный рендеринг...")
    render_layers_progressive(root, args.size)
    print("Готово!")

if __name__ == "__main__":
    # Если запустить без параметров командной строки, Python выведет help.
    # Для тестов перейдите к Шагу 4.
    main()
