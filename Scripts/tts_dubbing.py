# =========================================================
# 0.0 tts_dubbing.py (INTEGRAZIONE MENU CONFIG - VARIABILI UNIFICATE)
# =========================================================

from pathlib import Path
from core import utils_tts
from monitoraggio_consumo import ConsumoTTS
from tts_merge import merge_audio_files
import datetime
from Scripts import backup_utils
import json
import os
import sys

root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_path not in sys.path:
    sys.path.insert(0, root_path)
from core.messages import Messages
messages = Messages()  # istanza locale

BASE_DIR = Path(__file__).resolve().parent.parent
TTS_OUTPUT_DIR = BASE_DIR / "Dubbed"


# =========================
# Leggi settings correnti dal JSON
# =========================
import settings_manager
settings_file = Path.cwd() / "Settings" / "settings.json"
with settings_file.open("r", encoding="utf-8-sig") as f:
    settings = json.load(f)
    
    
def tts_dubbing(config):
    file_input = config["file_srt"]
    selected_engine = config["provider"]
    voice_name = config["api_tag"]
    output_format = config["output_format"]
    language_code = config.get("language_code")

    # Crea cartella unica per questo run: timestamp + nome file
    base_name = file_input.stem
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = TTS_OUTPUT_DIR / selected_engine.upper() / f"{timestamp}_{base_name}"
    utils_tts.assicurati_cartella(output_dir)

    # Lazy import e chiamata al provider corretto
    if selected_engine.lower() == "google":
        from tts_google import sintetizza_google_batch
        sintetizza_google_batch(
            file_input=file_input,
            output_dir=output_dir,
            voice_name=voice_name,
            output_format=output_format,
            language_code=config.get("tts_language_code", language_code)
        )
    elif selected_engine.lower() == "azure":
        from tts_azure import sintetizza_azure_batch
        sintetizza_azure_batch(
            file_input=file_input,
            output_dir=output_dir,
            voice_name=voice_name,
            output_format=output_format
        )
    else:
        return "[ERROR] Provider non valido o assente"

    # Aggiornamento consumo
    totale_caratteri = utils_tts.count_characters(file_input)
    consumo = ConsumoTTS(motore=selected_engine)
    consumo.aggiungi_caratteri(totale_caratteri)

    # Merge audio
    merged_path = output_dir / f"merged.{output_format}"
    merge_audio_files(output_dir, merged_path, output_format)

    # Backup / gestione storico
    backup_utils.manage_history(output_dir.parent, settings, messages)

    return merged_path