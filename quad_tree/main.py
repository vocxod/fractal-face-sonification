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
    return [
        (x, y),          # Top-Left
        (x + half, y),   # Top-Right
        (x, y + half),   # Bottom-Left
        (x + half, y + half) # Bottom-Right
    ]

def get_hilbert_order(x, y, half, rotation=0):
    quads = [
        (x, y),                  # 0: Top-Left (TL)
        (x + half, y),           # 1: Top-Right (TR)
        (x + half, y + half),    # 2: Bottom-Right (BR)
        (x, y + half)            # 3: Bottom-Left (BL)
    ]
    
    # Карта состояний Гильберта: для каждого rotation задаем (order, rotations)
    hilbert_states = {
        0: ([0, 3, 2, 1], [1, 0, 0, 3]),
        1: ([0, 1, 2, 3], [0, 1, 1, 2]),
        2: ([2, 1, 0, 3], [3, 2, 2, 1]),
        3: ([2, 3, 0, 1], [2, 3, 3, 0])
    }
    
    order, rotations = hilbert_states[rotation]
    
    return [(quads[i], quads[i], rotations[idx]) for idx, i in enumerate(order)]

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
# Построение и сжатие дерева
# ==========================================
def build_tree(img_array, x, y, size, curve_type="z", rotation=0):
    node = QuadNode(x, y, size)
    if size == 1:
        node.color = img_array[y, x].tolist()
        return node
    
    half = size // 2
    if curve_type == "hilbert":
        for cx, cy, next_rot in get_hilbert_order(x, y, half, rotation):
            node.children.append(build_tree(img_array, cx, cy, half, curve_type, next_rot))
    else:
        for cx, cy in get_z_order(x, y, half):
            node.children.append(build_tree(img_array, cx, cy, half, curve_type))
            
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
            node.children = []

# ==========================================
# Покадровый рендеринг (Оптимизирован для FFmpeg)
# ==========================================
def render_video_frames(root_node, img_size, output_dir="video_frames"):
    """
    Рендерит дерево сверху вниз. 
    Сохраняет изображение КАЖДЫЙ раз, когда на холсте прорисовывается новая четверка узлов.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    # Холст для отрисовки
    current_img = np.zeros((img_size, img_size, 3), dtype=np.uint8)
    
    # Сквозной счетчик кадров для FFmpeg (важно начать с 1 или 0 стабильно)
    frame_counter = 1
    
    # Слой 0: Отрисовываем самый корень (серый холст)
    current_img[:, :] = root_node.get_grayscale_color()
    Image.fromarray(current_img).save(f"{output_dir}/frame_{frame_counter:05d}.png")
    frame_counter += 1

    queue = deque([root_node])
    
    while queue:
        layer_size = len(queue)
        next_queue = deque()
        
        # Определяем, является ли следующий уровень абстракции финальным (пиксельным)
        # Если в текущей очереди ни у кого нет детей, значит мы дошли до дна
        is_final_layer = all(not n.children or n.is_compressed for n in queue)
        
        for _ in range(layer_size):
            node = queue.popleft()
            
            if node.children and not node.is_compressed:
                # Отрисовываем группу из 4-х детей на холсте
                for child in node.children:
                    # Если слой финальный — рисуем исходный RGB-цвет, иначе — Ч/Б
                    render_color = child.color if is_final_layer else child.get_grayscale_color()
                    current_img[child.y:child.y+child.size, child.x:child.x+child.size] = render_color
                
                # Добавляем детей в очередь на следующий слой
                next_queue.extend(node.children)
                
                # СХРАНЯЕМ КАДР: после прорисовки каждого родительского блока (его детей)
                # Это создаст эффект плавного "сканирования" картинки по траектории кривой
                Image.fromarray(current_img).save(f"{output_dir}/frame_{frame_counter:05d}.png")
                frame_counter += 1
            else:
                # Если узел сжат, он просто сохраняет свое состояние, на холсте перерисовывать нечего
                pass
                
        if not next_queue:
            break
        queue = next_queue

    print(f"[Успешно] Сгенерировано кадров для видео: {frame_counter - 1}")

# ==========================================
# CLI
# ==========================================
def main():
    parser = argparse.ArgumentParser(description="Покадровая генерация слоев Квадродерева.")
    parser.add_argument("image_path", type=str, help="Путь к исходному файлу")
    parser.add_argument("-s", "--size", type=int, default=512, help="Размер картинки (степень 2)")
    parser.add_argument("-t", "--threshold", type=float, default=5.0, help="Порог сжатия %")
    parser.add_argument("-c", "--curve", type=str, choices=["z", "hilbert"], default="z", help="Тип кривой: z или hilbert")
    
    args = parser.parse_args()
    
    if (args.size & (args.size - 1)) != 0 or args.size <= 0:
        print("[Ошибка]: Размер должен быть степенью 2", file=sys.stderr)
        sys.exit(1)
        
    print(f" Загрузка {args.image_path}...")
    img = Image.open(args.image_path).convert('RGB')
    img_array = np.array(img.resize((args.size, args.size), Image.Resampling.LANCZOS))
    
    print(f" Построение дерева ({args.curve.upper()})...")
    root = build_tree(img_array, 0, 0, args.size, curve_type=args.curve)
    
    print(f" Прунинг дерева ({args.threshold}%)...")
    compress_tree(root, args.threshold)
    
    print(" Генерация покадровой анимации обхода...")
    render_video_frames(root, args.size, "video_frames")

if __name__ == "__main__":
    main()

