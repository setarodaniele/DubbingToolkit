# Architecture and Technical Reference

This document describes the internal structure of the project, the main modules, development conventions, and component status. It is intended primarily for contributors or anyone who wants to understand the internal workings of the system.

---

## Folder Structure

The root structure contains system modules; project data is isolated in the Workspace model:

```
DubbingToolkit/
├── Billing/                TTS usage and cost monitoring
├── core/                   Shared Python support modules
├── credentials/            API credentials (excluded from Git)
├── Installation/           Local Python runtimes (3.10, 3.11)
├── installer/              Build and packaging system
├── locale/                 Localization and language management
│   ├── Active/             Active language JSON files (it, en, es, de, fr, pt, ru, zh)
│   └── System/             Language metadata (Whisper, supported languages)
├── Logs/                   Operational logs
├── ps/                     PowerShell modules (logging, messaging)
├── Repository/             Shared resources and local models
├── Scripts/                Operational scripts and Python modules
│   └── maintenance/        Maintenance scripts and localization pipeline
├── Settings/               Active and reference configuration
├── Temp/                   Temporary files
├── Tools/                  External binaries (ffmpeg)
├── venv/                   Main Python virtual environment
├── voices/                 Available TTS voices and audio samples
└── Workspace/              Project data (created automatically)
    └── projects/
        └── {project_name}/
            ├── project_info.json                    Project metadata and audio tracks
            ├── audio_extraction/
            │   ├── current/                         Current audio tracks (track_01.wav, etc.)
            │   └── archive/                         Archive of previous extractions
            ├── transcripts/
            │   ├── current/                         Current SRT transcriptions
            │   └── archive/                         Archive of previous transcriptions
            ├── translated/
            │   ├── current/                         Current SRT translations
            │   └── archive/                         Archive of previous translations
            ├── dubbed/
            │   ├── current/                         Current TTS audio
            │   └── archive/                         Archive of previous TTS output
            ├── video_input/                         Source videos (never modified)
            └── audio_input/                         Direct audio input (optional)
```

---

## Startup Chain

```
StartDubbing.bat
  └→ Scripts/Launcher.ps1
       Activates venv, UTF-8 setup, logging, language loading
         └→ Scripts/Regista.py
              Main menu and pipeline orchestration
```

The Launcher handles: local Python runtime selection (`Installation/`), venv creation/activation, log system setup, interface language loading.

`Regista.py` is the central coordinator: it presents the menu to the user and delegates execution to the specific modules for each stage.

---

## Operational Pipeline

| Stage | Module | Input → Output |
|---|---|---|
| 1 — Audio extraction | `Scripts/estrai_tracce.py` | `video_input/` → `audio_extraction/current/` (track_01.wav, etc.) |
| 2 — Transcription | `Scripts/trascrivi_audio.py` | `audio_extraction/current/` or `audio_input/` → `transcripts/current/` (SRT) |
| 3 — Translation | `Scripts/traduci_testo.py` | `transcripts/current/` → `translated/current/` (SRT) |
| 4 — TTS | `Scripts/tts_menu.py` | `translated/current/` → `dubbed/current/` (MP3/WAV) |

All paths are relative to `Workspace/projects/{project_name}/`. `tts_menu.py` delegates to `tts_azure.py` or `tts_google.py` based on the active provider.

Files processed at each stage are automatically archived in `archive/` subdirectories to preserve history.

---

## Core Modules (`core/`)

These modules are shared across the entire pipeline. They should not be called directly by the user.

### `messages.py`
Centralized localized messaging system. Reads `Settings/settings.json` → `interface_lang` field → loads `locale/Active/<lang>.json`.

Usage in scripts:
```python
from core.messages import Messages
msg = Messages()
print(msg._("message_key"))
```

Missing keys produce the fallback `[MISSING: key]` and do not cause crashes. All missing keys must be corrected before release.

### `credentials_manager.py`
Centralized loading and validation of API credentials. It is the only point in the project authorized to read files in `credentials/`. No other module should access those files directly.

### `api_check.py`
Verifies credential validity before allowing access to the TTS menu. It is invoked automatically when entering the TTS menu.

### `ui_printer.py` + `ui_colors.py`
Functions for console output with formatting and colors. All scripts must use these modules instead of direct `print()` calls, to ensure visual consistency.

