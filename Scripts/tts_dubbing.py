# =========================================================
# 0.0 tts_dubbing.py (INTEGRAZIONE MENU CONFIG - VARIABILI UNIFICATE)
# =========================================================

from pathlib import Path
from core import utils_tts
from monitoraggio_consumo import ConsumoTTS
from tts_merge import merge_audio_files
import datetime
import json
import os
import sys

root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_path not in sys.path:
    sys.path.insert(0, root_path)

from core.workspace_manager import WorkspaceManager
from core.utils_settings import write_json_atomic
from core.archive_pruner import prune_with_confirmation
from info_manager import InfoManager
    
    
def tts_dubbing(config, settings=None, messages=None):
    file_input = config["file_srt"]
    selected_engine = config["provider"]
    voice_name = config["api_tag"]
    output_format = config["output_format"]
    language_code = config.get("language_code")
    track_id = config.get("track_id") or "track_01"
    _settings = settings or {}

    ws = WorkspaceManager.get_active()
    ws.rotate_to_archive("dubbed", track_id)
    if messages is not None:
        prune_with_confirmation(
            ws, "dubbed", track_id, messages,
            show_confirmations=_settings.get("show_confirmations", True),
            high_risk=True,
            use_trash=_settings.get("use_trash", False),
            max_count=_settings.get("max_backups", 10),
            max_size_mb=_settings.get("max_folders_size_gb", 5) * 1024,
        )
    else:
        ws.prune_archives("dubbed", track_id,
                          max_count=_settings.get("max_backups", 10),
                          max_size_mb=_settings.get("max_folders_size_gb", 5) * 1024)
    output_dir = ws.stage_current("dubbed", track_id)
    output_dir.mkdir(parents=True, exist_ok=True)

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

    # Write per-track metadata
    _created_at = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    write_json_atomic(output_dir / "metadata.json", {
        "schema_version":  1,
        "track_id":        track_id,
        "created_at":      _created_at,
        "source_srt":      Path(file_input).name,
        "provider":        selected_engine,
        "voice":           voice_name,
        "language_code":   language_code,
        "output_format":   output_format,
        "merged_file":     merged_path.name,
        "characters_used": totale_caratteri,
    })

    try:
        InfoManager(ws.root).update_tts(track_id, {
            "created_at":      _created_at,
            "provider":        selected_engine,
            "voice":           voice_name,
            "language_code":   language_code,
            "output_format":   output_format,
            "characters_used": totale_caratteri,
        })
    except Exception:
        pass

    return merged_path