import streamlit as st
import cv2
import numpy as np
import time

# Импортируем наш новый шаг обработки лица
from vision.face_processor import process_and_center_face
from vision.face_processor import get_positioned_face  
from core import process_face_to_layers
from audio.midi_generator import generate_face_midi

# --- НАСТРОЙКА СТРАНИЦЫ ---
st.set_page_config(
    page_title="Фрактальный аудио-портрет",
    page_icon="🎹",
    layout="wide"
)

st.title("🎹 Фрактальный аудио-портрет: Инструментальный стенд со-творца")
st.caption("Перевод геометрии и яркости лица в многослойную полифоническую музыку")

# --- БОКОВАЯ ПАНЕЛЬ (ИНТЕРФЕЙС СО-ТВОРЦА) ---
st.sidebar.header("🎛️ Панель управления")

# 1. Загрузка фотографии
uploaded_file = st.sidebar.file_uploader("1. Загрузите фото лица", type=["jpg", "jpeg", "png"])

# Выбор алгоритма позиционирования и обрезки
alignment_strategy = st.sidebar.selectbox(
    "1. Алгоритм позиционирования лица",
    [
        "Позиционирование по глазам (Жесткая фрактальная сетка)", 
        "Простое кадрирование по центру холста"
    ]
)

# 2. Выбор математического движка обхода
curve_type = st.sidebar.selectbox(
    "2. Математическая кривая",
    ["Развертка Мортона (Z-кривая)", "Кривая Гильберта (Плавное легато)", "Кривая Пеано (Полиритмия 3x3)"]
)

# 3. Выбор музыкального пака
sound_preset = st.sidebar.selectbox(
    "3. Звуковая палитра (Пресет)",
    ["Космический Эмбиент", "Классика (Академический)", "Киберпанк (Электроника)", "Этно (Медитативный)"]
)

# 4. Настройка порогов яркости (Паузы)
st.sidebar.subheader("🎚️ Пороги активации слоев")
st.sidebar.markdown("<small>Если яркость зоны ниже порога, инструмент берет паузу</small>", unsafe_allow_html=True)


bass_threshold = st.sidebar.slider("Бас (Крупный слой, L2)", 0, 255, 40)
piano_threshold = st.sidebar.slider("Пианино (Средний слой, L3)", 0, 255, 60)
flute_threshold = st.sidebar.slider("Флейта (Мелкий слой, L4)", 0, 255, 80)


# --- ОСНОВНАЯ ЗОНА ИНТЕРФЕЙСА ---
col_orig, col_fractal = st.columns(2)