### `utils_tts.py`
Shared utilities for SRT parsing, used by both TTS backends.

### `file_selector.py`
Interface for file selection via interactive menu.

### `input_parsing.py`
Parsing and validation of user inputs.

---

## Main Scripts Modules

### `Regista.py`
Main orchestrator. Manages the top-level menu and coordinates execution of pipeline stages. Python entry point of the application.

### `estrai_tracce.py`
Extracts audio tracks from videos via ffmpeg. Saves audio files to `audio_extraction/current/` with names `track_01.wav`, `track_02.wav`, etc. Automatically generates metadata files (`track_XX_metadata.json`) and archives previous extractions in `audio_extraction/archive/`.

### `trascrivi_audio.py`
Audio transcription via Whisper (or WhisperX, when integrated). Output in SRT format in `transcripts/current/`. Previous files are archived in `transcripts/archive/`.

### `traduci_testo.py`
SRT translation via Helsinki-NLP MarianMT models running locally. Output in `translated/current/`. Previous files are archived in `translated/archive/`.

### `tts_dubbing.py` / `tts_menu.py`
TTS pipeline coordination. `tts_menu.py` is the user interface; `tts_dubbing.py` manages the segment generation and merging flow.

### `tts_azure.py` / `tts_google.py`
Provider-specific TTS backends. Generate audio segments and save them to `dubbed/current/`. Previous files are archived in `dubbed/archive/`.

### `tts_merge.py`
Merging and synchronization of TTS audio segments into the final file.

### `tts_config_manager.py`
TTS configuration management: active provider, selected voice, synthesis parameters.

### `info_manager.py`
Reading and writing the `project_info.json` file at the project root. Centralizes project metadata, list of extracted audio tracks (`audio_tracce[]`), pipeline state, and processing history. Ensures state traceability between stages.

### `settings_manager.py`
Reading, validation, and access to configurations in `Settings/settings.json`.

### `monitoraggio_consumo.py`
Thread-safe access to the TTS usage log in `Billing/consumo_tts.json`.

### `menu_lingue.py` / `menu_lingue_tts.py`
Language selection for transcription/translation and for the TTS pipeline.

### `menu_voices.py`
TTS voice selection and configuration from the interface.

### `backup_utils.py`
Backup management and history of generated files.

---

## Localization System

### Structure

```
locale/
├── Active/              Active language files (runtime)
│   ├── it.json
│   ├── en.json
│   ├── es.json
│   ├── de.json
│   ├── fr.json
│   ├── pt.json
│   ├── ru.json
│   └── zh.json
└── System/
    ├── languages.json           Conceptually supported languages
    └── whisper_languages.json   Languages supported by Whisper
```

### Rules

- All Python interface messages must use `core/messages.py`.
- All files in `locale/Active/` must be synchronized: a key present in `it.json` must exist in all other language files.
- Missing keys produce `[MISSING: key]` at runtime — not acceptable in a stable environment.
- PowerShell uses `ps/Messages.psm1` (equivalent system, separate).

### Localization Maintenance Pipeline

A complete pipeline for managing language files is available in `Scripts/maintenance/translation/`:

| Script | Function |
|---|---|
| `LocaleKeyAnalyzer.ps1` | Analyzes missing keys and inconsistencies between files |
| `LocaleTranslator.ps1` | Automatic translation with placeholder protection |
| `Validate-LocaleJson.ps1` | Validates JSON structure and integrity |
| `Fix-LocaleDuplicates.ps1` | Fixes duplicate keys |
| `Clean-LocaleUnusedKeys.ps1` | Removes unused keys |
| `Extract-Placeholders.ps1` | Extracts and maps placeholders |
| `Protect-Placeholders.ps1` | Protects placeholders during automatic translation |

---

## Configuration (`Settings/settings.json`)

Main fields:

```json
{
  "interface_lang": "it",
  "model": "small",
  "Transcript_Audio_Spoken_Lang": "it",
  "Translation_Target_Lang": "en",
  "Dubbing_Lang": "en"
}
```

| Field | Description |
|---|---|
| `interface_lang` | User interface language |
| `model` | Whisper model to use (`tiny`, `base`, `small`, `medium`, `large`) |
| `Transcript_Audio_Spoken_Lang` | Language spoken in the source audio |
| `Translation_Target_Lang` | Target language for translation |
| `Dubbing_Lang` | Language for TTS synthesis |

