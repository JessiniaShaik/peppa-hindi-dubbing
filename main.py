import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from stages.stages.stage2b_separate import separate_background
from stages.stages.stage1_extract import extract_audio
from stages.stages.stage2_denoise import denoise_audio
from stages.stages.stage3_diarize import diarize_audio
from stages.stages.stage4_transcribe import transcribe_audio
from stages.stages.stage5_translate import translate_segments
from stages.stages.stage6_tts import generate_tts
from stages.stages.stage7_align import build_dubbed_audio, merge_with_video

def run_pipeline(video_path: str):
    print("=" * 50)
    print("   PEPPA PIG DUBBING PIPELINE")
    print("=" * 50)

    print("\n[ STAGE 1 ] Audio Extraction")
    audio = extract_audio(video_path)

    print("\n[ STAGE 2 ] Noise Suppression")
    denoised = denoise_audio(audio)

    print("\n[ STAGE 2b ] Background Music Separation")
    background = separate_background(audio)

    print("\n[ STAGE 3 ] Speaker Diarization")
    diarize_audio(denoised)

    print("\n[ STAGE 4 ] Transcription (Whisper)")
    transcribe_audio(denoised)

    print("\n[ STAGE 5 ] Translation (English → Hindi)")
    translate_segments("output/04_transcription.json")

    print("\n[ STAGE 6 ] Hindi TTS Generation")
    generate_tts("output/05_translated.json")

    print("\n[ STAGE 7 ] Audio Alignment & Final Merge")
    dubbed_audio = build_dubbed_audio("output/06_tts_segments.json")
    final_video = merge_with_video(video_path, dubbed_audio, background)

    print("\n" + "=" * 50)
    print("   DUBBING COMPLETE!")
    print(f"   Output: {final_video}")
    print("=" * 50)


if __name__ == "__main__":
    VIDEO = "input/peppa_test.mp4"
    run_pipeline(VIDEO)