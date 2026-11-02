import streamlit as st
import cv2
import numpy as np
import time

# Импортируем наш новый шаг обработки лица
from vision.face_processor import process_and_center_face

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
        st.image(image_rgb, use_container_width=True)
        
    # --- КАРТИРОВАНИЕ И ПОДГОТОВКА МАТРИЦЫ ---
    # Переводим в градации серого
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Приводим к строгому квадрату 256x256 (степень двойки 2^8 для Мортона/Гильберта)
    square_size = 256
    # resized_gray = cv2.resize(gray, (square_size, square_size), interpolation=cv2.INTER_AREA)

    # --- ШАГ 2: ПОЗИЦИОНИРОВАНИЕ И ЦЕНТРИРОВАНИЕ ЛИЦА ---
    # Передаем картинку в наш процессор. Он вернет идеальный ч/б квадрат square_size x square_size
    resized_gray, face_found = process_and_center_face(image, target_size=square_size)

    
    with col_fractal:
        st.subheader("🏁 Фрактальная матрица (256x256)")
        # Отображаем ч/б квадрат, готовый к сканированию
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
        st.success(f"Запущен симулятор обхода по траектории: **{curve_type}**")
        
        # Заглушка под будущий цикл обхода и real-time отрисовку
        status_box = st.empty()
        progress_bar = st.progress(0)
        
        # Имитируем быстрый проход макро-зон (например, 16 шагов L2 уровня)
        for step in range(1, 17):
            status_box.markdown(f"**Шаг {step}/16:** Сканируем сектор. Режим: `{sound_preset}`. "
                                f"Бас: {'🎵 играет' if 120 > bass_threshold else '░ пауза'}")
            progress_bar.progress(step / 16)
            time.sleep(0.2)
            
        st.balloons()

else:
    st.info("💡 Пожалуйста, загрузите фотографию лица в левой панели для начала калибровки звука.")
