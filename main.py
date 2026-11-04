# main.py
import streamlit as st
import cv2
import numpy as np
import time
from PIL import Image

from vision.face_processor import get_positioned_face, apply_shift, apply_zoom
from core import process_face_to_layers
from audio.midi_generator import generate_face_midi, generate_face_wav
from audio.presets import AVAILABLE_INSTRUMENTS, SCALES
from streamlit_cropper import st_cropper

st.set_page_config(page_title="Фрактальный секвенсор", page_icon="🎹", layout="wide")
st.title("🎹 Универсальный фрактальный секвенсор: Пространственный Дифф-Стенд")

# --- БОКОВАЯ ПАНЕЛЬ ---
st.sidebar.header("🎛️ Панель управления")

app_mode = st.sidebar.radio(
    "0. Режим работы системы",
    ["Одиночное изображение", "Авто-девиация оригинала (Сдвиг/Масштаб)", "Дифференциальный анализ (2 файла)"]
)

st.sidebar.write("---")

uploaded_file_1 = None
uploaded_file_2 = None

# Настройка загрузки под выбранный режим
if app_mode == "Дифференциальный анализ (2 файла)":
    uploaded_file_1 = st.sidebar.file_uploader("1. Загрузите ЭТАЛОН", type=["jpg", "jpeg", "png"], key="b_img")
    uploaded_file_2 = st.sidebar.file_uploader("2. Загрузите ОБРАЗ", type=["jpg", "jpeg", "png"], key="s_img")
    alignment_strategy = "Простое автоматическое кадрирование по центру"
else:
    uploaded_file_1 = st.sidebar.file_uploader("1. Загрузите изображение", type=["jpg", "jpeg", "png"], key="single_img")
    alignment_strategy = st.sidebar.selectbox(
        "1б. Метод позиционирования",
        ["Ручная JS-калибровка по сетке (Рекомендуется)", "Простое автоматическое кадрирование по центру"]
    )

# Блок управления деформациями (появляется только в режиме Авто-девиации)
shift_x = 0.0
shift_y = 0.0
zoom_val = 0.0

if app_mode == "Авто-девиация оригинала (Сдвиг/Масштаб)":
    st.sidebar.subheader("📐 Параметры геометрии девиаций")
    transformation_type = st.sidebar.multiselect("Выберите тип искажения копии", ["Сдвиг (Shift)", "Масштабирование (Zoom)"], default=["Сдвиг (Shift)"])
    
    if "Сдвиг (Shift)" in transformation_type:
        shift_x = st.sidebar.slider("Сдвиг по горизонтали X (%)", -10.0, 10.0, 2.0, step=0.5)
        shift_y = st.sidebar.slider("Сдвиг по вертикали Y (%)", -10.0, 10.0, 0.0, step=0.5)
    if "Масштабирование (Zoom)" in transformation_type:
        zoom_val = st.sidebar.slider("Изменение масштаба (%)", -10.0, 10.0, 3.0, step=0.5)

# Стандартные настройки звука и математики
curve_type = st.sidebar.selectbox("2. Математическая кривая", ["Развертка Мортона (Z-кривая)", "Кривая Гильберта (Плавное легато)"])
selected_scale = st.sidebar.selectbox("3. Музыкальный лад (Гаммы)", list(SCALES.keys()))

st.sidebar.subheader("🎺 Конструктор фрактального оркестра")
instrument_large = st.sidebar.selectbox("БАС (L2)", list(AVAILABLE_INSTRUMENTS["large"].keys()))
instrument_medium = st.sidebar.selectbox("МИД (L3)", list(AVAILABLE_INSTRUMENTS["medium"].keys()))
instrument_small = st.sidebar.selectbox("ТОП (L4)", list(AVAILABLE_INSTRUMENTS["small"].keys()))

st.sidebar.subheader("🎚️ Пороги пауз")
bass_threshold = st.sidebar.slider("Бас порог", 0, 255, 40)
piano_threshold = st.sidebar.slider("Пианино порог", 0, 255, 60)
flute_threshold = st.sidebar.slider("Флейта порог", 0, 255, 80)

