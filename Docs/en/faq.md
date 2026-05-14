# FAQ and Troubleshooting

---

## Startup and Environment

**The project does not start with `StartDubbing.bat`.**

A common cause is PowerShell script execution being blocked.
Open PowerShell as administrator and run:
```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```
Then try launching again.

---

**The venv appears corrupted or fails to activate.**

Manually delete the `venv/` folder inside the project folder. On the next launch via `StartDubbing.bat`, the Launcher will detect the missing venv and recreate it automatically.

---

**`[MISSING: key]` error in the interface.**

This indicates that a key is absent from the active localization file. It is not blocking but reduces interface clarity. Report the missing key so it can be corrected.

---

## Credentials and API

**The system reports invalid Azure credentials.**

Verify that `credentials/azure_speech_credentials.json` contains the `subscription` (API key) and `region` (e.g. `westeurope`) fields. Use `credentials/azure_speech_credentials.template.json` as a reference for the correct structure.

---

**The system reports invalid Google credentials.**

`credentials/google_speech_credentials.json` must be the complete JSON file for a GCP service account with the Cloud Text-to-Speech role enabled. Verify that the file is not truncated or malformed.

> Dedicated guides for creating Azure and Google credentials are available in the same folder as this documentation.

---

## Transcription

**Transcription produces inaccurate results or the wrong language.**

Manually specify the source language via the language menu before starting transcription. Available languages are listed in the language selection menu.

---

**Transcription is very slow.**

Speed depends on the Whisper model selected and the available hardware. The model is selected directly in the transcription menu before starting the process.

| Model | Speed | Quality |
|---|---|---|
| `tiny` | Very high | Basic |
| `base` | High | Fair |
| `small` | Medium | Good |
| `medium` | Low | High |
| `large` | Very low | Maximum |

On CPU without a dedicated GPU, even the `small` model can be slow on long files.

---

**Transcription stops with a memory error.**

Very long audio files loaded entirely into RAM can cause issues on systems with limited memory. Consider splitting the audio file into shorter segments before transcription.

---

## Translation

**The desired language pair is not available.**

Not all language pairs have a direct Helsinki-NLP model available. Supported pairs are listed in the language selection menu. Translation via pivot language (English as intermediate) is planned but not yet implemented.

---

**The translated text contains errors or sounds unnatural.**

Helsinki-NLP models are machine translation models and can produce inaccuracies, especially on idiomatic phrases or technical terms. Text post-processing is planned as a future improvement.

---

## TTS Synthesis

**TTS generates audio with unnatural pauses or rhythm.**

Check the voice selected in the TTS menu. Neural voices (Azure Neural, Google WaveNet) produce significantly better results than standard voices. You can listen to audio samples before starting synthesis.

---

**TTS output is silent or contains only noise.**

Open the translated SRT file in `Translated/` with a text editor and verify that it contains valid segments with non-empty text.

---

**Usage monitoring is not updating.**

Usage is recorded in `Billing/consumo_tts.json`. If the file appears locked or corrupted, make a backup of it, delete it, and it will be recreated automatically on next use.

---

## Files and Folders

**I cannot find the generated output.**

Each stage creates a subfolder with the format `<timestamp>_<filename>` in its output directory. Look in:
- `Audio_Extracted/` for extracted audio
- `Transcripts/` for SRT transcriptions
- `Translated/` for SRT translations
- `Dubbed/<PROVIDER>/` for the final dubbed audio

The `_info.txt` file in each subfolder shows the processing details.

---

**I moved the project and now it no longer works.**

Manually delete the `venv/` folder. On the next launch via `StartDubbing.bat`, the Launcher will recreate the venv in the new location.

---

## Build and Distribution

**API credentials are not included in the distribution package.**

This is the correct behavior. Azure and Google credentials are never included in the package for security reasons. They must be manually placed in the `credentials/` folder on each machine after installation, following the structure of the template files.

---

## General Questions

**Is it possible to use the project without an internet connection?**

Partially. Transcription (Whisper) and translation (Helsinki-NLP) work offline after the models have been downloaded. TTS synthesis (Azure, Google) requires an internet connection as it uses cloud APIs.

---

**Is it possible to add new languages to the interface?**

Yes. New languages will be added progressively over time. To request a specific language you can contact the project directly. Anyone who wants to add it independently must:

1. Create the file `locale/Active/<language_code>.json` following the structure of the other existing language files
2. Add the new language to `locale/System/languages.json`

Both steps are required: without the second, the language will not be recognized by the system.

---

**Does the project support batch processing of multiple videos?**

Currently the workflow is designed for one file at a time. You can prepare multiple files and process them in sequence, but there is no automatic batch mode. This feature is being considered for future development.
