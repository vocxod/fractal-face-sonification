Fractal Sonification of Images Based on Quadtrees and Space-Filling Curves


TECHNICAL WHITE PAPER AND DEFENSIVE PUBLICATION (PRIOR ART DOCUMENT)

Priority Date: November 3, 2026
Status: Open International Standard (Public Domain / Copyleft Shield)
License: Apache License 2.0

1. Introduction and Purpose

This document describes the architecture, mathematical model, and software logic of a universal method for translating two-dimensional graphical matrices (specifically, images of human faces) into multi-layered polyphonic audio data (MIDI/audio signal).
The technology is engineered for:
• Sensory Substitution (Audio Vision): Assisting visually impaired and blind individuals in intuitively "hearing" the geometry, contours, and contrasts of human faces.
• Biometric Audio Authentication: Generating unique, mathematically invariant ringtones and acoustic identity passports based on anthropometric features.
• Interactive Digital Art (Science Art): Enabling synesthetic co-creation between a human user and an algorithmic engine.

2. Core Mathematical Model


2.1. Hierarchical Quadtree Decomposition

### 2.1. Scalable Hierarchical Space Decomposition
The core sonification framework is fully invariant to the resolution, aspect ratio, and scale of the input image matrix I. The application of a strict square matrix of size 2^n x 2^n (such as 256 × 256) is utilized purely as an illustrative benchmark to demonstrate the baseline execution of the principle. 

In the generalized model, the algorithm dynamically maps any arbitrary two-dimensional grid into a multi-layered hierarchical tree, computing the invariant mean brightness within each bounded local region (Region of Interest - ROI):
$$B_{node} = \frac{1}{S} \sum_{i,j \in ROI} I(i,j)$$
where S is the calculated area of the sub-matrix domain in pixels. The spatial boundaries adapt fluidly to non-square layouts, expanding the protective scope of this prior art to any discrete spatial-to-temporal transformation.


2.2. Multi-Layered Orchestral Mapping

Unlike linear raster-scanning methods, this technology applies the principle of structural temporal nesting, mapping the depth levels of the quadtree directly to musical registers:
• Gdepth Level 2 (4 × 4 = 16 nodes): BASS Layer (Macro-measures / Whole note durations).
• Depth Level 3 (8 × 8 = 64 nodes): MID / Accompaniment Layer (Quarter note durations).
• Depth Level 4 (16 × 16 = 256 nodes): TOP / Melodic Details Layer (Sixteenth note durations).
text
[Level 2: BASS]  |------------- 1 Whole Measure (16 steps) -------------|
[Level 3: MID]   |--- Quarter ---|--- Quarter ---|--- Quarter ---|--- Quarter ---|
[Level 4: TOP]   |_|_|_|_|_|_|_|_|_|_|_|_|_|_|_|_|_|_|_|_|_|_|_|_|_|_|_|_|_|_|_|_|
Используйте код с осторожностью.

2.3. Fractal Trajectories and SFC Strategy Dispatching

To preserve the spatial locality of neighboring pixels, the traversal of nodes at each level is parameterized via space-filling curves (SFC):
• Morton Z-Curve: Traversal index calculation via bit interleaving of X and Y coordinates. Generates a highly dynamic, syncopated rhythm.
• Hilbert Curve: Fully continuous traversal without spatial leaps. Generates smooth melodic lines (legato), which are critically superior for pattern recognition by the visually impaired.

2.4. Differential Sonification (Image Difference Analysis)

The algorithm can be applied not only to the raw processed source image matrix \(I_{source}\), but also to a differential matrix \(I_{diff}\) obtained by calculating the absolute difference between the source image and a predefined reference (baseline) image \(I_{reference}\):
\(I_{diff}(i,j)=|{}I_{source}(i,j)-I_{reference}(i,j)|{}\)
• Application 1 (Expression Tracking): If a neutral facial expression is set as \(I_{reference}\), the resulting polyphony explicitly sonifies only the changes (e.g., smiles, raised eyebrows, blinking), transforming emotional micro-movements into acoustic variations.
• Application 2 (Security and Deviation Analysis): In access control systems, this transforms structural biometric deviations between a target subject and an authorized template directly into a dissonant or alarm acoustic pattern.

3. Pause Management and Rhythmic Slicing

Polyphonic synchronization operates on a rigid algorithmic timeline:
1. The global loop iterator increments along the deepest time layer (TOP layer, 256 micro-steps).
2. At each micro-step, parent node indices are mapped for the MID and BASS tracks.
3. The engine evaluates the activation threshold for each active instrument:
\(\text{If\ }B_{node}<\text{Threshold}_{layer}\rightarrow \text{Instrument\ Mutes\ (Pause)}\)
4. When an instrument mutes, its MIDI note_on message is omitted. The duration of the missing note is added to the track's delta-time accumulator (\(accumulated\_time\)), shifting the subsequent note execution forward. This establishes a unique, fractured rhythmic grid ("subtractive rhythmic masking").

4. Scale Quantization and User Co-Creation

To prevent acoustic cacophony, all calculated note frequencies are strictly quantized to a selected mathematical scale matrix (e.g., Minor Pentatonic, Ancient Russian Obikhod Scale, or Dorian Mode):
\(N_{quantized}=\text{argmin}_{n\in Scale}|{}n-N_{raw}|{}\)
The user acts as a co-creator, possessing full parametric freedom over: the space-filling curve choice, individual timbre deployment (MIDI Program Change per layer), and separate layer activation thresholds.

5. Defensive Publication Status (Prior Art Enforcement)

