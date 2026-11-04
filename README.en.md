
🎹 Fractal Image Sonification Engine

A universal hierarchical image sonification sequencer based on space-filling curves.
This project operates at the intersection of Computer Vision, Advanced Fractal Mathematics, and Sensory Substitution (Audio Vision). The software transforms the geometry, contours, contrasts, and brightness of any two-dimensional graphical matrices (images) into multi-layered polyphonic music.

👁️ Purpose and Applications

1. Sensory Substitution (Accessibility): Creating an intuitive, fractal-based audio language that enables blind and visually impaired individuals to "hear" and recognize the contours, shapes, and boundaries of graphical objects.
	• Example: Transforming a human face into an individual acoustic portrait to track facial expressions or "hear" the emotional state of an interlocutor.
2. Acoustic Identity Passport / Ringtone: Generating unique, mathematically invariant melodies based on biometric or graphical data.
	• Example: A contact's profile photo from a smartphone address book is dynamically converted into a highly distinctive, personalized incoming call ringtone.
3. Co-Creation Platform: A Science-Art instrument where the user acts as a conductor and composer, explicitly configuring orchestration, musical scales, and traversal trajectories of the scanning sensor beam.

🧠 Mathematical Architecture (DRAKOН Logic)

The algorithm decomposes a flat two-dimensional image into hierarchical layers and translates graphical space into time using the following structural principles:


### 1. Scalable Quadtree Decomposition
The input graphical matrix can have any arbitrary resolution and dimensions. The application of a fixed 256 x 256 square grid ($2^n \times 2^n$) in our current test bench is utilized strictly for clarity, simplicity, and ease of architectural demonstration.

In production environments, the engine fluidly maps any resolution (including non-square layouts) into an N-layered hierarchical tree...

The depth of the quadtree and the number of layers chosen to construct the musical composition can be completely arbitrary (N layers), scales fluidly, and maps directly to custom polyphonic audio tracks.

As a primary base configuration, a 3-layer setup (Levels 2, 3, and 4) is utilized to demonstrate a standard three-register orchestra:
• 🎚️ Quadtree Level 2 (4x4 grid, 16 nodes - Example Configuration): BASS Layer (Macro-measures / Whole notes). Represents major geometric shapes and the foundational landscape of the image.
• 🎹 Quadtree Level 3 (8x8 grid, 64 nodes - Example Configuration): MID Layer / Piano / Gusli (Quarter notes). Outlines medium contours, primary textures, and shadows.
• 🪵 Quadtree Level 4 (16x16 grid, 256 nodes - Example Configuration): TOP Layer / Whistle / Flute (Sixteenth notes). Responsible for micro-details, sharp highlights, and intricate edges.

2. Traversal via Space-Filling Curves (SFC)

The sequence of node traversal at any given hierarchical level is strictly parameterized by mathematical space-filling curves to maximize the retention of local spatial boundaries:
• Morton Z-Curve: Traversal index generated via bit interleaving of coordinate dimensions (X and Y). Produces a highly dynamic, syncopated, and fractured digital rhythm.
• Hilbert Curve: Fully continuous traversal without spatial leaps (each subsequent pixel structurally borders the previous one). Generates fluid melodic movement (legato), which is highly optimized for spatial shape recognition through human hearing.

3. Subtractive Rhythmic Masking (Adaptive Pauses)

If the mean brightness of a particular graphical sector drops below a user-defined threshold, the instrument mapped to that specific register triggers a musical pause. The missed time quantum accumulates into the delta-time property of the MIDI track, dynamically generating a syncopated rhythmic signature unique to the processed image layout.

🛠️ Quick Start (Installation for Debian 12 / Ubuntu)

The engine is highly optimized for Python 3.11 and utilizes isolated runtime environments.

1. Environment Deployment

bash
# Navigate to the project directory
cd FractalSonicFace

# Create and activate an isolated virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Upgrade pip and install core dependencies
pip install --upgrade pip
pip install -r requirements.txt
Используйте код с осторожностью.

2. Launching the Interactive Workstation

bash
streamlit run main.py
Используйте код с осторожностью.
Once deployed, open the local network address in your web browser (default: http://localhost:8501).

🎛️ User Operation Guide (Orchestrating the Canvas)

1. Interactive Cropping (JavaScript Canvas Interface): Upload an image file. Use the mouse or touchscreen interface to isolate the key area within a rigid 1:1 square frame.
	• For Facial Profiling: Scale the portrait frame so that the centers of the eyes line up precisely with the blue calibration crosshairs of Nodes 0 and 1 on the first hierarchical level (coordinates (64,64) and (192,64)). This ensures strict biometric invariance and acoustic reproducibility.
2. Scale Calibration: Cycle through available musical scales (e.g., the resonant Ancient Russian Obikhod Scale, Major Pentatonic, or cosmic Minor Pentatonic). The structural pitch quantizer automatically shifts node values to fit the selected harmonic grid, preventing any acoustic cacophony.
3. Orchestra Configuration: Freely assign folk acoustic textures (Gusli, Balalaika, Whistle) or synthesizer waveforms to individual audio tracks independently.
4. Real-time Synthesis: Press the "▶ PLAY" button. The built-in additive wave synthesizer computes the acoustic stream directly within Python memory. You can audition the output using the native browser player or export the generated professional-grade MIDI file for external digital audio workstations (DAWs).

⚖️ Legal Defensive Patent Shield (Prior Art Protection)

The source code of this project is explicitly licensed under the Apache License 2.0, which contains mutual reciprocal grants of patent rights and protections.
The full mathematical, structural, and logical framework of this technology is openly published in the WHITEPAPER.md file as a Defensive Publication (Prior Art). Any attempts by third parties or patent trolls to enforce commercial patent restrictions on multi-layered image sonification via arbitrary quadtree-to-register mapping or space-filling curve delta-time pause calculation are legally invalid and subject to immediate revocation based on this open disclosure timestamp.