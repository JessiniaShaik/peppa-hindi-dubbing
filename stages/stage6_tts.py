import os
import json
import asyncio
import subprocess
import imageio_ffmpeg
import edge_tts

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()

def get_audio_duration(audio_path: str) -> float:
    cmd = [FFMPEG, "-i", audio_path, "-f", "null", "-"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    for line in result.stderr.split("\n"):
        if "Duration" in line:
            time_str = line.split("Duration:")[1].split(",")[0].strip()
            h, m, s = time_str.split(":")
            return float(h) * 3600 + float(m) * 60 + float(s)
    return 0.0

async def generate_segment(text: str, audio_path: str, rate: str = "-10%"):
    communicate = edge_tts.Communicate(text, voice="hi-IN-SwaraNeural", rate=rate)
    await communicate.save(audio_path)

def calculate_rate(original_duration: float, estimated_chars: int) -> str:
    # Rough chars-per-second for Hindi TTS at default rate is ~12
    estimated_tts_duration = estimated_chars / 12.0
    if estimated_tts_duration <= 0 or original_duration <= 0:
        return "-10%"
    ratio = estimated_tts_duration / original_duration
    if ratio > 1.3:
        # TTS will be too long — speed it up
        rate_pct = min(int((ratio - 1) * 100), 50)
        return f"+{rate_pct}%"
    elif ratio < 0.7:
        # TTS will be too short — slow it down
        rate_pct = min(int((1 - ratio) * 100), 30)
        return f"-{rate_pct}%"
    else:
        return "-10%"

def generate_tts(input_path: str, output_dir: str = "output") -> list:
    os.makedirs(output_dir, exist_ok=True)
    tts_dir = os.path.join(output_dir, "tts_segments")
    os.makedirs(tts_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "06_tts_segments.json")

    print("Loading translated segments...")
    with open(input_path, "r", encoding="utf-8") as f:
        segments = json.load(f)

    print("Generating Hindi TTS audio (Microsoft Neural Voice)...")
    tts_segments = []

    for seg in segments:
        hindi_text = seg["translated"]
        if not hindi_text:
            continue

        segment_id = seg["id"]
        audio_path = os.path.join(tts_dir, f"seg_{segment_id:03d}.mp3")
        original_duration = seg["end_time"] - seg["start_time"]

        # Pick a rate that pre-adjusts speed before stretching
        rate = calculate_rate(original_duration, len(hindi_text))

        asyncio.run(generate_segment(hindi_text, audio_path, rate=rate))
        duration = get_audio_duration(audio_path)

        tts_seg = {
            "id": segment_id,
            "start_time": seg["start_time"],
            "end_time": seg["end_time"],
            "original_duration": round(original_duration, 2),
            "tts_duration": round(duration, 2),
            "translated": hindi_text,
            "audio_path": audio_path
        }
        tts_segments.append(tts_seg)
        print(f"  Segment {segment_id:03d}: orig={original_duration:.1f}s tts={duration:.1f}s rate={rate}")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(tts_segments, f, indent=2, ensure_ascii=False)

    print(f"✅ TTS → {output_path} ({len(tts_segments)} segments)")
    return tts_segments


if __name__ == "__main__":
    INPUT = "output/05_translated.json"
    generate_tts(INPUT)