if uploaded_file is not None:
    # Чтение изображения через OpenCV
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    
    # Конвертируем в RGB для корректного отображения в Streamlit
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    with col_orig:
        st.subheader("🖼️ Оригинал")
        # st.image(image_rgb, use_container_width=True)
        st.image(image_rgb, width='stretch')
        
    # --- КАРТИРОВАНИЕ И ПОДГОТОВКА МАТРИЦЫ ---
    # Переводим в градации серого
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Приводим к строгому квадрату 256x256 (степень двойки 2^8 для Мортона/Гильберта)
    square_size = 256
    # resized_gray = cv2.resize(gray, (square_size, square_size), interpolation=cv2.INTER_AREA)

    # --- ШАГ 2: ПОЗИЦИОНИРОВАНИЕ И ЦЕНТРИРОВАНИЕ ЛИЦА ---
    from vision.face_processor import get_positioned_face
    
    resized_gray, face_found = get_positioned_face(image, alignment_strategy, target_size=256)
    
    with col_fractal:
        if face_found and alignment_strategy == "Позиционирование по глазам (Жесткая фрактальная сетка)":
            st.subheader("🎯 Сетка: Глаза в Узлах 0 и 1")
            
            # Создаем цветную копию для калибровочных маркеров
            preview_img = cv2.cvtColor(resized_gray, cv2.COLOR_GRAY2RGB)
            
            # Рисуем яркие красные мишени в точках (64,64) и (192,64)
            for center in [(64, 64), (192, 64)]:
                # Окружность вокруг центра зрачка
                cv2.circle(preview_img, center, 6, (255, 0, 0), 1)
                # Перекрестие
                cv2.line(preview_img, (center[0]-12, center[1]), (center[0]+12, center[1]), (255, 0, 0), 1)
                cv2.line(preview_img, (center[0], center[1]-12), (center[0], center[1]+12), (255, 0, 0), 1)
                
            st.image(preview_img, width=256)
        else:
            st.subheader("🏁 Фрактальная матрица")
            if not face_found:
                st.warning("⚠️ Лицо/глаза не распознаны. Применен автоматический центр кадра.")
            st.image(resized_gray, width=256, channels="GRAY")

    with col_fractal:
        if face_found:
            st.subheader("🎯 Центрированное лицо (256x256)")
        else:
            st.subheader("🏁 Фрактальная матрица (Лицо не найдено)")
            st.warning("Алгоритм не распознал лицо, взят центр кадра.")
            
        # Отображаем подготовленный для сканирования квадрат
        st.image(resized_gray, width=square_size, channels="GRAY")
        
    # --- ПАНЕЛЬ ВОСПРОИЗВЕДЕНИЯ ---
    st.write("---")
    st.subheader("🎵 Мониторинг проигрывания")
    
    col_btn1, col_btn2, _ = st.columns([1, 1, 4])
    with col_btn1:
        start_play = st.button("▶ ИГРАТЬ", use_container_width=True)
    with col_btn2:
        stop_play = st.button("❚❚ ПАУЗА", use_container_width=True)
        
    if start_play:
        st.success(f"🔥 Движок со-творчества запущен! Режим: **{curve_type}**")
        
        # 1. Запускаем математический послойный анализ лица через квадродерево
        with st.spinner("1. Математическое квадродерево строит слои изображения..."):
            face_layers = process_face_to_layers(resized_gray, curve_type)
            
        st.info(f"Структура дерева построена: Бас ({len(face_layers['large'])} зон), Пианино ({len(face_layers['medium'])} зон), Флейта ({len(face_layers['small'])} зон).")
        
        # 2. Передаем слои в MIDI-генератор с текущими ползунками порогов яркости
        with st.spinner("2. Аудио-сервер собирает полифоническую партитуру..."):
            current_thresholds = {
                'bass': bass_threshold,
                'piano': piano_threshold,
                'flute': flute_threshold
            }
            output_midi_file = "face_music.mid"
            generate_face_midi(face_layers, sound_preset, current_thresholds, output_midi_file)
            ###
            st.success("🎉 Партитура собрана! Запуск интерактивной визуализации обхода...")
        
            # --- БЛОК ИНТЕРАКТИВНОЙ ВИЗУАЛИЗАЦИИ ---
            # Создаем контейнер для динамического обновления картинки
            visual_container = st.empty()
            status_text = st.empty()
            playback_progress = st.progress(0)
            
            # Для отрисовки рамок переводим Ч/Б лицо обратно в цветной формат RGB
            base_canvas = cv2.cvtColor(resized_gray, cv2.COLOR_GRAY2RGB)
            
            # Будем шагать по басовому слою (16 макро-шагов)
            total_bass_steps = len(face_layers['large'])
            
            for b_idx in range(total_bass_steps):
                # Копируем базовый холст, чтобы рамки предыдущих шагов стирались
                frame = base_canvas.copy()
                
                # 1. Подсветка текущего БАС-узла (Крупный синий квадрат)
                b_node = face_layers['large'][b_idx]
                b_active = b_node.brightness >= bass_threshold
                b_color = (0, 102, 204) if b_active else (100, 100, 100) # Синий если играет, серый если пауза
                
                cv2.rectangle(
                    frame, 
                    (b_node.x, b_node.y), 
                    (b_node.x + b_node.size, b_node.y + b_node.size), 
                    b_color, 
                    2
                )
                
                # 2. Находим и подсвечиваем 4-х МИД-потомков (Пианино) внутри этого басового сектора
                # Так как дерево отсортировано по фрактальной кривой, они идут группами по 4
                for p_offset in range(4):
                    p_idx = b_idx * 4 + p_offset
                    if p_idx < len(face_layers['medium']):
                        p_node = face_layers['medium'][p_idx]
                        p_active = p_node.brightness >= piano_threshold
                        if p_active:
                            # Зеленая рамка для играющего пианино
                            cv2.rectangle(
                                frame, 
                                (p_node.x, p_node.y), 
                                (p_node.x + p_node.size, p_node.y + p_node.size), 
                                (0, 204, 102), 
                                1
                            )
                            
                # 3. Находим и подсвечиваем 16 ТОП-потомков (Флейта, самые мелкие вспышки)
                for f_offset in range(16):
                    f_idx = b_idx * 16 + f_offset
                    if f_idx < len(face_layers['small']):
                        f_node = face_layers['small'][f_idx]
                        f_active = f_node.brightness >= flute_threshold
                        if f_active:
                            # Маленькая красная точка-маркер в центре пикселя флейты
                            center_x = f_node.x + f_node.size // 2
                            center_y = f_node.y + f_node.size // 2
                            cv2.circle(frame, (center_x, center_y), 2, (255, 51, 51), -1)

                # Выводим обновленный кадр на панель
                visual_container.image(frame, width=512, caption=f"Сенсорный луч на фрактальной траектории ({curve_type})")
                
                # Обновляем текстовый статус
                status_text.markdown(
                    f"**Макро-такт {b_idx + 1}/{total_bass_steps}** | "
                    f"Бас: {'🔊 ИГРАЕТ' if b_active else '🔇 ПАУЗА'} (Яркость: {int(b_node.brightness)})"
                )
                
                # Двигаем ползунок прогресса
                playback_progress.progress((b_idx + 1) / total_bass_steps)
                
                # Имитируем темп музыки (скорость воспроизведения такта)
                time.sleep(0.4)
                
            st.balloons()
            st.success("🎉 Воспроизведение завершено! Музыкальный паспорт лица готов к скачиванию.")
            
            # 4. Предоставляем файл для скачивания разработчику
            with open(output_midi_file, "rb") as f:
                st.download_button(
                    label="📥 Скачать готовый MIDI-файл вашего лица",
                    data=f,
                    file_name=f"{sound_preset.replace(' ', '_')}_face.mid",
                    mime="audio/mid",
                    width='stretch'
                )
            ###
            
        st.balloons()
        st.success("🎉 Ваш уникальный аудио-портрет успешно сгенерирован!")
        
        # 3. Предоставляем файл для скачивания разработчику
        with open(output_midi_file, "rb") as f:
            st.download_button(
                label="📥 Скачать MIDI-файл вашего лица",
                data=f,
                file_name=f"{sound_preset.split()[0]}_face_portrait.mid",
                mime="audio/mid",
                use_container_width=True
            )

else:
    st.info("💡 Пожалуйста, загрузите фотографию лица в левой панели для начала калибровки звука.")
