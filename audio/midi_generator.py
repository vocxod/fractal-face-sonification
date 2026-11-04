# audio/midi_generator.py
import mido
from mido import Message, MidiFile, MidiTrack
from audio.presets import INSTRUMENTS, quantize_to_scale


def generate_face_midi(layers: dict, selected_instruments: dict, scale_name: str, thresholds: dict, output_path: str = "face_music.mid"):
    """
    Генератор полифонического MIDI со свободной конфигурацией инструментов.
    Обходит дерево по шагам ТОП-слоя (256 микро-шагов), вычисляя вложенность
    аккордов и индивидуальные накопительные дельта-паузы для каждого регистра.
    """
    mid = MidiFile()
    
    # Создаем 3 независимых трека для параллельного (полифонического) звучания
    bass_track = MidiTrack()
    piano_track = MidiTrack()
    flute_track = MidiTrack()
    mid.tracks.extend([bass_track, piano_track, flute_track])
    
    # Назначаем выбранные пользователем General MIDI инструменты на соответствующие каналы
    bass_track.append(Message('program_change', program=selected_instruments['large'], channel=0, time=0))
    piano_track.append(Message('program_change', program=selected_instruments['medium'], channel=1, time=0))
    flute_track.append(Message('program_change', program=selected_instruments['small'], channel=2, time=0))
    
    # Базовая длительность 16-й ноты (в тиках MIDI)
    tick_16th = 120
    
    # Накопители дельта-времени (тишины) для каналов: 0 (Бас), 1 (Мид), 2 (Топ)
    # Позволяют делать индивидуальные паузы для каждого инструмента
    accumulators = {0: 0, 1: 0, 2: 0}
    
    # Итерируемся по самому глубокому и частому слою (ТОП, 256 шагов)
    num_steps = len(layers['small'])
    
    for step in range(num_steps):
        # Вычисляем индексы родительских макро-блоков для текущего шага времени
        bass_idx = step // 16
        piano_idx = step // 4
        flute_idx = step
        
        # --- СЛОЙ 3: ТОП / ВЕРХНИЙ РЕГИСТР (Проверка на каждом шаге) ---
        f_node = layers['small'][flute_idx]
        if f_node.brightness >= thresholds['flute']:
            vel = max(20, min(int((f_node.brightness / 255.0) * 127), 127))
            raw_note = int(84 + (f_node.brightness % 12))
            note = quantize_to_scale(raw_note, 84, 100, scale_name)
            
            # Включаем ноту, учитывая накопленное время молчания этого инструмента
            flute_track.append(Message('note_on', note=note, velocity=vel, channel=2, time=accumulators[2]))
            flute_track.append(Message('note_off', note=note, velocity=vel, channel=2, time=tick_16th))
            accumulators[2] = 0  # Сбрасываем накопитель пауз
        else:
            accumulators[2] += tick_16th  # Накапливаем тишину, если блок темный
            
        # --- СЛОЙ 2: МИД / СРЕДНИЙ РЕГИСТР (Проверка каждые 4 шага) ---
        if step % 4 == 0 and piano_idx < len(layers['medium']):
            p_node = layers['medium'][piano_idx]
            if p_node.brightness >= thresholds['piano']:
                vel = max(20, min(int((p_node.brightness / 255.0) * 127), 127))
                raw_note = int(60 + (p_node.brightness % 12))
                note = quantize_to_scale(raw_note, 60, 80, scale_name)
                
                piano_track.append(Message('note_on', note=note, velocity=vel, channel=1, time=accumulators[1]))
                piano_track.append(Message('note_off', note=note, velocity=vel, channel=1, time=tick_16th * 4))
                accumulators[1] = 0
            else:
                accumulators[1] += tick_16th * 4
                
        # --- СЛОЙ 1: БАС / НИЖНИЙ РЕГИСТР (Проверка каждые 16 шагов) ---
        if step % 16 == 0 and bass_idx < len(layers['large']):
            b_node = layers['large'][bass_idx]
            if b_node.brightness >= thresholds['bass']:
                vel = max(30, min(int((b_node.brightness / 255.0) * 127), 127))
                raw_note = int(36 + (b_node.brightness % 12))
                note = quantize_to_scale(raw_note, 36, 55, scale_name)
                
                bass_track.append(Message('note_on', note=note, velocity=vel, channel=0, time=accumulators[0]))
                bass_track.append(Message('note_off', note=note, velocity=vel, channel=0, time=tick_16th * 16))
                accumulators[0] = 0
            else:
                accumulators[0] += tick_16th * 16

    # Финальный шаг: закрываем и выравниваем «отставшие» по времени треки тишиной,
    # чтобы MIDI-файл корректно завершался во всех дорожках одновременно
    for ch, track in enumerate([bass_track, piano_track, flute_track]):
        if accumulators[ch] > 0:
            track.append(Message('control_change', control=0, value=0, channel=ch, time=accumulators[ch]))
            
    mid.save(output_path)
    return output_path


