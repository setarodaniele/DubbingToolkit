# =========================================================
# core/utils_settings.py
# =========================================================
# Description:
#   Centralised utilities for reading and writing settings files.
#   All JSON writes use an atomic pattern (write .tmp then rename)
#   to prevent corruption on crash or forced termination.
#
#   Public API:
#     load_json(path)
#     write_json_atomic(path, data)
#     merge_and_rebuild(default_path, persistent_path, settings_path)
#
# Language rule:
#   All comments must be written in English.
# =========================================================

import json
import os
from pathlib import Path

# Fields in settings_persistent that are propagated to settings.json.
# All other fields come from settings_default.json.
PERSISTENT_FIELDS = {
    "language_preset_from_installer",
    "interface_lang",
    "model",
    "voice",
    "show_confirmations",
    "max_backups",
    "max_backups_per_language",
    "max_folders_size_gb",
    "use_trash",
    "MIN_SILENCE_LEN_MS",
    "SILENCE_THRESH_DBFS",
    "KEEP_SILENCE_MS",
    "Translation_Target_Lang",
    "Dubbing_Lang",
}

# These three fields are derived from interface_lang at rebuild time.
# They are session-level: overridable at runtime but not persisted.
LANG_DERIVED_FIELDS = (
    "Transcript_Audio_Spoken_Lang",
    "Transcript_Target_Lang",
    "Translation_Source_Lang",
)


def load_json(path: Path) -> dict:
    with Path(path).open("r", encoding="utf-8-sig") as f:
        return json.load(f)


def write_json_atomic(path: Path, data: dict) -> None:
    path = Path(path)
    tmp = path.with_suffix(".tmp")
    with tmp.open("w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    os.replace(tmp, path)


def merge_and_rebuild(
    default_path: Path,
    persistent_path: Path,
    settings_path: Path,
) -> dict:
    """
    Build settings.json from defaults + persistent overlay.

    Merge strategy:
      1. Start from settings_default.json (all fields, app defaults).
      2. Override with every PERSISTENT_FIELDS key found in settings_persistent.json.
         If settings_persistent.json is missing or corrupt, pure defaults are used
         and the file is not recreated here (BootstrapSettings.py handles creation).
      3. Derive the three audio-language fields from interface_lang
         (session-level only — not stored in persistent, reset at every startup).
      4. Enforce unidirectional sync: Translation_Target_Lang → Dubbing_Lang.

    Returns the merged dict (also written atomically to settings_path).
    Raises RuntimeError only if settings_default.json itself is unreadable.
    """
    # Step 1: load defaults — if this fails the app cannot start at all
    try:
        merged = load_json(default_path)
    except Exception as exc:
        raise RuntimeError(f"Cannot read settings_default.json ({default_path}): {exc}") from exc

    # Step 2: overlay persistent — silently fall back to pure defaults on any error
    if Path(persistent_path).exists():
        try:
            persistent = load_json(persistent_path)
            for key in PERSISTENT_FIELDS:
                if key in persistent:
                    merged[key] = persistent[key]
        except Exception:
            # Corrupt or unreadable persistent — continue with defaults only.
            # The file will be recreated by BootstrapSettings.py on the next run.
            pass

    # Step 3: derive session-level language fields from interface_lang
    lang = merged.get("interface_lang", "it")
    for field in LANG_DERIVED_FIELDS:
        merged[field] = lang

    # Step 4: enforce unidirectional sync Translation_Target_Lang → Dubbing_Lang
    if "Translation_Target_Lang" in merged:
        merged["Dubbing_Lang"] = merged["Translation_Target_Lang"]

    write_json_atomic(settings_path, merged)
    return merged
