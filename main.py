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
    # 1. Для JS-кроппера открываем как PIL.Image
    img_pil = Image.open(uploaded_file)
    
    # 2. Для автоматических режимов OpenCV делаем копию в формате numpy ndarray
    image = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # Результирующая ч/б матрица 256x256
    resized_gray = None
    
    # --- ШАГ 2: ПОЗИЦИОНИРОВАНИЕ И ЦЕНТРИРОВАНИЕ ЛИЦА ---
    if alignment_strategy == "Ручная JS-калибровка по сетке (Рекомендуется)":
        with col_orig:
            st.subheader("🎯 Кадрирование лица")
            st.caption("Выделите лицо квадратом. Масштабируйте его так, чтобы глаза были в верхней трети рамки.")
            
            # Передаем РIL объект вместо numpy
            cropped_image = st_cropper(
                img_file=img_pil, 
                realtime_update=True, 
                box_color='#FF3333', 
                aspect_ratio=(1, 1)
            )            
    else:
        # Автоматический режим (просто берет центр кадра)
        with col_orig:
            st.subheader("🖼️ Оригинал")
            st.image(image_rgb, width='stretch')
            
        resized_gray, _ = get_positioned_face(image, alignment_strategy, target_size=256)
        
        with col_fractal:
            st.subheader("🏁 Фрактальная матрица (Центр кадра)")
            st.image(resized_gray, width=256, channels="GRAY")
            
    # --- ПАНЕЛЬ ВОСПРОИЗВЕДЕНИЯ И ЗВУКА ---
    st.write("---")
    st.subheader("🎵 Мониторинг проигрывания")
    # Стало (добавлено явное количество колонок согласно стандартам Streamlit):
    col_btn1, col_btn2, _ = st.columns(3)
    with col_btn1:
        start_play = st.button("▶ ИГРАТЬ", use_container_width=True)
    with col_btn2:
        stop_play = st.button("❚❚ ПАУЗА", use_container_width=True)
        
    if start_play and resized_gray is not None:
        st.success(f"🔥 Движок со-творчества запущен! Режим: **{curve_type}**")
        
        # 1. Построение квадродерева и разделение по слоям
        with st.spinner("1. Математическое квадродерево строит слои изображения..."):
            face_layers = process_face_to_layers(resized_gray, curve_type)
            
        # 2. Полифоническая генерация MIDI
        with st.spinner("2. Аудио-сервер собирает полифоническую партитуру..."):
            current_thresholds = {
                'bass': bass_threshold,
                'piano': piano_threshold,
                'flute': flute_threshold
            }
            output_midi_file = "face_music.mid"
            generate_face_midi(face_layers, sound_preset, current_thresholds, output_midi_file)
            
        # 3. Интерактивная real-time визуализация обхода дерева на экране
        visual_container = st.empty()
        status_text = st.empty()
        playback_progress = st.progress(0)
        
        base_canvas = cv2.cvtColor(resized_gray, cv2.COLOR_GRAY2RGB)
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
