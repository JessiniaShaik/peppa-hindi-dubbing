import os
import json
import subprocess
import imageio_ffmpeg

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()


def get_audio_duration(path: str) -> float:
    cmd = [FFMPEG, "-i", path, "-f", "null", "-"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    for line in result.stderr.split("\n"):
        if "Duration" in line:
            t = line.split("Duration:")[1].split(",")[0].strip()
            h, m, s = t.split(":")
            return float(h) * 3600 + float(m) * 60 + float(s)
    return 0.0


def get_tempo_filter(ratio: float) -> str:
    ratio = max(0.6, min(1.6, ratio))
    if ratio <= 0.5:
        return f"atempo=0.5,atempo={ratio/0.5:.3f}"
    elif ratio >= 2.0:
        return f"atempo=2.0,atempo={ratio/2.0:.3f}"
    else:
        return f"atempo={ratio:.3f}"


def build_dubbed_audio(tts_path: str, output_dir: str = "output") -> str:
    os.makedirs(output_dir, exist_ok=True)
    stretched_dir = os.path.join(output_dir, "tts_stretched")
    os.makedirs(stretched_dir, exist_ok=True)

    print("Loading TTS segments...")
    with open(tts_path, "r", encoding="utf-8") as f:
        segments = json.load(f)

    dubbed_audio = os.path.join(output_dir, "07_dubbed_audio.wav")
    input_args = []
    filter_parts = []
    valid_segments = []

    print("Fitting each segment to original duration...")
    for seg in segments:
        audio_path = seg["audio_path"]
        if not os.path.exists(audio_path):
            continue

        tts_dur = get_audio_duration(audio_path)
        orig_dur = seg["original_duration"]

        if tts_dur <= 0 or orig_dur <= 0:
            continue

        ratio = tts_dur / orig_dur

        # Allow up to 1.3x overflow before stretching
        # so short segments don't get cut off
        if ratio <= 1.3:
            allowed_dur = tts_dur
        else:
            allowed_dur = orig_dur * 1.3

        stretched_path = os.path.join(stretched_dir, f"seg_{seg['id']:03d}.wav")

        if 0.85 <= ratio <= 1.3:
            # Close enough — convert without stretching
            subprocess.run([
                FFMPEG, "-y", "-i", audio_path,
                "-ar", "16000", "-ac", "1",
                stretched_path
            ], capture_output=True)
        else:
            # Stretch or compress to fit
            target_ratio = tts_dur / allowed_dur
            target_ratio = max(0.6, min(1.6, target_ratio))
            tempo_filter = get_tempo_filter(target_ratio)
            subprocess.run([
                FFMPEG, "-y", "-i", audio_path,
                "-filter:a", tempo_filter,
                "-ar", "16000", "-ac", "1",
                stretched_path
            ], capture_output=True)

        seg["stretched_path"] = stretched_path
        valid_segments.append(seg)
        print(f"  Segment {seg['id']:03d}: TTS={tts_dur:.1f}s → Target={orig_dur:.1f}s (ratio={ratio:.2f})")

    for i, seg in enumerate(valid_segments):
        start_ms = int(seg["start_time"] * 1000)
        input_args += ["-i", seg["stretched_path"]]
        filter_parts.append(
            f"[{i}:a]afade=t=in:st=0:d=0.03,adelay={start_ms}|{start_ms}[s{i}]"
        )

    mix_inputs = "".join([f"[s{i}]" for i in range(len(valid_segments))])
    filter_complex = ";".join(filter_parts) + f";{mix_inputs}amix=inputs={len(valid_segments)}:normalize=0[out]"

    cmd = [FFMPEG, "-y"] + input_args + [
        "-filter_complex", filter_complex,
        "-map", "[out]",
        "-ar", "16000", "-ac", "1",
        dubbed_audio
    ]

    print("Mixing all segments...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Mixing failed:\n{result.stderr[-500:]}")

    print(f"✅ Dubbed audio → {dubbed_audio}")
    return dubbed_audio


def merge_with_video(video_path: str, dubbed_audio: str, background_music: str, output_dir: str = "output") -> str:
    output_path = os.path.join(output_dir, "peppa_dubbed_hindi.mp4")

    print("Mixing Hindi voice with background music...")
    mixed_audio = os.path.join(output_dir, "07b_mixed_audio.wav")

    mix_cmd = [
        FFMPEG, "-y",
        "-i", dubbed_audio,
        "-i", background_music,
        "-filter_complex",
        "[0:a]volume=1.8[voice];[1:a]volume=1.2[music];[voice][music]amix=inputs=2:normalize=0[out]",
        "-map", "[out]",
        "-ar", "16000",
        "-ac", "1",
        mixed_audio
    ]

    result = subprocess.run(mix_cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Mixing failed:\n{result.stderr[-500:]}")

    print("Merging with video...")
    cmd = [
        FFMPEG, "-y",
        "-i", video_path,
        "-i", mixed_audio,
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-c:v", "copy",
        "-c:a", "aac",
        "-shortest",
        output_path
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Merge failed:\n{result.stderr[-500:]}")

    print(f"✅ Final dubbed video → {output_path}")
    return output_path


if __name__ == "__main__":
    TTS_JSON = "output/06_tts_segments.json"
    VIDEO = "input/peppa_test.mp4"
    BACKGROUND = "output/02b_background_music.wav"
    dubbed = build_dubbed_audio(TTS_JSON)
    merge_with_video(VIDEO, dubbed, BACKGROUND)