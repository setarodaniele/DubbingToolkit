# fetch_google_voices.py

import os
import json
from datetime import datetime
from google.cloud import texttospeech
from google.oauth2 import service_account
from google.api_core.exceptions import GoogleAPIError

# cartella radice DubbingToolkit
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # se lo script sta in voices/

SERVICE_ACCOUNT_FILE = os.path.join(BASE_DIR, "Tools", "google_speech_credentials.json")
VOICE_DIR = os.path.join(BASE_DIR, "voices")
COMPLETE_FILE = os.path.join(VOICE_DIR, "voices_google_complete.json")
FILTERED_FILE = os.path.join(VOICE_DIR, "voices_google.json")

# Lista engine considerati moderni / utilizzabili
MODERN_ENGINES = ["Wavenet", "Neural2", "Chirp3-HD", "Chirp-HD"]

def download_complete_json():
    """Scarica tutte le voci da Google e salva in voices_google_complete.json con estrazione corretta del nome e engine"""
    try:
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE
        )
        client = texttospeech.TextToSpeechClient(credentials=credentials)
        response = client.list_voices()

        voices_data = []
        for voice in response.voices:
            full_name = voice.name
            language_code = voice.language_codes[0] if voice.language_codes else "unknown"

            # Trova engine presente nel full_name, case-sensitive, ordinando per lunghezza decrescente
            found_engine = "unknown"
            for engine in sorted(MODERN_ENGINES, key=len, reverse=True):
                if engine in full_name:
                    found_engine = engine
                    break

            # Estrae il nome reale della voce: togli codice lingua e engine dal full_name
            name = full_name
            if name.startswith(language_code + "-"):
                name = name[len(language_code) + 1:]
            if found_engine != "unknown" and name.startswith(found_engine + "-"):
                name = name[len(found_engine) + 1:]

            display_name = name  # per Google è già il nome "umano"

            voices_data.append({
                "full_name": full_name,
                "name": name,
                "display_name": display_name,
                "api_tag": full_name,
                "languageCodes": language_code,
                "engine": found_engine,
                "ssmlGender": texttospeech.SsmlVoiceGender(voice.ssml_gender).name,
                "naturalSampleRateHertz": voice.natural_sample_rate_hertz
            })

        output_payload = {
            "provider": "google",
            "fetched_at": datetime.utcnow().isoformat(),
            "total_voices": len(voices_data),
            "voices": voices_data
        }

        with open(COMPLETE_FILE, "w", encoding="utf-8") as f:
            json.dump(output_payload, f, indent=4, ensure_ascii=False)

        print(f"OK - Salvate {len(voices_data)} voci in voices_google_complete.json")

    except GoogleAPIError as e:
        print("Errore API Google:", e)
    except Exception as e:
        print("Errore generico:", e)


def filter_and_normalize():
    """Filtra il JSON completo mantenendo solo le voci moderne con franchigia gratuita"""
    TTS_COST_FILE = os.path.join(BASE_DIR, "Billing", "tts_voices_cost.json")

    try:
        # Carica le voci complete
        with open(COMPLETE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Carica i dati di costo e franchigia
        with open(TTS_COST_FILE, "r", encoding="utf-8") as f:
            tts_cost_data = json.load(f)

        # Lista engine Google da considerare (coerenti con JSON costi)
        GOOGLE_ENGINES = ["Standard", "Wavenet", "Neural2", "Studio", "Polyglot_preview", "Chirp3-HD"]

        filtered_voices = []
        for v in data["voices"]:
            engine = v.get("engine", "unknown")
            if engine in GOOGLE_ENGINES:
                cost_info = tts_cost_data["google"].get(engine)
                if cost_info and cost_info.get("franchigia_gratuita", 0) > 0:
                    filtered_voices.append(v)

        output_payload = {
            "provider": "google",
            "fetched_at": data.get("fetched_at"),
            "total_voices": len(filtered_voices),
            "voices": filtered_voices
        }

        with open(FILTERED_FILE, "w", encoding="utf-8") as f:
            json.dump(output_payload, f, indent=4, ensure_ascii=False)

        print(f"OK - Salvate {len(filtered_voices)} voci filtrate in voices_google.json")

    except FileNotFoundError:
        print("File completo non trovato. Devi prima scaricare le voci complete.")
    except Exception as e:
        print("Errore durante il filtraggio:", e)


if __name__ == "__main__":
    if os.path.exists(COMPLETE_FILE):
        choice = input("voices_google_complete.json già esiste. Vuoi riscaricarlo? (y/n): ").strip().lower()
        if choice == "y":
            download_complete_json()
    else:
        download_complete_json()

    # Sempre esegue il filtraggio e normalizzazione
    filter_and_normalize()