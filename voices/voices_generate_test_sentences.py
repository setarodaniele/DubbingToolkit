# =========================================================
# voices_generate_test_sentences.py
# =========================================================

import json
from pathlib import Path
from datetime import datetime
from google.cloud import translate_v2 as translate
from google.oauth2 import service_account

# =========================================================
# CONFIG
# =========================================================

BASE_TEXT = "This is a sample sentence to test how this voice sounds for narration and dialogue."

VOICES_DIR = Path(__file__).parent
AZURE_JSON = VOICES_DIR / "voices_azure_complete.json"
GOOGLE_JSON = VOICES_DIR / "voices_google.json"

OUTPUT_JSON = VOICES_DIR / "voices_test_sentences.json"
LOG_FILE = VOICES_DIR / "voices_generate_test_sentences.log"

CREDENTIALS_PATH = r"D:\RecordingStudio\DubbingToolkit\Tools\google_speech_credentials.json"

PLACEHOLDER = "[TRANSLATION NOT AVAILABLE]"

# =========================================================
# INIT TRANSLATOR
# =========================================================

credentials = service_account.Credentials.from_service_account_file(CREDENTIALS_PATH)
translator = translate.Client(credentials=credentials)

# =========================================================
# UTILITIES
# =========================================================

def log(message: str):
    timestamp = datetime.utcnow().isoformat()
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")

def normalize_language_code(code: str) -> str:
    if not code:
        return None
    return code.replace("_", "-").strip()

def extract_base_language(code: str) -> str:
    return code.split("-")[0]

def load_language_codes(json_path: Path) -> set:
    if not json_path.exists():
        raise FileNotFoundError(f"File non trovato: {json_path}")

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    languages = set()
    for voice in data.get("voices", []):
        code = voice.get("languageCodes")
        if code:
            normalized = normalize_language_code(code)
            languages.add(normalized)
    return languages

# =========================================================
# MAIN
# =========================================================

def main():
    print("Caricamento liste voci...")

    azure_languages = load_language_codes(AZURE_JSON)
    google_languages = load_language_codes(GOOGLE_JSON)

    all_languages = sorted(azure_languages.union(google_languages))
    print(f"Lingue uniche trovate: {len(all_languages)}")

    sentences = {}
    failed_languages = []

    # Memorizza le traduzioni già fatte per lingua base
    translations_cache = {}

    for lang in all_languages:
        # Inglese: usa frase base
        if lang.lower().startswith("en"):
            sentences[lang] = BASE_TEXT
            continue

        base_lang = extract_base_language(lang)

        # Se traduzione già fatta, riutilizza
        if base_lang in translations_cache:
            sentences[lang] = translations_cache[base_lang]
            print(f"[OK] {lang} -> {base_lang} (riutilizzata)")
            continue

        # Prova a tradurre
        try:
            result = translator.translate(BASE_TEXT, target_language=base_lang)
            translated_text = result.get("translatedText", PLACEHOLDER)

            sentences[lang] = translated_text
            translations_cache[base_lang] = translated_text

            print(f"[OK] {lang} -> {base_lang}")

        except Exception as e:
            log(f"Traduzione fallita per {lang}: {str(e)}")
            sentences[lang] = PLACEHOLDER
            failed_languages.append(lang)
            print(f"[PLACEHOLDER] {lang}")

    # Salvataggio JSON
    output_data = {
        "meta": {
            "base_text": BASE_TEXT,
            "generated_at": datetime.utcnow().isoformat(),
            "total_languages": len(sentences),
            "failed_languages": failed_languages
        },
        "sentences": sentences
    }

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=4, ensure_ascii=False)

    print("\nCompletato.")
    print(f"File salvato: {OUTPUT_JSON}")
    print(f"Lingue con placeholder: {len(failed_languages)}")

if __name__ == "__main__":
    main()