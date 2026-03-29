import os
import subprocess
import torch
import imageio_ffmpeg
from demucs.pretrained import get_model
from demucs.apply import apply_model
import torchaudio

def separate_background(input_path: str, output_dir: str = "output") -> str:
    os.makedirs(output_dir, exist_ok=True)
    background_path = os.path.join(output_dir, "02b_background_music.wav")

    print("Loading Demucs model...")
    model = get_model("htdemucs")
    model.eval()

    print(f"Loading audio: {input_path}")
    wav, sr = torchaudio.load(input_path)

    # Resample to model's expected sample rate (44100)
    if sr != model.samplerate:
        wav = torchaudio.functional.resample(wav, sr, model.samplerate)

    # Make stereo if mono
    if wav.shape[0] == 1:
        wav = wav.repeat(2, 1)

    wav = wav.unsqueeze(0)  # add batch dimension

    print("Separating vocals from background (2-3 mins)...")
    with torch.no_grad():
        sources = apply_model(model, wav, progress=True)[0]

    # sources order: drums, bass, other, vocals
    source_names = model.sources
    print(f"Available stems: {source_names}")

    # Get everything except vocals (drums + bass + other)
    vocals_idx = source_names.index("vocals")
    background = torch.zeros_like(sources[0])
    for i, name in enumerate(source_names):
        if name != "vocals":
            background += sources[i]

    # Convert back to mono 16kHz
    background_mono = background.mean(0, keepdim=True)
    background_mono = torchaudio.functional.resample(background_mono, model.samplerate, 16000)

    torchaudio.save(background_path, background_mono, 16000)
    size_kb = os.path.getsize(background_path) / 1024
    print(f"✅ Background music (no dialogue) → {background_path} ({size_kb:.1f} KB)")
    return background_path


if __name__ == "__main__":
    INPUT = "output/01_extracted_audio.wav"
    separate_background(INPUT)