import os
import json
from deep_translator import MyMemoryTranslator

SIMPLIFY_DICT = {
    # Fix gibberish/misheared segments
    "पाई जल्दी खींचो": "",
    "पाई पानी्दी खींचो": "",
    "andho me kana raja": "",
    "आह संगीत": "",

    # Fix unpleasant/inappropriate words
    "चाटना": "खाना",
    "चाट": "खा",
    "चाटता": "खाता",
    "चाटती": "खाती",
    "चाटो": "खाओ",
    "थूकना": "नहीं करना",
    "थूको": "मत करो",

    # Fix fever mistranslation
    "बहुत बहुत हॉट हो": "बुखार है",
    "तुम बहुत hot हो": "तुम्हें बुखार है",
    "बहुत hot हो": "बुखार है",
    "hot हो": "बुखार है",
    "बहुत गरम हो": "तुम्हें बुखार है",
    "बहुत हॉट हो": "बुखार है",
    "हॉट हो": "बुखार है",
    "तीन सौ डिग्री": "बुखार",
    "तीन डिग्री": "बुखार",

    # Fix kholo mistranslation
    "कृपया खोल दोें": "मुँह खोलो",
    "कृपया खोलो": "खोलो",
    "पूरा खोलो": "खोलो",
    "पूरा खोल": "खोल दो",
    "पूरा कर": "कर दो",
    "पूरा करो": "करो",
    "पूर्ण करो": "करो",
    "पूर्ण": "पूरा",
    "संपूर्ण": "पूरा",

    # Fix bowl mistranslation
    "किसी को कटोरे को खाना होगा": "कोई कटोरा चाटेगा",
    "कटोरे को खाना": "कटोरा चाटना",

    # Fix Pig/character name mistranslations FIRST (order matters)
    "पेप्पा सुअर": "Peppa Pig",
    "मम्मी सुअर": "Mummy Pig",
    "डैडी सुअर": "Daddy Pig",
    "सूसी भेड़": "Susie Sheep",
    "माँ Pig": "Mummy Pig",
    "सुअर": "Pig",
    "काली मिर्च": "Peppa",
    "पेप्पर": "Peppa",
    "भेड़": "Sheep",
    "मोबी": "Mummy",
    "पापाजी": "Daddy",

    # Fix doctor/medical translations
    "ज्वर": "बुखार",
    "तापमान": "बुखार",
    "चिकित्सक": "डॉक्टर",
    "औषधि": "दवाई",
    "स्वस्थ": "ठीक",
    "अस्वस्थ": "बीमार",
    "उपचार": "इलाज",
    "पीड़ा": "दर्द",
    "मरीज़": "मरीज",
    "आगंतुक": "मिलने वाले",
    "मलबा": "कुछ",

    # Formal/complex words → simple child-friendly equivalents
    "शयनकक्ष": "कमरा",
    "प्रतीक्षा": "इंतज़ार",
    "आगमन": "आना",
    "प्रस्थान": "जाना",
    "निवास": "घर",
    "भोजन": "खाना",
    "जल": "पानी",
    "पुस्तक": "किताब",
    "विद्यालय": "स्कूल",
    "अध्यापक": "टीचर",
    "मित्र": "दोस्त",
    "क्रीड़ा": "खेल",
    "उपयोग": "इस्तेमाल",
    "समाप्त": "खत्म",
    "प्रारंभ": "शुरू",
    "तत्पश्चात": "फिर",
    "पश्चात": "बाद में",
    "अत्यंत": "बहुत",
    "संभवतः": "शायद",
    "वास्तव": "सच में",
    "इच्छा": "चाहना",
    "आनंद": "मज़ा",
    "प्रसन्न": "खुश",
    "क्रोधित": "गुस्सा",
    "भयभीत": "डरा हुआ",
    "शीघ्र": "जल्दी",
    "धीरे-धीरे": "आराम से",
    "परंतु": "लेकिन",
    "तथापि": "फिर भी",
    "तब्दील": "बन",
    "आवश्यक": "ज़रूरी",
    "विशेष": "खास",
    "निद्रा": "नींद",
    "स्वप्न": "सपना",
    "वर्षा": "बारिश",
    "सूर्य": "सूरज",
    "चंद्रमा": "चाँद",
    "आकाश": "आसमान",
    "वायु": "हवा",
    "पुष्प": "फूल",
    "वृक्ष": "पेड़",
    "उद्यान": "बगीचा",
    "क्षेत्र": "जगह",
    "स्थान": "जगह",
    "गृह": "घर",
    "द्वार": "दरवाज़ा",
    "रसोई": "किचन",
    "स्नानघर": "बाथरूम",
    "वस्त्र": "कपड़े",
    "पादत्राण": "जूते",
    "वाहन": "गाड़ी",
    "यात्रा": "सफर",
    "माता": "मम्मी",
    "पिता": "पापा",
    "भ्राता": "भाई",
    "भगिनी": "बहन",
    "मित्रता": "दोस्ती",
    "प्रेम": "प्यार",
    "सहायता": "मदद",
    "क्षमा": "माफ़ी",
    "प्रश्न": "सवाल",
    "उत्तर": "जवाब",
    "कठिन": "मुश्किल",
    "सरल": "आसान",
    "तीव्र": "तेज़",
    "मंद": "धीमा",
    "उच्च": "ऊँचा",
    "निम्न": "नीचा",
    "विशाल": "बड़ा",
    "क्षुद्र": "छोटा",
    "चिकित्सालय": "अस्पताल",
    "परिवहन": "गाड़ी",
    "धन": "पैसे",
    "अकेलापन": "अकेला",
}


