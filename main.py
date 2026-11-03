# main.py
import streamlit as st
import cv2
import numpy as np
import time
from PIL import Image
# Импортируем наше ДРАКОН-ядро и модули музыкальной генерации
from vision.face_processor import get_positioned_face
from core import process_face_to_layers
from audio.midi_generator import generate_face_midi

# Библиотека для интерактивного JS-кроппинга на Canvas (под капотом Cropper.js)
from streamlit_cropper import st_cropper
# Подтягиваем списки инструментов из пресетов
from audio.presets import AVAILABLE_INSTRUMENTS, SCALES

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

# 1б. Алгоритм позиционирования лица (включая ручной JS-режим)
alignment_strategy = st.sidebar.selectbox(
    "1б. Метод позиционирования лица",
    [
        "Ручная JS-калибровка по сетке (Рекомендуется)", 
        "Простое автоматическое кадрирование по центру"
    ]
)

# 2. Выбор математического движка обхода
curve_type = st.sidebar.selectbox(
    "2. Математическая кривая",
    ["Развертка Мортона (Z-кривая)", "Кривая Гильберта (Плавное легато)"]
)

# deprecated
# 3. Выбор музыкального пака
sound_preset = st.sidebar.selectbox(
    "3. Звуковая палитра (Пресет)",
    ["Космический Эмбиент", "Классика (Академический)", "Киберпанк (Электроника)", "Этно (Медитативный)"]
)

# 3. Выбор музыкального лада (Гаммы)
selected_scale = st.sidebar.selectbox(
    "3. Музыкальный лад (Гамма)",
    list(SCALES.keys())
)

# 3б. Свободный выбор инструментов по регистрам
st.sidebar.subheader("🎺 Конструктор фрактального оркестра")

