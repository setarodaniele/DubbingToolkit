# fetch_azure_voices.py (modifica principale)

import os
import json
import requests
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # se lo script sta in voices/
CREDENTIALS_FILE = os.path.join(BASE_DIR, "Tools", "azure_speech_credentials.json")
VOICE_DIR = os.path.join(BASE_DIR, "voices")
COMPLETE_FILE = os.path.join(VOICE_DIR, "voices_azure_complete.json")

MODERN_ENGINES = ["Neural", "Standard"]  # per eventuale filtraggio futuro

# ==========================================
# Funzione di estrazione display_name
# ==========================================
def extract_display_name(name: str) -> str:
    """
    Estrae il nome 'umano' della voce da ShortName Azure.
    Esempi:
    - en-US-DavisMultilingualNeural -> Davis
    - de-DE-Seraphina:DragonHDLatestNeural -> Seraphina
    - zh-CN-shandong-YunxiangNeural -> Yunxiang
    """

    if not name or name == "unknown":
        return name

    # Rimuove eventuale parte dopo ":"
    base = name.split(":")[0]

    # Rimuove prefisso lingua (xx-YY- o simili)
    parts = base.split("-")
    if len(parts) >= 3:
        base = parts[-1]
    else:
        base = base

    # Rimuove suffissi noti (ordine dal più lungo al più corto)
    suffixes = [
        "MultilingualNeural",
        "DragonHDLatestNeural",
        "NeuralHD",
        "Multilingual",
        "Neural",
        "Standard"
    ]

    for suffix in sorted(suffixes, key=len, reverse=True):
        if base.endswith(suffix):
            base = base[: -len(suffix)]
            break

    return base

# ==========================================
# Caricamento credenziali
# ==========================================
def load_credentials():
    with open(CREDENTIALS_FILE, "r", encoding="utf-8") as f:
        creds = json.load(f)
    if "subscription" not in creds or "region" not in creds:
        raise ValueError("Credenziali Azure incomplete: serve subscription e region")
    return creds["subscription"], creds["region"]

# ==========================================
# Download completo JSON Azure
# ==========================================
def download_complete_json():
    """Scarica tutte le voci da Azure TTS e salva in voices_azure_complete.json"""
    if os.path.exists(COMPLETE_FILE):
        risposta = input(f"{COMPLETE_FILE} esiste già. Vuoi riscaricare le voci? [s/N]: ").strip().lower()
        if risposta != "s":
            print("Saltato il download. Uso il file esistente.")
            return

    try:
        subscription, region = load_credentials()
        url = f"https://{region}.tts.speech.microsoft.com/cognitiveservices/voices/list"
        headers = {"Ocp-Apim-Subscription-Key": subscription}

        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            raise RuntimeError(f"Errore Azure API: status {response.status_code}, {response.text}")

        voices_data_raw = response.json()
        if not voices_data_raw:
            raise RuntimeError("La risposta Azure è vuota. Controllare chiave e regione.")

        voices_data = []
        for voice in voices_data_raw:
            full_name = voice.get("Name", "unknown")
            name = voice.get("ShortName", "unknown")
            locale = voice.get("Locale", "unknown")
            engine = voice.get("VoiceType", "unknown")
            gender = voice.get("Gender", "unknown")
            sample_rate = int(voice.get("SampleRateHertz", 24000))

            display_name = extract_display_name(name)

            voices_data.append({
                "full_name": full_name,
                "name": name,
                "display_name": display_name,  # nuovo campo corretto
                "api_tag": name,  # unificato per chiamata API
                "languageCodes": locale,
                "engine": engine,
                "ssmlGender": gender,
                "naturalSampleRateHertz": sample_rate
            })

        # Salva JSON completo
        os.makedirs(VOICE_DIR, exist_ok=True)
        output_payload = {
            "provider": "azure",
            "fetched_at": datetime.utcnow().isoformat(),
            "total_voices": len(voices_data),
            "voices": voices_data
        }

        with open(COMPLETE_FILE, "w", encoding="utf-8") as f:
            json.dump(output_payload, f, indent=4, ensure_ascii=False)

        print(f"OK - Salvate {len(voices_data)} voci in voices_azure_complete.json")

    except requests.RequestException as e:
        print("Errore HTTP Azure:", e)
    except Exception as e:
        print("Errore:", e)

## ==========================================
# Filtraggio voci Azure gratuite (rigoroso)
# ==========================================
def filter_free_voices():
    """
    Filtra il JSON completo mantenendo solo le voci incluse nella free tier Azure.
    Logica:
    - Controlla full_name e name per tag premium
    - Se viene trovato un tag premium, la voce viene scartata
    """
    filtered_file = os.path.join(VOICE_DIR, "voices_azure.json")
    PREMIUM_TAGS = ["hd", "dragon", "latest", "multilingual", "neuralhd"]  # suffissi premium

    try:
        with open(COMPLETE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        filtered_voices = []
        for v in data["voices"]:
            # converto in minuscolo per confronto
            full_lower = v.get("full_name", "").lower()
            name_lower = v.get("name", "").lower()

            # scarta se contiene uno dei tag premium
            if any(tag in full_lower or tag in name_lower for tag in PREMIUM_TAGS):
                continue

            filtered_voices.append(v)

        output_payload = {
            "provider": "azure",
            "fetched_at": data.get("fetched_at"),
            "total_voices": len(filtered_voices),
            "voices": filtered_voices
        }

        with open(filtered_file, "w", encoding="utf-8") as f:
            json.dump(output_payload, f, indent=4, ensure_ascii=False)

        print(f"OK - Salvate {len(filtered_voices)} voci gratuite in voices_azure.json")

    except FileNotFoundError:
        print("File completo non trovato. Devi prima scaricare le voci complete.")
    except Exception as e:
        print("Errore durante il filtraggio:", e)
        
        
        
if __name__ == "__main__":
    download_complete_json()
    filter_free_voices()  # crea voices_azure.json con le voci gratuite