import scipy.io.wavfile as wavfile

def generate_face_wav(layers: dict, selected_instruments: dict, scale_name: str, thresholds: dict, output_path: str = "face_music.wav"):
    """
    Генерирует WAV-файл в реальном времени методом прямого аддитивного синтеза.
    Позволяет прослушивать партитуру прямо в веб-плеере Streamlit без внешних плееров.
    """
    sample_rate = 22050  # Частота дискретизации (оптимально для скорости расчета)
    duration_16th = 0.15 # Длительность 16-й ноты в секундах (соответствует нашему темпу)
    
    num_steps = len(layers['small'])
    total_samples = int(num_steps * duration_16th * sample_rate)
    audio_buffer = np.zeros(total_samples, dtype=np.float32)
    
    # Мапим MIDI-ноты в физическую частоту (Гц)
    def midi_to_freq(note):
        return 440.0 * (2.0 ** ((note - 69) / 12.0))

    # Синтезируем каждый микро-шаг (всего 256)
    for step in range(num_steps):
        start_sample = int(step * duration_16th * sample_rate)
        end_sample = int((step + 1) * duration_16th * sample_rate)
        t = np.linspace(0, duration_16th, end_sample - start_sample, endpoint=False)
        
        step_wave = np.zeros_like(t)
        active_instruments = 0
        
        # --- СЛОЙ 3: ТОП (Свирель / Колокольчик) ---
        f_node = layers['small'][step]
        if f_node.brightness >= thresholds['flute']:
            from audio.presets import quantize_to_scale
            raw_note = int(84 + (f_node.brightness % 12))
            freq = midi_to_freq(quantize_to_scale(raw_note, 84, 100, scale_name))
            # Синтезируем чистый синус (флейта)
            step_wave += 0.3 * np.sin(2 * np.pi * freq * t)
            active_instruments += 1

        # --- СЛОЙ 2: МИД (Гусли / Пианино) ---
        piano_idx = step // 4
        if step % 4 == 0 and piano_idx < len(layers['medium']):
            p_node = layers['medium'][piano_idx]
            if p_node.brightness >= thresholds['piano']:
                from audio.presets import quantize_to_scale
                raw_note = int(60 + (p_node.brightness % 12))
                freq = midi_to_freq(quantize_to_scale(raw_note, 60, 80, scale_name))
                # Добавляем немного гармоник (имитация струны пианино/гуслей)
                step_wave += 0.4 * (np.sin(2 * np.pi * freq * t) + 0.5 * np.sin(4 * np.pi * freq * t))
                active_instruments += 1

        # --- СЛОЙ 1: БАС ---
        bass_idx = step // 16
        if step % 16 == 0 and bass_idx < len(layers['large']):
            b_node = layers['large'][bass_idx]
            if b_node.brightness >= thresholds['bass']:
                from audio.presets import quantize_to_scale
                raw_note = int(36 + (b_node.brightness % 12))
                freq = midi_to_freq(quantize_to_scale(raw_note, 36, 55, scale_name))
                # Органный глубокий бас (с суб-гармониками)
                step_wave += 0.5 * np.sin(2 * np.pi * freq * t)
                active_instruments += 1
                
        if active_instruments > 0:
            # Нормализуем микс, чтобы не было хрипа (клиппинга)
            step_wave /= active_instruments
            audio_buffer[start_sample:end_sample] = step_wave

    # Переводим в 16-битный PCM WAV формат
    audio_int16 = np.int16(audio_buffer * 32767)
    wavfile.write(output_path, sample_rate, audio_int16)
    return output_path