def simplify_hindi(text: str) -> str:
    for complex_word, simple_word in SIMPLIFY_DICT.items():
        text = text.replace(complex_word, simple_word)
    return text


def translate_segments(input_path: str, output_dir: str = "output") -> list:
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "05_translated.json")

    print("Loading transcription...")
    with open(input_path, "r", encoding="utf-8") as f:
        segments = json.load(f)

    print("Translating English → Hindi (MyMemory)...")
    translator = MyMemoryTranslator(source="en-US", target="hi-IN")
    translated_segments = []

    skip_phrases = [
        "George wants to play too",
        "puppwuk",
        "95",
        "Pie pull quick",
        "pie pull",
        "Ah music",
        "And me.",
        "andho",
    ]

    for seg in segments:
        text = seg["text"].strip()
        if not text:
            continue

        # Fix Whisper mishearing corrections
        text = text.replace("Pepper Pig", "Peppa Pig")
        text = text.replace("pepper pig", "Peppa Pig")
        text = text.replace("Pepper's", "Peppa's")
        text = text.replace("Pepper,", "Peppa,")
        text = text.replace("Pepper.", "Peppa.")
        text = text.replace("Pepper ", "Peppa ")
        text = text.replace("Moby Pig", "Mummy Pig")
        text = text.replace("Moby.", "Mummy.")
        text = text.replace("Yes, Moby", "Yes, Mummy")
        text = text.replace("moby", "Mummy")

        # Skip unwanted/repeated/gibberish segments
        if any(phrase.lower() in text.lower() for phrase in skip_phrases):
            print(f"  SKIPPED: {text}")
            continue

        # Skip very short segments under 0.5s
        duration = seg["end_time"] - seg["start_time"]
        if duration < 0.5:
            print(f"  SKIPPED (too short {duration:.1f}s): {text}")
            continue

        try:
            hindi_text = translator.translate(text)
        except Exception as e:
            print(f"  ⚠️ Translation failed for: {text} — {e}")
            continue

        hindi_simple = simplify_hindi(hindi_text)

        # Skip if empty after simplification
        if not hindi_simple.strip():
            print(f"  SKIPPED (empty): {text}")
            continue

        translated_seg = {
            "id": seg["id"],
            "start_time": seg["start_time"],
            "end_time": seg["end_time"],
            "original": text,
            "translated": hindi_simple,
            "translated_raw": hindi_text
        }
        translated_segments.append(translated_seg)
        print(f"  EN:     {text}")
        print(f"  RAW:    {hindi_text}")
        print(f"  SIMPLE: {hindi_simple}")
        print()

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(translated_segments, f, indent=2, ensure_ascii=False)

    print(f"✅ Translation → {output_path} ({len(translated_segments)} segments)")
    return translated_segments


if __name__ == "__main__":
    INPUT = "output/04_transcription.json"
    translate_segments(INPUT)