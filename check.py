import json

with open("output/05_translated.json", "r", encoding="utf-8") as f:
    segments = json.load(f)

for seg in segments:
    dur = seg["end_time"] - seg["start_time"]
    print(f'ID {seg["id"]:03d} | {dur:.1f}s | {seg["translated"][:60]}')