---

## TTS Voice Management

Available voices are catalogued in `voices/`:

| File | Contents |
|---|---|
| `voices_azure.json` | Filtered Azure voices ready for use |
| `voices_azure_complete.json` | Full Azure catalogue |
| `voices_google.json` | Filtered Google voices |
| `voices_google_complete.json` | Full Google catalogue |
| `voices_index.json` | Unified index of all voices (Azure + Google) with metadata |

Voice audio samples (for listening) are in `voices/voices_output/<provider>/<LANG-CODE>/<voice>.mp3`, if generated via `Scripts/VoicesRepository.py`.

To update the voice catalogue from providers:
```bash
voices/fetch_azure_voices.py
voices/fetch_google_voices.py
```

---

## Build and Distribution System

The project includes a packaging system in `installer/`:

```powershell
installer/build.ps1
```

Include/exclude rules are in:

| File | Purpose |
|---|---|
| `build_include.json` | What to copy, where, and in what mode |
| `build_exclude.json` | Global blacklist (all modes) |
| `build_exclude_test.json` | Additional blacklist only in TEST mode (Python runtime, ffmpeg, voices) |
| `build_protected.json` | Paths copied verbatim — exclusion rules are ignored |
| `build_empty_dirs.json` | Empty folders to create in the package |

Available parameters:
```powershell
.\build.ps1              # interactive menu (choice 1/2/3)
.\build.ps1 -Test        # lightweight build without heavy components
.\build.ps1 -Production  # full build with confirmation
.\build.ps1 -DryRun      # simulation without writing files
```

Output goes to `installer/build_payload/`. Real credential files are never included in the build — only `*.template.json` files are shipped.

---

## Development Conventions

### Naming

| Element | Convention |
|---|---|
| Folders (new) | `lowercase_underscore` |
| Python modules | `lowercase_underscore.py` |
| Classes | `CamelCase` |
| Functions and variables | `lowercase_underscore` |
| Test scripts | `test_` prefix required |

### Script Structure

All scripts must follow the numbered structure defined in Section 6 of `RecapDubbing.txt`:

```
# 1. IMPORTS / DEPENDENCIES
# 2. CONFIGURATION – Paths, settings, constants
# 3. UTILITIES – Helper functions
# 4. CORE LOGIC – Main processing
# 5. MAIN EXECUTION – Entry point
```

Every script must include a standard header with name, description, input, output, and operational notes. Code comments must be in English.

### Messaging

- No hardcoded strings in runtime modules.
- All messages come from localization JSON files via `core/messages.py` (Python) or `ps/Messages.psm1` (PowerShell).
- Exception: bootstrap scripts and maintenance scripts may use non-localized output.

### Paths

All paths must be relative to the project root. No absolute paths in runtime modules.

### Generated Files

Each pipeline stage generates files in the `current/` subdirectory of the relevant stage (e.g., `audio_extraction/current/`, `transcripts/current/`, etc.). When a new run starts in the same stage, previous files in `current/` are automatically archived in `archive/` with timestamps, preserving history.

Some stages generate metadata files (e.g., `track_XX_metadata.json`, `_info.txt`) to track processing properties.

---

## Component Status

| Component | Status |
|---|---|
| Audio extraction | ✅ Operational |
| Whisper transcription | ✅ Operational |
| Helsinki-NLP translation | ✅ Operational |
| Azure TTS | ✅ Operational |
| Google TTS | ✅ Operational |
| Multilingual interface (8 languages) | ✅ Operational |
| TTS usage monitoring | ✅ Operational |
| Build/packaging system | ✅ Operational |
| Subtitles (menu option 5) | ⚠️ Stub — not implemented |
| Advanced segmentation | ⚠️ Placeholder — not in pipeline |
| WhisperX | ⚠️ Venv prepared, not integrated |
| OpenAI / ElevenLabs TTS | ⚠️ Credentials present, not connected to menu |
| Pivot translation (intermediate language) | 🔲 Planned |
| Text post-processing (Translation→TTS) | 🔲 Planned |
| Project-based model (Workspace with per-project folder) | ✅ Operational |
