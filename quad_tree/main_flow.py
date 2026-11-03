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
        (x, y),              # 0: TL
        (x + half, y),       # 1: TR
        (x, y + half),       # 2: BL
        (x + half, y + half) # 3: BR
    ]

def get_hilbert_order(x, y, half, rotation=0):
    quads = [
        (x, y),                  # 0: TL
        (x + half, y),           # 1: TR
        (x + half, y + half),    # 2: BR
        (x, y + half)            # 3: BL
    ]
    # Словарь состояний Гильберта: для каждого поворота задаем (порядок квадрантов, следующие повороты)
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
        for (cx, cy), _, next_rot in get_hilbert_order(x, y, half, rotation):
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
# НОВАЯ КРУПНОМАЗКОВАЯ (INTERLEAVED) ОТРИСОВКА
# ==========================================
def render_interleaved_frames(root_node, img_size, output_dir="video_frames"):
    """
    Рендерит дерево по новой логике: 
    Слой за слоем, чередуя потомков: сначала первые потомки всех родителей, затем вторые и т.д.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    current_img = np.zeros((img_size, img_size, 3), dtype=np.uint8)
    frame_counter = 1
    
    # Кадр 1: Стартовый корень (полностью усредненный серый холст)
    current_img[:, :] = root_node.get_grayscale_color()
    Image.fromarray(current_img).save(f"{output_dir}/frame_{frame_counter:05d}.png")
    frame_counter += 1

    # В очереди хранятся только активные РОДИТЕЛИ текущего уровня детализации
    queue = deque([root_node])
    
    while queue:
        # Отбираем только тех родителей текущего слоя, у которых есть живые несжатые дети
        active_parents = [node for node in queue if node.children and not node.is_compressed]
        
        if not active_parents:
            break
            
        # Проверяем, будет ли следующий шаг раскрытия абсолютно финальным (пиксели 1х1)
        # Если дети активных родителей имеют размер 1, значит, это финал — выводим в цвете!
        is_final_layer = (active_parents[0].children[0].size == 1)
        
        # Обходим поочередно каждого из 4 потомков (индексы от 0 до 3)
        for child_idx in range(4):
            # Переменная, чтобы фиксировать изменения на холсте
            canvas_changed = False
            
            # Идем горизонтальным срезом: берем child_idx у каждого родителя по очереди
            for parent in active_parents:
                child = parent.children[child_idx]
                
                # Финал — в исходном RGB, промежуточные — в Grayscale
                render_color = child.color if is_final_layer else child.get_grayscale_color()
                
                # Отрисовываем квадрат данного потомка
                current_img[child.y:child.y+child.size, child.x:child.x+child.size] = render_color
                canvas_changed = True
                
            # Сохраняем новый кадр видео после того, как ВСЕ родители выдали своего i-го потомка
            if canvas_changed:
                Image.fromarray(current_img).save(f"{output_dir}/frame_{frame_counter:05d}.png")
                frame_counter += 1
                
        # Формируем очередь родителей для следующего уровня детализации
        next_queue = deque()
        for parent in queue:
            if parent.children and not parent.is_compressed:
                next_queue.extend(parent.children)
            else:
                # Если узел сжат, он остается в структуре, но детей у него больше нет
                next_queue.append(parent)
                
        # Если в новой очереди вообще не осталось узлов, способных дробиться дальше, выходим
        if all(not n.children or n.is_compressed for n in next_queue):
            break
            
        queue = next_queue

    print(f"[Успешно] Сгенерировано кадров новой интерливинг-анимации: {frame_counter - 1}")

# ==========================================
# CLI
# ==========================================
def main():
    parser = argparse.ArgumentParser(description="Крупномасштабное послойное проявление квадродерева.")
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
    
    print(" Генерация интерливинг-анимации...")
    render_interleaved_frames(root, args.size, "video_frames")

if __name__ == "__main__":
    main()


