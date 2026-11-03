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
