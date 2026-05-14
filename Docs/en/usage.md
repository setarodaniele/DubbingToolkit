# Usage Guide

This guide describes the operational workflow of DubbingToolkit, from preparing input files to the final dubbed audio.

---

## Starting the Project

Double-click `StartDubbing.bat`. The project launches and presents the main interface with the project management menu.

---

## Creating and Selecting a Project

From the main screen, select "Project Management" (option 0) and create a new project. Each project is an isolated workspace for a specific video.

Once created, the project is set as active and remains available for subsequent operations.

---

## Operational Workflow

The process consists of 4 stages. Each stage can be run individually or as part of the full workflow.

| Stage | Operation              | Output Folder                                    |
|-------|------------------------|--------------------------------------------------|
| 1     | Audio extraction       | `Workspace/projects/{name}/audio_extraction/current/` |
| 2     | Transcription          | `Workspace/projects/{name}/transcripts/current/`      |
| 3     | Translation            | `Workspace/projects/{name}/translated/current/`       |
| 4     | Text-to-speech (TTS)   | `Workspace/projects/{name}/dubbed/current/`           |

> **Important:** after transcription and after translation, a manual review of the generated text is recommended. Corrections allow you to improve the quality of the final audio and handle any timing mismatches with the original speech.

---

## Preparing Input

### Video Input

During audio extraction, the system presents an import dialog that allows you to:
1. Use the video from an external location (maintains original path)
2. Copy the video into the project (`Workspace/projects/{name}/video_input/`)
3. Move the video into the project

Supported formats: those handled by ffmpeg (mp4, mkv, avi, mov, etc.).

### Direct Audio Input

If you already have extracted audio, during transcription you can manually select an audio file from the `Workspace/projects/{name}/audio_input/` folder or from an external location. In this case, Stage 1 — Audio extraction can be skipped.

---

## Stage 1 — Audio Extraction

The system extracts audio tracks from the video via ffmpeg. All extracted audio files are saved in `Workspace/projects/{name}/audio_extraction/current/` with names `track_01.wav`, `track_02.wav`, etc.

For each track, a metadata file is automatically generated (`track_XX_metadata.json`) containing information about codec, sample rate, duration, and other properties.

---

## Stage 2 — Transcription

The audio is transcribed into SRT format. The spoken language is detected automatically and can be changed from the menu before starting transcription. The result is saved in `Workspace/projects/{name}/transcripts/current/`.

> **Tip:** before proceeding to translation, review and correct the transcribed text. Errors at this stage carry over to all subsequent stages.

---

## Stage 3 — Translation

The transcribed SRT file is translated into the target language. Translation happens entirely locally. Required models are downloaded automatically on first run for each language pair. The result is saved in `Workspace/projects/{name}/translated/current/`.

If the direct language pair is not available, pivot translation via English as an intermediate language is planned for the future.

> **Tip:** review the translated text before starting synthesis. Manual corrections allow you to handle any timing mismatches with the original speech.

---

## Stage 4 — Text-to-Speech (TTS)

The translated text is synthesized segment by segment via the selected TTS provider. Segments are then merged into the final audio file, saved in `Workspace/projects/{name}/dubbed/current/`.

### TTS Providers

The system currently supports two providers:

- **Azure Cognitive Services Speech** — Microsoft's cloud TTS service
- **Google Cloud Text-to-Speech** — Google's cloud TTS service

Provider and voice are selected directly from the TTS menu. The system includes a dedicated function to listen to audio samples of available voices before starting synthesis.

### Cost Monitoring

When the TTS module starts, an estimated usage is automatically displayed. To check actual consumption, consult your provider's dashboard directly.

---

## Interface Language

The interface language is selected at startup and can be changed at any time from the settings menu without restarting the project.

---

## Project Management

### Duplication

You can duplicate an existing project to create a copy with a new name. Useful for testing variations of the same source.

### Rename

A project can be renamed at any time from project management. If the project is active, the active pointer is updated automatically.

### Deletion

A project can be deleted. If the `use_trash` setting is enabled, the project is moved to Trash; otherwise it is permanently deleted.

### Open Folder

You can open a project folder directly in Explorer to manually inspect generated files.

---

## Operational Tips

- Use short project and file names without spaces or special characters to avoid path-related issues.
- Files in `Workspace/projects/{name}/video_input/` are never modified by the system.
- Each stage generates metadata (`.json` files or `_info.txt`): useful for tracking progress or diagnosing issues.
- If the process is interrupted, you can resume from the next stage after the one already completed, using the files in the intermediate output folders.
- Processed files at each stage are automatically archived in that stage's `archive/` folder to preserve history.
