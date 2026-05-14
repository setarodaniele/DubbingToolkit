# =========================================================
# menu_voices.py (fix Messages + uniformità con traduci_testo)
# =========================================================

import sys
import subprocess
from pathlib import Path
import os
import json
import msvcrt
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(BASE_DIR))
from core.messages import Messages

# =========================================================
# 0. Setup base e settings
# =========================================================
SETTINGS_FILE = BASE_DIR / "Settings" / "settings.json"
messages = Messages(settings_file=SETTINGS_FILE)

# =========================================================
# 1. Configurazioni e percorsi (RELATIVI)
# =========================================================
VOICE_INDEX_FILE = BASE_DIR / "voices" / "voices_index.json"
CONSUMO_FILE = BASE_DIR / "Billing" / "consumo_tts.json"
COST_FILE = BASE_DIR / "Billing" / "tts_voices_cost.json"

VIEWPORT_SIZE = 51

FFPLAY = Path(BASE_DIR) / "Tools" / "ffmpeg-7.1.1-full_build" / "bin" / "ffplay.exe"

# =========================================================
# 2. Caricamento JSON delle voci
# =========================================================
def load_voices():
    if not VOICE_INDEX_FILE.exists():
        print(messages.menu_voices_errors_file_not_found.format(value=str(VOICE_INDEX_FILE)))
        return []
    with open(VOICE_INDEX_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

# =========================================================
# 2.1 Billing helpers
# =========================================================
def get_current_month():
    return datetime.now().strftime("%Y-%m")

def load_json_safe(path):
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def get_usage_summary():
    consumo = load_json_safe(CONSUMO_FILE)
    costs = load_json_safe(COST_FILE)
    month = get_current_month()

    azure_used = consumo.get("azure", {}).get(month, 0)
    azure_free = costs.get("azure", {}).get("neural", {}).get("franchigia_gratuita", 0)

    google_used = consumo.get("google", {}).get(month, 0)
    google_engines = costs.get("google", {})
    google_free = max([e.get("franchigia_gratuita", 0) for e in google_engines.values()], default=0)

    return {
        "azure": (azure_used, azure_free),
        "google": (google_used, google_free)
    }

# =========================================================
# 3. Filtraggio voci
# =========================================================
def filter_voices(voices, language=None, provider=None, gender=None):
    result = []
    for v in voices:
        if language and v["language"] != language:
            continue
        if provider and v["provider"] != provider:
            continue
        if gender and v["gender"].lower() != gender.lower():
            continue
        result.append(v)
    return result

# =========================================================
# 3.1 Allineamento voci equivalenti (corretto)
# =========================================================
def align_voices(voices):
    """
    Restituisce una lista di voci ordinata in modo che voci equivalenti
    (stesso display_name) di provider diversi siano consecutive.
    Mantiene tutte le voci, anche se hanno motori diversi.
    """
    from collections import defaultdict

    # Raggruppa le voci per display_name
    grouped = defaultdict(list)
    for v in voices:
        grouped[v["display_name"]].append(v)

    aligned = []
    for name in sorted(grouped.keys()):
        # Per ciascun display_name, prima Azure (in ordine di engine), poi Google
        azure_voices = [v for v in grouped[name] if v["provider"].lower() == "azure"]
        google_voices = [v for v in grouped[name] if v["provider"].lower() == "google"]

        # Ordina per engine all’interno dello stesso provider
        azure_voices.sort(key=lambda x: x["engine"])
        google_voices.sort(key=lambda x: x["engine"])

        # Aggiungi alla lista finale
        aligned.extend(azure_voices)
        aligned.extend(google_voices)
    
    return aligned
    

# =========================================================
# 4. Riproduzione voce
# =========================================================
def play_voice(voice):
    path = Path(voice["path"])
    if not path.exists():
        print(messages.menu_voices_errors_audio_file_missing.format(value=str(path)))
        return None
    try:
        return subprocess.Popen(
            [
                str(FFPLAY),
                "-nodisp",
                "-autoexit",
                "-loglevel", "quiet",
                str(path)
            ]
        )
    except Exception as e:
        print(messages.menu_voices_errors_audio_playback.format(value=str(e)))
        return None

# =========================================================
# 5. Lettura tasto Windows
# =========================================================
def get_key():
    key = msvcrt.getch()
    if key in b'\x00\xe0':
        key = msvcrt.getch()
    return key.decode("utf-8").lower()

# =========================================================
# 6. Header UI aggiornato con conteggio voci per provider
# =========================================================
def print_header(language, provider, gender, voices):
    """
    voices -> lista filtrata delle voci
    """
    total = len(voices)
    azure_count = sum(1 for v in voices if v["provider"].lower() == "azure")
    google_count = sum(1 for v in voices if v["provider"].lower() == "google")

    usage = get_usage_summary()
    az_used, az_free = usage["azure"]
    go_used, go_free = usage["google"]

    print("=" * 60)
    print(f"Selezione voci: {total} trovate per {language}")
    print(f"Voci Azure: {azure_count} | Voci Google: {google_count}")
    print(f"Provider: {provider or 'Tutti'} | Genere: {gender or 'Tutti'}")
    print(f"Azure usato: {az_used} / {az_free} gratis")
    print(f"Google usato: {go_used} / {go_free} gratis")
    print("=" * 60)
    
'''
def jump_to_index(messages, total):
    """
    Modalità dedicata per salto diretto.
    Usa input standard (bloccante) per inserire il numero.
    """
    try:
        value = input("\n" + getattr(messages, "menu_voices_jump_prompt") + " ").strip()
        if not value.isdigit():
            return None

        index = int(value) - 1
        if 0 <= index < total:
            return index
        return None
    except:
        return None
'''
 
# =========================================================
# 7. Menu interattivo
# ========================================================= 
def voice_menu(voices, language=None, provider=None, gender=None):
    # Ordina alfabeticamente tutte le voci prima di filtrare
    voices = sorted(voices, key=lambda v: v["display_name"].lower())

    filtered = filter_voices(voices, language, provider, gender)
    if not filtered:
        print(messages.menu_voices_no_voices)
        return None

    current_index = 0
    play_obj = None

    # calcola larghezza colonne dinamicamente
    name_width = max(len(v['display_name']) for v in filtered)
    provider_width = max(len(v['provider']) for v in filtered)
    gender_width = max(len(v['gender']) for v in filtered)
    engine_width = max(len(v['engine']) for v in filtered)

    while True:
        start = max(0, current_index - VIEWPORT_SIZE // 2)
        end = min(start + VIEWPORT_SIZE, len(filtered))
        start = max(0, end - VIEWPORT_SIZE)

        os.system("cls" if os.name == "nt" else "clear")
        print_header(language, provider, gender, filtered)

        for i in range(start, end):
            v = filtered[i]
            prefix = messages.menu_voices_cursor if i == current_index else "  "
            print(f"{prefix}{i+1:<3} | "
                  f"{v['display_name']:<{name_width}} | "
                  f"{v['provider']:<{provider_width}} | "
                  f"{v['gender']:<{gender_width}} | "
                  f"{v['engine']:<{engine_width}} |")

        print()
        print(messages.menu_voices_commands)
        print(messages.menu_voices_jump)

        if play_obj:
            play_obj.terminate()

        play_obj = play_voice(filtered[current_index])

        key = get_key()

        if key == "j":
            try:
                value = input("\n" + messages.menu_voices_jump_prompt + " ").strip()
                if value.isdigit():
                    jump_index = int(value) - 1
                    if 0 <= jump_index < len(filtered):
                        current_index = jump_index
            except:
                pass

        elif key == "n":
            if current_index < len(filtered) - 1:
                current_index += 1

        elif key == "b":
            if current_index > 0:
                current_index -= 1

        elif key == "s":
            return filtered[current_index]

        elif key == "f":
            # Mostra menu filtro provider
            print(messages.menu_voices_filter_header)
            print(f"1. {messages.menu_voices_filter_all}")
            print(f"2. {messages.menu_voices_filter_provider_azure}")
            print(f"3. {messages.menu_voices_filter_provider_google}")
            provider_choice = input(messages.menu_voices_filter_prompt_provider)

            if provider_choice == "1":
                provider = None
            elif provider_choice == "2":
                provider = "azure"
            elif provider_choice == "3":
                provider = "google"

            # Mostra menu filtro genere
            print(f"1. {messages.menu_voices_filter_all}")
            print(f"2. {messages.menu_voices_filter_gender_male}")
            print(f"3. {messages.menu_voices_filter_gender_female}")
            gender_choice = input(messages.menu_voices_filter_prompt_gender)

            if gender_choice == "1":
                gender = None
            elif gender_choice == "2":
                gender = "Male"
            elif gender_choice == "3":
                gender = "Female"

            # Rifiltra la lista
            filtered = filter_voices(voices, language, provider, gender)
            filtered = align_voices(filtered)  # allinea le voci equivalenti
            current_index = 0  # torna all'inizio della lista

        elif key == "q":
            return None

# =========================================================
# 8. Esecuzione standalone
# =========================================================
if __name__ == "__main__":
    all_voices = load_voices()
    # Ordina alfabeticamente per display_name prima di qualsiasi filtro
    all_voices.sort(key=lambda v: v["display_name"].lower())
    selected = voice_menu(all_voices, language="it")
    if selected:
        print(messages.menu_voices_selected)
        print(selected)