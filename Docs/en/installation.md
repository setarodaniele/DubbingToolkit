# Installation and Configuration

This guide covers system requirements, credential structure, and the initial setup process for DubbingToolkit.

---

## System Requirements

- **Operating system:** Windows with PowerShell 5.1
- **Python:** included in the project — no system-level installation required
  - Python 3.11 is currently used, located in the `Installation/` folder and managed internally.
- **ffmpeg:** included in `Tools/ffmpeg-7.1.1-full_build/` — no separate installation required
- **Internet connection:** required for modules that access external resources, including TTS APIs (Azure, Google) and translation model downloads on first run.

---

## TTS Credentials

Credentials for TTS providers must be placed in the `credentials/` folder. The currently supported providers are Azure and Google, each with its own JSON file.

| File | Provider |
|---|---|
| `azure_speech_credentials.json` | Azure Cognitive Services Speech |
| `google_speech_credentials.json` | Google Cloud TTS |

A template file with the required structure is available for each provider:

```
credentials/azure_speech_credentials.template.json
credentials/google_speech_credentials.template.json
```

Copy the template file, remove the `.template` extension, and fill in your credentials in the resulting file.

---

## Virtual Environment and Python Dependencies

When the project starts, the Launcher automatically handles virtual environment creation and activation, and dependency installation. No manual intervention is required under normal conditions.

The main dependencies are listed in `Scripts/requirements.txt`.

### Resetting the Virtual Environment

**Reset from within the project** (the project must be able to start):

Select the reset option from the interface, or run directly:
```powershell
Scripts/reset_env.ps1
```
This script recreates the venv and reinstalls dependencies automatically.

**Full manual reset** (when the project will not start):

Manually delete the `venv/` folder. On the next launch via `StartDubbing.bat`, the Launcher will detect the missing venv and recreate it automatically.

---

## Initial Configuration

The project's operational settings are in `Settings/`:

| File | Purpose |
|---|---|
| `settings.json` | Active configuration |
| `settings_default.json` | Reference configuration (do not modify) |
| `reset.json` | Reset parameters |

### Main Parameters in `settings.json`

- **`interface_lang`** — interface language (e.g. `"it"`, `"en"`, `"es"`)
- TTS provider settings (active provider, selected voice, target language)
- Whisper transcription parameters (model, language)

> **Note:** settings are currently not persistent between sessions. On startup the interface language is requested; all other settings reset to default values. Settings persistence is planned as a future improvement.

---

## Startup and Automatic Initialization

The user launches the project via:

```
StartDubbing.bat
```

The Launcher then automatically performs the following steps, without user intervention:

1. Verification and activation of the local Python runtime
2. Creation or activation of the virtual environment
3. API credentials check
4. Launch of the main interface

If credentials are missing or invalid, the system reports this in the menu before granting access to TTS functions.
Other functions — audio extraction, transcription, and translation — do not depend on credentials and remain accessible.

---

## Moving the Project and Uninstalling

Although not recommended, the project can be moved to a different location on disk or to another machine, but after every move the virtual environment must be recreated, as the venv contains absolute paths tied to the original location. Procedure:

1. Delete the `venv/` folder
2. Launch `StartDubbing.bat` — the Launcher will recreate the venv and reinstall dependencies

If the project was installed via the distribution package, after a move the entry in Windows **Apps & Features** will no longer be valid. You do not need to use it: to uninstall the project simply delete the entire folder. No files are written outside of it.
