# GenerateWhisperLangs.py - versione autonoma con messaggi e conferma
import json
import whisper
from pathlib import Path
from core.messages import Messages

# ------------------------------------------------------
# Percorso progetto e file di output
# ------------------------------------------------------
ROOT = Path(__file__).parent.parent
OUTPUT_FILE = ROOT / "Locale" / "System" / "whisper_languages.json"

# ------------------------------------------------------
# Carica messaggi
# ------------------------------------------------------
msgs = Messages()

# Assicuriamoci che la cartella esista
OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

# ------------------------------------------------------
# Funzione principale
# ------------------------------------------------------
def main():
    try:
        langs = whisper.tokenizer.LANGUAGES
    except Exception as e:
        print(msgs.GWL_RetrievalError.format(e))
        return

    sorted_langs = dict(sorted(langs.items(), key=lambda x: x[0]))

    if OUTPUT_FILE.exists():
        resp = input(f"{msgs.GWL_WhisperLangJSONExists} Sovrascrivere? (s/N): ").strip().lower()
        if resp != "s":
            print(msgs.GWL_WhisperLangJSONExists)
            return

    try:
        with OUTPUT_FILE.open("w", encoding="utf-8") as f:
            json.dump(sorted_langs, f, indent=4, ensure_ascii=False)
        print(msgs.GWL_WhisperLangJSONCreated)
    except Exception as e:
        print(msgs.GWL_WriteError.format(e))

if __name__ == "__main__":
    print(msgs.GWL_CreatingWhisperLangJSON)
    main()