# =========================================================
# tts_config_manager.py
# =========================================================

from pathlib import Path
import os
import json
from colorama import Fore, Style

from core.file_selector import select_file_menu
from core.credentials_manager import get_active_providers
from menu_voices import load_voices, voice_menu
from menu_lingue_tts import seleziona_lingua_tts

# =========================================================
# PATH
# =========================================================
BASE_DIR = Path(__file__).resolve().parent.parent
SRT_DIR = BASE_DIR / "Translated"

# =========================================================
# STATO CONFIG
# =========================================================
config_status = {
    "file_srt": None,
    "language_code": None,
    "tts_language_code": None,
    "language_source": None,
    "provider": None,
    "display_name": None,
    "api_tag": None,
    "output_format": "mp3"
}

# =========================================================
# FUNZIONI CONFIG
# =========================================================

def aggiorna_file_srt(messages):
    file_selezionato = select_file_menu(
        messages,
        base_folder=SRT_DIR,
        file_types=[("SRT files","*.srt")]
    )
    if file_selezionato:
        # Selezionato nuovo file SRT
        config_status["file_srt"] = file_selezionato
        
        # reset delle altre impostazioni tranne output_format
        for key in ["language_code", "tts_language_code", "language_source", "provider", "display_name", "api_tag"]:
            config_status[key] = None
        
        # Aggiorna lingua basandosi sul nuovo file SRT
        aggiorna_lingua(messages)


# =========================================================
# aggiorna_lingua (aggiornata)
# =========================================================
def aggiorna_lingua(messages):
    import json, os

    json_file = os.path.join(os.path.dirname(config_status["file_srt"]), "project_info.json")
    lingua = None

    if os.path.exists(json_file):
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            traduzioni = data.setdefault("traduzioni", {})
            lingua = traduzioni.get("target_lang")
            if lingua:
                config_status["language_code"] = lingua
                config_status["language_source"] = "auto"
                return
        except Exception:
            pass

    # fallback: richiesta manuale tramite menu
    print(f"\n{Fore.YELLOW}{messages.DUBBING_WarningNoProjectInfo}{Style.RESET_ALL}\n")
    selected_lang = seleziona_lingua_tts(messages)  
    if selected_lang:
        config_status["language_code"] = selected_lang
        config_status["language_source"] = "manual"



def aggiorna_motore_tts(messages):
    # Prende solo i provider con credenziali valide
    active_providers = get_active_providers()

    if not active_providers:
        print(Fore.YELLOW + "[WARNING] Nessun provider TTS attivo." + Style.RESET_ALL)
        input(messages.DUBBING_PromptContinue)
        return

    while True:
        print("\n" + messages.DUBBING_SelectEngine + ":")
        for idx, p in enumerate(active_providers, start=1):
            print(f"{idx}. {p.capitalize()}")
        print(f"0. {messages.DUBBING_Annulla}")

        scelta = input(messages.DUBBING_PromptSelect).strip().lower()

        if scelta == "0":
            return

        # Gestione input numerico o testuale
        if scelta.isdigit():
            idx = int(scelta) - 1
            if 0 <= idx < len(active_providers):
                nuovo = active_providers[idx]
            else:
                print(messages.DUBBING_InvalidSelection)
                continue
        elif scelta in [p.lower() for p in active_providers]:
            nuovo = scelta
        else:
            print(messages.DUBBING_InvalidSelection)
            continue

        if config_status.get("provider") != nuovo:
            config_status["display_name"] = None
            config_status["api_tag"] = None

        config_status["provider"] = nuovo
        return


def aggiorna_voce(messages):
    if not config_status.get("file_srt") or not config_status.get("language_code"):
        print(messages.DUBBING_SelectLanguageFirst)
        return

    voices = load_voices()
    if not voices:
        print(messages.DUBBING_NoVoicesAvailable)
        return

    selected = voice_menu(
        voices=voices,
        language=config_status["language_code"],
        provider=config_status.get("provider")
    )

    if selected:
        config_status["display_name"] = selected["display_name"]
        config_status["api_tag"] = selected["api_tag"]
        #config_status["language_code"] = selected["language_code"]
        config_status["provider"] = selected["provider"].lower()
        config_status["tts_language_code"] = selected.get("language_code", config_status["language_code"])


def aggiorna_formato_output(messages):
    opzioni = ["mp3", "wav"]

    scelta = input(messages.DUBBING_SelectFormat).strip()
    if scelta in ["1", "2"]:
        config_status["output_format"] = opzioni[int(scelta)-1]