Publishing this technical specification within a public or historically auditable repository establishes a global Prior Art (level of technique) footprint. Effective from the date of publication, any attempt by third parties or patent trolls to claim exclusive intellectual property rights or patent coverage on:
1. Sonification of images by mapping structural quadtree hierarchy levels to distinct musical registers (Bass/Mid/Top);
2. Dynamic accumulation of delta-time across independent polyphonic tracks to generate adaptive pauses via space-filling curves;
3. Image difference sonification utilizing an absolute deviation matrix against a reference baseline;
is legally invalid, and any such granted patents can be overturned in court based on the timestamped priority verified by this document.

Русский текст (может быть не полным. Приоритет - английский текст):
Дата фиксации приоритета: 3 ноября 2026 года
Статус: Открытый международный стандарт (Public Domain / Copyleft Shield)

1. Введение и назначение технологии

Настоящий документ описывает архитектуру, математическую модель и программную логику универсального метода перевода двумерных графических матриц (в частности, изображений человеческих лиц) в многослойные полифонические аудиоданные (MIDI/аудиосигнал).
Технология предназначена для:
• Сенсорного замещения (Звукового зрения): Помощи слабовидящим и незрячим людям в интуитивном «слышании» геометрии и контрастов человеческих лиц.
• Биометрической аутентификации звука: Генерации уникальных, математически инвариантных рингтонов и звуковых паспортов на основе антропометрических данных.
• Интерактивного искусства (Science Art): Синестетического со-творчества человека и алгоритма.

2. Математическая модель ядра


### 2.1. Масштабируемое иерархическое пространственное разложение
Описываемый метод сонификации полностью инвариантен к разрешению, соотношению сторон и масштабу входной матрицы изображения I. Применение строгого квадратного формата размера 2^n x 2^n (в частности, 256 × 256 пикселей) используется исключительно в качестве наглядного примера для демонстрации базовой работы принципа. 

В общем виде алгоритм динамически проецирует любую произвольную двумерную сетку в многоуровневое иерархическое дерево, вычисляя среднюю яркость внутри каждой ограниченной локальной области (ROI):
$$B_{node} = \frac{1}{S} \sum_{i,j \in ROI} I(i,j)$$
где S — площадь подматрицы в пикселях. Пространственные границы адаптивно подстраиваются под любые неквадратные структуры данных.


### 2.2. Послойное оркестровое картирование

В отличие от линейных методов растрового сканирования, данная технология применяет принцип структурной вложенности слоев во времени, сопоставляя уровни глубины квадродерева с музыкальными регистрами:
• Уровень вложенности 2 (4 × 4 = 16 узлов): Слой БАСА (Макро-такты / Целые длительности).
• Уровень вложенности 3 (8 × 8 = 64 узла): Слой МИД / Аккомпанемент (Четвертные длительности).
• Уровень вложенности 4 (16 × 16 = 256 узлов): Слой ТОП / Мелодические детали (Шестнадцатые длительности).
[Уровень 2: БАС]       |------------- 1 Целый такт (16 шагов) -------------|
[Уровень 3: МИД]       |--- Четверть ---|--- Четверть ---|--- Четверть ---|
[Уровень 4: ТОП]       |_|_|_|_|_|_|_|_|_|_|_|_|_|_|_|_|_|_|_|_|_|_|_|_|_|_|

2.3. Фрактальные траектории и ДРАКОН-выбор стратегий

Для сохранения пространственной связности соседних пикселей обход узлов на каждом уровне осуществляется по параметрическому выбору пространственно-заполняющих кривых (SFC):
• Развертка Мортона (Z-кривая): Расчет индекса через битовое перемежение координат X и Y. Создает синкопированную, ломаную динамику.
• Кривая Гильберта: Непрерывный обход без пространственных скачков. Создает плавные мелодические линии (легато), критически важные для распознавания образов незрячими.

3. Алгоритм управления паузами и динамикой

Синхронизация полифонии выполняется по следующей логике (ДРАКОН-схема):
1. Итератор движется по самому глубокому временному слою (ТОП, 256 микро-шагов).
2. На каждом шаге рассчитываются индексы родительских узлов для слоев МИД и БАС.
3. Происходит проверка порогов активации инструментов:
\(\text{Если }B_{node}<\text{Threshold}_{layer}\rightarrow \text{Инструмент молчит (Пауза)}\)
4. Если инструмент молчит, его MIDI-сообщение note_on не генерируется, а длительность шага накапливается в дельта-время (accumulated_time) трека, сдвигая следующую ноту вперед. Это формирует уникальный, ломаный ритмический рисунок («трафаретное ритмическое вычитание»).

4. Гармоническое квантование и со-творчество

Для исключения какофонии все рассчитанные частоты нот принудительно привязываются к выбранной пользователем математической матрице лада (Пентатоники, Обиходного древнерусского лада или Дорийского минора):
\(N_{quantized}=\text{argmin}_{n\in Scale}|{}n-N_{raw}|{}\)
Пользователю (со-творцу) предоставляется полная параметрическая свобода: независимый выбор кривой обхода, индивидуальное назначение тембров (MIDI Program Change) на каждый слой и регулировка порогов чувствительности.

5. Правовой статус публикации (Защита от патентования)

Публикация данного технического описания в открытом репозитории GitHub преследует цель создания общедоступного Prior Art (уровня техники). С момента публикации любая попытка третьих лиц запатентовать:
• Сонификацию изображений посредством привязки уровней квадродерева к музыкальным регистрам (Бас/Мид/Топ);
• Синхронизацию дельта-времени независимых треков для генерации пауз на фрактальных кривых;
• Интерактивную калибровку лица по узлам 0 и 1 первого уровня фрактальной матрицы;
является незаконной, а выданные патенты могут быть легко аннулированы в суде любой юрисдикции на основании даты настоящей публикации.
Исходный код проекта распространяется под защитной патентной лицензией Apache License 2.0, гарантирующей свободу использования и модификации для всех разработчиков.
