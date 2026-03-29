import os
import subprocess
from moviepy import VideoFileClip
import imageio_ffmpeg

def get_ffmpeg_path():
    return imageio_ffmpeg.get_ffmpeg_exe()

def extract_audio(video_path: str, output_dir: str = "output") -> str:
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "01_extracted_audio.wav")
    ffmpeg = get_ffmpeg_path()

    command = [
        ffmpeg, "-i", video_path,
        "-vn",
        "-acodec", "pcm_s16le",
        "-ar", "16000",
        "-ac", "1",
        "-y",
        output_path
    ]

    print(f"Extracting audio from: {video_path}")
    result = subprocess.run(command, capture_output=True, text=True)

    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg failed:\n{result.stderr}")

    size_kb = os.path.getsize(output_path) / 1024
    print(f"✅ Extracted → {output_path} ({size_kb:.1f} KB)")
    return output_path


def get_video_info(video_path: str) -> dict:
    clip = VideoFileClip(video_path)
    info = {
        "duration_seconds": round(clip.duration, 2),
        "fps": clip.fps,
        "has_audio": clip.audio is not None,
        "resolution": clip.size
    }
    clip.close()
    return info


if __name__ == "__main__":
    VIDEO = "input/peppa_test.mp4"

    print("Analysing video...")
    info = get_video_info(VIDEO)
    print(f"  Duration   : {info['duration_seconds']}s")
    print(f"  FPS        : {info['fps']}")
    print(f"  Resolution : {info['resolution']}")
    print(f"  Has audio  : {info['has_audio']}")

    if not info["has_audio"]:
        print("No audio track found!")
    else:
        extract_audio(VIDEO)