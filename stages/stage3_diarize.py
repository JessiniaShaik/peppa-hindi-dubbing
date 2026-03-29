import os
import json
import librosa
import numpy as np

def diarize_audio(input_path: str, output_dir: str = "output") -> list:
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "03_diarization.json")

    print(f"Loading audio: {input_path}")
    audio, sr = librosa.load(input_path, sr=16000, mono=True)

    print("Detecting speech segments...")
    hop_length = 512
    frame_length = 2048
    energy = librosa.feature.rms(y=audio, frame_length=frame_length, hop_length=hop_length)[0]
    threshold = np.mean(energy) * 0.5
    speech_frames = energy > threshold

    segments = []
    in_speech = False
    start_time = 0.0
    min_segment_duration = 1.0

    for i, is_speech in enumerate(speech_frames):
        time = librosa.frames_to_time(i, sr=sr, hop_length=hop_length)
        if is_speech and not in_speech:
            start_time = time
            in_speech = True
        elif not is_speech and in_speech:
            duration = time - start_time
            if duration >= min_segment_duration:
                segments.append({
                    "speaker": "SPEAKER_00",
                    "start_time": round(start_time, 2),
                    "end_time": round(time, 2)
                })
            in_speech = False

    if in_speech:
        segments.append({
            "speaker": "SPEAKER_00",
            "start_time": round(start_time, 2),
            "end_time": round(len(audio) / sr, 2)
        })

    for seg in segments:
        print(f"  {seg['speaker']}: {seg['start_time']}s → {seg['end_time']}s")

    with open(output_path, "w") as f:
        json.dump(segments, f, indent=2)

    print(f"✅ Diarization → {output_path} ({len(segments)} segments)")
    return segments


if __name__ == "__main__":
    INPUT = "output/02_denoised_audio.wav"
    diarize_audio(INPUT)