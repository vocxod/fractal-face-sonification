# audio/midi_generator.py
import mido
from mido import Message, MidiFile, MidiTrack
from audio.presets import INSTRUMENTS, quantize_to_scale

def generate_face_midi(layers: dict, preset_name: str, thresholds: dict, output_path: str = "face_music.mid"):
    """
    Генератор полифонического MIDI на основе слоев квадродерева.
    Синхронизирует макро- и микро-доли во времени с учетом порогов пауз.
    """
    mid = MidiFile()
    
    # 3 независимых трека для полифонии
    bass_track = MidiTrack()
    piano_track = MidiTrack()
    flute_track = MidiTrack()
    mid.tracks.extend([bass_track, piano_track, flute_track])
    
    # Назначаем инструменты из выбранного пресета
    patch_info = INSTRUMENTS.get(preset_name, INSTRUMENTS["Космический Эмбиент"])
    bass_track.append(Message('program_change', program=patch_info['large'], channel=0, time=0))
    piano_track.append(Message('program_change', program=patch_info['medium'], channel=1, time=0))
    flute_track.append(Message('program_change', program=patch_info['small'], channel=2, time=0))
    
    # Музыкальные кванты времени (в MIDI тиках)
    tick_16th = 120  # Длительность самой короткой ноты (Флейта)
    
    # Накопители тишины (пауз) для дельта-времени каждого трека
    accumulators = {0: 0, 1: 0, 2: 0}
    
    # В квадродереве: 16 узлов бас, 64 узла пианино, 256 узлов флейты
    num_steps = len(layers['small']) # Всего 256 микро-шагов
    
    for step in range(num_steps):
        # Вычисляем индексы родительских узлов для текущего микро-шага
        bass_idx = step // 16
        piano_idx = step // 4
        flute_idx = step
        
        # --- СЛОЙ 3: ФЛЕЙТА (Каждый шаг) ---
        f_node = layers['small'][flute_idx]
        if f_node.brightness >= thresholds['flute']:
            vel = max(20, min(int((f_node.brightness / 255.0) * 127), 127))
            raw_note = int(84 + (f_node.brightness % 12))
            note = quantize_to_scale(raw_note, 84, 100)
            
            flute_track.append(Message('note_on', note=note, velocity=vel, channel=2, time=accumulators[2]))
            flute_track.append(Message('note_off', note=note, velocity=vel, channel=2, time=tick_16th))
            accumulators[2] = 0
        else:
            accumulators[2] += tick_16th
            
        # --- СЛОЙ 2: ПИАНИНО (Каждые 4 шага флейты) ---
        if step % 4 == 0 and piano_idx < len(layers['medium']):
            p_node = layers['medium'][piano_idx]
            if p_node.brightness >= thresholds['piano']:
                vel = max(20, min(int((p_node.brightness / 255.0) * 127), 127))
                raw_note = int(60 + (p_node.brightness % 12))
                note = quantize_to_scale(raw_note, 60, 80)
                
                piano_track.append(Message('note_on', note=note, velocity=vel, channel=1, time=accumulators[1]))
                piano_track.append(Message('note_off', note=note, velocity=vel, channel=1, time=tick_16th * 4))
                accumulators[1] = 0
            else:
                accumulators[1] += tick_16th * 4
                
        # --- СЛОЙ 1: БАС (Каждые 16 шагов флейты) ---
        if step % 16 == 0 and bass_idx < len(layers['large']):
            b_node = layers['large'][bass_idx]
            if b_node.brightness >= thresholds['bass']:
                vel = max(30, min(int((b_node.brightness / 255.0) * 127), 127))
                raw_note = int(36 + (b_node.brightness % 12))
                note = quantize_to_scale(raw_note, 36, 55)
                
                bass_track.append(Message('note_on', note=note, velocity=vel, channel=0, time=accumulators[0]))
                bass_track.append(Message('note_off', note=note, velocity=vel, channel=0, time=tick_16th * 16))
                accumulators[0] = 0
            else:
                accumulators[0] += tick_16th * 16

    # Финальное выравнивание треков тишиной
    for ch, track in enumerate([bass_track, piano_track, flute_track]):
        if accumulators[ch] > 0:
            track.append(Message('control_change', control=0, value=0, channel=ch, time=accumulators[ch]))
            
    mid.save(output_path)
    return output_path
