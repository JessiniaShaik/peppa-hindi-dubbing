import os
import numpy as np
import soundfile as sf
import librosa

def denoise_audio(input_path: str, output_dir: str = "output") -> str:
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "02_denoised_audio.wav")

    print(f"Loading audio: {input_path}")
    audio, sr = librosa.load(input_path, sr=16000, mono=True)

    print("Applying noise suppression...")
    stft = librosa.stft(audio)
    magnitude, phase = librosa.magphase(stft)
    noise_estimate = np.mean(magnitude[:, :10], axis=1, keepdims=True)
    magnitude_denoised = np.maximum(magnitude - noise_estimate, 0)
    stft_denoised = magnitude_denoised * phase
    audio_denoised = librosa.istft(stft_denoised)

    sf.write(output_path, audio_denoised, sr)
    size_kb = os.path.getsize(output_path) / 1024
    print(f"✅ Denoised → {output_path} ({size_kb:.1f} KB)")
    return output_path


if __name__ == "__main__":
    INPUT = "output/01_extracted_audio.wav"
    denoise_audio(INPUT)