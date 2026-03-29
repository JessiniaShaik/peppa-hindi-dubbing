 Peppa Pig — English to Hindi AI Dubbing Pipeline

![Python](https://img.shields.io/badge/Python-3.12-blue)
![Whisper](https://img.shields.io/badge/AI-OpenAI%20Whisper-green)
![TTS](https://img.shields.io/badge/TTS-Microsoft%20Neural-orange)
![Translator](https://img.shields.io/badge/Translator-MyMemory-yellow)
![FFmpeg](https://img.shields.io/badge/Audio-FFmpeg-red)

 A fully automated AI pipeline that takes an English Peppa Pig episode and produces a complete Hindi dubbed version — with background music, timing alignment, and child-friendly language.

 Project Overview

This project is an end-to-end automated video dubbing system built for a hackathon challenge. It takes an English cartoon video (Peppa Pig) and produces a fully dubbed Hindi version. The entire pipeline runs with a single command `python main.py` and processes everything automatically from raw video input to final dubbed output.

 **Input:** English Peppa Pig episode (MP4)
 **Output:** Hindi dubbed Peppa Pig episode (MP4) with background music

 Problem Statement

The hackathon challenge was to build an AI-powered audio dubbing platform that could:

 Extract speech from a video
 Transcribe it accurately
 Translate it to another language
 Generate natural-sounding dubbed audio
 Sync the dubbed audio back with the original video
 
 Tech Stack

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.12 | Core programming language |
| FFmpeg | 7.1 | Audio/video extraction and merging |
| MoviePy | 2.2.1 | Video file analysis |
| imageio-ffmpeg | 0.6.0 | FFmpeg Python bindings |
| OpenAI Whisper | 20231117 | Speech recognition and transcription |
| librosa | 0.10.1 | Audio processing and noise suppression |
| numpy | 1.26.4 | Numerical audio processing |
| soundfile | 0.12.1 | Audio file reading and writing |
| deep-translator | latest | Translation via MyMemory API |
| edge-tts | 7.2.8 | Microsoft Neural TTS voice generation |
| pydub | 0.25.1 | Audio segment manipulation |
| PyCharm | Community | IDE used for development |

 Pipeline Architecture
input/peppa_test.mp4
        ↓
[ Stage 1 ]  Audio Extraction
        ↓
[ Stage 2 ]  Noise Suppression
[ Stage 2b ] Background Music Separation
        ↓
[ Stage 3 ]  Speaker Diarization
        ↓
[ Stage 4 ]  Speech Transcription (Whisper)
        ↓
[ Stage 5 ]  Translation + Simplification
        ↓
[ Stage 6 ]  Hindi TTS Generation
        ↓
[ Stage 7 ]  Audio Alignment + Final Merge
        ↓
output/peppa_dubbed_hindi.mp4

 Project Structure

peppa_dubbing/
├── input/
│   └── peppa_test.mp4          ← source video
├── output/
│   ├── 01_extracted_audio.wav
│   ├── 02_denoised_audio.wav
│   ├── 02b_background_music.wav
│   ├── 03_diarization.json
│   ├── 04_transcription.json
│   ├── 05_translated.json
│   ├── 06_tts_segments.json
│   ├── tts_segments/           ← individual Hindi MP3s
│   ├── tts_stretched/          ← time-adjusted WAVs
│   ├── 07_dubbed_audio.wav
│   ├── 07b_mixed_audio.wav
│   └── peppa_dubbed_hindi.mp4  ← FINAL OUTPUT
├── stages/
│   ├── stage1_extract.py
│   ├── stage2_denoise.py
│   ├── stage2b_separate.py
│   ├── stage3_diarize.py
│   ├── stage4_transcribe.py
│   ├── stage5_translate.py
│   ├── stage6_tts.py
│   └── stage7_align.py
└── main.py                     ← runs entire pipeline

 Stage-by-Stage Explanation

 Stage 1 — Audio Extraction
Extracts the raw audio track from the input MP4 video file using FFmpeg via imageio_ffmpeg. Converts to WAV format at 16000Hz sample rate, mono channel. 16kHz is specifically chosen because Whisper requires this sample rate.

 Stage 2 — Noise Suppression
Cleans up the audio by removing background noise using librosa. Performs Short-Time Fourier Transform (STFT), estimates noise from the first 10 frames, applies spectral subtraction, then converts back using Inverse STFT.

 Stage 2b — Background Music Separation
Extracts just the background music by using diarization data to know exactly when speech occurs, creating a mask that zeros out all speech regions, then applying spectral smoothing to reduce artifacts.
 Stage 3 — Speaker Diarization
Detects when speech is happening using energy-based voice activity detection via librosa. Computes RMS energy, sets threshold at 50% of mean energy, and merges consecutive speech frames into segments.

Stage 4 — Speech Transcription
Uses **OpenAI Whisper (base model)** to convert English speech into text with timestamps. Loads audio via librosa at 16kHz and passes raw audio array directly to Whisper's transformer-based encoder-decoder.

 Stage 5 — Translation + Simplification
- **Whisper corrections:** Fixes common mishearing errors (e.g. "Pepper Pig" → "Peppa Pig")
- **Translation:** Uses MyMemoryTranslator for better Hindi quality than Google Translate
- **Simplification dictionary:** 100+ word replacements converting complex Hindi to child-friendly equivalents
- **Segment filtering:** Skips segments that are too short, gibberish, or repeated

 Stage 6 — Hindi TTS Generation
Uses **Microsoft Edge TTS** (hi-IN-SwaraNeural voice) to generate natural-sounding Hindi speech. Dynamically adjusts speaking rate based on original segment duration to reduce time-stretching needed later.

 Stage 7 — Audio Alignment and Final Merge
Time stretching:** Uses FFmpeg's atempo filter to fit each segment to its timestamp
Audio mixing:** Uses FFmpeg's adelay filter to position each segment correctly
Final merge:** Mixes Hindi voice (1.8x volume) with background music (1.2x volume) and combines with original video

 AI Models Used

| Model | Type | Purpose |
|-------|------|---------|
| OpenAI Whisper (base) | Speech Recognition Transformer | English transcription with timestamps |
| Microsoft hi-IN-SwaraNeural | Neural TTS | Natural Hindi voice generation |
| MyMemory Translator | Machine Translation | English to Hindi translation |

 How to Run
bash
 Install dependencies
pip install moviepy ffmpeg-python imageio[ffmpeg] librosa soundfile
pip install openai-whisper torch==2.2.0+cpu --index-url https://download.pytorch.org/whl/cpu
pip install deep-translator edge-tts noisereduce pydub

 Run entire pipeline
python main.py

 Challenges and Solutions

| Challenge | Solution |
|-----------|----------|
| DeepFilterNet requires Rust compiler | Switched to librosa-based spectral subtraction |
| pyannote.audio numpy/torch conflicts | Switched to energy-based VAD using librosa |
| Whisper FFmpeg PATH issue on Windows | Load audio via librosa, pass numpy array directly |
| PyTorch fbgemm.dll missing | Install CPU-only PyTorch from official wheel |
| Google Translate produces complex Hindi | Switched to MyMemoryTranslator |
| Character names being translated | Priority-ordered replacement dictionary |
| TTS audio too long/short for segments | Dynamic rate adjustment + atempo stretching |
| Words getting cut off | 30% overflow buffer in alignment stage |
| Gibberish from background music | Segment skip list with phrase matching |

---
 Possible Improvements

Better diarization** — use pyannote.audio for proper multi-speaker identification
Voice cloning** — use Coqui XTTS to clone Peppa's actual voice
Better source separation** — use Demucs (Meta's model) for cleaner background music
LLM post-processing** — use Claude or GPT for more contextually natural translations
Lip sync** — use Wav2Lip to align mouth movements with dubbed audio


## 💡 Key Learning Points

- Real-world AI pipelines require handling many dependency conflicts
- Simple approaches often work better than complex ones when dependencies are problematic
- Audio timing and synchronization is the hardest part of dubbing
- TTS quality has a huge impact on the final output
- Building modular stages makes debugging and iteration much easier

 Built by Jessinia Shaik
Hackathon Project — AI Audio Dubbing Platform