instrument_large = st.sidebar.selectbox(
    "Инструмент для БАСА (Крупный слой)",
    list(AVAILABLE_INSTRUMENTS["large"].keys())
)
instrument_medium = st.sidebar.selectbox(
    "Инструмент для МИД (Средний слой)",
    list(AVAILABLE_INSTRUMENTS["medium"].keys())
)
instrument_small = st.sidebar.selectbox(
    "Инструмент для ТОП (Мелкие детали)",
    list(AVAILABLE_INSTRUMENTS["small"].keys())
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
    # 1. Открываем как PIL.Image для JS-кроппера
    img_pil = Image.open(uploaded_file)
    
    # Копия в формате numpy для автоматических режимов
    image = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # Инициализируем постоянную память сессии для нашей ч/б матрицы, если её еще нет
    if 'resized_gray' not in st.session_state:
        st.session_state.resized_gray = None
    
    # --- ШАГ 2: ПОЗИЦИОНИРОВАНИЕ И ЦЕНТРИРОВАНИЕ ЛИЦА ---
    if alignment_strategy == "Ручная JS-калибровка по сетке (Рекомендуется)":
        with col_orig:
            st.subheader("🎯 Кадрирование лица")
            st.caption("Выделите лицо квадратом. Масштабируйте его так, чтобы глаза были в верхней трети рамки.")
            
            cropped_image = st_cropper(
                img_file=img_pil, 
                realtime_update=True, 
                box_color='#FF3333', 
                aspect_ratio=(1, 1)
            )
            # Записываем результат работы JS-кроппера напрямую в память сессии!
            gray_matrix = cv2.cvtColor(np.array(cropped_image), cv2.COLOR_RGB2GRAY)
            st.session_state.resized_gray = cv2.resize(gray_matrix, (256, 256), interpolation=cv2.INTER_AREA)
            
        with col_fractal:
            st.subheader("🏁 Результат калибровки")
            st.caption("Визуальные мишени Узлов 0 и 1")
            
            preview_img = cv2.cvtColor(st.session_state.resized_gray, cv2.COLOR_GRAY2RGB)
            for center in [(64, 64), (192, 64)]:
                # Распаковываем кортеж на отдельные координаты X и Y
                cx, cy = center
                
                # Окружность вокруг центра зрачка
                cv2.circle(preview_img, (cx, cy), 6, (255, 0, 0), 1)
                
                # Горизонтальная линия перекрестия (меняется только координата X)
                cv2.line(preview_img, (cx - 12, cy), (cx + 12, cy), (255, 0, 0), 1)
                
                # Вертикальная линия перекрестия (меняется только координата Y)
                cv2.line(preview_img, (cx, cy - 12), (cx, cy + 12), (255, 0, 0), 1)
                
            st.image(preview_img, width=256)

            
    else:
        # Автоматический режим (центр кадра)
        with col_orig:
            st.subheader("🖼️ Оригинал")
            st.image(image_rgb, width='stretch')
            
        auto_gray, _ = get_positioned_face(image, alignment_strategy, target_size=256)
        st.session_state.resized_gray = auto_gray
        
        with col_fractal:
            st.subheader("🏁 Фрактальная матрица (Центр кадра)")
            st.image(st.session_state.resized_gray, width=256, channels="GRAY")
            
    # --- ПАНЕЛЬ ВОСПРОИЗВЕДЕНИЯ И ЗВУКА ---
    st.write("---")
    st.subheader("🎵 Мониторинг проигрывания")
    
    col_btn1, col_btn2, _ = st.columns(3)
    with col_btn1:
        start_play = st.button("▶ ИГРАТЬ", use_container_width=True)
    with col_btn2:
        stop_play = st.button("❚❚ ПАУЗА", use_container_width=True)
        
    # Проверяем матрицу из ПАМЯТИ СЕССИИ (теперь она никогда не будет None)
    if start_play and st.session_state.resized_gray is not None:
        st.success(f"🔥 Фрактальный оркестр запущен! Лад: **{selected_scale}**")
        
        with st.spinner("1. Математическое квадродерево строит слои изображения..."):
            face_layers = process_face_to_layers(st.session_state.resized_gray, curve_type)
            
        with st.spinner("2. Сборка индивидуальной партитуры со-творца..."):
            current_thresholds = {
                'bass': bass_threshold,
                'piano': piano_threshold,
                'flute': flute_threshold
            }
            
            # Собираем словарь ID выбранных инструментов для передачи в генератор
            user_instruments = {
                'large': AVAILABLE_INSTRUMENTS["large"][instrument_large],
                'medium': AVAILABLE_INSTRUMENTS["medium"][instrument_medium],
                'small': AVAILABLE_INSTRUMENTS["small"][instrument_small]
            }
            
            output_midi_file = "face_music.mid"
            output_wav_file = "face_music.wav"

            # Передаем новые параметры оркестровки и лада
            generate_face_midi(face_layers, user_instruments, selected_scale, current_thresholds, output_midi_file)

            # Генерируем звуковую волну для встроенного плеера!
            from audio.midi_generator import generate_face_wav
            generate_face_wav(face_layers, user_instruments, selected_scale, current_thresholds, output_wav_file)
            
        # ВСТРАИВАЕМ HTML5 АУДИОПЛЕЕР ПРЯМО НА ПАНЕЛЬ
        # st.write("### 🔊 Встроенный плеер аудио-паспорта")
        # with open(output_wav_file, "rb") as audio_file:
        #     st.audio(audio_file.read(), format="audio/wav")            

        # Отрисовка анимации (берем холст из сессии)
        visual_container = st.empty()
        status_text = st.empty()
        playback_progress = st.progress(0)
        
        base_canvas = cv2.cvtColor(st.session_state.resized_gray, cv2.COLOR_GRAY2RGB)
        total_bass_steps = len(face_layers['large'])
        
        for b_idx in range(total_bass_steps):
            frame = base_canvas.copy()
            
            # Подсветка Баса (Уровень 2, синий квадрат)
            b_node = face_layers['large'][b_idx]
            b_active = b_node.brightness >= bass_threshold
            b_color = (0, 102, 204) if b_active else (100, 100, 100)
            cv2.rectangle(frame, (b_node.x, b_node.y), (b_node.x + b_node.size, b_node.y + b_node.size), b_color, 2)
            
            # Подсветка Пианино (Уровень 3, зелёные квадраты внутри баса)
            for p_offset in range(4):
                p_idx = b_idx * 4 + p_offset
                if p_idx < len(face_layers['medium']):
                    p_node = face_layers['medium'][p_idx]
                    if p_node.brightness >= piano_threshold:
                        cv2.rectangle(frame, (p_node.x, p_node.y), (p_node.x + p_node.size, p_node.y + p_node.size), (0, 204, 102), 1)
                        
            # Подсветка Флейты (Уровень 4, красные точки)
            for f_offset in range(16):
                f_idx = b_idx * 16 + f_offset
                if f_idx < len(face_layers['small']):
                    f_node = face_layers['small'][f_idx]
                    if f_node.brightness >= flute_threshold:
                        center_x = f_node.x + f_node.size // 2
                        center_y = f_node.y + f_node.size // 2
                        cv2.circle(frame, (center_x, center_y), 2, (255, 51, 51), -1)

            visual_container.image(frame, width=512, caption=f"Сенсорный луч на траектории {curve_type}")
            status_text.markdown(f"**Макро-такт {b_idx + 1}/{total_bass_steps}** | Бас: {'🔊 ИГРАЕТ' if b_active else '🔇 ПАУЗА'}")
            playback_progress.progress((b_idx + 1) / total_bass_steps)
            time.sleep(0.4)
            
        st.balloons()
        st.success("🎉 Воспроизведение завершено! Музыкальный паспорт лица готов.")
        
        # Кнопка скачивания MIDI
        with open(output_midi_file, "rb") as f:
            st.download_button(
                label="📥 Скачать готовый MIDI-файл вашего лица",
                data=f,
                file_name=f"{sound_preset.replace(' ', '_')}_face.mid",
                mime="audio/mid",
                use_container_width=True
            )
else:
    st.info("💡 Пожалуйста, загрузите фотографию лица в левой панели для начала калибровки звука.")