if 'resized_gray' not in st.session_state:
    st.session_state.resized_gray = None

# --- ВЫПОЛНЕНИЕ ЛОГИКИ СТЕНДА ---

if uploaded_file_1 is not None:
    img_pil = Image.open(uploaded_file_1)
    
    # Режим 1: Одиночный кадр
    if app_mode == "Одиночное изображение":
        col_orig, col_fractal = st.columns(2)
        if alignment_strategy == "Ручная JS-калибровка по сетке (Рекомендуется)":
            with col_orig:
                st.subheader("🎯 Кадрирование")
                cropped_image = st_cropper(img_file=img_pil, realtime_update=True, box_color='#FF3333', aspect_ratio=(1, 1))
                st.session_state.resized_gray = cv2.resize(cv2.cvtColor(np.array(cropped_image), cv2.COLOR_RGB2GRAY), (256, 256))
            with col_fractal:
                st.subheader("🏁 Результат калибровки")
                preview_img = cv2.cvtColor(st.session_state.resized_gray, cv2.COLOR_GRAY2RGB)
                for center in [(64, 64), (192, 64)]:
                    cx, cy = center
                    cv2.circle(preview_img, (cx, cy), 6, (255, 0, 0), 1)
                    cv2.line(preview_img, (cx-12, cy), (cx+12, cy), (255, 0, 0), 1)
                    cv2.line(preview_img, (cx, cy-12), (cx, cy+12), (255, 0, 0), 1)
                st.image(preview_img, width=256)
        else:
            with col_orig:
                st.image(img_pil, width=256)
            mat_bgr = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
            st.session_state.resized_gray, _ = get_positioned_face(mat_bgr, alignment_strategy, 256)
            with col_fractal:
                st.image(st.session_state.resized_gray, width=256, channels="GRAY")

    # Режим 2: АВТО-ДЕВИАЦИЯ (СДВИГ / МАСШТАБ ОДНОГО КАДРА)
    elif app_mode == "Авто-девиация оригинала (Сдвиг/Масштаб)":
        col_img1, col_img2, col_diff = st.columns(3)
        
        # Шаг А: Получаем базовый очищенный квадрат 256x256 из оригинала
        if alignment_strategy == "Ручная JS-калибровка по сетке (Рекомендуется)":
            with col_img1:
                st.subheader("🎯 1. Оригинал (Кроп)")
                cropped_image = st_cropper(img_file=img_pil, realtime_update=True, box_color='#FF3333', aspect_ratio=(1, 1))
                gray_origin = cv2.resize(cv2.cvtColor(np.array(cropped_image), cv2.COLOR_RGB2GRAY), (256, 256))
                st.image(gray_origin, width=230, channels="GRAY")
        else:
            mat_bgr = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
            gray_origin, _ = get_positioned_face(mat_bgr, alignment_strategy, 256)
            with col_img1:
                st.subheader("🖼️ 1. Оригинал")
                st.image(gray_origin, width=230, channels="GRAY")
        
        # Шаг Б: Строим вторичное деформированное изображение на основе параметров
        modified_matrix = gray_origin.copy()
        if "Сдвиг (Shift)" in transformation_type:
            modified_matrix = apply_shift(modified_matrix, shift_x, shift_y)
        if "Масштабирование (Zoom)" in transformation_type:
            modified_matrix = apply_zoom(modified_matrix, zoom_val)
            
        with col_img2:
            st.subheader("📐 2. Геометрическая копия")
            st.image(modified_matrix, width=230, channels="GRAY")
            
        # Шаг В: Вычисляем абсолютную попиксельную разницу (Картинка 3)
        diff_matrix = cv2.absdiff(gray_origin, modified_matrix)
        st.session_state.resized_gray = diff_matrix # Отправляем разность в музыкальное ядро
        
        with col_diff:
            st.subheader("📊 3. Матрица разности")
            st.caption(f"X-сдвиг: {shift_x}%, Y-сдвиг: {shift_y}%, Масштаб: {zoom_val}%")
            st.image(diff_matrix, width=230, channels="GRAY")

    # Режим 3: Разность двух независимых файлов
    elif app_mode == "Дифференциальный анализ (2 файла)" and uploaded_file_2 is not None:
        col_img1, col_img2, col_diff = st.columns(3)
        gray1, _ = get_positioned_face(cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR), alignment_strategy, 256)
        gray2, _ = get_positioned_face(cv2.cvtColor(np.array(Image.open(uploaded_file_2)), cv2.COLOR_RGB2BGR), alignment_strategy, 256)
        
        diff_matrix = cv2.absdiff(gray1, gray2)
        st.session_state.resized_gray = diff_matrix
        
        with col_img1: st.image(gray1, width=230, channels="GRAY", caption="1. Эталон")
        with col_img2: st.image(gray2, width=230, channels="GRAY", caption="2. Образ")
        with col_diff: st.image(diff_matrix, width=230, channels="GRAY", caption="3. Разность")

