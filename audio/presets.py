# audio/presets.py

# MIDI номера инструментов
INSTRUMENTS = {
    "Космический Эмбиент": {"large": 89, "medium": 81, "small": 98},     # Pad (Warm), Lead (Sawtooth), Crystal
    "Классика (Академический)": {"large": 42, "medium": 0, "small": 73},  # Cello, Acoustic Grand Piano, Flute
    "Киберпанк (Электроника)": {"large": 38, "medium": 80, "small": 84}, # Synth Bass 2, Lead (Square), Lead (Charang)
    "Этно (Медитативный)": {"large": 24, "medium": 25, "small": 78}      # Acoustic Guitar (nylon), (steel), Whistle
}

# Массив нот минорной пентатоники (ля-минор) для квантования частот, чтобы избежать какофонии
PENTATONIC_SCALE = [36, 39, 41, 43, 46, 48, 51, 53, 55, 58, 60, 63, 65, 67, 70, 72, 75, 77, 79, 82, 84, 87, 89, 91, 94, 96]

def quantize_to_scale(raw_note: int, min_note: int, max_note: int) -> int:
    """ Находит ближайшую к расчетной ноту из разрешенного гармоничного лада """
    allowed_notes = [n for n in PENTATONIC_SCALE if min_note <= n <= max_note]
    if not allowed_notes:
        return min_note
    return min(allowed_notes, key=lambda x: abs(x - raw_note))


###
'''

# Доступные лады для квантования частот
SCALES = {
    "Минорная пентатоника (Эмбиент)":,
    "Обиходный лад (Древнерусский)":,
    "Дорийский минор (Фольклорный)":,
    "Мажорная пентатоника (Светлый)": [36, 38, 40, 43, 45, 48, 50, 52, 55, 57, 60, 62, 64, 67, 69, 72, 74, 76, 79, 81, 84, 86, 88, 91, 93, 96, 98, 100, 103]
}

# Каталог доступных MIDI-инструментов, сгруппированных по регистрам
AVAILABLE_INSTRUMENTS = {
    "large": {
        "Глубокий Бас-синтезатор": 38,
        "Церковный Орган (Бас)": 19,
        "Акустический контрабас": 32,
        "Низкая славянская билы/гонг": 9,
    },
    "medium": {
        "Акустическое Пианино": 0,
        "Балалайка / Домра (Тремоло)": 106, # Из секции GM Ethnic (Shamisen)
        "Гусли (Струнный щипковый)": 46,    # GM Harp (Арфа)
        "Духовой Орган (Аккомпанемент)": 16,
        "Деревянная Маримба": 12
    },
    "small": {
        "Пастуший рожок / Жалейка": 68,     # GM Oboe (Гобой, близкий по спектру)
        "Свирель / Деревянная флейта": 73,  # GM Flute
        "Космический колокольчик": 98,
        "Скрипичное пиццикато": 45
    }
}

def quantize_to_scale(raw_note: int, min_note: int, max_note: int, scale_name: str) -> int:
    """ Находит ближайшую к расчетной ноту из выбранного пользователем лада """
    scale_notes = SCALES.get(scale_name, SCALES["Минорная пентатоника (Эмбиент)"])
    allowed_notes = [n for n in scale_notes if min_note <= n <= max_note]
    if not allowed_notes:
        return min_note
    return min(allowed_notes, key=lambda x: abs(x - raw_note))
'''
    