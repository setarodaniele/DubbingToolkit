# =========================================================
# Scripts/BootstrapSettings.py
# =========================================================
# Description:
#   Runs at every launch (called by Launcher.ps1 before venv setup).
#   Uses Installation/Python311 — NOT the venv — so it must rely
#   only on the stdlib.
#
#   Steps:
#     1. Create settings_persistent.json from settings_persistent_default.json
#        if it does not exist yet (first run or hard reset).
#     2. If new_lang is provided (language selected in Launcher or by installer),
#        write it to settings_persistent.json.
#     3. Rebuild settings.json via merge:
#        settings_default.json + settings_persistent.json → settings.json
#        The three audio-language fields are derived from interface_lang.
#
# Usage (called by Launcher.ps1):
#   python BootstrapSettings.py <settings_path> <default_path>
#                               <persistent_path> <persistent_default_path>
#                               [new_lang]
#
# =========================================================
# LANGUAGE LIFECYCLE
# =========================================================
# The interface language flows through the system in this order:
#
#   1. INSTALLER (InnoSetup) — optional path:
#      Writes settings_persistent.json with:
#        { "language_preset_from_installer": true, "interface_lang": "XX" }
#      Launcher.ps1 detects this flag and skips the interactive menu.
#
#   2. LAUNCHER (interactive path, no installer):
#      Shows language selection menu.
#      Passes selected lang as [new_lang] argument to this script.
#
#   3. BOOTSTRAP (this script):
#      Writes interface_lang to settings_persistent.json.
#      Rebuilds settings.json via merge — the three audio-language fields
#      (Transcript_Audio_Spoken_Lang, Transcript_Target_Lang,
#      Translation_Source_Lang) are derived from interface_lang here.
#
#   4. RUNTIME (settings_manager.py, menu 8→3):
#      User can change interface_lang at any time.
#      Change is written to settings_persistent.json + settings.json rebuilt.
#
#   5. SOFT RESET (menu 8→2):
#      settings_persistent.json restored from settings_persistent_default.json.
#      settings.json rebuilt from merged defaults.
#      interface_lang reverts to the factory default ("it").
#
#   6. HARD RESET (menu 8→9):
#      Same as soft reset + venv/ is deleted and rebuilt on next launch.
#
# =========================================================
# Language rule:
#   All comments must be written in English.
# =========================================================

import json
import os
import shutil
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Inline atomic write — cannot import core/ here (venv not yet active)
# ---------------------------------------------------------------------------

def _load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8-sig") as f:
        return json.load(f)


def _write_atomic(path: Path, data: dict) -> None:
    tmp = path.with_suffix(".tmp")
    with tmp.open("w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    os.replace(tmp, path)


# ---------------------------------------------------------------------------
# Fields that live in settings_persistent and override defaults at merge
# ---------------------------------------------------------------------------

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

LANG_DERIVED_FIELDS = (
    "Transcript_Audio_Spoken_Lang",
    "Transcript_Target_Lang",
    "Translation_Source_Lang",
)


# ---------------------------------------------------------------------------
# Migration
# ---------------------------------------------------------------------------

def _migrate_persistent(data: dict, from_version: int, to_version: int) -> dict:
    """Apply sequential migrations to bring settings_persistent up to to_version.

    Each migration block handles one version step (from_version → from_version+1).
    Add a new block here whenever CURRENT_SCHEMA_VERSION is incremented.
    Always ends by setting schema_version to the target version.
    """
    if from_version < 1:
        # v0 → v1: first versioned release — remove obsolete keys if present,
        # ensure all current persistent fields exist with sensible defaults.
        for dead_key in ("output_transcripts", "output_dubbed",
                         "archive_wav_max_count", "archive_wav_max_size_mb"):
            data.pop(dead_key, None)
        data.setdefault("max_backups", 10)
        data.setdefault("max_backups_per_language", 10)
        data.setdefault("max_folders_size_gb", 5)
        data.setdefault("use_trash", False)
        data.setdefault("show_confirmations", True)

    # Always ensure schema_version is the first key in the file
    version = to_version
    data.pop("schema_version", None)
    data = {"schema_version": version, **data}

    return data


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) < 5:
        print("[BootstrapSettings] ERROR: insufficient arguments.", file=sys.stderr)
        print("Usage: BootstrapSettings.py <settings> <default> <persistent> <persistent_default> [new_lang]",
              file=sys.stderr)
        sys.exit(1)

    settings_path          = Path(sys.argv[1])
    default_path           = Path(sys.argv[2])
    persistent_path        = Path(sys.argv[3])
    persistent_default_path = Path(sys.argv[4])
    new_lang               = sys.argv[5] if len(sys.argv) > 5 else None

    # Current schema version — increment here when settings_persistent structure changes
    CURRENT_SCHEMA_VERSION = 1

    # 1. Create persistent from persistent_default if missing
    if not persistent_path.exists():
        shutil.copyfile(persistent_default_path, persistent_path)

    # 1b. Migrate settings_persistent.json if its schema_version is outdated
    if persistent_path.exists():
        try:
            persistent = _load_json(persistent_path)
            file_version = persistent.get("schema_version", 0)
            if file_version < CURRENT_SCHEMA_VERSION:
                persistent = _migrate_persistent(persistent, file_version, CURRENT_SCHEMA_VERSION)
                _write_atomic(persistent_path, persistent)
        except Exception:
            pass  # Corrupt file — will be handled in step 3

    # 2. Apply new_lang if provided (Launcher or installer language selection)
    if new_lang:
        persistent = _load_json(persistent_path)
        persistent["interface_lang"] = new_lang
        _write_atomic(persistent_path, persistent)

    # 3. Rebuild settings.json via merge
    try:
        merged = _load_json(default_path)
    except Exception as exc:
        print(f"[BootstrapSettings] FATAL: cannot read settings_default.json: {exc}", file=sys.stderr)
        sys.exit(1)

    if persistent_path.exists():
        try:
            persistent = _load_json(persistent_path)
            for key in PERSISTENT_FIELDS:
                if key in persistent:
                    merged[key] = persistent[key]
        except Exception:
            # Corrupt persistent — fall back to pure defaults silently.
            # Do not recreate here: the next launch will create it from _default.
            pass

    # Derive session-level language fields from interface_lang
    lang = merged.get("interface_lang", "it")
    for field in LANG_DERIVED_FIELDS:
        merged[field] = lang

    # Unidirectional sync: Translation_Target_Lang → Dubbing_Lang
    if "Translation_Target_Lang" in merged:
        merged["Dubbing_Lang"] = merged["Translation_Target_Lang"]

    _write_atomic(settings_path, merged)


if __name__ == "__main__":
    main()