# --- ГЛОБАЛЬНЫЙ БЛОК ВОСПРОИЗВЕДЕНИЯ ---
if st.session_state.resized_gray is not None:
    st.write("---")
    st.subheader("🎵 Мониторинг проигрывания")
    
    col_btn1, col_btn2, _ = st.columns(3)
    with col_btn1: start_play = st.button("▶ ИГРАТЬ", use_container_width=True)
    with col_btn2: stop_play = st.button("❚❚ ПАУЗА", use_container_width=True)
        
    if start_play:
        st.success(f"🔥 Фрактальный движок активирован. Режим: **{curve_type}**")
        
        face_layers = process_face_to_layers(st.session_state.resized_gray, curve_type)
        current_thresholds = {'bass': bass_threshold, 'piano': piano_threshold, 'flute': flute_threshold}
        user_instruments = {
            'large': AVAILABLE_INSTRUMENTS["large"][instrument_large],
            'medium': AVAILABLE_INSTRUMENTS["medium"][instrument_medium],
            'small': AVAILABLE_INSTRUMENTS["small"][instrument_small]
        }
        
        output_midi_file = "face_music.mid"
        output_wav_file = "face_music.wav"
        
        generate_face_midi(face_layers, user_instruments, selected_scale, current_thresholds, output_midi_file)
        generate_face_wav(face_layers, user_instruments, selected_scale, current_thresholds, output_wav_file)
        
        st.write("### 🔊 Встроенный плеер аудио-паспорта")
        with open(output_wav_file, "rb") as audio_file:
            st.audio(audio_file.read(), format="audio/wav")
            
        visual_container = st.empty()
        status_text = st.empty()
        playback_progress = st.progress(0)
        
        base_canvas = cv2.cvtColor(st.session_state.resized_gray, cv2.COLOR_GRAY2RGB)
        total_bass_steps = len(face_layers['large'])
        
        for b_idx in range(total_bass_steps):
            frame = base_canvas.copy()
            b_node = face_layers['large'][b_idx]
            b_active = b_node.brightness >= bass_threshold
            b_color = (0, 102, 204) if b_active else (100, 100, 100)
            cv2.rectangle(frame, (b_node.x, b_node.y), (b_node.x + b_node.size, b_node.y + b_node.size), b_color, 2)

            # Подсветка Пианино (Уровень 3, зелёные квадраты внутри баса)
            for p_offset in range(4):
                ###
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

            visual_container.image(frame, width=512, caption="Сенсорный луч на разностной матрице")
            status_text.markdown(f"Макро-такт {b_idx + 1}/{total_bass_steps}")
            playback_progress.progress((b_idx + 1) / total_bass_steps)
            time.sleep(0.4)

            st.balloons()
            st.success("🎉 Подготовка к скадивания завершена! Музыкальный паспорт картинки готов.")

            with open(output_midi_file, "rb") as f:
                st.download_button(
                    label="📥 Скачать MIDI-файл разностной партитуры", 
                    data=f, 
                    file_name="diff_composition.mid", 
                    mime="audio/mid", 
                    use_container_width=True
                )
else:
    st.info("💡 Пожалуйста, загрузите фотографию в левой панели для начала калибровки звука.")
                        



