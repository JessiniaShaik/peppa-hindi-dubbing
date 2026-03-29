import os
import json
import whisper
import numpy as np
import librosa

def transcribe_audio(input_path: str, output_dir: str = "output") -> list:
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "04_transcription.json")

    print("Loading Whisper model...")
    model = whisper.load_model("base")

    print(f"Loading audio: {input_path}")
    audio, sr = librosa.load(input_path, sr=16000, mono=True)
    audio = audio.astype(np.float32)

    print("Transcribing...")
    result = model.transcribe(audio, language="en", word_timestamps=True)

    segments = []
    for segment in result["segments"]:
        seg = {
            "id": segment["id"],
            "start_time": round(segment["start"], 2),
            "end_time": round(segment["end"], 2),
            "text": segment["text"].strip()
        }
        segments.append(seg)
        print(f"  [{seg['start_time']}s → {seg['end_time']}s] {seg['text']}")

    with open(output_path, "w") as f:
        json.dump(segments, f, indent=2, ensure_ascii=False)

    print(f"✅ Transcription → {output_path} ({len(segments)} segments)")
    return segments


if __name__ == "__main__":
    INPUT = "output/02_denoised_audio.wav"
    transcribe_audio(INPUT)